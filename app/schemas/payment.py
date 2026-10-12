import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import PaymentStatus, PaymentType


class PayResponse(BaseModel):
    """Returned by POST /bookings/{id}/pay and /deposit.

    client_secret is None when nothing needs to be paid (100% coupon);
    in that case confirmed=True. Otherwise the frontend confirms the
    PaymentIntent with Stripe.js and the webhook confirms the booking.
    """

    client_secret: str | None
    payment_id: uuid.UUID | None
    confirmed: bool = False


class PaymentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    booking_id: uuid.UUID
    type: PaymentType
    amount: Decimal
    currency: str
    status: PaymentStatus
    failure_reason: str | None = None
    note: str | None = None
    authorization_expires_at: datetime | None = None
    created_at: datetime


class PaymentListResponse(BaseModel):
    items: list[PaymentOut]
    total: int
    page: int
    limit: int


class DepositCaptureRequest(BaseModel):
    amount: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    reason: str = Field(min_length=3, max_length=255)
