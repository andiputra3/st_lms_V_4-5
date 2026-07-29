"""
ST-LMS v3 — Shared Constants
Foundation Core — Phase 1

All layers MUST import constants from here.
No layer may hardcode values.
Reference: MASTER_SPECIFICATION.html S2-S5, CONFIG bounded registry.
"""

# ── Supertrend ─────────────────────────────────────────────────
ST_MULTIPLIER: float = 3.0

# ── Indicator Periods ──────────────────────────────────────────
ATR_PERIOD: int = 10
EMA_PERIOD: int = 14
EMA_FAST: int = 12
EMA_SLOW: int = 26
MACD_SIGNAL: int = 9
RSI_PERIOD: int = 10
WPR_PERIOD: int = 14

# ── Bounded Parameters (defaults) ──────────────────────────────
ENTRY_OFFSET_BASE_K: float = 1.0
ENTRY_OFFSET_MIN_ATR: float = 0.15
ENTRY_OFFSET_MAX_CAP_PCT: float = 0.30
WPR_VELOCITY_DEADZONE: int = 5
WPR_ACCEL_DEADZONE: int = 8
GRID_MIN_NET_PCT_OF_FILL: float = 0.50
CAGE_TIGHT_ATR: float = 2.0
CAGE_LOOSE_ATR: float = 4.0
CAGE_WALL_MIN_DISTANCE_ATR: float = 0.25
WRONG_ENTRY_PCT: float = 2.0
FEE_SAFETY_BUFFER_PCT: float = 0.10
FEE_DISCOUNT_PCT: float = 0.0
GRID_BUY_ZONE_MAX: float = 0.30
GRID_SELL_ZONE_MIN: float = 0.70
GRID_MAX_FILLS_PER_SIDE: int = 2
TP_ATR_MULT: float = 2.0
TRAIL_ATR_MULT: float = 1.5
TRAIL_ACTIVATE_R: float = 1.0
PARTIAL_TP_PCT: float = 0.5
TIME_EXIT_CANDLES: int = 40
SAMPLE_GATE: int = 30
ST_DIST_VOL_WINDOW: int = 96

# ── Fee ────────────────────────────────────────────────────────
REQUIRED_MOVE: float = 0.7
FEE_MAKER: float = 0.04
FEE_MIXED: float = 0.07
FEE_TAKER: float = 0.10
SLIP_ESTIMATE: float = 0.05

# ── Assets ─────────────────────────────────────────────────────
ASSETS: dict = {
    "BTCUSDT": {"base": 61750.0, "tick": 0.1, "prec": 1},
    "SOLUSDT": {"base": 71.84, "tick": 0.01, "prec": 2},
    "AKEUSDT": {"base": 0.0031760, "tick": 0.0000001, "prec": 7},
    "TLMUSDT": {"base": 0.004043, "tick": 0.0000001, "prec": 7},
}

# ── Bounded Registry (24 parameters) ───────────────────────────
BOUNDED_REGISTRY: dict = {
    "ENTRY_OFFSET_BASE_K":     [1.0, 0.3, 3.0],
    "ENTRY_OFFSET_MIN_ATR":    [0.15, 0.05, 0.5],
    "ENTRY_OFFSET_MAX_CAP_PCT":[0.30, 0.10, 1.0],
    "WPR_VELOCITY_DEADZONE":   [5, 1, 20],
    "WPR_ACCEL_DEADZONE":      [8, 2, 40],
    "GRID_MIN_NET_PCT_OF_FILL":[0.50, 0.20, 1.5],
    "CAGE_TIGHT_ATR":          [2.0, 1.0, 4.0],
    "CAGE_LOOSE_ATR":          [4.0, 2.0, 8.0],
    "CAGE_WALL_MIN_DISTANCE_ATR":[0.25, 0.10, 0.50],
    "WRONG_ENTRY_PCT":         [2.0, 0.5, 6.0],
    "FEE_SAFETY_BUFFER_PCT":   [0.10, 0.0, 0.5],
    "FEE_DISCOUNT_PCT":        [0.0, 0.0, 0.25],
    "GRID_BUY_ZONE_MAX":       [0.30, 0.10, 0.45],
    "GRID_SELL_ZONE_MIN":      [0.70, 0.55, 0.90],
    "GRID_MAX_FILLS_PER_SIDE": [2, 1, 4],
    "TP_ATR_MULT":             [2.0, 1.0, 5.0],
    "TRAIL_ATR_MULT":          [1.5, 0.5, 4.0],
    "TRAIL_ACTIVATE_R":        [1.0, 0.5, 3.0],
    "PARTIAL_TP_PCT":          [0.5, 0.0, 0.8],
    "TIME_EXIT_CANDLES":       [40, 5, 200],
    "SAMPLE_GATE":             [30, 10, 200],
    "ST_DIST_VOL_WINDOW":      [96, 24, 240],
}

# ── Wave to MTF Mapping ────────────────────────────────────────
WAVE_MTF_TABLE: dict = {
    "STRONG_ACCUMULATION":   ("BULLISH_TREND", 8500),
    "STRONG_DISTRIBUTION":   ("BEARISH_TREND", 8500),
    "CONTINUATION_UP":       ("BULLISH_TREND", 7000),
    "CONTINUATION_DOWN":     ("BEARISH_TREND", 7000),
    "CONFIRMED_RANGE":       ("RANGE", 7500),
    "RANGE_EXPANDING":       ("RANGE", 6500),
    "RANGE_COMPRESSING":     ("COMPRESSION", 7000),
    "REVERSAL_UP":           ("REVERSAL_UP", 6500),
    "REVERSAL_DOWN":         ("REVERSAL_DOWN", 6500),
    "EXHAUSTION_UP":         ("EXHAUSTION", 5500),
    "EXHAUSTION_DOWN":       ("EXHAUSTION", 5500),
    "SIDEWAY":               ("RANGE", 7000),
    "CHAOS":                 ("CHAOS", 3000),
}

# ── Oracle Vector Dimensions ───────────────────────────────────
ORACLE_VECTOR_SIZE: int = 9

# ── Pipeline ───────────────────────────────────────────────────
PIPELINE_STAGES: int = 22
SHARED_STAGES: tuple = (1, 2, 3, 4)
PER_CLONE_STAGES: tuple = (5, 6, 7, 8, 9, 10, 11)
SHARED_AGAIN_STAGES: tuple = (12, 13, 14, 16, 17, 18, 19, 20, 21, 22)
ON_DEMAND_STAGES: tuple = (15,)

# ── Time ───────────────────────────────────────────────────────
WIB_OFFSET_SECONDS: int = 7 * 3600
MS_PER_MINUTE: int = 60000

# ── Limits ─────────────────────────────────────────────────────
MAX_CARDS_IN_MEMORY: int = 10000
MAX_MARKERS_IN_MEMORY: int = 5000
MAX_SNAPSHOTS_IN_MEMORY: int = 5000
ORACLE_HISTORY_MAX: int = 600
CHRONICLE_MAX: int = 6000
QUERY_RESULT_LIMIT: int = 10000
QUERY_TIMEOUT_MS: int = 30000
WORKER_TIMEOUT_MS: int = 120000
