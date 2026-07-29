"""
=====================================================
MODULE:     truth_replay.py
PURPOSE:    Truth Replay — navigation over TruthPoint
            history with step and range controls.
=====================================================
"""

from typing import Optional

from ..truth.point import TruthPoint


class TruthReplay:
    """
    Navigates a TruthPoint history collection.
    Supports goto, step forward/back, and range replay.
    """

    def __init__(self, points: list[TruthPoint]):
        self._points = sorted(points, key=lambda p: p.ts)
        self._index: int = -1

    @property
    def points(self) -> list[TruthPoint]:
        return list(self._points)

    @property
    def current_index(self) -> int:
        return self._index

    @property
    def current(self) -> Optional[TruthPoint]:
        if 0 <= self._index < len(self._points):
            return self._points[self._index]
        return None

    def goto(self, index: int) -> Optional[TruthPoint]:
        if not self._points:
            self._index = -1
            return None
        self._index = max(0, min(index, len(self._points) - 1))
        return self._points[self._index]

    def step_forward(self) -> Optional[TruthPoint]:
        if not self._points:
            return None
        if self._index < len(self._points) - 1:
            self._index += 1
        return self._points[self._index]

    def step_back(self) -> Optional[TruthPoint]:
        if not self._points or self._index <= 0:
            if self._points:
                self._index = 0
            return self._points[self._index] if self._points else None
        self._index -= 1
        return self._points[self._index]

    def replay_range(self, start: int, end: int) -> list[TruthPoint]:
        if not self._points:
            return []
        return [p for p in self._points if start <= p.ts <= end]

    def reset(self):
        self._index = -1

    def seek_ts(self, ts: int) -> Optional[TruthPoint]:
        if not self._points:
            return None
        for i, p in enumerate(self._points):
            if p.ts >= ts:
                self._index = i
                return p
        self._index = len(self._points) - 1
        return self._points[self._index]
