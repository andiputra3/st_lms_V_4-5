"""
Historical Collection Engine dengan Auto Batch Calculator.
48000 = Market Observation Window. BUKAN batas API.
"""
from dataclasses import dataclass, field
from typing import Optional

from ..core.constants import MARKET_OBSERVATION_MEMORY, MS_PER_MINUTE


@dataclass
class BatchPlan:
    target_count: int
    max_per_request: int
    total_batches: int
    batch_sizes: list[int]
    provider_name: str = "auto"


class AutoBatchCalculator:
    @staticmethod
    def calculate(target_count: int, max_per_request: int) -> BatchPlan:
        if max_per_request <= 0:
            return BatchPlan(
                target_count=target_count,
                max_per_request=max_per_request,
                total_batches=1,
                batch_sizes=[target_count],
                provider_name="unlimited"
            )
        total_batches = (target_count + max_per_request - 1) // max_per_request
        batch_sizes = []
        remaining = target_count
        for _ in range(total_batches):
            size = min(remaining, max_per_request)
            batch_sizes.append(size)
            remaining -= size
        return BatchPlan(
            target_count=target_count,
            max_per_request=max_per_request,
            total_batches=total_batches,
            batch_sizes=batch_sizes,
            provider_name="auto"
        )


class ContinuityValidator:
    @staticmethod
    def validate(candles: list, timeframe_ms: int) -> tuple[bool, list[str]]:
        issues = []
        for i in range(1, len(candles)):
            expected_ts = candles[i - 1].time + timeframe_ms
            actual_ts = candles[i].time
            if actual_ts != expected_ts:
                issues.append(
                    f"Gap at index {i}: expected {expected_ts}, got {actual_ts}"
                )
        return len(issues) == 0, issues


class HistoricalCandleBuilder:
    @staticmethod
    def merge(batches: list[list]) -> list:
        all_candles = []
        seen = set()
        for batch in batches:
            for c in batch:
                if c.time not in seen:
                    all_candles.append(c)
                    seen.add(c.time)
        all_candles.sort(key=lambda c: c.time)
        return all_candles


class HistoricalCollectionEngine:
    def __init__(self, provider, target_count: int = None):
        self._provider = provider
        self._target_count = target_count or MARKET_OBSERVATION_MEMORY
        self._calculator = AutoBatchCalculator()
        self._validator = ContinuityValidator()
        self._builder = HistoricalCandleBuilder()

    def collect(self, symbol: str, timeframe: str,
                start_ms: int = None, max_per_request: int = None) -> dict:
        max_per_req = max_per_request or getattr(self._provider, "max_per_request", 1500)
        plan = self._calculator.calculate(self._target_count, max_per_req)

        all_batches = []
        for batch_idx, batch_size in enumerate(plan.batch_sizes):
            batch = self._provider.fetch(symbol, timeframe,
                                         start_ms, None, batch_size)
            all_batches.append(batch)

        candles = self._builder.merge(all_batches)

        timeframe_ms_map = {
            "1m": 60000, "3m": 180000, "5m": 300000,
            "15m": 900000, "30m": 1800000,
            "1h": 3600000, "4h": 14400000,
            "1d": 86400000, "1w": 604800000,
        }
        tf_ms = timeframe_ms_map.get(timeframe, MS_PER_MINUTE)
        continuity_ok, issues = self._validator.validate(candles, tf_ms)

        return {
            "candles": candles,
            "batch_plan": {
                "target_count": plan.target_count,
                "max_per_request": plan.max_per_request,
                "total_batches": plan.total_batches,
                "batch_sizes": plan.batch_sizes,
            },
            "continuity_ok": continuity_ok,
            "continuity_issues": issues,
            "total_collected": len(candles),
        }
