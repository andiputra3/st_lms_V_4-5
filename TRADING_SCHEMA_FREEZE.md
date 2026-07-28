# TRADING SCHEMA FREEZE — ST-LMS v3

## Native HTML Market Geometry Intelligence Operating System

**Date:** 2026-07-28
**Phase:** PHASE 0 — Prompt 03
**Status:** CONSTITUTIONALLY FROZEN
**Sources:** MASTER_SPECIFICATION.html, DOCUMENT_DEPENDENCY.html, QWEN_14_DOC.html, ST_LMS_CORE.js, 01-07_IMPLEMENTATION_AUDIT.md

---

## 1. TRADING LIFECYCLE

### 1.1 Per-Candle Pipeline (22 Stages)

```
STAGE  TYPE              NAME                    DESCRIPTION
─────  ────────────────  ──────────────────────  ──────────────────────────────────
 1     ONCE              BOOT                    Establish system physics
 2     SHARED            MARKET OBSERVATION      Quarantine/canonize candle data
 3     SHARED            TRUTH LAYER             Pure geometry computation
 4     SHARED            STRUCTURE LAYER         Cage/wave/ladder/phase
 5     SHARED            EVIDENCE LAYER          3-bus witness system
       ═══════════════════════════════════════════════════════════════════════════
 6     PER-CLONE ×3      CLONE OBSERVATION       Record hypothesis (mandatory)
 7     PER-CLONE ×3      ENTRY VALIDATION        Conjunction gate check
 8     PER-CLONE ×3      POSITION MGMT           Manage live position
 9     PER-CLONE ×3      PROFIT MGMT             Secure profit adaptively
10     PER-CLONE ×3      EXIT VALIDATION         Decide close and why
11     PER-CLONE ×3      CLOSE POSITION          After-fee adverse-first
12     PER-CLONE ×3      TRADE MARKER            Aggregate markers
       ═══════════════════════════════════════════════════════════════════════════
13     SHARED-AGAIN      STATISTICS              Aggregate (sample-gated)
14     SHARED-AGAIN      RIVER                   Append-only archivist
15     ON-DEMAND         BENCHMARK               WASIT 5-gate (not per candle)
16     SHARED-AGAIN      ACADEMY                 Empirical win_rate per bucket
17     SHARED-AGAIN      ORACLE                  Similarity matching
18     SHARED-AGAIN      HIVEMIND                Market understanding
19     SHARED-AGAIN      CERMIN                  Calibration error
20     SHARED-AGAIN      DARWIN                  Parameter proposals
21     SHARED-AGAIN      PREDICTION              Empirical + similarity
22     SHARED-AGAIN      GOVERNANCE              Rem & kemudi
       ═══════════════════════════════════════════════════════════════════════════
OPT    OPTIONAL          CONSUMER                Trade intent (live DISABLED)
```

---

## 2. MARKET LIFECYCLE

### 2.1 Market Observation Stage

```
RAW CANDLE (OHLCV + takerBuyRatio)
  │
  ├─ HYGIENE CHECK
  │   H ≥ max(O, C) ∧ L ≤ min(O, C) ∧ H ≥ L ∧ V ≥ 0
  │   Pass → CLOSED; Fail → INVALID
  │
  ├─ GAP DETECTION
  │   ts[i] - ts[i-1] > 60000ms → gap_flag = 1
  │
  ├─ OI PROXY
  │   Derived from volume + takerBuyRatio (5m slots)
  │   Source = "PROXY_FROM_VOLUME_DERIVED"
  │
  └─ PRODUCE market_snapshot
      Fields: ts, symbol, tf, OHLCV, taker_buy_ratio, taker_sell_volume,
              data_status, gap_flag, wib_iso
```

### 2.2 Market States

| State | Condition | Trading Implication |
|-------|-----------|-------------------|
| CLOSED | Candle complete + hygiene passed | Produces FINAL snapshot |
| PROVISIONAL | Candle incomplete | No final snapshot |
| WARMUP | Insufficient history for indicators | truth_status = WARMUP |
| INSUFFICIENT_DATA | Missing required data | NULL + status |
| GAP | Time gap detected | gap_flag = 1; quality reduced |
| INVALID | Hygiene failed | Candle rejected |

---

## 3. CLONE LIFECYCLE

### 3.1 Clone Types

