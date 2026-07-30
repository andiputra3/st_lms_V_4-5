"""
=====================================================
MODULE:     core/continuity.py
PURPOSE:    Observation Continuity Engine
            Manages the lifecycle of observations across
            the 48000-observation window.
            
            Observation #1 → #2 → ... → #48000
            → #48001 → Snapshot-1 freeze
            → #48002 → ...
            
            Only 1 LIVE observation at any time.
            Historical observations: immutable.
            All objects maintain lifecycle.
STATUS:     LOCKED CONTRACT — DO NOT SIMPLIFY
=====================================================
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import time


class ObservationState(Enum):
    """Lifecycle states for a single Market Observation."""
    LIVE = "LIVE"           # Current active observation (only 1)
    FROZEN = "FROZEN"       # Immutable, part of active window
    ARCHIVED = "ARCHIVED"   # Moved to SnapshotBatch, stored in SQLite
    HISTORICAL = "HISTORICAL" # Long-term storage, queryable


class WindowState(Enum):
    """States for the 48000-observation window."""
    COLLECTING = "COLLECTING"   # Initial historical load (0 → 47999)
    LIVE = "LIVE"               # Window full, syncing 1 candle at a time
    FREEZING = "FREEZING"       # SnapshotBatch being created
    ROTATING = "ROTATING"       # Window sliding: old frozen, new appended


@dataclass
class ContinuityRecord:
    """Tracks continuity between consecutive observations."""
    from_index: int
    to_index: int
    timestamp_gap_ms: int = 0
    is_continuous: bool = True
    gap_detected: bool = False
    duplicate_detected: bool = False
    notes: str = ""


class ObservationContinuityEngine:
    """
    Manages observation continuity across the 48000 window.
    
    CONTRACT (LOCKED):
    
    1. Only 1 LIVE observation at any time.
    2. Historical observations are IMMUTABLE after freeze.
    3. All objects maintain lifecycle through transitions.
    4. Window rotation: freeze old, append new, maintain 48000.
    5. Snapshot transition: LIVE → PRE_FREEZE → FREEZE → ARCHIVE.
    6. Append-only: data is NEVER deleted.
    
    This engine does NOT store data — it manages state transitions.
    Data storage is handled by MarketObservationMemory.
    """
    
    def __init__(self, window_size: int = 48000):
        self._window_size = window_size
        self._window_state = WindowState.COLLECTING
        self._live_index: int = -1
        self._frozen_count: int = 0
        self._archived_count: int = 0
        self._continuity_log: list[ContinuityRecord] = []
        self._snapshot_transitions: list[dict] = []
    
    @property
    def window_state(self) -> WindowState:
        return self._window_state
    
    @property
    def live_index(self) -> int:
        return self._live_index
    
    @property
    def is_window_full(self) -> bool:
        return self._frozen_count + 1 >= self._window_size
    
    # ── Observation Lifecycle ────────────────────────────────
    
    def register_live(self, observation_index: int) -> ObservationState:
        """
        Register a new LIVE observation.
        Freezes the previous LIVE observation.
        
        Returns: ObservationState.LIVE
        """
        if self._live_index >= 0:
            self._frozen_count += 1
            self._continuity_log.append(ContinuityRecord(
                from_index=self._live_index,
                to_index=observation_index,
                is_continuous=True
            ))
        
        self._live_index = observation_index
        
        if self._frozen_count + 1 >= self._window_size:
            self._window_state = WindowState.LIVE
        
        return ObservationState.LIVE
    
    def freeze_observation(self, observation_index: int) -> ObservationState:
        """Freeze an observation (make immutable)."""
        return ObservationState.FROZEN
    
    def archive_observation(self, observation_index: int) -> ObservationState:
        """Archive observation to SnapshotBatch + SQLite."""
        self._archived_count += 1
        return ObservationState.ARCHIVED
    
    # ── Window Management ────────────────────────────────────
    
    def begin_snapshot_freeze(self) -> dict:
        """
        Begin SnapshotBatch freeze transition.
        Window: LIVE → FREEZING → ROTATING.
        
        Returns dict with freeze metadata.
        """
        self._window_state = WindowState.FREEZING
        return {
            "state": self._window_state.value,
            "frozen_count": self._frozen_count,
            "live_index": self._live_index,
            "timestamp": time.time(),
        }
    
    def complete_snapshot_freeze(self, batch_id: int) -> dict:
        """
        Complete SnapshotBatch freeze.
        Window: FREEZING → ROTATING → LIVE.
        
        Records snapshot transition for historical tracking.
        """
        transition = {
            "batch_id": batch_id,
            "from_state": "LIVE",
            "to_state": "ARCHIVE",
            "observation_count": self._window_size,
            "frozen_at": time.time(),
        }
        self._snapshot_transitions.append(transition)
        self._window_state = WindowState.LIVE
        
        return transition
    
    # ── Continuity Tracking ──────────────────────────────────
    
    def record_gap(self, from_index: int, to_index: int, gap_ms: int):
        """Record a gap between consecutive observations."""
        self._continuity_log.append(ContinuityRecord(
            from_index=from_index,
            to_index=to_index,
            timestamp_gap_ms=gap_ms,
            is_continuous=False,
            gap_detected=True,
            notes=f"Gap of {gap_ms}ms detected"
        ))
    
    def record_duplicate(self, index: int):
        """Record a duplicate observation."""
        self._continuity_log.append(ContinuityRecord(
            from_index=index,
            to_index=index,
            is_continuous=False,
            duplicate_detected=True,
            notes=f"Duplicate at index {index}"
        ))
    
    def get_continuity_report(self) -> dict:
        """Get continuity statistics."""
        total = len(self._continuity_log)
        gaps = sum(1 for c in self._continuity_log if c.gap_detected)
        duplicates = sum(1 for c in self._continuity_log if c.duplicate_detected)
        return {
            "total_transitions": total,
            "continuous": total - gaps - duplicates,
            "gaps_detected": gaps,
            "duplicates_detected": duplicates,
            "continuity_pct": round((total - gaps - duplicates) / total * 100, 2) if total > 0 else 100,
        }
    
    # ── State Query ──────────────────────────────────────────
    
    def get_state(self) -> dict:
        """Get current engine state."""
        return {
            "window_state": self._window_state.value,
            "window_size": self._window_size,
            "live_index": self._live_index,
            "frozen_count": self._frozen_count,
            "archived_count": self._archived_count,
            "is_full": self.is_window_full,
            "snapshot_transitions": len(self._snapshot_transitions),
            "continuity": self.get_continuity_report(),
        }
