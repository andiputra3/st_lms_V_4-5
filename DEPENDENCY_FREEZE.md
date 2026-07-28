# DEPENDENCY_FREEZE.md

## ST-LMS v3 — Comprehensive Dependency Documentation

**Date:** 2026-07-28
**Phase:** PHASE 0
**Authority:** Derived from MASTER_SPECIFICATION.html (APEX), DOCUMENT_DEPENDENCY.html, QWEN_14_DOC.html, stlms_sqlite_schema_v1.sql
**Status:** FROZEN — LOCKED

---

## TABLE OF CONTENTS

1. [DOCUMENT DEPENDENCY](#1-document-dependency)
2. [COMPONENT DEPENDENCY](#2-component-dependency)
3. [PIPELINE DEPENDENCY](#3-pipeline-dependency)
4. [TRADING DEPENDENCY](#4-trading-dependency)
5. [KNOWLEDGE DEPENDENCY](#5-knowledge-dependency)
6. [GOVERNANCE DEPENDENCY](#6-governance-dependency)
7. [SNAPSHOT DEPENDENCY](#7-snapshot-dependency)
8. [SQLITE DEPENDENCY](#8-sqlite-dependency)
9. [VIEW DEPENDENCY](#9-view-dependency)
10. [WORKER DEPENDENCY](#10-worker-dependency)

---

## 1. DOCUMENT DEPENDENCY

### 1.1 Reading Order of 16 Documents

The 16 documents form a strict reading hierarchy. An implementer who has never seen the project MUST read in this order. Jumping = losing conceptual prerequisites.

| # | Document | Provides | Reading Prerequisites |
|---|----------|----------|----------------------|
| 0 | **MASTER_SPECIFICATION.html** | Highest laws, matrices, snapshots, stop-rules | — (apex) |
| 1 | **DOCUMENT_DEPENDENCY.html** | Reading order & build dependencies | MASTER |
| 2 | **Doc01** Feature Inventory Audit | Inventory of 19 domains + 82 components | MASTER |
| 3 | **Doc02** Implementation Constitution | 15 implementation laws + platform-binding | MASTER, Doc01 |
| 4 | **Doc03** Program Target & Benchmark | PASS/FAIL targets | Doc02 |
| 5 | **Doc04** Workspace Architecture | Tiered storage browser | Doc02 |
| 6 | **Doc05** Runtime Architecture | Thread topology | Doc04 |
| 7 | **Doc06** Pipeline Architecture | 22 stages SHARED/PER-CLONE/ON-DEMAND | Doc02, MASTER §6 |
| 8 | **Doc07** Market Snapshot Architecture | 10 snapshots W/OD | Doc06, MASTER §9 |
| 9 | **Doc08** Knowledge Architecture | 6 entities unidirectional | Doc07 |
| 10 | **Doc09** Simulation Architecture | Sim first-class | Doc06, Doc07 |
| 11 | **Doc10** Replay Architecture | 6 replay types | Doc07, Doc09 |
| 12 | **Doc11** Governance Architecture | 6 validations + 3 rem | MASTER §11 |
| 13 | **Doc12** HTML OS Blueprint | Module→thread→store | Doc04–11 |
| 14 | **Doc13** Implementation Plan | Steps S1–S15 | Doc01–12 |
| 15 | **Doc14** Build Approval Report | 15 stop-rule PASS | Doc01–13 |

**Note:** Doc01–14 are consolidated into QWEN_14_DOC.html as PHASE 0–13.

### 1.2 Document Dependency Graph

```
                    ┌──────────────────────┐
                    │  MASTER_SPECIFICATION │  ◄── APEX (highest authority)
                    │  (16 constitutions,   │
                    │   18 laws, matrices)   │
                    └──────┬───────┬───────┘
                           │       │
              ┌────────────┘       └──────────────┐
              ▼                                    ▼
    ┌─────────────────────┐              ┌──────────────────────┐
    │ DOCUMENT_DEPENDENCY  │              │   Doc01 (Inventory)  │
    │ (build graph, order) │              └──────────┬───────────┘
    └──────────┬───────────┘                         │
               │                                     ▼
               │                           ┌──────────────────────┐
               │                           │ Doc02 (Impl. Const.)  │
               │                           └──┬───────┬───────┬───┘
               │                              │       │       │
               │                    ┌─────────┘       │       └─────────┐
               │                    ▼                  ▼                 ▼
               │           ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
               │           │ Doc03 Target │  │ Doc04 Wksp   │  │ Doc06 Pipe   │
               │           └──────────────┘  └──────┬───────┘  └──┬───────┬───┘
               │                                    │              │       │
               │                                    ▼              │       │
               │                           ┌──────────────┐        │       │
               │                           │ Doc05 Runtime│        │       │
               │                           └──────────────┘        │       │
               │                                           ┌───────┘       │
               │                                           ▼               │
               │                                   ┌──────────────┐        │
               │                                   │ Doc07 Snap   │◄───────┘
               │                                   └──┬───────┬───┘
               │                                      │       │
               │                        ┌─────────────┘       └─────────────┐
               │                        ▼                                     ▼
               │               ┌──────────────┐                        ┌──────────────┐
               │               │ Doc08 Know   │                        │ Doc09 Sim    │
               │               └──────┬───────┘                        └──────┬───────┘
               │                      │                                       │
               │                      │                             ┌─────────┘
               │                      │                             ▼
               │                      │                    ┌──────────────┐
               │                      │                    │ Doc10 Replay │
               │                      │                    └──────────────┘
               │                      │
               │         ┌────────────┼────────────┐
               │         ▼            ▼            ▼
               │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
               │  │ Doc11 Gov    │ │ Doc12 Blue   │ │ Doc13 Plan   │
               │  │ (MASTER §11) │ │ (Doc04–11)   │ │ (Doc01–12)   │
               │  └──────────────┘ └──────────────┘ └──────┬───────┘
               │                                            │
               │                                            ▼
               │                                   ┌──────────────┐
               └──────────────────────────────────►│ Doc14 Approv │
                                                   │ (Doc01–13)   │
                                                   └──────────────┘
```

### 1.3 Dependency Classification Per Document

| Document | Upstream (feeds into) | Downstream (feeds from) | Mandatory | Optional | Forbidden |
|----------|----------------------|------------------------|-----------|----------|-----------|
| MASTER_SPEC | all other 15 docs | — (apex) | YES | NO | — |
| DEPENDENCY | Doc01–14 | MASTER | YES | NO | — |
| Doc01 | Doc02 | MASTER | YES | NO | — |
| Doc02 | Doc03, Doc04, Doc06 | MASTER, Doc01 | YES | NO | — |
| Doc03 | — | Doc02 | YES | NO | — |
| Doc04 | Doc05 | Doc02 | YES | NO | — |
| Doc05 | Doc12 (via Doc04–11) | Doc04 | YES | NO | — |
| Doc06 | Doc07, Doc09 | Doc02, MASTER §6 | YES | NO | — |
| Doc07 | Doc08, Doc09, Doc10 | Doc06, MASTER §9 | YES | NO | — |
| Doc08 | Doc12, HiveMind | Doc07 | YES | NO | — |
| Doc09 | Doc10, Doc12 | Doc06, Doc07 | YES | NO | — |
| Doc10 | Doc12 | Doc07, Doc09 | YES | NO | — |
| Doc11 | Doc12 | MASTER §11 | YES | NO | — |
| Doc12 | Doc13 | Doc04–11 | YES | NO | — |
| Doc13 | Doc14 | Doc01–12 | YES | NO | — |
| Doc14 | — (gate) | Doc01–13 | YES | NO | — |

### 1.4 Conflict Resolution Rules

```
Content conflict:    MASTER_SPECIFICATION > DOCUMENT_DEPENDENCY > QWEN_14_DOC > ST_LMS_CORE
Ordering conflict:   DOCUMENT_DEPENDENCY > MASTER_SPECIFICATION > QWEN_14_DOC > ST_LMS_CORE
Platform binding:    QWEN_14_DOC (Doc02 §1.3) is authority for platform-specific decisions
```

---

## 2. COMPONENT DEPENDENCY

### 2.1 Complete Domain Dependency Map (20 Domains)

| # | Domain | Produces | Depends On (Upstream) | Consumed By (Downstream) |
|---|--------|----------|----------------------|--------------------------|
| 1 | **BOOT** | runtime+config+ckpt+registry | — | all domains |
| 2 | **WORKSPACE** | IndexedDB stores, tiered storage, checkpoints | BOOT | MARKET, all persistence |
| 3 | **MARKET** | market_snapshot (OHLCV, hygiene, gaps, OI proxy) | BOOT, WORKSPACE | TRUTH |
| 4 | **TRUTH** | truth_snapshot (st, ATR, EMA, MACD, W%R, RSI, dist, distAtr, vel, acc) | MARKET | STRUCTURE, EVIDENCE |
| 5 | **STRUCTURE** | structure_snapshot (cage, wave, ladder, nearest, pp, dist_ceiling, dist_floor, market_phase, escape_path) | TRUTH | CLONE, GRID, EVIDENCE (ctx) |
| 6 | **EVIDENCE** | evidence_snapshot (3 buses: direction, exit, correction; OI, MTF, max_score) | TRUTH, MARKET, STRUCTURE | CLONE, HIVEMIND |
| 7 | **CLONE** | clone_observation + clone_snapshot (LONG/SHORT/GRID) | STRUCTURE, EVIDENCE, TRUTH | TRADE, STATISTICS |
| 8 | **TRADE** | trade_markers (ENTRY, EXIT, P&L, MAE/MFE) | CLONE, STRUCTURE, EVIDENCE | POSITION, STATISTICS |
| 9 | **POSITION** | position state (MAE/MFE/trail/partial/lock) | TRADE, CLONE | TRADE (exit), STATISTICS |
| 10 | **STATISTICS** | statistics_snapshot (win_rate, expectancy, PF, fee_drag, wrong_rate, sample-gated) | TRADE, POSITION, STRUCTURE | KNOWLEDGE |
| 11 | **KNOWLEDGE** | knowledge_snapshot (Academy, River, Oracle, HiveMind, Darwin, Librarian, CERMIN) | STATISTICS, all snapshots | PREDICTION, GOVERNANCE |
| 12 | **PREDICTION** | prediction_snapshot (empirical win_rate, similarity, calibration_error) | KNOWLEDGE | CONSUMER |
| 13 | **REPLAY** | 6 replay types (candle/snapshot/trade/clone/knowledge/governance) | All snapshots | AUDIT, VISUALIZATION, GOVERNANCE |
| 14 | **SIMULATION** | Simulation engine (historical/live/strategy/clone) | All pipeline | REPLAY, BENCHMARK |
| 15 | **GOVERNANCE** | decisions, config_version, rollback, bounded registry | KNOWLEDGE, BOUNDED params | all domains (param only) |
| 16 | **CONSUMER** | intent/report/trade-intent | PREDICTION, KNOWLEDGE | — (optional terminal) |
| 17 | **AUDIT** | audit_logs, compliance checks, fingerprint | all cards (read-only) | human (via VISUALIZATION) |
| 18 | **BENCHMARK** | benchmark_snapshot (WASIT 5-gate, walk-forward, fold metrics) | SIMULATION | GOVERNANCE |
| 19 | **VISUALIZATION** | UI viewers, panels, charts | all cards (read-only) | human |
| 20 | **FINAL_VALIDATION** | 12-domain validation results, constitution checks | all domains | AUDIT, human |

### 2.2 Complete Data Flow Chain (ASCII)

```
                                 ┌──────────────────────────────────────────────┐
                                 │                  BOOT                         │
                                 │  (config, registry, checkpoint, runtime)      │
                                 └────────────────────┬─────────────────────────┘
                                                      │
                                                      ▼
                                 ┌──────────────────────────────────────────────┐
                                 │                WORKSPACE                       │
                                 │  (IndexedDB: cards, config, checkpoints,       │
                                 │   governance, audit_log, runs)                │
                                 └────────────────────┬─────────────────────────┘
                                                      │
                    ┌─────────────────────────────────┼─────────────────────────────┐
                    │                                 │                              │
                    ▼                                 ▼                              ▼
    ┌───────────────────────────┐     ┌───────────────────────────┐     ┌───────────────────────────┐
    │         MARKET             │     │   open_interest_series    │     │      market_metadata       │
    │  market_snapshot           │     │   (OI proxy / external)   │     │   market_gaps              │
    │  (OHLCV + hygiene + gap)   │     └───────────────────────────┘     └───────────────────────────┘
    └─────────────┬─────────────┘
                  │
                  ▼
    ┌─────────────────────────────────────────────────────────────────────────────────┐
    │                                  TRUTH                                            │
    │  truth_snapshot: st, stDir, color, ATR, EMA12/26, MACD, MACD_signal,             │
    │  MACD_hist, RSI, W%R, W%R_vel, W%R_acc, dist_to_st, distAtr, volume_delta        │
    │  truth_point, truth_cache, truth_status (ok/warmup/provisional/insufficient)     │
    └─────────────┬───────────────────────────────────────────────────┬───────────────┘
                  │                                                   │
                  ▼                                                   ▼
    ┌───────────────────────────┐                       ┌───────────────────────────┐
    │        STRUCTURE           │                       │         EVIDENCE           │
    │  structure_snapshot:       │                       │  evidence_snapshot:        │
    │  cage{status,upper,lower,  │                       │  dir_bus (EMA,OI,VD,MTF)   │
    │   pp,rangeAtr,breakout},   │                       │  exit_bus (RSI,W%R,MACD,   │
    │  wave{structure,count},    │                       │   HOLD,vel,acc)            │
    │  ladder, nearest{sup,res}, │                       │  correction_bus (pp,phase, │
    │  dist_ceiling, dist_floor, │                       │   dist_ceiling,dist_floor, │
    │  market_phase, escape_path │                       │   wave,cage,breakout)      │
    │  wave_history, cage_history│                       │  mtf, max_score            │
    └─────────────┬─────────────┘                       └─────────────┬─────────────┘
                  │                                                   │
                  │         ┌─────────────────────────────────────────┘
                  │         │
                  ▼         ▼
    ┌───────────────────────────────────────────────────────────────────────────────────┐
    │                              CLONE (×3 PER-CLONE)                                  │
    │                                                                                   │
    │  ┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐               │
    │  │   LONG Clone     │    │   SHORT Clone     │    │   GRID Clone    │               │
    │  │  stDir=+1        │    │  stDir=-1         │    │  cage_valid     │               │
    │  │  EMA-slope>0     │    │  EMA-slope<0      │    │  fee_safe       │               │
    │  │  vd>0            │    │  vd<0             │    │  breakout_none  │               │
    │  │  corridor.inZone │    │  corridor SHORT   │    │  pp_zone        │               │
    │  │  fee_safe        │    │  fee_safe(dist_f) │    │  grid_fills[]   │               │
    │  │  global_ok       │    │  global_ok        │    │  (buta arah)    │               │
    │  └────────┬────────┘    └─────────┬─────────┘    └────────┬────────┘               │
    │           │                       │                        │                        │
    │  clone_observation + clone_snapshot per candle (even no-trade)                      │
    └───────────┼───────────────────────┼────────────────────────┼────────────────────────┘
                │                       │                        │
                ▼                       ▼                        ▼
    ┌───────────────────┐   ┌───────────────────┐   ┌───────────────────┐
    │ TRADE (LONG)       │   │ TRADE (SHORT)      │   │ TRADE (GRID)       │
    │ entry→position→    │   │ entry→position→    │   │ grid_eval→fills→   │
    │ profit→exit→marker │   │ profit→exit→marker │   │ close→marker       │
    └─────────┬─────────┘   └─────────┬─────────┘   └─────────┬─────────┘
              │                       │                        │
              ▼                       ▼                        ▼
    ┌───────────────────┐   ┌───────────────────┐   ┌───────────────────┐
    │ POSITION (LONG)    │   │ POSITION (SHORT)   │   │ POSITION (GRID)    │
    │ MAE/MFE/trail/     │   │ MAE/MFE/trail/     │   │ fills/coverage/    │
    │ partial/breakeven  │   │ partial/breakeven  │   │ imbalance          │
    └─────────┬─────────┘   └─────────┬─────────┘   └─────────┬─────────┘
              │                       │                        │
              └───────────────────────┼────────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────────────┐
                    │            STATISTICS                    │
                    │  statistics_snapshot: per_clone {        │
                    │    sample, win_rate, expectancy, PF,     │
                    │    MAE, MFE, fee_drag, wrong_rate,       │
                    │    coverage, distance_health,            │
                    │    fee_safe_margin, wrong_entry_dist     │
                    │  } sample-gated (≥30 = CUKUP)            │
                    └─────────────────┬───────────────────────┘
                                      │
                                      ▼
    ┌───────────────────────────────────────────────────────────────────────────────────┐
    │                                KNOWLEDGE                                            │
    │                                                                                   │
    │  River (append+index+chronicle)                                                    │
    │    │                                                                              │
    │    └──► Academy (win_rate empiris bersyarat per clone/structure/distance/reason)   │
    │           │                                                                        │
    │           ├──► Oracle (euclidean similarity; match>7500; vektor beku)  [PARALLEL]  │
    │           │       │                                                                │
    │           │       └──► HiveMind (market_understanding: score+bias+boost)           │
    │           │              (wajib currentEvidence dari evidence_snapshot)            │
    │           │                                                                        │
    │           ├──► Darwin (usul mutasi Kelas-A bounded / Kelas-B PEX)                 │
    │           │                                                                        │
    │           ├──► Librarian (lifecycle: NEW→OBS→TRUSTED→MATURE/DEAD/DEPRECATED)      │
    │           │                                                                        │
    │           └──► CERMIN (calibration_error: predicted vs actual)                     │
    │                                                                                   │
    │  knowledge_snapshot: academy_artifacts[], oracle_match, market_understanding,      │
    │                      darwin_proposals[], librarian_events[], cermin                │
    └───────────────┬───────────────────────────────────────────────────────────────────┘
                    │
                    ├──────────────────────────────────────────┐
                    ▼                                          ▼
    ┌───────────────────────────┐              ┌───────────────────────────┐
    │        PREDICTION          │              │        GOVERNANCE          │
    │  prediction_snapshot:      │              │  governance_proposals:     │
    │  intelligence_score,       │              │  param_name, proposed_value│
    │  dominant_bias,            │              │  bounded_check, status     │
    │  empirical_win_rate,       │              │  (PENDING/APPROVED/        │
    │  similarity_score,         │              │   REJECTED/ROLLED_BACK)    │
    │  pattern_boost,            │              │  governance_logs,          │
    │  oracle_boost,             │              │  rollback_logs             │
    │  cermin_error              │              │  6 validations:            │
    └─────────────┬─────────────┘              │   Constitution/Proposal/    │
                  │                            │   Authority Matrix/Build/   │
                  ▼                            │   Runtime/Governance Audit  │
    ┌───────────────────────────┐              │  3-rem: Darwin/WASIT/Human  │
    │         CONSUMER           │              └───────────────────────────┘
    │  (opsional, terminal)      │
    │  fundEval, vetoGate,       │
    │  intentBuilder,            │
    │  liveAdapter (disabled     │
    │  default), exportCSV       │
    └───────────────────────────┘

    ┌───────────────────────────────────────────────────────────────────────────────────┐
    │                              CROSS-CUTTING                                          │
    │                                                                                   │
    │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
    │  │   REPLAY      │  │  SIMULATION  │  │   AUDIT      │  │   BENCHMARK          │  │
    │  │  6 types:     │  │  4 types:    │  │  6 domains:  │  │  WASIT 5-gate:       │  │
    │  │  candle       │  │  historical  │  │  pipeline    │  │  G1 aggregate        │  │
    │  │  snapshot     │  │  live        │  │  snapshot    │  │  G2 consistency      │  │
    │  │  trade        │  │  strategy    │  │  clone       │  │  G3 improvement      │  │
    │  │  clone        │  │  clone       │  │  trade       │  │  G4 significance     │  │
    │  │  knowledge    │  │  (adverse-   │  │  knowledge   │  │  G5 stability        │  │
    │  │  governance   │  │   first)     │  │  governance  │  │  walk-forward        │  │
    │  └──────────────┘  └──────────────┘  └──────────────┘  │  parallel (Worker)    │  │
    │                                                         └──────────────────────┘  │
    │                                                                                   │
    │  ┌──────────────────────────────────────────────────────────────────────────────┐ │
    │  │                        VISUALIZATION (12 components)                          │ │
    │  │  Geometry Viewer | Clone Viewer | Trade Viewer | Replay Viewer |              │ │
    │  │  Knowledge Viewer | Panel Renderer | Governance UI | Simulation UI |          │ │
    │  │  Prediction Display | Consumer Display | Audit Display | Final Validation      │ │
    │  └──────────────────────────────────────────────────────────────────────────────┘ │
    │                                                                                   │
    │  ┌──────────────────────────────────────────────────────────────────────────────┐ │
    │  │                     FINAL_VALIDATION (12 components)                          │ │
    │  │  Runtime Check | Pipeline Check | Namespace Check | Feature Check |           │ │
    │  │  Truth Check | Clone Check | Trading Check | Knowledge Check |                │ │
    │  │  Replay Check | Governance Check | Constitution Check | Console Error Check   │ │
    │  └──────────────────────────────────────────────────────────────────────────────┘ │
    └───────────────────────────────────────────────────────────────────────────────────┘
```

### 2.3 Forbidden Dependencies (BUILD STOP)

```
                    ┌───────────────────────────────────────────────────────────────┐
                    │                    FORBIDDEN DEPENDENCIES                       │
                    │                      (any = BUILD STOP)                         │
                    ├───────────────────────────────────────────────────────────────┤
                    │                                                                │
                    │  KNOWLEDGE → TRUTH          ◄── loop back to Core              │
                    │  KNOWLEDGE → STRUCTURE      ◄── loop back to Core              │
                    │  KNOWLEDGE → EVIDENCE       ◄── loop back to Core              │
                    │  KNOWLEDGE → CLONE          ◄── loop back to Core              │
                    │  CONSUMER → TRUTH           ◄── Consumer modifies Core         │
                    │  CONSUMER → STRUCTURE       ◄── Consumer modifies Core         │
                    │  CONSUMER → EVIDENCE        ◄── Consumer modifies Core         │
                    │  ORACLE → TRUTH             ◄── HiveMind writes Truth          │
                    │  HIVEMIND → CLONE           ◄── HiveMind writes Clone          │
                    │  DARWIN → auto-execute      ◄── Darwin auto-executes           │
                    │  GOVERNANCE → Core-logic    ◄── only BOUNDED params allowed    │
                    │  CLONE → TRUTH              ◄── Clone computes geometry        │
                    │  EVIDENCE → TRUTH           ◄── Evidence writes Truth          │
                    │  W%R → Entry                ◄── LAW-MASTER-08                  │
                    │  MACD → Entry               ◄── LAW-MASTER-15                  │
                    │  RSI → Entry                ◄── LAW-MASTER-15                  │
                    │  GRID → active in trend     ◄── HUKUM CAGE                    │
                    │  WORKER → IndexedDB write   ◄── LAW-MASTER-17                  │
                    │  Date.now() → logic         ◄── LAW-MASTER-01                  │
                    │  Math.random() → logic      ◄── LAW-MASTER-01                  │
                    │                                                                │
                    │  Only valid backward arrow: GOVERNANCE → BOUNDED params        │
                    └───────────────────────────────────────────────────────────────┘
```

---

## 3. PIPELINE DEPENDENCY

### 3.1 Complete 22-Stage Pipeline

```
 ┌────────────────────────────────────────────────────────────────────────────────────┐
 │                                  PIPELINE PER CLOSED CANDLE                          │
 └────────────────────────────────────────────────────────────────────────────────────┘

 ╔══════════════════════════════════════════════════════════════════════════════════════╗
 ║                          SHARED BLOCK (stages 1–5, 1×)                              ║
 ║                    dilarang dibungkus loop clone (Card Sharing)                      ║
 ╠════╤══════════════════════╤══════════╤══════════════════════════╤════════════════════╣
 ║ #  │ Stage                │ Input    │ Output                  │ Dependency          ║
 ╠════╪══════════════════════╪══════════╪══════════════════════════╪════════════════════╣
 ║ 1  │ BOOT                 │ config/  │ SYSTEM_BOOT             │ upstream: —         ║
 ║    │                      │ registry │ runtime+config+ckpt     │ downstream: all     ║
 ║    │                      │          │                         │ mandatory: config   ║
 ║    │                      │          │                         │ forbidden: —        ║
 ╠════╪══════════════════════╪══════════╪══════════════════════════╪════════════════════╣
 ║ 2  │ Market Observation   │ candle   │ market_snapshot         │ upstream: BOOT      ║
 ║    │ (MARKET)             │ mentah   │ (OHLCV+hygiene+gap+OI)  │ downstream: TRUTH   ║
 ║    │                      │          │                         │ mandatory: CLOSED   ║
 ║    │                      │          │                         │ forbidden: PROV     ║
 ╠════╪══════════════════════╪══════════╪══════════════════════════╪════════════════════╣
 ║ 3  │ Truth                │ market   │ truth_snapshot          │ upstream: MARKET    ║
 ║    │ (TRUTH)              │ + ckpt   │ (st,ATR,EMA,MACD,       │ downstream: STRUCT, ║
 ║    │                      │          │  W%R,RSI,dist,distAtr)  │              EVID    ║
 ║    │                      │          │                         │ mandatory: VALID    ║
 ║    │                      │          │                         │ forbidden: padding  ║
 ╠════╪══════════════════════╪══════════╪══════════════════════════╪════════════════════╣
 ║ 4  │ Structure            │ truth    │ structure_snapshot      │ upstream: TRUTH     ║
 ║    │ (STRUCTURE)          │ + lines  │ (cage,wave,ladder,       │ downstream: CLONE,  ║
 ║    │                      │          │  nearest,pp,phase,       │              GRID   ║
 ║    │                      │          │  dist_ceiling/floor)     │ mandatory: HUKUM    ║
 ║    │                      │          │                         │ forbidden: padded   ║
 ╠════╪══════════════════════╪══════════╪══════════════════════════╪════════════════════╣
 ║ 5  │ Evidence             │ truth    │ evidence_snapshot       │ upstream: TRUTH,    ║
 ║    │ (EVIDENCE)           │ + candle │ (dir_bus,exit_bus,       │           MARKET,   ║
 ║    │                      │ + OI     │  correction_bus,MTF,     │           STRUCT    ║
 ║    │                      │ + wave   │  max_score)              │ downstream: CLONE,  ║
 ║    │                      │          │                         │           HIVEMIND   ║
 ║    │                      │          │                         │ mandatory: 3 buses  ║
 ║    │                      │          │                         │ forbidden: W%R→entry║
 ╚════╧══════════════════════╧══════════╧══════════════════════════╧════════════════════╝

 ╔══════════════════════════════════════════════════════════════════════════════════════╗
 ║                      PER-CLONE BLOCK (stages 6–12, ×3)                              ║
 ║                    LONG / SHORT / GRID — sub-ledger terisolasi                       ║
 ╠════╤══════════════════════╤══════════╤══════════════════════════╤════════════════════╣
 ║ #  │ Stage                │ Input    │ Output                  │ Dependency          ║
 ╠════╪══════════════════════╪══════════╪══════════════════════════╪════════════════════╣
 ║ 6  │ Clone Observation    │ snapshot │ clone_observation       │ upstream: STRUCT,   ║
 ║    │ (CLONE)              │ + ledger │ + clone_snapshot        │           EVID,     ║
 ║    │                      │          │ (wajib tiap candle,     │           TRUTH     ║
 ║    │                      │          │  even no-trade)         │ downstream: TRADE   ║
 ║    │                      │          │                         │ mandatory: 3 obs    ║
 ║    │                      │          │                         │ forbidden: skip     ║
 ╠════╪══════════════════════╪══════════╪══════════════════════════╪════════════════════╣
 ║ 7  │ Entry Validation     │ observasi│ ENTRY_MARKER /          │ upstream: CLONE     ║
 ║    │ (TRADE)              │ + global │ no-trade (beralasan)    │ downstream: POS     ║
 ║    │                      │          │                         │ mandatory: konjungsi║
 ║    │                      │          │                         │ forbidden: W%R/RSI  ║
 ║    │                      │          │                         │            entry    ║
 ╠════╪══════════════════════╪══════════╪══════════════════════════╪════════════════════╣
 ║ 8  │ Position Management  │ posisi   │ mae/mfe/trail update    │ upstream: TRADE     ║
 ║    │ (POSITION)           │ + candle │                         │ downstream: PROFIT  ║
 ║    │                      │ + exit   │                         │ mandatory: position ║
 ║    │                      │ _bus     │                         │ forbidden: —        ║
 ╠════╪══════════════════════╪══════════╪══════════════════════════╪════════════════════╣
 ║ 9  │ Profit Management    │ unreal   │ partial/lock/trail      │ upstream: POS       ║
 ║    │ (POSITION)           │ + ATR    │                         │ downstream: EXIT    ║
 ║    │                      │ + exit   │                         │ mandatory: —        ║
 ║    │                      │ _bus     │                         │ optional: hold-veto ║
 ╠════╪══════════════════════╪══════════╪══════════════════════════╪════════════════════╣
 ║ 10 │ Exit Validation      │ guard    │ alasan exit / null      │ upstream: POS       ║
 ║    │ (TRADE/POSITION)     │ + cage   │                         │ downstream: CLOSE   ║
 ║    │                      │ + prior  │                         │ mandatory: 1–5 >    ║
 ║    │                      │ itas     │                         │            6–7     ║
 ║    │                      │          │                         │ forbidden: —        ║
 ╠════╪══════════════════════╪══════════╪══════════════════════════╪════════════════════╣
 ║ 11 │ Close + Marker       │ alasan   │ EXIT_MARKER             │ upstream: EXIT      ║
 ║    │ (SIM)                │ + harga  │ + trade_snapshot        │ downstream: STATS   ║
 ║    │                      │ (adverse │ (after-fee, WIN only    │ mandatory: adverse- ║
 ║    │                      │  -first) │  if net>0)              │            first    ║
 ║    │                      │          │                         │ forbidden: TP > SL  ║
 ║    │                      │          │                         │            se-candle║
 ╠════╪══════════════════════╪══════════╪══════════════════════════╪════════════════════╣
 ║ 12 │ Trade Marker         │ entry/   │ trade_snapshot          │ upstream: CLOSE     ║
 ║    │ (SIM)                │ exit     │ (aggregated markers)    │ downstream: STATS   ║
 ║    │                      │ candle   │                         │ mandatory: after-fee║
 ║    │                      │ ini      │                         │ forbidden: —        ║
 ╚════╧══════════════════════╧══════════╧══════════════════════════╧════════════════════╝

 ╔══════════════════════════════════════════════════════════════════════════════════════╗
 ║                    SHARED-AGAIN BLOCK (stages 13–22, 1×)                             ║
 ║                        card-agnostic, unidirectional                                  ║
 ╠════╤══════════════════════╤══════════╤══════════════════════════╤════════════════════╣
 ║ #  │ Stage                │ Input    │ Output                  │ Dependency          ║
 ╠════╪══════════════════════╪══════════╪══════════════════════════╪════════════════════╣
 ║ 13 │ Statistics           │ marker   │ statistics_snapshot     │ upstream: TRADE     ║
 ║    │ (STATISTICS)         │ + snap   │ (win_rate,expectancy,   │ downstream: KNOW    ║
 ║    │                      │          │  PF,MAE,MFE, fee_drag)  │ mandatory: CUKUP    ║
 ║    │                      │          │                         │            iff ≥30  ║
 ║    │                      │          │                         │ forbidden: <ambang  ║
 ╠════╪══════════════════════╪══════════╪══════════════════════════╪════════════════════╣
 ║ 14 │ Knowledge            │ card-    │ knowledge_snapshot      │ upstream: STATS     ║
 ║    │ (KNOWLEDGE)          │ agnostic │ (Academy→…→Chronicle)   │ downstream: PRED,   ║
 ║    │                      │          │                         │           GOV       ║
 ║    │                      │          │                         │ mandatory: unidir   ║
 ║    │                      │          │                         │ forbidden: ML/loop  ║
 ╠════╪══════════════════════╪══════════╪══════════════════════════╪════════════════════╣
 ║ 15 │ Benchmark            │ 2 config │ benchmark_snapshot      │ upstream: SIM       ║
 ║    │ (BENCHMARK)          │ + replay │ (WASIT 5-gate)          │ downstream: GOV     ║
 ║    │                      │          │                         │ mandatory: —        ║
 ║    │                      │          │                         │ optional: ON-DEMAND ║
 ║    │                      │          │                         │ forbidden: per-candle║
 ╠════╪══════════════════════╪══════════╪══════════════════════════╪════════════════════╣
 ║ 16 │ Oracle               │ vektor   │ oracle_match            │ upstream: ACADEMY   ║
 ║    │ (KNOWLEDGE)          │ kini +   │ (euclidean similarity)  │ downstream: HIVE    ║
 ║    │                      │ historis │                         │ mandatory: match>   ║
 ║    │                      │          │                         │            7500     ║
 ║    │                      │          │                         │ forbidden: W%R/MACD ║
 ╠════╪══════════════════════╪══════════╪══════════════════════════╪════════════════════╣
 ║ 17 │ HiveMind             │ artifact │ market_understanding    │ upstream: ACADEMY,  ║
 ║    │ (KNOWLEDGE)          │ + oracle │ (score+bias+boost)      │           ORACLE,   ║
 ║    │                      │ + evid   │                         │           EVID      ║
 ║    │                      │ ence     │                         │ downstream: PRED    ║
 ║    │                      │          │                         │ mandatory: current  ║
 ║    │                      │          │                         │           Evidence   ║
 ║    │                      │          │                         │ forbidden: signal   ║
 ╠════╪══════════════════════╪══════════╪══════════════════════════╪════════════════════╣
 ║ 18 │ Academy              │ marker   │ academy_artifacts       │ upstream: STATS     ║
 ║    │ (KNOWLEDGE)          │ + bucket │ (per clone/structure/   │ downstream: HIVE,   ║
 ║    │                      │          │  distance_bucket/reason) │           ORACLE,   ║
 ║    │                      │          │                         │           DARWIN,   ║
 ║    │                      │          │                         │           LIBRARIAN ║
 ║    │                      │          │                         │ mandatory: 4-dim    ║
 ║    │                      │          │                         │ forbidden: no-ML    ║
 ╠════╪══════════════════════╪══════════╪══════════════════════════╪════════════════════╣
 ║ 19 │ River                │ seluruh  │ append+index+chronicle  │ upstream: all cards ║
 ║    │ (KNOWLEDGE)          │ card     │                         │ downstream: all     ║
 ║    │                      │          │                         │ mandatory: archivist║
 ║    │                      │          │                         │ forbidden: berpikir ║
 ╠════╪══════════════════════╪══════════╪══════════════════════════╪════════════════════╣
 ║ 20 │ Darwin               │ artifact │ darwin_proposals        │ upstream: ACADEMY   ║
 ║    │ (GOVERNANCE)         │ + bounded│ (Kelas-A bounded /      │ downstream: GOV     ║
 ║    │                      │ + PEX    │  Kelas-B PEX)           │ mandatory: —        ║
 ║    │                      │          │                         │ forbidden: auto-exec║
 ╠════╪══════════════════════╪══════════╪══════════════════════════╪════════════════════╣
 ║ 21 │ Prediction           │ under-   │ prediction_snapshot     │ upstream: KNOW      ║
 ║    │ (PREDICTION)         │ standing │ (empiris+similarity)    │ downstream: CONS    ║
 ║    │                      │ + academy│                         │ mandatory: no-model ║
 ║    │                      │ + oracle │                         │ forbidden: forecast ║
 ╠════╪══════════════════════╪══════════╪══════════════════════════╪════════════════════╣
 ║ 22 │ Governance           │ proposal │ decision+config_version │ upstream: DARWIN    ║
 ║    │ (GOVERNANCE)         │ + verdict│ (loop only to BOUNDED)  │ downstream: all     ║
 ║    │                      │ + human  │                         │            (params) ║
 ║    │                      │          │                         │ mandatory: 6 valid  ║
 ║    │                      │          │                         │ forbidden: Core-log║
 ╚════╧══════════════════════╧══════════╧══════════════════════════╧════════════════════╝

 ╔══════════════════════════════════════════════════════════════════════════════════════╗
 ║                          ON-DEMAND (stage 15)                                        ║
 ║                    Benchmark = NOT per-candle                                         ║
 ╠════╤══════════════════════╤══════════╤══════════════════════════╤════════════════════╣
 ║ 15 │ Benchmark            │ 2 config │ benchmark_snapshot      │ Absent on closed    ║
 ║    │ (BENCHMARK)          │ + replay │ (WASIT 5-gate,          │ candle biasa.       ║
 ║    │                      │          │  walk-forward)          │ Triggered only on   ║
 ║    │                      │          │                         │ demand.             ║
 ╚════╧══════════════════════╧══════════╧══════════════════════════╧════════════════════╝

 ╔══════════════════════════════════════════════════════════════════════════════════════╗
 ║                          OPTIONAL (Consumer)                                         ║
 ╠════╤══════════════════════╤══════════╤══════════════════════════╤════════════════════╣
 ║ —  │ Consumer             │ under-   │ intent/report           │ live disabled       ║
 ║    │ (CONSUMER)           │ standing │ (trade is optional)     │ default. Trade is   ║
 ║    │                      │ + rapor  │                         │ Optional, Learning  ║
 ║    │                      │          │                         │ is Mandatory.       ║
 ╚════╧══════════════════════╧══════════╧══════════════════════════╧════════════════════╝
```

### 3.2 Pipeline Invarian

```
SHARED (stages 2–5):    DILARANG dibungkus loop clone — pelanggaran Card Sharing
PER-CLONE (stages 6–12): WAJIB per-clone dengan sub-ledger terisolasi
SHARED-AGAIN (13–22):   card-agnostic & unidirectional — tak menulis balik ke 2–12
                         kecuali parameter bounded via stage 22 (GOVERNANCE)
ON-DEMAND (15):         Benchmark TIDAK per-candle
OPTIONAL:               Consumer di ujung; live disabled default
```

---

## 4. TRADING DEPENDENCY

### 4.1 Entry Dependencies

| Dependency | LONG | SHORT | GRID | Type | Source |
|-----------|------|-------|------|------|--------|
| **stDir** | stDir = +1 | stDir = −1 | — (buta arah) | mandatory | TRUTH |
| **EMA-slope** | EMA-slope > 0 | EMA-slope < 0 | — (buta arah) | mandatory | TRUTH (dir_bus.ema) |
| **volDelta** | vd > 0 | vd < 0 | — (buta arah) | mandatory | TRUTH (dir_bus.vd) |
| **corridor** | corridor.inZone (LONG zone) | corridor.inZone (SHORT zone) | — | mandatory | CLONE_SHARED.corridor |
| **fee_safe** | dist_ceiling ≥ required | dist_floor ≥ required | width ≥ 3·required | mandatory | FEE, STRUCTURE |
| **global_ok** | gross/net exposure < limit | gross/net exposure < limit | gross/net exposure < limit | mandatory | CLONE_SHARED |
| **open** | open == null (no existing position) | open == null | — | mandatory | POSITION |
| **cage_valid** | — | — | cage.status ∈ {VALID, LOOSE} | mandatory | STRUCTURE |
| **breakout_none** | — | — | cage.breakout = NONE | mandatory | STRUCTURE |
| **pp_zone** | — | — | pp ∈ {BUY_ZONE, SELL_ZONE} | mandatory | STRUCTURE |
| **fills_per_side** | — | — | fills < max_fills | mandatory | GRID |
| **MTF** | mtf.long (context) | mtf.short (context) | — (buta MTF) | optional | EVIDENCE |
| **OI** | oi.status (context) | oi.status (context) | — (buta arah) | optional | EVIDENCE (oiInherit) |
| **confidence** | confidence_score (context) | confidence_score (context) | — | optional | EVIDENCE |

#### LONG Entry Conjunction
```
stDir = +1
  ∧ dir_ok(EMA-slope > 0 ∧ vd > 0)
  ∧ corridor.inZone
  ∧ fee_safe(dist_ceiling ≥ required)
  ∧ global_ok
  ∧ open == null
```

#### SHORT Entry Conjunction (mirror)
```
stDir = −1
  ∧ dir_ok(EMA-slope < 0 ∧ vd < 0)
  ∧ corridor.inZone (SHORT zone)
  ∧ fee_safe(dist_floor ≥ required)
  ∧ global_ok
  ∧ open == null
```

#### GRID Entry Conjunction
```
cage_valid (status ∈ {VALID, LOOSE})
  ∧ fee_safe(width ≥ 3·required)
  ∧ breakout_none
  ∧ pp ∈ {BUY_ZONE, SELL_ZONE}
  ∧ fills_per_side < max_fills
  ∧ arah fill dari zona pp
```

### 4.2 Exit Dependencies

| Dependency | LONG | SHORT | GRID | Type | Priority | Source |
|-----------|------|-------|------|------|----------|--------|
| **SL** | floor (nearest.support) | ceiling (nearest.resistance) | — | mandatory | 1 (highest) | STRUCTURE |
| **TP** | min(ceiling, cage.upper, entry+TP_ATR·ATR) | min(floor, cage.lower, entry−TP_ATR·ATR) | prof ≥ required | mandatory | 2 | STRUCTURE, FEE |
| **wrong-entry** | floor breach / vel > 0 / acc > 0 | ceiling breach / vel < 0 / acc < 0 | adv ≥ WRONG_PCT | mandatory | 3 | EVIDENCE, POSITION |
| **exit-bus** | RSI/W%R/MACD overbought | RSI/W%R/MACD oversold | — | mandatory | 4 | EVIDENCE (exit_bus) |
| **hold-veto** | hold-veto tahan 6–7 candle | hold-veto tahan 6–7 candle | — | mandatory | 5 | EVIDENCE (exit_bus.hold) |
| **time-exit** | hold_count ≥ max_hold | hold_count ≥ max_hold | — | optional | 6 | POSITION |
| **trailing** | ATR-based trailing stop | ATR-based trailing stop | — | optional | — | POSITION |
| **stop-semua** | — | — | ¬cage_valid | mandatory | — | STRUCTURE |
| **range-break** | — | — | breakout berlawanan | mandatory | — | STRUCTURE |

#### Exit Priority Chain
```
SL (priority 1) > TP (2) > wrong-entry (3) > exit-bus (4) > hold-veto (5) > time-exit (6)
1–5 > 6–7  (hard vs soft)
Adverse-first: SL & TP se-candle → SL menang
```

### 4.3 Fee Dependencies

| Fee Layer | LONG | SHORT | GRID | Type | Source |
|-----------|------|-------|------|------|--------|
| **fee_murni** | 0.04%–0.10% (taker fee) | 0.04%–0.10% | 0.04%–0.10% | mandatory | FEE module |
| **required** | GRID_MIN_NET + fee_murni + slip_seeded + safety | same | same | mandatory | FEE module |
| **layered** | net = gross − fee_murni − slip_seeded − safety | same | same | mandatory | SIM |
| **slip_seeded** | seeded PRNG, bounded | seeded PRNG, bounded | seeded PRNG, bounded | mandatory | SIM |
| **WIN** | only if net > 0 (after-fee) | only if net > 0 | only if net > 0 | mandatory | SIM |
| **adverse-first** | SL beats TP same-candle | SL beats TP same-candle | — | mandatory | SIM |

#### REQUIRED_MOVE Formula
```
REQUIRED_MOVE = GRID_MIN_NET_PCT_OF_FILL + fee_murni(taker, discount) + slip_seeded + safety_margin
              = 0.7% nominal (bounded; configurable via BOUNDED registry)
```

### 4.4 Clone-Specific Forbidden Dependencies

| Forbidden | LONG | SHORT | GRID |
|-----------|------|-------|------|
| W%R → entry | X | X | — |
| RSI → entry | X | X | — |
| MACD → entry | X | X | — |
| Read Oracle/HiveMind directly | X | X | — |
| Write Truth | X | X | — |
| Entry saat fee-unsafe | X | X | — |
| Compute geometry from OHLCV | X | X | X |
| Mix LONG/SHORT statistics | X | X | — |
| SIDEWAY → LONG | X | — | — |
| Active in trend (cage NONE) | — | — | X |
| Use MTF as veto | — | — | X |
| Trailing ATR per fill | — | — | X |
| Read Direction/MTF | — | — | X |

---

## 5. KNOWLEDGE DEPENDENCY

### 5.1 Six Knowledge Entities + CERMIN

| Entity | Reads (Upstream) | Produces (Output) | Consumed By (Downstream) |
|--------|-----------------|-------------------|--------------------------|
| **River** | seluruh card (all snapshots) | store+index+chronicle (append-only) | Academy, Oracle, HiveMind, Darwin, Librarian, CERMIN, AUDIT |
| **Academy** | marker (EXIT) + snapshot (join on ts/candle_id) | academy_artifacts (per clone/structure/distance_bucket/reason), CERMIN materials | Oracle, HiveMind, Darwin, Librarian, PREDICTION |
| **Oracle** | vektor kini (current candle) + vektor historis (Academy) | oracle_match (euclidean similarity; match>7500; tie-break terbaru) | HiveMind, PREDICTION |
| **HiveMind** | artifacts (Academy) + oracle_match (Oracle) + **currentEvidence** (evidence_snapshot) | market_understanding (score+bias+boost) | PREDICTION, CONSUMER |
| **Darwin** | artifacts (Academy) + bounded registry + PEX | darwin_proposals (Kelas-A bounded / Kelas-B PEX) | GOVERNANCE |
| **Librarian** | artifacts (Academy) | lifecycle events (NEW→OBS→TRUSTED→MATURE/DEAD/DEPRECATED) | Darwin (filter proposals), GOVERNANCE |
| **CERMIN** | predicted vs actual per clone | calibration_error (band, predicted, actual) | PREDICTION (calibration_error), HiveMind (confidence adjustment) |

### 5.2 Canonical Chain (ASCII)

```
┌───────────────────────────────────────────────────────────────────────────────────┐
│                            KNOWLEDGE CANONICAL CHAIN                                │
│                                                                                   │
│  ┌──────────┐                                                                     │
│  │  RIVER    │ ◄── continuously records ALL cards (archivist, no thinking)        │
│  │  (dasar)  │     store + index + chronicle                                      │
│  └─────┬─────┘                                                                     │
│        │                                                                           │
│        ▼                                                                           │
│  ┌──────────┐                                                                     │
│  │ ACADEMY   │ ◄── marker (EXIT) + snapshot (join on ts/candle_id)               │
│  │           │     win_rate empiris bersyarat per (clone, structure,              │
│  │           │     distance_bucket, reason) — 4 dimensions                        │
│  │           │     sample-gated (CUKUP iff n ≥ 30)                                │
│  └──┬───┬───┘                                                                     │
│     │   │                                                                          │
│     │   │  ╔══════════════════════════════════╗                                   │
│     │   │  ║       PARALLEL BRANCH            ║                                   │
│     │   │  ╠══════════════════════════════════╣                                   │
│     │   │  ║  ┌──────────┐                    ║                                   │
│     │   ├──╫─►│ ORACLE    │  ◄── vektor kini  ║                                   │
│     │   │  ║  │           │      + historis    ║                                   │
│     │   │  ║  │           │      euclidean     ║                                   │
│     │   │  ║  │           │      similarity    ║                                   │
│     │   │  ║  │           │      match > 7500  ║                                   │
│     │   │  ║  │           │      tie-break     ║                                   │
│     │   │  ║  │           │      terbaru       ║                                   │
│     │   │  ║  └─────┬─────┘                    ║                                   │
│     │   │  ║        │                          ║                                   │
│     │   │  ║        ▼                          ║                                   │
│     │   │  ║  ┌──────────┐                    ║                                   │
│     │   └──╫─►│ HIVEMIND │  ◄── artifacts      ║                                   │
│     │      ║  │           │      + oracle_match ║                                   │
│     │      ║  │           │      + currentEvid  ║  ◄── WAJIB dari evidence_snapshot│
│     │      ║  │           │      market_        ║     (bukan konstanta)             │
│     │      ║  │           │      understanding  ║                                   │
│     │      ║  │           │      (score+bias    ║                                   │
│     │      ║  │           │       +boost)       ║                                   │
│     │      ║  └───────────┘                    ║                                   │
│     │      ╚══════════════════════════════════╝                                    │
│     │                                                                              │
│     ├──────────────► ┌──────────┐                                                  │
│     │                │  DARWIN   │ ◄── artifacts + bounded registry + PEX          │
│     │                │           │     usul mutasi Kelas-A (bounded)               │
│     │                │           │     / Kelas-B (PEX)                             │
│     │                │           │     tak auto-execute                            │
│     │                └─────┬─────┘                                                  │
│     │                      │                                                       │
│     │                      ▼                                                       │
│     │                ┌──────────┐                                                  │
│     └───────────────►│LIBRARIAN │ ◄── artifacts                                     │
│                      │           │     lifecycle: NEW → OBSERVATION →              │
│                      │           │     TRUSTED → MATURE / DEAD / DEPRECATED        │
│                      │           │     sample + stability gated                    │
│                      │           │     DEAD/DEPRECATED = non-aktif                 │
│                      └─────┬─────┘                                                  │
│                            │                                                       │
│                            ▼                                                       │
│                      ┌──────────┐                                                  │
│                      │ CHRONICLE │ ◄── all events recorded                          │
│                      │           │     audit trail complete                        │
│                      └──────────┘                                                  │
│                                                                                   │
│  ┌──────────────────────────────────────────────────────────────────────────┐    │
│  │                              CERMIN                                        │    │
│  │  Calibration error tracking: predicted vs actual per clone per bucket     │    │
│  │  Input: STATISTICS (tradeStats) + ACADEMY (artifacts)                      │    │
│  │  Output: calibration_error (band, predicted, actual)                       │    │
│  │  Consumed by: PREDICTION (confidence honesty), HIVEMIND (adjustment)       │    │
│  └──────────────────────────────────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────────────────────────────────┘

Canonical chain: River → Academy → (Oracle ∥) → HiveMind → Darwin → Librarian → Chronicle
```

### 5.3 Oracle Vector (Frozen)

```
Vector = [norm_code(wave), norm_code(cage.status), pp,
          norm01(dir_bus.ema), norm01(dir_bus.oi), norm01(dir_bus.vd),
          norm_code(mtf.sector), norm01(rsi), norm01(distAtr)]

Forbidden in vector: W%R, MACD (LAW-MASTER-08/15)
Changing norm_code table = config_version baru
```

### 5.4 Knowledge Dependency Classification

| Entity | Upstream (feeds into) | Downstream (feeds from) | Mandatory | Optional | Forbidden |
|--------|----------------------|------------------------|-----------|----------|-----------|
| River | Academy, Oracle, all | all cards | YES | NO | berpikir, no-ML |
| Academy | Oracle, HiveMind, Darwin, Librarian, CERMIN | River, marker+snapshot | YES (4-dim) | NO | ML, forecasting |
| Oracle | HiveMind, PREDICTION | Academy, vector | YES (match>7500) | NO | W%R/MACD in vector |
| HiveMind | PREDICTION, CONSUMER | Academy, Oracle, EVIDENCE | YES (currentEvidence) | NO | signal, loop back |
| Darwin | GOVERNANCE | Academy, bounded, PEX | YES (no auto-exec) | NO | auto-execute |
| Librarian | Darwin, GOVERNANCE | Academy | YES (6 statuses) | NO | — |
| CERMIN | PREDICTION, HiveMind | STATISTICS, Academy | YES | NO | arbitrary fallback |

---

## 6. GOVERNANCE DEPENDENCY

### 6.1 Six Validations

```
┌───────────────────────────────────────────────────────────────────────────────────┐
│                              GOVERNANCE VALIDATIONS                                 │
│                                                                                   │
│  ┌──────────────────────────┐  ┌──────────────────────────┐                       │
│  │ 1. Constitution Validation│  │ 2. Proposal Validation   │                       │
│  │  18 laws + authority      │  │  bounded-check +         │                       │
│  │  matrix + W%R/clone/      │  │  label-peran PEX +       │                       │
│  │  snapshot contract        │  │  constitutional-atom     │                       │
│  │  GAGAL → BUILD STOP       │  │  GAGAL → auto-reject     │                       │
│  └──────────────────────────┘  │  (OUT_OF_RANGE/VIOLATION) │                       │
│                                └──────────────────────────┘                       │
│  ┌──────────────────────────┐  ┌──────────────────────────┐                       │
│  │ 3. Authority Matrix Val.  │  │ 4. Build Validation      │                       │
│  │  komponen tak dipakai di  │  │  15 build-stop-rule +    │                       │
│  │  luar kolom sah           │  │  inventory lengkap +     │                       │
│  │  (mis. W%R ≠ entry)       │  │  determinisme build      │                       │
│  │  GAGAL → BUILD STOP       │  │  GAGAL → BUILD STOP      │                       │
│  └──────────────────────────┘  └──────────────────────────┘                       │
│  ┌──────────────────────────┐  ┌──────────────────────────┐                       │
│  │ 5. Runtime Validation     │  │ 6. Governance Audit      │                       │
│  │  checksum card, lineage,  │  │  timeline keputusan,     │                       │
│  │  no-race writer,          │  │  rollback deterministik, │                       │
│  │  sample-gate, no-mock     │  │  deprecated tak hidup    │                       │
│  │  GAGAL → card ditolak /   │  │  GAGAL → ANOMALY event   │                       │
│  │          panel N/A        │  │                          │                       │
│  └──────────────────────────┘  └──────────────────────────┘                       │
└───────────────────────────────────────────────────────────────────────────────────┘
```

### 6.2 Proposal Lifecycle

```
┌───────────────────────────────────────────────────────────────────────────────────┐
│                              PROPOSAL LIFECYCLE                                     │
│                                                                                   │
│  ┌──────────────────┐                                                              │
│  │ 1. DARWIN writes  │                                                              │
│  │    proposal       │                                                              │
│  │    status: PENDING│                                                              │
│  │    or auto-       │                                                              │
│  │    REJECTED_OUT_OF│                                                              │
│  │    _RANGE/        │                                                              │
│  │    VIOLATION      │                                                              │
│  └────────┬─────────┘                                                              │
│           │                                                                         │
│           ▼                                                                         │
│  ┌──────────────────┐                                                              │
│  │ 2. WASIT walk-   │                                                              │
│  │    forward        │                                                              │
│  │    parallel 5-gate│                                                              │
│  │    FAIL → REJECTED│                                                              │
│  │    _BY_WASIT      │                                                              │
│  └────────┬─────────┘                                                              │
│           │                                                                         │
│           ▼                                                                         │
│  ┌──────────────────┐                                                              │
│  │ 3. PENDING_HUMAN │                                                              │
│  │    _APPROVAL      │                                                              │
│  │    → human        │                                                              │
│  │    approve/reject │                                                              │
│  └────────┬─────────┘                                                              │
│           │                                                                         │
│           ▼                                                                         │
│  ┌──────────────────┐                                                              │
│  │ 4. APPROVED →    │                                                              │
│  │    config_version │                                                              │
│  │    baru + audit   │                                                              │
│  │    rollback =     │                                                              │
│  │    tunjuk version │                                                              │
│  │    lama           │                                                              │
│  └──────────────────┘                                                              │
│                                                                                   │
│  Post-deploy: monitor rapor baru → bila memburuk → rollback                        │
│  Amandemen konstitusi (§3) = approval GANDA + tercatat CONSTITUTION_AMENDED        │
└───────────────────────────────────────────────────────────────────────────────────┘
```

### 6.3 Three-Rem (Darwin, WASIT, Human) Authority Matrix

```
┌───────────────────────────────────────────────────────────────────────────────────┐
│                              3-REM AUTHORITY MATRIX                                 │
│                                                                                   │
│  ┌──────────┬──────────────────────────────────┬──────────────────────────────┐   │
│  │  AKTOR   │             BOLEH                 │           DILARANG            │   │
│  ├──────────┼──────────────────────────────────┼──────────────────────────────┤   │
│  │  DARWIN  │ • usul Kelas-A (bounded params)  │ • auto-execute                │   │
│  │          │ • usul Kelas-B (PEX)             │ • ubah batas min/max           │   │
│  │          │ • baca artifact + bounded        │ • sentuh constitutional atom   │   │
│  │          │ • validator tolak campur-peran   │ • approve (hanya mengusulkan)  │   │
│  ├──────────┼──────────────────────────────────┼──────────────────────────────┤   │
│  │  WASIT   │ • walk-forward paralel           │ • approve (hanya menyaring)    │   │
│  │          │ • 5-gate evaluation              │ • meloloskan FAIL             │   │
│  │          │ • auto-reject FAIL               │ • rubber-stamp identik (G2)    │   │
│  │          │ • base vs candidate parallel     │                                │   │
│  ├──────────┼──────────────────────────────────┼──────────────────────────────┤   │
│  │  HUMAN   │ • approve/reject proposal        │ • — (rem terakhir)             │   │
│  │          │   yang lulus WASIT               │ • meloloskan bounded violation │   │
│  │          │ • approval GANDA untuk           │                                │   │
│  │          │   amandemen konstitusi           │                                │   │
│  ├──────────┼──────────────────────────────────┼──────────────────────────────┤   │
│  │ BOUNDED  │ • auto-reject nilai luar rentang │ • menerima nilai gila          │   │
│  │ REGISTRY │ • define min/max per parameter   │ • mengubah batas tanpa         │   │
│  │          │                                  │   amandemen konstitusi         │   │
│  ├──────────┼──────────────────────────────────┼──────────────────────────────┤   │
│  │ RUNTIME  │ • terapkan config_version baru   │ • hot-swap acak                │   │
│  │          │   pada boundary                  │ • loop balik ke Core-logic     │   │
│  │          │ • rollback deterministik         │                                │   │
│  └──────────┴──────────────────────────────────┴──────────────────────────────┘   │
│                                                                                   │
│  Kelas-A (BOUNDED):   parameter dalam rentang bounded registry                    │
│  Kelas-B (PEX):       Performance EXperiment — parameter baru / rentang baru      │
│                       → wajib WASIT walk-forward + approval ganda                 │
│  Amandemen Konstitusi: perubahan §3 freeze matrix → CONSTITUTION_AMENDED          │
│                       → WASIT + approval GANDA + Chronicle                        │
└───────────────────────────────────────────────────────────────────────────────────┘
```

### 6.4 Governance Dependency Classification

| Actor | Upstream | Downstream | Mandatory | Optional | Forbidden |
|-------|----------|------------|-----------|----------|-----------|
| Darwin | GOVERNANCE | WASIT | YES | NO | auto-execute |
| WASIT | Darwin | HUMAN | YES (5-gate) | NO | approve, rubber-stamp |
| Human | WASIT | RUNTIME | YES | NO | bypass bounded |
| Bounded | CONFIG | Darwin, WASIT | YES | NO | accept out-of-range |
| Runtime | HUMAN | all (params) | YES (rollback) | NO | loop to Core-logic |

### 6.5 Governance Lifecycle Flow

```
Constitution Validation → Proposal Validation → Authority Matrix Validation
  → Build Validation → Runtime Validation → Governance Audit

Gagal konstitusi/authority/build = BUILD STOP
Gagal proposal = auto-reject (OUT_OF_RANGE / VIOLATION)
Gagal runtime = card ditolak / panel N/A
Gagal audit = ANOMALY event
```

---

## 7. SNAPSHOT DEPENDENCY

### 7.1 Ten Snapshots

```
┌───────────────────────────────────────────────────────────────────────────────────┐
│                            10 SNAPSHOTS PER CLOSED CANDLE                          │
│                                                                                   │
│  ┌──────────┬───────────────┬─────────────────────┬──────────────┬──────────────┐ │
│  │ Snapshot │   Producer    │      Consumer        │   Creation   │  Validation  │ │
│  │          │   (domain)    │     (downstream)     │   Timing     │   / Replay   │ │
│  ├──────────┼───────────────┼─────────────────────┼──────────────┼──────────────┤ │
│  │ 1.Market │ MARKET        │ TRUTH               │ candle       │ checksum +   │ │
│  │          │               │                     │ CLOSED       │ hygiene      │ │
│  │          │               │                     │              │ candle/snap  │ │
│  │          │               │                     │              │ replay       │ │
│  ├──────────┼───────────────┼─────────────────────┼──────────────┼──────────────┤ │
│  │ 2.Truth  │ TRUTH         │ STRUCTURE, EVIDENCE │ after Market │ checksum +   │ │
│  │          │               │                     │              │ lineage      │ │
│  │          │               │                     │              │ snapshot     │ │
│  │          │               │                     │              │ replay       │ │
│  ├──────────┼───────────────┼─────────────────────┼──────────────┼──────────────┤ │
│  │ 3.Struct.│ STRUCTURE     │ CLONE, GRID         │ after Truth  │ HUKUM CAGE   │ │
│  │          │               │                     │              │ check        │ │
│  │          │               │                     │              │ snapshot     │ │
│  │          │               │                     │              │ replay       │ │
│  ├──────────┼───────────────┼─────────────────────┼──────────────┼──────────────┤ │
│  │ 4.Evid.  │ EVIDENCE      │ CLONE, HIVEMIND     │ after Truth  │ clamp+status │ │
│  │          │               │                     │              │ snapshot     │ │
│  │          │               │                     │              │ replay       │ │
│  ├──────────┼───────────────┼─────────────────────┼──────────────┼──────────────┤ │
│  │ 5.Clone  │ CLONE ×3      │ STATISTICS          │ per candle   │ 3-obs check  │ │
│  │          │               │                     │              │ clone replay │ │
│  ├──────────┼───────────────┼─────────────────────┼──────────────┼──────────────┤ │
│  │ 6.Trade  │ SIM           │ STATISTICS          │ per candle   │ net=WIN      │ │
│  │          │               │                     │              │ check        │ │
│  │          │               │                     │              │ trade replay │ │
│  ├──────────┼───────────────┼─────────────────────┼──────────────┼──────────────┤ │
│  │ 7.Stats. │ STATISTICS    │ KNOWLEDGE           │ after Trade  │ sample-gate  │ │
│  │          │               │                     │              │ knowledge    │ │
│  │          │               │                     │              │ replay       │ │
│  ├──────────┼───────────────┼─────────────────────┼──────────────┼──────────────┤ │
│  │ 8.Know.  │ KNOWLEDGE     │ PREDICTION, GOV     │ after Stats  │ unidir check │ │
│  │          │               │                     │              │ knowledge    │ │
│  │          │               │                     │              │ replay       │ │
│  ├──────────┼───────────────┼─────────────────────┼──────────────┼──────────────┤ │
│  │ 9.Bench. │ BENCHMARK     │ GOVERNANCE          │ on-demand    │ 5-gate       │ │
│  │          │               │                     │ (absent per  │ governance   │ │
│  │          │               │                     │  candle)     │ replay       │ │
│  ├──────────┼───────────────┼─────────────────────┼──────────────┼──────────────┤ │
│  │10.Pred.  │ PREDICTION    │ CONSUMER            │ after Know   │ no-model     │ │
│  │          │               │                     │              │ check        │ │
│  │          │               │                     │              │ knowledge    │ │
│  │          │               │                     │              │ replay       │ │
│  └──────────┴───────────────┴─────────────────────┴──────────────┴──────────────┘ │
└───────────────────────────────────────────────────────────────────────────────────┘
```

### 7.2 Snapshot W/OD Field Classification

| Snapshot | W (Stored Frozen) | OD (On-Demand, Deterministic) | Source |
|----------|-------------------|-------------------------------|--------|
| Market | ts, symbol, tf, OHLCV, taker_buy_ratio, taker_sell_volume, data_status, gap_flag, wib_iso | — | MARKET |
| Truth | close, st, st_canon, stDir, color, atr, ema, ema12, ema26, macd, macd_signal, macd_hist, rsi, wpr, dist, distAtr, *_status | — | TRUTH |
| Structure | cage{status,upper,lower,pp,rangeAtr,breakout}, ladder, nearest{sup,res}, cluster5d, active_line, slope, pending_wave, last_wave_structure | dist_ceiling, dist_floor, ceiling_floor_ratio, dist_delta | STRUCTURE |
| Evidence | dir_bus{ema,oi,oi_status,oi_source,vd,mtf_long,mtf_short}, exit_bus{rsi,wpr,macd_hist,hold,vel,acc}, mtf, max_score, data_quality | — | EVIDENCE |
| Clone | per_clone{clone_id,bias,observation,open_position,grid_fills[]} | — | CLONE |
| Trade | markers[{kind,clone,side,reason,entry,exit,gross,fee,slip,net,result,mae,mfe,hold}], running_per_clone | — | SIM |
| Statistics | per_clone{sample,win_rate_net,expectancy_net,pf,mae,mfe,fee_drag,wrong_rate,coverage}, distance_health_hist, fee_safe_margin_dist, wrong_entry_dist | all fields (from Trade) | STATISTICS |
| Knowledge | academy_artifacts[], oracle_match, hivemind{intelligence_score,dominant_bias,*_boost,evidence_adj}, darwin_proposals[], librarian_events[], cermin | — | KNOWLEDGE |
| Benchmark | param, base, cand, folds, totals, gates{G1..G5}, per_fold[], verdict | trigger-only (absent per candle) | BENCHMARK |
| Prediction | intelligence_score, dominant_bias, empirical_win_rate_per_clone, similarity_score, pattern_boost, oracle_boost | empirical_win_rate (from Academy) | PREDICTION |

### 7.3 Snapshot Lifecycle

```
PRODUCE → FREEZE → STORE → CONSUME → REPLAY

Produce: pada tahap pipeline yang sah (satu sumber per besaran)
Freeze:  Object.freeze + checksum + dependencies=[candle_id, config_version]
Store:   append-only (IndexedDB cold/warm); index by type+ts & config+ts
Consume: read-only oleh lapisan hilir & Consumer/Visualization
Replay:  baca urutan snapshot; Re-validate = checksum+lineage saat load

FINAL only from candle CLOSED; PROVISIONAL does not produce final snapshot
Benchmark Snapshot ABSENT on regular closed candles (on-demand only)
Prediction Snapshot FORBIDDEN to contain predictive model output
Adding/removing snapshot fields = amandemen §3 (constitution_version baru)
```

### 7.4 Snapshot Dependency Classification

| Snapshot | Upstream | Downstream | Mandatory | Optional | Forbidden |
|----------|----------|------------|-----------|----------|-----------|
| Market | TRUTH | — (data source) | YES | NO | PROVISIONAL→final |
| Truth | STRUCTURE, EVIDENCE | MARKET | YES (VALID/WARMUP) | NO | padding, NULL→0 |
| Structure | CLONE, GRID | TRUTH | YES (HUKUM CAGE) | NO | padded wave |
| Evidence | CLONE, HIVEMIND | TRUTH, MARKET, STRUCTURE | YES (3 buses) | NO | W%R→entry |
| Clone | STATISTICS | STRUCTURE, EVIDENCE, TRUTH | YES (3 obs/candle) | NO | skip no-trade |
| Trade | STATISTICS | SIM, CLONE | YES (after-fee) | NO | TP>SL se-candle |
| Statistics | KNOWLEDGE | TRADE | YES (CUKUP≥30) | NO | <ambang→confident |
| Knowledge | PREDICTION, GOVERNANCE | STATISTICS, all snapshots | YES (unidirectional) | NO | ML, loop back |
| Benchmark | GOVERNANCE | SIMULATION | NO | YES (ON-DEMAND) | per-candle |
| Prediction | CONSUMER | KNOWLEDGE | YES (no-model) | NO | forecast model |

---

## 8. SQLITE DEPENDENCY

### 8.1 Table-to-Layer Mapping

```
┌───────────────────────────────────────────────────────────────────────────────────┐
│                         SQLite TABLE → PIPELINE LAYER MAPPING                        │
│                                                                                   │
│  LAYER 0 — CORE METADATA                                                          │
│  ┌──────────────────────────────────────────────────────────────────────────┐    │
│  │ app_sessions      │ session registry (build/sim/replay/benchmark/...)      │    │
│  │ symbols           │ asset definitions (symbol, tick_size, step_size)       │    │
│  │ timeframes        │ timeframe dictionary (1m, 3m, 5m, ..., 1d)            │    │
│  │ pipeline_runs     │ run tracking (collector/sim/replay/benchmark/...)      │    │
│  └──────────────────────────────────────────────────────────────────────────┘    │
│                                                                                   │
│  LAYER 1 — MARKET LAYER                                                           │
│  ┌──────────────────────────────────────────────────────────────────────────┐    │
│  │ market_candles    │ OHLCV + taker_volume + gap_flag + data_status          │    │
│  │ market_metadata   │ key-value metadata per symbol/tf/ts                    │    │
│  │ open_interest_series│ OI + OI_delta + source + status                      │    │
│  │ market_gaps       │ gap detection records                                  │    │
│  └──────────────────────────────────────────────────────────────────────────┘    │
│                                                                                   │
│  LAYER 2 — TRUTH LAYER                                                            │
│  ┌──────────────────────────────────────────────────────────────────────────┐    │
│  │ truth_snapshots   │ st, ATR, EMA, MACD, RSI, W%R, dist, distAtr, OI      │    │
│  │ truth_cache       │ key-value cache per truth snapshot                     │    │
│  └──────────────────────────────────────────────────────────────────────────┘    │
│                                                                                   │
│  LAYER 3 — STRUCTURE LAYER                                                        │
│  ┌──────────────────────────────────────────────────────────────────────────┐    │
│  │ structure_snapshots│ cage, wave, ladder, nearest, pp, dist_ceiling/floor   │    │
│  │ wave_history      │ wave line composition per structure snapshot           │    │
│  │ cage_history      │ cage version history per structure snapshot            │    │
│  └──────────────────────────────────────────────────────────────────────────┘    │
│                                                                                   │
│  LAYER 4 — EVIDENCE LAYER                                                         │
│  ┌──────────────────────────────────────────────────────────────────────────┐    │
│  │ evidence_snapshots│ dir_bus, exit_bus, correction_bus (JSON), max_score    │    │
│  └──────────────────────────────────────────────────────────────────────────┘    │
│                                                                                   │
│  LAYER 5 — CLONE LAYER                                                            │
│  ┌──────────────────────────────────────────────────────────────────────────┐    │
│  │ clones            │ clone registry (LONG/SHORT/GRID per session/symbol)    │    │
│  │ clone_observations│ observation per clone per candle (entry_legal, etc.)   │    │
│  └──────────────────────────────────────────────────────────────────────────┘    │
│                                                                                   │
│  LAYER 6 — TRADE LAYER                                                            │
│  ┌──────────────────────────────────────────────────────────────────────────┐    │
│  │ trade_markers     │ ENTRY/EXIT/PARTIAL/BREAKEVEN/TRAILING/HOLD/PASS/      │    │
│  │                   │ NO_TRADE with gross/fee/slip/net/result/MAE/MFE       │    │
│  └──────────────────────────────────────────────────────────────────────────┘    │
│                                                                                   │
│  LAYER 7 — POSITION LAYER                                                         │
│  ┌──────────────────────────────────────────────────────────────────────────┐    │
│  │ positions         │ position state (entry/exit/sl/tp/trail/liquidation)    │    │
│  │ position_timeline │ event timeline per position (MAE/MFE/hold)             │    │
│  └──────────────────────────────────────────────────────────────────────────┘    │
│                                                                                   │
│  LAYER 8 — STATISTICS LAYER                                                       │
│  ┌──────────────────────────────────────────────────────────────────────────┐    │
│  │ trade_statistics  │ win_rate, expectancy, PF, MAE, MFE, fee_drag,          │    │
│  │                   │ wrong_rate, coverage, distance_health                  │    │
│  │ market_statistics │ phase, wave_structure, pp, dist_bucket, hit_counts     │    │
│  └──────────────────────────────────────────────────────────────────────────┘    │
│                                                                                   │
│  LAYER 9 — BAG (Behavior Acquisition) LAYER                                        │
│  ┌──────────────────────────────────────────────────────────────────────────┐    │
│  │ bag_artifacts     │ behavior/market/entry/exit/risk/knowledge bags         │    │
│  │ bag_patterns      │ ranked patterns per bag                               │    │
│  │ bag_compression   │ compression metrics per bag                           │    │
│  └──────────────────────────────────────────────────────────────────────────┘    │
│                                                                                   │
│  LAYER 10 — KNOWLEDGE LAYER                                                       │
│  ┌──────────────────────────────────────────────────────────────────────────┐    │
│  │ knowledge_artifacts│ ACADEMY/RIVER/ORACLE/HIVEMIND/DARWIN/LIBRARIAN/CERMIN │    │
│  └──────────────────────────────────────────────────────────────────────────┘    │
│                                                                                   │
│  LAYER 11 — PREDICTION LAYER                                                      │
│  ┌──────────────────────────────────────────────────────────────────────────┐    │
│  │ predictions       │ predicted_side, confidence, similarity_score, etc.     │    │
│  │ prediction_results│ actual vs predicted outcomes                          │    │
│  └──────────────────────────────────────────────────────────────────────────┘    │
│                                                                                   │
│  LAYER 12 — GOVERNANCE LAYER                                                      │
│  ┌──────────────────────────────────────────────────────────────────────────┐    │
│  │ governance_proposals│ param_name, proposed_value, status, bounded_check    │    │
│  │ governance_logs   │ event log per proposal/session                        │    │
│  │ rollback_logs     │ rollback records                                      │    │
│  └──────────────────────────────────────────────────────────────────────────┘    │
│                                                                                   │
│  LAYER 13 — REPLAY LAYER                                                          │
│  ┌──────────────────────────────────────────────────────────────────────────┐    │
│  │ replay_sessions   │ candle/snapshot/trade/clone/knowledge/governance       │    │
│  │ replay_frames     │ per-frame data (frame_index, ts, frame_kind, JSON)     │    │
│  └──────────────────────────────────────────────────────────────────────────┘    │
│                                                                                   │
│  LAYER 14 — BENCHMARK LAYER                                                       │
│  ┌──────────────────────────────────────────────────────────────────────────┐    │
│  │ benchmark_runs    │ wasit/walk_forward/clone/trade/market runs            │    │
│  │ benchmark_cases   │ per-case input/output/pass_flag                       │    │
│  └──────────────────────────────────────────────────────────────────────────┘    │
│                                                                                   │
│  LAYER 15 — AUDIT LAYER                                                           │
│  ┌──────────────────────────────────────────────────────────────────────────┐    │
│  │ audit_logs        │ CRITICAL/HIGH/MEDIUM/LOW/INFO per domain              │    │
│  │ audit_issues      │ per-audit issue details                               │    │
│  └──────────────────────────────────────────────────────────────────────────┘    │
│                                                                                   │
│  LAYER 16 — SETTINGS / DICTIONARY / UTILITY                                       │
│  ┌──────────────────────────────────────────────────────────────────────────┐    │
│  │ app_settings      │ key-value app settings (schema_version, etc.)          │    │
│  │ domain_dictionary │ domain registry (market→15 layers)                     │    │
│  │ purge_jobs        │ deletion/purge job tracking                            │    │
│  │ row_lifecycle     │ generic row lifecycle tracking                         │    │
│  └──────────────────────────────────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────────────────────────────────┘
```

### 8.2 Foreign Key Dependency Chain

```
app_sessions ───────────────────────────────────────────────────────────────────────┐
  │                                                                                 │
  ├──► market_candles (session_id → app_sessions)                                   │
  │      │                                                                          │
  │      ├──► truth_snapshots (candle_id → market_candles)                          │
  │      │      │                                                                   │
  │      │      ├──► structure_snapshots (truth_id → truth_snapshots,               │
  │      │      │        candle_id → market_candles)                                │
  │      │      │      │                                                            │
  │      │      │      ├──► evidence_snapshots (truth_id → truth_snapshots,         │
  │      │      │      │        structure_id → structure_snapshots,                 │
  │      │      │      │        candle_id → market_candles)                         │
  │      │      │      │      │                                                     │
  │      │      │      │      ├──► clone_observations (evidence_id → evidence)      │
  │      │      │      │      │      │                                              │
  │      │      │      │      │      ├──► trade_markers (clone_id → clones,        │
  │      │      │      │      │      │        candle_id → market_candles)           │
  │      │      │      │      │      │      │                                       │
  │      │      │      │      │      │      ├──► positions (entry_marker_id →       │
  │      │      │      │      │      │      │        trade_markers,                 │
  │      │      │      │      │      │      │        exit_marker_id →               │
  │      │      │      │      │      │      │        trade_markers,                 │
  │      │      │      │      │      │      │        clone_id → clones)             │
  │      │      │      │      │      │      │      │                                │
  │      │      │      │      │      │      │      ├──► position_timeline           │
  │      │      │      │      │      │      │      │        (position_id →          │
  │      │      │      │      │      │      │      │         positions)             │
  │      │      │      │      │      │      │      │                                │
  │      │      │      │      │      │      │      └──► trade_statistics            │
  │      │      │      │      │      │      │              (clone_id → clones)      │
  │      │      │      │      │      │      │                │                      │
  │      │      │      │      │      │      │                ├──► bag_artifacts      │
  │      │      │      │      │      │      │                │        (stat_id →     │
  │      │      │      │      │      │      │                │         trade_stats)  │
  │      │      │      │      │      │      │                │         │             │
  │      │      │      │      │      │      │                │         ├──► bag_     │
  │      │      │      │      │      │      │                │         │   patterns  │
  │      │      │      │      │      │      │                │         │             │
  │      │      │      │      │      │      │                │         └──► bag_     │
  │      │      │      │      │      │      │                │             compress  │
  │      │      │      │      │      │      │                │                        │
  │      │      │      │      │      │      │                └──► knowledge_artifacts │
  │      │      │      │      │      │      │                        (bag_id, stat_id)│
  │      │      │      │      │      │      │                          │              │
  │      │      │      │      │      │      │                          ├──► predict.  │
  │      │      │      │      │      │      │                          │   (know_id)  │
  │      │      │      │      │      │      │                          │     │        │
  │      │      │      │      │      │      │                          │     └──►     │
  │      │      │      │      │      │      │                          │   pred_res.  │
  │      │      │      │      │      │      │                          │              │
  │      │      │      │      │      │      │                          └──► govern.   │
  │      │      │      │      │      │      │                              proposals  │
  │      │      │      │      │      │      │                                │        │
  │      │      │      │      │      │      │                                ├──► gov │
  │      │      │      │      │      │      │                                │   logs │
  │      │      │      │      │      │      │                                │        │
  │      │      │      │      │      │      │                                └──► roll│
  │      │      │      │      │      │      │                                   back  │
  │      │      │      │      │      │      │                                          │
  │      │      │      │      │      │      └──► market_statistics                    │
  │      │      │      │      │      │                                                 │
  │      │      │      │      │      └──► clones (clone registry per session)          │
  │      │      │      │      │                                                         │
  │      │      │      │      └──► open_interest_series                                │
  │      │      │      │                                                                │
  │      │      │      └──► wave_history, cage_history                                  │
  │      │      │                                                                       │
  │      │      └──► truth_cache                                                       │
  │      │                                                                              │
  │      └──► market_metadata, market_gaps                                             │
  │                                                                                     │
  ├──► pipeline_runs (session_id → app_sessions)                                       │
  │      └──► audit_logs (run_id → pipeline_runs)                                      │
  │                                                                                     │
  ├──► replay_sessions (session_id → app_sessions)                                     │
  │      └──► replay_frames                                                            │
  │                                                                                     │
  └──► benchmark_runs (session_id → app_sessions)                                      │
         └──► benchmark_cases                                                           │
```

### 8.3 Complete Dependency Chain (Linear)

```
app_sessions
  → symbols
  → timeframes
  → market_candles
    → truth_snapshots
      → structure_snapshots
        → evidence_snapshots
          → clone_observations
            → trade_markers
              → positions
                → position_timeline
                → trade_statistics
                  → bag_artifacts
                    → bag_patterns
                    → bag_compression
                  → knowledge_artifacts
                    → predictions
                      → prediction_results
                    → governance_proposals
                      → governance_logs
                      → rollback_logs
  → pipeline_runs
    → audit_logs
      → audit_issues
  → replay_sessions
    → replay_frames
  → benchmark_runs
    → benchmark_cases
```

### 8.4 SQLite Dependency Classification

| Table | Upstream | Downstream | Mandatory FK | Optional FK | Forbidden |
|-------|----------|------------|-------------|-------------|-----------|
| app_sessions | all | — | NO (root) | NO | — |
| market_candles | truth_snapshots | app_sessions | session_id | run_id | — |
| truth_snapshots | structure_snapshots, evidence_snapshots | market_candles | candle_id | — | — |
| structure_snapshots | evidence_snapshots | truth_snapshots, market_candles | truth_id, candle_id | — | — |
| evidence_snapshots | clone_observations | truth_snapshots, structure_snapshots, market_candles | truth_id, structure_id, candle_id | — | — |
| clone_observations | trade_markers (via clones) | evidence_snapshots, clones | evidence_id, clone_id | — | — |
| trade_markers | positions, trade_statistics | clones, market_candles | clone_id, candle_id | — | — |
| positions | position_timeline, trade_markers (exit) | clones, trade_markers (entry) | clone_id | entry_marker_id, exit_marker_id | — |
| trade_statistics | bag_artifacts, knowledge_artifacts | clones | — | clone_id | — |
| knowledge_artifacts | predictions, governance_proposals | bag_artifacts, trade_statistics | — | bag_id, stat_id | — |
| predictions | prediction_results | knowledge_artifacts | — | knowledge_id | — |
| governance_proposals | governance_logs, rollback_logs | knowledge_artifacts | — | knowledge_id | — |

---

## 9. VIEW DEPENDENCY

### 9.1 Twelve Visualization Components

```
┌───────────────────────────────────────────────────────────────────────────────────┐
│                         12 VISUALIZATION COMPONENTS                                 │
│                                                                                   │
│  ┌─────────────────────────┬──────────────────────────────────────────────────┐  │
│  │      COMPONENT           │                  DATA SOURCES                     │  │
│  ├─────────────────────────┼──────────────────────────────────────────────────┤  │
│  │ 1. Geometry Viewer       │ truth_snapshot (st, stDir, color, ATR, EMA),      │  │
│  │    (VIEW.drawGeom)       │ structure_snapshot (cage, wave, pp, dist),        │  │
│  │                          │ market_candles (OHLCV), trade_markers (entry/exit)│  │
│  │                          │ Upstream: TRUTH, STRUCTURE, MARKET, TRADE         │  │
│  │                          │ Downstream: human                                 │  │
│  ├─────────────────────────┼──────────────────────────────────────────────────┤  │
│  │ 2. Clone Viewer          │ clone_observations (per LONG/SHORT/GRID),         │  │
│  │    (VIEW.renderClone)    │ positions (open state, MAE/MFE),                  │  │
│  │                          │ clone_snapshot (observation cards)                │  │
│  │                          │ Upstream: CLONE, POSITION                         │  │
│  │                          │ Downstream: human                                 │  │
│  ├─────────────────────────┼──────────────────────────────────────────────────┤  │
│  │ 3. Trade Viewer          │ trade_markers (history table),                    │  │
│  │    (VIEW.renderTrade,    │ trade_statistics (win_rate, expectancy, PF),      │  │
│  │     VIEW.drawEq)         │ positions (equity curve), trade_snapshot          │  │
│  │                          │ Upstream: TRADE, STATISTICS, POSITION             │  │
│  │                          │ Downstream: human, CSV export                     │  │
│  ├─────────────────────────┼──────────────────────────────────────────────────┤  │
│  │ 4. Replay Viewer         │ replay_sessions (6 types),                        │  │
│  │    (VIEW.renderReplay,   │ replay_frames (per-frame data),                   │  │
│  │     VIEW.step, VIEW.play)│ all 10 snapshots (sequential read)                │  │
│  │                          │ Upstream: REPLAY, all snapshots                   │  │
│  │                          │ Downstream: human                                 │  │
│  ├─────────────────────────┼──────────────────────────────────────────────────┤  │
│  │ 5. Knowledge Viewer      │ knowledge_artifacts (Academy table),              │  │
│  │    (VIEW.renderKnow)     │ oracle_match (similarity display),                │  │
│  │                          │ hivemind (understanding), CERMIN (calibration),   │  │
│  │                          │ librarian_events (lifecycle),                     │  │
│  │                          │ darwin_proposals                                  │  │
│  │                          │ Upstream: KNOWLEDGE                               │  │
│  │                          │ Downstream: human                                 │  │
│  ├─────────────────────────┼──────────────────────────────────────────────────┤  │
│  │ 6. Panel Renderer        │ truth_snapshot (indicator gauges),                │  │
│  │    (VIEW.renderPanels)   │ structure_snapshot (wave, cage, versioning),      │  │
│  │                          │ evidence_snapshot (direction, exit, correction),  │  │
│  │                          │ market_candles (volume, OI)                       │  │
│  │                          │ Upstream: TRUTH, STRUCTURE, EVIDENCE, MARKET      │  │
│  │                          │ Downstream: human                                 │  │
│  ├─────────────────────────┼──────────────────────────────────────────────────┤  │
│  │ 7. Governance UI         │ governance_proposals (list),                      │  │
│  │    (VIEW.renderGov)      │ governance_logs (timeline),                       │  │
│  │                          │ rollback_logs, benchmark_runs (WASIT results)     │  │
│  │                          │ Upstream: GOVERNANCE, BENCHMARK                   │  │
│  │                          │ Downstream: human (approve/reject)                │  │
│  ├─────────────────────────┼──────────────────────────────────────────────────┤  │
│  │ 8. Simulation UI         │ simulation engine state,                          │  │
│  │    (VIEW.renderSim)      │ simulation types (historical/live/strategy/clone),│  │
│  │                          │ determinismHash                                   │  │
│  │                          │ Upstream: SIMULATION                              │  │
│  │                          │ Downstream: human                                 │  │
│  ├─────────────────────────┼──────────────────────────────────────────────────┤  │
│  │ 9. Prediction Display    │ prediction_snapshot (intelligence_score,          │  │
│  │    (VIEW.renderPred)     │   dominant_bias, empirical_win_rate,              │  │
│  │                          │   similarity_score, cermin_error)                 │  │
│  │                          │ Upstream: PREDICTION                              │  │
│  │                          │ Downstream: human, CONSUMER                       │  │
│  ├─────────────────────────┼──────────────────────────────────────────────────┤  │
│  │ 10. Consumer Display     │ CONSUMER state (fundEval, vetoGate),              │  │
│  │     (VIEW.renderConsumer)│ intentBuilder (trade intent preview),             │  │
│  │                          │ liveAdapter status, exportCSV                     │  │
│  │                          │ Upstream: CONSUMER                                │  │
│  │                          │ Downstream: human                                 │  │
│  ├─────────────────────────┼──────────────────────────────────────────────────┤  │
│  │ 11. Audit Display        │ audit_logs (self-test results),                   │  │
│  │     (VIEW.renderAudit)   │ audit_issues (per-domain audit),                  │  │
│  │                          │ fingerprint (deterministic system hash)           │  │
│  │                          │ Upstream: AUDIT                                   │  │
│  │                          │ Downstream: human                                 │  │
│  ├─────────────────────────┼──────────────────────────────────────────────────┤  │
│  │ 12. Final Validation     │ FINAL_VALIDATION results (12-domain check),       │  │
│  │     Display              │ constitution check, namespace check,              │  │
│  │     (VIEW.renderFinal    │ pipeline check, truth check, clone check,          │  │
│  │      Validation)         │ trading check, knowledge check, governance check  │  │
│  │                          │ Upstream: FINAL_VALIDATION                        │  │
│  │                          │ Downstream: human                                 │  │
│  └─────────────────────────┴──────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────────────────────┘
```

### 9.2 View Component Dependency Classification

| Component | Upstream (data) | Downstream (consumer) | Mandatory | Optional | Forbidden |
|-----------|----------------|----------------------|-----------|----------|-----------|
| Geometry Viewer | TRUTH, STRUCTURE, MARKET, TRADE | human | YES | NO | compute logic |
| Clone Viewer | CLONE, POSITION | human | YES (3 clones) | NO | compute logic |
| Trade Viewer | TRADE, STATISTICS, POSITION | human, CSV | YES | NO | compute logic |
| Replay Viewer | REPLAY, all snapshots | human | YES (6 types) | NO | compute logic |
| Knowledge Viewer | KNOWLEDGE | human | YES | NO | compute logic |
| Panel Renderer | TRUTH, STRUCTURE, EVIDENCE, MARKET | human | YES | NO | mock values |
| Governance UI | GOVERNANCE, BENCHMARK | human (approve/reject) | YES | NO | auto-execute |
| Simulation UI | SIMULATION | human | YES | NO | — |
| Prediction Display | PREDICTION | human, CONSUMER | YES (no-model) | NO | forecast |
| Consumer Display | CONSUMER | human | YES | NO | live default on |
| Audit Display | AUDIT | human | YES | NO | — |
| Final Validation | FINAL_VALIDATION | human | YES | NO | — |

### 9.3 UI Contract (Anti-Mock)

```
UI MEMBACA card via API internal (query IndexedDB)
UI TIDAK menghitung logika market
UI TIDAK menyimpan kebenaran di localStorage (hanya preferensi)
Kosong = N/A (bukan nilai placeholder/hardcode)
Tombol = perintah ke engine main-thread
Live-adapter = DISABLED DEFAULT
```

---

## 10. WORKER DEPENDENCY

### 10.1 Five Worker Types + Main Thread

```
┌───────────────────────────────────────────────────────────────────────────────────┐
│                         THREAD TOPOLOGY — 5 WORKER TYPES                            │
│                                                                                   │
│  ┌──────────────────────────────────────────────────────────────────────────┐    │
│  │                         MAIN THREAD (hot)                                  │    │
│  │                                                                           │    │
│  │  Tugas:                                                                   │    │
│  │  • BOOT — establish system physics, load config, init workspace           │    │
│  │  • Server-less event loop — drive pipeline per candle                     │    │
│  │  • Truth/Structure/Evidence — per-candle SEQUENTIAL (state contiguous)    │    │
│  │  • Clone (LONG/SHORT/GRID) — per-candle SEQUENTIAL                        │    │
│  │  • IndexedDB Writer — SERIAL (single writer, nol race)                    │    │
│  │  • UI Render — all 12 visualization components                            │    │
│  │  • Clock WIB — display only                                               │    │
│  │                                                                           │    │
│  │  Upstream: — (root thread)                                                │    │
│  │  Downstream: all workers (via postMessage), IndexedDB (write), UI (render)│    │
│  │  Mandatory: YES (state contiguous, writer serial)                         │    │
│  │  Forbidden: setInterval pemutar candle di idle                            │    │
│  └──────────────────────────────────────────────────────────────────────────┘    │
│                                                                                   │
│  ┌──────────────────────────────────────────────────────────────────────────┐    │
│  │                    Worker·Data (cold, dies after batch)                    │    │
│  │                                                                           │    │
│  │  Tugas:                                                                   │    │
│  │  • Bootstrap batch — load historical fixture data                         │    │
│  │  • Derived-TF aggregation — aggregate 1m → higher TF (3m, 5m, ..., 1d)   │    │
│  │  • Gap-repair — detect and repair time gaps                               │    │
│  │  • I/O-bound — fetch fixture via network                                  │    │
│  │                                                                           │    │
│  │  Upstream: MAIN (config, symbol, tf)                                      │    │
│  │  Downstream: MAIN (market_candles via postMessage)                        │    │
│  │  Mandatory: NO (optional for bootstrap)                                   │    │
│  │  Optional: YES (batch data loading)                                       │    │
│  │  Forbidden: IndexedDB write langsung, per-candle processing               │    │
│  └──────────────────────────────────────────────────────────────────────────┘    │
│                                                                                   │
│  ┌──────────────────────────────────────────────────────────────────────────┐    │
│  │                 Worker·Knowledge (cold, dies after batch)                  │    │
│  │                                                                           │    │
│  │  Tugas:                                                                   │    │
│  │  • Academy batch — compute empirical win_rate per bucket (4-dim)          │    │
│  │  • Oracle similarity — euclidean match against historical vectors         │    │
│  │  • Darwin proposal — generate parameter mutation proposals                │    │
│  │  • Librarian evaluation — lifecycle status updates                        │    │
│  │  • CPU-bound — infrequent computation                                     │    │
│  │                                                                           │    │
│  │  Upstream: MAIN (markers, snapshots via postMessage)                      │    │
│  │  Downstream: MAIN (knowledge_artifacts via postMessage)                   │    │
│  │  Mandatory: NO (can run on main for small datasets)                       │    │
│  │  Optional: YES (parallel for large datasets)                              │    │
│  │  Forbidden: IndexedDB write langsung, read Truth/Clone, loop back         │    │
│  └──────────────────────────────────────────────────────────────────────────┘    │
│                                                                                   │
│  ┌──────────────────────────────────────────────────────────────────────────┐    │
│  │               Worker·Benchmark (cold, parallel sub-tasks)                  │    │
│  │                                                                           │    │
│  │  Tugas:                                                                   │    │
│  │  • WASIT walk-forward — base vs candidate PARALLEL (2 sub-tasks)          │    │
│  │  • 5-gate evaluation — G1 aggregate, G2 consistency, G3 improvement,      │    │
│  │    G4 significance, G5 stability                                          │    │
│  │  • Fold metrics — per-fold statistics aggregation                         │    │
│  │  • Multi-core utilization — memanfaatkan multi-core browser               │    │
│  │                                                                           │    │
│  │  Upstream: MAIN (2 configs + replay data via postMessage)                 │    │
│  │  Downstream: MAIN (benchmark_snapshot via postMessage)                    │    │
│  │  Mandatory: NO (can run sequentially)                                     │    │
│  │  Optional: YES (parallel for speed)                                       │    │
│  │  Forbidden: IndexedDB write langsung, non-deterministic computation       │    │
│  └──────────────────────────────────────────────────────────────────────────┘    │
│                                                                                   │
│  ┌──────────────────────────────────────────────────────────────────────────┐    │
│  │              Worker·Replay (cold, parallel per-symbol)                     │    │
│  │                                                                           │    │
│  │  Tugas:                                                                   │    │
│  │  • Replay panjang — per-symbol parallel playback                          │    │
│  │  • Independent antar-symbol — no cross-symbol state                       │    │
│  │  • 6 replay types — candle/snapshot/trade/clone/knowledge/governance      │    │
│  │                                                                           │    │
│  │  Upstream: MAIN (replay config + snapshots via postMessage)               │    │
│  │  Downstream: MAIN (replay_frames via postMessage)                         │    │
│  │  Mandatory: NO (can run on main)                                          │    │
│  │  Optional: YES (parallel multi-symbol replay)                             │    │
│  │  Forbidden: IndexedDB write langsung                                      │    │
│  └──────────────────────────────────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────────────────────────────────┘
```

### 10.2 Thread Safety Rules

```
┌───────────────────────────────────────────────────────────────────────────────────┐
│                         THREAD SAFETY — MANDATORY RULES                              │
│                                                                                   │
│  ╔═══════════════════════════════════════════════════════════════════════════════╗ │
│  ║                           FORBIDDEN OPERATIONS                                ║ │
│  ╠═══════════════════════════════════════════════════════════════════════════════╣ │
│  ║                                                                               ║ │
│  ║  1. WORKER MUST NOT write IndexedDB directly                                  ║ │
│  ║     → All writes go through main thread serial writer                         ║ │
│  ║     → Worker sends results via postMessage, main persists                     ║ │
│  ║     → Violation = BUILD STOP (LAW-MASTER-17)                                  ║ │
│  ║                                                                               ║ │
│  ║  2. Truth/Structure/Evidence/Clone per-candle for one symbol                  ║ │
│  ║     MUST be SEQUENTIAL on main thread                                         ║ │
│  ║     → State is contiguous (EMA, ATR, position state)                          ║ │
│  ║     → Parallelizing per-candle = breaks state continuity                      ║ │
│  ║     → Violation = BUILD STOP (state corruption)                               ║ │
│  ║                                                                               ║ │
│  ║  3. Worker MUST NOT use Math.random() in logic                                ║ │
│  ║     → PRNG Mulberry32 seeded ts+config_version only                           ║ │
│  ║     → Violation = non-determinism (LAW-MASTER-01)                             ║ │
│  ║                                                                               ║ │
│  ║  4. Worker MUST NOT use Date.now() in logic                                   ║ │
│  ║     → Timestamps from candle data only                                        ║ │
│  ║     → Violation = non-determinism (LAW-MASTER-01)                             ║ │
│  ║                                                                               ║ │
│  ║  5. Worker MUST NOT read/write SharedArrayBuffer for shared state             ║ │
│  ║     → SharedArrayBuffer/Atomics only for signaling                            ║ │
│  ║     → No shared mutable state across threads                                  ║ │
│  ║     → Violation = race condition (LAW-MASTER-17)                              ║ │
│  ║                                                                               ║ │
│  ║  6. Worker MUST die after completion (RAM returned)                           ║ │
│  ║     → No persistent workers                                                   ║ │
│  ║     → No setInterval in workers                                               ║ │
│  ║     → Violation = resource leak                                               ║ │
│  ║                                                                               ║ │
│  ╚═══════════════════════════════════════════════════════════════════════════════╝ │
│                                                                                   │
│  ╔═══════════════════════════════════════════════════════════════════════════════╗ │
│  ║                         ALLOWED PARALLELISM                                    ║ │
│  ╠═══════════════════════════════════════════════════════════════════════════════╣ │
│  ║                                                                               ║ │
│  ║  1. Antar-simbol — each symbol can process in parallel                        ║ │
│  ║  2. Base-vs-Candidate — WASIT walk-forward parallel (2 sub-tasks)             ║ │
│  ║  3. Batch knowledge — Academy/Oracle/Darwin/Librarian as batch jobs           ║ │
│  ║  4. Data loading — bootstrap batch data loading via Worker·Data               ║ │
│  ║                                                                               ║ │
│  ╚═══════════════════════════════════════════════════════════════════════════════╝ │
└───────────────────────────────────────────────────────────────────────────────────┘
```

### 10.3 Worker Communication Flow

```
┌───────────────────────────────────────────────────────────────────────────────────┐
│                         WORKER COMMUNICATION FLOW                                    │
│                                                                                   │
│  ┌──────────┐                                                                     │
│  │   MAIN   │                                                                     │
│  │  THREAD  │                                                                     │
│  └────┬─────┘                                                                     │
│       │                                                                           │
│       │  postMessage({job, config, data})                                         │
│       │                                                                           │
│       ├──────────────────────────────────────────┐                                │
│       │                                          │                                │
│       ▼                                          ▼                                │
│  ┌──────────┐                              ┌──────────┐                           │
│  │ Worker·  │                              │ Worker·  │                           │
│  │ Data     │                              │Knowledge │                           │
│  │          │                              │          │                           │
│  │ bootstrap│                              │ Academy  │                           │
│  │ derived  │                              │ Oracle   │                           │
│  │ TF agg   │                              │ Darwin   │                           │
│  │ gap fix  │                              │Librarian │                           │
│  └────┬─────┘                              └────┬─────┘                           │
│       │                                          │                                │
│       │  postMessage({result, data})              │  postMessage({result, data})   │
│       │                                          │                                │
│       ▼                                          ▼                                │
│  ┌──────────┐                              ┌──────────┐                           │
│  │ Worker·  │                              │ Worker·  │                           │
│  │Benchmark │                              │ Replay   │                           │
│  │          │                              │          │                           │
│  │ WASIT    │                              │ per-     │                           │
│  │ walk-    │                              │ symbol   │                           │
│  │ forward  │                              │ parallel │                           │
│  │ base vs  │                              │ 6 types  │                           │
│  │ candidate│                              │          │                           │
│  └────┬─────┘                              └────┬─────┘                           │
│       │                                          │                                │
│       │  postMessage({result, data})              │  postMessage({result, data})   │
│       │                                          │                                │
│       └──────────────────────────────────────────┘                                │
│                          │                                                         │
│                          ▼                                                         │
│                    ┌──────────┐                                                    │
│                    │   MAIN   │                                                    │
│                    │  THREAD  │                                                    │
│                    │          │                                                    │
│                    │ receives │                                                    │
│                    │ results  │                                                    │
│                    │ persists │                                                    │
│                    │ via      │                                                    │
│                    │ IndexedDB│                                                    │
│                    │ (serial  │                                                    │
│                    │  writer) │                                                    │
│                    └──────────┘                                                    │
│                                                                                   │
│  Rule: ALL IndexedDB writes go through MAIN thread serial writer                   │
│  Rule: Workers send results via postMessage, never write IndexedDB directly        │
│  Rule: Workers are COLD — they die after completing their job                      │
└───────────────────────────────────────────────────────────────────────────────────┘
```

### 10.4 Worker Dependency Classification

| Worker | Upstream | Downstream | Mandatory | Optional | Forbidden |
|--------|----------|------------|-----------|----------|-----------|
| Main Thread | — | all workers, IndexedDB, UI | YES | NO | setInterval idle, race |
| Worker·Data | MAIN (config) | MAIN (market_candles) | NO | YES (bootstrap) | IndexedDB write, per-candle |
| Worker·Knowledge | MAIN (markers, snapshots) | MAIN (knowledge_artifacts) | NO | YES (batch) | IndexedDB write, read Truth/Clone |
| Worker·Benchmark | MAIN (2 configs, replay) | MAIN (benchmark_snapshot) | NO | YES (parallel) | IndexedDB write, non-deterministic |
| Worker·Replay | MAIN (config, snapshots) | MAIN (replay_frames) | NO | YES (multi-symbol) | IndexedDB write |

### 10.5 Resource Governor Rules

```
┌───────────────────────────────────────────────────────────────────────────────────┐
│                         RESOURCE GOVERNOR THRESHOLDS                                │
│                                                                                   │
│  70% RAM:  flush warm + gc + kill idle workers                                    │
│  85% RAM:  pause spawn new workers (hot path continues)                           │
│  95% RAM:  degraded — skip evidence opsional, reject new entries                  │
│                                                                                   │
│  No setInterval pemutar candle di idle                                             │
│  System driven by request/replay (hemat saat tab pasif)                            │
│  performance.memory (bila tersedia) + heuristic ukuran store                      │
└───────────────────────────────────────────────────────────────────────────────────┘
```

---

## APPENDIX: BUILD STOP RULE (15 Conditions)

```
┌───────────────────────────────────────────────────────────────────────────────────┐
│                       15 BUILD STOP CONDITIONS (MASTER §12)                        │
│                                                                                   │
│  #1  Specification conflict        — kontradiksi antar-doc tak ter-resolve         │
│  #2  Hidden assumption             — nilai tanpa sumber / tanpa NULL+status        │
│  #3  Missing feature               — fitur konstitusi tak terimplementasi          │
│  #4  Missing domain                — domain required absen dari inventory          │
│  #5  Missing pipeline              — tahap lifecycle absen / salah jenis           │
│  #6  Missing authority matrix      — indikator dipakai di luar kolom sah           │
│  #7  Missing market logic          — corridor/TP/wrong/grid/cage tak ter-spesifikasi│
│  #8  Governance conflict           — loop balik ke Core / auto-execute / bounded   │
│  #9  Constitution conflict         — pelanggaran LAW-MASTER-01..18                 │
│  #10 Undefined behavior            — adverse-first/tie-break/escape/no-trade/HOLD  │
│  #11 Undefined snapshot            — snapshot/field W-OD tak terdefinisi           │
│  #12 Undefined clone lifecycle     — lifecycle/3-obs/sub-ledger tak terdefinisi    │
│  #13 Undefined knowledge lifecycle — Librarian/unidirectional tak terdefinisi      │
│  #14 Undefined simulation lifecycle— 4 jenis sim / 5 hukum eksekusi tak terdefinisi│
│  #15 Undefined implementation      — native-binding/writer-serial tak terdefinisi  │
│      contract                                                                      │
│                                                                                   │
│  Any condition triggered = BUILD STOP — build FORBIDDEN to proceed                 │
│  Tension yang RESOLVED (mis. platform-binding) = NOT build stop                    │
│  Only unresolved conflicts trigger BUILD STOP                                      │
│                                                                                   │
│  Special: loop back to Core = BUILD STOP                                           │
│  KNOWLEDGE → TRUTH          ◄══ BUILD STOP                                         │
│  KNOWLEDGE → STRUCTURE      ◄══ BUILD STOP                                         │
│  KNOWLEDGE → EVIDENCE       ◄══ BUILD STOP                                         │
│  KNOWLEDGE → CLONE          ◄══ BUILD STOP                                         │
│  CONSUMER → TRUTH           ◄══ BUILD STOP                                         │
│  CONSUMER → CORE            ◄══ BUILD STOP                                         │
│  ORACLE → TRUTH             ◄══ BUILD STOP                                         │
│  HIVEMIND → CLONE           ◄══ BUILD STOP                                         │
│  DARWIN → auto-execute      ◄══ BUILD STOP                                         │
│  GOVERNANCE → Core-logic    ◄══ BUILD STOP                                         │
│  CLONE → TRUTH              ◄══ BUILD STOP                                         │
│  EVIDENCE → TRUTH           ◄══ BUILD STOP                                         │
│  W%R → Entry                ◄══ BUILD STOP (LAW-MASTER-08)                         │
│  MACD → Entry               ◄══ BUILD STOP (LAW-MASTER-15)                         │
│  RSI → Entry                ◄══ BUILD STOP (LAW-MASTER-15)                         │
│  GRID → active in trend     ◄══ BUILD STOP (HUKUM CAGE)                            │
│  WORKER → IndexedDB write   ◄══ BUILD STOP (LAW-MASTER-17)                         │
│  Date.now() → logic         ◄══ BUILD STOP (LAW-MASTER-01)                         │
│  Math.random() → logic      ◄══ BUILD STOP (LAW-MASTER-01)                         │
└───────────────────────────────────────────────────────────────────────────────────┘
```

---

## DOCUMENT STATUS

```
┌───────────────────────────────────────────────────────────────────────────────────┐
│                                                                                   │
│   DEPENDENCY_FREEZE.md — COMPLETE & LOCKED                                         │
│                                                                                   │
│   Sections: 10 main + 1 appendix                                                   │
│   ASCII diagrams: 28                                                               │
│   Dependency tables: 62+                                                            │
│   Forbidden dependency rules: 20                                                    │
│   Build stop conditions: 15                                                         │
│                                                                                   │
│   Sources referenced:                                                              │
│   • MASTER_SPECIFICATION.html (§3, §4, §5, §6, §7, §8, §9, §10, §11, §12)        │
│   • DOCUMENT_DEPENDENCY.html (§1–§7, §9, §10, §11)                                │
│   • QWEN_14_DOC.html (D0–D13)                                                      │
│   • stlms_sqlite_schema_v1.sql (all 18 table groups)                               │
│   • COMPONENT_INVENTORY.md (20 domains, 158 components)                            │
│   • FILE_RELATIONSHIP.md (hierarchy, authority chain)                              │
│   • REFERENCE_FREEZE.md (frozen architecture summary)                              │
│   • 01-07_IMPLEMENTATION_AUDIT.md.md (bug fixes, compliance)                       │
│                                                                                   │
│   Status: FROZEN — LOCKED                                                          │
│   Date: 2026-07-28                                                                 │
│                                                                                   │
└───────────────────────────────────────────────────────────────────────────────────┘
```
