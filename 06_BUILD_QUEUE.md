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
