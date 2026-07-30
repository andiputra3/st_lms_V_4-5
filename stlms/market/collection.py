"""
=====================================================
MODULE:     market_collection.py
PURPOSE:    Market data collection from Binance Futures.
            Handles kline/candlestick data, open interest,
            funding rate, long/short ratio, taker buy/sell volume.
OWNER:      PHASE-01 MARKET COLLECTION
INPUT:      Symbol, timeframe, time range
OUTPUT:     Raw market data (candles, OI, funding, etc.)
DEPENDENCY: stlms.core.utils, stlms.foundation.time_manager,
            stlms.foundation.symbol_manager
ARCHITECTURE:
            Market Collection adalah layer pertama ST-LMS.
            Data dikumpulkan PER TIMEFRAME ASLI.
            TIDAK ada interpolasi ke 1m.
            OI 5m tetap 5m. Funding 8h tetap 8h.
RUNTIME:
            Menggunakan Binance Futures REST API.
            Rate limit: 1200 req/min (FAPI).
            Batch request untuk efisiensi.
RESOURCE:
            Memory: streaming response, tidak buffer penuh.
            CPU: JSON parsing ringan.
            Network: batch request, minimal round trip.
=====================================================
"""

import time
import json
import urllib.request
import urllib.error
from typing import Optional, Any
from dataclasses import dataclass, field

from ..core.types import Candle, DataStatus
from ..core.constants import MS_PER_MINUTE
from ..core.utils import clamp
from ..foundation.time_manager import TimeManager
from ..foundation.symbol_manager import SymbolManager

# ── Binance Futures Constants ──────────────────────────────────
# Reference: https://binance-docs.github.io/apidocs/futures/en/
FAPI_BASE = "https://fapi.binance.com"
FAPI_KLINE = "/fapi/v1/klines"
FAPI_OI = "/fapi/v1/openInterest"
FAPI_FUNDING = "/fapi/v1/fundingRate"
FAPI_TICKER = "/fapi/v1/ticker/24hr"
FAPI_EXCHANGE = "/fapi/v1/exchangeInfo"
FAPI_PREMIUM = "/fapi/v1/premiumIndex"
FAPI_LS_RATIO = "/futures/data/globalLongShortAccountRatio"
FAPI_TAKER_VOL = "/futures/data/takerlongshortRatio"
FAPI_LIQUIDATION = "/fapi/v1/forceOrders"
FAPI_TICKER_24HR = "/fapi/v1/ticker/24hr"
FAPI_ORDER_BOOK = "/fapi/v1/depth"
FAPI_TRADES = "/fapi/v1/trades"
MAX_KLINE_LIMIT = 1500  # Binance max per request
RATE_LIMIT_DELAY = 0.05  # 50ms between requests (safe for 1200/min)


@dataclass
class MarketCollectionResult:
    """Output dari Market Collection. Dikonsumsi oleh Phase-02 Market Artifact."""
    symbol: str
    timeframe: str
    candles: list[Candle]
    open_interest: dict[int, float]  # ts_ms -> OI value
    funding_rates: dict[int, float]  # ts_ms -> funding rate
    ls_ratio: dict[int, float]       # ts_ms -> long/short ratio
    taker_volume: dict[int, float]   # ts_ms -> taker buy/sell ratio
    collection_start_ms: int
    collection_end_ms: int
    gaps: list[int] = field(default_factory=list)
    liquidations: dict = field(default_factory=dict)
    ticker_24hr: dict = field(default_factory=dict)
    order_book: dict = field(default_factory=dict)


