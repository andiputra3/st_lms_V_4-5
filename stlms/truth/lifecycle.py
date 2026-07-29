"""
=====================================================
MODULE:     truth_lifecycle.py
PURPOSE:    SP Lifecycle — state machine for TruthPoint
            life phases from creation to export.
=====================================================
"""

from enum import Enum
from typing import Optional


class SPLifecycle(Enum):
    OPEN = "OPEN"
    LIVE = "LIVE"
    UPDATE = "UPDATE"
    FLIP = "FLIP"
    CLOSE = "CLOSE"
    SNAPSHOT = "SNAPSHOT"
    STATISTICS = "STATISTICS"
    RECOMMENDATION = "RECOMMENDATION"
    REPLAY = "REPLAY"
    EXPORT = "EXPORT"


_TRANSITIONS: dict[SPLifecycle, set[SPLifecycle]] = {
    SPLifecycle.OPEN:           {SPLifecycle.LIVE, SPLifecycle.CLOSE},
    SPLifecycle.LIVE:           {SPLifecycle.UPDATE, SPLifecycle.FLIP, SPLifecycle.SNAPSHOT, SPLifecycle.CLOSE},
    SPLifecycle.UPDATE:         {SPLifecycle.LIVE, SPLifecycle.FLIP, SPLifecycle.SNAPSHOT},
    SPLifecycle.FLIP:           {SPLifecycle.LIVE, SPLifecycle.SNAPSHOT},
    SPLifecycle.CLOSE:          {SPLifecycle.STATISTICS, SPLifecycle.REPLAY, SPLifecycle.EXPORT},
    SPLifecycle.SNAPSHOT:       {SPLifecycle.STATISTICS, SPLifecycle.RECOMMENDATION, SPLifecycle.REPLAY},
    SPLifecycle.STATISTICS:     {SPLifecycle.RECOMMENDATION, SPLifecycle.EXPORT},
    SPLifecycle.RECOMMENDATION: {SPLifecycle.EXPORT, SPLifecycle.REPLAY},
    SPLifecycle.REPLAY:         {SPLifecycle.STATISTICS, SPLifecycle.EXPORT},
    SPLifecycle.EXPORT:         set(),
}


class SPLifecycleManager:
    """
    Tracks SP state transitions and validates them.
    Only allows transitions defined in the state graph.
    """

    def __init__(self):
        self._current: Optional[SPLifecycle] = None
        self._history: list[SPLifecycle] = []

    @property
    def current(self) -> Optional[SPLifecycle]:
        return self._current

    @property
    def history(self) -> list[SPLifecycle]:
        return list(self._history)

    def transition(self, to_state: SPLifecycle) -> bool:
        if self._current is None:
            self._current = to_state
            self._history.append(to_state)
            return True

        allowed = _TRANSITIONS.get(self._current, set())
        if to_state not in allowed:
            return False

        self._current = to_state
        self._history.append(to_state)
        return True

    def can_transition(self, to_state: SPLifecycle) -> bool:
        if self._current is None:
            return True
        return to_state in _TRANSITIONS.get(self._current, set())

    def reset(self):
        self._current = None
        self._history.clear()
