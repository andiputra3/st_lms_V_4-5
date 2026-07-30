"""
Market Collection Engine — LOCKED CONTRACT.
48000 → 32 batch requests → collector → validator → repair gap →
continuity checker → merge → sort timestamp → duplicate checker →
observation builder.

This file defines the binding specification. All methods WILL be implemented.
"""

from typing import Optional


class GapDetector:
    """Detects and repairs gaps in candle data."""

    def detect(self, candles: list) -> list[dict]:
        """Return list of gap descriptors: [{start_idx, end_idx, gap_size}, ...]."""
        return []

    def repair(self, candles: list, gaps: list[dict]) -> list:
        """Repair detected gaps and return repaired candle list."""
        return candles


class TimestampValidator:
    """Validates timestamp ordering and interval consistency."""

    def validate_order(self, candles: list) -> bool:
        """Return True if timestamps are strictly ascending."""
        return True

    def validate_interval(self, candles: list, interval_ms: int) -> list[str]:
        """Return list of warnings for interval inconsistencies."""
        return []


class DuplicateValidator:
    """Detects and removes duplicate candles."""

    def detect(self, candles: list) -> list[int]:
        """Return list of indices of duplicate entries."""
        return []

    def remove(self, candles: list, indices: list[int]) -> list:
        """Return candle list with duplicates at given indices removed."""
        return candles


class MarketCollectionEngine:
    """
    Orchestrates the full collection pipeline:
    batch collect → validate → repair → merge → sort → dedup → build.
    """

    def __init__(self, provider, target_count: int = 48000):
        self._provider = provider
        self._target_count = target_count

    def collect(self, symbol: str, timeframe: str) -> dict:
        """Run full collection pipeline and return result dict with candles and metadata."""
        return {"symbol": symbol, "timeframe": timeframe, "candles": [], "stats": {}}

    def collect_historical(self, symbol: str, timeframe: str, start_ms: int, end_ms: int) -> dict:
        """Collect historical candles within [start_ms, end_ms]."""
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "candles": [],
            "start_ms": start_ms,
            "end_ms": end_ms,
            "stats": {},
        }

    def collect_live(self, symbol: str, timeframe: str) -> dict:
        """Collect live/streaming candles and return result dict."""
        return {"symbol": symbol, "timeframe": timeframe, "candles": [], "stats": {}}

    def get_collection_stats(self) -> dict:
        """Return collection pipeline statistics."""
        return {"total_collected": 0, "gaps_detected": 0, "duplicates_removed": 0}