| Clone | Bias | Direction | Cage Dependency | Entry Conjunction |
|-------|------|-----------|----------------|-------------------|
| LONG | EXPANSION_UP | stDir=+1 | floor for SL, ceiling for TP | stDir=+1 ∧ EMA>0 ∧ vd>0 ∧ corridor ∧ fee_safe ∧ global_ok |
| SHORT | EXHAUSTION_DOWN | stDir=-1 | ceiling for SL, floor for TP | stDir=-1 ∧ EMA<0 ∧ vd<0 ∧ corridor ∧ fee_safe ∧ global_ok |
| GRID | COMPRESSION_RANGE | cage-only | cage for zone + fills | cage_valid ∧ width≥3·req ∧ breakout=NONE ∧ pp in zone |

### 3.2 Clone State Machine

```
                  ┌─────────────────────────────────┐
                  │          NO POSITION             │
                  │  (observing, no open trade)      │
                  └──────────────┬──────────────────┘
                                 │
                    entry_allowed = true
                    (conjunction gate passed)
                                 │
                                 ▼
                  ┌─────────────────────────────────┐
                  │         POSITION OPEN            │
                  │  entry_price, sl, tp, hold_c=0   │
                  └──────────────┬──────────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
              ▼                  ▼                  ▼
     ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
     │  EXIT: WIN   │  │ EXIT: LOSS   │  │EXIT: BREAK   │
     │  net > 0     │  │ net < 0      │  │  EVEN        │
     └──────────────┘  └──────────────┘  │ net = 0      │
                                         └──────────────┘
              │                  │                  │
              └──────────────────┼──────────────────┘
                                 │
                                 ▼
                  ┌─────────────────────────────────┐
                  │         NO POSITION              │
                  │  (back to observing)             │
                  └─────────────────────────────────┘
```

### 3.3 Clone Observation Contract

Per closed candle, each clone MUST produce an observation card with:
- `clone_id`: clone identifier (LONG/SHORT/GRID)
- `bias`: clone bias string
- `setup_score`: 0-10000 score
- `entry_allowed`: boolean
- `entry_reason`: string (if entry_allowed)
- `no_entry_reason`: string (if NOT entry_allowed)
- `confidence`: 0-10000
- `corridor`: {floor, ceil, inZone} (directional) or null (GRID)
- `grid_state`: {active, bias, fills, range, pp} (GRID) or null (directional)
- `expected_move`: percentage
- `required_move`: percentage
- `fee_safe`: boolean
- `mtf_conflict`: boolean
- `open_position`: boolean

**Mandatory rule**: Observation produced even if no trade (no_entry_reason must be set).

---

## 4. POSITION LIFECYCLE

### 4.1 Position States

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│   OPEN   │────▶│  HOLD    │────▶│  CLOSED  │     │BREAKEVEN │
│ hold_c=0 │     │hold_c≥1  │     │ exit!=null│    │ SL=entry │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
     │                │                                  │
     │                │                                  │
     ▼                ▼                                  ▼
┌──────────┐     ┌──────────┐                      ┌──────────┐
│ PARTIAL  │     │ TRAILING │                      │  CLOSED  │
│profit% tp│     │ATR trail │                      │          │
└──────────┘     └──────────┘                      └──────────┘
```

### 4.2 Position Tracking

| Field | Description | Source |
|-------|-------------|--------|
| entry_price | Price at entry | ENTRY_MARKER |
| exit_price | Price at exit | EXIT_MARKER |
| stop_loss | Stop loss level | Calculated at entry |
| take_profit | Take profit level | Calculated at entry |
| profit_lock | Partial TP level | Profit Management stage |
| trailing_stop | Trailing stop level | Profit Management stage |
| liquidation_distance | Distance to liquidation | Risk validation |
| mae | Maximum Adverse Excursion | Updated per candle |
| mfe | Maximum Favorable Excursion | Updated per candle |
| hold_count | Candles held | Incremented per candle |

### 4.3 Position Update (per candle)

```
POSITION.update(pos, hi, lo):
  1. pos.hold_c += 1
  2. Compute favorable: (hi - entry) / entry * 100  (LONG)
                        (entry - lo) / entry * 100  (SHORT)
  3. Compute adverse:   (entry - lo) / entry * 100  (LONG)
                        (hi - entry) / entry * 100  (SHORT)
  4. pos.mfe = max(pos.mfe, favorable)
  5. pos.mae = min(pos.mae, -adverse)
```

---

## 5. STATISTICS LIFECYCLE

### 5.1 Statistics Aggregation

```
TRADE MARKERS (all EXIT kind)
  │
  ├─ GROUP BY clone (LONG/SHORT/GRID)
  │
  ├─ COMPUTE per clone:
  │     sample: count of exits
  │     wins: count where result = WIN
  │     win_rate: (wins / sample) × 100
  │     expectancy: sum(net) / sample
  │     pf (profit factor): sum(gross_positive) / sum(|gross_negative|)
  │     mae: sum(|mae|) / sample
  │     mfe: sum(mfe) / sample
  │     fee_drag: sum(fee) / sample
  │     wrong_rate: (wrong_entry exits / sample) × 100
  │
  └─ SAMPLE GATE:
       sample ≥ SAMPLE_GATE (30) → CUKUP
       sample < SAMPLE_GATE (30) → BELUM_CUKUP
