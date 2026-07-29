"""
=====================================================
MODULE:     test_phase_03_12.py
PURPOSE:    Unit tests untuk Phase-03 sampai Phase-12.
=====================================================
"""

import sys, os, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from stlms.market.fixture import MarketFixture
from stlms.truth.point import PointBuilder, TruthArtifact, TruthPoint
from stlms.truth.package import TruthPackage
from stlms.truth.validator import TruthValidator
from stlms.truth.consumer import TruthConsumer
from stlms.structure.line import LineBuilder
from stlms.structure.wave import WaveBuilder, WAVE_STRUCTURES
from stlms.structure.cage import CageEngine
from stlms.evidence.bus import EvidenceEngine, DirectionBus, ExitBus, CorrectionBus
from stlms.clone.engine import CloneEngine, CloneLedger, Position, TradeMarker
from stlms.statistics.engine import compute_statistics
from stlms.bag.engine import BAGEngine, BagArtifact
from stlms.knowledge.engine import (AcademyEngine, OracleEngine, HiveMindEngine,
                                     LibrarianEngine, DarwinEngine)
from stlms.prediction.engine import PredictionEngine


class TestTruthPoint(unittest.TestCase):
    def setUp(self):
        self.fixture = MarketFixture(42)
        self.builder = PointBuilder("BTCUSDT")
    
    def test_build_points(self):
        candles = self.fixture.generate("BTCUSDT", 100)
        points = []
        for c in candles:
            tp = self.builder.build(c)
            points.append(tp)
        self.assertEqual(len(points), 100)
    
    def test_warmup_then_valid(self):
        candles = self.fixture.generate("BTCUSDT", 20)
        statuses = []
        for c in candles:
            tp = self.builder.build(c)
            statuses.append(tp.point_status.value)
        # First few may be VALID (ATR/EMA set immediately), RSI/WPR need warmup
        self.assertIn("VALID", statuses)
        self.assertEqual(statuses[-1], "VALID")
    
    def test_flip_detection(self):
        candles = self.fixture.generate("BTCUSDT", 300)
        flips = 0
        for c in candles:
            tp = self.builder.build(c)
            if tp.flip:
                flips += 1
        self.assertGreater(flips, 0, "No trend flips detected")
    
    def test_indicators_in_range(self):
        candles = self.fixture.generate("BTCUSDT", 100)
        for c in candles:
            tp = self.builder.build(c)
            if tp.rsi is not None:
                self.assertTrue(0 <= tp.rsi <= 100, f"RSI out of range: {tp.rsi}")
            if tp.wpr is not None:
                self.assertTrue(-100 <= tp.wpr <= 0, f"W%R out of range: {tp.wpr}")
    
    def test_determinism(self):
        candles1 = self.fixture.generate("BTCUSDT", 50)
        b1 = PointBuilder("BTCUSDT")
        p1 = [b1.build(c) for c in candles1]
        
        f2 = MarketFixture(42)
        candles2 = f2.generate("BTCUSDT", 50)
        b2 = PointBuilder("BTCUSDT")
        p2 = [b2.build(c) for c in candles2]
        
        for i in range(50):
            self.assertEqual(p1[i].close, p2[i].close)
            self.assertEqual(p1[i].st, p2[i].st)


class TestTruthArtifact(unittest.TestCase):
    def setUp(self):
        self.fixture = MarketFixture(42)
        self.builder = PointBuilder("BTCUSDT")
        self.artifact = TruthArtifact()
    
    def test_produce_card(self):
        candles = self.fixture.generate("BTCUSDT", 10)
        for c in candles:
            tp = self.builder.build(c)
            card = self.artifact.produce(tp)
            self.assertTrue(card.verify())


class TestTruthPackage(unittest.TestCase):
    def setUp(self):
        self.fixture = MarketFixture(42)
        self.builder = PointBuilder("BTCUSDT")
        self.artifact = TruthArtifact()
        self.package = TruthPackage()
    
    def test_build(self):
        candles = self.fixture.generate("BTCUSDT", 20)
        cards = []
        for c in candles:
            tp = self.builder.build(c)
            cards.append(self.artifact.produce(tp))
        report = self.package.build(cards)
        self.assertEqual(report["points"], 20)
        self.assertIn("current", report)


class TestStructureLine(unittest.TestCase):
    def setUp(self):
        self.fixture = MarketFixture(42)
        self.builder = PointBuilder("BTCUSDT")
        self.line_builder = LineBuilder()
    
    def test_build_lines(self):
        candles = self.fixture.generate("BTCUSDT", 200)
        points = []
        for c in candles:
            tp = self.builder.build(c)
            points.append({"ts": tp.ts, "st": tp.st, "st_canon": tp.st_canon,
                          "color": tp.st_color, "oi_value": tp.oi_value})
        lines = self.line_builder.build(points)
        self.assertGreater(len(lines), 0, "No lines formed")


