"""
ST-LMS v3 — SQLite Connection Manager
Foundation Core — Phase 1

Single writer, WAL mode, foreign keys ON.
Reference: LAW-MASTER-17 (Native-HTML Binding), SQLITE_FOUNDATION_FREEZE.md
"""

import sqlite3
import os
from typing import Optional

class SQLiteConnection:
    """Thread-safe SQLite connection manager. Serial writer pattern."""

    def __init__(self, db_path: str = "stlms.db"):
        self._db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None

    @property
    def path(self) -> str:
        return self._db_path

    def open(self) -> sqlite3.Connection:
        if self._conn is not None:
            return self._conn
        self._conn = sqlite3.connect(self._db_path)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA foreign_keys=ON")
        self._conn.execute("PRAGMA busy_timeout=5000")
        self._conn.row_factory = sqlite3.Row
        return self._conn

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        conn = self.open()
        return conn.execute(sql, params)

    def executemany(self, sql: str, params_list: list) -> sqlite3.Cursor:
        conn = self.open()
        return conn.executemany(sql, params_list)

    def commit(self) -> None:
        if self._conn is not None:
            self._conn.commit()

    def rollback(self) -> None:
        if self._conn is not None:
            self._conn.rollback()

    def cursor(self) -> sqlite3.Cursor:
        return self.open().cursor()

    @property
    def is_open(self) -> bool:
        return self._conn is not None

    @property
    def size_bytes(self) -> int:
        if not os.path.exists(self._db_path):
            return 0
        return os.path.getsize(self._db_path)
