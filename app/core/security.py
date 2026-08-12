# create jwttoken and hash password utils function
import uuid
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException, status
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from pwdlib.hashers.bcrypt import BcryptHasher

from app.schemas.auth import TokenData

from .config import settings

password_hash = PasswordHash(
    (
        Argon2Hasher(),
        BcryptHasher(),
    )
)


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hash: str) -> bool:
    return password_hash.verify(password, hash)


def create_access_token(data: TokenData, expires_delta: timedelta | None = None):
    to_encode = data.model_dump(mode="json")
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode["exp"] = expire
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_ACCESS_TOKEN, algorithm=settings.ALGORITHMS
    )
    return encoded_jwt


def create_refresh_token(
    data: TokenData, expires_delta: timedelta | None = None
) -> str:

    to_encode = data.model_dump(mode="json")

    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    to_encode["exp"] = expire
    to_encode["jti"] = str(uuid.uuid4())

    token = jwt.encode(
        to_encode, settings.SECRET_REFRESH_TOKEN, algorithm=settings.ALGORITHMS
    )
    return token


def verify_access_token(token: str) -> dict:
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_ACCESS_TOKEN, algorithms=[settings.ALGORITHMS]
        )
        return payload
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
