from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user
from app.db import get_db
from app.models import User
from app.schemas.user import ChangePassword, UserUpdate
from app.services.user_service import UserService

router = APIRouter(
    prefix="/v1/user",
    tags=["user"],
)


@router.patch("/profile")
async def update_user(
    payload: UserUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[
        User,
        Depends(get_current_active_user),
    ],
):
    user_service = UserService(db)

    return await user_service.update_user(
        current_user.id,
        payload,
    )


@router.patch("/change-password")
async def change_password(
    payload: ChangePassword,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[
        User,
        Depends(get_current_active_user),
    ],
):
    user_service = UserService(db)

    return await user_service.change_password(
        current_user.id,
        payload,
    )


@router.delete("/delete-account")
async def delete_account(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[
        User,
        Depends(get_current_active_user),
    ],
):
    user_service = UserService(db)

    return await user_service.delete_account(
        current_user.id,
    )
