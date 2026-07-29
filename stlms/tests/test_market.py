"""
=====================================================
MODULE:     test_market.py
PURPOSE:    Unit tests untuk Market Layer (Phase-01 + Phase-02).
            Test: fixture generation, artifact production,
            package building, validation, consumer API.
=====================================================
"""

import sys
import os
import unittest
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from stlms.market.fixture import MarketFixture
from stlms.market.artifact import MarketArtifact
from stlms.market.package import MarketPackage
from stlms.market.validator import MarketValidator
from stlms.market.consumer import MarketConsumer
from stlms.market.collection import MarketCollectionResult
from stlms.core.types import Candle


class TestMarketFixture(unittest.TestCase):
    """Test fixture generator."""
    
    def setUp(self):
        self.fixture = MarketFixture(seed=42)
    
    def test_generate_candles(self):
        candles = self.fixture.generate("BTCUSDT", 100)
        self.assertEqual(len(candles), 100)
        self.assertIsInstance(candles[0], Candle)
    
    def test_candle_hygiene(self):
        """Semua candle dari fixture harus lulus hygiene."""
        candles = self.fixture.generate("BTCUSDT", 200)
        for c in candles:
            self.assertGreaterEqual(c.high, max(c.open, c.close),
                                    f"Hygiene fail at {c.time}: high < max(open,close)")
            self.assertLessEqual(c.low, min(c.open, c.close),
                                 f"Hygiene fail at {c.time}: low > min(open,close)")
            self.assertGreaterEqual(c.high, c.low)
            self.assertGreaterEqual(c.volume, 0)
    
    def test_determinism(self):
        """Fixture harus deterministik — seed sama = output sama."""
        c1 = self.fixture.generate("BTCUSDT", 50)
        f2 = MarketFixture(seed=42)
        c2 = f2.generate("BTCUSDT", 50)
        for i in range(50):
            self.assertEqual(c1[i].time, c2[i].time)
            self.assertEqual(c1[i].open, c2[i].open)
            self.assertEqual(c1[i].close, c2[i].close)
    
    def test_oi_series(self):
        """OI series: 1 OI slot = 5 candles."""
        candles = self.fixture.generate("BTCUSDT", 50)
        oi = self.fixture.generate_oi_series(candles)
        self.assertEqual(len(oi), 10)  # 50 candles / 5 = 10 slots
        for ts, val in oi.items():
            self.assertGreater(val, 0)
    
    def test_multiple_symbols(self):
        """Test semua symbol yang terdaftar."""
        for sym in ["BTCUSDT", "SOLUSDT", "AKEUSDT", "TLMUSDT"]:
            candles = self.fixture.generate(sym, 20)
            self.assertEqual(len(candles), 20)


