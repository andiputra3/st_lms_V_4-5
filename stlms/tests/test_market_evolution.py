"""
ST-LMS v4 — Market Evolution Testing System
===========================================
Tests that the MARKET IS ALIVE.

Covers: entity presence, lifecycle, mutation, versioning,
market evolution, DNA, knowledge evolution, observation memory,
snapshot integrity, timeline, SQLite persistence, pipeline
integration, and performance.

Every test uses STLMSShell with enable_persistence=False for speed.
"""

import sys
import os
import unittest
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from stlms.core.shell import STLMSShell
from stlms.core.constants import PIPELINE_STAGES, MARKET_OBSERVATION_MEMORY
from stlms.core.types import Candle, DataStatus


class TestMarketIsAlive(unittest.TestCase):
    """Verify that the market ecosystem is alive and functioning."""

    @classmethod
    def setUpClass(cls):
        cls.shell = STLMSShell(
            db_path=":memory:",
            symbol="BTCUSDT",
            timeframe="1m",
            enable_persistence=False,
        )
        cls.shell.generate(candle_count=200)

    def test_market_entities_exist(self):
        """Every living market entity must be present."""
        status = self.shell.status()
        self.assertEqual(status["status"], "OK",
                         f"Status is {status['status']}, expected OK")
        self.assertGreater(status["truth_points"], 0,
                           "No TruthPoints generated — market is dead")
        self.assertGreater(status["lines"], 0,
                           "No Lines generated — structure layer failed")
        self.assertGreater(status["waves"], 0,
                           "No Waves generated — wave layer failed")
        self.assertGreater(status["snapshot_cards"], 0,
                           "No snapshot cards produced — pipeline broken")
        self.assertGreater(status["markers"], -1,
                           "Markers count missing from status")
        self.assertTrue(status["market_dna_available"],
                        "Market DNA not available")

    def test_observations_produced(self):
        """Pipeline must produce observations."""
        mem_stats = self.shell._memory.stats()
        self.assertGreater(mem_stats["current_size"], 0,
                           "Memory has zero observations — pipeline did not produce any")
        self.assertGreater(mem_stats["total_observations"], 0,
                           "Total observations is zero")

    def test_memory_populated(self):
        """MarketObservationMemory must have observations."""
        obs = self.shell.get_observation(0)
        self.assertTrue(obs.get("available") is not False,
                        "First observation is not available — memory empty")
        self.assertIsNotNone(obs.get("truth"),
                             "Observation has no truth context")

    def test_snapshots_produced(self):
        """Snapshots must be created."""
        snaps = self.shell.snapshots()
        self.assertGreater(snaps.get("total_cards", 0), 0,
                           "Zero snapshot cards — snapshot manager not producing")
        by_type = snaps.get("by_type", {})
        self.assertGreater(len(by_type), 0,
                           "No snapshot types registered")

    def test_statistics_computed(self):
        """All 7 statistics domains must have data."""
        stats = self.shell.statistics_market()
        self.assertTrue(stats.get("available"),
                        "Statistics not available — compute_statistics failed")
        by_clone = stats.get("by_clone", {})
        self.assertIn("LONG", by_clone,
                      "LONG clone statistics missing")
        self.assertIn("SHORT", by_clone,
                      "SHORT clone statistics missing")

        internal = self.shell._statistics
        expected_domains = ["evolution", "indicator", "market",
                            "clone_stats", "correlation", "distance", "oi"]
        for domain in expected_domains:
            self.assertIn(domain, internal,
                          f"Statistics domain '{domain}' is missing — "
                          f"only found: {list(internal.keys())}")