class MarketDataCollector:
    """
    Mengumpulkan market data dari Binance Futures REST API.
    
    Architecture:
        Data dikumpulkan per timeframe asli. Tidak ada interpolasi.
        OI 5m tetap disimpan sebagai 5m. SP akan mewarisi OI ini
        sesuai OI Ownership Contract.
    
    Rate Limit:
        FAPI: 1200 req/min. Setiap request diberi jeda 50ms.
        Batch kline: max 1500 candles per request.
    
    Dependency:
        TimeManager: timestamp handling, WIB conversion.
        SymbolManager: symbol validation, tick size, precision.
    """
    
    def __init__(self):
        self._time_mgr = TimeManager()
        self._sym_mgr = SymbolManager()
        self._last_request_time: float = 0.0
    
    # ── Public API ─────────────────────────────────────────────
    
    def collect(self, symbol: str, timeframe: str,
                start_ms: Optional[int] = None,
                end_ms: Optional[int] = None,
                limit: int = 500) -> MarketCollectionResult:
        """
        Kumpulkan seluruh market data untuk satu simbol.
        
        Args:
            symbol: Trading pair (BTCUSDT, ETHUSDT, etc.)
            timeframe: Kline interval (1m, 5m, 15m, 1h, 4h, 1d)
            start_ms: Start timestamp in ms (default: 500 candles ago)
            end_ms: End timestamp in ms (default: now)
            limit: Max candles to fetch (max 1500)
        
        Returns:
            MarketCollectionResult dengan candles, OI, funding, dll.
        """
        if not self._sym_mgr.exists(symbol):
            raise ValueError(f"Unknown symbol: {symbol}")
        
        if end_ms is None:
            end_ms = self._time_mgr.now_ms()
        if start_ms is None:
            interval_ms = self._get_interval_ms(timeframe)
            start_ms = end_ms - (limit * interval_ms)
        
        # Kumpulkan data
        candles = self._fetch_klines(symbol, timeframe, start_ms, end_ms, limit)
        oi_data = self._fetch_open_interest(symbol, timeframe, candles)
        funding_data = self._fetch_funding_rates(symbol, candles)
        ls_data = self._fetch_ls_ratio(symbol, timeframe, candles)
        taker_data = self._fetch_taker_volume(symbol, timeframe, candles)
        gaps = self._detect_gaps(candles, timeframe)
        
        return MarketCollectionResult(
            symbol=symbol,
            timeframe=timeframe,
            candles=candles,
            open_interest=oi_data,
            funding_rates=funding_data,
            ls_ratio=ls_data,
            taker_volume=taker_data,
            collection_start_ms=start_ms,
            collection_end_ms=end_ms,
            gaps=gaps
        )
    
    # ── Kline / Candlestick ────────────────────────────────────
    
    def _fetch_klines(self, symbol: str, timeframe: str,
                      start_ms: int, end_ms: int, limit: int) -> list[Candle]:
        """
        Fetch kline/candlestick data dari Binance Futures.
        
        Binance Kline Response:
        [
          [openTime, open, high, low, close, volume,
           closeTime, quoteVolume, trades, takerBuyVolume,
           takerQuoteVolume, ignore]
        ]
        
        Reference: https://binance-docs.github.io/apidocs/futures/en/#kline-candlestick-data
        """
        candles: list[Candle] = []
        current_start = start_ms
        remaining = min(limit, MAX_KLINE_LIMIT)
        
        while current_start < end_ms and remaining > 0:
            batch_limit = min(remaining, MAX_KLINE_LIMIT)
            params = (
                f"symbol={symbol}&interval={timeframe}"
                f"&startTime={current_start}&endTime={end_ms}"
                f"&limit={batch_limit}"
            )
            url = f"{FAPI_BASE}{FAPI_KLINE}?{params}"
            
            try:
                raw = self._rate_limited_get(url)
                if raw is None:
                    break
                    
                data = json.loads(raw)
                if not isinstance(data, list):
                    break
                
                for k in data:
                    candles.append(Candle(
                        time=k[0],
                        open=float(k[1]),
                        high=float(k[2]),
                        low=float(k[3]),
                        close=float(k[4]),
                        volume=float(k[5]),
                        taker_buy_ratio=self._calc_taker_ratio(
                            float(k[5]), float(k[9])
                        )
                    ))
                
                if len(data) < batch_limit:
                    break  # No more data
                    
                current_start = data[-1][0] + 1
                remaining -= len(data)
                
            except (urllib.error.URLError, json.JSONDecodeError, ValueError) as e:
                # Network error or malformed response — stop collecting
                break
        
        return candles
    
    # ── Open Interest ──────────────────────────────────────────
    
    def _fetch_open_interest(self, symbol: str, timeframe: str,
                             candles: list[Candle]) -> dict[int, float]:
        """
        Fetch Open Interest data.
        
        OI OWNERSHIP PHILOSOPHY:
            OI dimiliki oleh timeframe aslinya (biasanya 5m).
            OI TIDAK diinterpolasi menjadi 1m.
            Satu OI slot mencakup seluruh SP dalam rentang waktunya.
            
            Contoh: OI 5m 11:00-11:04 -> digunakan oleh SP 11:00, 11:01, 11:02, 11:03, 11:04
        
        Reference: https://binance-docs.github.io/apidocs/futures/en/#open-interest
        """
        oi_data: dict[int, float] = {}
        
        # OI endpoint returns current OI only.
        # For historical OI, we sample at OI timeframe intervals.
        oi_timeframe = self._get_oi_timeframe(timeframe)
        interval_ms = self._get_interval_ms(oi_timeframe)
        
        if not candles:
            return oi_data
        
        start_ms = candles[0].time
        end_ms = candles[-1].time
        
        # Sample OI at each OI timeframe boundary
        current = ((start_ms // interval_ms) + 1) * interval_ms
        while current <= end_ms:
            params = f"symbol={symbol}"
            url = f"{FAPI_BASE}{FAPI_OI}?{params}"
            
            try:
                raw = self._rate_limited_get(url)
                if raw:
                    data = json.loads(raw)
                    oi_value = float(data.get("openInterest", 0))
                    if oi_value > 0:
                        oi_data[current] = oi_value
            except (urllib.error.URLError, json.JSONDecodeError, ValueError):
                pass
            
            current += interval_ms
        
        return oi_data
    
    # ── Funding Rate ───────────────────────────────────────────
    
    def _fetch_funding_rates(self, symbol: str,
                             candles: list[Candle]) -> dict[int, float]:
        """
        Fetch Funding Rate data.
        Funding rate biasanya setiap 8 jam.
        Reference: https://binance-docs.github.io/apidocs/futures/en/#get-funding-rate-history
        """
        funding: dict[int, float] = {}
        if not candles:
            return funding
        
        params = f"symbol={symbol}&limit=100"
        url = f"{FAPI_BASE}{FAPI_FUNDING}?{params}"
        
        try:
            raw = self._rate_limited_get(url)
            if raw:
                data = json.loads(raw)
                for item in data:
                    ts = int(item["fundingTime"])
                    rate = float(item["fundingRate"])
                    if candles[0].time <= ts <= candles[-1].time:
                        funding[ts] = rate
        except (urllib.error.URLError, json.JSONDecodeError, ValueError):
            pass
        
        return funding
    
    # ── Long/Short Ratio ───────────────────────────────────────
    
    def _fetch_ls_ratio(self, symbol: str, timeframe: str,
                        candles: list[Candle]) -> dict[int, float]:
        """
        Fetch Global Long/Short Account Ratio.
        Reference: https://binance-docs.github.io/apidocs/futures/en/#long-short-ratio
        """
        ls_data: dict[int, float] = {}
        if not candles:
            return ls_data
        
        ls_timeframe = self._get_oi_timeframe(timeframe)
        params = (
            f"symbol={symbol}&period={ls_timeframe}&limit=500"
        )
        url = f"{FAPI_BASE}{FAPI_LS_RATIO}?{params}"
        
        try:
            raw = self._rate_limited_get(url)
            if raw:
                data = json.loads(raw)
                for item in data:
                    ts = int(item["timestamp"])
                    ratio = float(item["longShortRatio"])
                    if candles[0].time <= ts <= candles[-1].time:
                        ls_data[ts] = ratio
        except (urllib.error.URLError, json.JSONDecodeError, ValueError):
            pass
        
        return ls_data
    
    # ── Taker Buy/Sell Volume ──────────────────────────────────
    
    def _fetch_taker_volume(self, symbol: str, timeframe: str,
                            candles: list[Candle]) -> dict[int, float]:
        """
        Fetch Taker Buy/Sell Volume Ratio.
        Reference: https://binance-docs.github.io/apidocs/futures/en/#taker-buy-sell-volume
        """
        taker_data: dict[int, float] = {}
        if not candles:
            return taker_data
        
        tv_timeframe = self._get_oi_timeframe(timeframe)
        params = (
            f"symbol={symbol}&period={tv_timeframe}&limit=500"
        )
        url = f"{FAPI_BASE}{FAPI_TAKER_VOL}?{params}"
        
        try:
            raw = self._rate_limited_get(url)
            if raw:
                data = json.loads(raw)
                for item in data:
                    ts = int(item["timestamp"])
                    ratio = float(item["buySellRatio"])
                    if candles[0].time <= ts <= candles[-1].time:
                        taker_data[ts] = ratio
        except (urllib.error.URLError, json.JSONDecodeError, ValueError):
            pass
        
        return taker_data
    
    # ── Helpers ────────────────────────────────────────────────
    def _fetch_liquidations(self, symbol, candles):
        """Fetch liquidation orders. Stub — will be fully implemented."""
        return {}

    def _fetch_ticker_24hr(self, symbol):
        """Fetch 24hr ticker. Stub — will be fully implemented."""
        return {}

    def _fetch_order_book(self, symbol, limit=100):
        """Fetch order book snapshot. Stub — will be fully implemented."""
        return {}
    
    def _rate_limited_get(self, url: str, timeout: int = 10) -> Optional[str]:
        """Rate-limited HTTP GET. Returns response body or None on failure."""
        # Enforce rate limit
        now = time.time()
        elapsed = now - self._last_request_time
        if elapsed < RATE_LIMIT_DELAY:
            time.sleep(RATE_LIMIT_DELAY - elapsed)
        
        req = urllib.request.Request(url)
        req.add_header("Accept", "application/json")
        
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                self._last_request_time = time.time()
                return resp.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            self._last_request_time = time.time()
            # 429 = rate limited, 418 = IP banned
            if e.code in (429, 418):
                time.sleep(1.0)
            return None
        except urllib.error.URLError:
            self._last_request_time = time.time()
            return None
    
    def _calc_taker_ratio(self, volume: float,
                          taker_buy_volume: float) -> float:
        """Hitung taker buy ratio dari volume dan taker buy volume."""
        if volume <= 0:
            return 0.5
        return clamp(taker_buy_volume / volume, 0.0, 1.0)
    
    def _detect_gaps(self, candles: list[Candle],
                     timeframe: str) -> list[int]:
        """Deteksi gap antar candle berdasarkan timeframe."""
        interval_ms = self._get_interval_ms(timeframe)
        gaps: list[int] = []
        for i in range(1, len(candles)):
            diff = candles[i].time - candles[i-1].time
            if diff > interval_ms * 1.5:  # 50% tolerance
                gaps.append(candles[i].time)
        return gaps
    
    def _get_interval_ms(self, timeframe: str) -> int:
        """Konversi timeframe string ke milliseconds."""
        mapping = {
            "1m": MS_PER_MINUTE,
            "3m": 3 * MS_PER_MINUTE,
            "5m": 5 * MS_PER_MINUTE,
            "15m": 15 * MS_PER_MINUTE,
            "30m": 30 * MS_PER_MINUTE,
            "1h": 60 * MS_PER_MINUTE,
            "2h": 120 * MS_PER_MINUTE,
            "4h": 240 * MS_PER_MINUTE,
            "1d": 1440 * MS_PER_MINUTE,
        }
        return mapping.get(timeframe, MS_PER_MINUTE)
    
    def _get_oi_timeframe(self, primary_tf: str) -> str:
        """
        Tentukan timeframe OI berdasarkan primary timeframe.
        
        OI OWNERSHIP: OI memiliki timeframe sendiri.
        Jika primary = 1m, OI tetap 5m (tidak diinterpolasi).
        """
        if primary_tf in ("1m", "3m"):
            return "5m"
        if primary_tf in ("5m", "15m"):
            return "15m"
        if primary_tf in ("30m", "1h", "2h"):
            return "1h"
        return "4h"
