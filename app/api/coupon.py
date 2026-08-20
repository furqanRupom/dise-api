from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin
from app.db import get_db
from app.models import User

router = APIRouter(
    prefix="/v1/coupon",
    tags=["coupon"],
)


@router.get("/")
async def get_coupons(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin)],
):
    return {"coupons": []}


@router.get("/{coupon_id}")
async def get_coupon(
    coupon_id: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin)],
):
    return {"coupon": {"id": coupon_id}}


@router.post("/")
async def create_coupon(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin)],
):
    return {"message": "coupon created"}


@router.put("/{coupon_id}")
async def update_coupon(
    coupon_id: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin)],
):
    return {"message": "coupon updated"}


@router.delete("/{coupon_id}")
async def delete_coupon(
    coupon_id: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin)],
):
    return {"message": "coupon deleted"}
