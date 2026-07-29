# ST-LMS v3 — RENCANA PERBAIKAN
## 82 GAPS — 28 CRITICAL, 33 HIGH, 18 MEDIUM, 3 LOW

**Date:** 2026-07-29
**Status:** ACTION PLAN — SIAP IMPLEMENTASI

---

## PRIORITY P0 — CRITICAL (Harus Diselesaikan Pertama)

### P0-1: REBUILD Statistics System
**Current:** 1 fungsi `compute_statistics()` di `stlms/statistics/engine.py` (41 lines)
**Target:** 10-domain Market Analyst System

```
stlms/statistics/
  __init__.py
  artifact.py       — StatisticsArtifact(BaseArtifact) → statistics_snapshot Card
  package.py        — StatisticsPackage(BasePackage) → StatisticsReport
  validator.py      — StatisticsValidator(BaseValidator)
  consumer.py       — StatisticsConsumer(BaseConsumer)
  engine.py         — StatisticsEngine (10 domain methods)
  domains/
    market_stats.py      — phase distribution, wave frequency, cage lifetime
    indicator_stats.py   — RSI/W%R/MACD/EMA distribution, extremes, correlation
    distance_stats.py    — bucket distribution, optimal range, volatility
    clone_stats.py       — per-clone, observation-to-entry ratio, activation time
    oi_stats.py          — OI trend, divergence, accumulation rate
    volume_stats.py      — volume profile, delta distribution
    correlation_stats.py — indicator correlation matrix
    regime_stats.py      — market regime classification
    temporal_stats.py    — time-of-day, day-of-week, session performance
    distribution_stats.py— histogram, percentile, outlier detection
```

**Effort:** 4 hari | **Tests:** 50+ unit tests | **Dependencies:** TRUTH, STRUCTURE, EVIDENCE, CLONE

---

### P0-2: ISI TRADE Layer
**Current:** `stlms/trade/__init__.py` — empty (0 bytes)
**Target:** Trade Engine terpisah dari Clone

```
stlms/trade/
  __init__.py
  artifact.py       — TradeArtifact(BaseArtifact) → trade_snapshot Card
  package.py        — TradePackage(BasePackage) → TradeReport
  validator.py      — TradeValidator(BaseValidator)
  consumer.py       — TradeConsumer(BaseConsumer)
  engine.py         — TradeEngine (entry_marker, exit_marker, P&L, fee, slip)
```

**Pindahkan dari clone/engine.py:** TradeMarker, make_exit, fee calculation
**Effort:** 1 hari | **Tests:** 15 unit tests | **Dependencies:** CLONE

---

### P0-3: ISI POSITION Layer
**Current:** `stlms/position/__init__.py` — empty (0 bytes)
**Target:** Position Engine terpisah dari Clone

```
stlms/position/
  __init__.py
  artifact.py       — PositionArtifact(BaseArtifact) → position_snapshot Card
  package.py        — PositionPackage(BasePackage) → PositionReport
  validator.py      — PositionValidator(BaseValidator)
  consumer.py       — PositionConsumer(BaseConsumer)
  engine.py         — PositionEngine (update_position, trailing_stop, partial_tp, breakeven)
```

**Pindahkan dari clone/engine.py:** Position, update_position, trailing stop logic
**Effort:** 1 hari | **Tests:** 15 unit tests | **Dependencies:** TRADE

---

### P0-4: BANGUN DISTANCE Layer
**Current:** Tidak ada directory — 13 artifacts dihitung inline
**Target:** Distance Layer dengan 8 metrics

```
stlms/distance/
  __init__.py
  artifact.py       — DistanceArtifact(BaseArtifact) → distance_snapshot Card
  package.py        — DistancePackage(BasePackage) → DistanceReport
  validator.py      — DistanceValidator(BaseValidator)
  consumer.py       — DistanceConsumer(BaseConsumer)
  engine.py         — DistanceEngine (dist, distAtr, ceiling, floor, sdv, p90, fingerprint, bucket, trend, velocity)
```

**Effort:** 1 hari | **Tests:** 10 unit tests | **Dependencies:** TRUTH, STRUCTURE

---

### P0-5: IMPLEMENTASI CERMIN + RIVER
**Current:** KnowledgeEntity enum has CERMIN + RIVER, no implementation
**Target:** 7/7 Knowledge entities complete

```
stlms/knowledge/
  cermin.py         — CerminEngine (calibration_error per clone, predicted vs actual)
  river.py          — RiverEngine (chronicle, append-only event log)
```

**Effort:** 0.5 hari | **Tests:** 10 unit tests | **Dependencies:** STATISTICS (CERMIN), all cards (RIVER)

