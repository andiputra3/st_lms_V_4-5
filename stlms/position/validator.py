"""
=====================================================
MODULE:     position_validator.py
PURPOSE:    Position Validator — validasi MAE/MFE tracking,
            hold counter, position state integrity.
OWNER:      PHASE-11 POSITION LAYER
INPUT:      position_snapshot cards
OUTPUT:     ValidationResult list
DEPENDENCY: stlms.foundation.base_validator (BaseValidator)
ARCHITECTURE:
            Validator memeriksa setiap position_snapshot card.
            MAE/MFE: MAE <= 0, MFE >= 0, values monotonik.
            Hold counter: meningkat per snapshot.
            State: status sesuai kondisi posisi.
=====================================================
"""

from typing import Any
from ..core.utils import Card
from ..core.types import ValidationResult
from ..foundation.base_validator import BaseValidator


class PositionValidator(BaseValidator):
    """
    Validasi position_snapshot cards.

    Checks:
        1. MAE/MFE sign consistency: MAE <= 0, MFE >= 0
        2. Hold counter: hold_c >= 0, monotonically increasing
        3. Price sanity: entry_price > 0, sl and tp defined
        4. Position state: status is a valid state string
    """

    VALID_STATUSES = {"OPEN", "HOLD", "CLOSED", "BREAKEVEN", "TRAILING", "PARTIAL"}

    def __init__(self):
        super().__init__("POSITION")

    def validate(self, artifact: Any) -> list[ValidationResult]:
        """
        Validate one position_snapshot artifact.

        Returns:
            List of ValidationResult — PASS/FAIL per check.
        """
        results: list[ValidationResult] = []
        p = artifact.payload if hasattr(artifact, 'payload') else artifact

        # 1. Required fields
        required = ["side", "entry_price", "sl", "tp", "mae", "mfe", "hold_c", "status"]
        missing = [f for f in required if f not in p or p[f] is None]
        results.append(ValidationResult(
            name="required_fields",
            passed=len(missing) == 0,
            detail=f"Missing: {missing}" if missing else "All present"
        ))

        # 2. Price sanity
        entry = p.get("entry_price", 0)
        sl = p.get("sl", 0)
        tp = p.get("tp", 0)
        price_ok = entry > 0 and sl > 0 and tp > 0
        results.append(ValidationResult(
            name="price_sanity",
            passed=price_ok,
            detail="OK" if price_ok else "Non-positive price detected"
        ))

        # 3. SL/TP relative to entry (directional check)
        side = p.get("side")
        if side == "LONG":
            sl_tp_ok = sl < entry < tp
            detail = f"Expected SL({sl}) < Entry({entry}) < TP({tp})"
        elif side == "SHORT":
            sl_tp_ok = tp < entry < sl
            detail = f"Expected TP({tp}) < Entry({entry}) < SL({sl})"
        else:
            sl_tp_ok = True
            detail = "OK"

        results.append(ValidationResult(
            name="sl_tp_direction",
            passed=sl_tp_ok,
            detail=detail if not sl_tp_ok else "OK"
        ))

        # 4. MAE/MFE sign consistency
        mae = p.get("mae", 0)
        mfe = p.get("mfe", 0)
        sign_ok = mae <= 0 and mfe >= 0
        results.append(ValidationResult(
            name="mae_mfe_sign",
            passed=sign_ok,
            detail=f"MAE={mae}, MFE={mfe}" if not sign_ok else "OK"
        ))

        # 5. Hold counter
        hold_c = p.get("hold_c", 0)
        hold_ok = hold_c >= 0
        results.append(ValidationResult(
            name="hold_counter",
            passed=hold_ok,
            detail=f"hold_c={hold_c}" if not hold_ok else "OK"
        ))

        # 6. Status validity
        status = p.get("status", "")
        status_ok = status in self.VALID_STATUSES
        results.append(ValidationResult(
            name="status_validity",
            passed=status_ok,
            detail=f"Invalid status: {status}" if not status_ok else "OK"
        ))

        return results

    def validate_sequence(
        self, artifacts: list[Card], side: str
    ) -> list[ValidationResult]:
        """
        Validate MAE/MFE and hold_c monotonicity across a sequence
        of snapshots for the same position side.

        Args:
            artifacts: ordered list of position_snapshot Cards
            side: filter by side (LONG / SHORT)

        Returns:
            ValidationResult for monotonicity checks.
        """
        results: list[ValidationResult] = []
        filtered = [
            c for c in artifacts
            if c.payload.get("side") == side
        ]

        if len(filtered) < 2:
            return results

        # Hold counter monotonic
        hold_vals = [c.payload.get("hold_c", 0) for c in filtered]
        hold_monotonic = all(
            hold_vals[i] >= hold_vals[i - 1]
            for i in range(1, len(hold_vals))
        )
        results.append(ValidationResult(
            name="hold_monotonic",
            passed=hold_monotonic,
            detail="Hold counter increases monotonically"
            if hold_monotonic else "Hold counter decreased"
        ))

        # MAE should never increase (get less negative)
        mae_vals = [c.payload.get("mae", 0) for c in filtered]
        mae_monotonic = all(
            mae_vals[i] <= mae_vals[i - 1]
            for i in range(1, len(mae_vals))
        )
        results.append(ValidationResult(
            name="mae_monotonic",
            passed=mae_monotonic,
            detail="MAE is monotonic (non-increasing)"
            if mae_monotonic else "MAE increased (worsened less than prior max adverse)"
        ))

        # MFE should never decrease
        mfe_vals = [c.payload.get("mfe", 0) for c in filtered]
        mfe_monotonic = all(
            mfe_vals[i] >= mfe_vals[i - 1]
            for i in range(1, len(mfe_vals))
        )
        results.append(ValidationResult(
            name="mfe_monotonic",
            passed=mfe_monotonic,
            detail="MFE is monotonic (non-decreasing)"
            if mfe_monotonic else "MFE decreased"
        ))

        return results
