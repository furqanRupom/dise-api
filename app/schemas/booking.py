"""all validation schemas of booking model"""

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.enums import BookingStatus


class BookingCreate(BaseModel):
    vehicle_id: uuid.UUID
    pickup_location_id: uuid.UUID
    dropoff_location_id: uuid.UUID
    start_date: date
    end_date: date
    coupon_code: str | None = Field(default=None, max_length=30)

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date <= self.start_date:
            raise ValueError("End date must be after start date")

        return self


class BookingPriceResponse(BaseModel):
    base_price: Decimal
    discount_amount: Decimal
    total_price: Decimal
    currency: str
    duration_days: int


class BookingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID

    customer_id: uuid.UUID
    vehicle_id: uuid.UUID

    pickup_location_id: uuid.UUID
    dropoff_location_id: uuid.UUID

    start_date: date
    end_date: date

    status: BookingStatus

    base_price: Decimal
    discount_amount: Decimal
    total_price: Decimal
    currency: str

    coupon_id: uuid.UUID | None

    deposit_hold_amount: Decimal

    approval_deadline: datetime | None

    created_by: uuid.UUID

    created_at: datetime
    updated_at: datetime


class BookingListParams(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)

    status: BookingStatus | None = None

    vehicle_id: uuid.UUID | None = None
    customer_id: uuid.UUID | None = None

    pickup_location_id: uuid.UUID | None = None
    dropoff_location_id: uuid.UUID | None = None

    start_date_from: date | None = None
    start_date_to: date | None = None

    end_date_from: date | None = None
    end_date_to: date | None = None

    price_min: Decimal | None = Field(default=None, ge=0)
    price_max: Decimal | None = Field(default=None, ge=0)

    sort_by: Literal[
        "created_at",
        "updated_at",
        "start_date",
        "end_date",
        "total_price",
        "status",
    ] = "created_at"

    sort_order: Literal["asc", "desc"] = "desc"


class BookingListResponse(BaseModel):
    page: int
    limit: int

    total: int
    total_pages: int

    has_next: bool
    has_previous: bool

    data: list[BookingResponse]
