"""
=====================================================
MODULE:     evidence_bus.py
PURPOSE:    Evidence Layer — 3 buses (Direction, Exit, Correction).
            Direction: entry-legal witnesses (EMA, OI, VolDelta, MTF)
            Exit: close-only signals (RSI, W%R, MACD, HOLD-veto)
            Correction: market context (pp, phase, distances)
OWNER:      PHASE-08 EVIDENCE LAYER
ARCHITECTURE:
            Evidence = saksi independen. Truth buta terhadap
            indikator. Indikator buta terhadap geometri.
            W%R/MACD/RSI = EXIT ONLY, bukan entry.
=====================================================
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class DirectionBus:
    """Entry-legal witnesses."""
    ema: float = 5000
    oi: Optional[float] = None
    oi_status: str = "INSUFFICIENT_DATA"
    oi_source: str = "NONE"
    vd: float = 5000
    mtf_long: float = 5000
    mtf_short: float = 5000


@dataclass
class ExitBus:
    """Close-only exit signals."""
    rsi: Optional[float] = None
    wpr: Optional[float] = None
    macd_hist: Optional[float] = None
    hold: bool = False
    vel: Optional[float] = None
    acc: Optional[float] = None
    vel_signal: str = "SILENT"
    acc_signal: str = "SILENT"
    early_invalidation: bool = False


@dataclass
class CorrectionBus:
    """Market context."""
    price_position: float = 0.5
    market_phase: str = "TRANSITION"
    dist_ceiling: Optional[float] = None
    dist_floor: Optional[float] = None
    wave_structure: Optional[str] = None
    cage_status: str = "NONE"
    cage_range_atr: Optional[float] = None
    breakout: str = "NONE"


class EvidenceEngine:
    """Membangun 3 evidence buses dari truth + structure data."""
    
    def __init__(self):
        self._wpr_vel_deadzone = 5
        self._wpr_acc_deadzone = 8
    
    def dir_bus(self, sp: dict, oi_score: Optional[float],
                oi_status: str, oi_source: str,
                mtf_long: float, mtf_short: float) -> DirectionBus:
        """Bangun Direction Bus."""
        ema_score = self._score(sp.get("ema_slope", 0) * 500, 0, 10000)
        vd_score = self._score(sp.get("vol_delta", 0) * 2500, 0, 10000)
        return DirectionBus(
            ema=ema_score, oi=oi_score, oi_status=oi_status,
            oi_source=oi_source, vd=vd_score,
            mtf_long=mtf_long, mtf_short=mtf_short
        )
    
    def exit_bus(self, sp: dict) -> ExitBus:
        """Bangun Exit Bus. W%R/MACD/RSI = EXIT ONLY."""
        macd = sp.get("macd_hist")
        prev_macd = sp.get("prev_macd_hist")
        expand = prev_macd is not None and macd is not None and abs(macd) > abs(prev_macd)
        acc = sp.get("acc")
        with_side = acc is not None and abs(acc) > self._wpr_acc_deadzone
        hold = expand and with_side
        
        vel = sp.get("vel")
        early = vel is not None and abs(vel) > self._wpr_vel_deadzone
        
        vel_sig = "SILENT"
        if vel is not None and abs(vel) > self._wpr_vel_deadzone:
            vel_sig = "ACTIVE"
        
        acc_sig = "SILENT"
        if acc is not None and abs(acc) > self._wpr_acc_deadzone:
            acc_sig = "ACTIVE"
        
        return ExitBus(
            rsi=sp.get("rsi"), wpr=sp.get("wpr"),
            macd_hist=macd, hold=hold,
            vel=vel, acc=acc,
            vel_signal=vel_sig, acc_signal=acc_sig,
            early_invalidation=early
        )
    
    def correction_bus(self, sp: dict, cage, wave_structure: Optional[str]) -> CorrectionBus:
        """Bangun Correction Bus."""
        phase = "TREND" if cage.status == "NONE" else "SIDEWAY"
        dist_ceiling = cage.upper - sp.get("close", 0) if cage.upper else None
        dist_floor = sp.get("close", 0) - cage.lower if cage.lower else None
        
        return CorrectionBus(
            price_position=cage.pp,
            market_phase=phase,
            dist_ceiling=dist_ceiling,
            dist_floor=dist_floor,
            wave_structure=wave_structure,
            cage_status=cage.status,
            cage_range_atr=cage.range_atr,
            breakout=cage.breakout
        )
    
    def oi_inherit(self, oi_series: dict[int, float], ts: int) -> tuple:
        """OI inheritance dengan freshness-weighted scoring."""
        if not oi_series:
            return None, "INSUFFICIENT_DATA", "NONE"
        slot = (ts // 300000) * 300000
        value = oi_series.get(slot)
        if value is None:
            return None, "INSUFFICIENT_DATA", "NONE"
        age_min = (ts - slot) / 60000
        fresh = max(0, 1 - age_min / 5)
        score = min(10000, max(0, 5000 + value * 0.00001 * fresh))
        return int(score), "OK", "PROXY_FROM_VOLUME_DERIVED"
    
    def mtf_sector(self, wave_structure: str, st_dir: int) -> tuple:
        """Multi-Timeframe sector dari wave structure."""
        mtf_table = {
            "STRONG_ACCUMULATION": ("BULLISH_TREND", 8500),
            "STRONG_DISTRIBUTION": ("BEARISH_TREND", 8500),
            "CONTINUATION_UP": ("BULLISH_TREND", 7000),
            "CONTINUATION_DOWN": ("BEARISH_TREND", 7000),
            "CONFIRMED_RANGE": ("RANGE", 7500),
            "RANGE_EXPANDING": ("RANGE", 6500),
            "RANGE_COMPRESSING": ("COMPRESSION", 7000),
            "REVERSAL_UP": ("REVERSAL_UP", 6500),
            "REVERSAL_DOWN": ("REVERSAL_DOWN", 6500),
            "EXHAUSTION_UP": ("EXHAUSTION", 5500),
            "EXHAUSTION_DOWN": ("EXHAUSTION", 5500),
            "SIDEWAY": ("RANGE", 7000),
            "CHAOS": ("CHAOS", 3000),
        }
        sector, score = mtf_table.get(wave_structure, ("CHAOS", 3000))
        long_score = score if st_dir == 1 else 10000 - score
        short_score = score if st_dir == -1 else 10000 - score
        return sector, long_score, short_score
    
    def _score(self, value: float, lo: float, hi: float) -> float:
        return max(0, min(10000, 5000 + value))