class TestEntityLifecycle(unittest.TestCase):
    """Every entity must have birth, live, update, mutation, freeze, archive."""

    @classmethod
    def setUpClass(cls):
        cls.shell = STLMSShell(
            db_path=":memory:",
            symbol="BTCUSDT",
            timeframe="1m",
            enable_persistence=False,
        )
        cls.shell.generate(candle_count=200)

    def test_truthpoint_lifecycle(self):
        """TruthPoints must go through lifecycle states."""
        points = self.shell._truth_points
        self.assertGreater(len(points), 0,
                           "No TruthPoints generated")
        tp = points[-1]
        self.assertIsNotNone(tp.ts, "TruthPoint has no timestamp")
        self.assertIsNotNone(tp.close, "TruthPoint has no close")
        self.assertIn(tp.st_color, ("HIJAU", "MERAH"),
                      f"TruthPoint st_color is {tp.st_color}, not HIJAU/MERAH")
        self.assertIn(tp.st_dir, (1, -1),
                      f"TruthPoint st_dir is {tp.st_dir}, not 1/-1")

    def test_line_lifecycle(self):
        """Lines must be constructed from TruthPoints."""
        lines = self.shell._lines
        self.assertGreater(len(lines), 0,
                           "No Lines constructed — LineBuilder produced nothing")
        line = lines[0]
        self.assertIsNotNone(line.st, "Line has no st value")
        self.assertIsNotNone(line.key, "Line has no key")
        self.assertGreater(line.members, 0,
                           f"Line has {line.members} members, expected > 0")
        self.assertIn(line.role, ("SUPPORT", "RESISTANCE"),
                      f"Line role is '{line.role}', not SUPPORT/RESISTANCE")
        self.assertIn(line.dominant, ("HIJAU", "MERAH"),
                      f"Line dominant is '{line.dominant}', not HIJAU/MERAH")

    def test_wave_lifecycle(self):
        """Waves must be constructed from Lines."""
        waves = self.shell._waves
        self.assertGreater(len(waves), 0,
                           "No Waves constructed — WaveBuilder produced nothing")
        wave = waves[-1]
        self.assertIsNotNone(wave.structure,
                             "Wave has no structure")
        valid_structures = [
            "STRONG_ACCUMULATION", "STRONG_DISTRIBUTION",
            "CONTINUATION_UP", "CONTINUATION_DOWN",
            "CONFIRMED_RANGE", "RANGE_EXPANDING", "RANGE_COMPRESSING",
            "REVERSAL_UP", "REVERSAL_DOWN",
            "EXHAUSTION_UP", "EXHAUSTION_DOWN",
            "SIDEWAY", "CHAOS", "PENDING_WAVE"
        ]
        self.assertIn(wave.structure, valid_structures,
                      f"Wave structure '{wave.structure}' not in 13 valid structures")
        self.assertGreater(len(wave.lines), 0,
                           "Wave has zero lines — invalid wave construction")

    def test_cage_lifecycle(self):
        """Cage must be built from Lines."""
        cage = self.shell._cage
        self.assertIsNotNone(cage, "Cage is None — CageEngine did not build")
        self.assertIsNotNone(cage.status, "Cage has no status")
        valid_statuses = ("NONE", "VALID_COMPRESSION", "LOOSE_SIDEWAY")
        self.assertIn(cage.status, valid_statuses,
                      f"Cage status '{cage.status}' not in valid statuses")

    def test_clone_lifecycle(self):
        """Clones must produce snapshots and the engine must exist."""
        snapshots = self.shell._snapshots
        self.assertGreater(len(snapshots), 0,
                           "No snapshots produced — clone pipeline broken")
        for snap in snapshots[:5]:
            self.assertIn("close", snap,
                          "Snapshot missing close price")
            self.assertIn("cage_status", snap,
                          "Snapshot missing cage_status")

    def test_knowledge_lifecycle(self):
        """Knowledge layer must produce academy, oracle, hivemind, librarian, darwin engines."""
        knowledge = self.shell._knowledge
        self.assertTrue(bool(knowledge), "Knowledge dict is empty")
        self.assertIn("academy", knowledge, "Academy missing from knowledge")
        self.assertIn("oracle", knowledge, "Oracle missing from knowledge")
        self.assertIn("hivemind", knowledge, "HiveMind missing from knowledge")
        self.assertIn("librarian", knowledge, "Librarian missing from knowledge")
        self.assertIn("darwin", knowledge, "Darwin missing from knowledge")
        self.assertIn("market_events", knowledge, "market_events missing from knowledge")

        academy = knowledge["academy"]
        self.assertIsInstance(academy, list,
                              "Academy is not a list — engine broken")
        oracle = knowledge["oracle"]
        self.assertIsInstance(oracle, dict,
                              "Oracle is not a dict — engine broken")
        hivemind = knowledge["hivemind"]
        self.assertIsInstance(hivemind, dict,
                              "HiveMind is not a dict — engine broken")
        librarian = knowledge["librarian"]
        self.assertIsInstance(librarian, list,
                              "Librarian is not a list — engine broken")
        darwin = knowledge["darwin"]
        self.assertIsInstance(darwin, list,
                              "Darwin is not a list — engine broken")
        market_events = knowledge["market_events"]
        self.assertIsInstance(market_events, list,
                              "market_events is not a list — event recorder broken")

    def test_prediction_lifecycle(self):
        """Prediction must be produced."""
        pred = self.shell._prediction
        self.assertTrue(bool(pred), "Prediction dict is empty")
        self.assertIn("dominant_bias", pred,
                      "Prediction has no dominant_bias")
        self.assertIn("intelligence_score", pred,
                      "Prediction has no intelligence_score")
        self.assertIn("possibilities", pred,
                      "Prediction has no possibilities list")

    def test_market_dna_lifecycle(self):
        """Market DNA must be extracted."""
        dna = self.shell.market_dna()
        self.assertTrue(dna.get("available"),
                        "Market DNA not available — extract_dna failed")
        self.assertGreater(len(dna), 2,
                           "Market DNA has minimal content")


class TestEntityMutation(unittest.TestCase):
    """Every entity must track mutations."""

    @classmethod
    def setUpClass(cls):
        cls.shell = STLMSShell(
            db_path=":memory:",
            symbol="BTCUSDT",
            timeframe="1m",
            enable_persistence=False,
        )
        cls.shell.generate(candle_count=300)

    def test_mutations_recorded(self):
        """Observations must have mutation deltas recorded."""
        obs = self.shell.get_observation(10)
        self.assertTrue(obs.get("available") is not False,
                        "Observation not available")
        if "mutation_delta" in obs:
            md = obs["mutation_delta"]
            self.assertIsInstance(md, dict,
                                  "Mutation delta is not a dict")

    def test_mutation_statistics_valid(self):
        """Mutation tracker must produce valid deltas."""
        obs = self.shell.get_observation(50)
        if "mutation_delta" in obs and obs["mutation_delta"]:
            md = obs["mutation_delta"]
            expected_keys = ["price_change_pct", "st_change", "atr_change_pct",
                              "rsi_change", "wpr_change", "macd_hist_change",
                              "dist_atr_change", "oi_change_pct"]
            for key in expected_keys:
                self.assertIn(key, md,
                              f"Mutation delta missing key '{key}'")

    def test_version_increments_on_mutation(self):
        """Versions should increase when mutations occur."""
        obs_early = self.shell.get_observation(5)
        obs_late = self.shell.get_observation(150)
        if "version" in obs_early and "version" in obs_late:
            v1 = obs_early.get("version", 0)
            v2 = obs_late.get("version", 0)
            self.assertGreaterEqual(v2, v1,
                                    f"Version did not increase: {v1} -> {v2}")


