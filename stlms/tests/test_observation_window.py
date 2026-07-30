"""
ST-LMS v4 — Observation Window Tests
=====================================
Tests for configurable Market Observation Window,
SnapshotBatch lifecycle, and memory independence.
"""
import sys
import os
import time
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from stlms.core.shell import STLMSShell
from stlms.core.memory import MarketObservationMemory, SnapshotBatch


class TestConfigurableObservationWindow(unittest.TestCase):
    def _run_and_verify(self, candle_count):
        t0 = time.time()
        shell = STLMSShell(
            db_path=":memory:",
            symbol="BTCUSDT",
            timeframe="1m",
            enable_persistence=False,
        )
        shell.generate(candle_count=candle_count)
        elapsed = time.time() - t0

        status = shell.status()
        mem_stats = shell._memory.stats()

        self.assertEqual(len(shell._truth_points), candle_count,
                         f"Expected {candle_count} truth_points, got {len(shell._truth_points)}")
        self.assertEqual(mem_stats["current_size"], candle_count,
                         f"Expected {candle_count} memory obs, got {mem_stats['current_size']}")
        self.assertGreater(mem_stats["total_observations"], 0)

        snaps = shell.snapshots()
        self.assertGreater(snaps.get("total_cards", 0), 0)

        stats = shell.statistics_market()
        self.assertTrue(stats.get("available"), "Statistics not computed")

        internal = shell._statistics
        for domain in ["evolution", "indicator", "market", "clone_stats", "correlation", "distance", "oi"]:
            self.assertIn(domain, internal, f"Missing statistics domain: {domain}")

        self.assertLess(elapsed, 20, f"Generation took {elapsed:.1f}s, exceeds 20s limit")

    def test_window_100(self):
        self._run_and_verify(100)

    def test_window_500(self):
        self._run_and_verify(500)

    def test_window_1000(self):
        self._run_and_verify(1000)

    def test_window_5000(self):
        self._run_and_verify(5000)


class TestObservationWindowRotation(unittest.TestCase):
    def test_batch_created_when_window_full(self):
        memory = MarketObservationMemory(max_size=20)
        for i in range(45):
            memory.append({"candle_index": i, "data": f"obs_{i}"})

        stats = memory.stats()
        self.assertEqual(memory.batch_count, 2,
                         f"Expected 2 completed batches, got {memory.batch_count}")
        self.assertEqual(len(memory.completed_batches), 2)
        self.assertIsNotNone(memory.current_batch)
        self.assertGreater(memory.current_batch.size, 0)

    def test_batch_preserves_historical_data(self):
        memory = MarketObservationMemory(max_size=15)
        for i in range(40):
            memory.append({"candle_index": i, "value": i * 10})

        stats = memory.stats()
        self.assertGreater(memory.batch_count, 0)
        total_archived = sum(b.size for b in memory.completed_batches)
        self.assertGreater(total_archived, 0)

        obs = memory.get(5)
        self.assertFalse(obs.get("available") is False,
                         f"Observation 5 not available after archival")

        all_batches = memory.get_all_batches()
        self.assertGreater(len(all_batches), 0)

    def test_batch_lifecycle_transitions(self):
        memory = MarketObservationMemory(max_size=10)
        for i in range(35):
            memory.append({"candle_index": i, "x": i})

        self.assertEqual(len(memory.completed_batches), 3)
        for batch in memory.completed_batches:
            self.assertEqual(batch.lifecycle_state, "ARCHIVE",
                             f"Batch {batch.batch_id} is {batch.lifecycle_state}, expected ARCHIVE")
            self.assertIsInstance(batch.summary(), dict)
            summary = batch.summary()
            self.assertIn("batch_id", summary)
            self.assertIn("lifecycle_state", summary)
            self.assertIn("observation_count", summary)

        current = memory.current_batch
        self.assertIsNotNone(current)
        self.assertEqual(current.lifecycle_state, "LIVE")


class TestObservationMemoryIndependence(unittest.TestCase):
    def test_memory_window_not_api_limit(self):
        memory = MarketObservationMemory(max_size=50)
        for i in range(60):
            memory.append({"candle_index": i})
        stats = memory.stats()
        self.assertEqual(stats["max_size"], 50)

        memory2 = MarketObservationMemory(max_size=100)
        for i in range(120):
            memory2.append({"candle_index": i})
        stats2 = memory2.stats()
        self.assertEqual(stats2["max_size"], 100)

    def test_window_size_configurable(self):
        for size in [10, 25, 50, 100, 200]:
            memory = MarketObservationMemory(max_size=size)
            for i in range(size + 5):
                memory.append({"candle_index": i})
            stats = memory.stats()
            self.assertEqual(stats["max_size"], size)
            self.assertGreater(stats["total_observations"], size)

    def test_window_independent_of_provider(self):
        memory = MarketObservationMemory(max_size=42)
        for i in range(100):
            memory.append({"candle_index": i})
        self.assertEqual(memory.batch_count, 2)
        stats = memory.stats()
        self.assertEqual(stats["max_size"], 42)
