"""
=====================================================
MODULE:     truth_reliability.py
PURPOSE:    Reliability Scorer — per-indicator and
            overall reliability scoring for TruthPoints.
=====================================================
"""

from typing import Optional

from ..truth.point import TruthPoint


class ReliabilityScorer:
    """
    Scores individual TruthPoints for indicator reliability.
    Returns 0-1 scores per indicator plus an overall score.

    Reliability factors:
      - Indicator availability (not None)
      - RSI/WPR in sane ranges
      - MACD histogram consistency
      - Distance to ATR ratio stability
      - ST direction consistency with close price
    """

    def score(self, sp: TruthPoint) -> dict:
        scores: dict[str, float] = {}

        scores["rsi"] = self._score_rsi(sp.rsi)
        scores["wpr"] = self._score_wpr(sp.wpr)
        scores["macd"] = self._score_macd(sp.macd, sp.macd_signal, sp.macd_hist)
        scores["atr"] = self._score_atr(sp.atr)
        scores["ema"] = self._score_ema(sp.ema, sp.close)
        scores["dist_atr"] = self._score_dist_atr(sp.dist_atr)
        scores["st_consistency"] = self._score_st_consistency(sp.st, sp.close, sp.st_dir)
        scores["oi"] = self._score_oi(sp.oi_value)

        present = [v for v in scores.values() if v > 0]
        overall = sum(present) / len(present) if present else 0.0

        return {
            "ts": sp.ts,
            "overall": round(overall, 4),
            "indicators": scores,
        }

    def _score_rsi(self, rsi: Optional[float]) -> float:
        if rsi is None:
            return 0.0
        if 20 <= rsi <= 80:
            return 1.0
        if 10 <= rsi <= 90:
            return 0.5
        return 0.2

    def _score_wpr(self, wpr: Optional[float]) -> float:
        if wpr is None:
            return 0.0
        if -80 <= wpr <= -20:
            return 1.0
        if -90 <= wpr <= -10:
            return 0.5
        return 0.2

    def _score_macd(self, macd: Optional[float],
                    macd_signal: Optional[float],
                    macd_hist: Optional[float]) -> float:
        if macd is None or macd_signal is None or macd_hist is None:
            return 0.0
        consistency = macd - macd_signal
        if abs(consistency - macd_hist) < 0.0001:
            return 1.0
        return 0.8

    def _score_atr(self, atr: Optional[float]) -> float:
        if atr is None or atr <= 0:
            return 0.0
        return 1.0

    def _score_ema(self, ema: Optional[float], close: float) -> float:
        if ema is None or close == 0:
            return 0.0
        return 1.0

    def _score_dist_atr(self, dist_atr: Optional[float]) -> float:
        if dist_atr is None:
            return 0.0
        if dist_atr < 0:
            return 0.0
        if 0 <= dist_atr <= 5.0:
            return 1.0
        if 5.0 < dist_atr <= 10.0:
            return 0.5
        return 0.2

    def _score_st_consistency(self, st: float, close: float, st_dir: int) -> float:
        if st_dir == 1 and close > st:
            return 1.0
        if st_dir == -1 and close < st:
            return 1.0
        return 0.3

    def _score_oi(self, oi_value: Optional[float]) -> float:
        if oi_value is None:
            return 0.0
        if oi_value > 0:
            return 1.0
        return 0.5

    def score_batch(self, points: list[TruthPoint]) -> list[dict]:
        return [self.score(p) for p in points]
