import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.models.base import TimestampMixin
from app.models.enums import PaymentStatus, PaymentType


class Payment(Base, TimestampMixin):
    __tablename__ = "payments"
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
    )
    booking_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("bookings.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    type: Mapped[PaymentType] = mapped_column(Enum(PaymentType), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus), default=PaymentStatus.pending, nullable=False, index=True
    )
    stripe_payment_intent_id: Mapped[str | None] = mapped_column(
        String(100), unique=True
    )
    idempotency_key: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False
    )

    booking: Mapped["Booking"] = relationship(back_populates="payments")

    __table_args__ = (CheckConstraint("amount >= 0", name="ck_payments_amount"),)


class ProcessedWebhookEvent(Base):
    """One row per Stripe event we have fully handled (dedupe on redelivery).

    The row is inserted in the SAME transaction as the handler's changes, so a
    handler failure rolls the row back and Stripe's retry reprocesses the event.
    """

    __tablename__ = "processed_webhook_events"

    event_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    processed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
