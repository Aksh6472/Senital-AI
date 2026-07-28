"""
AI Pipeline — Unit & Functional Test Suite.
"""

from __future__ import annotations

import asyncio
from uuid import uuid4
import pytest

from backend.ai_pipeline.base_contracts import DetectionBox, FrameContext
from backend.ai_pipeline.inference_services.object_detection.detector import ObjectDetector
from backend.ai_pipeline.inference_services.tracking.tracker import MultiObjectTracker
from backend.ai_pipeline.inference_services.action_recognition.recognizer import ActionRecognizer
from backend.ai_pipeline.aggregator.confidence_aggregator import ConfidenceAggregator
from backend.ai_pipeline.decision_engine.engine import DecisionEngine
from backend.ai_pipeline.orchestrator import PipelineOrchestrator


def test_stage1_object_detection():
    detector = ObjectDetector(confidence_threshold=0.50)
    ctx = FrameContext(camera_id=uuid4(), site_id=uuid4(), frame_index=1)
    
    simulated = [
        {"class_name": "person", "confidence": 0.85, "bbox": [0.1, 0.1, 0.2, 0.4]},
        {"class_name": "unknown_class", "confidence": 0.99, "bbox": [0.0, 0.0, 0.1, 0.1]},
    ]
    detections = detector.detect(frame=None, context=ctx, simulated_objects=simulated)
    assert len(detections) == 1
    assert detections[0].class_name == "person"
    assert detections[0].confidence == 0.85


def test_stage2_multi_object_tracking():
    tracker = MultiObjectTracker(iou_threshold=0.30)
    ctx1 = FrameContext(camera_id=uuid4(), site_id=uuid4(), frame_index=1)
    ctx2 = FrameContext(camera_id=uuid4(), site_id=uuid4(), frame_index=2)

    det1 = [DetectionBox(class_name="person", confidence=0.90, bbox=[0.10, 0.10, 0.20, 0.40])]
    tracks1 = tracker.update(det1, ctx1)
    assert len(tracks1) == 1
    initial_id = tracks1[0].track_id

    det2 = [DetectionBox(class_name="person", confidence=0.92, bbox=[0.12, 0.10, 0.20, 0.40])]
    tracks2 = tracker.update(det2, ctx2)
    assert len(tracks2) == 1
    assert tracks2[0].track_id == initial_id
    assert len(tracks2[0].history) == 2


def test_stage3_action_recognition_fall():
    recognizer = ActionRecognizer()
    ctx = FrameContext(camera_id=uuid4(), site_id=uuid4(), frame_index=1)
    
    from backend.ai_pipeline.base_contracts import TrackedObject
    tracked_person = TrackedObject(
        track_id=1,
        class_name="person",
        confidence=0.88,
        bbox=[0.3, 0.4, 0.4, 0.2],
        velocity=[0.0, 0.06],
    )
    actions = recognizer.analyze_actions([tracked_person], [], ctx)
    assert len(actions) == 1
    assert actions[0].action_code == "fall_collapse"


def test_stage4_single_frame_noise_suppression():
    aggregator = ConfidenceAggregator(window_size=10, min_consensus_ratio=0.40)
    cam_id = uuid4()
    site_id = uuid4()

    for f in range(10):
        ctx = FrameContext(camera_id=cam_id, site_id=site_id, frame_index=f)
        dets = [DetectionBox("weapon", 0.95, [0.1, 0.1, 0.1, 0.1])] if f == 5 else []
        sig = aggregator.push_and_aggregate(dets, [], [], ctx)

    assert len(sig.detected_objects) == 0
    assert sig.aggregated_confidence == 0.0


@pytest.mark.asyncio
async def test_end_to_end_pipeline_weapon_incident():
    orchestrator = PipelineOrchestrator()
    cam_id = uuid4()
    site_id = uuid4()

    simulated_frame_data = [
        {"class_name": "person", "confidence": 0.90, "bbox": [0.2, 0.2, 0.2, 0.5]},
        {"class_name": "weapon", "confidence": 0.85, "bbox": [0.22, 0.25, 0.08, 0.08]},
    ]

    final_decision = None
    for f in range(15):
        ctx = FrameContext(camera_id=cam_id, site_id=site_id, frame_index=f)
        final_decision = await orchestrator.process_frame(
            frame=None, context=ctx, simulated_objects=simulated_frame_data
        )

    assert final_decision is not None
    assert final_decision.should_alert is True
    assert final_decision.incident_type_code == "weapon_threat"
    assert final_decision.severity == "critical"
    assert "Incident 'weapon_threat' flagged" in final_decision.ai_explanation
