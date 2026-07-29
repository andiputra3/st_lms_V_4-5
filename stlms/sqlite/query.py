"""
ST-LMS v3 — SQLite Query Helper
Foundation Core — Phase 1

Parameterized query builder. No string concatenation.
"""

from typing import Any, Optional
from .connection import SQLiteConnection

class QueryHelper:
    def __init__(self, connection: SQLiteConnection):
        self._conn = connection

    def insert(self, table: str, data: dict) -> str:
        columns = ", ".join(data.keys())
        placeholders = ", ".join("?" for _ in data)
        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        self._conn.execute(sql, tuple(data.values()))
        self._conn.commit()
        return data.get(list(data.keys())[0], "")

    def insert_or_ignore(self, table: str, data: dict) -> None:
        columns = ", ".join(data.keys())
        placeholders = ", ".join("?" for _ in data)
        sql = f"INSERT OR IGNORE INTO {table} ({columns}) VALUES ({placeholders})"
        self._conn.execute(sql, tuple(data.values()))
        self._conn.commit()

    def update(self, table: str, data: dict, where: dict) -> int:
        sets = ", ".join(f"{k} = ?" for k in data)
        wheres = " AND ".join(f"{k} = ?" for k in where)
        sql = f"UPDATE {table} SET {sets} WHERE {wheres}"
        params = tuple(data.values()) + tuple(where.values())
        cur = self._conn.execute(sql, params)
        self._conn.commit()
        return cur.rowcount

    def delete(self, table: str, where: dict) -> int:
        wheres = " AND ".join(f"{k} = ?" for k in where)
        sql = f"DELETE FROM {table} WHERE {wheres}"
        cur = self._conn.execute(sql, tuple(where.values()))
        self._conn.commit()
        return cur.rowcount

    def select_one(self, table: str, where: dict) -> Optional[dict]:
        wheres = " AND ".join(f"{k} = ?" for k in where)
        sql = f"SELECT * FROM {table} WHERE {wheres} LIMIT 1"
        row = self._conn.execute(sql, tuple(where.values())).fetchone()
        return dict(row) if row else None

    def select_all(self, table: str, where: dict = None,
                   order_by: str = None, limit: int = None) -> list[dict]:
        sql = f"SELECT * FROM {table}"
        params = ()
        if where:
            wheres = " AND ".join(f"{k} = ?" for k in where)
            sql += f" WHERE {wheres}"
            params = tuple(where.values())
        if order_by:
            sql += f" ORDER BY {order_by}"
        if limit:
            sql += f" LIMIT {limit}"
        rows = self._conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]

    def exists(self, table: str, where: dict) -> bool:
        return self.select_one(table, where) is not None

    def count(self, table: str, where: dict = None) -> int:
        sql = f"SELECT COUNT(*) as cnt FROM {table}"
        params = ()
        if where:
            wheres = " AND ".join(f"{k} = ?" for k in where)
            sql += f" WHERE {wheres}"
            params = tuple(where.values())
        row = self._conn.execute(sql, params).fetchone()
        return row["cnt"] if row else 0
