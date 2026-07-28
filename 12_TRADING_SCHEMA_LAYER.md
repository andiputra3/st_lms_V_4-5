# 12_TRADING_SCHEMA_LAYER.md

## ST-LMS — Trading Schema Layer Architecture Mapping

**Date:** 2026-07-28
**Status:** ARCHITECTURE MAPPING — FROZEN
**Sources:** MASTER_SPECIFICATION.html §6, §7, ST_LMS_CORE.js (CLONE_SHARED, LONG_CLONE, SHORT_CLONE, GRID_CLONE, TRADE, FEE namespaces), TRADING_SCHEMA_FREEZE.md, DECISION_TREE_FREEZE.md

---

### 1. Responsibility

Trading Schema Layer mendefinisikan seluruh skema trading ST-LMS: LONG, SHORT, GRID, WAIT, NO TRADE, dan WARMUP. Layer ini adalah blueprint yang mendefinisikan bagaimana setiap clone berperilaku dalam setiap kondisi market, kapan entry, kapan exit, kapan wait, dan kapan tidak trading. Trading Schema adalah kontrak yang mengikat implementasi trading.

### 2. Purpose

- Mendefinisikan skema trading untuk LONG, SHORT, dan GRID
- Mendefinisikan kondisi WAIT (observasi tanpa entry)
- Mendefinisikan kondisi NO TRADE (observasi mandatory dengan alasan)
- Mendefinisikan kondisi WARMUP (data tidak mencukupi)
- Menjadi referensi tunggal untuk semua aturan trading
- Memastikan konsistensi antara spesifikasi dan implementasi

### 3. Input

- Market conditions (phase, wave, cage, stDir)
- Indicator values (dari Truth, Structure, Evidence)
- Clone state (positions, equity)
- Config (bounded parameters)

### 4. Output

- Trading decisions: ENTRY, EXIT, WAIT, NO TRADE, WARMUP
- Entry reasons: CORRIDOR, GRID_FILL
- No-entry reasons: STDIR_OR_DIRBUS_MISMATCH, OUT_OF_CORRIDOR, EXPECTED_MOVE_LESS_THAN_REQUIRED, GLOBAL_RISK_BREACH, POSITION_ALREADY_OPEN, CAGE_NONE, WARMUP
- Exit reasons: WRONG_ENTRY_EARLY, WRONG_ENTRY_GEOM, HYPOTHESIS_INVALID, SL, TP, EXIT_BUS, TIME_EXIT, RANGE_BREAK, GRID_TP, STOP_ALL

### 5. Dependency Layer

- **Upstream**: STRUCTURE (cage, phase), EVIDENCE (buses), TRUTH (indicators)
- **Downstream**: TRADING (mengimplementasikan schema)

### 6. Previous Pipeline

EVIDENCE — Trading Schema membaca data dari Evidence/Structure/Truth.

### 7. Next Pipeline

TRADING — Trading Schema diterapkan oleh Trading Layer.

### 8. SQLite Tables yang Digunakan

Tidak langsung — Trading Schema adalah definisi, bukan runtime. Trading Layer yang membaca SQLite.

### 9. SQLite Tables yang Dihasilkan

Tidak ada — Trading Schema tidak menulis ke SQLite.

### 10. Artifact yang Dihasilkan

- Trading Schema definitions (dokumentasi)
- Entry condition matrices
- Exit priority chains
- Market condition → trading behavior mappings

### 11. Validator yang Dibutuhkan

- **Schema Compliance Validator** — implementasi sesuai dengan schema
- **Entry Conjunction Validator** — semua kondisi entry terpenuhi
- **Exit Priority Validator** — urutan exit sesuai priority chain
- **Forbidden Indicator Validator** — W%R/MACD/RSI tidak untuk entry
- **Market Condition Validator** — clone aktif sesuai kondisi market

### 12. Knowledge Entity yang Digunakan

Tidak langsung — Knowledge membaca hasil trading, bukan schema.

### 13. Trading Entity yang Digunakan

| Schema | Clone | Kondisi |
|--------|-------|---------|
| LONG | LONG | UPTREND, BREAKOUT_UP |
| SHORT | SHORT | DOWNTREND, BREAKOUT_DOWN |
| GRID | GRID | SIDEWAY_COMPRESSION, LOOSE_SIDEWAY |
| WAIT | All | Kondisi entry tidak terpenuhi |
| NO TRADE | All | Observasi mandatory dengan alasan |
| WARMUP | All | Data tidak mencukupi |

### 14. Snapshot yang Digunakan

Tidak langsung — Schema adalah definisi.

### 15. Benchmark yang Digunakan

Tidak langsung — Schema menjadi acuan untuk benchmark validation.

### 16. Dashboard Component yang Digunakan

- Trading Schema Viewer — menampilkan aturan trading per clone
- Market Condition Panel — menampilkan kondisi market saat ini
- Entry/Exit Reason Panel — menampilkan alasan entry/exit

### 17. Mandatory atau Optional

**MANDATORY** — Trading Schema adalah kontrak yang mengikat seluruh trading behavior.

### 18. Specification Reference

- MASTER_SPECIFICATION.html §6 (Master Trading Lifecycle)
- MASTER_SPECIFICATION.html §7 (Clone Master)
- MASTER_SPECIFICATION.html §5 (Indicator Authority Matrix)
- TRADING_SCHEMA_FREEZE.md
- DECISION_TREE_FREEZE.md
- ST_LMS_CORE.js lines 287-369

### 19. Build Order Recommendation

```
Build Order: 12 (definisi — tidak ada kode)
Dependencies: STRUCTURE, EVIDENCE, TRUTH (untuk definisi)
Build setelah: Semua upstream layers didefinisikan
Build sebelum: TRADING (implementasi)
```

### 20. Notes dan Constraint

- **LONG Schema**: Entry if stDir=+1 ∧ EMA-slope>0 ∧ vd>0 ∧ corridor.inZone ∧ fee_safe ∧ global_ok ∧ open==null
- **SHORT Schema**: Mirror LONG; stDir=-1, EMA-slope<0, vd<0
- **GRID Schema**: Entry if cage_valid ∧ width≥3×req ∧ breakout=NONE ∧ pp in zone ∧ fills_per_side<max
- **WAIT Schema**: Clone mengamati tapi tidak entry (alasan wajib)
- **NO TRADE Schema**: Observasi mandatory; no_entry_reason wajib diisi
- **WARMUP Schema**: Semua clone mengamati; tidak entry sampai data cukup
- **Exit Priority**: 1.WRONG_ENTRY_EARLY → 2.WRONG_ENTRY_GEOM → 3.HYPOTHESIS_INVALID → 4.SL → 5.HOLD-VETO → 6.TP → 7.EXIT_BUS → 8.TIME_EXIT
- **HOLD-Veto**: MACD expanding + velocity with trend → delay TP
- **Adverse-First**: SL beats TP on same candle
- **Fee Berlapis**: 0.7% REQUIRED_MOVE; fee_murni 0.04-0.10%; WIN only net > 0
- **Market Conditions**: 13 kondisi (TRENDING_UP, TRENDING_DOWN, SIDEWAY_COMPRESSION, LOOSE_SIDEWAY, REVERSAL_UP, REVERSAL_DOWN, BREAKOUT_UP, BREAKOUT_DOWN, EXHAUSTION_UP, EXHAUSTION_DOWN, RANGE_COMPRESSING, CHAOS, WARMUP)
- **Wave → MTF Mapping**: 13 wave structures → MTF sector + score
- **Forbidden**: W%R/MACD/RSI untuk entry; GRID di trend; trailing ATR per fill GRID
