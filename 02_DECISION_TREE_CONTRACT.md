# 02_DECISION_TREE_CONTRACT.md

## ST-LMS Implementation Contract Freeze V1 — Decision Tree Contract

**Date:** 2026-07-28
**Status:** CONSTITUTIONALLY FROZEN
**Audit:** Existing decision trees in DECISION_TREE_FREEZE.md (11 trees) and 03_TRADING_CONSTITUTION.md (41 schemas). This document formalizes decision tree contracts.

---

## 1. TRADING DECISION TREE

**Producer:** TRADE Layer
**Consumer:** CLONE Layer (LONG/SHORT/GRID)
**Reference:** DECISION_TREE_FREEZE.md S1-S2

### Required Artifacts
- truth_snapshot (stDir, emaSlope, volDelta, close, atr)
- structure_snapshot (cage, nearest, phase)
- evidence_snapshot (dir_bus, exit_bus)
- clone_ledger (positions, equity)

### Forbidden Artifacts
- W%R, MACD, RSI (for entry decisions — exit only)
- Oracle, HiveMind (clone must not read directly)

### Decision Flow

```
NEW CANDLE -> WARMUP? -> POSITION OPEN? -> stDir OK? ->
DIRBUS OK? -> CORRIDOR? -> FEE SAFE? -> GLOBAL OK? ->
ENTER (or NO TRADE with reason)
```

### Minimum Condition
All 5-7 entry conjunction conditions must be TRUE for entry.

### Optional Condition
Pullback detection, breakout confirmation, reversal validation.

### Confidence Source
setup_score = entry_allowed ? clamp(5000 + expected_move * 400, 0, 10000) : 2500

### Output
ENTRY_MARKER (if all conditions met) or NO_TRADE observation (with reason)

---

## 2. ENTRY DECISION TREE

**Producer:** TRADE Layer
**Consumer:** CLONE Layer
**Reference:** DECISION_TREE_FREEZE.md S1, 03_TRADING_CONSTITUTION.md S3

### Entry Schemas (11)

| Schema | Required Artifacts | Minimum Condition | Confidence |
|--------|-------------------|-------------------|------------|
| LONG CONTINUATION | truth(stDir,ema,volDelta), structure(wave,cage), evidence(dir_bus) | stDir=+1, wave=CONTINUATION_UP/STRONG_ACCUMULATION | HIGH |
| LONG PULLBACK | truth(stDir,distAtr), structure(cage,nearest), evidence(dir_bus) | stDir=+1, pullback to floor, fee_safe | MEDIUM |
| LONG BREAKOUT | structure(cage.breakout,pressureUp), truth(stDir) | stDir=+1, breakout=IMMINENT_UP | MEDIUM |
| LONG REVERSAL | truth(flip,stDir), structure(wave) | TREND_FLIP_UP, wave=REVERSAL_UP | LOW |
| SHORT CONTINUATION | truth(stDir,ema,volDelta), structure(wave,cage), evidence(dir_bus) | stDir=-1, wave=CONTINUATION_DOWN/STRONG_DISTRIBUTION | HIGH |
| SHORT PULLBACK | truth(stDir,distAtr), structure(cage,nearest), evidence(dir_bus) | stDir=-1, pullback to ceiling, fee_safe | MEDIUM |
| SHORT BREAKOUT | structure(cage.breakout,pressureDn), truth(stDir) | stDir=-1, breakout=IMMINENT_DOWN | MEDIUM |
| SHORT REVERSAL | truth(flip,stDir), structure(wave) | TREND_FLIP_DOWN, wave=REVERSAL_DOWN | LOW |
| GRID COMPRESSION | structure(cage.status,rangeAtr,pp) | cage=VALID_COMPRESSION | HIGH |
| GRID RANGE | structure(cage,wave) | wave=CONFIRMED_RANGE/SIDEWAY | MEDIUM |
| GRID EXPANSION | structure(cage.status,rangeAtr,pp) | cage=LOOSE_SIDEWAY | LOW |

### Forbidden Artifacts (All Entry Schemas)
- W%R, MACD (X in Entry column per Authority Matrix)
- RSI (not in Entry column)

---

## 3. EXIT DECISION TREE

**Producer:** TRADE Layer
**Consumer:** CLONE Layer
**Reference:** DECISION_TREE_FREEZE.md S2, 03_TRADING_CONSTITUTION.md S5

