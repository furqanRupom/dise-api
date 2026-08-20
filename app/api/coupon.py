from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin
from app.db import get_db
from app.models import User
from app.schemas.coupon import CouponCreate, CouponUpdate
from app.services.coupon_service import CouponService

router = APIRouter(
    prefix="/v1/coupon",
    tags=["coupon"],
)


@router.get("/")
async def get_coupons(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin)],
):
    coupon = CouponService(db)
    return coupon.get_coupons()


@router.get("/{coupon_id}")
async def get_coupon(
    coupon_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin)],
):
    coupon = CouponService(db)
    return coupon.get_coupon(coupon_id)


@router.post("/")
async def create_coupon(
    payload: CouponCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin)],
):
    coupon = CouponService(db)
    return coupon.create_coupon(payload)


@router.put("/{coupon_id}")
async def update_coupon(
    coupon_id: UUID,
    payload: CouponUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin)],
):
    coupon = CouponService(db)
    return coupon.update_coupon(coupon_id, payload)


@router.delete("/{coupon_id}")
async def delete_coupon(
    coupon_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin)],
):
    coupon = CouponService(db)
    return coupon.delete_coupon(coupon_id)


@router.patch("/{coupon_id}/activate")
async def activate_coupon(
    coupon_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin)],
):
    coupon = CouponService(db)
    return coupon.activate_coupon(coupon_id)


@router.patch("/{coupon_id}/deactivate")
async def deactivate_coupon(
    coupon_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin)],
):
    coupon = CouponService(db)
    return coupon.deactivate_coupon(coupon_id)
