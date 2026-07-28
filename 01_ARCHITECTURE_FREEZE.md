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