---

## PRIORITY P1 — HIGH (Fondasi Arsitektur)

### P1-1: SNAPSHOT System
**Current:** Card implisit via BaseArtifact — tidak ada SnapshotManager
**Target:** Snapshot sebagai sistem cross-cutting

```
stlms/snapshot/
  __init__.py
  manager.py        — SnapshotManager (produce, freeze, store, consume, replay)
  registry.py       — SnapshotRegistry (10 snapshot types registered)
  validator.py      — SnapshotValidator (W/OD check, lineage, determinism)
  consumer.py       — SnapshotConsumer (API untuk REPLAY, AUDIT, DASHBOARD)
```

**Effort:** 1 hari | **Tests:** 15 unit tests | **Dependencies:** Semua layer artifact

---

### P1-2: PRODUCE ARTIFACT CARDS — Semua Layer
**Current:** Hanya MARKET + TRUTH yang produce Card. 8 layer lain tidak.
**Target:** Setiap layer produce immutable Card via BaseArtifact

| Layer | Card Type | File |
|-------|-----------|------|
| STRUCTURE | structure_snapshot | structure/artifact.py |
| EVIDENCE | evidence_snapshot | evidence/artifact.py |
| CLONE | clone_observation | clone/artifact.py |
| TRADE | trade_snapshot | trade/artifact.py |
| POSITION | position_snapshot | position/artifact.py |
| STATISTICS | statistics_snapshot | statistics/artifact.py |
| BAG | bag_artifact | bag/artifact.py |
| KNOWLEDGE | knowledge_snapshot | knowledge/artifact.py |
| PREDICTION | prediction_snapshot | prediction/artifact.py |
| BENCHMARK | benchmark_snapshot | bench/artifact.py |
| GOVERNANCE | config_version | governance/artifact.py |
| DISTANCE | distance_snapshot | distance/artifact.py |

**Effort:** 2 hari | **Tests:** 30 unit tests | **Dependencies:** BaseArtifact

---

### P1-3: PACKAGE + VALIDATOR + CONSUMER — Semua Layer
**Current:** Hanya MARKET + TRUTH yang punya Package/Validator/Consumer
**Target:** 13 layer punya 4-output structure

**Effort:** 2 hari | **Tests:** 40 unit tests | **Dependencies:** BasePackage, BaseValidator, BaseConsumer

---

### P1-4: ENFORCE FORBIDDEN DEPENDENCIES
**Current:** 10 forbidden dependencies didefinisikan di kontrak, tidak ada runtime check
**Target:** ArchitectureValidator yang mengecek:

```
- KNOWLEDGE → CORE/CLONE (backward loop)
- CONSUMER → CORE/CLONE (backward loop)
- BAG → TRUTH/STRUCTURE (upstream write)
- GOVERNANCE → TRUTH/STRUCTURE (except BOUNDED)
- WORKER → INDEXEDDB (direct write)
- CLONE → ORACLE/HIVEMIND (direct read)
- TRADE → W%R/MACD/RSI for entry
- GRID → stDir/MTF
- DARWIN → AUTO-EXECUTE
- PREDICTION → MODEL
```

**Effort:** 0.5 hari | **Tests:** 10 unit tests | **Dependencies:** Integration

---

## PRIORITY P2 — MEDIUM (Enrichment)

### P2-1: BAG Enrichment (14 Operasi)
**Current:** Hanya `group_by_clone_structure()`. 14 operasi lain stub.
**Target:** Full BAG dengan pattern mining, fingerprint, behavior analysis

```
stlms/bag/
  pattern_miner.py     — association rules, clustering, anomaly
  fingerprint.py       — distance fingerprint 12-dimensi
  behavior.py          — 6 behavior profiles
  sequence.py          — wave/cage/trade sequence analysis
  temporal.py          — time-based pattern analysis
  compressor.py        — artifact deduplication
```

**Effort:** 2 hari | **Tests:** 20 unit tests | **Dependencies:** STATISTICS

---

### P2-2: Recommendation — 12 Section Tambahan
**Current:** 8/20 sections. Missing: Market Identity, Market Character, Distance, Snapshot, Statistics, Entry/Position/Exit Truth, Risk, Invalidation.
**Target:** 20/20 sections sesuai contract.

**Effort:** 1 hari | **Tests:** 10 unit tests | **Dependencies:** STATISTICS, KNOWLEDGE, PREDICTION

---

### P2-3: Schema — 20 Schema Tambahan
**Current:** 21/41 schemas. Missing: Trading (7), Position (7), Exit (6).
**Target:** 41/41 schemas dengan full artifact registry.

