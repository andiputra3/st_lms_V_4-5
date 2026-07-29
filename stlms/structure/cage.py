"""
=====================================================
MODULE:     structure_cage.py
PURPOSE:    Cage Engine — support/resistance walls,
            versioning, breakout detection.
            HUKUM CAGE: 2 dinding = kompresi, 1 = trend.
OWNER:      PHASE-08 STRUCTURE LAYER
=====================================================
"""

from dataclasses import dataclass, field
from typing import Optional
from .line import Line


@dataclass
class Cage:
    """Cage — sangkar harga dari 2 dinding (support + resistance)."""
    upper: Optional[float] = None
    lower: Optional[float] = None
    pp: float = 0.5  # price position 0-1
    range_atr: Optional[float] = None
    status: str = "NONE"  # NONE / VALID_COMPRESSION / LOOSE_SIDEWAY
    breakout: str = "NONE"  # NONE / IMMINENT_UP / IMMINENT_DOWN / SQUEEZE
    up_vi: Optional[int] = None
    low_vi: Optional[int] = None
    cross: bool = False
    pressure_up: bool = False
    pressure_dn: bool = False


class CageEngine:
    """
    Membangun Cage dari support/resistance lines.
    
    HUKUM CAGE (LAW-MASTER-10):
        2 dinding valid = kompresi/sideways
        1 dinding = trend (jarak seberang = NULL)
    
    Reference: ST_LMS_CORE.js STRUCTURE.CageEngine (lines 222-241)
    """
    
    def __init__(self):
        self._tight_atr = 2.0
        self._loose_atr = 4.0
        self._wall_min_dist_atr = 0.25
    
    def build(self, lines: list[Line], price: float, atr: float) -> Cage:
        """
        Bangun cage dari lines.
        
        Args:
            lines: List of Line objects
            price: Current close price
            atr: Current ATR value
        
        Returns:
            Cage object
        """
        supports = [L for L in lines if L.role == "SUPPORT" and L.st < price]
        resistances = [L for L in lines if L.role == "RESISTANCE" and L.st > price]
        
        # Sort by recency (end_ts descending)
        supports.sort(key=lambda L: L.end_ts, reverse=True)
        resistances.sort(key=lambda L: L.end_ts, reverse=True)
        
        low = supports[0] if supports else None
        up = resistances[0] if resistances else None
        
        if not low or not up:
            return Cage(
                upper=up.st if up else None,
                lower=low.st if low else None,
                status="NONE",
                up_vi=0 if up else None,
                low_vi=0 if low else None,
            )
        
        u, d = up.st, low.st
        rng = u - d
        pp_val = (price - d) / rng if rng > 0 else 0.5
        pp_val = max(0.0, min(1.0, pp_val))
        
        range_atr_val = rng / atr if atr > 0 else None
        
        # Status
        if range_atr_val is not None:
            if range_atr_val <= self._tight_atr:
                status = "VALID_COMPRESSION"
            elif range_atr_val <= self._loose_atr:
                status = "LOOSE_SIDEWAY"
            else:
                status = "NONE"
        else:
            status = "NONE"
        
        # Breakout
        breakout = "NONE"
        min_dist = self._wall_min_dist_atr * atr
        pressure_up = (u - price) < min_dist
        pressure_dn = (price - d) < min_dist
        
        if pressure_up and pressure_dn:
            breakout = "SQUEEZE"
        elif pressure_up:
            breakout = "IMMINENT_UP"
        elif pressure_dn:
            breakout = "IMMINENT_DOWN"
        
        return Cage(
            upper=u,
            lower=d,
            pp=round(pp_val, 4),
            range_atr=round(range_atr_val, 3) if range_atr_val else None,
            status=status,
            breakout=breakout,
            up_vi=0,
            low_vi=0,
            cross=False,
            pressure_up=pressure_up,
            pressure_dn=pressure_dn,
        )
