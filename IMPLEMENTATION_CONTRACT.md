# IMPLEMENTATION CONTRACT — ST-LMS v3

## Native HTML Market Geometry Intelligence Operating System

**Date:** 2026-07-28
**Phase:** PHASE 0 — Prompt 03
**Status:** CONSTITUTIONALLY FROZEN
**Sources:** DOCUMENT_DEPENDENCY.html §8–§9, QWEN_14_DOC.html D12–D13, MASTER_SPECIFICATION.html §13

---

## 1. THREE-LAYER BUILD ARCHITECTURE

```
┌──────────────────────────────────────────────────────────────────────────┐
│                        FOUNDATION LAYER                                   │
│                                                                           │
│  Specifications          SQLite Schema          Build Contract            │
│  (MASTER_SPECIFICATION,  (stlms_sqlite_         (BUILD_CONTRACT.md,       │
│   DOCUMENT_DEPENDENCY,   schema_v1.sql)         IMPLEMENTATION_CONTRACT   │
│   QWEN_14_DOC,                                                     .md)  │
│   TRADING_SCHEMA_                                                        │
│   FREEZE, TRUTH_LAYER_                                                   │
│   FREEZE, DECISION_                                                      │
│   TREE_FREEZE)                                                           │
│                                                                           │
│  ↓                                                                        │
│                                                                           │
│  Bedrock Components:                                                      │
│  decimal/int-tick, canonical, id, wib, hash, prng, lifecycle, card,       │
│  validator, bus, bounded, governor, IndexedDB writer-serial               │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                        IMPLEMENTATION LAYER                               │
│                                                                           │
│  MARKET ──▶ TRUTH ──▶ STRUCTURE ──▶ EVIDENCE                             │
│                                                                           │
│  CLONE (LONG/SHORT/GRID) ──▶ TRADE ──▶ POSITION                          │
│                                                                           │
│  STATISTICS ──▶ KNOWLEDGE ──▶ PREDICTION                                 │
│                                                                           │
│  REPLAY ──▶ SIMULATION ──▶ GOVERNANCE                                    │
│                                                                           │
│  CONSUMER ──▶ AUDIT ──▶ BENCHMARK ──▶ VIEW                               │
│                                                                           │
│  SQLITE VIEWER ──▶ SQLITE MANAGER ──▶ DECISION TREE                      │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                        INTEGRATION LAYER                                  │
│                                                                           │
│  Workers (Data, Knowledge, Benchmark, Replay)                             │
│  Integration Testing                                                      │
│  Performance Testing                                                      │
│  Benchmark Validation                                                     │
│  Final Audit                                                              │
│  Build Approval                                                           │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 2. COMPONENT BUILD ORDER

### 2.1 Foundation Layer (S1–S2)

```
ORDER  COMPONENT              DEPENDS ON            PRODUCES
─────  ─────────────────────  ────────────────────  ────────────────────────
1.1    Decimal / Int-Tick     None                  CORE.ASSETS, toTick, fromTick
1.2    Canonical String       Decimal               CORE.canon, CORE.roundPrec
1.3    ID Generator           Canonical, WIB        ID.gen (deterministic)
1.4    WIB Clock              None                  CORE.wib
1.5    SHA-256 Hash           None                  CRYPTO.sha256
1.6    PRNG (Mulberry32)      None                  CORE.prng, CORE.seedFrom
1.7    Lifecycle Manager      None                  Card lifecycle states
1.8    Card Factory           ID, Hash, WIB         CARD.mk, CARD.verify
1.9    Validator              Card                  Card validation logic
1.10   Bus Factory            None                  Direction/Exit/Correction buses
1.11   Bounded Registry       None                  CONFIG (all bounded params)
1.12   Governor               Bounded               CONFIG.get/set/valid
1.13   IndexedDB Writer       Card                  WORKSPACE (serial writer)
───    ─────────────────────  ────────────────────  ────────────────────────
2.1    BOOT                   1.1–1.13              System initialization
2.2    Workspace Manager      BOOT                  Tiered storage setup
2.3    Checkpoint Manager     Workspace             State save/resume
2.4    Config Loader          BOOT                  Config version loading
```

### 2.2 Implementation Layer (S3–S14)

```
ORDER  COMPONENT              DEPENDS ON            PRODUCES
─────  ─────────────────────  ────────────────────  ────────────────────────
3.1    Data Worker            Bedrock               Batch data processing
3.2    Hygiene Validator      Bedrock               MARKET.hygiene
3.3    Gap Detector           Bedrock               MARKET.gaps
3.4    OI Proxy Generator     Bedrock               MARKET.oiProxy
3.5    Market Snapshot Engine 3.1–3.4               market_snapshot card
───    ─────────────────────  ────────────────────  ────────────────────────
4.1    Point Builder          MARKET                TRUTH.PointBuilder
4.2    Supertrend             Point Builder         st, stDir, color
4.3    ATR/EMA/MACD/RSI/W%R   Point Builder         All indicators
4.4    Flip Detector          Supertrend            Trend flip events
4.5    Truth Snapshot         4.1–4.4               truth_snapshot card
───    ─────────────────────  ────────────────────  ────────────────────────
5.1    Line Builder           TRUTH                 Line segments
5.2    Slope Builder          TRUTH + Lines         Slope transitions
5.3    Wave Builder           Lines + Slopes        Wave classification (13)
5.4    Cage Engine            Lines + Price + ATR   Cage with versioning
5.5    Ladder Analyzer        Lines                 Ladder patterns
5.6    Nearest Finder         Lines                 Nearest S/R
5.7    Phase Engine           Cage + Wave + stDir   Market phase
5.8    Distance Engine        Cage + Close          dist_ceiling, dist_floor
5.9    Structure Snapshot     5.1–5.8               structure_snapshot card
───    ─────────────────────  ────────────────────  ────────────────────────
6.1    Direction Bus          TRUTH                 Entry-legal witnesses
6.2    Exit Bus               TRUTH                 Close-only exit signals
6.3    Correction Bus         TRUTH + STRUCTURE     Market context
6.4    OI Inheritor           MARKET                OI scoring
6.5    MTF Sector             STRUCTURE             MTF classification
6.6    Max Score              EVIDENCE              Data quality ceiling
6.7    ST-Dist-Vol            TRUTH                 Volatility proxy
6.8    Evidence Snapshot      6.1–6.7               evidence_snapshot card
───    ─────────────────────  ────────────────────  ────────────────────────
7.1    Clone Orchestrator     EVIDENCE              Clone activation mgmt
7.2    LONG Clone             STRUCTURE+EVIDENCE    LONG observations
7.3    SHORT Clone            STRUCTURE+EVIDENCE    SHORT observations
7.4    GRID Clone             STRUCTURE            GRID observations
7.5    Entry Corridor         CLONE                 Adaptive entry zone
7.6    Global Risk Validator  CLONE                 Exposure limits
7.7    Entry Marker           TRADE                 ENTRY_MARKER
7.8    Exit Marker            TRADE                 EXIT_MARKER (P&L)
7.9    Position Manager       TRADE                 Position state
7.10   MAE/MFE Tracker        POSITION              Excursion tracking
7.11   Profit Lock            POSITION              Partial TP
7.12   Trailing Stop          POSITION              ATR-based trail
7.13   Breakeven Manager      POSITION              SL to entry
7.14   Wrong Entry Guard      POSITION              Wrong entry detection
───    ─────────────────────  ────────────────────  ────────────────────────
8.1    Simulation Engine      CLONE+TRADE+POSITION  Trade execution
8.2    Historical Sim         SIMULATION            Fixture replay
8.3    Live Sim               SIMULATION            Real-time feed
8.4    Strategy Sim           SIMULATION            Single clone study
8.5    Clone Sim              SIMULATION            3-clone parallel
8.6    Candle Replay          REPLAY                Candle sequence
8.7    Snapshot Replay        REPLAY                Full frame replay
8.8    Trade Replay           REPLAY                Trade history replay
8.9    Clone Replay           REPLAY                Clone observation replay
8.10   Knowledge Replay       REPLAY                Knowledge evolution replay
8.11   Governance Replay      REPLAY                Governance timeline replay
8.12   Determinism Verifier   SIMULATION            2-run hash compare
───    ─────────────────────  ────────────────────  ────────────────────────
9.1    Trade Statistics       TRADE                 Per-clone stats
9.2    Market Statistics      STATISTICS            Market-level stats
9.3    Sample Gate            STATISTICS            CUKUP/BELUM_CUKUP
9.4    River                  All cards             Chronicle
9.5    Academy                STATISTICS            Win rate per bucket
9.6    Oracle                 TRUTH+STRUCTURE+EV    Similarity matching
9.7    HiveMind               Academy+Oracle+EV     Understanding synthesis
9.8    CERMIN                 STATISTICS            Calibration error
9.9    Librarian              Academy               Lifecycle management
9.10   Darwin                 Academy               Parameter proposals
9.11   Knowledge Worker       9.4–9.10              Batch knowledge compute
───    ─────────────────────  ────────────────────  ────────────────────────
10.1   WASIT 5-Gate           BENCHMARK             Walk-forward validation
10.2   WASIT Parallel         BENCHMARK             Worker-based parallel
10.3   Walk-Forward Engine    BENCHMARK             Base vs candidate
10.4   Benchmark Worker       10.1–10.3             Parallel benchmark
───    ─────────────────────  ────────────────────  ────────────────────────
11.1   Empirical Aggregator   KNOWLEDGE             Win rate per clone
11.2   Similarity Aggregator  KNOWLEDGE             Oracle score
11.3   Intelligence Aggregator KNOWLEDGE            HiveMind score
11.4   Calibration Aggregator KNOWLEDGE             CERMIN error
11.5   Prediction Snapshot    11.1–11.4             prediction_snapshot
───    ─────────────────────  ────────────────────  ────────────────────────
12.1   Constitution Validator GOVERNANCE            18-law check
12.2   Proposal Validator     GOVERNANCE            Bounded + label-peran
12.3   Authority Validator    GOVERNANCE            Indicator column check
12.4   Build Validator        GOVERNANCE            15 stop-rule check
12.5   Runtime Validator      GOVERNANCE            Checksum + lineage
12.6   Governance Auditor     GOVERNANCE            Timeline + rollback
12.7   Proposal Engine        GOVERNANCE            Darwin→WASIT→Human
12.8   Rollback Manager       GOVERNANCE            Config version revert
───    ─────────────────────  ────────────────────  ────────────────────────
13.1   Fund Manager           CONSUMER              Equity/margin/available
13.2   Veto Gate              CONSUMER              Risk checks
13.3   Intent Builder         CONSUMER              Trade intent
13.4   Paper Trader           CONSUMER              Simulated execution
13.5   Live Adapter           CONSUMER              DISABLED default
13.6   CSV Exporter           CONSUMER              Marker export
13.7   API Layer              CONSUMER              Internal query interface
───    ─────────────────────  ────────────────────  ────────────────────────
14.1   Pipeline Audit         AUDIT                 Stage verification
14.2   Snapshot Audit         AUDIT                 10-snapshot verification
14.3   Clone Audit            AUDIT                 3-clone verification
14.4   Trade Audit            AUDIT                 P&L verification
14.5   Knowledge Audit        AUDIT                 Unidirectional check
14.6   Governance Audit       AUDIT                 Decision verification
14.7   Self-Test Suite        AUDIT                 16 automated tests
14.8   Fingerprint Generator  AUDIT                 Deterministic hash
14.9   Geometry Viewer        VIEW                  Candle + ST + cage chart
14.10  Clone Viewer           VIEW                  3 clone cards
14.11  Trade Viewer           VIEW                  History + equity
14.12  Replay Viewer          VIEW                  Scrubber + playback
14.13  Knowledge Viewer       VIEW                  Academy + Oracle
14.14  Panel Renderer         VIEW                  Indicator gauges
14.15  Governance UI          VIEW                  Proposals + rollback
14.16  Simulation UI          VIEW                  Config + results
14.17  Prediction Display     VIEW                  Empirical summary
14.18  Consumer Display       VIEW                  Intent preview
14.19  Audit Display          VIEW                  Test results
14.20  SQLite Viewer          VIEW                  Table browser
14.21  SQLite Manager         VIEW                  Admin operations
14.22  Query Console          VIEW                  SQL execution
14.23  Final Validation       VIEW                  12-domain check
```

---

## 3. WORKER BUILD ORDER

```
ORDER  WORKER                DEPENDS ON            THREAD      LIFECYCLE
─────  ────────────────────  ────────────────────  ──────────  ──────────
W1     Data Worker           S3 (MARKET)           Separate    Cold
W2     Knowledge Worker      S9 (KNOWLEDGE)        Separate    Cold
W3     Benchmark Worker      S10 (BENCHMARK)       Separate    Cold
W4     Replay Worker         S8 (REPLAY)           Separate    Cold
W5     Query Worker          SQLite Viewer         Separate    Cold
W6     Import Worker         SQLite Viewer         Separate    Cold
W7     Export Worker         SQLite Viewer         Separate    Cold
W8     Backup Worker         SQLite Manager        Separate    Cold
W9     Integrity Worker      SQLite Manager        Separate    Cold