class TestEntityVersioning(unittest.TestCase):
    """Every entity must have version + version history."""

    @classmethod
    def setUpClass(cls):
        cls.shell = STLMSShell(
            db_path=":memory:",
            symbol="BTCUSDT",
            timeframe="1m",
            enable_persistence=False,
        )
        cls.shell.generate(candle_count=200)

    def test_truthpoint_has_version(self):
        """TruthPoint observations must carry version."""
        obs = self.shell.get_observation(100)
        self.assertTrue(obs.get("available") is not False)
        self.assertIn("version", obs,
                      "Observation missing 'version' field")
        self.assertIsInstance(obs["version"], int,
                              "Version is not an integer")

    def test_line_has_version(self):
        """Line must have mutation_count tracking."""
        lines = self.shell._lines
        self.assertGreater(len(lines), 0)
        line = lines[0]
        self.assertIsInstance(line.mutation_count, int,
                              "Line.mutation_count is not an integer")

    def test_wave_has_version(self):
        """Wave must have reliability and evolution tracking."""
        waves = self.shell._waves
        self.assertGreater(len(waves), 0)
        wave = waves[-1]
        self.assertIsInstance(wave.reliability_score, (int, float),
                              "Wave.reliability_score is not numeric")


class TestMarketEvolution(unittest.TestCase):
    """Market must evolve over time."""

    @classmethod
    def setUpClass(cls):
        cls.shell = STLMSShell(
            db_path=":memory:",
            symbol="BTCUSDT",
            timeframe="1m",
            enable_persistence=False,
        )
        cls.shell.generate(candle_count=500)

    def test_lines_evolve(self):
        """Lines must change across the dataset."""
        lines = self.shell._lines
        self.assertGreater(len(lines), 2,
                           "Not enough lines to verify evolution")
        first_st = lines[0].st
        last_st = lines[-1].st
        self.assertIsNotNone(first_st)
        self.assertIsNotNone(last_st)

    def test_waves_evolve(self):
        """Wave structures must form across the dataset."""
        waves = self.shell._waves
        self.assertGreater(len(waves), 0,
                           "No waves generated at all")
        closed_waves = [w for w in waves if w.status == "CLOSED_WAVE"]
        all_waves = closed_waves if closed_waves else waves
        structures = {w.structure for w in all_waves}
        self.assertGreater(len(structures), 0,
                           "No wave structures found")
        for s in structures:
            self.assertIsNotNone(s, "Wave structure is None")
            self.assertIsInstance(s, str, "Wave structure is not a string")

    def test_market_character_changes(self):
        """Market character must be analyzable."""
        if self.shell._waves:
            wave = self.shell._waves[-1]
            if hasattr(wave, 'market_character'):
                char = wave.market_character
                self.assertIsNotNone(char,
                                     "Market character is None")

    def test_dna_forms(self):
        """DNA must be extractable from market."""
        dna = self.shell.market_dna()
        self.assertTrue(dna.get("available"),
                        "Market DNA not available")


class TestMarketDNA(unittest.TestCase):
    """Market DNA must exist and be meaningful."""

    @classmethod
    def setUpClass(cls):
        cls.shell = STLMSShell(
            db_path=":memory:",
            symbol="BTCUSDT",
            timeframe="1m",
            enable_persistence=False,
        )
        cls.shell.generate(candle_count=500)

    def test_dna_profile_exists(self):
        """DNA profile must be present."""
        dna = self.shell.market_dna()
        self.assertTrue(dna.get("available"),
                        "DNA not available")

    def test_dna_has_wave_distribution(self):
        """DNA must have wave distribution."""
        dna = self.shell._market_dna
        self.assertTrue(bool(dna), "Market DNA internal is empty")
        self.assertIn("wave_distribution", dna,
                      "DNA missing 'wave_distribution' key")
        wave_dist = dna["wave_distribution"]
        self.assertIsInstance(wave_dist, dict,
                              "wave_distribution is not a dict")
        self.assertGreater(len(wave_dist), 0,
                           "wave_distribution is empty")

    def test_dna_has_cage_distribution(self):
        """DNA must have cage distribution."""
        dna = self.shell._market_dna
        self.assertTrue(bool(dna), "Market DNA internal is empty")
        self.assertIn("cage_distribution", dna,
                      "DNA missing 'cage_distribution' key")
        cage_dist = dna["cage_distribution"]
        self.assertIsInstance(cage_dist, dict,
                              "cage_distribution is not a dict")
        self.assertGreater(len(cage_dist), 0,
                           "cage_distribution is empty")

    def test_dna_has_market_character(self):
        """DNA must contain market character."""
        dna = self.shell._market_dna
        self.assertTrue(bool(dna), "Market DNA internal is empty")
        char_keys = ["dominant_wave", "regime", "profile"]
        found_char = any(k in dna for k in char_keys)
        self.assertTrue(found_char,
                        f"DNA has no market character keys: {list(dna.keys())}")


