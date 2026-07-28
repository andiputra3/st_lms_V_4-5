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
