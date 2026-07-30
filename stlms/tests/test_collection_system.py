"""
ST-LMS v4 — Collection System Tests
====================================
Tests for AutoBatchCalculator, ContinuityValidator,
HistoricalCollectionEngine, and Provider abstraction.
"""
import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from stlms.market.batch_collector import (
    AutoBatchCalculator, ContinuityValidator,
    HistoricalCandleBuilder, HistoricalCollectionEngine, BatchPlan
)
from stlms.market.provider import FixtureProvider, DataProvider
from stlms.core.types import Candle
from stlms.core.constants import MS_PER_MINUTE


class TestAutoBatchCalculator(unittest.TestCase):
    def test_48000_with_binance_limit(self):
        plan = AutoBatchCalculator.calculate(48000, 1500)
        self.assertEqual(plan.target_count, 48000)
        self.assertEqual(plan.total_batches, 32)
        self.assertEqual(len(plan.batch_sizes), 32)
        self.assertEqual(sum(plan.batch_sizes), 48000)

    def test_different_provider_limits(self):
        plan_2000 = AutoBatchCalculator.calculate(48000, 2000)
        self.assertEqual(plan_2000.total_batches, 24)
        self.assertEqual(sum(plan_2000.batch_sizes), 48000)

        plan_500 = AutoBatchCalculator.calculate(48000, 500)
        self.assertEqual(plan_500.total_batches, 96)
        self.assertEqual(sum(plan_500.batch_sizes), 48000)

    def test_unlimited_provider_single_batch(self):
        plan = AutoBatchCalculator.calculate(48000, 0)
        self.assertEqual(plan.total_batches, 1)
        self.assertEqual(plan.batch_sizes, [48000])
        self.assertEqual(plan.max_per_request, 0)
        self.assertEqual(plan.provider_name, "unlimited")

    def test_small_target(self):
        plan = AutoBatchCalculator.calculate(100, 1500)
        self.assertEqual(plan.total_batches, 1)
        self.assertEqual(plan.batch_sizes, [100])
        self.assertEqual(sum(plan.batch_sizes), 100)

    def test_batch_sizes_sum_to_target(self):
        for target in [100, 500, 1000, 5000, 10000, 48000]:
            for limit in [100, 500, 1500, 2000]:
                plan = AutoBatchCalculator.calculate(target, limit)
                self.assertEqual(sum(plan.batch_sizes), target,
                                 f"sum mismatch: target={target}, limit={limit}")

    def test_configurable_window_sizes(self):
        for size in [100, 1000, 5000, 10000, 48000]:
            plan = AutoBatchCalculator.calculate(size, 1500)
            self.assertEqual(plan.target_count, size)
            self.assertEqual(sum(plan.batch_sizes), size)


class TestContinuityValidator(unittest.TestCase):
    def test_continuous_candles_pass(self):
        candles = [
            Candle(time=1000, open=100, high=101, low=99, close=100.5, volume=50, taker_buy_ratio=0.5),
            Candle(time=1060, open=100.5, high=102, low=100, close=101, volume=60, taker_buy_ratio=0.6),
            Candle(time=1120, open=101, high=103, low=100.5, close=102, volume=70, taker_buy_ratio=0.55),
        ]
        ok, issues = ContinuityValidator.validate(candles, 60)
        self.assertTrue(ok)
        self.assertEqual(len(issues), 0)

    def test_gap_detection(self):
        candles = [
            Candle(time=1000, open=100, high=101, low=99, close=100.5, volume=50, taker_buy_ratio=0.5),
            Candle(time=2000, open=100.5, high=102, low=100, close=101, volume=60, taker_buy_ratio=0.6),
        ]
        ok, issues = ContinuityValidator.validate(candles, 60)
        self.assertFalse(ok)
        self.assertGreater(len(issues), 0)

    def test_duplicate_detection(self):
        candles = [
            Candle(time=1000, open=100, high=101, low=99, close=100.5, volume=50, taker_buy_ratio=0.5),
            Candle(time=1060, open=100.5, high=102, low=100, close=101, volume=60, taker_buy_ratio=0.6),
        ]
        builder = HistoricalCandleBuilder()
        merged = builder.merge([candles, candles])
        self.assertEqual(len(merged), 2)

    def test_out_of_order_detection(self):
        candles = [
            Candle(time=1120, open=101, high=103, low=100.5, close=102, volume=70, taker_buy_ratio=0.55),
            Candle(time=1060, open=100.5, high=102, low=100, close=101, volume=60, taker_buy_ratio=0.6),
            Candle(time=1000, open=100, high=101, low=99, close=100.5, volume=50, taker_buy_ratio=0.5),
        ]
        builder = HistoricalCandleBuilder()
        merged = builder.merge([candles])
        self.assertEqual(merged[0].time, 1000)
        self.assertEqual(merged[1].time, 1060)
        self.assertEqual(merged[2].time, 1120)


class TestHistoricalCollectionEngine(unittest.TestCase):
    def test_collect_with_fixture_provider(self):
        provider = FixtureProvider(seed=42)
        engine = HistoricalCollectionEngine(provider, target_count=100)
        result = engine.collect("BTCUSDT", "1m")
        self.assertIn("candles", result)
        self.assertEqual(result["total_collected"], 100)
        self.assertEqual(len(result["candles"]), 100)
        self.assertIsInstance(result["candles"][0], Candle)

    def test_collect_reports_batch_plan(self):
        provider = FixtureProvider(seed=42)
        engine = HistoricalCollectionEngine(provider, target_count=100)
        result = engine.collect("BTCUSDT", "1m", max_per_request=30)
        plan = result["batch_plan"]
        self.assertEqual(plan["target_count"], 100)
        self.assertEqual(plan["max_per_request"], 30)
        self.assertGreater(plan["total_batches"], 1)
        self.assertEqual(sum(plan["batch_sizes"]), 100)

    def test_collect_validates_continuity(self):
        provider = FixtureProvider(seed=42)
        engine = HistoricalCollectionEngine(provider, target_count=50)
        result = engine.collect("BTCUSDT", "1m")
        self.assertIn("continuity_ok", result)
        self.assertTrue(result["continuity_ok"])
        self.assertEqual(len(result["continuity_issues"]), 0)

    def test_collect_configurable_window(self):
        for count in [50, 100, 200]:
            provider = FixtureProvider(seed=42)
            engine = HistoricalCollectionEngine(provider, target_count=count)
            result = engine.collect("BTCUSDT", "1m")
            self.assertEqual(result["total_collected"], count)
            self.assertEqual(len(result["candles"]), count)


class TestProviderAbstraction(unittest.TestCase):
    def test_fixture_provider_produces_candles(self):
        provider = FixtureProvider(seed=42)
        candles = provider.fetch("BTCUSDT", "1m", 1753500000000, None, 50)
        self.assertEqual(len(candles), 50)
        for c in candles:
            self.assertIsInstance(c, Candle)
            self.assertGreater(c.high, 0)
            self.assertGreaterEqual(c.high, c.low)
            self.assertGreaterEqual(c.high, c.open)
            self.assertGreaterEqual(c.high, c.close)

    def test_providers_have_fetch_method(self):
        provider = FixtureProvider(seed=42)
        self.assertTrue(hasattr(provider, "fetch"))
        self.assertTrue(callable(provider.fetch))

    def test_provider_max_per_request(self):
        provider = FixtureProvider(seed=42)
        self.assertTrue(hasattr(provider, "max_per_request"))
        self.assertIsInstance(provider.max_per_request, int)
