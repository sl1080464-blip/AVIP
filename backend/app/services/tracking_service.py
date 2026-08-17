from __future__ import annotations

from ai.tracking.base_tracker import BaseTracker, TrackResult


class TrackingService(BaseTracker):
    """Starter tracking service that binds detections to track IDs."""

    def track(self, detections: list[object]) -> list[TrackResult]:
        return [
            TrackResult(
                track_id=f"track-{index}",
                label=getattr(detection, "label", "unknown"),
                metadata={"confidence": getattr(detection, "confidence", 0.0)},
            )
            for index, detection in enumerate(detections, start=1)
        ]
