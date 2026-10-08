from datetime import datetime, timezone
from decimal import ROUND_HALF_UP, Decimal
from uuid
from fastapi import HTTPException, status
from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Booking, Coupon, CouponUsage
from app.models.enums import DiscountType
from app.schemas.coupon import CouponCreate, CouponUpdate

CENT = Decimal("0.01")


class CouponService:
    def __init__(self, db: Session):
        self.db = db

    # HELPERS
    @staticmethod
    def normalize_code(code: str) -> str:
        return code.strip().upper()

    def _get_by_code(self, code: str, for_update: bool = False):
        stmt = select(Coupon).where(
            Coupon.code == self.normalize_code(code),
            Coupon.deleted_at.is_(None),
        )
        if for_update:
            stmt = stmt.with_for_update(of=Coupon).execution_options(
                populate_existing=True
            )
        coupon = self.db.execute(stmt).scalar_one_or_none()
        if coupon is None:
            # Same message for unknown/deleted codes: don't help code guessing.
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid coupon code"
            )
        return coupon

    def get_coupons(self):
        result = self.db.execute(
            select(Coupon)
            .where(Coupon.deleted_at.is_(None))
            .order_by(Coupon.created_at.desc())
        )
        return result.scalars().all()

    def create_coupon(self, payload: CouponCreate):
        code = payload.code.strip().upper()

        existing_coupon = self.db.execute(
            select(Coupon).where(
                Coupon.code == code,
                Coupon.deleted_at.is_(None),
            )
        ).scalar_one_or_none()

        if existing_coupon:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Coupon already exists",
            )

        if payload.valid_to <= payload.valid_from:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="valid_to must be after valid_from",
            )

        coupon_data = payload.model_dump(exclude={"code"})

        coupon = Coupon(
            **coupon_data,
            code=code,
        )

        try:
            self.db.add(coupon)
            self.db.commit()
            self.db.refresh(coupon)

            return coupon

        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Coupon could not be created",
            )

    def get_coupon(self, coupon_id: UUID):
        coupon = self.db.execute(
            select(Coupon).where(
                Coupon.id == coupon_id,
                Coupon.deleted_at.is_(None),
            )
        ).scalar_one_or_none()

        if not coupon:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Coupon not found",
            )

        return coupon

    def update_coupon(
        self,
        coupon_id: UUID,
        payload: CouponUpdate,
    ):
        coupon = self.get_coupon(coupon_id)

        update_data = payload.model_dump(exclude_unset=True)

        # Normalize code if provided
        if "code" in update_data:
            code = update_data["code"].strip().upper()

            existing_coupon = self.db.execute(
                select(Coupon).where(
                    Coupon.code == code,
                    Coupon.id != coupon_id,
                    Coupon.deleted_at.is_(None),
                )
            ).scalar_one_or_none()

            if existing_coupon:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Coupon code already exists",
                )

            update_data["code"] = code

        # Validate dates
        valid_from = update_data.get(
            "valid_from",
            coupon.valid_from,
        )

        valid_to = update_data.get(
            "valid_to",
            coupon.valid_to,
        )

        if valid_to <= valid_from:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="valid_to must be greater than valid_from",
            )

        # Apply changes
        for field, value in update_data.items():
            setattr(coupon, field, value)

        try:
            self.db.commit()
            self.db.refresh(coupon)

            return coupon

        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Coupon could not be updated",
            )

    def delete_coupon(self, coupon_id: UUID):
        coupon = self.get_coupon(coupon_id)

        coupon.deleted_at = datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(coupon)

        return coupon

    def activate_coupon(self, coupon_id: UUID):
        coupon = self.get_coupon(coupon_id)

        now = datetime.now(timezone.utc)

        if now > coupon.valid_to:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Coupon is not valid anymore",
            )

        coupon.is_active = True

        self.db.commit()
        self.db.refresh(coupon)

        return coupon

    def deactivate_coupon(self, coupon_id: UUID):
        coupon = self.get_coupon(coupon_id)

        coupon.is_active = False

        self.db.commit()
        self.db.refresh(coupon)

        return coupon

    def validate(
        self,
        code: str,
        customer_id: uuid.UUID,
        *,
        for_update: bool = False,
    ) -> Coupon:
        """Return the coupon if the customer may use it right now.

        for_update=True when the result will be consumed (booking creation);
        False for the read-only preview endpoint.
        """
        coupon = self._get_by_code(code, for_update=for_update)
        now = datetime.now(timezone.utc)

        if not coupon.is_active:
            raise _bad_request("Invalid coupon code")
        if now < coupon.valid_from:
            raise _bad_request("Coupon is not valid yet")
        if now >= coupon.valid_to:
            raise _bad_request("Coupon has expired")
        if coupon.max_usage is not None and coupon.usage_count >= coupon.max_usage:
            raise _bad_request("Coupon usage limit has been reached")

        already_used = self.db.execute(
            select(func.count())
            .select_from(CouponUsage)
            .where(
                CouponUsage.coupon_id == coupon.id,
                CouponUsage.customer_id == customer_id,
            )
        ).scalar_one()
        if already_used:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already used this coupon",
            )

        return coupon

    def calculate_discount(self, coupon: Coupon, base_price: Decimal) -> Decimal:
        """Discount amount, never more than the base price."""
        value = Decimal(str(coupon.discount_value))

        if coupon.discount_type == DiscountType.percentage:
            discount = (base_price * value / Decimal("100")).quantize(
                CENT, rounding=ROUND_HALF_UP
            )
        else:
            discount = value

        return min(discount, base_price)

    def reserve(self, coupon: Coupon, booking: Booking) -> None:
        """Consume one usage. Caller must hold the row lock
        (validate(for_update=True)) and must have flushed the booking."""
        coupon.usage_count += 1
        self.db.add(
            CouponUsage(
                coupon_id=coupon.id,
                customer_id=booking.customer_id,
                booking_id=booking.id,
            )
        )

    def release(self, booking: Booking) -> None:
        """Give the usage back.

    Idempotent: only releases the coupon if a usage record exists.
    """
        if booking.coupon_id is None:
            return

        usage = self.db.execute(
        select(CouponUsage).where(
            CouponUsage.booking_id == booking.id
        )
    ).scalar_one_or_none()

        if usage is None:
            return

        self.db.delete(usage)

        self.db.execute(
        update(Coupon)
        .where(
            Coupon.id == booking.coupon_id,
            Coupon.usage_count > 0,
        )
        .values(
            usage_count=Coupon.usage_count - 1
        )
        .execution_options(synchronize_session=False)
    )
