"""
Tahap 19 · SQLite Writer
Tugas: SATU-SATUNYA writer ke SQLite. Nol race condition.
TIDAK ada stage lain yang menulis ke SQLite.
Output: rows_written, checksum
"""

import hashlib
import json
import sqlite3
from typing import Optional


class SQLiteWriter:
    """Satu-satunya writer. Serial. Nol race."""

    def __init__(self, db_path: str):
        self._db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None
        self._rows_written = 0
        self._write_count = 0
        self._table_stats: dict[str, int] = {}

    def _ensure_connection(self):
        if self._conn is None:
            self._conn = sqlite3.connect(self._db_path)
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA foreign_keys=ON")
            self._conn.execute("PRAGMA busy_timeout=5000")

    def close(self):
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def _write_table(self, table: str, data: dict, replace: bool = True) -> int:
        self._ensure_connection()
        if not data:
            return 0
        observation_id = data.get(
            "observation_id",
            hashlib.sha256(json.dumps(data, sort_keys=True, default=str).encode()).hexdigest()[:16]
        )
        json_data = json.dumps(data, default=str)
        self._conn.execute(
            f"CREATE TABLE IF NOT EXISTS {table} (observation_id TEXT PRIMARY KEY, data TEXT)"
        )
        action = "REPLACE" if replace else "INSERT"
        sql = f"{action} INTO {table} (observation_id, data) VALUES (?, ?)"
        self._conn.execute(sql, (observation_id, json_data))
        self._conn.commit()
        rows = 1
        self._rows_written += rows
        self._table_stats[table] = self._table_stats.get(table, 0) + 1
        return rows

    def write_truth_snapshots(self, data: dict) -> int:
        return self._write_table("truth_snapshots", data)

    def write_structure_snapshots(self, data: dict) -> int:
        return self._write_table("structure_snapshots", data)

    def write_evidence_snapshots(self, data: dict) -> int:
        return self._write_table("evidence_snapshots", data)

    def write_clone_observations(self, data: dict) -> int:
        return self._write_table("clone_observations", data)

    def write_trade_markers(self, data: dict) -> int:
        return self._write_table("trade_markers", data)

    def write_trade_statistics(self, data: dict) -> int:
        return self._write_table("trade_statistics", data)

    def write_bag_artifacts(self, data: dict) -> int:
        return self._write_table("bag_artifacts", data)

    def write_knowledge_artifacts(self, data: dict) -> int:
        return self._write_table("knowledge_artifacts", data)

    def write_predictions(self, data: dict) -> int:
        return self._write_table("predictions", data)

    def write_snapshot_batches(self, data: dict) -> int:
        return self._write_table("snapshot_batches", data)

    def write_all(self, frozen_observation) -> dict:
        self._ensure_connection()
        from ..core.freeze_engine import FrozenObservation

        if isinstance(frozen_observation, FrozenObservation):
            snapshot = frozen_observation.frozen_snapshot
        else:
            snapshot = frozen_observation

        results = {}
        table_map = {
            "truth": self.write_truth_snapshots,
            "structure": self.write_structure_snapshots,
            "evidence": self.write_evidence_snapshots,
            "clone": self.write_clone_observations,
            "trade_markers": self.write_trade_markers,
            "trade_statistics": self.write_trade_statistics,
            "bag": self.write_bag_artifacts,
            "knowledge": self.write_knowledge_artifacts,
            "prediction": self.write_predictions,
        }
        for key, writer_fn in table_map.items():
            if key in snapshot:
                rows = writer_fn(snapshot[key])
                results[key] = rows

        self._write_count += 1
        return {
            "tables_written": results,
            "total_rows": sum(results.values()),
            "checksum": hashlib.sha256(
                json.dumps(snapshot, sort_keys=True, default=str).encode()
            ).hexdigest(),
        }

    def get_writer_stats(self) -> dict:
        return {
            "db_path": self._db_path,
            "total_rows_written": self._rows_written,
            "total_write_operations": self._write_count,
            "table_stats": self._table_stats,
        }
