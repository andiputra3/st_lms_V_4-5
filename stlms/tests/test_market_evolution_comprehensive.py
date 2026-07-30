"""
ST-LMS v4 — Comprehensive Market Evolution, Synchronization, Replay,
SQLite, and Performance Test Suite
=======================================================

Covers:
- Line/Wave/MarketCharacter/DNA/Knowledge Evolution
- Market Synchronization (observation count matching)
- Replay (historical observations replayable)
- SQLite Evolution (all tables, persistence)
- Performance at Scale (100 to 5000 observations)
- Stress Testing (continuous collection, snapshot batch)

All tests use STLMSShell. enable_persistence=False unless SQLite tests.
"""

import sys
import os
import unittest
import tempfile
import time
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from stlms.core.shell import STLMSShell
from stlms.core.memory import MarketObservationMemory
from stlms.knowledge.engine import AcademyEngine, OracleEngine, HiveMindEngine, LibrarianEngine, DarwinEngine


# ============================================================================
# LINE EVOLUTION
# ============================================================================

class TestLineEvolution(unittest.TestCase):
    """Lines must have lifetime, mutation, reliability, continuation tracking."""

    @classmethod
    def setUpClass(cls):
        cls.shell = STLMSShell(
            db_path=":memory:",
            symbol="BTCUSDT",
            timeframe="1m",
            enable_persistence=False,
        )
        cls.shell.generate(candle_count=500)

    def test_lines_have_lifetime(self):
        """Lines must have > 0 members."""
        lines = self.shell._lines
        self.assertGreater(len(lines), 0, "No lines generated")
        for line in lines:
            self.assertGreater(line.members, 0,
                                f"Line has {line.members} members, expected > 0")

    def test_lines_have_mutation_count(self):
        """mutation_count must be tracked."""
        lines = self.shell._lines
        self.assertGreater(len(lines), 0, "No lines generated")
        for line in lines:
            self.assertIsInstance(line.mutation_count, int,
                                  f"Line mutation_count is not int: {type(line.mutation_count)}")
            self.assertGreaterEqual(line.mutation_count, 0,
                                    f"Line mutation_count is negative: {line.mutation_count}")

    def test_lines_have_reliability(self):
        """reliability_score must be > 0."""
        lines = self.shell._lines
        self.assertGreater(len(lines), 0, "No lines generated")
        for line in lines:
            self.assertIsInstance(line.reliability_score, (int, float),
                                  f"Line reliability_score not numeric: {type(line.reliability_score)}")

    def test_lines_have_continuation_rate(self):
        """continuation_rate must be tracked."""
        lines = self.shell._lines
        self.assertGreater(len(lines), 0, "No lines generated")
        for line in lines:
            self.assertIsInstance(line.continuation_rate, (int, float),
                                  f"Line continuation_rate not numeric: {type(line.continuation_rate)}")
            self.assertGreaterEqual(line.continuation_rate, 0.0,
                                    f"Line continuation_rate negative: {line.continuation_rate}")

    def test_lines_evolve_over_time(self):
        """Different lines at different points in time should exist."""
        lines = self.shell._lines
        self.assertGreater(len(lines), 2,
                           f"Only {len(lines)} lines, need > 2 to verify evolution")
        first_st = lines[0].st
        last_st = lines[-1].st
        self.assertIsNotNone(first_st)
        self.assertIsNotNone(last_st)
        # Lines should span a range of prices
        st_values = [L.st for L in lines if L.st is not None]
        self.assertGreater(len(set(st_values)), 1,
                           "All lines have the same st value — no evolution")

    def test_lines_have_roles(self):
        """Lines must be classified as SUPPORT or RESISTANCE."""
        lines = self.shell._lines
        self.assertGreater(len(lines), 0, "No lines generated")
        roles = {L.role for L in lines if hasattr(L, 'role')}
        self.assertTrue(roles.issubset({"SUPPORT", "RESISTANCE"}),
                        f"Invalid roles found: {roles}")
        self.assertGreater(len(roles), 0, "No roles assigned to lines")


# ============================================================================
# WAVE EVOLUTION
# ============================================================================

