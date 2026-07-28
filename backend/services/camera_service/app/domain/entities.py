"""
Camera Service — Domain Entities.

Pure data classes for sites, zones, cameras, and detection module config.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass
class Site:
    """Physical location / facility."""
    id: UUID
    organization_id: UUID
    name: str
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    timezone: str = "UTC"
    created_at: datetime | None = None


@dataclass
class Zone:
    """Logical grouping within a site (e.g., 'Lobby', 'Parking Lot B')."""
    id: UUID
    site_id: UUID
    name: str
    description: str | None = None


@dataclass
class CameraDetectionModule:
    """Per-camera AI module toggle + configuration."""
    camera_id: UUID
    module_code: str          # 'object_detection', 'pose', 'action', etc.
    is_enabled: bool = True
    config: dict = field(default_factory=dict)


@dataclass
class Camera:
    """Registered camera / video source."""
    id: UUID
    site_id: UUID
    zone_id: UUID | None
    name: str
    stream_type: str          # 'rtsp', 'onvif', 'webcam', 'upload'
    stream_url: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    status: str = "offline"   # 'online', 'offline', 'degraded'
    last_heartbeat_at: datetime | None = None
    resolution: str | None = None
    fps: int | None = None
    is_audio_enabled: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None
    # Populated on read
    detection_modules: list[CameraDetectionModule] = field(default_factory=list)
    site: Site | None = None
    zone: Zone | None = None