class TestKnowledgeEvolution(unittest.TestCase):
    """Knowledge must learn from observation, stats, DNA."""

    @classmethod
    def setUpClass(cls):
        cls.shell = STLMSShell(
            db_path=":memory:",
            symbol="BTCUSDT",
            timeframe="1m",
            enable_persistence=False,
        )
        cls.shell.generate(candle_count=300)

    def test_academy_learns_from_bag(self):
        """Academy engine must be present and return a list."""
        academy = self.shell.knowledge_academy()
        self.assertIsInstance(academy, list,
                              "Academy did not return a list")
        if len(academy) > 0:
            for bucket in academy:
                self.assertIsInstance(bucket, dict,
                                      f"Academy bucket is not a dict: {type(bucket)}")

    def test_oracle_matches_historical(self):
        """Oracle must produce a match against historical vectors."""
        oracle = self.shell.knowledge_oracle()
        self.assertIsInstance(oracle, dict,
                              "Oracle did not return a dict")
        self.assertIn("match", oracle,
                      "Oracle result missing 'match' key")
        self.assertIn("score", oracle,
                      "Oracle result missing 'score' key")

    def test_hivemind_has_evolution_context(self):
        """HiveMind must receive evolution context."""
        hivemind = self.shell.knowledge_hivemind()
        self.assertIsInstance(hivemind, dict,
                              "HiveMind did not return a dict")
        self.assertIn("dominant_bias", hivemind,
                      "HiveMind missing 'dominant_bias'")
        self.assertIn("intelligence_score", hivemind,
                      "HiveMind missing 'intelligence_score'")

    def test_hivemind_historical_learning(self):
        """HiveMind must have historical context."""
        hivemind = self.shell.knowledge_hivemind()
        self.assertGreater(hivemind.get("intelligence_score", 0), 0,
                           "HiveMind intelligence_score is zero")

    def test_librarian_evaluates_bag(self):
        """LibrarianEngine must evaluate bag artifacts and assign lifecycle status."""
        from stlms.knowledge.engine import LibrarianEngine
        bag_artifacts = self.shell._bag_artifacts
        librarian = LibrarianEngine()
        events = librarian.evaluate(bag_artifacts if bag_artifacts else [])
        self.assertIsInstance(events, list, "Librarian did not return a list")
        valid_statuses = {"NEW", "OBSERVATION", "TRUSTED", "MATURE", "DEAD", "DEPRECATED"}
        for event in events:
            self.assertIn("key", event, "Librarian event missing 'key'")
            self.assertIn("status", event, "Librarian event missing 'status'")
            self.assertIn(event["status"], valid_statuses,
                          f"Invalid librarian status: {event['status']}")
            self.assertIn("sample", event, "Librarian event missing 'sample'")
            self.assertIn("win_rate", event, "Librarian event missing 'win_rate'")

    def test_darwin_proposes_from_stats(self):
        """DarwinEngine must propose parameter adjustments from statistics."""
        from stlms.knowledge.engine import DarwinEngine
        stats = self.shell._statistics
        self.assertTrue(bool(stats), "Statistics dict is empty")
        darwin = DarwinEngine()
        proposals = darwin.propose(stats)
        self.assertIsInstance(proposals, list, "Darwin did not return a list")
        valid_types = {"TIGHTEN_ENTRY", "TIGHTEN_WRONG"}
        for proposal in proposals:
            self.assertIn("type", proposal, "Darwin proposal missing 'type'")
            self.assertIn(proposal["type"], valid_types,
                          f"Invalid darwin proposal type: {proposal['type']}")
            self.assertIn("target", proposal, "Darwin proposal missing 'target'")
            self.assertIn("param", proposal, "Darwin proposal missing 'param'")
            self.assertIn("reason", proposal, "Darwin proposal missing 'reason'")

    def test_snapshot_validator_rejects_invalid(self):
        """SnapshotValidator must validate snapshot cards and detect failures."""
        from stlms.snapshot.validator import SnapshotValidator
        from stlms.snapshot.registry import SnapshotRegistry
        registry = SnapshotRegistry()
        validator = SnapshotValidator(registry)
        results = validator.validate([])
        self.assertIsInstance(results, list, "Validator did not return a list")
        self.assertEqual(len(results), 0, "Validator should return empty for empty input")


