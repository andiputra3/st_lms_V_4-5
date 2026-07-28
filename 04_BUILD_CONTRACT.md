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
