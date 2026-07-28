# 01_PIPELINE_CONTRACT.md

## ST-LMS Implementation Contract Freeze V1 — Pipeline Contract

**Date:** 2026-07-28
**Status:** CONSTITUTIONALLY FROZEN
**Audit:** Existing pipelines referenced from 01_ARCHITECTURE_FREEZE.md, DOCUMENT_DEPENDENCY.html, MASTER_SPECIFICATION.html

---

## AUDIT NOTE

Pipeline stages already frozen in `01_ARCHITECTURE_FREEZE.md` §1 (22 stages). Trading schemas frozen in `03_TRADING_CONSTITUTION.md` (41 schemas). This document formalizes pipeline contracts without redefining existing content.

---

## 1. PHYSICAL PIPELINE CONTRACT

**Owner:** INTEGRATION Layer
**Reference:** MASTER_SPECIFICATION.html S6, 01_ARCHITECTURE_FREEZE.md S1

### Execution Order (22 Stages)

| Order | Stage | Type | Owner | Input | Output | Consumer |
|-------|-------|------|-------|-------|--------|----------|
| 0 | BOOT | ONCE | BOOT | Config | SYSTEM_BOOT | All layers |
| 1 | MARKET | SHARED | MARKET | Raw candle | market_snapshot | TRUTH |
| 2 | TRUTH | SHARED | TRUTH | market_snapshot | truth_snapshot | STRUCTURE, EVIDENCE |
| 3 | STRUCTURE | SHARED | STRUCTURE | truth_snapshot | structure_snapshot | EVIDENCE, CLONE |
| 4 | EVIDENCE | SHARED | EVIDENCE | truth+structure | evidence_snapshot | CLONE, HIVEMIND |
| 5 | CLONE OBS | PER-CLONE x3 | CLONE | shared snapshots | clone_observation | TRADE |
| 6 | ENTRY VAL | PER-CLONE x3 | TRADE | clone_obs | ENTRY_MARKER | POSITION |
| 7 | POSITION | PER-CLONE x3 | POSITION | entry_marker | position_state | TRADE |
| 8 | PROFIT | PER-CLONE x3 | POSITION | position+candle | profit_mgmt | TRADE |
| 9 | EXIT VAL | PER-CLONE x3 | TRADE | position+guard | exit_reason | TRADE |
| 10 | CLOSE | PER-CLONE x3 | TRADE | exit_reason | EXIT_MARKER | STATISTICS |
| 11 | MARKER | PER-CLONE x3 | TRADE | entry+exit | trade_snapshot | STATISTICS |
| 12 | STATISTICS | SHARED-AGAIN | STATISTICS | trade_markers | statistics_snapshot | BAG |
| 13 | BAG | SHARED-AGAIN | BAG | statistics | bag_artifacts | KNOWLEDGE |
| 14 | RIVER | SHARED-AGAIN | KNOWLEDGE | all cards | chronicle | AUDIT |
| 15 | BENCHMARK | ON-DEMAND | BENCHMARK | trade_markers | benchmark_snapshot | GOVERNANCE |
| 16 | ACADEMY | SHARED-AGAIN | KNOWLEDGE | BAG+markers | academy_artifacts | PREDICTION |
| 17 | ORACLE | SHARED-AGAIN | KNOWLEDGE | vectors | oracle_match | HIVEMIND |
| 18 | HIVEMIND | SHARED-AGAIN | KNOWLEDGE | academy+oracle+ev | understanding | PREDICTION |
| 19 | CERMIN | SHARED-AGAIN | KNOWLEDGE | markers+conf | calibration | PREDICTION |
| 20 | DARWIN | SHARED-AGAIN | KNOWLEDGE | academy | proposals | GOVERNANCE |
| 21 | PREDICTION | SHARED-AGAIN | PREDICTION | knowledge | prediction_snapshot | TRADING SCHEMA |
| 22 | GOVERNANCE | SHARED-AGAIN | GOVERNANCE | proposals+verdict | config_version | CONSUMER |

### Invariant Rules

1. Stages 1-4: SHARED (1x compute, 3x share) — MUST NOT be inside clone loop
2. Stages 5-11: PER-CLONE (3x, isolated sub-ledgers) — MUST have separate ledgers
3. Stages 12-22: SHARED-AGAIN (1x, card-agnostic) — MUST NOT write to Core
4. Stage 15: ON-DEMAND — MUST NOT execute per candle
5. CONSUMER: OPTIONAL — terminal, no downstream

---

## 2. LOGICAL PIPELINE CONTRACT

**Owner:** INTEGRATION Layer
**Reference:** FINAL_LOGICAL_PIPELINE.md, 01_ARCHITECTURE_FREEZE.md S2

### Logical Flow

```
FOUNDATION:    BOOT -> WORKSPACE -> SQLITE FOUNDATION
SHARED:        MARKET -> TRUTH -> DISTANCE(logical) -> STRUCTURE -> EVIDENCE
PER-CLONE x3:  CLONE -> TRADE -> POSITION
SHARED-AGAIN:  STATISTICS -> BAG -> KNOWLEDGE -> PREDICTION -> TRADING SCHEMA -> GOVERNANCE
ON-DEMAND:     BENCHMARK
OPTIONAL:      CONSUMER
CROSS-CUTTING: SNAPSHOT, SIMULATION, REPLAY, DASHBOARD, AUDIT, INTEGRATION, FINAL VALIDATION
```

### Responsibility per Block

| Block | Responsibility | Dependency | Consumer |
|-------|---------------|------------|----------|
| FOUNDATION | System initialization, storage, config | None | All blocks |
| SHARED | Pure geometry + market structure | FOUNDATION | PER-CLONE |
| PER-CLONE | Trading execution (3 isolated clones) | SHARED | SHARED-AGAIN |
| SHARED-AGAIN | Aggregation, learning, governance | PER-CLONE | ON-DEMAND, OPTIONAL |
| ON-DEMAND | Benchmark evaluation | SHARED-AGAIN | SHARED-AGAIN |
| OPTIONAL | Trade intent, UI | SHARED-AGAIN | Human |

---

## 3. TRADING PIPELINE CONTRACT

**Owner:** TRADE Layer
**Reference:** 03_TRADING_CONSTITUTION.md, MASTER_SPECIFICATION.html S6-S7

### Trading Execution Order (Per Clone, Per Candle)

```
1. OBSERVE      Clone observes market (mandatory, even if no-trade)
2. VALIDATE     Check entry conjunction (5-7 conditions)
3. ENTER        If all conditions met -> ENTRY_MARKER
4. MANAGE       Update position (MAE/MFE, hold_c)
5. PROFIT       Check profit lock, trailing, breakeven
6. EXIT         Check exit conditions (priority 1-8)
7. CLOSE        If exit triggered -> EXIT_MARKER (adverse-first)
8. MARK         Aggregate markers -> trade_snapshot
```

### Clone-Specific Contracts

| Clone | Entry Conjunction | Exit Priority | Forbidden |
|-------|-----------------|---------------|-----------|
| LONG | stDir=+1, ema>0, vd>0, corridor, fee_safe, global_ok, open=null | WRONG_EARLY->WRONG_GEOM->HYPOTHESIS->SL->HOLD->TP->EXIT_BUS->TIME | W%R/MACD/RSI for entry |
| SHORT | stDir=-1, ema<0, vd<0, corridor, fee_safe, global_ok, open=null | Mirror LONG | W%R/MACD/RSI for entry |
| GRID | cage_valid, width>=3*req, breakout=NONE, pp in zone, fills<max | RANGE_BREAK->WRONG->GRID_TP->STOP_ALL | stDir, dir_bus, MTF, W%R, MACD, RSI |

---

## 4. BUILD PIPELINE CONTRACT

**Owner:** INTEGRATION Layer
**Reference:** 04_BUILD_CONTRACT.md

### Build Phase Sequence (10 Phases, 26 Sub-Phases)

