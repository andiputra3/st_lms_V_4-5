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
