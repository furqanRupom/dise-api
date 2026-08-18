import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class LocationCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=150,
        description="Location name",
    )

    city: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="City name",
    )

    address: str = Field(
        ...,
        min_length=1,
        description="Full address",
    )

    latitude: float | None = Field(
        default=None,
        ge=-90,
        le=90,
        description="Latitude must be between -90 and 90",
    )

    longitude: float | None = Field(
        default=None,
        ge=-180,
        le=180,
        description="Longitude must be between -180 and 180",
    )

    is_active: bool = Field(default=True)


class LocationUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )

    city: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    address: str | None = Field(
        default=None,
        min_length=1,
    )

    latitude: float | None = Field(
        default=None,
        ge=-90,
        le=90,
    )

    longitude: float | None = Field(
        default=None,
        ge=-180,
        le=180,
    )

    is_active: bool | None = Field(default=None)


class LocationResponse(BaseModel):
    id: uuid.UUID

    name: str = Field(
        ...,
        min_length=1,
        max_length=150,
    )

    city: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    address: str = Field(
        ...,
        min_length=1,
    )

    latitude: float | None = Field(
        default=None,
        ge=-90,
        le=90,
    )

    longitude: float | None = Field(
        default=None,
        ge=-180,
        le=180,
    )

    is_active: bool

    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    deleted_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
