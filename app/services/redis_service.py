import hmac
import uuid
from typing import Literal

from fastapi import HTTPException, status
from redis.asyncio import Redis

from app.core.config import settings

OtpPurpose = Literal["verify", "reset"]

OTP_TTL_SECONDS = 300
OTP_MAX_ATTEMPTS = 5


def _to_str(value: bytes | str) -> str:
    """Redis returns bytes unless the client was created with decode_responses=True."""
    return value.decode() if isinstance(value, bytes) else value


class RedisService:
    def __init__(self, redis: Redis):
        self.redis = redis

    # ------------------------------------------------------------------ #
    # Refresh-token sessions
    #
    # refresh:{jti}            -> user_id   (one key per session, with TTL)
    # user_sessions:{user_id}  -> set of jti (lets us revoke every session
    #                             for a user, e.g. after a password change)
    # ------------------------------------------------------------------ #
    @staticmethod
    def _session_key(jti: str) -> str:
        return f"refresh:{jti}"

    @staticmethod
    def _user_sessions_key(user_id: uuid.UUID | str) -> str:
        return f"user_sessions:{user_id}"

    async def store_refresh_token(self, jti: str, user_id: uuid.UUID | str) -> None:
        ttl = settings.REFRESH_TOKEN_EXPIRE_SECONDS
        index_key = self._user_sessions_key(user_id)

        async with self.redis.pipeline(transaction=True) as pipe:
            pipe.set(self._session_key(jti), str(user_id), ex=ttl)
            pipe.sadd(index_key, jti)
            pipe.expire(index_key, ttl)
            await pipe.execute()

    async def get_refresh_token(self, jti: str) -> str | None:
        value = await self.redis.get(self._session_key(jti))
        return _to_str(value) if value is not None else None

    async def consume_refresh_token(self, jti: str) -> str | None:
        """Atomically fetch AND delete a session (GETDEL, Redis >= 6.2).

        Use this for rotation: if two requests present the same refresh token
        at the same time, only one gets the user_id back; the other gets None.
        """
        value = await self.redis.getdel(self._session_key(jti))
        return _to_str(value) if value is not None else None

    async def delete_refresh_token(self, jti: str) -> None:
        await self.redis.delete(self._session_key(jti))

    async def revoke_all_user_sessions(self, user_id: uuid.UUID | str) -> None:
        """Log the user out everywhere."""
        index_key = self._user_sessions_key(user_id)
        jtis = await self.redis.smembers(index_key)

        async with self.redis.pipeline(transaction=True) as pipe:
            for jti in jtis:
                pipe.delete(self._session_key(_to_str(jti)))
            pipe.delete(index_key)
            await pipe.execute()

    # ------------------------------------------------------------------ #
    # OTP
    #
    # Keys are namespaced by purpose so an email-verification OTP can never
    # be replayed to reset a password (and vice versa).
    # ------------------------------------------------------------------ #
    @staticmethod
    def _otp_key(email: str, purpose: OtpPurpose) -> str:
        return f"otp:{purpose}:{email}"

    @staticmethod
    def _otp_attempts_key(email: str, purpose: OtpPurpose) -> str:
        return f"otp_attempts:{purpose}:{email}"

    async def store_otp(
        self,
        email: str,
        otp: str,
        purpose: OtpPurpose = "verify",
        expire: int = OTP_TTL_SECONDS,
    ) -> None:
        async with self.redis.pipeline(transaction=True) as pipe:
            pipe.set(self._otp_key(email, purpose), otp, ex=expire)
            # A fresh OTP gets a fresh attempt budget.
            pipe.delete(self._otp_attempts_key(email, purpose))
            await pipe.execute()

    async def verify_otp(
        self, email: str, otp: str, purpose: OtpPurpose = "verify"
    ) -> bool:
        otp_key = self._otp_key(email, purpose)
        attempts_key = self._otp_attempts_key(email, purpose)

        stored = await self.redis.get(otp_key)
        if stored is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP expired or not found",
            )

        # Cap guesses: a 6-digit OTP is trivially brute-forceable otherwise.
        attempts = await self.redis.incr(attempts_key)
        if attempts == 1:
            await self.redis.expire(attempts_key, OTP_TTL_SECONDS)
        if attempts > OTP_MAX_ATTEMPTS:
            await self.redis.delete(otp_key, attempts_key)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many incorrect attempts. Please request a new OTP",
            )

        # Constant-time comparison; also works whether Redis returns bytes or str.
        if not hmac.compare_digest(_to_str(stored).encode(), otp.encode()):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OTP",
            )

        await self.redis.delete(otp_key, attempts_key)
        return True

    async def check_rate_limit(
        self, email: str, purpose: OtpPurpose = "verify", cooldown: int = 60
    ) -> None:
        """Cooldown between OTP requests.

        Uses a single atomic SET NX EX. The old exists() -> setex() pair let
        two concurrent requests both pass the check.
        """
        key = f"otp_rate:{purpose}:{email}"
        acquired = await self.redis.set(key, "1", ex=cooldown, nx=True)
        if not acquired:
            ttl = max(await self.redis.ttl(key), 1)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Please wait {ttl} seconds before requesting another OTP",
            )
