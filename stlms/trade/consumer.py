"""
=====================================================
MODULE:     trade_consumer.py
PURPOSE:    Trade Consumer — downstream API untuk
            POSITION layer. Menyediakan query interface.
OWNER:      PHASE-10 TRADE LAYER
INPUT:      trade_snapshot cards
OUTPUT:     Consumable format untuk POSITION
DEPENDENCY: stlms.foundation.base_consumer (BaseConsumer)
ARCHITECTURE:
            Consumer adalah API interface. POSITION membaca
            trade_snapshot melalui consumer ini.
            Menyediakan filter by clone, side, kind, result.
=====================================================
"""

from typing import Any, Optional
from ..core.utils import Card
from ..foundation.base_consumer import BaseConsumer


class TradeConsumer(BaseConsumer):
    """
    Consumer API untuk trade_snapshot cards.

    Consumer: POSITION layer, TRUTH layer
    Transform: Card -> consumable dict
    """

    def __init__(self):
        super().__init__("TRADE")

    def consume(self, card: Card) -> dict:
        """
        Transform card ke format yang dikonsumsi POSITION.

        Returns:
            Dict dengan trade data + card metadata.
        """
        p = card.payload
        return {
            "ts": p.get("ts"),
            "clone": p.get("clone"),
            "side": p.get("side"),
            "kind": p.get("kind"),
            "reason": p.get("reason"),
            "entry": p.get("entry"),
            "exit": p.get("exit"),
            "gross": p.get("gross"),
            "fee": p.get("fee"),
            "slip": p.get("slip"),
            "net": p.get("net"),
            "result": p.get("result"),
            "mae": p.get("mae", 0.0),
            "mfe": p.get("mfe", 0.0),
            "hold": p.get("hold", 0),
            "card_id": card.entity_id,
            "card_checksum": card.checksum,
        }

    def query(self, **filters) -> list[dict]:
        """
        Query artifacts with filters.

        Supported filters:
            clone: str (LONG / SHORT / GRID)
            side: str (LONG / SHORT)
            kind: str (ENTRY / EXIT)
            result: str (WIN / LOSS / BREAKEVEN)
            start_ts: int
            end_ts: int
        """
        return []

    def filter_entries(self, cards: list[Card]) -> list[dict]:
        """Extract ENTRY markers only."""
        return [
            self.consume(c) for c in cards
            if c.payload.get("kind") == "ENTRY"
        ]

    def filter_exits(self, cards: list[Card]) -> list[dict]:
        """Extract EXIT markers only."""
        return [
            self.consume(c) for c in cards
            if c.payload.get("kind") == "EXIT"
        ]

    def by_clone(self, cards: list[Card], clone: str) -> list[dict]:
        """Filter by clone ID."""
        return [
            self.consume(c) for c in cards
            if c.payload.get("clone") == clone
        ]

    def win_loss_ratio(self, cards: list[Card]) -> dict:
        """Compute win/loss ratio from trade cards."""
        exits = self.filter_exits(cards)
        wins = [e for e in exits if e.get("result") == "WIN"]
        losses = [e for e in exits if e.get("result") == "LOSS"]
        total = len(wins) + len(losses)
        return {
            "total": len(exits),
            "wins": len(wins),
            "losses": len(losses),
            "breakevens": len(exits) - len(wins) - len(losses),
            "win_rate": round(len(wins) / total * 100, 1) if total else 0.0,
        }
