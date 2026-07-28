# 04_DISTANCE_LAYER.md

## ST-LMS — Distance Layer Architecture Mapping

**Date:** 2026-07-28
**Status:** ARCHITECTURE MAPPING — FROZEN
**Sources:** MASTER_SPECIFICATION.html §4, ST_LMS_CORE.js (EVIDENCE.correctionBus, TRUTH.PointBuilder)

---

### 1. Responsibility

Distance Layer bertanggung jawab untuk menghitung dan mengelola seluruh metrik jarak dalam ST-LMS. Ini mencakup Distance-to-ST (dist, distAtr), Distance-Ceiling (jarak ke atas), Distance-Floor (jarak ke bawah), dan ST-Dist-Vol (volatilitas dari distAtr). Layer ini adalah sub-layer dari Truth/Structure yang fokus pada aspek spasial market.

**Catatan Arsitektur:** Dalam referensi MASTER_SPECIFICATION, Distance bukan layer terpisah. Distance-to-ST diproduksi di Truth, Distance-Ceiling/Floor diproduksi di Structure (OD fields). Prompt ini meminta Distance sebagai layer terpisah untuk kejelasan pemetaan.

### 2. Purpose

- Menyediakan metrik jarak yang menjadi dasar keputusan entry/exit
- Mengukur seberapa jauh price dari support/resistance
- Menyediakan volatility proxy via ST-Dist-Vol
- Menjadi input untuk fee_safe check dan corridor computation

### 3. Input

- `truth_snapshot` — close, st, atr (dari TRUTH)
- `structure_snapshot` — cage.upper, cage.lower (dari STRUCTURE)

### 4. Output

- Distance-to-ST: `dist = |close - st|`
- Distance-to-ST/ATR: `distAtr = dist / atr`
- Distance-Ceiling: `dist_ceiling = cage.upper - close` (NULL jika tidak ada ceiling)
- Distance-Floor: `dist_floor = close - cage.lower` (NULL jika tidak ada floor)
- ST-Dist-Vol: rolling standard deviation of distAtr (sdv, p90, n)

### 5. Dependency Layer

- **Upstream**: TRUTH (close, st, atr), STRUCTURE (cage.upper, cage.lower)
- **Downstream**: CLONE (corridor, fee_safe), EVIDENCE (correction_bus), KNOWLEDGE (Academy distance_bucket)

### 6. Previous Pipeline

TRUTH + STRUCTURE — Distance metrics dihitung setelah truth dan structure tersedia.

### 7. Next Pipeline

CLONE — Distance metrics digunakan untuk corridor dan fee_safe checks.
EVIDENCE — Distance metrics masuk ke correction_bus.

### 8. SQLite Tables yang Digunakan

- `truth_snapshots` — membaca close, st, atr, distAtr
- `structure_snapshots` — membaca cage_upper, cage_lower

### 9. SQLite Tables yang Dihasilkan

Distance metrics tersimpan dalam:
- `truth_snapshots.dist_atr` — distAtr (W field)
- `truth_snapshots.dist_to_st` — dist (W field)
- `structure_snapshots.dist_ceiling` — dist_ceiling (OD field)
- `structure_snapshots.dist_floor` — dist_floor (OD field)

### 10. Artifact yang Dihasilkan

- Distance metrics (dist, distAtr, dist_ceiling, dist_floor)
- ST-Dist-Vol statistics (sdv, p90)
- Distance bucket classification: WARMUP, OPTIMAL (≤0.5), NEAR (≤1), EXTENDED (≤2), FAR (>2)

### 11. Validator yang Dibutuhkan

- **NULL Validator** — dist=NULL saat WARMUP (bukan 0)
- **Ceiling NULL Validator** — dist_ceiling=NULL pada downtrend (bukan 0)
- **Floor NULL Validator** — dist_floor=NULL pada uptrend (bukan 0)
- **ATR Validator** — distAtr hanya valid jika atr != null

### 12. Knowledge Entity yang Digunakan

- Academy — distance_bucket sebagai dimensi bucket key
- Oracle — norm01(distAtr, 0, 3) sebagai vektor dimensi

### 13. Trading Entity yang Digunakan

- Entry Corridor — menggunakan sdv untuk volatility adjustment
- Fee Safety — dist_ceiling ≥ required_move (LONG), dist_floor ≥ required_move (SHORT)
- Expected Move — ceiling - close (LONG), close - floor (SHORT)

### 14. Snapshot yang Digunakan

- `truth_snapshot` — dist, distAtr
- `structure_snapshot` — dist_ceiling, dist_floor

### 15. Benchmark yang Digunakan

Tidak langsung — distance metrics adalah input untuk trading decisions yang di-benchmark.

### 16. Dashboard Component yang Digunakan

- Distance Gauges — menampilkan dist/ATR
- Price Position Indicator — menampilkan posisi dalam cage

### 17. Mandatory atau Optional

**MANDATORY** — Distance metrics adalah fondasi untuk entry/exit decisions.

### 18. Specification Reference

- MASTER_SPECIFICATION.html §4 (Market Geometry Master — Distance-to-ST, Distance-Ceiling, Distance-Floor)
- MASTER_SPECIFICATION.html §5 (Indicator Authority Matrix — Distance columns)
- ST_LMS_CORE.js lines 166-184 (PointBuilder: dist, distAtr)
- ST_LMS_CORE.js lines 269-274 (EVIDENCE.correctionBus: dist_ceiling, dist_floor)
- ST_LMS_CORE.js lines 272-274 (EVIDENCE.StDistVol)

### 19. Build Order Recommendation

```
Build Order: 4.5 (antara TRUTH dan STRUCTURE, atau sebagai sub-layer)
Dependencies: TRUTH (close, st, atr), STRUCTURE (cage)
Build setelah: TRUTH, STRUCTURE
Build sebelum: EVIDENCE, CLONE
```

### 20. Notes dan Constraint

- **dist_to_st**: Diproduksi di TRUTH.PointBuilder sebagai W field
- **distAtr**: Diproduksi di TRUTH.PointBuilder sebagai W field
- **dist_ceiling**: Diproduksi di EVIDENCE.correctionBus sebagai OD field (dari sumber beku)
- **dist_floor**: Diproduksi di EVIDENCE.correctionBus sebagai OD field (dari sumber beku)
- **NULL pada trend**: dist_ceiling=NULL pada downtrend; dist_floor=NULL pada uptrend
- **HUKUM CAGE**: 1 dinding → jarak seberang = NULL
- **ST_DIST_VOL window**: 96 candles (ST_DIST_VOL_WINDOW, bounded)
- **Distance Buckets**: OPTIMAL ≤ 0.5, NEAR ≤ 1, EXTENDED ≤ 2, FAR > 2, WARMUP = null
- **Corridor volatility**: sdv digunakan untuk adaptive entry corridor width
- **Authority Matrix**: Distance-to-ST = S (Entry), — (Exit), V (Validation), W,K (Statistics), K (Knowledge), P+ (Prediction)
- **Authority Matrix**: Distance-Ceiling = T (Entry), T (Exit), V (Validation), W (Statistics), K (Knowledge), P− (Prediction), B (Governance)
- **Authority Matrix**: Distance-Floor = T (Entry), T (Exit), V (Validation), W (Statistics), K (Knowledge), P− (Prediction), B (Governance)
