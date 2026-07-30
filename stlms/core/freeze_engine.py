"""
Tahap 18 · Observation Freeze Engine
Tugas: Membekukan seluruh artifact di SATU tempat.
TIDAK tersebar di setiap stage. Object.freeze + checksum + lifecycle=FROZEN.
Output: FrozenObservation
"""

from dataclasses import dataclass, field
import hashlib
import json
import time
from typing import Optional


@dataclass
class FrozenObservation:
    observation_id: str
    frozen_snapshot: dict
    checksum: str
    lifecycle: str = "FROZEN"
    frozen_at: float = field(default_factory=time.time)


class ObservationFreezeEngine:
    """Freeze terpusat. Satu tempat, satu tugas."""

    def __init__(self):
        self._freeze_count = 0
        self._frozen_ids: list[str] = []
        self._last_checksum: Optional[str] = None

    def freeze(self, snapshot: dict) -> FrozenObservation:
        observation_id = snapshot.get(
            "observation_id",
            hashlib.sha256(
                json.dumps(snapshot, sort_keys=True, default=str).encode()
            ).hexdigest()[:16]
        )
        frozen_snapshot = self._deep_copy(snapshot)
        frozen_snapshot["lifecycle"] = "FROZEN"
        frozen_snapshot["frozen_at"] = time.time()
        checksum = self.generate_checksum(frozen_snapshot)
        frozen = FrozenObservation(
            observation_id=observation_id,
            frozen_snapshot=frozen_snapshot,
            checksum=checksum,
        )
        self._freeze_count += 1
        self._frozen_ids.append(observation_id)
        self._last_checksum = checksum
        return frozen

    def generate_checksum(self, data: dict) -> str:
        payload = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(payload.encode()).hexdigest()

    def verify_checksum(self, frozen: FrozenObservation) -> bool:
        computed = self.generate_checksum(frozen.frozen_snapshot)
        return computed == frozen.checksum

    def is_frozen(self, observation) -> bool:
        if isinstance(observation, FrozenObservation):
            return observation.lifecycle == "FROZEN"
        if isinstance(observation, dict):
            return observation.get("lifecycle") == "FROZEN"
        return False

    def freeze_batch(self, snapshots: list[dict]) -> list[FrozenObservation]:
        return [self.freeze(s) for s in snapshots]

    def get_freeze_stats(self) -> dict:
        return {
            "total_frozen": self._freeze_count,
            "frozen_ids": self._frozen_ids,
            "last_checksum": self._last_checksum,
        }

    @staticmethod
    def _deep_copy(data):
        return json.loads(json.dumps(data, default=str))