WORKER BUILD RULES:
  - Each worker built after its dependency layer is complete
  - Worker tested with postMessage protocol before integration
  - Worker fallback: sequential execution if Worker API unavailable
  - Worker timeout: 120s (query), 300s (import/export/backup)
```

---

## 4. TESTING ORDER

```
ORDER  TEST TYPE            AFTER BUILDING         TESTS
─────  ───────────────────  ─────────────────────  ─────────────────────────
T1     Unit Tests           Each S1 component      Individual function tests
T2     Integration Tests    Each layer (S3–S14)    Cross-component data flow
T3     Pipeline Tests       S7 complete            22-stage sequence
T4     Determinism Tests    S1 and all subsequent  2-run checksum identity
T5     Constitution Tests   Each build phase       18-law compliance
T6     Self-Tests           S14 complete           16 automated AUDIT tests
T7     Regression Tests     After each fix          All previous tests
T8     Performance Tests    After each layer       RAM/CPU within limits
T9     Worker Tests         After each worker      postMessage protocol
T10    SQLite Tests         After SQLite Viewer    CRUD, search, export
T11    Final Validation     S15                    12-domain check

TEST GATES:
  - Unit: HARD (must pass before next component)
  - Integration: HARD (must pass before next layer)
  - Pipeline: HARD (must pass before S8)
  - Determinism: HARD (must pass at every stage)
  - Constitution: HARD (must pass at every phase)
  - Performance: SOFT (record; governor degrades if fail)
