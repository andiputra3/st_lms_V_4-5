# TRADING SCHEMA LAYER — Patch 03

## ST-LMS Architecture Enrichment Patch V1

**Date:** 2026-07-28
**Status:** ENRICHMENT ANALYSIS — FROZEN
**Sources:** MASTER_SPECIFICATION.html §6, §7, ST_LMS_CORE.js (CLONE_SHARED), TRADING_SCHEMA_FREEZE.md, DECISION_TREE_FREEZE.md

---

## 1. PERBEDAAN TRADING LAYER vs TRADING SCHEMA LAYER

| Aspek | TRADING LAYER | TRADING SCHEMA LAYER |
|-------|--------------|---------------------|
| **Fungsi** | Eksekusi trading (ENTRY, EXIT, POSITION) | Definisi kondisi market dan perilaku clone |
| **Runtime** | PER-CLONE, per candle | Definisi statis (blueprint) |
| **Output** | Trade markers, position state | Trading rules, condition matrices |
| **Consumer** | STATISTICS | TRADING LAYER (sebagai acuan) |
| **Pipeline** | Stage 6-12 | Pre-stage (definisi sebelum eksekusi) |

---

## 2. SELURUH TRADING SCHEMA

### 2.1 NO TRADE SCHEMA

```
KONDISI: Clone tidak entry karena kondisi tidak terpenuhi.
OBSERVASI: Mandatory (LAW-MASTER-06).

REASONS:
  - STDIR_OR_DIRBUS_MISMATCH
  - OUT_OF_CORRIDOR
  - EXPECTED_MOVE_LESS_THAN_REQUIRED
  - GLOBAL_RISK_BREACH
  - POSITION_ALREADY_OPEN
  - CAGE_NONE (GRID)
  - WARMUP

ENTRY_ALLOWED: false
NO_ENTRY_REASON: {reason}
SETUP_SCORE: 2500
CONFIDENCE: 2500
```

### 2.2 LONG SCHEMA

```
KONDISI: UPTREND — stDir = +1

ENTRY CONJUNCTION (ALL must be true):
  1. stDir === 1
  2. EMA slope > 0
  3. Volume Delta > 0
  4. corridor.inZone
  5. fee_safe (dist_ceiling ≥ required_move)
  6. global_ok
  7. open_position === false

EXIT PRIORITY:
  1. WRONG_ENTRY_EARLY   (vel < -deadzone ∧ hold ≤ 2)
  2. WRONG_ENTRY_GEOM    (adverse ≥ WRONG_ENTRY_PCT ∧ hold ≤ 2)
  3. HYPOTHESIS_INVALID  (breakout = IMMINENT_DOWN)
  4. SL                  (low ≤ sl)
  5. HOLD-VETO           (MACD expanding → delay TP)
  6. TP                  (high ≥ tp)
  7. EXIT_BUS            (RSI > 70 OR W%R > -20)
  8. TIME_EXIT           (hold ≥ TIME_EXIT ∧ profit < required)

SL: floor (cage.lower ?? nearest.support ?? close)
TP: min(ceiling, cage.upper, entry + TP_ATR_MULT × ATR)
```

### 2.3 SHORT SCHEMA

```
KONDISI: DOWNTREND — stDir = -1

ENTRY CONJUNCTION (ALL must be true):
  1. stDir === -1
  2. EMA slope < 0
  3. Volume Delta < 0
  4. corridor.inZone
  5. fee_safe (dist_floor ≥ required_move)
  6. global_ok
  7. open_position === false

EXIT PRIORITY:
  1. WRONG_ENTRY_EARLY   (vel > +deadzone ∧ hold ≤ 2)
  2. WRONG_ENTRY_GEOM    (adverse ≥ WRONG_ENTRY_PCT ∧ hold ≤ 2)
  3. HYPOTHESIS_INVALID  (breakout = IMMINENT_UP)
  4. SL                  (high ≥ sl)
  5. HOLD-VETO           (MACD expanding → delay TP)
  6. TP                  (low ≤ tp)
  7. EXIT_BUS            (RSI < 30 OR W%R < -80)
  8. TIME_EXIT           (hold ≥ TIME_EXIT ∧ profit < required)

SL: ceiling (cage.upper ?? nearest.resistance ?? close)
TP: max(floor, cage.lower, entry - TP_ATR_MULT × ATR)
```

### 2.4 GRID SCHEMA

