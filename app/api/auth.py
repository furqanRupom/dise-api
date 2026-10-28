from typing import Annotated

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Cookie,
    Depends,
    Response,
    status,
)
from pydantic import EmailStr
from redis.asyncio import Redis
from sqlalchemy.orm import Session

from app.core.cookies import clear_auth_cookies, set_auth_cookies
from app.core.dependencies import get_current_active_user
from app.db.database import get_db
from app.db.redis import get_redis
from app.models import User
from app.schemas.auth import (
    Login,
    OTPVerify,
    Register,
    RegisterResponse,
    ResetPassword,
    TokenPair,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/v1/auth", tags=["auth"])


def get_auth_service(
    db: Annotated[Session, Depends(get_db)],
    redis: Annotated[Redis, Depends(get_redis)],
) -> AuthService:
    return AuthService(db, redis)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
CurrentUser = Annotated[User, Depends(get_current_active_user)]


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    register: Register,
    background_tasks: BackgroundTasks,
    service: AuthServiceDep,
):
    return await service.register(register, background_tasks)


@router.post("/login", response_model=TokenPair)
async def login_user(response: Response, login: Login, service: AuthServiceDep):
    result = await service.login(login)
    set_auth_cookies(response, result.access_token, result.refresh_token)
    return result


@router.post("/send-otp", response_model=bool)
async def send_otp(
    email: EmailStr,
    background_tasks: BackgroundTasks,
    service: AuthServiceDep,
):
    return await service.verification_otp(email, background_tasks)


@router.post("/verify-email", response_model=bool)
async def verify_otp(data: OTPVerify, service: AuthServiceDep):
    return await service.verify_email(data.email, data.otp)


@router.post("/refresh-token", response_model=bool)
async def refresh_token(
    response: Response,
    service: AuthServiceDep,
    refresh_token: Annotated[str | None, Cookie()] = None,
):
    tokens = await service.refresh_session(refresh_token)
    set_auth_cookies(response, tokens.access_token, tokens.refresh_token)
    return True


@router.post("/forgot-password", response_model=bool)
async def forgot_password(
    email: EmailStr,
    background_tasks: BackgroundTasks,
    service: AuthServiceDep,
):
    return await service.forgot_password(email, background_tasks)


@router.post("/reset-password", response_model=bool)
async def reset_password(
    payload: ResetPassword,
    user: CurrentUser,
    service: AuthServiceDep,
):
    return await service.reset_password(user, payload)


@router.post("/logout", response_model=bool)
async def logout(
    response: Response,
    service: AuthServiceDep,
    refresh_token: Annotated[str | None, Cookie()] = None,
):
    await service.logout(refresh_token)
    clear_auth_cookies(response)
    return True


@router.get("/get-me")
async def get_me(user: CurrentUser):
    return user
