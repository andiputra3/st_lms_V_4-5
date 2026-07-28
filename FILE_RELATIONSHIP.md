# FILE_RELATIONSHIP.md

## ST-LMS v3 — File Relationship & Dependency Map

**Date:** 2026-07-28
**Phase:** PHASE 0 — Prompt 01
**Purpose:** Explain relationships between all 5 reference files

---

## 1. HIERARCHY OVERVIEW

```
                         MASTER_SPECIFICATION.html
                         (APEX — Highest Authority)
                                   │
                                   │ defines WHAT is frozen:
                                   │ 18 laws, 16 constitutions,
                                   │ indicator matrix, 10 snapshots,
                                   │ 15 build-stop rules
                                   │
                                   ▼
                         DOCUMENT_DEPENDENCY.html
                         (Build Graph — Order Authority)
                                   │
                                   │ defines ORDER & DEPENDENCIES:
                                   │ reading order, build phases,
                                   │ validation gates, dependency graphs
                                   │
                                   ▼
                         QWEN_14_DOC.html
                         (Implementation Docs — Doc01–14)
                                   │
                                   │ expands into 14 detailed documents:
                                   │ inventory, constitution, target,
                                   │ workspace, runtime, pipeline,
                                   │ snapshot, knowledge, simulation,
                                   │ replay, governance, blueprint,
                                   │ implementation plan, approval
                                   │
                                   ▼
                         ST_LMS_CORE.js
                         (Implementation — Subordinate)
                                   │
                                   │ partial implementation:
                                   │ 26 namespaces, 842 lines,
                                   │ monolithic single file
                                   │
                                   ▼
                         01-07_IMPLEMENTATION_AUDIT.md
                         (Verification — Subordinate)
                                   │
                                   │ audits implementation vs spec:
                                   │ 7-part report, 6 bugs fixed,
                                   │ 21 remaining issues
```

---

## 2. AUTHORITY CHAIN

