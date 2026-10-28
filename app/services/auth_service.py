import uuid

import jwt
from fastapi import BackgroundTasks, HTTPException, status
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

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

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    @staticmethod
    def _normalize_email(email: str) -> str:
        return email.strip().lower()

    def _get_user_by_email(self, email: str) -> User | None:
        """Single place for the 'non-deleted user by email' query."""
        return self.db.execute(
            select(User).where(
                User.email == self._normalize_email(email),
                User.deleted_at.is_(None),
            )
        ).scalar_one_or_none()

    def find_by_id(self, user_id: uuid.UUID) -> User:
        user = self.db.execute(
            select(User).where(User.id == user_id, User.deleted_at.is_(None))
        ).scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User does not exist",
            )
        return user

    def find_by_email(self, email: str) -> User:
        user = self._get_user_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User does not exist",
            )
        return user

    @staticmethod
    def _decode_refresh_token(token: str) -> dict:
        """Decode a refresh token, turning JWT errors into 401s instead of 500s."""
        try:
            return jwt.decode(
                token,
                settings.SECRET_REFRESH_TOKEN,
                algorithms=[settings.ALGORITHMS],
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has expired",
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

    async def _issue_tokens(self, token_data: TokenData) -> TokenPair:
        """Create an access/refresh pair and register the refresh session in Redis."""
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        payload = self._decode_refresh_token(refresh_token)
        await self.redis_service.store_refresh_token(payload["jti"], token_data.id)

        return TokenPair(access_token=access_token, refresh_token=refresh_token)

    def _get_active_user_or_401(self, user_id: uuid.UUID | str) -> User:
        user = self.db.execute(
            select(User).where(User.id == user_id, User.deleted_at.is_(None))
        ).scalar_one_or_none()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )
        return user

    # ------------------------------------------------------------------ #
    # Registration / verification
    # ------------------------------------------------------------------ #
    async def register(
        self, register: Register, background_tasks: BackgroundTasks
    ) -> RegisterResponse:
        email = self._normalize_email(register.email)

        if self._get_user_by_email(email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists",
            )

        new_user = User(
            name=register.name,
            email=email,
            password=hash_password(register.password),
        )

        try:
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)
        except IntegrityError:
            # Two concurrent requests passed the check above; the unique
            # constraint on email caught the loser.
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists",
            )
        except Exception:
            self.db.rollback()
            raise

        otp = generate_otp()
        await self.redis_service.store_otp(email, otp)
        await send_otp_mail(email, otp, background_tasks)

        return RegisterResponse(
            id=new_user.id,
            name=new_user.name,
            email=new_user.email,
        )

    async def verification_otp(
        self, email: str, background_tasks: BackgroundTasks
    ) -> bool:
        email = self._normalize_email(email)

        # Rate limit first so the response doesn't depend on whether the user exists.
        await self.redis_service.check_rate_limit(email)

        if self._get_user_by_email(email):
            otp = generate_otp()
            await self.redis_service.store_otp(email, otp)
            await send_otp_mail(email, otp, background_tasks)
        return True

    async def verify_email(self, email: str, otp: str) -> bool:
        email = self._normalize_email(email)

        await self.redis_service.verify_otp(email, otp)
        user = self.find_by_email(email)

        user.is_verified = True
        user.is_active = True
        self.db.commit()
        return True

    # ------------------------------------------------------------------ #
    # Login / sessions
    # ------------------------------------------------------------------ #
    async def login(self, data: Login) -> TokenPair:
        user = self._get_user_by_email(data.email)

        # Same error for "no such user" and "wrong password".
        if not user or not verify_password(data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please verify your email first!",
            )

        return await self._issue_tokens(TokenData(id=user.id, role=user.role))

    async def refresh_session(self, refresh_token: str | None) -> TokenPair:
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token is missing!",
            )

        payload = self._decode_refresh_token(refresh_token)

        # Atomically take the session: it must still exist (not revoked) and
        # can only be used once, even under concurrent requests.
        session = await self.redis_service.consume_refresh_token(payload["jti"])
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        # Re-read the user so role changes / deletions / deactivation take
        # effect instead of trusting claims baked into the old token.
        user = self._get_active_user_or_401(payload["id"])

        return await self._issue_tokens(TokenData(id=user.id, role=user.role))

    async def logout(self, refresh_token: str | None) -> bool:
        """Revoke this refresh session in Redis."""
        if not refresh_token:
            return True

        try:
            # Expired tokens still identify a session worth deleting.
            payload = jwt.decode(
                refresh_token,
                settings.SECRET_REFRESH_TOKEN,
                algorithms=[settings.ALGORITHMS],
                options={"verify_exp": False},
            )
        except jwt.InvalidTokenError:
            return True  # Garbage token: nothing to revoke.

        if jti := payload.get("jti"):
            await self.redis_service.delete_refresh_token(jti)
        return True

    # ------------------------------------------------------------------ #
    # Password management
    # ------------------------------------------------------------------ #
    async def forgot_password(
        self, email: str, background_tasks: BackgroundTasks
    ) -> bool:
        email = self._normalize_email(email)
        await self.redis_service.check_rate_limit(email, purpose="reset")

        # Always return True: don't reveal which emails are registered.
        if self._get_user_by_email(email):
            otp = generate_otp()
            await self.redis_service.store_otp(email, otp, purpose="reset")
            await send_forgot_password_mail(email, otp, background_tasks)
        return True

    async def reset_forgotten_password(
        self, email: str, otp: str, new_password: str
    ) -> bool:
        """Second half of forgot-password: verify the OTP, set a new password.

        Reset OTPs live in their own Redis namespace, so an email-verification
        OTP can't be replayed here. Needs a route (not wired up yet).
        """
        email = self._normalize_email(email)
        await self.redis_service.verify_otp(email, otp, purpose="reset")

        user = self.find_by_email(email)
        user.password = hash_password(new_password)
        self.db.commit()

        # Whoever had the old password shouldn't stay logged in.
        await self.redis_service.revoke_all_user_sessions(user.id)
        return True

    async def reset_password(self, user: User, payload: ResetPassword) -> bool:
        """Change password for the logged-in user (needs the current password)."""
        if not verify_password(payload.current_password, user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid current password",
            )

        user.password = hash_password(payload.new_password)
        self.db.commit()

        await self.redis_service.revoke_all_user_sessions(user.id)
        return True
