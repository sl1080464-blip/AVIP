from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DangerousObjectDetectionResult:
    """Placeholder object returned by dangerous object detection workflows."""

    label: str
    confidence: float
    context: dict[str, Any] = field(default_factory=dict)
    track_id: str | None = None


class DangerousObjectDetector:
    """Architecture-only interface for a dangerous-object detector.

    This project intentionally does not ship a trained model yet. The interface is
    designed to evolve into an inference pipeline that feeds the risk engine.
    """

    def predict(self, frame: Any) -> DangerousObjectDetectionResult:
        raise NotImplementedError("Dangerous object detection model is not implemented yet.")
