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


# ── Evolution Lifecycle ──────────────────────────────────────
# Separate from pipeline lifecycle. Tracks SP maturity over time.
# Reference: MARKET_OBSERVATION_CONTRACT.md

class EvolutionLifecycle(Enum):
    NEW = "NEW"
    LIVE = "LIVE"
    UPDATE = "UPDATE"
    MATURE = "MATURE"
    FREEZE = "FREEZE"
    ARCHIVE = "ARCHIVE"


_EVOLUTION_TRANSITIONS = {
    None: {EvolutionLifecycle.NEW},
    EvolutionLifecycle.NEW: {EvolutionLifecycle.LIVE},
    EvolutionLifecycle.LIVE: {EvolutionLifecycle.UPDATE, EvolutionLifecycle.MATURE},
    EvolutionLifecycle.UPDATE: {EvolutionLifecycle.UPDATE, EvolutionLifecycle.MATURE},
    EvolutionLifecycle.MATURE: {EvolutionLifecycle.FREEZE},
    EvolutionLifecycle.FREEZE: {EvolutionLifecycle.ARCHIVE},
    EvolutionLifecycle.ARCHIVE: set(),
}


class EvolutionLifecycleManager:
    """Tracks SP evolution state (maturity over time)."""
    
    def __init__(self):
        self._current: Optional[EvolutionLifecycle] = None
        self._history: list = []
    
    @property
    def current(self) -> Optional[EvolutionLifecycle]:
        return self._current
    
    def transition(self, to_state: EvolutionLifecycle) -> bool:
        if not self.can_transition(to_state):
            return False
        self._current = to_state
        self._history.append(to_state.value)
        return True
    
    def can_transition(self, to_state: EvolutionLifecycle) -> bool:
        if self._current is None:
            return True
        return to_state in _EVOLUTION_TRANSITIONS.get(self._current, set())
    
    def reset(self):
        self._current = None
        self._history.clear()
