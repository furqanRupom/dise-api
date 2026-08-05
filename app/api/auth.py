from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Cookie, Depends, Response
from pydantic import EmailStr
from redis.asyncio import Redis
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.dependencies import get_current_active_user
from app.db.database import get_db
from app.db.redis import get_redis
from app.models import User
from app.schemas.auth import Login, OTPVerify, Register, ResetPassword
from app.schemas.response import SendRespose
from app.services.auth_service import AuthService

router = APIRouter(prefix="/v1/auth", tags=["auth"])


def get_auth_service(
    db: Session = Depends(get_db), redis: Redis = Depends(get_redis)
) -> AuthService:
    return AuthService(db, redis)


@router.post("/register")
async def register_user(
    register: Register,
    background_tasks: BackgroundTasks,
    service: AuthService = Depends(get_auth_service),
):
    registered_user = await service.register(register, background_tasks)
    return registered_user


@router.post("/login")
async def login_user(
    response: Response, login: Login, service: AuthService = Depends(get_auth_service)
) -> SendRespose:

    result = await service.login(login)

    response.set_cookie(
        key="access_token",
        value=result.data.access_token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_SECONDS,
        samesite="lax",
        secure=True,
    )

    response.set_cookie(
        key="refresh_token",
        value=result.data.refresh_token,
        httponly=True,
        max_age=settings.REFRESH_TOKEN_EXPIRE_SECONDS,
        samesite="lax",
        secure=True,
    )

    return result


@router.post("/send-otp")
async def send_otp(
    email: EmailStr,
    background_tasks: BackgroundTasks,
    service: AuthService = Depends(get_auth_service),
):
    return await service.verification_otp(email, background_tasks)


@router.post("/verify-email")
async def verify_otp(
    data: OTPVerify,
    service: AuthService = Depends(get_auth_service),
):
    return await service.verify_email(data.email, data.otp)


@router.post("/refresh-token")
async def refresh_token(
    response: Response,
    refresh_token: Annotated[str | None, Cookie()] = None,
    service: AuthService = Depends(get_auth_service),
):
    return await service.refresh_session(refresh_token, response)


@router.post("/forgot-password")
async def forgot_password(
    email: EmailStr,
    background_tasks: BackgroundTasks,
    service: AuthService = Depends(get_auth_service),
):
    return await service.forgot_password(email, background_tasks)


@router.post("/reset-password")
async def reset_password(
    payload: ResetPassword,
    service: AuthService = Depends(get_auth_service),
):
    return await service.reset_password(payload)


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    return SendRespose(success=True, message="User logout successfully", data=None)


@router.get("/get-me")
async def get_me(get_user: User = Depends(get_current_active_user)):
    return get_user
