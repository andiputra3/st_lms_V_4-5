"""
ST-LMS v3 — Base Consumer
Foundation Core — Phase 1

All layer consumers MUST extend BaseConsumer.
Consumers provide downstream API interfaces.
Reference: IMPLEMENTATION_FREEZE.md S7
"""

from abc import ABC, abstractmethod
from typing import Any, Optional
from ..core.utils import Card

class BaseConsumer(ABC):
    """Base class for all layer consumers. Downstream API interface."""

    def __init__(self, layer_name: str):
        self._layer = layer_name

    @property
    def layer(self) -> str:
        return self._layer

    @abstractmethod
    def consume(self, card: Card) -> dict:
        """Transform a card into a consumable format for downstream layers."""
        ...

    @abstractmethod
    def query(self, **filters) -> list[dict]:
        """Query artifacts with filters for downstream consumers."""
        ...

    def export(self, cards: list[Card], fmt: str = "dict") -> Any:
        """Export cards in requested format."""
        if fmt == "dict":
            return [c.to_dict() for c in cards]
        if fmt == "json":
            import json
            return json.dumps([c.to_dict() for c in cards], default=str)
        return [c.to_dict() for c in cards]
