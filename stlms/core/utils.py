"""
ST-LMS v3 — Shared Utilities
Foundation Core — Phase 1

Math, hashing, PRNG, WIB, canonical, tick conversion.
Reference: MASTER_SPECIFICATION.html LAW-MASTER-01 (Determinism), LAW-MASTER-03 (Immutability)
"""

import math
import hashlib
import struct
from datetime import datetime, timezone, timedelta
from typing import Optional
from .constants import WIB_OFFSET_SECONDS

# ── Math ───────────────────────────────────────────────────────

def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))

def norm01(value: float, lo: float, hi: float) -> float:
    denom = (hi - lo) or 1.0
    return clamp((value - lo) / denom, 0.0, 1.0)

def round_prec(value: float, prec: int) -> float:
    factor = 10.0 ** prec
    return round(value * factor) / factor

def canon(value: float, prec: int) -> str:
    return f"{value:.{prec}f}"

# ── Tick ───────────────────────────────────────────────────────

def to_tick(value: float, tick_size: float) -> int:
    return round(value / tick_size)

def from_tick(ticks: int, tick_size: float) -> float:
    return ticks * tick_size

# ── Hash ───────────────────────────────────────────────────────

def sha256(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()

def sha256_short(data: str, length: int = 8) -> str:
    return sha256(data)[:length].upper()

# ── PRNG (Mulberry32 — deterministic, seeded) ──────────────────

def mulberry32(seed: int) -> float:
    """Deterministic PRNG. Same seed = same sequence. Reference: LAW-MASTER-01."""
    seed = (seed & 0xFFFFFFFF)
    seed = (seed + 0x6D2B79F5) & 0xFFFFFFFF
    t = (seed ^ (seed >> 15)) & 0xFFFFFFFF
    t = (t * (1 | t)) & 0xFFFFFFFF
    t = (t ^ (t >> 7)) & 0xFFFFFFFF
    t = (t * (61 | t)) & 0xFFFFFFFF
    t = (t ^ (t >> 14)) & 0xFFFFFFFF
    return t / 4294967296.0

def seed_from_string(s: str) -> int:
    h = 2166136261
    for ch in s:
        h = ((h ^ ord(ch)) * 16777619) & 0xFFFFFFFF
    return h

class PRNG:
    def __init__(self, seed: int):
        self._state = seed & 0xFFFFFFFF

    def next(self) -> float:
        self._state = (self._state + 0x6D2B79F5) & 0xFFFFFFFF
        t = (self._state ^ (self._state >> 15)) & 0xFFFFFFFF
        t = (t * (1 | t)) & 0xFFFFFFFF
        t = (t ^ (t >> 7)) & 0xFFFFFFFF
        t = (t * (61 | t)) & 0xFFFFFFFF
        t = (t ^ (t >> 14)) & 0xFFFFFFFF
        return t / 4294967296.0

# ── WIB ────────────────────────────────────────────────────────

WIB = timezone(timedelta(seconds=WIB_OFFSET_SECONDS))

def wib_now() -> datetime:
    return datetime.now(WIB)

def wib_iso(ts_ms: int) -> str:
    dt = datetime.fromtimestamp(ts_ms / 1000.0, tz=WIB)
    return dt.isoformat()

def wib_ymd(ts_ms: int) -> str:
    dt = datetime.fromtimestamp(ts_ms / 1000.0, tz=WIB)
    return dt.strftime("%Y%m%d")

def wib_hhmm(ts_ms: int) -> str:
    dt = datetime.fromtimestamp(ts_ms / 1000.0, tz=WIB)
    return dt.strftime("%H%M")

# ── ID Generation (Deterministic) ──────────────────────────────

class IDGenerator:
    """Deterministic ID: YYYYMMDD_HHMM_COMP_FILE_SEQ_HEX. Reference: LAW-MASTER-03."""

    def __init__(self):
        self._seq: dict = {}

    def generate(self, ts_ms: int, component: str, source_file: str, payload: str = "") -> str:
        ymd = wib_ymd(ts_ms)
        hhmm = wib_hhmm(ts_ms)
        key = f"{component}|{source_file}|{ymd}_{hhmm}"
        self._seq[key] = self._seq.get(key, 0) + 1
        seq = self._seq[key]
        seed_data = f"{component}|{source_file}|{ts_ms}|{seq}|{payload}"
        hex_suffix = sha256_short(seed_data, 8)
        return f"{ymd}_{hhmm}_{component}_{source_file}_{seq:06d}_{hex_suffix}"

    def reset(self) -> None:
        self._seq.clear()

# ── Card ────────────────────────────────────────────────────────

class Card:
    """Immutable card. Reference: LAW-MASTER-03 (Immutability), LAW-MASTER-16 (Snapshot)."""

    def __init__(self, entity_type: str, payload: dict, dependencies: list,
                 ts_ms: int, id_gen: IDGenerator):
        component = entity_type.upper().replace(" ", "_")[:12]
        self.entity_id = id_gen.generate(ts_ms, component, "OS", str(payload))
        self.entity_type = entity_type
        self.entity_state = "CREATED"
        self.entity_version = "1.0"
        self.timestamp_wib = wib_iso(ts_ms)
        self.timestamp_ms = ts_ms
        self.component_name = component
        self.source_file = "OS"
        self.dependencies = tuple(sorted(dependencies))
        self.payload = payload
        self.checksum = self._compute_checksum()

    def _compute_checksum(self) -> str:
        canonical = f"t:{self.entity_type}|v:{self.entity_version}|d:{sorted(self.dependencies)}|p:{self.payload}"
        return sha256(canonical)

    def verify(self) -> bool:
        return self.checksum == self._compute_checksum()

    def to_dict(self) -> dict:
        return {
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "entity_state": self.entity_state,
            "entity_version": self.entity_version,
            "timestamp_wib": self.timestamp_wib,
            "timestamp_ms": self.timestamp_ms,
            "component_name": self.component_name,
            "source_file": self.source_file,
            "dependencies": list(self.dependencies),
            "payload": self.payload,
            "checksum": self.checksum,
        }
