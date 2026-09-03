import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user, require_admin
from app.db import get_db
from app.models import User
from app.schemas.user import (
    LicenseDecisionRequest,
    LicenseStatusResponse,
    LicenseSubmitRequest,
    UserAvatarUpdate,
    UserUpdate,
)
from app.services.user_service import UserService

router = APIRouter(
    prefix="/v1/user",
    tags=["user"],
)


@router.patch("/profile", response_model=UserUpdate)
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


@router.patch("/avatar", response_model=UserAvatarUpdate)
async def update_avatar(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[
        User,
        Depends(get_current_active_user),
    ],
    file: Annotated[UploadFile, File(...)],
):
    user_service = UserService(db)

    return await user_service.update_avatar(
        current_user.id,
        file,
    )


@router.delete("/delete-account", response_model=None)
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


@router.post("/me/license", response_model=None)
async def submit_my_license(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    payload: LicenseSubmitRequest,
    file: Annotated[UploadFile, File(...)],
):
    user_service = UserService(db)
    return await user_service.submit_license(current_user.id, payload, file)


@router.get("/admin/licenses", response_model=list[LicenseStatusResponse])
async def list_licenses(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin)],
):
    user_service = UserService(db)
    return await user_service.list_pending_licences()


@router.put("/admin/license/{user_id}", response_model=None)
async def decide_license(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin)],
    payload: LicenseDecisionRequest,
    user_id: uuid.UUID,
):
    pass
