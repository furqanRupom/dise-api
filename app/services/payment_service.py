"""Phase 6: Stripe payments.

Rules this module follows
-------------------------
1. Webhooks drive state. `start_charge` only returns a client_secret; only the
   `payment_intent.succeeded` webhook confirms a booking.
2. Stripe calls never happen inside a long transaction. Pattern: insert the
   Payment row + commit -> call Stripe with the row's idempotency_key -> update
   the row. The only lock held across a Stripe call is a single Payment row
   (taken in process_* methods) and it acts as a mutex against double-sends.
3. A declined card does not fail a charge row. The PaymentIntent goes back to
   requires_payment_method and can be retried, so we only record failure_reason.
4. This module never imports FleetService (FleetService imports this one).
"""

import logging
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import stripe
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import BookingStatusHistory, Payment, User
from app.models.booking import Booking
from app.models.enums import BookingStatus, PaymentStatus, PaymentType, UserRole
from app.models.payments import ProcessedWebhookEvent
from app.services.booking_service import BookingService
from app.services.stripe_service import StripeService

logger = logging.getLogger(__name__)

LIVE = (PaymentStatus.pending, PaymentStatus.succeeded)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class PaymentService:
    def __init__(self, db: Session, gateway: StripeService | None = None):
        self.db = db
        self._gateway = gateway
        self.booking_service = BookingService(db)

    @property
    def gateway(self) -> StripeService:
        # Lazy: FleetService builds a PaymentService but never needs Stripe.
        if self._gateway is None:
            self._gateway = StripeService()
        return self._gateway

    def _commit(self) -> None:
        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

    @staticmethod
    def _attempt_key(prefix: str, booking_id: uuid.UUID, attempt: int) -> str:
        """First attempt keeps the plain key from the plan (charge:{id});
        later attempts get a suffix so retries never collide on UNIQUE."""
        base = f"{prefix}:{booking_id}"
        return base if attempt == 0 else f"{base}:{attempt}"

    def _payments_of(self, booking_id: uuid.UUID, type_: PaymentType) -> list[Payment]:
        return list(
            self.db.execute(
                select(Payment)
                .where(Payment.booking_id == booking_id, Payment.type == type_)
                .order_by(Payment.created_at.asc())
            )
            .scalars()
            .all()
        )

    def _active_hold(self, booking_id: uuid.UUID) -> Payment | None:
        """Newest deposit_hold that is pending or authorized."""
        return self.db.execute(
            select(Payment)
            .where(
                Payment.booking_id == booking_id,
                Payment.type == PaymentType.deposit_hold,
                Payment.status.in_(LIVE),
            )
            .order_by(Payment.created_at.desc())
            .limit(1)
        ).scalar_one_or_none()

    def _lock_payment(self, payment_id: uuid.UUID) -> Payment:
        return self.db.execute(
            select(Payment)
            .where(Payment.id == payment_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        ).scalar_one()

    def _get_or_create(
        self,
        booking: Booking,
        type_: PaymentType,
        amount: Decimal,
        key: str,
    ) -> Payment:
        stmt = select(Payment).where(Payment.idempotency_key == key)
        payment = self.db.execute(stmt).scalar_one_or_none()
        if payment:
            return payment

        self.db.add(
            Payment(
                booking_id=booking.id,
                type=type_,
                amount=amount,
                currency=booking.currency,
                status=PaymentStatus.pending,
                idempotency_key=key,
            )
        )
        try:
            self.db.commit()
        except IntegrityError:  # a concurrent retry won the insert
            self.db.rollback()
        return self.db.execute(stmt).scalar_one()

    # ---- Stripe customer ------------------------------------------------ #
    def _ensure_stripe_customer(self, customer_id: uuid.UUID) -> str:
        user = self.db.execute(
            select(User)
            .where(User.id == customer_id)
            .execution_options(populate_existing=True)
        ).scalar_one()

        if user.stripe_customer_id:
            return user.stripe_customer_id

        # Safe under concurrency: both callers use the same idempotency key
        # (customer:{user.id}), so Stripe hands both the same customer.
        customer = self.gateway.create_customer(user)
        user.stripe_customer_id = customer.id
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status.HTTP_409_CONFLICT, "Please retry")
        return customer.id

    def _ensure_intent(
        self,
        payment: Payment,
        booking: Booking,
        customer_id: uuid.UUID,
        **intent_kwargs,
    ):
        """Create the PaymentIntent once; on retries return the existing one."""
        try:
            if payment.stripe_payment_intent_id is None:
                stripe_customer_id = self._ensure_stripe_customer(customer_id)
                intent = self.gateway.create_intent(
                    payment, booking, customer_id=stripe_customer_id, **intent_kwargs
                )
                payment.stripe_payment_intent_id = intent.id
                self.db.commit()
            else:
                intent = self.gateway.retrieve_intent(payment.stripe_payment_intent_id)
        except stripe.StripeError:
            self.db.rollback()
            raise HTTPException(
                status.HTTP_502_BAD_GATEWAY, "Payment provider error, please retry"
            )
        return intent

    def _assert_dates_available(self, booking: Booking) -> None:
        """Fail fast so a customer is not asked to pay for a vehicle that was
        confirmed for someone else. The DB exclusion constraint is still the
        final authority (see _confirm_booking)."""
        conflict = self.db.execute(
            select(Booking.id)
            .where(
                Booking.vehicle_id == booking.vehicle_id,
                Booking.id != booking.id,
                Booking.status.in_([BookingStatus.confirmed, BookingStatus.active]),
                Booking.deleted_at.is_(None),
                Booking.start_date < booking.end_date,
                Booking.end_date > booking.start_date,
            )
            .limit(1)
        ).scalar_one_or_none()
        if conflict:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "Vehicle is no longer available for the requested dates",
            )

    # ------------------------------------------------------------------ #
    # Customer-facing: charge
    # ------------------------------------------------------------------ #
    def start_charge(self, customer_id: uuid.UUID, booking_id: uuid.UUID) -> dict:
        booking = self.booking_service.get_customer_booking(customer_id, booking_id)

        if booking.status != BookingStatus.pending_payment:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                f"Booking is {booking.status.value}, cannot be paid",
            )
        self._assert_dates_available(booking)

        # 100% coupon: nothing to charge, confirm directly.
        if booking.total_price == Decimal("0.00"):
            self._confirm_booking(
                booking.id, None, reason="Confirmed - no payment required"
            )
            self._commit()
            self.db.refresh(booking)
            if booking.status != BookingStatus.confirmed:
                raise HTTPException(
                    status.HTTP_409_CONFLICT,
                    "Vehicle is no longer available for the requested dates",
                )
            return {"client_secret": None, "payment_id": None, "confirmed": True}

        charges = self._payments_of(booking.id, PaymentType.charge)
        latest = charges[-1] if charges else None

        if latest is not None and latest.status == PaymentStatus.succeeded:
            raise HTTPException(status.HTTP_409_CONFLICT, "Booking is already paid")

        if latest is None or latest.status in (
            PaymentStatus.cancelled,
            PaymentStatus.failed,
        ):
            payment = self._get_or_create(
                booking,
                PaymentType.charge,
                booking.total_price,
                self._attempt_key("charge", booking.id, len(charges)),
            )
        else:
            payment = latest  # pending: retry on the same PaymentIntent

        intent = self._ensure_intent(
            payment, booking, customer_id, save_card=settings.STRIPE_SAVE_CARDS
        )
        return {
            "client_secret": intent.client_secret,
            "payment_id": payment.id,
            "confirmed": False,
        }

    def cancel_open_charge(self, booking_id: uuid.UUID) -> None:
        """After a customer cancels a pending_payment booking: kill the open
        PaymentIntent so they cannot still pay for a dead booking. If this
        fails, _confirm_booking refunds any late payment anyway."""
        open_charges = (
            self.db.execute(
                select(Payment).where(
                    Payment.booking_id == booking_id,
                    Payment.type == PaymentType.charge,
                    Payment.status == PaymentStatus.pending,
                    Payment.stripe_payment_intent_id.is_not(None),
                )
            )
            .scalars()
            .all()
        )
        for payment in open_charges:
            try:
                self.gateway.cancel_intent(
                    payment.stripe_payment_intent_id, f"cancel_charge:{payment.id}"
                )
                payment.status = PaymentStatus.cancelled
                self.db.commit()
            except stripe.StripeError:
                self.db.rollback()
                logger.warning("Could not cancel open charge %s", payment.id)

    # ------------------------------------------------------------------ #
    # Customer-facing: deposit hold
    # ------------------------------------------------------------------ #
    def start_deposit_hold(self, customer_id: uuid.UUID, booking_id: uuid.UUID) -> dict:
        """Card hold (manual capture). Holds lapse after ~7 days, so it is only
        allowed within DEPOSIT_HOLD_WINDOW_DAYS of pickup; check-out requires it."""
        booking = self.booking_service.get_customer_booking(customer_id, booking_id)

        if booking.status != BookingStatus.confirmed:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "Deposit can only be authorized for confirmed bookings",
            )
        if booking.deposit_hold_amount <= Decimal("0.00"):
            raise HTTPException(status.HTTP_409_CONFLICT, "No deposit is required")

        today = business_today()
        if today >= booking.end_date:
            raise HTTPException(status.HTTP_409_CONFLICT, "Booking period has ended")
        if (booking.start_date - today).days > settings.DEPOSIT_HOLD_WINDOW_DAYS:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                f"Deposit can be authorized from {settings.DEPOSIT_HOLD_WINDOW_DAYS} "
                "days before pickup",
            )

        holds = self._payments_of(booking.id, PaymentType.deposit_hold)
        active = self._active_hold(booking.id)
        now = _utcnow()

        if active is not None and active.status == PaymentStatus.succeeded:
            if (
                active.authorization_expires_at is None
                or active.authorization_expires_at > now
            ):
                raise HTTPException(
                    status.HTTP_409_CONFLICT, "Deposit is already authorized"
                )
            active = None  # authorization lapsed -> new attempt below

        if active is not None:  # pending: reuse the same intent
            payment = active
        else:
            payment = self._get_or_create(
                booking,
                PaymentType.deposit_hold,
                booking.deposit_hold_amount,
                self._attempt_key("deposit_hold", booking.id, len(holds)),
            )

        intent = self._ensure_intent(payment, booking, customer_id, manual_capture=True)
        return {
            "client_secret": intent.client_secret,
            "payment_id": payment.id,
            "confirmed": False,
        }

    def assert_deposit_ready(self, booking: Booking) -> None:
        """Called by FleetService.check_out."""
        if booking.deposit_hold_amount <= Decimal("0.00"):
            return
        hold = self._active_hold(booking.id)
        if hold is None or hold.status != PaymentStatus.succeeded:
            raise HTTPException(
                status.HTTP_409_CONFLICT, "Deposit hold has not been authorized"
            )
        if (
            hold.authorization_expires_at is not None
            and hold.authorization_expires_at <= _utcnow()
        ):
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "Deposit authorization has expired; the customer must re-authorize",
            )

    # ------------------------------------------------------------------ #
    # Staff: deposit capture / release after check-in
    # ------------------------------------------------------------------ #
    def _assert_no_deposit_outcome(self, booking_id: uuid.UUID) -> None:
        rows = self._payments_of(
            booking_id, PaymentType.deposit_capture
        ) + self._payments_of(booking_id, PaymentType.deposit_release)
        if any(r.status in LIVE for r in rows):
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "A deposit capture or release already exists for this booking",
            )

    def capture_deposit(
        self,
        booking_id: uuid.UUID,
        amount: Decimal,
        reason: str,
    ) -> Payment:
        booking = self.booking_service.get_booking(booking_id, for_update=True)
        if booking.status != BookingStatus.completed:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "Deposit can only be captured after the vehicle is returned",
            )
        hold = self._active_hold(booking.id)
        if hold is None or hold.status != PaymentStatus.succeeded:
            raise HTTPException(
                status.HTTP_409_CONFLICT, "No authorized deposit hold to capture from"
            )
        if amount > hold.amount:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                f"Amount exceeds the authorized deposit ({hold.amount})",
            )
        self._assert_no_deposit_outcome(booking.id)

        attempts = len(self._payments_of(booking.id, PaymentType.deposit_capture))
        payment = self._get_or_create(
            booking,
            PaymentType.deposit_capture,
            amount,
            self._attempt_key("deposit_capture", booking.id, attempts),
        )
        payment.note = reason.strip()[:255]
        self._commit()

        self.process_deposit_capture(payment.id)
        self.db.refresh(payment)
        return payment

    def release_deposit(self, booking_id: uuid.UUID) -> Payment:
        """Clean return, no findings: release the hold."""
        booking = self.booking_service.get_booking(booking_id, for_update=True)
        if booking.status != BookingStatus.completed:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "Deposit can only be released after the vehicle is returned",
            )
        hold = self._active_hold(booking.id)
        if hold is None or hold.status != PaymentStatus.succeeded:
            raise HTTPException(
                status.HTTP_409_CONFLICT, "No authorized deposit hold to release"
            )
        self._assert_no_deposit_outcome(booking.id)

        payment = self._get_or_create(
            booking,
            PaymentType.deposit_release,
            hold.amount,
            f"deposit_release:{booking.id}",
        )
        self.process_deposit_release(payment.id)
        self.db.refresh(payment)
        return payment

    # ------------------------------------------------------------------ #
    # Read APIs
    # ------------------------------------------------------------------ #
    def list_payments(self, booking_id: uuid.UUID, user: User) -> list[Payment]:
        booking = self.booking_service.get_booking(booking_id)
        # 404 (not 403) so booking ids cannot be probed.
        if user.role == UserRole.customer and booking.customer_id != user.id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Booking not found")
        return list(
            self.db.execute(
                select(Payment)
                .where(Payment.booking_id == booking.id)
                .order_by(Payment.created_at.asc())
            )
            .scalars()
            .all()
        )

    def admin_list_payments(
        self,
        type_: PaymentType | None,
        status_: PaymentStatus | None,
        page: int,
        limit: int,
    ) -> tuple[list[Payment], int]:
        query = select(Payment)
        count_query = select(func.count()).select_from(Payment)
        if type_ is not None:
            query = query.where(Payment.type == type_)
            count_query = count_query.where(Payment.type == type_)
        if status_ is not None:
            query = query.where(Payment.status == status_)
            count_query = count_query.where(Payment.status == status_)
        query = (
            query.order_by(Payment.created_at.desc(), Payment.id.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        total = self.db.execute(count_query).scalar_one()
        return list(self.db.execute(query).scalars().all()), total

    # ------------------------------------------------------------------ #
    # Webhooks
    # ------------------------------------------------------------------ #
    def handle_event(self, event: dict) -> None:
        """`event` is the verified, JSON-decoded Stripe event (plain dict)."""
        # Dedupe inside the SAME transaction as the handling: if the handler
        # fails the event row rolls back and Stripe's retry reprocesses it.
        self.db.add(
            ProcessedWebhookEvent(event_id=event["id"], event_type=event["type"])
        )
        try:
            self.db.flush()
        except IntegrityError:
            self.db.rollback()
            return  # already processed (concurrent duplicates wait on this insert)

        handlers = {
            "payment_intent.succeeded": self._on_intent_succeeded,
            "payment_intent.payment_failed": self._on_intent_failed,
            "payment_intent.canceled": self._on_intent_canceled,
            "payment_intent.amount_capturable_updated": self._on_hold_authorized,
            "refund.updated": self._on_refund_updated,
            "refund.failed": self._on_refund_updated,
            "charge.refund.updated": self._on_refund_updated,
        }
        try:
            handler = handlers.get(event["type"])
            if handler:
                handler(event["data"]["object"])
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

    def _find_by_intent(self, obj: dict) -> Payment | None:
        base = (
            select(Payment).with_for_update().execution_options(populate_existing=True)
        )
        payment = self.db.execute(
            base.where(Payment.stripe_payment_intent_id == obj["id"])
        ).scalar_one_or_none()
        if payment is None:
            payment = self._find_by_metadata(base, obj)
        return payment

    def _find_by_refund(self, obj: dict) -> Payment | None:
        base = (
            select(Payment).with_for_update().execution_options(populate_existing=True)
        )
        payment = self.db.execute(
            base.where(Payment.stripe_refund_id == obj["id"])
        ).scalar_one_or_none()
        if payment is None:
            # Webhook can beat our commit of stripe_refund_id. The metadata
            # lookup blocks on the row lock process_refund holds, then sees
            # the committed result.
            payment = self._find_by_metadata(base, obj)
        return payment

    def _find_by_metadata(self, base, obj: dict) -> Payment | None:
        raw = (obj.get("metadata") or {}).get("payment_id")
        if not raw:
            return None
        try:
            pid = uuid.UUID(raw)
        except ValueError:
            return None
        return self.db.execute(base.where(Payment.id == pid)).scalar_one_or_none()

    def _on_intent_succeeded(self, obj: dict) -> None:
        payment = self._find_by_intent(obj)
        # deposit_hold PIs also emit "succeeded" when captured; that is
        # settled synchronously in process_deposit_capture, so ignore here.
        if payment is None or payment.type != PaymentType.charge:
            return
        if payment.status == PaymentStatus.succeeded:
            return
        payment.status = PaymentStatus.succeeded
        payment.failure_reason = None
        self._confirm_booking(payment.booking_id, payment)

    def _on_intent_failed(self, obj: dict) -> None:
        # Intent returns to requires_payment_method and stays retryable, so
        # record why but keep the row pending.
        payment = self._find_by_intent(obj)
        if payment and payment.status == PaymentStatus.pending:
            err = obj.get("last_payment_error") or {}
            payment.failure_reason = (err.get("message") or "Payment failed")[:255]

    def _on_intent_canceled(self, obj: dict) -> None:
        payment = self._find_by_intent(obj)
        if payment is None:
            return
        if payment.status == PaymentStatus.pending:
            payment.status = PaymentStatus.cancelled
        elif (
            payment.type == PaymentType.deposit_hold
            and payment.status == PaymentStatus.succeeded
        ):
            # Stripe auto-cancels an uncaptured hold when the authorization lapses.
            payment.status = PaymentStatus.cancelled

    def _on_hold_authorized(self, obj: dict) -> None:
        if obj.get("status") != "requires_capture":
            return
        payment = self._find_by_intent(obj)
        if (
            payment is None
            or payment.type != PaymentType.deposit_hold
            or payment.status != PaymentStatus.pending
        ):
            return
        now = _utcnow()
        payment.status = PaymentStatus.succeeded
        payment.failure_reason = None
        payment.authorized_at = now
        payment.authorization_expires_at = self.gateway.get_capture_before(
            obj["id"]
        ) or (now + timedelta(days=settings.DEPOSIT_HOLD_FALLBACK_EXPIRY_DAYS))

    def _on_refund_updated(self, obj: dict) -> None:
        payment = self._find_by_refund(obj)
        if (
            payment is None
            or payment.type != PaymentType.refund
            or payment.status != PaymentStatus.pending
        ):
            return
        payment.stripe_refund_id = payment.stripe_refund_id or obj["id"]
        payment.status = self._map_refund_status(obj.get("status", ""))
        if payment.status == PaymentStatus.failed:
            payment.failure_reason = (obj.get("failure_reason") or "Refund failed")[
                :255
            ]

    @staticmethod
    def _map_refund_status(s: str) -> PaymentStatus:
        return {
            "succeeded": PaymentStatus.succeeded,
            "failed": PaymentStatus.failed,
            "canceled": PaymentStatus.failed,
        }.get(s, PaymentStatus.pending)

    # ---- booking confirmation (+ the two race conditions) --------------- #
    def _confirm_booking(
        self,
        booking_id: uuid.UUID,
        payment: Payment | None,
        *,
        reason: str = "Payment received",
    ) -> None:
        """pending_payment -> confirmed. Does not commit.

        Race 1: paid, but the booking was cancelled meanwhile -> queue refund.
        Race 2: two customers paid for overlapping dates (the exclusion
                constraint only covers confirmed/active, so both can reach
                pay). The second UPDATE raises IntegrityError -> cancel + refund.
        """
        booking = self.db.execute(
            select(Booking)  # no deleted_at filter: a paid booking must be dealt with
            .where(Booking.id == booking_id)
            .with_for_update(of=Booking)
            .execution_options(populate_existing=True)
        ).scalar_one()

        if booking.status == BookingStatus.confirmed:
            return

        if booking.status != BookingStatus.pending_payment:
            logger.warning(
                "Payment for booking %s arrived while %s; refunding",
                booking.id,
                booking.status.value,
            )
            self._queue_full_refund(booking, payment)
            return

        try:
            with self.db.begin_nested():
                booking.status = BookingStatus.confirmed
                self.db.add(
                    BookingStatusHistory(
                        booking=booking,
                        from_status=BookingStatus.pending_payment.value,
                        to_status=BookingStatus.confirmed.value,
                        changed_by=None,
                        reason=reason,
                    )
                )
                self.db.flush()  # exclusion constraint fires here
            return
        except IntegrityError:
            pass  # savepoint rolled back; fall through to cancel + refund

        self.db.refresh(booking)
        booking.status = BookingStatus.cancelled
        booking.approval_deadline = None
        self.db.add(
            BookingStatusHistory(
                booking=booking,
                from_status=BookingStatus.pending_payment.value,
                to_status=BookingStatus.cancelled.value,
                changed_by=None,
                reason="Vehicle no longer available; payment refunded",
            )
        )
        self.booking_service.coupon_service.release(booking)
        self._queue_full_refund(booking, payment)

    def _queue_full_refund(self, booking: Booking, payment: Payment | None) -> None:
        if payment is None:
            return
        key = f"refund:{booking.id}"
        exists = self.db.execute(
            select(Payment.id).where(Payment.idempotency_key == key)
        ).scalar_one_or_none()
        if exists:
            return
        self.db.add(
            Payment(
                booking_id=booking.id,
                type=PaymentType.refund,
                amount=payment.amount,
                currency=payment.currency,
                status=PaymentStatus.pending,
                idempotency_key=key,
                note="Automatic full refund: booking could not be fulfilled",
            )
        )

    # ------------------------------------------------------------------ #
    # Settling queued rows (called from router background tasks + sweeper)
    # ------------------------------------------------------------------ #
    def process_refund(self, payment_id: uuid.UUID) -> None:
        payment = self._lock_payment(payment_id)

        # stripe_refund_id is the durable double-refund guard (Stripe only
        # remembers idempotency keys ~24h).
        if (
            payment.type != PaymentType.refund
            or payment.status != PaymentStatus.pending
            or payment.stripe_refund_id
        ):
            self.db.rollback()
            return

        charge = self.db.execute(
            select(Payment).where(
                Payment.booking_id == payment.booking_id,
                Payment.type == PaymentType.charge,
                Payment.status == PaymentStatus.succeeded,
            )
        ).scalar_one_or_none()

        if charge is None or charge.stripe_payment_intent_id is None:
            payment.status = PaymentStatus.failed
            payment.failure_reason = "No settled charge to refund"
            self._commit()
            return

        try:
            refund = self.gateway.create_refund(
                charge.stripe_payment_intent_id, payment
            )
        except stripe.InvalidRequestError as e:  # permanent, e.g. already refunded
            payment.status = PaymentStatus.failed
            payment.failure_reason = str(e)[:255]
            self._commit()
            return
        except stripe.StripeError:  # transient: stay pending, sweeper retries
            self.db.rollback()
            return

        payment.stripe_refund_id = refund.id
        payment.status = self._map_refund_status(refund.status)
        if payment.status == PaymentStatus.failed:
            payment.failure_reason = "Refund failed"
        self._commit()

    def _cancel_hold_intent(self, hold: Payment, key: str) -> None:
        try:
            self.gateway.cancel_intent(hold.stripe_payment_intent_id, key)
        except stripe.InvalidRequestError:
            # Already cancelled on Stripe's side (e.g. authorization lapsed)?
            if self.gateway.retrieve_intent(hold.stripe_payment_intent_id).status != (
                "canceled"
            ):
                raise

    def process_deposit_release(self, payment_id: uuid.UUID) -> None:
        release = self._lock_payment(payment_id)
        if (
            release.type != PaymentType.deposit_release
            or release.status != PaymentStatus.pending
        ):
            self.db.rollback()
            return

        captured = any(
            r.status in LIVE
            for r in self._payments_of(release.booking_id, PaymentType.deposit_capture)
        )
        hold = self._active_hold(release.booking_id)

        try:
            if captured:
                # Stripe already released the uncaptured remainder on capture.
                release.status = PaymentStatus.cancelled
                release.note = "Deposit was captured; remainder released by Stripe"
            elif hold is None or hold.stripe_payment_intent_id is None:
                release.status = PaymentStatus.cancelled  # nothing was ever held
            else:
                was_authorized = hold.status == PaymentStatus.succeeded
                self._cancel_hold_intent(hold, release.idempotency_key)
                release.status = (
                    PaymentStatus.succeeded
                    if was_authorized
                    else PaymentStatus.cancelled
                )
                hold.status = PaymentStatus.cancelled
        except stripe.InvalidRequestError as e:
            release.status = PaymentStatus.failed
            release.failure_reason = str(e)[:255]
        except stripe.StripeError:
            self.db.rollback()
            return
        self._commit()

    def process_deposit_capture(self, payment_id: uuid.UUID) -> None:
        capture = self._lock_payment(payment_id)
        if (
            capture.type != PaymentType.deposit_capture
            or capture.status != PaymentStatus.pending
        ):
            self.db.rollback()
            return

        hold = self._active_hold(capture.booking_id)
        if hold is None or hold.status != PaymentStatus.succeeded:
            capture.status = PaymentStatus.failed
            capture.failure_reason = "No authorized deposit hold"
            self._commit()
            return

        try:
            self.gateway.capture_intent(
                hold.stripe_payment_intent_id,
                to_minor_units(capture.amount, capture.currency),
                capture.idempotency_key,
            )
            capture.status = PaymentStatus.succeeded
        except stripe.InvalidRequestError as e:
            # Typically an expired authorization: needs manual follow-up.
            capture.status = PaymentStatus.failed
            capture.failure_reason = str(e)[:255]
        except stripe.StripeError:
            self.db.rollback()  # transient: stays pending, sweeper retries
            return
        self._commit()

    def process_pending(self) -> int:
        """Sweeper. Safe to run every minute, after cancellations and after
        webhooks. Rows that failed permanently are NOT retried (admin list)."""
        rows = self.db.execute(
            select(Payment.id, Payment.type)
            .where(
                Payment.status == PaymentStatus.pending,
                Payment.type.in_(
                    [
                        PaymentType.refund,
                        PaymentType.deposit_release,
                        PaymentType.deposit_capture,
                    ]
                ),
                or_(
                    Payment.type != PaymentType.refund,
                    Payment.stripe_refund_id.is_(None),
                ),
            )
            .order_by(Payment.created_at)
            .limit(50)
        ).all()
        self.db.rollback()  # end the read transaction before Stripe calls

        handlers = {
            PaymentType.refund: self.process_refund,
            PaymentType.deposit_release: self.process_deposit_release,
            PaymentType.deposit_capture: self.process_deposit_capture,
        }
        for pid, ptype in rows:
            try:
                handlers[ptype](pid)
            except Exception:
                self.db.rollback()
                logger.exception("Failed processing payment %s", pid)
        return len(rows)