```
PHASE 0: SPECIFICATION FREEZE (COMPLETE)
PHASE 1: FOUNDATION (Phase-01 to 03)
PHASE 2: MARKET + TRUTH (Phase-04 to 06)
PHASE 3: STRUCTURE + EVIDENCE (Phase-07 to 08)
PHASE 4: TRADING CORE (Phase-09 to 11)
PHASE 5: SIMULATION + REPLAY (Phase-12 to 13)
PHASE 6: STATISTICS + BAG + KNOWLEDGE (Phase-14 to 16)
PHASE 7: PREDICTION + GOVERNANCE (Phase-17 to 20)
PHASE 8: CONSUMER + DASHBOARD (Phase-21 to 22)
PHASE 9: INTEGRATION + AUDIT (Phase-23 to 25)
PHASE 10: BUILD APPROVAL (Phase-26)
```

### Build Rules

1. SEQUENTIAL: Each phase completes before next begins
2. GATE: Each phase must pass HARD validation gate
3. FOUNDATION FIRST: Phase-01 through 03 must complete first
4. NO SKIPPING: Phases cannot be skipped
5. NO PARALLEL: Single builder, sequential execution

---

## 5. LAYER PIPELINE CONTRACT

**Owner:** INTEGRATION Layer
**Reference:** 01_ARCHITECTURE_FREEZE.md S2

### Layer Data Flow

| Layer | Reads From | Writes To |
|-------|-----------|-----------|
| BOOT | Config | All namespaces |
| WORKSPACE | — | IndexedDB (serial) |
| SQLITE | — | All tables |
| MARKET | Raw candle | market_snapshot |
| TRUTH | market_snapshot | truth_snapshot |
| DISTANCE | truth + structure | distance metrics |
| STRUCTURE | truth_snapshot | structure_snapshot |
| EVIDENCE | truth + structure | evidence_snapshot |
| CLONE | shared snapshots | clone_observation |
| TRADE | clone_obs | trade_markers |
| POSITION | trade_markers | position_state |
| STATISTICS | trade_markers | statistics_snapshot |
| BAG | statistics + snapshot | bag_artifacts |
| KNOWLEDGE | BAG + statistics | knowledge_snapshot |
| PREDICTION | knowledge | prediction_snapshot |
| TRADING SCHEMA | prediction + BAG | schema_definitions |
| GOVERNANCE | knowledge + BAG | config_version |
| BENCHMARK | trade_markers | benchmark_snapshot |
| CONSUMER | prediction | trade_intent |

---

## 6. SQLITE PIPELINE CONTRACT

**Owner:** SQLITE FOUNDATION Layer
**Reference:** STLMS_SQLITE_SCHEMA_V1.sql, 01_ARCHITECTURE_FREEZE.md S6

### SQLite Write Chain

```
app_sessions -> symbols, timeframes
  -> pipeline_runs
    -> market_candles -> market_metadata, open_interest_series, market_gaps
      -> truth_snapshots -> truth_cache
        -> structure_snapshots -> wave_history, cage_history
          -> evidence_snapshots
            -> clones -> clone_observations
              -> trade_markers
                -> positions -> position_timeline
                  -> trade_statistics, market_statistics
                    -> bag_artifacts -> bag_patterns, bag_compression
                      -> knowledge_artifacts
                        -> predictions -> prediction_results
                          -> governance_proposals -> governance_logs, rollback_logs
                            -> benchmark_runs -> benchmark_cases
                              -> audit_logs -> audit_issues
```

### SQLite Read Chain (Replay)

```
replay_sessions -> replay_frames
  reads: market_candles, truth_snapshots, structure_snapshots, evidence_snapshots,
         clone_observations, trade_markers, positions, trade_statistics,
         knowledge_artifacts, predictions, governance_proposals, benchmark_runs
```

---

## 7. SNAPSHOT PIPELINE CONTRACT

**Owner:** SNAPSHOT Layer
**Reference:** MASTER_SPECIFICATION.html S9, 01_ARCHITECTURE_FREEZE.md S7

### Snapshot Production Order

| Order | Snapshot | Stage | Producer | W Fields | OD Fields |
|-------|----------|-------|----------|----------|-----------|
| 1 | Market | 1 | MARKET | All | — |
| 2 | Truth | 2 | TRUTH | All | — |
| 3 | Structure | 3 | STRUCTURE | cage,wave,ladder,phase,nearest | dist_ceiling, dist_floor |
| 4 | Evidence | 4 | EVIDENCE | All | — |
| 5 | Clone | 5 | CLONE x3 | All | — |
| 6 | Trade | 6-11 | SIM | All | — |
| 7 | Statistics | 12 | STATISTICS | per_clone | All (from Trade) |
| 8 | Knowledge | 14,16-20 | KNOWLEDGE | All | — |
| 9 | Benchmark | 15 | BENCHMARK | All (on-demand) | — |
| 10 | Prediction | 21 | PREDICTION | score,bias,no_model | emp_win_rate |

### Snapshot Lifecycle

```
PRODUCE -> FREEZE -> STORE -> CONSUME -> REPLAY
  │         │         │         │          │
  │     Object.    append-   read-     baca urutan
  │     freeze +   only      only      snapshot
  │     checksum  IndexedDB  oleh       deterministik
  │                         hilir
  │
  FINAL only from CLOSED candle
  PROVISIONAL -> no final snapshot
```

---

## PIPELINE CONTRACT STATUS: LOCKED

All 7 pipeline contracts (Physical, Logical, Trading, Build, Layer, SQLite, Snapshot) are constitutionally frozen. Each pipeline defines owner, responsibility, input, output, consumer, dependency, and execution order. No new pipeline may be created without Architecture Approval.
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
# 03_COMPONENT_CONTRACT.md

## ST-LMS Implementation Contract Freeze V1 — Component Contract

**Date:** 2026-07-28
**Status:** CONSTITUTIONALLY FROZEN
**Audit:** Components inventoried in 02_ARTIFACT_REGISTRY.md (145 artifacts). This document formalizes component contracts.

---

## COMPONENT RESTRICTION RULE

DILARANG MEMBUAT COMPONENT BARU. Component baru hanya boleh dibuat apabila:
1. Belum pernah didefinisikan dalam registry
2. Wajib untuk BAG, Distance, Trading Schema, atau SQLite
3. Tidak konflik dengan MASTER_SPECIFICATION

---

## 1. TRUTH COMPONENTS

| Component | Owner | Input | Output | Consumer | SQLite | Snapshot | Tests |
|-----------|-------|-------|--------|----------|--------|----------|-------|
| PointBuilder | TRUTH | market_snapshot | truth_point | STRUCTURE, EVIDENCE | truth_snapshots | Truth (W) | indicator accuracy, determinism |
| Supertrend | TRUTH | PointBuilder state | st, stDir, color | STRUCTURE, CLONE | truth_snapshots.st, .st_dir, .st_color | Truth (W) | st computation, flip detection |
| ATR | TRUTH | PointBuilder state | atr | STRUCTURE, CLONE, DISTANCE | truth_snapshots.atr | Truth (W) | ATR period 10 accuracy |
| EMA | TRUTH | PointBuilder state | ema, ema12, ema26 | EVIDENCE, CLONE | truth_snapshots.ema, .ema12, .ema26 | Truth (W) | EMA period 14 accuracy |
| MACD | TRUTH | PointBuilder state | macd, signal, histogram | EVIDENCE | truth_snapshots.macd, .macd_signal, .macd_hist | Truth (W) | MACD 12/26/9 accuracy |
| RSI | TRUTH | PointBuilder state | rsi | EVIDENCE, DASHBOARD | truth_snapshots.rsi | Truth (W) | RSI 0-100 range |
| W%R | TRUTH | PointBuilder state | wpr, vel, acc | EVIDENCE, CLONE | truth_snapshots.wpr | Truth (W) | W%R -100-0 range, exit-only |
| Volume Delta | TRUTH | PointBuilder state | volDelta | EVIDENCE, CLONE | truth_snapshots.volume_delta | Truth (W) | -1 to +1 range |
| Flip Detector | TRUTH | PointBuilder state | flip events | BAG, TRADING SCHEMA | — | Truth (W) | TREND_FLIP detection |

---

## 2. DISTANCE COMPONENTS