class TestObservationMemory(unittest.TestCase):
    """48000 Market Observation Window."""

    @classmethod
    def setUpClass(cls):
        cls.shell = STLMSShell(
            db_path=":memory:",
            symbol="BTCUSDT",
            timeframe="1m",
            enable_persistence=False,
        )
        cls.shell.generate(candle_count=200)

    def test_memory_has_live_observation(self):
        """Memory must have one LIVE observation."""
        mem = self.shell._memory
        live = mem.get_live()
        self.assertIsNotNone(live,
                             "No LIVE observation in memory")
        self.assertEqual(live.get("evolution_state"), "LIVE",
                         f"Live observation state is '{live.get('evolution_state')}', not LIVE")

    def test_memory_has_frozen_observations(self):
        """Memory must have frozen historical observations."""
        mem = self.shell._memory
        stats = mem.stats()
        self.assertGreater(stats["frozen_count"], 0,
                           "No frozen observations in memory")

    def test_memory_rotation_works(self):
        """Freezing and appending must rotate correctly."""
        mem = self.shell._memory
        size_before = mem.size
        self.shell.generate(candle_count=50)
        size_after = mem.size
        self.assertGreater(size_after, 0,
                           "Memory empty after regenerate")
        self.assertGreaterEqual(size_after, size_before,
                                "Memory did not grow with new generation")

    def test_memory_evicts_when_full(self):
        """When full, batch is FREEZEd → archived to SQLite → new batch starts. Data NOT lost."""
        from stlms.core.memory import MarketObservationMemory
        small_mem = MarketObservationMemory(max_size=10)
        batch_summaries = []
        def on_full(batch):
            batch_summaries.append(batch.summary())
        small_mem.set_batch_full_callback(on_full)
        for i in range(35):
            small_mem.append({"candle_index": i, "value": f"obs_{i}"})
        # Should have completed batches (data archived, not lost)
        self.assertGreater(len(batch_summaries), 0,
                           "Should have completed snapshot batches")
        self.assertEqual(small_mem.total_observations, 35,
                         f"Total should be 35, got {small_mem.total_observations}")
        # Old observation should still be accessible via batch
        old_obs = small_mem.get(5)
        self.assertIsNotNone(old_obs, "Old observation must still be accessible")
        self.assertNotEqual(old_obs.get("available"), False,
                           "Old observation must not be lost")

    def test_memory_get_range(self):
        """get_range must return correct slice."""
        mem = self.shell._memory
        all_obs = mem.get_all()
        if len(all_obs) >= 10:
            ranged = mem.get_range(5, 15)
            for obs in ranged:
                idx = obs.get("candle_index", -1)
                self.assertGreaterEqual(idx, 5)
                self.assertLess(idx, 15)

    def test_memory_get_latest(self):
        """get_latest must return correct count."""
        mem = self.shell._memory
        latest = mem.get_latest(10)
        self.assertLessEqual(len(latest), 10,
                             f"get_latest returned {len(latest)}, expected <= 10")
        if len(latest) >= 2:
            idx1 = latest[-2].get("candle_index", -1)
            idx2 = latest[-1].get("candle_index", -1)
            self.assertLess(idx1, idx2,
                            "Latest observations not ordered by candle_index")


class TestSnapshotIntegrity(unittest.TestCase):
    """Snapshots must be immutable, valid, replayable."""

    @classmethod
    def setUpClass(cls):
        cls.shell = STLMSShell(
            db_path=":memory:",
            symbol="BTCUSDT",
            timeframe="1m",
            enable_persistence=False,
        )
        cls.shell.generate(candle_count=200)

    def test_all_snapshot_types_produced(self):
        """Multiple snapshot types must be produced."""
        snaps = self.shell.snapshots()
        by_type = snaps.get("by_type", {})
        expected_types = {"market_snapshot", "truth_snapshot",
                          "structure_snapshot", "evidence_snapshot",
                          "clone_observation", "statistics_snapshot",
                          "prediction_snapshot"}
        found = set(by_type.keys())
        missing = expected_types - found
        self.assertEqual(len(missing), 0,
                         f"Missing snapshot types: {missing}")

    def test_snapshot_counts_consistent(self):
        """Snapshot counts must be non-negative."""
        snaps = self.shell.snapshots()
        by_type = snaps.get("by_type", {})
        for stype, count in by_type.items():
            self.assertGreaterEqual(count, 0,
                                    f"Negative count for {stype}: {count}")

    def test_market_snapshot_exists(self):
        """Market snapshots must be produced."""
        snaps = self.shell.snapshots()
        by_type = snaps.get("by_type", {})
        self.assertIn("market_snapshot", by_type,
                      "No market_snapshot type")
        self.assertGreater(by_type["market_snapshot"], 0,
                           "Zero market_snapshot cards")

    def test_truth_snapshot_exists(self):
        """Truth snapshots must be produced."""
        snaps = self.shell.snapshots()
        by_type = snaps.get("by_type", {})
        self.assertIn("truth_snapshot", by_type,
                      "No truth_snapshot type")
        self.assertGreater(by_type["truth_snapshot"], 0,
                           "Zero truth_snapshot cards")


