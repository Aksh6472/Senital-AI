"""
Auth Service — Application / Use-Case Layer.

Orchestrates login, refresh, logout, and user registration business logic.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.auth_service.app.infrastructure.models import UserModel
from backend.services.auth_service.app.infrastructure.repositories import (
    OrganizationRepository,
    RefreshTokenRepository,
    RoleRepository,
    UserRepository,
)
from backend.services.shared.auth_middleware import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from backend.services.shared.exceptions import (
    BadRequestError,
    ConflictError,
    NotFoundError,
    UnauthorizedError,
)

# ── Password hashing ───────────────────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Core authentication & user-management use cases."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.role_repo = RoleRepository(db)
        self.token_repo = RefreshTokenRepository(db)
        self.org_repo = OrganizationRepository(db)

    # ── Login ───────────────────────────────────────────────────

    async def login(self, email: str, password: str) -> dict:
        """
        Authenticate user by email + password.
        Returns {access_token, refresh_token, token_type, user}.
        """
        user = await self.user_repo.get_by_email(email)

        if user is None:
            raise UnauthorizedError(detail="Invalid email or password.")

        if not user.is_active:
            raise UnauthorizedError(detail="Account is deactivated.")

        if not pwd_context.verify(password, user.password_hash):
            raise UnauthorizedError(detail="Invalid email or password.")

        # Issue tokens
        access_token = create_access_token(
            user_id=str(user.id),
            role_name=user.role.name,
        )
        refresh_token_str, refresh_expires_at = create_refresh_token(
            user_id=str(user.id),
        )

        # Persist refresh token hash
        await self.token_repo.create(
            user_id=user.id,
            raw_token=refresh_token_str,
            expires_at=refresh_expires_at,
        )

        # Update last login
        await self.user_repo.update_last_login(user.id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token_str,
            "token_type": "bearer",
            "user": user,
        }

    # ── Refresh ─────────────────────────────────────────────────

    async def refresh(self, refresh_token: str) -> dict:
        """
        Validate refresh token and issue a new access token.
        The refresh token itself is NOT rotated (long-lived by design).
        """
        # Verify the JWT signature and expiry
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise UnauthorizedError(detail="Invalid token type. Refresh token required.")

        # Verify the token hash is stored and not revoked
        stored = await self.token_repo.find_valid_token(refresh_token)
        if stored is None:
            raise UnauthorizedError(detail="Refresh token revoked or expired.")

        # Load user
        user_id = UUID(payload["sub"])
        user = await self.user_repo.get_by_id(user_id)
        if user is None or not user.is_active:
            raise UnauthorizedError(detail="User not found or deactivated.")

        # Issue new access token
        access_token = create_access_token(
            user_id=str(user.id),
            role_name=user.role.name,
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
        }

    # ── Logout ──────────────────────────────────────────────────

    async def logout(self, refresh_token: str) -> bool:
        """Revoke a single refresh token."""
        revoked = await self.token_repo.revoke(refresh_token)
        return revoked

    # ── Get Current User Profile ────────────────────────────────

    async def get_user_profile(self, user_id: UUID) -> UserModel:
        """Load user with role, permissions, and organization."""
        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise NotFoundError(entity="User", entity_id=str(user_id))
        return user

    # ── Register User ──────────────────────────────────────────

    async def register_user(
        self,
        email: str,
        password: str,
        full_name: str,
        organization_id: UUID,
        role_name: str = "viewer",
        phone: str | None = None,
    ) -> UserModel:
        """
        Register a new user. Typically called by an admin.
        Validates org exists, role exists, email not taken.
        """
        # Check email uniqueness
        existing = await self.user_repo.get_by_email(email)
        if existing is not None:
            raise ConflictError(detail=f"Email '{email}' is already registered.")

        # Validate organization
        org = await self.org_repo.get_by_id(organization_id)
        if org is None:
            raise NotFoundError(entity="Organization", entity_id=str(organization_id))

        # Resolve role
        role = await self.role_repo.get_by_name(role_name)
        if role is None:
            raise BadRequestError(detail=f"Role '{role_name}' does not exist.")

        # Create user
        user = UserModel(
            email=email,
            password_hash=pwd_context.hash(password),
            full_name=full_name,
            organization_id=organization_id,
            role_id=role.id,
            phone=phone,
        )
        user = await self.user_repo.create(user)

        # Reload with relationships
        return await self.user_repo.get_by_id(user.id)