```
Level 0: MASTER_SPECIFICATION.html
  │
  │  Role: Defines WHAT the system IS and WHAT rules govern it
  │  Scope: 14 sections (§0–§14)
  │  Authority: On content conflict, THIS document wins over ALL others
  │  Key contents:
  │    - §0: Apex & Authority Declaration
  │    - §1: System Identity (what ST-LMS IS and IS NOT)
  │    - §2: 18 Master Implementation Laws (LAW-MASTER-01..18)
  │    - §3: Constitution Freeze Matrix (16 frozen constitutions)
  │    - §4: Market Geometry Master (11 geometry entities)
  │    - §5: Indicator Authority Matrix (29 indicators × 7 columns)
  │    - §6: Master Trading Lifecycle (22 pipeline stages)
  │    - §7: Clone Master (LONG/SHORT/GRID rules)
  │    - §8: Knowledge Master (6 knowledge entities)
  │    - §9: Snapshot Master (10 snapshots W/OD)
  │    - §10: Prediction Master (empirical, no-model)
  │    - §11: Governance Master (3-rem, 6 validations)
  │    - §12: Build Stop Master (15 stop conditions)
  │    - §13: Implementation Checklist
  │    - §14: Readiness Self-Audit
  │
  ├──▶ DOCUMENT_DEPENDENCY.html
  │     │
  │     │  Role: Defines ORDER in which to read, build, validate
  │     │  Scope: 13 sections (§0–§12)
  │     │  Authority: On ordering conflict, THIS document wins
  │     │  Key contents:
  │     │    - §0: Document Identity
  │     │    - §1: Reading Order (16 documents)
  │     │    - §2: Document Dependency Graph (SVG interactive)
  │     │    - §3: Feature Dependency Graph (14 domains)
  │     │    - §4: Pipeline Dependency Graph (11 stages)
  │     │    - §5: Clone Dependency Graph (LONG/SHORT/GRID)
  │     │    - §6: Knowledge Dependency Graph (6 entities)
  │     │    - §7: Snapshot Dependency Graph (10 snapshots)
  │     │    - §8: Implementation Order (F1–F14)
  │     │    - §9: Build Graph (PHASE 0–12)
  │     │    - §10: Validation Order (13 gates)
  │     │    - §11: Build Stop Rule (8 conditions)
  │     │    - §12: Readiness Graph (5 dimensions)
  │     │
  │     └──▶ QWEN_14_DOC.html
  │           │
  │           │  Role: Expands into 14 detailed implementation documents
  │           │  Scope: 14 phases (PHASE 0–13)
  │           │  Authority: Implementation specification authority
  │           │  Key contents:
  │           │    - PHASE 0 (Doc01): Feature Inventory Audit (19 domains, 82 components)
  │           │    - PHASE 1 (Doc02): Implementation Constitution (15 laws)
  │           │    - PHASE 2 (Doc03): Program Target & Benchmark (12 targets)
  │           │    - PHASE 3 (Doc04): Workspace Architecture (tiered storage)
  │           │    - PHASE 4 (Doc05): Runtime Architecture (thread topology)
  │           │    - PHASE 5 (Doc06): Pipeline Architecture (22 stages)
  │           │    - PHASE 6 (Doc07): Market Snapshot Architecture (10 snapshots)
  │           │    - PHASE 7 (Doc08): Knowledge Architecture (6 entities)
  │           │    - PHASE 8 (Doc09): Simulation Architecture (4 types, 5 laws)
  │           │    - PHASE 9 (Doc10): Replay Architecture (6 types)
  │           │    - PHASE 10 (Doc11): Governance Architecture (6 validations)
  │           │    - PHASE 11 (Doc12): HTML OS Blueprint (module→thread→store)
  │           │    - PHASE 12 (Doc13): Implementation Plan (S1–S15)
  │           │    - PHASE 13 (Doc14): Build Approval Report (15/15 PASS)
  │           │
  │           └──▶ ST_LMS_CORE.js
  │                 │
  │                 │  Role: Partial implementation of the specification
  │                 │  Scope: 842 lines, 26 namespaces
  │                 │  Authority: Subordinate to all specification documents
  │                 │  Key contents:
  │                 │    - CORE (math utils, asset registry, PRNG)
  │                 │    - CRYPTO (SHA-256)
  │                 │    - ID (deterministic ID generation)
  │                 │    - CONFIG (bounded parameter registry)
  │                 │    - CARD (immutable card creation)
  │                 │    - WORKSPACE (IndexedDB + memory store)
  │                 │    - MARKET (fixture generator, hygiene, gaps, OI proxy)
  │                 │    - TRUTH (PointBuilder: all indicators)
  │                 │    - STRUCTURE (LineBuilder, SlopeBuilder, WaveBuilder, CageEngine)
  │                 │    - EVIDENCE (dirBus, exitBus, correctionBus, OI, MTF)
  │                 │    - FEE (murni, required, layered)
  │                 │    - TRADE (mkEntry, mkExit)
  │                 │    - POSITION (update MAE/MFE)
  │                 │    - CLONE_SHARED (corridor, decideClose, dirObserve, gridObserve)
  │                 │    - LONG_CLONE, SHORT_CLONE, GRID_CLONE
  │                 │    - STATISTICS (tradeStats)
  │                 │    - KNOWLEDGE (Academy, Oracle, HiveMind, CERMIN, Librarian, Darwin)
  │                 │    - SIMULATION (freshState, process, computeAll, determinismHash)
  │                 │    - BENCHMARK (wasit, wasitParallel, walkForward)
  │                 │    - REPLAY (6 types)
  │                 │    - GOVERNANCE (validations, decide, rollback)
  │                 │    - PREDICTION (summarize)
  │                 │    - CONSUMER (fundEval, vetoGate, intentBuilder, exportCSV)
  │                 │    - AUDIT (run, domains, fingerprint)
  │                 │    - FINAL_VALIDATION (runAll)
  │                 │    - VIEW (geometry chart, panels, replay, simulation)
  │                 │
  │                 └──▶ 01-07_IMPLEMENTATION_AUDIT.md
  │                       │
  │                       │  Role: Verify implementation against specification
  │                       │  Scope: 1087 lines, 7-part report
  │                       │  Authority: Subordinate to all specification documents
  │                       │  Key contents:
  │                       │    - 01: Root Cause Analysis (6 bugs found)
  │                       │    - 02: Implementation Plan (fix order)
  │                       │    - 03: Code Patch (exact diffs)
  │                       │    - 04: Validation Report (syntax + correctness)
  │                       │    - 05: Regression Report (20 domains checked)
  │                       │    - 06: Specification Compliance (18/18 laws)
  │                       │    - 07: Final Audit (100% compliance post-fix)
```

---

## 3. DEPENDENCY CHAIN

### 3.1 Reading Dependency (from DOCUMENT_DEPENDENCY §1)

