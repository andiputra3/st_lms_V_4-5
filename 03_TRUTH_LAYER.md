# 03_TRUTH_LAYER.md

## ST-LMS — Truth Layer Architecture Mapping

**Date:** 2026-07-28
**Status:** ARCHITECTURE MAPPING — FROZEN
**Sources:** MASTER_SPECIFICATION.html §4, §6, QWEN_14_DOC.html D5, ST_LMS_CORE.js (TRUTH namespace)

---

### 1. Responsibility

Truth Layer adalah single source of truth untuk semua komputasi geometri market. Layer ini menghitung Supertrend, ATR, EMA, MACD, RSI, W%R, velocity, acceleration, distance-to-ST, dan volume delta. Truth adalah satu-satunya tempat di mana geometri dihitung dari OHLCV — tidak ada layer lain yang boleh menghitung ulang.

### 2. Purpose

- Menjadi satu-satunya sumber kebenaran untuk geometri market
- Menghitung seluruh indikator teknikal dari data candle
- Mendeteksi trend flip (TREND_FLIP_UP/DOWN)
- Mengelola status WARMUP/VALID
- Memproduksi truth_snapshot untuk downstream layers

### 3. Input

- `market_snapshot` — dari MARKET layer
- Checkpoint — previous candle state (pc, atr, ema, e12, e26, sig, puf, plf, trend, ag, al, hs, ls, wp1, vp, mh1)

### 4. Output

- `truth_snapshot` card (immutable)
- Fields: close, st, st_canon, stDir, color, atr, ema, ema12, ema26, macd, macd_signal, macd_hist, dist, distAtr, rsi, wpr, vel, acc, volDelta, point_status, flip

### 5. Dependency Layer

- **Upstream**: MARKET (market_snapshot)
- **Downstream**: STRUCTURE (truth_snapshot → structure_snapshot), EVIDENCE (truth_snapshot → evidence_snapshot)

### 6. Previous Pipeline

MARKET — Truth membaca market_snapshot dari MARKET.

### 7. Next Pipeline

STRUCTURE — Truth snapshot mengalir ke Structure untuk cage/wave/phase.
EVIDENCE — Truth snapshot mengalir ke Evidence untuk bus construction.

### 8. SQLite Tables yang Digunakan

- `market_candles` — membaca candle_id reference
- `truth_cache` — membaca previous state (jika checkpoint dari DB)

### 9. SQLite Tables yang Dihasilkan

- `truth_snapshots` — per-candle truth physics
- `truth_cache` — key-value cache per truth snapshot

### 10. Artifact yang Dihasilkan

- `truth_snapshot` card (immutable)
- `truth_point` per candle (state internal)
- Trend flip events

### 11. Validator yang Dibutuhkan

- **Point Status Validator** — WARMUP vs VALID
- **Warmup Validator** — memastikan NULL+status selama warmup (bukan fake value)
- **Determinism Validator** — 2 run seed sama → checksum identik
- **Float Precision Validator** — canonical string representation

### 12. Knowledge Entity yang Digunakan

Tidak langsung — Truth adalah upstream, knowledge membaca dari snapshot.

### 13. Trading Entity yang Digunakan

Tidak langsung — Truth tidak membuat keputusan trading. Clone membaca truth_snapshot via Card Sharing.

### 14. Snapshot yang Digunakan

- `market_snapshot` — dari MARKET

### 15. Benchmark yang Digunakan

Tidak ada — Benchmark adalah downstream.

### 16. Dashboard Component yang Digunakan

- Indicator Gauges — menampilkan RSI, W%R, dist/ATR, ATR
- Truth Status — menampilkan WARMUP/VALID

### 17. Mandatory atau Optional

**MANDATORY** — Truth adalah fondasi geometri. Tanpa Truth, tidak ada indikator.

### 18. Specification Reference

- MASTER_SPECIFICATION.html §4 (Market Geometry Master)
- MASTER_SPECIFICATION.html §6 (Lifecycle: Truth stage)
- QWEN_14_DOC.html D5 (Pipeline Architecture)
- ST_LMS_CORE.js lines 153-185 (TRUTH namespace)
- TRUTH_LAYER_FREEZE.md

### 19. Build Order Recommendation

```
Build Order: 4
Dependencies: MARKET, SQLite Foundation
Build setelah: MARKET
Build sebelum: STRUCTURE, EVIDENCE
```

### 20. Notes dan Constraint

- **Single Source of Truth**: Hanya Truth yang menghitung geometri. Tidak ada layer lain yang menghitung ulang dari OHLCV.
- **State Contiguity**: Truth memerlukan state kontigu (previous candle). Tidak bisa diparalelkan per-candle untuk satu simbol.
- **WARMUP**: dist=NULL, distAtr=NULL, point_status="WARMUP" (bukan nilai 0)
- **Supertrend**: multiplier = 3 (ST_MUL), dibekukan
- **ATR**: period = 10 (ATR_P), dibekukan
- **EMA**: period = 14 (EMA_P), dibekukan
- **MACD**: 12/26/9, dibekukan
- **RSI**: period = 10, smoothed average gain/loss
- **W%R**: period = 14, exit-only (dilarang untuk entry)
- **Velocity/Acceleration**: W%R derivative, deadzone bounded
- **Flip Detection**: cl > puf → TREND_FLIP_UP; cl < plf → TREND_FLIP_DOWN
- **Tie-break warna**: saat close == st, ikut trend
- **Thread**: Main thread (hot, sequential)
- **Card Sharing**: truth_snapshot di-share ke Structure dan Evidence
