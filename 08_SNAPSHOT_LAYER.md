# 08_SNAPSHOT_LAYER.md

## ST-LMS — Snapshot Layer Architecture Mapping

**Date:** 2026-07-28
**Status:** ARCHITECTURE MAPPING — FROZEN
**Sources:** MASTER_SPECIFICATION.html §9, QWEN_14_DOC.html D6, ST_LMS_CORE.js (SIMULATION.process)

---

### 1. Responsibility

Snapshot Layer bertanggung jawab untuk membungkus (wrap) output pipeline menjadi immutable cards per closed candle. Snapshot adalah pembungkusan terpartisi — bukan komputasi baru. Setiap snapshot dibekukan (Object.freeze + checksum + lineage), disimpan append-only, dan dikonsumsi read-only oleh layer hilir.

### 2. Purpose

- Membungkus output pipeline menjadi immutable cards
- Memisahkan field W (frozen stored) dan OD (on-demand deterministik)
- Menjamin determinisme replay (snapshot sequence = bit-per-bit identik)
- Menyediakan lineage dan audit trail untuk setiap fakta
- Mencegah drift data (satu sumber, banyak turunan)

### 3. Input

- Output dari setiap pipeline stage (market, truth, structure, evidence, clone, trade, statistics, knowledge, benchmark, prediction)

### 4. Output

10 snapshot cards per closed candle:

| # | Snapshot | Producer | W Fields | OD Fields |
|---|----------|----------|----------|-----------|
| 1 | Market | MARKET | ts, symbol, tf, OHLCV, taker_buy_ratio, data_status, gap_flag, wib_iso | — |
| 2 | Truth | TRUTH | close, st, st_canon, stDir, color, atr, ema, macd_hist, dist, distAtr, rsi, wpr, point_status | — |
| 3 | Structure | STRUCTURE | cage{status,upper,lower,pp,rangeAtr,breakout}, ladder, nearest, phase, wave | dist_ceiling, dist_floor |
| 4 | Evidence | EVIDENCE | dir_bus, exit_bus, correction_bus, mtf, max_score, data_quality | — |
| 5 | Clone | CLONE ×3 | per_clone{clone_id, bias, observation, open_position, grid_fills} | — |
| 6 | Trade | SIM | markers[{kind,clone,side,reason,entry,exit,gross,fee,slip,net,result,mae,mfe,hold}] | — |
| 7 | Statistics | STATISTICS | per_clone{sample,win_rate,expectancy,pf,mae,mfe,fee_drag,wrong_rate} | all (from Trade) |
| 8 | Knowledge | KNOWLEDGE | academy_artifacts, oracle_match, hivemind, cermin, librarian, darwin_proposals | — |
| 9 | Benchmark | BENCHMARK | param, base, cand, folds, totals, gates, per_fold, verdict | trigger-only |
| 10 | Prediction | PREDICTION | intelligence_score, dominant_bias, empirical_win_rate, similarity_score, no_model | empirical_win_rate |

### 5. Dependency Layer

- **Upstream**: Semua pipeline stages (MARKET → GOVERNANCE)
- **Downstream**: Semua downstream consumers (REPLAY, VIEW, AUDIT, CONSUMER)

### 6. Previous Pipeline

Cross-cutting — Snapshot diproduksi di setiap pipeline stage.

### 7. Next Pipeline

Cross-cutting — Snapshot dikonsumsi oleh semua downstream layers.

### 8. SQLite Tables yang Digunakan

Snapshot TIDAK membaca SQLite tables. Snapshot DIPRODUKSI dan DISIMPAN ke SQLite.

### 9. SQLite Tables yang Dihasilkan

Setiap snapshot memiliki corresponding SQLite table:
- Market → `market_candles`
- Truth → `truth_snapshots`
- Structure → `structure_snapshots`
- Evidence → `evidence_snapshots`
- Clone → `clone_observations`
- Trade → `trade_markers`
- Statistics → `trade_statistics`
- Knowledge → `knowledge_artifacts`
- Benchmark → `benchmark_runs` + `benchmark_cases`
- Prediction → `predictions`

