"""
ST-LMS v3 — SQLite Viewer
Foundation Core — Phase 1

Read-only data browser with filtering, sorting, pagination, search, export.
Reference: SQLITE_FOUNDATION_FREEZE.md Section 5
"""

import json
import csv
import io
from typing import Optional
from .connection import SQLiteConnection

class SQLiteViewer:
    def __init__(self, connection: SQLiteConnection):
        self._conn = connection

    def query(self, sql: str, params: tuple = (),
              limit: int = 1000, offset: int = 0) -> dict:
        """Execute read query with pagination."""
        count_sql = f"SELECT COUNT(*) as total FROM ({sql})"
        total_row = self._conn.execute(count_sql, params).fetchone()
        total = total_row["total"] if total_row else 0
        paginated = f"{sql} LIMIT ? OFFSET ?"
        rows = self._conn.execute(paginated, params + (limit, offset)).fetchall()
        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "rows": [dict(r) for r in rows],
            "columns": [d[0] for d in rows[0].keys()] if rows else [],
        }

    def select_table(self, table: str, columns: list = None,
                     where: dict = None, order_by: str = None,
                     limit: int = 100, offset: int = 0) -> dict:
        cols = ", ".join(columns) if columns else "*"
        sql = f"SELECT {cols} FROM {table}"
        params = ()
        if where:
            clauses = [f"{k} = ?" for k in where]
            sql += " WHERE " + " AND ".join(clauses)
            params = tuple(where.values())
        if order_by:
            sql += f" ORDER BY {order_by}"
        return self.query(sql, params, limit, offset)

    def search_table(self, table: str, term: str,
                     columns: list = None, limit: int = 100) -> dict:
        """Full-text search across text columns."""
        text_cols = self._get_text_columns(table)
        if columns:
            text_cols = [c for c in columns if c in text_cols]
        if not text_cols:
            return {"total": 0, "rows": [], "columns": []}
        like_clauses = [f"{c} LIKE ?" for c in text_cols]
        sql = f"SELECT * FROM {table} WHERE {' OR '.join(like_clauses)}"
        params = tuple(f"%{term}%" for _ in text_cols)
        return self.query(sql, params, limit)

    def export_json(self, sql: str, params: tuple = ()) -> str:
        rows = self._conn.execute(sql, params).fetchall()
        return json.dumps([dict(r) for r in rows], indent=2, default=str)

    def export_csv(self, sql: str, params: tuple = ()) -> str:
        rows = self._conn.execute(sql, params).fetchall()
        if not rows:
            return ""
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows([dict(r) for r in rows])
        return output.getvalue()

    def get_schema(self, table: str) -> Optional[str]:
        row = self._conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name=?",
            (table,)
        ).fetchone()
        return row["sql"] if row else None

    def get_table_info(self, table: str) -> list[dict]:
        rows = self._conn.execute(f"PRAGMA table_info({table})").fetchall()
        return [dict(r) for r in rows]

    def explain_query(self, sql: str, params: tuple = ()) -> list[dict]:
        rows = self._conn.execute(f"EXPLAIN QUERY PLAN {sql}", params).fetchall()
        return [dict(r) for r in rows]

    def _get_text_columns(self, table: str) -> list[str]:
        info = self.get_table_info(table)
        return [r["name"] for r in info if "TEXT" in r.get("type", "").upper() or r["name"].endswith("json")]