```
MASTER_SPECIFICATION.html          (prerequisite: none — apex)
  │
  ├── DOCUMENT_DEPENDENCY.html     (prerequisite: MASTER)
  │
  ├── Doc01: Feature Inventory     (prerequisite: MASTER)
  ├── Doc02: Implementation Const. (prerequisite: MASTER, Doc01)
  ├── Doc03: Program Target        (prerequisite: Doc02)
  ├── Doc04: Workspace             (prerequisite: Doc02)
  ├── Doc05: Runtime               (prerequisite: Doc04)
  ├── Doc06: Pipeline              (prerequisite: Doc02, MASTER §6)
  ├── Doc07: Snapshot              (prerequisite: Doc06, MASTER §9)
  ├── Doc08: Knowledge             (prerequisite: Doc07)
  ├── Doc09: Simulation            (prerequisite: Doc06, Doc07)
  ├── Doc10: Replay                (prerequisite: Doc07, Doc09)
  ├── Doc11: Governance            (prerequisite: MASTER §11)
  ├── Doc12: Blueprint             (prerequisite: Doc04–11)
  ├── Doc13: Implementation Plan   (prerequisite: Doc01–12)
  └── Doc14: Build Approval        (prerequisite: Doc01–13)
```

**Note:** Docs 01–14 are consolidated into QWEN_14_DOC.html as PHASE 0–13.

### 3.2 Feature Dependency (from DOCUMENT_DEPENDENCY §3)

```
BOOT
  └──▶ MARKET ──▶ TRUTH ──▶ STRUCTURE ──▶ CLONE ──▶ TRADE ──▶ STATISTICS
                     │            │             │
                     │            │             └──▶ GRID ──▶ STATISTICS
                     │            │
                     │            └──▶ EVIDENCE ──▶ CLONE
                     │                               │
                     │                               └──▶ HIVEMIND
                     │
                     └──▶ EVIDENCE

STATISTICS ──▶ KNOWLEDGE ──▶ PREDICTION ──▶ CONSUMER
                  │
                  └──▶ GOVERNANCE (loop only to BOUNDED params)
```

### 3.3 Pipeline Dependency (from DOCUMENT_DEPENDENCY §4)

```
SHARED (1×):
  BOOT → MARKET → TRUTH → STRUCTURE → EVIDENCE

PER-CLONE (3×):
  CLONE_OBSERVATION → ENTRY_VALIDATION → POSITION → PROFIT → EXIT → CLOSE → MARKER

SHARED-AGAIN (1×):
  STATISTICS → KNOWLEDGE → PREDICTION → GOVERNANCE

ON-DEMAND:
  BENCHMARK

OPTIONAL:
  CONSUMER
```

### 3.4 Knowledge Dependency (from DOCUMENT_DEPENDENCY §6)

```
River (continuously records all cards)
  │
  └──▶ Academy (marker + snapshot join)
         │
         ├──▶ Oracle (vector now + historical) — parallel to Academy
         │      │
         │      └──▶ HiveMind (artifacts + oracle + evidence_snapshot)
         │
         ├──▶ Darwin (artifacts + bounded + PEX)
         │
         └──▶ Librarian (artifacts)

Canonical chain: River → Academy → (Oracle ∥) → HiveMind → Darwin → Librarian → Chronicle
```

---

## 4. IMPLEMENTATION CHAIN

### 4.1 Specification → Implementation Mapping

| Specification Source | Implemented In | Coverage |
|---------------------|----------------|----------|
| MASTER §1 (Identity) | ST_LMS_CORE: header comment | Implicit |
| MASTER §2 (18 Laws) | ST_LMS_CORE: all namespaces | 100% (post-fix) |
| MASTER §3 (Freeze Matrix) | ST_LMS_CORE: all domains | 100% |
| MASTER §4 (Geometry) | ST_LMS_CORE: TRUTH, STRUCTURE | 100% |
| MASTER §5 (Indicator Matrix) | ST_LMS_CORE: EVIDENCE | 100% |
| MASTER §6 (Lifecycle) | ST_LMS_CORE: SIMULATION.process | 100% |
| MASTER §7 (Clone) | ST_LMS_CORE: CLONE_SHARED, *_CLONE | 100% |
| MASTER §8 (Knowledge) | ST_LMS_CORE: KNOWLEDGE | 100% |
| MASTER §9 (Snapshot) | ST_LMS_CORE: process() snap object | 100% |
| MASTER §10 (Prediction) | ST_LMS_CORE: PREDICTION | 100% |
| MASTER §11 (Governance) | ST_LMS_CORE: GOVERNANCE | 100% |
| MASTER §12 (Build Stop) | ST_LMS_CORE: AUDIT | Implicit |
| QWEN_DOC D3 (Workspace) | ST_LMS_CORE: WORKSPACE | Partial |
| QWEN_DOC D4 (Runtime) | ST_LMS_CORE: (single thread) | Partial |
| QWEN_DOC D8 (Simulation) | ST_LMS_CORE: SIMULATION | 95% |
| QWEN_DOC D9 (Replay) | ST_LMS_CORE: REPLAY | 100% |
| QWEN_DOC D11 (Consumer) | ST_LMS_CORE: CONSUMER | 85% |

