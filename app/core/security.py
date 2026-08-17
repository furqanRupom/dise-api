# create jwttoken and hash password utils function
import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum

import jwt
from fastapi import HTTPException, status
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from pwdlib.hashers.bcrypt import BcryptHasher

from app.models.enums import UserRole
from app.schemas.auth import TokenData

from .config import settings

password_hash = PasswordHash(
    (
        Argon2Hasher(),
        BcryptHasher(),
    )
)


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hash: str) -> bool:
    return password_hash.verify(password, hash)


def create_access_token(data: TokenData, expires_delta: timedelta | None = None):
    to_encode = data.model_dump(mode="json")
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode["exp"] = expire
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_ACCESS_TOKEN, algorithm=settings.ALGORITHMS
    )
    return encoded_jwt


def create_refresh_token(
    data: TokenData, expires_delta: timedelta | None = None
) -> str:

    to_encode = data.model_dump(mode="json")

    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    to_encode["exp"] = expire
    to_encode["jti"] = str(uuid.uuid4())

    token = jwt.encode(
        to_encode, settings.SECRET_REFRESH_TOKEN, algorithm=settings.ALGORITHMS
    )
    return token


def verify_access_token(token: str) -> dict:
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_ACCESS_TOKEN, algorithms=[settings.ALGORITHMS]
        )
        return payload
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


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


# Single source of truth for role → permissions
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
        Permission.USERS_READ,
        Permission.USERS_VERIFY_LICENSE,
        Permission.BOOKINGS_READ_ALL,
        Permission.BOOKINGS_MANAGE,
        Permission.PAYMENTS_READ_ALL,
        Permission.PAYMENTS_REFUND,
        Permission.VEHICLES_READ,
    },
    UserRole.admin: set(Permission),  # all permissions
}


class PermissionChecker:
    @classmethod
    def has_permission(
        cls,
        user_role: UserRole,
        permission: Permission,
    ) -> bool:
        return permission in ROLE_PERMISSIONS.get(user_role, set())

    @classmethod
    def require_permission(
        cls,
        user_role: UserRole,
        permission: Permission,
    ) -> None:
        if not cls.has_permission(user_role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permission: {permission.value}",
            )

    @classmethod
    def require_role(
        cls,
        user_role: UserRole,
        required_roles: UserRole | list[UserRole],
    ) -> None:
        if isinstance(required_roles, UserRole):
            required_roles = [required_roles]

        if user_role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Role not allowed",
            )
