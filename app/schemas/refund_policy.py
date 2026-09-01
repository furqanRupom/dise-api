import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class RefundPolicyTierBase(BaseModel):
    hours_before_pickup: int = Field(
        ..., ge=0, description="Cancel at least this many hours before pickup"
    )
    refund_percentage: Decimal = Field(..., ge=0, le=100)
    is_active: bool = True


class RefundPolicyTierCreate(RefundPolicyTierBase):
    pass


class RefundPolicyTierUpdate(BaseModel):
    hours_before_pickup: int | None = Field(None, ge=0)
    refund_percentage: Decimal | None = Field(None, ge=0, le=100)
    is_active: bool | None = None


class RefundPolicyTierOut(RefundPolicyTierBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    deleted_at: datetime
    created_at: datetime
    updated_at: datetime


class RefundQuoteRequest(BaseModel):
    hours_until_pickup: int = Field(..., ge=0)


class RefundQuoteResponse(BaseModel):
    hours_until_pickup: int
    refund_percentage: Decimal
    matched_tier_id: uuid.UUID | None
