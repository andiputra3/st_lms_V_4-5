"""
=====================================================
MODULE:     distance_package.py
PURPOSE:    Distance Package — structured report dari
            distance_snapshot cards.
OWNER:      PHASE-05 DISTANCE LAYER
=====================================================
"""

from ..core.utils import Card
from ..foundation.base_package import BasePackage


class DistancePackage(BasePackage):

    def __init__(self):
        super().__init__("DISTANCE")

    def build(self, artifacts: list[Card]) -> dict:
        if not artifacts:
            return {"layer": self.layer, "status": "EMPTY", "snapshots": 0}

        last = artifacts[-1].payload
        buckets = [a.payload.get("bucket") for a in artifacts if a.payload.get("bucket")]
        bucket_counts = {}
        for b in buckets:
            bucket_counts[b] = bucket_counts.get(b, 0) + 1

        return {
            "layer": self.layer,
            "snapshots": len(artifacts),
            "current": {
                "dist": last.get("dist"),
                "dist_atr": last.get("dist_atr"),
                "dist_ceiling": last.get("dist_ceiling"),
                "dist_floor": last.get("dist_floor"),
                "bucket": last.get("bucket"),
                "sdv": last.get("sdv"),
                "p90": last.get("p90"),
                "trend": last.get("trend"),
                "velocity": last.get("velocity"),
                "ceiling_floor_ratio": last.get("ceiling_floor_ratio"),
                "dist_delta": last.get("dist_delta"),
            },
            "bucket_distribution": bucket_counts,
            "status": "OK",
        }

    def summary(self, report: dict) -> str:
        if report.get("status") == "EMPTY":
            return "Distance Report: No data"
        c = report.get("current", {})
        return (
            f"Distance Report: {report.get('snapshots')} snapshots | "
            f"dist_atr={c.get('dist_atr')} bucket={c.get('bucket')} | "
            f"trend={c.get('trend')} vel={c.get('velocity')} | "
            f"sdv={c.get('sdv')} p90={c.get('p90')}"
        )
