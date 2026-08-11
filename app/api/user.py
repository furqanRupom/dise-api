from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.response import SendRespose
from app.schemas.user import UserUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/v1/user", tags=["user"])


@router.patch("/{user_id}")
async def update_user(
    user_id: str, payload: UserUpdate, db: Annotated[Session, Depends(get_db)]
):
    user_service = UserService(db)
    result = user_service.update_user(user_id, payload)
    return SendRespose(
        success=True,
        message="User updated successfully",
        data=result,
    )
