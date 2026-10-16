"""Thin wrapper around the Stripe SDK.

Every Stripe call in the app goes through here so that:
  * tests can inject a fake gateway,
  * minor-unit conversion lives in one place,
  * swapping to another PSP later only touches this file.

Requires stripe>=8 (exceptions are exposed as stripe.StripeError, etc.).
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

import stripe

from app.core.config import settings

ZERO_DECIMAL = {
    "BIF",
    "CLP",
    "DJF",
    "GNF",
    "JPY",
    "KMF",
    "KRW",
    "MGA",
    "PYG",
    "RWF",
    "UGX",
    "VND",
    "VUV",
    "XAF",
    "XOF",
    "XPF",
}


def to_minor_units(amount: Decimal, currency: str) -> int:
    """Convert a decimal amount to the currency's smallest unit."""
    if currency.upper() in ZERO_DECIMAL:
        return int(amount)

    return int((amount * 100).quantize(Decimal("1")))


class StripeService:
    def __init__(self) -> None:
        stripe.api_key = settings.STRIPE_SECRET_KEY

    # ---- customers -------------------------------------------------------

    def create_customer(self, user):
        return stripe.Customer.create(
            email=user.email,
            name=user.name,
            metadata={"user_id": str(user.id)},
            idempotency_key=f"customer:{user.id}",
        )

    # ---- payment intents -------------------------------------------------

    def create_intent(
        self,
        payment,
        booking,
        *,
        customer_id: str,
        manual_capture: bool = False,
        save_card: bool = False,
    ):
        params: dict[str, Any] = {
            "amount": to_minor_units(payment.amount, payment.currency),
            "currency": payment.currency.lower(),
            "customer": customer_id,
            "automatic_payment_methods": {"enabled": True},
            "capture_method": "manual" if manual_capture else "automatic",
            "metadata": {
                "booking_id": str(booking.id),
                "customer_id": str(booking.customer_id),
                "payment_id": str(payment.id),
                "type": payment.type.value,
            },
            "idempotency_key": payment.idempotency_key,
        }

        if save_card:
            params["setup_future_usage"] = "off_session"

        return stripe.PaymentIntent.create(**params)

    def retrieve_intent(self, pi_id: str):
        return stripe.PaymentIntent.retrieve(pi_id)

    def cancel_intent(self, pi_id: str, idempotency_key: str):
        """Cancel an intent and release its authorization when applicable."""
        return stripe.PaymentIntent.cancel(
            pi_id,
            idempotency_key=idempotency_key,
        )

    def capture_intent(
        self,
        pi_id: str,
        amount_minor: int,
        idempotency_key: str,
    ):
        """Capture a payment in full or partially."""
        return stripe.PaymentIntent.capture(
            pi_id,
            amount_to_capture=amount_minor,
            idempotency_key=idempotency_key,
        )

    def get_capture_before(self, pi_id: str) -> datetime | None:
        """Return the card authorization expiry if Stripe provides it."""
        try:
            payment_intent = stripe.PaymentIntent.retrieve(
                pi_id,
                expand=["latest_charge"],
            )

            latest_charge = payment_intent.latest_charge
            if not isinstance(latest_charge, stripe.Charge):
                return None

            payment_method_details = latest_charge.payment_method_details
            if payment_method_details is None:
                return None

            card = payment_method_details.card
            if card is None:
                return None

            timestamp = card.capture_before
            if timestamp is None:
                return None

            return datetime.fromtimestamp(timestamp, tz=timezone.utc)

        except (stripe.StripeError, AttributeError, KeyError, TypeError):
            return None

    # ---- refunds ---------------------------------------------------------

    def create_refund(self, pi_id: str, payment):
        return stripe.Refund.create(
            payment_intent=pi_id,
            amount=to_minor_units(payment.amount, payment.currency),
            metadata={
                "booking_id": str(payment.booking_id),
                "payment_id": str(payment.id),
            },
            idempotency_key=payment.idempotency_key,
        )
