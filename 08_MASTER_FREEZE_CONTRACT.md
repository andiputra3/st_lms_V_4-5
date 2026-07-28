# 01_ARCHITECTURE_FREEZE.md

## ST-LMS Final Freeze Contract V1 — Architecture Freeze

**Date:** 2026-07-28
**Status:** CONSTITUTIONALLY FROZEN — FINAL
**Sources:** MASTER_SPECIFICATION.html, DOCUMENT_DEPENDENCY.html, QWEN_14_DOC.html, ST_LMS_CORE.js, STLMS_SQLITE_SCHEMA_V1.sql, ENRICHMENT_REPORT_V1.md

---

## 1. 22 PIPELINE STAGES (FROZEN)

```
STAGE  TYPE              NAME                    DESCRIPTION
─────  ────────────────  ──────────────────────  ──────────────────────────────
 0     ONCE              BOOT                    Establish system physics
 1     SHARED            MARKET OBSERVATION      Quarantine/canonize candle
 2     SHARED            TRUTH LAYER             Pure geometry computation
 3     SHARED            STRUCTURE LAYER         Cage/wave/ladder/phase
 4     SHARED            EVIDENCE LAYER          3-bus witness system
       ═══════════════════════════════════════════════════════════════════════
 5     PER-CLONE x3      CLONE OBSERVATION       Record hypothesis (mandatory)
 6     PER-CLONE x3      ENTRY VALIDATION        Conjunction gate check
 7     PER-CLONE x3      POSITION MGMT           Manage live position
 8     PER-CLONE x3      PROFIT MGMT             Secure profit adaptively
 9     PER-CLONE x3      EXIT VALIDATION         Decide close and why
10     PER-CLONE x3      CLOSE POSITION          After-fee adverse-first
11     PER-CLONE x3      TRADE MARKER            Aggregate markers
       ═══════════════════════════════════════════════════════════════════════
12     SHARED-AGAIN      STATISTICS              Aggregate (sample-gated)
13     SHARED-AGAIN      BAG                     Grouped classification
14     SHARED-AGAIN      RIVER (KNOWLEDGE)       Append-only archivist
15     ON-DEMAND         BENCHMARK               WASIT 5-gate (not per candle)
16     SHARED-AGAIN      ACADEMY (KNOWLEDGE)     Empirical win_rate per bucket
17     SHARED-AGAIN      ORACLE (KNOWLEDGE)      Similarity matching
18     SHARED-AGAIN      HIVEMIND (KNOWLEDGE)    Market understanding
19     SHARED-AGAIN      CERMIN (KNOWLEDGE)      Calibration error
20     SHARED-AGAIN      DARWIN (KNOWLEDGE)      Parameter proposals
21     SHARED-AGAIN      PREDICTION              Empirical + similarity
22     SHARED-AGAIN      GOVERNANCE              Rem and kemudi
       ═══════════════════════════════════════════════════════════════════════
OPT    OPTIONAL          CONSUMER                Trade intent (live DISABLED)
```

**INVARIANT:** Stages 1-4 are SHARED (1x compute, 3x share). Stages 5-11 are PER-CLONE (3x, isolated sub-ledgers). Stages 12-22 are SHARED-AGAIN (1x, card-agnostic). Stage 15 is ON-DEMAND (not per candle). CONSUMER is OPTIONAL (terminal).

---

## 2. LOGICAL LAYERS (FROZEN)

### 2.1 Layer Registry (26 Layers)

| # | Layer | Type | Pipeline Stage | Mandatory |
|---|-------|------|---------------|-----------|
| 1 | BOOT | ONCE | 0 | YES |
| 2 | WORKSPACE | FOUNDATION | — | YES |
| 3 | SQLITE FOUNDATION | FOUNDATION | — | YES |
| 4 | MARKET | SHARED | 1 | YES |
| 5 | TRUTH | SHARED | 2 | YES |
| 6 | DISTANCE | LOGICAL SUB-LAYER | 2-3 | YES |
| 7 | STRUCTURE | SHARED | 3 | YES |
| 8 | EVIDENCE | SHARED | 4 | YES |
| 9 | CLONE | PER-CLONE x3 | 5 | YES |
| 10 | TRADE | PER-CLONE x3 | 6,9,10,11 | YES |
| 11 | POSITION | PER-CLONE x3 | 7,8 | YES |
| 12 | STATISTICS | SHARED-AGAIN | 12 | YES |
| 13 | BAG | SHARED-AGAIN | 13 | YES |
| 14 | KNOWLEDGE | SHARED-AGAIN | 14,16-20 | YES |
| 15 | PREDICTION | SHARED-AGAIN | 21 | YES |
| 16 | TRADING SCHEMA | SHARED-AGAIN | — (blueprint) | YES |
| 17 | GOVERNANCE | SHARED-AGAIN | 22 | YES |
| 18 | BENCHMARK | ON-DEMAND | 15 | YES |
| 19 | CONSUMER | OPTIONAL | — | NO |
| 20 | SNAPSHOT | CROSS-CUTTING | — | YES |
| 21 | SIMULATION | CROSS-CUTTING | — | YES |
| 22 | REPLAY | CROSS-CUTTING | — | YES |
| 23 | DASHBOARD | CROSS-CUTTING | — | YES |
| 24 | AUDIT | CROSS-CUTTING | — | YES |
| 25 | INTEGRATION | CROSS-CUTTING | — | YES |
| 26 | FINAL VALIDATION | CROSS-CUTTING | — | YES |

### 2.2 Layer Hierarchy

```
FOUNDATION:    BOOT -> WORKSPACE -> SQLITE FOUNDATION
SHARED:        MARKET -> TRUTH -> DISTANCE(logical) -> STRUCTURE -> EVIDENCE
PER-CLONE x3:  CLONE -> TRADE -> POSITION
SHARED-AGAIN:  STATISTICS -> BAG -> KNOWLEDGE -> PREDICTION -> TRADING SCHEMA -> GOVERNANCE
ON-DEMAND:     BENCHMARK
OPTIONAL:      CONSUMER
CROSS-CUTTING: SNAPSHOT, SIMULATION, REPLAY, DASHBOARD, AUDIT, INTEGRATION, FINAL VALIDATION
```

---

## 3. LAYER AUTHORITY (FROZEN)

| Layer | READ FROM | WRITE TO | FORBIDDEN |
|-------|-----------|----------|-----------|
| BOOT | Config | All namespaces | — |
| WORKSPACE | — | IndexedDB (serial) | — |
| SQLITE | — | All tables | — |
| MARKET | Raw candle | market_snapshot | TRUTH |
| TRUTH | market_snapshot | truth_snapshot | STRUCTURE |
| DISTANCE | truth + structure | distance metrics | TRADE |
| STRUCTURE | truth_snapshot | structure_snapshot | TRUTH |
| EVIDENCE | truth + structure | evidence_snapshot | TRUTH |
| CLONE | shared snapshots | clone_observation | TRUTH |
| TRADE | clone_obs | trade_markers | CLONE |
| POSITION | trade_markers | position_state | CLONE |
| STATISTICS | trade_markers | statistics_snapshot | TRADE |
| BAG | statistics + snapshot | bag_artifacts | TRUTH, CORE |
| KNOWLEDGE | BAG + statistics | knowledge_snapshot | CORE, CLONE |
| PREDICTION | knowledge | prediction_snapshot | CORE |
| TRADING SCHEMA | prediction + BAG | schema_definitions | CORE |
| GOVERNANCE | knowledge + BAG | config_version (BOUNDED) | CORE, TRUTH |
| BENCHMARK | trade_markers | benchmark_snapshot | CORE |
| CONSUMER | prediction | trade_intent | CORE |

**AUTHORITY RULES:**
1. UNIDIRECTIONAL: Data flows one way. No backward loops to Core.
2. CARD SHARING: Truth/Structure/Evidence 1x -> shared to 3 clones.
3. NO GEOMETRY RECOMPUTE: Only TRUTH computes geometry from OHLCV.
4. NO INDICATOR OVERRIDE: Indicators used only per Authority Matrix.
5. BOUNDED ONLY: GOVERNANCE writes only to BOUNDED parameters.
6. WORKERS VIA POSTMESSAGE: Workers do NOT access IndexedDB directly.
7. SERIAL WRITER: Single writer on main thread.

---

## 4. DEPENDENCY MATRIX (FROZEN)

| UPSTREAM | DOWNSTREAM |
|----------|------------|
| BOOT | All layers |
| WORKSPACE | All layers (storage) |
| SQLITE FOUNDATION | All layers (persistence) |
| MARKET | TRUTH |
| TRUTH | STRUCTURE, EVIDENCE, DISTANCE |
| DISTANCE | CLONE, BAG, KNOWLEDGE, TRADING SCHEMA |
| STRUCTURE | EVIDENCE, CLONE |
| EVIDENCE | CLONE, HIVEMIND |
| CLONE | TRADE |
| TRADE | POSITION, STATISTICS |
| POSITION | STATISTICS |
| STATISTICS | BAG |
| BAG | KNOWLEDGE, PREDICTION, TRADING SCHEMA |
| KNOWLEDGE | PREDICTION, GOVERNANCE |
| PREDICTION | TRADING SCHEMA, CONSUMER |
| TRADING SCHEMA | GOVERNANCE |
| GOVERNANCE | BENCHMARK, CONSUMER |
| BENCHMARK | GOVERNANCE (verdict) |
| CONSUMER | — (terminal) |

**FORBIDDEN DEPENDENCIES (BUILD STOP):**
- KNOWLEDGE -> CORE/CLONE (backward loop)
- CONSUMER -> CORE/CLONE (backward loop)
- BAG -> TRUTH/STRUCTURE (upstream write)
- GOVERNANCE -> TRUTH/STRUCTURE (except BOUNDED params)
- WORKER -> INDEXEDDB (direct write)
- CLONE -> ORACLE/HIVEMIND (direct read)
- TRADE -> W%R/MACD/RSI for entry (authority violation)
- GRID -> stDir/MTF (authority violation)
- DARWIN -> AUTO-EXECUTE (governance violation)
- PREDICTION -> MODEL (constitution violation)

---

## 5. CONSUMER MATRIX (FROZEN)

| ARTIFACT | CONSUMERS |
|----------|-----------|
| market_snapshot | TRUTH, DASHBOARD |
| truth_snapshot | STRUCTURE, EVIDENCE, DISTANCE, CLONE, BAG, KNOWLEDGE, DASHBOARD |
| distance_metrics | CLONE, BAG, KNOWLEDGE, ORACLE, TRADING SCHEMA, DASHBOARD |
| structure_snapshot | EVIDENCE, CLONE, BAG, KNOWLEDGE, TRADING SCHEMA, DASHBOARD |
| evidence_snapshot | CLONE, HIVEMIND, BAG, DASHBOARD |
| clone_observation | TRADE, STATISTICS, BAG, DASHBOARD |
| trade_markers | POSITION, STATISTICS, BAG, KNOWLEDGE, DASHBOARD, REPLAY |
| position_state | STATISTICS, BAG, DASHBOARD |
| statistics_snapshot | BAG, KNOWLEDGE, PREDICTION, BENCHMARK, DASHBOARD |
| bag_artifacts | KNOWLEDGE, PREDICTION, TRADING SCHEMA, BENCHMARK, DASHBOARD |
| knowledge_snapshot | PREDICTION, GOVERNANCE, DASHBOARD |
| prediction_snapshot | TRADING SCHEMA, CONSUMER, DASHBOARD |
| trading_schema_defs | GOVERNANCE, DASHBOARD |
| governance_decisions | BENCHMARK, CONSUMER, DASHBOARD |
| benchmark_snapshot | GOVERNANCE, DASHBOARD |

---

## 6. SQLITE MAPPING (FROZEN)

| LAYER | SQLite TABLES |
|-------|--------------|
| BOOT | app_settings, domain_dictionary |
| WORKSPACE | (IndexedDB — runtime) |
| SQLITE FOUNDATION | All 40 tables (schema owner) |
| MARKET | market_candles, market_metadata, open_interest_series, market_gaps |
| TRUTH | truth_snapshots, truth_cache |
| DISTANCE | (uses truth_snapshots + structure_snapshots) |
| STRUCTURE | structure_snapshots, wave_history, cage_history |
| EVIDENCE | evidence_snapshots |
| CLONE | clones, clone_observations |
| TRADE | trade_markers |
| POSITION | positions, position_timeline |
| STATISTICS | trade_statistics, market_statistics |
| BAG | bag_artifacts, bag_patterns, bag_compression |
| KNOWLEDGE | knowledge_artifacts |
| PREDICTION | predictions, prediction_results |
| TRADING SCHEMA | (definition only — no table) |
| GOVERNANCE | governance_proposals, governance_logs, rollback_logs |
| BENCHMARK | benchmark_runs, benchmark_cases |
| REPLAY | replay_sessions, replay_frames |
| AUDIT | audit_logs, audit_issues |
| INTEGRATION | pipeline_runs |
| UTILITY | purge_jobs, row_lifecycle |
| REFERENCE | symbols, timeframes, app_sessions |

---

## 7. SNAPSHOT MAPPING (FROZEN)

| # | SNAPSHOT | PRODUCER | CONSUMER | W/OD |
|---|----------|----------|----------|------|
| 1 | Market | MARKET | TRUTH | W (all) |
| 2 | Truth | TRUTH | STRUCTURE, EVIDENCE | W (all) |
| 3 | Structure | STRUCTURE | CLONE, GRID | W (cage,wave,ladder,phase,nearest), OD (dist_ceiling, dist_floor) |
| 4 | Evidence | EVIDENCE | CLONE, HIVEMIND | W (all) |
| 5 | Clone | CLONE x3 | STATISTICS | W (all) |
| 6 | Trade | SIM | STATISTICS | W (all) |
| 7 | Statistics | STATISTICS | BAG, KNOWLEDGE | W (per_clone), OD (all from Trade) |
| 8 | Knowledge | KNOWLEDGE | PREDICTION, GOV | W (all) |
| 9 | Benchmark | BENCHMARK | GOVERNANCE | W (all, on-demand) |
| 10 | Prediction | PREDICTION | CONSUMER | W (score,bias,no_model), OD (emp_win_rate) |

---

## 8. BAG POSITION (FROZEN)

```
FINAL POSITION: STATISTICS -> BAG -> KNOWLEDGE
PIPELINE STAGE: 13 (SHARED-AGAIN)

RESPONSIBILITY:
  - Group artifacts from STATISTICS
  - Classify into bag_kind (behavior, market, entry, exit, risk, knowledge)
  - Pattern mining (association, clustering, anomaly)
  - Behavior analysis (market behavior profiles)
  - Distance fingerprint generation
  - Consensus and conflict detection
  - Maturity assessment
  - Compression of redundant artifacts

AUTHORITY:
  READ: trade_statistics, market_statistics, trade_markers, knowledge_artifacts
  WRITE: bag_artifacts, bag_patterns, bag_compression
  FORBIDDEN: truth, structure, evidence, clone, trade, position, governance

CONSUMER:
  KNOWLEDGE (mandatory via bag_id FK)
  PREDICTION, TRADING SCHEMA, BENCHMARK, DASHBOARD (optional)
```

---

## 9. DISTANCE POSITION (FROZEN)

