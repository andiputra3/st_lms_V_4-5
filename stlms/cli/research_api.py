"""
Market Research API — LOCKED CONTRACT.
ST-LMS is NOT a Trading Bot. It is a Market Research System.
This API provides research-mode queries for Truth, Line, Wave, DNA,
Statistics, and Knowledge domains.

This file defines the binding specification. All methods WILL be implemented.
"""

from typing import Optional


class MarketResearchAPI:
    """
    Market research interface — query-only, read-only.
    Provides structured access to all research domains within ST-LMS.
    """

    def __init__(self, shell):
        self._shell = shell

    def research_truth(self, start: int, end: int, indicators: Optional[list] = None) -> dict:
        """Research truth points in range [start, end] with optional indicator filters."""
        return {}

    def research_lines(self, filters: Optional[dict] = None) -> list:
        """Research Supertrend lines matching optional filters."""
        return []

    def research_waves(self, filters: Optional[dict] = None) -> list:
        """Research wave structures matching optional filters."""
        return []

    def research_dna(self, batch_range: Optional[tuple] = None) -> dict:
        """Research DNA profiles optionally scoped to a batch range."""
        return {}

    def research_statistics(self, domain: str, start: int, end: int) -> dict:
        """Research statistics for a given domain within [start, end]."""
        return {}

    def research_knowledge(self, entity: str, filters: Optional[dict] = None) -> dict:
        """Research knowledge entities matching optional filters."""
        return {}

    def research_mutations(self, entity_type: str, start: int, end: int) -> list:
        """Research mutation events for entity_type within [start, end]."""
        return []

    def research_reliability(self, entity_type: str) -> dict:
        """Research reliability metrics for a given entity type."""
        return {}

    def research_market_character(self, batch_range: Optional[tuple] = None) -> dict:
        """Research market character profiles optionally scoped to a batch range."""
        return {}

    def research_pattern_frequency(self, pattern_type: str, window: int = 48000) -> dict:
        """Research frequency distribution of a pattern type over the window."""
        return {}
