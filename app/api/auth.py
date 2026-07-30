from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.redis import get_redis
from app.schemas.auth import Login, Register, RegisterResponse, TokenFair
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


def get_auth_service(
    db: Session = Depends(get_db), redis: Redis = Depends(get_redis)
) -> AuthService:
    return AuthService(db, redis)


@router.post("/register")
async def register_user(
    register: Register, service: AuthService = Depends(get_auth_service)
) -> RegisterResponse:
    registered_user = service.register(register)
    return registered_user


@router.post("/login")
async def login_user(
    login: Login, service: AuthService = Depends(get_auth_service)
) -> TokenFair:
    logged_in_user = service.login(login)
    return logged_in_user
