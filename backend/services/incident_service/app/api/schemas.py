"""
Incident Service — Pydantic Schemas.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class IncidentTypeResponse(BaseModel):
    code: str
    category: str
    display_name: str
    default_severity: str
    default_response: str | None = None

    model_config = {"from_attributes": True}


class EvidenceResponse(BaseModel):
    id: UUID
    incident_id: UUID
    evidence_type: str
    storage_url: str
    buffer_segment: str
    duration_seconds: int | None = None
    checksum_sha256: str
    metadata_: dict = Field(alias="metadata", default_factory=dict)
    created_at: datetime | None = None

    model_config = {"from_attributes": True, "populate_by_name": True}


class IncidentResponse(BaseModel):
    id: UUID
    incident_type_code: str
    camera_id: UUID
    site_id: UUID
    status: str
    confidence_score: float
    severity: str
    priority: str
    detected_objects: list = []
    detected_actions: list = []
    ai_explanation: str | None = None
    recommended_response: str | None = None
    detected_at: datetime | None = None
    confirmed_by: UUID | None = None
    confirmed_at: datetime | None = None
    resolved_at: datetime | None = None
    latitude: str | None = None
    longitude: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    
    incident_type: IncidentTypeResponse | None = None
    evidence: list[EvidenceResponse] = []

    model_config = {"from_attributes": True}


class DismissIncidentRequest(BaseModel):
    is_false_positive: bool = False