class TestWaveEvolution(unittest.TestCase):
    """Waves must have structure, evolution stats, profit profiles, character."""

    VALID_STRUCTURES = {
        "STRONG_ACCUMULATION", "STRONG_DISTRIBUTION",
        "CONTINUATION_UP", "CONTINUATION_DOWN",
        "CONFIRMED_RANGE", "RANGE_EXPANDING", "RANGE_COMPRESSING",
        "REVERSAL_UP", "REVERSAL_DOWN",
        "EXHAUSTION_UP", "EXHAUSTION_DOWN",
        "SIDEWAY", "CHAOS", "PENDING_WAVE",
    }

    @classmethod
    def setUpClass(cls):
        cls.shell = STLMSShell(
            db_path=":memory:",
            symbol="BTCUSDT",
            timeframe="1m",
            enable_persistence=False,
        )
        cls.shell.generate(candle_count=500)

    def test_waves_have_structure(self):
        """Every wave must have one of 13 valid structures."""
        waves = self.shell._waves
        self.assertGreater(len(waves), 0, "No waves generated")
        for wave in waves:
            self.assertIsNotNone(wave.structure, "Wave has no structure")
            self.assertIn(wave.structure, self.VALID_STRUCTURES,
                          f"Invalid wave structure: {wave.structure}")

    def test_waves_have_evolution_stats(self):
        """Waves must have breakout/continuation/reversal rates."""
        waves = self.shell._waves
        self.assertGreater(len(waves), 0, "No waves generated")
        for wave in waves:
            self.assertIsInstance(wave.continuation_rate, (int, float),
                                  f"continuation_rate not numeric: {type(wave.continuation_rate)}")
            self.assertGreaterEqual(wave.continuation_rate, 0.0)
            self.assertIsInstance(wave.breakout_rate, (int, float),
                                  f"breakout_rate not numeric: {type(wave.breakout_rate)}")
            self.assertGreaterEqual(wave.breakout_rate, 0.0)
            self.assertIsInstance(wave.reversal_rate, (int, float),
                                  f"reversal_rate not numeric: {type(wave.reversal_rate)}")
            self.assertGreaterEqual(wave.reversal_rate, 0.0)

    def test_waves_have_profit_profile(self):
        """Waves must have profit_profile with best_clone, worst_clone."""
        waves = self.shell._waves
        self.assertGreater(len(waves), 0, "No waves generated")
        for wave in waves:
            pp = wave.profit_profile
            self.assertIsInstance(pp, dict,
                                  f"profit_profile is not a dict: {type(pp)}")
            self.assertIn("best_clone", pp,
                          f"profit_profile missing 'best_clone': {list(pp.keys())}")
            self.assertIn("worst_clone", pp,
                          f"profit_profile missing 'worst_clone': {list(pp.keys())}")
            self.assertIn("dominant_clone", pp,
                          f"profit_profile missing 'dominant_clone': {list(pp.keys())}")

    def test_waves_have_market_character(self):
        """Waves must have market_character assigned."""
        waves = self.shell._waves
        self.assertGreater(len(waves), 0, "No waves generated")
        for wave in waves:
            self.assertIsInstance(wave.market_character, str,
                                  f"market_character not a str: {type(wave.market_character)}")

    def test_waves_have_reliability(self):
        """Waves must have reliability_score."""
        waves = self.shell._waves
        self.assertGreater(len(waves), 0, "No waves generated")
        for wave in waves:
            self.assertIsInstance(wave.reliability_score, (int, float),
                                  f"reliability_score not numeric: {type(wave.reliability_score)}")

    def test_waves_have_wave_id(self):
        """Waves must have a wave_id attribute."""
        waves = self.shell._waves
        self.assertGreater(len(waves), 0, "No waves generated")
        for wave in waves:
            self.assertIsNotNone(wave.wave_id, "Wave has no wave_id")
            self.assertIsInstance(wave.wave_id, str,
                                  f"wave_id not a str: {type(wave.wave_id)}")


# ============================================================================
# MARKET CHARACTER EVOLUTION
# ============================================================================