class TestMarketArtifact(unittest.TestCase):
    """Test artifact production."""
    
    def setUp(self):
        self.fixture = MarketFixture(seed=42)
        self.artifact = MarketArtifact()
    
    def test_produce_cards(self):
        candles = self.fixture.generate("BTCUSDT", 50)
        oi = self.fixture.generate_oi_series(candles)
        result = MarketCollectionResult(
            symbol="BTCUSDT", timeframe="1m",
            candles=candles, open_interest=oi,
            funding_rates={}, ls_ratio={}, taker_volume={},
            collection_start_ms=candles[0].time,
            collection_end_ms=candles[-1].time,
            gaps=[]
        )
        cards = self.artifact.produce(result)
        self.assertEqual(len(cards), 50)
    
    def test_card_immutability(self):
        """Card harus memiliki checksum dan verifiable."""
        candles = self.fixture.generate("BTCUSDT", 10)
        oi = self.fixture.generate_oi_series(candles)
        result = MarketCollectionResult(
            symbol="BTCUSDT", timeframe="1m",
            candles=candles, open_interest=oi,
            funding_rates={}, ls_ratio={}, taker_volume={},
            collection_start_ms=candles[0].time,
            collection_end_ms=candles[-1].time,
            gaps=[]
        )
        cards = self.artifact.produce(result)
        for card in cards:
            self.assertTrue(card.verify(), f"Card verification failed: {card.entity_id}")
            self.assertIsNotNone(card.checksum)
            self.assertEqual(len(card.checksum), 64)
    
    def test_oi_in_card(self):
        """OI harus ada di payload card."""
        candles = self.fixture.generate("BTCUSDT", 25)
        oi = self.fixture.generate_oi_series(candles)
        result = MarketCollectionResult(
            symbol="BTCUSDT", timeframe="1m",
            candles=candles, open_interest=oi,
            funding_rates={}, ls_ratio={}, taker_volume={},
            collection_start_ms=candles[0].time,
            collection_end_ms=candles[-1].time,
            gaps=[]
        )
        cards = self.artifact.produce(result)
        oi_count = sum(1 for c in cards if c.payload.get("oi_value") is not None)
        self.assertGreater(oi_count, 0, "No OI values in cards")
    
    def test_validate_input(self):
        """Validasi input harus menolak data kosong."""
        empty = MarketCollectionResult(
            symbol="", timeframe="",
            candles=[], open_interest={},
            funding_rates={}, ls_ratio={}, taker_volume={},
            collection_start_ms=0, collection_end_ms=0,
            gaps=[]
        )
        self.assertFalse(self.artifact.validate_input(empty))


class TestMarketPackage(unittest.TestCase):
    """Test package building."""
    
    def setUp(self):
        self.fixture = MarketFixture(seed=42)
        self.artifact = MarketArtifact()
        self.package = MarketPackage()
    
    def test_build_report(self):
        candles = self.fixture.generate("BTCUSDT", 50)
        oi = self.fixture.generate_oi_series(candles)
        result = MarketCollectionResult(
            symbol="BTCUSDT", timeframe="1m",
            candles=candles, open_interest=oi,
            funding_rates={}, ls_ratio={}, taker_volume={},
            collection_start_ms=candles[0].time,
            collection_end_ms=candles[-1].time,
            gaps=[]
        )
        cards = self.artifact.produce(result)
        report = self.package.build(cards)
        self.assertEqual(report["candles"], 50)
        self.assertEqual(report["symbol"], "BTCUSDT")
        self.assertIn("price_summary", report)
    
    def test_summary(self):
        candles = self.fixture.generate("BTCUSDT", 10)
        result = MarketCollectionResult(
            symbol="BTCUSDT", timeframe="1m",
            candles=candles, open_interest={},
            funding_rates={}, ls_ratio={}, taker_volume={},
            collection_start_ms=candles[0].time,
            collection_end_ms=candles[-1].time,
            gaps=[]
        )
        cards = self.artifact.produce(result)
        report = self.package.build(cards)
        summary = self.package.summary(report)
        self.assertIn("BTCUSDT", summary)
        self.assertIn("1m", summary)


