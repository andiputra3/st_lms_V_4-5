"""
=====================================================
MODULE:     distance_artifact.py
PURPOSE:    Distance Artifact — immutable distance_snapshot
            cards from DistanceMetrics.
OWNER:      PHASE-05 DISTANCE LAYER
=====================================================
"""

from ..core.utils import Card, IDGenerator, wib_iso
from ..foundation.base_artifact import BaseArtifact
from .engine import DistanceMetrics


class DistanceArtifact(BaseArtifact):

    def __init__(self):
        super().__init__("DISTANCE")

    def produce(self, metrics: DistanceMetrics, ts_ms: int) -> Card:
        if not self.validate_input(metrics):
            raise ValueError("Invalid DistanceMetrics")

        payload = {
            "dist": metrics.dist,
            "dist_atr": metrics.dist_atr,
            "dist_ceiling": metrics.dist_ceiling,
            "dist_floor": metrics.dist_floor,
            "bucket": metrics.bucket,
            "sdv": metrics.sdv,
            "p90": metrics.p90,
            "trend": metrics.trend,
            "velocity": metrics.velocity,
            "ceiling_floor_ratio": metrics.ceiling_floor_ratio,
            "dist_delta": metrics.dist_delta,
            "wib_iso": wib_iso(ts_ms),
        }

        return self.make_card("distance_snapshot", payload, [], ts_ms)

    def validate_input(self, metrics: DistanceMetrics) -> bool:
        return metrics.dist is not None and metrics.dist_atr is not None