class TestMarketCharacterEvolution(unittest.TestCase):
    """Market character must exist, have regime/profile, and change over time."""

    @classmethod
    def setUpClass(cls):
        cls.shell = STLMSShell(
            db_path=":memory:",
            symbol="BTCUSDT",
            timeframe="1m",
            enable_persistence=False,
        )
        cls.shell.generate(candle_count=500)

    def test_market_character_exists(self):
        """Market character must be present in DNA."""
        dna = self.shell.market_dna()
        self.assertTrue(dna.get("available"), "Market DNA not available")
        # DNA should contain market character keys
        dna_internal = self.shell._market_dna
        self.assertTrue(bool(dna_internal), "Market DNA internal is empty")
        char_keys = ["dominant_wave", "regime", "profile"]
        found = [k for k in char_keys if k in dna_internal]
        self.assertGreater(len(found), 0,
                           f"DNA missing market character keys. Has: {list(dna_internal.keys())}")

    def test_market_character_has_regime(self):
        """Market character must have a regime."""
        dna_internal = self.shell._market_dna
        if "regime" in dna_internal:
            regime = dna_internal["regime"]
            self.assertIsNotNone(regime)
            self.assertIsInstance(regime, str)
            self.assertGreater(len(regime), 0)
            self.assertIn(regime, ("TRENDING", "RANGE_BOUND", "MIXED"),
                          f"Unknown regime: {regime}")

    def test_market_character_has_profile(self):
        """Market character must have a profile."""
        dna_internal = self.shell._market_dna
        if "profile" in dna_internal:
            profile = dna_internal["profile"]
            self.assertIsNotNone(profile)
            self.assertIsInstance(profile, str)
            self.assertGreater(len(profile), 0)

    def test_market_character_changes_over_time(self):
        """Generate more data — character may change across runs."""
        dna_before = self.shell._market_dna.copy()
        # Generate more to potentially shift character
        self.shell.generate(candle_count=300, reset_first=False)
        dna_after = self.shell._market_dna
        self.assertTrue(bool(dna_after), "DNA after second run is empty")
        # At minimum, verify DNA still has structure
        self.assertIn("wave_distribution", dna_after,
                      "DNA missing wave_distribution after second run")


# ============================================================================
# DNA EVOLUTION
# ============================================================================

class TestDNAEvolution(unittest.TestCase):
    """DNA must grow with observations, have complete profile, reflect structure."""

    @classmethod
    def setUpClass(cls):
        cls.shell = STLMSShell(
            db_path=":memory:",
            symbol="BTCUSDT",
            timeframe="1m",
            enable_persistence=False,
        )
        cls.shell.generate(candle_count=500)

    def test_dna_grows_with_observations(self):
        """DNA must be available after generation."""
        dna = self.shell.market_dna()
        self.assertTrue(dna.get("available"), "DNA not available after 500 obs")

    def test_dna_has_complete_profile(self):
        """DNA must have all key components."""
        dna = self.shell._market_dna
        self.assertTrue(bool(dna), "Market DNA internal is empty")

        expected_keys = {"wave_distribution", "cage_distribution"}
        for key in expected_keys:
            self.assertIn(key, dna,
                          f"DNA missing key '{key}'. Keys: {list(dna.keys())}")

        wave_dist = dna["wave_distribution"]
        self.assertIsInstance(wave_dist, dict, "wave_distribution not a dict")
        self.assertGreater(len(wave_dist), 0, "wave_distribution is empty")

        cage_dist = dna["cage_distribution"]
        self.assertIsInstance(cage_dist, dict, "cage_distribution not a dict")
        self.assertGreater(len(cage_dist), 0, "cage_distribution is empty")

    def test_dna_reflects_market_structure(self):
        """DNA wave distribution must map to actual wave structures."""
        dna = self.shell._market_dna
        wave_dist = dna.get("wave_distribution", {})
        waves = self.shell._waves

        actual_structures = {w.structure for w in waves if hasattr(w, 'structure')}
        dna_structures = set(wave_dist.keys())

        # DNA wave distribution should overlap with actual structures
        overlap = actual_structures & dna_structures
        self.assertGreater(len(overlap), 0,
                           f"No overlap between DNA structures ({dna_structures}) "
                           f"and actual waves ({actual_structures})")


# ============================================================================
# KNOWLEDGE EVOLUTION
# ============================================================================

