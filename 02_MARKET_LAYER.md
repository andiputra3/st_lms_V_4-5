# 02_MARKET_LAYER.md

## ST-LMS — Market Layer Architecture Mapping

**Date:** 2026-07-28
**Status:** ARCHITECTURE MAPPING — FROZEN
**Sources:** MASTER_SPECIFICATION.html §6, QWEN_14_DOC.html D5, ST_LMS_CORE.js (MARKET namespace)

---

### 1. Responsibility

Market Layer bertanggung jawab untuk mengamati (observe) data candle mentah, melakukan validasi hygiene, mendeteksi gap, menghasilkan OI proxy, dan memproduksi market_snapshot card. Layer ini adalah pintu masuk data ke dalam pipeline ST-LMS.

### 2. Purpose

- Mengkarantina dan mengkanonisasi data candle mentah
- Memastikan hanya data valid yang masuk ke pipeline
- Menyediakan market_snapshot sebagai input untuk TRUTH layer
- Mendeteksi anomali data (gap, invalid)

### 3. Input

- Raw candle data: OHLCV + takerBuyRatio
- Data source: fixture generator (offline) atau live feed (fetch/WebSocket)
- Session context: symbol, timeframe, session_id

### 4. Output

- `market_snapshot` card (immutable)
- Fields: ts, symbol, tf, OHLCV(o,h,l,c,v), taker_buy_ratio, taker_sell_volume, data_status, gap_flag, wib_iso

### 5. Dependency Layer

- **Upstream**: BOOT (config, session initialization)
- **Downstream**: TRUTH (market_snapshot → truth_snapshot)

### 6. Previous Pipeline

BOOT — Market dimulai setelah system initialization.

### 7. Next Pipeline

TRUTH — Market snapshot mengalir ke Truth Layer untuk komputasi geometri.

### 8. SQLite Tables yang Digunakan

- `symbols` — membaca symbol registry
- `timeframes` — membaca timeframe registry
- `app_sessions` — session context
- `pipeline_runs` — run tracking

### 9. SQLite Tables yang Dihasilkan

- `market_candles` — candle data per symbol/timeframe/timestamp
- `market_metadata` — key-value metadata
- `open_interest_series` — OI time series (proxied)
- `market_gaps` — detected time/price gaps

### 10. Artifact yang Dihasilkan

- `market_snapshot` card (immutable, SHA-256 checksum)
- Data hygiene report
- Gap detection report
- OI proxy series

### 11. Validator yang Dibutuhkan

- **Hygiene Validator** — H ≥ max(O,C), L ≤ min(O,C), H ≥ L, V ≥ 0
- **Gap Detector** — ts[i] - ts[i-1] > 60000ms → gap_flag = 1
- **Data Status Validator** — CLOSED (complete) vs PROVISIONAL (incomplete)
- **Source Validator** — memverifikasi sumber data valid

### 12. Knowledge Entity yang Digunakan

Tidak ada — Market adalah layer paling upstream, tidak membaca knowledge.

### 13. Trading Entity yang Digunakan

Tidak ada — Market tidak membuat keputusan trading.

### 14. Snapshot yang Digunakan

Tidak ada — Market memproduksi snapshot pertama dalam pipeline.

### 15. Benchmark yang Digunakan

Tidak ada — Benchmark adalah downstream.

### 16. Dashboard Component yang Digunakan

- Market Data Table — menampilkan OHLCV candle data
- Data Quality Indicator — menampilkan status data (OK/GAP/INVALID)

### 17. Mandatory atau Optional

**MANDATORY** — Tanpa Market Layer, tidak ada data yang masuk ke pipeline.

### 18. Specification Reference

- MASTER_SPECIFICATION.html §6 (Lifecycle: Observation Market stage)
- QWEN_14_DOC.html D5 (Pipeline Architecture)
- ST_LMS_CORE.js lines 138-151 (MARKET namespace)

### 19. Build Order Recommendation

```
Build Order: 2
Dependencies: BOOT, SQLite Foundation
Build setelah: BOOT + Workspace + SQLite Foundation
Build sebelum: TRUTH
```

### 20. Notes dan Constraint

- **WARMUP**: data_status = 'warmup' jika data history tidak mencukupi
- **PROVISIONAL**: candle belum closed → tidak menghasilkan FINAL snapshot
- **INSUFFICIENT_DATA**: data hilang → NULL + status, bukan fake value
- **GAP**: gap_flag = 1 mengurangi data quality score
- **OI Proxy**: OI di-derive dari volume + takerBuyRatio (bukan data real)
- **Data Worker**: batch bootstrap, TF aggregation, gap-repair (cold worker)
- **Hygiene wajib**: candle yang gagal hygiene → INVALID, ditolak
- **UNIQUE constraint**: (symbol, timeframe, ts) — satu candle per timestamp
