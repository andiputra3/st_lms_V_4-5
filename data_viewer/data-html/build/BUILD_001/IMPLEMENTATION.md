# IMPLEMENTATION_ORDER.md

## ST-LMS v3 — Implementation Order

**Date:** 2026-07-29
**Phase:** 0 → 1 Transition
**Status:** FROZEN

---

## Build Sequence (26 Phases)

### PHASE 0: SPECIFICATION FREEZE (COMPLETE)
**Output:** 67 artifacts (specifications, freeze contracts, enrichment, architecture mapping)

---

### PHASE 1: FOUNDATION

| Order | Phase | Component | Depends On | Key Output |
|-------|-------|-----------|------------|------------|
| 1 | Phase-01 | SQLite Foundation | — | schema.sql, 40 tables, 9 indexes, 4 triggers, seed data |
| 2 | Phase-02 | BOOT + Workspace + Checkpoint | Phase-01 | boot.py, workspace.py, checkpoint.py |
| 3 | Phase-03 | Config + Bounded Registry | Phase-02 | config.py, 24 bounded parameters |

---

### PHASE 2: MARKET + TRUTH

| Order | Phase | Component | Depends On | Key Output |
|-------|-------|-----------|------------|------------|
| 4 | Phase-04 | Market Layer | Phase-03 | market.py, data_worker.py, hygiene, gap, OI proxy |
| 5 | Phase-05 | Truth Layer | Phase-04 | truth.py, PointBuilder, all indicators |
| 6 | Phase-06 | Distance Metrics | Phase-05 | distance.py, dist, distAtr, dist_ceiling, dist_floor, ST_DIST_VOL |

---

### PHASE 3: STRUCTURE + EVIDENCE

| Order | Phase | Component | Depends On | Key Output |
|-------|-------|-----------|------------|------------|
| 7 | Phase-07 | Structure Layer | Phase-05 | structure.py, LineBuilder, WaveBuilder, CageEngine |
| 8 | Phase-08 | Evidence Layer | Phase-05,07 | evidence.py, dir_bus, exit_bus, correction_bus |

---

### PHASE 4: TRADING CORE

| Order | Phase | Component | Depends On | Key Output |
|-------|-------|-----------|------------|------------|
| 9 | Phase-09 | Clone Layer | Phase-07,08 | clone.py, LONG, SHORT, GRID |
| 10 | Phase-10 | Trade Layer | Phase-09 | trade.py, mkEntry, mkExit, P&L |
| 11 | Phase-11 | Position Layer | Phase-10 | position.py, MAE/MFE, hold counter |

---

### PHASE 5: SIMULATION + REPLAY

| Order | Phase | Component | Depends On | Key Output |
|-------|-------|-----------|------------|------------|
| 12 | Phase-12 | Simulation Engine | Phase-09,10,11 | simulation.py, freshState, process, computeAll |
| 13 | Phase-13 | Replay Engine | Phase-12 | replay.py, 6 replay types |

---

### PHASE 6: STATISTICS + BAG + KNOWLEDGE

| Order | Phase | Component | Depends On | Key Output |
|-------|-------|-----------|------------|------------|
| 14 | Phase-14 | Statistics Layer | Phase-10,11 | statistics.py, tradeStats, sample gate |
| 15 | Phase-15 | BAG Layer | Phase-14 | bag.py, grouping, pattern mining, fingerprint |
| 16 | Phase-16 | Knowledge Layer | Phase-15 | knowledge.py, 7 entities |

---

### PHASE 7: PREDICTION + GOVERNANCE

| Order | Phase | Component | Depends On | Key Output |
|-------|-------|-----------|------------|------------|
| 17 | Phase-17 | Prediction Layer | Phase-16 | prediction.py, empirical only, no-model |
| 18 | Phase-18 | Trading Schema Layer | Phase-17 | trading_schema.py, 41 schemas |
| 19 | Phase-19 | Governance Layer | Phase-16,18 | governance.py, 6 validations, rollback |
| 20 | Phase-20 | Benchmark Layer | Phase-12,19 | benchmark.py, WASIT 5-gate, parallel worker |

---

### PHASE 8: CONSUMER + DASHBOARD

| Order | Phase | Component | Depends On | Key Output |
|-------|-------|-----------|------------|------------|
| 21 | Phase-21 | Consumer Layer | Phase-17,19 | consumer.py, fund, veto, intent, CSV export |
| 22 | Phase-22 | Dashboard Layer | Phase-21 | dashboard.html, view.js, 20+ panels |

---