```

### 5.2 Statistics States

| State | Condition | Meaning |
|-------|-----------|---------|
| BELUM_CUKUP | sample < 30 | Not enough data to express confidence |
| CUKUP | sample ≥ 30 | Sufficient data; statistics are reliable |

---

## 6. KNOWLEDGE LIFECYCLE

### 6.1 Knowledge Entity Chain

```
RIVER (append-only archivist)
  │  Records all cards → store + index + chronicle
  │
  ├─▶ ACADEMY (empirical win_rate)
  │     Bucket key: clone | structure | distance_bucket | reason
  │     Per bucket: sample, wins, net
  │     Status: CUKUP (sample≥30) / BELUM_CUKUP
  │
  ├─▶ ORACLE (similarity matching) — parallel to Academy
  │     Vector: [normCodeWave, normCodeCage, pp, norm(ema), norm(oi), norm(vd), norm(mtf), norm(rsi), norm(distAtr)]
  │     Euclidean distance to historical vectors
  │     Match if similarity_score > 7500
  │     Vector is FROZEN — versioned via config_version
  │
  ├─▶ HIVEMIND (market understanding)
  │     Synthesizes: Academy top bucket + Oracle match + evidence adjustment
  │     Output: intelligence_score (0-10000), dominant_bias (BULLISH/BEARISH/NEUTRAL)
  │     Reads currentEvidence from evidence_snapshot (not constant)
  │     NOT a signal — is understanding
  │
  ├─▶ DARWIN (parameter proposals)
  │     Reads Academy artifacts + bounded parameters
  │     Proposes: TIGHTEN_ENTRY (if expectancy<0), TIGHTEN_WRONG (if wrong_rate>30)
  │     Kelas-A: bounded parameter adjustment
  │     Kelas-B: PEX (constitutional amendment)
  │     NO auto-execute
  │
  └─▶ LIBRARIAN (lifecycle management)
        Evaluates each Academy bucket:
          NEW         (n < 10)
          OBSERVATION (10 ≤ n < 30, or n≥30 with wr<5500 and not DEPRECATED)
          TRUSTED     (n ≥ 30, 5500 ≤ wr < 6500)
          MATURE      (n ≥ 30, wr ≥ 6500)
          DEPRECATED  (n ≥ 50, 3000 ≤ wr < 4000)
          DEAD        (n ≥ 50, wr < 3000)
        DEAD/DEPRECATED → not active for boost/entry-PEX

  └─▶ CERMIN (calibration)
        Per clone: predicted confidence vs actual win_rate
        calibration_error = actual - predicted
        Feeds into Prediction for confidence honesty
```

### 6.2 Knowledge States

| State | Entity | Meaning |
|-------|--------|---------|
| NEW | Librarian | < 10 samples; insufficient data |
| OBSERVATION | Librarian | 10-29 samples; being observed |
| TRUSTED | Librarian | ≥ 30 samples, win_rate 55-65% |
| MATURE | Librarian | ≥ 30 samples, win_rate ≥ 65% |
| DEPRECATED | Librarian | ≥ 50 samples, win_rate 30-40% |
| DEAD | Librarian | ≥ 50 samples, win_rate < 30% |
| CUKUP | Academy | sample ≥ 30 |
| BELUM_CUKUP | Academy | sample < 30 |

---

## 7. PREDICTION LIFECYCLE

### 7.1 Prediction Sources

```
PREDICTION (empirical only — NO model)
  │
  ├─ Academy win_rate per bucket → empirical_win_rate_per_clone
  │
  ├─ Oracle similarity_score → similarity_score
  │
  ├─ HiveMind intelligence_score → intelligence_score
  │     dominant_bias → dominant_bias
  │     pattern_boost, oracle_boost, evidence_adj
  │
  ├─ CERMIN calibration_error → calibration_error
  │
  └─ RULE: no_model = true (always)
       NULL if sample insufficient
