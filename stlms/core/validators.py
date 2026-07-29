"""
ST-LMS v3 — Shared Validators
Foundation Core — Phase 1
"""

from typing import Any, Optional
from .constants import BOUNDED_REGISTRY, ASSETS

def validate_bounded(key: str, value: float) -> tuple[bool, str]:
    """Validate value against BOUNDED registry. Reference: LAW-MASTER-14."""
    if key not in BOUNDED_REGISTRY:
        return False, f"UNKNOWN_PARAM: {key}"
    default, lo, hi = BOUNDED_REGISTRY[key]
    if not (lo <= value <= hi):
        return False, f"OUT_OF_RANGE: {key}={value}, range=[{lo}, {hi}]"
    return True, "OK"

def validate_symbol(symbol: str) -> bool:
    return symbol in ASSETS

def validate_candle(open_p: float, high: float, low: float, close: float, volume: float) -> tuple[bool, str]:
    """Validate candle hygiene. Reference: MARKET.hygiene."""
    if high < max(open_p, close):
        return False, "high < max(open, close)"
    if low > min(open_p, close):
        return False, "low > min(open, close)"
    if high < low:
        return False, "high < low"
    if volume < 0:
        return False, "volume < 0"
    return True, "OK"

def validate_timestamp_sequence(timestamps: list[int], expected_interval_ms: int = 60000) -> list[int]:
    """Detect gaps in timestamp sequence. Returns list of gap timestamps."""
    gaps = []
    for i in range(1, len(timestamps)):
        if timestamps[i] - timestamps[i-1] > expected_interval_ms:
            gaps.append(timestamps[i])
    return gaps

def validate_sample_gate(sample_count: int, gate: int = 30) -> tuple[bool, str]:
    """Check sample gate. Reference: LAW-MASTER-12."""
    if sample_count >= gate:
        return True, "CUKUP"
    return False, "BELUM_CUKUP"

def validate_confidence_range(score: float, lo: float = 0.0, hi: float = 10000.0) -> bool:
    return lo <= score <= hi

def validate_win_rate(wr: Optional[float]) -> bool:
    if wr is None:
        return True
    return 0.0 <= wr <= 100.0