| Component | Owner | Input | Output | Consumer | SQLite | Snapshot | Tests |
|-----------|-------|-------|--------|----------|--------|----------|-------|
| Distance-to-ST | TRUTH | close, st | dist, distAtr | CLONE, BAG, KNOWLEDGE | truth_snapshots.dist_to_st, .dist_atr | Truth (W) | NULL during warmup |
| Distance-Ceiling | STRUCTURE | cage.upper, close | dist_ceiling | CLONE (LONG), BAG | structure_snapshots.dist_ceiling | Structure (OD) | NULL on downtrend |
| Distance-Floor | STRUCTURE | cage.lower, close | dist_floor | CLONE (SHORT), BAG | structure_snapshots.dist_floor | Structure (OD) | NULL on uptrend |
| ST_DIST_VOL | EVIDENCE | distAtr series | sdv, p90 | CLONE, BAG | — | — | rolling stddev accuracy |
| Distance Fingerprint | BAG | distAtr trajectory | fingerprint vector | KNOWLEDGE, ORACLE | bag_artifacts.payload_json | — | 12 dimensions present |
| Distance Bucket | DISTANCE | distAtr | bucket label | KNOWLEDGE, BAG | — | — | 5 buckets correct |
| Distance Trend | DISTANCE | distAtr series | trend label | BAG, TRADING SCHEMA | — | — | expanding/contracting/stable |
| Distance Velocity | DISTANCE | distAtr series | velocity | CLONE, BAG | — | — | rate of change correct |

---

## 3. STRUCTURE COMPONENTS

| Component | Owner | Input | Output | Consumer | SQLite | Snapshot | Tests |
|-----------|-------|-------|--------|----------|--------|----------|-------|
| LineBuilder | STRUCTURE | truth_points | line segments | WaveBuilder, CageEngine | — | — | >=4 members per line |
| SlopeBuilder | STRUCTURE | points, lines | slope transitions | WaveBuilder | — | — | 6 pattern types |
| WaveBuilder | STRUCTURE | lines, slopes | wave structures (13) | EVIDENCE, KNOWLEDGE, BAG | wave_history | Structure (W) | all 13 reachable, <6=PENDING |
| CageEngine | STRUCTURE | lineage, price, atr | cage object | CLONE, GRID, BAG | structure_snapshots, cage_history | Structure (W) | HUKUM CAGE, versioning |
| Ladder | STRUCTURE | lines, price | ladder analysis | BAG, TRADING SCHEMA | — | Structure (W) | stepped detection |
| Nearest | STRUCTURE | lines, price | nearest S/R | CLONE | — | Structure (W) | correct nearest |
| Phase | STRUCTURE | cage, wave, stDir | market_phase | CLONE, BAG, TRADING SCHEMA | — | Structure (W) | 4 phases correct |

---

## 4. TRADING COMPONENTS

| Component | Owner | Input | Output | Consumer | SQLite | Snapshot | Tests |
|-----------|-------|-------|--------|----------|--------|----------|-------|
| LONG Clone | CLONE | shared snapshots | LONG observation | TRADE | clone_observations | Clone (W) | entry conjunction, 1 obs/candle |
| SHORT Clone | CLONE | shared snapshots | SHORT observation | TRADE | clone_observations | Clone (W) | mirror LONG, 1 obs/candle |
| GRID Clone | CLONE | structure_snapshot | GRID observation | TRADE | clone_observations | Clone (W) | cage-only, 1 obs/candle |
| Entry Corridor | CLONE | floor, ceiling, close, atr, sdv | corridor zone | CLONE | — | — | adaptive width |
| Entry Marker | TRADE | clone_obs | ENTRY_MARKER | POSITION | trade_markers | Trade (W) | sl, tp calculated |
| Exit Marker | TRADE | position, reason, prices | EXIT_MARKER | STATISTICS | trade_markers | Trade (W) | P&L, after-fee, adverse-first |
| Position Manager | POSITION | entry_marker | position_state | TRADE | positions | — | mae, mfe, hold_c |
| Exit Decider | TRADE | position, market | exit_reason | TRADE | — | — | priority order correct |
| Fee Calculator | TRADE | gross, kind | net, result | STATISTICS | trade_markers.net, .result | Trade (W) | WIN only net>0 |
| Global Risk | CLONE | positions | global_ok | CLONE | — | — | exposure limits |
| Grid Evaluator | CLONE | cage, price, fills | grid_state | TRADE | — | — | fills management |
| Wrong Entry Guard | TRADE | position(hold<=2), truth(vel,close) | wrong_entry flag | TRADE | — | — | early detection |

---

## 5. STATISTICS COMPONENTS

| Component | Owner | Input | Output | Consumer | SQLite | Snapshot | Tests |
|-----------|-------|-------|--------|----------|--------|----------|-------|
| TradeStats | STATISTICS | trade_markers | per-clone metrics | BAG, KNOWLEDGE | trade_statistics | Statistics | sample gate, accuracy |
| MarketStats | STATISTICS | structure, market | market-level metrics | BAG | market_statistics | — | phase distribution |
| Sample Gate | STATISTICS | sample count | CUKUP/BELUM_CUKUP | BAG, KNOWLEDGE | — | Statistics (W) | >=30 = CUKUP |

---

## 6. BAG COMPONENTS

| Component | Owner | Input | Output | Consumer | SQLite | Snapshot | Tests |
|-----------|-------|-------|--------|----------|--------|----------|-------|
| Grouper | BAG | statistics, snapshots | bag_artifacts | KNOWLEDGE | bag_artifacts | — | bag_key unique per session |
| Classifier | BAG | bag_artifacts | bag_kind assignment | KNOWLEDGE | bag_artifacts.bag_kind | — | 6 kinds correct |
| Pattern Miner | BAG | bag_artifacts | bag_patterns | KNOWLEDGE, DASHBOARD | bag_patterns | — | patterns detected |
| Fingerprint Generator | BAG | distance metrics | distance_fingerprint | KNOWLEDGE, ORACLE | bag_artifacts.payload_json | — | 12 dimensions |
| Consensus Engine | BAG | grouped artifacts | consensus score | KNOWLEDGE | bag_artifacts.consensus | — | HIGH/MEDIUM/LOW/NONE |
| Conflict Detector | BAG | grouped artifacts | conflict_level | KNOWLEDGE | bag_artifacts.conflict_level | — | NONE/LOW/MEDIUM/HIGH |
| Maturity Assessor | BAG | artifact stats | maturity_score | KNOWLEDGE | bag_artifacts.payload_json | — | 0-10000 range |
| Behavior Analyzer | BAG | bag_artifacts | behavior_profiles | KNOWLEDGE, TRADING SCHEMA | bag_artifacts.payload_json | — | 6 profiles |
| Compressor | BAG | redundant artifacts | bag_compression | DASHBOARD | bag_compression | — | compression_ratio 0-1 |
| Sequence Analyzer | BAG | wave_history, cage_history | sequence_patterns | KNOWLEDGE | bag_patterns | — | patterns detected |
| Temporal Analyzer | BAG | timestamped artifacts | temporal_patterns | KNOWLEDGE | bag_patterns | — | time patterns |

---

## 7. KNOWLEDGE COMPONENTS

| Component | Owner | Input | Output | Consumer | SQLite | Snapshot | Tests |
|-----------|-------|-------|--------|----------|--------|----------|-------|
| Academy | KNOWLEDGE | BAG + markers + snapshots | win_rate per bucket | PREDICTION, DARWIN | knowledge_artifacts | Knowledge (W) | 4-dim bucket, sample-gated |
| Oracle | KNOWLEDGE | vectors (now + historical) | oracle_match | HIVEMIND, PREDICTION | knowledge_artifacts | Knowledge (W) | euclidean, match>7500 |
| HiveMind | KNOWLEDGE | academy + oracle + evidence | understanding | PREDICTION | knowledge_artifacts | Knowledge (W) | score 0-10000, bias |
| CERMIN | KNOWLEDGE | markers + confidence | calibration_error | PREDICTION, GOVERNANCE | knowledge_artifacts | Knowledge (W) | predicted vs actual |
| Librarian | KNOWLEDGE | academy_artifacts | lifecycle events | DASHBOARD, AUDIT | knowledge_artifacts | Knowledge (W) | 6 statuses |
| Darwin | KNOWLEDGE | academy + BAG | proposals | GOVERNANCE | knowledge_artifacts | Knowledge (W) | no auto-execute |
| River | KNOWLEDGE | all cards | chronicle | AUDIT | — | — | append-only |

