import uuid
from datetime import date

from sqlalchemy import Boolean, Date, Enum, Index, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.models.base import SoftDeleteMixin, TimestampMixin
from app.models.enums import LicenseStatus, UserRole


class User(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String, nullable=True)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), default=UserRole.customer, nullable=False, index=True
    )
    date_of_birth: Mapped[date | None] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    license_number: Mapped[str | None] = mapped_column(String(50))
    license_document_url: Mapped[str | None] = mapped_column(String(500))
    license_status: Mapped[LicenseStatus] = mapped_column(
        Enum(LicenseStatus), default=LicenseStatus.unsubmitted
    )
    stripe_customer_id: Mapped[str | None] = mapped_column(String(100), unique=True)

    bookings: Mapped[list["Booking"]] = relationship(
        back_populates="customer", foreign_keys="Booking.customer_id"
    )

    __table_args__ = (
        # Use a raw text() predicate rather than referencing
        # SoftDeleteMixin.deleted_at.is_(None): at class-body evaluation
        # time the class isn't mapped yet, so that attribute access
        # doesn't behave like a real column expression and previously
        # raised at import time. A partial index on a column name that
        # belongs to this same table is unambiguous as plain SQL text.
        Index(
            "idx_users_role",
            "role",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "idx_users_active",
            "is_active",
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )
