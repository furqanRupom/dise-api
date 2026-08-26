import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_current_active_user,
    require_admin_or_staff,
)
from app.db import get_db
from app.models import User

router = APIRouter(
    prefix="/vehicles",
    tags=["vehicles"],
)


@router.get("/")
async def get_vehicles(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return {"message": "vehicles"}


@router.post("/")
async def create_vehicle(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin_or_staff)],
):
    return {"message": "vehicle created"}


@router.get("/{vehicle_id}")
async def get_vehicle(
    vehicle_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return {"message": f"vehicle {vehicle_id}"}


@router.put("/{vehicle_id}")
async def update_vehicle(
    vehicle_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin_or_staff)],
):
    return {"message": f"vehicle {vehicle_id} updated"}


@router.delete("/{vehicle_id}")
async def delete_vehicle(
    vehicle_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin_or_staff)],
):
    return {"message": f"vehicle {vehicle_id} deleted"}
