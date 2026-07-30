"""
=====================================================
MODULE:     structure_wave.py
PURPOSE:    Wave — 6 Line menjadi 1 Wave.
            13 wave structures.
            Wave mewarisi OI dari Line.
OWNER:      PHASE-07 WAVE
=====================================================
"""

from dataclasses import dataclass, field
from typing import Optional
from .line import Line


# 13 Wave Structures — Reference: MASTER_SPECIFICATION.html S4
WAVE_STRUCTURES = [
    "STRONG_ACCUMULATION", "STRONG_DISTRIBUTION",
    "CONTINUATION_UP", "CONTINUATION_DOWN",
    "CONFIRMED_RANGE", "RANGE_EXPANDING", "RANGE_COMPRESSING",
    "REVERSAL_UP", "REVERSAL_DOWN",
    "EXHAUSTION_UP", "EXHAUSTION_DOWN",
    "SIDEWAY", "CHAOS"
]


@dataclass
class Wave:
    """Satu Wave — 6 Line + 5 slope transitions."""
    lines: list[Line]
    structure: str  # salah satu dari 13 WAVE_STRUCTURES
    start_ts: int
    end_ts: int
    status: str = "CLOSED_WAVE"  # CLOSED_WAVE / PENDING_WAVE
    
    # OI inheritance dari 6 lines
    oi_profile: list[float] = field(default_factory=list)  # [oi_avg line1..line6]
    oi_trend: str = "STABLE"
    oi_divergence: str = "NONE"
    oi_interpretation: str = ""
    
    # ── Evolution Enrichment (MARKET_OBSERVATION_CONTRACT) ──
    wave_id: str = ""
    lifecycle_state: str = "NEW"
    age_candles: int = 0
    evolution: dict = field(default_factory=lambda: {
        "breakout": 0, "continuation": 0, "reversal": 0,
        "compression": 0, "expansion": 0
    })
    continuation_rate: float = 0.0
    breakout_rate: float = 0.0
    reversal_rate: float = 0.0
    reliability_score: float = 0.0
    historical_occurrences: int = 0
    dna_similarity: float = 0.0
    profit_profile: dict = field(default_factory=lambda: {
        "dominant_clone": "", "best_clone": "", "worst_clone": "",
        "historical_expectancy": 0.0
    })
    market_character: str = ""
    prediction_context: dict = field(default_factory=dict)


class WaveBuilder:
    """
    Membangun Wave dari kumpulan Line.
    
    Reference: ST_LMS_CORE.js STRUCTURE.WaveBuilder (lines 209-221)
    
    Algorithm:
        Sort lines by start_ts. Group into chunks of 6.
        Klasifikasi berdasarkan dominasi warna.
        Wave < 6 lines = PENDING_WAVE (no padding).
    """
    
    def build(self, lines: list[Line]) -> list[Wave]:
        """
        Bangun waves dari lines.
        
        Returns:
            List of Wave objects. Wave terakhir mungkin PENDING_WAVE.
        """
        sorted_lines = sorted(lines, key=lambda L: L.start_ts)
        waves: list[Wave] = []
        
        for i in range(0, len(sorted_lines), 6):
            chunk = sorted_lines[i:i+6]
            if len(chunk) < 6:
                # PENDING_WAVE — tidak cukup line
                waves.append(Wave(
                    lines=chunk,
                    structure="PENDING_WAVE",
                    start_ts=chunk[0].start_ts,
                    end_ts=chunk[-1].end_ts,
                    status="PENDING_WAVE"
                ))
                continue
            
            structure = self._classify(chunk)
            
            # OI inheritance
            oi_profile = [L.oi_avg for L in chunk if L.oi_avg is not None]
            oi_trend = self._oi_trend(chunk)
            oi_divergence = self._oi_divergence(chunk)
            oi_interpretation = self._oi_interpret(oi_trend, oi_divergence)
            
            waves.append(Wave(
                lines=chunk,
                structure=structure,
                start_ts=chunk[0].start_ts,
                end_ts=chunk[-1].end_ts,
                status="CLOSED_WAVE",
                oi_profile=oi_profile,
                oi_trend=oi_trend,
                oi_divergence=oi_divergence,
                oi_interpretation=oi_interpretation,
            ))
        
        return waves
    
    def _classify(self, chunk: list[Line]) -> str:
        """Klasifikasi wave structure dari 6 lines."""
        g = sum(1 for L in chunk if L.dominant == "HIJAU")
        r = 6 - g
        alt = sum(1 for i in range(1, 6) if chunk[i].dominant != chunk[i-1].dominant)
        
        if g >= 5:
            return "STRONG_ACCUMULATION"
        if r >= 5:
            return "STRONG_DISTRIBUTION"
        
        # REVERSAL_UP: 3 MERAH pertama, HIJAU terakhir
        if (chunk[0].dominant + chunk[1].dominant + chunk[2].dominant == "MERAHMERAHMERAH"
                and chunk[5].dominant == "HIJAU"):
            return "REVERSAL_UP"
        # REVERSAL_DOWN: 3 HIJAU pertama, MERAH terakhir
        if (chunk[0].dominant + chunk[1].dominant + chunk[2].dominant == "HIJAUHIJAUHIJAU"
                and chunk[5].dominant == "MERAH"):
            return "REVERSAL_DOWN"
        
        if g >= 4 and chunk[5].dominant == "MERAH":
            return "EXHAUSTION_UP"
        if r >= 4 and chunk[5].dominant == "HIJAU":
            return "EXHAUSTION_DOWN"
        
        if alt >= 4:
            return "CONFIRMED_RANGE"
        if g >= 3 and r == 0:
            return "CONTINUATION_UP"
        if r >= 3 and g == 0:
            return "CONTINUATION_DOWN"
        if g >= 2 and r >= 2:
            return "SIDEWAY"
        
        return "CHAOS"
    
    def _oi_trend(self, chunk: list[Line]) -> str:
        """Tentukan OI trend dari 6 lines."""
        acc = sum(1 for L in chunk if L.oi_trend == "ACCUMULATION")
        dist = sum(1 for L in chunk if L.oi_trend == "DISTRIBUTION")
        if acc > dist:
            return "ACCUMULATION"
        if dist > acc:
            return "DISTRIBUTION"
        return "STABLE"
    
    def _oi_divergence(self, chunk: list[Line]) -> str:
        """Deteksi OI vs Price divergence."""
        # Simplified: jika OI naik tapi price flat/turun -> BULLISH divergence
        oi_trend = self._oi_trend(chunk)
        first_price = chunk[0].st
        last_price = chunk[-1].st
        price_change = (last_price - first_price) / first_price * 100 if first_price > 0 else 0
        
        if oi_trend == "ACCUMULATION" and price_change < 1.0:
            return "BULLISH"
        if oi_trend == "DISTRIBUTION" and price_change > -1.0:
            return "BEARISH"
        return "NONE"
    
    def _oi_interpret(self, oi_trend: str, oi_divergence: str) -> str:
        """Interpretasi perilaku OI."""
        if oi_trend == "ACCUMULATION" and oi_divergence == "BULLISH":
            return "Smart money accumulating before breakout"
        if oi_trend == "DISTRIBUTION" and oi_divergence == "BEARISH":
            return "Smart money distributing before breakdown"
        if oi_trend == "ACCUMULATION":
            return "Institutional accumulation, strong support"
        if oi_trend == "DISTRIBUTION":
            return "Institutional distribution, weakening trend"
        return "OI stable, no clear signal"
