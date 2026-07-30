# ST-LMS v4 — Test Report 1220

**Date:** 2026-07-30 12:20 WIB
**System:** ST-LMS v4.0.0 — Market Evolution Operating System
**Repository:** andiputra3/st_lms_V_4-5
**Branch:** build/phase-0-rebuild

---

## 1. EXECUTIVE SUMMARY

| Metric | Value |
|--------|-------|
| Total tests | **165** (155 unit + 10 benchmark) |
| Passed | **165** |
| Failed | **0** |
| Errors | **0** |
| Execution time | **2.17s** |
| Peak memory | **53.3 MB** |
| Doctor health score | **95% [EXCELLENT]** |
| Python modules | **132** production |
| Test files | **7** |
| SQLite tables | **40** (verified) |
| Pipeline stages | **23/23** (verified) |

### Verdict: ST-LMS IS HEALTHY. ALL TESTS PASSED.

---

## 2. TEST CATEGORY BREAKDOWN

### 2.1 Foundation Tests (32 tests — `test_foundation.py`)

| Class | Tests | Purpose |
|-------|-------|---------|
| TestCoreTypes | 2 | Candle dataclass, Enum values |
| TestCoreUtils | 8 | Canonical string, Card, clamp, ID generator, norm01, PRNG determinism, round precision, SHA-256 |
| TestCoreValidators | 5 | Bounded validation, sample gate, symbol validation |
| TestFoundationComponents | 5 | Config manager, registry, resource manager, symbol manager, time manager |
| TestImportAll | 4 | CLI, core, foundation, SQLite imports |
| TestSQLiteFoundation | 8 | Benchmark, connection, index count, integrity, seed data, table count, validator, viewer query |

**Result:** 32/32 PASS

---

### 2.2 Market Tests (18 tests — `test_market.py`)

| Class | Tests | Purpose |
|-------|-------|---------|
| TestMarketArtifact | 4 | Card immutability, OI in card, produce cards, input validation |
| TestMarketConsumer | 3 | Consume card, to candles, to OI series |
| TestMarketFixture | 5 | Candle hygiene, determinism, generate candles, multiple symbols, OI series |
| TestMarketImport | 1 | All imports |
| TestMarketPackage | 2 | Build report, summary |
| TestMarketValidator | 3 | All validator pass, clean candles, sequence validation |

**Result:** 18/18 PASS

---

### 2.3 Phase 03-12 Tests (27 tests — `test_phase_03_12.py`)

| Class | Tests | Purpose |
|-------|-------|---------|
| TestTruthPoint | 5 | Build points, warmup→valid, flip detection, indicators in range, determinism |
| TestTruthArtifact | 1 | Produce card with verification |
| TestTruthPackage | 1 | Build package |
| TestStructureLine | 1 | Build lines from SPs |
| TestStructureWave | 1 | Build waves from lines |
| TestStructureCage | 1 | Build cage from lines |
| TestEvidence | 3 | Correction bus, direction bus, exit bus sterility (W%R/MACD/RSI exit-only) |
| TestCloneEngine | 5 | Exit priority, grid observation, long/short observation, make exit PnL |
| TestBAG | 1 | Group by clone structure |
| TestStatistics | 1 | Compute statistics |
| TestKnowledge | 5 | Academy, Darwin, HiveMind, Librarian, Oracle |
| TestPrediction | 1 | Predict |
| TestImportAll | 1 | All imports |

**Result:** 27/27 PASS

---

### 2.4 Phase 13-20 Tests (25 tests — `test_phase_13_20.py`)

| Class | Tests | Purpose |
|-------|-------|---------|
| TestSchema | 6 | Active clones, entry grid, entry/market schema counts, select breakout, select compression |
| TestRecommendation | 1 | Build report |
| TestSimulation | 2 | Architecture, balance |
| TestConsumer | 6 | CSV export, fund eval, intent grid, live disabled, veto allow/reject |
| TestBenchmark | 2 | WASIT better candidate, WASIT identical fails |
| TestGovernance | 5 | Approve, propose out-of-range/valid, rollback, validations |
| TestIntegration | 2 | Architecture validation, pipeline report |
| TestImportAll | 1 | All imports |

**Result:** 25/25 PASS

---

### 2.5 Market Evolution Tests (53 tests — `test_market_evolution.py`)

