import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin
from app.db import get_db
from app.models import User
from app.schemas.location import LocationCreate, LocationResponse, LocationUpdate
from app.services.location_service import LocationService

router = APIRouter(
    prefix="/v1/location",
    tags=["location"],
)


@router.post("/", response_model=LocationResponse)
async def create_location(
    payload: LocationCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin)],
):
    location = LocationService(db)
    return location.create_location(payload)


@router.put("/{location_id}", response_model=LocationResponse)
async def update_location(
    location_id: uuid.UUID,
    payload: LocationUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin)],
):
    location = LocationService(db)
    return location.update_location(location_id, payload)


@router.get("/", response_model=list[LocationResponse])
async def get_location(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin)],
):
    location = LocationService(db)
    return location.get_location()


@router.get("/{location_id}", response_model=LocationResponse)
async def get_location_by_id(
    location_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin)],
):
    location = LocationService(db)
    return location.get_location_by_id(location_id)


@router.delete("/{location_id}", response_model=LocationResponse)
async def delete_location(
    location_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin)],
):
    location = LocationService(db)
    return location.delete_location(location_id)