### 4.2 Build Phases (from DOCUMENT_DEPENDENCY §8–9)

```
PHASE 0: Architecture Audit
PHASE 1: Feature Validation
PHASE 2: Implementation Validation
PHASE 3: Architecture Validation
PHASE 4: Pipeline Validation
PHASE 5: Knowledge Validation
PHASE 6: Simulation Validation
PHASE 7: Replay Validation
PHASE 8: Governance Validation
PHASE 9: Blueprint Validation
PHASE 10: Implementation Plan Validation
PHASE 11: Build Approval
PHASE 12: Native HTML Implementation (F1–F14)
```

### 4.3 Implementation Steps (from QWEN_DOC §D12)

```
S1:  Bedrock (decimal, id, wib, hash, prng, card, validator, bus, bounded, governor, store)
S2:  BOOT + Workspace + Checkpoint + Config
S3:  MARKET (data.worker, hygiene, derived, cascade, gap)
S4:  TRUTH (point→line→slope→wave→versioning→validation→flip)
S5:  STRUCTURE (cage+wall+ladder+nearest+cluster)
S6:  EVIDENCE (3-bus+oi+voldelta+mtf+maxscore)
S7:  CLONE + TRADE + POSITION + GRID (3 ledger, orchestrator, grid_eval)
S8:  SIM + REPLAY (6 replay)
S9:  STATISTICS + KNOWLEDGE (river→academy→oracle→hivemind→darwin→librarian→cermin)
S10: BENCHMARK (wasit worker paralel)
S11: PREDICTION (empiris)
S12: GOVERNANCE (6 validasi + workflow + rollback)
S13: CONSUMER (fund/veto/intent/simplugin/liveadapter-off) + API internal
S14: AUDIT + VISUALIZATION (5 viewer)
S15: Runtime/Build/Constitution Validation akhir → BUILD_APPROVAL
```

---

## 5. AUDIT CHAIN

### 5.1 Audit Document Structure

```
01-07_IMPLEMENTATION_AUDIT.md
  │
  ├── 01_ROOT_CAUSE_ANALYSIS.md
  │     └── Identifies 6 bugs in ST_LMS_CORE.js:
  │           C1: mkExit argument order (CRITICAL)
  │           C2: REVERSAL_UP wave typo (CRITICAL)
  │           H1: Date.now() in GOVERNANCE (HIGH)
  │           H2: Academy bucket dimensions (HIGH)
  │           H3: Librarian DEPRECATED status (HIGH)
  │           M:  Correction Bus separation (MEDIUM)
  │
  ├── 02_IMPLEMENTATION_PLAN.md
  │     └── Fix order respecting dependencies:
  │           1. C2 (wave typo)
  │           2. C1 (mkExit args)
  │           3. H1 (Date.now())
  │           4. M  (correction bus)
  │           5. H2 (academy dimensions)
  │           6. H3 (librarian DEPRECATED)
  │
  ├── 03_CODE_PATCH.md
  │     └── Exact diffs for each fix in ST_LMS_CORE.js
  │
  ├── 04_VALIDATION_REPORT.md
  │     └── Syntax + correctness check for each patch
  │
  ├── 05_REGRESSION_REPORT.md
  │     └── 20 domains checked, 0 regressions, 8 improved
  │
  ├── 06_SPECIFICATION_COMPLIANCE.md
  │     └── Before: 78% → After: 100% compliance
  │         - LAW-MASTER: 14/18 → 18/18
  │         - Build Stop: 9/15 → 15/15
  │         - Evidence buses: 2/3 → 3/3
  │         - Academy dims: 2/4 → 4/4
  │         - Librarian statuses: 5/6 → 6/6
  │         - Wave structures: 12/13 → 13/13
  │
  └── 07_FINAL_AUDIT.md
        └── Overall: 91% → 97% coverage
            - 7 bugs fixed (2 CRITICAL, 4 HIGH, 1 MEDIUM)
            - 21 non-critical bugs remain
            - BUILD CAN PROCEED TO NEXT PHASE
```

### 5.2 Audit Verification Flow

