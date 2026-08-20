from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Coupon
from app.schemas.coupon import CouponCreate, CouponUpdate


class CouponService:
    def __init__(self, db: Session):
        self.db = db

    def create_coupon(self, payload: CouponCreate):
        code = payload.code.strip().upper()

        existing_coupon = self.db.query(Coupon).filter_by(code=code).first()

        if existing_coupon:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Coupon already exists"
            )

        if payload.valid_to <= payload.valid_from:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="valid_to must be after valid_from",
            )

        coupon = Coupon(**payload.model_dump(exclude={"code"}))

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

    def get_coupon(self, coupon_id: str):
        coupon = self.db.query(Coupon).filter_by(id=coupon_id).first()
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

            existing_coupon = (
                self.db.query(Coupon)
                .filter(
                    Coupon.code == code,
                    Coupon.id != coupon_id,
                )
                .first()
            )

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
