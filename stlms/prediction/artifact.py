"""
=====================================================
MODULE:     prediction/artifact.py
PURPOSE:    Prediction Artifact — immutable prediction_snapshot
            cards from PredictionEngine results.
OWNER:      PREDICTION LAYER
=====================================================
"""

from ..core.utils import Card, wib_iso
from ..foundation.base_artifact import BaseArtifact


class PredictionArtifact(BaseArtifact):

    def __init__(self):
        super().__init__("PREDICTION")

    def produce(self, prediction_dict: dict, ts: int) -> Card:
        if not self.validate_input(prediction_dict, ts):
            raise ValueError("Invalid Prediction input")

        payload = {
            "intelligence_score": prediction_dict.get("intelligence_score"),
            "dominant_bias": prediction_dict.get("dominant_bias"),
            "possibilities": prediction_dict.get("possibilities"),
            "no_model": True,
            "wib_iso": wib_iso(ts),
        }

        return self.make_card("prediction_snapshot", payload, [], ts)

    def validate_input(self, prediction_dict: dict, ts: int) -> bool:
        return (prediction_dict is not None and ts is not None and ts > 0)
