"""
ST-LMS v3 — Foundation Benchmarks
Phase 1
"""

import sys
import os
import time
import unittest
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestFoundationBenchmark(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from stlms.sqlite.connection import SQLiteConnection
        from stlms.sqlite.manager import SQLiteManager
        cls.tmpdir = tempfile.mkdtemp()
        cls.db_path = os.path.join(cls.tmpdir, "bench.db")
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

    def test_sqlite_insert_speed(self):
        start = time.perf_counter()
        ts = int(time.time() * 1000)
        for i in range(100):
            self.conn.execute(
                "INSERT OR IGNORE INTO app_settings(setting_key, setting_value, updated_at) VALUES (?,?,?)",
                (f"bench_{i}", f"val_{i}", ts)
            )
        self.conn.commit()
        elapsed = (time.perf_counter() - start) * 1000
        self.assertLess(elapsed, 500, f"Insert too slow: {elapsed:.1f}ms")

    def test_sqlite_select_speed(self):
        from stlms.sqlite.viewer import SQLiteViewer
        viewer = SQLiteViewer(self.conn)
        start = time.perf_counter()
        r = viewer.select_table("timeframes", limit=9)
        elapsed = (time.perf_counter() - start) * 1000
        self.assertLess(elapsed, 10, f"Select too slow: {elapsed:.1f}ms")

    def test_import_speed(self):
        start = time.perf_counter()
        import stlms.core.types
        import stlms.core.constants
        import stlms.core.utils
        import stlms.core.validators
        import stlms.core.exceptions
        import stlms.sqlite.connection
        import stlms.sqlite.manager
        import stlms.sqlite.viewer
        import stlms.sqlite.validator
        import stlms.foundation.base_artifact
        import stlms.foundation.config_manager
        import stlms.foundation.registry
        elapsed = (time.perf_counter() - start) * 1000
        self.assertLess(elapsed, 2000, f"Import too slow: {elapsed:.1f}ms")

    def test_memory_friendly(self):
        from stlms.foundation.resource_manager import ResourceManager
        ok, msg = ResourceManager.is_vps_friendly(memory_limit_mb=1536.0)
        self.assertTrue(ok, f"Memory not VPS friendly: {msg}")

    def test_determinism(self):
        from stlms.core.utils import PRNG
        p1 = PRNG(42)
        p2 = PRNG(42)
        s1 = [p1.next() for _ in range(100)]
        s2 = [p2.next() for _ in range(100)]
        self.assertEqual(s1, s2)

if __name__ == "__main__":
    unittest.main(verbosity=2)
