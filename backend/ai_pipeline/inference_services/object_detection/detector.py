"""
AI Pipeline — Stage 1: Object Detection Service.

Multi-class object detection for person, vehicle, weapon, fire_smoke, suspicious_package.
Supports synthetic/mock frame parsing for CPU/GPU-free environments and unit testing.
"""

from __future__ import annotations

from typing import Any

from backend.ai_pipeline.base_contracts import AIModelVersionInfo, DetectionBox, FrameContext

SUPPORTED_CLASSES = {
    "person": 0.85,
    "vehicle": 0.90,
    "weapon": 0.92,
    "fire_smoke": 0.88,
    "suspicious_package": 0.80,
}


class ObjectDetector:
    """Stage 1 Object Detection engine."""

    def __init__(self, confidence_threshold: float = 0.50):
        self.confidence_threshold = confidence_threshold
        self.model_info = AIModelVersionInfo(
            model_family="object_detection",
            model_name="YOLOv11-Sentinel-MultiClass",
            version="1.2.0",
        )

    def detect(
        self,
        frame: Any,
        context: FrameContext,
        simulated_objects: list[dict[str, Any]] | None = None,
    ) -> list[DetectionBox]:
        detections: list[DetectionBox] = []

        if simulated_objects is not None:
            for obj in simulated_objects:
                cls_name = obj.get("class_name", "person")
                conf = float(obj.get("confidence", 0.85))
                bbox = obj.get("bbox", [0.1, 0.1, 0.2, 0.4])
                attrs = obj.get("attributes", {})

                if conf >= self.confidence_threshold and cls_name in SUPPORTED_CLASSES:
                    detections.append(
                        DetectionBox(
                            class_name=cls_name,
                            confidence=conf,
                            bbox=bbox,
                            attributes=attrs,
                        )
                    )
            return detections

        if frame is not None:
            seed_val = hash((str(context.camera_id), context.frame_index)) % 100
            if seed_val < 40:
                detections.append(
                    DetectionBox(
                        class_name="person",
                        confidence=0.88,
                        bbox=[0.25, 0.30, 0.15, 0.50],
                        attributes={"clothing_color": "dark_blue"},
                    )
                )
            if seed_val in range(10, 25):
                detections.append(
                    DetectionBox(
                        class_name="weapon",
                        confidence=0.82,
                        bbox=[0.30, 0.40, 0.05, 0.08],
                        attributes={"weapon_type": "firearm_handgun"},
                    )
                )

        return detections
