"""
AI Pipeline — Orchestrator & Event-Bus Adapter Interface.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from backend.ai_pipeline.aggregator.confidence_aggregator import ConfidenceAggregator
from backend.ai_pipeline.base_contracts import DecisionResult, FrameContext
from backend.ai_pipeline.decision_engine.engine import DecisionEngine
from backend.ai_pipeline.inference_services.action_recognition.recognizer import ActionRecognizer
from backend.ai_pipeline.inference_services.object_detection.detector import ObjectDetector
from backend.ai_pipeline.inference_services.tracking.tracker import MultiObjectTracker


class EventBusProducer:
    def __init__(self, topic_prefix: str = "sentinel.ai"):
        self.topic_prefix = topic_prefix

    async def publish_event(self, topic: str, payload: dict[str, Any]) -> bool:
        full_topic = f"{self.topic_prefix}.{topic}"
        return True


class PipelineOrchestrator:
    def __init__(
        self,
        event_bus: EventBusProducer | None = None,
        global_confidence_threshold: float = 0.60,
    ):
        self.event_bus = event_bus or EventBusProducer()
        self.detector = ObjectDetector(confidence_threshold=0.50)
        self.tracker = MultiObjectTracker(iou_threshold=0.30)
        self.action_recognizer = ActionRecognizer()
        self.aggregator = ConfidenceAggregator(window_size=15)
        self.decision_engine = DecisionEngine(global_confidence_threshold=global_confidence_threshold)

    async def process_frame(
        self,
        frame: Any,
        context: FrameContext,
        simulated_objects: list[dict[str, Any]] | None = None,
    ) -> DecisionResult:
        detections = self.detector.detect(
            frame=frame,
            context=context,
            simulated_objects=simulated_objects,
        )

        tracked_objects = self.tracker.update(
            detections=detections,
            context=context,
        )

        actions = self.action_recognizer.analyze_actions(
            tracked_objects=tracked_objects,
            detections=detections,
            context=context,
        )

        aggregated_signal = self.aggregator.push_and_aggregate(
            detections=detections,
            tracked_objects=tracked_objects,
            actions=actions,
            context=context,
        )

        decision = self.decision_engine.evaluate(
            signal=aggregated_signal,
            context=context,
        )

        if decision.should_alert:
            event_payload = {
                "event_id": str(uuid4()),
                "camera_id": str(context.camera_id),
                "site_id": str(context.site_id),
                "incident_type": decision.incident_type_code,
                "severity": decision.severity,
                "confidence": decision.confidence_score,
                "ai_explanation": decision.ai_explanation,
                "model_version_id": str(self.detector.model_info.id),
                "multi_signal_corroborated": decision.multi_signal_corroborated,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            await self.event_bus.publish_event("incidents.detected", event_payload)

        return decision
