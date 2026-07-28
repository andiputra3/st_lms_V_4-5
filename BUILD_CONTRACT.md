# BUILD CONTRACT — ST-LMS v3

## Native HTML Market Geometry Intelligence Operating System

**Date:** 2026-07-28
**Phase:** PHASE 0 — Prompt 03
**Status:** CONSTITUTIONALLY FROZEN
**Sources:** MASTER_SPECIFICATION.html, DOCUMENT_DEPENDENCY.html, QWEN_14_DOC.html, 01-07_IMPLEMENTATION_AUDIT.md

---

## 1. BUILD ORDER

### 1.1 Implementation Phases (F1–F14)

```
PHASE   LAYER                   COMPONENTS
─────   ──────────────────────  ──────────────────────────────────────────
F1      BEDROCK                 decimal/int-tick/canonical, id, wib, hash,
                                prng, lifecycle, card, validator, bus,
                                bounded, governor, IndexedDB writer-serial
F2      BOOT + WORKSPACE        BOOT, workspace, checkpoint, config
F3      MARKET                  data.worker, hygiene, derived, cascade, gap
F4      TRUTH                   point→line→slope→wave→versioning→validation→flip
F5      STRUCTURE               cage+wall+ladder+nearest+cluster
F6      EVIDENCE                3-bus+oi+voldelta+mtf+maxscore
F7      CLONE + TRADE +        3 ledger, orchestrator, grid_eval
        POSITION + GRID
F8      SIM + REPLAY            engine + 6 replay
F9      STATISTICS + KNOWLEDGE  river→academy→oracle→hivemind→darwin→librarian→cermin
F10     BENCHMARK               wasit worker paralel
F11     PREDICTION              empiris
F12     GOVERNANCE              6 validasi + workflow + rollback
F13     CONSUMER                fund/veto/intent/simplugin/liveadapter-off + API
F14     AUDIT + VISUALIZATION   6 audit + 5 viewer
```

### 1.2 Build Steps (S1–S15)

```
STEP   BUILDS                    DEFINITION OF DONE
────   ────────────────────────  ────────────────────────────────────────
S1     Bedrock                   round-trip AKE/SOL/BTC; id deterministik;
                                 verify mendeteksi 1-byte tamper
S2     BOOT+Workspace+Checkpoint resume pasca-close tab; config_version termuat
       +Config
S3     MARKET                    gap ter-anomali; derived=agregasi 1m
S4     TRUTH                     wave no-padding; zero-tolerance; AKE tak patah
S5     STRUCTURE                 HUKUM CAGE; escape v0→v1→v2
S6     EVIDENCE                  OI kosong=INSUFFICIENT; W%R≠entry
S7     CLONE+TRADE+POSITION+GRID 3 obs/candle; GRID marker; adverse-first; HOLD-veto
S8     SIM+REPLAY                replay deterministik; resume checkpoint
S9     STATISTICS+KNOWLEDGE      unidirectional; no-ML; sample-gated
S10    BENCHMARK                 identik→G2 FAIL; 5 gate utuh
S11    PREDICTION                tanpa output model; N/A bila sample kurang
S12    GOVERNANCE                bounded auto-reject; rollback deterministik
S13    CONSUMER                  SIDEWAY→GRID_INTENT; veto tanpa proyeksi
S14    AUDIT + VISUALIZATION     no-mock; export CSV dari card
S15    FINAL VALIDATION          15 stop-rule PASS → BUILD_APPROVAL
```

### 1.3 Build Gate Sequence

```
PHASE 0  → Architecture Audit       (audit all docs vs MASTER)
PHASE 1  → Feature Validation       (all features frozen)
PHASE 2  → Implementation Validation (15 laws + platform-binding)
PHASE 3  → Architecture Validation  (workspace + runtime)
PHASE 4  → Pipeline Validation      (22 stages + Card Sharing)
PHASE 5  → Knowledge Validation     (unidirectional + no-ML)
PHASE 6  → Simulation Validation    (adverse-first + fee)
PHASE 7  → Replay Validation        (6 replay deterministic)
PHASE 8  → Governance Validation    (6 validations + rollback)
PHASE 9  → Blueprint Validation     (module→thread→store)
PHASE 10 → Implementation Plan      (S1–S15 respects dependencies)
PHASE 11 → Build Approval           (15 stop-rule PASS)
PHASE 12 → Native HTML Implementation (F1–F14; each passes HARD gate)
```

