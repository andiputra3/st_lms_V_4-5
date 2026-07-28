# TRUTH LAYER FREEZE — ST-LMS v3

## Native HTML Market Geometry Intelligence Operating System

**Date:** 2026-07-28
**Phase:** PHASE 0 — Prompt 03
**Status:** CONSTITUTIONALLY FROZEN
**Sources:** MASTER_SPECIFICATION.html §4, DOCUMENT_DEPENDENCY.html, QWEN_14_DOC.html, ST_LMS_CORE.js (TRUTH namespace)

---

## 1. TRUTH LAYER ARCHITECTURE

### 1.1 Position in Pipeline

```
MARKET (market_snapshot)
  │
  ▼
┌──────────────────────────────────────────────────────────────────┐
│                         TRUTH LAYER                               │
│                     (Stage 3 — SHARED, 1×)                        │
│                                                                    │
│  Point Builder ──▶ Line Builder ──▶ Slope Builder ──▶ Wave Builder│
│       │                                                  │        │
│       │              ┌──────────────────────────────────┘        │
│       │              ▼                                            │
│       │        Cage Engine ──▶ Phase Engine                       │
│       │              │              │                             │
│       │              ├──────────────┤                             │
│       │              ▼              ▼                             │
│       │        Distance Engine  Nearest Engine                    │
│       │              │              │                             │
│       └──────────────┴──────────────┘                             │
│                      │                                            │
│                      ▼                                            │
│               truth_snapshot                                      │
└──────────────────────────────────────────────────────────────────┘
  │
  ▼
STRUCTURE (structure_snapshot) + EVIDENCE (evidence_snapshot)
```

### 1.2 Truth Pipeline Detail

```
POINT BUILDER
  Input: market_snapshot + checkpoint (previous candle state)
  Output: truth_point per candle
  Computes: st, stDir, color, atr, ema, ema12, ema26, macd, macd_signal,
            macd_hist, rsi, wpr, vel, acc, dist, distAtr, volDelta, flip

LINE BUILDER
  Input: truth_points (array)
  Output: lines (segments where ST value is constant, n ≥ 4)
  Each line: {st, key, mem, cols, s, e, n, dom, role, green, red, flip}

SLOPE BUILDER
  Input: truth_points + lines
  Output: slopes (transitions between lines, non-line-member points)
  Each slope: {s, e, dir, col, n, pat, stf}
  Patterns: STAIRCASE_UP/DOWN, PARABOLIC_UP/DOWN, REVERSAL_TRANSITION,
            SPIKE_UP/DOWN, FLAT_NOISE

WAVE BUILDER
  Input: lines + slopes
  Output: waves (groups of 6 lines + transitions between them)
  Each wave: {mem (6 lines), trans (5 slopes), s, e, structure, status}
  Structures (13): STRONG_ACCUMULATION, STRONG_DISTRIBUTION,
    CONTINUATION_UP, CONTINUATION_DOWN, CONFIRMED_RANGE,
    RANGE_EXPANDING, RANGE_COMPRESSING, REVERSAL_UP, REVERSAL_DOWN,
    EXHAUSTION_UP, EXHAUSTION_DOWN, SIDEWAY, CHAOS
  Status: CLOSED_WAVE (6 lines) / PENDING_WAVE (< 6 lines)

CAGE ENGINE
  Input: lineage_lines + price + atr + current_line_run
  Output: cage {upper, lower, pp, rangeAtr, status, breakout,
                upVi, lowVi, cross, pressureUp, pressureDn, versioning}
  Resolves: support wall + resistance wall with versioning (v0→v1→v2)
  Escape path: finds "comfortable" wall (distance ≥ threshold × ATR)
  Status: NONE (1 wall) / VALID_COMPRESSION (tight, 2 walls) /
          LOOSE_SIDEWAY (wide, 2 walls)
  Breakout: NONE / IMMINENT_UP / IMMINENT_DOWN / SQUEEZE

PHASE ENGINE
  Input: cage + wave + stDir
  Output: market_phase {cage_status, wave_structure, stDir, phase}
  Phase: UPTREND / DOWNTREND / TRANSITION / SIDEWAY_COMPRESSION

DISTANCE ENGINE
  Input: close + cage.upper + cage.lower
  Output: dist_ceiling (ceiling - close), dist_floor (close - floor)
  NULL on trend with missing opposite wall

NEAREST ENGINE
  Input: lines + price
  Output: nearest_support, nearest_resistance
  Finds closest support and resistance lines from all FINAL lines
```

