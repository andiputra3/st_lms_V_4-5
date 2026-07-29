"""
ST-LMS v3 — Foundation Tests
Phase 1
"""

import sys
import os
import unittest
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stlms.core.types import DataStatus, TradeKind, TradeResult, CloneKind, Candle
from stlms.core.constants import BOUNDED_REGISTRY, ASSETS, SAMPLE_GATE
from stlms.core.utils import clamp, norm01, round_prec, canon, sha256, PRNG, IDGenerator, Card
from stlms.core.validators import validate_bounded, validate_symbol, validate_sample_gate
from stlms.core.exceptions import BoundedRangeError

class TestCoreTypes(unittest.TestCase):
    def test_enums(self):
        self.assertEqual(DataStatus.OK, "ok")
        self.assertEqual(TradeKind.ENTRY, "ENTRY")
        self.assertEqual(TradeResult.WIN, "WIN")
        self.assertEqual(CloneKind.LONG, "LONG")

    def test_candle(self):
        c = Candle(time=1000, open=100.0, high=105.0, low=99.0, close=103.0, volume=1000.0, taker_buy_ratio=0.55)
        self.assertEqual(c.open, 100.0)
        self.assertEqual(c.high, 105.0)

class TestCoreUtils(unittest.TestCase):
    def test_clamp(self):
        self.assertEqual(clamp(5, 0, 10), 5)
        self.assertEqual(clamp(-1, 0, 10), 0)
        self.assertEqual(clamp(15, 0, 10), 10)

    def test_norm01(self):
        self.assertAlmostEqual(norm01(50, 0, 100), 0.5)
        self.assertAlmostEqual(norm01(0, 0, 100), 0.0)
        self.assertAlmostEqual(norm01(100, 0, 100), 1.0)

    def test_round_prec(self):
        self.assertEqual(round_prec(0.0032011, 7), 0.0032011)
        self.assertEqual(round_prec(71.84, 2), 71.84)

    def test_canon(self):
        self.assertEqual(canon(0.0032011, 7), "0.0032011")
        self.assertEqual(canon(61750.0, 1), "61750.0")

    def test_sha256(self):
        h = sha256("test")
        self.assertEqual(len(h), 64)
        self.assertEqual(sha256("test"), sha256("test"))

    def test_prng_determinism(self):
        p1 = PRNG(42)
        p2 = PRNG(42)
        seq1 = [p1.next() for _ in range(10)]
        seq2 = [p2.next() for _ in range(10)]
        self.assertEqual(seq1, seq2)

    def test_id_generator(self):
        gen = IDGenerator()
        id1 = gen.generate(1753500000000, "TEST", "OS", "data")
        id2 = gen.generate(1753500000000, "TEST", "OS", "data")
        self.assertNotEqual(id1, id2)

    def test_card(self):
        gen = IDGenerator()
        card = Card("test_card", {"x": 1}, [], 1000, gen)
        self.assertTrue(card.verify())
        card.payload["x"] = 2
        self.assertFalse(card.verify())

class TestCoreValidators(unittest.TestCase):
    def test_validate_bounded_ok(self):
        ok, msg = validate_bounded("SAMPLE_GATE", 50)
        self.assertTrue(ok)

    def test_validate_bounded_out_of_range(self):
        ok, msg = validate_bounded("SAMPLE_GATE", 5)
        self.assertFalse(ok)
        self.assertIn("OUT_OF_RANGE", msg)

    def test_validate_bounded_unknown(self):
        ok, msg = validate_bounded("NONEXISTENT", 1)
        self.assertFalse(ok)

    def test_validate_symbol(self):
        self.assertTrue(validate_symbol("BTCUSDT"))
        self.assertFalse(validate_symbol("NONEXISTENT"))

    def test_validate_sample_gate(self):
        ok, status = validate_sample_gate(50)
        self.assertTrue(ok)
        self.assertEqual(status, "CUKUP")
        ok, status = validate_sample_gate(10)
        self.assertFalse(ok)
        self.assertEqual(status, "BELUM_CUKUP")

