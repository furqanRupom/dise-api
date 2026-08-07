import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    SmallInteger,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin, TimestampMixin
from app.models.enums import FuelType, TransmissionType, VehicleStatus


class VehicleCategory(Base, TimestampMixin):
    __tablename__ = "vehicle_categories"
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
    )
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(500))
    vehicles: Mapped[list["Vehicle"]] = relationship(back_populates="category")


class Vehicle(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "vehicles"
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("vehicle_categories.id", ondelete="RESTRICT"), nullable=False
    )
    location_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("locations.id", ondelete="RESTRICT"), nullable=False
    )
    # Future-proof: owner_id for marketplace hybrid model
    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    make: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    year: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    license_plate: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    transmission: Mapped[TransmissionType] = mapped_column(
        Enum(TransmissionType), nullable=False
    )
    fuel_type: Mapped[FuelType] = mapped_column(Enum(FuelType), nullable=False)
    seats: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    daily_rate: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="BDT", nullable=False)
    deposit_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[VehicleStatus] = mapped_column(
        Enum(VehicleStatus), default=VehicleStatus.available, nullable=False
    )
    odometer_km: Mapped[int] = mapped_column(default=0)

    category: Mapped["VehicleCategory"] = relationship(back_populates="vehicles")
    images: Mapped[list["VehicleImage"]] = relationship(
        back_populates="vehicle",
        cascade="all, delete-orphan",
        order_by="VehicleImage.sort_order",
    )

    __table_args__ = (
        CheckConstraint("year >= 1990", name="ck_vehicles_year"),
        CheckConstraint("seats > 0", name="ck_vehicles_seats"),
        CheckConstraint("daily_rate >= 0", name="ck_vehicles_rate"),
        Index("idx_vehicles_location_status", "location_id", "status"),
        Index("idx_vehicles_category", "category_id"),
    )


class VehicleImage(Base):
    __tablename__ = "vehicle_images"
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
    )
    vehicle_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    sort_order: Mapped[int] = mapped_column(SmallInteger, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    vehicle: Mapped["Vehicle"] = relationship(back_populates="images")