---

## 2. BUILD RULES

### 2.1 Core Build Rules

| Rule | Description |
|------|-------------|
| SINGLE BUILDER | Only one build process at a time. No parallel building. |
| SEQUENTIAL STEPS | Each step completes fully before the next begins. |
| GATE BEFORE NEXT | Each build phase must pass its HARD validation gate before proceeding. |
| FOUNDATION FIRST | Bedrock (S1) must be complete before any other step. |
| RESPECT DEPENDENCIES | No building a component before its dependencies are built. |
| TEST AFTER BUILD | Each component tested immediately after building, before next component. |
| NO SKIPPING | Steps must be built in order (S1 → S2 → ... → S15). |

### 2.2 Platform Binding Rules

| Rule | Description |
|------|-------------|
| NATIVE HTML ONLY | No backend, no server, no DB server, no framework |
| INDEXEDDB | Append-only card store. Writer serial on main thread. |
| WEB WORKER | Cold workers (die after completion). No direct IndexedDB access. |
| COMPRESSIONSTREAM | For cold/archive tier storage. |
| BIGINT TICK | Integer-tick per asset for hot representation. |
| CANONICAL STRING | For audit and determinism verification. |
| PRNG MULBERRY32 | Seeded with ts + config_version. |

### 2.3 Determinism Rules

| Rule | Description |
|------|-------------|
| NO DATE.NOW() | Timestamps from candle data only. |
| NO MATH.RANDOM() | Use seeded PRNG (Mulberry32). |
| TIE-BREAK DETERMINISTIC | All tie-breaks must be deterministic. |
| FLOAT BINARY BAN | No float binary in truth representation. |
| 2-RUN IDENTICAL | Same seed + same config → identical checksums. |

### 2.4 No-Fake Data Rules

| Rule | Description |
|------|-------------|
| NULL + STATUS | Missing data = NULL + status string. |
| NO NEUTRAL VALUES | OI empty ≠ 5000; wave<6 ≠ padded. |
| NO MOCK DASHBOARD | Empty panel = N/A, not placeholder. |
| BELUM_CUKUP | Below sample threshold = BELUM_CUKUP, not expressed confidence. |

### 2.5 Immutability Rules

| Rule | Description |
|------|-------------|
| OBJECT.FREEZE | All cards frozen on creation. |
| CHECKSUM | SHA-256 checksum per card. |
| LINEAGE | Update = new card version, never mutation in-place. |
| AUDIT ID | YYYYMMDD_HHMM_KOMP_FILE_SEQ_HEX (WIB). |
| APPEND-ONLY | Store is append-only; no card modification. |

---

## 3. WORKER RULES

### 3.1 Worker Types

| Worker | Purpose | Lifecycle | Thread |
|--------|---------|-----------|--------|
| Data Worker | Batch bootstrap, TF aggregation, gap-repair | Cold (dies after batch) | Separate |
| Knowledge Worker | Academy batch, Oracle similarity, Darwin, Librarian | Cold (dies after completion) | Separate |
| Benchmark Worker | WASIT walk-forward parallel (base vs candidate) | Cold (dies after completion) | Separate |
| Replay Worker | Replay per symbol (parallel across symbols) | Cold (dies after completion) | Separate |
| Main Thread | Truth/Structure/Evidence/Clone sequential | Hot (always running) | Main |

### 3.2 Worker Contracts

| Contract | Description |
|----------|-------------|
| NO DIRECT INDEXEDDB | Workers must NOT open IndexedDB connections. |
| POSTMESSAGE ONLY | Workers send results via postMessage. |
| MAIN PERSISTS | Main thread validates and persists worker results. |
| SERIAL WRITER | Single writer on main thread = zero race conditions. |
| COLD WORKERS | Workers created on demand, terminated after completion. |
| RAM RETURNED | Worker memory freed after termination. |
| NO SETINTERVAL | No idle candle playback loops. |

### 3.3 Thread Safety Rules

