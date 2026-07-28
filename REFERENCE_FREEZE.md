# REFERENCE_FREEZE.md

## ST-LMS v3 — Full Reference Freeze

**Date:** 2026-07-28
**Phase:** PHASE 0 — Prompt 01
**Purpose:** Freeze all reference documents as-is. No modification, no redesign, no optimization.

---

## 1. TOTAL REFERENCE FILES

| # | File | Type | Lines | Purpose |
|---|------|------|-------|---------|
| 1 | MASTER_SPECIFICATION.html | HTML | 687 | Highest authority constitution document |
| 2 | DOCUMENT_DEPENDENCY.html | HTML | 611 | Build & implementation dependency graph |
| 3 | QWEN_14_DOC.html | HTML | 733 | Implementation constitution reader (Doc01–14) |
| 4 | ST_LMS_CORE.js | JavaScript | 842 | Native HTML OS implementation (monolithic) |
| 5 | 01-07_IMPLEMENTATION_AUDIT.md | Markdown | 1087 | 7-part implementation audit & fix report |

**TOTAL: 5 reference files**

---

## 2. SPECIFICATION HIERARCHY

```
LEVEL 0 (APEX):           MASTER_SPECIFICATION.html
                           - 14 sections (S0–S14)
                           - 18 Master Implementation Laws
                           - 16 frozen constitutions
                           - Indicator authority matrix (7 columns)
                           - 10 snapshots (W/OD)
                           - 15 build-stop rules

LEVEL 1 (DEPENDENCY):     DOCUMENT_DEPENDENCY.html
                           - 13 sections (D0–D12)
                           - Document dependency graph (16 nodes)
                           - Feature dependency graph (14 domains)
                           - Pipeline dependency graph (22 stages)
                           - Clone dependency graph (LONG/SHORT/GRID)
                           - Knowledge dependency graph (6 entities)
                           - Snapshot dependency graph (10 snapshots)
                           - Implementation order (14 phases)
                           - Build graph (PHASE 0–12)
                           - Validation order (13 gates)
                           - Build stop rules (8 conditions)

LEVEL 2 (DOCS 01–14):     QWEN_14_DOC.html
                           - PHASE 0: Feature Inventory Audit (Doc01)
                           - PHASE 1: Implementation Constitution (Doc02)
                           - PHASE 2: Program Target & Benchmark (Doc03)
                           - PHASE 3: Workspace Architecture (Doc04)
                           - PHASE 4: Runtime Architecture (Doc05)
                           - PHASE 5: Pipeline Architecture (Doc06)
                           - PHASE 6: Market Snapshot Architecture (Doc07)
                           - PHASE 7: Knowledge Architecture (Doc08)
                           - PHASE 8: Simulation Architecture (Doc09)
                           - PHASE 9: Replay Architecture (Doc10)
                           - PHASE 10: Governance Architecture (Doc11)
                           - PHASE 11: HTML OS Blueprint (Doc12)
                           - PHASE 12: Implementation Plan (Doc13)
                           - PHASE 13: Build Approval Report (Doc14)

LEVEL 3 (IMPLEMENTATION): ST_LMS_CORE.js
                           - Monolithic JavaScript implementation
                           - 26 namespaces/domains
                           - 842 lines of code
                           - Partial implementation of the specification

LEVEL 4 (AUDIT):          01-07_IMPLEMENTATION_AUDIT.md
                           - 7-part audit document
                           - 01: Root Cause Analysis
                           - 02: Implementation Plan
                           - 03: Code Patch
                           - 04: Validation Report
                           - 05: Regression Report
                           - 06: Specification Compliance
                           - 07: Final Audit
```

---

## 3. SOURCE OF TRUTH HIERARCHY

| Priority | Document | Role |
|----------|----------|------|
| 1 (Highest) | MASTER_SPECIFICATION.html | Defines WHAT is frozen (laws, matrices, snapshots, stop-rules) |
| 2 | DOCUMENT_DEPENDENCY.html | Defines ORDER & DEPENDENCIES of building |
| 3 | QWEN_14_DOC.html | Expands into 14 detailed implementation documents |
| 4 | ST_LMS_CORE.js | Partial implementation (reference for current state) |
| 5 | 01-07_IMPLEMENTATION_AUDIT.md | Audits the implementation against specification |