---

## 2. TRUTH LAYER RESPONSIBILITIES

### 2.1 Core Responsibilities

| Responsibility | Description |
|---------------|-------------|
| Geometry Computation | Compute all market geometry primitives (st, atr, ema, macd, rsi, wpr) |
| Single Source of Truth | Truth is the ONLY source for all geometry; no other layer recomputes from OHLCV |
| Warmup Management | Track warmup state; return NULL+status during warmup |
| Flip Detection | Detect trend flip events (TREND_FLIP_UP/DOWN) |
| Point Status | Mark each candle as WARMUP or VALID |
| Card Sharing | truth_snapshot is shared to Structure and Evidence (not recomputed) |

### 2.2 What Truth Layer MUST NOT Do

| Forbidden | Reason |
|-----------|--------|
| Compute structure/cage | That's STRUCTURE's job |
| Use indicators for decisions | Truth is blind to indicators per LAW-MASTER-15 |
| Write to Structure or Evidence | Unidirectional flow |
| Return neutral values during warmup | NULL+status per LAW-MASTER-02 |
| Use Date.now() or Math.random() | Determinism per LAW-MASTER-01 |
| Depend on Evidence or Structure | Truth is upstream; must not read downstream |

---

## 3. TRUTH LAYER CONTRACTS

### 3.1 Point Builder Contract

```
COMPONENT: STLMS.TRUTH.PointBuilder
NAMESPACE: STLMS.TRUTH
FILE: ST_LMS_CORE.js (lines 154-185)

STATE (per symbol, contiguous):
  pc: previous close
  atr: average true range (period 10)
  ema: exponential moving average (period 14)
  e12: EMA 12 (for MACD)
  e26: EMA 26 (for MACD)
  sig: MACD signal line (period 9)
  puf: previous upper band (Supertrend)
  plf: previous lower band (Supertrend)
  trend: current trend direction (1 or -1)
  ag: average gain (for RSI)
  al: average loss (for RSI)
  hs: high history (for W%R, last 14)
  ls: low history (for W%R, last 14)
  wp1: previous W%R (for velocity)
  vp: previous velocity (for acceleration)
  mh1: previous MACD histogram (for signal)

BUILD(sym):
  1. Validate candle hygiene
  2. Compute TR = max(H-L, |H-pc|, |L-pc|)
  3. Update ATR: atr + (TR - atr) / ATR_P  (ATR_P = 10)
  4. Update EMA: ema + (close - ema) × 2/(EMA_P+1)  (EMA_P = 14)
  5. Update EMA12/EMA26 for MACD
  6. Compute MACD = e12 - e26; signal = sig + (macd - sig) × 2/10
  7. Compute Supertrend bands: ub = hl2 + atr×ST_MUL, lb = hl2 - atr×ST_MUL
  8. Apply band continuation logic (uf/lf)
  9. Detect trend flip: cl > puf → TREND_FLIP_UP; cl < plf → TREND_FLIP_DOWN
  10. Compute st = trend===1 ? lf : uf
  11. Determine color: cl > st → HIJAU; cl < st → MERAH; else follow trend
  12. Compute RSI: ag/al smoothed over ATR_P; RSI = 100 - 100/(1 + ag/al)
  13. Compute W%R: (hh - cl) / (hh - ll) × -100  (14-period)
  14. Compute velocity: wpr - wp1
  15. Compute acceleration: vel - vp
  16. Compute dist = |cl - st|; distAtr = dist / atr
  17. Compute volDelta = 2 × takerBuyRatio - 1
  18. Set point_status: WARMUP (atr==null || ema==null) / VALID

OUTPUT truth_point:
  {ts, close, st, st_canon, st_tick, stDir, color, atr, ema,
   macdHist, prevMacdHist, dist, distAtr, rsi, wpr, vel, acc,
   volDelta, emaSlope, flip, point_status}
```

