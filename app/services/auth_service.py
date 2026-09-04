import uuid

import jwt
from fastapi import BackgroundTasks, HTTPException, Response, status
from redis.asyncio import Redis
from sqlalchemy.orm import Session
from starlette.status import HTTP_401_UNAUTHORIZED

from app.core.config import settings
from app.core.mail_client import send_forgot_password_mail, send_otp_mail
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import (
    Login,
    Register,
    RegisterResponse,
    ResetPassword,
    TokenData,
    TokenPair,
)
from app.services.redis_service import RedisService
from app.utils.auth import generate_otp


class AuthService:
    def __init__(self, db: Session, redis: Redis):
        self.db = db
        self.redis = redis
        self.redis_service = RedisService(redis)

    def find_by_id(self, id: uuid.UUID):
        user = (
            self.db.query(User).filter(User.id == id, User.deleted_at.is_(None)).first()
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not exit",
            )
        return user

    def find_by_email(self, email: str):
        user = (
            self.db.query(User)
            .filter(User.email == email, User.deleted_at.is_(None))
            .first()
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not exit",
            )
        return user

    async def register(
        self, register: Register, background_tasks: BackgroundTasks
    ) -> RegisterResponse:
        is_exit = (
            self.db.query(User)
            .filter(User.email == register.email, User.deleted_at.is_(None))
            .first()
        )
        if is_exit:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User Already Exits with this Email",
            )

        passwordHash = hash_password(register.password)

        new_user = User(name=register.name, email=register.email, password=passwordHash)

        try:
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)
        except:
            self.db.rollback()
            raise

        otp = generate_otp()
        await self.redis_service.store_otp(register.email, otp)
        await send_otp_mail(register.email, otp, background_tasks)

        return RegisterResponse(
            id=new_user.id,
            name=new_user.name,
            email=new_user.email,
        )

    async def login(self, data: Login) -> TokenPair:
        user = self.find_by_email(data.email)
        verify_pass = verify_password(data.password, user.password)
        if not verify_pass:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password did not matched!",
            )

        if not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please verify your email first!",
            )

        token_data = TokenData(id=user.id, role=user.role)

        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        payload = jwt.decode(
            refresh_token,
            settings.SECRET_REFRESH_TOKEN,
            algorithms=[settings.ALGORITHMS],
        )
        jti = payload["jti"]

        # STORING REFRESH TOKEN IN REDIS
        await self.redis_service.store_refresh_token(jti, user.id)
        return TokenPair(access_token=access_token, refresh_token=refresh_token)

    async def verification_otp(
        self, email: str, background_tasks: BackgroundTasks
    ) -> bool:
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        await self.redis_service.check_rate_limit(email)
        otp = generate_otp()
        await self.redis_service.store_otp(email, otp)
        await send_otp_mail(email, otp, background_tasks)
        return True

    async def verify_email(self, email: str, otp: str) -> bool:
        await self.redis_service.verify_otp(email, otp)
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        user.is_verified = True
        user.is_active = True
        self.db.commit()
        return True

    async def refresh_session(
        self, refresh_token: str | None, response: Response
    ) -> bool:
        if not refresh_token:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED, detail="Refresh Token is missing!"
            )

        payload = jwt.decode(
            refresh_token,
            settings.SECRET_REFRESH_TOKEN,
            algorithms=[settings.ALGORITHMS],
        )

        # GET THE EXISTING SESSION FROM REDIS

        session = await self.redis_service.get_refresh_token(payload["jti"])

        if not session:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        # DELETE THE EXISTING SESSION

        await self.redis_service.delete_refresh_token(payload["jti"])

        token_data = TokenData(id=payload["id"], role=payload["role"])

        new_access_token = create_access_token(token_data)
        new_refresh_token = create_refresh_token(token_data)

        new_payload = jwt.decode(
            new_refresh_token,
            settings.SECRET_REFRESH_TOKEN,
            algorithms=[settings.ALGORITHMS],
        )
        # STORE NEW SESSION FOR REFRESH TOKEN
        await self.redis_service.store_refresh_token(
            new_payload["jti"], new_payload["id"]
        )

        response.set_cookie(
            key="access_token",
            value=new_access_token,
            httponly=True,
            max_age=settings.ACCESS_TOKEN_EXPIRE_SECONDS,
            samesite="lax",
            secure=True,
        )
        response.set_cookie(
            key="refresh_token",
            value=new_refresh_token,
            httponly=True,
            max_age=settings.REFRESH_TOKEN_EXPIRE_SECONDS,
            samesite="lax",
            secure=True,
        )

        return True

    async def forgot_password(
        self, email: str, background_tasks: BackgroundTasks
    ) -> bool:
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        otp = generate_otp()
        await self.redis_service.store_otp(email, otp)

        await send_forgot_password_mail(email, otp, background_tasks)

        return True

    async def reset_password(self, payload: ResetPassword) -> bool:
        user = self.db.query(User).filter(User.email == payload.email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not verify_password(payload.current_password, user.password):
            raise HTTPException(status_code=400, detail="Invalid current password")

        user.password = hash_password(payload.new_password)
        self.db.commit()

        return True
