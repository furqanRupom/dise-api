from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Coupon
from app.schemas.coupon import CouponCreate, CouponUpdate


class CouponService:
    def __init__(self, db: Session):
        self.db = db

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