```

### 7.2 Prediction Rules

| Rule | Description |
|------|-------------|
| EMPIRICAL ONLY | Probabilities = conditional frequency + similarity |
| NO MODEL | No predictive/forecasting model |
| NO HIDDEN AI | Every number has card lineage |
| SAMPLE GATED | Below threshold = BELUM_CUKUP/NULL |
| CERMIN HONESTY | calibration_error included for confidence honesty |

---

## 8. GOVERNANCE LIFECYCLE

### 8.1 Proposal Lifecycle

```
DARWIN writes proposal
  │
  ├─ AUTO-REJECT: if value outside BOUNDED range → REJECTED_OUT_OF_RANGE
  │
  ├─ WASIT 5-gate walk-forward
  │     G1: cand exits ≥ 30
  │     G2: expectancy_cand > expectancy_base (majority of folds)
  │     G3: worst_loss not worse > 10% (majority of folds)
  │     G4: win_rate not dropped > 2% (majority of folds)
  │     G5: fee_drag not increased > 0.001 (majority of folds)
  │     FAIL → REJECTED_BY_WASIT
  │
  ├─ PENDING_HUMAN_APPROVAL
  │     Human reviews WASIT results
  │     APPROVED → apply new config_version
  │     REJECTED → discard
  │
  └─ APPLY at boundary
        config_version incremented
        Chronicle records CONSTITUTION_AMENDED
        Rollback = revert to previous config_version
```

### 8.2 Governance Authority Matrix

| Actor | May | Must NOT |
|-------|-----|----------|
| Darwin | Propose Kelas-A/B; read artifacts+bounded | Auto-execute; change min/max bounds; touch constitutional atom |
| WASIT | Walk-forward parallel; 5-gate; auto-reject FAIL | Approve (filter only) |
| Human | Approve/reject proposals passing WASIT | — (final rem) |
| Bounded Registry | Auto-reject values outside range | Accept out-of-range values |
| Runtime | Apply config_version at boundary; rollback deterministically | Hot-swap; loop back to Core logic |

### 8.3 Governance Validations

| Validation | Checks | Failure Consequence |
|-----------|--------|-------------------|
| Constitution | 18 laws + authority matrix compliance | BUILD STOP |
| Proposal | bounded-check + label-peran + constitutional-atom | auto-reject |
| Authority Matrix | Indicators used only in valid columns | BUILD STOP |
| Build | 15 stop-rules + inventory + determinism | BUILD STOP |
| Runtime | checksum + lineage + no-race writer + sample-gate | card rejected / panel N/A |
| Governance Audit | decision timeline + rollback + deprecated enforcement | ANOMALY event |

---

## 9. TRADING SCHEMAS

### 9.1 LONG Trading Schema

```
ENTRY CONDITIONS (conjunction — ALL must be true):
  ┌─────────────────────────────────────────────────────────────┐
  │ 1. stDir === 1               (Supertrend direction is UP)   │
  │ 2. EMA slope > 0             (EMA is rising)                │
  │ 3. Volume Delta > 0          (net buying pressure)          │
  │ 4. corridor.inZone           (price in adaptive corridor)   │
  │ 5. fee_safe                  (dist_ceiling ≥ required_move) │
  │ 6. global_ok                 (no global risk breach)        │
  │ 7. open_position === false   (no position already open)     │
  └─────────────────────────────────────────────────────────────┘

EXIT CONDITIONS (priority-ordered — first match wins):
  ┌─────────────────────────────────────────────────────────────┐
  │ 1. WRONG_ENTRY_EARLY   W%R velocity < -deadzone ∧ hold≤2   │
  │ 2. WRONG_ENTRY_GEOM    adverse ≥ WRONG_ENTRY_PCT ∧ hold≤2  │
  │ 3. HYPOTHESIS_INVALID  cage.breakout === IMMINENT_DOWN     │
  │ 4. SL                  low ≤ stop_loss                     │
  │ 5. TP (after HOLD)     high ≥ take_profit (HOLD vetoes)    │
  │ 6. EXIT_BUS            RSI > 70 OR W%R > -20               │
  │ 7. TIME_EXIT           hold ≥ TIME_EXIT ∧ profit < required │
  └─────────────────────────────────────────────────────────────┘

SL/TP CALCULATION:
  SL = floor (cage.lower ?? nearest.support ?? close)
  TP = min(ceiling, cage.upper, entry + TP_ATR_MULT × ATR)
```

### 9.2 SHORT Trading Schema

```
ENTRY CONDITIONS (conjunction — ALL must be true):
  ┌─────────────────────────────────────────────────────────────┐
  │ 1. stDir === -1              (Supertrend direction is DOWN) │
  │ 2. EMA slope < 0             (EMA is falling)               │
  │ 3. Volume Delta < 0          (net selling pressure)         │
  │ 4. corridor.inZone           (price in adaptive corridor)   │
  │ 5. fee_safe                  (dist_floor ≥ required_move)   │
  │ 6. global_ok                 (no global risk breach)        │
  │ 7. open_position === false   (no position already open)     │
  └─────────────────────────────────────────────────────────────┘

