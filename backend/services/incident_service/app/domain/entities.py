"""
Incident & Evidence Service — Domain Entities.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass
class IncidentType:
    code: str
    category: str
    display_name: str
    default_severity: str
    default_response: str | None = None


@dataclass
class Evidence:
    id: UUID
    incident_id: UUID
    evidence_type: str
    storage_url: str
    buffer_segment: str
    checksum_sha256: str
    duration_seconds: int | None = None
    metadata: dict = field(default_factory=dict)
    created_at: datetime | None = None


@dataclass
class Incident:
    id: UUID
    incident_type_code: str
    camera_id: UUID
    site_id: UUID
    status: str
    confidence_score: float
    severity: str
    priority: str
    detected_objects: list = field(default_factory=list)
    detected_actions: list = field(default_factory=list)
    ai_explanation: str | None = None
    recommended_response: str | None = None
    detected_at: datetime | None = None
    confirmed_by: UUID | None = None
    confirmed_at: datetime | None = None
    resolved_at: datetime | None = None
    latitude: float | None = None
    longitude: float | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    incident_type: IncidentType | None = None
    evidence: list[Evidence] = field(default_factory=list)
