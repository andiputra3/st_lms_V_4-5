"""
=====================================================
MODULE:     position_package.py
PURPOSE:    Position Package — structured report dari
            position_snapshot cards.
OWNER:      PHASE-11 POSITION LAYER
INPUT:      List of position_snapshot Cards
OUTPUT:     PositionReportPackage (dict)
DEPENDENCY: stlms.foundation.base_package (BasePackage)
ARCHITECTURE:
            Package mengagregasi multiple position snapshot
            cards menjadi laporan terstruktur. Meringkas
            status posisi, MAE/MFE, hold duration.
=====================================================
"""

from typing import Any
from ..core.utils import Card
from ..foundation.base_package import BasePackage


class PositionPackage(BasePackage):
    """
    Membangun Position Report Package dari position_snapshot cards.

    Consumer:
        Dashboard, Recommendation Layer
    """

    def __init__(self):
        super().__init__("POSITION")

    def build(self, artifacts: list[Card]) -> dict:
        """
        Build structured report from position_snapshot cards.

        Returns:
            PositionReportPackage dict with position summary.
        """
        if not artifacts:
            return {"layer": self.layer, "status": "EMPTY", "positions": 0}

        sides = set(c.payload.get("side", "?") for c in artifacts)
        statuses = set(c.payload.get("status", "?") for c in artifacts)

        mae_values = [c.payload.get("mae", 0) for c in artifacts]
        mfe_values = [c.payload.get("mfe", 0) for c in artifacts]
        hold_values = [c.payload.get("hold_c", 0) for c in artifacts]

        return {
            "layer": self.layer,
            "snapshots": len(artifacts),
            "sides": sorted(sides),
            "statuses": sorted(statuses),
            "mae": {
                "min": round(min(mae_values), 3),
                "max": round(max(mae_values), 3),
                "avg": round(sum(mae_values) / len(mae_values), 3),
            },
            "mfe": {
                "min": round(min(mfe_values), 3),
                "max": round(max(mfe_values), 3),
                "avg": round(sum(mfe_values) / len(mfe_values), 3),
            },
            "hold": {
                "min": min(hold_values),
                "max": max(hold_values),
                "avg": round(sum(hold_values) / len(hold_values), 1),
            },
            "status": "OK",
        }

    def summary(self, report: dict) -> str:
        """Human-readable summary."""
        if report.get("status") == "EMPTY":
            return "Position Report: No positions"

        mae = report.get("mae", {})
        mfe = report.get("mfe", {})
        hold = report.get("hold", {})

        return (
            f"Position Report: {report.get('snapshots')} snapshots | "
            f"Sides: {', '.join(report.get('sides', []))} | "
            f"MAE: {mae.get('min')}/{mae.get('avg')}/{mae.get('max')} | "
            f"MFE: {mfe.get('min')}/{mfe.get('avg')}/{mfe.get('max')} | "
            f"Hold: {hold.get('avg')} avg"
        )