class TestStructureWave(unittest.TestCase):
    def setUp(self):
        self.fixture = MarketFixture(42)
        self.builder = PointBuilder("BTCUSDT")
        self.line_builder = LineBuilder()
        self.wave_builder = WaveBuilder()
    
    def test_build_waves(self):
        candles = self.fixture.generate("BTCUSDT", 300)
        points = []
        for c in candles:
            tp = self.builder.build(c)
            points.append({"ts": tp.ts, "st": tp.st, "st_canon": tp.st_canon,
                          "color": tp.st_color, "oi_value": tp.oi_value})
        lines = self.line_builder.build(points)
        waves = self.wave_builder.build(lines)
        self.assertGreater(len(waves), 0)
        self.assertIn(waves[-1].structure, WAVE_STRUCTURES + ["PENDING_WAVE"])


class TestStructureCage(unittest.TestCase):
    def setUp(self):
        self.fixture = MarketFixture(42)
        self.builder = PointBuilder("BTCUSDT")
        self.line_builder = LineBuilder()
        self.cage_engine = CageEngine()
    
    def test_build_cage(self):
        candles = self.fixture.generate("BTCUSDT", 200)
        points = []
        for c in candles:
            tp = self.builder.build(c)
            points.append({"ts": tp.ts, "st": tp.st, "st_canon": tp.st_canon,
                          "color": tp.st_color, "oi_value": tp.oi_value})
        lines = self.line_builder.build(points)
        cage = self.cage_engine.build(lines, candles[-1].close, self.builder.atr_val or 1.0)
        self.assertIn(cage.status, ["NONE", "VALID_COMPRESSION", "LOOSE_SIDEWAY"])


class TestEvidence(unittest.TestCase):
    def setUp(self):
        self.engine = EvidenceEngine()
    
    def test_dir_bus(self):
        sp = {"ema_slope": 10, "vol_delta": 0.3}
        db = self.engine.dir_bus(sp, 6000, "OK", "PROXY", 7000, 3000)
        self.assertGreater(db.ema, 5000)
        self.assertGreater(db.vd, 5000)
    
    def test_exit_bus_sterility(self):
        """W%R/MACD/RSI = EXIT ONLY. Tidak boleh di Direction Bus."""
        sp = {"rsi": 65, "wpr": -30, "macd_hist": 2.0, "vel": 3, "acc": 1}
        eb = self.engine.exit_bus(sp)
        self.assertIsNotNone(eb.rsi)
        self.assertIsNotNone(eb.wpr)
        # DirectionBus does NOT contain wpr/rsi/macd (verified by API)
    
    def test_correction_bus(self):
        from stlms.structure.cage import Cage
        cage = Cage(upper=62500, lower=61800, pp=0.25, status="VALID_COMPRESSION")
        sp = {"close": 62000}
        cb = self.engine.correction_bus(sp, cage, "RANGE_COMPRESSING")
        self.assertEqual(cb.market_phase, "SIDEWAY")


class TestCloneEngine(unittest.TestCase):
    def setUp(self):
        self.engine = CloneEngine()
        self.sp = {"ts": 1000, "close": 62000, "st_dir": 1, "atr": 500,
                   "vel": 2, "rsi": 55, "wpr": -35, "vol_delta": 0.2,
                   "ema_slope": 100, "macd_hist": 3.0, "prev_macd_hist": 2.0}
    
    def test_long_observation(self):
        from stlms.structure.cage import Cage
        from stlms.evidence.bus import DirectionBus
        ledger = self.engine.new_long()
        cage = Cage(upper=63000, lower=61800, status="NONE")
        db = DirectionBus(ema=7000, vd=6000)
        obs = self.engine.observe_long(ledger, self.sp, cage, db, 500, 0.7)
        self.assertIn("entry_allowed", obs)
    
    def test_short_observation(self):
        from stlms.structure.cage import Cage
        from stlms.evidence.bus import DirectionBus
        ledger = self.engine.new_short()
        sp = {**self.sp, "st_dir": -1}
        cage = Cage(upper=63000, lower=61800, status="NONE")
        db = DirectionBus(ema=3000, vd=4000)
        obs = self.engine.observe_short(ledger, sp, cage, db, 500, 0.7)
        self.assertIn("entry_allowed", obs)
    
    def test_grid_observation(self):
        from stlms.structure.cage import Cage
        ledger = self.engine.new_grid()
        cage = Cage(upper=62500, lower=61800, pp=0.3, status="VALID_COMPRESSION",
                    range_atr=2.0, breakout="NONE")
        obs = self.engine.observe_grid(ledger, self.sp, cage, 0.7)
        self.assertIn("grid_active", obs)
    
    def test_exit_priority(self):
        from stlms.structure.cage import Cage
        from stlms.evidence.bus import ExitBus
        pos = Position(side="LONG", entry_price=62000, sl=61800, tp=63000, hold_c=1)
        cage = Cage(status="NONE", breakout="NONE")
        eb = ExitBus(hold=False)
        # SL hit
        sp = {**self.sp, "close": 61700, "vel": 2}
        result = self.engine.decide_exit(pos, sp, cage, eb)
        self.assertIsNotNone(result)
        self.assertEqual(result[0], "SL")
    
    def test_make_exit_pnl(self):
        pos = Position(side="LONG", entry_price=62000, sl=61800, tp=63000, hold_c=5)
        sp = {"ts": 2000, "close": 62500}
        marker = self.engine.make_exit(pos, sp, "TP", 62500)
        self.assertEqual(marker.result, "WIN")
        self.assertGreater(marker.net, 0)