```

---

## 5. INTEGRATION ORDER

```
ORDER  INTEGRATION POINT          COMPONENTS              VERIFICATION
─────  ─────────────────────────  ──────────────────────  ──────────────────
I1     MARKET → TRUTH             market_snapshot →       Card sharing check
                                  truth_snapshot
I2     TRUTH → STRUCTURE          truth_snapshot →        Geometry sourcing
                                  structure_snapshot
I3     TRUTH + STRUCTURE →        truth + structure →     3-bus separation
      EVIDENCE                    evidence_snapshot
I4     SHARED → CLONE (×3)        All 3 snapshots →       Card sharing check
                                  clone_observations
I5     CLONE → TRADE              clone_obs →             Entry/exit flow
                                  trade_markers
I6     TRADE → POSITION           trade_markers →         Position lifecycle
                                  position_state
I7     TRADE → STATISTICS         trade_markers →         Sample gate check
                                  statistics_snapshot
I8     STATISTICS → KNOWLEDGE     stats → academy,        Unidirectional check
                                  oracle, hivemind
I9     KNOWLEDGE → PREDICTION     knowledge →             No-model check
                                  prediction_snapshot
I10    KNOWLEDGE → GOVERNANCE     knowledge →             Bounded loop only
                                  config_version
I11    GOVERNANCE → CONSUMER      config_version →        Live-adapter off
                                  trade intent
