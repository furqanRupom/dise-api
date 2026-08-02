from fastapi import HTTPException, status
from redis.asyncio import Redis


class OTPService:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def store_otp(self, email: str, otp: str, expire: int = 300):
        await self.redis.setex(f"otp:{email}", expire, otp)

    async def verify_otp(self, email: str, otp: str) -> bool:
        stored = await self.redis.get(f"otp:{email}")
        if not stored:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP expired or not found",
            )
        if stored != otp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OTP",
            )
        await self.redis.delete(f"otp:{email}")
        return True

    async def check_rate_limit(self, email: str, cooldown: int = 60):
        key = f"otp_rate:{email}"
        if await self.redis.exists(key):
            ttl = await self.redis.ttl(key)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Please wait {ttl} seconds before requesting another OTP",
            )
        await self.redis.setex(key, cooldown, "1")
