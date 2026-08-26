import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import Location, User, Vehicle, VehicleCategory
from app.schemas.vehicle import VehicleCreate, VehicleUpdate


class VehicleService:
    def __init__(self, db: Session):
        self.db = db

    def get_vehicles(self) -> list[Vehicle]:
        return (
            self.db.query(Vehicle)
            .filter(Vehicle.deleted_at.is_(None))
            .order_by(Vehicle.created_at)
            .all()
        )

    def get_vehicle(self, vehicle_id: uuid.UUID) -> Vehicle:
        vehicle = (
            self.db.query(Vehicle)
            .filter(
                Vehicle.id == vehicle_id,
                Vehicle.deleted_at.is_(None),
            )
            .first()
        )

        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found",
            )

        return vehicle

    def create_vehicle(self, payload: VehicleCreate) -> Vehicle:
        # Check location
        location = (
            self.db.query(Location)
            .filter(
                Location.id == payload.location_id,
                Location.deleted_at.is_(None),
                Location.is_active.is_(True),
            )
            .first()
        )

        if not location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Location not found",
            )

        # Check vehicle category
        vehicle_category = (
            self.db.query(VehicleCategory)
            .filter(
                VehicleCategory.id == payload.category_id,
                VehicleCategory.deleted_at.is_(None),
                VehicleCategory.is_active.is_(True),
            )
            .first()
        )

        if not vehicle_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle category not found",
            )

        # Check owner only when owner_id is provided
        if payload.owner_id is not None:
            owner = (
                self.db.query(User)
                .filter(
                    User.id == payload.owner_id,
                    User.deleted_at.is_(None),
                    User.is_active.is_(True),
                )
                .first()
            )

            if not owner:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Owner not found",
                )

        vehicle = Vehicle(**payload.model_dump())

        try:
            self.db.add(vehicle)
            self.db.commit()
            self.db.refresh(vehicle)
        except SQLAlchemyError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create vehicle",
            )

        return vehicle

    def update_vehicle(
        self,
        vehicle_id: uuid.UUID,
        payload: VehicleUpdate,
    ) -> Vehicle:
        vehicle = (
            self.db.query(Vehicle)
            .filter(
                Vehicle.id == vehicle_id,
                Vehicle.deleted_at.is_(None),
            )
            .first()
        )

        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found",
            )

        update_data = payload.model_dump(exclude_unset=True)

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update",
            )

        # Validate location if it is being changed
        if "location_id" in update_data:
            location = (
                self.db.query(Location)
                .filter(
                    Location.id == update_data["location_id"],
                    Location.deleted_at.is_(None),
                    Location.is_active.is_(True),
                )
                .first()
            )

            if not location:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Location not found",
                )

        # Validate category if it is being changed
        if "category_id" in update_data:
            vehicle_category = (
                self.db.query(VehicleCategory)
                .filter(
                    VehicleCategory.id == update_data["category_id"],
                    VehicleCategory.deleted_at.is_(None),
                    VehicleCategory.is_active.is_(True),
                )
                .first()
            )

            if not vehicle_category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Vehicle category not found",
                )

        # Validate owner if it is being changed
        if "owner_id" in update_data and update_data["owner_id"] is not None:
            owner = (
                self.db.query(User)
                .filter(
                    User.id == update_data["owner_id"],
                    User.deleted_at.is_(None),
                    User.is_active.is_(True),
                )
                .first()
            )

            if not owner:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Owner not found",
                )

        try:
            for field, value in update_data.items():
                setattr(vehicle, field, value)

            self.db.commit()
            self.db.refresh(vehicle)
        except SQLAlchemyError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update vehicle",
            )

        return vehicle

    def delete_vehicle(self, vehicle_id: uuid.UUID) -> None:
        vehicle = (
            self.db.query(Vehicle)
            .filter(
                Vehicle.id == vehicle_id,
                Vehicle.deleted_at.is_(None),
            )
            .first()
        )

        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found",
            )

        try:
            vehicle.deleted_at = datetime.now(timezone.utc)
            self.db.commit()
        except SQLAlchemyError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete vehicle",
            )
