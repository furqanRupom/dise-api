import uuid

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.enums import UserRole


class UserBase(BaseModel):
    name: str
    email: EmailStr


class Register(UserBase):
    password: str


class RegisterResponse(UserBase):
    id: uuid.UUID


class Login(BaseModel):
    email: EmailStr
    password: str


class TokenData(BaseModel):
    id: uuid.UUID
    role: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str


class OTPVerify(BaseModel):
    email: EmailStr
    otp: str


class ResetPassword(BaseModel):
    email: EmailStr
    current_password: str
    new_password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    email: EmailStr
    avatar_url: str
    date_of_birth: str
    license_number: str
    license_document_url: str
    license_status: str
    role: UserRole
    is_verified: bool
    is_active: bool
