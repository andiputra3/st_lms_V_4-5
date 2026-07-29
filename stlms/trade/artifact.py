"""
=====================================================
MODULE:     trade_artifact.py
PURPOSE:    Trade Artifact — wraps TradeMarker into
            immutable trade_snapshot cards.
OWNER:      PHASE-10 TRADE LAYER
INPUT:      TradeMarker dataclass
OUTPUT:     trade_snapshot immutable cards
DEPENDENCY: stlms.foundation.base_artifact (BaseArtifact),
            stlms.core.utils (Card)
ARCHITECTURE:
            Setiap TradeMarker (ENTRY atau EXIT) dibungkus
            menjadi immutable card. Card dapat dikonsumsi
            oleh POSITION layer dan TRUTH layer.
=====================================================
"""

from typing import Optional
from ..core.utils import Card
from ..foundation.base_artifact import BaseArtifact
from ..clone.engine import TradeMarker


class TradeArtifact(BaseArtifact):
    """
    Memproduksi trade_snapshot immutable cards dari TradeMarker.

    Architecture:
        Extends BaseArtifact. Satu TradeMarker = satu Card.
        Card immutable dengan checksum SHA-256.

    Consumer:
        POSITION layer, TRUTH layer
    """

    def __init__(self):
        super().__init__("TRADE")

    def produce(self, marker: TradeMarker) -> Card:
        """
        Produce immutable trade_snapshot Card from a TradeMarker.

        Args:
            marker: TradeMarker dataclass instance

        Returns:
            Immutable Card with entity_type="trade_snapshot"
        """
        if not self.validate_input(marker):
            raise ValueError("Invalid TradeMarker: missing required fields")

        payload = {
            "ts": marker.ts,
            "clone": marker.clone,
            "side": marker.side,
            "kind": marker.kind,
            "reason": marker.reason,
            "entry": marker.entry,
            "exit": marker.exit,
            "gross": marker.gross,
            "fee": marker.fee,
            "slip": marker.slip,
            "net": marker.net,
            "result": marker.result,
            "mae": marker.mae,
            "mfe": marker.mfe,
            "hold": marker.hold,
        }

        deps = []
        card = self.make_card("trade_snapshot", payload, deps, marker.ts)
        return card

    def produce_batch(self, markers: list[TradeMarker]) -> list[Card]:
        """Produce cards for a batch of TradeMarkers."""
        return [self.produce(m) for m in markers]

    def validate_input(self, marker: TradeMarker) -> bool:
        """Validate TradeMarker before producing artifact."""
        if marker.ts is None or marker.ts <= 0:
            return False
        if not marker.clone:
            return False
        if not marker.side:
            return False
        if not marker.kind:
            return False
        if marker.kind == "EXIT":
            if marker.entry is None or marker.entry <= 0:
                return False
        return True
