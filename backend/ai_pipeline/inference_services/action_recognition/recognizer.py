"""
AI Pipeline — Stage 3: Pose & Action Recognition Service.
"""

from __future__ import annotations

import math
from typing import Any

from backend.ai_pipeline.base_contracts import ActionResult, DetectionBox, FrameContext, TrackedObject


class ActionRecognizer:
    def __init__(self, velocity_threshold_running: float = 0.05, loitering_window: int = 10):
        self.velocity_threshold_running = velocity_threshold_running
        self.loitering_window = loitering_window

    def analyze_actions(
        self,
        tracked_objects: list[TrackedObject],
        detections: list[DetectionBox],
        context: FrameContext,
    ) -> list[ActionResult]:
        actions: list[ActionResult] = []

        persons = [obj for obj in tracked_objects if obj.class_name == "person"]
        weapons = [obj for obj in detections if obj.class_name == "weapon"]

        for p in persons:
            dx, dy = p.velocity
            speed = math.sqrt(dx * dx + dy * dy)

            bbox_w, bbox_h = p.bbox[2], p.bbox[3]
            if dy > 0.04 and (bbox_w > bbox_h * 1.1):
                actions.append(
                    ActionResult(
                        action_code="fall_collapse",
                        confidence=0.89,
                        target_track_id=p.track_id,
                        metadata={"dy": dy, "aspect_ratio": bbox_w / max(bbox_h, 0.001)},
                    )
                )

            elif speed >= self.velocity_threshold_running:
                actions.append(
                    ActionResult(
                        action_code="running_panic",
                        confidence=min(0.95, 0.70 + speed * 3.0),
                        target_track_id=p.track_id,
                        metadata={"speed": speed},
                    )
                )

            elif len(p.history) >= self.loitering_window:
                start_x, start_y = p.history[0]
                end_x, end_y = p.history[-1]
                net_displacement = math.sqrt((end_x - start_x) ** 2 + (end_y - start_y) ** 2)
                if net_displacement < 0.05:
                    actions.append(
                        ActionResult(
                            action_code="loitering",
                            confidence=0.82,
                            target_track_id=p.track_id,
                            metadata={"duration_frames": len(p.history), "displacement": net_displacement},
                        )
                    )

            for w in weapons:
                px, py = p.bbox[0] + p.bbox[2] / 2.0, p.bbox[1] + p.bbox[3] / 2.0
                wx, wy = w.bbox[0] + w.bbox[2] / 2.0, w.bbox[1] + w.bbox[3] / 2.0
                dist = math.sqrt((px - wx) ** 2 + (py - wy) ** 2)
                if dist < 0.25:
                    actions.append(
                        ActionResult(
                            action_code="weapon_brandishing",
                            confidence=min(0.98, w.confidence + 0.10),
                            target_track_id=p.track_id,
                            metadata={"weapon_proximity": dist, "weapon_confidence": w.confidence},
                        )
                    )

        if len(persons) >= 2:
            for i in range(len(persons)):
                for j in range(i + 1, len(persons)):
                    p1, p2 = persons[i], persons[j]
                    p1_center = [p1.bbox[0] + p1.bbox[2] / 2.0, p1.bbox[1] + p1.bbox[3] / 2.0]
                    p2_center = [p2.bbox[0] + p2.bbox[2] / 2.0, p2.bbox[1] + p2.bbox[3] / 2.0]
                    dist = math.sqrt((p1_center[0] - p2_center[0]) ** 2 + (p1_center[1] - p2_center[1]) ** 2)
                    
                    p1_speed = math.sqrt(p1.velocity[0]**2 + p1.velocity[1]**2)
                    p2_speed = math.sqrt(p2.velocity[0]**2 + p2.velocity[1]**2)

                    if dist < 0.15 and (p1_speed > 0.02 or p2_speed > 0.02):
                        actions.append(
                            ActionResult(
                                action_code="fighting_gesture",
                                confidence=0.86,
                                target_track_id=p1.track_id,
                                metadata={"partner_track_id": p2.track_id, "proximity": dist},
                            )
                        )

        return actions
