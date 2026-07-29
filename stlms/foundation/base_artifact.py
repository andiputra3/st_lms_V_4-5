"""
ST-LMS v3 — Base Artifact
Foundation Core — Phase 1

All layer artifacts MUST extend BaseArtifact.
Reference: IMPLEMENTATION_FREEZE.md S7 (Layer Output Contract)
"""

from abc import ABC, abstractmethod
from typing import Any, Optional
from ..core.utils import Card, IDGenerator

class BaseArtifact(ABC):
    """Base class for all layer artifacts. Produces immutable cards."""

    def __init__(self, layer_name: str):
        self._layer = layer_name
        self._id_gen = IDGenerator()

    @property
    def layer(self) -> str:
        return self._layer

    @abstractmethod
    def produce(self, *args, **kwargs) -> Card:
        """Produce an immutable card from input data."""
        ...

    @abstractmethod
    def validate_input(self, *args, **kwargs) -> bool:
        """Validate input before producing artifact."""
        ...

    def make_card(self, entity_type: str, payload: dict,
                  dependencies: list, ts_ms: int) -> Card:
        return Card(entity_type, payload, dependencies, ts_ms, self._id_gen)

    def reset_ids(self) -> None:
        self._id_gen.reset()