**Conflict resolution rule:**
- On content conflict: MASTER_SPECIFICATION wins over all others
- On ordering conflict: DOCUMENT_DEPENDENCY wins over all others
- On platform details: QWEN_14_DOC wins (platform binding is explicit there)

---

## 4. AUTHORITY HIERARCHY

```
MASTER_SPECIFICATION.html
  └─ (on content conflict, this document wins)
  │
  ├─▶ DOCUMENT_DEPENDENCY.html
  │   └─ (on ordering conflict, this document wins)
  │   │
  │   └─▶ QWEN_14_DOC.html
  │       │
  │       └─▶ ST_LMS_CORE.js (implementation)
  │           │
  │           └─▶ 01-07_IMPLEMENTATION_AUDIT.md (verification)
```

**Authority chain:**
1. MASTER_SPECIFICATION = Highest authority
2. DOCUMENT_DEPENDENCY = Build graph authority
3. QWEN_14_DOC = Implementation specification authority
4. ST_LMS_CORE = Implementation (subordinate to all above)
5. IMPLEMENTATION_AUDIT = Verification (subordinate to all above)

---

## 5. FROZEN ARCHITECTURE SUMMARY

### 5.1 System Identity
- **ST-LMS** = Native HTML Market Geometry Intelligence Operating System
- **NOT**: Trading bot, AI assistant, market scanner, research tool, dashboard
- **IS**: Laboratory for observation, behavior, simulation, replay, knowledge, governance, prediction-empiris, and audit
- **Core philosophy**: "Trade is Optional, Learning is Mandatory"

### 5.2 Architecture Layers (Data Flow)
```
Data → Truth → Structure → Evidence → Clone → Sim → Knowledge → Consumer
```
- Unidirectional flow (LAW-MASTER-04)
- No backward loops to Core logic
- Only governance can write to BOUNDED parameters

### 5.3 Pipeline Stages (22 total)
- **SHARED** (1x): BOOT → MARKET → TRUTH → STRUCTURE → EVIDENCE
- **PER-CLONE** (3x): Clone Observation → Entry Validation → Position → Profit → Exit → Close → Marker
- **SHARED-AGAIN** (1x): Statistics → Knowledge → Prediction → Governance
- **ON-DEMAND**: Benchmark
- **OPTIONAL**: Consumer

### 5.4 Domains (19 required + visualization)
BOOT, MARKET, TRUTH, STRUCTURE, EVIDENCE, CLONE, TRADE, POSITION, GRID, STATISTICS, KNOWLEDGE, PREDICTION, BENCHMARK, SIMULATION, REPLAY, GOVERNANCE, CONSUMER, AUDIT, VISUALIZATION

### 5.5 Knowledge Entities (6)
Academy, River, Oracle, HiveMind, Darwin, Librarian

### 5.6 Clones (3)
LONG (EXPANSION_UP), SHORT (EXHAUSTION_DOWN), GRID (COMPRESSION_RANGE)

### 5.7 Snapshots (10 per closed candle)
Market, Truth, Structure, Evidence, Clone, Trade, Statistics, Knowledge, Benchmark (on-demand), Prediction

### 5.8 Platform Binding
- SQLite → IndexedDB
- ProcessPool → Web Worker
- File LZMA → CompressionStream + IndexedDB blob
- Float → BigInt integer-tick per-asset + canonical string
- PRNG Mulberry32 → JavaScript-native

### 5.9 Implementation Phases (F1–F14 per DOCUMENT_DEPENDENCY)
F1 Bedrock → F2 Boot/Workspace → F3 Market → F4 Truth → F5 Structure → F6 Evidence → F7 Clone+Trade+Position+Grid → F8 Sim+Replay → F9 Statistics+Knowledge → F10 Benchmark → F11 Prediction → F12 Governance → F13 Consumer → F14 Audit+Vis

---

## 6. FORBIDDEN MODIFICATIONS

The following are **constitutionally forbidden** at this stage:

1. ❌ Redesigning the architecture
2. ❌ Adding new components
3. ❌ Removing existing components
4. ❌ Changing component names
5. ❌ Modifying the data flow direction
6. ❌ Changing indicator authority matrix assignments
7. ❌ Altering snapshot field definitions
8. ❌ Modifying pipeline stage order or type
9. ❌ Changing LAW-MASTER-01 through LAW-MASTER-18
10. ❌ Adding/removing build-stop rules
11. ❌ Changing platform binding decisions
12. ❌ Adding ML/predictive models (forbidden by constitution)
13. ❌ Adding backend/server dependencies
14. ❌ Changing clone lifecycle
15. ❌ Modifying fee calculation rules
16. ❌ Altering the cage logic (HUKUM CAGE)
17. ❌ Changing wave classification (13 structures)
18. ❌ Modifying governance authority matrix

