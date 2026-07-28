# 05_STRUCTURE_LAYER.md

## ST-LMS — Structure Layer Architecture Mapping

**Date:** 2026-07-28
**Status:** ARCHITECTURE MAPPING — FROZEN
**Sources:** MASTER_SPECIFICATION.html §4, §6, ST_LMS_CORE.js (STRUCTURE namespace), QWEN_14_DOC.html D5

---

### 1. Responsibility

Structure Layer bertanggung jawab untuk membangun geometri market dari truth_snapshot. Layer ini membangun line segments, slope transitions, wave classification (13 struktur), cage dengan versioning, ladder patterns, nearest support/resistance, market phase, dan distance metrics. Structure adalah single source of truth untuk semua geometri spasial market.

### 2. Purpose

- Membangun line segments dari Supertrend points
- Membangun slope transitions antar lines
- Mengklasifikasi wave structures (13 jenis)
- Menghitung cage dengan wall resolution dan versioning (v0→v1→v2)
- Menentukan market phase dari cage + wave + stDir
- Menemukan nearest support/resistance
- Menganalisis ladder patterns
- Memproduksi structure_snapshot

### 3. Input

- `truth_snapshot` — points (st, st_canon, color, ts), price (close), atr
- Current line run — state dari line yang sedang berjalan
- Lineage lines — history lines untuk cage resolution

### 4. Output

- `structure_snapshot` card (immutable)
- W fields: cage{status,upper,lower,pp,rangeAtr,breakout,upVi,lowVi,cross,pressureUp,pressureDn,versioning}, ladder, nearest{support,resistance}, phase, wave, pending_wave
- OD fields: dist_ceiling, dist_floor, ceiling_floor_ratio, dist_delta

### 5. Dependency Layer

- **Upstream**: TRUTH (truth_snapshot)
- **Downstream**: EVIDENCE (structure_snapshot → evidence_snapshot), CLONE (structure_snapshot via Card Sharing), GRID (cage data)

### 6. Previous Pipeline

TRUTH — Structure membaca truth_snapshot dari TRUTH.

### 7. Next Pipeline

EVIDENCE — Structure snapshot mengalir ke Evidence untuk bus construction.
CLONE — Structure snapshot di-share ke clone untuk trading decisions.

### 8. SQLite Tables yang Digunakan

- `truth_snapshots` — membaca truth_id, close, st, atr
- `market_candles` — membaca candle_id reference

### 9. SQLite Tables yang Dihasilkan

- `structure_snapshots` — per-candle market geometry
- `wave_history` — wave line details (per structure, up to 6 lines)
- `cage_history` — cage version history

### 10. Artifact yang Dihasilkan

- `structure_snapshot` card (immutable)
- Line segments array (st, key, s, e, n, dom, role)
- Slope transitions array (s, e, dir, col, n, pat, stf)
- Wave objects (mem 6 lines + 5 transitions, structure classification, status)
- Cage object (upper, lower, pp, rangeAtr, status, breakout, versioning)
- Market phase object (cage_status, wave_structure, stDir, phase)
- Ladder analysis (support_stepped, resistance_stepped)
- Nearest S/R (support, resistance)

### 11. Validator yang Dibutuhkan

- **HUKUM CAGE Validator** — 2 dinding = compression; 1 dinding = trend
- **Wave Validator** — < 6 lines = PENDING_WAVE (no padding)
- **Escape Path Validator** — jarak ≥ CAGE_WALL_MIN_DISTANCE_ATR × ATR
- **Versioning Validator** — v0→v1→v2, boundary max-2
- **Structure Status Validator** — WARMUP/VALID/INSUFFICIENT

### 12. Knowledge Entity yang Digunakan

Tidak langsung — Structure adalah upstream. Knowledge membaca structure_snapshot.

### 13. Trading Entity yang Digunakan

Tidak langsung — Clone membaca structure_snapshot via Card Sharing untuk:
- LONG: floor (SL), ceiling (TP), cage status
- SHORT: ceiling (SL), floor (TP), cage status
- GRID: cage upper/lower/pp/rangeAtr/breakout

### 14. Snapshot yang Digunakan

- `truth_snapshot` — dari TRUTH

### 15. Benchmark yang Digunakan

Tidak ada — Benchmark adalah downstream.

### 16. Dashboard Component yang Digunakan

- Cage Panel — menampilkan status, upper, lower, pp, rangeAtr, breakout
- Wave Panel — menampilkan structure, phase, pending count
- Versioning Panel — menampilkan support/resistance versions (Sv0, Rv0, v1, v2)
- Ladder Panel — menampilkan stepped patterns, nearest S/R
- Geometry Viewer — candle chart + ST + cage lines + versioning

### 17. Mandatory atau Optional

**MANDATORY** — Structure adalah fondasi geometri spasial untuk semua trading decisions.

### 18. Specification Reference

- MASTER_SPECIFICATION.html §4 (Market Geometry Master)
- MASTER_SPECIFICATION.html §6 (Lifecycle: Structure stage)
- MASTER_SPECIFICATION.html §7 (Clone Master — cage usage)
- QWEN_14_DOC.html D5 (Pipeline Architecture)
- ST_LMS_CORE.js lines 187-253 (STRUCTURE namespace)

### 19. Build Order Recommendation

```
Build Order: 5
Dependencies: TRUTH, SQLite Foundation
Build setelah: TRUTH
Build sebelum: EVIDENCE, CLONE
```

### 20. Notes dan Constraint

- **Line Builder**: Group consecutive ST points with same st_canon; line = ≥ 4 members
- **Slope Builder**: Transitions between lines; 6 pattern types (STAIRCASE_UP/DOWN, PARABOLIC_UP/DOWN, REVERSAL_TRANSITION, SPIKE_UP/DOWN, FLAT_NOISE)
- **Wave Builder**: 13 wave structures (all reachable post C2 fix)
- **Wave < 6**: PENDING_WAVE — tidak boleh dipadding
- **Cage Engine**: Wall resolution dengan versioning (v0=v0 terdekat, v1/v2=escape path)
- **Escape Path**: Mencari dinding "nyaman" (jarak ≥ threshold × ATR)
- **HUKUM CAGE**: 2 dinding valid ⇔ kompresi/sideway; 1 dinding ⇔ trend (jarak seberang = NULL)
- **Cage Status**: NONE (1 wall) / VALID_COMPRESSION (tight) / LOOSE_SIDEWAY (wide)
- **Breakout**: NONE / IMMINENT_UP / IMMINENT_DOWN / SQUEEZE
- **Phase**: UPTREND / DOWNTREND / TRANSITION / SIDEWAY_COMPRESSION
- **Thread**: Main thread (hot, sequential)
- **Card Sharing**: structure_snapshot di-share ke Evidence dan Clone
- **13 Wave Structures**: STRONG_ACCUMULATION, STRONG_DISTRIBUTION, CONTINUATION_UP, CONTINUATION_DOWN, CONFIRMED_RANGE, RANGE_EXPANDING, RANGE_COMPRESSING, REVERSAL_UP, REVERSAL_DOWN, EXHAUSTION_UP, EXHAUSTION_DOWN, SIDEWAY, CHAOS
