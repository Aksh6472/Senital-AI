"""
Auth Service — Domain Entities.

Pure data classes representing the identity & access domain.
No ORM or framework dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass
class Permission:
    """A single permission like 'camera:read' or 'incident:write'."""
    id: UUID
    code: str
    description: str | None = None


@dataclass
class Role:
    """Named role with a set of permissions."""
    id: UUID
    name: str
    description: str | None = None
    created_at: datetime | None = None
    permissions: list[Permission] = field(default_factory=list)


@dataclass
class Organization:
    """Top-level tenant / org."""
    id: UUID
    name: str
    type: str | None = None
    created_at: datetime | None = None


@dataclass
class User:
    """Registered platform user."""
    id: UUID
    organization_id: UUID
    email: str
    full_name: str
    password_hash: str
    phone: str | None = None
    role_id: UUID | None = None
    is_active: bool = True
    mfa_enabled: bool = False
    last_login_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None
    # Populated at runtime after auth middleware loads permissions
    role: Role | None = None
    organization: Organization | None = None


@dataclass
class RefreshToken:
    """Opaque refresh token stored server-side."""
    id: UUID
    user_id: UUID
    token_hash: str
    expires_at: datetime
    revoked_at: datetime | None = None
    created_at: datetime | None = None