I12    ALL → AUDIT                All domains             Card lineage check
I13    ALL → VIEW                 All cards               No-mock check
I14    ALL → FINAL VALIDATION     All domains             12 checks
I15    SQLite → ALL               SQLite tables           FK integrity

INTEGRATION RULES:
  - Each integration point verified before next begins
  - Card sharing: Truth/Structure/Evidence 1× → shared to 3 clones
  - Unidirectional: No backward data flow detected
  - Worker bridge: Workers send via postMessage; main persists
```

---

## 6. BENCHMARK ORDER

```
ORDER  BENCHMARK              CONFIG                  VERIFICATION
─────  ─────────────────────  ──────────────────────  ──────────────────────
B1     WASIT Identical        Same config             G2 must FAIL
B2     WASIT Tighten Entry    Reduce ENTRY_OFFSET     G1–G5 evaluation
B3     WASIT Tighten Wrong    Reduce WRONG_ENTRY_PCT  G1–G5 evaluation
B4     WASIT Widen Corridor   Increase ENTRY_OFFSET   G1–G5 evaluation
B5     WASIT Loose Cage       Increase CAGE_TIGHT     G1–G5 evaluation
B6     WASIT Tight Cage       Decrease CAGE_TIGHT     G1–G5 evaluation
B7     Clone Benchmark        Per-clone isolation     Clone stats compare
B8     Trade Benchmark        All markers             P&L verification
B9     Market Benchmark       Market stats            Phase distribution

