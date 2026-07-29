"""
=====================================================
MODULE:     distance_engine.py
PURPOSE:    Distance Engine — ST_DIST_VOL rolling window,
            bucket classification, trend, velocity.
            Reference: MASTER_SPECIFICATION.html S5 (Distance)
OWNER:      PHASE-05 DISTANCE LAYER
=====================================================
"""

from dataclasses import dataclass, field
from typing import Optional
from collections import deque
import math

from ..core.constants import ST_DIST_VOL_WINDOW
from ..truth.point import TruthPoint
from ..structure.cage import Cage


@dataclass
class DistanceMetrics:
    dist: Optional[float] = None
    dist_atr: Optional[float] = None
    dist_ceiling: Optional[float] = None
    dist_floor: Optional[float] = None
    bucket: Optional[str] = None
    sdv: Optional[float] = None
    p90: Optional[float] = None
    trend: Optional[str] = None
    velocity: Optional[float] = None
    ceiling_floor_ratio: Optional[float] = None
    dist_delta: Optional[float] = None


class DistanceEngine:

    def __init__(self, window: int = ST_DIST_VOL_WINDOW):
        self._window = window
        self._dist_history: deque[float] = deque(maxlen=window)
        self._prev_dist: Optional[float] = None

    def compute(self, sp: TruthPoint, cage: Cage) -> DistanceMetrics:
        dist = abs(sp.close - sp.st)
        atr = sp.atr if sp.atr and sp.atr > 0 else 0.0001
        dist_atr = dist / atr

        self._dist_history.append(dist_atr)

        sdv = None
        p90 = None
        if len(self._dist_history) >= 3:
            n = len(self._dist_history)
            mean = sum(self._dist_history) / n
            variance = sum((x - mean) ** 2 for x in self._dist_history) / n
            sdv = math.sqrt(variance)
            sorted_vals = sorted(self._dist_history)
            idx = int(n * 0.9)
            p90 = sorted_vals[idx] if idx < n else sorted_vals[-1]

        dist_ceiling = None
        dist_floor = None
        if cage.upper is not None:
            dist_ceiling = abs(sp.close - cage.upper) / atr
        if cage.lower is not None:
            dist_floor = abs(sp.close - cage.lower) / atr

        trend: Optional[str] = None
        if sdv is not None and self._prev_dist is not None and len(self._dist_history) >= 3:
            recent = list(self._dist_history)[-3:]
            if all(recent[i] <= recent[i + 1] for i in range(len(recent) - 1)):
                trend = "EXPANDING"
            elif all(recent[i] >= recent[i + 1] for i in range(len(recent) - 1)):
                trend = "CONTRACTING"
            else:
                trend = "STABLE"

        if trend == "CONTRACTING":
            dist_ceiling = None
        elif trend == "EXPANDING":
            dist_floor = None

        bucket: Optional[str] = None
        if sp.point_status.value == "WARMUP":
            bucket = "WARMUP"
        elif dist_atr <= 0.5:
            bucket = "OPTIMAL"
        elif dist_atr <= 1.0:
            bucket = "NEAR"
        elif dist_atr <= 2.0:
            bucket = "EXTENDED"
        else:
            bucket = "FAR"

        velocity: Optional[float] = None
        if self._prev_dist is not None:
            velocity = dist_atr - self._prev_dist

        ceiling_floor_ratio: Optional[float] = None
        if dist_ceiling is not None and dist_floor is not None and dist_floor > 0:
            ceiling_floor_ratio = dist_ceiling / dist_floor

        dist_delta: Optional[float] = None
        if self._prev_dist is not None:
            dist_delta = dist_atr - self._prev_dist

        self._prev_dist = dist_atr

        return DistanceMetrics(
            dist=round(dist, 6),
            dist_atr=round(dist_atr, 4),
            dist_ceiling=round(dist_ceiling, 4) if dist_ceiling is not None else None,
            dist_floor=round(dist_floor, 4) if dist_floor is not None else None,
            bucket=bucket,
            sdv=round(sdv, 4) if sdv is not None else None,
            p90=round(p90, 4) if p90 is not None else None,
            trend=trend,
            velocity=round(velocity, 4) if velocity is not None else None,
            ceiling_floor_ratio=round(ceiling_floor_ratio, 4) if ceiling_floor_ratio is not None else None,
            dist_delta=round(dist_delta, 4) if dist_delta is not None else None,
        )

    def reset(self) -> None:
        self._dist_history.clear()
        self._prev_dist = None
