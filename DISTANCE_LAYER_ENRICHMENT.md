# DISTANCE LAYER ENRICHMENT — Patch 01

## ST-LMS Architecture Enrichment Patch V1

**Date:** 2026-07-28
**Status:** ENRICHMENT ANALYSIS — FROZEN
**Sources:** MASTER_SPECIFICATION.html §4, ST_LMS_CORE.js (TRUTH, EVIDENCE namespaces)

---

## 1. ANALISIS: Apakah Distance Layer pantas menjadi logical layer tersendiri?

### 1.1 Status Saat Ini dalam Referensi

Berdasarkan MASTER_SPECIFICATION.html §4 (Market Geometry Master):

| Entitas | Lapisan Asal | Authority |
|---------|-------------|-----------|
| Supertrend (st, stDir, color) | **TRUTH** | Satu-satunya sumber garis aktif |
| Distance-to-ST (dist, distAtr) | **TRUTH** | Satu-satunya jarak beku di Truth |
| Distance-Ceiling | **STRUCTURE (OD)** | ceiling − close; NULL pada downtrend |
| Distance-Floor | **STRUCTURE (OD)** | close − floor; NULL pada uptrend |

Berdasarkan ST_LMS_CORE.js:
- `dist` dan `distAtr` dihitung di `TRUTH.PointBuilder.build()` (line 178)
- `dist_ceiling` dan `dist_floor` dihitung di `EVIDENCE.correctionBus()` (lines 270-271)
- `ST_DIST_VOL` (sdv, p90) dihitung di `EVIDENCE.StDistVol` (lines 272-274)

**Kesimpulan:** Distance TIDAK ada sebagai layer terpisah dalam referensi. Distance metrics tersebar di TRUTH (dist, distAtr), STRUCTURE (dist_ceiling, dist_floor sebagai OD), dan EVIDENCE (ST_DIST_VOL).

### 1.2 Analisis: Apakah Distance pantas sebagai logical layer?

**ARGUMEN PRO (Distance sebagai logical layer):**
1. Distance metrics memiliki consumer yang jelas: CLONE (corridor, fee_safe), EVIDENCE (correction_bus), KNOWLEDGE (Academy distance_bucket)
2. Distance memiliki 14 sub-komponen yang dapat dikelompokkan secara logis
3. Distance adalah jembatan antara geometri (TRUTH/STRUCTURE) dan keputusan trading (CLONE)
4. Distance memiliki aturan authority sendiri dalam Indicator Authority Matrix (§5)

**ARGUMEN KONTRA (Distance tetap di TRUTH/STRUCTURE):**
1. MASTER_SPECIFICATION tidak mendefinisikan Distance sebagai layer terpisah
2. dist dan distAtr adalah W fields di truth_snapshot — memisahkannya akan melanggar "satu sumber per besaran"
3. dist_ceiling dan dist_floor adalah OD fields di structure_snapshot — dihitung dari sumber beku

**KEPUTUSAN:** Distance pantas sebagai **LOGICAL SUB-LAYER** (bukan physical layer terpisah). Distance metrics tetap diproduksi di TRUTH (dist, distAtr) dan STRUCTURE (dist_ceiling, dist_floor) sesuai referensi, tetapi dikelompokkan secara logis untuk kejelasan arsitektur.

---

## 2. KOMPONEN DISTANCE LAYER

### 2.1 Distance to ST

| Atribut | Nilai |
|---------|-------|
| **Authority** | TRUTH — PointBuilder (W field di truth_snapshot) |
| **Rumus** | `dist = |close - st|` |
| **Dependency** | TRUTH (close, st) |
| **Consumer** | CLONE (corridor), EVIDENCE (ST_DIST_VOL), KNOWLEDGE (Academy bucket) |
| **Pipeline** | Stage 3 (TRUTH) — SHARED |
| **SQLite** | `truth_snapshots.dist_to_st` |
| **Snapshot** | truth_snapshot (W field) |

### 2.2 Distance ATR

| Atribut | Nilai |
|---------|-------|
| **Authority** | TRUTH — PointBuilder (W field di truth_snapshot) |
| **Rumus** | `distAtr = dist / atr` |
| **Dependency** | TRUTH (dist, atr) |
| **Consumer** | CLONE (volatility-adjusted corridor), KNOWLEDGE (Academy distance_bucket: OPTIMAL≤0.5, NEAR≤1, EXTENDED≤2, FAR>2), ORACLE (vector dimension) |
| **Pipeline** | Stage 3 (TRUTH) — SHARED |
| **SQLite** | `truth_snapshots.dist_atr` |
| **Snapshot** | truth_snapshot (W field) |

### 2.3 Distance Ceiling