```
KONDISI: SIDEWAY — cage.status ≠ NONE

ENTRY CONJUNCTION:
  1. cage_valid (status = VALID_COMPRESSION OR LOOSE_SIDEWAY)
  2. fee_safe (width ≥ 3 × required_move)
  3. breakout_none (breakout = NONE)
  4. pp in BUY_ZONE (pp < GRID_BUY_ZONE_MAX) → LONG fill
  5. pp in SELL_ZONE (pp > GRID_SELL_ZONE_MIN) → SHORT fill
  6. fills_per_side < GRID_MAX_FILLS_PER_SIDE

EXIT:
  1. RANGE_BREAK (cage no longer valid)
  2. RANGE_BREAK (breakout against fill)
  3. WRONG_ENTRY (adverse ≥ WRONG_ENTRY_PCT)
  4. GRID_TP (profit ≥ required_move)
  5. STOP_ALL (¬cage_valid)

RULES:
  - Blind to direction (no stDir, Direction Bus, MTF)
  - Scaling = multiple fills (not pyramiding)
  - Forbidden in trend (cage NONE)
```

### 2.5 WAIT SCHEMA

```
KONDISI: Clone mengamati tanpa entry. Kondisi market tidak mendukung.

WAIT STATES:
  WARMUP           — insufficient data (semua clone)
  TREND_OPPOSITE   — SHORT wait di UPTREND; LONG wait di DOWNTREND
  SIDEWAY_DIRECTIONAL — LONG/SHORT wait di SIDEWAY (GRID active)
  REVERSAL         — trend flipping (semua clone wait)
  CHAOS            — no clear structure (semua clone wait)
  EXHAUSTION       — trend exhausting (opposite clone wait)

OBSERVASI: Mandatory
NO_ENTRY_REASON: Sesuai wait state
```

### 2.6 HOLD SCHEMA

```
KONDISI: Posisi terbuka, tidak ada alasan exit.

HOLD BEHAVIOR:
  - hold_c += 1 per candle
  - Update MAE/MFE
  - HOLD-VETO active: MACD expanding + velocity with trend → delay TP
  - Continue monitoring exit conditions

HOLD-VETO RULES:
  - prevMacdHist != null
  - |macdHist| < |prevMacdHist| (MACD shrinking) → NOT hold
  - |macdHist| > |prevMacdHist| (MACD expanding) → hold possible
  - velocity with trend → HOLD active
  - HOLD delays TP (TP only triggers if HOLD is not active)
```

### 2.7 SKIP SCHEMA

```
KONDISI: Candle tidak valid atau data insufficient.

SKIP CONDITIONS:
  - data_status != "FINAL" (PROVISIONAL candle)
  - gap_flag = 1 (gap detected — quality reduced)
  - data_status = "INVALID" (hygiene failed)

BEHAVIOR:
  - Tidak ada entry
  - Posisi terbuka tetap dimonitor
  - Observasi tetap diproduksi (dengan status data)
```

### 2.8 LONG BREAKOUT SCHEMA

```
KONDISI: UPTREND + cage.breakout = IMMINENT_UP

ENTRY:
  - stDir = +1
  - cage.breakout = IMMINENT_UP
  - pressureUp = true (resistance under pressure)
  - Entry conjunction standard LONG

EXIT:
  - TP: cage.upper (resistance yang akan ditembus)
  - SL: cage.lower (support terdekat)
  - HYPOTHESIS_INVALID if breakout fails

CONFIDENCE: setup_score + breakout boost
```

### 2.9 LONG REVERSAL SCHEMA

```
KONDISI: DOWNTREND → UPTREND flip detected

ENTRY:
  - TREND_FLIP_UP detected (cl > puf)
  - stDir = +1 (baru flip)
  - Wave structure = REVERSAL_UP
  - Entry conjunction standard LONG (dengan konfirmasi tambahan)

CAUTION:
  - hold_c ≤ 2: wrong entry exit lebih agresif
  - false reversal risk: monitor ketat
```

### 2.10 LONG CONTINUATION SCHEMA

```
KONDISI: UPTREND established + wave = CONTINUATION_UP

ENTRY:
  - stDir = +1
  - wave = CONTINUATION_UP or STRONG_ACCUMULATION
  - Entry conjunction standard LONG

CONFIDENCE: Higher — trend established
EXIT: Standard LONG exit priority
```

### 2.11 LONG PULLBACK SCHEMA

```
KONDISI: UPTREND + price pullback ke floor/support

ENTRY:
  - stDir = +1 (trend masih UP)
  - dist_ceiling membesar (pullback dari ceiling)
  - corridor.inZone (price dekat floor)
  - fee_safe (dist_ceiling ≥ required_move — room to ceiling)

OPTIMAL: Pullback ke cage.lower atau nearest.support
CONFIDENCE: setup_score + pullback boost
```

### 2.12 SHORT BREAKOUT SCHEMA

