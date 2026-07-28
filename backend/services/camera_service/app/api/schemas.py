"""
Camera Service — Pydantic Schemas (API request/response models).
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


# ── Request schemas ─────────────────────────────────────────────

class CreateCameraRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    site_id: UUID
    stream_type: str = Field(..., pattern=r"^(rtsp|onvif|webcam|upload)$")
    stream_url: str | None = None
    zone_id: UUID | None = None
    latitude: str | None = None
    longitude: str | None = None
    resolution: str | None = Field(default=None, max_length=20)
    fps: int | None = Field(default=None, ge=1, le=120)
    is_audio_enabled: bool = False


class UpdateCameraRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    stream_type: str | None = Field(default=None, pattern=r"^(rtsp|onvif|webcam|upload)$")
    stream_url: str | None = None
    zone_id: UUID | None = None
    latitude: str | None = None
    longitude: str | None = None
    resolution: str | None = None
    fps: int | None = Field(default=None, ge=1, le=120)
    is_audio_enabled: bool | None = None
    status: str | None = Field(default=None, pattern=r"^(online|offline|degraded)$")


class DetectionModuleConfig(BaseModel):
    module_code: str = Field(..., max_length=50)
    is_enabled: bool = True
    config: dict = Field(default_factory=dict)


class ConfigureDetectionModulesRequest(BaseModel):
    modules: list[DetectionModuleConfig]


# ── Response schemas ────────────────────────────────────────────

class SiteResponse(BaseModel):
    id: UUID
    organization_id: UUID
    name: str
    address: str | None = None
    latitude: str | None = None
    longitude: str | None = None
    timezone: str
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class ZoneResponse(BaseModel):
    id: UUID
    site_id: UUID
    name: str
    description: str | None = None

    model_config = {"from_attributes": True}


class DetectionModuleResponse(BaseModel):
    camera_id: UUID
    module_code: str
    is_enabled: bool
    config: dict

    model_config = {"from_attributes": True}


class CameraResponse(BaseModel):
    id: UUID
    site_id: UUID
    zone_id: UUID | None = None
    name: str
    stream_type: str
    stream_url: str | None = None
    latitude: str | None = None
    longitude: str | None = None
    status: str
    last_heartbeat_at: datetime | None = None
    resolution: str | None = None
    fps: int | None = None
    is_audio_enabled: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None
    site: SiteResponse | None = None
    zone: ZoneResponse | None = None
    detection_modules: list[DetectionModuleResponse] = []

    model_config = {"from_attributes": True}


class CameraHealthResponse(BaseModel):
    camera_id: UUID
    status: str
    last_heartbeat_at: datetime | None = None
    resolution: str | None = None
    fps: int | None = None
    is_audio_enabled: bool
    active_detection_modules: list[str] = []
