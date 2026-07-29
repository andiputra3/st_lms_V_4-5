"""
ST-LMS v3 — Snapshot Manager
Snapshot System — Phase 1

Produces immutable snapshot cards, freezes them, and persists to SQLite.
Reference: LAW-MASTER-16 (Snapshot), IMPLEMENTATION_FREEZE.md
"""

from typing import Optional
from ..core.utils import Card, IDGenerator
from ..foundation.base_artifact import BaseArtifact
from ..sqlite.connection import SQLiteConnection

SNAPSHOT_TABLE = "snapshots"

SNAPSHOT_TYPES = [
    "market_snapshot",
    "truth_snapshot",
    "structure_snapshot",
    "evidence_snapshot",
    "clone_observation",
    "trade_snapshot",
    "position_snapshot",
    "statistics_snapshot",
    "knowledge_snapshot",
    "prediction_snapshot",
    "benchmark_snapshot",
]

_SNAPSHOT_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS snapshots (
    entity_id        TEXT PRIMARY KEY,
    entity_type      TEXT NOT NULL,
    entity_state     TEXT NOT NULL DEFAULT 'FROZEN',
    entity_version   TEXT NOT NULL,
    timestamp_wib    TEXT NOT NULL,
    timestamp_ms     INTEGER NOT NULL,
    component_name   TEXT NOT NULL,
    source_file      TEXT NOT NULL,
    dependencies     TEXT NOT NULL,
    payload_json     TEXT NOT NULL,
    checksum         TEXT NOT NULL,
    frozen_at        TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_snapshots_ts      ON snapshots(timestamp_ms);
CREATE INDEX IF NOT EXISTS idx_snapshots_type    ON snapshots(entity_type);
CREATE INDEX IF NOT EXISTS idx_snapshots_state   ON snapshots(entity_state);
"""

class SnapshotManager(BaseArtifact):
    """Produces, freezes, stores, and replays immutable snapshot cards."""

    def __init__(self, connection: SQLiteConnection):
        super().__init__("snapshot")
        self._conn = connection
        self._cards: dict[str, Card] = {}
        self._init_store()

    def _init_store(self) -> None:
        db = self._conn.open()
        db.executescript(_SNAPSHOT_SCHEMA_SQL)
        self._conn.commit()

    def validate_input(self, *args, **kwargs) -> bool:
        return True

    def produce(self, layer_name: str, entity_type: str, payload: dict,
                dependencies: list, ts_ms: int) -> Card:
        if entity_type not in SNAPSHOT_TYPES:
            raise ValueError(f"Unknown snapshot type: {entity_type}")
        card = self.make_card(entity_type, payload, dependencies, ts_ms)
        self._cards[card.entity_id] = card
        return card

    def freeze(self, card: Card) -> Card:
        card.entity_state = "FROZEN"
        self._cards[card.entity_id] = card
        return card

    def store(self, card: Card) -> None:
        if card.entity_state != "FROZEN":
            raise ValueError("Card must be frozen before storing")
        self._conn.execute(
            """INSERT OR REPLACE INTO snapshots
               (entity_id, entity_type, entity_state, entity_version,
                timestamp_wib, timestamp_ms, component_name, source_file,
                dependencies, payload_json, checksum)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (
                card.entity_id,
                card.entity_type,
                card.entity_state,
                card.entity_version,
                card.timestamp_wib,
                card.timestamp_ms,
                card.component_name,
                card.source_file,
                ",".join(card.dependencies),
                _payload_to_json(card.payload),
                card.checksum,
            ),
        )
        self._conn.commit()

    def consume(self, card_id: str) -> Optional[Card]:
        row = self._conn.execute(
            "SELECT * FROM snapshots WHERE entity_id = ?", (card_id,)
        ).fetchone()
        if row is None:
            return None
        return _row_to_card(dict(row))

    def replay(self, start_ts: int, end_ts: int) -> list[Card]:
        rows = self._conn.execute(
            "SELECT * FROM snapshots WHERE timestamp_ms >= ? AND timestamp_ms <= ? ORDER BY timestamp_ms",
            (start_ts, end_ts),
        ).fetchall()
        return [_row_to_card(dict(r)) for r in rows]

    @property
    def snapshot_types(self) -> list[str]:
        return list(SNAPSHOT_TYPES)


def _payload_to_json(payload: dict) -> str:
    import json
    return json.dumps(payload, default=str)


def _row_to_card(row: dict) -> Card:
    import json
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
    card._id_gen = IDGenerator()
    return card
