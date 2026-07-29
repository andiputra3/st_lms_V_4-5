"""
=====================================================
MODULE:     statistics/consumer.py
PURPOSE:    Statistics Consumer — downstream API for
            consuming statistics_snapshot cards.
            Provides query and export capabilities.
OWNER:      STATISTICS LAYER
=====================================================
"""

from typing import Any, Optional
from ..core.utils import Card
from ..foundation.base_consumer import BaseConsumer


class StatisticsConsumer(BaseConsumer):
    """
    Consumer API for statistics_snapshot cards.

    Provides query, filter, and export capabilities
    for downstream layers (Recommendation, Dashboard).
    """

    def __init__(self):
        super().__init__("STATISTICS")
        self._store: list[Card] = []

    def consume(self, card: Card) -> dict:
        """
        Transform a statistics_snapshot card into
        a consumable dict format.

        Returns:
            Dict with domain results flattened for downstream.
        """
        p = card.payload
        return {
            "card_id": card.entity_id,
            "checksum": card.checksum,
            "symbol": p.get("symbol", ""),
            "clone_id": p.get("clone_id", ""),
            "domain_count": p.get("domain_count", 0),
            "timestamp_wib": card.timestamp_wib,
            "timestamp_ms": card.timestamp_ms,
            "domains": p.get("domains", {}),
            "wib_iso": p.get("wib_iso", ""),
        }

    def query(self, **filters) -> list[dict]:
        """
        Query stored cards with filters.

        Supported filters:
            symbol: str
            clone_id: str
            domain: str (filter by domain presence)
        """
        results: list[dict] = []
        symbol_filter = filters.get("symbol")
        clone_filter = filters.get("clone_id")
        domain_filter = filters.get("domain")

        for card in self._store:
            p = card.payload
            if symbol_filter and p.get("symbol") != symbol_filter:
                continue
            if clone_filter and p.get("clone_id") != clone_filter:
                continue
            if domain_filter and domain_filter not in p.get("domains", {}):
                continue
            results.append(self.consume(card))

        return results

    def ingest(self, cards: list[Card]) -> int:
        """
        Ingest statistics_snapshot cards into the store.

        Returns:
            Number of cards ingested.
        """
        count = 0
        for card in cards:
            if card.entity_type == "statistics_snapshot":
                self._store.append(card)
                count += 1
        return count

    def get_domain(self, domain: str, symbol: str = "") -> dict:
        """
        Extract a specific domain's statistics across all snapshots.

        Args:
            domain: Domain name (market, indicator, distance, clone, oi, correlation)
            symbol: Optional symbol filter

        Returns:
            Dict with domain snapshots aggregated.
        """
        snapshots: list[dict] = []
        for card in self._store:
            p = card.payload
            if symbol and p.get("symbol") != symbol:
                continue
            domain_data = p.get("domains", {}).get(domain)
            if domain_data:
                snapshots.append({
                    "ts": card.timestamp_ms,
                    "wib": card.timestamp_wib,
                    "data": domain_data,
                })

        return {
            "domain": domain,
            "symbol": symbol or "*",
            "snapshots": len(snapshots),
            "history": snapshots,
        }

    def clear(self) -> None:
        """Clear the in-memory store."""
        self._store.clear()
