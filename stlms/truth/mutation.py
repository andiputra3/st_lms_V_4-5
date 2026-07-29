"""
=====================================================
MODULE:     truth_mutation.py
PURPOSE:    Mutation Tracker — tracks indicator changes
            between consecutive TruthPoints.
=====================================================
"""

from typing import Optional

from ..truth.point import TruthPoint


class MutationTracker:
    """
    Tracks changes between consecutive TruthPoints.
    Returns a dict of indicator deltas for each transition.
    """

    def __init__(self):
        self._prev: Optional[TruthPoint] = None

    def track(self, prev_sp: TruthPoint, curr_sp: TruthPoint) -> dict:
        pc = prev_sp.close
        cc = curr_sp.close
        price_change_pct = ((cc - pc) / pc * 100.0) if pc and pc != 0 else 0.0

        st_change = curr_sp.st - prev_sp.st if prev_sp.st and curr_sp.st else 0.0

        atr_prev = prev_sp.atr or 0.0
        atr_curr = curr_sp.atr or 0.0
        atr_change_pct = ((atr_curr - atr_prev) / atr_prev * 100.0) if atr_prev != 0 else 0.0

        rsi_prev = prev_sp.rsi
        rsi_curr = curr_sp.rsi
        rsi_change = (rsi_curr - rsi_prev) if rsi_prev is not None and rsi_curr is not None else 0.0

        wpr_prev = prev_sp.wpr
        wpr_curr = curr_sp.wpr
        wpr_change = (wpr_curr - wpr_prev) if wpr_prev is not None and wpr_curr is not None else 0.0

        mh_prev = prev_sp.macd_hist or 0.0
        mh_curr = curr_sp.macd_hist or 0.0
        macd_hist_change = mh_curr - mh_prev

        da_prev = prev_sp.dist_atr or 0.0
        da_curr = curr_sp.dist_atr or 0.0
        dist_atr_change = da_curr - da_prev

        oi_prev = prev_sp.oi_value or 0.0
        oi_curr = curr_sp.oi_value or 0.0
        oi_change_pct = ((oi_curr - oi_prev) / oi_prev * 100.0) if oi_prev != 0 else 0.0

        return {
            "price_change_pct": round(price_change_pct, 4),
            "st_change": round(st_change, 4),
            "atr_change_pct": round(atr_change_pct, 4),
            "rsi_change": round(rsi_change, 4),
            "wpr_change": round(wpr_change, 4),
            "macd_hist_change": round(macd_hist_change, 4),
            "dist_atr_change": round(dist_atr_change, 4),
            "flip": curr_sp.flip,
            "oi_change_pct": round(oi_change_pct, 4),
        }

    def track_sequence(self, points: list[TruthPoint]) -> list[dict]:
        if len(points) < 2:
            return []
        results = []
        for i in range(1, len(points)):
            mutation = self.track(points[i - 1], points[i])
            mutation["ts"] = points[i].ts
            results.append(mutation)
        return results
