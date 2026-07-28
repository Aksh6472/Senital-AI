"""
Auth Service — SQLAlchemy ORM models.

Maps exactly to the Identity & Access tables in 04_database_schema.sql §1.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from backend.services.shared.database import Base


# ── Helper ──────────────────────────────────────────────────────
def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ── Roles & Permissions ────────────────────────────────────────

class RoleModel(Base):
    __tablename__ = "roles"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)

    # Relationships
    role_permissions = relationship("RolePermissionModel", back_populates="role", lazy="selectin")
    users = relationship("UserModel", back_populates="role")


class PermissionModel(Base):
    __tablename__ = "permissions"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(100), unique=True, nullable=False)
    description = Column(Text)

    # Relationships
    role_permissions = relationship("RolePermissionModel", back_populates="permission")


class RolePermissionModel(Base):
    __tablename__ = "role_permissions"

    role_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    )
    permission_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    )

    # Relationships
    role = relationship("RoleModel", back_populates="role_permissions")
    permission = relationship("PermissionModel", back_populates="role_permissions", lazy="selectin")


# ── Organizations ───────────────────────────────────────────────

class OrganizationModel(Base):
    __tablename__ = "organizations"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    type = Column(String(50))
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)

    # Relationships
    users = relationship("UserModel", back_populates="organization")
    sites = relationship("SiteModel", back_populates="organization")


# ── Users ───────────────────────────────────────────────────────

class UserModel(Base):
    __tablename__ = "users"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(30))
    role_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("roles.id"),
        nullable=False,
    )
    is_active = Column(Boolean, nullable=False, default=True)
    mfa_enabled = Column(Boolean, nullable=False, default=False)
    last_login_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow)
    deleted_at = Column(DateTime(timezone=True))

    # Relationships
    role = relationship("RoleModel", back_populates="users", lazy="selectin")
    organization = relationship("OrganizationModel", back_populates="users", lazy="selectin")
    refresh_tokens = relationship("RefreshTokenModel", back_populates="user", cascade="all, delete-orphan")


# ── Refresh Tokens ──────────────────────────────────────────────

class RefreshTokenModel(Base):
    __tablename__ = "refresh_tokens"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    token_hash = Column(String(255), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)

    # Relationships
    user = relationship("UserModel", back_populates="refresh_tokens")
