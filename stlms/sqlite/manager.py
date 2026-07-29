"""
ST-LMS v3 — SQLite Manager
Foundation Core — Phase 1

Schema initialization, backup, restore, vacuum, integrity, optimization.
Reference: SQLITE_FOUNDATION_FREEZE.md Section 6
"""

import os
import shutil
import sqlite3
from typing import Optional
from .connection import SQLiteConnection

class SQLiteManager:
    def __init__(self, connection: SQLiteConnection):
        self._conn = connection

    def init_schema(self, schema_path: str) -> None:
        """Execute schema SQL file. Idempotent (IF NOT EXISTS)."""
        with open(schema_path, "r") as f:
            sql = f.read()
        db = self._conn.open()
        db.executescript(sql)
        self._conn.commit()

    def table_count(self) -> int:
        row = self._conn.execute(
            "SELECT COUNT(*) as cnt FROM sqlite_master WHERE type='table'"
        ).fetchone()
        return row["cnt"] if row else 0

    def index_count(self) -> int:
        row = self._conn.execute(
            "SELECT COUNT(*) as cnt FROM sqlite_master WHERE type='index'"
        ).fetchone()
        return row["cnt"] if row else 0

    def trigger_count(self) -> int:
        row = self._conn.execute(
            "SELECT COUNT(*) as cnt FROM sqlite_master WHERE type='trigger'"
        ).fetchone()
        return row["cnt"] if row else 0

    def view_count(self) -> int:
        row = self._conn.execute(
            "SELECT COUNT(*) as cnt FROM sqlite_master WHERE type='view'"
        ).fetchone()
        return row["cnt"] if row else 0

    def table_row_count(self, table_name: str) -> int:
        row = self._conn.execute(
            f"SELECT COUNT(*) as cnt FROM {table_name}"
        ).fetchone()
        return row["cnt"] if row else 0

    def list_tables(self) -> list[str]:
        rows = self._conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
        return [r["name"] for r in rows]

    def list_indexes(self) -> list[dict]:
        rows = self._conn.execute(
            "SELECT name, tbl_name FROM sqlite_master WHERE type='index' ORDER BY name"
        ).fetchall()
        return [{"name": r["name"], "table": r["tbl_name"]} for r in rows]

    def integrity_check(self) -> tuple[bool, str]:
        row = self._conn.execute("PRAGMA integrity_check").fetchone()
        result = row[0] if row else "no result"
        return (result == "ok", str(result))

    def foreign_key_check(self) -> list[dict]:
        rows = self._conn.execute("PRAGMA foreign_key_check").fetchall()
        return [dict(r) for r in rows]

    def vacuum(self) -> None:
        self._conn.execute("VACUUM")

    def vacuum_into(self, target_path: str) -> None:
        self._conn.execute(f"VACUUM INTO '{target_path}'")

    def analyze(self) -> None:
        self._conn.execute("ANALYZE")

    def reindex(self) -> None:
        self._conn.execute("REINDEX")

    def optimize(self) -> None:
        self._conn.execute("PRAGMA optimize")

    def backup(self, backup_path: str) -> str:
        src = sqlite3.connect(self._conn.path)
        dst = sqlite3.connect(backup_path)
        src.backup(dst)
        src.close()
        dst.close()
        return backup_path

    def restore(self, backup_path: str) -> None:
        self._conn.close()
        shutil.copy2(backup_path, self._conn.path)
        self._conn.open()

    @property
    def size_bytes(self) -> int:
        return self._conn.size_bytes

    @property
    def stats(self) -> dict:
        return {
            "path": self._conn.path,
            "size_bytes": self.size_bytes,
            "tables": self.table_count(),
            "indexes": self.index_count(),
            "triggers": self.trigger_count(),
            "views": self.view_count(),
            "is_open": self._conn.is_open,
        }