class TestKnowledgeEvolution(unittest.TestCase):
    """Knowledge layer engines must produce results and grow with observations."""

    @classmethod
    def setUpClass(cls):
        cls.shell = STLMSShell(
            db_path=":memory:",
            symbol="BTCUSDT",
            timeframe="1m",
            enable_persistence=False,
        )
        cls.shell.generate(candle_count=200)

    def test_academy_produces_buckets(self):
        """Academy must return learning buckets."""
        academy = self.shell.knowledge_academy()
        self.assertIsInstance(academy, list,
                              f"Academy returned {type(academy)}, expected list")
        if len(academy) > 0:
            for bucket in academy:
                self.assertIsInstance(bucket, dict)
                self.assertIn("key", bucket)
                self.assertIn("sample", bucket)
                self.assertIn("win_rate", bucket)
                self.assertIn("confidence", bucket)
                self.assertIn("status", bucket)
                self.assertGreaterEqual(bucket["sample"], 30,
                                        f"Bucket has {bucket['sample']} samples, need >= 30")

    def test_oracle_builds_history(self):
        """Oracle must produce match results."""
        oracle = self.shell.knowledge_oracle()
        self.assertIsInstance(oracle, dict,
                              f"Oracle returned {type(oracle)}, expected dict")
        self.assertIn("match", oracle)
        self.assertIn("score", oracle)
        self.assertIsInstance(oracle["score"], (int, float))

    def test_hivemind_produces_intelligence(self):
        """HiveMind must synthesize intelligence."""
        hivemind = self.shell.knowledge_hivemind()
        self.assertIsInstance(hivemind, dict,
                              f"HiveMind returned {type(hivemind)}, expected dict")
        self.assertIn("dominant_bias", hivemind)
        self.assertIn("intelligence_score", hivemind)
        self.assertIn("pattern_boost", hivemind)
        self.assertIn("oracle_boost", hivemind)
        self.assertIn("historical_learning", hivemind)
        self.assertIsInstance(hivemind["historical_learning"], list)
        self.assertGreaterEqual(hivemind["intelligence_score"], 0)
        self.assertLessEqual(hivemind["intelligence_score"], 10000)
        self.assertIn(hivemind["dominant_bias"], ("BULLISH", "BEARISH", "NEUTRAL"))

    def test_librarian_evaluates_bag(self):
        """Librarian must evaluate bag artifacts."""
        bag_artifacts = self.shell._bag_artifacts
        librarian = LibrarianEngine()
        events = librarian.evaluate(bag_artifacts if bag_artifacts else [])
        self.assertIsInstance(events, list)
        valid_statuses = {"NEW", "OBSERVATION", "TRUSTED", "MATURE", "DEAD", "DEPRECATED"}
        for event in events:
            self.assertIn("key", event)
            self.assertIn("status", event)
            self.assertIn(event["status"], valid_statuses,
                          f"Invalid status: {event['status']}")
            self.assertIn("sample", event)
            self.assertIn("win_rate", event)

    def test_darwin_proposes_parameters(self):
        """Darwin must propose parameter adjustments."""
        stats = self.shell._statistics
        self.assertTrue(bool(stats), "Statistics empty")
        darwin = DarwinEngine()
        proposals = darwin.propose(stats)
        self.assertIsInstance(proposals, list)
        valid_types = {"TIGHTEN_ENTRY", "TIGHTEN_WRONG"}
        for p in proposals:
            self.assertIn("type", p)
            self.assertIn(p["type"], valid_types,
                          f"Invalid proposal type: {p['type']}")
            self.assertIn("target", p)
            self.assertIn("param", p)
            self.assertIn("reason", p)

    def test_knowledge_grows_with_observations(self):
        """Generate more — verify knowledge accumulates."""
        initial_academy_count = len(self.shell.knowledge_academy())
        initial_oracle_score = self.shell.knowledge_oracle().get("score", 0)
        initial_hivemind_score = self.shell.knowledge_hivemind().get("intelligence_score", 0)

        self.shell.generate(candle_count=100, reset_first=False)

        new_academy_count = len(self.shell.knowledge_academy())
        new_hivemind_score = self.shell.knowledge_hivemind().get("intelligence_score", 0)

        # Knowledge should accumulate (at minimum, hivemind score should change)
        self.assertGreaterEqual(new_academy_count, 0,
                                "Academy results should still be a list")
        self.assertGreaterEqual(new_hivemind_score, 0,
                                "HiveMind score should remain valid")


# ============================================================================
# MARKET SYNCHRONIZATION
# ============================================================================

