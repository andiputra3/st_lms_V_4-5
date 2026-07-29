"""
=====================================================
MODULE:     statistics/artifact.py
PURPOSE:    Statistics Artifact — produces immutable
            statistics_snapshot cards from domain
            statistics results.
OWNER:      STATISTICS LAYER
=====================================================
"""

from typing import Any
from ..core.utils import Card, wib_iso
from ..foundation.base_artifact import BaseArtifact


class StatisticsArtifact(BaseArtifact):
    """
    Produce statistics_snapshot immutable cards from
    aggregated domain statistics.

    A single card represents a full statistics snapshot
    across all domains for a given symbol/session.
    """

    def __init__(self):
        super().__init__("STATISTICS")

    def produce(self,
                domain_results: dict[str, dict],
                symbol: str = "",
                ts_ms: int = 0,
                clone_id: str = "") -> Card:
        """
        Produce one statistics_snapshot card.

        Args:
            domain_results: Dict mapping domain name to its result dict
            symbol: Trading symbol
            ts_ms: Timestamp of the snapshot
            clone_id: Optional clone identifier

        Returns:
            Immutable Card
        """
        if not self.validate_input(domain_results):
            raise ValueError("Invalid domain results")

        payload = {
            "symbol": symbol,
            "clone_id": clone_id,
            "domains": domain_results,
            "domain_count": len(domain_results),
            "wib_iso": wib_iso(ts_ms) if ts_ms > 0 else "",
        }

        deps = []
        return self.make_card("statistics_snapshot", payload, deps, ts_ms)

    def validate_input(self, domain_results: dict[str, dict]) -> bool:
        return isinstance(domain_results, dict) and len(domain_results) > 0
