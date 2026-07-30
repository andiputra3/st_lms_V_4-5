"""
Historical Observation Query Engine — LOCKED CONTRACT.
Answers questions like:
"win rate for Supertrend lines with 20-40 members, wave=expansion, DNA=trending,
over the last 1 million observations"

This file defines the binding specification. All methods WILL be implemented.
"""

from typing import Optional


class HistoricalQueryEngine:
    """
    Query engine for historical observations stored in SQLite.
    Supports queries by range, pattern, statistics, evolution, and more.
    """

    def __init__(self, memory, sqlite_connection):
        self._memory = memory
        self._conn = sqlite_connection

    def query_by_range(self, start: int, end: int, entity_type: Optional[str] = None) -> list:
        """Return observations within [start, end] optionally filtered by entity_type."""
        return []

    def query_by_pattern(self, filters: dict, limit: int = 1000) -> list:
        """Return observations matching the given filter dict, up to limit."""
        return []

    def query_statistics(self, start: int, end: int, stat_type: str) -> dict:
        """Return computed statistics for the given range and stat_type."""
        return {}

    def query_evolution(self, entity_type: str, metric: str, start: int, end: int) -> list:
        """Return evolution timeline of metric for entity_type over the range."""
        return []

    def query_dna_transitions(self, batch_start: int, batch_end: int) -> list:
        """Return DNA transition events between batch indices."""
        return []

    def query_reliability_trend(self, entity_type: str, metric: str, window: int = 1000) -> list:
        """Return reliability trend data over rolling window."""
        return []

    def get_total_observations(self) -> int:
        """Return total number of observations in the database."""
        return 0

    def get_observation_count_by_entity(self, entity_type: str) -> int:
        """Return number of observations for a specific entity type."""
        return 0
