"""
ST-LMS v3 — Snapshot Consumer
Snapshot System — Phase 1

Downstream API for querying, exporting, and retrieving snapshots.
Reference: LAW-MASTER-16 (Snapshot), IMPLEMENTATION_FREEZE.md
"""

import json
import csv
import io
from typing import Any, Optional
from ..core.utils import Card
from ..foundation.base_consumer import BaseConsumer
from ..sqlite.connection import SQLiteConnection


class SnapshotConsumer(BaseConsumer):
    """Downstream consumer for querying and exporting snapshot cards."""

    def __init__(self, connection: SQLiteConnection):
        super().__init__("snapshot")
        self._conn = connection

    def consume(self, card: Card) -> dict:
        return card.to_dict()

    def query(self,
              snapshot_type: Optional[str] = None,
              ts_start: Optional[int] = None,
              ts_end: Optional[int] = None,
              symbol: Optional[str] = None,
              timeframe: Optional[str] = None,
              limit: int = 1000,
              **filters) -> list[dict]:
        clauses = []
        params = []
        if snapshot_type:
            clauses.append("entity_type = ?")
            params.append(snapshot_type)
        if ts_start is not None:
            clauses.append("timestamp_ms >= ?")
            params.append(ts_start)
        if ts_end is not None:
            clauses.append("timestamp_ms <= ?")
            params.append(ts_end)
        if symbol:
            clauses.append("payload_json LIKE ?")
            params.append(f"%{symbol}%")
        if timeframe:
            clauses.append("payload_json LIKE ?")
            params.append(f"%{timeframe}%")
        where = " AND ".join(clauses) if clauses else "1=1"
        sql = f"SELECT * FROM snapshots WHERE {where} ORDER BY timestamp_ms DESC LIMIT ?"
        params.append(limit)
        rows = self._conn.execute(sql, tuple(params)).fetchall()
        cards = [self._row_to_card(dict(r)) for r in rows]
        return self.export(cards, fmt="dict")

    def _row_to_card(self, row: dict) -> Card:
        card = Card.__new__(Card)
        card.entity_id = row["entity_id"]
        card.entity_type = row["entity_type"]
        card.entity_state = row["entity_state"]
        card.entity_version = row["entity_version"]
        card.timestamp_wib = row["timestamp_wib"]
        card.timestamp_ms = row["timestamp_ms"]
        card.component_name = row["component_name"]
        card.source_file = row["source_file"]
        card.dependencies = tuple(row["dependencies"].split(",")) if row["dependencies"] else ()
        card.payload = json.loads(row["payload_json"]) if isinstance(row["payload_json"], str) else row["payload_json"]
        card.checksum = row["checksum"]
        return card

    def export_json(self, cards: list[dict]) -> str:
        return json.dumps(cards, default=str, indent=2)

    def export_csv(self, cards: list[dict]) -> str:
        if not cards:
            return ""
        output = io.StringIO()
        fieldnames = list(cards[0].keys())
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for card in cards:
            row = {k: json.dumps(v, default=str) if isinstance(v, (dict, list)) else v for k, v in card.items()}
            writer.writerow(row)
        return output.getvalue()

    def get_latest(self, snapshot_type: str, symbol: Optional[str] = None) -> Optional[dict]:
        clauses = ["entity_type = ?"]
        params: list = [snapshot_type]
        if symbol:
            clauses.append("payload_json LIKE ?")
            params.append(f"%{symbol}%")
        where = " AND ".join(clauses)
        row = self._conn.execute(
            f"SELECT * FROM snapshots WHERE {where} ORDER BY timestamp_ms DESC LIMIT 1",
            tuple(params),
        ).fetchone()
        if row is None:
            return None
        card = self._row_to_card(dict(row))
        return card.to_dict()