EXIT CONDITIONS (priority-ordered — first match wins):
  ┌─────────────────────────────────────────────────────────────┐
  │ 1. WRONG_ENTRY_EARLY   W%R velocity > +deadzone ∧ hold≤2   │
  │ 2. WRONG_ENTRY_GEOM    adverse ≥ WRONG_ENTRY_PCT ∧ hold≤2  │
  │ 3. HYPOTHESIS_INVALID  cage.breakout === IMMINENT_UP       │
  │ 4. SL                  high ≥ stop_loss                    │
  │ 5. TP (after HOLD)     low ≤ take_profit (HOLD vetoes)     │
  │ 6. EXIT_BUS            RSI < 30 OR W%R < -80               │
  │ 7. TIME_EXIT           hold ≥ TIME_EXIT ∧ profit < required │
  └─────────────────────────────────────────────────────────────┘

SL/TP CALCULATION:
  SL = ceiling (cage.upper ?? nearest.resistance ?? close)
  TP = max(floor, cage.lower, entry - TP_ATR_MULT × ATR)
```

### 9.3 GRID Trading Schema

```
ENTRY CONDITIONS:
  ┌─────────────────────────────────────────────────────────────┐
  │ 1. cage_valid               cage.status ≠ NONE             │
  │ 2. fee_safe                 width ≥ 3 × required_move      │
  │ 3. breakout_none            cage.breakout === NONE          │
  │ 4. pp in BUY_ZONE           pp < GRID_BUY_ZONE_MAX → LONG  │
  │ 5. pp in SELL_ZONE          pp > GRID_SELL_ZONE_MIN → SHORT│
  │ 6. fills_per_side < max     long/short fills under limit   │
  └─────────────────────────────────────────────────────────────┘

EXIT CONDITIONS:
  ┌─────────────────────────────────────────────────────────────┐
  │ 1. RANGE_BREAK         cage becomes NONE (trend)           │
  │ 2. RANGE_BREAK         breakout opposite to fill side      │
  │ 3. WRONG_ENTRY         adverse ≥ WRONG_ENTRY_PCT           │
  │ 4. GRID_TP             profit ≥ required_move              │
  │ 5. STOP_ALL            cage no longer valid                │
  └─────────────────────────────────────────────────────────────┘

GRID RULES:
  - Blind to direction: no stDir, Direction Bus, MTF
  - Scaling = multiple fills (not pyramiding directional)
  - Forbidden in trend (cage NONE)
  - Forbidden to use MTF as veto
  - Forbidden to use trailing ATR per fill
```

### 9.4 WAIT Trading Schema

```
WAIT STATE: Clone has no position AND entry conditions are not met.

WAIT REASONS (directional):
  - STDIR_OR_DIRBUS_MISMATCH  (direction not confirmed)
  - OUT_OF_CORRIDOR           (price outside entry zone)
  - EXPECTED_MOVE_LESS_THAN_REQUIRED (not fee-safe)
  - GLOBAL_RISK_BREACH        (global exposure limit)
  - POSITION_ALREADY_OPEN     (only 1 position at a time)

WAIT REASONS (GRID):
  - CAGE_NONE                 (cage not valid)
  - CAGE_TIGHT                (width < 3 × required)
  - BREAKOUT_IMMINENT         (breakout detected)
  - FILLS_MAX                 (max fills per side reached)

OBSERVATION STILL PRODUCED: mandatory per LAW-MASTER-06
```

### 9.5 NO TRADE Trading Schema

```
NO TRADE is a per-candle state where:
  - Clone observes but does not enter
  - Observation card still produced (mandatory)
  - no_entry_reason field populated
  - setup_score and confidence still computed

NO TRADE ≠ SKIP: Observation is mandatory per candle per clone.
```

### 9.6 WARMUP Trading Schema

```
WARMUP STATE:
  - truth_status = WARMUP (indicators not yet ready)
  - point_status = WARMUP (insufficient history)
  - dist, distAtr = NULL (not 0)
  - Wave < 6 = PENDING_WAVE (not padded)
  - OI empty = INSUFFICIENT_DATA (not 5000)

WARMUP RULES:
  - No entry during warmup
  - Observation still produced (with WARMUP reason)
  - NULL values used, not neutral fake values
  - Indicators require warmup period before VALID status
