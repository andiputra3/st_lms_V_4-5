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
