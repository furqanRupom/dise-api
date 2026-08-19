import uuid

from pydantic import BaseModel, EmailStr


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
