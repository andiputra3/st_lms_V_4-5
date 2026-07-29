"""
=====================================================
MODULE:     test_market_benchmark.py
PURPOSE:    Benchmark untuk Market Layer.
=====================================================
"""

import sys
import os
import time
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from stlms.market.fixture import MarketFixture
from stlms.market.artifact import MarketArtifact
from stlms.market.validator import MarketValidator
from stlms.market.package import MarketPackage
from stlms.market.consumer import MarketConsumer
from stlms.market.collection import MarketCollectionResult


class TestMarketBenchmark(unittest.TestCase):
    
    def setUp(self):
        self.fixture = MarketFixture(seed=42)
        self.artifact = MarketArtifact()
        self.validator = MarketValidator()
        self.package = MarketPackage()
        self.consumer = MarketConsumer()
    
    def test_fixture_generation_speed(self):
        """Fixture generation: target < 100ms untuk 1000 candles."""
        start = time.perf_counter()
        candles = self.fixture.generate("BTCUSDT", 1000)
        elapsed = (time.perf_counter() - start) * 1000
        self.assertLess(elapsed, 100, f"Fixture too slow: {elapsed:.1f}ms")
        self.assertEqual(len(candles), 1000)
    
    def test_artifact_production_speed(self):
        """Artifact production: target < 200ms untuk 500 cards."""
        candles = self.fixture.generate("BTCUSDT", 500)
        oi = self.fixture.generate_oi_series(candles)
        result = MarketCollectionResult(
            symbol="BTCUSDT", timeframe="1m",
            candles=candles, open_interest=oi,
            funding_rates={}, ls_ratio={}, taker_volume={},
            collection_start_ms=candles[0].time,
            collection_end_ms=candles[-1].time, gaps=[]
        )
        start = time.perf_counter()
        cards = self.artifact.produce(result)
        elapsed = (time.perf_counter() - start) * 1000
        self.assertLess(elapsed, 200, f"Artifact too slow: {elapsed:.1f}ms")
        self.assertEqual(len(cards), 500)
    
    def test_validation_speed(self):
        """Validation: target < 100ms untuk 500 cards."""
        candles = self.fixture.generate("BTCUSDT", 500)
        result = MarketCollectionResult(
            symbol="BTCUSDT", timeframe="1m",
            candles=candles, open_interest={},
            funding_rates={}, ls_ratio={}, taker_volume={},
            collection_start_ms=candles[0].time,
            collection_end_ms=candles[-1].time, gaps=[]
        )
        cards = self.artifact.produce(result)
        start = time.perf_counter()
        for card in cards:
            self.validator.validate(card)
        elapsed = (time.perf_counter() - start) * 1000
        self.assertLess(elapsed, 100, f"Validation too slow: {elapsed:.1f}ms")
    
    def test_memory_footprint(self):
        """Memory: 1000 cards harus < 10 MB."""
        candles = self.fixture.generate("BTCUSDT", 1000)
        result = MarketCollectionResult(
            symbol="BTCUSDT", timeframe="1m",
            candles=candles, open_interest={},
            funding_rates={}, ls_ratio={}, taker_volume={},
            collection_start_ms=candles[0].time,
            collection_end_ms=candles[-1].time, gaps=[]
        )
        cards = self.artifact.produce(result)
        # Estimate: each card ~2KB -> 1000 cards ~2MB
        import json
        size = len(json.dumps([c.to_dict() for c in cards[:10]]))
        estimated_total = size * 100
        self.assertLess(estimated_total, 2_000_000, 
                        f"Memory estimate too high: {estimated_total} bytes")
    
    def test_package_build_speed(self):
        """Package build: target < 50ms untuk 500 cards."""
        candles = self.fixture.generate("BTCUSDT", 500)
        result = MarketCollectionResult(
            symbol="BTCUSDT", timeframe="1m",
            candles=candles, open_interest={},
            funding_rates={}, ls_ratio={}, taker_volume={},
            collection_start_ms=candles[0].time,
            collection_end_ms=candles[-1].time, gaps=[]
        )
        cards = self.artifact.produce(result)
        start = time.perf_counter()
        self.package.build(cards)
        elapsed = (time.perf_counter() - start) * 1000
        self.assertLess(elapsed, 50, f"Package too slow: {elapsed:.1f}ms")


if __name__ == "__main__":
    unittest.main(verbosity=2)
