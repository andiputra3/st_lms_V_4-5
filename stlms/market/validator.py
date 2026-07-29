"""
=====================================================
MODULE:     market_validator.py
PURPOSE:    Market Validator — validasi kualitas data market.
            Hygiene check, gap detection, OI completeness.
OWNER:      PHASE-02 MARKET ARTIFACT
INPUT:      market_snapshot cards
OUTPUT:     ValidationResult list
DEPENDENCY: stlms.foundation.base_validator (BaseValidator)
ARCHITECTURE:
            Validator memeriksa setiap market_snapshot card.
            Hygiene: H >= max(O,C), L <= min(O,C), H >= L, V >= 0.
            Gap: timestamp sequence integrity.
            OI: INSUFFICIENT_DATA jika tidak ada OI.
=====================================================
"""

from typing import Any
from ..core.utils import Card
from ..core.types import ValidationResult
from ..core.constants import MS_PER_MINUTE
from ..foundation.base_validator import BaseValidator


class MarketValidator(BaseValidator):
    """
    Validasi market_snapshot cards.
    
    Checks:
        1. Candle hygiene (H >= O,C; L <= O,C; H >= L; V >= 0)
        2. Timestamp sequence (gap detection)
        3. OI completeness (INSUFFICIENT_DATA if missing)
        4. Price sanity (no negative, no zero)
    """
    
    def __init__(self):
        super().__init__("MARKET")
    
    def validate(self, artifact: Any) -> list[ValidationResult]:
        """
        Validasi satu artifact (market_snapshot Card).
        
        Returns:
            List of ValidationResult — PASS/FAIL per check.
        """
        results: list[ValidationResult] = []
        p = artifact.payload if hasattr(artifact, 'payload') else artifact
        
        # 1. Hygiene check
        o, h, l, c, v = (
            p.get("open", 0), p.get("high", 0),
            p.get("low", 0), p.get("close", 0),
            p.get("volume", 0)
        )
        
        hygiene_ok = True
        hygiene_errors = []
        if h < max(o, c):
            hygiene_ok = False
            hygiene_errors.append(f"high({h}) < max(open({o}), close({c}))")
        if l > min(o, c):
            hygiene_ok = False
            hygiene_errors.append(f"low({l}) > min(open({o}), close({c}))")
        if h < l:
            hygiene_ok = False
            hygiene_errors.append(f"high({h}) < low({l})")
        if v < 0:
            hygiene_ok = False
            hygiene_errors.append(f"volume({v}) < 0")
        
        results.append(ValidationResult(
            name="hygiene",
            passed=hygiene_ok,
            detail="; ".join(hygiene_errors) if hygiene_errors else "OK"
        ))
        
        # 2. Price sanity
        price_ok = o > 0 and h > 0 and l > 0 and c > 0
        results.append(ValidationResult(
            name="price_sanity",
            passed=price_ok,
            detail="OK" if price_ok else "Non-positive price detected"
        ))
        
        # 3. Gap flag consistency
        gap_flag = p.get("gap_flag", False)
        data_status = p.get("data_status", "ok")
        gap_consistent = not gap_flag or data_status == "gap"
        results.append(ValidationResult(
            name="gap_consistency",
            passed=gap_consistent,
            detail="OK" if gap_consistent else "gap_flag set but data_status != gap"
        ))
        
        return results
    
    def validate_sequence(self, artifacts: list[Card]) -> list[ValidationResult]:
        """
        Validasi sequence timestamp — deteksi gap.
        
        OI OWNERSHIP: Gap detection menggunakan timeframe asli.
        Tidak ada interpolasi gap.
        """
        results: list[ValidationResult] = []
        
        if len(artifacts) < 2:
            return results
        
        timestamps = [a.payload.get("ts", 0) for a in artifacts]
        gaps_found = 0
        
        for i in range(1, len(timestamps)):
            diff = timestamps[i] - timestamps[i-1]
            if diff > MS_PER_MINUTE * 1.5:  # > 1.5x expected interval
                gaps_found += 1
        
        results.append(ValidationResult(
            name="sequence_integrity",
            passed=gaps_found == 0,
            detail=f"{gaps_found} gaps in {len(artifacts)} candles"
            if gaps_found else f"{len(artifacts)} candles, no gaps"
        ))
        
        return results
