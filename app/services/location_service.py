import uuid

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Location
from app.schemas.location import LocationCreate, LocationUpdate
from app.schemas.response import SendRespose


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
        return SendRespose(
            success=True,
            message="Location created successfully",
            data=location,
        )

    """
    Updates an existing location in the database.
    """

    def update_location(
        self,
        location_id: uuid.UUID,
        payload: LocationUpdate,
    ):
        location = self.db.query(Location).filter(Location.id == location_id).first()
        if location:
            for key, value in payload.model_dump().items():
                setattr(location, key, value)
            self.db.commit()
            return SendRespose(
                success=True,
                message="Location updated successfully",
                data=location,
            )
        raise HTTPException(status_code=404, detail="Location not found")

    """
    Retrieves a location by its ID.
    """

    def get_location(
        self,
    ):
        locations = self.db.query(Location).all()
        return SendRespose(
            success=True,
            message="Locations retrieved successfully",
            data=locations,
        )

    """
    Retrieves a location by its ID.
    """

    def get_location_by_id(
        self,
        location_id: uuid.UUID,
    ):
        location = self.db.query(Location).filter(Location.id == location_id).first()
        return SendRespose(
            success=True,
            message="Location retrieved successfully",
            data=location,
        )

    """
    Deletes a location by its ID.
    """

    def delete_location(
        self,
        location_id: uuid.UUID,
    ):
        location = self.db.query(Location).filter(Location.id == location_id).first()
        if location:
            self.db.delete(location)
            self.db.commit()
            return SendRespose(
                success=True,
                message="Location deleted successfully",
                data=None,
            )
        return SendRespose(
            success=False,
            message="Location not found",
            data=None,
        )