```
FINAL POSITION: LOGICAL SUB-LAYER of TRUTH + STRUCTURE
PIPELINE STAGE: 2-3 (SHARED, produced alongside TRUTH and STRUCTURE)

RESPONSIBILITY:
  - Distance-to-ST (dist, distAtr) from TRUTH (W fields)
  - Distance-Ceiling/Floor from STRUCTURE (OD fields)
  - ST_DIST_VOL (sdv, p90) from EVIDENCE (runtime)
  - Distance Fingerprint (12 dimensions) from BAG (grouping)
  - Distance trend, velocity, acceleration

AUTHORITY:
  PRODUCED BY: TRUTH, STRUCTURE, EVIDENCE, BAG
  FORBIDDEN: Cannot be a separate physical pipeline stage

CONSUMER:
  CLONE, BAG, KNOWLEDGE, PREDICTION, TRADING SCHEMA
```

---

## 10. TRADING SCHEMA POSITION (FROZEN)

```
FINAL POSITION: After PREDICTION, before GOVERNANCE
PIPELINE STAGE: Blueprint layer (not a physical stage)

RESPONSIBILITY:
  - Define 41 trading schemas in 5 categories
  - Map market conditions to trading behavior
  - Define entry/exit/position rules per schema
  - Consume prediction for confidence adjustment

CATEGORIES:
  MARKET SCHEMA (10): TREND, SIDEWAY, RANGE, CHAOS, COMPRESSION, EXPANSION, BREAKOUT, REVERSAL, EXHAUSTION, WARMUP
  TRADING SCHEMA (7): LONG, SHORT, GRID, NO TRADE, WAIT, HOLD, SKIP
  ENTRY SCHEMA (11): LONG/SHORT CONTINUATION/PULLBACK/BREAKOUT/REVERSAL, GRID COMPRESSION/RANGE/EXPANSION
  POSITION SCHEMA (7): ADD POSITION, PARTIAL TP, TRAILING TP, BREAKEVEN, TIME EXIT, WRONG ENTRY, LOCK PROFIT
  EXIT SCHEMA (6): SL, TP, EXIT BUS, MANUAL EXIT, TIME EXIT, EARLY EXIT

AUTHORITY:
  READ: prediction_snapshot, bag_artifacts, knowledge_snapshot
  WRITE: schema_definitions (blueprint only)
  FORBIDDEN: Cannot modify trading logic directly
```

---

## 11. GOVERNANCE POSITION (FROZEN)

```
FINAL POSITION: After TRADING SCHEMA, before BENCHMARK
PIPELINE STAGE: 22 (SHARED-AGAIN)

RESPONSIBILITY:
  - 6 validations (Constitution, Proposal, Authority Matrix, Build, Runtime, Governance Audit)
  - Proposal lifecycle (Darwin -> WASIT -> Human -> apply/rollback)
  - Bounded auto-reject
  - Rollback deterministik
  - Loop ONLY to BOUNDED parameters

AUTHORITY:
  READ: knowledge_snapshot, darwin_proposals, benchmark_snapshot
  WRITE: config_version (BOUNDED parameters only)
  FORBIDDEN: Writing to Core logic, auto-executing proposals

ACTORS:
  Darwin: Propose Kelas-A (bounded) / Kelas-B (PEX); NO auto-execute
  WASIT: 5-gate walk-forward filter; NO approve
  Human: Final approve/reject
  Bounded Registry: Auto-reject out-of-range
  Runtime: Apply config_version at boundary; rollback
```

---

## ARCHITECTURE FREEZE STATUS: LOCKED

All 22 pipeline stages, 26 logical layers, authority matrix, dependency matrix, consumer matrix, SQLite mapping, snapshot mapping, BAG position, Distance position, Trading Schema position, and Governance position are constitutionally frozen. No modification permitted without governance amendment.
# 02_ARTIFACT_REGISTRY.md

## ST-LMS Final Freeze Contract V1 — Artifact Registry

**Date:** 2026-07-28
**Status:** CONSTITUTIONALLY FROZEN — FINAL
**Rule:** NO ARTIFACT WITHOUT OWNER.

---

## ARTIFACT INVENTORY

### MARKET LAYER

| Artifact | Owner | Type | Producer | Consumer | SQLite | Snapshot |
|----------|-------|------|----------|----------|--------|----------|
| market_snapshot | MARKET | Immutable Card | MARKET.process | TRUTH, DASHBOARD | market_candles | Market (W) |
| candle_hygiene_report | MARKET | Validation | MARKET.hygiene | MARKET, AUDIT | — | — |
| gap_report | MARKET | Detection | MARKET.gaps | MARKET, EVIDENCE, AUDIT | market_gaps | — |
| oi_proxy_series | MARKET | Derived Data | MARKET.oiProxy | EVIDENCE, TRUTH | open_interest_series | — |
| data_status | MARKET | Status | MARKET | TRUTH, DASHBOARD | market_candles.data_status | Market (W) |

### TRUTH LAYER

| Artifact | Owner | Type | Producer | Consumer | SQLite | Snapshot |
|----------|-------|------|----------|----------|--------|----------|
| truth_snapshot | TRUTH | Immutable Card | TRUTH.PointBuilder | STRUCTURE, EVIDENCE, DISTANCE, CLONE, BAG, KNOWLEDGE, DASHBOARD | truth_snapshots | Truth (W) |
| truth_point | TRUTH | Internal State | TRUTH.PointBuilder.build | STRUCTURE (LineBuilder) | — | — |
| st | TRUTH | Geometry | TRUTH.PointBuilder | STRUCTURE, DASHBOARD | truth_snapshots.st | Truth (W) |
| stDir | TRUTH | Direction | TRUTH.PointBuilder | CLONE, STRUCTURE, TRADING SCHEMA | truth_snapshots.st_dir | Truth (W) |
| atr | TRUTH | Volatility | TRUTH.PointBuilder | STRUCTURE, CLONE, DISTANCE | truth_snapshots.atr | Truth (W) |
| ema | TRUTH | Trend | TRUTH.PointBuilder | EVIDENCE, CLONE | truth_snapshots.ema | Truth (W) |
| macd_hist | TRUTH | Momentum | TRUTH.PointBuilder | EVIDENCE (HOLD-veto) | truth_snapshots.macd_hist | Truth (W) |
| rsi | TRUTH | Oscillator | TRUTH.PointBuilder | EVIDENCE (exit_bus), DASHBOARD | truth_snapshots.rsi | Truth (W) |
| wpr | TRUTH | Oscillator | TRUTH.PointBuilder | EVIDENCE (exit_bus), DASHBOARD | truth_snapshots.wpr | Truth (W) |
| vel | TRUTH | Momentum | TRUTH.PointBuilder | CLONE (wrong entry), EVIDENCE | — | Truth (W) |
| acc | TRUTH | Momentum | TRUTH.PointBuilder | EVIDENCE (acc_signal) | — | Truth (W) |
| volDelta | TRUTH | Volume | TRUTH.PointBuilder | EVIDENCE (dir_bus), CLONE | truth_snapshots.volume_delta | Truth (W) |
| flip | TRUTH | Event | TRUTH.PointBuilder | BAG, TRADING SCHEMA, DASHBOARD | — | Truth (W) |
| point_status | TRUTH | Status | TRUTH.PointBuilder | CLONE, DASHBOARD | truth_snapshots.truth_status | Truth (W) |
| truth_cache | TRUTH | Cache | TRUTH | TRUTH (internal) | truth_cache | — |

### DISTANCE LAYER (Logical Sub-Layer)

| Artifact | Owner | Type | Producer | Consumer | SQLite | Snapshot |
|----------|-------|------|----------|----------|--------|----------|
| dist | TRUTH | Distance | TRUTH.PointBuilder | DASHBOARD, BAG | truth_snapshots.dist_to_st | Truth (W) |
| distAtr | TRUTH | Distance | TRUTH.PointBuilder | CLONE, EVIDENCE, BAG, KNOWLEDGE, ORACLE | truth_snapshots.dist_atr | Truth (W) |
| dist_ceiling | STRUCTURE | Distance | EVIDENCE.correctionBus | CLONE (LONG: fee_safe), BAG | structure_snapshots.dist_ceiling | Structure (OD) |
| dist_floor | STRUCTURE | Distance | EVIDENCE.correctionBus | CLONE (SHORT: fee_safe), BAG | structure_snapshots.dist_floor | Structure (OD) |
| sdv | EVIDENCE | Volatility | EVIDENCE.StDistVol | CLONE (corridor) | — | — |
| p90 | EVIDENCE | Volatility | EVIDENCE.StDistVol | BAG | — | — |
| distance_fingerprint | BAG | Fingerprint | BAG.fingerprint | KNOWLEDGE, ORACLE, PREDICTION | bag_artifacts.payload_json | — |
| dist_trend | DISTANCE | Derived | DISTANCE | BAG, TRADING SCHEMA | — | — |
| dist_velocity | DISTANCE | Derived | DISTANCE | CLONE, BAG | — | — |
| dist_acceleration | DISTANCE | Derived | DISTANCE | CLONE, BAG | — | — |
| ceiling_floor_ratio | DISTANCE | Derived | DISTANCE | BAG, TRADING SCHEMA | — | — |
| dist_delta | DISTANCE | Derived | DISTANCE | BAG, TRADING SCHEMA | — | — |
| distance_bucket | DISTANCE | Classification | DISTANCE | KNOWLEDGE (Academy), BAG | — | — |

### STRUCTURE LAYER

| Artifact | Owner | Type | Producer | Consumer | SQLite | Snapshot |
|----------|-------|------|----------|----------|--------|----------|
| structure_snapshot | STRUCTURE | Immutable Card | STRUCTURE.compute | EVIDENCE, CLONE, BAG, KNOWLEDGE, TRADING SCHEMA, DASHBOARD | structure_snapshots | Structure |
| lines | STRUCTURE | Geometry | STRUCTURE.LineBuilder | STRUCTURE (WaveBuilder, CageEngine) | — | — |
| slopes | STRUCTURE | Geometry | STRUCTURE.SlopeBuilder | STRUCTURE (WaveBuilder) | — | — |
| waves | STRUCTURE | Classification | STRUCTURE.WaveBuilder | EVIDENCE (MTF), KNOWLEDGE, BAG | wave_history | Structure (W) |
| cage | STRUCTURE | Geometry | STRUCTURE.CageEngine | CLONE, GRID, EVIDENCE, BAG, TRADING SCHEMA | structure_snapshots, cage_history | Structure (W) |
| ladder | STRUCTURE | Pattern | STRUCTURE.ladder | DASHBOARD, BAG, TRADING SCHEMA | — | Structure (W) |
| nearest_support | STRUCTURE | Level | STRUCTURE.nearest | CLONE (SL fallback) | — | Structure (W) |
| nearest_resistance | STRUCTURE | Level | STRUCTURE.nearest | CLONE (SL fallback) | — | Structure (W) |
| market_phase | STRUCTURE | Classification | STRUCTURE.phase | CLONE, BAG, TRADING SCHEMA, DASHBOARD | — | Structure (W) |
| pending_wave | STRUCTURE | Status | STRUCTURE.WaveBuilder | DASHBOARD, TRADING SCHEMA | — | Structure (W) |

### EVIDENCE LAYER

| Artifact | Owner | Type | Producer | Consumer | SQLite | Snapshot |
|----------|-------|------|----------|----------|--------|----------|
| evidence_snapshot | EVIDENCE | Immutable Card | EVIDENCE | CLONE, HIVEMIND, BAG, DASHBOARD | evidence_snapshots | Evidence (W) |
| dir_bus | EVIDENCE | Bus | EVIDENCE.dirBus | CLONE, BAG, DASHBOARD | evidence_snapshots.direction_bus_json | Evidence (W) |
| exit_bus | EVIDENCE | Bus | EVIDENCE.exitBus | CLONE, BAG, DASHBOARD | evidence_snapshots.exit_bus_json | Evidence (W) |
| correction_bus | EVIDENCE | Bus | EVIDENCE.correctionBus | BAG, TRADING SCHEMA, DASHBOARD | evidence_snapshots.correction_bus_json | Evidence (W) |
| oi_score | EVIDENCE | Score | EVIDENCE.oiInherit | EVIDENCE (dir_bus), BAG | — | Evidence (W) |
| mtf_sector | EVIDENCE | Classification | EVIDENCE.mtfSector | EVIDENCE (dir_bus), BAG | — | Evidence (W) |
| max_score | EVIDENCE | Ceiling | EVIDENCE.maxScore | DASHBOARD | evidence_snapshots.max_score | Evidence (W) |
| data_quality | EVIDENCE | Quality | EVIDENCE | CLONE, AUDIT, DASHBOARD | evidence_snapshots.data_quality_json | Evidence (W) |

### CLONE LAYER

| Artifact | Owner | Type | Producer | Consumer | SQLite | Snapshot |
|----------|-------|------|----------|----------|--------|----------|
| clone_observation | CLONE | Immutable Card | CLONE_SHARED.dirObserve/gridObserve | TRADE, STATISTICS, BAG, DASHBOARD | clone_observations | Clone (W) |
| clone_ledger | CLONE | Internal State | CLONE_SHARED.freshClone | CLONE (internal) | — | — |
| corridor | CLONE | Zone | CLONE_SHARED.corridor | CLONE (entry check) | — | — |
| entry_allowed | CLONE | Boolean | CLONE_SHARED | TRADE | — | Clone (W) |
| no_entry_reason | CLONE | String | CLONE_SHARED | BAG, DASHBOARD | — | Clone (W) |
| setup_score | CLONE | Score | CLONE_SHARED | BAG, DASHBOARD | — | Clone (W) |
| confidence | CLONE | Score | CLONE_SHARED | BAG, KNOWLEDGE (CERMIN), DASHBOARD | — | Clone (W) |

### TRADE LAYER

| Artifact | Owner | Type | Producer | Consumer | SQLite | Snapshot |
|----------|-------|------|----------|----------|--------|----------|
| entry_marker | TRADE | Marker | TRADE.mkEntry | POSITION, STATISTICS, BAG, DASHBOARD | trade_markers | Trade (W) |
| exit_marker | TRADE | Marker | TRADE.mkExit | POSITION, STATISTICS, BAG, KNOWLEDGE, DASHBOARD, REPLAY | trade_markers | Trade (W) |
| trade_snapshot | TRADE | Immutable Card | SIMULATION.process | STATISTICS, BAG | trade_markers | Trade (W) |
| gross | TRADE | PnL | TRADE.mkExit | STATISTICS, BAG | trade_markers.gross | Trade (W) |
| net | TRADE | PnL | TRADE.mkExit | STATISTICS, BAG, KNOWLEDGE | trade_markers.net | Trade (W) |
| result | TRADE | Outcome | TRADE.mkExit | STATISTICS, BAG, KNOWLEDGE, ACADEMY | trade_markers.result | Trade (W) |
| fee | TRADE | Cost | TRADE.mkExit | STATISTICS, BAG, BENCHMARK | trade_markers.fee | Trade (W) |
| slip | TRADE | Cost | TRADE.mkExit | STATISTICS, BAG | trade_markers.slip | Trade (W) |

### POSITION LAYER

| Artifact | Owner | Type | Producer | Consumer | SQLite | Snapshot |
|----------|-------|------|----------|----------|--------|----------|
| position_state | POSITION | State | POSITION.update | STATISTICS, BAG, DASHBOARD | positions | — |
| mae | POSITION | Excursion | POSITION.update | STATISTICS, BAG | positions.mae | Trade (W) |
| mfe | POSITION | Excursion | POSITION.update | STATISTICS, BAG | positions.mfe | Trade (W) |
| hold_count | POSITION | Counter | POSITION.update | STATISTICS, BAG, PREDICTION | positions.hold_count | Trade (W) |
| position_timeline | POSITION | History | POSITION | BAG, DASHBOARD, REPLAY | position_timeline | — |

