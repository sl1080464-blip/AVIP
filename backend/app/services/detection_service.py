from __future__ import annotations

from ai.detection.base_detector import BaseDetector, DetectionResult


class DetectionService(BaseDetector):
    """Concrete starter implementation for the AVIP detection layer."""

    def detect(self, frame: object) -> list[DetectionResult]:
        _ = frame
        return [
            DetectionResult(
                label="person",
                confidence=0.94,
                x=120.0,
                y=80.0,
                width=80.0,
                height=180.0,
                metadata={"source": "starter-pipeline"},
            ),
            DetectionResult(
                label="vehicle",
                confidence=0.88,
                x=350.0,
                y=210.0,
                width=140.0,
                height=90.0,
                metadata={"source": "starter-pipeline"},
            ),
        ]
