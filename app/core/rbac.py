# app/core/rbac.py
from enum import Enum

from app.models.enums import UserRole


class Permission(str, Enum):
    USERS_READ = "users:read"
    USERS_WRITE = "users:write"
    USERS_VERIFY_LICENSE = "users:verify_license"
    VEHICLES_READ = "vehicles:read"
    VEHICLES_WRITE = "vehicles:write"
    VEHICLES_IMAGES_WRITE = "vehicles:images:write"
    VEHICLES_AVAIL_MANAGE = "vehicles:availability:manage"
    BOOKINGS_READ_OWN = "bookings:read:own"
    BOOKINGS_READ_ALL = "bookings:read:all"
    BOOKINGS_WRITE_OWN = "bookings:write:own"
    BOOKINGS_APPROVE = "bookings:approve"
    BOOKINGS_MANAGE = "bookings:manage"
    BOOKINGS_CHECKIN = "bookings:checkin"
    PAYMENTS_READ_OWN = "payments:read:own"
    PAYMENTS_READ_ALL = "payments:read:all"
    PAYMENTS_REFUND = "payments:refund"
    COUPONS_READ = "coupons:read"
    COUPONS_MANAGE = "coupons:manage"
    LOCATIONS_READ = "locations:read"
    LOCATIONS_MANAGE = "locations:manage"
    REVIEWS_WRITE_OWN = "reviews:write:own"
    REPORTS_VIEW = "reports:view"


ROLE_PERMISSIONS: dict[UserRole, set[Permission]] = {
    UserRole.customer: {
        Permission.VEHICLES_READ,
        Permission.LOCATIONS_READ,
        Permission.BOOKINGS_READ_OWN,
        Permission.BOOKINGS_WRITE_OWN,
        Permission.PAYMENTS_READ_OWN,
        Permission.COUPONS_READ,
        Permission.REVIEWS_WRITE_OWN,
    },
    UserRole.fleet_staff: {
        Permission.VEHICLES_READ,
        Permission.VEHICLES_WRITE,
        Permission.VEHICLES_IMAGES_WRITE,
        Permission.VEHICLES_AVAIL_MANAGE,
        Permission.BOOKINGS_READ_ALL,
        Permission.BOOKINGS_APPROVE,
        Permission.BOOKINGS_CHECKIN,
        Permission.LOCATIONS_READ,
    },
    UserRole.support: {
        Permission.USERS_READ
        if hasattr(Permission, "USERS_READ")
        else Permission.USERS_VERIFY_LICENSE,
        Permission.USERS_VERIFY_LICENSE,
        Permission.BOOKINGS_READ_ALL,
        Permission.BOOKINGS_MANAGE,
        Permission.PAYMENTS_READ_ALL,
        Permission.PAYMENTS_REFUND,
        Permission.VEHICLES_READ,
    },
    UserRole.admin: set(Permission),  # all
}
