# 14_BENCHMARK_LAYER.md

## ST-LMS — Benchmark Layer Architecture Mapping

**Date:** 2026-07-28
**Status:** ARCHITECTURE MAPPING — FROZEN
**Sources:** MASTER_SPECIFICATION.html §11, ST_LMS_CORE.js (BENCHMARK namespace), QWEN_14_DOC.html D10

---

### 1. Responsibility

Benchmark Layer bertanggung jawab untuk mengevaluasi proposal governance melalui WASIT 5-gate walk-forward validation. Benchmark berjalan secara paralel via Web Worker (dengan fallback sequential deterministik) dan bersifat ON-DEMAND (tidak per candle).

### 2. Purpose

- Mengevaluasi config changes melalui walk-forward validation
- Menyaring proposal yang tidak memenuhi 5-gate criteria
- Menyediakan data objektif untuk human approval
- Memastikan config changes tidak memperburuk performa

### 3. Input

- Base config — current bounded parameters
- Candidate config — proposed parameter values
- Trade markers — base dan candidate
- Fold count — jumlah fold untuk walk-forward

### 4. Output

- `benchmark_snapshot` card (on-demand)
- WASIT verdict: PASS/FAIL
- 5-gate results: G1(sample), G2(expectancy), G3(worst-loss), G4(win_rate), G5(fee)
- Per-fold metrics: base vs candidate per fold
- Total base/cand exits

### 5. Dependency Layer

- **Upstream**: SIMULATION (trade markers), CONFIG (bounded parameters)
- **Downstream**: GOVERNANCE (benchmark results → proposal decision)

### 6. Previous Pipeline

SIMULATION — Benchmark menggunakan simulation untuk walk-forward.

### 7. Next Pipeline

GOVERNANCE — Benchmark results mengalir ke Governance untuk proposal decision.

### 8. SQLite Tables yang Digunakan

- `trade_markers` — membaca marker data
- `pipeline_runs` — run tracking

### 9. SQLite Tables yang Dihasilkan

- `benchmark_runs` — benchmark containers (5 run_kinds)
- `benchmark_cases` — individual test cases per run

### 10. Artifact yang Dihasilkan

- `benchmark_snapshot` card (on-demand)
- WASIT result object: {folds, total_base, total_cand, gates{G1..G5}, per_fold[], verdict}
- Per-fold metrics: {base{win_rate,expectancy,worst,fee}, cand{...}, gates{G2..G5}}

### 11. Validator yang Dibutuhkan

- **G1 Validator** — candidate exits ≥ 30
- **G2 Validator** — candidate expectancy > base expectancy (majority folds)
- **G3 Validator** — candidate worst-loss not worse > 10% (majority folds)
- **G4 Validator** — candidate win_rate not dropped > 2% (majority folds)
- **G5 Validator** — candidate fee_drag not increased > 0.001 (majority folds)
- **Identical Config Validator** — base = candidate → G2 must FAIL (bukan rubber-stamp)
- **Majority Vote Validator** — per-gate pass requires majority of folds

### 12. Knowledge Entity yang Digunakan

Tidak langsung — Benchmark adalah downstream dari Knowledge.

### 13. Trading Entity yang Digunakan

- Trade markers — base dan candidate markers untuk perbandingan

### 14. Snapshot yang Digunakan

- `trade_snapshot` — markers untuk walk-forward

### 15. Benchmark yang Digunakan

Benchmark adalah layer itu sendiri.

### 16. Dashboard Component yang Digunakan

- WASIT Panel — menampilkan 5-gate results + verdict
- Benchmark Run Panel — daftar benchmark runs
- Per-Fold Panel — detail per fold

### 17. Mandatory atau Optional

**MANDATORY** — Benchmark adalah gate wajib untuk setiap proposal governance.

### 18. Specification Reference

- MASTER_SPECIFICATION.html §11 (Governance Master — WASIT)
- MASTER_SPECIFICATION.html §14 (Human Approval + Bounded LAW-MASTER-14)
- QWEN_14_DOC.html D10 (Governance Architecture)
- ST_LMS_CORE.js lines 512-558 (BENCHMARK namespace)

### 19. Build Order Recommendation

```
Build Order: 14
Dependencies: SIMULATION, CONFIG
Build setelah: SIMULATION
Build sebelum: GOVERNANCE
```

### 20. Notes dan Constraint

- **ON-DEMAND**: Benchmark TIDAK per candle — hanya saat proposal governance
- **5 run_kinds**: wasit, walk_forward, clone, trade, market
- **WASIT 5-Gate**: G1(sample≥30), G2(expectancy>base), G3(worst not worse>10%), G4(win_rate not dropped>2%), G5(fee not increased)
- **Majority vote**: Per-gate pass requires majority of folds (Math.floor(folds/2)+1)
- **Identical → G2 FAIL**: Config yang sama dengan base = rubber-stamp, harus gagal G2
- **Parallel Worker**: WASIT berjalan di Benchmark Worker (paralel base vs candidate)
- **Fallback Sequential**: Jika Worker API tidak tersedia, jalankan sequential (deterministik)
- **Worker timeout**: 2500ms untuk parallel worker; fallback ke sequential jika timeout
- **Folds**: Minimum 3 folds (configurable)
- **Per-fold metrics**: win_rate, expectancy, worst_loss, fee per fold
- **Verdict**: PASS (all 5 gates pass) / FAIL (any gate fails)
- **Thread**: Benchmark Worker (cold, parallel); Main thread untuk orchestration
- **No approval**: WASIT hanya menyaring, tidak menyetujui
