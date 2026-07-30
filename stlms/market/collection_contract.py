"""
Market Collection Contract — LOCKED.
All data types ST-LMS must collect from Binance Futures.
OHLCV, OI, Funding, Trades, Orderbook, Taker Ratio, Ticker, LS Ratio, Liquidation.
STATUS: EVOLUTION_ALLOWED — data types can expand.
"""
from dataclasses import dataclass, field


@dataclass
class CompleteMarketData:
    symbol: str
    timeframe: str
    candles: list = field(default_factory=list)
    open_interest: dict = field(default_factory=dict)
    funding_rates: dict = field(default_factory=dict)
    ls_ratio: dict = field(default_factory=dict)
    taker_volume: dict = field(default_factory=dict)
    liquidations: dict = field(default_factory=dict)
    ticker_24hr: dict = field(default_factory=dict)
    order_book: dict = field(default_factory=dict)
    trades: list = field(default_factory=list)
    gaps: list = field(default_factory=list)


class MarketCollectionContract:
    """Defines what data ST-LMS MUST collect. All 10 data types."""

    REQUIRED_DATA_TYPES = [
        "OHLCV",
        "OpenInterest",
        "FundingRate",
        "Liquidation",
        "LongShortRatio",
        "TakerBuyRatio",
        "Ticker24hr",
        "OrderBook",
        "Trades",
        "TimestampGap",
    ]

    @classmethod
    def validate(cls, data: CompleteMarketData) -> tuple[bool, list[str]]:
        missing = []
        if not data.candles:
            missing.append("OHLCV")
        if not data.open_interest:
            missing.append("OpenInterest")
        if not data.ticker_24hr:
            missing.append("Ticker24hr")
        return len(missing) == 0, missing

    @classmethod
    def get_collection_plan(cls, target_count=48000, max_per_request=1500) -> dict:
        batches = (target_count + max_per_request - 1) // max_per_request
        return {
            "target": target_count,
            "max_per_request": max_per_request,
            "batches": batches,
            "provider": "BinanceFutures",
        }
