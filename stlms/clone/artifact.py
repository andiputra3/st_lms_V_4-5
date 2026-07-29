"""
=====================================================
MODULE:     clone/artifact.py
PURPOSE:    Clone Artifact — immutable clone_observation
            cards from per-clone observation dicts.
OWNER:      CLONE LAYER
=====================================================
"""

from ..core.utils import Card, wib_iso
from ..foundation.base_artifact import BaseArtifact


class CloneArtifact(BaseArtifact):

    def __init__(self):
        super().__init__("CLONE")

    def produce(self, observation_dict: dict, clone_id: str,
                ts: int) -> Card:
        if not self.validate_input(observation_dict, clone_id, ts):
            raise ValueError("Invalid Clone observation")

        payload = {
            "clone_id": clone_id,
            "bias": observation_dict.get("bias"),
            "entry_allowed": observation_dict.get("entry_allowed"),
            "no_entry_reason": observation_dict.get("no_entry_reason"),
            "setup_score": observation_dict.get("setup_score"),
            "confidence": observation_dict.get("confidence"),
            "expected_move": observation_dict.get("expected_move"),
            "fee_safe": observation_dict.get("fee_safe"),
            "open_position": observation_dict.get("open_position"),
            "wib_iso": wib_iso(ts),
        }

        return self.make_card("clone_observation", payload, [], ts)

    def validate_input(self, observation_dict: dict, clone_id: str,
                       ts: int) -> bool:
        return (observation_dict is not None and clone_id
                and ts is not None and ts > 0)
