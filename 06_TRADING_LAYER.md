# 06_TRADING_LAYER.md

## ST-LMS — Trading Layer Architecture Mapping

**Date:** 2026-07-28
**Status:** ARCHITECTURE MAPPING — FROZEN
**Sources:** MASTER_SPECIFICATION.html §6, §7, ST_LMS_CORE.js (CLONE_SHARED, LONG_CLONE, SHORT_CLONE, GRID_CLONE, TRADE, POSITION namespaces)

---

### 1. Responsibility

Trading Layer bertanggung jawab untuk seluruh lifecycle trading: observasi clone, entry validation, position management, profit management, exit validation, dan trade marker generation. Layer ini mencakup LONG, SHORT, dan GRID clone yang beroperasi secara terisolasi dengan sub-ledger masing-masing. Trading adalah PER-CLONE (3× per candle).

### 2. Purpose

- Mengamati market dan mencatat hipotesis per clone (mandatory, termasuk no-trade)
- Memvalidasi entry conditions (conjunction gate)
- Mengelola posisi terbuka (MAE/MFE tracking)
- Mengamankan profit (partial TP, trailing stop, breakeven)
- Memutuskan exit dan alasannya
- Menghasilkan trade markers dengan P&L after-fee adverse-first

### 3. Input

- Shared snapshots: truth_snapshot, structure_snapshot, evidence_snapshot (via Card Sharing)
- Clone ledger: positions, gridFills, equity, capital, lastObs
- Global context: required_move, globalOk, idx

### 4. Output

- `clone_observation` per clone per candle (mandatory)
- `ENTRY_MARKER` (saat entry)
- `EXIT_MARKER` (saat exit, dengan P&L)
- `trade_snapshot` card (aggregate markers)
- Updated clone ledger (positions, equity, capital)

### 5. Dependency Layer

- **Upstream**: EVIDENCE (evidence_snapshot), STRUCTURE (structure_snapshot), TRUTH (truth_snapshot)
- **Downstream**: STATISTICS (trade_markers → statistics_snapshot), SIMULATION (executes trade markers)

### 6. Previous Pipeline

EVIDENCE — Trading membaca shared snapshots dari Evidence/Structure/Truth.

### 7. Next Pipeline

STATISTICS — Trade markers mengalir ke Statistics untuk agregasi.

### 8. SQLite Tables yang Digunakan

- `clones` — clone entities (LONG/SHORT/GRID)
- `truth_snapshots` — membaca stDir, close, atr, distAtr
- `structure_snapshots` — membaca cage, nearest, phase
- `evidence_snapshots` — membaca dir_bus, exit_bus, correction_bus

### 9. SQLite Tables yang Dihasilkan

- `clone_observations` — per-candle observation per clone
- `trade_markers` — ENTRY/EXIT/PARTIAL/BREAKEVEN/TRAILING/HOLD/PASS/NO_TRADE
- `positions` — position lifecycle
- `position_timeline` — event timeline per position

### 10. Artifact yang Dihasilkan

- Clone observation cards (3 per candle — LONG, SHORT, GRID)
- ENTRY_MARKER: {ts, clone, side, kind=ENTRY, reason, entry, sl, tp}
- EXIT_MARKER: {ts, clone, side, kind=EXIT, reason, entry, exit, gross, fee, slip, net, result, mae, mfe, hold}
- Position state: {side, entry, sl, tp, mae, mfe, hold_c}
- Grid fills: [{side, entry, oi_idx}]

### 11. Validator yang Dibutuhkan

- **Entry Conjunction Validator** — 5-7 kondisi harus ALL TRUE
- **Exit Priority Validator** — urutan prioritas exit (1-8)
- **Adverse-First Validator** — SL beats TP on same candle
- **Fee Safety Validator** — expected_move ≥ required_move
- **Global Risk Validator** — gross/net exposure limits
- **Wrong Entry Validator** — velocity/geometry-based detection (hold ≤ 2)
- **HOLD-Veto Validator** — MACD expanding + velocity → delay TP
- **Time Exit Validator** — hold ≥ TIME_EXIT_CANDLES ∧ profit < required
- **3-Observation Validator** — 3 observation cards per candle (mandatory)

### 12. Knowledge Entity yang Digunakan

Tidak langsung — Trading adalah upstream. Knowledge membaca trade_markers.

### 13. Trading Entity yang Digunakan