class TestSQLiteFoundation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from stlms.sqlite.connection import SQLiteConnection
        from stlms.sqlite.manager import SQLiteManager
        cls.tmpdir = tempfile.mkdtemp()
        cls.db_path = os.path.join(cls.tmpdir, "test.db")
        cls.conn = SQLiteConnection(cls.db_path)
        cls.mgr = SQLiteManager(cls.conn)
        schema_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "STLMS_SQLITE_SCHEMA_V1.sql")
        if os.path.exists(schema_path):
            cls.mgr.init_schema(schema_path)

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()
        import shutil
        shutil.rmtree(cls.tmpdir, ignore_errors=True)

    def test_connection_open(self):
        self.assertTrue(self.conn.is_open)

    def test_table_count(self):
        count = self.mgr.table_count()
        self.assertGreaterEqual(count, 40)

    def test_index_count(self):
        count = self.mgr.index_count()
        self.assertGreaterEqual(count, 9)

    def test_integrity(self):
        ok, detail = self.mgr.integrity_check()
        self.assertTrue(ok, f"Integrity failed: {detail}")

    def test_seed_data(self):
        from stlms.sqlite.viewer import SQLiteViewer
        viewer = SQLiteViewer(self.conn)
        r = viewer.select_table("timeframes", limit=20)
        self.assertGreaterEqual(r["total"], 9)
        r = viewer.select_table("domain_dictionary", limit=20)
        self.assertGreaterEqual(r["total"], 15)

    def test_viewer_query(self):
        from stlms.sqlite.viewer import SQLiteViewer
        viewer = SQLiteViewer(self.conn)
        r = viewer.select_table("timeframes", limit=5)
        self.assertGreater(r["total"], 0)
        self.assertIn("columns", r)

    def test_validator(self):
        from stlms.sqlite.validator import SQLiteValidator
        v = SQLiteValidator(self.conn)
        results = v.run_all()
        for r in results:
            self.assertTrue(r["passed"], f"{r['name']} failed: {r['detail']}")

    def test_benchmark(self):
        from stlms.sqlite.benchmark import SQLiteBenchmark
        b = SQLiteBenchmark(self.conn)
        results = b.run_all()
        for r in results:
            self.assertIsNone(r["error"], f"{r['name']} error: {r['error']}")
            self.assertLess(r["elapsed_ms"], 5000, f"{r['name']} too slow: {r['elapsed_ms']}ms")

class TestFoundationComponents(unittest.TestCase):
    def test_config_manager(self):
        from stlms.foundation.config_manager import ConfigurationManager
        cfg = ConfigurationManager()
        self.assertAlmostEqual(cfg.get("SAMPLE_GATE"), 30)
        ok, _ = cfg.set("SAMPLE_GATE", 50)
        self.assertTrue(ok)
        self.assertAlmostEqual(cfg.get("SAMPLE_GATE"), 50)
        ok, _ = cfg.set("SAMPLE_GATE", 5)
        self.assertFalse(ok)
        cfg.reset()
        self.assertAlmostEqual(cfg.get("SAMPLE_GATE"), 30)

    def test_symbol_manager(self):
        from stlms.foundation.symbol_manager import SymbolManager
        self.assertTrue(SymbolManager.exists("BTCUSDT"))
        self.assertEqual(SymbolManager.tick_size("BTCUSDT"), 0.1)
        self.assertEqual(SymbolManager.precision("BTCUSDT"), 1)

    def test_time_manager(self):
        from stlms.foundation.time_manager import TimeManager
        iso = TimeManager.wib_iso(1753500000000)
        self.assertIn("+07:00", iso)

    def test_registry(self):
        from stlms.foundation.registry import FoundationRegistry
        reg = FoundationRegistry()
        reg.register_layer("MARKET", {"type": "SHARED", "stage": 1})
        self.assertEqual(reg.layer_count(), 1)

    def test_resource_manager(self):
        from stlms.foundation.resource_manager import ResourceManager
        ok, msg = ResourceManager.is_vps_friendly()
        self.assertIsInstance(ok, bool)
        status = ResourceManager.status()
        self.assertIn("memory_mb", status)

class TestImportAll(unittest.TestCase):
    def test_import_core(self):
        import stlms.core.types
        import stlms.core.constants
        import stlms.core.utils
        import stlms.core.validators
        import stlms.core.exceptions

    def test_import_sqlite(self):
        import stlms.sqlite.connection
        import stlms.sqlite.manager
        import stlms.sqlite.viewer
        import stlms.sqlite.validator
        import stlms.sqlite.query
        import stlms.sqlite.benchmark

    def test_import_foundation(self):
        import stlms.foundation.base_artifact
        import stlms.foundation.base_package
        import stlms.foundation.base_consumer
        import stlms.foundation.base_validator
        import stlms.foundation.config_manager
        import stlms.foundation.time_manager
        import stlms.foundation.symbol_manager
        import stlms.foundation.resource_manager
        import stlms.foundation.registry

    def test_import_cli(self):
        import stlms.cli.foundation_cli

if __name__ == "__main__":
    unittest.main(verbosity=2)