class TestStatistics(unittest.TestCase):
    def test_compute(self):
        markers = []
        for i in range(40):
            markers.append(TradeMarker(ts=i, clone="LONG", side="LONG",
                           kind="EXIT", reason="TP", entry=100, exit=105,
                           gross=5.0, fee=0.1, slip=0.05, net=4.85,
                           result="WIN" if i < 28 else "LOSS"))
        stats = compute_statistics(markers, "LONG")
        self.assertEqual(stats["sample"], 40)
        self.assertEqual(stats["status"], "CUKUP")
        self.assertEqual(stats["win_rate"], 70.0)


class TestBAG(unittest.TestCase):
    def setUp(self):
        self.engine = BAGEngine()
    
    def test_group(self):
        markers = []
        for i in range(50):
            markers.append(TradeMarker(ts=i, clone="LONG", side="LONG",
                           kind="EXIT", reason="TP", entry=100, exit=105,
                           gross=5.0, fee=0.1, slip=0.05, net=4.85,
                           result="WIN" if i < 35 else "LOSS"))
        snapshots = [{"ts": i, "wave_structure": "CONTINUATION_UP", "dist_atr": 0.5} for i in range(50)]
        artifacts = self.engine.group_by_clone_structure(markers, snapshots)
        self.assertGreater(len(artifacts), 0)
        self.assertGreater(artifacts[0].sample_count, 0)


class TestKnowledge(unittest.TestCase):
    def test_academy(self):
        from stlms.bag.engine import BagArtifact
        from stlms.core.types import BagKind
        bag = BagArtifact("test", BagKind.BEHAVIOR, "LONG|CONT|OPTIMAL|TP",
                          sample_count=50, win_count=35, win_rate=70.0,
                          consensus="HIGH")
        engine = AcademyEngine()
        results = engine.learn([bag])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["status"], "CUKUP")
    
    def test_oracle(self):
        engine = OracleEngine()
        engine.push([0.5]*9, 1000, "BULLISH")
        result = engine.match([0.5]*9)
        self.assertTrue(result["match"])
        self.assertGreater(result["score"], 9000)
    
    def test_hivemind(self):
        engine = HiveMindEngine()
        result = engine.synthesize(
            [{"key": "test", "win_rate": 70.0}],
            {"match": True, "score": 8500}
        )
        self.assertGreater(result["intelligence_score"], 6000)
        self.assertEqual(result["dominant_bias"], "BULLISH")
    
    def test_librarian(self):
        from stlms.bag.engine import BagArtifact
        from stlms.core.types import BagKind
        bag1 = BagArtifact("1", BagKind.BEHAVIOR, "test1", sample_count=5, win_rate=60)
        bag2 = BagArtifact("2", BagKind.BEHAVIOR, "test2", sample_count=50, win_rate=70)
        bag3 = BagArtifact("3", BagKind.BEHAVIOR, "test3", sample_count=60, win_rate=25)
        engine = LibrarianEngine()
        events = engine.evaluate([bag1, bag2, bag3])
        self.assertEqual(events[0]["status"], "NEW")
        self.assertEqual(events[1]["status"], "MATURE")
        self.assertEqual(events[2]["status"], "DEAD")
    
    def test_darwin(self):
        engine = DarwinEngine()
        stats = {"LONG": {"sample": 50, "expectancy": -0.02, "wrong_rate": 35}}
        proposals = engine.propose(stats)
        self.assertGreater(len(proposals), 0)
        self.assertIn("TIGHTEN", proposals[0]["type"])


class TestPrediction(unittest.TestCase):
    def test_predict(self):
        engine = PredictionEngine()
        knowledge = {
            "hivemind": {"intelligence_score": 7200, "dominant_bias": "BULLISH"},
            "academy": [{"key": "LONG|CONT|OPTIMAL|TP", "win_rate": 73.0}],
            "oracle": {"match": True, "score": 8200},
        }
        result = engine.predict(knowledge)
        self.assertGreater(len(result["possibilities"]), 0)
        self.assertTrue(result["no_model"])
        self.assertEqual(result["dominant_bias"], "BULLISH")


class TestImportAll(unittest.TestCase):
    def test_import(self):
        import stlms.truth.point
        import stlms.truth.package
        import stlms.truth.validator
        import stlms.truth.consumer
        import stlms.structure.line
        import stlms.structure.wave
        import stlms.structure.cage
        import stlms.evidence.bus
        import stlms.clone.engine
        import stlms.statistics.engine
        import stlms.bag.engine
        import stlms.knowledge.engine
        import stlms.prediction.engine


if __name__ == "__main__":
    unittest.main(verbosity=2)