### STATISTICS LAYER

| Artifact | Owner | Type | Producer | Consumer | SQLite | Snapshot |
|----------|-------|------|----------|----------|--------|----------|
| statistics_snapshot | STATISTICS | Immutable Card | STATISTICS.tradeStats | BAG, KNOWLEDGE, PREDICTION, BENCHMARK, DASHBOARD | trade_statistics | Statistics |
| win_rate | STATISTICS | Metric | STATISTICS.tradeStats | BAG, KNOWLEDGE, PREDICTION, DASHBOARD | trade_statistics.win_rate | Statistics (W) |
| expectancy | STATISTICS | Metric | STATISTICS.tradeStats | BAG, KNOWLEDGE, BENCHMARK, DASHBOARD | trade_statistics.expectancy | Statistics (W) |
| pf | STATISTICS | Metric | STATISTICS.tradeStats | BAG, KNOWLEDGE, DASHBOARD | trade_statistics.profit_factor | Statistics (W) |
| fee_drag | STATISTICS | Metric | STATISTICS.tradeStats | BAG, KNOWLEDGE, BENCHMARK | trade_statistics.fee_drag | Statistics (W) |
| wrong_rate | STATISTICS | Metric | STATISTICS.tradeStats | BAG, KNOWLEDGE, DARWIN | trade_statistics.wrong_rate | Statistics (W) |
| sample_status | STATISTICS | Status | STATISTICS.tradeStats | BAG, KNOWLEDGE, DASHBOARD | — | Statistics (W) |
| market_statistics | STATISTICS | Aggregation | STATISTICS | BAG, DASHBOARD | market_statistics | — |

### BAG LAYER

| Artifact | Owner | Type | Producer | Consumer | SQLite | Snapshot |
|----------|-------|------|----------|----------|--------|----------|
| bag_artifact | BAG | Grouped Data | BAG | KNOWLEDGE, PREDICTION, TRADING SCHEMA, BENCHMARK, DASHBOARD | bag_artifacts | — |
| bag_pattern | BAG | Pattern | BAG.pattern_mining | KNOWLEDGE, DASHBOARD | bag_patterns | — |
| bag_compression | BAG | Metric | BAG.compress | DASHBOARD | bag_compression | — |
| consensus | BAG | Score | BAG.consensus | KNOWLEDGE (HiveMind), DASHBOARD | bag_artifacts.consensus | — |
| conflict_level | BAG | Score | BAG.conflict | KNOWLEDGE (Darwin), DASHBOARD | bag_artifacts.conflict_level | — |
| maturity_score | BAG | Score | BAG.maturity | KNOWLEDGE (Librarian), DASHBOARD | bag_artifacts.payload_json | — |
| behavior_profile | BAG | Profile | BAG.behavior_analysis | KNOWLEDGE, TRADING SCHEMA, DASHBOARD | bag_artifacts.payload_json | — |
| sequence_pattern | BAG | Pattern | BAG.sequence_analysis | KNOWLEDGE, DASHBOARD | bag_patterns | — |
| temporal_pattern | BAG | Pattern | BAG.temporal_analysis | KNOWLEDGE, DASHBOARD | bag_patterns | — |
| distance_fingerprint | BAG | Fingerprint | BAG.fingerprint | KNOWLEDGE, ORACLE, PREDICTION | bag_artifacts.payload_json | — |

### KNOWLEDGE LAYER

| Artifact | Owner | Type | Producer | Consumer | SQLite | Snapshot |
|----------|-------|------|----------|----------|--------|----------|
| knowledge_snapshot | KNOWLEDGE | Immutable Card | KNOWLEDGE | PREDICTION, GOVERNANCE, DASHBOARD | knowledge_artifacts | Knowledge (W) |
| academy_artifacts | KNOWLEDGE | Learning | KNOWLEDGE.ACADEMY | PREDICTION, GOVERNANCE, DARWIN, DASHBOARD | knowledge_artifacts | Knowledge (W) |
| oracle_match | KNOWLEDGE | Similarity | KNOWLEDGE.ORACLE | HIVEMIND, PREDICTION, DASHBOARD | knowledge_artifacts | Knowledge (W) |
| hivemind_understanding | KNOWLEDGE | Understanding | KNOWLEDGE.HIVEMIND | PREDICTION, DASHBOARD | knowledge_artifacts | Knowledge (W) |
| cermin_calibration | KNOWLEDGE | Calibration | KNOWLEDGE.CERMIN | PREDICTION, GOVERNANCE, DASHBOARD | knowledge_artifacts | Knowledge (W) |
| librarian_events | KNOWLEDGE | Lifecycle | KNOWLEDGE.LIBRARIAN | DASHBOARD, AUDIT | knowledge_artifacts | Knowledge (W) |
| darwin_proposals | KNOWLEDGE | Proposal | KNOWLEDGE.DARWIN | GOVERNANCE, DASHBOARD | knowledge_artifacts | Knowledge (W) |
| chronicle | KNOWLEDGE | History | KNOWLEDGE.River | AUDIT, DASHBOARD | — | — |

### PREDICTION LAYER

| Artifact | Owner | Type | Producer | Consumer | SQLite | Snapshot |
|----------|-------|------|----------|----------|--------|----------|
| prediction_snapshot | PREDICTION | Immutable Card | PREDICTION.summarize | TRADING SCHEMA, CONSUMER, DASHBOARD | predictions | Prediction |
| intelligence_score | PREDICTION | Score | PREDICTION | TRADING SCHEMA, CONSUMER, DASHBOARD | predictions.confidence | Prediction (W) |
| dominant_bias | PREDICTION | Direction | PREDICTION | TRADING SCHEMA, CONSUMER, DASHBOARD | predictions.predicted_side | Prediction (W) |
| empirical_win_rate | PREDICTION | Probability | PREDICTION | TRADING SCHEMA, CONSUMER, GOVERNANCE | predictions.empirical_win_rate | Prediction (OD) |
| similarity_score | PREDICTION | Score | PREDICTION | TRADING SCHEMA, CONSUMER | predictions.similarity_score | Prediction (W) |
| cermin_error | PREDICTION | Error | PREDICTION | GOVERNANCE, CONSUMER | predictions.cermin_error | Prediction (W) |
| no_model | PREDICTION | Flag | PREDICTION | AUDIT | — | Prediction (W) |

### TRADING SCHEMA LAYER

| Artifact | Owner | Type | Producer | Consumer | SQLite | Snapshot |
|----------|-------|------|----------|----------|--------|----------|
| market_schema_defs | TRADING SCHEMA | Blueprint | TRADING SCHEMA | GOVERNANCE, DASHBOARD | — | — |
| trading_schema_defs | TRADING SCHEMA | Blueprint | TRADING SCHEMA | GOVERNANCE, DASHBOARD | — | — |
| entry_schema_defs | TRADING SCHEMA | Blueprint | TRADING SCHEMA | GOVERNANCE, DASHBOARD | — | — |
| position_schema_defs | TRADING SCHEMA | Blueprint | TRADING SCHEMA | GOVERNANCE, DASHBOARD | — | — |
| exit_schema_defs | TRADING SCHEMA | Blueprint | TRADING SCHEMA | GOVERNANCE, DASHBOARD | — | — |
| schema_confidence_map | TRADING SCHEMA | Mapping | TRADING SCHEMA | GOVERNANCE | — | — |

### GOVERNANCE LAYER

| Artifact | Owner | Type | Producer | Consumer | SQLite | Snapshot |
|----------|-------|------|----------|----------|--------|----------|
| config_version | GOVERNANCE | Config | GOVERNANCE.decide | All layers (BOUNDED params) | app_settings | — |
| proposal | GOVERNANCE | Proposal | GOVERNANCE | BENCHMARK, DASHBOARD | governance_proposals | — |
| governance_log | GOVERNANCE | Log | GOVERNANCE | AUDIT, DASHBOARD | governance_logs | — |
| rollback_log | GOVERNANCE | Log | GOVERNANCE.rollback | AUDIT, DASHBOARD | rollback_logs | — |
| validation_results | GOVERNANCE | Validation | GOVERNANCE.validations | DASHBOARD, AUDIT | — | — |

### BENCHMARK LAYER

| Artifact | Owner | Type | Producer | Consumer | SQLite | Snapshot |
|----------|-------|------|----------|----------|--------|----------|
| benchmark_snapshot | BENCHMARK | Immutable Card | BENCHMARK.wasit | GOVERNANCE, DASHBOARD | benchmark_runs | Benchmark (W) |
| wasit_verdict | BENCHMARK | Verdict | BENCHMARK.wasit | GOVERNANCE | benchmark_runs.verdict | Benchmark (W) |
| gates_G1_G5 | BENCHMARK | Gates | BENCHMARK.wasit | GOVERNANCE, DASHBOARD | benchmark_runs.gates_json | Benchmark (W) |
| per_fold_metrics | BENCHMARK | Metrics | BENCHMARK.wasit | GOVERNANCE, DASHBOARD | benchmark_cases | Benchmark (W) |

### SIMULATION LAYER

| Artifact | Owner | Type | Producer | Consumer | SQLite | Snapshot |
|----------|-------|------|----------|----------|--------|----------|
| simulation_state | SIMULATION | State | SIMULATION.freshState | REPLAY, AUDIT, DASHBOARD | pipeline_runs | — |
| determinism_hash | SIMULATION | Hash | SIMULATION.determinismHash | AUDIT | — | — |
| pipeline_run | SIMULATION | Run | SIMULATION.computeAll | AUDIT, DASHBOARD | pipeline_runs | — |

### REPLAY LAYER

| Artifact | Owner | Type | Producer | Consumer | SQLite | Snapshot |
|----------|-------|------|----------|----------|--------|----------|
| replay_session | REPLAY | Session | REPLAY.create | DASHBOARD, AUDIT | replay_sessions | — |
| replay_frames | REPLAY | Frames | REPLAY | DASHBOARD, AUDIT | replay_frames | — |

### DASHBOARD LAYER

| Artifact | Owner | Type | Producer | Consumer | SQLite | Snapshot |
|----------|-------|------|----------|----------|--------|----------|
| geometry_chart | DASHBOARD | UI | VIEW.drawGeom | Human | — | — |
| clone_cards | DASHBOARD | UI | VIEW.renderClone | Human | — | — |
| trade_history | DASHBOARD | UI | VIEW.renderTrade | Human | — | — |
| equity_curve | DASHBOARD | UI | VIEW.drawEq | Human | — | — |
| rapor_table | DASHBOARD | UI | VIEW (renderTrade) | Human | — | — |
| academy_table | DASHBOARD | UI | VIEW.renderKnow | Human | — | — |
| knowledge_panels | DASHBOARD | UI | VIEW.renderKnow | Human | — | — |
| governance_ui | DASHBOARD | UI | VIEW.renderGov | Human | — | — |
| simulation_ui | DASHBOARD | UI | VIEW.renderSim | Human | — | — |
| replay_viewer | DASHBOARD | UI | VIEW.renderReplay | Human | — | — |
| prediction_panel | DASHBOARD | UI | VIEW.renderPred | Human | — | — |
| consumer_panel | DASHBOARD | UI | VIEW.renderConsumer | Human | — | — |
| audit_panel | DASHBOARD | UI | VIEW.renderAudit | Human | — | — |
| final_validation | DASHBOARD | UI | VIEW.renderFinalValidation | Human | — | — |
| csv_export | DASHBOARD | Export | CONSUMER.exportCSV | Human | — | — |

### INTEGRATION LAYER

| Artifact | Owner | Type | Producer | Consumer | SQLite | Snapshot |
|----------|-------|------|----------|----------|--------|----------|
| worker_bridge | INTEGRATION | Bridge | INTEGRATION | All workers | — | — |
| pipeline_orchestrator | INTEGRATION | Orchestrator | INTEGRATION | All layers | — | — |

### FINAL VALIDATION LAYER

| Artifact | Owner | Type | Producer | Consumer | SQLite | Snapshot |
|----------|-------|------|----------|----------|--------|----------|
| validation_results | FINAL VALIDATION | Report | FINAL_VALIDATION.runAll | DASHBOARD, GOVERNANCE | — | — |
| self_test_results | FINAL VALIDATION | Report | AUDIT.run | DASHBOARD, GOVERNANCE | — | — |
| domain_audit | FINAL VALIDATION | Report | AUDIT.domains | DASHBOARD, GOVERNANCE | audit_logs | — |
| fingerprint | FINAL VALIDATION | Hash | AUDIT.fingerprint | DASHBOARD | — | — |

---

## ARTIFACT SUMMARY

| Layer | Artifact Count |
|-------|---------------|
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

## ARTIFACT REGISTRY STATUS: LOCKED

All 145 artifacts across 20 layers are registered with owner, type, producer, consumer, SQLite mapping, and snapshot mapping. NO ARTIFACT WITHOUT OWNER.
# 03_TRADING_CONSTITUTION.md

## ST-LMS Final Freeze Contract V1 — Trading Constitution

**Date:** 2026-07-28
**Status:** CONSTITUTIONALLY FROZEN — FINAL
**Sources:** MASTER_SPECIFICATION.html S7, ST_LMS_CORE.js CLONE_SHARED, ENRICHMENT_REPORT_V1.md

---

## 1. MARKET SCHEMA (10 schemas)

### TREND

| Aspect | Value |
|--------|-------|
| Required Artifact | truth_snapshot (stDir), structure_snapshot (cage.status) |
| Optional Artifact | evidence_snapshot (dir_bus) |
| Forbidden Artifact | W%R, MACD (for entry) |
| Confidence Source | stDir + EMA direction agreement |
| Minimum Condition | stDir != 0, cage.status = NONE |
| Exit Condition | stDir flip, wave exhaustion |
| Consumer | LONG (UP), SHORT (DOWN) |

### SIDEWAY

| Aspect | Value |
|--------|-------|
| Required Artifact | structure_snapshot (cage.status, cage.pp) |
| Optional Artifact | evidence_snapshot (correction_bus) |
| Forbidden Artifact | stDir (for GRID decision) |
| Confidence Source | cage.rangeAtr stability |
| Minimum Condition | cage.status != NONE |
| Exit Condition | cage becomes NONE, breakout |
| Consumer | GRID |

### RANGE

| Aspect | Value |
|--------|-------|
| Required Artifact | structure_snapshot (wave, cage) |
| Optional Artifact | wave_history |
| Forbidden Artifact | MTF (for GRID) |
| Confidence Source | wave = CONFIRMED_RANGE / SIDEWAY |
| Minimum Condition | wave = CONFIRMED_RANGE or SIDEWAY |
| Exit Condition | wave changes to non-range |
| Consumer | GRID |

### CHAOS

| Aspect | Value |
|--------|-------|
| Required Artifact | structure_snapshot (wave) |
| Optional Artifact | — |
| Forbidden Artifact | — |
| Confidence Source | wave = CHAOS |
| Minimum Condition | wave = CHAOS |
| Exit Condition | wave changes to non-CHAOS |
| Consumer | None (WAIT all clones) |

### COMPRESSION

