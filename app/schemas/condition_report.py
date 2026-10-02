import uuid
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from app.models.enums import ReportType

imageUrl = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)
]


class CondtionReportCreate(BaseModel):
    """
    Payload for both check-in (pick up) and check-up (return)
    The Report Type is decided by endpoint never by client
    """

    odometer_km: int = Field(ge=0)
    fuel_level_pct: int = Field(ge=0, le=100)
    notes: str | None = Field(default=None, max_length=2000)
    image_urls: list[str] = Field(default_factory=list, max_length=20)


class ConditionReportImageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    image_url: str
    created_at: datetime


class ConditionReportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    booking_id: uuid.UUID
    type: ReportType
    odometer_km: int
    fuel_level_pct: int
    notes: str | None
    recorded_by: uuid.UUID
    created_at: datetime
    images: list[ConditionReportImageRead]
