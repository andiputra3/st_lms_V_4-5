"""
ST-LMS v3 — SQLite Benchmark
Foundation Core — Phase 1
"""

import time
from .connection import SQLiteConnection
from .manager import SQLiteManager
from .viewer import SQLiteViewer

class SQLiteBenchmark:
    def __init__(self, connection: SQLiteConnection):
        self._conn = connection
        self._mgr = SQLiteManager(connection)
        self._viewer = SQLiteViewer(connection)

    def run_all(self) -> list[dict]:
        return [
            self._bench("insert_100_rows", self._bench_insert),
            self._bench("select_indexed", self._bench_select_indexed),
            self._bench("integrity_check", self._bench_integrity),
            self._bench("vacuum", self._bench_vacuum),
            self._bench("analyze", self._bench_analyze),
        ]

    def _bench(self, name: str, fn) -> dict:
        start = time.perf_counter()
        try:
            result = fn()
            elapsed_ms = (time.perf_counter() - start) * 1000
            return {"name": name, "elapsed_ms": round(elapsed_ms, 2), "result": result, "error": None}
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start) * 1000
            return {"name": name, "elapsed_ms": round(elapsed_ms, 2), "result": None, "error": str(e)}

    def _bench_insert(self) -> str:
        start = int(time.time() * 1000)
        for i in range(100):
            self._conn.execute(
                "INSERT OR IGNORE INTO app_settings(setting_key, setting_value, updated_at) VALUES (?,?,?)",
                (f"bench_{i}", f"value_{i}", start)
            )
        self._conn.commit()
        return "100 rows inserted"

    def _bench_select_indexed(self) -> str:
        rows = self._viewer.select_table("timeframes", limit=100)
        return f"{rows['total']} rows returned"

    def _bench_integrity(self) -> str:
        ok, detail = self._mgr.integrity_check()
        return f"integrity={ok}, detail={detail}"

    def _bench_vacuum(self) -> str:
        self._mgr.vacuum()
        return f"vacuum complete, size={self._mgr.size_bytes} bytes"

    def _bench_analyze(self) -> str:
        self._mgr.analyze()
        return "analyze complete"
