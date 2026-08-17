from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class TrackResult:
    track_id: str
    label: str
    status: str = "active"
    metadata: dict[str, Any] | None = None


class BaseTracker(ABC):
    """Abstract interface for tracking service implementations."""

    @abstractmethod
    def track(self, detections: list[Any]) -> list[TrackResult]:
        raise NotImplementedError