**Effort:** 1 hari | **Tests:** 10 unit tests | **Dependencies:** STATISTICS

---

### P2-4: Clone Observation Log
**Current:** Observasi hanya di memori. NO_TRADE tidak disimpan.
**Target:** Semua observasi (termasuk NO_TRADE) disimpan sebagai Card.

**Effort:** 0.5 hari | **Tests:** 5 unit tests | **Dependencies:** CLONE

---

## PRIORITY P3 — MEDIUM-LOW (Simulation + Runtime)

### P3-1: Simulation — 5 Simulator Sebenarnya
**Current:** 5 stub validator. Bukan simulator.
**Target:** 5 simulator yang benar-benar menjalankan simulasi.

**Effort:** 3 hari | **Tests:** 25 unit tests | **Dependencies:** Semua layer

---

### P3-2: Runtime System
**Current:** Tidak ada runtime monitoring.
**Target:** Progress bar, ETA, throughput, memory, error tracking.

```
stlms/runtime/
  monitor.py        — RuntimeMonitor (progress, ETA, memory, CPU)
  reporter.py       — RuntimeReporter (per-stage status, warnings, errors)
```

**Effort:** 1 hari | **Tests:** 5 unit tests | **Dependencies:** Integration

---

### P3-3: CLI Per-Layer
**Current:** 7 foundation commands. Tidak ada per-layer CLI.
**Target:** 20+ commands — `stlms truth status`, `stlms statistics market`, dll.

**Effort:** 1 hari | **Tests:** 10 unit tests | **Dependencies:** Semua layer

---

## PRIORITY P4 — LOW (Infrastructure)

### P4-1: SQLite Statistics Explorer
**Current:** Hanya table browser. Tidak ada agregasi query.
**Target:** Statistics Explorer dengan GROUP BY, AVG, SUM, COUNT, time-series.

**Effort:** 0.5 hari | **Tests:** 5 unit tests | **Dependencies:** SQLite

---

### P4-2: Integration Orchestrator
**Current:** Pass-through aggregator. Tidak menjalankan pipeline.
**Target:** Orchestrator yang benar-benar mengeksekusi 23 stages.

**Effort:** 1 hari | **Tests:** 10 unit tests | **Dependencies:** Semua layer

---

### P4-3: AUDIT + DASHBOARD + REPLAY
**Current:** Tidak ada code sama sekali.
**Target:** Minimal implementation untuk 3 cross-cutting layers.

**Effort:** 2 hari | **Tests:** 15 unit tests | **Dependencies:** Snapshot, semua layer

---

## IMPLEMENTATION TIMELINE

| Week | Priority | Tasks | Effort |
|------|----------|-------|--------|
| **Week 1** | P0 | Statistics REBUILD, TRADE, POSITION, DISTANCE, CERMIN+RIVER | 4.5 hari |
| **Week 2** | P1 | Snapshot System, Artifact Cards semua layer, Package+Validator+Consumer, Forbidden Deps | 5.5 hari |
| **Week 3** | P2 | BAG Enrichment, Recommendation 12 sections, Schema 20 schemas, Clone Observation Log | 4.5 hari |
| **Week 4** | P3 | Simulation 5 simulators, Runtime System, CLI per-layer | 5 hari |
| **Week 5** | P4 | SQLite Explorer, Integration Orchestrator, AUDIT+DASHBOARD+REPLAY | 3.5 hari |

**Total: ~23 hari kerja untuk menutup 82 gaps.**

---

## SUCCESS CRITERIA

| Criteria | Target |
|----------|--------|
| Semua 13 layer produce Artifact+Package+Validator+Consumer | 13/13 |
| Semua 145 artifacts diproduce sebagai immutable Card | 145/145 |
| Statistics System 10 domain | 10/10 |
| Knowledge 7/7 entities | 7/7 |
| Recommendation 20/20 sections | 20/20 |
| Trading Schema 41/41 | 41/41 |
| Simulation 5 simulators sebenarnya | 5/5 |
| Unit tests | 102 → 350+ |
| Benchmark tests | 10 → 25+ |

---

## RISIKO

| Risiko | Mitigasi |
|--------|----------|
| Statistics REBUILD mempengaruhi 6 downstream layer | Update dependency contract sebelum mulai |
| TRADE + POSITION dipisah dari Clone — breaking change | Pindahkan logic, jangan duplikasi |
| Timeline 5 minggu terlalu optimis | Prioritaskan P0+P1 dulu (2 minggu), sisanya bisa paralel |
| Test coverage rendah setelah rebuild | TDD: tulis test sebelum kode |
