"""
=====================================================
MODULE:     statistics/domains/distance_stats.py
PURPOSE:    Distance Statistics — bucket distribution,
            optimal range, volatility.
OWNER:      STATISTICS LAYER — DISTANCE DOMAIN
=====================================================
"""

from typing import Optional
from ...truth.point import TruthPoint


class DistanceStatistics:
    """
    Compute distance-level statistics from TruthPoint data.

    Metrics:
        - Distance bucket distribution (dist_atr)
        - Optimal range identification
        - Volatility (ATR distribution)
    """

    BUCKETS = [
        (0.0, 0.5, "0.0-0.5"),
        (0.5, 1.0, "0.5-1.0"),
        (1.0, 1.5, "1.0-1.5"),
        (1.5, 2.0, "1.5-2.0"),
        (2.0, 3.0, "2.0-3.0"),
        (3.0, float("inf"), "3.0+"),
    ]

    def compute(self,
                points: Optional[list[TruthPoint]] = None) -> dict:
        result: dict = {
            "bucket_distribution": {b[2]: 0 for b in self.BUCKETS},
            "optimal_range": {"low": 0.0, "high": 0.0, "center": 0.0},
            "volatility": {
                "atr_mean": 0.0, "atr_min": None, "atr_max": None,
                "atr_pct_of_price": 0.0,
            },
            "valid_points": 0,
        }

        if not points:
            return result

        dist_atrs: list[float] = []
        atrs: list[float] = []
        closes: list[float] = []

        for p in points:
            if p.dist_atr is not None:
                dist_atrs.append(p.dist_atr)
                for lo, hi, label in self.BUCKETS:
                    if lo <= p.dist_atr < hi:
                        result["bucket_distribution"][label] += 1
                        break
            if p.atr is not None:
                atrs.append(p.atr)
            closes.append(p.close)

        result["valid_points"] = len(points)

        if dist_atrs:
            sorted_dists = sorted(dist_atrs)
            p10_idx = max(0, int(len(sorted_dists) * 0.10))
            p90_idx = min(len(sorted_dists) - 1, int(len(sorted_dists) * 0.90))
            result["optimal_range"]["low"] = round(sorted_dists[p10_idx], 3)
            result["optimal_range"]["high"] = round(sorted_dists[p90_idx], 3)
            result["optimal_range"]["center"] = round(
                sum(sorted_dists) / len(sorted_dists), 3
            )

        if atrs:
            result["volatility"]["atr_mean"] = round(
                sum(atrs) / len(atrs), 4
            )
            result["volatility"]["atr_min"] = round(min(atrs), 4)
            result["volatility"]["atr_max"] = round(max(atrs), 4)
            if closes:
                avg_close = sum(closes) / len(closes)
                if avg_close > 0:
                    result["volatility"]["atr_pct_of_price"] = round(
                        result["volatility"]["atr_mean"] / avg_close * 100, 2
                    )

        return result