| Class | Tests | Purpose |
|-------|-------|---------|
| **TestMarketIsAlive** | 5 | Market entities exist, observations produced, memory populated, snapshots produced, statistics computed |
| **TestEntityLifecycle** | 8 | TruthPoint, Line, Wave, Cage, Clone, Knowledge, Prediction, Market DNA lifecycle |
| **TestEntityMutation** | 3 | Mutations recorded, mutation statistics valid, version increments on mutation |
| **TestEntityVersioning** | 3 | TruthPoint version, Line mutation_count, Wave reliability tracking |
| **TestMarketEvolution** | 4 | Lines evolve, waves evolve, market character changes, DNA forms |
| **TestMarketDNA** | 4 | DNA profile exists, wave distribution, cage distribution, market character |
| **TestKnowledgeEvolution** | 4 | Academy learns from BAG, Oracle matches historical, HiveMind evolution context, HiveMind historical learning |
| **TestObservationMemory** | 6 | LIVE observation, frozen observations, rotation, eviction when full, get_range, get_latest |
| **TestSnapshotIntegrity** | 4 | All types produced, counts consistent, market snapshot, truth snapshot |
| **TestTimeline** | 2 | Observation timeline, range query |
| **TestSQLitePersistence** | 3 | Tables exist, writes data, queries return data |
| **TestPipelineIntegration** | 4 | Pipeline complete, 23 stages executed, prediction not signal, persistence toggle |
| **TestPerformance** | 3 | 100, 500, 1000 observations under time limit |

**Result:** 53/53 PASS

---

### 2.6 Benchmark Tests (10 tests — `stlms/benchmarks/`)

| Class | Tests | Purpose |
|-------|-------|---------|
| TestFoundationBenchmark | 5 | Determinism, import speed, memory friendly, SQLite insert/select speed |
| TestMarketBenchmark | 5 | Artifact production speed, fixture generation speed, memory footprint, package build speed, validation speed |

**Result:** 10/10 PASS

---

## 3. MARKET EVOLUTION TEST — DETAILED RESULTS

### 3.1 Market Is Alive

| Test | Result | Evidence |
|------|--------|----------|
| Market entities exist | ✅ PASS | All 41 living market entities present |
| Observations produced | ✅ PASS | 200 observations in MarketObservationMemory |
| Memory populated | ✅ PASS | 1 LIVE + 199 FROZEN observations |
| Snapshots produced | ✅ PASS | 225 snapshot cards across 11 types |
| Statistics computed | ✅ PASS | All 7 statistics domains have data |

### 3.2 Entity Lifecycle

| Entity | Result | States Verified |
|--------|--------|----------------|
| TruthPoint | ✅ PASS | Goes through WARMUP→VALID lifecycle |
| Line | ✅ PASS | Constructed from TruthPoints, has mutation_count |
| Wave | ✅ PASS | Constructed from Lines, has 13 structure types |
| Cage | ✅ PASS | Built from Lines, has NONE/COMPRESSION/SIDEWAY states |
| Clone | ✅ PASS | LONG/SHORT/GRID produce snapshots |
| Knowledge | ✅ PASS | Academy, Oracle, HiveMind engines active |
| Prediction | ✅ PASS | Market possibilities produced |
| Market DNA | ✅ PASS | DNA profile extracted from waves+cages+SPs |

### 3.3 Entity Mutation

| Test | Result | Evidence |
|------|--------|----------|
| Mutations recorded | ✅ PASS | Mutation deltas present in observations |
| Mutation statistics valid | ✅ PASS | Delta keys: price, st, atr, rsi, wpr, macd, dist_atr, oi, flip |
| Version increments | ✅ PASS | Versions increase when mutations occur |

### 3.4 Observation Memory

| Test | Result | Evidence |
|------|--------|----------|
| LIVE observation | ✅ PASS | Exactly 1 LIVE observation at any time |
| Frozen observations | ✅ PASS | Historical observations frozen after new candle |
| Rotation works | ✅ PASS | Freeze→append cycle maintains LIVE/FROZEN states |
| Eviction when full | ✅ PASS | Oldest evicted when buffer reaches max_size |
| get_range | ✅ PASS | Correct slice returned for index range |
| get_latest | ✅ PASS | Correct count of latest observations returned |

### 3.5 Knowledge Evolution

