from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models import DiscountType


class CouponCreate(BaseModel):
    code: str
    discount_type: DiscountType
    discount_value: Decimal
    max_usage: int | None = None
    valid_from: datetime
    valid_to: datetime
    is_active: bool = True


class CouponUpdate(BaseModel):
    code: str | None = None
    discount_type: DiscountType | None = None
    discount_value: Decimal | None = None
    max_usage: int | None = None
    valid_from: datetime | None = None
    valid_to: datetime | None = None
    is_active: bool | None = None


class CouponResponse(BaseModel):
    id: UUID
    code: str
    discount_type: DiscountType
    discount_value: Decimal
    max_usage: int | None
    usage_count: int
    valid_from: datetime
    valid_to: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
