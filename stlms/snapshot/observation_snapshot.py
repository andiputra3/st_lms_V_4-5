"""
Tahap 15 · Observation Snapshot Builder
Tugas: Membungkus seluruh artifact menjadi 1 Observation Snapshot.
1 snapshot = 1 observation. Berisi seluruh layer.
Output: ObservationSnapshot
"""
from dataclasses import dataclass, field
import hashlib
import json
import time


@dataclass
class ObservationSnapshot:
    observation_id: str
    candle_index: int
    market: dict = field(default_factory=dict)
    truth: dict = field(default_factory=dict)
    structure: dict = field(default_factory=dict)
    evidence: dict = field(default_factory=dict)
    clone: dict = field(default_factory=dict)
    statistics: dict = field(default_factory=dict)
    bag: dict = field(default_factory=dict)
    knowledge: dict = field(default_factory=dict)
    possibility: dict = field(default_factory=dict)
    simulation: dict = field(default_factory=dict)
    recommendation: dict = field(default_factory=dict)
    timeline: list = field(default_factory=list)
    frozen: bool = False
    checksum: str = ""


class ObservationSnapshotBuilder:
    """Membungkus seluruh artifact menjadi 1 snapshot per observation."""

    def build(self, observation_id: str, candle_index: int,
              artifacts: dict) -> ObservationSnapshot:
        snapshot = ObservationSnapshot(
            observation_id=observation_id,
            candle_index=candle_index,
            market=artifacts.get("market", {}),
            truth=artifacts.get("truth", {}),
            structure=artifacts.get("structure", {}),
            evidence=artifacts.get("evidence", {}),
            clone=artifacts.get("clone", {}),
            statistics=artifacts.get("statistics", {}),
            bag=artifacts.get("bag", {}),
            knowledge=artifacts.get("knowledge", {}),
            possibility=artifacts.get("possibility", {}),
            simulation=artifacts.get("simulation", {}),
            recommendation=artifacts.get("recommendation", {}),
            timeline=artifacts.get("timeline", []),
        )
        snapshot.checksum = self._compute_checksum(snapshot)
        return snapshot

    def freeze(self, snapshot: ObservationSnapshot) -> ObservationSnapshot:
        snapshot.frozen = True
        snapshot.checksum = self._compute_checksum(snapshot)
        return snapshot

    def verify_checksum(self, snapshot: ObservationSnapshot) -> bool:
        expected = self._compute_checksum(snapshot)
        return snapshot.checksum == expected

    def _compute_checksum(self, snapshot: ObservationSnapshot) -> str:
        payload = {
            "observation_id": snapshot.observation_id,
            "candle_index": snapshot.candle_index,
            "market": snapshot.market,
            "truth": snapshot.truth,
            "structure": snapshot.structure,
            "evidence": snapshot.evidence,
            "clone": snapshot.clone,
            "statistics": snapshot.statistics,
            "bag": snapshot.bag,
            "knowledge": snapshot.knowledge,
            "possibility": snapshot.possibility,
            "simulation": snapshot.simulation,
            "recommendation": snapshot.recommendation,
            "timeline": snapshot.timeline,
            "frozen": snapshot.frozen,
        }
        raw = json.dumps(payload, sort_keys=True, default=str)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()
