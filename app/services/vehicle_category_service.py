import uuid
from collections.abc import Sequence
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import VehicleCategory
from app.schemas.vehicle_category import (
    VehicleCategoryCreate,
    VehicleCategoryUpdate,
)


class VehicleCategoryService:
    def __init__(self, db: Session):
        self.db = db

    def create_vehicle_category(
        self,
        payload: VehicleCategoryCreate,
    ) -> VehicleCategory:
        vehicle_category = VehicleCategory(**payload.model_dump())

        self.db.add(vehicle_category)
        self.db.commit()
        self.db.refresh(vehicle_category)

        return vehicle_category

    def get_vehicle_categories(self) -> Sequence[VehicleCategory]:
        result = self.db.execute(
            select(VehicleCategory).where(
                VehicleCategory.is_active.is_(True),
                VehicleCategory.deleted_at.is_(None),
            )
        )

        return result.scalars().all()

    def get_vehicle_category(
        self,
        vehicle_category_id: uuid.UUID,
    ) -> VehicleCategory:
        vehicle_category = self.db.execute(
            select(VehicleCategory).where(
                VehicleCategory.id == vehicle_category_id,
                VehicleCategory.is_active.is_(True),
                VehicleCategory.deleted_at.is_(None),
            )
        ).scalar_one_or_none()

        if not vehicle_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle category not found",
            )

        return vehicle_category

    def update_vehicle_category(
        self,
        vehicle_category_id: uuid.UUID,
        payload: VehicleCategoryUpdate,
    ) -> VehicleCategory:
        vehicle_category = self.db.execute(
            select(VehicleCategory).where(
                VehicleCategory.id == vehicle_category_id,
                VehicleCategory.deleted_at.is_(None),
            )
        ).scalar_one_or_none()

        if not vehicle_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle category not found",
            )

        update_data = payload.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(vehicle_category, key, value)

        self.db.commit()
        self.db.refresh(vehicle_category)

        return vehicle_category

    def delete_vehicle_category(
        self,
        vehicle_category_id: uuid.UUID,
    ) -> VehicleCategory:
        vehicle_category = self.db.execute(
            select(VehicleCategory).where(
                VehicleCategory.id == vehicle_category_id,
                VehicleCategory.deleted_at.is_(None),
            )
        ).scalar_one_or_none()

        if not vehicle_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle category not found",
            )

        vehicle_category.deleted_at = datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(vehicle_category)

        return vehicle_category

    def toggle_vehicle_category(
        self,
        vehicle_category_id: uuid.UUID,
    ) -> VehicleCategory:
        vehicle_category = self.db.execute(
            select(VehicleCategory).where(
                VehicleCategory.id == vehicle_category_id,
                VehicleCategory.deleted_at.is_(None),
            )
        ).scalar_one_or_none()

        if not vehicle_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle category not found",
            )

        vehicle_category.is_active = not vehicle_category.is_active

        self.db.commit()
        self.db.refresh(vehicle_category)

        return vehicle_category
