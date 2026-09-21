import uuid
from collections.abc import Sequence
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Location
from app.schemas.location import LocationCreate, LocationUpdate


class LocationService:
    def __init__(self, db: Session):
        self.db = db

    def create_location(
        self,
        payload: LocationCreate,
    ) -> Location:
        location = Location(**payload.model_dump())

        self.db.add(location)
        self.db.commit()
        self.db.refresh(location)

        return location

    def update_location(
        self,
        location_id: uuid.UUID,
        payload: LocationUpdate,
    ) -> Location:
        location = self.db.execute(
            select(Location).where(
                Location.id == location_id,
                Location.deleted_at.is_(None),
                Location.is_active.is_(True),
            )
        ).scalar_one_or_none()

        if not location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Location not found",
            )

        update_data = payload.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(location, key, value)

        self.db.commit()
        self.db.refresh(location)

        return location

    def get_locations(self) -> Sequence[Location]:
        result = self.db.execute(
            select(Location)
            .where(
                Location.deleted_at.is_(None),
                Location.is_active.is_(True),
            )
            .order_by(Location.created_at)
        )

        return result.scalars().all()

    def get_location_by_id(
        self,
        location_id: uuid.UUID,
    ) -> Location | None:
        return self.db.execute(
            select(Location).where(
                Location.id == location_id,
                Location.deleted_at.is_(None),
            )
        ).scalar_one_or_none()

    def delete_location(
        self,
        location_id: uuid.UUID,
    ) -> Location:
        location = self.db.execute(
            select(Location).where(
                Location.id == location_id,
                Location.deleted_at.is_(None),
            )
        ).scalar_one_or_none()

        if not location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Location not found",
            )

        location.deleted_at = datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(location)

        return location
