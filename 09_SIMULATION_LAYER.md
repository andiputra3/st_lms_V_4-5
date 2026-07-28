# 09_SIMULATION_LAYER.md

## ST-LMS — Simulation Layer Architecture Mapping

**Date:** 2026-07-28
**Status:** ARCHITECTURE MAPPING — FROZEN
**Sources:** MASTER_SPECIFICATION.html §6, QWEN_14_DOC.html D8, ST_LMS_CORE.js (SIMULATION, REPLAY namespaces)

---

### 1. Responsibility

Simulation Layer bertanggung jawab untuk mengeksekusi niat clone terhadap candle dan menulis marker after-fee (adverse-first). Simulator adalah first-class citizen — clone tidak menghitung PnL sendiri. Layer ini juga mencakup replay engine (6 jenis replay) dan determinism verification.

### 2. Purpose

- Mengeksekusi clone intent terhadap candle data
- Menghitung P&L after-fee dengan adverse-first rule
- Menyediakan 4 jenis simulasi (historical, live, strategy, clone)
- Menyediakan 6 jenis replay (candle, snapshot, trade, clone, knowledge, governance)
- Memverifikasi determinisme dengan dual-run hash comparison
- Mengelola state pipeline (freshState, process, computeAll)

### 3. Input

- Candle data (OHLCV) — fixture atau live feed
- Clone intents — dari CLONE layer
- Config — bounded parameters
- Previous state — checkpoint (untuk resume)

### 4. Output

- `trade_snapshot` card — markers per candle
- Trade markers — ENTRY_MARKER, EXIT_MARKER
- Simulation state — frames, snapshots, cards, markers
- Replay frames — per replay session
- Determinism hash — dual-run comparison

### 5. Dependency Layer

- **Upstream**: CLONE (clone intents), TRADE (trade markers), MARKET (candle data)
- **Downstream**: STATISTICS (trade markers), KNOWLEDGE (snapshots), VIEW (replay data)

### 6. Previous Pipeline

CLONE + TRADE — Simulation mengeksekusi setelah clone intents dibuat.

### 7. Next Pipeline

STATISTICS — Trade markers dari simulation mengalir ke Statistics.

### 8. SQLite Tables yang Digunakan

- `market_candles` — membaca candle data
- `pipeline_runs` — run tracking
- `clones` — clone reference

### 9. SQLite Tables yang Dihasilkan

- `replay_sessions` — replay containers (6 replay kinds)
- `replay_frames` — individual replay frames per session

### 10. Artifact yang Dihasilkan

- Simulation state object: {sym, candles, points, curRun, cageHist, snapshots, frames, cards, markers, oracleHist, darwin, activeClones, oiSeries, gaps, sdv, pb, idGen, clones}
- Per-candle snapshots (9 per candle + benchmark on-demand)
- Immutable cards (via CARD.mk)
- Replay sessions (6 kinds)
- Determinism hash: {h1, h2, ok}

### 11. Validator yang Dibutuhkan

- **Determinism Validator** — 2 run seed sama → checksum identik
- **Adverse-First Validator** — SL beats TP on same candle
- **Fee Validator** — net = gross - fee - slip; WIN only if net > 0
- **Entry = Close Validator** — entry pada close candle FINAL; provisional ditolak
- **MAE/MFE Validator** — dilacak per posisi
- **Persist Serial Validator** — worker kirim hasil; main yang tulis
- **Replay Determinism Validator** — replay reproduktibel bit-per-bit

### 12. Knowledge Entity yang Digunakan

Tidak langsung — Simulation adalah upstream. Knowledge membaca dari snapshots.

### 13. Trading Entity yang Digunakan

- Clone intents — entry/exit decisions dari CLONE
- Trade markers — diproduksi oleh SIM

### 14. Snapshot yang Digunakan

Semua 10 snapshots diproduksi dalam simulation process().

### 15. Benchmark yang Digunakan

Tidak langsung — Benchmark menggunakan simulation untuk WASIT walk-forward.

### 16. Dashboard Component yang Digunakan

- Simulation UI — jenis simulasi selector + results
- Replay Viewer — scrubber + step + auto-play
- Geometry Chart — candle + ST + cage + markers

### 17. Mandatory atau Optional

**MANDATORY** — Simulation adalah first-class citizen. Tanpa simulation, tidak ada trade execution.

### 18. Specification Reference

- MASTER_SPECIFICATION.html §6 (Lifecycle: Close + Marker stage)
- MASTER_SPECIFICATION.html §9.3 (Replay Philosophy)
- QWEN_14_DOC.html D8 (Simulation Architecture)
- QWEN_14_DOC.html D9 (Replay Architecture)
- ST_LMS_CORE.js lines 409-573 (SIMULATION, BENCHMARK, REPLAY namespaces)

### 19. Build Order Recommendation

```
Build Order: 9
Dependencies: CLONE, TRADE, POSITION, MARKET
Build setelah: CLONE + TRADE + POSITION
Build sebelum: STATISTICS
```

### 20. Notes dan Constraint

- **4 jenis simulasi**: Historical (fixture/IndexedDB), Live (feed 1m), Strategy (1 clone terisolasi), Clone (3 clone bersamaan)
- **6 jenis replay**: Candle, Snapshot, Trade, Clone, Knowledge, Governance
- **Adverse-First**: SL & TP same candle → SL menang (konservatif, jujur)
- **Fee Berlapis**: net = gross - fee_murni - slip_seeded - safety; WIN only net > 0
- **Entry = Close**: Entry pada close candle FINAL; provisional ditolak
- **MAE/MFE**: Dilacak per posisi → bahan kalibrasi SL/TP (CERMIN-EXIT)
- **Persist Serial**: Worker kirim hasil; main yang tulis IndexedDB → nol race
- **Resume**: Replay membaca checkpoints; bila absen, recompute hanya hot-window 3h
- **Determinism**: 2 run dengan seed sama → checksum identik
- **freshState**: Membuat state baru per simbol dengan semua komponen
- **process**: Memproses 1 candle melalui seluruh pipeline
- **computeAll**: Memproses seluruh candles
- **runActive**: computeAll + persist ke WORKSPACE
- **Replay Worker**: Paralel antar-simbol untuk replay panjang
- **No double exit**: Adverse-first memastikan tidak ada double exit per clone per candle