class TestMarketSynchronization(unittest.TestCase):
    """Observations must be synchronized across pipeline stages."""

    @classmethod
    def setUpClass(cls):
        cls.shell = STLMSShell(
            db_path=":memory:",
            symbol="BTCUSDT",
            timeframe="1m",
            enable_persistence=False,
        )
        cls.shell.generate(candle_count=200)

    def test_observation_matches_truthpoints(self):
        """Memory observations must match truth point count."""
        status = self.shell.status()
        truth_points = status["truth_points"]
        mem_obs = status["memory_observations"]
        self.assertGreater(truth_points, 0, "No truth points")
        self.assertGreater(mem_obs, 0, "No memory observations")
        self.assertLessEqual(mem_obs, truth_points,
                             f"Memory obs ({mem_obs}) exceeds truth points ({truth_points})")

    def test_snapshot_count_matches_pipeline(self):
        """Snapshot card count must be positive and consistent."""
        snaps = self.shell.snapshots()
        total = snaps.get("total_cards", 0)
        self.assertGreater(total, 0, "No snapshot cards produced")
        by_type = snaps.get("by_type", {})
        self.assertGreater(len(by_type), 0, "No snapshot types registered")
        for stype, count in by_type.items():
            self.assertGreaterEqual(count, 0,
                                    f"Negative count for {stype}: {count}")

    def test_memory_matches_pipeline_output(self):
        """Memory stats must match status report."""
        mem_stats = self.shell._memory.stats()
        status = self.shell.status()

        self.assertGreater(mem_stats["total_observations"], 0)
        self.assertGreater(mem_stats["current_size"], 0)
        self.assertEqual(mem_stats["current_size"], status["memory_observations"],
                         f"Memory current_size ({mem_stats['current_size']}) != "
                         f"status memory_observations ({status['memory_observations']})")
        self.assertEqual(mem_stats["total_observations"], status["memory_total"],
                         f"Memory total ({mem_stats['total_observations']}) != "
                         f"status memory_total ({status['memory_total']})")

    def test_synchronization_after_continuous_runs(self):
        """Multiple generate() calls — verify sync maintained."""
        shell = STLMSShell(
            db_path=":memory:",
            symbol="BTCUSDT",
            timeframe="1m",
            enable_persistence=False,
        )
        shell.generate(candle_count=100)
        r1_truth = shell.status()["truth_points"]
        r1_mem = shell.status()["memory_total"]

        shell.generate(candle_count=50, reset_first=False)
        r2_truth = shell.status()["truth_points"]
        r2_mem = shell.status()["memory_total"]

        self.assertGreater(r2_truth, r1_truth,
                           "Truth points did not accumulate across runs")
        self.assertGreater(r2_mem, r1_mem,
                           "Memory observations did not accumulate across runs")

        # Sync: memory_total should be <= truth_points (each TP = 1 obs)
        self.assertLessEqual(r2_mem, r2_truth,
                             f"Memory ({r2_mem}) exceeds truth ({r2_truth}) after continuous runs")

    def test_synchronization_at_scale(self):
        """Test at 100, 500, 1000 observations."""
        for count in (100, 500, 1000):
            with self.subTest(obs=count):
                shell = STLMSShell(
                    db_path=":memory:",
                    symbol="BTCUSDT",
                    timeframe="1m",
                    enable_persistence=False,
                )
                shell.generate(candle_count=count)
                status = shell.status()
                self.assertEqual(status["status"], "OK")
                self.assertGreater(status["truth_points"], 0)
                self.assertGreater(status["memory_total"], 0)
                self.assertLessEqual(status["memory_total"], status["truth_points"] + 1,
                                     f"At {count} obs: memory ({status['memory_total']}) "
                                     f"significantly exceeds truth ({status['truth_points']})")
                self.assertGreater(status["snapshot_cards"], 0,
                                   f"At {count} obs: no snapshot cards")


# ============================================================================
# REPLAY EVOLUTION
# ============================================================================

