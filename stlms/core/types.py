"""
ST-LMS v3 — Shared Types
Foundation Core — Phase 1

All layers MUST use these types.
No layer may define its own equivalent types.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional, Any

# ── Enums ──────────────────────────────────────────────────────

class DataStatus(str, Enum):
    OK = "ok"
    WARMUP = "warmup"
    PROVISIONAL = "provisional"
    INSUFFICIENT = "insufficient"
    GAP = "gap"
    INVALID = "invalid"

class PointStatus(str, Enum):
    WARMUP = "WARMUP"
    VALID = "VALID"

class SampleStatus(str, Enum):
    CUKUP = "CUKUP"
    BELUM_CUKUP = "BELUM_CUKUP"

class TradeKind(str, Enum):
    ENTRY = "ENTRY"
    EXIT = "EXIT"
    PARTIAL = "PARTIAL"
    BREAKEVEN = "BREAKEVEN"
    TRAILING = "TRAILING"
    HOLD = "HOLD"
    PASS = "PASS"
    NO_TRADE = "NO_TRADE"

class TradeSide(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"
    GRID = "GRID"

class TradeResult(str, Enum):
    WIN = "WIN"
    LOSS = "LOSS"
    BREAKEVEN = "BREAKEVEN"
    OPEN = "OPEN"
    PASS = "PASS"
    NA = "NA"

class PositionStatus(str, Enum):
    OPEN = "OPEN"
    HOLD = "HOLD"
    CLOSED = "CLOSED"
    BREAKEVEN = "BREAKEVEN"
    TRAILING = "TRAILING"
    PARTIAL = "PARTIAL"

class CloneKind(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"
    GRID = "GRID"

class BagKind(str, Enum):
    BEHAVIOR = "behavior"
    MARKET = "market"
    ENTRY = "entry"
    EXIT = "exit"
    RISK = "risk"
    KNOWLEDGE = "knowledge"

class KnowledgeEntity(str, Enum):
    ACADEMY = "ACADEMY"
    RIVER = "RIVER"
    ORACLE = "ORACLE"
    HIVEMIND = "HIVEMIND"
    DARWIN = "DARWIN"
    LIBRARIAN = "LIBRARIAN"
    CERMIN = "CERMIN"

class SessionKind(str, Enum):
    BUILD = "build"
    SIMULATION = "simulation"
    REPLAY = "replay"
    BENCHMARK = "benchmark"
    ANALYSIS = "analysis"
    MANUAL = "manual"

class RunKind(str, Enum):
    COLLECTOR = "collector"
    SIMULATION = "simulation"
    REPLAY = "replay"
    BENCHMARK = "benchmark"
    AUDIT = "audit"
    BUILD = "build"

class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

class SupertrendColor(str, Enum):
    HIJAU = "HIJAU"
    MERAH = "MERAH"

class SupertrendDirection(int, Enum):
    UP = 1
    DOWN = -1

class LineRole(str, Enum):
    SUPPORT = "SUPPORT"
    RESISTANCE = "RESISTANCE"

class WaveStructure(str, Enum):
    STRONG_ACCUMULATION = "STRONG_ACCUMULATION"
    STRONG_DISTRIBUTION = "STRONG_DISTRIBUTION"
    CONTINUATION_UP = "CONTINUATION_UP"
    CONTINUATION_DOWN = "CONTINUATION_DOWN"
    CONFIRMED_RANGE = "CONFIRMED_RANGE"
    RANGE_EXPANDING = "RANGE_EXPANDING"
    RANGE_COMPRESSING = "RANGE_COMPRESSING"
    REVERSAL_UP = "REVERSAL_UP"
    REVERSAL_DOWN = "REVERSAL_DOWN"
    EXHAUSTION_UP = "EXHAUSTION_UP"
    EXHAUSTION_DOWN = "EXHAUSTION_DOWN"
    SIDEWAY = "SIDEWAY"
    CHAOS = "CHAOS"

class CageStatus(str, Enum):
    NONE = "NONE"
    VALID_COMPRESSION = "VALID_COMPRESSION"
    LOOSE_SIDEWAY = "LOOSE_SIDEWAY"

class CageBreakout(str, Enum):
    NONE = "NONE"
    IMMINENT_UP = "IMMINENT_UP"
    IMMINENT_DOWN = "IMMINENT_DOWN"
    SQUEEZE = "SQUEEZE"

class MarketPhase(str, Enum):
    UPTREND = "UPTREND"
    DOWNTREND = "DOWNTREND"
    TRANSITION = "TRANSITION"
    SIDEWAY_COMPRESSION = "SIDEWAY_COMPRESSION"

class ConsensusLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    NONE = "NONE"

class ConflictLevel(str, Enum):
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class LibrarianStatus(str, Enum):
    NEW = "NEW"
    OBSERVATION = "OBSERVATION"
    TRUSTED = "TRUSTED"
    MATURE = "MATURE"
    DEAD = "DEAD"
    DEPRECATED = "DEPRECATED"

class ReplayKind(str, Enum):
    CANDLE = "candle"
    SNAPSHOT = "snapshot"
    TRADE = "trade"
    CLONE = "clone"
    KNOWLEDGE = "knowledge"
    GOVERNANCE = "governance"

class BenchmarkRunKind(str, Enum):
    WASIT = "wasit"
    WALK_FORWARD = "walk_forward"
    CLONE = "clone"
    TRADE = "trade"
    MARKET = "market"

# ── Base Dataclasses ───────────────────────────────────────────

@dataclass
class Candle:
    time: int
    open: float
    high: float
    low: float
    close: float
    volume: float
    taker_buy_ratio: float

@dataclass
class MarketSnapshot:
    ts: int
    symbol: str
    timeframe: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    taker_buy_ratio: float
    data_status: DataStatus = DataStatus.OK
    gap_flag: bool = False
    wib_iso: str = ""

@dataclass
class BoundedParam:
    key: str
    current: float
    minimum: float
    maximum: float

@dataclass
class AuditEntry:
    domain: str
    audit_type: str
    severity: Severity
    title: str
    detail: str = ""
    status: str = "open"

@dataclass
class ValidationResult:
    name: str
    passed: bool
    detail: str = ""
