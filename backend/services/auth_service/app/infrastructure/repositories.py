"""
Auth Service — Database Repositories.

Async SQLAlchemy repository layer for users, roles, refresh tokens.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.services.auth_service.app.infrastructure.models import (
    OrganizationModel,
    PermissionModel,
    RefreshTokenModel,
    RoleModel,
    RolePermissionModel,
    UserModel,
)


# ── Helpers ─────────────────────────────────────────────────────

def _hash_token(token: str) -> str:
    """SHA-256 hash of a refresh token for secure storage."""
    return hashlib.sha256(token.encode()).hexdigest()


# ── User Repository ────────────────────────────────────────────

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_email(self, email: str) -> UserModel | None:
        """Fetch user by email with role + permissions eagerly loaded."""
        stmt = (
            select(UserModel)
            .options(
                selectinload(UserModel.role)
                .selectinload(RoleModel.role_permissions)
                .selectinload(RolePermissionModel.permission),
                selectinload(UserModel.organization),
            )
            .where(UserModel.email == email)
            .where(UserModel.deleted_at.is_(None))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: UUID) -> UserModel | None:
        """Fetch user by ID with role + permissions eagerly loaded."""
        stmt = (
            select(UserModel)
            .options(
                selectinload(UserModel.role)
                .selectinload(RoleModel.role_permissions)
                .selectinload(RolePermissionModel.permission),
                selectinload(UserModel.organization),
            )
            .where(UserModel.id == user_id)
            .where(UserModel.deleted_at.is_(None))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, user: UserModel) -> UserModel:
        """Insert a new user."""
        self.db.add(user)
        await self.db.flush()
        return user

    async def update_last_login(self, user_id: UUID) -> None:
        """Stamp last_login_at on successful authentication."""
        stmt = (
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(last_login_at=datetime.now(timezone.utc))
        )
        await self.db.execute(stmt)

    async def list_users(
        self,
        org_id: UUID | None = None,
        is_active: bool | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[UserModel], int]:
        """Paginated user list with optional filters. Returns (items, total)."""
        from sqlalchemy import func

        base = select(UserModel).where(UserModel.deleted_at.is_(None))
        count_base = select(func.count(UserModel.id)).where(UserModel.deleted_at.is_(None))

        if org_id:
            base = base.where(UserModel.organization_id == org_id)
            count_base = count_base.where(UserModel.organization_id == org_id)
        if is_active is not None:
            base = base.where(UserModel.is_active == is_active)
            count_base = count_base.where(UserModel.is_active == is_active)

        # Total count
        total_result = await self.db.execute(count_base)
        total = total_result.scalar() or 0

        # Paginated items
        stmt = (
            base
            .options(
                selectinload(UserModel.role),
                selectinload(UserModel.organization),
            )
            .order_by(UserModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        items = list(result.scalars().all())

        return items, total


# ── Role Repository ────────────────────────────────────────────

class RoleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_name(self, name: str) -> RoleModel | None:
        stmt = select(RoleModel).where(RoleModel.name == name)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, role_id: UUID) -> RoleModel | None:
        stmt = (
            select(RoleModel)
            .options(
                selectinload(RoleModel.role_permissions)
                .selectinload(RolePermissionModel.permission)
            )
            .where(RoleModel.id == role_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(self) -> list[RoleModel]:
        stmt = (
            select(RoleModel)
            .options(
                selectinload(RoleModel.role_permissions)
                .selectinload(RolePermissionModel.permission)
            )
            .order_by(RoleModel.name)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create(self, role: RoleModel) -> RoleModel:
        self.db.add(role)
        await self.db.flush()
        return role


# ── Refresh Token Repository ───────────────────────────────────

class RefreshTokenRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: UUID, raw_token: str, expires_at: datetime) -> RefreshTokenModel:
        """Store a hashed refresh token."""
        token_model = RefreshTokenModel(
            user_id=user_id,
            token_hash=_hash_token(raw_token),
            expires_at=expires_at,
        )
        self.db.add(token_model)
        await self.db.flush()
        return token_model

    async def find_valid_token(self, raw_token: str) -> RefreshTokenModel | None:
        """Look up a non-revoked, non-expired refresh token by its hash."""
        token_hash = _hash_token(raw_token)
        now = datetime.now(timezone.utc)
        stmt = (
            select(RefreshTokenModel)
            .where(RefreshTokenModel.token_hash == token_hash)
            .where(RefreshTokenModel.revoked_at.is_(None))
            .where(RefreshTokenModel.expires_at > now)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def revoke(self, raw_token: str) -> bool:
        """Revoke a refresh token. Returns True if a token was actually revoked."""
        token_hash = _hash_token(raw_token)
        stmt = (
            update(RefreshTokenModel)
            .where(RefreshTokenModel.token_hash == token_hash)
            .where(RefreshTokenModel.revoked_at.is_(None))
            .values(revoked_at=datetime.now(timezone.utc))
        )
        result = await self.db.execute(stmt)
        return result.rowcount > 0

    async def revoke_all_for_user(self, user_id: UUID) -> int:
        """Revoke all active refresh tokens for a user (e.g., on password change)."""
        stmt = (
            update(RefreshTokenModel)
            .where(RefreshTokenModel.user_id == user_id)
            .where(RefreshTokenModel.revoked_at.is_(None))
            .values(revoked_at=datetime.now(timezone.utc))
        )
        result = await self.db.execute(stmt)
        return result.rowcount


# ── Organization Repository ────────────────────────────────────

class OrganizationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, org_id: UUID) -> OrganizationModel | None:
        stmt = select(OrganizationModel).where(OrganizationModel.id == org_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(self) -> list[OrganizationModel]:
        stmt = select(OrganizationModel).order_by(OrganizationModel.name)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create(self, org: OrganizationModel) -> OrganizationModel:
        self.db.add(org)
        await self.db.flush()
        return org
