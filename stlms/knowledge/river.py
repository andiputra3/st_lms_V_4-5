"""
=====================================================
MODULE:     river.py
PURPOSE:    Knowledge Layer — RIVER (Event Chronicle)
            Append-only event log. Queryable by type/timerange.
OWNER:      PHASE-11 KNOWLEDGE LAYER
=====================================================
"""

from ..core.constants import CHRONICLE_MAX


class RiverEngine:
    """Append-only event log with query and slice capabilities."""

    max_history = CHRONICLE_MAX

    def __init__(self):
        self.chronicle: list[dict] = []

    def record(self, event_type: str, entity_id: str, payload: dict) -> None:
        import time
        ts = int(time.time() * 1000)
        event = {
            "ts": ts,
            "event_type": event_type,
            "entity_id": entity_id,
            "payload": payload,
        }
        self.chronicle.append(event)
        if len(self.chronicle) > self.max_history:
            self.chronicle = self.chronicle[-self.max_history:]

    def query(self, entity_type: str | None = None,
              start_ts: int | None = None, end_ts: int | None = None) -> list[dict]:
        results = self.chronicle
        if entity_type is not None:
            results = [e for e in results if e["event_type"] == entity_type]
        if start_ts is not None:
            results = [e for e in results if e["ts"] >= start_ts]
        if end_ts is not None:
            results = [e for e in results if e["ts"] <= end_ts]
        return results

    def slice(self, n: int = 40) -> list[dict]:
        return self.chronicle[-n:] if self.chronicle else []

    def stats(self) -> dict:
        counts: dict[str, int] = {}
        for e in self.chronicle:
            t = e["event_type"]
            counts[t] = counts.get(t, 0) + 1
        return counts
