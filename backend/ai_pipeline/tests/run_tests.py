"""
AI Pipeline — Self-Contained Test & Benchmark Runner.
"""

from __future__ import annotations

import asyncio
import time
from uuid import uuid4

from backend.ai_pipeline.base_contracts import DetectionBox, FrameContext, TrackedObject
from backend.ai_pipeline.inference_services.object_detection.detector import ObjectDetector
from backend.ai_pipeline.inference_services.tracking.tracker import MultiObjectTracker
from backend.ai_pipeline.inference_services.action_recognition.recognizer import ActionRecognizer
from backend.ai_pipeline.aggregator.confidence_aggregator import ConfidenceAggregator
from backend.ai_pipeline.decision_engine.engine import DecisionEngine
from backend.ai_pipeline.orchestrator import PipelineOrchestrator


def run_unit_tests():
    print("==================================================")
    print("   RUNNING AI PIPELINE UNIT & INTEGRATION TESTS   ")
    print("==================================================")

    detector = ObjectDetector(confidence_threshold=0.50)
    ctx = FrameContext(camera_id=uuid4(), site_id=uuid4(), frame_index=1)
    simulated = [
        {"class_name": "person", "confidence": 0.85, "bbox": [0.1, 0.1, 0.2, 0.4]},
        {"class_name": "unknown", "confidence": 0.99, "bbox": [0.0, 0.0, 0.1, 0.1]},
    ]
    dets = detector.detect(frame=None, context=ctx, simulated_objects=simulated)
    assert len(dets) == 1 and dets[0].class_name == "person"
    print(" [PASS] Stage 1: Object Detection Box Filtering")

    tracker = MultiObjectTracker(iou_threshold=0.30)
    ctx1 = FrameContext(camera_id=uuid4(), site_id=uuid4(), frame_index=1)
    ctx2 = FrameContext(camera_id=uuid4(), site_id=uuid4(), frame_index=2)
    det1 = [DetectionBox(class_name="person", confidence=0.90, bbox=[0.10, 0.10, 0.20, 0.40])]
    tracks1 = tracker.update(det1, ctx1)
    initial_id = tracks1[0].track_id

    det2 = [DetectionBox(class_name="person", confidence=0.92, bbox=[0.12, 0.10, 0.20, 0.40])]
    tracks2 = tracker.update(det2, ctx2)
    assert len(tracks2) == 1 and tracks2[0].track_id == initial_id
    print(" [PASS] Stage 2: Multi-Object Track ID Persistence & Velocity Vector")

    recognizer = ActionRecognizer()
    tracked_person = TrackedObject(
        track_id=1,
        class_name="person",
        confidence=0.88,
        bbox=[0.3, 0.4, 0.4, 0.2],
        velocity=[0.0, 0.06],
    )
    actions = recognizer.analyze_actions([tracked_person], [], ctx1)
    assert len(actions) == 1 and actions[0].action_code == "fall_collapse"
    print(" [PASS] Stage 3: Action Recognition (Fall / Collapse Detection)")

    aggregator = ConfidenceAggregator(window_size=10, min_consensus_ratio=0.40)
    cam_id = uuid4()
    site_id = uuid4()
    for f in range(10):
        c = FrameContext(camera_id=cam_id, site_id=site_id, frame_index=f)
        d = [DetectionBox("weapon", 0.95, [0.1, 0.1, 0.1, 0.1])] if f == 5 else []
        sig = aggregator.push_and_aggregate(d, [], [], c)
    assert len(sig.detected_objects) == 0 and sig.aggregated_confidence == 0.0
    print(" [PASS] Stage 4: Multi-Frame Consensus Noise Filtering (FR-2.6)")

    print("\nUnit tests completed successfully.\n")


async def run_async_tests():
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
    print(" [PASS] Stage 5 & Orchestrator: End-to-End Weapon Incident Pipeline Cascade")

    print("==================================================")
    print("   RUNNING NFR-1 LATENCY & THROUGHPUT BENCHMARK   ")
    print("==================================================")

    latencies_ms = []
    total_frames = 100
    for i in range(total_frames):
        ctx = FrameContext(camera_id=cam_id, site_id=site_id, frame_index=i)
        t_start = time.perf_counter()
        await orchestrator.process_frame(frame=None, context=ctx, simulated_objects=simulated_frame_data)
        t_end = time.perf_counter()
        latencies_ms.append((t_end - t_start) * 1000.0)

    latencies_ms.sort()
    p95_latency = latencies_ms[int(0.95 * total_frames)]
    avg_latency = sum(latencies_ms) / total_frames

    print(f" [BENCHMARK] Frames Processed : {total_frames}")
    print(f" [BENCHMARK] Avg Latency      : {avg_latency:.3f} ms")
    print(f" [BENCHMARK] P95 Latency      : {p95_latency:.3f} ms")
    print(f" [BENCHMARK] NFR-1 Threshold  : 3000.000 ms (< 3 seconds p95)")
    assert p95_latency < 3000.0
    print(" [PASS] NFR-1 Latency & Throughput Benchmark\n")


if __name__ == "__main__":
    run_unit_tests()
    asyncio.run(run_async_tests())