class TestMarketValidator(unittest.TestCase):
    """Test validation."""
    
    def setUp(self):
        self.fixture = MarketFixture(seed=42)
        self.artifact = MarketArtifact()
        self.validator = MarketValidator()
    
    def test_validate_clean_candles(self):
        """Semua fixture candle harus lulus validasi."""
        candles = self.fixture.generate("BTCUSDT", 50)
        result = MarketCollectionResult(
            symbol="BTCUSDT", timeframe="1m",
            candles=candles, open_interest={},
            funding_rates={}, ls_ratio={}, taker_volume={},
            collection_start_ms=candles[0].time,
            collection_end_ms=candles[-1].time,
            gaps=[]
        )
        cards = self.artifact.produce(result)
        for card in cards:
            results = self.validator.validate(card)
            for r in results:
                self.assertTrue(r.passed, f"{r.name} failed: {r.detail}")
    
    def test_validate_sequence(self):
        candles = self.fixture.generate("BTCUSDT", 50)
        result = MarketCollectionResult(
            symbol="BTCUSDT", timeframe="1m",
            candles=candles, open_interest={},
            funding_rates={}, ls_ratio={}, taker_volume={},
            collection_start_ms=candles[0].time,
            collection_end_ms=candles[-1].time,
            gaps=[]
        )
        cards = self.artifact.produce(result)
        results = self.validator.validate_sequence(cards)
        self.assertTrue(results[0].passed, f"Sequence failed: {results[0].detail}")
    
    def test_all_validator_pass(self):
        """Semua validasi harus PASS untuk data bersih."""
        candles = self.fixture.generate("BTCUSDT", 100)
        result = MarketCollectionResult(
            symbol="BTCUSDT", timeframe="1m",
            candles=candles, open_interest={},
            funding_rates={}, ls_ratio={}, taker_volume={},
            collection_start_ms=candles[0].time,
            collection_end_ms=candles[-1].time,
            gaps=[]
        )
        cards = self.artifact.produce(result)
        all_results = self.validator.run_all(cards)
        self.assertTrue(self.validator.is_valid(all_results),
                        f"Some validations failed: {self.validator.summary(all_results)}")


class TestMarketConsumer(unittest.TestCase):
    """Test consumer API."""
    
    def setUp(self):
        self.fixture = MarketFixture(seed=42)
        self.artifact = MarketArtifact()
        self.consumer = MarketConsumer()
    
    def test_consume_card(self):
        candles = self.fixture.generate("BTCUSDT", 5)
        result = MarketCollectionResult(
            symbol="BTCUSDT", timeframe="1m",
            candles=candles, open_interest={},
            funding_rates={}, ls_ratio={}, taker_volume={},
            collection_start_ms=candles[0].time,
            collection_end_ms=candles[-1].time,
            gaps=[]
        )
        cards = self.artifact.produce(result)
        consumed = self.consumer.consume(cards[0])
        self.assertIn("candle", consumed)
        self.assertIsInstance(consumed["candle"], Candle)
    
    def test_to_candles(self):
        candles = self.fixture.generate("BTCUSDT", 20)
        result = MarketCollectionResult(
            symbol="BTCUSDT", timeframe="1m",
            candles=candles, open_interest={},
            funding_rates={}, ls_ratio={}, taker_volume={},
            collection_start_ms=candles[0].time,
            collection_end_ms=candles[-1].time,
            gaps=[]
        )
        cards = self.artifact.produce(result)
        extracted = self.consumer.to_candles(cards)
        self.assertEqual(len(extracted), 20)
        for i, c in enumerate(extracted):
            self.assertEqual(c.time, candles[i].time)
            self.assertEqual(c.close, candles[i].close)
    
    def test_to_oi_series(self):
        candles = self.fixture.generate("BTCUSDT", 25)
        oi = self.fixture.generate_oi_series(candles)
        result = MarketCollectionResult(
            symbol="BTCUSDT", timeframe="1m",
            candles=candles, open_interest=oi,
            funding_rates={}, ls_ratio={}, taker_volume={},
            collection_start_ms=candles[0].time,
            collection_end_ms=candles[-1].time,
            gaps=[]
        )
        cards = self.artifact.produce(result)
        oi_series = self.consumer.to_oi_series(cards)
        self.assertGreater(len(oi_series), 0)
        # OI slots = 25 candles / 5 = 5 slots
        self.assertEqual(len(oi_series), 5)


class TestMarketImport(unittest.TestCase):
    """Test semua module import."""
    
    def test_import_all(self):
        import stlms.market.fixture
        import stlms.market.artifact
        import stlms.market.package
        import stlms.market.validator
        import stlms.market.consumer
        import stlms.market.collection


if __name__ == "__main__":
    unittest.main(verbosity=2)