---

## 8. PREDICTION COMPONENTS

| Component | Owner | Input | Output | Consumer | SQLite | Snapshot | Tests |
|-----------|-------|-------|--------|----------|--------|----------|-------|
| Summarizer | PREDICTION | knowledge_snapshot | prediction_snapshot | TRADING SCHEMA, CONSUMER | predictions | Prediction | no-model, empirical |
| Empirical Agg | PREDICTION | academy_artifacts | empirical_win_rate | TRADING SCHEMA, CONSUMER | predictions.empirical_win_rate | Prediction (OD) | per clone accuracy |
| Similarity Agg | PREDICTION | oracle_match | similarity_score | TRADING SCHEMA, CONSUMER | predictions.similarity_score | Prediction (W) | 0-10000 range |
| Intelligence Agg | PREDICTION | hivemind | intelligence_score, bias | TRADING SCHEMA, CONSUMER | predictions.confidence | Prediction (W) | 0-10000 range |

---

## 9. BENCHMARK COMPONENTS

| Component | Owner | Input | Output | Consumer | SQLite | Snapshot | Tests |
|-----------|-------|-------|--------|----------|--------|----------|-------|
| WASIT 5-Gate | BENCHMARK | base + cand markers | gates, verdict | GOVERNANCE | benchmark_runs | Benchmark (W) | identical->G2 FAIL |
| Fold Metrics | BENCHMARK | per-fold markers | per-fold stats | GOVERNANCE | benchmark_cases | Benchmark (W) | metrics accuracy |
| Walk-Forward | BENCHMARK | configs, markers | benchmark_snapshot | GOVERNANCE | benchmark_runs | Benchmark (W) | majority vote |
| Parallel Worker | BENCHMARK | base, cand, folds | wasit result | GOVERNANCE | — | — | worker executes |

---

## 10. DASHBOARD COMPONENTS

| Component | Owner | Input | Output | Consumer | SQLite | Tests |
|-----------|-------|-------|--------|----------|--------|-------|
| Geometry Viewer | DASHBOARD | truth + structure + markers | candle chart | Human | — | no-mock render |
| Clone Cards | DASHBOARD | clone_observations | 3 clone panels | Human | — | all 3 rendered |
| Trade History | DASHBOARD | trade_markers | history table | Human | trade_markers | correct P&L display |
| Equity Curve | DASHBOARD | clone.equity | equity chart | Human | — | correct rendering |
| Rapor Table | DASHBOARD | statistics_snapshot | stats table | Human | trade_statistics | sample gate display |
| Academy Table | DASHBOARD | academy_artifacts | bucket table | Human | knowledge_artifacts | 4-dim key display |
| Knowledge Panels | DASHBOARD | oracle, hivemind, cermin | knowledge panels | Human | knowledge_artifacts | all entities displayed |
| Governance UI | DASHBOARD | proposals, validations | proposal management | Human | governance_proposals | approve/reject/rollback |
| Replay Viewer | DASHBOARD | replay_frames | scrubber + playback | Human | replay_frames | 6 kinds supported |
| Prediction Panel | DASHBOARD | prediction_snapshot | prediction display | Human | predictions | no-model indicator |
| Consumer Panel | DASHBOARD | trade_intent | intent preview | Human | — | live-adapter disabled |
| Audit Panel | DASHBOARD | audit_logs, self-tests | audit display | Human | audit_logs | pass/fail indicators |
| SQLite Viewer | DASHBOARD | all tables | table browser | Human | all tables | CRUD operations |
| SQLite Manager | DASHBOARD | database | admin operations | Human | — | backup/restore/vacuum |
| Query Console | DASHBOARD | user SQL | query results | Human | all tables | readonly/transaction/write |

---

## 11. INTEGRATION COMPONENTS

| Component | Owner | Input | Output | Consumer | SQLite | Tests |
|-----------|-------|-------|--------|----------|--------|-------|
| Pipeline Orchestrator | INTEGRATION | pipeline config | execution order | All layers | pipeline_runs | 22 stages in order |
| Worker Bridge | INTEGRATION | worker messages | postMessage results | Main thread | — | protocol correct |
| Card Sharing Enforcer | INTEGRATION | pipeline stages | shared cards | CLONE x3 | — | SHARED 1x, PER-CLONE 3x |
| Unidirectional Guard | INTEGRATION | data flow | violation alerts | AUDIT | — | no backward loops |
| Serial Writer | INTEGRATION | write requests | IndexedDB writes | WORKSPACE | — | single writer, zero race |
| Resource Governor | INTEGRATION | performance.memory | degrade actions | All layers | — | 70/85/95% thresholds |

---

## COMPONENT CONTRACT STATUS: LOCKED

All components across 11 categories are constitutionally frozen. Each component defines owner, responsibility, input, output, consumer, dependency, SQLite table, snapshot usage, and required tests. No new component may be created without Architecture Approval.
# 04_WORKER_CONTRACT.md

## ST-LMS Implementation Contract Freeze V1 — Worker Contract

**Date:** 2026-07-28
**Status:** CONSTITUTIONALLY FROZEN

---

## WORKER AUTHORITY RULES

1. Workers are COLD: created on demand, terminated after completion
2. Workers use POSTMESSAGE: send results to main thread
3. Workers DO NOT access IndexedDB directly
4. Workers DO NOT access SQLite directly
5. Main thread PERSISTS: validates and stores worker results
6. Workers are DETERMINISTIC: same input -> same output
7. Workers have TIMEOUT: terminated if exceeding limit

---

## 1. MARKET WORKER (Data Worker)

| Aspect | Value |
|--------|-------|
| Authority | Read raw data, process batches |
| Responsibility | Batch bootstrap, TF aggregation, gap-repair |
| Input | Raw candle data (OHLCV) |
| Output | Processed market data, derived TFs |
| Dependency | MARKET layer |
| Execution Order | After MARKET data available, before TRUTH |
| Thread | Separate (cold) |
| Timeout | 120s |
| Fallback | Sequential on main thread |
| Forbidden | IndexedDB write, SQLite write, trading decisions |

---

## 2. TRUTH WORKER

| Aspect | Value |
|--------|-------|
| Authority | N/A — Truth is main thread only |
| Responsibility | N/A — Truth requires state continuity |
| Input | N/A |
| Output | N/A |
| Dependency | N/A |
| Execution Order | N/A |
| Note | **Truth is NOT a worker.** Truth/Structure/Evidence/Clone per-candle for one symbol MUST be sequential on main thread. Parallelizing per-candle breaks EMA/ATR continuity. |

---

## 3. DISTANCE WORKER

| Aspect | Value |
|--------|-------|
| Authority | N/A — Distance is computed alongside Truth/Structure |
| Responsibility | N/A |
| Input | N/A |
| Output | N/A |
| Dependency | N/A |
| Execution Order | N/A |
| Note | **Distance is NOT a separate worker.** Distance metrics are computed in TRUTH (W fields) and STRUCTURE (OD fields). |

---

## 4. STRUCTURE WORKER

| Aspect | Value |
|--------|-------|
| Authority | N/A — Structure is main thread only |
| Responsibility | N/A — Structure requires state continuity |
| Input | N/A |
| Output | N/A |
| Dependency | N/A |
| Execution Order | N/A |
| Note | **Structure is NOT a worker.** Same as Truth — requires contiguous state. |

---

## 5. TRADING WORKER

| Aspect | Value |
|--------|-------|
| Authority | N/A — Trading is main thread only |
| Responsibility | N/A — Clone execution is PER-CLONE on main thread |
| Input | N/A |
| Output | N/A |
| Dependency | N/A |
| Execution Order | N/A |
| Note | **Trading is NOT a worker.** Clone observation/entry/exit must be sequential per symbol. Parallel across symbols is allowed. |

