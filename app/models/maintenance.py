import uuid
from datetime import date, datetime

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, String, func, text
from sqlalchemy.dialects.postgresql import ExcludeConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class MaintenanceBlock(Base):
    __tablename__ = "maintenance_blocks"
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
    )
    vehicle_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    reason: Mapped[str | None] = mapped_column(String(255))
    created_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint("end_date >= start_date", name="ck_maintenance_dates"),
        # Also requires btree_gist (same extension as bookings' exclude constraint).
        # text() wrap required - see booking.py for why a bare string breaks this.
        ExcludeConstraint(
            ("vehicle_id", "="),
            (text("daterange(start_date, end_date, '[]')"), "&&"),
            name="excl_no_overlap_maintenance",
        ),
    )