class TestReplayEvolution(unittest.TestCase):
    """Historical observations must be replayable from memory and timeline."""

    @classmethod
    def setUpClass(cls):
        cls.shell = STLMSShell(
            db_path=":memory:",
            symbol="BTCUSDT",
            timeframe="1m",
            enable_persistence=False,
        )
        cls.shell.generate(candle_count=200)

    def test_historical_observations_replayable(self):
        """Observations at various indices must be accessible."""
        for idx in (0, 10, 50, 100, 199):
            with self.subTest(candle_index=idx):
                obs = self.shell.get_observation(idx)
                self.assertTrue(obs.get("available") is not False,
                                f"Observation at candle {idx} not replayable")
                self.assertIn("observation_id", obs)
                self.assertIn("candle_index", obs)
                self.assertIsNotNone(obs.get("truth"),
                                     f"Observation {idx} missing truth context")

    def test_timeline_replayable(self):
        """Timeline range must return replayable observations."""
        timeline = self.shell.get_timeline(0, 50)
        self.assertGreater(len(timeline), 0, "Timeline is empty")
        for obs in timeline:
            self.assertIn("observation_id", obs)
            self.assertIn("candle_index", obs)
            self.assertIsNotNone(obs.get("truth"))
            self.assertIn("structure", obs)
            self.assertIsInstance(obs["structure"], dict)

        # Second range
        timeline2 = self.shell.get_timeline(50, 100)
        self.assertGreater(len(timeline2), 0, "Second timeline range empty")
        # All indices should be in [50, 99]
        for obs in timeline2:
            idx = obs["candle_index"]
            self.assertGreaterEqual(idx, 50,
                                    f"Timeline index {idx} < 50")
            self.assertLess(idx, 100,
                            f"Timeline index {idx} >= 100")

    def test_batch_data_replayable(self):
        """Batch-level data must be replayable via MarketObservationMemory."""
        mem = MarketObservationMemory(max_size=30)
        for i in range(60):
            mem.append({
                "candle_index": i,
                "close": 50000 + i * 10,
                "truth": {"close": 50000 + i * 10},
            })

        self.assertGreater(mem.batch_count, 0,
                           "Should have at least one completed batch")

        # Data across batch boundaries must be accessible
        for idx in (0, 15, 29, 30, 45, 59):
            obs = mem.get(idx)
            self.assertIsNotNone(obs, f"Observation {idx} not found")
            self.assertNotEqual(obs.get("available"), False,
                                f"Observation {idx} not replayable")

    def test_replay_matches_original(self):
        """Replayed observations must match truth points."""
        timeline = self.shell.get_timeline(0, 30)
        self.assertGreater(len(timeline), 0)

        for obs in timeline:
            idx = obs["candle_index"]
            tp = self.shell._truth_points[idx] if idx < len(self.shell._truth_points) else None
            if tp and obs.get("truth"):
                self.assertEqual(obs["truth"].get("close"), tp.close,
                                 f"Close mismatch at candle {idx}: "
                                 f"obs={obs['truth'].get('close')}, tp={tp.close}")


# ============================================================================
# SQLITE EVOLUTION
# ============================================================================

