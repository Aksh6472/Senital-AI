"""
AI Pipeline — Stage 2: Multi-Object Tracking Service.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from backend.ai_pipeline.base_contracts import DetectionBox, FrameContext, TrackedObject


def calculate_iou(boxA: list[float], boxB: list[float]) -> float:
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[0] + boxA[2], boxB[0] + boxB[2])
    yB = min(boxA[1] + boxA[3], boxB[1] + boxB[3])

    interWidth = max(0.0, xB - xA)
    interHeight = max(0.0, yB - yA)
    interArea = interWidth * interHeight

    boxAArea = boxA[2] * boxA[3]
    boxBArea = boxB[2] * boxB[3]

    unionArea = boxAArea + boxBArea - interArea
    if unionArea <= 0.0:
        return 0.0
    return interArea / unionArea


class MultiObjectTracker:
    def __init__(self, iou_threshold: float = 0.30, max_age_frames: int = 15):
        self.iou_threshold = iou_threshold
        self.max_age_frames = max_age_frames
        self._next_track_id = 1
        self._active_tracks: dict[int, dict[str, Any]] = {}

    def update(
        self,
        detections: list[DetectionBox],
        context: FrameContext,
    ) -> list[TrackedObject]:
        now = context.timestamp or datetime.now(timezone.utc)
        matched_track_ids = set()
        matched_det_indices = set()

        track_ids = list(self._active_tracks.keys())
        for track_id in track_ids:
            track = self._active_tracks[track_id]
            best_iou = 0.0
            best_det_idx = -1

            for idx, det in enumerate(detections):
                if idx in matched_det_indices:
                    continue
                if det.class_name != track["class_name"]:
                    continue

                iou = calculate_iou(track["bbox"], det.bbox)
                if iou > best_iou:
                    best_iou = iou
                    best_det_idx = idx

            if best_iou >= self.iou_threshold and best_det_idx >= 0:
                det = detections[best_det_idx]
                matched_track_ids.add(track_id)
                matched_det_indices.add(best_det_idx)

                old_center_x = track["bbox"][0] + track["bbox"][2] / 2.0
                old_center_y = track["bbox"][1] + track["bbox"][3] / 2.0
                new_center_x = det.bbox[0] + det.bbox[2] / 2.0
                new_center_y = det.bbox[1] + det.bbox[3] / 2.0

                velocity = [new_center_x - old_center_x, new_center_y - old_center_y]

                track["bbox"] = det.bbox
                track["confidence"] = det.confidence
                track["velocity"] = velocity
                track["history"].append([new_center_x, new_center_y])
                if len(track["history"]) > 50:
                    track["history"].pop(0)
                track["last_seen_at"] = now
                track["age"] = 0

        for idx, det in enumerate(detections):
            if idx not in matched_det_indices:
                new_id = self._next_track_id
                self._next_track_id += 1

                center_x = det.bbox[0] + det.bbox[2] / 2.0
                center_y = det.bbox[1] + det.bbox[3] / 2.0

                self._active_tracks[new_id] = {
                    "track_id": new_id,
                    "class_name": det.class_name,
                    "confidence": det.confidence,
                    "bbox": det.bbox,
                    "velocity": [0.0, 0.0],
                    "history": [[center_x, center_y]],
                    "first_seen_at": now,
                    "last_seen_at": now,
                    "age": 0,
                }

        to_purge = []
        for track_id, track in self._active_tracks.items():
            if track_id not in matched_track_ids:
                track["age"] += 1
                if track["age"] > self.max_age_frames:
                    to_purge.append(track_id)

        for tid in to_purge:
            del self._active_tracks[tid]

        result: list[TrackedObject] = []
        for track in self._active_tracks.values():
            result.append(
                TrackedObject(
                    track_id=track["track_id"],
                    class_name=track["class_name"],
                    confidence=track["confidence"],
                    bbox=track["bbox"],
                    velocity=track["velocity"],
                    history=list(track["history"]),
                    first_seen_at=track["first_seen_at"],
                    last_seen_at=track["last_seen_at"],
                )
            )

        return result
