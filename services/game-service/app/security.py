# Module 6 — used when you add JWT validation to game-service.
# Nothing to implement here. Your task is to wire require_admin into the
# DELETE /v1/games/{id} endpoint in main.py as a FastAPI dependency.
#
# Before this file will work you need to add one setting to your config.py:
#
#   auth_secret_key: str = "dev-secret-change-in-production"
#
# It must match the SECRET_KEY in auth-service — that's how game-service can
# verify a token without ever calling auth-service.

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.config import settings

bearer_scheme = HTTPBearer()


async def require_admin(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    """
    FastAPI dependency — verifies the JWT and asserts the caller has the admin role.

    Usage in main.py:
        from app.security import require_admin

        @app.delete("/v1/games/{game_id}", dependencies=[Depends(require_admin)])
        async def delete_game(game_id: str, ...):
            ...

    Returns the decoded token payload if valid and role == "admin".
    Raises 403 if the token is valid but the role is not admin.
    Raises 401 if the token is missing, expired, or tampered with.

    Note: 401 means "I don't know who you are".
          403 means "I know who you are, but you can't do this".
    """
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.auth_secret_key,
            algorithms=["HS256"],
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    if payload.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )

    return payload