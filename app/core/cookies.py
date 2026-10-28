"""app/core/cookies.py: HTTP cookie handling for auth tokens (API layer only)."""

from fastapi import Response

from app.core.config import settings

# The refresh token is only needed by the auth routes, so don't send it with
# every API request.
REFRESH_COOKIE_PATH = "/v1/auth"

_COMMON = {"httponly": True, "samesite": "lax", "secure": True}


def set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_SECONDS,
        **_COMMON,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_SECONDS,
        path=REFRESH_COOKIE_PATH,
        **_COMMON,
    )


def clear_auth_cookies(response: Response) -> None:
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token", path=REFRESH_COOKIE_PATH)
    # Also clear the old root-path cookie for users logged in before the path
    # change. Safe to remove once those sessions have expired.
    response.delete_cookie("refresh_token", path="/")
