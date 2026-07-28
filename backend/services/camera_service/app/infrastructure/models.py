"""
Camera Service — SQLAlchemy ORM Models.

Maps to the Sites, Zones & Cameras tables in 04_database_schema.sql §2.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    SmallInteger,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import relationship

from backend.services.shared.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ── Sites ───────────────────────────────────────────────────────

class SiteModel(Base):
    __tablename__ = "sites"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    name = Column(String(255), nullable=False)
    address = Column(Text)
    # PostGIS GEOGRAPHY stored as lat/lon text for portability;
    # in production, use GeoAlchemy2 for proper geography columns.
    latitude = Column(String(20))
    longitude = Column(String(20))
    timezone = Column(String(64), nullable=False, default="UTC")
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)

    # Relationships
    organization = relationship("OrganizationModel", back_populates="sites")
    zones = relationship("ZoneModel", back_populates="site", cascade="all, delete-orphan")
    cameras = relationship("CameraModel", back_populates="site", cascade="all, delete-orphan")


# ── Zones ───────────────────────────────────────────────────────

class ZoneModel(Base):
    __tablename__ = "zones"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("sites.id", ondelete="CASCADE"),
        nullable=False,
    )
    name = Column(String(255), nullable=False)
    description = Column(Text)

    # Relationships
    site = relationship("SiteModel", back_populates="zones")
    cameras = relationship("CameraModel", back_populates="zone")


# ── Cameras ─────────────────────────────────────────────────────

class CameraModel(Base):
    __tablename__ = "cameras"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("sites.id", ondelete="CASCADE"),
        nullable=False,
    )
    zone_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("zones.id", ondelete="SET NULL"),
    )
    name = Column(String(255), nullable=False)
    stream_type = Column(String(20), nullable=False)  # rtsp, onvif, webcam, upload
    stream_url = Column(Text)
    latitude = Column(String(20))
    longitude = Column(String(20))
    status = Column(String(20), nullable=False, default="offline")
    last_heartbeat_at = Column(DateTime(timezone=True))
    resolution = Column(String(20))
    fps = Column(SmallInteger)
    is_audio_enabled = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow)
    deleted_at = Column(DateTime(timezone=True))

    # Relationships
    site = relationship("SiteModel", back_populates="cameras", lazy="selectin")
    zone = relationship("ZoneModel", back_populates="cameras", lazy="selectin")
    detection_modules = relationship(
        "CameraDetectionModuleModel",
        back_populates="camera",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


# ── Camera Detection Modules ───────────────────────────────────

class CameraDetectionModuleModel(Base):
    __tablename__ = "camera_detection_modules"

    camera_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("cameras.id", ondelete="CASCADE"),
        primary_key=True,
    )
    module_code = Column(String(50), primary_key=True)
    is_enabled = Column(Boolean, nullable=False, default=True)
    config = Column(JSONB, nullable=False, default=dict)

    # Relationships
    camera = relationship("CameraModel", back_populates="detection_modules")
