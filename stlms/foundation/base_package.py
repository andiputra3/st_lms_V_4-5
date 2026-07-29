"""
ST-LMS v3 — Base Package
Foundation Core — Phase 1

All layer packages MUST extend BasePackage.
Packages aggregate multiple artifacts into structured reports.
Reference: IMPLEMENTATION_FREEZE.md S7
"""

from abc import ABC, abstractmethod
from typing import Any
from ..core.utils import Card

class BasePackage(ABC):
    """Base class for all layer report packages."""

    def __init__(self, layer_name: str):
        self._layer = layer_name

    @property
    def layer(self) -> str:
        return self._layer

    @abstractmethod
    def build(self, artifacts: list[Card]) -> dict:
        """Build a structured report from artifacts."""
        ...

    @abstractmethod
    def summary(self, report: dict) -> str:
        """Generate a human-readable summary of the report."""
        ...

    def merge_reports(self, reports: list[dict]) -> dict:
        """Merge multiple reports into one."""
        merged = {"layer": self._layer, "reports": reports}
        return merged
