# create jwttoken and hash password utils function
from pwdlib import PasswordHash
from .config import settings
import jwt
from datetime import timedelta,timezone,datetime
from app.schemas.auth import TokenData
password_hash = PasswordHash.recommended()
def hash_password(password:str) -> str:
    return password_hash.hash(password)

def verify_password(password:str,hash:str) -> bool:
    return password_hash.verify(password,hash)
    


def create_access_token(data: TokenData, expires_delta: timedelta | None = None):
    to_encode = data.model_dump()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode['exp'] = expire
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_ACCESS_TOKEN, algorithm=settings.ALGORITHMS)
    return encoded_jwt


def create_refresh_token(
    data: TokenData,
    expires_delta: timedelta | None = None
) -> str:

    to_encode = data.model_dump()

    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))
    to_encode["exp"] = expire

    token = jwt.encode(
        to_encode,
        settings.SECRET_REFRESH_TOKEN,
        algorithm=settings.ALGORITHMS
    )
    return token