| Atribut | Nilai |
|---------|-------|
| **Authority** | STRUCTURE — correctionBus (OD field di structure_snapshot) |
| **Rumus** | `dist_ceiling = cage.upper - close` |
| **Dependency** | STRUCTURE (cage.upper), TRUTH (close) |
| **Consumer** | CLONE (LONG: fee_safe check, expected_move), TRADING_SCHEMA (entry condition) |
| **Pipeline** | Stage 5 (EVIDENCE) — SHARED |
| **SQLite** | `structure_snapshots.dist_ceiling` |
| **Snapshot** | structure_snapshot (OD field) |
| **NULL rule** | NULL pada downtrend (tidak ada ceiling) |

### 2.4 Distance Floor

| Atribut | Nilai |
|---------|-------|
| **Authority** | STRUCTURE — correctionBus (OD field di structure_snapshot) |
| **Rumus** | `dist_floor = close - cage.lower` |
| **Dependency** | STRUCTURE (cage.lower), TRUTH (close) |
| **Consumer** | CLONE (SHORT: fee_safe check, expected_move), TRADING_SCHEMA (entry condition) |
| **Pipeline** | Stage 5 (EVIDENCE) — SHARED |
| **SQLite** | `structure_snapshots.dist_floor` |
| **Snapshot** | structure_snapshot (OD field) |
| **NULL rule** | NULL pada uptrend (tidak ada floor) |

### 2.5 Distance Volatility (ST_DIST_VOL)

| Atribut | Nilai |
|---------|-------|
| **Authority** | EVIDENCE — StDistVol |
| **Rumus** | Rolling standard deviation of distAtr (window = ST_DIST_VOL_WINDOW, default 96) |
| **Output** | `{sdv, p90, n}` |
| **Dependency** | TRUTH (distAtr) |
| **Consumer** | CLONE (adaptive corridor width — sdv digunakan untuk volatility adjustment) |
| **Pipeline** | Stage 5 (EVIDENCE) — SHARED |
| **SQLite** | Tidak ada dedicated column (dihitung runtime) |
| **Snapshot** | Internal state (sdv dipakai di corridor computation) |

### 2.6 Distance Compression

| Atribut | Nilai |
|---------|-------|
| **Authority** | STRUCTURE — CageEngine |
| **Deskripsi** | Jarak antar dinding cage mengecil (rangeAtr menurun) |
| **Indikator** | `cage.rangeAtr ≤ CAGE_TIGHT_ATR` → VALID_COMPRESSION |
| **Dependency** | STRUCTURE (cage.rangeAtr) |
| **Consumer** | CLONE (GRID: kompresi = entry opportunity), TRADING_SCHEMA (SIDEWAY_COMPRESSION) |
| **Pipeline** | Stage 4 (STRUCTURE) — SHARED |
| **SQLite** | `structure_snapshots.cage_range_atr` |
| **Snapshot** | structure_snapshot (W field) |

### 2.7 Distance Expansion

| Atribut | Nilai |
|---------|-------|
| **Authority** | STRUCTURE — CageEngine |
| **Deskripsi** | Jarak antar dinding cage membesar (rangeAtr meningkat) |
| **Indikator** | `cage.rangeAtr > CAGE_LOOSE_ATR` → LOOSE_SIDEWAY atau NONE |
| **Dependency** | STRUCTURE (cage.rangeAtr) |
| **Consumer** | CLONE (GRID: ekspansi = caution), TRADING_SCHEMA (RANGE_EXPANDING) |
| **Pipeline** | Stage 4 (STRUCTURE) — SHARED |
| **SQLite** | `structure_snapshots.cage_range_atr` |
| **Snapshot** | structure_snapshot (W field) |

### 2.8 Distance Breakout

| Atribut | Nilai |
|---------|-------|
| **Authority** | STRUCTURE — CageEngine |
| **Deskripsi** | Price menembus dinding cage (cage.breakout ≠ NONE) |
| **Indikator** | `cage.breakout = IMMINENT_UP / IMMINENT_DOWN / SQUEEZE` |
| **Dependency** | STRUCTURE (cage.breakout, pressure) |
| **Consumer** | CLONE (exit: HYPOTHESIS_INVALID), TRADING_SCHEMA (BREAKOUT condition) |
| **Pipeline** | Stage 4 (STRUCTURE) — SHARED |
| **SQLite** | `structure_snapshots.cage_breakout` |
| **Snapshot** | structure_snapshot (W field) |

### 2.9 Distance Pullback

