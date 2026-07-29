"""
ST-LMS v3 — Snapshot Validator
Snapshot System — Phase 1

Validates snapshot cards: checksum, W/OD contract, lineage, determinism.
Reference: LAW-MASTER-01 (Determinism), LAW-MASTER-03 (Immutability), LAW-MASTER-16 (Snapshot)
"""

from typing import Any
from ..core.types import ValidationResult
from ..core.utils import Card, sha256
from ..foundation.base_validator import BaseValidator
from .registry import SnapshotRegistry


class SnapshotValidator(BaseValidator):
    """Validates snapshot cards for integrity, lineage, and determinism."""

    def __init__(self, registry: SnapshotRegistry):
        super().__init__("snapshot")
        self._registry = registry

    def validate(self, artifact: Any) -> list[ValidationResult]:
        if isinstance(artifact, Card):
            return self.validate_card(artifact)
        results = []
        for card in artifact if isinstance(artifact, list) else [artifact]:
            results.extend(self.validate_card(card))
        return results

    def validate_card(self, card: Card) -> list[ValidationResult]:
        results = []
        results.append(self._check_checksum(card))
        results.extend(self.validate_w_fields(card))
        results.extend(self.validate_od_fields(card))
        results.extend(self.validate_lineage(card))
        return results

    def _check_checksum(self, card: Card) -> ValidationResult:
        ok = card.verify()
        return ValidationResult(
            name="snapshot_checksum",
            passed=ok,
            detail="checksum matches" if ok else f"checksum mismatch for {card.entity_id}",
        )

    def validate_w_fields(self, card: Card) -> list[ValidationResult]:
        results = []
        try:
            self._registry.validate_snapshot(card.entity_type, card.payload)
            results.append(ValidationResult(
                name="snapshot_w_fields",
                passed=True,
                detail=f"all W fields present and non-null for {card.entity_type}",
            ))
        except ValueError as e:
            results.append(ValidationResult(
                name="snapshot_w_fields",
                passed=False,
                detail=str(e),
            ))
        return results

    def validate_od_fields(self, card: Card) -> list[ValidationResult]:
        results = []
        try:
            od_fields = self._registry.get_od_fields(card.entity_type)
        except ValueError as e:
            return [ValidationResult(
                name="snapshot_od_fields",
                passed=False,
                detail=str(e),
            )]
        violations = [f for f in od_fields if f in card.payload]
        if violations:
            results.append(ValidationResult(
                name="snapshot_od_fields",
                passed=False,
                detail=f"OD fields found in payload: {violations}",
            ))
        else:
            results.append(ValidationResult(
                name="snapshot_od_fields",
                passed=True,
                detail="no OD fields in stored payload",
            ))
        return results

    def validate_lineage(self, card: Card) -> list[ValidationResult]:
        results = []
        deps = set(card.dependencies)
        has_candle = any(d.startswith("candle_") for d in deps)
        has_config = any("config" in d.lower() for d in deps)
        results.append(ValidationResult(
            name="snapshot_lineage_candle",
            passed=has_candle,
            detail="has candle dependency" if has_candle else "missing candle_id in dependencies",
        ))
        results.append(ValidationResult(
            name="snapshot_lineage_config",
            passed=has_config,
            detail="has config dependency" if has_config else "missing config_version in dependencies",
        ))
        return results

    def validate_determinism(self, cards1: list[Card], cards2: list[Card]) -> ValidationResult:
        if len(cards1) != len(cards2):
            return ValidationResult(
                name="snapshot_determinism",
                passed=False,
                detail=f"card count mismatch: {len(cards1)} vs {len(cards2)}",
            )
        checksums1 = {c.entity_id: c.checksum for c in cards1}
        checksums2 = {c.entity_id: c.checksum for c in cards2}
        mismatches = []
        for eid in checksums1:
            if eid not in checksums2:
                mismatches.append(f"{eid} missing in run 2")
            elif checksums1[eid] != checksums2[eid]:
                mismatches.append(f"{eid} checksum differs: {checksums1[eid]} vs {checksums2[eid]}")
        for eid in checksums2:
            if eid not in checksums1:
                mismatches.append(f"{eid} missing in run 1")
        if mismatches:
            return ValidationResult(
                name="snapshot_determinism",
                passed=False,
                detail="; ".join(mismatches),
            )
        return ValidationResult(
            name="snapshot_determinism",
            passed=True,
            detail=f"all {len(cards1)} cards match across 2 runs",
        )
