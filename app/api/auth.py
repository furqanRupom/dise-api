from fastapi import APIRouter, BackgroundTasks, Depends
from pydantic import EmailStr
from redis.asyncio import Redis
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.redis import get_redis
from app.schemas.auth import Login, OTPVerify, Register
from app.schemas.response import SendRespose
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


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
    login: Login, service: AuthService = Depends(get_auth_service)
) -> SendRespose:
    logged_in_user = service.login(login)
    return logged_in_user


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
