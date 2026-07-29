"""
=====================================================
MODULE:     knowledge/artifact.py
PURPOSE:    Knowledge Artifact — immutable knowledge_snapshot
            cards from knowledge entities.
OWNER:      KNOWLEDGE LAYER
=====================================================
"""

from ..core.utils import Card, wib_iso
from ..foundation.base_artifact import BaseArtifact


class KnowledgeArtifact(BaseArtifact):

    def __init__(self):
        super().__init__("KNOWLEDGE")

    def produce(self, entity_type: str, data: dict, ts: int) -> Card:
        if not self.validate_input(entity_type, data, ts):
            raise ValueError("Invalid Knowledge input")

        payload = {
            "entity": entity_type,
            "payload": data,
            "wib_iso": wib_iso(ts),
        }

        return self.make_card("knowledge_snapshot", payload, [], ts)

    def validate_input(self, entity_type: str, data: dict, ts: int) -> bool:
        return (entity_type is not None and data is not None
                and ts is not None and ts > 0)