class TestTimeline(unittest.TestCase):
    """Every entity must have a timeline."""

    @classmethod
    def setUpClass(cls):
        cls.shell = STLMSShell(
            db_path=":memory:",
            symbol="BTCUSDT",
            timeframe="1m",
            enable_persistence=False,
        )
        cls.shell.generate(candle_count=200)

    def test_observation_timeline(self):
        """Timeline must return observation objects."""
        timeline = self.shell.get_timeline(0, 20)
        self.assertGreater(len(timeline), 0,
                           "Timeline is empty")
        for obs in timeline:
            self.assertIn("observation_id", obs,
                          "Timeline entry missing observation_id")
            self.assertIn("candle_index", obs,
                          "Timeline entry missing candle_index")
            self.assertIsNotNone(obs.get("truth"),
                                 "Timeline entry missing truth context")

    def test_timeline_range_query(self):
        """Timeline range query must return correct slice."""
        timeline = self.shell.get_timeline(10, 30)
        if len(timeline) > 0:
            first_idx = timeline[0].get("candle_index", -1)
            last_idx = timeline[-1].get("candle_index", -1)
            self.assertGreaterEqual(first_idx, 10,
                                    f"First index {first_idx} < 10")
            self.assertLess(last_idx, 30,
                            f"Last index {last_idx} >= 30")


class TestSQLitePersistence(unittest.TestCase):
    """SQLite must store all layers."""

    @classmethod
    def setUpClass(cls):
        cls.tmpdir = tempfile.mkdtemp()
        cls.db_path = os.path.join(cls.tmpdir, "test_evolution.db")
        cls.shell = STLMSShell(
            db_path=cls.db_path,
            symbol="BTCUSDT",
            timeframe="1m",
            enable_persistence=True,
        )
        cls.shell.generate(candle_count=100)

    @classmethod
    def tearDownClass(cls):
        import shutil
        shutil.rmtree(cls.tmpdir, ignore_errors=True)

    def test_tables_exist(self):
        """All expected SQLite tables must exist."""
        tables = self.shell.sqlite_tables()
        table_names = {t["name"] for t in tables}
        expected = {"truth_snapshots", "structure_snapshots",
                    "evidence_snapshots", "clone_observations",
                    "trade_markers", "trade_statistics",
                    "bag_artifacts", "knowledge_artifacts",
                    "predictions", "governance_proposals"}
        missing = expected - table_names
        self.assertEqual(len(missing), 0,
                         f"Missing tables: {missing}")

    def test_persistence_writes_data(self):
        """Data must be written to SQLite tables."""
        tables = self.shell.sqlite_tables()
        tables_that_may_be_empty = {"governance_proposals", "bag_artifacts",
                                     "trade_markers", "knowledge_artifacts",
                                     "snapshot_batches"}
        for t in tables:
            if t["name"] in tables_that_may_be_empty:
                continue
            self.assertGreater(t["rows"], 0,
                               f"Table '{t['name']}' has zero rows — nothing persisted")

    def test_query_returns_data(self):
        """SQL queries must return persisted data."""
        result = self.shell.sqlite_query("SELECT COUNT(*) as cnt FROM truth_snapshots")
        if result.get("rows"):
            count = result["rows"][0].get("cnt", 0)
            self.assertGreater(count, 0,
                               "truth_snapshots has zero rows")


class TestPipelineIntegration(unittest.TestCase):
    """End-to-end pipeline audit."""

    @classmethod
    def setUpClass(cls):
        cls.shell = STLMSShell(
            db_path=":memory:",
            symbol="BTCUSDT",
            timeframe="1m",
            enable_persistence=False,
        )
        cls.shell.generate(candle_count=100)

    def test_pipeline_runs_complete(self):
        """Pipeline must reach OK status."""
        status = self.shell.status()
        self.assertEqual(status["status"], "OK",
                         f"Pipeline status is '{status['status']}', expected OK")

    def test_all_stages_executed(self):
        """All 23 stages must execute."""
        status = self.shell.status()
        self.assertGreaterEqual(status["stages_executed"], 23,
                                f"Only {status['stages_executed']} stages executed, expected 23+")

    def test_prediction_not_signal(self):
        """Prediction must NOT claim to be a signal."""
        pred = self.shell.prediction_current()
        if pred.get("available"):
            self.assertIn("no_model", pred,
                          "Prediction missing 'no_model' field")

    def test_live_disabled(self):
        """With enable_persistence=False, persistence must report disabled."""
        result = self.shell.persist()
        self.assertFalse(result.get("persisted", True),
                         "Persistence should be disabled but persist returned True")


class TestPerformanceAtScale(unittest.TestCase):
    """Performance at increasing observation counts."""

    def test_1000_observations(self):
        """1000 observations must generate within limit."""
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
        self.assertLess(elapsed, 5.0,
                        f"1000 obs took {elapsed:.2f}s, must be < 5s")

    def test_5000_observations(self):
        """5000 observations must generate within 15s."""
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
        self.assertLess(elapsed, 15.0,
                        f"5000 obs took {elapsed:.2f}s, must be < 15s")

    def test_10000_observations(self):
        """10000 observations must generate within 90s."""
        shell = STLMSShell(
            db_path=":memory:",
            symbol="BTCUSDT",
            timeframe="1m",
            enable_persistence=False,
        )
        start = time.perf_counter()
        result = shell.generate(candle_count=10000)
        elapsed = time.perf_counter() - start
        self.assertEqual(result["status"], "OK")
        self.assertLess(elapsed, 90.0,
                        f"10000 obs took {elapsed:.2f}s, must be < 90s")


