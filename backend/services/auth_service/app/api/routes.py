"""
Auth Service — FastAPI Router.

Endpoints:
    POST /api/v1/auth/login       → Email/password → access + refresh token
    POST /api/v1/auth/refresh     → Refresh token → new access token
    POST /api/v1/auth/logout      → Revoke refresh token
    GET  /api/v1/auth/me          → Current user profile + permissions
    POST /api/v1/auth/register    → Register new user (admin only)
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.auth_service.app.api.schemas import (
    LoginRequest,
    LoginResponse,
    LogoutRequest,
    LogoutResponse,
    RefreshRequest,
    RefreshResponse,
    RegisterUserRequest,
    UserResponse,
)
from backend.services.auth_service.app.application.auth_service import AuthService
from backend.services.shared.auth_middleware import get_current_user, require_permission
from backend.services.shared.database import get_db

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ── POST /auth/login ───────────────────────────────────────────

@router.post("/login", response_model=LoginResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate with email + password. Returns JWT access & refresh tokens."""
    svc = AuthService(db)
    result = await svc.login(email=body.email, password=body.password)

    return LoginResponse(
        access_token=result["access_token"],
        refresh_token=result["refresh_token"],
        token_type=result["token_type"],
        user=UserResponse.model_validate(result["user"]),
    )


# ── POST /auth/refresh ─────────────────────────────────────────

@router.post("/refresh", response_model=RefreshResponse)
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """Exchange a valid refresh token for a new access token."""
    svc = AuthService(db)
    result = await svc.refresh(refresh_token=body.refresh_token)

    return RefreshResponse(
        access_token=result["access_token"],
        token_type=result["token_type"],
    )


# ── POST /auth/logout ──────────────────────────────────────────

@router.post("/logout", response_model=LogoutResponse)
async def logout(body: LogoutRequest, db: AsyncSession = Depends(get_db)):
    """Revoke a refresh token (invalidate session)."""
    svc = AuthService(db)
    await svc.logout(refresh_token=body.refresh_token)
    return LogoutResponse()


# ── GET /auth/me ────────────────────────────────────────────────

@router.get("/me", response_model=UserResponse)
async def get_me(current_user=Depends(get_current_user)):
    """Return current authenticated user's profile, role, and permissions."""
    return UserResponse.model_validate(current_user)


# ── POST /auth/register ────────────────────────────────────────

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201,
    dependencies=[Depends(require_permission("user:create"))],
)
async def register_user(
    body: RegisterUserRequest,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user. Requires 'user:create' permission (admin only)."""
    svc = AuthService(db)
    user = await svc.register_user(
        email=body.email,
        password=body.password,
        full_name=body.full_name,
        organization_id=body.organization_id,
        role_name=body.role_name,
        phone=body.phone,
    )
    return UserResponse.model_validate(user)
