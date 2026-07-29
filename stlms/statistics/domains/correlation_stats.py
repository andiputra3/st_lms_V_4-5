"""
=====================================================
MODULE:     statistics/domains/correlation_stats.py
PURPOSE:    Correlation Statistics — indicator
            correlation matrix.
OWNER:      STATISTICS LAYER — CORRELATION DOMAIN
=====================================================
"""

import math
from typing import Optional
from ...truth.point import TruthPoint


class CorrelationStatistics:
    """
    Compute indicator correlation matrix from TruthPoint data.

    Metrics:
        - Pearson correlation between: RSI, W%R, MACD, EMA slope,
          distance, volume delta, OI delta
    """

    INDICATORS = ["rsi", "wpr", "macd", "ema_slope", "dist", "vol_delta", "oi_delta"]

    def compute(self,
                points: Optional[list[TruthPoint]] = None) -> dict:
        result: dict = {
            "correlation_matrix": {},
            "pair_count": 0,
            "valid_points": 0,
        }

        if not points:
            for i in self.INDICATORS:
                for j in self.INDICATORS:
                    if i < j:
                        result["correlation_matrix"][f"{i}_vs_{j}"] = 0.0
            return result

        valid = [p for p in points if p.point_status.value == "VALID"]
        result["valid_points"] = len(valid)

        series: dict[str, list[float]] = {k: [] for k in self.INDICATORS}
        for p in valid:
            series["rsi"].append(p.rsi if p.rsi is not None else 0.0)
            series["wpr"].append(p.wpr if p.wpr is not None else 0.0)
            series["macd"].append(p.macd_hist if p.macd_hist is not None else 0.0)
            series["ema_slope"].append(p.ema_slope)
            series["dist"].append(p.dist_atr if p.dist_atr is not None else 0.0)
            series["vol_delta"].append(p.vol_delta)
            series["oi_delta"].append(p.oi_delta if p.oi_delta is not None else 0.0)

        pairs = 0
        for i_idx, i_name in enumerate(self.INDICATORS):
            for j_name in self.INDICATORS[i_idx + 1:]:
                corr = self._pearson(series[i_name], series[j_name])
                result["correlation_matrix"][f"{i_name}_vs_{j_name}"] = corr
                pairs += 1

        result["pair_count"] = pairs
        return result

    def _pearson(self, xs: list[float], ys: list[float]) -> float:
        n = min(len(xs), len(ys))
        if n < 3:
            return 0.0

        x_sub = xs[:n]
        y_sub = ys[:n]

        mx = sum(x_sub) / n
        my = sum(y_sub) / n

        num = 0.0
        dx2 = 0.0
        dy2 = 0.0

        for x, y in zip(x_sub, y_sub):
            dx = x - mx
            dy = y - my
            num += dx * dy
            dx2 += dx * dx
            dy2 += dy * dy

        denom = math.sqrt(dx2 * dy2)
        if denom == 0:
            return 0.0

        return round(num / denom, 4)
