"""
=====================================================
MODULE:     evidence/mtf_inheritance.py
PURPOSE:    MTF Inheritance — propagate higher-TF
            context to 1m Supertrend Points
OWNER:      EVIDENCE LAYER (Stage 4)
ARCHITECTURE: Market Observation Contract
            5m→1m (5 SP), 15m→1m (15 SP),
            1h→1m (60 SP), 4h→1m (240 SP)
=====================================================
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class MTFContext:
    """Multi-Timeframe context untuk satu SP 1m."""
    tf_5m: Optional[dict] = None
    tf_15m: Optional[dict] = None
    tf_1h: Optional[dict] = None
    tf_4h: Optional[dict] = None
    
    def to_dict(self) -> dict:
        return {
            "tf_5m": self.tf_5m,
            "tf_15m": self.tf_15m,
            "tf_1h": self.tf_1h,
            "tf_4h": self.tf_4h,
        }


class MTFInheritance:
    """
    Propagate higher-TF TruthPoint context to 1m SPs.
    
    INHERITANCE RULES:
        1 candle 5m → 5 Truth Observations 1m
        1 candle 15m → 15 Truth Observations 1m
        1 candle 1h → 60 Truth Observations 1m
        1 candle 4h → 240 Truth Observations 1m
    
    INHERITANCE = REFERENCE, NOT INTERPOLATION.
    OI value TIDAK diubah. Hanya REFERENSI yang di-attach.
    """
    
    # Timeframe to 1m candle ratio
    TF_RATIO = {
        "5m": 5,
        "15m": 15,
        "30m": 30,
        "1h": 60,
        "2h": 120,
        "4h": 240,
        "1d": 1440,
    }
    
    def __init__(self):
        self._tf_data: dict = {}  # {timeframe: {slot_ts: TruthPoint}}
    
    def register_tf_point(self, timeframe: str, slot_ts: int, point):
        """Register higher-TF TruthPoint untuk inheritance."""
        if timeframe not in self._tf_data:
            self._tf_data[timeframe] = {}
        self._tf_data[timeframe][slot_ts] = point
    
    def get_context(self, sp_ts: int) -> MTFContext:
        """
        Dapatkan MTF context untuk SP 1m pada timestamp tertentu.
        
        Args:
            sp_ts: timestamp SP 1m
        
        Returns:
            MTFContext dengan data dari 5m, 15m, 1h, 4h
        """
        ctx = MTFContext()
        
        for tf, ratio in self.TF_RATIO.items():
            if tf not in self._tf_data:
                continue
            interval_ms = self._get_interval_ms(tf)
            slot_ts = (sp_ts // interval_ms) * interval_ms
            point = self._tf_data[tf].get(slot_ts)
            if point:
                tf_context = {
                    "st": point.st,
                    "st_dir": point.st_dir,
                    "st_color": point.st_color,
                    "atr": point.atr,
                    "ema": point.ema,
                    "rsi": point.rsi,
                    "wpr": point.wpr,
                    "dist_atr": point.dist_atr,
                    "point_status": point.point_status.value if hasattr(point.point_status, 'value') else str(point.point_status),
                }
                if tf == "5m":
                    ctx.tf_5m = tf_context
                elif tf == "15m":
                    ctx.tf_15m = tf_context
                elif tf == "1h":
                    ctx.tf_1h = tf_context
                elif tf == "4h":
                    ctx.tf_4h = tf_context
        
        return ctx
    
    def _get_interval_ms(self, timeframe: str) -> int:
        mapping = {
            "5m": 300000, "15m": 900000, "30m": 1800000,
            "1h": 3600000, "2h": 7200000, "4h": 14400000, "1d": 86400000,
        }
        return mapping.get(timeframe, 300000)
