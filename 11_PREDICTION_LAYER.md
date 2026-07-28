# 11_PREDICTION_LAYER.md

## ST-LMS — Prediction Layer Architecture Mapping

**Date:** 2026-07-28
**Status:** ARCHITECTURE MAPPING — FROZEN
**Sources:** MASTER_SPECIFICATION.html §10, ST_LMS_CORE.js (PREDICTION namespace)

---

### 1. Responsibility

Prediction Layer bertanggung jawab untuk mengagregasi probabilitas empiris dari Knowledge layer. Prediction bersifat murni empiris — probabilitas = frekuensi bersyarat (Academy) + similarity (Oracle). Tidak ada model prediktif, tidak ada forecasting, tidak ada black-box AI.

### 2. Purpose

- Mengagregasi empirical win_rate per clone dari Academy
- Menggabungkan similarity_score dari Oracle
- Menyertakan calibration_error dari CERMIN
- Memproduksi prediction_snapshot dengan no_model=true
- Menyediakan probabilitas empiris untuk Consumer

### 3. Input

- `knowledge_snapshot` — academy_artifacts, oracle_match, hivemind, cermin
- Academy win_rate per clone per bucket
- Oracle similarity_score
- HiveMind intelligence_score, dominant_bias
- CERMIN calibration_error

### 4. Output

- `prediction_snapshot` card (immutable)
- Fields: intelligence_score, dominant_bias, empirical_win_rate_per_clone{LONG, SHORT, GRID}, similarity_score, pattern_boost, oracle_boost, no_model=true
- OD fields: empirical_win_rate (dari Academy)

### 5. Dependency Layer

- **Upstream**: KNOWLEDGE (knowledge_snapshot)
- **Downstream**: CONSUMER (prediction_snapshot → trade intent)

### 6. Previous Pipeline

KNOWLEDGE — Prediction membaca knowledge_snapshot.

### 7. Next Pipeline

CONSUMER — Prediction snapshot mengalir ke Consumer untuk trade intent.

### 8. SQLite Tables yang Digunakan

- `knowledge_artifacts` — membaca academy, oracle, hivemind, cermin data

### 9. SQLite Tables yang Dihasilkan

- `predictions` — empirical predictions per candle
- `prediction_results` — actual outcomes vs predictions

### 10. Artifact yang Dihasilkan

- `prediction_snapshot` card (immutable)
- Prediction object: {prediction, calibration, empirical, no_model, sources, note}
- Sources: ["Academy win_rate per bucket", "Oracle similarity_score", "CERMIN calibration_error"]
- Note: "probabilitas = frekuensi empiris + similarity; BUKAN forecast model"

### 11. Validator yang Dibutuhkan

- **No-Model Validator** — no_model = true (selalu)
- **Sample Gate Validator** — BELUM_CUKUP → NULL (bukan angka)
- **Empirical-Only Validator** — tidak ada forecasting model
- **Lineage Validator** — setiap angka punya card lineage
- **CERMIN Honesty Validator** — calibration_error disertakan

### 12. Knowledge Entity yang Digunakan

- Academy — empirical win_rate per bucket
- Oracle — similarity_score
- HiveMind — intelligence_score, dominant_bias
- CERMIN — calibration_error

### 13. Trading Entity yang Digunakan

Tidak langsung — Prediction adalah input untuk Consumer trade intent.

### 14. Snapshot yang Digunakan

- `knowledge_snapshot` — dari KNOWLEDGE

### 15. Benchmark yang Digunakan

Tidak langsung — Prediction accuracy dapat di-benchmark.

### 16. Dashboard Component yang Digunakan

- Prediction Panel — menampilkan intelligence_score, dominant_bias, similarity, empirical win_rates
- CERMIN Panel — menampilkan calibration_error per clone
- Sources Panel — menampilkan sumber probabilitas

### 17. Mandatory atau Optional

**MANDATORY** — Prediction adalah output pembelajaran ST-LMS.

### 18. Specification Reference

- MASTER_SPECIFICATION.html §10 (Prediction Master Constitution)
- MASTER_SPECIFICATION.html §13 (Prediction = Empiris LAW-MASTER-13)
- ST_LMS_CORE.js lines 600-607 (PREDICTION namespace)

### 19. Build Order Recommendation

```
Build Order: 11
Dependencies: KNOWLEDGE
Build setelah: KNOWLEDGE
Build sebelum: CONSUMER, GOVERNANCE
```

### 20. Notes dan Constraint

- **Empirical only**: Probabilitas = frekuensi bersyarat (Academy) + similarity (Oracle)
- **NO forecasting**: Dilarang forecasting harga/arah dari model
- **NO hidden AI**: Tidak ada black-box; setiap angka punya lineage card
- **NO unsupported prediction**: Di bawah ambang sample = BELUM_CUKUP/NULL
- **no_model = true**: Selalu true; tidak ada model prediktif
- **Probability types**: continuation/reversal/breakout/sideway (win_rate per bucket), LONG/SHORT/GRID profitability (win_rate_net per clone per bucket), market similarity (oracle_match.similarity_score/10000)
- **CERMIN honesty**: calibration_error disertakan agar kejujuran confidence terukur
- **SHARED-AGAIN (1×)**: Prediction dijalankan 1× setelah Knowledge
- **Thread**: Main thread
- **Forbidden**: Output model prediktif dalam prediction_snapshot
