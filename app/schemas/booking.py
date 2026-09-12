"""all validation schemas of booking model"""

import uuid
from datetime import date, datetime
from decimal import Decimal

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