| Aspect | Value |
|--------|-------|
| Required Artifact | structure_snapshot (cage.status, cage.rangeAtr) |
| Optional Artifact | cage_history |
| Forbidden Artifact | stDir (for GRID) |
| Confidence Source | cage.rangeAtr <= CAGE_TIGHT_ATR |
| Minimum Condition | cage.status = VALID_COMPRESSION |
| Exit Condition | breakout, cage expands |
| Consumer | GRID (aggressive) |

### EXPANSION

| Aspect | Value |
|--------|-------|
| Required Artifact | structure_snapshot (cage.status, cage.rangeAtr) |
| Optional Artifact | cage_history |
| Forbidden Artifact | stDir (for GRID) |
| Confidence Source | cage.rangeAtr > CAGE_TIGHT_ATR |
| Minimum Condition | cage.status = LOOSE_SIDEWAY |
| Exit Condition | breakout, cage compresses |
| Consumer | GRID (conservative) |

### BREAKOUT

| Aspect | Value |
|--------|-------|
| Required Artifact | structure_snapshot (cage.breakout) |
| Optional Artifact | truth_snapshot (stDir) |
| Forbidden Artifact | — |
| Confidence Source | cage.breakout direction + pressure |
| Minimum Condition | cage.breakout != NONE |
| Exit Condition | breakout fails, price reverses |
| Consumer | LONG (IMMINENT_UP), SHORT (IMMINENT_DOWN) |

### REVERSAL

| Aspect | Value |
|--------|-------|
| Required Artifact | truth_snapshot (flip), structure_snapshot (wave) |
| Optional Artifact | wave_history |
| Forbidden Artifact | — |
| Confidence Source | flip event + wave = REVERSAL_UP/DOWN |
| Minimum Condition | TREND_FLIP detected, wave = REVERSAL |
| Exit Condition | reversal fails (false flip) |
| Consumer | LONG (REVERSAL_UP), SHORT (REVERSAL_DOWN) — caution |

### EXHAUSTION

| Aspect | Value |
|--------|-------|
| Required Artifact | structure_snapshot (wave), truth_snapshot (distAtr) |
| Optional Artifact | truth_snapshot (vel, acc) |
| Forbidden Artifact | — |
| Confidence Source | wave = EXHAUSTION + distAtr expanding |
| Minimum Condition | wave = EXHAUSTION_UP/DOWN |
| Exit Condition | trend resumes or reverses |
| Consumer | Opposite clone (observe), existing positions exit |

### WARMUP

| Aspect | Value |
|--------|-------|
| Required Artifact | truth_snapshot (point_status) |
| Optional Artifact | — |
| Forbidden Artifact | — |
| Confidence Source | N/A (no confidence during warmup) |
| Minimum Condition | point_status = WARMUP |
| Exit Condition | point_status = VALID |
| Consumer | None (WAIT all clones) |

---

## 2. TRADING SCHEMA (7 schemas)

### LONG

| Aspect | Value |
|--------|-------|
| Required Artifact | truth_snapshot (stDir, emaSlope, volDelta, close), structure_snapshot (cage, nearest), evidence_snapshot (dir_bus), clone_ledger |
| Optional Artifact | distance_metrics (dist_ceiling) |
| Forbidden Artifact | W%R, MACD, RSI (for entry) |
| Confidence Source | setup_score (5000 + expected_move * 400) |
| Minimum Condition | stDir=+1, ema>0, vd>0, corridor.inZone, fee_safe, global_ok, open=null |
| Exit Condition | WRONG_ENTRY_EARLY -> WRONG_ENTRY_GEOM -> HYPOTHESIS_INVALID -> SL -> HOLD-VETO -> TP -> EXIT_BUS -> TIME_EXIT |
| Consumer | TRADE (LONG entry/exit markers) |

### SHORT

| Aspect | Value |
|--------|-------|
| Required Artifact | truth_snapshot (stDir, emaSlope, volDelta, close), structure_snapshot (cage, nearest), evidence_snapshot (dir_bus), clone_ledger |
| Optional Artifact | distance_metrics (dist_floor) |
| Forbidden Artifact | W%R, MACD, RSI (for entry) |
| Confidence Source | setup_score (5000 + expected_move * 400) |
| Minimum Condition | stDir=-1, ema<0, vd<0, corridor.inZone, fee_safe, global_ok, open=null |
| Exit Condition | Mirror LONG exit priority |
| Consumer | TRADE (SHORT entry/exit markers) |

### GRID

| Aspect | Value |
|--------|-------|
| Required Artifact | structure_snapshot (cage), clone_ledger (gridFills) |
| Optional Artifact | — |
| Forbidden Artifact | stDir, dir_bus, MTF, W%R, MACD, RSI |
| Confidence Source | active ? 7000 : 2000 |
| Minimum Condition | cage_valid, width>=3*req, breakout=NONE, pp in zone, fills<max |
| Exit Condition | RANGE_BREAK -> WRONG_ENTRY -> GRID_TP -> STOP_ALL |
| Consumer | TRADE (GRID fill markers) |

### NO TRADE

| Aspect | Value |
|--------|-------|
| Required Artifact | clone_observation |
| Optional Artifact | — |
| Forbidden Artifact | — |
| Confidence Source | setup_score = 2500 |
| Minimum Condition | Entry conditions not met |
| Exit Condition | N/A (no position) |
| Consumer | STATISTICS (observation recorded) |

### WAIT

| Aspect | Value |
|--------|-------|
| Required Artifact | structure_snapshot (phase, wave), truth_snapshot (point_status) |
| Optional Artifact | — |
| Forbidden Artifact | — |
| Confidence Source | setup_score = 2500 |
| Minimum Condition | Market condition not favorable for clone |
| Exit Condition | Market condition becomes favorable |
| Consumer | STATISTICS (observation recorded) |

### HOLD

| Aspect | Value |
|--------|-------|
| Required Artifact | position_state, truth_snapshot, structure_snapshot, evidence_snapshot (exit_bus) |
| Optional Artifact | distance_metrics |
| Forbidden Artifact | — |
| Confidence Source | Position PnL |
| Minimum Condition | Position open, no exit reason triggered |
| Exit Condition | Any exit reason triggered |
| Consumer | POSITION (update mae/mfe/hold_c) |

### SKIP

| Aspect | Value |
|--------|-------|
| Required Artifact | market_snapshot (data_status, gap_flag) |
| Optional Artifact | — |
| Forbidden Artifact | — |
| Confidence Source | N/A |
| Minimum Condition | data_status != FINAL or gap_flag = 1 |
| Exit Condition | data_status = FINAL |
| Consumer | STATISTICS (observation recorded with data issue) |

---

## 3. ENTRY SCHEMA (11 schemas)

### LONG CONTINUATION

| Aspect | Value |
|--------|-------|
| Required Artifact | truth_snapshot (stDir, ema, volDelta), structure_snapshot (wave, cage), evidence_snapshot (dir_bus) |
| Optional Artifact | bag_artifacts (behavior_profile) |
| Forbidden Artifact | W%R, MACD (for entry) |
| Confidence Source | HIGH (trend established) |
| Minimum Condition | stDir=+1, wave=CONTINUATION_UP or STRONG_ACCUMULATION, standard LONG conjunction |
| Exit Condition | Standard LONG exit priority |
| Consumer | TRADE (LONG entry) |

### LONG PULLBACK

| Aspect | Value |
|--------|-------|
| Required Artifact | truth_snapshot (stDir, distAtr), structure_snapshot (cage, nearest), evidence_snapshot (dir_bus) |
| Optional Artifact | distance_fingerprint |
| Forbidden Artifact | — |
| Confidence Source | MEDIUM |
| Minimum Condition | stDir=+1, dist_ceiling expanding (pullback), corridor.inZone near floor, fee_safe |
| Exit Condition | Standard LONG exit priority |
| Consumer | TRADE (LONG entry) |

### LONG BREAKOUT

| Aspect | Value |
|--------|-------|
| Required Artifact | structure_snapshot (cage.breakout, cage.pressureUp), truth_snapshot (stDir) |
| Optional Artifact | cage_history |
| Forbidden Artifact | — |
| Confidence Source | MEDIUM |
| Minimum Condition | stDir=+1, cage.breakout=IMMINENT_UP, standard LONG conjunction |
| Exit Condition | TP=cage.upper, HYPOTHESIS_INVALID if breakout fails |
| Consumer | TRADE (LONG entry) |

### LONG REVERSAL

| Aspect | Value |
|--------|-------|
| Required Artifact | truth_snapshot (flip, stDir), structure_snapshot (wave) |
| Optional Artifact | wave_history |
| Forbidden Artifact | — |
| Confidence Source | LOW (false reversal risk) |
| Minimum Condition | TREND_FLIP_UP, wave=REVERSAL_UP, standard LONG conjunction |
| Exit Condition | Aggressive wrong entry exit (hold<=2), standard LONG exit |
| Consumer | TRADE (LONG entry) |

### SHORT CONTINUATION

| Aspect | Value |
|--------|-------|
| Required Artifact | truth_snapshot (stDir, ema, volDelta), structure_snapshot (wave, cage), evidence_snapshot (dir_bus) |
| Optional Artifact | bag_artifacts (behavior_profile) |
| Forbidden Artifact | W%R, MACD (for entry) |
| Confidence Source | HIGH |
| Minimum Condition | stDir=-1, wave=CONTINUATION_DOWN or STRONG_DISTRIBUTION, standard SHORT conjunction |
| Exit Condition | Standard SHORT exit priority |
| Consumer | TRADE (SHORT entry) |

### SHORT PULLBACK

| Aspect | Value |
|--------|-------|
| Required Artifact | truth_snapshot (stDir, distAtr), structure_snapshot (cage, nearest), evidence_snapshot (dir_bus) |
| Optional Artifact | distance_fingerprint |
| Forbidden Artifact | — |
| Confidence Source | MEDIUM |
| Minimum Condition | stDir=-1, dist_floor expanding (pullback), corridor.inZone near ceiling, fee_safe |
| Exit Condition | Standard SHORT exit priority |
| Consumer | TRADE (SHORT entry) |

### SHORT BREAKOUT

| Aspect | Value |
|--------|-------|
| Required Artifact | structure_snapshot (cage.breakout, cage.pressureDn), truth_snapshot (stDir) |
| Optional Artifact | cage_history |
| Forbidden Artifact | — |
| Confidence Source | MEDIUM |
| Minimum Condition | stDir=-1, cage.breakout=IMMINENT_DOWN, standard SHORT conjunction |
| Exit Condition | TP=cage.lower, HYPOTHESIS_INVALID if breakout fails |
| Consumer | TRADE (SHORT entry) |

### SHORT REVERSAL

| Aspect | Value |
|--------|-------|
| Required Artifact | truth_snapshot (flip, stDir), structure_snapshot (wave) |
| Optional Artifact | wave_history |
| Forbidden Artifact | — |
| Confidence Source | LOW |
| Minimum Condition | TREND_FLIP_DOWN, wave=REVERSAL_DOWN, standard SHORT conjunction |
| Exit Condition | Aggressive wrong entry exit (hold<=2) |
| Consumer | TRADE (SHORT entry) |

### GRID COMPRESSION

| Aspect | Value |
|--------|-------|
| Required Artifact | structure_snapshot (cage.status, cage.rangeAtr, cage.pp) |
| Optional Artifact | cage_history, bag_artifacts (compression pattern) |
| Forbidden Artifact | stDir, dir_bus, MTF |
| Confidence Source | HIGH (tight range) |
| Minimum Condition | cage.status=VALID_COMPRESSION, standard GRID conjunction |
| Exit Condition | Standard GRID exit priority (aggressive) |
| Consumer | TRADE (GRID fills) |

### GRID RANGE

| Aspect | Value |
|--------|-------|
| Required Artifact | structure_snapshot (cage, wave) |
| Optional Artifact | wave_history |
| Forbidden Artifact | stDir, dir_bus, MTF |
| Confidence Source | MEDIUM |
| Minimum Condition | wave=CONFIRMED_RANGE or SIDEWAY, standard GRID conjunction |
| Exit Condition | Standard GRID exit priority |
| Consumer | TRADE (GRID fills) |

### GRID EXPANSION

| Aspect | Value |
|--------|-------|
| Required Artifact | structure_snapshot (cage.status, cage.rangeAtr, cage.pp) |
| Optional Artifact | cage_history |
| Forbidden Artifact | stDir, dir_bus, MTF |
| Confidence Source | LOW (wide range, higher risk) |
| Minimum Condition | cage.status=LOOSE_SIDEWAY, standard GRID conjunction |
| Exit Condition | Standard GRID exit priority (conservative) |
| Consumer | TRADE (GRID fills) |

---

## 4. POSITION SCHEMA (7 schemas)

### ADD POSITION

| Aspect | Value |
|--------|-------|
| Required Artifact | position_state (fills count), structure_snapshot (cage.pp) |
| Optional Artifact | — |
| Forbidden Artifact | — |
| Confidence Source | GRID active confidence |
| Minimum Condition | GRID only: pp in zone, fills_per_side < GRID_MAX_FILLS_PER_SIDE |
| Exit Condition | Per-fill exit rules |
| Consumer | TRADE (GRID fill marker) |

### PARTIAL TP

| Aspect | Value |
|--------|-------|
| Required Artifact | position_state (profit_pct) |
| Optional Artifact | bag_artifacts (optimal_partial_level) |
| Forbidden Artifact | — |
| Confidence Source | Position profit percentage |
| Minimum Condition | profit_pct >= PARTIAL_TP activation |
| Exit Condition | Close PARTIAL_TP_PCT, SL to entry for remainder |
| Consumer | TRADE (PARTIAL marker) |

### TRAILING TP

| Aspect | Value |
|--------|-------|
| Required Artifact | position_state (profit_pct), truth_snapshot (atr) |
| Optional Artifact | distance_metrics |
| Forbidden Artifact | — |
| Confidence Source | Position profit percentage |
| Minimum Condition | profit_pct >= TRAIL_ACTIVATE_R * ATR |
| Exit Condition | SL trails behind price by TRAIL_ATR_MULT * ATR |
| Consumer | POSITION (trailing_stop update) |

### BREAKEVEN

| Aspect | Value |
|--------|-------|
| Required Artifact | position_state (profit_pct, entry_price) |
| Optional Artifact | — |
| Forbidden Artifact | — |
| Confidence Source | Position profit percentage |
| Minimum Condition | profit_pct >= BREAKEVEN threshold |
| Exit Condition | SL moved to entry_price |
| Consumer | POSITION (stop_loss update) |

### TIME EXIT

| Aspect | Value |
|--------|-------|
| Required Artifact | position_state (hold_count, profit_pct) |
| Optional Artifact | bag_artifacts (optimal_hold_duration) |
| Forbidden Artifact | — |
| Confidence Source | N/A (exit trigger) |
| Minimum Condition | hold_count >= TIME_EXIT_CANDLES AND profit_pct < required_move |
| Exit Condition | Close at market |
| Consumer | TRADE (TIME_EXIT marker) |

### WRONG ENTRY

| Aspect | Value |
|--------|-------|
| Required Artifact | position_state (hold_count, entry_price), truth_snapshot (vel, close) |
| Optional Artifact | distance_metrics (adverse) |
| Forbidden Artifact | — |
| Confidence Source | N/A (exit trigger) |
| Minimum Condition | (vel wrong direction OR adverse >= WRONG_ENTRY_PCT) AND hold_count <= 2 |
| Exit Condition | Close immediately at market |
| Consumer | TRADE (WRONG_ENTRY marker) |

### LOCK PROFIT