---

## 7. BUILD ASSUMPTIONS

Based on the frozen references:

1. **Native HTML Platform**: Runs entirely in browser; no backend/server/DB-server/framework
2. **Deterministic**: All outputs identical for same inputs + config, anytime, any tab
3. **No-Fake Data**: NULL+status preferred over neutral fake values
4. **Immutable Cards**: Every fact = frozen card + checksum + lineage
5. **Unidirectional Flow**: Data flows one way; no loops back to Core
6. **Card Sharing**: Truth/Structure/Evidence computed 1x/candle, shared to 3 clones
7. **1 Candle = 3 Knowledge**: LONG/SHORT/GRID each write observation per closed candle
8. **No-Reduction**: Intelligence not reduced to single score/signal
9. **W%R Limited**: W%R/Vel/Acc = exit only, forbidden for entry
10. **Fee Layered Honest**: 0.7% REQUIRED_MOVE; WIN only if net > 0; adverse-first
11. **HUKUM CAGE**: 2 valid walls = compression/sideways; 1 wall = trend
12. **Clone = Runtime**: Clones are living entities with ledger/statistics/config
13. **Sample-Gated**: Statistics below threshold do not express confidence
14. **Prediction = Empirical**: Probabilities = conditional frequency + similarity
15. **Human Approval + Bounded**: Darwin proposes, WASIT filters, human decides
16. **Evidence Sterility**: Evidence = independent witness; Truth blind to indicators
17. **Snapshot Complete & Immutable**: 10 snapshots per closed candle
18. **Native-HTML Binding**: Browser native; no backend; writer serial on main thread
19. **Audit Comprehensive**: Every domain auditable

---

## 8. SPECIFICATION CONFLICTS

### 8.1 Resolved Tensions (from QWEN_14_DOC §13.2)

| Tension | Resolution |
|---------|-----------|
| RT-1: Reference HTML contains mock/placeholder values | Adopted as field contract; values from pipeline or N/A |
| RT-2: History uses Python/SQLite/ProcessPool; master requires Native-HTML | Platform binding: IndexedDB/Worker/CompressionStream/BigInt-tick |

### 8.2 Remaining Specification Conflicts

**None detected.** All 5 reference documents are internally consistent at freeze time.

---

## 9. IMPLEMENTATION CONFLICTS

Based on the 01-07_IMPLEMENTATION_AUDIT.md, the following conflicts exist between ST_LMS_CORE.js and the specification:

### 9.1 FIXED (in ST_LMS_CORE.js — audit patches applied)

| ID | Severity | Issue | Status |
|----|----------|-------|--------|
| C1 | CRITICAL | mkExit argument order wrong (garbled P&L) | FIXED |
| C2 | CRITICAL | REVERSAL_UP wave classification typo ("MAERAH" vs "MERAH") | FIXED |
| H1 | HIGH | Date.now() in GOVERNANCE (5 instances) | FIXED |
| H2 | HIGH | Academy bucket only 2 dimensions (needs 4) | FIXED |
| H3 | HIGH | Librarian missing DEPRECATED status (5/6 statuses) | FIXED |
| M | MEDIUM | Correction Bus not separated (only 2/3 buses) | FIXED |

### 9.2 REMAINING (not yet addressed)

| ID | Severity | Issue |
|----|----------|-------|
| M1 | MEDIUM | WARMUP flag only 1 candle |
| M2 | MEDIUM | RSI ~99 instead of 100 |
| M3 | MEDIUM | Hardcoded 60000ms gap detection |
| M4 | MEDIUM | cageHist orphaned state |
| M5 | MEDIUM | rapor not in freshState() |
| M6 | MEDIUM | No chronological candle sort |
| M7 | MEDIUM | Oracle self-prediction feedback |
| M8 | MEDIUM | CERMIN fallback 5000 arbitrary |
| M9 | MEDIUM | DARWIN no .id field |
| M10 | MEDIUM | FEE grid-specific param for all |
| M11 | MEDIUM | WASIT G1 aggregate vs per-fold |
| M12 | MEDIUM | rollback() doesn't clear log |
| M13 | MEDIUM | Constitution gate non-deterministic |
| M14 | MEDIUM | TIME_EXIT always true for losers |
| L1–L7 | LOW | Various cosmetic/minor issues |

