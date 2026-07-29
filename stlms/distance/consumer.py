"""
=====================================================
MODULE:     distance_consumer.py
PURPOSE:    Distance Consumer — API untuk downstream
            layers (Structure, Prediction, Governance).
OWNER:      PHASE-05 DISTANCE LAYER
=====================================================
"""

from ..core.utils import Card
from ..foundation.base_consumer import BaseConsumer


class DistanceConsumer(BaseConsumer):

    def __init__(self):
        super().__init__("DISTANCE")

    def consume(self, card: Card) -> dict:
        p = card.payload
        return {
            "ts": p.get("ts"),
            "dist": p.get("dist"),
            "dist_atr": p.get("dist_atr"),
            "dist_ceiling": p.get("dist_ceiling"),
            "dist_floor": p.get("dist_floor"),
            "bucket": p.get("bucket"),
            "sdv": p.get("sdv"),
            "p90": p.get("p90"),
            "trend": p.get("trend"),
            "velocity": p.get("velocity"),
            "ceiling_floor_ratio": p.get("ceiling_floor_ratio"),
            "dist_delta": p.get("dist_delta"),
            "wib_iso": p.get("wib_iso"),
            "card_id": card.entity_id,
        }

    def query(self, **filters) -> list[dict]:
        return []