| Aspect | Value |
|--------|-------|
| Required Artifact | position_state (profit_pct) |
| Optional Artifact | — |
| Forbidden Artifact | — |
| Confidence Source | Position profit percentage |
| Minimum Condition | profit_pct >= LOCK_PROFIT threshold |
| Exit Condition | Disable EXIT_BUS, hold to TP |
| Consumer | POSITION (exit_bus disabled) |

---

## 5. EXIT SCHEMA (6 schemas)

### SL

| Aspect | Value |
|--------|-------|
| Required Artifact | position_state (sl), market_snapshot (high, low) |
| Optional Artifact | — |
| Forbidden Artifact | — |
| Confidence Source | N/A |
| Minimum Condition | LONG: low <= sl; SHORT: high >= sl |
| Exit Condition | Exit at sl price |
| Consumer | TRADE (SL exit marker) |
| Priority | 4 |

### TP

| Aspect | Value |
|--------|-------|
| Required Artifact | position_state (tp), market_snapshot (high, low), evidence_snapshot (exit_bus.hold) |
| Optional Artifact | — |
| Forbidden Artifact | — |
| Confidence Source | N/A |
| Minimum Condition | LONG: high >= tp AND NOT hold; SHORT: low <= tp AND NOT hold |
| Exit Condition | Exit at tp price |
| Consumer | TRADE (TP exit marker) |
| Priority | 6 (delayed by HOLD-veto at priority 5) |

### EXIT BUS

| Aspect | Value |
|--------|-------|
| Required Artifact | truth_snapshot (rsi, wpr) |
| Optional Artifact | — |
| Forbidden Artifact | W%R, MACD (for entry — exit only is OK) |
| Confidence Source | RSI/W%R signal strength |
| Minimum Condition | LONG: RSI>70 OR W%R>-20; SHORT: RSI<30 OR W%R<-80 |
| Exit Condition | Exit at close price |
| Consumer | TRADE (EXIT_BUS marker) |
| Priority | 7 |

### MANUAL EXIT

| Aspect | Value |
|--------|-------|
| Required Artifact | position_state |
| Optional Artifact | — |
| Forbidden Artifact | — |
| Confidence Source | Human decision |
| Minimum Condition | Human approves exit |
| Exit Condition | Exit at close price |
| Consumer | TRADE (MANUAL exit marker) |
| Priority | 0 (override all) |

### TIME EXIT

| Aspect | Value |
|--------|-------|
| Required Artifact | position_state (hold_count, profit_pct) |
| Optional Artifact | — |
| Forbidden Artifact | — |
| Confidence Source | N/A |
| Minimum Condition | hold_count >= TIME_EXIT_CANDLES AND profit_pct < required_move |
| Exit Condition | Exit at close price |
| Consumer | TRADE (TIME_EXIT marker) |
| Priority | 8 |

### EARLY EXIT

| Aspect | Value |
|--------|-------|
| Required Artifact | position_state (hold_count), truth_snapshot (vel, close) |
| Optional Artifact | distance_metrics (adverse) |
| Forbidden Artifact | — |
| Confidence Source | N/A |
| Minimum Condition | Wrong entry detected in first 2 candles |
| Exit Condition | Exit at close price |
| Consumer | TRADE (WRONG_ENTRY marker) |
| Priority | 1-2 |

---

## TRADING CONSTITUTION STATUS: LOCKED

All 41 trading schemas across 5 categories are constitutionally frozen. Each schema defines required artifacts, optional artifacts, forbidden artifacts, confidence source, minimum condition, exit condition, and consumer. No trading logic may be implemented outside these schemas.
# 04_BUILD_CONTRACT.md

## ST-LMS Final Freeze Contract V1 — Build Contract

**Date:** 2026-07-28
**Status:** CONSTITUTIONALLY FROZEN — FINAL
**Sources:** DOCUMENT_DEPENDENCY.html S8-S9, QWEN_14_DOC.html D12-D13

---

## 1. BUILD PHASES

```
PHASE 0: SPECIFICATION FREEZE (COMPLETE)
  Output: All freeze documents, enrichment reports, architecture mapping

PHASE 1: FOUNDATION
  Phase-01: SQLite Foundation
  Phase-02: BOOT + Workspace + Checkpoint
  Phase-03: Config + Bounded Registry

PHASE 2: MARKET + TRUTH
  Phase-04: Market Layer
  Phase-05: Truth Layer
  Phase-06: Distance Metrics (logical sub-layer)

PHASE 3: STRUCTURE + EVIDENCE
  Phase-07: Structure Layer
  Phase-08: Evidence Layer

PHASE 4: TRADING CORE
  Phase-09: Clone Layer (LONG/SHORT/GRID)
  Phase-10: Trade Layer
  Phase-11: Position Layer

PHASE 5: SIMULATION + REPLAY
  Phase-12: Simulation Engine
  Phase-13: Replay Engine (6 types)

PHASE 6: STATISTICS + BAG + KNOWLEDGE
  Phase-14: Statistics Layer
  Phase-15: BAG Layer (grouping, pattern mining, fingerprint)
  Phase-16: Knowledge Layer (Academy, Oracle, HiveMind, CERMIN, Librarian, Darwin)

PHASE 7: PREDICTION + GOVERNANCE
  Phase-17: Prediction Layer
  Phase-18: Trading Schema Layer (41 schemas)
  Phase-19: Governance Layer
  Phase-20: Benchmark Layer (WASIT 5-gate)

PHASE 8: CONSUMER + DASHBOARD
  Phase-21: Consumer Layer
  Phase-22: Dashboard Layer

PHASE 9: INTEGRATION + AUDIT
  Phase-23: Integration Layer (workers, bridges)
  Phase-24: Audit Layer
  Phase-25: Final Validation

PHASE 10: BUILD APPROVAL
  Phase-26: 15 stop-rule PASS -> BUILD_APPROVAL
```

---

## 2. BUILD ORDER (SEQUENTIAL)

| Order | Phase | Layer | Depends On | Output Files | Required Tests |
|-------|-------|-------|------------|-------------|----------------|
| 1 | Phase-01 | SQLite Foundation | — | schema.sql, seed data | integrity_check, foreign_key_check |
| 2 | Phase-02 | BOOT + Workspace | Phase-01 | boot.js, workspace.js | namespace init, IndexedDB open |
| 3 | Phase-03 | Config + Bounded | Phase-02 | config.js | bounded validation, get/set/valid |
| 4 | Phase-04 | Market Layer | Phase-03 | market.js, data.worker.js | hygiene, gap detection, OI proxy |
| 5 | Phase-05 | Truth Layer | Phase-04 | truth.js | determinism, indicator accuracy |
| 6 | Phase-06 | Distance Metrics | Phase-05 | distance.js | dist, distAtr, ceiling, floor |
| 7 | Phase-07 | Structure Layer | Phase-05 | structure.js | HUKUM CAGE, wave 13 structures |
| 8 | Phase-08 | Evidence Layer | Phase-05,07 | evidence.js | 3-bus separation, W%R!=entry |
| 9 | Phase-09 | Clone Layer | Phase-07,08 | clone.js, long.js, short.js, grid.js | 3 obs/candle, entry conjunction |
| 10 | Phase-10 | Trade Layer | Phase-09 | trade.js | P&L correctness, adverse-first |
| 11 | Phase-11 | Position Layer | Phase-10 | position.js | MAE/MFE tracking, hold counter |
| 12 | Phase-12 | Simulation Engine | Phase-09,10,11 | simulation.js | determinism, pipeline stages |
| 13 | Phase-13 | Replay Engine | Phase-12 | replay.js | 6 replay types, bit-per-bit |
| 14 | Phase-14 | Statistics Layer | Phase-10,11 | statistics.js | sample gate, metrics accuracy |
| 15 | Phase-15 | BAG Layer | Phase-14 | bag.js | grouping, pattern mining, fingerprint |
| 16 | Phase-16 | Knowledge Layer | Phase-15 | knowledge.js | unidirectional, no-ML, 7 entities |
| 17 | Phase-17 | Prediction Layer | Phase-16 | prediction.js | no-model, empirical only |
| 18 | Phase-18 | Trading Schema | Phase-17 | trading_schema.js | 41 schemas, 5 categories |
| 19 | Phase-19 | Governance Layer | Phase-16,18 | governance.js | 6 validations, bounded, rollback |
| 20 | Phase-20 | Benchmark Layer | Phase-12,19 | benchmark.js | WASIT 5-gate, parallel worker |
| 21 | Phase-21 | Consumer Layer | Phase-17,19 | consumer.js | fund eval, veto, intent, CSV export |
| 22 | Phase-22 | Dashboard Layer | Phase-21 | dashboard.html, view.js | no-mock, all panels render |
| 23 | Phase-23 | Integration Layer | Phase-22 | integration.js | worker bridges, orchestration |
| 24 | Phase-24 | Audit Layer | Phase-23 | audit.js | 16 self-tests, 6 domain audits |
| 25 | Phase-25 | Final Validation | Phase-24 | final_validation.js | 12-domain check |
| 26 | Phase-26 | BUILD APPROVAL | Phase-25 | approval_report.md | 15 stop-rule PASS |

---

## 3. DEPENDENCY RULES

```
1. NO SKIPPING: Each phase must complete before the next begins.
2. GATE BEFORE NEXT: Each phase must pass HARD validation gate.
3. FOUNDATION FIRST: Phase-01 through Phase-03 must complete first.
4. RESPECT DEPENDENCIES: No building before dependencies are built.
5. TEST AFTER BUILD: Each component tested immediately after building.
6. NO PARALLEL BUILD: Single builder, sequential execution.
```

---

## 4. OUTPUT FILES PER PHASE

| Phase | Output Files |
|-------|-------------|
| Phase-01 | schema.sql, seed.sql, indexes.sql |
| Phase-02 | boot.js, workspace.js, checkpoint.js |
| Phase-03 | config.js, bounded_registry.js |
| Phase-04 | market.js, data.worker.js, market.test.js |
| Phase-05 | truth.js, truth.test.js |
| Phase-06 | distance.js, distance.test.js |
| Phase-07 | structure.js, structure.test.js |
| Phase-08 | evidence.js, evidence.test.js |
| Phase-09 | clone.js, long_clone.js, short_clone.js, grid_clone.js, clone.test.js |
| Phase-10 | trade.js, trade.test.js |
| Phase-11 | position.js, position.test.js |
| Phase-12 | simulation.js, simulation.test.js |
| Phase-13 | replay.js, replay.test.js |
| Phase-14 | statistics.js, statistics.test.js |
| Phase-15 | bag.js, bag.test.js |
| Phase-16 | knowledge.js, knowledge.test.js |
| Phase-17 | prediction.js, prediction.test.js |
| Phase-18 | trading_schema.js, trading_schema.test.js |
| Phase-19 | governance.js, governance.test.js |
| Phase-20 | benchmark.js, benchmark.worker.js, benchmark.test.js |
| Phase-21 | consumer.js, consumer.test.js |
| Phase-22 | dashboard.html, view.js, view.css |
| Phase-23 | integration.js, worker_bridge.js |
| Phase-24 | audit.js, audit.test.js |
| Phase-25 | final_validation.js |
| Phase-26 | approval_report.md |

---

## 5. REQUIRED TESTS PER PHASE

| Phase | Unit Test | Integration Test | Benchmark Test |
|-------|-----------|-----------------|----------------|
| Phase-01 | Schema syntax | FK integrity | Query performance |
| Phase-02 | Namespace init | IndexedDB open | — |
| Phase-03 | Bounded valid | Get/set/valid | — |
| Phase-04 | Hygiene, gap, OI | market_snapshot flow | — |
| Phase-05 | Indicator accuracy | truth_snapshot flow | Determinism |
| Phase-06 | Distance metrics | dist_ceiling/floor flow | — |
| Phase-07 | HUKUM CAGE, wave | structure_snapshot flow | — |
| Phase-08 | 3-bus, W%R!=entry | evidence_snapshot flow | — |
| Phase-09 | 3 obs/candle | Card sharing | — |
| Phase-10 | P&L, adverse-first | Entry/exit flow | — |
| Phase-11 | MAE/MFE, hold | Position lifecycle | — |
| Phase-12 | Pipeline stages | Full pipeline flow | Determinism |
| Phase-13 | 6 replay types | Replay bit-per-bit | — |
| Phase-14 | Sample gate | Statistics accuracy | — |
| Phase-15 | Grouping, pattern | BAG->Knowledge flow | — |
| Phase-16 | 7 entities, no-ML | Unidirectional check | — |
| Phase-17 | No-model | Prediction accuracy | — |
| Phase-18 | 41 schemas | Schema->Trading mapping | — |
| Phase-19 | 6 validations | Bounded, rollback | — |
| Phase-20 | WASIT 5-gate | Parallel worker | Identical->G2 FAIL |
| Phase-21 | Fund, veto, intent | CSV export | — |
| Phase-22 | No-mock render | All panels | — |
| Phase-23 | Worker bridges | Orchestration | — |
| Phase-24 | 16 self-tests | 6 domain audits | — |
| Phase-25 | 12-domain check | — | — |
| Phase-26 | 15 stop-rule | — | — |

---

## 6. BENCHMARK REQUIREMENTS

| Benchmark | Phase | Target |
|-----------|-------|--------|
| Determinism | Phase-05,12 | 2-run checksum identical |
| WASIT Identical | Phase-20 | G2 must FAIL |
| WASIT Tighten Entry | Phase-20 | G1-G5 evaluation |
| WASIT Tighten Wrong | Phase-20 | G1-G5 evaluation |
| Query Performance | Phase-01 | < 5ms for indexed queries |
| Replay Performance | Phase-13 | < 500ms for 1000 candles |
| Pipeline Performance | Phase-12 | < 100ms per candle |
| UI Render | Phase-22 | < 50ms per panel |

---

## BUILD CONTRACT STATUS: LOCKED

All 26 build phases, their order, dependencies, output files, required tests, and benchmark requirements are constitutionally frozen. No phase may be skipped. No phase may be built before its dependencies. Every phase must pass HARD gate before proceeding.
# 05_TEST_CONTRACT.md

## ST-LMS Final Freeze Contract V1 — Test Contract

**Date:** 2026-07-28
**Status:** CONSTITUTIONALLY FROZEN — FINAL

---

## RULE: LAYER TIDAK BOLEH DILANJUTKAN APABILA TEST GAGAL.

---

## TEST REQUIREMENTS PER LAYER

### 1. SQLite Foundation

| Test Type | Test Name | Pass Condition | Fail Consequence |
|-----------|-----------|---------------|-----------------|
| Unit | Schema syntax check | SQL parses without error | STOP BUILD |
| Unit | Table creation | All 40 tables created | STOP BUILD |
| Unit | Index creation | All 9 indexes created | STOP BUILD |
| Unit | Trigger creation | All 4 triggers created | STOP BUILD |
| Unit | Seed data | 9 timeframes, 2 settings, 15 domains | STOP BUILD |
| SQLite | integrity_check | No errors returned | STOP BUILD |
| SQLite | foreign_key_check | No orphaned references | STOP BUILD |
| SQLite | Constraint validation | CHECK, UNIQUE, NOT NULL enforced | STOP BUILD |
| SQLite | CASCADE delete | Session delete cascades to 23 tables | STOP BUILD |
| Benchmark | Query performance | Indexed query < 5ms | SOFT (record) |

### 2. BOOT + Workspace

