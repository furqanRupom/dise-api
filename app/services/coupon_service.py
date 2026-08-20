from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Coupon
from app.schemas.coupon import CouponCreate


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
