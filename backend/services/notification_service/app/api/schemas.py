"""
Notification Service — Pydantic Schemas.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class NotificationPolicyResponse(BaseModel):
    id: UUID
    site_id: UUID
    incident_type_code: str
    requires_confirmation: bool
    auto_escalate_threshold: float | None = None
    recipients: list = []
    channels: list = []

    model_config = {"from_attributes": True}


class UpdateNotificationPolicyRequest(BaseModel):
    requires_confirmation: bool | None = None
    auto_escalate_threshold: float | None = None
    recipients: list | None = None
    channels: list | None = None


class NotificationResponse(BaseModel):
    id: UUID
    incident_id: UUID
    channel: str
    recipient: str
    status: str
    sent_at: datetime | None = None
    delivered_at: datetime | None = None
    error_message: str | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}