| Test Type | Test Name | Pass Condition | Fail Consequence |
|-----------|-----------|---------------|-----------------|
| Unit | Namespace initialization | All 26 namespaces present | STOP BUILD |
| Unit | IndexedDB open | Database opens successfully | STOP BUILD |
| Unit | Card storage | Card written and retrieved | STOP BUILD |
| Unit | Card verification | SHA-256 checksum matches | STOP BUILD |
| Integration | Workspace reset | Clean state after reset | STOP BUILD |

### 3. Config + Bounded Registry

| Test Type | Test Name | Pass Condition | Fail Consequence |
|-----------|-----------|---------------|-----------------|
| Unit | Bounded get | Returns current value | STOP BUILD |
| Unit | Bounded set valid | Accepts value in range | STOP BUILD |
| Unit | Bounded set invalid | Rejects value out of range | STOP BUILD |
| Unit | Bounded auto-reject | OUT_OF_RANGE returned | STOP BUILD |
| Unit | Config reset | Returns to defaults | STOP BUILD |

### 4. Market Layer

| Test Type | Test Name | Pass Condition | Fail Consequence |
|-----------|-----------|---------------|-----------------|
| Unit | Fixture generation | Generates valid OHLCV | STOP BUILD |
| Unit | Hygiene valid | H>=O,C; L<=O,C; H>=L | STOP BUILD |
| Unit | Hygiene invalid | Invalid candle rejected | STOP BUILD |
| Unit | Gap detection | Gap between candles detected | STOP BUILD |
| Unit | OI proxy | OI derived from volume+takerBuyRatio | STOP BUILD |
| Snapshot | market_snapshot | All W fields present | STOP BUILD |
| Integration | MARKET -> TRUTH | market_snapshot flows correctly | STOP BUILD |

### 5. Truth Layer

| Test Type | Test Name | Pass Condition | Fail Consequence |
|-----------|-----------|---------------|-----------------|
| Unit | Supertrend computation | st, stDir, color correct | STOP BUILD |
| Unit | ATR computation | ATR matches expected | STOP BUILD |
| Unit | EMA computation | EMA matches expected | STOP BUILD |
| Unit | MACD computation | MACD line + signal + histogram | STOP BUILD |
| Unit | RSI computation | RSI in 0-100 range | STOP BUILD |
| Unit | W%R computation | W%R in -100-0 range | STOP BUILD |
| Unit | Velocity/Acceleration | vel = wpr - prev; acc = vel - prev | STOP BUILD |
| Unit | Distance computation | dist = |close - st|, distAtr = dist/atr | STOP BUILD |
| Unit | Flip detection | TREND_FLIP_UP/DOWN detected | STOP BUILD |
| Unit | WARMUP state | NULL values, WARMUP status | STOP BUILD |
| Snapshot | truth_snapshot | All W fields present | STOP BUILD |
| Determinism | 2-run identical | Same seed -> same checksum | STOP BUILD |

### 6. Distance Metrics

| Test Type | Test Name | Pass Condition | Fail Consequence |
|-----------|-----------|---------------|-----------------|
| Unit | dist calculation | |close - st| correct | STOP BUILD |
| Unit | distAtr calculation | dist / atr correct | STOP BUILD |
| Unit | dist_ceiling | ceiling - close, NULL on downtrend | STOP BUILD |
| Unit | dist_floor | close - floor, NULL on uptrend | STOP BUILD |
| Unit | ST_DIST_VOL | Rolling stddev correct | STOP BUILD |
| Unit | Distance bucket | OPTIMAL<=0.5, NEAR<=1, EXTENDED<=2, FAR>2 | STOP BUILD |

### 7. Structure Layer

| Test Type | Test Name | Pass Condition | Fail Consequence |
|-----------|-----------|---------------|-----------------|
| Unit | Line building | Lines with >=4 members created | STOP BUILD |
| Unit | Slope building | Transitions between lines | STOP BUILD |
| Unit | Wave classification | All 13 structures reachable | STOP BUILD |
| Unit | Wave < 6 | PENDING_WAVE, not padded | STOP BUILD |
| Unit | HUKUM CAGE 1 wall | cage.status = NONE | STOP BUILD |
| Unit | HUKUM CAGE 2 walls | cage.status = VALID/LOOSE | STOP BUILD |
| Unit | Cage versioning | v0, v1, v2 walls resolved | STOP BUILD |
| Unit | Escape path | Comfortable wall found | STOP BUILD |
| Unit | Market phase | UPTREND/DOWNTREND/SIDEWAY | STOP BUILD |
| Snapshot | structure_snapshot | All W + OD fields present | STOP BUILD |

### 8. Evidence Layer

| Test Type | Test Name | Pass Condition | Fail Consequence |
|-----------|-----------|---------------|-----------------|
| Unit | Direction Bus | ema, oi, vd, mtf scores | STOP BUILD |
| Unit | Exit Bus | rsi, wpr, macd_hist, hold, vel, acc | STOP BUILD |
| Unit | Correction Bus | pp, phase, distances, wave, cage | STOP BUILD |
| Unit | Bus sterility | W%R not in Direction Bus | STOP BUILD |
| Unit | OI insufficient | INSUFFICIENT_DATA when no OI | STOP BUILD |
| Unit | MTF sector | Wave -> MTF mapping correct | STOP BUILD |
| Snapshot | evidence_snapshot | All W fields present | STOP BUILD |

### 9. Clone Layer

| Test Type | Test Name | Pass Condition | Fail Consequence |
|-----------|-----------|---------------|-----------------|
| Unit | LONG observation | 1 obs per candle | STOP BUILD |
| Unit | SHORT observation | 1 obs per candle | STOP BUILD |
| Unit | GRID observation | 1 obs per candle | STOP BUILD |
| Unit | 3 obs/candle | LONG + SHORT + GRID all produce | STOP BUILD |
| Unit | No-trade reason | no_entry_reason populated | STOP BUILD |
| Unit | Entry conjunction | All conditions checked | STOP BUILD |
| Unit | LONG entry | Correct entry when conditions met | STOP BUILD |
| Unit | SHORT entry | Correct entry when conditions met | STOP BUILD |
| Unit | GRID entry | Correct fills when cage valid | STOP BUILD |
| Integration | Card sharing | Shared snapshots read correctly | STOP BUILD |

### 10. Trade Layer

| Test Type | Test Name | Pass Condition | Fail Consequence |
|-----------|-----------|---------------|-----------------|
| Unit | Entry marker | ENTRY_MARKER with sl, tp | STOP BUILD |
| Unit | Exit marker | EXIT_MARKER with P&L | STOP BUILD |
| Unit | P&L LONG | gross = (exit-entry)/entry*100 | STOP BUILD |
| Unit | P&L SHORT | gross = (entry-exit)/entry*100 | STOP BUILD |
| Unit | WIN condition | net > 0 = WIN | STOP BUILD |
| Unit | LOSS condition | net < 0 = LOSS | STOP BUILD |
| Unit | Fee layered | net = gross - fee - slip | STOP BUILD |
| Unit | Adverse-first | SL beats TP on same candle | STOP BUILD |
| Unit | GRID fills | Multiple fills managed | STOP BUILD |

### 11. Position Layer

| Test Type | Test Name | Pass Condition | Fail Consequence |
|-----------|-----------|---------------|-----------------|
| Unit | Position update | hold_c incremented | STOP BUILD |
| Unit | MAE tracking | mae = min(mae, -adverse) | STOP BUILD |
| Unit | MFE tracking | mfe = max(mfe, favorable) | STOP BUILD |
| Unit | Exit decision | Correct priority order | STOP BUILD |
| Unit | Wrong entry early | vel wrong + hold<=2 | STOP BUILD |
| Unit | Wrong entry geom | adverse>=WRONG_PCT + hold<=2 | STOP BUILD |
| Unit | SL hit | Exit at SL price | STOP BUILD |
| Unit | TP hit | Exit at TP price | STOP BUILD |
| Unit | HOLD-veto | MACD expanding delays TP | STOP BUILD |
| Unit | TIME_EXIT | hold>=TIME_EXIT + profit<req | STOP BUILD |

### 12. Simulation Engine

| Test Type | Test Name | Pass Condition | Fail Consequence |
|-----------|-----------|---------------|-----------------|
| Unit | freshState | State created correctly | STOP BUILD |
| Unit | process | 1 candle processed | STOP BUILD |
| Unit | computeAll | All candles processed | STOP BUILD |
| Unit | pipeline stages | All 22 stages executed | STOP BUILD |
| Unit | Card sharing | SHARED stages 1x | STOP BUILD |
| Determinism | 2-run hash | Identical checksums | STOP BUILD |
| Integration | Full pipeline | market->truth->...->governance | STOP BUILD |

### 13. Replay Engine

| Test Type | Test Name | Pass Condition | Fail Consequence |
|-----------|-----------|---------------|-----------------|
| Unit | Candle replay | Candle sequence correct | STOP BUILD |
| Unit | Snapshot replay | Full frame correct | STOP BUILD |
| Unit | Trade replay | Markers correct | STOP BUILD |
| Unit | Clone replay | Observations correct | STOP BUILD |
| Unit | Knowledge replay | Artifacts correct | STOP BUILD |
| Unit | Governance replay | Timeline correct | STOP BUILD |
| Determinism | Replay bit-per-bit | Identical to original | STOP BUILD |

### 14. Statistics Layer

| Test Type | Test Name | Pass Condition | Fail Consequence |
|-----------|-----------|---------------|-----------------|
| Unit | Trade stats | Per-clone metrics correct | STOP BUILD |
| Unit | Sample gate | >=30 = CUKUP, <30 = BELUM_CUKUP | STOP BUILD |
| Unit | Win rate | wins/sample * 100 | STOP BUILD |
| Unit | Expectancy | sum(net)/sample | STOP BUILD |
| Unit | PF | sum(gross_pos)/sum(abs(gross_neg)) | STOP BUILD |
| Unit | Fee drag | sum(fee)/sample | STOP BUILD |
| Unit | Wrong rate | wrong/sample * 100 | STOP BUILD |

### 15. BAG Layer

| Test Type | Test Name | Pass Condition | Fail Consequence |
|-----------|-----------|---------------|-----------------|
| Unit | Grouping | Artifacts grouped by bag_key | STOP BUILD |
| Unit | Classification | bag_kind assigned correctly | STOP BUILD |
| Unit | Consensus | HIGH/MEDIUM/LOW/NONE calculated | STOP BUILD |
| Unit | Conflict | conflict_level calculated | STOP BUILD |
| Unit | Pattern mining | Patterns detected | SOFT |
| Unit | Fingerprint | Distance fingerprint generated | STOP BUILD |
| Unit | Compression | Redundant artifacts compressed | SOFT |
| Unit | No write-back | BAG does not write to upstream | STOP BUILD |

### 16. Knowledge Layer

| Test Type | Test Name | Pass Condition | Fail Consequence |
|-----------|-----------|---------------|-----------------|
| Unit | Academy | win_rate per 4-dim bucket | STOP BUILD |
| Unit | Oracle | Euclidean similarity match | STOP BUILD |
| Unit | HiveMind | intelligence_score 0-10000 | STOP BUILD |
| Unit | CERMIN | calibration_error per clone | STOP BUILD |
| Unit | Librarian | 6 lifecycle statuses | STOP BUILD |
| Unit | Darwin | Proposals generated | STOP BUILD |
| Unit | River | Chronicle appended | STOP BUILD |
| Unit | Unidirectional | No write-back to Core | STOP BUILD |
| Unit | No-ML | No ML detected | STOP BUILD |
| Unit | Oracle vector | W%R/MACD not in vector | STOP BUILD |

### 17. Prediction Layer

| Test Type | Test Name | Pass Condition | Fail Consequence |
|-----------|-----------|---------------|-----------------|
| Unit | Empirical only | no_model = true | STOP BUILD |
| Unit | Sample gate | BELUM_CUKUP -> NULL | STOP BUILD |
| Unit | Intelligence score | 0-10000 range | STOP BUILD |
| Unit | No forecast model | No predictive model detected | STOP BUILD |

### 18. Trading Schema Layer

| Test Type | Test Name | Pass Condition | Fail Consequence |
|-----------|-----------|---------------|-----------------|
| Unit | Market schemas | 10 schemas defined | STOP BUILD |
| Unit | Trading schemas | 7 schemas defined | STOP BUILD |
| Unit | Entry schemas | 11 schemas defined | STOP BUILD |
| Unit | Position schemas | 7 schemas defined | STOP BUILD |
| Unit | Exit schemas | 6 schemas defined | STOP BUILD |
| Unit | Schema completeness | All required fields per schema | STOP BUILD |
| Unit | No spec override | Schema does not modify spec | STOP BUILD |

### 19. Governance Layer

| Test Type | Test Name | Pass Condition | Fail Consequence |
|-----------|-----------|---------------|-----------------|
| Unit | Constitution validation | 18 laws checked | STOP BUILD |
| Unit | Proposal validation | Bounded-check enforced | STOP BUILD |
| Unit | Authority matrix | Indicator usage checked | STOP BUILD |
| Unit | Bounded auto-reject | Out-of-range rejected | STOP BUILD |
| Unit | Rollback | Config reverted | STOP BUILD |
| Unit | No auto-execute | Darwin does not auto-execute | STOP BUILD |
| Unit | No Core write | Governance only writes BOUNDED | STOP BUILD |

### 20. Benchmark Layer

| Test Type | Test Name | Pass Condition | Fail Consequence |
|-----------|-----------|---------------|-----------------|
| Unit | WASIT 5-gate | All gates evaluated | STOP BUILD |
| Unit | Identical -> G2 FAIL | Same config fails G2 | STOP BUILD |
| Unit | Majority vote | Per-gate majority of folds | STOP BUILD |
| Unit | Parallel worker | Worker executes | SOFT |
| Unit | Fallback sequential | Sequential if worker fails | STOP BUILD |

### 21. Consumer Layer

| Test Type | Test Name | Pass Condition | Fail Consequence |
|-----------|-----------|---------------|-----------------|
| Unit | Fund evaluation | Position size, drawdown | STOP BUILD |
| Unit | Veto gate | Risk checks | STOP BUILD |
| Unit | Intent builder | Trade intent constructed | STOP BUILD |
| Unit | CSV export | Markers exported correctly | STOP BUILD |
| Unit | Live adapter disabled | Cannot enable without approval | STOP BUILD |

### 22. Dashboard Layer

| Test Type | Test Name | Pass Condition | Fail Consequence |
|-----------|-----------|---------------|-----------------|
| Unit | No-mock render | Empty = N/A, not placeholder | STOP BUILD |
| Unit | Geometry chart | Candle + ST + cage rendered | STOP BUILD |
| Unit | Clone cards | 3 clone cards rendered | STOP BUILD |
| Unit | Trade history | Table rendered | STOP BUILD |
| Unit | Equity curve | Chart rendered | STOP BUILD |
| Unit | All panels | 20+ panels render without error | STOP BUILD |
| Unit | Read-only | Dashboard does not compute logic | STOP BUILD |

### 23. Integration Layer

| Test Type | Test Name | Pass Condition | Fail Consequence |
|-----------|-----------|---------------|-----------------|
| Unit | Worker bridge | postMessage protocol works | STOP BUILD |
| Unit | Pipeline orchestration | 22 stages in order | STOP BUILD |
| Unit | Card sharing | SHARED 1x, PER-CLONE 3x | STOP BUILD |
| Unit | Serial writer | Single writer, zero race | STOP BUILD |
| Unit | Worker no-direct-DB | Workers do not access IndexedDB | STOP BUILD |

### 24. Audit Layer

