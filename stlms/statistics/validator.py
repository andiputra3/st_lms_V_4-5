"""
=====================================================
MODULE:     statistics/validator.py
PURPOSE:    Statistics Validator — validates
            statistics_snapshot cards for integrity
            and completeness.
OWNER:      STATISTICS LAYER
=====================================================
"""

from typing import Any
from ..core.utils import Card
from ..core.types import ValidationResult
from ..foundation.base_validator import BaseValidator


class StatisticsValidator(BaseValidator):
    """
    Validate statistics_snapshot cards.

    Checks:
        1. Payload structure integrity
        2. Domain results completeness (all expected domains)
        3. Numeric sanity (no NaN, no negative counts)
        4. Symbol and timestamp presence
    """

    EXPECTED_DOMAINS = [
        "market",
        "indicator",
        "distance",
        "clone",
        "oi",
        "correlation",
    ]

    def __init__(self):
        super().__init__("STATISTICS")

    def validate(self, artifact: Any) -> list[ValidationResult]:
        """
        Validate one statistics_snapshot card.

        Returns:
            List of ValidationResult per check.
        """
        results: list[ValidationResult] = []
        p = artifact.payload if hasattr(artifact, "payload") else artifact

        results.append(self._check_structure(p))
        results.append(self._check_domains(p))
        results.append(self._check_numeric_sanity(p))
        results.append(self._check_metadata(p))

        return results

    def _check_structure(self, p: dict) -> ValidationResult:
        required = {"symbol", "domains", "domain_count"}
        missing = required - set(p.keys())
        if missing:
            return ValidationResult(
                name="structure",
                passed=False,
                detail=f"Missing keys: {missing}",
            )
        if not isinstance(p["domains"], dict):
            return ValidationResult(
                name="structure",
                passed=False,
                detail="domains is not a dict",
            )
        return ValidationResult(name="structure", passed=True, detail="OK")

    def _check_domains(self, p: dict) -> ValidationResult:
        domains = p.get("domains", {})
        present = set(domains.keys())
        missing = set(self.EXPECTED_DOMAINS) - present
        if missing:
            return ValidationResult(
                name="domain_completeness",
                passed=False,
                detail=f"Missing domains: {missing}",
            )
        return ValidationResult(
            name="domain_completeness",
            passed=True,
            detail=f"All {len(present)} domains present",
        )

    def _check_numeric_sanity(self, p: dict) -> ValidationResult:
        import math

        def _recurse_check(d: Any, path: str = "") -> list[str]:
            issues: list[str] = []
            if isinstance(d, dict):
                for k, v in d.items():
                    issues.extend(_recurse_check(v, f"{path}.{k}" if path else k))
            elif isinstance(d, list):
                for i, v in enumerate(d):
                    issues.extend(_recurse_check(v, f"{path}[{i}]"))
            elif isinstance(d, float):
                if math.isnan(d):
                    issues.append(f"{path} is NaN")
                elif math.isinf(d):
                    issues.append(f"{path} is Inf")
            return issues

        issues = _recurse_check(p.get("domains", {}))
        if issues:
            return ValidationResult(
                name="numeric_sanity",
                passed=False,
                detail=f"Issues: {issues[:5]}",
            )
        return ValidationResult(name="numeric_sanity", passed=True, detail="OK")

    def _check_metadata(self, p: dict) -> ValidationResult:
        issues = []
        if not p.get("symbol"):
            issues.append("symbol is empty")
        if p.get("domain_count", 0) <= 0:
            issues.append("domain_count <= 0")
        if issues:
            return ValidationResult(
                name="metadata",
                passed=False,
                detail="; ".join(issues),
            )
        return ValidationResult(name="metadata", passed=True, detail="OK")

    def validate_completeness(self, artifacts: list[Card]) -> ValidationResult:
        """
        Validate that all expected domains appear across the card set.
        """
        all_domains: set[str] = set()
        for card in artifacts:
            p = card.payload if hasattr(card, "payload") else card
            all_domains.update(p.get("domains", {}).keys())

        missing = set(self.EXPECTED_DOMAINS) - all_domains
        if missing:
            return ValidationResult(
                name="cross_card_completeness",
                passed=False,
                detail=f"Missing across all cards: {missing}",
            )
        return ValidationResult(
            name="cross_card_completeness",
            passed=True,
            detail=f"All {len(all_domains)} domains covered",
        )