| Rule | Description |
|------|-------------|
| TRUTH SEQUENTIAL | Truth/Structure/Evidence/Clone per-candle for one symbol = sequential on main. |
| NO PER-CANDLE PARALLEL | Cannot parallelize per-candle for same symbol (breaks EMA/ATR continuity). |
| SYMBOL PARALLEL | Parallel across different symbols (independent state). |
| BASE VS CANDIDATE | Benchmark: base and candidate can run parallel. |
| BATCH KNOWLEDGE | Knowledge computation can run in worker (batch, not per-candle). |

---

## 4. TESTING RULES

### 4.1 Test Requirements

| Test Type | When | What |
|-----------|------|------|
| Unit Test | After each component built | Individual component correctness |
| Integration Test | After each layer complete | Cross-component data flow |
| Pipeline Test | After each build phase | Stage sequence and card sharing |
| Determinism Test | After S1 and all subsequent | 2-run checksum identity |
| Regression Test | After each fix/change | All previous tests still pass |
| Constitution Test | After each build phase | LAW-MASTER compliance |
| Self-Test | Continuous | AUDIT.run() automated suite |

### 4.2 Test Gates

| Gate | Type | Pass Condition | Fail Consequence |
|------|------|---------------|-----------------|
| Unit | HARD | All unit tests pass | Fix component before continuing |
| Integration | HARD | Data flows correctly | Fix integration before continuing |
| Pipeline | HARD | 22 stages correct | Fix pipeline before continuing |
| Determinism | HARD | 2-run identical checksums | Fix non-determinism before continuing |
| Constitution | HARD | 18 laws compliant | Fix violation before continuing |
| Performance | SOFT | RAM/CPU within limits | Record; governor degrades |

---

## 5. BENCHMARK RULES

### 5.1 WASIT 5-Gate

```
G1: candidate exits ≥ 30
G2: candidate expectancy > base expectancy (majority of folds)
G3: candidate worst-loss not worse > 10% vs base (majority of folds)
G4: candidate win_rate not dropped > 2% vs base (majority of folds)
G5: candidate fee_drag not increased > 0.001 vs base (majority of folds)

VERDICT: PASS if G1 ∧ G2 ∧ G3 ∧ G4 ∧ G5
         FAIL otherwise
```

### 5.2 Benchmark Rules

| Rule | Description |
|------|-------------|
| IDENTICAL → G2 FAIL | Same config as base = rubber-stamp, must fail G2 |
| FOLDS ≥ 3 | Minimum 3 folds for statistical significance |
| PARALLEL WORKER | Base and candidate run in parallel worker |
| FALLBACK SEQUENTIAL | If Worker API unavailable, run sequential (deterministic) |
| MAJORITY VOTE | Per-gate pass requires majority of folds |

---

## 6. AUDIT RULES

### 6.1 Audit Domains

| Domain | Checks |
|--------|--------|
| Pipeline | 22 stages, card sharing, unidirectional |
| Snapshot | 10 snapshots, W/OD fields, NULL+status |
| Clone | 3 clones, 3 obs/candle, sub-ledgers |
| Trade | P&L correctness, after-fee, adverse-first |
| Knowledge | Unidirectional, no-ML, sample-gated |
| Governance | Decision timeline, rollback, deprecated |

### 6.2 Audit Rules

| Rule | Description |
|------|-------------|
| EVERY CARD AUDITABLE | checksum + lineage + dependency per card |
| NO LOGIC WITHOUT CARD | Every decision must produce a card |
| NO DECISION WITHOUT DEPENDENCY | Every card must list its dependencies |
| CHRONICLE | All card events recorded in chronicle |
| 6 AUDIT DOMAINS | Pipeline, Snapshot, Clone, Trade, Knowledge, Governance |

---

## 7. INTEGRATION RULES

### 7.1 Integration Sequence

```
FOUNDATION LAYER:
  S1: Bedrock → S2: BOOT/Workspace/Checkpoint/Config

IMPLEMENTATION LAYER:
  S3: MARKET → S4: TRUTH → S5: STRUCTURE → S6: EVIDENCE
  → S7: CLONE/TRADE/POSITION/GRID → S8: SIM/REPLAY
  → S9: STATISTICS/KNOWLEDGE → S10: BENCHMARK
  → S11: PREDICTION → S12: GOVERNANCE

INTEGRATION LAYER:
  S13: CONSUMER → S14: AUDIT/VISUALIZATION → S15: FINAL VALIDATION
```

