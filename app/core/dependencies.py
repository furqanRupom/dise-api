import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyCookie
from redis.asyncio import Redis
from sqlalchemy.orm import Session

from app.core.rbac import ROLE_PERMISSIONS, Permission
from app.core.settings import verify_access_token
from app.db import get_redis
from app.db.database import get_db
from app.models import UserRole
from app.models.user import User
from app.services.auth_service import AuthService

cookie_scheme = APIKeyCookie(name="access_token", auto_error=False)


def get_current_user(
    db: Annotated[Session, Depends(get_db)],
    redis: Annotated[Redis, Depends(get_redis)],
    token: str | None = Security(cookie_scheme),
) -> User:
    """Get current authenticated user from JWT token in cookie."""
    if not token:
        # Auth is cookie-based here, not a Bearer token, so the
        # WWW-Authenticate: Bearer header (left over from a header-auth
        # implementation) was misleading and has been dropped.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    payload = verify_access_token(token)
    raw_id = payload.get("id")
    raw_role = payload.get("role")
    if raw_id is None or raw_role is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    # Every primary key in this schema is a UUID, not an int. Coercing to
    # `int` here would either throw on a real UUID or, worse, silently
    # look up the wrong row if raw_id happened to parse as a number.
    try:
        user_id = uuid.UUID(str(raw_id))
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    role: str = raw_role

    auth_service = AuthService(db, redis)
    user = auth_service.find_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user


def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Get current active user. Previously this just returned whatever
    get_current_user gave it — the name promised an activeness check that
    never actually happened, so deactivated accounts could still use any
    endpoint depending on this dependency."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is not active",
        )
    return current_user


def require_permission(permission: Permission):
    """Require a specific permission for the current user."""

    def dep(current_user: Annotated[User, Depends(get_current_active_user)]):
        perms = ROLE_PERMISSIONS.get(current_user.role, set())
        if permission not in perms:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permission: {permission}",
            )
        return current_user

    return dep


def require_roles(roles: list[UserRole]):
    """Require a specific role for the current user."""

    def dep(current_user: Annotated[User, Depends(get_current_active_user)]):
        if current_user.role not in roles:
            raise HTTPException(status_code=403, detail="Role not allowed")
        return current_user

    return dep
