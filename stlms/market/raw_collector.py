"""
Tahap 01 · Raw Market Collector
Tugas: HANYA mengumpulkan data mentah dari sumber eksternal.
TIDAK menghitung indikator. TIDAK membuat observation. TIDAK menyimpan.
Output: RawMarketData Object
"""
from dataclasses import dataclass, field
import time

from ..core.types import Candle
from ..core.utils import PRNG, seed_from_string, round_prec
from ..foundation.symbol_manager import SymbolManager
from .provider import DataProvider, BinanceFuturesProvider, FixtureProvider


@dataclass
class RawMarketData:
    symbol: str
    timeframe: str
    candles: list = field(default_factory=list)
    open_interest: dict = field(default_factory=dict)
    funding_rates: dict = field(default_factory=dict)
    liquidations: dict = field(default_factory=dict)
    ls_ratio: dict = field(default_factory=dict)
    taker_volume: dict = field(default_factory=dict)
    ticker_24hr: dict = field(default_factory=dict)
    order_book: dict = field(default_factory=dict)
    collection_start_ms: int = 0
    collection_end_ms: int = 0


class RawMarketCollector:
    """HANYA mengumpulkan. Tidak menghitung. Tidak menyimpan."""

    def __init__(self, provider: DataProvider | None = None):
        self._provider = provider or BinanceFuturesProvider()

    def collect(self, symbol: str, timeframe: str,
                candle_count: int = 48000) -> RawMarketData:
        start_ms = int(time.time() * 1000)
        candles = self._provider.fetch(
            symbol=symbol,
            timeframe=timeframe,
            start_ms=0,
            end_ms=None,
            limit=candle_count,
        )
        end_ms = int(time.time() * 1000)

        return RawMarketData(
            symbol=symbol,
            timeframe=timeframe,
            candles=candles,
            collection_start_ms=start_ms,
            collection_end_ms=end_ms,
        )

    def collect_from_fixture(self, symbol: str,
                             candle_count: int) -> RawMarketData:
        provider = FixtureProvider()
        start_ms = int(time.time() * 1000)
        candles = provider.fetch(
            symbol=symbol,
            timeframe="1m",
            start_ms=0,
            end_ms=None,
            limit=candle_count,
        )
        end_ms = int(time.time() * 1000)

        return RawMarketData(
            symbol=symbol,
            timeframe="1m",
            candles=candles,
            collection_start_ms=start_ms,
            collection_end_ms=end_ms,
        )
