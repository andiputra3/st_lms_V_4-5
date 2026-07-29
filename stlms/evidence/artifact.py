"""
=====================================================
MODULE:     evidence/artifact.py
PURPOSE:    Evidence Artifact — immutable evidence_snapshot
            cards from 3 buses (Direction, Exit, Correction).
OWNER:      EVIDENCE LAYER
=====================================================
"""

from ..core.utils import Card, wib_iso
from ..foundation.base_artifact import BaseArtifact
from .bus import DirectionBus, ExitBus, CorrectionBus


class EvidenceArtifact(BaseArtifact):

    def __init__(self):
        super().__init__("EVIDENCE")

    def produce(self, dir_bus: DirectionBus, exit_bus: ExitBus,
                correction_bus: CorrectionBus, max_score: float,
                data_quality: float, ts: int) -> Card:
        if not self.validate_input(dir_bus, exit_bus, correction_bus, ts):
            raise ValueError("Invalid Evidence input")

        payload = {
            "dir_bus": {
                "ema": dir_bus.ema,
                "oi": dir_bus.oi,
                "vd": dir_bus.vd,
                "mtf": dir_bus.mtf_long,
            },
            "exit_bus": {
                "rsi": exit_bus.rsi,
                "wpr": exit_bus.wpr,
                "macd_hist": exit_bus.macd_hist,
                "hold": exit_bus.hold,
                "vel": exit_bus.vel,
                "acc": exit_bus.acc,
            },
            "correction_bus": {
                "pp": correction_bus.price_position,
                "phase": correction_bus.market_phase,
                "dist_ceiling": correction_bus.dist_ceiling,
                "dist_floor": correction_bus.dist_floor,
            },
            "max_score": max_score,
            "data_quality": data_quality,
            "wib_iso": wib_iso(ts),
        }

        return self.make_card("evidence_snapshot", payload, [], ts)

    def validate_input(self, dir_bus: DirectionBus, exit_bus: ExitBus,
                       correction_bus: CorrectionBus, ts: int) -> bool:
        return (dir_bus is not None and exit_bus is not None
                and correction_bus is not None and ts is not None and ts > 0)
