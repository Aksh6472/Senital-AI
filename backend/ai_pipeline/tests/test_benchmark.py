"""
AI Pipeline — NFR-1 Latency & Throughput Benchmark Suite.

Verifies detection-to-alert processing latency remains below 3,000ms p95 (NFR-1).
"""

from __future__ import annotations

import asyncio
import time
from uuid import uuid4
import pytest

from backend.ai-pipeline.base_contracts import FrameContext
from backend.ai-pipeline.orchestrator import PipelineOrchestrator


@pytest.mark.asyncio
async def test_nfr1_latency_benchmark():
    orchestrator = PipelineOrchestrator()
    cam_id = uuid4()
    site_id = uuid4()

    simulated_objects = [
        {"class_name": "person", "confidence": 0.88, "bbox": [0.3, 0.2, 0.15, 0.45]},
    ]

    latencies_ms: list[float] = []
    total_frames = 100

    for i in range(total_frames):
        ctx = FrameContext(camera_id=cam_id, site_id=site_id, frame_index=i)
        t_start = time.perf_counter()
        
        await orchestrator.process_frame(
            frame=None,
            context=ctx,
            simulated_objects=simulated_objects,
        )
        
        t_end = time.perf_counter()
        latencies_ms.append((t_end - t_start) * 1000.0)

    latencies_ms.sort()
    p95_index = int(0.95 * total_frames)
    p95_latency = latencies_ms[p95_index]
    avg_latency = sum(latencies_ms) / total_frames

    print(f"\n[BENCHMARK RESULT] Processed {total_frames} frames.")
    print(f"[BENCHMARK RESULT] Avg Latency: {avg_latency:.3f} ms | P95 Latency: {p95_latency:.3f} ms")

    # NFR-1 Requirement: Latency < 3,000 ms (3 seconds p95)
    assert p95_latency < 3000.0, f"P95 latency {p95_latency:.2f}ms exceeded 3000ms threshold!"
    # In-process engine should be ultra fast (< 50ms p95)
    assert p95_latency < 50.0, f"In-process pipeline latency unexpectedly high: {p95_latency:.2f}ms"
