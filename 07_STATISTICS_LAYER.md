# 07_STATISTICS_LAYER.md

## ST-LMS — Statistics Layer Architecture Mapping

**Date:** 2026-07-28
**Status:** ARCHITECTURE MAPPING — FROZEN
**Sources:** MASTER_SPECIFICATION.html §6, ST_LMS_CORE.js (STATISTICS namespace), QWEN_14_DOC.html D5

---

### 1. Responsibility

Statistics Layer bertanggung jawab untuk mengagregasi trade markers menjadi statistik per clone. Layer ini menghitung win_rate, expectancy, profit factor, MAE, MFE, fee_drag, dan wrong_rate. Statistics menerapkan sample gate (CUKUP iff sample ≥ 30) dan tidak menyatakan keyakinan di bawah ambang sample.

### 2. Purpose

- Mengagregasi trade markers per clone (LONG/SHORT/GRID)
- Menghitung metrik performa trading
- Menerapkan sample gate untuk reliabilitas statistik
- Memproduksi statistics_snapshot untuk Knowledge layer
- Menyediakan data untuk Academy, CERMIN, dan Darwin

### 3. Input

- `trade_markers` — semua marker dengan kind=EXIT
- `trade_snapshot` — aggregate markers per candle

### 4. Output

- `statistics_snapshot` card (immutable)
- Per clone: sample, win_rate, expectancy, pf, mae, mfe, fee_drag, wrong_rate, coverage, status (CUKUP/BELUM_CUKUP)
- Market-level: distance_health_hist, fee_safe_margin_dist, wrong_entry_dist

### 5. Dependency Layer

- **Upstream**: TRADE (trade_markers)
- **Downstream**: KNOWLEDGE (statistics_snapshot → Academy, CERMIN, Darwin), BAG (statistics_snapshot → bag_artifacts)

### 6. Previous Pipeline

TRADE — Statistics membaca trade_markers dari TRADE.

### 7. Next Pipeline

KNOWLEDGE — Statistics snapshot mengalir ke Knowledge untuk Academy, CERMIN, Darwin.
BAG — Statistics snapshot mengalir ke BAG untuk behavioral grouping.

### 8. SQLite Tables yang Digunakan

- `trade_markers` — membaca marker data
- `clones` — clone reference

### 9. SQLite Tables yang Dihasilkan

- `trade_statistics` — aggregated trade stats per session/clone/bucket
- `market_statistics` — market-level stats per session

### 10. Artifact yang Dihasilkan

- `statistics_snapshot` card (immutable)
- Per-clone statistics object:
  - sample: count of EXIT markers
  - wins: count where result = WIN
  - win_rate: (wins / sample) × 100
  - expectancy: Σnet / sample
  - pf (profit factor): Σgross_pos / Σ|gross_neg|
  - mae: Σ|mae| / sample
  - mfe: Σmfe / sample
  - fee_drag: Σfee / sample
  - wrong_rate: (wrong_entry exits / sample) × 100
  - status: CUKUP (sample ≥ 30) / BELUM_CUKUP (sample < 30)

### 11. Validator yang Dibutuhkan

- **Sample Gate Validator** — sample ≥ SAMPLE_GATE (30) → CUKUP
- **Win Rate Validator** — 0 ≤ win_rate ≤ 100
- **PF Validator** — PF = null jika tidak ada losses
- **Fee Consistency Validator** — net = gross - fee - slip (tolerance 1e-6)
- **Status Validator** — CUKUP atau BELUM_CUKUP (tidak boleh confidence dinyatakan jika BELUM)

### 12. Knowledge Entity yang Digunakan

Statistics TIDAK membaca Knowledge. Statistics adalah upstream.

### 13. Trading Entity yang Digunakan

- Trade markers — semua EXIT markers dari LONG/SHORT/GRID

### 14. Snapshot yang Digunakan

- `trade_snapshot` — dari TRADE

### 15. Benchmark yang Digunakan

Tidak langsung — Statistics data menjadi input untuk WASIT benchmark.

### 16. Dashboard Component yang Digunakan

- Rapor Table — menampilkan statistics per clone (sample, win_rate, expectancy, PF, MAE, MFE, fee_drag, wrong_rate, status)
- Statistics Status — CUKUP/BELUM_CUKUP indicator

### 17. Mandatory atau Optional

**MANDATORY** — Statistics adalah input wajib untuk Knowledge layer.

### 18. Specification Reference

- MASTER_SPECIFICATION.html §6 (Lifecycle: Statistics stage)
- MASTER_SPECIFICATION.html §12 (Sample-Gated LAW-MASTER-12)
- QWEN_14_DOC.html D5 (Pipeline Architecture)
- ST_LMS_CORE.js lines 374-383 (STATISTICS namespace)

### 19. Build Order Recommendation

```
Build Order: 7
Dependencies: TRADE, SQLite Foundation
Build setelah: TRADE
Build sebelum: KNOWLEDGE, BAG
```

### 20. Notes dan Constraint

- **SHARED-AGAIN (1×)**: Statistics dijalankan 1× setelah semua clone selesai
- **Per clone, tidak dicampur**: LONG/SHORT/GRID statistics terpisah
- **Sample Gate**: CUKUP iff sample ≥ 30 (SAMPLE_GATE, bounded)
- **BELUM_CUKUP**: Tidak boleh menyatakan keyakinan di bawah ambang sample
- **WIN only if net > 0**: Sesuai fee berlapis (LAW-MASTER-09)
- **PF = null**: Jika tidak ada losses (tidak ada denominator)
- **Card-agnostic**: Statistics membaca markers tanpa mengetahui clone logic
- **Thread**: Main thread (dapat menggunakan worker untuk batch aggregation)
- **OD fields**: Seluruh statistics fields adalah OD (on-demand dari Trade markers)
- **Market statistics**: phase, wave_structure, support_hits, resistance_hits, breakout_count, sideways_count, trend_count