```
MASTER_SPECIFICATION (spec)
        │
        │  compared against
        ▼
ST_LMS_CORE.js (implementation)
        │
        │  verified by
        ▼
01-07_IMPLEMENTATION_AUDIT.md
        │
        │  produces
        ▼
    Compliance Report
    (18/18 laws, 15/15 build-stop, 100% determinism)
```

---

## 6. CROSS-REFERENCE MATRIX

| MASTER § | DOCUMENT_DEPENDENCY § | QWEN_DOC Phase | ST_LMS_CORE Namespace | Audit Section |
|----------|----------------------|----------------|----------------------|---------------|
| §0 (Apex) | §0 (Identity) | — | — | — |
| §1 (Identity) | — | PHASE 1 (Doc02) | header comment | 06 (LAW compliance) |
| §2 (18 Laws) | — | PHASE 1 (Doc02) | all namespaces | 06 (18/18) |
| §3 (Freeze) | — | PHASE 0 (Doc01) | all domains | 01, 05 (regression) |
| §4 (Geometry) | — | PHASE 5 (Doc06) | TRUTH, STRUCTURE | 05 (improved) |
| §5 (Indicator) | — | PHASE 5 (Doc06) | EVIDENCE | 06 (authority check) |
| §6 (Lifecycle) | §4 (Pipeline) | PHASE 5 (Doc06) | SIMULATION.process | 02, 05 |
| §7 (Clone) | §5 (Clone) | PHASE 7 (Doc08) | CLONE_SHARED, *_CLONE | 01 (C1), 05 |
| §8 (Knowledge) | §6 (Knowledge) | PHASE 7 (Doc08) | KNOWLEDGE | 01 (H2, H3) |
| §9 (Snapshot) | §7 (Snapshot) | PHASE 6 (Doc07) | process() snap | 01 (M), 04, 06 |
| §10 (Prediction) | — | PHASE 7 (Doc08) | PREDICTION | 06 |
| §11 (Governance) | — | PHASE 10 (Doc11) | GOVERNANCE | 01 (H1), 06 |
| §12 (Build Stop) | §11 (Build Stop) | PHASE 13 (Doc14) | AUDIT | 06 (15/15) |
| §13 (Checklist) | — | PHASE 12 (Doc13) | all namespaces | 07 (97%) |
| §14 (Readiness) | §12 (Readiness) | PHASE 13 (Doc14) | FINAL_VALIDATION | 07 (final) |

---

## 7. FILE SIZE & COMPLEXITY

| File | Lines | Sections | Components Defined | Role |
|------|-------|----------|-------------------|------|
| MASTER_SPECIFICATION.html | 687 | 14 (§0–§14) | 16 constitutions | Constitution |
| DOCUMENT_DEPENDENCY.html | 611 | 13 (§0–§12) | 16 document nodes | Build Graph |
| QWEN_14_DOC.html | 733 | 14 (PHASE 0–13) | 14 documents (Doc01–14) | Specification |
| ST_LMS_CORE.js | 842 | 26 namespaces | 134 implemented components | Implementation |
| 01-07_IMPLEMENTATION_AUDIT.md | 1087 | 7 audit sections | 6 bugs + 21 remaining | Verification |

**TOTAL: 3,960 lines across 5 files**

---

## 8. CONFLICT RESOLUTION RULES

1. **Content conflict**: MASTER_SPECIFICATION > DOCUMENT_DEPENDENCY > QWEN_14_DOC > ST_LMS_CORE
2. **Ordering conflict**: DOCUMENT_DEPENDENCY > MASTER_SPECIFICATION > QWEN_14_DOC > ST_LMS_CORE
3. **Platform binding**: QWEN_14_DOC (Doc02 §1.3) is the authority for platform-specific decisions
4. **Implementation correctness**: 01-07_IMPLEMENTATION_AUDIT.md identifies gaps but does not override specification
5. **Missing specification**: Default to MASTER_SPECIFICATION as source of truth

---

## RELATIONSHIP SUMMARY

```
MASTER_SPECIFICATION  ─── defines WHAT ───▶ all other files
DOCUMENT_DEPENDENCY   ─── defines ORDER ──▶ QWEN_14_DOC → ST_LMS_CORE
QWEN_14_DOC           ─── defines HOW ────▶ ST_LMS_CORE
ST_LMS_CORE           ─── IS the code ────▶ 01-07_IMPLEMENTATION_AUDIT
01-07_AUDIT           ─── VERIFIES code ──▶ against MASTER_SPECIFICATION
```

All 5 files form a closed loop: Specification → Dependency Graph → Detailed Docs → Implementation → Audit → back to Specification.