### 3.2 Line Builder Contract

```
COMPONENT: STLMS.STRUCTURE.LineBuilder (runs in Truth pipeline)
INPUT: truth_points (array of {ts, st, st_canon, color})
OUTPUT: lines (array of line segments)

ALGORITHM:
  1. Iterate through points
  2. Group consecutive points with same st_canon value
  3. A line is formed when st_canon is constant for ≥ 4 candles
  4. Track: start ts, end ts, member timestamps, colors per member
  5. Classify: dom = majority color (HIJAU/MERAH)
  6. Assign: role = SUPPORT (dom=HIJAU) / RESISTANCE (dom=MERAH)

LINE OBJECT:
  {st, stf, key, s, e, n, dom, role, green, red, flip}

CONTRACT:
  - st: Supertrend value (price level)
  - stf: final st value (same as st, used for lineage)
  - key: st_canon (canonical string representation)
  - s: start timestamp (first member)
  - e: end timestamp (last member)
  - n: number of members (≥ 4)
  - dom: dominant color (HIJAU/MERAH)
  - role: SUPPORT (HIJAU-dominant) / RESISTANCE (MERAH-dominant)
  - green: count of HIJAU members
  - red: count of MERAH members
  - flip: min(green, red) — measure of contention
```

### 3.3 Wave Builder Contract

```
COMPONENT: STLMS.STRUCTURE.WaveBuilder (runs in Truth pipeline)
INPUT: lines (sorted by start ts), slopes
OUTPUT: waves + pending

ALGORITHM:
  1. Sort lines by start timestamp
  2. Group into chunks of 6 consecutive lines
  3. For each chunk of 6 lines:
     a. Classify structure via cls() function
     b. Find transitions (slopes) between consecutive lines
     c. Create CLOSED_WAVE
  4. If last chunk < 6 lines → PENDING_WAVE

CLASSIFICATION (cls function, 13 structures):
  g = count of HIJAU-dominant lines
  r = count of MERAH-dominant lines
  alt = number of color alternations

  STRONG_ACCUMULATION:   g ≥ 5
  STRONG_DISTRIBUTION:   r ≥ 5
  REVERSAL_UP:           first 3 = MERAH, last = HIJAU
  REVERSAL_DOWN:         first 3 = HIJAU, last = MERAH
  EXHAUSTION_UP:         g ≥ 4, last = MERAH
  EXHAUSTION_DOWN:       r ≥ 4, last = HIJAU
  CONFIRMED_RANGE:       alt ≥ 4
  CONTINUATION_UP:       g ≥ 3, r = 0
  CONTINUATION_DOWN:     r ≥ 3, g = 0
  SIDEWAY:               g ≥ 2, r ≥ 2
  CHAOS:                 default (fallback)

CONTRACT:
  - Wave < 6 lines → PENDING_WAVE (no padding)
  - 13 structures exactly (all reachable post C2 fix)
  - Transition slopes between consecutive lines
```

### 3.4 Cage Engine Contract