BENCHMARK RULES:
  - Each benchmark runs in parallel worker (fallback: sequential)
  - 5-gate evaluation with majority voting
  - Verdict: PASS (all 5 gates pass) / FAIL (any gate fails)
  - Identical config must fail G2 (expectancy not improved)
```

---

## 7. AUDIT ORDER

```
ORDER  AUDIT DOMAIN          CHECKS                    GATE
─────  ────────────────────  ────────────────────────  ────────────────────
A1     Pipeline Audit        22 stages, card sharing    HARD
A2     Snapshot Audit        10 snapshots, W/OD         HARD
A3     Clone Audit           3 clones, 3 obs/candle     HARD
A4     Trade Audit           P&L, after-fee, adverse    HARD
A5     Knowledge Audit       Unidirectional, no-ML      HARD
A6     Governance Audit      Timeline, rollback         HARD
A7     SQLite Audit          40 tables, 49 FK           HARD
A8     Worker Audit          postMessage, no-direct-DB  HARD
A9     Integration Audit     All integration points     HARD
A10    Final Audit           15 stop-rule PASS          HARD

AUDIT RULES:
  - Each audit domain must PASS before build continues
  - Audit failures = BUILD STOP
  - Audit results logged to audit_logs
  - Every card must have checksum + lineage
```

---

## 8. RECOMMENDED BUILD SEQUENCE

```
┌──────────────────────────────────────────────────────────────────────────┐
│                     RECOMMENDED BUILD SEQUENCE                            │
│                     (respects all dependencies)                           │
└──────────────────────────────────────────────────────────────────────────┘

