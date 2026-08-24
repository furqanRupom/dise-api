import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin
from app.db import get_db
from app.models import User
from app.schemas.vehicle_category import (
    VehicleCategoryCreate,
    VehicleCategoryResponse,
    VehicleCategoryUpdate,
)
from app.services.vehicle_category_service import VehicleCategoryService

router = APIRouter(
    prefix="/vehicle-categories",
    tags=["vehicle-categories"],
)


@router.get("/", response_model=list[VehicleCategoryResponse])
async def get_vehicle_categories(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_admin)],
):
    vehicle_category = VehicleCategoryService(db)
    return vehicle_category.get_vehicle_categories()


@router.post("/", response_model=VehicleCategoryResponse)
async def create_vehicle_category(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_admin)],
    payload: VehicleCategoryCreate,
):
    vehicle_category = VehicleCategoryService(db)
    return vehicle_category.create_vehicle_category(payload)


@router.get("/{vehicle_category_id}", response_model=VehicleCategoryResponse)
async def get_vehicle_category(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_admin)],
    vehicle_category_id: uuid.UUID,
):
    vehicle_category = VehicleCategoryService(db)
    return vehicle_category.get_vehicle_category(vehicle_category_id)


@router.put("/{vehicle_category_id}", response_model=VehicleCategoryResponse)
async def update_vehicle_category(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_admin)],
    vehicle_category_id: uuid.UUID,
    payload: VehicleCategoryUpdate,
):
    vehicle_category = VehicleCategoryService(db)
    return vehicle_category.update_vehicle_category(vehicle_category_id, payload)


@router.delete("/{vehicle_category_id}", response_model=VehicleCategoryResponse)
async def delete_vehicle_category(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_admin)],
    vehicle_category_id: uuid.UUID,
):
    vehicle_category = VehicleCategoryService(db)
    return vehicle_category.delete_vehicle_category(vehicle_category_id)


@router.patch("/{vehicle_category_id}", response_model=VehicleCategoryResponse)
async def toggle_vehicle_category(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_admin)],
    vehicle_category_id: uuid.UUID,
):
    vehicle_category = VehicleCategoryService(db)
    return vehicle_category.toggle_vehicle_category(vehicle_category_id)
