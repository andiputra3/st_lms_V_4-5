"""
=====================================================
MODULE:     statistics/domains/oi_stats.py
PURPOSE:    OI Statistics — trend classification,
            divergence score, accumulation rate.
OWNER:      STATISTICS LAYER — OI DOMAIN
=====================================================
"""

from typing import Optional
from ...truth.point import TruthPoint


class OIStatistics:
    """
    Compute open-interest statistics from TruthPoint data.

    Metrics:
        - OI trend classification (accumulation/distribution/stable)
        - Divergence score (OI vs price)
        - Accumulation rate
    """

    def compute(self,
                points: Optional[list[TruthPoint]] = None) -> dict:
        result: dict = {
            "trend_classification": {
                "accumulation": 0, "distribution": 0, "stable": 0,
                "dominant": "none",
            },
            "divergence_score": 0.0,
            "accumulation_rate": 0.0,
            "oi_delta_total": 0.0,
            "oi_delta_mean": 0.0,
            "oi_start": None,
            "oi_end": None,
            "oi_change_pct": 0.0,
            "valid_points": 0,
        }

        if not points:
            return result

        oi_points = [p for p in points if p.oi_value is not None]
        if not oi_points:
            return result

        result["valid_points"] = len(oi_points)
        result["oi_start"] = oi_points[0].oi_value
        result["oi_end"] = oi_points[-1].oi_value

        if result["oi_start"] and result["oi_start"] > 0:
            result["oi_change_pct"] = round(
                ((result["oi_end"] or 0) - result["oi_start"]) /
                result["oi_start"] * 100, 2
            )

        oi_deltas = [
            p.oi_delta for p in oi_points
            if p.oi_delta is not None
        ]
        if oi_deltas:
            result["oi_delta_total"] = round(sum(oi_deltas), 4)
            result["oi_delta_mean"] = round(
                sum(oi_deltas) / len(oi_deltas), 4
            )

            pos_deltas = sum(1 for d in oi_deltas if d > 0.01)
            neg_deltas = sum(1 for d in oi_deltas if d < -0.01)
            stable = len(oi_deltas) - pos_deltas - neg_deltas

            result["trend_classification"]["accumulation"] = pos_deltas
            result["trend_classification"]["distribution"] = neg_deltas
            result["trend_classification"]["stable"] = stable

            if pos_deltas >= neg_deltas and pos_deltas >= stable:
                result["trend_classification"]["dominant"] = "accumulation"
            elif neg_deltas >= pos_deltas and neg_deltas >= stable:
                result["trend_classification"]["dominant"] = "distribution"
            else:
                result["trend_classification"]["dominant"] = "stable"

        closes = [p.close for p in oi_points if p.close > 0]
        if len(oi_points) >= 2 and closes:
            price_change = (
                (closes[-1] - closes[0]) / closes[0] * 100
                if closes[0] > 0 else 0
            )
            if result["oi_change_pct"] > 0 and price_change < 0:
                result["divergence_score"] = round(
                    abs(result["oi_change_pct"] - abs(price_change)), 2
                )
            elif result["oi_change_pct"] < 0 and price_change > 0:
                result["divergence_score"] = round(
                    abs(abs(result["oi_change_pct"]) - price_change), 2
                )
            else:
                result["divergence_score"] = round(
                    abs(result["oi_change_pct"] - price_change), 2
                )

        if len(oi_points) > 0 and result["oi_start"] and result["oi_start"] > 0:
            result["accumulation_rate"] = round(
                result["oi_delta_mean"] / result["oi_start"] * 100, 4
            )

        return result