```

---

## 10. TRADING STAGES

### 10.1 Entry Stage

```
INPUT:  truth_snapshot + structure_snapshot + evidence_snapshot + clone_ledger
OUTPUT: ENTRY_MARKER / no-trade (with reason)

ENTRY CONJUNCTION (all must pass):
  1. Direction check (stDir + EMA + vd)
  2. Corridor check (price in adaptive zone)
  3. Fee safety check (expected_move ≥ required_move)
  4. Global risk check (exposure limits)
  5. Position check (no open position)

ENTRY MARKER fields:
  ts, clone, side, kind=ENTRY, reason=CORRIDOR/GRID_FILL,
  entry=close_price, sl, tp
```

### 10.2 Correction Stage

```
INPUT:  truth_snapshot + structure_snapshot
OUTPUT: correction_bus

CORRECTION BUS fields:
  price_position (pp): 0-1 position within cage
  market_phase: TREND (cage NONE) or SIDEWAY (cage valid)
  dist_ceiling: cage.upper - close (NULL if no ceiling)
  dist_floor: close - cage.lower (NULL if no floor)
  wave_structure: current wave classification
  cage_status: NONE / VALID_COMPRESSION / LOOSE_SIDEWAY
  cage_range_atr: cage width in ATR units
  breakout: NONE / IMMINENT_UP / IMMINENT_DOWN / SQUEEZE

ROLE: Market context for clone decisions.
      NOT used for entry (entry uses Direction Bus).
      Used for position management and exit validation.
```

### 10.3 Position Management Stage

```
INPUT:  open_position + candle_data + exit_bus
OUTPUT: updated position state (mae, mfe, hold_count)

PER-CANDLE UPDATE:
  1. Increment hold_count
  2. Update MAE/MFE
  3. Check profit lock conditions
  4. Update trailing stop
  5. Check breakeven conditions

PROFIT MANAGEMENT:
  - partial_tp: close percentage at profit threshold
  - lock: secure profit, tighten SL
  - trail: ATR-based trailing stop
  - HOLD-veto: MACD expanding + velocity with trend → delay exit
```

### 10.4 Exit Stage

```
INPUT:  position + guard + cage + exit_bus
OUTPUT: exit_reason / null (continue holding)

EXIT PRIORITY (directional):
  1. WRONG_ENTRY_EARLY  (velocity-based, hold ≤ 2)
  2. WRONG_ENTRY_GEOM   (price-based, hold ≤ 2)
  3. HYPOTHESIS_INVALID (cage breakout against position)
  4. SL                 (stop loss hit)
  5. HOLD-VETO          (MACD expanding → delay TP)
  6. TP                 (take profit hit, if not vetoed)
  7. EXIT_BUS           (RSI/W%R exit signals)
  8. TIME_EXIT          (hold ≥ threshold, profit < required)

EXIT PRIORITY (GRID):
  1. RANGE_BREAK        (cage no longer valid)
  2. RANGE_BREAK        (breakout against fill)
  3. WRONG_ENTRY        (adverse ≥ threshold)
  4. GRID_TP            (profit ≥ required)
  5. STOP_ALL           (cage invalid)
```

### 10.5 Reentry Stage

```
REENTRY CONDITIONS:
  - Previous position closed
  - Entry conjunction passes
  - No cooldown enforced (reentry possible next candle)

REENTRY RULES:
  - Each candle evaluated independently
  - No position → check entry conditions
  - Entry conditions met → enter
  - Only 1 position per clone at a time
```

### 10.6 Time Exit

```
TIME EXIT CONDITIONS:
  hold_count ≥ TIME_EXIT_CANDLES (default: 40)
  AND current_profit_pct < required_move

PURPOSE: Close stale positions that are not producing
         sufficient profit after extended hold time.
```

### 10.7 Profit Lock

```
PROFIT LOCK CONDITIONS:
  When profit reaches threshold:
    - Close PARTIAL_TP_PCT of position
    - Move SL to entry (breakeven)
    - Continue holding remainder

NOT IMPLEMENTED in ST_LMS_CORE.js (specification only).
```

### 10.8 Breakeven

```
BREAKEVEN CONDITIONS:
  When profit reaches activation threshold:
    - Move SL to entry price
    - Position cannot lose after this point

NOT IMPLEMENTED in ST_LMS_CORE.js (specification only).
```

### 10.9 Stop Loss

```
STOP LOSS CALCULATION:
  LONG:  SL = floor (cage.lower ?? nearest.support ?? close)
  SHORT: SL = ceiling (cage.upper ?? nearest.resistance ?? close)

STOP LOSS RULES:
  - Set at entry time
  - Static (not trailing — trailing is separate mechanism)
  - Takes priority over TP on same candle (adverse-first)
  - GRID: no stop loss per fill; uses WRONG_ENTRY threshold instead
