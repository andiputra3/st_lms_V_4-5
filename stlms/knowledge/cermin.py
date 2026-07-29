"""
=====================================================
MODULE:     cermin.py
PURPOSE:    Knowledge Layer — CERMIN (Calibration Mirror)
            Predicted confidence vs actual win_rate.
            Detects overconfidence / underconfidence drift.
OWNER:      PHASE-11 KNOWLEDGE LAYER
=====================================================
"""

import math


class CerminEngine:
    """Calibration engine. Compares predicted confidence to actual win_rate per clone."""

    def __init__(self):
        self._last_calibration: dict = {}
        self._last_history: list[dict] = []

    def calibrate(self, predictions: list[dict], actuals: list[dict]) -> dict:
        """
        Compute calibration_error per clone: actual_win_rate - predicted_confidence.
        predictions: [{clone, confidence}, ...]
        actuals:     [{clone, win_rate}, ...]
        """
        act_map = {a["clone"]: a.get("win_rate", 0) for a in actuals}
        errors = {}
        for p in predictions:
            clone = p.get("clone", "UNKNOWN")
            confidence = p.get("confidence", 0)
            actual_wr = act_map.get(clone, 0)
            errors[clone] = actual_wr - confidence

        overall = sum(errors.values()) / len(errors) if errors else 0
        self._last_calibration = {
            "per_clone": errors,
            "overall_error": overall,
            "overconfidence": overall < -5,
            "underconfidence": overall > 5,
            "n": len(errors),
        }
        self._last_history.append(self._last_calibration)
        return self._last_calibration

    def per_clone_error(self) -> dict:
        """Returns {clone: error} from last calibration."""
        return dict(self._last_calibration.get("per_clone", {}))

    def calibration_trend(self, history: list[dict] | None = None) -> str:
        """
        Assess trend of overall_error across history entries.
        Returns "IMPROVING", "WORSENING", or "STABLE".
        """
        h = history if history is not None else self._last_history
        if len(h) < 2:
            return "STABLE"

        errors = [e.get("overall_error", 0) for e in h[-10:]]
        errors_abs = [abs(e) for e in errors]
        first_half = errors_abs[:len(errors_abs)//2]
        second_half = errors_abs[len(errors_abs)//2:]
        avg_first = sum(first_half) / len(first_half) if first_half else 0
        avg_second = sum(second_half) / len(second_half) if second_half else 0

        if avg_second < avg_first - 1:
            return "IMPROVING"
        elif avg_second > avg_first + 1:
            return "WORSENING"
        return "STABLE"

    def overconfidence_detection(self) -> bool:
        """True if confidence consistently > actual across all clones."""
        errors = self._last_calibration.get("per_clone", {})
        if not errors:
            return False
        return all(e < 0 for e in errors.values())

    def underconfidence_detection(self) -> bool:
        """True if confidence consistently < actual across all clones."""
        errors = self._last_calibration.get("per_clone", {})
        if not errors:
            return False
        return all(e > 0 for e in errors.values())

    def band(self) -> float:
        """Predicted confidence band rounded to nearest 1000."""
        errors = self._last_calibration.get("per_clone", {})
        if not errors:
            return 0
        avg_confidence = sum(max(0, -e) for e in errors.values()) / len(errors)
        return round(avg_confidence / 1000) * 1000
