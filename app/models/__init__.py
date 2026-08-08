"""
Central import point for the ORM. Importing everything here (rather than
each model importing only what it directly needs) guarantees every model
class is registered on `Base.metadata` before anything calls
Base.metadata.create_all() or Alembic autogenerate runs - a model that's
never imported anywhere never gets mapped, and its table silently never
gets created.

Import order matters only for the modules that do *real* (non
TYPE_CHECKING-guarded) cross-model imports at the top of their file:
  - booking.py imports User and Vehicle for real (used unquoted in
    `Mapped[User]` / `Mapped[Vehicle]`)
  - everything else only references other models via TYPE_CHECKING-guarded
    string forward refs, so it doesn't matter when they're imported
Since user.py and vehicle.py never import booking.py at real-import-time,
there's no actual circularity - the order below is just the natural
dependency order, not a strict requirement.
"""

from app.db.database import Base
from app.models.audit_logs import AuditLog

# --- booking imports User + Vehicle for real, so must come after them ---
from app.models.booking import Booking, BookingStatusHistory
from app.models.condition_reports import ConditionReport, ConditionReportImage
from app.models.coupons import Coupon, CouponUsage

# --- enums (no dependencies) ---
from app.models.enums import (
    BookingStatus,
    DiscountType,
    FuelType,
    LicenseStatus,
    NotificationChannel,
    NotificationStatus,
    PaymentStatus,
    PaymentType,
    ReportType,
    TransmissionType,
    UserRole,
    VehicleStatus,
)

# --- models with no cross-model dependencies ---
from app.models.location import Location
from app.models.maintenance import MaintenanceBlock
from app.models.notifications import Notification

# --- everything else (only TYPE_CHECKING-guarded refs back to Booking) ---
from app.models.payments import Payment
from app.models.reviews import Review
from app.models.user import User
from app.models.vehicle import Vehicle, VehicleCategory, VehicleImage

# This tells Python what to export when someone does `from app.models import *`
__all__ = [
    "AuditLog",
    "Base",
    "Booking",
    "BookingStatus",
    "BookingStatusHistory",
    "ConditionReport",
    "ConditionReportImage",
    "Coupon",
    "CouponUsage",
    "DiscountType",
    "FuelType",
    "LicenseStatus",
    "Location",
    "MaintenanceBlock",
    "Notification",
    "NotificationChannel",
    "NotificationStatus",
    "Payment",
    "PaymentStatus",
    "PaymentType",
    "ReportType",
    "Review",
    "TransmissionType",
    "User",
    "UserRole",
    "Vehicle",
    "VehicleCategory",
    "VehicleImage",
    "VehicleStatus",
]