| Test | Result | Evidence |
|------|--------|----------|
| Academy learns from BAG | ✅ PASS | Academy engine produces learning results |
| Oracle matches historical | ✅ PASS | 9-dim vector matching against history |
| HiveMind evolution context | ✅ PASS | evolution_context parameter accepted |
| HiveMind historical learning | ✅ PASS | Historical learning insights generated |

### 3.6 Performance

| Observation Count | Result | Requirement |
|-------------------|--------|-------------|
| 100 | ✅ PASS | Under 5s time limit |
| 500 | ✅ PASS | Under 5s time limit |
| 1000 | ✅ PASS | Under 5s time limit |

---

## 4. DOCTOR DIAGNOSTIC

| Check | Status | Detail |
|-------|--------|--------|
| Python Version | ✅ PASS | 3.12.3 (>= 3.10 required) |
| Disk Space | ✅ PASS | 28.5 GB free of 39.3 GB |
| Memory | ✅ PASS | 14.8 MB process memory |
| Network | ✅ PASS | Connected |
| Directory Structure | ✅ PASS | All 24 core directories present |
| Configuration | ✅ PASS | ~/.stlms/config.json (BTCUSDT 1m) |
| SQLite Available | ✅ PASS | 3.45.1 |
| Database Integrity | ✅ PASS | integrity_check: ok |
| Module Imports | ✅ PASS | All 42 core modules import successfully |
| Pipeline | ⚠️ WARN | 23/23 stages — OK (warning is for log check, not failure) |

**Health Score: 95% [EXCELLENT]**

---

## 5. ARCHITECTURAL COMPLIANCE

| Check | Result |
|-------|--------|
| 22 pipeline stages | ✅ All 23 executed (22 + OPT) |
| 26 layers | ✅ All present |
| 40 SQLite tables | ✅ All exist, integrity ok |
| 15 build-stop rules | ✅ All PASS |
| 18 LAW-MASTER | ✅ All compliant |
| W%R/MACD exit-only | ✅ Verified by test_exit_bus_sterility |
| Oracle vector 9-dim frozen | ✅ W%R/MACD not in vector |
| Sample gate ≥ 30 | ✅ Enforced in Academy |
| Live DISABLED | ✅ Verified |
| Prediction ≠ BUY/SELL | ✅ no_model=true |
| No circular dependencies | ✅ Verified |

---

## 6. ENRICHMENT STATUS

| System | Status | Tests |
|--------|--------|-------|
| MarketObservationMemory | ✅ Wired | 6 tests PASS |
| TruthObservationObject | ✅ Wired | Verified in lifecycle tests |
| StructureObservationObject | ✅ Wired | Verified in lifecycle tests |
| MutationTracker | ✅ Wired | 3 tests PASS |
| ReliabilityScorer | ✅ Wired | Verified in versioning tests |
| EvolutionLifecycleManager | ✅ Wired | Verified in lifecycle tests |
| 7 Statistics Domains | ✅ Wired | 5 tests PASS |
| SnapshotManager | ✅ Wired | 4 tests PASS |
| SQLite Persistence | ✅ Wired | 3 tests PASS |
| Market DNA | ✅ Wired | 4 tests PASS |
| HiveMind evolution_context | ✅ Wired | 2 tests PASS |
| Prediction enrichment | ✅ Wired | Verified |
| Recommendation enrichment | ✅ Wired | Verified |

---

## 7. SYSTEM INVENTORY

| Component | Count |
|-----------|-------|
| Python modules (production) | 132 |
| Python modules (tests) | 7 |
| Python modules (benchmarks) | 3 |
| SQLite tables | 40 |
| Living market entities | 41 |
| Pipeline stages | 23 |
| Statistics domains | 7 |
| Snapshot types | 11 |
| CLI subcommands | 22 |
| Web dashboard pages | 17 |
| API endpoints | 17 |
| Doctor checks | 10 |

---

## 8. COMMANDS

```bash
stlms test        # Full 165-test suite
stlms doctor      # 10 diagnostic checks
stlms run         # Pipeline with defaults (BTCUSDT, 1m, 48000)
stlms statistics  # All 7 statistics domains
stlms dashboard   # Web dashboard on :8082
stlms health      # Quick health check
```

---

**Test Report completed 2026-07-30 12:20 WIB.**
**165/165 tests PASS. 0 failures. 0 errors.**
**ST-LMS v4 is healthy and ready for operation.**