### 7.2 Integration Rules

| Rule | Description |
|------|-------------|
| CONTRACT VERIFICATION | Each integration point must verify input/output contracts |
| CARD SHARING VERIFICATION | Truth/Structure/Evidence computed 1×, shared to 3 clones |
| UNIDIRECTIONAL CHECK | No backward data flow detected |
| WORKER BRIDGE CHECK | Workers send via postMessage; main persists |
| CROSS-LAYER AUDIT | Each integration point produces audit log |

---

## 8. CODING RULES

### 8.1 Mandatory Rules

| Rule | Description |
|------|-------------|
| DETERMINISTIC | No Date.now(), no Math.random(), no non-deterministic APIs |
| IMMUTABLE CARDS | Object.freeze + SHA-256 checksum on every fact |
| NULL + STATUS | Missing data = NULL + status, never fake neutral |
| NO REDUCTION | Intelligence not reduced to single score/signal |
| NO MOCK | No placeholder values as truth |
| UNIDIRECTIONAL | Data flows one way; no backward loops |
| CARD SHARING | Truth/Structure/Evidence 1× per candle |
| 1 CANDLE = 3 KNOWLEDGE | 3 observations per candle mandatory |
| SAMPLE GATED | Statistics below threshold = BELUM_CUKUP |
| ADVERSE FIRST | SL beats TP on same candle |
| FEE LAYERED | 0.7% REQUIRED_MOVE; WIN only if net > 0 |
| HUKUM CAGE | 2 walls = compression; 1 wall = trend |
| NATIVE HTML | No backend, no framework, IndexedDB + Worker + CompressionStream |
| SERIAL WRITER | Single writer on main thread; workers via postMessage |
| W%R LIMITED | W%R = exit only; forbidden for entry |
| PREDICTION EMPIRICAL | No forecasting model; empirical + similarity only |
| HUMAN APPROVAL | Darwin proposes, WASIT filters, human decides |
| AUDIT EVERYWHERE | Every domain auditable via card lineage |

### 8.2 Forbidden Rules

| Rule | Description |
|------|-------------|
| NO BACKEND | No server, no database server, no framework |
| NO ML | No machine learning models |
| NO BLACK BOX | Every number has card lineage |
| NO DATE.NOW() | No current time in logic |
| NO MATH.RANDOM() | No random in logic |
| NO FLOAT BINARY | No float in truth representation |
| NO MOCK | No placeholder values as data |
| NO PADDING | No padding wave to 6 lines |
| NO NEUTRAL FAKES | No OI=5000, no dist=0 during warmup |
| NO W%R ENTRY | W%R/MACD/RSI forbidden for entry decisions |
| NO BACKWARD LOOP | No writing from Knowledge/Consumer to Core |
| NO AUTO-EXECUTE | Darwin must not auto-execute proposals |
| NO WORKER WRITE | Workers must not write IndexedDB directly |
| NO SETINTERVAL | No idle candle playback |
| NO REDUCTION | No reducing intelligence to BUY/SELL signal |
| NO MODEL PREDICTION | No forecasting model in prediction |

---

## 9. SPECIFICATION RULES

### 9.1 Specification Hierarchy

```
MASTER_SPECIFICATION.html (APEX — wins on content conflict)
  ↓
DOCUMENT_DEPENDENCY.html (wins on ordering conflict)
  ↓
QWEN_14_DOC.html (Doc01–14)
  ↓
01-07_IMPLEMENTATION_AUDIT.md (verification)
  ↓
STLMS_SQLITE_SCHEMA_V1.sql (data model)
  ↓
ST_LMS_CORE.js (MUST NOT override specification)
```

### 9.2 Specification Rules

| Rule | Description |
|------|-------------|
| MASTER WINS | MASTER_SPECIFICATION always wins on content conflict |
| DEPENDENCY WINS ON ORDER | DOCUMENT_DEPENDENCY wins on build order conflict |
| IMPLEMENTATION SUBORDINATE | ST_LMS_CORE.js must never override specification |
| FROZEN CONSTITUTION | 16 constitutions frozen; amendment = governance Class-B |
| NO SILENT MODIFICATION | Any spec change must go through governance |
| TRACEABILITY | Every implementation decision must reference a specification section |