| Test Type | Test Name | Pass Condition | Fail Consequence |
|-----------|-----------|---------------|-----------------|
| Unit | 16 self-tests | All pass | STOP BUILD |
| Unit | Pipeline audit | 22 stages verified | STOP BUILD |
| Unit | Snapshot audit | 10 snapshots verified | STOP BUILD |
| Unit | Clone audit | 3 clones, 3 obs/candle | STOP BUILD |
| Unit | Trade audit | P&L, after-fee, adverse-first | STOP BUILD |
| Unit | Knowledge audit | Unidirectional, no-ML | STOP BUILD |
| Unit | Governance audit | Timeline, rollback | STOP BUILD |
| Unit | Fingerprint | Deterministic hash | STOP BUILD |

### 25. Final Validation

| Test Type | Test Name | Pass Condition | Fail Consequence |
|-----------|-----------|---------------|-----------------|
| Unit | Runtime check | State + frames + snapshots | STOP BUILD |
| Unit | Pipeline check | Snapshots per frame | STOP BUILD |
| Unit | Namespace check | 26 namespaces present | STOP BUILD |
| Unit | Feature check | 9 snapshot partitions | STOP BUILD |
| Unit | Truth check | st/stDir/color/atr/ema/rsi/wpr/macd | STOP BUILD |
| Unit | Clone check | LONG/SHORT/GRID present | STOP BUILD |
| Unit | Trading check | entry->position->exit->marker | STOP BUILD |
| Unit | Knowledge check | 7 entities present | STOP BUILD |
| Unit | Replay check | 6 replay types | STOP BUILD |
| Unit | Governance check | 6 validations | STOP BUILD |
| Unit | Constitution check | Audit tests pass | STOP BUILD |
| Unit | Console check | No swallowed errors | STOP BUILD |

### 26. BUILD APPROVAL

| Test Type | Test Name | Pass Condition | Fail Consequence |
|-----------|-----------|---------------|-----------------|
| Integration | 15 stop-rule | All PASS | STOP BUILD |
| Integration | 18 LAW-MASTER | All compliant | STOP BUILD |
| Integration | Determinism | 2-run identical | STOP BUILD |
| Integration | No spec conflict | Zero conflicts | STOP BUILD |
| Integration | No missing component | All components present | STOP BUILD |

---

## TEST CONTRACT STATUS: LOCKED

All test requirements for all 26 phases are constitutionally frozen. LAYER TIDAK BOLEH DILANJUTKAN APABILA TEST GAGAL. Every HARD gate must PASS before proceeding to the next phase.
# 06_CONSUMER_MATRIX.md

## ST-LMS Final Freeze Contract V1 — Consumer Matrix

**Date:** 2026-07-28
**Status:** CONSTITUTIONALLY FROZEN — FINAL

---

## CONSUMER MATRIX: ARTIFACT -> CONSUMER CHAIN

```
FORMAT:
  artifact
    -> consumer_layer
      -> consumer_component
        -> consumer_worker (if applicable)
          -> consumer_schema (if applicable)
```

---

### MARKET LAYER ARTIFACTS

```
market_snapshot
  -> TRUTH
    -> PointBuilder
      -> (main thread)
        -> TRUTH schema

candle_hygiene_report
  -> MARKET (internal)
  -> AUDIT
    -> Pipeline Audit

gap_report
  -> EVIDENCE
    -> maxScore (data quality)
  -> AUDIT
    -> Data Quality Audit

oi_proxy_series
  -> EVIDENCE
    -> oiInherit (OI scoring)
      -> (main thread)
        -> EVIDENCE schema
  -> TRUTH
    -> PointBuilder (OI value)

data_status
  -> TRUTH (point_status propagation)
  -> CLONE (SKIP schema if not FINAL)
  -> DASHBOARD
    -> Market Now Panel
```

### TRUTH LAYER ARTIFACTS

```
truth_snapshot
  -> STRUCTURE
    -> LineBuilder, CageEngine, WaveBuilder, PhaseEngine
      -> (main thread)
        -> STRUCTURE schema
  -> EVIDENCE
    -> dirBus, exitBus, correctionBus
      -> (main thread)
        -> EVIDENCE schema
  -> DISTANCE
    -> dist, distAtr computation
  -> CLONE
    -> dirObserve, gridObserve (via Card Sharing)
      -> (main thread, PER-CLONE)
        -> LONG/SHORT/GRID schema
  -> BAG
    -> Grouping by indicator values
      -> (Knowledge Worker)
        -> BAG schema
  -> KNOWLEDGE
    -> Academy (distance_bucket), Oracle (vector)
      -> (Knowledge Worker)
        -> KNOWLEDGE schema
  -> DASHBOARD
    -> Indicator Gauges, Wave Panel
      -> (main thread, UI render)

stDir
  -> CLONE
    -> dirObserve (entry direction check)
      -> LONG/SHORT schema
  -> STRUCTURE
    -> phase (market phase determination)
  -> TRADING SCHEMA
    -> TREND, REVERSAL, BREAKOUT schemas

atr
  -> STRUCTURE
    -> CageEngine (rangeAtr, wall distance)
  -> CLONE
    -> corridor (volatility adjustment)
    -> dirObserve (TP_ATR_MULT)
  -> DISTANCE
    -> distAtr (normalization)

ema
  -> EVIDENCE
    -> dirBus (ema score)
  -> CLONE
    -> dirObserve (dirOk: ema>5000/ema<5000)

macd_hist
  -> EVIDENCE
    -> exitBus (HOLD-veto: expanding/contracting)
  -> CLONE
    -> decideClose (HOLD-veto check)

rsi
  -> EVIDENCE
    -> exitBus (rsi exit signal)
  -> CLONE
    -> decideClose (EXIT_BUS: RSI>70/RSI<30)
  -> DASHBOARD
    -> Indicator Gauges

wpr
  -> EVIDENCE
    -> exitBus (wpr exit signal)
  -> CLONE
    -> decideClose (EXIT_BUS: WPR>-20/WPR<-80)
  -> DASHBOARD
    -> Indicator Gauges

vel
  -> CLONE
    -> decideClose (WRONG_ENTRY_EARLY: vel against position)
  -> EVIDENCE
    -> exitBus (vel_signal)

acc
  -> EVIDENCE
    -> exitBus (acc_signal)

volDelta
  -> EVIDENCE
    -> dirBus (vd score)
  -> CLONE
    -> dirObserve (dirOk: vd>5000/vd<5000)

flip
  -> TRADING SCHEMA
    -> LONG/SHORT REVERSAL schema activation
  -> BAG
    -> Behavior analysis (flip frequency)
  -> DASHBOARD
    -> Wave Panel

point_status
  -> CLONE
    -> dirObserve (WARMUP -> no entry)
  -> DASHBOARD
    -> Truth Status indicator
```

### DISTANCE LAYER ARTIFACTS

```
distAtr
  -> CLONE
    -> corridor (volatility-adjusted width)
      -> LONG/SHORT schema
  -> EVIDENCE
    -> StDistVol (rolling stddev)
  -> BAG
    -> Fingerprint (d_entry..d_exit dimensions)
    -> Grouping (distance_bucket)
  -> KNOWLEDGE
    -> Academy (distance_bucket: OPTIMAL/NEAR/EXTENDED/FAR)
    -> Oracle (norm01(distAtr,0,3) as vector dimension)
  -> PREDICTION
    -> empirical_win_rate per distance_bucket

dist_ceiling
  -> CLONE
    -> dirObserve (LONG: fee_safe, expected_move)
      -> LONG schema
  -> BAG
    -> Fingerprint, Grouping
  -> TRADING SCHEMA
    -> LONG PULLBACK (ceiling distance for pullback detection)

dist_floor
  -> CLONE
    -> dirObserve (SHORT: fee_safe, expected_move)
      -> SHORT schema
  -> BAG
    -> Fingerprint, Grouping
  -> TRADING SCHEMA
    -> SHORT PULLBACK (floor distance for pullback detection)

sdv (ST_DIST_VOL)
  -> CLONE
    -> corridor (volatility adjustment)
      -> (main thread)
        -> LONG/SHORT schema

p90 (ST_DIST_VOL)
  -> BAG
    -> Behavior analysis (extreme volatility)
  -> TRADING SCHEMA
    -> Volatility regime classification

distance_fingerprint
  -> BAG
    -> Pattern mining (fingerprint clustering)
  -> KNOWLEDGE
    -> Oracle (fingerprint similarity matching)
  -> PREDICTION
    -> empirical_win_rate per fingerprint cluster

distance_bucket
  -> KNOWLEDGE
    -> Academy (bucket dimension)
  -> BAG
    -> Grouping (bag_key dimension)
```

### STRUCTURE LAYER ARTIFACTS

```
structure_snapshot
  -> EVIDENCE
    -> correctionBus, mtfSector
  -> CLONE
    -> dirObserve, gridObserve (via Card Sharing)
      -> LONG/SHORT/GRID schema
  -> BAG
    -> Grouping by market condition
  -> KNOWLEDGE
    -> Academy (structure dimension)
  -> TRADING SCHEMA
    -> All market schemas
  -> DASHBOARD
    -> Cage, Wave, Versioning, Ladder panels

cage
  -> CLONE
    -> dirObserve (floor/ceiling for SL/TP)
    -> gridObserve (cage_valid, width, breakout, pp)
      -> GRID schema
  -> EVIDENCE
    -> correctionBus (pp, phase, distances)
  -> BAG
    -> Grouping (cage status, rangeAtr, breakout)
    -> Behavior analysis (compression/expansion patterns)
  -> TRADING SCHEMA
    -> COMPRESSION, EXPANSION, BREAKOUT, SIDEWAY schemas

wave
  -> EVIDENCE
    -> mtfSector (wave -> MTF mapping)
  -> KNOWLEDGE
    -> Academy (structure dimension)
    -> Oracle (normCodeWave as vector dimension)
  -> BAG
    -> Sequence analysis (wave sequence patterns)
  -> TRADING SCHEMA
    -> CONTINUATION, REVERSAL, EXHAUSTION, RANGE, CHAOS schemas

market_phase
  -> CLONE
    -> Clone activation (which clone is active)
  -> BAG
    -> Grouping (phase distribution)
  -> TRADING SCHEMA
    -> TREND, SIDEWAY schema selection
  -> DASHBOARD
    -> Phase indicator

nearest_support / nearest_resistance
  -> CLONE
    -> dirObserve (fallback SL/TP when cage absent)
      -> LONG/SHORT schema

ladder
  -> BAG
    -> Behavior analysis (trend strength)
  -> TRADING SCHEMA
    -> Trend strength confirmation
  -> DASHBOARD
    -> Ladder Panel
```

### EVIDENCE LAYER ARTIFACTS

```
evidence_snapshot
  -> CLONE
    -> dirObserve, decideClose (via Card Sharing)
      -> LONG/SHORT/GRID schema
  -> HIVEMIND
    -> synth (currentEvidence from evidence_snapshot)
  -> BAG
    -> Grouping by bus values
  -> DASHBOARD
    -> Direction Bus, Exit Bus panels

dir_bus
  -> CLONE
    -> dirObserve (dirOk: ema, vd, mtf_long, mtf_short)
      -> LONG/SHORT schema
  -> BAG
    -> Grouping (direction strength)
  -> DASHBOARD
    -> Direction Bus gauges

exit_bus
  -> CLONE
    -> decideClose (HOLD-veto, EXIT_BUS)
      -> LONG/SHORT schema
  -> BAG
    -> Grouping (exit signal frequency)
  -> DASHBOARD
    -> Exit Bus panel

correction_bus
  -> BAG
    -> Grouping (market context)
  -> TRADING SCHEMA
    -> Market condition validation
  -> DASHBOARD
    -> Correction indicators

oi_score
  -> EVIDENCE
    -> dirBus (oi dimension)
  -> BAG
    -> Grouping (OI patterns)

mtf_sector
  -> EVIDENCE
    -> dirBus (mtf_long, mtf_short)
  -> CLONE
    -> dirObserve (mtf_conflict detection)
  -> BAG
    -> Grouping (MTF patterns)

max_score / data_quality
  -> CLONE
    -> SKIP schema (if quality degraded)
  -> AUDIT
    -> Data Quality Audit
  -> DASHBOARD
    -> Data quality indicator
```

### CLONE LAYER ARTIFACTS

```
clone_observation
  -> TRADE
    -> mkEntry (if entry_allowed)
      -> LONG/SHORT/GRID schema
  -> STATISTICS
    -> tradeStats (observation counting)
  -> BAG
    -> Grouping (observation patterns)
  -> DASHBOARD
    -> Clone Cards

entry_allowed / no_entry_reason
  -> TRADE (entry decision)
  -> BAG
    -> Grouping (entry frequency, rejection reasons)
  -> DASHBOARD
    -> Clone Cards (reason display)

setup_score / confidence
  -> BAG
    -> Grouping (score distribution)
  -> KNOWLEDGE
    -> CERMIN (calibration: predicted vs actual)
  -> DASHBOARD
    -> Clone Cards (score display)
```

### TRADE LAYER ARTIFACTS

```
trade_markers
  -> POSITION
    -> update (mae/mfe/hold_c)
  -> STATISTICS
    -> tradeStats (aggregation)
  -> BAG
    -> Grouping (entry/exit patterns)
    -> Fingerprint (distance at entry/exit)
  -> KNOWLEDGE
    -> Academy (win_rate per bucket)
    -> CERMIN (calibration)
  -> DASHBOARD
    -> Trade History Table, Equity Curve
  -> REPLAY
    -> Trade Replay

entry_marker
  -> POSITION
    -> Position open (entry_price, sl, tp)
  -> BAG
    -> Grouping (entry conditions)

exit_marker
  -> POSITION
    -> Position close (exit_price, P&L)
  -> STATISTICS
    -> tradeStats (win/loss counting)
  -> BAG
    -> Grouping (exit reasons)
    -> Pattern mining (win/loss patterns)
  -> KNOWLEDGE
    -> Academy (outcome per bucket)

result (WIN/LOSS/BREAKEVEN)
  -> STATISTICS
    -> tradeStats (win_rate)
  -> BAG
    -> Consensus (outcome agreement)
  -> KNOWLEDGE
    -> Academy (win counting)
```

### POSITION LAYER ARTIFACTS

```
mae / mfe
  -> STATISTICS
    -> tradeStats (avg mae/mfe)
  -> BAG
    -> Grouping (excursion patterns)
  -> KNOWLEDGE
    -> CERMIN (SL/TP calibration)

hold_count
  -> CLONE
    -> decideClose (TIME_EXIT, WRONG_ENTRY)
  -> STATISTICS
    -> tradeStats (avg_hold)
  -> BAG
    -> Temporal analysis (hold duration patterns)
  -> PREDICTION
    -> Optimal hold duration
```

### STATISTICS LAYER ARTIFACTS

