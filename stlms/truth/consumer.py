"""
=====================================================
MODULE:     truth_consumer.py
PURPOSE:    Truth Consumer — API untuk Structure, Evidence.
=====================================================
"""

from ..core.utils import Card
from ..core.types import Candle
from ..foundation.base_consumer import BaseConsumer


class TruthConsumer(BaseConsumer):
    """Consumer API untuk truth_snapshot cards."""
    
    def __init__(self):
        super().__init__("TRUTH")
    
    def consume(self, card: Card) -> dict:
        p = card.payload
        return {
            "ts": p.get("ts"),
            "close": p.get("close"),
            "st": p.get("st"),
            "st_canon": p.get("st_canon"),
            "st_dir": p.get("st_dir"),
            "st_color": p.get("st_color"),
            "atr": p.get("atr"),
            "ema": p.get("ema"),
            "macd_hist": p.get("macd_hist"),
            "prev_macd_hist": p.get("prev_macd_hist"),
            "rsi": p.get("rsi"),
            "wpr": p.get("wpr"),
            "vel": p.get("vel"),
            "acc": p.get("acc"),
            "vol_delta": p.get("vol_delta"),
            "dist": p.get("dist"),
            "dist_atr": p.get("dist_atr"),
            "flip": p.get("flip"),
            "point_status": p.get("point_status"),
            "ema_slope": p.get("ema_slope"),
            "oi_value": p.get("oi_value"),
            "oi_delta": p.get("oi_delta"),
            "card_id": card.entity_id,
        }
    
    def query(self, **filters) -> list[dict]:
        return []
