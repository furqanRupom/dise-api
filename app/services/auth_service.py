import jwt
from fastapi import BackgroundTasks, HTTPException, Response, status
from redis.asyncio import Redis
from sqlalchemy.orm import Session
from starlette.status import HTTP_401_UNAUTHORIZED

from app.core.config import settings
from app.core.settings import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import Login, Register, RegisterResponse, TokenData, TokenFair
from app.schemas.response import SendRespose
from app.services.email_service import EmailService
from app.services.otp_service import OTPService


class AuthService:
    def __init__(self, db: Session, redis: Redis):
        self.db = db
        self.redis = redis
        self.otp_service = OTPService(redis)

    """ STORE REFRESH TOKEN VIA REDIS HERE FOR NOW """

    async def _store_refresh_token(self, jti: str, user_id: int | str):
        await self.redis.set(
            f"refresh:{jti}",
            str(user_id),
            ex=settings.REFRESH_TOKEN_EXPIRE_SECONDS,
        )

    async def _get_refresh_token(self, jti: str) -> bytes | str | None:
        return await self.redis.get(f"refresh:{jti}")

    async def _delete_refresh_token(self, jti: str):
        await self.redis.delete(f"refresh:{jti}")

    def findById(self, email: str):
        user = self.db.query(User).filter_by(email=email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not exit",
            )
        return user

    async def register(
        self, register: Register, background_tasks: BackgroundTasks
    ) -> SendRespose:
        is_exit = self.db.query(User).filter(User.email == register.email).first()
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

        otp = self.otp_service.generate_otp()
        await self.otp_service.store_otp(register.email, otp)
        await EmailService.send_otp_email(register.email, otp, background_tasks)

        return SendRespose(
            success=True,
            message="User Registered Successfully.check your mail",
            data=RegisterResponse(
                id=new_user.id, name=new_user.name, email=new_user.email
            ),
        )

    async def login(self, data: Login) -> SendRespose:
        user = self.findById(data.email)
        verify_pass = verify_password(data.password, user.password)
        if not verify_pass:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password didnot matched!",
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
        await self._store_refresh_token(jti, user.id)
        return SendRespose(
            success=True,
            message="User Logged in Successfully",
            data=TokenFair(access_token=access_token, refresh_token=refresh_token),
        )

    async def verification_otp(self, email: str, background_tasks: BackgroundTasks):
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        await self.otp_service.check_rate_limit(email)
        otp = self.otp_service.generate_otp()
        await self.otp_service.store_otp(email, otp)
        await EmailService.send_otp_email(email, otp, background_tasks)
        return SendRespose(
            success=True, message="Verification OTP sent successfully", data=None
        )

    async def verify_email(self, email: str, otp: str):
        await self.otp_service.verify_otp(email, otp)
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        user.is_verified = True
        self.db.commit()
        return SendRespose(
            success=True, message="user verified successfully", data=None
        )

    async def refresh_session(self, refresh_token: str | None, response: Response):
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

        session = await self._get_refresh_token(payload["jti"])

        if not session:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        # DELETE THE EXISTING SESSION

        await self._delete_refresh_token(payload["jti"])

        token_data = TokenData(id=payload["id"], role=payload["role"])

        new_access_token = create_access_token(token_data)
        new_refresh_token = create_refresh_token(token_data)

        new_payload = jwt.decode(
            new_refresh_token,
            settings.SECRET_REFRESH_TOKEN,
            algorithms=[settings.ALGORITHMS],
        )
        # STORE NEW SESSION FOR REFRESH TOKEN
        await self._store_refresh_token(new_payload["jti"], new_payload["id"])

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

        return SendRespose(
            success=True, message="Tokens refreshed successfully", data=None
        )