### Exit Priority (Directional: LONG/SHORT)

| Priority | Exit Type | Required Artifacts | Condition |
|----------|-----------|-------------------|-----------|
| 1 | WRONG_ENTRY_EARLY | truth(vel), position(hold_c<=2) | vel against position |
| 2 | WRONG_ENTRY_GEOM | position(entry,hold_c<=2), market(low/high) | adverse >= WRONG_ENTRY_PCT |
| 3 | HYPOTHESIS_INVALID | structure(cage.breakout) | breakout against position |
| 4 | SL | position(sl), market(low/high) | price crosses SL |
| 5 | HOLD-VETO | evidence(exit_bus.hold) | MACD expanding -> delay TP |
| 6 | TP | position(tp), market(low/high) | price crosses TP (if not vetoed) |
| 7 | EXIT_BUS | truth(rsi,wpr) | RSI>70/WPR>-20 (LONG), RSI<30/WPR<-80 (SHORT) |
| 8 | TIME_EXIT | position(hold_c,profit) | hold>=TIME_EXIT, profit<required |

### Exit Priority (GRID)

| Priority | Exit Type | Required Artifacts | Condition |
|----------|-----------|-------------------|-----------|
| 1 | RANGE_BREAK | structure(cage.status) | cage no longer valid |
| 2 | RANGE_BREAK | structure(cage.breakout) | breakout against fill |
| 3 | WRONG_ENTRY | position(entry,adverse) | adverse >= WRONG_ENTRY_PCT |
| 4 | GRID_TP | position(profit) | profit >= required_move |
| 5 | STOP_ALL | structure(cage.status) | cage invalid |

### Minimum Condition
At least one exit condition must be TRUE for exit.

### Confidence Source
Exit reason priority chain (1 = highest confidence of wrong trade, 8 = lowest).

### Output
EXIT_MARKER with reason, exit price, P&L (after-fee, adverse-first).

---

## 4. POSITION DECISION TREE

**Producer:** POSITION Layer
**Consumer:** CLONE Layer
**Reference:** DECISION_TREE_FREEZE.md S3, 03_TRADING_CONSTITUTION.md S4

### Position Schemas (7)

| Schema | Required Artifacts | Minimum Condition | Output |
|--------|-------------------|-------------------|--------|
| ADD POSITION | position(fills), structure(cage.pp) | GRID only: pp in zone, fills<max | New GRID fill marker |
| PARTIAL TP | position(profit_pct) | profit >= PARTIAL_TP threshold | PARTIAL marker, SL to entry |
| TRAILING TP | position(profit_pct), truth(atr) | profit >= TRAIL_ACTIVATE_R * ATR | Trailing stop update |
| BREAKEVEN | position(profit_pct, entry) | profit >= BREAKEVEN threshold | SL = entry_price |
| TIME EXIT | position(hold_c, profit) | hold >= TIME_EXIT, profit < required | TIME_EXIT marker |
| WRONG ENTRY | position(hold_c<=2), truth(vel,close) | vel wrong or adverse >= WRONG_PCT | WRONG_ENTRY marker |
| LOCK PROFIT | position(profit_pct) | profit >= LOCK threshold | EXIT_BUS disabled |

### Forbidden Artifacts
None — position management can use all available data.

---

## 5. PREDICTION DECISION TREE

**Producer:** PREDICTION Layer
**Consumer:** TRADING SCHEMA, CONSUMER
**Reference:** DECISION_TREE_FREEZE.md S11

### Required Artifacts
- knowledge_snapshot (academy_artifacts, oracle_match, hivemind, cermin)
- BAG artifacts (grouped statistics)

### Forbidden Artifacts
- Predictive models (constitution violation)
- Black-box AI (constitution violation)

### Decision Flow

```
ACADEMY CUKUP? -> YES: use empirical win_rate
                  NO: BELUM_CUKUP -> NULL

ORACLE MATCH?  -> YES: pattern_boost + oracle_boost
                  NO: no boost

HIVEMIND?      -> intelligence_score = 5000 + pattern_boost + oracle_boost + evidence_adj
                  dominant_bias = score>6500?BULLISH : score<3500?BEARISH : NEUTRAL

CERMIN?        -> calibration_error = actual - predicted

OUTPUT: prediction_snapshot (no_model=true)
```