| Entity | Clone | Deskripsi |
|--------|-------|-----------|
| Directional Entry | LONG/SHORT | stDir + EMA + vd + corridor + fee_safe + global_ok |
| GRID Entry | GRID | cage_valid + width≥3×req + breakout=NONE + pp in zone |
| Position Management | All | MAE/MFE tracking, hold counter |
| Exit Decision | All | Priority-ordered exit reasons |
| Fee Calculation | All | gross - fee_murni - slip; WIN only if net > 0 |
| Adverse-First | All | SL beats TP on same candle |
| HOLD-Veto | LONG/SHORT | MACD expanding delays TP |

### 14. Snapshot yang Digunakan

- `truth_snapshot` — stDir, close, atr, emaSlope, volDelta, rsi, wpr, vel, acc, macdHist
- `structure_snapshot` — cage, nearest, phase, wave
- `evidence_snapshot` — dir_bus, exit_bus, correction_bus

### 15. Benchmark yang Digunakan

Tidak langsung — Trade markers menjadi input untuk WASIT benchmark.

### 16. Dashboard Component yang Digunakan

- Clone Cards — LONG/SHORT/GRID observation + position status
- Trade History Table — semua markers dengan P&L
- Equity Curve — capital evolution per clone
- Entry/Exit Indicators — visual markers pada geometry chart

### 17. Mandatory atau Optional

**MANDATORY** — Trading adalah inti dari ST-LMS. "Trade is Optional, Learning is Mandatory" berarti observasi tetap wajib walau tidak entry.

### 18. Specification Reference

- MASTER_SPECIFICATION.html §6 (Master Trading Lifecycle)
- MASTER_SPECIFICATION.html §7 (Clone Master)
- MASTER_SPECIFICATION.html §9 (Snapshot Master)
- QWEN_14_DOC.html D5 (Pipeline Architecture)
- ST_LMS_CORE.js lines 287-369 (TRADE, POSITION, CLONE_SHARED, LONG_CLONE, SHORT_CLONE, GRID_CLONE)
- TRADING_SCHEMA_FREEZE.md
- DECISION_TREE_FREEZE.md

### 19. Build Order Recommendation

```
Build Order: 6
Dependencies: STRUCTURE, EVIDENCE, TRUTH, SQLite Foundation
Build setelah: EVIDENCE
Build sebelum: STATISTICS, SIMULATION
```

### 20. Notes dan Constraint

- **PER-CLONE (3×)**: Clone observation, entry, position, exit dijalankan 3× (LONG, SHORT, GRID)
- **Sub-ledger terisolasi**: Setiap clone memiliki ledger sendiri; statistik tidak dicampur
- **Card Sharing**: Truth/Structure/Evidence dihitung 1×, di-share ke 3 clone
- **1 Candle = 3 Knowledge**: LONG/SHORT/GRID masing-masing menulis observasi (mandatory)
- **No entry without reason**: Jika tidak entry, no_entry_reason wajib diisi
- **Only 1 position per clone**: Tidak ada pyramiding
- **LONG entry conjunction**: stDir=+1 ∧ EMA-slope>0 ∧ vd>0 ∧ corridor.inZone ∧ fee_safe ∧ global_ok ∧ open==null
- **SHORT entry conjunction**: stDir=-1 ∧ EMA-slope<0 ∧ vd<0 ∧ corridor.inZone ∧ fee_safe ∧ global_ok ∧ open==null
- **GRID entry conjunction**: cage_valid ∧ width≥3×req ∧ breakout=NONE ∧ pp in zone ∧ fills_per_side<max
- **Exit priority**: 1.WRONG_ENTRY_EARLY → 2.WRONG_ENTRY_GEOM → 3.HYPOTHESIS_INVALID → 4.SL → 5.HOLD-VETO → 6.TP → 7.EXIT_BUS → 8.TIME_EXIT
- **Adverse-first**: SL dan TP same candle → SL menang
- **Fee berlapis**: net = gross - fee_murni - slip; WIN only if net > 0
- **W%R/MACD/RSI**: HANYA untuk exit, TIDAK untuk entry
- **GRID**: Buta arah; tidak pakai stDir/Direction/MTF/RSI/W%R/MACD
- **GRID aktif hanya di kompresi**: cage NONE → GRID tidak aktif
- **Thread**: Main thread (hot, sequential per symbol)
