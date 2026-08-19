from datetime import date

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import LicenseStatus, UserRole


class UserBase(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    date_of_birth: date | None = None
    license_number: str | None = Field(
        default=None,
        max_length=50,
    )
    license_document_url: str | None = Field(
        default=None,
        max_length=500,
    )


# ============================================================
# Update own profile
# ============================================================


class UserUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )
    email: EmailStr | None = None
    date_of_birth: date | None = None
    license_number: str | None = Field(
        default=None,
        max_length=50,
    )
    license_document_url: str | None = Field(
        default=None,
        max_length=500,
    )


class UserAvatarUpdate(BaseModel):
    avatar_url: str | None = Field(
        default=None,
        max_length=500,
    )


# ============================================================
# Admin update
# ============================================================


class AdminUserUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )
    email: EmailStr | None = None
    role: UserRole | None = None
    is_active: bool | None = None
    is_verified: bool | None = None
    date_of_birth: date | None = None
    license_number: str | None = Field(
        default=None,
        max_length=50,
    )
    license_document_url: str | None = Field(
        default=None,
        max_length=500,
    )
    license_status: LicenseStatus | None = None


# ============================================================
# Change password
# ============================================================


class ChangePassword(BaseModel):
    current_password: str = Field(
        min_length=8,
        max_length=128,
    )
    new_password: str = Field(
        min_length=8,
        max_length=128,
    )