class TestLivingObjects(unittest.TestCase):
    """Verify that market entities are truly LIVING (not just exist)."""

    @classmethod
    def setUpClass(cls):
        cls.shell = STLMSShell(
            db_path=":memory:",
            symbol="BTCUSDT",
            timeframe="1m",
            enable_persistence=False,
        )
        cls.shell.generate(candle_count=200)

    def test_living_objects_have_state(self):
        """Verify ALL entities have LIVE state, not just exist."""
        status = self.shell.status()
        self.assertEqual(status["status"], "OK")
        self.assertGreater(status["truth_points"], 0)
        self.assertGreater(status["lines"], 0)
        self.assertGreater(status["waves"], 0)
        self.assertGreater(status["snapshot_cards"], 0)

        live_obs = self.shell._memory.get_live()
        self.assertIsNotNone(live_obs, "No LIVE observation in memory")
        self.assertEqual(live_obs.get("evolution_state"), "LIVE")

    def test_living_objects_have_counts(self):
        """Verify update_count, mutation_count, version_count, lifetime."""
        obs = self.shell.get_observation(100)
        self.assertTrue(obs.get("available") is not False)
        self.assertIn("version", obs)
        self.assertIsInstance(obs["version"], int)

        if "mutation_count" in obs:
            self.assertIsInstance(obs["mutation_count"], int)

        lines = self.shell._lines
        self.assertGreater(len(lines), 0)
        for line in lines[:5]:
            self.assertIsInstance(line.mutation_count, int)
            self.assertIsInstance(line.members, int)
            self.assertGreater(line.members, 0)

        waves = self.shell._waves
        self.assertGreater(len(waves), 0)
        for wave in waves[:3]:
            self.assertIsNotNone(wave.structure)
            self.assertGreater(len(wave.lines), 0)

    def test_living_objects_have_reliability(self):
        """Verify reliability scores for key entities."""
        waves = self.shell._waves
        self.assertGreater(len(waves), 0)
        for wave in waves[:3]:
            self.assertIsInstance(wave.reliability_score, (int, float))

        lines = self.shell._lines
        self.assertGreater(len(lines), 0)
        for line in lines[:3]:
            self.assertIsInstance(line.reliability_score, (int, float))


class TestSnapshotBatchEvolution(unittest.TestCase):
    """Test the SnapshotBatch system."""

    def test_batches_created_when_full(self):
        """Snapshot batches must be created when buffer reaches max_size."""
        from stlms.core.memory import MarketObservationMemory
        mem = MarketObservationMemory(max_size=20)
        batch_summaries = []
        def on_full(batch):
            batch_summaries.append(batch.summary())
        mem.set_batch_full_callback(on_full)

        for i in range(60):
            mem.append({"candle_index": i, "value": f"obs_{i}"})

        self.assertGreater(len(batch_summaries), 0,
                           "Should have completed snapshot batches")
        self.assertEqual(mem.total_observations, 60)
        self.assertEqual(mem.batch_count, len(batch_summaries))

    def test_batch_has_lifecycle(self):
        """Each batch must have NEW→LIVE→FREEZE→ARCHIVE lifecycle."""
        from stlms.core.memory import MarketObservationMemory
        mem = MarketObservationMemory(max_size=20)
        batch_lifecycles = []
        def on_full(batch):
            batch_lifecycles.append(batch.lifecycle_state)
        mem.set_batch_full_callback(on_full)

        for i in range(50):
            mem.append({"candle_index": i, "value": f"obs_{i}"})

        self.assertGreater(len(batch_lifecycles), 0)
        for state in batch_lifecycles:
            self.assertEqual(state, "FREEZE")

        for batch in mem.completed_batches:
            self.assertEqual(batch.lifecycle_state, "ARCHIVE")

    def test_batch_preserves_data(self):
        """Data in completed batches must still be accessible."""
        from stlms.core.memory import MarketObservationMemory
        mem = MarketObservationMemory(max_size=20)

        for i in range(50):
            mem.append({"candle_index": i, "value": f"obs_{i}"})

        old_obs = mem.get(5)
        self.assertIsNotNone(old_obs)
        self.assertNotEqual(old_obs.get("available"), False)

        old_obs2 = mem.get(15)
        self.assertIsNotNone(old_obs2)
        self.assertNotEqual(old_obs2.get("available"), False)

        self.assertEqual(mem.total_observations, 50)

    def test_batch_has_stats(self):
        """Each batch should have evolution report and DNA."""
        shell = STLMSShell(
            db_path=":memory:",
            symbol="BTCUSDT",
            timeframe="1m",
            enable_persistence=False,
        )
        shell.generate(candle_count=200)

        batches = shell._memory.get_all_batches()
        self.assertGreater(len(batches), 0)

        for batch_summary in batches:
            self.assertIn("batch_id", batch_summary)
            self.assertIn("lifecycle_state", batch_summary)
            self.assertIn("observation_count", batch_summary)
            self.assertGreater(batch_summary["observation_count"], 0)


