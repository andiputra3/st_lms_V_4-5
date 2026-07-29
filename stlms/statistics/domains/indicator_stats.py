"""
=====================================================
MODULE:     statistics/domains/indicator_stats.py
PURPOSE:    Indicator Statistics — RSI distribution,
            W%R extremes, MACD divergence count,
            EMA slope distribution.
OWNER:      STATISTICS LAYER — INDICATOR DOMAIN
=====================================================
"""

from typing import Optional
from ...truth.point import TruthPoint


class IndicatorStatistics:
    """
    Compute indicator-level statistics from TruthPoint data.

    Metrics:
        - RSI distribution (oversold/neutral/overbought buckets)
        - W%R extremes
        - MACD divergence count
        - EMA slope distribution
    """

    def compute(self,
                points: Optional[list[TruthPoint]] = None) -> dict:
        result: dict = {
            "rsi_distribution": {
                "oversold": 0, "neutral": 0, "overbought": 0,
                "mean": 0.0, "min": None, "max": None,
            },
            "wpr_extremes": {
                "oversold": 0, "overbought": 0,
                "mean": 0.0, "min": None, "max": None,
            },
            "macd_divergence": {
                "bullish": 0, "bearish": 0, "total": 0,
            },
            "ema_slope_distribution": {
                "positive": 0, "negative": 0, "flat": 0,
                "mean": 0.0, "min": None, "max": None,
            },
            "valid_points": 0,
        }

        if not points:
            return result

        rsi_vals: list[float] = []
        wpr_vals: list[float] = []
        ema_slopes: list[float] = []

        for p in points:
            if p.rsi is not None:
                rsi_vals.append(p.rsi)
                if p.rsi < 30:
                    result["rsi_distribution"]["oversold"] += 1
                elif p.rsi > 70:
                    result["rsi_distribution"]["overbought"] += 1
                else:
                    result["rsi_distribution"]["neutral"] += 1

            if p.wpr is not None:
                wpr_vals.append(p.wpr)
                if p.wpr > -20:
                    result["wpr_extremes"]["overbought"] += 1
                elif p.wpr < -80:
                    result["wpr_extremes"]["oversold"] += 1

            if p.macd_hist is not None and p.prev_macd_hist is not None:
                if p.macd_hist > 0 and p.prev_macd_hist < 0:
                    result["macd_divergence"]["bullish"] += 1
                elif p.macd_hist < 0 and p.prev_macd_hist > 0:
                    result["macd_divergence"]["bearish"] += 1

            ema_slopes.append(p.ema_slope)
            if p.ema_slope > 0.01:
                result["ema_slope_distribution"]["positive"] += 1
            elif p.ema_slope < -0.01:
                result["ema_slope_distribution"]["negative"] += 1
            else:
                result["ema_slope_distribution"]["flat"] += 1

        result["macd_divergence"]["total"] = (
            result["macd_divergence"]["bullish"] +
            result["macd_divergence"]["bearish"]
        )
        result["valid_points"] = len(points)

        if rsi_vals:
            result["rsi_distribution"]["mean"] = round(
                sum(rsi_vals) / len(rsi_vals), 1
            )
            result["rsi_distribution"]["min"] = round(min(rsi_vals), 1)
            result["rsi_distribution"]["max"] = round(max(rsi_vals), 1)

        if wpr_vals:
            result["wpr_extremes"]["mean"] = round(
                sum(wpr_vals) / len(wpr_vals), 1
            )
            result["wpr_extremes"]["min"] = round(min(wpr_vals), 1)
            result["wpr_extremes"]["max"] = round(max(wpr_vals), 1)

        if ema_slopes:
            result["ema_slope_distribution"]["mean"] = round(
                sum(ema_slopes) / len(ema_slopes), 4
            )
            result["ema_slope_distribution"]["min"] = round(min(ema_slopes), 4)
            result["ema_slope_distribution"]["max"] = round(max(ema_slopes), 4)

        return result
