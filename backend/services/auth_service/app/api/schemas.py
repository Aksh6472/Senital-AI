"""
Auth Service — Pydantic Schemas (API request/response models).
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# ── Requests ────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class RegisterUserRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=1, max_length=255)
    organization_id: UUID
    role_name: str = Field(default="viewer", max_length=50)
    phone: str | None = Field(default=None, max_length=30)


# ── Responses ───────────────────────────────────────────────────

class PermissionResponse(BaseModel):
    id: UUID
    code: str
    description: str | None = None

    model_config = {"from_attributes": True}


class RoleResponse(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    permissions: list[PermissionResponse] = []

    model_config = {"from_attributes": True}


class OrganizationResponse(BaseModel):
    id: UUID
    name: str
    type: str | None = None

    model_config = {"from_attributes": True}


class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    phone: str | None = None
    is_active: bool
    mfa_enabled: bool
    last_login_at: datetime | None = None
    created_at: datetime | None = None
    role: RoleResponse | None = None
    organization: OrganizationResponse | None = None

    model_config = {"from_attributes": True}


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class RefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LogoutResponse(BaseModel):
    message: str = "Successfully logged out."
