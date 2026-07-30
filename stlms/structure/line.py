"""
=====================================================
MODULE:     structure_line.py
PURPOSE:    Supertrend Line — kumpulan SP dengan st sama.
            Line mewarisi OI, volume, distance dari SP.
OWNER:      PHASE-05 SUPERTREND LINE
ARCHITECTURE:
            Line = rangkaian SP dengan st_canon sama (>=4).
            Line adalah "dinding" support/resistance.
            Line mewarisi seluruh properti dari member SP.
=====================================================
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Line:
    """Satu Supertrend Line — dinding support atau resistance."""
    st: float
    key: str  # st_canon
    start_ts: int
    end_ts: int
    members: int  # jumlah SP dalam line
    dominant: str  # HIJAU / MERAH
    role: str  # SUPPORT (HIJAU-dominant) / RESISTANCE (MERAH-dominant)
    green_count: int = 0
    red_count: int = 0
    flip_count: int = 0
    
    # OI inheritance dari member SP
    oi_avg: Optional[float] = None
    oi_start: Optional[float] = None
    oi_end: Optional[float] = None
    oi_trend: str = "STABLE"  # ACCUMULATION / DISTRIBUTION / STABLE
    oi_delta_pct: float = 0.0
    
    # ── Evolution Enrichment (MARKET_OBSERVATION_CONTRACT) ──
    line_id: str = ""
    lifecycle_state: str = "NEW"
    age_candles: int = 0
    mutation_count: int = 0
    reliability_score: float = 0.0
    strength: float = 0.0
    continuation_rate: float = 0.0
    survival_rate: float = 0.0
    historical_occurrences: int = 0
    dna_similarity: float = 0.0
    market_character: str = ""
    best_clone: str = ""
    worst_clone: str = ""
    death_reason: str = ""


class LineBuilder:
    """
    Membangun Line dari kumpulan Supertrend Point.
    
    Algorithm:
        Group consecutive SP dengan st_canon yang sama.
        Line valid jika >= 4 members.
    
    Reference: ST_LMS_CORE.js STRUCTURE.LineBuilder (lines 190-198)
    """
    
    def build(self, points: list[dict]) -> list[Line]:
        """
        Bangun lines dari list of SP dicts.
        
        Args:
            points: List of dict dengan keys: ts, st, st_canon, color, oi_value
        
        Returns:
            List of Line objects
        """
        lines: list[Line] = []
        if not points:
            return lines
        
        cur_members: list[dict] = []
        cur_key = None
        
        for p in points:
            key = p.get("st_canon", "")
            if cur_key is None:
                cur_key = key
                cur_members.append(p)
            elif key == cur_key:
                cur_members.append(p)
            else:
                if len(cur_members) >= 4:
                    lines.append(self._finish_line(cur_members))
                cur_key = key
                cur_members = [p]
        
        # Last group
        if len(cur_members) >= 4:
            lines.append(self._finish_line(cur_members))
        
        return lines
    
    def _finish_line(self, members: list[dict]) -> Line:
        """Selesaikan satu line dari member SP."""
        green = sum(1 for m in members if m.get("color") == "HIJAU")
        red = len(members) - green
        dominant = "HIJAU" if green >= red else "MERAH"
        role = "SUPPORT" if dominant == "HIJAU" else "RESISTANCE"
        
        # OI inheritance
        oi_vals = [m.get("oi_value") for m in members if m.get("oi_value") is not None]
        oi_avg = sum(oi_vals) / len(oi_vals) if oi_vals else None
        oi_start = oi_vals[0] if oi_vals else None
        oi_end = oi_vals[-1] if oi_vals else None
        
        oi_trend = "STABLE"
        oi_delta_pct = 0.0
        if oi_start and oi_end and oi_start > 0:
            oi_delta_pct = (oi_end - oi_start) / oi_start * 100
            if oi_delta_pct > 2.0:
                oi_trend = "ACCUMULATION"
            elif oi_delta_pct < -2.0:
                oi_trend = "DISTRIBUTION"
        
        return Line(
            st=members[0].get("st", 0),
            key=members[0].get("st_canon", ""),
            start_ts=members[0].get("ts", 0),
            end_ts=members[-1].get("ts", 0),
            members=len(members),
            dominant=dominant,
            role=role,
            green_count=green,
            red_count=red,
            flip_count=min(green, red),
            oi_avg=oi_avg,
            oi_start=oi_start,
            oi_end=oi_end,
            oi_trend=oi_trend,
            oi_delta_pct=oi_delta_pct,
        )