### 10. Artifact yang Dihasilkan

- 10 immutable snapshot cards per closed candle
- Setiap card: entity_id, entity_type, entity_state, entity_version, timestamp_wib, timestamp_ms, component_name, source_file, dependencies[], payload{}, checksum (SHA-256)
- Card lineage: dependencies = [candle_id, config_version]

### 11. Validator yang Dibutuhkan

- **Checksum Validator** — SHA-256 verify pada setiap card
- **Lineage Validator** — dependencies mencakup candle_id + config_version
- **Immutability Validator** — Object.freeze pada setiap card
- **W/OD Validator** — W fields disimpan beku; OD fields deterministik dari sumber beku
- **NULL+Status Validator** — field tak terhitung = NULL + status (bukan nilai netral)
- **10-Snapshot Validator** — 10 snapshot per closed candle
- **FINAL-only Validator** — Snapshot FINAL hanya dari candle CLOSED
- **No-Model Validator** — Prediction Snapshot tidak memuat output model prediktif

### 12. Knowledge Entity yang Digunakan

Snapshot menyimpan knowledge artifacts (diproduksi oleh KNOWLEDGE layer).

### 13. Trading Entity yang Digunakan

Snapshot menyimpan trade markers dan clone observations.

### 14. Snapshot yang Digunakan

Snapshot adalah layer itu sendiri — memproduksi dan menyimpan semua snapshot.

### 15. Benchmark yang Digunakan

Snapshot menyimpan benchmark results (on-demand, tidak per candle).

### 16. Dashboard Component yang Digunakan

Semua dashboard components membaca snapshot cards.

### 17. Mandatory atau Optional

**MANDATORY** — Snapshot adalah fondasi untuk determinisme, replay, dan audit.

### 18. Specification Reference

- MASTER_SPECIFICATION.html §9 (Market Snapshot Master Constitution)
- MASTER_SPECIFICATION.html §3 (Constitution Freeze Matrix — Snapshot constitution)
- MASTER_SPECIFICATION.html §16 (Snapshot Lengkap & Immutable — LAW-MASTER-16)
- QWEN_14_DOC.html D6 (Market Snapshot Architecture)
- ST_LMS_CORE.js lines 423-449 (snapshot construction in process())

### 19. Build Order Recommendation

```
Build Order: Cross-cutting (dibangun bersama setiap pipeline stage)
Dependencies: CARD factory, CRYPTO (SHA-256), ID generator
Build setelah: Bedrock (S1)
Build bersama: Setiap pipeline stage (S3-S14)
```

### 20. Notes dan Constraint

- **Immutable**: Sekali ditulis, tak berubah; koreksi = snapshot versi baru ber-lineage
- **W fields**: Disimpan beku (frozen stored)
- **OD fields**: Boleh on-demand (deterministik dari sumber beku) — mencegah drift & hemat storage
- **NULL+status**: Field tak terhitung = NULL+status, BUKAN nilai netral (LAW-MASTER-02)
- **FINAL only**: Snapshot FINAL hanya dari candle CLOSED; PROVISIONAL tidak melahirkan snapshot final
- **Benchmark absent**: Benchmark Snapshot absen pada closed candle biasa (on-demand saja)
- **No model**: Prediction Snapshot dilarang memuat output model prediktif
- **Amendemen**: Menambah/menghapus field snapshot = amandemen §3 (constitution_version baru)
- **Replay**: Membaca card, bukan menghitung ulang; reproduktibel bit-per-bit
- **Resume**: Via checkpoints; bila absen, recompute hanya hot-window 3h
- **Append-only**: Store IndexedDB cold/warm; index by type+ts & config+ts
- **One source**: Satu sumber per besaran (dist hanya di Truth; dist_ceiling/floor hanya di Structure)
- **Card factory**: CARD.mk(type, payload, deps, ts, idGen) → Object.freeze + checksum
