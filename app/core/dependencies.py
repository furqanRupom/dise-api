from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyCookie  # ← changed
from redis.asyncio import Redis
from sqlalchemy.orm import Session

from app.core.settings import verify_access_token
from app.db import get_redis
from app.db.database import get_db
from app.models.user import User
from app.services.auth_service import AuthService

cookie_scheme = APIKeyCookie(name="access_token", auto_error=False)


def get_current_user(
    token: str | None = Security(cookie_scheme),
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> User:
    """Get current authenticated user from JWT token in cookie."""

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = verify_access_token(token)

    raw_id = payload.get("id")
    raw_role = payload.get("role")

    if raw_id is None or raw_role is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    id: int = raw_id
    role: str = raw_role

    auth_service = AuthService(db, redis)
    user = auth_service.find_by_id(id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user."""
    return current_user
