"""
ST-LMS v4 — Living Objects Tests
=================================
Verifies ALL living market objects are truly alive:
entities present, full lifecycle, and entity relationships.
"""
import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from stlms.core.shell import STLMSShell


class TestAllEntitiesAlive(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.shell = STLMSShell(
            db_path=":memory:",
            symbol="BTCUSDT",
            timeframe="1m",
            enable_persistence=False,
        )
        cls.shell.generate(candle_count=200)

    def test_truthpoint_is_alive(self):
        points = self.shell._truth_points
        self.assertGreater(len(points), 0)
        tp = points[-1]
        self.assertIsNotNone(tp.ts)
        self.assertIsNotNone(tp.close)
        self.assertIsNotNone(tp.st)
        self.assertIn(tp.st_dir, (1, -1))
        self.assertIn(tp.st_color, ("HIJAU", "MERAH"))
        self.assertIsNotNone(tp.point_status)
        self.assertIsNotNone(tp.atr)
        self.assertIsNotNone(tp.rsi)
        self.assertIsNotNone(tp.wpr)
        self.assertIsNotNone(tp.ema)
        self.assertIsNotNone(tp.macd_hist)

    def test_line_is_alive(self):
        lines = self.shell._lines
        self.assertGreater(len(lines), 0)
        line = lines[0]
        self.assertIsNotNone(line.st)
        self.assertIsNotNone(line.key)
        self.assertGreater(line.members, 0)
        self.assertIn(line.role, ("SUPPORT", "RESISTANCE"))
        self.assertIn(line.dominant, ("HIJAU", "MERAH"))

    def test_wave_is_alive(self):
        waves = self.shell._waves
        self.assertGreater(len(waves), 0)
        wave = waves[-1]
        self.assertIsNotNone(wave.structure)
        valid_structures = [
            "STRONG_ACCUMULATION", "STRONG_DISTRIBUTION",
            "CONTINUATION_UP", "CONTINUATION_DOWN",
            "CONFIRMED_RANGE", "RANGE_EXPANDING", "RANGE_COMPRESSING",
            "REVERSAL_UP", "REVERSAL_DOWN",
            "EXHAUSTION_UP", "EXHAUSTION_DOWN",
            "SIDEWAY", "CHAOS", "PENDING_WAVE"
        ]
        self.assertIn(wave.structure, valid_structures)
        self.assertGreater(len(wave.lines), 0)

    def test_cage_is_alive(self):
        cage = self.shell._cage
        self.assertIsNotNone(cage)
        self.assertIsNotNone(cage.status)
        valid_statuses = ("NONE", "VALID_COMPRESSION", "LOOSE_SIDEWAY")
        self.assertIn(cage.status, valid_statuses)
        self.assertIsNotNone(cage.pp)

    def test_clone_is_alive(self):
        snapshots = self.shell._snapshots
        self.assertGreater(len(snapshots), 0)
        snap = snapshots[0]
        self.assertIn("close", snap)
        self.assertIn("cage_status", snap)

    def test_bag_is_alive(self):
        artifacts = self.shell._bag_artifacts
        self.assertIsNotNone(artifacts)
        self.assertIsInstance(artifacts, list)
        if len(artifacts) > 0:
            ba = artifacts[0]
            self.assertTrue(hasattr(ba, "bag_id"))
            self.assertTrue(hasattr(ba, "bag_kind"))

    def test_knowledge_is_alive(self):
        knowledge = self.shell._knowledge
        self.assertTrue(bool(knowledge))
        for engine in ["academy", "oracle", "hivemind", "librarian", "darwin"]:
            self.assertIn(engine, knowledge, f"{engine} missing from knowledge")
        self.assertIsInstance(knowledge["academy"], list)
        self.assertIsInstance(knowledge["oracle"], dict)
        self.assertIsInstance(knowledge["hivemind"], dict)
        self.assertIsInstance(knowledge["librarian"], list)
        self.assertIsInstance(knowledge["darwin"], list)

    def test_prediction_is_alive(self):
        pred = self.shell._prediction
        self.assertTrue(bool(pred))
        self.assertIn("dominant_bias", pred)
        self.assertIn("intelligence_score", pred)
        self.assertIn("possibilities", pred)
        self.assertIsInstance(pred["possibilities"], list)

    def test_recommendation_is_alive(self):
        rec = self.shell._recommendation
        self.assertIsNotNone(rec)
        self.assertIsInstance(rec, dict)

    def test_snapshot_is_alive(self):
        snaps = self.shell.snapshots()
        self.assertGreater(snaps.get("total_cards", 0), 0)
        by_type = snaps.get("by_type", {})
        self.assertGreater(len(by_type), 0)

    def test_memory_is_alive(self):
        mem_stats = self.shell._memory.stats()
        self.assertGreater(mem_stats["current_size"], 0)
        self.assertGreater(mem_stats["total_observations"], 0)
        self.assertGreaterEqual(mem_stats["live_count"], 0)

    def test_dna_is_alive(self):
        dna = self.shell.market_dna()
        self.assertTrue(dna.get("available"))
        self.assertGreater(len(dna), 2)

    def test_market_events_alive(self):
        knowledge = self.shell._knowledge
        self.assertIn("market_events", knowledge)
        self.assertIsInstance(knowledge["market_events"], list)


class TestEntityLifecycleComplete(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.shell = STLMSShell(
            db_path=":memory:",
            symbol="BTCUSDT",
            timeframe="1m",
            enable_persistence=False,
        )
        cls.shell.generate(candle_count=200)

    def test_truthpoint_has_full_lifecycle(self):
        points = self.shell._truth_points
        self.assertGreater(len(points), 0)
        tp = points[-1]
        self.assertIsNotNone(tp.ts)
        self.assertIsNotNone(tp.point_status)
        self.assertIsNotNone(tp.close)
        obs = self.shell.get_observation(len(points) - 1)
        self.assertTrue(obs.get("available") is not False)
        self.assertIn("version", obs)
        self.assertIn("mutation_count", obs)

    def test_line_has_full_lifecycle(self):
        lines = self.shell._lines
        self.assertGreater(len(lines), 0)
        line = lines[0]
        self.assertIsNotNone(line.st)
        self.assertIsNotNone(line.key)
        self.assertIsNotNone(line.role)
        self.assertGreater(line.members, 0)
        for line2 in lines:
            if hasattr(line2, 'lifecycle_state'):
                self.assertIn(line2.lifecycle_state,
                              ("NEW", "LIVE", "FREEZE", "ARCHIVE", "OPEN", "CLOSED"))

    def test_wave_has_full_lifecycle(self):
        waves = self.shell._waves
        self.assertGreater(len(waves), 0)
        wave = waves[-1]
        self.assertIsNotNone(wave.structure)
        self.assertGreater(len(wave.lines), 0)

    def test_memory_has_full_lifecycle(self):
        mem_stats = self.shell._memory.stats()
        self.assertGreater(mem_stats["total_observations"], 0)
        self.assertGreater(mem_stats["current_size"], 0)
        self.assertIsNotNone(self.shell._memory.current_batch)
        self.assertEqual(self.shell._memory.current_batch.lifecycle_state, "LIVE")


class TestEntityRelationships(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.shell = STLMSShell(
            db_path=":memory:",
            symbol="BTCUSDT",
            timeframe="1m",
            enable_persistence=False,
        )
        cls.shell.generate(candle_count=200)

    def test_candle_produces_truthpoint(self):
        self.assertGreater(len(self.shell._truth_points), 0)
        self.assertEqual(len(self.shell._truth_points), 200)

    def test_truthpoints_produce_lines(self):
        self.assertGreater(len(self.shell._lines), 0)
        self.assertGreater(len(self.shell._truth_points), 0)

    def test_lines_produce_waves(self):
        self.assertGreater(len(self.shell._waves), 0)
        self.assertGreater(len(self.shell._lines), 0)

    def test_lines_produce_cage(self):
        self.assertIsNotNone(self.shell._cage)
        self.assertGreater(len(self.shell._lines), 0)

    def test_waves_produce_mtf(self):
        waves = self.shell._waves
        self.assertGreater(len(waves), 0)
        from stlms.core.constants import WAVE_MTF_TABLE
        wave = waves[-1]
        if wave.structure in WAVE_MTF_TABLE:
            mtf_label, mtf_score = WAVE_MTF_TABLE[wave.structure]
            self.assertIsNotNone(mtf_label)
            self.assertGreater(mtf_score, 0)

    def test_markers_produce_bag(self):
        self.assertIsNotNone(self.shell._bag_artifacts)
        self.assertIsInstance(self.shell._bag_artifacts, list)

    def test_bag_produces_knowledge(self):
        knowledge = self.shell._knowledge
        self.assertTrue(bool(knowledge))
        self.assertIn("academy", knowledge)

    def test_knowledge_produces_prediction(self):
        pred = self.shell._prediction
        self.assertTrue(bool(pred))
        self.assertIn("dominant_bias", pred)
        self.assertIn("possibilities", pred)