---

## 6. STATISTICS WORKER

| Aspect | Value |
|--------|-------|
| Authority | Compute statistics from markers |
| Responsibility | Batch aggregation of trade statistics |
| Input | trade_markers array |
| Output | Aggregated statistics (win_rate, expectancy, pf, mae, mfe, fee_drag, wrong_rate) |
| Dependency | STATISTICS layer |
| Execution Order | After TRADE markers available, before BAG |
| Thread | Main thread (lightweight) or Knowledge Worker (batch) |
| Timeout | 30s |
| Fallback | Sequential on main thread |
| Forbidden | IndexedDB write, SQLite write |

---

## 7. BAG WORKER (Knowledge Worker — shared)

| Aspect | Value |
|--------|-------|
| Authority | Group, classify, mine patterns, generate fingerprints |
| Responsibility | BAG artifact generation, pattern mining, behavior analysis |
| Input | trade_statistics, market_statistics, trade_markers, snapshots |
| Output | bag_artifacts, bag_patterns, bag_compression, fingerprints |
| Dependency | BAG layer, STATISTICS |
| Execution Order | After STATISTICS, before KNOWLEDGE |
| Thread | Separate (cold) — shared Knowledge Worker |
| Timeout | 120s |
| Fallback | Sequential on main thread |
| Forbidden | IndexedDB write, SQLite write, Core write |

---

## 8. KNOWLEDGE WORKER

| Aspect | Value |
|--------|-------|
| Authority | Learn from BAG, compute knowledge entities |
| Responsibility | Academy, Oracle, Darwin, Librarian computation |
| Input | BAG artifacts, trade_markers, snapshots |
| Output | academy_artifacts, oracle_match, darwin_proposals, librarian_events |
| Dependency | KNOWLEDGE layer, BAG |
| Execution Order | After BAG, before PREDICTION |
| Thread | Separate (cold) |
| Timeout | 300s |
| Fallback | Sequential on main thread |
| Forbidden | IndexedDB write, SQLite write, Core write, grouping (BAG does that) |

---

## 9. PREDICTION WORKER

| Aspect | Value |
|--------|-------|
| Authority | N/A — Prediction is main thread only |
| Responsibility | N/A — Prediction is lightweight aggregation |
| Input | N/A |
| Output | N/A |
| Dependency | N/A |
| Execution Order | N/A |
| Note | **Prediction is NOT a separate worker.** Lightweight aggregation on main thread. |

---

## 10. GOVERNANCE WORKER

| Aspect | Value |
|--------|-------|
| Authority | N/A — Governance is main thread only |
| Responsibility | N/A — Governance decisions require human interaction |
| Input | N/A |
| Output | N/A |
| Dependency | N/A |
| Execution Order | N/A |
| Note | **Governance is NOT a worker.** Requires human approval. WASIT benchmark uses Benchmark Worker. |

---

## 11. SIMULATION WORKER

| Aspect | Value |
|--------|-------|
| Authority | N/A — Simulation orchestrates main thread pipeline |
| Responsibility | N/A — Simulation state management is on main thread |
| Input | N/A |
| Output | N/A |
| Dependency | N/A |
| Execution Order | N/A |
| Note | **Simulation is NOT a separate worker.** Orchestrates main thread pipeline execution. Replay uses Replay Worker. |

---

## 12. BENCHMARK WORKER

| Aspect | Value |
|--------|-------|
| Authority | Evaluate config changes via WASIT walk-forward |
| Responsibility | Parallel WASIT 5-gate walk-forward validation |
| Input | Base markers, candidate markers, fold count |
| Output | WASIT result (gates, per_fold, verdict) |
| Dependency | BENCHMARK layer |
| Execution Order | ON-DEMAND — when governance proposal needs evaluation |
| Thread | Separate (cold) — parallel base vs candidate |
| Timeout | 300s |
| Fallback | Sequential on main thread (deterministic) |
| Forbidden | IndexedDB write, SQLite write, approve proposals |

---

## 13. DASHBOARD WORKER

| Aspect | Value |
|--------|-------|
| Authority | N/A — Dashboard is UI rendering on main thread |
| Responsibility | N/A — UI must be on main thread |
| Input | N/A |
| Output | N/A |
| Dependency | N/A |
| Execution Order | N/A |
| Note | **Dashboard is NOT a worker.** UI rendering on main thread. Long queries use Query Worker. |

---

## 14. INTEGRATION WORKER (Replay Worker)

| Aspect | Value |
|--------|-------|
| Authority | Replay snapshots deterministically |
| Responsibility | Parallel replay across symbols |
| Input | Snapshot sequences from IndexedDB |
| Output | Replay frames |
| Dependency | REPLAY layer |
| Execution Order | On-demand — when user requests replay |
| Thread | Separate (cold) — parallel across symbols |
| Timeout | 600s |
| Fallback | Sequential on main thread |
| Forbidden | IndexedDB write, SQLite write, modify cards |

---

## WORKER EXECUTION ORDER

```
1. Data Worker        — MARKET batch processing (cold, dies after)
2. (Main Thread)      — TRUTH, STRUCTURE, EVIDENCE (hot, sequential)
3. (Main Thread)      — CLONE, TRADE, POSITION (hot, PER-CLONE)
4. (Main Thread)      — STATISTICS (lightweight aggregation)
5. Knowledge Worker   — BAG + KNOWLEDGE (cold, batch, dies after)
6. (Main Thread)      — PREDICTION, GOVERNANCE (lightweight)
7. Benchmark Worker   — WASIT evaluation (cold, on-demand, dies after)
8. Replay Worker      — Replay across symbols (cold, on-demand, dies after)
9. (Main Thread)      — DASHBOARD, CONSUMER (UI, terminal)
```

---

## WORKER CONTRACT STATUS: LOCKED

All 14 worker contracts are constitutionally frozen. Only 4 workers are actual separate-thread workers (Data, Knowledge/BAG, Benchmark, Replay). Truth, Structure, Trading, Prediction, Governance, Dashboard are main-thread only. Each worker defines authority, responsibility, input, output, dependency, execution order, timeout, fallback, and forbidden operations. No new worker may be created without Architecture Approval.
# 05_REGISTRY_CONTRACT.md

## ST-LMS Implementation Contract Freeze V1 — Registry Contract

**Date:** 2026-07-28
**Status:** CONSTITUTIONALLY FROZEN
**Audit:** Registries sourced from existing frozen documents.

---

## 1. LAYER REGISTRY

**Source:** 01_ARCHITECTURE_FREEZE.md S2

| # | Layer | Type | Mandatory | Pipeline Stage |
|---|-------|------|-----------|---------------|
| 1 | BOOT | ONCE | YES | 0 |
| 2 | WORKSPACE | FOUNDATION | YES | — |
| 3 | SQLITE FOUNDATION | FOUNDATION | YES | — |
| 4 | MARKET | SHARED | YES | 1 |
| 5 | TRUTH | SHARED | YES | 2 |
| 6 | DISTANCE | LOGICAL SUB-LAYER | YES | 2-3 |
| 7 | STRUCTURE | SHARED | YES | 3 |
| 8 | EVIDENCE | SHARED | YES | 4 |
| 9 | CLONE | PER-CLONE x3 | YES | 5 |
| 10 | TRADE | PER-CLONE x3 | YES | 6,9,10,11 |
| 11 | POSITION | PER-CLONE x3 | YES | 7,8 |
| 12 | STATISTICS | SHARED-AGAIN | YES | 12 |
| 13 | BAG | SHARED-AGAIN | YES | 13 |
| 14 | KNOWLEDGE | SHARED-AGAIN | YES | 14,16-20 |
| 15 | PREDICTION | SHARED-AGAIN | YES | 21 |
| 16 | TRADING SCHEMA | SHARED-AGAIN | YES | — (blueprint) |
| 17 | GOVERNANCE | SHARED-AGAIN | YES | 22 |
| 18 | BENCHMARK | ON-DEMAND | YES | 15 |
| 19 | CONSUMER | OPTIONAL | NO | — |
| 20 | SNAPSHOT | CROSS-CUTTING | YES | — |
| 21 | SIMULATION | CROSS-CUTTING | YES | — |
| 22 | REPLAY | CROSS-CUTTING | YES | — |
| 23 | DASHBOARD | CROSS-CUTTING | YES | — |
| 24 | AUDIT | CROSS-CUTTING | YES | — |
| 25 | INTEGRATION | CROSS-CUTTING | YES | — |
| 26 | FINAL VALIDATION | CROSS-CUTTING | YES | — |

