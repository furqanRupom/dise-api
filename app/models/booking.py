import uuid
from datetime import date, datetime

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    String,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import ExcludeConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.models.base import SoftDeleteMixin, TimestampMixin
from app.models.enums import BookingStatus
from app.models.user import User
from app.models.vehicle import Vehicle


class Booking(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "bookings"
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    vehicle_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("vehicles.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    pickup_location_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("locations.id", ondelete="RESTRICT"), nullable=False
    )
    dropoff_location_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("locations.id", ondelete="RESTRICT"), nullable=False
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[BookingStatus] = mapped_column(
        Enum(BookingStatus),
        default=BookingStatus.pending_payment,
        nullable=False,
        index=True,
    )
    base_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    discount_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    total_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="BDT", nullable=False)
    coupon_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("coupons.id", ondelete="SET NULL")
    )
    deposit_hold_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    approval_deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )

    # lazy="selectin": these two are needed on almost every booking read
    # (list view, detail view, receipts...) so we eager-load them by
    # default in exactly 2 extra queries total instead of 1-per-row (N+1).
    customer: Mapped[User] = relationship(
        foreign_keys=[customer_id], back_populates="bookings", lazy="selectin"
    )
    vehicle: Mapped[Vehicle] = relationship(lazy="selectin")

    status_history: Mapped[list["BookingStatusHistory"]] = relationship(
        back_populates="booking", cascade="all, delete-orphan"
    )
    # Not eager-loaded by default (not needed on every read) — use
    # selectinload(Booking.payments) / .review / .condition_reports at the
    # query site when you actually need them, instead of a fresh query per row.
    payments: Mapped[list["Payment"]] = relationship(
        back_populates="booking", cascade="all, delete-orphan"
    )
    review: Mapped["Review | None"] = relationship(
        back_populates="booking", uselist=False, cascade="all, delete-orphan"
    )
    condition_reports: Mapped[list["ConditionReport"]] = relationship(
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("end_date >= start_date", name="ck_bookings_dates"),
        CheckConstraint("base_price >= 0", name="ck_bookings_base_price"),
        CheckConstraint("total_price >= 0", name="ck_bookings_total_price"),
        CheckConstraint("discount_amount >= 0", name="ck_bookings_discount_amount"),
        CheckConstraint(
            "deposit_hold_amount >= 0", name="ck_bookings_deposit_hold_amount"
        ),
        Index("idx_bookings_vehicle_dates", "vehicle_id", "start_date", "end_date"),
        # DB-level double-booking guard - requires the btree_gist extension:
        #   CREATE EXTENSION IF NOT EXISTS btree_gist;
        # `deleted_at IS NULL` added: without it, a soft-deleted confirmed/
        # active booking would permanently block that vehicle/date range.
        #
        # Both the daterange(...) expression and the where clause must be
        # wrapped in text() - a bare string is interpreted by SQLAlchemy as
        # a *column name* to look up on the table, not a raw SQL expression,
        # which is what caused the ConstraintColumnNotFoundError.
        ExcludeConstraint(
            ("vehicle_id", "="),
            (text("daterange(start_date, end_date, '[]')"), "&&"),
            where=text("status IN ('confirmed','active') AND deleted_at IS NULL"),
            name="excl_no_overlapping_confirmed_bookings",
        ),
    )


class BookingStatusHistory(Base):
    __tablename__ = "booking_status_history"
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
    )
    booking_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False, index=True
    )
    from_status: Mapped[str | None] = mapped_column(String(30))
    to_status: Mapped[str] = mapped_column(String(30), nullable=False)
    changed_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )
    reason: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    booking: Mapped["Booking"] = relationship(back_populates="status_history")
