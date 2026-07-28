"""
Notification Service — Domain Entities.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass
class NotificationPolicy:
    id: UUID
    site_id: UUID
    incident_type_code: str
    requires_confirmation: bool
    auto_escalate_threshold: float | None = None
    recipients: list = field(default_factory=list)
    channels: list = field(default_factory=list)


@dataclass
class Notification:
    id: UUID
    incident_id: UUID
    channel: str
    recipient: str
    status: str
    sent_at: datetime | None = None
    delivered_at: datetime | None = None
    error_message: str | None = None
    created_at: datetime | None = None