**Total: 26 layers**

---

## 2. COMPONENT REGISTRY

**Source:** 03_COMPONENT_CONTRACT.md, 02_ARTIFACT_REGISTRY.md

| Category | Components | Count |
|----------|-----------|-------|
| TRUTH | PointBuilder, Supertrend, ATR, EMA, MACD, RSI, W%R, Volume Delta, Flip Detector | 9 |
| DISTANCE | Distance-to-ST, Distance-Ceiling, Distance-Floor, ST_DIST_VOL, Distance Fingerprint, Distance Bucket, Distance Trend, Distance Velocity | 8 |
| STRUCTURE | LineBuilder, SlopeBuilder, WaveBuilder, CageEngine, Ladder, Nearest, Phase | 7 |
| TRADING | LONG Clone, SHORT Clone, GRID Clone, Entry Corridor, Entry Marker, Exit Marker, Position Manager, Exit Decider, Fee Calculator, Global Risk, Grid Evaluator, Wrong Entry Guard | 12 |
| STATISTICS | TradeStats, MarketStats, Sample Gate | 3 |
| BAG | Grouper, Classifier, Pattern Miner, Fingerprint Generator, Consensus Engine, Conflict Detector, Maturity Assessor, Behavior Analyzer, Compressor, Sequence Analyzer, Temporal Analyzer | 11 |
| KNOWLEDGE | Academy, Oracle, HiveMind, CERMIN, Librarian, Darwin, River | 7 |
| PREDICTION | Summarizer, Empirical Agg, Similarity Agg, Intelligence Agg | 4 |
| BENCHMARK | WASIT 5-Gate, Fold Metrics, Walk-Forward, Parallel Worker | 4 |
| DASHBOARD | Geometry Viewer, Clone Cards, Trade History, Equity Curve, Rapor Table, Academy Table, Knowledge Panels, Governance UI, Replay Viewer, Prediction Panel, Consumer Panel, Audit Panel, SQLite Viewer, SQLite Manager, Query Console | 15 |
| INTEGRATION | Pipeline Orchestrator, Worker Bridge, Card Sharing Enforcer, Unidirectional Guard, Serial Writer, Resource Governor | 6 |

**Total: 86 components across 11 categories**

---

## 3. WORKER REGISTRY

**Source:** 04_WORKER_CONTRACT.md

| # | Worker | Type | Thread | Lifecycle |
|---|--------|------|--------|-----------|
| 1 | Data Worker | Actual Worker | Separate | Cold |
| 2 | Knowledge Worker (BAG + Knowledge) | Actual Worker | Separate | Cold |
| 3 | Benchmark Worker | Actual Worker | Separate | Cold |
| 4 | Replay Worker | Actual Worker | Separate | Cold |
| 5 | Query Worker | SQLite Worker | Separate | Cold |
| 6 | Import Worker | SQLite Worker | Separate | Cold |
| 7 | Export Worker | SQLite Worker | Separate | Cold |
| 8 | Backup Worker | SQLite Worker | Separate | Cold |
| 9 | Integrity Worker | SQLite Worker | Separate | Cold |
| — | TRUTH | Main Thread Only | Main | Hot |
| — | STRUCTURE | Main Thread Only | Main | Hot |
| — | EVIDENCE | Main Thread Only | Main | Hot |
| — | CLONE/TRADE/POSITION | Main Thread Only | Main | Hot |
| — | STATISTICS | Main Thread | Main | Hot |
| — | PREDICTION | Main Thread | Main | Hot |
| — | GOVERNANCE | Main Thread | Main | Hot |
| — | DASHBOARD | Main Thread | Main | Hot |

**Total: 9 actual workers (4 ST-LMS + 5 SQLite), 8 main-thread-only layers**

---

## 4. ARTIFACT REGISTRY

**Source:** 02_ARTIFACT_REGISTRY.md

| Layer | Artifacts |
|-------|----------|
| MARKET | 5 |
| TRUTH | 15 |
| DISTANCE | 13 |
| STRUCTURE | 10 |
| EVIDENCE | 8 |
| CLONE | 7 |
| TRADE | 8 |
| POSITION | 5 |
| STATISTICS | 8 |
| BAG | 10 |
| KNOWLEDGE | 8 |
| PREDICTION | 7 |
| TRADING SCHEMA | 6 |
| GOVERNANCE | 5 |
| BENCHMARK | 4 |
| SIMULATION | 3 |
| REPLAY | 2 |
| DASHBOARD | 15 |
| INTEGRATION | 2 |
| FINAL VALIDATION | 4 |
| **TOTAL** | **145** |

---

## 5. SQLite REGISTRY

**Source:** STLMS_SQLITE_SCHEMA_V1.sql, 01_ARCHITECTURE_FREEZE.md S6

| Layer Group | Tables | Count |
|------------|--------|-------|
| CORE METADATA | app_sessions, symbols, timeframes, pipeline_runs | 4 |
| MARKET | market_candles, market_metadata, open_interest_series, market_gaps | 4 |
| TRUTH | truth_snapshots, truth_cache | 2 |
| STRUCTURE | structure_snapshots, wave_history, cage_history | 3 |
| EVIDENCE | evidence_snapshots | 1 |
| CLONE | clones, clone_observations | 2 |
| TRADE | trade_markers | 1 |
| POSITION | positions, position_timeline | 2 |
| STATISTICS | trade_statistics, market_statistics | 2 |
| BAG | bag_artifacts, bag_patterns, bag_compression | 3 |
| KNOWLEDGE | knowledge_artifacts | 1 |
| PREDICTION | predictions, prediction_results | 2 |
| GOVERNANCE | governance_proposals, governance_logs, rollback_logs | 3 |
| REPLAY | replay_sessions, replay_frames | 2 |
| BENCHMARK | benchmark_runs, benchmark_cases | 2 |
| AUDIT | audit_logs, audit_issues | 2 |
| SETTINGS | app_settings, domain_dictionary | 2 |
| UTILITY | purge_jobs, row_lifecycle | 2 |
| **TOTAL** | | **40** |

**Indexes:** 9 | **Triggers:** 4 | **FKs:** 49 | **CHECKs:** 31 | **UNIQUEs:** 19

---

## 6. SNAPSHOT REGISTRY

**Source:** 01_ARCHITECTURE_FREEZE.md S7

| # | Snapshot | Producer | W Fields | OD Fields |
|---|----------|----------|----------|-----------|
| 1 | Market | MARKET | All | — |
| 2 | Truth | TRUTH | All | — |
| 3 | Structure | STRUCTURE | cage,wave,ladder,phase,nearest | dist_ceiling, dist_floor |
| 4 | Evidence | EVIDENCE | All | — |
| 5 | Clone | CLONE x3 | All | — |
| 6 | Trade | SIM | All | — |
| 7 | Statistics | STATISTICS | per_clone | All (from Trade) |
| 8 | Knowledge | KNOWLEDGE | All | — |
| 9 | Benchmark | BENCHMARK | All (on-demand) | — |
| 10 | Prediction | PREDICTION | score,bias,no_model | emp_win_rate |

---

## 7. TRADING SCHEMA REGISTRY

**Source:** 03_TRADING_CONSTITUTION.md