```

---

## 11. TRADING CONDITIONS

### 11.1 Market Condition Matrix

| Condition | Cage Status | stDir | Wave | Clone Active | Trading Behavior |
|-----------|------------|-------|------|-------------|-----------------|
| TRENDING_UP | NONE | +1 | CONTINUATION_UP / STRONG_ACCUMULATION | LONG | Directional LONG entries; GRID disabled |
| TRENDING_DOWN | NONE | -1 | CONTINUATION_DOWN / STRONG_DISTRIBUTION | SHORT | Directional SHORT entries; GRID disabled |
| SIDEWAY_COMPRESSION | VALID_COMPRESSION | ±1 | CONFIRMED_RANGE / SIDEWAY | GRID | GRID entries; directional may observe |
| LOOSE_SIDEWAY | LOOSE_SIDEWAY | ±1 | RANGE_EXPANDING | GRID | GRID entries with wider range |
| REVERSAL_UP | NONE→VALID | -1→+1 | REVERSAL_UP | Transition | No entry during flip; observe |
| REVERSAL_DOWN | NONE→VALID | +1→-1 | REVERSAL_DOWN | Transition | No entry during flip; observe |
| BREAKOUT_UP | NONE | +1 | — | LONG | Directional; cage breaking upward |
| BREAKOUT_DOWN | NONE | -1 | — | SHORT | Directional; cage breaking downward |
| EXHAUSTION_UP | NONE | +1 | EXHAUSTION_UP | SHORT (observe) | LONG exits; SHORT observes |
| EXHAUSTION_DOWN | NONE | -1 | EXHAUSTION_DOWN | LONG (observe) | SHORT exits; LONG observes |
| RANGE_COMPRESSING | VALID_COMPRESSION | ±1 | RANGE_COMPRESSING | GRID | Tight range; grid entries |
| CHAOS | NONE | 0 | CHAOS | None active | All clones observe; no entry |
| WARMUP | NONE | 0 | PENDING_WAVE | None active | Insufficient data; observe only |

### 11.2 Wave Structure → MTF Sector Mapping

| Wave Structure | MTF Sector | Score |
|---------------|-----------|-------|
| STRONG_ACCUMULATION | BULLISH_TREND | 8500 |
| STRONG_DISTRIBUTION | BEARISH_TREND | 8500 |
| CONTINUATION_UP | BULLISH_TREND | 7000 |
| CONTINUATION_DOWN | BEARISH_TREND | 7000 |
| CONFIRMED_RANGE | RANGE | 7500 |
| RANGE_EXPANDING | RANGE | 6500 |
| RANGE_COMPRESSING | COMPRESSION | 7000 |
| REVERSAL_UP | REVERSAL_UP | 6500 |
| REVERSAL_DOWN | REVERSAL_DOWN | 6500 |
| EXHAUSTION_UP | EXHAUSTION | 5500 |
| EXHAUSTION_DOWN | EXHAUSTION | 5500 |
| SIDEWAY | RANGE | 7000 |
| CHAOS | CHAOS | 3000 |

---

## 12. TRADING CONCEPTS

### 12.1 Hold Counter (hold_c)

```
DEFINITION: Number of candles a position has been held.
INITIAL VALUE: 0 (set at entry)
INCREMENT: +1 per candle via POSITION.update()
USAGE:
  - Wrong entry detection: hold_c ≤ 2 for early wrong exit
  - Time exit: hold_c ≥ TIME_EXIT_CANDLES triggers time-based exit
  - MAE/MFE tracking: per-candle excursion
```

### 12.2 Statistics Concept

```
PURPOSE: Aggregate trade outcomes per clone.
SAMPLE GATE: CUKUP iff sample ≥ 30.
METRICS:
  - win_rate: percentage of WIN results
  - expectancy: average net per trade
  - profit_factor: gross_positive / |gross_negative|
  - mae: average maximum adverse excursion
  - mfe: average maximum favorable excursion
  - fee_drag: average fee per trade
  - wrong_rate: percentage of wrong-entry exits
RULE: Below sample gate → BELUM_CUKUP (no confidence expressed)
```

### 12.3 Knowledge Concept

```
PURPOSE: Extract empirical understanding from trade outcomes.
ENTITIES:
  - Academy: conditional win_rate per 4-dim bucket
  - Oracle: euclidean similarity to historical market states
  - HiveMind: synthesized market understanding (score + bias)
  - CERMIN: calibration error (predicted vs actual)
  - Darwin: parameter mutation proposals
  - Librarian: artifact lifecycle management
