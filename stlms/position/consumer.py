"""
=====================================================
MODULE:     position_consumer.py
PURPOSE:    Position Consumer — downstream API untuk
            TRUTH dan Recommendation layers.
OWNER:      PHASE-11 POSITION LAYER
INPUT:      position_snapshot cards
OUTPUT:     Consumable format untuk downstream
DEPENDENCY: stlms.foundation.base_consumer (BaseConsumer)
ARCHITECTURE:
            Consumer adalah API interface. TRUTH dan
            Recommendation membaca position_snapshot
            melalui consumer ini. Menyediakan filter
            by side, status, hold duration.
=====================================================
"""

from typing import Any, Optional
from ..core.utils import Card
from ..foundation.base_consumer import BaseConsumer


class PositionConsumer(BaseConsumer):
    """
    Consumer API untuk position_snapshot cards.

    Consumer: TRUTH layer, Recommendation layer
    Transform: Card -> consumable dict
    """

    def __init__(self):
        super().__init__("POSITION")

    def consume(self, card: Card) -> dict:
        """
        Transform card ke format yang dikonsumsi downstream.

        Returns:
            Dict dengan position data + card metadata.
        """
        p = card.payload
        return {
            "ts": p.get("ts"),
            "side": p.get("side"),
            "entry_price": p.get("entry_price"),
            "sl": p.get("sl"),
            "tp": p.get("tp"),
            "mae": p.get("mae", 0.0),
            "mfe": p.get("mfe", 0.0),
            "hold_c": p.get("hold_c", 0),
            "status": p.get("status", "OPEN"),
            "card_id": card.entity_id,
            "card_checksum": card.checksum,
        }

    def query(self, **filters) -> list[dict]:
        """
        Query artifacts with filters.

        Supported filters:
            side: str (LONG / SHORT)
            status: str (OPEN / HOLD / CLOSED / BREAKEVEN / TRAILING / PARTIAL)
            start_ts: int
            end_ts: int
        """
        return []

    def by_side(self, cards: list[Card], side: str) -> list[dict]:
        """Filter by side (LONG / SHORT)."""
        return [
            self.consume(c) for c in cards
            if c.payload.get("side") == side
        ]

    def by_status(self, cards: list[Card], status: str) -> list[dict]:
        """Filter by position status."""
        return [
            self.consume(c) for c in cards
            if c.payload.get("status") == status
        ]

    def open_positions(self, cards: list[Card]) -> list[dict]:
        """Get all currently open positions."""
        open_statuses = {"OPEN", "HOLD", "TRAILING", "BREAKEVEN", "PARTIAL"}
        return [
            self.consume(c) for c in cards
            if c.payload.get("status") in open_statuses
        ]

    def closed_positions(self, cards: list[Card]) -> list[dict]:
        """Get all closed positions."""
        return [
            self.consume(c) for c in cards
            if c.payload.get("status") == "CLOSED"
        ]

    def max_adverse(self, cards: list[Card]) -> dict:
        """Find maximum adverse excursion across positions."""
        mae_values = [c.payload.get("mae", 0) for c in cards]
        mfe_values = [c.payload.get("mfe", 0) for c in cards]
        return {
            "worst_mae": min(mae_values) if mae_values else 0.0,
            "best_mfe": max(mfe_values) if mfe_values else 0.0,
            "avg_mae": sum(mae_values) / len(mae_values) if mae_values else 0.0,
            "avg_mfe": sum(mfe_values) / len(mfe_values) if mfe_values else 0.0,
        }
