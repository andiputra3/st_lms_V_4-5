"""
=====================================================
MODULE:     truth/observation.py
PURPOSE:    TruthObservationObject — wrapper untuk
            TruthPoint + lifecycle + version +
            mutation + reliability + structure_context +
            mtf_context + clone_context +
            statistics_context + historical_index +
            timeline_entry
OWNER:      TRUTH LAYER (Stage 2)
ARCHITECTURE: Market Observation Contract
            1 Candle = 1 Market Observation Object
=====================================================
"""

from dataclasses import dataclass, field
from typing import Optional
from .point import TruthPoint


@dataclass
class TruthObservationObject:
    """
    Satu Truth Observation = 1 candle.
    Berisi TruthPoint + seluruh metadata observasi.
    
    Reference: MARKET_OBSERVATION_CONTRACT.md
    """
    # ── TruthPoint (15 indikator) ──────────────────────────
    point: Optional[TruthPoint] = None
    
    # ── Identity ───────────────────────────────────────────
    observation_id: str = ""
    candle_index: int = 0
    
    # ── Lifecycle ──────────────────────────────────────────
    pipeline_state: str = "OPEN"
    evolution_state: str = "NEW"
    lifecycle_history: list = field(default_factory=list)
    
    # ── Version ────────────────────────────────────────────
    version: int = 1
    mutation_count: int = 0
    
    # ── Mutation ───────────────────────────────────────────
    mutation_delta: Optional[dict] = None
    
    # ── Reliability ────────────────────────────────────────
    reliability: Optional[dict] = None
    
    # ── Structure Context ──────────────────────────────────
    structure_context: Optional[dict] = None
    
    # ── MTF Context (inherited from higher TFs) ────────────
    mtf_context: Optional[dict] = None
    
    # ── Clone Context ──────────────────────────────────────
    clone_context: Optional[dict] = None
    
    # ── Statistics Context ─────────────────────────────────
    statistics_context: Optional[dict] = None
    
    # ── Historical Index ───────────────────────────────────
    historical_index: int = 0
    snapshot_batch_id: str = ""
    
    # ── Timeline ───────────────────────────────────────────
    timeline_entry: Optional[dict] = None
    
    # ── Events ─────────────────────────────────────────────
    events: list = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "observation_id": self.observation_id,
            "candle_index": self.candle_index,
            "pipeline_state": self.pipeline_state,
            "evolution_state": self.evolution_state,
            "version": self.version,
            "mutation_count": self.mutation_count,
            "reliability": self.reliability,
            "structure_context": self.structure_context,
            "mtf_context": self.mtf_context,
            "clone_context": self.clone_context,
            "statistics_context": self.statistics_context,
            "historical_index": self.historical_index,
            "snapshot_batch_id": self.snapshot_batch_id,
        }
