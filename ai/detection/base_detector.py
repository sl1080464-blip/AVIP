from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class DetectionResult:
    label: str
    confidence: float
    x: float | None = None
    y: float | None = None
    width: float | None = None
    height: float | None = None
    metadata: dict[str, Any] | None = None


class BaseDetector(ABC):
    """Abstract interface for vision detection services."""

    @abstractmethod
    def detect(self, frame: Any) -> list[DetectionResult]:
        raise NotImplementedError
