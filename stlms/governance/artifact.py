"""
=====================================================
MODULE:     governance/artifact.py
PURPOSE:    Governance Artifact — immutable config_version
            cards from configuration snapshots.
OWNER:      GOVERNANCE LAYER
=====================================================
"""

from ..core.utils import Card, wib_iso
from ..foundation.base_artifact import BaseArtifact


class GovernanceArtifact(BaseArtifact):

    def __init__(self):
        super().__init__("GOVERNANCE")

    def produce(self, config_snapshot: dict, ts: int) -> Card:
        if not self.validate_input(config_snapshot, ts):
            raise ValueError("Invalid Governance input")

        payload = {
            "params": config_snapshot.get("params", config_snapshot),
            "version": config_snapshot.get("version", "1.0"),
            "timestamp": ts,
            "wib_iso": wib_iso(ts),
        }

        return self.make_card("config_version", payload, [], ts)

    def validate_input(self, config_snapshot: dict, ts: int) -> bool:
        return (config_snapshot is not None and ts is not None and ts > 0)
