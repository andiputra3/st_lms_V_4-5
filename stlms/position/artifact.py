"""
=====================================================
MODULE:     position_artifact.py
PURPOSE:    Position Artifact — wraps Position state into
            immutable position_snapshot cards.
OWNER:      PHASE-11 POSITION LAYER
INPUT:      Position dataclass
OUTPUT:     position_snapshot immutable cards
DEPENDENCY: stlms.foundation.base_artifact (BaseArtifact),
            stlms.core.utils (Card)
ARCHITECTURE:
            Setiap snapshot posisi (per candle untuk posisi
            yang masih terbuka) dibungkus menjadi immutable
            card. Card dikonsumsi oleh TRUTH layer.
=====================================================
"""

from typing import Optional
from ..core.utils import Card
from ..foundation.base_artifact import BaseArtifact
from ..clone.engine import Position


class PositionArtifact(BaseArtifact):
    """
    Memproduksi position_snapshot immutable cards dari Position.

    Architecture:
        Extends BaseArtifact. Satu Position snapshot = satu Card.
        Card immutable dengan checksum SHA-256.

    Consumer:
        TRUTH layer, Recommendation layer
    """

    def __init__(self):
        super().__init__("POSITION")

    def produce(self, pos: Position, ts: int) -> Card:
        """
        Produce immutable position_snapshot Card from a Position.

        Args:
            pos: Position dataclass instance
            ts: timestamp in ms

        Returns:
            Immutable Card with entity_type="position_snapshot"
        """
        if not self.validate_input(pos, ts):
            raise ValueError("Invalid Position: missing required fields")

        payload = {
            "ts": ts,
            "side": pos.side,
            "entry_price": pos.entry_price,
            "sl": pos.sl,
            "tp": pos.tp,
            "mae": pos.mae,
            "mfe": pos.mfe,
            "hold_c": pos.hold_c,
            "status": pos.status,
        }

        deps = []
        card = self.make_card("position_snapshot", payload, deps, ts)
        return card

    def produce_batch(
        self, positions: list[Position], ts: int
    ) -> list[Card]:
        """Produce cards for a batch of Positions at a given timestamp."""
        return [self.produce(p, ts) for p in positions]

    def validate_input(self, pos: Position, ts: int) -> bool:
        """Validate Position before producing artifact."""
        if ts is None or ts <= 0:
            return False
        if not pos.side:
            return False
        if pos.entry_price is None or pos.entry_price <= 0:
            return False
        if pos.sl is None:
            return False
        if pos.tp is None:
            return False
        return True