```
COMPONENT: STLMS.STRUCTURE.CageEngine (runs in Truth pipeline)
INPUT: lineage_lines, price, atr, curLineRun
OUTPUT: cage object

WALL RESOLUTION (_resolve method):
  1. Collect candidate walls for given side (SUP/RES)
  2. Include current line run if active
  3. Include lineage lines (FINAL status)
  4. Check if price has broken through (broken = price crossed line)
  5. Filter broken walls → broken_count, broken_sts
  6. Sort remaining by recency (most recent first)
  7. Take top 3 as versions (v0, v1, v2)
  8. Escape path: find first wall with distance ≥ CAGE_WALL_MIN_DISTANCE_ATR × ATR
  9. Mark tight walls (distance < threshold)
  10. pressure = all candidates tight and no comfortable wall found

CAGE COMPUTATION:
  1. Resolve support wall → sup (with versioning)
  2. Resolve resistance wall → res (with versioning)
  3. If either wall missing → cage NONE
  4. Both walls present:
     - upper = res.selected.st
     - lower = sup.selected.st
     - pp = (price - lower) / (upper - lower)
     - rangeAtr = (upper - lower) / atr
     - status = rangeAtr ≤ CAGE_TIGHT_ATR → VALID_COMPRESSION
              = rangeAtr ≤ CAGE_LOOSE_ATR → LOOSE_SIDEWAY
              = otherwise → NONE
     - breakout = both pressure → SQUEEZE
                = res.pressure → IMMINENT_UP
                = sup.pressure → IMMINENT_DOWN
                = otherwise → NONE
     - upVi = up.vi, lowVi = low.vi
     - cross = up.vi ≠ low.vi (escape detected)

CAGE OBJECT:
  {upper, lower, pp, rangeAtr, status, breakout, upVi, lowVi,
   cross, pressureUp, pressureDn, versioning}

HUKUM CAGE (LAW-MASTER-10):
  - 2 valid walls → compression/sideways
  - 1 wall → trend (opposite wall distance = NULL)
  - Compression from same-direction line = forbidden
  - GRID active only in compression
  - Escape path: v0 → v1 → v2 (boundary max-2, internal many)
```

### 3.5 Phase Engine Contract

```
COMPONENT: STLMS.STRUCTURE.phase
INPUT: cage, wave, stDir
OUTPUT: market_phase

PHASE DETERMINATION:
  IF cage.status === NONE:
    stDir === 1  → UPTREND
    stDir === -1 → DOWNTREND
    else         → TRANSITION
  ELSE:
    → SIDEWAY_COMPRESSION

MARKET PHASE OBJECT:
  {cage: cage.status, wave: wave.structure, stDir: stDir, phase: phase_string}
```

### 3.6 Distance Engine Contract

```
COMPONENT: STLMS.EVIDENCE.correctionBus (uses Truth data)
INPUT: point (close), cage (upper, lower), struct (wave)
OUTPUT: correction_bus with distances

DISTANCE CEILING:
  cage.upper != null → cage.upper - point.close
  cage.upper == null → NULL (trend with no upper wall)

DISTANCE FLOOR:
  cage.lower != null → point.close - cage.lower
  cage.lower == null → NULL (trend with no lower wall)

RULE:
  - NULL on trend with single wall (not 0)
  - Produced in EVIDENCE layer but sourced from TRUTH geometry
  - OD (on-demand) fields in structure_snapshot
```

### 3.7 Truth Snapshot Contract

```
COMPONENT: truth_snapshot (produced in SIMULATION.process)
FIELDS (W — frozen stored):
  close: candle close price
  st: Supertrend value
  st_canon: canonical string representation
  stDir: trend direction (1, -1)
  color: HIJAU (above ST) / MERAH (below ST)
  atr: Average True Range
  ema: Exponential Moving Average (14)
  ema12: EMA 12 (for MACD)
  ema26: EMA 26 (for MACD)
  macd: MACD line value
  macd_signal: MACD signal line
  macd_hist: MACD histogram (macd - signal)
  rsi: Relative Strength Index
  wpr: Williams %R
  dist: absolute distance from close to ST
  distAtr: dist / ATR
  point_status: WARMUP / VALID

PRODUCER: TRUTH layer (via SIMULATION.process)
CONSUMER: STRUCTURE, EVIDENCE
CREATION: After market_snapshot, before structure
VALIDATION: checksum + lineage
REPLAY: snapshot replay
```

