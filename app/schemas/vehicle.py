import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ---------- VehicleImage ----------
class VehicleImageCreate(BaseModel):
    image_url: str = Field(
        ...,
        max_length=500,
        description="URL of the vehicle image",
    )
    sort_order: int = Field(
        default=0,
        ge=0,
        description="Display order of the image",
    )


class VehicleImageUpdate(BaseModel):
    image_url: str | None = Field(
        default=None,
        max_length=500,
        description="URL of the vehicle image",
    )
    sort_order: int | None = Field(
        default=None,
        ge=0,
        description="Display order of the image",
    )


class VehicleImageResponse(BaseModel):
    id: uuid.UUID
    vehicle_id: uuid.UUID
    image_url: str = Field(..., max_length=500)
    sort_order: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------- Vehicle ----------
class VehicleCreate(BaseModel):
    category_id: uuid.UUID = Field(..., description="Vehicle category ID")
    location_id: uuid.UUID = Field(..., description="Location ID")
    owner_id: uuid.UUID | None = Field(default=None, description="Owner ID (optional)")

    make: str = Field(..., min_length=1, max_length=100, description="Vehicle make")
    model: str = Field(..., min_length=1, max_length=100, description="Vehicle model")
    year: int = Field(..., ge=1990, description="Manufacturing year")
    license_plate: str = Field(
        ..., min_length=1, max_length=20, description="License plate number"
    )

    transmission: str = Field(..., description="Transmission type (enum value)")
    fuel_type: str = Field(..., description="Fuel type (enum value)")

    seats: int = Field(..., gt=0, description="Number of seats")
    daily_rate: float = Field(..., ge=0, description="Daily rental rate")
    currency: str = Field(
        default="BDT", min_length=3, max_length=3, description="Currency code"
    )
    deposit_amount: float = Field(
        default=0, ge=0, description="Security deposit amount"
    )

    requires_approval: bool = Field(
        default=False, description="Whether vehicle requires approval"
    )
    status: str = Field(default="available", description="Vehicle status (enum value)")
    odometer_km: int = Field(default=0, ge=0, description="Odometer reading in km")


class VehicleUpdate(BaseModel):
    category_id: uuid.UUID | None = Field(
        default=None, description="Vehicle category ID"
    )
    location_id: uuid.UUID | None = Field(default=None, description="Location ID")
    owner_id: uuid.UUID | None = Field(default=None, description="Owner ID (optional)")

    make: str | None = Field(
        default=None, min_length=1, max_length=100, description="Vehicle make"
    )
    model: str | None = Field(
        default=None, min_length=1, max_length=100, description="Vehicle model"
    )
    year: int | None = Field(default=None, ge=1990, description="Manufacturing year")
    license_plate: str | None = Field(
        default=None, min_length=1, max_length=20, description="License plate number"
    )

    transmission: str | None = Field(
        default=None, description="Transmission type (enum value)"
    )
    fuel_type: str | None = Field(default=None, description="Fuel type (enum value)")

    seats: int | None = Field(default=None, gt=0, description="Number of seats")
    daily_rate: float | None = Field(
        default=None, ge=0, description="Daily rental rate"
    )
    currency: str | None = Field(
        default=None, min_length=3, max_length=3, description="Currency code"
    )
    deposit_amount: float | None = Field(
        default=None, ge=0, description="Security deposit amount"
    )

    requires_approval: bool | None = Field(
        default=None, description="Whether vehicle requires approval"
    )
    status: str | None = Field(default=None, description="Vehicle status (enum value)")
    odometer_km: int | None = Field(
        default=None, ge=0, description="Odometer reading in km"
    )


class VehicleResponse(BaseModel):
    id: uuid.UUID
    category_id: uuid.UUID
    location_id: uuid.UUID
    owner_id: uuid.UUID | None

    make: str
    model: str
    year: int
    license_plate: str
    transmission: str
    fuel_type: str
    seats: int
    daily_rate: float
    currency: str
    deposit_amount: float
    requires_approval: bool
    status: str
    odometer_km: int

    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

    # Optional nested responses (if you eager-load relationships)
    # category: VehicleCategoryResponse | None = None
    # images: list[VehicleImageResponse] = []

    model_config = ConfigDict(from_attributes=True)
