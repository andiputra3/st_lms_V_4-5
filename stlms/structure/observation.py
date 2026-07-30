"""
=====================================================
MODULE:     structure/observation.py
PURPOSE:    StructureObservationObject — wrapper untuk
            Line/Wave/Cage context per candle
OWNER:      STRUCTURE LAYER (Stage 3)
ARCHITECTURE: Market Observation Contract
=====================================================
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class LineObservation:
    """Observasi satu Supertrend Line pada candle tertentu."""
    line_id: str = ""
    role: str = ""  # SUPPORT / RESISTANCE
    st_value: float = 0.0
    lifecycle_state: str = "NEW"
    age_candles: int = 0
    members: int = 0
    first_member_index: int = 0
    last_member_index: int = 0
    dominant_color: str = ""
    mutation_count: int = 0
    flip_count: int = 0
    reliability_score: float = 0.0
    strength: float = 0.0
    oi_avg: Optional[float] = None
    oi_trend: str = "STABLE"
    continuation_rate: float = 0.0
    survival_rate: float = 0.0
    historical_occurrences: int = 0
    dna_similarity: float = 0.0
    market_character: str = ""
    best_clone: str = ""
    worst_clone: str = ""
    death_reason: str = ""


@dataclass
class WaveObservation:
    """Observasi satu Wave pada candle tertentu."""
    wave_id: str = ""
    structure: str = "CHAOS"
    lifecycle_state: str = "NEW"
    age_candles: int = 0
    lines_count: int = 0
    support_lines: int = 0
    resistance_lines: int = 0
    evolution: dict = field(default_factory=lambda: {
        "breakout": 0, "continuation": 0, "reversal": 0,
        "compression": 0, "expansion": 0
    })
    continuation_rate: float = 0.0
    breakout_rate: float = 0.0
    reversal_rate: float = 0.0
    reliability_score: float = 0.0
    oi_trend: str = "STABLE"
    oi_divergence: str = "NONE"
    historical_occurrences: int = 0
    dna_similarity: float = 0.0
    profit_profile: dict = field(default_factory=lambda: {
        "dominant_clone": "", "best_clone": "", "worst_clone": "",
        "historical_expectancy": 0.0
    })
    market_character: str = ""
    prediction_context: dict = field(default_factory=dict)


@dataclass
class CageObservation:
    """Observasi Cage pada candle tertentu."""
    status: str = "NONE"
    upper: Optional[float] = None
    lower: Optional[float] = None
    range_pct: float = 0.0
    range_atr: Optional[float] = None
    breakout: str = "NONE"
    pp: float = 0.5
    maturity_pct: float = 0.0


@dataclass
class StructureObservationObject:
    """
    Satu Structure Observation = 1 candle.
    Berisi Line/Wave/Cage context.
    """
    observation_id: str = ""
    candle_index: int = 0
    
    # Active lines at this candle
    active_support: Optional[LineObservation] = None
    active_resistance: Optional[LineObservation] = None
    all_lines: list = field(default_factory=list)
    
    # Active wave at this candle
    current_wave: Optional[WaveObservation] = None
    
    # Current cage
    current_cage: Optional[CageObservation] = None
    
    # Market phase
    market_phase: str = "TRANSITION"
    
    def to_dict(self) -> dict:
        return {
            "observation_id": self.observation_id,
            "candle_index": self.candle_index,
            "market_phase": self.market_phase,
            "active_support": self.active_support.__dict__ if self.active_support else None,
            "active_resistance": self.active_resistance.__dict__ if self.active_resistance else None,
            "current_wave": self.current_wave.__dict__ if self.current_wave else None,
            "current_cage": self.current_cage.__dict__ if self.current_cage else None,
        }