| Atribut | Nilai |
|---------|-------|
| **Authority** | STRUCTURE — CageEngine + TRUTH (stDir) |
| **Deskripsi** | Price mundur ke arah ST dalam trend (distance-to-ST mengecil dalam trend) |
| **Indikator** | `stDir ≠ 0 ∧ distAtr menurun dari peak` |
| **Dependency** | TRUTH (stDir, distAtr), STRUCTURE (cage) |
| **Consumer** | CLONE (LONG: pullback ke floor = entry opportunity), TRADING_SCHEMA |
| **Pipeline** | Stage 4-5 — SHARED |
| **SQLite** | Derived dari `truth_snapshots.dist_atr` + `structure_snapshots` |
| **Snapshot** | Derived metric (tidak ada dedicated field) |

### 2.10 Distance Recovery

| Atribut | Nilai |
|---------|-------|
| **Authority** | STRUCTURE + TRUTH |
| **Deskripsi** | Price kembali mendekati ceiling/floor setelah pullback |
| **Indikator** | `dist_ceiling menurun (LONG) atau dist_floor menurun (SHORT)` |
| **Dependency** | STRUCTURE (dist_ceiling, dist_floor), TRUTH (stDir) |
| **Consumer** | CLONE (reentry opportunity), TRADING_SCHEMA |
| **Pipeline** | Stage 5 — SHARED |
| **SQLite** | Derived metric |
| **Snapshot** | Derived metric |

### 2.11 Distance Exhaustion

| Atribut | Nilai |
|---------|-------|
| **Authority** | STRUCTURE — WaveBuilder + TRUTH |
| **Deskripsi** | Trend melemah — distance-to-ST membesar tanpa arah yang jelas |
| **Indikator** | `wave = EXHAUSTION_UP/DOWN ∧ distAtr > threshold` |
| **Dependency** | STRUCTURE (wave), TRUTH (distAtr, stDir) |
| **Consumer** | CLONE (exit existing, observe), TRADING_SCHEMA (EXHAUSTION condition) |
| **Pipeline** | Stage 4-5 — SHARED |
| **SQLite** | Derived dari `structure_snapshots.wave_structure` + `truth_snapshots.dist_atr` |
| **Snapshot** | Derived metric |

### 2.12 Distance Maturity

| Atribut | Nilai |
|---------|-------|
| **Authority** | STRUCTURE — WaveBuilder + TRUTH |
| **Deskripsi** | Trend sudah matang — wave structure menunjukkan kontinuasi yang established |
| **Indikator** | `wave = CONTINUATION_UP/DOWN ∧ distAtr stabil` |
| **Dependency** | STRUCTURE (wave), TRUTH (distAtr) |
| **Consumer** | CLONE (confidence adjustment), TRADING_SCHEMA |
| **Pipeline** | Stage 4-5 — SHARED |
| **SQLite** | Derived metric |
| **Snapshot** | Derived metric |

### 2.13 Distance Cluster

| Atribut | Nilai |
|---------|-------|
| **Authority** | STRUCTURE — CageEngine (versioning) |
| **Deskripsi** | Beberapa support/resistance walls berkumpul (v0, v1, v2 berdekatan) |
| **Indikator** | `versioning: v0, v1, v2 walls dengan jarak < threshold` |
| **Dependency** | STRUCTURE (cage.versioning) |
| **Consumer** | CLONE (cluster = strong S/R zone), TRADING_SCHEMA |
| **Pipeline** | Stage 4 — SHARED |
| **SQLite** | `cage_history` (version_label, upper, lower) |
| **Snapshot** | structure_snapshot.versioning |

### 2.14 Distance Memory

| Atribut | Nilai |
|---------|-------|
| **Authority** | KNOWLEDGE — Oracle + Academy |
| **Deskripsi** | Historical distance patterns yang mirip dengan kondisi saat ini |
| **Indikator** | `oracle_match.score > 7500` pada vektor yang mengandung distAtr |
| **Dependency** | KNOWLEDGE (Oracle), TRUTH (distAtr) |
| **Consumer** | PREDICTION (similarity_score), HIVEMIND (understanding) |
| **Pipeline** | Stage 17 (ORACLE) — SHARED-AGAIN |
| **SQLite** | `knowledge_artifacts` (oracle_match) |
| **Snapshot** | knowledge_snapshot |

---

## 3. AUTHORITY MATRIX (Distance Sub-Components)

