from fastapi import HTTPException, status
from redis.asyncio import Redis
from sqlalchemy.orm import Session

from app.core.settings import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import Login, Register, RegisterResponse, TokenData, TokenFair


class AuthService:
    def __init__(self, db: Session, redis: Redis):
        self.db = db
        self.redis = redis

    def findById(self, email: str):
        user = self.db.query(User).filter_by(email=email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not exit",
            )
        return user

    def register(self, register: Register) -> RegisterResponse:
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

        return RegisterResponse(
            id=new_user.id,
            name=new_user.name,
            email=new_user.email,
        )

    def login(self, data: Login) -> TokenFair:
        user = self.findById(data.email)
        verify_pass = verify_password(data.password, user.password)
        if not verify_pass:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password didnot matched!",
            )

        token_data = TokenData(id=user.id, role=user.role)

        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        return TokenFair(access_token=access_token, refresh_token=refresh_token)

    async def store_otp(self, email: str, otp: str, expire: int = 300):
        await self.redis.setex(f"otp:{email}", expire, otp)

    async def verify_otp(self, email: str, otp: str) -> bool:
        stored_otp = await self.redis.get(f"otp:{email}")

        if not stored_otp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP Expired or not found",
            )

        if stored_otp != otp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP"
            )

        await self.redis.delete(f"otp:{email}")
        return True
