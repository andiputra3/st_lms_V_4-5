"""
=====================================================
MODULE:     market_fixture.py
PURPOSE:    Market fixture generator untuk testing offline.
            Menghasilkan synthetic candle data untuk
            development dan testing tanpa Binance API.
OWNER:      PHASE-01 MARKET COLLECTION
INPUT:      Symbol, count, seed
OUTPUT:     list[Candle]
DEPENDENCY: stlms.core.utils (PRNG), stlms.foundation.symbol_manager
ARCHITECTURE:
            Fixture mensimulasikan pergerakan harga dengan
            phase: SIDE -> UP -> DOWN -> SIDE.
            Mencakup berbagai kondisi market: trending,
            ranging, breakout, pullback.
            Digunakan saat Binance API tidak tersedia.
=====================================================
"""

from ..core.types import Candle
from ..core.utils import PRNG, seed_from_string, clamp, round_prec
from ..core.constants import MS_PER_MINUTE
from ..foundation.symbol_manager import SymbolManager


class MarketFixture:
    """
    Generate synthetic market data untuk testing.
    
    Phase cycle (per 200 candles):
        SIDE (60): sideways / ranging
        UP (50): uptrend
        DOWN (50): downtrend
        SIDE (40): sideways / ranging
    
    Reference: ST_LMS_CORE.js MARKET.fixture (line 140-146)
    """
    
    def __init__(self, seed: int = 42):
        self._rng = PRNG(seed)
    
    def generate(self, symbol: str, count: int,
                 start_time_ms: int = 1753500000000) -> list[Candle]:
        """
        Generate synthetic candles.
        
        Args:
            symbol: Trading pair
            count: Number of candles to generate
            start_time_ms: Starting timestamp
        
        Returns:
            List of Candle objects
        """
        asset = SymbolManager.get(symbol)
        base_price = asset["base"]
        prec = asset["prec"]
        
        candles: list[Candle] = []
        price = base_price
        t0 = start_time_ms
        
        for i in range(count):
            c = i % 200
            if c < 60:
                phase = "SIDE"
            elif c < 110:
                phase = "UP"
            elif c < 150:
                phase = "DOWN"
            else:
                phase = "SIDE"
            
            step = base_price * 0.0030
            
            if phase == "SIDE":
                drift = (self._rng.next() - 0.5) * step * 0.5 + (base_price - price) * 0.02
            elif phase == "UP":
                drift = step * 0.9 + (self._rng.next() - 0.4) * step * 0.6
            else:  # DOWN
                drift = -step * 0.9 + (self._rng.next() - 0.6) * step * 0.6
            
            o = price
            cl = max(base_price * 0.2, o + drift)
            wick = step * (0.4 + self._rng.next() * 0.8)
            hi = max(o, cl) + wick * self._rng.next()
            lo = min(o, cl) - wick * self._rng.next()
            
            # Taker buy ratio: bias toward trend direction
            tbr = clamp(0.5 + 0.18 * (1 if drift > 0 else -1) + (self._rng.next() - 0.5) * 0.1, 0.05, 0.95)
            
            candles.append(Candle(
                time=t0 + i * MS_PER_MINUTE,
                open=round_prec(o, prec),
                high=round_prec(hi, prec),
                low=round_prec(lo, prec),
                close=round_prec(cl, prec),
                volume=100 + self._rng.next() * 900,
                taker_buy_ratio=round_prec(tbr, 4)
            ))
            
            price = cl
        
        return candles
    
    def generate_oi_series(self, candles: list[Candle]) -> dict[int, float]:
        """
        Generate synthetic OI data (5m timeframe).
        
        OI OWNERSHIP: 1 OI slot = 5 candles (5 menit).
        OI meningkat dalam uptrend, menurun dalam downtrend.
        """
        oi: dict[int, float] = {}
        base_oi = 100_000_000  # 100M
        
        for i in range(0, len(candles), 5):
            slot_ts = candles[i].time
            trend = 1 if i < len(candles) // 2 else -1
            noise = (self._rng.next() - 0.5) * 5_000_000
            oi_value = base_oi + trend * (i * 100_000) + noise
            oi[slot_ts] = max(1_000_000, oi_value)
        
        return oi