```
KONDISI: DOWNTREND + cage.breakout = IMMINENT_DOWN

ENTRY:
  - stDir = -1
  - cage.breakout = IMMINENT_DOWN
  - pressureDn = true (support under pressure)
  - Entry conjunction standard SHORT

EXIT:
  - TP: cage.lower (support yang akan ditembus)
  - SL: cage.upper (resistance terdekat)
```

### 2.13 SHORT REVERSAL SCHEMA

```
KONDISI: UPTREND → DOWNTREND flip detected

ENTRY:
  - TREND_FLIP_DOWN detected (cl < plf)
  - stDir = -1 (baru flip)
  - Wave structure = REVERSAL_DOWN
  - Entry conjunction standard SHORT

CAUTION:
  - hold_c ≤ 2: wrong entry exit lebih agresif
```

### 2.14 SHORT CONTINUATION SCHEMA

```
KONDISI: DOWNTREND established + wave = CONTINUATION_DOWN

ENTRY:
  - stDir = -1
  - wave = CONTINUATION_DOWN or STRONG_DISTRIBUTION
  - Entry conjunction standard SHORT

CONFIDENCE: Higher — trend established
```

### 2.15 SHORT PULLBACK SCHEMA

```
KONDISI: DOWNTREND + price pullback ke ceiling/resistance

ENTRY:
  - stDir = -1 (trend masih DOWN)
  - dist_floor membesar (pullback dari floor)
  - corridor.inZone (price dekat ceiling)
  - fee_safe (dist_floor ≥ required_move)

OPTIMAL: Pullback ke cage.upper atau nearest.resistance
```

### 2.16 SIDEWAY GRID SCHEMA

```
KONDISI: SIDEWAY_COMPRESSION — cage valid, range stabil

ENTRY: Standard GRID schema
FILLS: Buy di lower zone, sell di upper zone
EXIT: GRID_TP saat profit ≥ required_move per fill
```

### 2.17 RANGE GRID SCHEMA

```
KONDISI: CONFIRMED_RANGE — wave menunjukkan range behavior

ENTRY: Standard GRID schema
WAVE: CONFIRMED_RANGE, RANGE_COMPRESSING, SIDEWAY
FILLS: Multiple fills dalam range
```

### 2.18 COMPRESSION GRID SCHEMA

```
KONDISI: VALID_COMPRESSION — range menyempit

ENTRY: Standard GRID schema
CAGE: VALID_COMPRESSION (tight range)
FILLS: Lebih agresif — kompresi sering menghasilkan breakout
CAUTION: Monitor breakout imminent
```

### 2.19 EXPANSION GRID SCHEMA

```
KONDISI: LOOSE_SIDEWAY — range melebar

ENTRY: Standard GRID schema
CAGE: LOOSE_SIDEWAY (wide range)
FILLS: Lebih konservatif — range lebar = risk lebih besar
```

### 2.20 EXIT SCHEMA (UMUM)

```
KONDISI: Posisi terbuka, alasan exit terpenuhi

EXIT PRIORITY (directional):
  1. WRONG_ENTRY_EARLY
  2. WRONG_ENTRY_GEOM
  3. HYPOTHESIS_INVALID
  4. SL
  5. HOLD-VETO (delay TP)
  6. TP
  7. EXIT_BUS
  8. TIME_EXIT

EXIT PRIORITY (GRID):
  1. RANGE_BREAK
  2. RANGE_BREAK (against fill)
  3. WRONG_ENTRY
  4. GRID_TP
  5. STOP_ALL
```

### 2.21 TIME EXIT SCHEMA

```
KONDISI: Posisi terlalu lama tanpa profit cukup

TRIGGER:
  hold_c ≥ TIME_EXIT_CANDLES (default: 40)
  AND current_profit_pct < required_move

PURPOSE: Menutup posisi stagnant
PRIORITY: Terendah (8) — hanya jika tidak ada alasan exit lain
```

### 2.22 PARTIAL EXIT SCHEMA

```
KONDISI: Profit mencapai threshold partial TP

TRIGGER:
  profit_pct ≥ PARTIAL_TP activation threshold

ACTION:
  - Close PARTIAL_TP_PCT (default: 50%) dari posisi
  - Move SL ke entry (breakeven untuk sisa posisi)
  - Continue holding remainder

STATUS: PARTIAL (position_status)
```

### 2.23 TRAILING EXIT SCHEMA

```
KONDISI: Profit mencapai trailing activation

TRIGGER:
  profit_pct ≥ TRAIL_ACTIVATE_R × ATR (default: 1.0)

ACTION:
  - SL digeser mengikuti price dengan jarak TRAIL_ATR_MULT × ATR
  - LONG: SL = max(SL, price - TRAIL_ATR_MULT × ATR)
  - SHORT: SL = min(SL, price + TRAIL_ATR_MULT × ATR)

STATUS: TRAILING (position_status)
```