---

## 10. STOP BUILD RULES

### 10.1 15 Build-Stop Conditions

```
┌────┬──────────────────────────────┬──────────────────────────────────────┐
│ #  │ CONDITION                    │ DETECTION                             │
├────┼──────────────────────────────┼──────────────────────────────────────┤
│ 1  │ Specification conflict       │ Contradiction between docs unresolved│
│ 2  │ Hidden assumption            │ Value without source / NULL+status   │
│ 3  │ Missing feature              │ Constitutional feature not implemented│
│ 4  │ Missing domain               │ Required domain absent from inventory│
│ 5  │ Missing pipeline             │ Lifecycle stage absent / wrong type  │
│ 6  │ Missing authority matrix     │ Indicator used outside valid column  │
│ 7  │ Missing market logic         │ corridor/TP/wrong/grid/cage undefined│
│ 8  │ Governance conflict          │ Loop back to Core / auto-execute     │
│ 9  │ Constitution conflict        │ LAW-MASTER-01..18 violation          │
│ 10 │ Undefined behavior           │ adverse-first/tie-break/escape/no-   │
│    │                              │ trade/HOLD-veto undefined            │
│ 11 │ Undefined snapshot           │ Snapshot/field W-OD undefined        │
│ 12 │ Undefined clone lifecycle    │ lifecycle/3-obs/sub-ledger undefined │
│ 13 │ Undefined knowledge lifecycle│ Librarian/unidirectional undefined   │
│ 14 │ Undefined simulation lifecycle│ 4 types / 5 laws undefined           │
│ 15 │ Undefined implementation     │ native-binding/writer-serial undefined│
│    │ contract                     │                                      │
└────┴──────────────────────────────┴──────────────────────────────────────┘
```

### 10.2 Additional STOP BUILD Rules

```
┌──────────────────────────────────────────────────────────────────┐
│  STOP BUILD IMMEDIATELY IF:                                       │
│                                                                    │
│  - Specification conflict detected (unresolved)                   │
│  - Dependency conflict detected (cycle in forbidden direction)    │
│  - Hidden assumption found (value without source)                 │
│  - Architecture violation (data flow backward to Core)            │
│  - Undefined behavior (missing edge case handling)                │
│  - Undefined component (spec requires, implementation missing)    │
│  - Undefined authority (component acting outside its contract)    │
│  - Pipeline conflict (wrong stage type: SHARED/PER-CLONE)         │
│  - Non-determinism detected (2-run checksums differ)              │
│  - LAW-MASTER violation (any of 18 laws broken)                   │
│  - Authority matrix violation (indicator outside valid column)    │
│  - Mock data found (placeholder as truth value)                   │
│  - Worker writing directly to IndexedDB                           │
│  - Date.now() or Math.random() in logic                           │
│  - W%R/MACD/RSI used for entry decisions                          │
│  - Backward loop from Knowledge/Consumer to Core                  │
│  - Predictive model in prediction layer                           │
│  - Auto-execute governance proposal                               │
│  - Neutral fake values (OI=5000, dist=0 during warmup)            │
│  - Padded wave (wave padded to 6 lines)                           │
└──────────────────────────────────────────────────────────────────┘
```

### 10.3 Tension vs Conflict

```
TENSION (resolved) ≠ BUILD STOP:
  - Placeholder reference → contract field (RESOLVED)
  - Python → browser platform-binding (RESOLVED)
  - Tension that has a documented resolution = recorded as RESOLVED

CONFLICT (unresolved) = BUILD STOP:
  - Open contradiction between specifications
  - Implementation violating specification
  - Missing required component with no resolution plan
```

---

## BUILD CONTRACT STATUS: LOCKED

This BUILD CONTRACT is the governing document for all ST-LMS v3 implementation. Every build step, every worker, every test, every benchmark, every audit, every integration, every line of code, and every specification reference must comply with the rules defined herein. Violation of any STOP BUILD rule requires immediate halt of all build activity until the violation is resolved and documented.
