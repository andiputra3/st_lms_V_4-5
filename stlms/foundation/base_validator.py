"""
ST-LMS v3 — Base Validator
Foundation Core — Phase 1

All layer validators MUST extend BaseValidator.
Reference: IMPLEMENTATION_FREEZE.md S7
"""

from abc import ABC, abstractmethod
from typing import Any
from ..core.types import ValidationResult

class BaseValidator(ABC):
    """Base class for all layer validators."""

    def __init__(self, layer_name: str):
        self._layer = layer_name

    @property
    def layer(self) -> str:
        return self._layer

    @abstractmethod
    def validate(self, artifact: Any) -> list[ValidationResult]:
        """Validate an artifact. Returns list of validation results."""
        ...

    def run_all(self, artifacts: list) -> list[ValidationResult]:
        """Run all validations on a list of artifacts."""
        results = []
        for artifact in artifacts:
            results.extend(self.validate(artifact))
        return results

    def is_valid(self, results: list[ValidationResult]) -> bool:
        return all(r.passed for r in results)

    def summary(self, results: list[ValidationResult]) -> dict:
        passed = sum(1 for r in results if r.passed)
        failed = len(results) - passed
        return {
            "layer": self._layer,
            "total": len(results),
            "passed": passed,
            "failed": failed,
            "all_pass": failed == 0,
        }
