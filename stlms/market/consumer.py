"""
=====================================================
MODULE:     market_consumer.py
PURPOSE:    Market Consumer — downstream API untuk
            TRUTH layer. Menyediakan query interface.
OWNER:      PHASE-02 MARKET ARTIFACT
INPUT:      market_snapshot cards
OUTPUT:     Consumable format untuk TRUTH
DEPENDENCY: stlms.foundation.base_consumer (BaseConsumer)
ARCHITECTURE:
            Consumer adalah API interface. TRUTH membaca
            market_snapshot melalui consumer ini.
            Tidak melakukan komputasi — hanya transformasi format.
=====================================================
"""

from typing import Any, Optional
from ..core.utils import Card
from ..core.types import Candle, DataStatus
from ..foundation.base_consumer import BaseConsumer


class MarketConsumer(BaseConsumer):
    """
    Consumer API untuk market_snapshot cards.
    
    Consumer: TRUTH layer
    Transform: Card -> Candle (untuk PointBuilder)
    """
    
    def __init__(self):
        super().__init__("MARKET")
    
    def consume(self, card: Card) -> dict:
        """
        Transform card ke format yang dikonsumsi TRUTH.
        
        Returns:
            Dict dengan candle data + OI + funding.
        """
        p = card.payload
        return {
            "ts": p.get("ts"),
            "symbol": p.get("symbol"),
            "timeframe": p.get("timeframe"),
            "candle": Candle(
                time=p.get("ts", 0),
                open=p.get("open", 0.0),
                high=p.get("high", 0.0),
                low=p.get("low", 0.0),
                close=p.get("close", 0.0),
                volume=p.get("volume", 0.0),
                taker_buy_ratio=p.get("taker_buy_ratio", 0.5),
            ),
            "oi_value": p.get("oi_value"),
            "funding_rate": p.get("funding_rate"),
            "data_status": p.get("data_status", "ok"),
            "gap_flag": p.get("gap_flag", False),
            "wib_iso": p.get("wib_iso", ""),
            "card_id": card.entity_id,
            "card_checksum": card.checksum,
        }
    
    def query(self, **filters) -> list[dict]:
        """
        Query artifacts dengan filter.
        
        Supported filters:
            symbol: str
            timeframe: str
            start_ts: int
            end_ts: int
        """
        # Placeholder — full implementation saat integrasi SQLite
        return []
    
    def to_candles(self, cards: list[Card]) -> list[Candle]:
        """Konversi cards ke list of Candle untuk PointBuilder."""
        return [
            Candle(
                time=c.payload["ts"],
                open=c.payload["open"],
                high=c.payload["high"],
                low=c.payload["low"],
                close=c.payload["close"],
                volume=c.payload["volume"],
                taker_buy_ratio=c.payload.get("taker_buy_ratio", 0.5),
            )
            for c in cards
        ]
    
    def to_oi_series(self, cards: list[Card]) -> dict[int, float]:
        """
        Ekstrak OI series dari cards.
        
        OI OWNERSHIP: Satu OI value untuk banyak cards dalam slot yang sama.
        Returns dict[ts_slot, oi_value].
        """
        oi: dict[int, float] = {}
        for c in cards:
            oi_val = c.payload.get("oi_value")
            if oi_val is not None:
                ts = c.payload["ts"]
                slot = (ts // 300000) * 300000  # 5m slot
                if slot not in oi:
                    oi[slot] = oi_val
        return oi