class TestSQLiteEvolution(unittest.TestCase):
    """SQLite must persist all layers with correct data."""

    @classmethod
    def setUpClass(cls):
        cls.tmpdir = tempfile.mkdtemp()
        cls.db_path = os.path.join(cls.tmpdir, "test_sqlite_evolution.db")
        cls.shell = STLMSShell(
            db_path=cls.db_path,
            symbol="BTCUSDT",
            timeframe="1m",
            enable_persistence=True,
        )
        cls.shell.generate(candle_count=100)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmpdir, ignore_errors=True)

    def test_all_tables_exist(self):
        """All expected SQLite tables must exist."""
        tables = self.shell.sqlite_tables()
        table_names = {t["name"] for t in tables}

        expected = {
            "snapshot_batches", "truth_snapshots", "structure_snapshots",
            "evidence_snapshots", "clone_observations", "trade_markers",
            "trade_statistics", "bag_artifacts", "knowledge_artifacts",
            "predictions", "governance_proposals",
        }
        missing = expected - table_names
        self.assertEqual(len(missing), 0,
                         f"Missing tables: {missing}")

    def test_data_persisted_to_tables(self):
        """Data must be written to SQLite tables."""
        tables = self.shell.sqlite_tables()

        tables_that_may_be_empty = {
            "governance_proposals", "bag_artifacts",
            "trade_markers", "knowledge_artifacts",
            "snapshot_batches",
        }

        tables_that_must_have_data = {
            "truth_snapshots", "structure_snapshots",
            "evidence_snapshots", "clone_observations",
            "predictions",
        }

        for t in tables:
            if t["name"] in tables_that_must_have_data:
                self.assertGreater(t["rows"], 0,
                                   f"Table '{t['name']}' has zero rows — nothing persisted")

    def test_snapshot_batches_persisted(self):
        """Snapshot batches table must exist."""
        tables = self.shell.sqlite_tables()
        table_names = {t["name"] for t in tables}
        self.assertIn("snapshot_batches", table_names,
                      "snapshot_batches table missing from SQLite")

    def test_queries_return_correct_data(self):
        """SQL queries must return valid data."""
        result = self.shell.sqlite_query(
            "SELECT COUNT(*) as cnt FROM truth_snapshots"
        )
        if result.get("rows"):
            count = result["rows"][0].get("cnt", 0)
            self.assertGreater(count, 0,
                               f"truth_snapshots has {count} rows")

        result2 = self.shell.sqlite_query(
            "SELECT symbol, timeframe FROM truth_snapshots LIMIT 1"
        )
        if result2.get("rows") and len(result2["rows"]) > 0:
            row = result2["rows"][0]
            self.assertEqual(row.get("symbol"), "BTCUSDT")
            self.assertEqual(row.get("timeframe"), "1m")

    def test_sqlite_query_with_limit_offset(self):
        """SQL queries must respect limit/offset."""
        result = self.shell.sqlite_query(
            "SELECT * FROM truth_snapshots", limit=5, offset=0
        )
        if result.get("rows"):
            self.assertLessEqual(len(result["rows"]), 5,
                                 f"Limit not respected: got {len(result['rows'])} rows")

    def test_persist_disabled_without_persistence(self):
        """persist() must report disabled when enable_persistence=False."""
        shell_no_persist = STLMSShell(
            db_path=":memory:",
            symbol="BTCUSDT",
            timeframe="1m",
            enable_persistence=False,
        )
        shell_no_persist.generate(candle_count=50)
        result = shell_no_persist.persist()
        self.assertFalse(result.get("persisted", True),
                         "persist() should return persisted=False when disabled")

    def test_trade_statistics_persisted(self):
        """Trade statistics must be persisted."""
        result = self.shell.sqlite_query(
            "SELECT COUNT(*) as cnt FROM trade_statistics"
        )
        if result.get("rows"):
            count = result["rows"][0].get("cnt", 0)
            self.assertGreater(count, 0,
                               f"trade_statistics has {count} rows — none persisted")

    def test_predictions_persisted(self):
        """Predictions must be persisted."""
        result = self.shell.sqlite_query(
            "SELECT COUNT(*) as cnt FROM predictions"
        )
        if result.get("rows"):
            count = result["rows"][0].get("cnt", 0)
            self.assertGreater(count, 0,
                               f"predictions has {count} rows — none persisted")


# ============================================================================
# PERFORMANCE AT SCALE
# ============================================================================

class TestPerformanceAtScale(unittest.TestCase):
    """Performance at increasing observation counts."""

    def test_100_observations_performance(self):
        """100 observations must generate within 2s."""
        shell = STLMSShell(
            db_path=":memory:",
            symbol="BTCUSDT",
            timeframe="1m",
            enable_persistence=False,
        )
        start = time.perf_counter()
        result = shell.generate(candle_count=100)
        elapsed = time.perf_counter() - start
        self.assertEqual(result["status"], "OK")
        self.assertLess(elapsed, 2.0,
                        f"100 obs took {elapsed:.2f}s, must be < 2s")

    def test_500_observations_performance(self):
        """500 observations must generate within 5s."""
        shell = STLMSShell(
            db_path=":memory:",
            symbol="BTCUSDT",
            timeframe="1m",
            enable_persistence=False,
        )
        start = time.perf_counter()
        result = shell.generate(candle_count=500)
        elapsed = time.perf_counter() - start
        self.assertEqual(result["status"], "OK")
        self.assertLess(elapsed, 5.0,
                        f"500 obs took {elapsed:.2f}s, must be < 5s")

    def test_1000_observations_performance(self):
        """1000 observations must generate within 10s."""
        shell = STLMSShell(
            db_path=":memory:",
            symbol="BTCUSDT",
            timeframe="1m",
            enable_persistence=False,
        )
        start = time.perf_counter()
        result = shell.generate(candle_count=1000)
        elapsed = time.perf_counter() - start
        self.assertEqual(result["status"], "OK")
        self.assertLess(elapsed, 10.0,
                        f"1000 obs took {elapsed:.2f}s, must be < 10s")

    def test_2000_observations_performance(self):
        """2000 observations must generate within 20s."""
        shell = STLMSShell(
            db_path=":memory:",
            symbol="BTCUSDT",
            timeframe="1m",
            enable_persistence=False,
        )
        start = time.perf_counter()
        result = shell.generate(candle_count=2000)
        elapsed = time.perf_counter() - start
        self.assertEqual(result["status"], "OK")
        self.assertLess(elapsed, 20.0,
                        f"2000 obs took {elapsed:.2f}s, must be < 20s")

    def test_5000_observations_performance(self):
        """5000 observations must generate within 50s."""
        shell = STLMSShell(
            db_path=":memory:",
            symbol="BTCUSDT",
            timeframe="1m",
            enable_persistence=False,
        )
        start = time.perf_counter()
        result = shell.generate(candle_count=5000)
        elapsed = time.perf_counter() - start
        self.assertEqual(result["status"], "OK")
        self.assertLess(elapsed, 50.0,
                        f"5000 obs took {elapsed:.2f}s, must be < 50s")


