"""
=====================================================
MODULE:     truth_statistics.py
PURPOSE:    Truth Statistics — aggregate statistics
            over TruthPoint collections.
=====================================================
"""

from collections import Counter
from typing import Optional

from ..truth.point import TruthPoint
from ..core.types import PointStatus


class TruthStatistics:
    """
    Computes aggregate statistics over a list of TruthPoints.
    """

    def compute(self, sp_list: list[TruthPoint]) -> dict:
        if not sp_list:
            return {
                "trend_duration": 0,
                "flip_frequency": 0.0,
                "avg_indicators": {},
                "indicator_distribution": {},
                "warmup_ratio": 0.0,
            }

        n = len(sp_list)
        valid = [p for p in sp_list if p.point_status == PointStatus.VALID]
        flips = [p for p in sp_list if p.flip is not None]

        trend_duration = self._compute_trend_duration(sp_list)
        flip_frequency = len(flips) / n if n > 0 else 0.0
        avg_indicators = self._compute_avg_indicators(valid)
        indicator_distribution = self._compute_indicator_distribution(valid)
        warmup_ratio = (n - len(valid)) / n if n > 0 else 1.0

        return {
            "trend_duration": trend_duration,
            "flip_frequency": round(flip_frequency, 4),
            "avg_indicators": avg_indicators,
            "indicator_distribution": indicator_distribution,
            "warmup_ratio": round(warmup_ratio, 4),
        }

    def _compute_trend_duration(self, points: list[TruthPoint]) -> int:
        if not points:
            return 0
        max_run = 1
        current_run = 1
        for i in range(1, len(points)):
            if points[i].st_dir == points[i - 1].st_dir:
                current_run += 1
            else:
                max_run = max(max_run, current_run)
                current_run = 1
        return max(max_run, current_run)

    def _compute_avg_indicators(self, valid: list[TruthPoint]) -> dict:
        if not valid:
            return {}
        n = len(valid)

        rsi_vals = [p.rsi for p in valid if p.rsi is not None]
        wpr_vals = [p.wpr for p in valid if p.wpr is not None]
        macd_hist_vals = [p.macd_hist for p in valid if p.macd_hist is not None]
        atr_vals = [p.atr for p in valid if p.atr is not None]
        dist_atr_vals = [p.dist_atr for p in valid if p.dist_atr is not None]

        return {
            "rsi": round(sum(rsi_vals) / len(rsi_vals), 2) if rsi_vals else None,
            "wpr": round(sum(wpr_vals) / len(wpr_vals), 2) if wpr_vals else None,
            "macd_hist": round(sum(macd_hist_vals) / len(macd_hist_vals), 4) if macd_hist_vals else None,
            "atr": round(sum(atr_vals) / len(atr_vals), 4) if atr_vals else None,
            "dist_atr": round(sum(dist_atr_vals) / len(dist_atr_vals), 4) if dist_atr_vals else None,
        }

    def _compute_indicator_distribution(self, valid: list[TruthPoint]) -> dict:
        if not valid:
            return {}

        st_colors = Counter(p.st_color for p in valid)
        st_dirs = Counter("UP" if p.st_dir == 1 else "DOWN" for p in valid)
        flips_counted = Counter(p.flip for p in valid if p.flip is not None)

        rsi_bins = {"oversold": 0, "normal": 0, "overbought": 0}
        wpr_bins = {"oversold": 0, "normal": 0, "overbought": 0}

        for p in valid:
            if p.rsi is not None:
                if p.rsi <= 30:
                    rsi_bins["oversold"] += 1
                elif p.rsi >= 70:
                    rsi_bins["overbought"] += 1
                else:
                    rsi_bins["normal"] += 1
            if p.wpr is not None:
                if p.wpr <= -80:
                    wpr_bins["oversold"] += 1
                elif p.wpr >= -20:
                    wpr_bins["overbought"] += 1
                else:
                    wpr_bins["normal"] += 1

        return {
            "st_colors": dict(st_colors),
            "st_directions": dict(st_dirs),
            "flip_types": dict(flips_counted),
            "rsi_distribution": rsi_bins,
            "wpr_distribution": wpr_bins,
        }
