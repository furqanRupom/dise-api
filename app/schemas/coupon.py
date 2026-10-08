from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models import DiscountType
from app.models.enums import DiscountType


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


class CouponValidateRequest(BaseModel):
    code: str = Field(min_length=1, max_length=30)
    base_price: Decimal = Field(gt=0)


class CouponValidateResponse(BaseModel):
    code: str
    discount_type: DiscountType
    discount_value: Decimal
    base_price: Decimal
    discount_amount: Decimal
    final_price: Decimal
