# app/models/enums.py
import enum


class UserRole(str, enum.Enum):
    customer = "customer"
    fleet_staff = "fleet_staff"
    support = "support"
    admin = "admin"


class LicenseStatus(str, enum.Enum):
    unsubmitted = "unsubmitted"
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class VehicleStatus(str, enum.Enum):
    available = "available"
    booked = "booked"
    in_maintenance = "in_maintenance"
    retired = "retired"


class TransmissionType(str, enum.Enum):
    automatic = "automatic"
    manual = "manual"


class FuelType(str, enum.Enum):
    petrol = "petrol"
    diesel = "diesel"
    hybrid = "hybrid"
    electric = "electric"


class BookingStatus(str, enum.Enum):
    pending_payment = "pending_payment"
    pending_approval = "pending_approval"
    confirmed = "confirmed"
    active = "active"
    completed = "completed"
    cancelled = "cancelled"
    rejected = "rejected"
    no_show = "no_show"


class PaymentType(str, enum.Enum):
    charge = "charge"
    deposit_hold = "deposit_hold"
    deposit_capture = "deposit_capture"
    deposit_release = "deposit_release"
    refund = "refund"


class PaymentStatus(str, enum.Enum):
    pending = "pending"
    succeeded = "succeeded"
    failed = "failed"
    cancelled = "cancelled"


class DiscountType(str, enum.Enum):
    percentage = "percentage"
    fixed_amount = "fixed_amount"


class ReportType(str, enum.Enum):
    check_in = "check_in"
    check_out = "check_out"


class NotificationChannel(str, enum.Enum):
    email = "email"
    sms = "sms"
    push = "push"


class NotificationStatus(str, enum.Enum):
    queued = "queued"
    sent = "sent"
    failed = "failed"
