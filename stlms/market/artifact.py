"""
=====================================================
MODULE:     market_artifact.py
PURPOSE:    Market Artifact — membungkus raw market data
            menjadi immutable card (market_snapshot).
OWNER:      PHASE-02 MARKET ARTIFACT
INPUT:      MarketCollectionResult (dari Phase-01)
OUTPUT:     market_snapshot immutable cards
DEPENDENCY: stlms.core.utils (Card, IDGenerator),
            stlms.foundation.base_artifact (BaseArtifact)
ARCHITECTURE:
            Market Artifact adalah layer kedua ST-LMS.
            Setelah data dikumpulkan, data dibungkus menjadi
            immutable cards yang akan dikonsumsi oleh TRUTH.
            Satu card = satu candle = satu market_snapshot.
RUNTIME:
            Loop per candle. Setiap candle menghasilkan satu card.
            Card di-freeze (immutable) setelah dibuat.
RESOURCE:
            Memory: satu card per iterasi, tidak buffer semua.
            CPU: ringan — hanya bungkus data.
=====================================================
"""

from dataclasses import dataclass, field
from typing import Optional
from ..core.types import Candle, MarketSnapshot, DataStatus
from ..core.utils import Card, IDGenerator, wib_iso
from ..core.constants import MS_PER_MINUTE
from ..foundation.base_artifact import BaseArtifact
from .collection import MarketCollectionResult


class MarketArtifact(BaseArtifact):
    """
    Memproduksi market_snapshot immutable cards dari MarketCollectionResult.
    
    Architecture:
        Extends BaseArtifact. Setiap card = satu candle.
        Card memiliki checksum SHA-256 untuk verifikasi determinisme.
    
    Consumer:
        TRUTH layer — market_snapshot -> truth_snapshot (Phase-03)
    """
    
    def __init__(self):
        super().__init__("MARKET")
    
    def produce(self, result: MarketCollectionResult) -> list[Card]:
        """
        Produksi immutable cards dari collection result.
        
        Args:
            result: MarketCollectionResult dari MarketDataCollector.collect()
        
        Returns:
            List of immutable Card objects (satu per candle)
        """
        if not self.validate_input(result):
            raise ValueError("Invalid MarketCollectionResult")
        
        cards: list[Card] = []
        oi_data = result.open_interest
        funding_data = result.funding_rates
        gap_timestamps = set(result.gaps)
        
        for candle in result.candles:
            # OI Inheritance: cari OI slot yang mencakup timestamp candle ini
            oi_interval = 5 * MS_PER_MINUTE  # OI default 5m
            oi_slot = (candle.time // oi_interval) * oi_interval
            oi_value = oi_data.get(oi_slot)
            
            # Funding rate: cari funding terdekat
            funding_value = self._find_nearest(funding_data, candle.time)
            
            # Data status
            status = DataStatus.OK
            if candle.time in gap_timestamps:
                status = DataStatus.GAP
            
            snapshot = MarketSnapshot(
                ts=candle.time,
                symbol=result.symbol,
                timeframe=result.timeframe,
                open=candle.open,
                high=candle.high,
                low=candle.low,
                close=candle.close,
                volume=candle.volume,
                taker_buy_ratio=candle.taker_buy_ratio,
                data_status=status,
                gap_flag=(candle.time in gap_timestamps),
                wib_iso=wib_iso(candle.time)
            )
            
            # Buat immutable card
            payload = {
                "ts": snapshot.ts,
                "symbol": snapshot.symbol,
                "timeframe": snapshot.timeframe,
                "open": snapshot.open,
                "high": snapshot.high,
                "low": snapshot.low,
                "close": snapshot.close,
                "volume": snapshot.volume,
                "taker_buy_ratio": snapshot.taker_buy_ratio,
                "data_status": snapshot.data_status.value,
                "gap_flag": snapshot.gap_flag,
                "wib_iso": snapshot.wib_iso,
                "oi_value": oi_value,
                "funding_rate": funding_value,
            }
            
            deps = []
            card = self.make_card("market_snapshot", payload, deps, candle.time)
            cards.append(card)
        
        return cards
    
    def validate_input(self, result: MarketCollectionResult) -> bool:
        """Validasi input sebelum produksi artifact."""
        if not result.candles:
            return False
        if not result.symbol:
            return False
        if not result.timeframe:
            return False
        return True
    
    def _find_nearest(self, data: dict[int, float],
                      target_ts: int) -> Optional[float]:
        """Cari nilai terdekat berdasarkan timestamp."""
        if not data:
            return None
        best_ts = min(data.keys(), key=lambda t: abs(t - target_ts))
        return data.get(best_ts)


@dataclass
class MarketArtifactReport:
    """Laporan hasil produksi Market Artifact."""
    symbol: str
    timeframe: str
    cards_produced: int
    gaps_detected: int
    oi_slots: int
    funding_rates: int
    status: str = "OK"
    errors: list[str] = field(default_factory=list)