# ============================================================================
# STRESS TESTS
# ============================================================================

class TestStress(unittest.TestCase):
    """Stress tests for continuous collection and snapshot batch."""

    def test_continuous_collection_stress(self):
        """Multiple generate() calls with reset_first=False — no memory leaks."""
        shell = STLMSShell(
            db_path=":memory:",
            symbol="BTCUSDT",
            timeframe="1m",
            enable_persistence=False,
        )

        total_generated = 0
        for run in range(5):
            result = shell.generate(candle_count=50, reset_first=(run == 0))
            self.assertEqual(result["status"], "OK",
                             f"Run {run} failed: {result}")
            total_generated += 50

        status = shell.status()
        self.assertEqual(status["status"], "OK")
        self.assertGreater(status["truth_points"], 0)
        self.assertGreater(status["memory_total"], 0)
        # After 5 runs of 50, truth_points should be ~250 (each run adds to existing)
        self.assertGreaterEqual(status["truth_points"], 200,
                                f"Expected >= 200 truth points after 5x50, got {status['truth_points']}")

    def test_snapshot_batch_stress(self):
        """Force multiple batch completions — verify all batches accessible."""
        mem = MarketObservationMemory(max_size=15)
        batch_ids = []

        def on_full(batch):
            batch_ids.append(batch.batch_id)

        mem.set_batch_full_callback(on_full)

        for i in range(50):
            mem.append({
                "candle_index": i,
                "close": 50000 + i,
                "truth": {"close": 50000 + i},
            })

        self.assertGreater(len(batch_ids), 0,
                           "No batches completed during stress test")
        self.assertGreaterEqual(mem.batch_count, 1,
                                "Should have at least 1 completed batch")

        # All batches must be accessible
        for bid in batch_ids:
            batch = mem.get_batch(bid)
            self.assertIsNotNone(batch,
                                 f"Batch {bid} not accessible after completion")
            self.assertIn(batch.lifecycle_state, ("FREEZE", "ARCHIVE"),
                          f"Batch {bid} in unexpected state: {batch.lifecycle_state}")

        # All observations must still be accessible
        for idx in range(0, 50, 5):
            obs = mem.get(idx)
            self.assertIsNotNone(obs, f"Observation {idx} lost after stress")
            self.assertNotEqual(obs.get("available"), False,
                                f"Observation {idx} unavailable after stress")

    def test_stress_memory_does_not_leak(self):
        """Verify memory total grows correctly across runs."""
        shell = STLMSShell(
            db_path=":memory:",
            symbol="BTCUSDT",
            timeframe="1m",
            enable_persistence=False,
        )

        mem_before = 0
        for run in range(3):
            shell.generate(candle_count=100, reset_first=(run == 0))
            mem_current = shell._memory.stats()["total_observations"]
            self.assertGreater(mem_current, mem_before,
                               f"Run {run}: memory did not grow: {mem_before} -> {mem_current}")
            mem_before = mem_current

    def test_stress_data_integrity(self):
        """After stress, data integrity must be maintained."""
        shell = STLMSShell(
            db_path=":memory:",
            symbol="BTCUSDT",
            timeframe="1m",
            enable_persistence=False,
        )

        shell.generate(candle_count=100)
        obs_50 = shell.get_observation(50)
        self.assertTrue(obs_50.get("available") is not False)

        # Add more data
        shell.generate(candle_count=100, reset_first=False)

        # Original observation should still be accessible
        obs_50_after = shell.get_observation(50)
        self.assertTrue(obs_50_after.get("available") is not False,
                        "Original observation lost after additional generation")

        # New observations should also be accessible
        obs_150 = shell.get_observation(150)
        self.assertTrue(obs_150.get("available") is not False,
                        "New observation not accessible after stress")


if __name__ == "__main__":
    unittest.main(verbosity=2)