PHASE 0: FOUNDATION (SPECIFICATION ONLY — NO CODE)
  ├── SPECIFICATION_FREEZE.md
  ├── DEPENDENCY_FREEZE.md
  ├── ARCHITECTURE_FREEZE.md
  ├── SQLITE_FOUNDATION_FREEZE.md
  ├── TRADING_SCHEMA_FREEZE.md
  ├── TRUTH_LAYER_FREEZE.md
  ├── DECISION_TREE_FREEZE.md
  ├── BUILD_CONTRACT.md
  └── IMPLEMENTATION_CONTRACT.md

PHASE 1: BEDROCK (S1)
  ├── Decimal, int-tick, canonical string
  ├── ID generator (deterministic)
  ├── WIB clock
  ├── SHA-256 hash
  ├── PRNG Mulberry32
  ├── Card factory (Object.freeze + checksum + lineage)
  ├── Validator, Bus factory
  ├── Bounded registry (CONFIG)
  ├── Governor
  └── IndexedDB writer (serial, main thread)

PHASE 2: BOOT + WORKSPACE (S2)
  ├── BOOT initialization
  ├── Workspace manager (tiered storage)
  ├── Checkpoint manager
  └── Config loader

PHASE 3: MARKET (S3)
  ├── Data Worker
  ├── Hygiene validator
  ├── Gap detector
  ├── OI proxy generator
  └── Market snapshot engine

PHASE 4: TRUTH (S4)
  ├── Point Builder (all indicators)
  ├── Supertrend with flip detection
  ├── ATR, EMA, MACD, RSI, W%R
  └── Truth snapshot

PHASE 5: STRUCTURE (S5)
  ├── Line Builder
  ├── Slope Builder
  ├── Wave Builder (13 structures)
  ├── Cage Engine (with versioning)
  ├── Ladder, Nearest, Phase, Distance
  └── Structure snapshot

PHASE 6: EVIDENCE (S6)
  ├── Direction Bus
  ├── Exit Bus
  ├── Correction Bus
  ├── OI Inheritor, MTF Sector
  ├── Max Score, ST-Dist-Vol
  └── Evidence snapshot

PHASE 7: CLONE + TRADE + POSITION + GRID (S7)
  ├── Clone Orchestrator
  ├── LONG Clone (observe + entry + exit)
  ├── SHORT Clone (mirror)
  ├── GRID Clone (cage-only)
  ├── Entry Corridor
  ├── Entry Marker, Exit Marker
  ├── Position Manager, MAE/MFE Tracker
  ├── Profit Lock, Trailing Stop, Breakeven
  └── Wrong Entry Guard

PHASE 8: SIM + REPLAY (S8)
  ├── Simulation Engine
  ├── 4 simulation types
  ├── 6 replay types
  └── Determinism Verifier

PHASE 9: STATISTICS + KNOWLEDGE (S9)
  ├── Trade Statistics, Market Statistics
  ├── Sample Gate
  ├── River (chronicle)
  ├── Academy (4-dim bucket)
  ├── Oracle (euclidean similarity)
  ├── HiveMind (understanding)
  ├── CERMIN (calibration)
  ├── Librarian (lifecycle)
  ├── Darwin (proposals)
  └── Knowledge Worker

PHASE 10: BENCHMARK (S10)
  ├── WASIT 5-Gate
  ├── WASIT Parallel
  ├── Walk-Forward Engine
  └── Benchmark Worker

PHASE 11: PREDICTION (S11)
  ├── Empirical Aggregator
  ├── Similarity Aggregator
  ├── Intelligence Aggregator
  ├── Calibration Aggregator
  └── Prediction Snapshot

PHASE 12: GOVERNANCE (S12)
  ├── 6 validators
  ├── Proposal Engine
  ├── Rollback Manager
  └── Governance Worker

PHASE 13: CONSUMER (S13)
  ├── Fund Manager
  ├── Veto Gate
  ├── Intent Builder
  ├── Paper Trader
  ├── Live Adapter (DISABLED)
  ├── CSV Exporter
  └── API Layer