RULE: Unidirectional (no write-back to Core). No ML.
```

### 12.4 Bag Concept

```
PURPOSE: Behavior Acquisition Group — intermediate aggregation
         between Statistics and Knowledge.
NOT IN MASTER_SPECIFICATION: Present in SQLite schema only.
BAG KINDS: behavior, market, entry, exit, risk, knowledge
FUNCTION: Groups statistics into consensus patterns,
          tracks conflict levels, compresses redundant data.
```

### 12.5 Supertrend Floor Concept

```
DEFINITION: The Supertrend line when stDir = +1 (uptrend).
             It acts as a dynamic support floor.
COMPUTATION: st = lower_band (lf) when trend = 1
USAGE:
  - LONG: SL is placed at or below the floor
  - Distance-to-ST (dist): |close - st|
  - Distance-to-ST/ATR (distAtr): dist / ATR
  - ST_DIST_VOL: standard deviation of distAtr (volatility proxy)
RULE: Single source of truth in TRUTH layer.
```

### 12.6 Supertrend Ceiling Concept

```
DEFINITION: The Supertrend line when stDir = -1 (downtrend).
             It acts as a dynamic resistance ceiling.
COMPUTATION: st = upper_band (uf) when trend = -1
USAGE:
  - SHORT: SL is placed at or above the ceiling
  - Distance-to-ST (dist): |close - st|
RULE: Single source of truth in TRUTH layer.
```

### 12.7 Distance ATR Concept

```
DEFINITION: Normalized distance from close to Supertrend,
            divided by ATR.
COMPUTATION: distAtr = |close - st| / ATR
PURPOSE: Measures how far price is from the trend line
         in volatility-adjusted terms.
USAGE:
  - Academy distance_bucket: OPTIMAL (≤0.5), NEAR (≤1),
    EXTENDED (≤2), FAR (>2), WARMUP (null)
  - Oracle vector: norm01(distAtr, 0, 3)
  - ST_DIST_VOL: rolling standard deviation of distAtr
  - Entry corridor: volatility adjustment via sdv
RULE: NULL during WARMUP, not 0.
```

---

## 13. FEE ARCHITECTURE

### 13.1 Fee Components

```
FEE_LAYERED:
  fee_murni: base fee rate (maker: 0.04%, mixed: 0.07%, taker: 0.10%)
             adjusted by FEE_DISCOUNT_PCT
  slip: 0.05% (fixed slippage estimate)
  safety: FEE_SAFETY_BUFFER_PCT (default: 0.10%)

REQUIRED_MOVE:
  = GRID_MIN_NET_PCT_OF_FILL + fee_murni(taker) + slip + safety
  Default: 0.50 + 0.10 + 0.05 + 0.10 = 0.75% (approx 0.7%)

RESULT CALCULATION:
  gross = (exit - entry) / entry × 100  (LONG)
  gross = (entry - exit) / entry × 100  (SHORT)
  net = gross - fee_murni - slip
  result = WIN (net > 0) / LOSS (net < 0) / BREAKEVEN (net = 0)

RULES:
  - WIN only if net > 0 (after all fees)
  - Adverse-first: SL beats TP on same candle
  - Fee murni is NOT 0.04% total (it's the base before discount)
```

### 13.2 Fee Safety

```
FEE_SAFE (directional):
  LONG:  (ceiling - close) / close × 100 ≥ REQUIRED_MOVE
  SHORT: (close - floor) / close × 100 ≥ REQUIRED_MOVE

FEE_SAFE (GRID):
  (cage.upper - cage.lower) / price × 100 ≥ 3 × REQUIRED_MOVE

UNSAFE → NO ENTRY: Entry blocked if expected move < required move.
```

---

## 14. ADVERSE-FIRST RULE

```
WHEN SL AND TP BOTH HIT ON SAME CANDLE:
  SL wins (conservative, honest).

IMPLEMENTATION:
  In decideClose(), SL check comes BEFORE TP check.
  TP is checked only if SL did not trigger.

PURPOSE:
  - Prevents overestimation of strategy performance
  - Realistic worst-case simulation
  - Required by LAW-MASTER-09 (Fee Berlapis Jujur)
```

---

## TRADING SCHEMA FREEZE STATUS: LOCKED

All trading schemas, lifecycles, conditions, and concepts are constitutionally frozen. No new trading logic may be added. No existing trading logic may be modified. This document reflects the complete trading architecture as specified in MASTER_SPECIFICATION.html, DOCUMENT_DEPENDENCY.html, QWEN_14_DOC.html, and ST_LMS_CORE.js.
