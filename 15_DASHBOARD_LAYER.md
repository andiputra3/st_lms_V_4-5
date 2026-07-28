# 15_DASHBOARD_LAYER.md

## ST-LMS — Dashboard Layer Architecture Mapping

**Date:** 2026-07-28
**Status:** ARCHITECTURE MAPPING — FROZEN
**Sources:** ST_LMS_CORE.js (VIEW namespace), QWEN_14_DOC.html D11, DOCUMENT_DEPENDENCY.html

---

### 1. Responsibility

Dashboard Layer bertanggung jawab untuk merender seluruh data ST-LMS ke dalam UI. Layer ini membaca cards via API internal (query IndexedDB/SQLite), tidak menghitung logika market, dan tidak menyimpan kebenaran di localStorage. Dashboard adalah control-plane — bukan data-plane.

### 2. Purpose

- Menampilkan geometry chart (candle + ST + cage + markers)
- Menampilkan clone cards (LONG/SHORT/GRID observations)
- Menampilkan trade history + equity curve
- Menampilkan replay viewer (scrubber + playback)
- Menampilkan knowledge artifacts (Academy, Oracle, HiveMind)
- Menampilkan governance UI (proposals + rollback)
- Menampilkan simulation UI
- Menampilkan prediction + consumer displays
- Menampilkan audit + final validation results
- Menyediakan SQLite Viewer + Manager + Query Console

### 3. Input

- Semua cards — dari IndexedDB/SQLite
- Config — bounded parameters
- State — simulation state

### 4. Output

- Rendered UI (HTML/CSS/JS)
- User interactions (button clicks, scrubber, play/pause)
- Export files (CSV dari trade markers)

### 5. Dependency Layer

- **Upstream**: Semua layers (membaca cards)
- **Downstream**: Tidak ada (terminal layer — UI)

### 6. Previous Pipeline

Semua pipeline stages — Dashboard membaca output dari seluruh pipeline.

### 7. Next Pipeline

Tidak ada — Dashboard adalah terminal layer (UI).

### 8. SQLite Tables yang Digunakan

Semua tables — Dashboard membaca semua data untuk rendering.

### 9. SQLite Tables yang Dihasilkan

Tidak ada — Dashboard TIDAK menulis ke SQLite.

### 10. Artifact yang Dihasilkan

- Rendered UI panels (20+ components)
- Export CSV files
- User interaction events

### 11. Validator yang Dibutuhkan

- **No-Mock Validator** — panel kosong = N/A (bukan placeholder)
- **No-Compute Validator** — Dashboard tidak menghitung logika market
- **No-LocalStorage Validator** — kebenaran tidak disimpan di localStorage
- **Read-Only Validator** — Dashboard hanya membaca cards

### 12. Knowledge Entity yang Digunakan

Semua knowledge entities — untuk rendering Academy, Oracle, HiveMind, CERMIN, Librarian panels.

### 13. Trading Entity yang Digunakan

Semua trading entities — untuk rendering clone cards, trade history, equity curve.

### 14. Snapshot yang Digunakan

Semua 10 snapshots — untuk rendering semua panels.

### 15. Benchmark yang Digunakan

Benchmark results — untuk rendering WASIT panel.

### 16. Dashboard Component yang Digunakan

| Component | Data Source | Purpose |
|-----------|-------------|---------|
| Geometry Viewer | truth + structure + trade markers | Candle chart + ST + cage + entry/exit markers |
| Indicator Gauges | truth (RSI, W%R, dist/ATR, ATR) | Visual indicator display |
| Wave Panel | structure (wave, phase, stDir) | Wave structure + phase display |
| Cage Panel | structure (cage status, upper, lower, pp, breakout) | Cage visualization |
| Versioning Panel | structure (support/resistance versions) | S/R wall versions |
| Ladder Panel | structure (ladder, nearest) | Ladder + nearest S/R |
| Direction Bus Panel | evidence (dir_bus) | EMA, OI, VolDelta, MTF gauges |
| Exit Bus Panel | evidence (exit_bus) | HOLD-veto, vel, acc, early invalidation |
| Market Now Panel | market (OHLCV, wib, data_status, gap) | Current candle data |
| Market Table | market (recent candles) | Candle history table |
| Clone Cards | clone (LONG/SHORT/GRID observations) | Clone status + positions |
| Trade History | trade markers | Trade history table |
| Equity Curve | clone (equity array) | Equity chart per clone |
| Rapor Table | statistics | Win rate, expectancy, PF, MAE, MFE per clone |
| Academy Table | knowledge (academy artifacts) | Bucket key, sample, win_rate, status |
| Knowledge KV | knowledge (oracle, hivemind) | Oracle match, intelligence, bias |
| CERMIN Panel | knowledge (cermin) | Calibration error per clone |
| Librarian Feed | knowledge (librarian events) | Lifecycle status feed |
| Governance Panel | governance (validations, proposals) | Validation results + proposal management |
| Config Table | config (bounded parameters) | Current/min/max values |
| Simulation UI | simulation | Type selector + results |
| Replay Viewer | replay (frames) | Scrubber + step + auto-play |
| Prediction Panel | prediction | Intelligence, bias, empirical win_rates |
| Consumer Panel | consumer | Trade intent + live-adapter status |
| Audit Panel | audit (self-test results) | Test pass/fail + fingerprint |
| Final Validation | final_validation | 12-domain check results |
| SQLite Viewer | SQLite tables | Table browser |
| SQLite Manager | SQLite | Backup, restore, vacuum, integrity |
| Query Console | SQLite | SQL execution |

### 17. Mandatory atau Optional

**MANDATORY** — Dashboard adalah control-plane untuk interaksi manusia dengan ST-LMS.

### 18. Specification Reference

- MASTER_SPECIFICATION.html §1 (System Identity — bukan dashboard trading)
- QWEN_14_DOC.html D11 (HTML OS Blueprint — UI anti-mock)
- QWEN_14_DOC.html D0 (Feature Inventory — panel mapping)
- ST_LMS_CORE.js lines 670-842 (VIEW namespace)

### 19. Build Order Recommendation

```
Build Order: 15
Dependencies: Semua layers
Build setelah: Semua layers selesai
Build sebelum: Tidak ada (terminal)
```

### 20. Notes dan Constraint

- **No-mock UI**: Panel kosong = N/A; tidak ada nilai hardcode sebagai kebenaran
- **Read-only**: Dashboard membaca cards via API internal; tidak menghitung logika market
- **No localStorage truth**: Hanya preferensi UI di localStorage; kebenaran di IndexedDB
- **Live-adapter DISABLED default**: Tombol live trading disabled
- **Viewer types**: Geometry, Clone, Trade, Replay, Knowledge
- **Anti-mock contract**: Placeholder referensi diadopsi sebagai kontrak field; nilai dari pipeline
- **Empty = N/A**: Sesuai LAW-MASTER-02 (No-Fake Data)
- **Tombol = perintah**: Ke engine main-thread, bukan logika UI
- **Export CSV**: Dari trade markers (card), bukan dari UI state
- **Clock WIB**: UI element, bukan logika (Date.now() di UI diizinkan)
- **Ambient/Animation**: UI element, bukan logika
- **Thread**: Main thread (UI rendering)