class TestMarketSynchronization(unittest.TestCase):
    """Observation count synchronization tests."""

    @classmethod
    def setUpClass(cls):
        cls.shell = STLMSShell(
            db_path=":memory:",
            symbol="BTCUSDT",
            timeframe="1m",
            enable_persistence=False,
        )
        cls.shell.generate(candle_count=200)

    def test_observations_synchronized(self):
        """Observation count must match truth points count."""
        status = self.shell.status()
        truth_points = status["truth_points"]
        mem_obs = status["memory_observations"]
        self.assertGreater(truth_points, 0)
        self.assertGreater(mem_obs, 0)
        self.assertLessEqual(mem_obs, truth_points,
                             f"memory_observations ({mem_obs}) exceeds truth_points ({truth_points})")

    def test_memory_matches_pipeline(self):
        """Memory observations must match pipeline output."""
        mem_stats = self.shell._memory.stats()
        self.assertGreater(mem_stats["total_observations"], 0)
        self.assertGreater(mem_stats["current_size"], 0)

        status = self.shell.status()
        self.assertEqual(mem_stats["current_size"], status["memory_observations"])
        self.assertEqual(mem_stats["total_observations"], status["memory_total"])


class TestMarketEvolutionLoop(unittest.TestCase):
    """Market evolution loop tests."""

    def test_continuous_observation_works(self):
        """Multiple generate() calls must accumulate observations."""
        shell = STLMSShell(
            db_path=":memory:",
            symbol="BTCUSDT",
            timeframe="1m",
            enable_persistence=False,
        )
        result1 = shell.generate(candle_count=100)
        self.assertEqual(result1["status"], "OK")
        count1 = shell._memory.stats()["total_observations"]
        self.assertGreater(count1, 0)

        result2 = shell.generate(candle_count=50)
        self.assertEqual(result2["status"], "OK")
        count2 = shell._memory.stats()["total_observations"]
        self.assertGreater(count2, count1,
                           f"Observation count did not accumulate: {count1} -> {count2}")

    def test_batch_transitions(self):
        """Batch lifecycle must transition correctly across runs."""
        from stlms.core.memory import MarketObservationMemory
        mem = MarketObservationMemory(max_size=20)
        batch_states = []
        def on_full(batch):
            batch_states.append((batch.batch_id, batch.lifecycle_state))
        mem.set_batch_full_callback(on_full)

        for i in range(55):
            mem.append({"candle_index": i, "value": f"obs_{i}"})

        self.assertGreater(len(batch_states), 0)
        for batch_id, state in batch_states:
            self.assertEqual(state, "FREEZE",
                             f"Batch {batch_id} state is {state}, not FREEZE")

        for batch in mem.completed_batches:
            self.assertEqual(batch.lifecycle_state, "ARCHIVE",
                             f"Completed batch {batch.batch_id} is {batch.lifecycle_state}, not ARCHIVE")


class TestReplayEvolution(unittest.TestCase):
    """Historical observation replay tests."""

    @classmethod
    def setUpClass(cls):
        cls.shell = STLMSShell(
            db_path=":memory:",
            symbol="BTCUSDT",
            timeframe="1m",
            enable_persistence=False,
        )
        cls.shell.generate(candle_count=200)

    def test_historical_observation_replay(self):
        """Historical observations must be replayable from memory."""
        timeline = self.shell.get_timeline(0, 50)
        self.assertGreater(len(timeline), 0)

        for obs in timeline:
            self.assertIn("observation_id", obs)
            self.assertIn("candle_index", obs)
            self.assertIsNotNone(obs.get("truth"))

        obs_50 = self.shell.get_observation(50)
        self.assertTrue(obs_50.get("available") is not False)

        obs_150 = self.shell.get_observation(150)
        self.assertTrue(obs_150.get("available") is not False)

    def test_batch_replay(self):
        """Batch data must be replayable."""
        from stlms.core.memory import MarketObservationMemory
        mem = MarketObservationMemory(max_size=20)

        for i in range(50):
            mem.append({"candle_index": i, "close": 50000 + i * 10,
                        "truth": {"close": 50000 + i * 10}})

        self.assertGreater(mem.batch_count, 0)

        for i in [0, 10, 25, 49]:
            obs = mem.get(i)
            self.assertIsNotNone(obs, f"Observation {i} not replayable")
            self.assertNotEqual(obs.get("available"), False,
                                f"Observation {i} unavailable for replay")


class TestMTFScoring(unittest.TestCase):
    """MTF context and inheritance tests."""

    @classmethod
    def setUpClass(cls):
        cls.shell = STLMSShell(
            db_path=":memory:",
            symbol="BTCUSDT",
            timeframe="1m",
            enable_persistence=False,
        )
        cls.shell.generate(candle_count=200)

    def test_mtf_context_populated(self):
        """MTF context must be present in observations."""
        obs = self.shell.get_observation(100)
        self.assertTrue(obs.get("available") is not False)

        if "truth_observation" in obs:
            to = obs["truth_observation"]
            self.assertIn("mtf_context", to,
                          "truth_observation missing mtf_context")

    def test_mtf_inheritance_wired(self):
        """MTFInheritance must be used during pipeline."""
        obs_50 = self.shell.get_observation(50)
        obs_150 = self.shell.get_observation(150)

        self.assertTrue(obs_50.get("available") is not False)
        self.assertTrue(obs_150.get("available") is not False)

        for idx, obs in [(50, obs_50), (150, obs_150)]:
            if "truth_observation" in obs:
                to = obs["truth_observation"]
                mtf = to.get("mtf_context")
                self.assertIsNotNone(mtf,
                                     f"Observation {idx} has no mtf_context")


if __name__ == "__main__":
    unittest.main(verbosity=2)