PHASE 14: AUDIT + VISUALIZATION + SQLite TOOLS (S14)
  ├── 6 audit domains
  ├── Self-Test Suite
  ├── Fingerprint Generator
  ├── 12 visualization components
  ├── SQLite Viewer
  ├── SQLite Manager
  ├── Query Console
  └── Final Validation (S15)
```

---

## 9. COMPONENT DEPENDENCY SEQUENCE

```
S1: Bedrock
 │
 ├─▶ S2: BOOT + Workspace + Checkpoint + Config
 │     │
 │     ├─▶ S3: MARKET
 │     │     │
 │     │     └─▶ S4: TRUTH
 │     │           │
 │     │           ├─▶ S5: STRUCTURE
 │     │           │     │
 │     │           │     └─▶ S7: CLONE (reads STRUCTURE)
 │     │           │
 │     │           └─▶ S6: EVIDENCE
 │     │                 │
 │     │                 └─▶ S7: CLONE (reads EVIDENCE)
 │     │
 │     └─▶ S7: CLONE + TRADE + POSITION + GRID
 │           │
 │           ├─▶ S8: SIM + REPLAY
 │           │     │
 │           │     └─▶ S15: FINAL VALIDATION
 │           │
 │           └─▶ S9: STATISTICS + KNOWLEDGE
 │                 │
 │                 ├─▶ S10: BENCHMARK
 │                 │
 │                 ├─▶ S11: PREDICTION
 │                 │     │
 │                 │     └─▶ S13: CONSUMER
 │                 │
 │                 └─▶ S12: GOVERNANCE
 │                       │
 │                       └─▶ S13: CONSUMER
 │
 └─▶ S14: AUDIT + VIEW + SQLite TOOLS (reads all)
       │
       └─▶ S15: FINAL VALIDATION
```

---

## 10. WORKER DEPENDENCY SEQUENCE

```
S3: MARKET
 │
 └─▶ W1: Data Worker
       (batch bootstrap, TF aggregation, gap-repair)

S9: KNOWLEDGE
 │
 └─▶ W2: Knowledge Worker
       (Academy batch, Oracle similarity, Darwin, Librarian)

S10: BENCHMARK
 │
 └─▶ W3: Benchmark Worker
       (WASIT walk-forward parallel)

S8: REPLAY
 │
 └─▶ W4: Replay Worker
       (replay per symbol parallel)

S14: SQLite TOOLS
 │
 ├─▶ W5: Query Worker (long-running SELECT)
 ├─▶ W6: Import Worker (CSV/JSON parse)
 ├─▶ W7: Export Worker (file format)
 ├─▶ W8: Backup Worker (VACUUM INTO)
 └─▶ W9: Integrity Worker (PRAGMA checks)
```

---

## 11. INTEGRATION SEQUENCE

```
I1:  MARKET → TRUTH            (after S4)
I2:  TRUTH → STRUCTURE          (after S5)
I3:  TRUTH + STRUCTURE → EVIDENCE (after S6)
I4:  SHARED → CLONE (×3)       (after S7)
I5:  CLONE → TRADE              (after S7)
I6:  TRADE → POSITION           (after S7)
I7:  TRADE → STATISTICS         (after S9)
I8:  STATISTICS → KNOWLEDGE     (after S9)
I9:  KNOWLEDGE → PREDICTION     (after S11)
I10: KNOWLEDGE → GOVERNANCE     (after S12)
I11: GOVERNANCE → CONSUMER      (after S13)
I12: ALL → AUDIT                (after S14)
I13: ALL → VIEW                 (after S14)
I14: ALL → FINAL VALIDATION     (after S15)
I15: SQLite → ALL               (throughout)
```

---

## IMPLEMENTATION CONTRACT STATUS: LOCKED

This IMPLEMENTATION CONTRACT defines the complete build sequence for ST-LMS v3. Every component, worker, test, integration point, benchmark, and audit has a defined position in the build order. No component may be built before its dependencies. No step may be skipped. No code may be generated until PHASE 1 implementation begins, and only after all PHASE 0 specification documents are complete and frozen.