---

## 4. TRUTH LAYER DEPENDENCIES

### 4.1 Upstream Dependencies

| Dependency | Type | Description |
|-----------|------|-------------|
| MARKET | MANDATORY | market_snapshot provides raw OHLCV + takerBuyRatio |
| BOOT | MANDATORY | CONFIG provides bounded parameters (ATR_P, EMA_P, ST_MUL) |
| Checkpoint | MANDATORY | Previous candle state for contiguous indicators |

### 4.2 Downstream Dependencies

| Consumer | Type | Description |
|----------|------|-------------|
| STRUCTURE | MANDATORY | truth_snapshot feeds LineBuilder, CageEngine, WaveBuilder |
| EVIDENCE | MANDATORY | truth_snapshot feeds Direction Bus, Exit Bus, Correction Bus |
| CLONE | MANDATORY | truth_snapshot shared via Card Sharing |

### 4.3 Forbidden Dependencies

| Dependency | Reason |
|-----------|--------|
| STRUCTURE | Truth is upstream; must not read downstream |
| EVIDENCE | Truth is blind to indicators per LAW-MASTER-15 |
| CLONE | Truth does not make trading decisions |
| Date.now() | Determinism per LAW-MASTER-01 |
| Math.random() | Determinism per LAW-MASTER-01 |

---

## 5. INDICATOR REQUIREMENTS

### 5.1 Indicator Computation Rules

| Indicator | Period | Formula | Warmup | Notes |
|-----------|--------|---------|--------|-------|
| Supertrend | — | hl2 = (H+L)/2; ub = hl2 + ATR×3; lb = hl2 - ATR×3; band continuation | Requires ATR | Multiplier = 3 (ST_MUL), frozen |
| ATR | 10 | atr + (TR - atr) / 10 | 1 candle | ATR_P = 10, frozen |
| EMA | 14 | ema + (close - ema) × 2/15 | 1 candle | EMA_P = 14, frozen |
| EMA12 | 12 | e12 + (close - e12) × 2/13 | 1 candle | For MACD |
| EMA26 | 26 | e26 + (close - e26) × 2/27 | 1 candle | For MACD |
| MACD | 12/26/9 | e12 - e26; signal = sig + (macd - sig) × 2/10 | Requires EMA12/26 | Histogram = macd - signal |
| RSI | 10 | 100 - 100/(1 + ag/al) | 10 candles | Smoothed average gain/loss |
| W%R | 14 | -100 × (hh - close) / (hh - ll) | 14 candles | Requires 14-period high/low |
| W%R Velocity | — | wpr - previous_wpr | Requires 2 W%R values | Deadzone bounded |
| W%R Acceleration | — | vel - previous_vel | Requires 2 velocity values | Deadzone bounded |
| Volume Delta | — | 2 × takerBuyRatio - 1 | None | Range: -1 to +1 |
| Distance-to-ST | — | |close - st| | Requires ST | NULL during warmup |
| Dist-to-ST/ATR | — | dist / atr | Requires ATR + ST | NULL during warmup |

### 5.2 Warmup Requirements

```
WARMUP STATE:
  - point_status = "WARMUP" when atr == null OR ema == null
  - dist = NULL (not 0)
  - distAtr = NULL (not 0)
  - RSI = null until 10 periods of gain/loss data
  - W%R = null until 14 periods of high/low data
  - Wave < 6 = PENDING_WAVE (not padded)
  - OI empty = INSUFFICIENT_DATA (not 5000)

WARMUP DURATION:
  - ATR: 1 candle (first TR value)
  - EMA: 1 candle (first close value)
  - MACD: 1 candle after EMA12/26 ready
  - RSI: 10 candles
  - W%R: 14 candles
  - Wave: until 6 lines formed (variable)
  - Cage: until at least 1 wall resolved (variable)

NO ENTRY DURING WARMUP: All clones observe but do not trade.
```

