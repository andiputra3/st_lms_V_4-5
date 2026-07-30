"""
=====================================================
MODULE:     core/memory.py
PURPOSE:    MarketObservationMemory — 48000 Market
            Observation Window. NOT a FIFO ring buffer.
            When full: FREEZE entire batch →
            Snapshot Batch → SQLite commit →
            clear buffer → continue.

            1 Candle = 1 Market Observation Object.
ARCHITECTURE: MARKET_OBSERVATION_CONTRACT.md
=====================================================
"""

from typing import Optional
from ..core.constants import MARKET_OBSERVATION_MEMORY


class SnapshotBatch:
    """
    Satu batch dari 48000 observation.
    Memiliki lifecycle sendiri: NEW → LIVE → FREEZE → ARCHIVE.
    """
    
    def __init__(self, batch_id: int, start_index: int, end_index: int):
        self.batch_id = batch_id
        self.start_index = start_index
        self.end_index = end_index
        self.lifecycle_state = "NEW"
        self.observations: list[dict] = []
        self.truth_stats: dict = {}
        self.structure_stats: dict = {}
        self.wave_stats: dict = {}
        self.dna_profile: dict = {}
        self.market_character: str = ""
        self.evolution_report: dict = {}
        self.created_at: float = 0.0
        self.frozen_at: float = 0.0
        self.archived_at: float = 0.0
    
    def add(self, obs: dict):
        self.observations.append(obs)
    
    def freeze(self):
        self.lifecycle_state = "FREEZE"
    
    def archive(self):
        self.lifecycle_state = "ARCHIVE"
    
    @property
    def is_full(self) -> bool:
        return len(self.observations) >= MARKET_OBSERVATION_MEMORY
    
    @property
    def size(self) -> int:
        return len(self.observations)
    
    def summary(self) -> dict:
        return {
            "batch_id": self.batch_id,
            "lifecycle_state": self.lifecycle_state,
            "start_index": self.start_index,
            "end_index": self.end_index,
            "observation_count": len(self.observations),
            "market_character": self.market_character,
            "has_dna": bool(self.dna_profile),
            "has_evolution_report": bool(self.evolution_report),
        }


