"""
Notification Service — SQLAlchemy ORM Models.

Maps to schema §6.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID

from backend.services.shared.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class NotificationPolicyModel(Base):
    __tablename__ = "notification_policies"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(PG_UUID(as_uuid=True), ForeignKey("sites.id", ondelete="CASCADE"), nullable=False)
    incident_type_code = Column(String(50), ForeignKey("incident_types.code"), nullable=False)
    requires_confirmation = Column(Boolean, nullable=False, default=True)
    auto_escalate_threshold = Column(Numeric(5, 2))
    recipients = Column(JSONB, nullable=False, default=list)
    channels = Column(JSONB, nullable=False, default=list)


class NotificationModel(Base):
    __tablename__ = "notifications"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id = Column(PG_UUID(as_uuid=True), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False)
    channel = Column(String(20), nullable=False)
    recipient = Column(String(255), nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    sent_at = Column(DateTime(timezone=True))
    delivered_at = Column(DateTime(timezone=True))
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)
