import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, Response, UploadFile, status
from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_current_active_user,
    require_admin_or_staff,
)
from app.db import get_db
from app.models import User
from app.schemas.vehicle import (
    VehicleCreate,
    VehicleResponse,
    VehicleUpdate,
)
from app.services.vehicle_service import VehicleService

router = APIRouter(
    prefix="/vehicles",
    tags=["vehicles"],
)


@router.get(
    "/",
    response_model=list[VehicleResponse],
)
def get_vehicles(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    vehicle_service = VehicleService(db)

    return vehicle_service.get_vehicles()


@router.post(
    "/",
    response_model=VehicleResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_vehicle(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin_or_staff)],
    payload: VehicleCreate,
):
    vehicle_service = VehicleService(db)

    return vehicle_service.create_vehicle(payload)


@router.get(
    "/{vehicle_id}",
    response_model=VehicleResponse,
)
def get_vehicle(
    vehicle_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    vehicle_service = VehicleService(db)

    return vehicle_service.get_vehicle(vehicle_id)


@router.put(
    "/{vehicle_id}",
    response_model=VehicleResponse,
)
def update_vehicle(
    vehicle_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin_or_staff)],
    payload: VehicleUpdate,
):
    vehicle_service = VehicleService(db)

    return vehicle_service.update_vehicle(
        vehicle_id,
        payload,
    )


@router.delete(
    "/{vehicle_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_vehicle(
    vehicle_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin_or_staff)],
):
    vehicle_service = VehicleService(db)

    vehicle_service.delete_vehicle(vehicle_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{vehicle_id}/images",
)
async def update_vehicle_image(
    vehicle_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin_or_staff)],
    file: Annotated[UploadFile, File(...)],
):
    vehicle_service = VehicleService(db)
    await vehicle_service.update_vehicle_image(vehicle_id, file)
    return {
        "message": "Image updated successfully",
    }