class MarketObservationMemory:
    """
    Market Observation Window — 48000 observations per batch.
    
    Philosophy:
        - 1 Candle = 1 Market Observation Object.
        - 48000 observations = 1 Snapshot Batch.
        - Saat 48000 tercapai: FREEZE batch → Snapshot → SQLite → batch baru.
        - Data TIDAK PERNAH dihapus. Hanya di-archive ke SQLite.
        - Historical observation selalu tersedia via SQLite query.
    
    Reference: MARKET_OBSERVATION_CONTRACT.md
    """
    
    def __init__(self, max_size: int = None):
        self._max_size = max_size or MARKET_OBSERVATION_MEMORY
        self._buffer: list[dict] = []
        self._live_index: int = -1
        self._total_observations: int = 0
        self._current_batch_index: int = 0
        self._completed_batches: list[SnapshotBatch] = []
        self._current_batch: Optional[SnapshotBatch] = None
        self._on_batch_full = None  # callback for Snapshot + SQLite commit
    
    @property
    def max_size(self) -> int:
        return self._max_size
    
    @property
    def size(self) -> int:
        return len(self._buffer)
    
    @property
    def total_observations(self) -> int:
        return self._total_observations
    
    @property
    def is_full(self) -> bool:
        return len(self._buffer) >= self._max_size
    
    @property
    def live_index(self) -> int:
        return self._live_index
    
    @property
    def batch_count(self) -> int:
        return len(self._completed_batches)
    
    @property
    def current_batch(self) -> Optional[SnapshotBatch]:
        return self._current_batch
    
    @property
    def completed_batches(self) -> list:
        return self._completed_batches
    
    def set_batch_full_callback(self, callback):
        """Set callback untuk dipanggil saat batch penuh (Snapshot + SQLite)."""
        self._on_batch_full = callback
    
    def append(self, observation: dict) -> int:
        """
        Tambah Market Observation Object ke memory.
        
        Saat buffer mencapai 48000:
        1. FREEZE current batch
        2. Panggil callback (Snapshot + SQLite commit)
        3. Batch baru dimulai
        4. Data LAMA tetap ada di SQLite — TIDAK dihapus.
        """
        # Freeze previous LIVE observation
        if self._live_index >= 0 and self._live_index < len(self._buffer):
            prev = self._buffer[self._live_index]
            prev["evolution_state"] = "FREEZE"
        
        # Set new observation as LIVE
        observation["evolution_state"] = "LIVE"
        
        # Init current batch if needed
        if self._current_batch is None:
            self._current_batch = SnapshotBatch(
                batch_id=self._current_batch_index + 1,
                start_index=self._total_observations,
                end_index=self._total_observations + self._max_size - 1
            )
            self._current_batch.lifecycle_state = "LIVE"
        
        # Add to current batch
        self._current_batch.add(observation)
        
        # Jika buffer mencapai max_size: FREEZE batch
        if len(self._buffer) >= self._max_size:
            self._freeze_current_batch()
        
        self._buffer.append(observation)
        self._live_index = len(self._buffer) - 1
        self._total_observations += 1
        
        return observation.get("candle_index", self._total_observations - 1)
    
    def _freeze_current_batch(self):
        """FREEZE current batch: panggil callback, archive, clear buffer."""
        if self._current_batch is None:
            return
        
        self._current_batch.end_index = self._total_observations - 1
        self._current_batch.freeze()
        
        # Callback: Snapshot + SQLite commit
        if self._on_batch_full:
            self._on_batch_full(self._current_batch)
        
        self._current_batch.archive()
        self._completed_batches.append(self._current_batch)
        
        # Start new batch — keep last observation as seed
        last_obs = self._buffer[-1] if self._buffer else None
        self._buffer = []
        if last_obs:
            last_obs["evolution_state"] = "LIVE"
            self._buffer.append(last_obs)
            self._live_index = 0
        
        self._current_batch_index += 1
        self._current_batch = SnapshotBatch(
            batch_id=self._current_batch_index + 1,
            start_index=self._total_observations,
            end_index=self._total_observations + self._max_size - 1
        )
        self._current_batch.lifecycle_state = "LIVE"
        if last_obs:
            self._current_batch.add(last_obs)
    
    def get(self, index: int) -> Optional[dict]:
        """Dapatkan observation by candle_index."""
        for obs in self._buffer:
            if obs.get("candle_index") == index:
                return obs
        for batch in self._completed_batches:
            for obs in batch.observations:
                if obs.get("candle_index") == index:
                    obs_copy = dict(obs)
                    obs_copy["status"] = "ARCHIVED_IN_BATCH"
                    obs_copy["batch_id"] = batch.batch_id
                    return obs_copy
        return {"available": False, "candle_index": index, "status": "NOT_FOUND"}
    
    def get_live(self) -> Optional[dict]:
        if self._live_index >= 0 and self._live_index < len(self._buffer):
            return self._buffer[self._live_index]
        return None
    
    def get_range(self, start: int, end: int) -> list[dict]:
        result = []
        for obs in self._buffer:
            idx = obs.get("candle_index", -1)
            if start <= idx < end:
                result.append(obs)
        for batch in self._completed_batches:
            for obs in batch.observations:
                idx = obs.get("candle_index", -1)
                if start <= idx < end:
                    result.append(obs)
        return result
    
    def get_all(self) -> list[dict]:
        return list(self._buffer)
    
    def get_latest(self, n: int = 50) -> list[dict]:
        return self._buffer[-n:] if n < len(self._buffer) else list(self._buffer)
    
    def freeze_live(self) -> Optional[dict]:
        if self._live_index >= 0 and self._live_index < len(self._buffer):
            obs = self._buffer[self._live_index]
            obs["evolution_state"] = "FREEZE"
            return obs
        return None
    
    def get_batch(self, batch_id: int) -> Optional[SnapshotBatch]:
        if self._current_batch and self._current_batch.batch_id == batch_id:
            return self._current_batch
        for batch in self._completed_batches:
            if batch.batch_id == batch_id:
                return batch
        return None
    
    def get_all_batches(self) -> list[dict]:
        batches = []
        if self._current_batch:
            batches.append(self._current_batch.summary())
        for batch in self._completed_batches:
            batches.append(batch.summary())
        return batches
    
    def stats(self) -> dict:
        live_count = 1 if self._live_index >= 0 else 0
        frozen_count = len(self._buffer) - live_count
        total_archived = sum(b.size for b in self._completed_batches)
        return {
            "max_size": self._max_size,
            "current_size": len(self._buffer),
            "total_observations": self._total_observations,
            "live_count": live_count,
            "frozen_count": frozen_count,
            "archived_count": total_archived,
            "is_full": self.is_full,
            "live_index": self._live_index,
            "batch_count": len(self._completed_batches),
            "current_batch_id": self._current_batch.batch_id if self._current_batch else 0,
            "current_batch_size": self._current_batch.size if self._current_batch else 0,
        }
