"""
=====================================================
MODULE:     trade_validator.py
PURPOSE:    Trade Validator — validasi P&L correctness,
            adverse-first, fee consistency.
OWNER:      PHASE-10 TRADE LAYER
INPUT:      trade_snapshot cards
OUTPUT:     ValidationResult list
DEPENDENCY: stlms.foundation.base_validator (BaseValidator)
ARCHITECTURE:
            Validator memeriksa setiap trade_snapshot card.
            P&L correctness: gross sesuai rumus, net = gross - fee - slip.
            Adverse-first: SL beats TP pada candle yang sama.
            Fee consistency: fee sesuai jenis (maker/taker).
=====================================================
"""

from typing import Any
from ..core.utils import Card
from ..core.types import ValidationResult
from ..core.constants import FEE_MAKER, FEE_TAKER, SLIP_ESTIMATE
from ..foundation.base_validator import BaseValidator


class TradeValidator(BaseValidator):
    """
    Validasi trade_snapshot cards.

    Checks:
        1. P&L correctness: gross formula and net = gross - fee - slip
        2. Adverse-first: SL beats TP on same candle
        3. Fee consistency: fee is maker (0.04%) or taker (0.10%)
        4. Marker integrity: required fields present
    """

    def __init__(self):
        super().__init__("TRADE")

    def validate(self, artifact: Any) -> list[ValidationResult]:
        """
        Validate one trade_snapshot artifact.

        Returns:
            List of ValidationResult — PASS/FAIL per check.
        """
        results: list[ValidationResult] = []
        p = artifact.payload if hasattr(artifact, 'payload') else artifact

        # 1. Required fields
        required = ["ts", "clone", "side", "kind", "reason", "entry"]
        missing = [f for f in required if f not in p or p[f] is None]
        results.append(ValidationResult(
            name="required_fields",
            passed=len(missing) == 0,
            detail=f"Missing: {missing}" if missing else "All present"
        ))

        # 2. Marker integrity
        kind = p.get("kind")
        if kind == "ENTRY":
            entry_ok = p.get("entry", 0) > 0
            exit_null = p.get("exit") is None
            results.append(ValidationResult(
                name="entry_marker_integrity",
                passed=entry_ok and exit_null,
                detail="OK" if entry_ok and exit_null else "ENTRY marker invalid"
            ))
        elif kind == "EXIT":
            entry = p.get("entry", 0)
            exit_val = p.get("exit", 0)
            marker_ok = entry > 0 and exit_val > 0
            results.append(ValidationResult(
                name="exit_marker_integrity",
                passed=marker_ok,
                detail="OK" if marker_ok else "EXIT marker missing entry/exit price"
            ))

            # 3. P&L correctness (EXIT only)
            if marker_ok:
                side = p.get("side", "LONG")
                if side == "LONG":
                    expected_gross = (exit_val - entry) / entry * 100
                else:
                    expected_gross = (entry - exit_val) / entry * 100

                actual_gross = p.get("gross", 0)
                gross_ok = abs(expected_gross - actual_gross) < 0.001
                results.append(ValidationResult(
                    name="pnl_gross_correctness",
                    passed=gross_ok,
                    detail=f"Expected: {round(expected_gross, 4)}, Got: {actual_gross}"
                    if not gross_ok else "OK"
                ))

                # Net = gross - fee - slip
                actual_net = p.get("net", 0)
                fee = p.get("fee", 0)
                slip = p.get("slip", 0)
                expected_net = actual_gross - fee - slip
                net_ok = abs(expected_net - actual_net) < 0.001
                results.append(ValidationResult(
                    name="pnl_net_correctness",
                    passed=net_ok,
                    detail=f"Expected: {round(expected_net, 4)}, Got: {actual_net}"
                    if not net_ok else "OK"
                ))

                # Result consistency
                result = p.get("result")
                if actual_net > 0:
                    result_ok = result == "WIN"
                elif actual_net < 0:
                    result_ok = result == "LOSS"
                else:
                    result_ok = result == "BREAKEVEN"
                results.append(ValidationResult(
                    name="result_consistency",
                    passed=result_ok,
                    detail=f"Net={actual_net}, Result={result}"
                    if not result_ok else "OK"
                ))

            # 4. Fee consistency
            fee_val = p.get("fee", 0)
            fee_ok = fee_val in (FEE_MAKER, FEE_TAKER)
            results.append(ValidationResult(
                name="fee_consistency",
                passed=fee_ok,
                detail=f"Fee={fee_val}" if not fee_ok else "OK"
            ))

            # 5. Slip consistency
            slip_val = p.get("slip", 0)
            slip_ok = abs(slip_val - SLIP_ESTIMATE) < 0.001
            results.append(ValidationResult(
                name="slip_consistency",
                passed=slip_ok,
                detail=f"Slip={slip_val}, Expected={SLIP_ESTIMATE}"
                if not slip_ok else "OK"
            ))

        return results

    def validate_adverse_first(
        self, markers: list[Any]
    ) -> list[ValidationResult]:
        """
        Validate adverse-first principle across a batch of markers.

        If both SL and TP exit markers exist for the same clone
        on the same timestamp, SL must be the one recorded (not TP).
        """
        results: list[ValidationResult] = []
        if len(markers) < 2:
            return results

        # Group by (ts, clone)
        groups: dict[tuple, list] = {}
        for m in markers:
            p = m.payload if hasattr(m, 'payload') else m
            key = (p.get("ts"), p.get("clone"))
            groups.setdefault(key, []).append(p)

        violations = 0
        for key, group in groups.items():
            sl_exits = [g for g in group if g.get("kind") == "EXIT" and g.get("reason") == "SL"]
            tp_exits = [g for g in group if g.get("kind") == "EXIT" and g.get("reason") == "TP"]
            if sl_exits and tp_exits:
                violations += 1

        results.append(ValidationResult(
            name="adverse_first",
            passed=violations == 0,
            detail=f"{violations} SL+TP conflicts found"
            if violations else "No SL+TP conflicts"
        ))

        return results
