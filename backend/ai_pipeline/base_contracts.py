"""
AI Pipeline — Core Base Contracts & Dataclasses.

Defines unified data models passed across pipeline stages:
Detection -> Tracking -> Action Recognition -> Confidence Aggregation -> Decision Engine.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4


@dataclass
class AIModelVersionInfo:
    """Model identity & audit metadata (FR-4.2 / schema §3)."""
    id: UUID = field(default_factory=uuid4)
    model_family: str = "object_detection"
    model_name: str = "YOLOv11-Sentinel"
    version: str = "v1.0.0"
    is_active: bool = True


@dataclass
class DetectionBox:
    """Single spatial object detection bounding box."""
    class_name: str          # 'person', 'vehicle', 'weapon', 'fire_smoke', 'suspicious_package'
    confidence: float        # 0.0 to 1.0
    bbox: list[float]        # [x_min, y_min, width, height] normalized (0.0 to 1.0)
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass
class TrackedObject:
    """Object maintained across continuous frame sequences via tracking."""
    track_id: int
    class_name: str
    confidence: float
    bbox: list[float]
    velocity: list[float] = field(default_factory=lambda: [0.0, 0.0])  # [dx, dy] per frame
    history: list[list[float]] = field(default_factory=list)          # Trajectory points [(x, y), ...]
    first_seen_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_seen_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ActionResult:
    """Temporal action / posture classification result."""
    action_code: str         # 'loitering', 'running_panic', 'fall_collapse', 'fighting_gesture', 'perimeter_breach', 'weapon_brandishing'
    confidence: float
    target_track_id: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class FrameContext:
    """Context accompanying a video frame through the pipeline."""
    camera_id: UUID
    site_id: UUID
    frame_index: int
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    active_modules_config: dict[str, Any] = field(default_factory=dict)


@dataclass
class AggregatedFrameSignal:
    """Output of Stage 4 (Confidence Aggregator) across temporal window T."""
    camera_id: UUID
    site_id: UUID
    window_start: datetime
    window_end: datetime
    sample_count: int
    detected_objects: list[dict[str, Any]]
    detected_actions: list[dict[str, Any]]
    aggregated_confidence: float
    tracked_subjects_count: int
    model_version: AIModelVersionInfo = field(default_factory=AIModelVersionInfo)


@dataclass
class DecisionResult:
    """Output of Stage 5 (Decision Engine) ready for Incident creation."""
    should_alert: bool
    incident_type_code: str | None = None
    severity: str = "medium"               # 'critical', 'high', 'medium', 'low'
    priority: str = "P2"                   # 'P1', 'P2', 'P3', 'P4'
    confidence_score: float = 0.0
    ai_explanation: str = ""
    recommended_response: str = ""
    detected_objects: list[dict[str, Any]] = field(default_factory=list)
    detected_actions: list[dict[str, Any]] = field(default_factory=list)
    multi_signal_corroborated: bool = False