| Komponen | Entry | Exit | Validation | Statistics | Knowledge | Prediction | Governance |
|----------|-------|------|-----------|-----------|-----------|-----------|-----------|
| Distance-to-ST | S | — | V | W,K | K | P+ | — |
| Distance-ATR | S | — | V | W,K | K | P+ | — |
| Distance-Ceiling | T | T | V | W | K | P− | B |
| Distance-Floor | T | T | V | W | K | P− | B |
| Distance-Volatility | S | — | V | W | K | P− | — |
| Distance-Compression | T | T | V | W | K | P+ | B |
| Distance-Expansion | S | S | S | W | K | P− | — |
| Distance-Breakout | T | T | V | W | K | P+ | B |
| Distance-Pullback | S | — | S | W | K | P+ | — |
| Distance-Recovery | S | — | S | W | K | P− | — |
| Distance-Exhaustion | S | T | V | W | K | P+ | — |
| Distance-Maturity | S | — | S | W,K | K | P− | — |
| Distance-Cluster | S | S | V | W | K | P− | — |
| Distance-Memory | — | — | — | W | K | P+ | — |

---

## 4. DEPENDENCY

```
TRUTH (close, st, atr)
  │
  ├── dist = |close - st|           (TRUTH — W field)
  ├── distAtr = dist / atr          (TRUTH — W field)
  │
  └──▶ STRUCTURE (cage.upper, cage.lower)
         │
         ├── dist_ceiling = upper - close   (STRUCTURE — OD field)
         ├── dist_floor = close - lower     (STRUCTURE — OD field)
         │
         └──▶ EVIDENCE (correction_bus)
                │
                └── ST_DIST_VOL (sdv, p90)  (EVIDENCE — runtime)
```

---

## 5. CONSUMER

| Consumer | Distance Metrics Used |
|----------|----------------------|
| CLONE — corridor | distAtr, sdv (volatility adjustment) |
| CLONE — fee_safe | dist_ceiling (LONG), dist_floor (SHORT) |
| CLONE — expected_move | dist_ceiling (LONG), dist_floor (SHORT) |
| CLONE — SL/TP | dist_ceiling, dist_floor (boundary) |
| EVIDENCE — correction_bus | dist_ceiling, dist_floor, wave_structure |
| KNOWLEDGE — Academy | distAtr → distance_bucket (OPTIMAL/NEAR/EXTENDED/FAR) |
| KNOWLEDGE — Oracle | norm01(distAtr, 0, 3) sebagai vektor dimensi |
| PREDICTION | empirical_win_rate per distance_bucket |
| TRADING_SCHEMA | Semua distance metrics untuk kondisi market |

---

## 6. PIPELINE POSITION

Distance TIDAK menjadi pipeline stage terpisah. Distance metrics diproduksi di:

```
Stage 3 (TRUTH):        dist, distAtr
Stage 4 (STRUCTURE):    dist_ceiling, dist_floor (OD)
Stage 5 (EVIDENCE):     ST_DIST_VOL (runtime)
Stage 14-19 (KNOWLEDGE): Distance-Memory (Oracle)
```

Distance adalah **LOGICAL SUB-LAYER** yang mengelompokkan seluruh distance metrics untuk kejelasan arsitektur, tetapi secara fisik tetap menjadi bagian dari TRUTH, STRUCTURE, dan EVIDENCE sesuai referensi.

---

## 7. SQLITE MAPPING

| Distance Metric | SQLite Table | Column |
|----------------|-------------|--------|
| dist | `truth_snapshots` | `dist_to_st` |
| distAtr | `truth_snapshots` | `dist_atr` |
| dist_ceiling | `structure_snapshots` | `dist_ceiling` |
| dist_floor | `structure_snapshots` | `dist_floor` |
| rangeAtr (compression/expansion) | `structure_snapshots` | `cage_range_atr` |
| breakout | `structure_snapshots` | `cage_breakout` |
| versioning (cluster) | `cage_history` | `version_label`, `upper`, `lower` |
| oracle (memory) | `knowledge_artifacts` | `payload_json` (oracle_match) |

---

## 8. SNAPSHOT MAPPING

| Distance Metric | Snapshot | Field Type |
|----------------|----------|-----------|
| dist, distAtr | truth_snapshot | W (frozen stored) |
| dist_ceiling, dist_floor | structure_snapshot | OD (on-demand dari sumber beku) |
| ST_DIST_VOL | Internal state | Runtime (tidak di-snapshot) |
| Distance-Memory | knowledge_snapshot | W (oracle_match) |

---

## KESIMPULAN PATCH 01

**Distance Layer** pantas sebagai **LOGICAL SUB-LAYER** yang mengelompokkan 14 distance metrics untuk kejelasan arsitektur. Distance TIDAK menjadi physical layer atau pipeline stage terpisah — distance metrics tetap diproduksi di TRUTH (W fields) dan STRUCTURE (OD fields) sesuai MASTER_SPECIFICATION §4. Pengelompokan logis ini membantu memahami consumer dan dependency distance metrics tanpa melanggar referensi.

**Tidak ada perubahan pada:** Konstitusi, spesifikasi, SQLite schema, pipeline stages, layer authority.
