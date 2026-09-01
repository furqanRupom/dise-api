import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Location
from app.schemas.location import LocationCreate, LocationUpdate


class LocationService:
    def __init__(self, db: Session):
        self.db = db

    """
    Creates a new location in the database.
    """

    def create_location(
        self,
        payload: LocationCreate,
    ):
        location = Location(**payload.model_dump())
        self.db.add(location)
        self.db.commit()
        self.db.refresh(location)
        return location

    """
    Updates an existing location in the database.
    """

    def update_location(
        self,
        location_id: uuid.UUID,
        payload: LocationUpdate,
    ):
        location = (
            self.db.query(Location)
            .filter(
                Location.id == location_id,
                Location.deleted_at.is_(None),
                Location.is_active.is_(True),
            )
            .first()
        )
        if not location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Location not found"
            )

        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(location, key, value)
        self.db.commit()
        self.db.refresh(location)
        return location

    """
    Retrieves a location by its ID.
    """

    def get_location(
        self,
    ):
        locations = (
            self.db.query(Location)
            .filter(Location.deleted_at._is(None))
            .order_by(Location.created_at.desc())
            .all()
        )
        return locations

    """
    Retrieves a location by its ID.
    """

    def get_location_by_id(
        self,
        location_id: uuid.UUID,
    ):
        location = (
            self.db.query(Location)
            .filter(Location.id == location_id, Location.deleted_at.is_(None))
            .first()
        )
        return location

    def delete_location(
        self,
        location_id: uuid.UUID,
    ):
        """
        Deletes a location by its ID.
        """
        location = (
            self.db.query(Location)
            .filter(Location.id == location_id, Location.deleted_at.is_(None))
            .first()
        )
        if location:
            location.deleted_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(location)
            return location
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Location not found"
        )