### Minimum Condition
Academy sample >= 30 (SAMPLE_GATE) for CUKUP status.

### Confidence Source
empirical_win_rate (Academy) + similarity_score (Oracle) + intelligence_score (HiveMind).

### Output
prediction_snapshot: intelligence_score, dominant_bias, empirical_win_rate_per_clone, similarity_score, no_model=true, calibration_error.

---

## 6. GOVERNANCE DECISION TREE

**Producer:** GOVERNANCE Layer
**Consumer:** BENCHMARK, CONSUMER
**Reference:** DECISION_TREE_FREEZE.md (embedded in trading trees)

### Required Artifacts
- knowledge_snapshot (darwin_proposals)
- BAG artifacts (consensus, conflict_level)
- benchmark_snapshot (WASIT verdict)

### Forbidden Artifacts
- Direct Core/Clone write (BOUNDED params only)
- Auto-execute (must go through WASIT -> Human)

### Decision Flow

```
DARWIN WRITES PROPOSAL
  -> BOUNDED CHECK: value in [min,max]?
     NO -> AUTO-REJECT (OUT_OF_RANGE)
     YES -> continue

  -> WASIT 5-GATE: walk-forward evaluation
     G1(sample>=30), G2(expectancy>base), G3(worst not worse>10%),
     G4(win_rate not dropped>2%), G5(fee not increased)
     FAIL -> REJECTED_BY_WASIT
     PASS -> PENDING_HUMAN

  -> HUMAN APPROVAL
     APPROVED -> config_version baru + audit
     REJECTED -> discard

  -> ROLLBACK: tunjuk config_version lama (deterministik)
```

### Minimum Condition
Proposal must pass bounded-check AND WASIT 5-gate before human review.

### Confidence Source
WASIT 5-gate results (majority of folds per gate).

### Output
config_version update (BOUNDED parameters only), governance_log, rollback_log.

---

## 7. SIMULATION DECISION TREE

**Producer:** SIMULATION Layer
**Consumer:** REPLAY, AUDIT
**Reference:** ST_LMS_CORE.js SIMULATION namespace

### Required Artifacts
- All pipeline snapshots
- Clone intents
- Config (bounded parameters)

### Forbidden Artifacts
None — simulation executes, does not decide.

### Decision Flow

```
FRESH STATE -> FOR EACH CANDLE:
  -> PROCESS (22 pipeline stages)
  -> COMPUTE ALL (full pipeline execution)
  -> PERSIST (cards to IndexedDB)
  -> VERIFY (determinism: 2-run hash comparison)
```

### Minimum Condition
All pipeline stages must execute in order.

### Confidence Source
Determinism hash (2-run identical).

### Output
Simulation state, trade markers, immutable cards, determinism hash.

---

## 8. BENCHMARK DECISION TREE

**Producer:** BENCHMARK Layer
**Consumer:** GOVERNANCE
**Reference:** ST_LMS_CORE.js BENCHMARK namespace

### Required Artifacts
- Base trade_markers (current config)
- Candidate trade_markers (proposed config)
- Config (bounded parameters)

### Forbidden Artifacts
None — benchmark evaluates, does not decide.

### Decision Flow

```
WALK-FORWARD (f folds):
  -> SPLIT markers into f time-based folds
  -> PER FOLD: compute base metrics, candidate metrics
  -> PER GATE: majority of folds must pass

GATES:
  G1: candidate exits >= 30
  G2: candidate expectancy > base expectancy
  G3: candidate worst-loss not worse > 10% vs base
  G4: candidate win_rate not dropped > 2% vs base
  G5: candidate fee_drag not increased > 0.001 vs base

VERDICT: PASS (all 5 gates) / FAIL (any gate fails)

IDENTICAL CONFIG: base = candidate -> G2 must FAIL
```

### Minimum Condition
At least 3 folds, candidate exits >= 30.

### Confidence Source
WASIT 5-gate majority vote per fold.

### Output
benchmark_snapshot: folds, total_base, total_cand, gates{G1..G5}, per_fold[], verdict.

---

## DECISION TREE CONTRACT STATUS: LOCKED

All 8 decision trees (Trading, Entry, Exit, Position, Prediction, Governance, Simulation, Benchmark) are constitutionally frozen. Each tree defines producer, consumer, required/forbidden artifacts, minimum/optional conditions, confidence source, and output. No new decision tree may be created without Architecture Approval.