### 2.24 WRONG ENTRY EXIT SCHEMA

```
KONDISI: Entry ternyata salah (detected dalam 2 candle pertama)

TRIGGERS:
  EARLY: W%R velocity berlawanan dengan posisi (hold ≤ 2)
  GEOM: adverse price movement ≥ WRONG_ENTRY_PCT (hold ≤ 2)

PRIORITY: Tertinggi (1-2) — exit segera
PURPOSE: Meminimalkan kerugian dari entry yang salah
```

---

## 3. SCHEMA SUMMARY

```
┌──────────────────────────────────────────────────────────────────────────┐
│                        ST-LMS TRADING SCHEMA                              │
│                                                                           │
│  STATE SCHEMAS (5):                                                       │
│    NO TRADE    — Observasi mandatory tanpa entry                          │
│    WAIT        — Menunggu kondisi market yang tepat                       │
│    HOLD        — Menahan posisi terbuka                                   │
│    SKIP        — Candle invalid/tidak lengkap                             │
│    EXIT        — Menutup posisi (8 priority levels)                       │
│                                                                           │
│  DIRECTIONAL SCHEMAS (8):                                                 │
│    LONG              — Standard LONG entry/exit                           │
│    LONG BREAKOUT     — LONG saat resistance breakout                      │
│    LONG REVERSAL     — LONG saat trend flip UP                            │
│    LONG CONTINUATION — LONG saat trend established                        │
│    LONG PULLBACK     — LONG saat pullback ke support                      │
│    SHORT             — Standard SHORT entry/exit                          │
│    SHORT BREAKOUT    — SHORT saat support breakout                        │
│    SHORT REVERSAL    — SHORT saat trend flip DOWN                         │
│    SHORT CONTINUATION— SHORT saat trend established                       │
│    SHORT PULLBACK    — SHORT saat pullback ke resistance                  │
│                                                                           │
│  GRID SCHEMAS (4):                                                        │
│    GRID              — Standard GRID entry/exit                           │
│    SIDEWAY GRID      — GRID di SIDEWAY_COMPRESSION                        │
│    RANGE GRID        — GRID di CONFIRMED_RANGE                            │
│    COMPRESSION GRID  — GRID di VALID_COMPRESSION (tight)                  │
│    EXPANSION GRID    — GRID di LOOSE_SIDEWAY (wide)                       │
│                                                                           │
│  EXIT SCHEMAS (4):                                                        │
│    TIME EXIT         — Exit karena hold terlalu lama                      │
│    PARTIAL EXIT      — Exit sebagian, lock profit                         │
│    TRAILING EXIT     — Exit dengan trailing stop                          │
│    WRONG ENTRY EXIT  — Exit karena entry salah (hold ≤ 2)                 │
│                                                                           │
│  TOTAL: 24 Trading Schemas                                                │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 4. SCHEMA → MARKET CONDITION MAPPING

| Market Condition | Active Schema |
|-----------------|---------------|
| TRENDING_UP | LONG, LONG CONTINUATION |
| TRENDING_DOWN | SHORT, SHORT CONTINUATION |
| SIDEWAY_COMPRESSION | SIDEWAY GRID, COMPRESSION GRID |
| LOOSE_SIDEWAY | EXPANSION GRID |
| REVERSAL_UP | LONG REVERSAL (caution) |
| REVERSAL_DOWN | SHORT REVERSAL (caution) |
| BREAKOUT_UP | LONG BREAKOUT |
| BREAKOUT_DOWN | SHORT BREAKOUT |
| EXHAUSTION_UP | WAIT (LONG exit, SHORT observe) |
| EXHAUSTION_DOWN | WAIT (SHORT exit, LONG observe) |
| RANGE_COMPRESSING | COMPRESSION GRID |
| RANGE_EXPANDING | EXPANSION GRID |
| CONFIRMED_RANGE | RANGE GRID |
| CHAOS | WAIT (semua clone) |
| WARMUP | WAIT (semua clone) |
| PULLBACK_UP | LONG PULLBACK |
| PULLBACK_DOWN | SHORT PULLBACK |

---

## KESIMPULAN PATCH 03

**Trading Schema Layer** mendefinisikan **24 trading schemas** yang mengelompokkan perilaku clone berdasarkan kondisi market. Trading Schema adalah blueprint statis yang diacu oleh Trading Layer saat eksekusi. Ini adalah enrichment logis — tidak menambah komponen baru, hanya mengelompokkan aturan yang sudah ada di MASTER_SPECIFICATION §7 dan ST_LMS_CORE.js CLONE_SHARED.

**Tidak ada perubahan pada:** Konstitusi, spesifikasi, SQLite schema, pipeline stages, layer authority, trading logic.