---

## 6. INDICATOR AUTHORITY MATRIX

### 6.1 Complete Authority Matrix

```
┌─────────────────────────┬───────┬──────┬───────────┬───────────┬──────────┬───────────┬───────────┐
│ INDICATOR               │ ENTRY │ EXIT │VALIDATION │STATISTICS │KNOWLEDGE │PREDICTION │GOVERNANCE │
├─────────────────────────┼───────┼──────┼───────────┼───────────┼──────────┼───────────┼───────────┤
│ Supertrend              │   T   │  T   │     V     │     W     │    K     │    P−     │  amend    │
│ Distance-to-ST          │   S   │  —   │     V     │   W,K     │    K     │    P+     │    —      │
│ Distance-Ceiling        │   T   │  T   │     V     │     W     │    K     │    P−     │    B      │
│ Distance-Floor          │   T   │  T   │     V     │     W     │    K     │    P−     │    B      │
│ Price-Position (pp)     │   T   │  T   │     S     │     W     │    K     │    P+     │    B      │
│ Required-Move           │   T   │  T   │     V     │     W     │    —     │    P−     │    B      │
│ Wave Structure          │   S   │  —   │     —     │   W,K     │    K     │    P+     │    —      │
│ Cage Status             │   T   │  T   │     V     │     W     │    K     │    P+     │    B      │
│ Ladder                  │   S   │  S   │     S     │     W     │    K     │    P−     │    —      │
│ Escape-Path             │   T   │  T   │     V     │     S     │    —     │    P−     │    B      │
│ ATR                     │   T   │  T   │     —     │   W,K     │    K     │    P−     │    B      │
│ EMA                     │   T   │  —   │     V     │     S     │    K     │    P+     │    —      │
│ MACD                    │   X   │  T   │     X     │     W     │    K     │    P−     │    —      │
│ Open Interest           │   S   │  —   │     V     │     W     │    K     │    P+     │    —      │
│ OI-Delta                │   S   │  —   │     V     │     W     │    K     │    P+     │    —      │
│ Volume                  │   —   │  —   │     —     │     W     │    —     │    P−     │    —      │
│ Volume-Delta            │   T   │  —   │     V     │     W     │    K     │    P+     │    —      │
│ W%R                     │   X   │  T   │     —     │     W     │    K     │    P−     │    —      │
│ W%R-Velocity            │   X   │  T   │     —     │     W     │    K     │    P−     │    B      │
│ W%R-Acceleration        │   X   │  T   │     —     │     W     │    K     │    P−     │    B      │
│ Adaptive-Entry-Corridor │   T   │  T   │     V     │     W     │    —     │    P−     │    B      │
│ Adaptive-TP             │   —   │  T   │     —     │     W     │    K     │    P−     │    B      │
│ Wrong-Entry-Guard       │   —   │  T   │     —     │     W     │    K     │    P−     │    B      │
│ Trade-Marker            │   —   │  —   │     —     │  sumber  │  sumber  │    P−     │  konteks  │
│ Structure-Score         │   S   │  —   │     S     │   W,K     │    K     │    P−     │    —      │
│ Evidence-Score          │   T   │  —   │     V     │     S     │    K     │    P−     │    —      │
│ Confidence-Score        │   S   │  —   │     V     │     W     │    K     │    P−     │    —      │
│ Market-Phase            │   S   │  S   │     S     │   W,K     │    K     │    P+     │    —      │
│ Clone-Observation-Card  │   —   │  —   │     —     │  sumber  │  sumber  │    P−     │  konteks  │
└─────────────────────────┴───────┴──────┴───────────┴───────────┴──────────┴───────────┴───────────┘

LEGEND:
  T = Trigger/Authority (decision input)
  V = Validation-only (confirm/deny)
  S = Strengthening/Context (supports, does not decide)
  W = Behavior/Stat Witness (observed, recorded)
  K = Knowledge Material (feeds Academy/Oracle/HiveMind)
  B = Benchmark Material (feeds WASIT gates)
  P+ = Empirical-Probability Contributor
  P− = No Prediction Contribution
  X = FORBIDDEN (using here = BUILD STOP)
  — = Unused
```