| Category | Schemas | Count |
|----------|---------|-------|
| MARKET | TREND, SIDEWAY, RANGE, CHAOS, COMPRESSION, EXPANSION, BREAKOUT, REVERSAL, EXHAUSTION, WARMUP | 10 |
| TRADING | LONG, SHORT, GRID, NO TRADE, WAIT, HOLD, SKIP | 7 |
| ENTRY | LONG/SHORT CONTINUATION/PULLBACK/BREAKOUT/REVERSAL, GRID COMPRESSION/RANGE/EXPANSION | 11 |
| POSITION | ADD POSITION, PARTIAL TP, TRAILING TP, BREAKEVEN, TIME EXIT, WRONG ENTRY, LOCK PROFIT | 7 |
| EXIT | SL, TP, EXIT BUS, MANUAL EXIT, TIME EXIT, EARLY EXIT | 6 |
| **TOTAL** | | **41** |

---

## 8. DECISION TREE REGISTRY

**Source:** 02_DECISION_TREE_CONTRACT.md, DECISION_TREE_FREEZE.md

| # | Decision Tree | Producer | Consumer |
|---|--------------|----------|----------|
| 1 | Trading Decision Tree | TRADE | CLONE |
| 2 | Entry Decision Tree (11 schemas) | TRADE | CLONE |
| 3 | Exit Decision Tree (8 priorities) | TRADE | CLONE |
| 4 | Position Decision Tree (7 schemas) | POSITION | CLONE |
| 5 | Prediction Decision Tree | PREDICTION | TRADING SCHEMA, CONSUMER |
| 6 | Governance Decision Tree | GOVERNANCE | BENCHMARK, CONSUMER |
| 7 | Simulation Decision Tree | SIMULATION | REPLAY, AUDIT |
| 8 | Benchmark Decision Tree | BENCHMARK | GOVERNANCE |

**Total: 8 decision trees**

---

## 9. BENCHMARK REGISTRY

**Source:** 04_BUILD_CONTRACT.md, ST_LMS_CORE.js BENCHMARK

| # | Benchmark | Phase | Target |
|---|-----------|-------|--------|
| 1 | Determinism | Phase-05,12 | 2-run checksum identical |
| 2 | WASIT Identical | Phase-20 | G2 must FAIL |
| 3 | WASIT Tighten Entry | Phase-20 | G1-G5 evaluation |
| 4 | WASIT Tighten Wrong | Phase-20 | G1-G5 evaluation |
| 5 | WASIT Widen Corridor | Phase-20 | G1-G5 evaluation |
| 6 | WASIT Loose Cage | Phase-20 | G1-G5 evaluation |
| 7 | WASIT Tight Cage | Phase-20 | G1-G5 evaluation |
| 8 | Clone Benchmark | Phase-20 | Clone stats compare |
| 9 | Trade Benchmark | Phase-20 | P&L verification |
| 10 | Market Benchmark | Phase-20 | Phase distribution |
| 11 | Query Performance | Phase-01 | <5ms indexed query |
| 12 | Replay Performance | Phase-13 | <500ms/1000 candles |
| 13 | Pipeline Performance | Phase-12 | <100ms/candle |
| 14 | UI Render | Phase-22 | <50ms/panel |

**Total: 14 benchmarks**

---

## REGISTRY CONTRACT STATUS: LOCKED

All 9 registries (Layer, Component, Worker, Artifact, SQLite, Snapshot, Trading Schema, Decision Tree, Benchmark) are constitutionally frozen. Totals: 26 layers, 86 components, 9 workers, 145 artifacts, 40 SQLite tables, 10 snapshots, 41 trading schemas, 8 decision trees, 14 benchmarks. No new registry entry without Architecture Approval.
# 06_BUILD_QUEUE.md

## ST-LMS Implementation Contract Freeze V1 — Build Queue

**Date:** 2026-07-28
**Status:** CONSTITUTIONALLY FROZEN
**Audit:** Build order sourced from 04_BUILD_CONTRACT.md (26 phases). This document formalizes build queue with completion requirements.

---

## BUILD RULE

**LAYER TIDAK BOLEH DILANJUTKAN APABILA:**
- Unit Test gagal
- SQLite Test gagal
- Snapshot Test gagal
- Benchmark Test gagal
- Integration Test gagal

---

## BUILD QUEUE

### PHASE 0: SPECIFICATION FREEZE (COMPLETE)

**Status:** DONE
**Output:** All freeze documents, enrichment reports, architecture mapping, freeze contracts

---

### Phase-01: SQLite Foundation

| Aspect | Value |
|--------|-------|
| Dependency | None |
| Required Tests | Schema syntax, table creation (40 tables), index creation (9 indexes), trigger creation (4 triggers), seed data verification, integrity_check, foreign_key_check |
| Benchmark | Query performance < 5ms for indexed queries |
| Output | schema.sql, seed.sql, indexes.sql |
| Completion | All 40 tables created, all constraints enforced, all seed data inserted, integrity_check PASS |

---

### Phase-02: BOOT + Workspace + Checkpoint

| Aspect | Value |
|--------|-------|
| Dependency | Phase-01 |
| Required Tests | Namespace initialization (26 namespaces), IndexedDB open, card storage + retrieval, card verification (SHA-256), workspace reset |
| Benchmark | — |
| Output | boot.js, workspace.js, checkpoint.js |
| Completion | All 26 namespaces initialized, IndexedDB functional, cards stored and verified |

---

### Phase-03: Config + Bounded Registry

| Aspect | Value |
|--------|-------|
| Dependency | Phase-02 |
| Required Tests | Bounded get/set/valid, bounded auto-reject (OUT_OF_RANGE), config reset to defaults |
| Benchmark | — |
| Output | config.js, bounded_registry.js |
| Completion | All 24 bounded parameters registered, auto-reject working, reset functional |

---

### Phase-04: Market Layer

| Aspect | Value |
|--------|-------|
| Dependency | Phase-03 |
| Required Tests | Fixture generation, hygiene validation (valid + invalid), gap detection, OI proxy, market_snapshot card |
| Benchmark | — |
| Output | market.js, data.worker.js, market.test.js |
| Completion | market_snapshot produced correctly, hygiene catches invalid candles, gaps detected |

---

### Phase-05: Truth Layer

| Aspect | Value |
|--------|-------|
| Dependency | Phase-04 |
| Required Tests | Supertrend, ATR, EMA, MACD, RSI, W%R, velocity/acceleration, distance, flip detection, WARMUP state, truth_snapshot |
| Benchmark | Determinism: 2-run checksum identical |
| Output | truth.js, truth.test.js |
| Completion | All indicators accurate, WARMUP handled correctly, determinism verified |

---

### Phase-06: Distance Metrics

| Aspect | Value |
|--------|-------|
| Dependency | Phase-05 |
| Required Tests | dist, distAtr, dist_ceiling, dist_floor, ST_DIST_VOL, distance bucket classification |
| Benchmark | — |
| Output | distance.js, distance.test.js |
| Completion | All distance metrics correct, NULL on appropriate conditions, buckets classified correctly |

---

### Phase-07: Structure Layer

| Aspect | Value |
|--------|-------|
| Dependency | Phase-05 |
| Required Tests | Line building (>=4 members), slope building, wave classification (all 13), wave<6=PENDING, HUKUM CAGE (1 wall=NONE, 2 walls=VALID/LOOSE), cage versioning, escape path, market phase, structure_snapshot |
| Benchmark | — |
| Output | structure.js, structure.test.js |
| Completion | All 13 wave structures reachable, HUKUM CAGE enforced, structure_snapshot complete |

---

### Phase-08: Evidence Layer

| Aspect | Value |
|--------|-------|
| Dependency | Phase-05, 07 |
| Required Tests | Direction Bus, Exit Bus, Correction Bus, bus sterility (W%R not in dir_bus), OI insufficient, MTF sector, evidence_snapshot |
| Benchmark | — |
| Output | evidence.js, evidence.test.js |
| Completion | 3 buses separated correctly, W%R/MACD not in Direction Bus, evidence_snapshot complete |

---

### Phase-09: Clone Layer

