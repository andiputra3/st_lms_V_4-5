"""
Data Provider abstraction. Binance, CSV, SQLite, Replay, Live feed.
Semua provider menghasilkan: list[Candle] + OI data.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
import json
import time
import urllib.request
import urllib.error
import sqlite3
import csv
import os

from ..core.types import Candle
from ..core.constants import MS_PER_MINUTE
from ..core.utils import PRNG, seed_from_string, clamp, round_prec
from ..foundation.symbol_manager import SymbolManager

# ── Binance Futures Constants ──────────────────────────────────
FAPI_BASE = "https://fapi.binance.com"
FAPI_KLINE = "/fapi/v1/klines"
MAX_KLINE_LIMIT = 1500
RATE_LIMIT_DELAY = 0.05


@dataclass
class ProviderConfig:
    name: str
    max_per_request: int
    rate_limit_delay: float = 0.05


class DataProvider(ABC):
    @abstractmethod
    def fetch(self, symbol: str, timeframe: str,
              start_ms: int, end_ms: Optional[int],
              limit: int) -> list[Candle]:
        ...


class BinanceFuturesProvider(DataProvider):
    def __init__(self):
        self.max_per_request = MAX_KLINE_LIMIT
        self._last_request_time: float = 0.0

    def fetch(self, symbol: str, timeframe: str,
              start_ms: int, end_ms: Optional[int],
              limit: int) -> list[Candle]:
        candles: list[Candle] = []
        current_start = start_ms
        if end_ms is None:
            end_ms = int(time.time() * 1000)
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
                    vol = float(k[5])
                    taker_buy_vol = float(k[9])
                    tbr = taker_buy_vol / vol if vol > 0 else 0.5
                    candles.append(Candle(
                        time=k[0],
                        open=float(k[1]),
                        high=float(k[2]),
                        low=float(k[3]),
                        close=float(k[4]),
                        volume=vol,
                        taker_buy_ratio=round(tbr, 4)
                    ))

                if len(data) < batch_limit:
                    break

                current_start = data[-1][0] + 1
                remaining -= len(data)

            except (urllib.error.URLError, json.JSONDecodeError, ValueError):
                break

        return candles

    def _rate_limited_get(self, url: str) -> Optional[str]:
        elapsed = time.monotonic() - self._last_request_time
        if elapsed < RATE_LIMIT_DELAY:
            time.sleep(RATE_LIMIT_DELAY - elapsed)
        self._last_request_time = time.monotonic()
        with urllib.request.urlopen(url, timeout=30) as resp:
            return resp.read().decode("utf-8")


class CSVProvider(DataProvider):
    def __init__(self, filepath: str):
        self.max_per_request = 0  # unlimited
        self._filepath = filepath

    def fetch(self, symbol: str, timeframe: str,
              start_ms: int, end_ms: Optional[int],
              limit: int) -> list[Candle]:
        candles: list[Candle] = []
        if not os.path.exists(self._filepath):
            return candles
        with open(self._filepath, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                ts = int(row["time"])
                if ts < start_ms:
                    continue
                if end_ms is not None and ts > end_ms:
                    continue
                candles.append(Candle(
                    time=ts,
                    open=float(row["open"]),
                    high=float(row["high"]),
                    low=float(row["low"]),
                    close=float(row["close"]),
                    volume=float(row["volume"]),
                    taker_buy_ratio=float(row.get("taker_buy_ratio", 0.5))
                ))
                if len(candles) >= limit:
                    break
        return candles


class SQLiteProvider(DataProvider):
    def __init__(self, db_path: str):
        self.max_per_request = 0  # unlimited
        self._db_path = db_path

    def fetch(self, symbol: str, timeframe: str,
              start_ms: int, end_ms: Optional[int],
              limit: int) -> list[Candle]:
        candles: list[Candle] = []
        if not os.path.exists(self._db_path):
            return candles
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        try:
            query = (
                "SELECT time, open, high, low, close, volume, taker_buy_ratio "
                "FROM candles WHERE symbol = ? AND timeframe = ? "
                "AND time >= ?"
            )
            params = [symbol, timeframe, start_ms]
            if end_ms is not None:
                query += " AND time <= ?"
                params.append(end_ms)
            query += " ORDER BY time ASC LIMIT ?"
            params.append(limit)

            for row in conn.execute(query, params):
                candles.append(Candle(
                    time=row["time"],
                    open=row["open"],
                    high=row["high"],
                    low=row["low"],
                    close=row["close"],
                    volume=row["volume"],
                    taker_buy_ratio=row["taker_buy_ratio"]
                ))
        finally:
            conn.close()
        return candles


class FixtureProvider(DataProvider):
    def __init__(self, seed: int = 42):
        self.max_per_request = 0  # unlimited
        self._rng = PRNG(seed)

    def fetch(self, symbol: str, timeframe: str,
              start_ms: int, end_ms: Optional[int],
              limit: int) -> list[Candle]:
        asset = SymbolManager.get(symbol)
        base_price = asset["base"]
        prec = asset["prec"]

        candles: list[Candle] = []
        price = base_price
        t0 = start_ms if start_ms is not None else 1753500000000

        for i in range(limit):
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
            else:
                drift = -step * 0.9 + (self._rng.next() - 0.6) * step * 0.6

            o = price
            cl = max(base_price * 0.2, o + drift)
            wick = step * (0.4 + self._rng.next() * 0.8)
            hi = max(o, cl) + wick * self._rng.next()
            lo = min(o, cl) - wick * self._rng.next()
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


class ReplayProvider(DataProvider):
    def __init__(self, replay_file: str):
        self.max_per_request = 0  # unlimited
        self._replay_file = replay_file

    def fetch(self, symbol: str, timeframe: str,
              start_ms: int, end_ms: Optional[int],
              limit: int) -> list[Candle]:
        candles: list[Candle] = []
        if not os.path.exists(self._replay_file):
            return candles
        with open(self._replay_file, "r") as f:
            data = json.load(f)
        for entry in data:
            ts = entry["time"]
            if ts < start_ms:
                continue
            if end_ms is not None and ts > end_ms:
                continue
            candles.append(Candle(
                time=ts,
                open=entry["open"],
                high=entry["high"],
                low=entry["low"],
                close=entry["close"],
                volume=entry["volume"],
                taker_buy_ratio=entry.get("taker_buy_ratio", 0.5)
            ))
            if len(candles) >= limit:
                break
        return candles


class LiveWebsocketProvider(DataProvider):
    def __init__(self, buffer_size: int = 1500):
        self.max_per_request = buffer_size
        self._buffer: list[Candle] = []

    def fetch(self, symbol: str, timeframe: str,
              start_ms: int, end_ms: Optional[int],
              limit: int) -> list[Candle]:
        return [c for c in self._buffer
                if c.time >= start_ms
                and (end_ms is None or c.time <= end_ms)][:limit]