### PHASE 9: INTEGRATION + AUDIT

| Order | Phase | Component | Depends On | Key Output |
|-------|-------|-----------|------------|------------|
| 23 | Phase-23 | Integration Layer | Phase-22 | integration.py, worker bridges, orchestration |
| 24 | Phase-24 | Audit Layer | Phase-23 | audit.py, 16 self-tests, 6 domain audits |
| 25 | Phase-25 | Final Validation | Phase-24 | final_validation.py, 12-domain check |

---

### PHASE 10: BUILD APPROVAL

| Order | Phase | Component | Depends On | Key Output |
|-------|-------|-----------|------------|------------|
| 26 | Phase-26 | BUILD APPROVAL | Phase-25 | approval_report.md, 15 stop-rule PASS |

---

## Gate Rules

1. Each phase must complete before the next begins
2. Each phase must pass ALL HARD gate tests
3. No phase may be skipped
4. No phase may be built before its dependencies
5. BUILD APPROVAL only after Phase-25 passes

## Pull Request Convention

Each phase produces a PR with branch: `build/phase-XX`
Merge manually after review.

---

## Per-Layer Build Pattern

Setiap layer dibangun dengan urutan: **Artifact → Package → Validator → Consumer**

| Order | File | Purpose |
|-------|------|---------|
| 1 | `{layer}_artifact.py` | Raw data/snapshot production |
| 2 | `{layer}_package.py` | Structured report from artifacts |
| 3 | `{layer}_validator.py` | Quality assurance checks |
| 4 | `{layer}_consumer.py` | Downstream API interface |

Contoh untuk TRUTH layer:
```
truth_artifact.py   — PointBuilder, semua indikator, truth_snapshot
truth_package.py    — SupertrendReport, IndicatorReport, TruthReportPackage
truth_validator.py  — determinism check, warmup check, range validation
truth_consumer.py   — API untuk Structure, Evidence, Dashboard
```

Dashboard TIDAK melakukan analisis. Dashboard hanya menggabungkan report packages dari seluruh layer.

---

## Refinement Implementation Order

All 20 refinements are already covered within existing phases. No new phases required.

| Refinement | Covered In Phase | Implementation Note |
|-----------|-----------------|---------------------|
| Present Dimension | Phase-05 (Truth) | truth_snapshot W fields — implement with full field set |
| Past Dimension | Phase-15,16 (BAG+Knowledge) | Academy historical buckets, Oracle vector history |
| Future Dimension | Phase-17 (Prediction) | prediction_snapshot — empirical win_rate only |
| Character Dimension | Phase-15 (BAG) | behavior_profile as part of behavior_analysis component |
| Trading Truth Package | Phase-09,10 (Clone+Trade) | clone_observation + trade_markers with full reason fields |
| Entry Truth | Phase-10 (Trade) | ENTRY_MARKER — reason, entry, sl, tp mandatory |
| Position Truth | Phase-11 (Position) | position_state — mae, mfe, hold_c tracking |
| Exit Truth | Phase-10 (Trade) | EXIT_MARKER — reason, exit, net, result mandatory |
| Market Intelligence Report | Phase-16 (Knowledge) | HiveMind synth — intelligence_score + dominant_bias |
| Living Market State | Phase-04,05 (Market+Truth) | Per-candle snapshot pair as living state |
| Market Character | Phase-15 (BAG) | behavior_profile with 6 profile types |
| Market Biography | Phase-15 (BAG) | sequence_analysis — wave/cage/trade sequences |
| Compression Maturity | Phase-15 (BAG) | maturity_score on cage compression bag_artifacts |
| Supertrend Snapshot | Phase-05 (Truth) | st, stDir, color, st_canon in truth_snapshot |
| Multi Time Frame Report | Phase-08 (Evidence) | mtf_sector from wave structure classification |
| Williams %R Integration | Phase-05,08 (Truth+Evidence) | W%R in truth_snapshot, exit-only in exit_bus |
| Market Timeline | Phase-16 (Knowledge) | River chronicle — all card events append-only |
| Expensive Data Classification | Phase-15 (BAG) | bag_kind=risk — fee_drag, wrong_rate grouping |
| Critical Data Classification | Phase-24 (Audit) | audit_logs severity — CRITICAL/HIGH/MEDIUM/LOW/INFO |
| Recommendation Package | Phase-16 (Knowledge) | Darwin proposals — TIGHTEN_ENTRY, TIGHTEN_WRONG |

**Refinement Build Rule:** Implement refinements within their respective phases. Do NOT create separate phases for refinements.