| Aspect | Value |
|--------|-------|
| Dependency | Phase-07, 08 |
| Required Tests | LONG/SHORT/GRID observation (1 per candle each), 3 obs/candle, no-trade reason, entry conjunction, Card Sharing verification |
| Benchmark | — |
| Output | clone.js, long_clone.js, short_clone.js, grid_clone.js, clone.test.js |
| Completion | 3 observations per candle mandatory, entry conjunction correct, Card Sharing verified |

---

### Phase-10: Trade Layer

| Aspect | Value |
|--------|-------|
| Dependency | Phase-09 |
| Required Tests | Entry marker, exit marker, P&L LONG/SHORT, WIN/LOSS condition, fee layered, adverse-first, GRID fills management |
| Benchmark | — |
| Output | trade.js, trade.test.js |
| Completion | P&L correct, adverse-first enforced, fee calculation correct, WIN only net>0 |

---

### Phase-11: Position Layer

| Aspect | Value |
|--------|-------|
| Dependency | Phase-10 |
| Required Tests | Position update (hold_c, mae, mfe), exit decision priority, wrong entry early/geom, SL hit, TP hit, HOLD-veto, TIME_EXIT |
| Benchmark | — |
| Output | position.js, position.test.js |
| Completion | MAE/MFE tracked correctly, exit priority enforced, HOLD-veto working |

---

### Phase-12: Simulation Engine

| Aspect | Value |
|--------|-------|
| Dependency | Phase-09, 10, 11 |
| Required Tests | freshState, process (1 candle), computeAll (all candles), pipeline stages (22), Card Sharing, full pipeline integration |
| Benchmark | Determinism: 2-run hash identical, Pipeline performance < 100ms/candle |
| Output | simulation.js, simulation.test.js |
| Completion | Full pipeline executes correctly, 22 stages in order, determinism verified |

---

### Phase-13: Replay Engine

| Aspect | Value |
|--------|-------|
| Dependency | Phase-12 |
| Required Tests | Candle replay, snapshot replay, trade replay, clone replay, knowledge replay, governance replay, replay bit-per-bit determinism |
| Benchmark | Replay performance < 500ms for 1000 candles |
| Output | replay.js, replay.test.js |
| Completion | All 6 replay types working, bit-per-bit determinism verified |

---

### Phase-14: Statistics Layer

| Aspect | Value |
|--------|-------|
| Dependency | Phase-10, 11 |
| Required Tests | Trade stats per clone, sample gate (>=30=CUKUP), win_rate, expectancy, PF, fee_drag, wrong_rate accuracy |
| Benchmark | — |
| Output | statistics.js, statistics.test.js |
| Completion | All metrics accurate, sample gate enforced, BELUM_CUKUP below threshold |

---

### Phase-15: BAG Layer

| Aspect | Value |
|--------|-------|
| Dependency | Phase-14 |
| Required Tests | Grouping (bag_key unique), classification (6 bag_kind), consensus, conflict, pattern mining, fingerprint (12 dimensions), compression, no write-back to upstream |
| Benchmark | — |
| Output | bag.js, bag.test.js |
| Completion | BAG artifacts produced, patterns detected, fingerprints generated, no upstream writes |

---

### Phase-16: Knowledge Layer

| Aspect | Value |
|--------|-------|
| Dependency | Phase-15 |
| Required Tests | Academy (4-dim bucket, sample-gated), Oracle (euclidean, match>7500, W%R/MACD not in vector), HiveMind (score 0-10000, currentEvidence from snapshot), CERMIN (calibration), Librarian (6 statuses), Darwin (proposals, no auto-execute), River (chronicle), unidirectional, no-ML |
| Benchmark | — |
| Output | knowledge.js, knowledge.test.js |
| Completion | All 7 entities working, unidirectional enforced, no-ML verified |

---

### Phase-17: Prediction Layer

| Aspect | Value |
|--------|-------|
| Dependency | Phase-16 |
| Required Tests | Empirical only (no_model=true), sample gate (BELUM_CUKUP->NULL), intelligence score 0-10000, no forecast model |
| Benchmark | — |
| Output | prediction.js, prediction.test.js |
| Completion | no_model=true always, empirical only, BELUM_CUKUP handled correctly |

---

### Phase-18: Trading Schema Layer

| Aspect | Value |
|--------|-------|
| Dependency | Phase-17 |
| Required Tests | 10 market schemas, 7 trading schemas, 11 entry schemas, 7 position schemas, 6 exit schemas, schema completeness (all required fields), no spec override |
| Benchmark | — |
| Output | trading_schema.js, trading_schema.test.js |
| Completion | All 41 schemas defined with complete fields, no specification override |

---

### Phase-19: Governance Layer

| Aspect | Value |
|--------|-------|
| Dependency | Phase-16, 18 |
| Required Tests | 6 validations, proposal lifecycle, bounded auto-reject, rollback deterministik, no auto-execute, no Core write |
| Benchmark | — |
| Output | governance.js, governance.test.js |
| Completion | All 6 validations working, bounded auto-reject enforced, rollback functional |

---

### Phase-20: Benchmark Layer

| Aspect | Value |
|--------|-------|
| Dependency | Phase-12, 19 |
| Required Tests | WASIT 5-gate, identical->G2 FAIL, majority vote, parallel worker, fallback sequential |
| Benchmark | WASIT Identical, WASIT Tighten Entry/Wrong/Corridor/Cage |
| Output | benchmark.js, benchmark.worker.js, benchmark.test.js |
| Completion | WASIT 5-gate functional, identical fails G2, parallel worker works |

---

### Phase-21: Consumer Layer

| Aspect | Value |
|--------|-------|
| Dependency | Phase-17, 19 |
| Required Tests | Fund evaluation, veto gate, intent builder, CSV export, live adapter disabled |
| Benchmark | — |
| Output | consumer.js, consumer.test.js |
| Completion | Trade intent built correctly, veto gate functional, live adapter disabled |

---

### Phase-22: Dashboard Layer

| Aspect | Value |
|--------|-------|
| Dependency | Phase-21 |
| Required Tests | No-mock render (empty=N/A), geometry chart, clone cards (3), trade history, equity curve, all panels (20+), read-only (no logic compute) |
| Benchmark | UI render < 50ms per panel |
| Output | dashboard.html, view.js, view.css |
| Completion | All panels render without mock data, all read-only from cards |

---

### Phase-23: Integration Layer

| Aspect | Value |
|--------|-------|
| Dependency | Phase-22 |
| Required Tests | Worker bridge (postMessage), pipeline orchestration (22 stages), Card Sharing (SHARED 1x, PER-CLONE 3x), serial writer, worker no-direct-DB |
| Benchmark | — |
| Output | integration.js, worker_bridge.js |
| Completion | All workers communicate via postMessage, pipeline orchestrated correctly |

---

### Phase-24: Audit Layer

| Aspect | Value |
|--------|-------|
| Dependency | Phase-23 |
| Required Tests | 16 self-tests (all PASS), 6 domain audits (Pipeline, Snapshot, Clone, Trade, Knowledge, Governance), fingerprint |
| Benchmark | — |
| Output | audit.js, audit.test.js |
| Completion | All self-tests PASS, all domain audits PASS, fingerprint deterministic |

---

### Phase-25: Final Validation

| Aspect | Value |
|--------|-------|
| Dependency | Phase-24 |
| Required Tests | 12-domain check (Runtime, Pipeline, Namespace, Feature, Truth, Clone, Trading, Knowledge, Replay, Governance, Constitution, Console Error) |
| Benchmark | — |
| Output | final_validation.js |
| Completion | All 12 checks PASS |

---

### Phase-26: BUILD APPROVAL

| Aspect | Value |
|--------|-------|
| Dependency | Phase-25 |
| Required Tests | 15 stop-rule PASS, 18 LAW-MASTER compliant, determinism verified, no spec conflict, no missing component |
| Benchmark | — |
| Output | approval_report.md |
| Completion | BUILD APPROVED — system ready for production |

---

## BUILD QUEUE STATUS: LOCKED

All 26 build phases are constitutionally frozen with dependencies, required tests, benchmark requirements, output requirements, and completion requirements. LAYER TIDAK BOLEH DILANJUTKAN APABILA TEST GAGAL. Every HARD gate must PASS before proceeding.