```
statistics_snapshot
  -> BAG
    -> Grouping (all statistics dimensions)
    -> Pattern mining (win_rate patterns)
  -> KNOWLEDGE
    -> Academy (win_rate per bucket)
    -> CERMIN (calibration)
    -> Darwin (proposals)
  -> PREDICTION
    -> empirical_win_rate
  -> BENCHMARK
    -> WASIT (base metrics)
  -> DASHBOARD
    -> Rapor Table

win_rate
  -> KNOWLEDGE
    -> Academy (per bucket)
    -> CERMIN (calibration)
  -> PREDICTION
    -> empirical_win_rate per clone
  -> BAG
    -> Consensus (win_rate agreement)
  -> BENCHMARK
    -> WASIT G4 (win_rate comparison)

expectancy
  -> KNOWLEDGE
    -> Academy (per bucket)
    -> Darwin (TIGHTEN_ENTRY if < 0)
  -> BENCHMARK
    -> WASIT G2 (expectancy comparison)

fee_drag
  -> BENCHMARK
    -> WASIT G5 (fee comparison)
  -> BAG
    -> Grouping (fee impact)

wrong_rate
  -> KNOWLEDGE
    -> Darwin (TIGHTEN_WRONG if > 30)
  -> BAG
    -> Grouping (wrong entry patterns)
```

### BAG LAYER ARTIFACTS

```
bag_artifacts
  -> KNOWLEDGE
    -> Academy (learn from BAG groupings)
    -> Oracle (similarity context)
    -> HiveMind (understanding synthesis)
    -> CERMIN (calibration per bag_key)
    -> Librarian (lifecycle per bag_artifact)
    -> Darwin (proposals from BAG insights)
      -> (Knowledge Worker)
        -> KNOWLEDGE schema
  -> PREDICTION
    -> empirical_win_rate (from BAG groupings)
  -> TRADING SCHEMA
    -> Schema confidence (from BAG consensus)
  -> BENCHMARK
    -> WASIT (grouped evaluation)
  -> DASHBOARD
    -> BAG panels (behavior, patterns)

bag_patterns
  -> KNOWLEDGE
    -> HiveMind (pattern-aware understanding)
  -> DASHBOARD
    -> Pattern Panel

consensus / conflict_level
  -> KNOWLEDGE
    -> HiveMind (conflict-aware synthesis)
    -> Darwin (proposal priority)
  -> TRADING SCHEMA
    -> Schema confidence adjustment

distance_fingerprint
  -> KNOWLEDGE
    -> Oracle (fingerprint similarity)
  -> PREDICTION
    -> empirical_win_rate per fingerprint

behavior_profile
  -> KNOWLEDGE
    -> HiveMind (behavior-aware understanding)
  -> TRADING SCHEMA
    -> Schema selection (based on behavior profile)
```

### KNOWLEDGE LAYER ARTIFACTS

```
knowledge_snapshot
  -> PREDICTION
    -> summarize (empirical + similarity)
  -> GOVERNANCE
    -> validations, decide (from darwin_proposals)
  -> DASHBOARD
    -> Academy Table, Oracle Panel, HiveMind Panel, CERMIN Panel, Librarian Feed

academy_artifacts
  -> PREDICTION
    -> empirical_win_rate per clone per bucket
  -> GOVERNANCE
    -> Darwin proposals (from win_rate/expectancy)
  -> DASHBOARD
    -> Academy Table

oracle_match
  -> HIVEMIND
    -> synth (oracle_boost)
  -> PREDICTION
    -> similarity_score
  -> DASHBOARD
    -> Oracle Panel

hivemind_understanding
  -> PREDICTION
    -> intelligence_score, dominant_bias
  -> DASHBOARD
    -> HiveMind Panel

cermin_calibration
  -> PREDICTION
    -> calibration_error
  -> GOVERNANCE
    -> Runtime validation
  -> DASHBOARD
    -> CERMIN Panel

darwin_proposals
  -> GOVERNANCE
    -> decide (proposal lifecycle)
  -> DASHBOARD
    -> Governance Proposal Panel
```

### PREDICTION LAYER ARTIFACTS

```
prediction_snapshot
  -> TRADING SCHEMA
    -> Schema confidence adjustment
  -> CONSUMER
    -> intentBuilder (trade intent)
  -> DASHBOARD
    -> Prediction Panel

intelligence_score / dominant_bias
  -> TRADING SCHEMA
    -> Schema selection (based on bias)
  -> CONSUMER
    -> intentBuilder (side determination)
  -> DASHBOARD
    -> Prediction Panel

empirical_win_rate
  -> TRADING SCHEMA
    -> Schema confidence (per clone)
  -> CONSUMER
    -> fundEval (position sizing)
  -> GOVERNANCE
    -> Build validation

cermin_error
  -> GOVERNANCE
    -> Runtime validation (calibration check)
  -> CONSUMER
    -> Confidence honesty display
```

### GOVERNANCE LAYER ARTIFACTS

```
config_version
  -> All layers
    -> BOUNDED parameter update
      -> (main thread, boundary application)

proposal
  -> BENCHMARK
    -> WASIT (walk-forward evaluation)
      -> (Benchmark Worker)
        -> BENCHMARK schema

governance_log / rollback_log
  -> AUDIT
    -> Governance Audit
  -> DASHBOARD
    -> Governance Log Panel

validation_results
  -> DASHBOARD
    -> Governance Validation Panel
  -> AUDIT
    -> Constitution Audit
```

### BENCHMARK LAYER ARTIFACTS

```
benchmark_snapshot
  -> GOVERNANCE
    -> decide (WASIT verdict -> proposal decision)
  -> DASHBOARD
    -> WASIT Panel

wasit_verdict / gates_G1_G5
  -> GOVERNANCE
    -> decide (PASS -> PENDING_HUMAN, FAIL -> REJECTED)
  -> DASHBOARD
    -> WASIT Panel (gate details)

per_fold_metrics
  -> GOVERNANCE
    -> decide (per-fold analysis)
  -> DASHBOARD
    -> Per-Fold Panel
```

### SIMULATION + REPLAY ARTIFACTS

```
simulation_state
  -> REPLAY
    -> create (replay session)
  -> AUDIT
    -> Pipeline Audit
  -> DASHBOARD
    -> Simulation UI

replay_frames
  -> DASHBOARD
    -> Replay Viewer (scrubber + playback)
  -> AUDIT
    -> Replay Determinism Audit

determinism_hash
  -> AUDIT
    -> Determinism verification
  -> DASHBOARD
    -> Audit Panel
```

---

## CONSUMER MATRIX STATUS: LOCKED

Complete artifact-to-consumer chain is frozen. Every artifact has a defined consumer path through layers, components, workers, and schemas. No artifact is left unconsumed.
# 07_BUILD_RESTRICTION.md

## ST-LMS Final Freeze Contract V1 — Build Restriction

**Date:** 2026-07-28
**Status:** CONSTITUTIONALLY FROZEN — FINAL

---

## CORE RESTRICTION

```
┌──────────────────────────────────────────────────────────────────┐
│  NO MODIFICATION WITHOUT ARCHITECTURE APPROVAL.                   │
│                                                                    │
│  Every change to the system MUST go through:                      │
│    1. Architecture Review                                         │
│    2. Specification Compliance Check                              │
│    3. Governance Approval (if constitutional)                     │
│    4. Build Validation                                            │
│    5. Documentation Update                                        │
└──────────────────────────────────────────────────────────────────┘
```

---

## 1. NO REFACTOR

```
RESTRICTION: DILARANG MELAKUKAN REFACTOR ARSITEKTUR.

SCOPE:
  - Cannot restructure pipeline stages
  - Cannot reorganize layer hierarchy
  - Cannot rename components
  - Cannot merge layers
  - Cannot split layers
  - Cannot change data flow direction
  - Cannot change card sharing model
  - Cannot change unidirectional flow

EXCEPTION:
  - Refactor allowed ONLY with Architecture Approval
  - Refactor must pass all 15 build-stop rules
  - Refactor must maintain 100% specification compliance
```

---

## 2. NO HIDDEN LOGIC

```
RESTRICTION: DILARANG MENAMBAHKAN LOGIC TERSEMBUNYI.

SCOPE:
  - No logic without card lineage
  - No decision without dependency tracking
  - No value without source specification
  - No computation outside defined pipeline stages
  - No side effects in read operations
  - No implicit state mutation
  - No hidden assumptions in calculations

REQUIREMENT:
  - Every logic path must produce a card
  - Every card must have checksum + lineage
  - Every value must trace to a specification section
  - Every computation must be in a defined pipeline stage
```

---

## 3. NO SQLITE CHANGE

```
RESTRICTION: DILARANG MENGUBAH SQLITE SCHEMA.

SCOPE:
  - No new tables
  - No removed tables
  - No altered columns
  - No new indexes (unless performance-critical with approval)
  - No removed indexes
  - No new constraints (unless data integrity with approval)
  - No removed constraints
  - No new triggers
  - No schema migration without approval

CURRENT SCHEMA: 40 tables, 9 indexes, 4 triggers, 49 FKs, 31 CHECKs, 19 UNIQUEs
STATUS: FROZEN
```

---

## 4. NO NEW PIPELINE

```
RESTRICTION: DILARANG MENAMBAHKAN PIPELINE STAGE BARU.

SCOPE:
  - No new pipeline stages beyond 22 defined stages
  - No changing stage types (SHARED/PER-CLONE/SHARED-AGAIN/ON-DEMAND)
  - No reordering pipeline stages
  - No removing pipeline stages
  - No bypassing pipeline stages
  - No conditional stage skipping

CURRENT PIPELINE: 22 stages
STATUS: FROZEN
```

---

## 5. NO NEW ARTIFACT

```
RESTRICTION: DILARANG MENAMBAHKAN ARTIFACT BARU TANPA APPROVAL.

SCOPE:
  - No new snapshot types beyond 10 defined snapshots
  - No new card types without specification reference
  - No new artifact without owner layer
  - No new artifact without consumer definition

CURRENT ARTIFACTS: 145 artifacts across 20 layers
STATUS: REGISTERED

EXCEPTION:
  - New artifact allowed ONLY with:
    1. Specification reference
    2. Owner layer defined
    3. Consumer chain defined
    4. SQLite mapping defined
    5. Architecture Approval
```

---

## 6. NO NEW WORKER

```
RESTRICTION: DILARANG MENAMBAHKAN WORKER BARU.

SCOPE:
  - No new worker types beyond defined workers
  - No worker accessing IndexedDB directly
  - No worker writing to SQLite
  - No worker bypassing postMessage protocol
  - No persistent/long-running workers (cold workers only)

DEFINED WORKERS:
  - Data Worker (batch bootstrap, TF aggregation)
  - Knowledge Worker (Academy, Oracle, Darwin, Librarian)
  - Benchmark Worker (WASIT parallel)
  - Replay Worker (replay per symbol)
  - Query Worker (long-running SQL queries)
  - Import Worker (CSV/JSON parsing)
  - Export Worker (file formatting)
  - Backup Worker (database backup)
  - Integrity Worker (PRAGMA checks)

EXCEPTION:
  - New worker allowed ONLY with Architecture Approval
  - Worker must follow postMessage contract
  - Worker must be cold (dies after completion)
```

---

## 7. NO NEW SCHEMA

```
RESTRICTION: DILARANG MENAMBAHKAN TRADING SCHEMA BARU TANPA APPROVAL.

SCOPE:
  - No new market schemas beyond 10
  - No new trading schemas beyond 7
  - No new entry schemas beyond 11
  - No new position schemas beyond 7
  - No new exit schemas beyond 6
  - No schema without specification reference

CURRENT SCHEMAS: 41 schemas in 5 categories
STATUS: FROZEN

EXCEPTION:
  - New schema allowed ONLY with:
    1. MASTER_SPECIFICATION reference
    2. All required/optional/forbidden artifacts defined
    3. Confidence source defined
    4. Minimum and exit conditions defined
    5. Consumer defined
    6. Architecture Approval
```

---

## 8. NO SPECIFICATION OVERRIDE

```
RESTRICTION: DILARANG MENGOVERRIDE SPESIFIKASI.

SCOPE:
  - No implementation overriding MASTER_SPECIFICATION
  - No code violating 18 LAW-MASTER
  - No code violating Indicator Authority Matrix
  - No code violating Snapshot rules
  - No code violating Pipeline rules
  - No code violating Clone contract
  - No code violating Knowledge rules
  - No code violating Governance rules

HIERARCHY:
  MASTER_SPECIFICATION.html (APEX — always wins)
    -> DOCUMENT_DEPENDENCY.html
      -> QWEN_14_DOC.html
        -> STLMS_SQLITE_SCHEMA_V1.sql
          -> ST_LMS_CORE.js (MUST NOT override specification)
```

---

## 9. NO PLACEHOLDER

```
RESTRICTION: DILARANG MENGGUNAKAN PLACEHOLDER SEBAGAI DATA.

SCOPE:
  - No "Initializing..." as data value
  - No "No trades yet" as truth
  - No hardcoded $10,000 as account value
  - No 0/5 indicator as real score
  - No mock values in any panel

REQUIREMENT:
  - Empty = N/A (not placeholder)
  - Missing = NULL + status (not neutral fake)
  - Warmup = WARMUP status (not fake values)
  - Insufficient = INSUFFICIENT_DATA (not 5000 for OI)
```

---

## 10. NO TODO

```
RESTRICTION: DILARANG MENINGGALKAN TODO DALAM KODE.

SCOPE:
  - No // TODO comments
  - No // FIXME without resolution plan
  - No unimplemented stubs
  - No placeholder functions
  - No "will implement later"

REQUIREMENT:
  - Every component must be complete before phase gate
  - Incomplete component = BUILD STOP
  - Missing implementation = BUILD STOP
```

---

## 11. NO ASSUMPTION

```
RESTRICTION: DILARANG MEMBUAT ASUMSI TERSEMBUNYI.

SCOPE:
  - No assumed default values without specification
  - No assumed data format without validation
  - No assumed market behavior without evidence
  - No assumed indicator values without computation
  - No assumed config values without CONFIG.get()

REQUIREMENT:
  - Every value must have a source
  - Every default must reference CONFIG or specification
  - Every assumption must be documented and validated
```

---

## 12. BUILD STOP CONDITIONS

```
┌──────────────────────────────────────────────────────────────────┐
│  STOP BUILD IMMEDIATELY IF:                                       │
│                                                                    │
│  1. Specification conflict detected                               │
│  2. Dependency conflict detected                                  │
│  3. Hidden assumption found                                       │
│  4. Architecture violation (backward loop)                        │
│  5. Undefined behavior (missing edge case)                        │
│  6. Undefined component (missing implementation)                  │
│  7. Undefined authority (component outside contract)              │
│  8. Pipeline conflict (wrong stage type)                          │
│  9. Non-determinism detected                                      │
│  10. LAW-MASTER violation                                         │
│  11. Authority matrix violation                                   │
│  12. Mock data found                                              │
│  13. Worker writing directly to IndexedDB                         │
│  14. Date.now() or Math.random() in logic                         │
│  15. W%R/MACD/RSI used for entry decisions                        │
│  16. Backward loop from Knowledge/Consumer to Core                │
│  17. Predictive model in prediction layer                         │
│  18. Auto-execute governance proposal                             │
│  19. Neutral fake values (OI=5000, dist=0)                        │
│  20. Padded wave (wave padded to 6 lines)                         │
│  21. Test failure at HARD gate                                    │
│  22. Missing artifact without owner                               │
│  23. SQLite schema modification without approval                  │
│  24. New pipeline stage without approval                          │
│  25. TODO left in code                                            │
└──────────────────────────────────────────────────────────────────┘
```

---

## BUILD RESTRICTION STATUS: LOCKED

All build restrictions are constitutionally frozen. NO REFACTOR, NO HIDDEN LOGIC, NO SQLITE CHANGE, NO NEW PIPELINE, NO NEW ARTIFACT, NO NEW WORKER, NO NEW SCHEMA without Architecture Approval. Any violation of these restrictions = BUILD STOP.