### 6.2 Forbidden Indicator Usage

```
┌──────────────────────────────────────────────────────────────────┐
│  FORBIDDEN — BUILD STOP IF VIOLATED:                              │
│                                                                    │
│  MACD in Entry column (X) → MUST NOT trigger/strengthen entry     │
│  W%R in Entry column (X) → MUST NOT trigger/strengthen entry      │
│  W%R-Velocity in Entry (X) → MUST NOT trigger entry               │
│  W%R-Acceleration in Entry (X) → MUST NOT trigger entry           │
│                                                                    │
│  W%R in Oracle vector → MUST NOT be included (vector beku rule)   │
│  MACD in Oracle vector → MUST NOT be included (vector beku rule)  │
│                                                                    │
│  W%R as entry signal → violation of LAW-MASTER-08                 │
│  RSI as entry signal → violation of LAW-MASTER-15                 │
│  MACD as entry signal → violation of LAW-MASTER-15                │
│                                                                    │
│  Any indicator outside its valid column → BUILD STOP               │
└──────────────────────────────────────────────────────────────────┘
```

---

## 7. DATA QUALITY RULES

### 7.1 Data Quality Statuses

| Status | Condition | Response |
|--------|-----------|----------|
| OK | All data present and valid | Normal processing |
| WARMUP | Insufficient history | NULL values; no entry |
| PROVISIONAL | Candle not yet closed | No final snapshot |
| INSUFFICIENT_DATA | Required data missing | NULL + status |
| GAP | Time gap detected | gap_flag = 1; quality reduced |
| INVALID | Hygiene check failed | Candle rejected |

### 7.2 NULL + Status Rule (LAW-MASTER-02)

```
WHEN DATA IS MISSING OR INSUFFICIENT:
  ✓ dist = NULL, point_status = "WARMUP"
  ✓ OI score = NULL, oi_status = "INSUFFICIENT_DATA"
  ✓ Wave = PENDING_WAVE (not padded with fake lines)
  ✓ Panel display = "N/A" (not placeholder values)

  ✗ dist = 0 (fake neutral value)
  ✗ OI = 5000 (fake neutral value)
  ✗ Wave = padded to 6 lines (fake data)
  ✗ Panel = "Initializing..." (mock placeholder)
```

### 7.3 Authority Rules

```
GEOMETRY = FOUNDATION (LAW-MASTER-08, ID-01):
  - Supertrend/line/cage/wave are the decision foundation
  - Indicators are only witnesses per authority matrix
  - Geometry is computed ONLY in Truth/Structure
  - No other layer recomputes geometry from OHLCV

EVIDENCE = INDEPENDENT WITNESS (LAW-MASTER-15):
  - Truth is blind to indicators
  - Indicators are blind to geometry as decisions
  - 3 buses are separate (Direction/Exit/Correction)
  - Distance does not enter Evidence score

UNIDIRECTIONAL FLOW (LAW-MASTER-04):
  - Data → Truth → Structure → Evidence → Clone → Sim → Knowledge → Consumer
  - No backward loops to Core logic
  - Knowledge/Consumer only read cards
```

---

## TRUTH LAYER FREEZE STATUS: LOCKED

The complete Truth Layer architecture, including Point Builder, Line Builder, Slope Builder, Wave Builder, Cage Engine, Phase Engine, Distance Engine, Nearest Engine, indicator computations, warmup rules, authority matrix, data quality rules, and forbidden rules, is constitutionally frozen. No modification, addition, or removal of any Truth Layer component, indicator, or rule is permitted.
