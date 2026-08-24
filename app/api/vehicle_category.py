import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class VehicleCategoryCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Vehicle category name",
    )

    description: str | None = Field(
        default=None,
        max_length=500,
        description="Vehicle category description",
    )

    is_active: bool = Field(default=True)


class VehicleCategoryUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Vehicle category name",
    )

    description: str | None = Field(
        default=None,
        max_length=500,
        description="Vehicle category description",
    )

    is_active: bool | None = Field(default=None)


class VehicleCategoryResponse(BaseModel):
    id: uuid.UUID

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    description: str | None = Field(default=None)

    is_active: bool

    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
