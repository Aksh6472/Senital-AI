"""
Incident Service — SQLAlchemy ORM Models.

Maps to schemas §3 and §4.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import relationship

from backend.services.shared.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class IncidentTypeModel(Base):
    __tablename__ = "incident_types"

    code = Column(String(50), primary_key=True)
    category = Column(String(50), nullable=False)
    display_name = Column(String(100), nullable=False)
    default_severity = Column(String(20), nullable=False)
    default_response = Column(Text)


class IncidentModel(Base):
    __tablename__ = "incidents"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_type_code = Column(String(50), ForeignKey("incident_types.code"), nullable=False)
    camera_id = Column(PG_UUID(as_uuid=True), ForeignKey("cameras.id"), nullable=False)
    site_id = Column(PG_UUID(as_uuid=True), ForeignKey("sites.id"), nullable=False)
    status = Column(String(20), nullable=False, default="open")
    confidence_score = Column(Numeric(5, 2), nullable=False)
    severity = Column(String(20), nullable=False)
    priority = Column(String(20), nullable=False)
    detected_objects = Column(JSONB, nullable=False, default=list)
    detected_actions = Column(JSONB, nullable=False, default=list)
    ai_explanation = Column(Text)
    recommended_response = Column(Text)
    detected_at = Column(DateTime(timezone=True), nullable=False)
    confirmed_by = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"))
    confirmed_at = Column(DateTime(timezone=True))
    resolved_at = Column(DateTime(timezone=True))
    latitude = Column(String(20))
    longitude = Column(String(20))
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow)

    # Relationships
    incident_type = relationship("IncidentTypeModel", lazy="selectin")
    evidence = relationship("EvidenceModel", back_populates="incident", cascade="all, delete-orphan")


class EvidenceModel(Base):
    __tablename__ = "evidence"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id = Column(PG_UUID(as_uuid=True), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False)
    evidence_type = Column(String(20), nullable=False)
    storage_url = Column(Text, nullable=False)
    buffer_segment = Column(String(20), nullable=False)
    duration_seconds = Column(Integer)
    checksum_sha256 = Column(String(64), nullable=False)
    metadata_ = Column("metadata", JSONB, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)

    incident = relationship("IncidentModel", back_populates="evidence")


class AIModelVersionModel(Base):
    __tablename__ = "ai_model_versions"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_family = Column(String(50), nullable=False)
    model_name = Column(String(100), nullable=False)
    version = Column(String(50), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    metadata_ = Column("metadata", JSONB, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)
