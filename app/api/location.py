from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.dependencies import require_permission
from app.core.rbac import Permission
from app.models import User

router = APIRouter(
    prefix="/v1/location",
    tags=["location"],
)


@router.get("/")
async def get_location(
    current_user: Annotated[
        User, Depends(require_permission(Permission.LOCATIONS_READ))
    ],
):
    pass