---

## 10. MISSING IMPLEMENTATIONS

Based on the audit and comparison between specification and ST_LMS_CORE.js:

### 10.1 Fully Implemented
- BOOT (runtime/config/workspace/checkpoint)
- MARKET (fixture, hygiene, gaps, oiProxy)
- TRUTH (PointBuilder: st, atr, ema, macd, rsi, wpr, vel, acc)
- STRUCTURE (LineBuilder, SlopeBuilder, WaveBuilder, CageEngine, ladder, nearest, phase)
- EVIDENCE (dirBus, exitBus, correctionBus, oiInherit, mtfSector, maxScore, StDistVol)
- CLONE (LONG, SHORT, GRID with shared observation and position management)
- TRADE (mkEntry, mkExit)
- POSITION (update MAE/MFE)
- STATISTICS (tradeStats)
- KNOWLEDGE (Academy, Oracle, HiveMind, CERMIN, Librarian, Darwin)
- PREDICTION (summarize)
- REPLAY (6 types: candle, snapshot, trade, clone, knowledge, governance)
- SIMULATION (freshState, process, computeAll, runActive, determinismHash)
- GOVERNANCE (validations, decide, rollback)
- CONSUMER (fundEval, vetoGate, intentBuilder, previewIntent, exportCSV)
- AUDIT (run, domains, fingerprint)
- BENCHMARK (wasit, wasitParallel, walkForward)
- VIEW (geometry chart, panel renders, equity chart, replay, simulation)
- FINAL_VALIDATION (runAll)

### 10.2 Partially Implemented
- POSITION: 60% per audit (profit lock, trailing stop, breakeven not fully implemented)
- CONSUMER: 85% per audit (live-adapter disabled default but not fully gated)
- SIMULATION: 95% per audit (some edge cases not covered)
- WORKSPACE: Basic implementation (no tiered storage, no archive/eviction)

### 10.3 Not Yet Implemented
- Tiered storage (L1–L5: Hot/Warm/Cold/Archive/Evict)
- Worker-based knowledge computation (Academy batch, Oracle similarity, Darwin, Librarian)
- Worker-based benchmark (WASIT parallel)
- Worker-based replay
- Resource governor (RAM pressure detection)
- Checkpoint system (resume after tab close)
- Live market data feed (fetch/WebSocket)
- Historical data import
- Full governance workflow UI (proposal lifecycle)
- Consumer live-adapter (disabled default per spec)
- Comprehensive audit (6 audit domains)

---

## 11. KNOWN LIMITATIONS

### 11.1 Architectural Limitations
1. **Monolithic file**: ST_LMS_CORE.js is a single 842-line file containing all 26 domains
2. **Fixture-only data**: Only synthetic fixture data; no real market data integration
3. **No tiered storage**: Workspace uses simple array storage, not the specified L1–L5 tiered system
4. **Single symbol**: No multi-symbol parallel processing
5. **No checkpoint/resume**: Cannot resume from tab close
6. **Memory-only workspace**: IndexedDB implementation is basic; no compression

### 11.2 Functional Limitations
1. **WARMUP period**: Only 1 candle warmup (spec implies longer warmup for indicators)
2. **RSI approximation**: RSI calculation gives ~99 instead of 100 at extremes
3. **Hardcoded time gaps**: 60000ms hardcoded for gap detection (not configurable)
4. **Oracle feedback**: Oracle can match against its own recently-pushed vectors
5. **CERMIN fallback**: Arbitrary 5000 confidence fallback
6. **Grid-specific fee param**: GRID_MIN_NET_PCT_OF_FILL used for all clones
7. **No real OI data**: OI is proxied from volume-derived data

### 11.3 Implementation Maturity
- Specification compliance: 97% (post-fix audit)
- Build stop rules: 15/15 PASS (post-fix)
- LAW-MASTER compliance: 18/18 (post-fix)
- Determinism: 100% (post-fix)

---

## FREEZE STATUS: LOCKED

All 5 reference files have been read, understood, and frozen. No modifications are permitted at this stage. This REFERENCE_FREEZE.md serves as the single source of truth for the frozen state of all reference documents.
