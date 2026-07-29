"""
=====================================================
MODULE:     structure/artifact.py
PURPOSE:    Structure Artifact — immutable structure_snapshot
            cards from Cage, Wave, and Lines.
OWNER:      STRUCTURE LAYER
=====================================================
"""

from typing import Optional
from ..core.utils import Card, wib_iso
from ..foundation.base_artifact import BaseArtifact
from .cage import Cage


class StructureArtifact(BaseArtifact):

    def __init__(self):
        super().__init__("STRUCTURE")

    def produce(self, cage: Cage, wave: Optional[str],
                lines: list, ts: int) -> Card:
        if not self.validate_input(cage, ts):
            raise ValueError("Invalid Structure input")

        payload = {
            "cage": {
                "status": cage.status,
                "upper": cage.upper,
                "lower": cage.lower,
                "pp": cage.pp,
                "range_atr": cage.range_atr,
                "breakout": cage.breakout,
            },
            "wave_structure": wave,
            "wave_status": "CLOSED_WAVE",
            "line_count": len(lines),
            "dist_ceiling": cage.upper - cage.pp if cage.upper else None,
            "dist_floor": cage.pp - cage.lower if cage.lower else None,
            "wib_iso": wib_iso(ts),
        }

        return self.make_card("structure_snapshot", payload, [], ts)

    def validate_input(self, cage: Cage, ts: int) -> bool:
        return cage is not None and ts is not None and ts > 0
