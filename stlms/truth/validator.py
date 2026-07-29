"""
=====================================================
MODULE:     truth_validator.py
PURPOSE:    Truth Validator — determinism, warmup, range.
=====================================================
"""

from ..core.utils import Card
from ..core.types import ValidationResult
from ..foundation.base_validator import BaseValidator


class TruthValidator(BaseValidator):
    """Validasi truth_snapshot cards."""
    
    def __init__(self):
        super().__init__("TRUTH")
    
    def validate(self, artifact) -> list[ValidationResult]:
        p = artifact.payload if hasattr(artifact, 'payload') else artifact
        results = []
        
        # WARMUP check — NULL values allowed during warmup
        status = p.get("point_status", "WARMUP")
        dist = p.get("dist")
        dist_atr = p.get("dist_atr")
        rsi = p.get("rsi")
        wpr = p.get("wpr")
        
        if status == "WARMUP":
            results.append(ValidationResult("warmup_nulls", dist is None or dist_atr is None,
                          "NULL during WARMUP" if dist is None else "dist not NULL during WARMUP"))
        else:
            results.append(ValidationResult("valid_has_indicators",
                          dist is not None and rsi is not None,
                          "All indicators present" if dist is not None else "Missing indicators"))
        
        # ST direction
        st_dir = p.get("st_dir")
        results.append(ValidationResult("st_dir_valid", st_dir in (1, -1),
                      f"st_dir={st_dir}" if st_dir in (1, -1) else f"Invalid st_dir={st_dir}"))
        
        # RSI range
        if rsi is not None:
            results.append(ValidationResult("rsi_range", 0 <= rsi <= 100,
                          f"RSI={rsi:.1f}"))
        
        # W%R range
        if wpr is not None:
            results.append(ValidationResult("wpr_range", -100 <= wpr <= 0,
                          f"W%R={wpr:.1f}"))
        
        return results
    
    def validate_determinism(self, cards1: list[Card], cards2: list[Card]) -> ValidationResult:
        """2-run determinism check."""
        if len(cards1) != len(cards2):
            return ValidationResult("determinism", False, f"Count mismatch: {len(cards1)} vs {len(cards2)}")
        for i, (c1, c2) in enumerate(zip(cards1, cards2)):
            if c1.checksum != c2.checksum:
                return ValidationResult("determinism", False, f"Mismatch at index {i}")
        return ValidationResult("determinism", True, f"{len(cards1)} cards identical")
