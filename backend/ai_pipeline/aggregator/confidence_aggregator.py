"""
AI Pipeline — Stage 4: Multi-Model, Multi-Frame Confidence Aggregator.

Aggregates object detection scores, tracking continuity, and temporal action probabilities
over a sliding window T (FR-2.6) to eliminate single-frame transient false positives.
"""

from __future__ import annotations

from collections import deque
from datetime import datetime, timezone
from typing import Any

from backend.ai_pipeline.base_contracts import (
    ActionResult,
    AggregatedFrameSignal,
    DetectionBox,
    FrameContext,
    TrackedObject,
)


class ConfidenceAggregator:
    def __init__(self, window_size: int = 15, min_consensus_ratio: float = 0.30):
        self.window_size = window_size
        self.min_consensus_ratio = min_consensus_ratio
        self._buffers: dict[str, deque[dict[str, Any]]] = {}

    def push_and_aggregate(
        self,
        detections: list[DetectionBox],
        tracked_objects: list[TrackedObject],
        actions: list[ActionResult],
        context: FrameContext,
    ) -> AggregatedFrameSignal:
        cam_key = str(context.camera_id)
        if cam_key not in self._buffers:
            self._buffers[cam_key] = deque(maxlen=self.window_size)

        now = context.timestamp or datetime.now(timezone.utc)

        frame_entry = {
            "timestamp": now,
            "detections": detections,
            "tracked_objects": tracked_objects,
            "actions": actions,
        }
        self._buffers[cam_key].append(frame_entry)

        buffer = self._buffers[cam_key]
        sample_count = len(buffer)
        window_start = buffer[0]["timestamp"]
        window_end = buffer[-1]["timestamp"]

        # 1. Aggregate object occurrences across window
        obj_class_counts: dict[str, int] = {}
        obj_confidence_sums: dict[str, float] = {}

        for frame_item in buffer:
            seen_classes_in_frame = set()
            for det in frame_item["detections"]:
                cls = det.class_name
                seen_classes_in_frame.add(cls)
                obj_confidence_sums[cls] = obj_confidence_sums.get(cls, 0.0) + det.confidence

            for cls in seen_classes_in_frame:
                obj_class_counts[cls] = obj_class_counts.get(cls, 0.0) + 1

        aggregated_objects = []
        for cls, count in obj_class_counts.items():
            consensus = count / float(sample_count)
            if consensus >= self.min_consensus_ratio:
                avg_conf = obj_confidence_sums[cls] / float(count)
                weighted_conf = (avg_conf * 0.5) + (consensus * 0.5)
                aggregated_objects.append(
                    {
                        "class_name": cls,
                        "frame_consensus_ratio": round(consensus, 2),
                        "raw_avg_confidence": round(avg_conf, 2),
                        "aggregated_confidence": round(weighted_conf, 2),
                    }
                )

        # 2. Aggregate action occurrences across window
        action_counts: dict[str, int] = {}
        action_conf_sums: dict[str, float] = {}

        for frame_item in buffer:
            seen_actions_in_frame = set()
            for act in frame_item["actions"]:
                acode = act.action_code
                seen_actions_in_frame.add(acode)
                action_conf_sums[acode] = action_conf_sums.get(acode, 0.0) + act.confidence

            for acode in seen_actions_in_frame:
                action_counts[acode] = action_counts.get(acode, 0.0) + 1

        aggregated_actions = []
        for acode, count in action_counts.items():
            consensus = count / float(sample_count)
            if consensus >= self.min_consensus_ratio:
                avg_conf = action_conf_sums[acode] / float(count)
                weighted_conf = (avg_conf * 0.6) + (consensus * 0.4)
                aggregated_actions.append(
                    {
                        "action_code": acode,
                        "frame_consensus_ratio": round(consensus, 2),
                        "aggregated_confidence": round(weighted_conf, 2),
                    }
                )

        all_confidences = [obj["aggregated_confidence"] for obj in aggregated_objects] + [
            act["aggregated_confidence"] for act in aggregated_actions
        ]
        overall_conf = max(all_confidences) if all_confidences else 0.0

        return AggregatedFrameSignal(
            camera_id=context.camera_id,
            site_id=context.site_id,
            window_start=window_start,
            window_end=window_end,
            sample_count=sample_count,
            detected_objects=aggregated_objects,
            detected_actions=aggregated_actions,
            aggregated_confidence=round(overall_conf, 2),
            tracked_subjects_count=len(tracked_objects),
        )
