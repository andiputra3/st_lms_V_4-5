"""
=====================================================
MODULE:     statistics/domains/market_stats.py
PURPOSE:    Market Statistics — phase distribution,
            wave frequency, cage lifetime,
            breakout direction distribution.
OWNER:      STATISTICS LAYER — MARKET DOMAIN
=====================================================
"""

from typing import Optional
from ...structure.wave import Wave
from ...structure.cage import Cage


class MarketStatistics:
    """
    Compute market-level statistics from Wave and Cage data.

    Metrics:
        - Phase distribution (wave structures count)
        - Wave frequency (waves per time unit)
        - Cage lifetime (duration, status counts)
        - Breakout direction distribution
    """

    def compute(self,
                waves: Optional[list[Wave]] = None,
                cages: Optional[list[Cage]] = None) -> dict:
        result: dict = {
            "phase_distribution": {},
            "wave_frequency": 0.0,
            "wave_count": 0,
            "cage_count": 0,
            "cage_lifetime": {"avg_range_atr": 0.0, "status_counts": {}},
            "breakout_distribution": {
                "NONE": 0, "IMMINENT_UP": 0, "IMMINENT_DOWN": 0, "SQUEEZE": 0,
            },
        }

        if waves:
            for w in waves:
                struct = w.structure
                result["phase_distribution"][struct] = \
                    result["phase_distribution"].get(struct, 0) + 1
            result["wave_count"] = len(waves)

            if len(waves) >= 2:
                duration = max(
                    (waves[-1].end_ts - waves[0].start_ts) / 3600000.0,
                    1.0
                )
                result["wave_frequency"] = round(
                    len(waves) / max(duration, 1.0), 2
                )

        if cages:
            range_atrs = []
            status_counts: dict[str, int] = {}
            for c in cages:
                status_counts[c.status] = status_counts.get(c.status, 0) + 1
                if c.range_atr is not None:
                    range_atrs.append(c.range_atr)
                result["breakout_distribution"][c.breakout] = \
                    result["breakout_distribution"].get(c.breakout, 0) + 1

            result["cage_count"] = len(cages)
            result["cage_lifetime"]["status_counts"] = status_counts
            if range_atrs:
                result["cage_lifetime"]["avg_range_atr"] = round(
                    sum(range_atrs) / len(range_atrs), 3
                )

        return result
