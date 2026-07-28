"""
Sentinel AI — JWT Authentication & RBAC Middleware.

Provides FastAPI dependencies:
    - get_current_user   → decodes JWT and returns the user row
    - require_permission → factory that returns a dependency checking a specific permission code
"""

from datetime import datetime, timedelta, timezone
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.services.shared.config import settings
from backend.services.shared.database import get_db
from backend.services.shared.exceptions import UnauthorizedError, ForbiddenError


# ── Token helpers ───────────────────────────────────────────────

def create_access_token(user_id: str, role_name: str) -> str:
    """Create a short-lived JWT access token."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "role": role_name,
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_expire_minutes),
        "type": "access",
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(user_id: str) -> tuple[str, datetime]:
    """Create a long-lived refresh token. Returns (token_string, expires_at)."""
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(days=settings.refresh_token_expire_days)
    payload = {
        "sub": user_id,
        "iat": now,
        "exp": expires_at,
        "type": "refresh",
    }
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return token, expires_at


def decode_token(token: str) -> dict:
    """Decode and validate a JWT. Raises UnauthorizedError on failure."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except JWTError:
        raise UnauthorizedError(detail="Invalid or expired token.")


# ── FastAPI Dependencies ────────────────────────────────────────

async def get_current_user(
    authorization: Annotated[str, Header()],
    db: AsyncSession = Depends(get_db),
):
    """
    Decode the Bearer token, load the user from DB, and return the ORM object.
    Attaches `user.permissions` (list of permission codes) for downstream RBAC checks.
    """
    # Lazy import to avoid circular deps at module level
    from backend.services.auth_service.app.infrastructure.models import (
        UserModel,
        RoleModel,
        RolePermissionModel,
        PermissionModel,
    )

    if not authorization.startswith("Bearer "):
        raise UnauthorizedError(detail="Authorization header must start with 'Bearer '.")

    token = authorization[7:]
    payload = decode_token(token)

    if payload.get("type") != "access":
        raise UnauthorizedError(detail="Invalid token type. Access token required.")

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedError(detail="Token missing subject claim.")

    # Load user + role + permissions in one query
    stmt = (
        select(UserModel)
        .options(
            selectinload(UserModel.role)
            .selectinload(RoleModel.role_permissions)
            .selectinload(RolePermissionModel.permission)
        )
        .where(UserModel.id == UUID(user_id))
        .where(UserModel.is_active.is_(True))
        .where(UserModel.deleted_at.is_(None))
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise UnauthorizedError(detail="User not found or deactivated.")

    # Attach flat permission codes for easy checking
    user.permission_codes = [
        rp.permission.code
        for rp in user.role.role_permissions
    ]
    return user


def require_permission(permission_code: str):
    """
    Factory that returns a FastAPI dependency ensuring the current user
    has a specific permission code.

    Usage:
        @router.get("/cameras", dependencies=[Depends(require_permission("camera:read"))])
    """
    async def _check(current_user=Depends(get_current_user)):
        if permission_code not in current_user.permission_codes:
            raise ForbiddenError(
                detail=f"Permission '{permission_code}' required."
            )
        return current_user

    return _check
