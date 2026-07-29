"""
=====================================================
MODULE:     bag/artifact.py
PURPOSE:    BAG Artifact — immutable bag_artifact
            cards from BagArtifact dataclass instances.
OWNER:      BAG LAYER
=====================================================
"""

from ..core.utils import Card, wib_iso
from ..foundation.base_artifact import BaseArtifact
from .engine import BagArtifact as BagData


class BAGArtifact(BaseArtifact):

    def __init__(self):
        super().__init__("BAG")

    def produce(self, bag: BagData, ts: int) -> Card:
        if not self.validate_input(bag, ts):
            raise ValueError("Invalid BAG input")

        payload = {
            "bag_id": bag.bag_id,
            "bag_kind": bag.bag_kind.value,
            "bag_key": bag.bag_key,
            "sample_count": bag.sample_count,
            "win_rate": bag.win_rate,
            "consensus": bag.consensus,
            "conflict_level": bag.conflict_level,
            "confidence": bag.confidence,
            "maturity_score": bag.maturity_score,
            "wib_iso": wib_iso(ts),
        }

        return self.make_card("bag_artifact", payload, [], ts)

    def validate_input(self, bag: BagData, ts: int) -> bool:
        return bag is not None and ts is not None and ts > 0
