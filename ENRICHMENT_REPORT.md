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
# BAG LAYER POSITION — Patch 02

## ST-LMS Architecture Enrichment Patch V1

**Date:** 2026-07-28
**Status:** ENRICHMENT ANALYSIS — FROZEN
**Sources:** STLMS_SQLITE_SCHEMA_V1.sql (BAG layer), BAG_ARCHITECTURE_SPECIFICATION.md, MASTER_SPECIFICATION.html, DOCUMENT_DEPENDENCY.html

---

## 1. ANALISIS POSISI BAG

### 1.1 Evidence dari SQLite Schema

```sql
-- BAG membaca dari STATISTICS:
bag_artifacts.stat_id REFERENCES trade_statistics(stat_id)

-- KNOWLEDGE membaca dari BAG:
knowledge_artifacts.bag_id REFERENCES bag_artifacts(bag_id)
```

FK chain: `trade_statistics` → `bag_artifacts` → `knowledge_artifacts`

Ini adalah bukti kuat bahwa BAG berada di **antara** STATISTICS dan KNOWLEDGE.

### 1.2 Evidence dari bag_kind

```sql
bag_kind IN ('behavior','market','entry','exit','risk','knowledge')
```

- `behavior` — perilaku market (dari market_statistics)
- `market` — kondisi market (dari market_statistics)
- `entry` — entry patterns (dari trade_statistics)
- `exit` — exit patterns (dari trade_statistics)
- `risk` — risk metrics (dari trade_statistics + positions)
- `knowledge` — knowledge patterns (dari knowledge_artifacts — read-only)

BAG membaca STATISTICS untuk 5 dari 6 bag_kind. Hanya `knowledge` yang membaca dari KNOWLEDGE (read-only).

### 1.3 Analisis Pipeline Options

**OPTION A: STATISTICS → BAG → KNOWLEDGE**

```
STATISTICS (trade_statistics, market_statistics)
    │
    ▼
  BAG (group, classify, summarize)
    │  - Membaca: trade_statistics, market_statistics
    │  - Menulis: bag_artifacts, bag_patterns, bag_compression
    │
    ▼
KNOWLEDGE (Academy, Oracle, HiveMind, CERMIN, Librarian, Darwin)
    │  - Membaca: bag_artifacts (via bag_id FK)
    │  - BAG menyediakan grouped statistics
```

**OPTION B: STATISTICS → KNOWLEDGE → BAG**

```
STATISTICS → KNOWLEDGE → BAG
                        ↑
                        └── BAG membaca knowledge_artifacts (read-only)
```

Masalah: BAG tidak bisa mengelompokkan statistics jika statistics sudah diproses Knowledge. BAG akan kehilangan akses ke raw statistics.

**OPTION C: STATISTICS → BAG → KNOWLEDGE → BAG (feedback loop)**

```
STATISTICS → BAG → KNOWLEDGE
              ↑        │
              └────────┘ (BAG membaca knowledge untuk bag_kind='knowledge')
```

Masalah: Loop BAG→KNOWLEDGE→BAG berpotensi circular.

---

## 2. KEPUTUSAN FINAL

### 2.1 Final Position: OPTION A (dengan read-only access ke KNOWLEDGE)

```
┌──────────────────────────────────────────────────────────────────┐
│                     FINAL BAG PIPELINE POSITION                    │
│                                                                    │
│  STATISTICS (trade_statistics, market_statistics)                  │
│      │                                                             │
│      ▼                                                             │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                        BAG LAYER                             │ │
│  │                                                              │ │
│  │  PRIMARY INPUT (WRITE PATH):                                 │ │
│  │    trade_statistics ──▶ bag_artifacts (bag_kind: behavior,   │ │
│  │    market_statistics        market, entry, exit, risk)       │ │
│  │                                                              │ │
│  │  SECONDARY INPUT (READ-ONLY):                                │ │
│  │    knowledge_artifacts ──▶ bag_artifacts (bag_kind: knowledge)│ │
│  │    (one-way read — BAG does NOT write to knowledge_artifacts)│ │
│  │                                                              │ │
│  │  OUTPUT:                                                     │ │
│  │    bag_artifacts ──▶ knowledge_artifacts (via bag_id FK)     │ │
│  │    bag_patterns, bag_compression                             │ │
│  └─────────────────────────────────────────────────────────────┘ │
│      │                                                             │
│      ▼                                                             │
│  KNOWLEDGE (Academy, Oracle, HiveMind, CERMIN, Librarian, Darwin)  │
│      │                                                             │
│      │  knowledge_artifacts.bag_id → REFERENCES bag_artifacts      │
│      │  (ONE-WAY READ — Knowledge reads BAG, not vice versa)       │
│      │                                                             │
│      ▼                                                             │
│  PREDICTION → GOVERNANCE                                           │
└──────────────────────────────────────────────────────────────────┘
```

### 2.2 Mengapa OPTION A?

1. **FK chain**: `trade_statistics` → `bag_artifacts` → `knowledge_artifacts` — BAG secara fisik berada di antara keduanya
2. **Data flow**: Statistics (raw aggregation) → BAG (grouped insights) → Knowledge (understanding)
3. **Unidirectional**: STATISTICS → BAG → KNOWLEDGE (tidak ada loop)
4. **Read-only knowledge access**: BAG membaca knowledge_artifacts untuk bag_kind='knowledge' secara ONE-WAY (read-only). BAG TIDAK menulis balik ke knowledge_artifacts. Ini bukan loop.
5. **Card-agnostic**: BAG membaca cards, tidak memodifikasi cards

---

## 3. RESPONSIBILITY

| Responsibility | Deskripsi |
|---------------|-----------|
| **PRIMARY** | Mengelompokkan trade_statistics dan market_statistics ke dalam bag_artifacts |
| **SECONDARY** | Membaca knowledge_artifacts untuk mengelompokkan knowledge patterns (read-only) |
| **OUTPUT** | Menghasilkan grouped insights (consensus, conflict_level, confidence) |
| **PATTERN** | Mendeteksi pola dalam artifact (bag_patterns) |
| **COMPRESSION** | Mengompresi artifact redundant (bag_compression) |

---

## 4. AUTHORITY

| Operasi | Status | Deskripsi |
|---------|--------|-----------|
| READ trade_statistics | ✅ ALLOWED | Primary data source |
| READ market_statistics | ✅ ALLOWED | Market condition data |
| READ knowledge_artifacts | ✅ ALLOWED | Read-only untuk bag_kind='knowledge' |
| READ trade_markers | ✅ ALLOWED | Untuk analisis detail |
| WRITE bag_artifacts | ✅ ALLOWED | Primary output |
| WRITE bag_patterns | ✅ ALLOWED | Pattern output |
| WRITE bag_compression | ✅ ALLOWED | Compression metrics |
| WRITE trade_statistics | ❌ FORBIDDEN | Unidirectional flow |
| WRITE knowledge_artifacts | ❌ FORBIDDEN | BAG tidak menulis knowledge |
| ENTRY/EXIT decision | ❌ FORBIDDEN | Trading authority |
| GOVERNANCE decision | ❌ FORBIDDEN | Governance authority |

---

## 5. CONSUMER

| Consumer | Access | Deskripsi |
|----------|--------|-----------|
| **KNOWLEDGE** | MANDATORY | Academy, Oracle, HiveMind membaca BAG via bag_id FK |
| **PREDICTION** | OPTIONAL | Dapat membaca BAG untuk empirical context |
| **BENCHMARK** | OPTIONAL | Dapat membaca BAG untuk grouped evaluation |
| **DASHBOARD** | OPTIONAL | Dapat menampilkan BAG insights |
| **AUDIT** | OPTIONAL | Dapat mengaudit BAG artifacts |

**FORBIDDEN CONSUMERS:**
- MARKET, TRUTH, STRUCTURE, EVIDENCE, CLONE, TRADE, POSITION (upstream layers)
- GOVERNANCE (harus melalui KNOWLEDGE, bukan BAG langsung)

---

## 6. DEPENDENCY

### 6.1 Upstream

| Dependency | Type | Source |
|-----------|------|--------|
| STATISTICS | MANDATORY | trade_statistics, market_statistics |
| KNOWLEDGE | OPTIONAL (read-only) | knowledge_artifacts untuk bag_kind='knowledge' |

### 6.2 Downstream

| Dependency | Type | Consumer |
|-----------|------|----------|
| KNOWLEDGE | MANDATORY | knowledge_artifacts.bag_id |

---

## 7. SQLITE MAPPING

### 7.1 Tables Read by BAG

| Table | Purpose |
|-------|---------|
| `trade_statistics` | PRIMARY — stat_id, win_rate, expectancy, pf, mae, mfe, fee_drag, wrong_rate, bucket_key |
| `market_statistics` | PRIMARY — phase, wave_structure, support_hits, resistance_hits, breakout_count |
| `knowledge_artifacts` | SECONDARY (read-only) — entity, bucket_key, win_rate, confidence |
| `trade_markers` | OPTIONAL — untuk analisis detail |

### 7.2 Tables Written by BAG

| Table | Purpose |
|-------|---------|
| `bag_artifacts` | PRIMARY OUTPUT — bag_id, bag_kind, bag_key, consensus, conflict_level, confidence, sample_count, payload_json |
| `bag_patterns` | Pattern output — pattern_rank, pattern_key, pattern_value |
| `bag_compression` | Compression metrics — source_count, compressed_count, compression_ratio |

### 7.3 Tables NOT Touched by BAG

| Table | Reason |
|-------|--------|
| `market_candles` | MARKET authority |
| `truth_snapshots` | TRUTH authority |
| `structure_snapshots` | STRUCTURE authority |
| `evidence_snapshots` | EVIDENCE authority |
| `clone_observations` | CLONE authority |
| `trade_markers` | Read-only (tidak menulis) |
| `positions` | POSITION authority |
| `governance_proposals` | GOVERNANCE authority |
| `predictions` | PREDICTION authority |

---

## 8. SNAPSHOT MAPPING

### 8.1 Snapshots Read by BAG

| Snapshot | Data Used |
|----------|-----------|
| Trade Snapshot | markers untuk analisis |
| Statistics Snapshot | trade_statistics (win_rate, expectancy, dll) |
| Knowledge Snapshot | knowledge_artifacts (read-only) |

### 8.2 Snapshots Produced by BAG

BAG TIDAK memproduksi snapshot sendiri. BAG menyimpan hasil ke SQLite tables (`bag_artifacts`, `bag_patterns`, `bag_compression`). Knowledge Snapshot dapat merujuk BAG artifacts melalui `bag_id`.

---

## KESIMPULAN PATCH 02

**BAG Final Position: STATISTICS → BAG → KNOWLEDGE (OPTION A)**

BAG adalah intermediate aggregation layer antara STATISTICS dan KNOWLEDGE. BAG membaca trade_statistics dan market_statistics, mengelompokkannya ke dalam bag_artifacts (6 bag_kind), dan KNOWLEDGE membaca hasil BAG melalui bag_id FK. BAG juga dapat membaca knowledge_artifacts secara read-only untuk bag_kind='knowledge' — ini ONE-WAY, bukan loop.

**Tidak ada perubahan pada:** Konstitusi, spesifikasi, SQLite schema, pipeline stages, layer authority.
# TRADING SCHEMA LAYER — Patch 03

## ST-LMS Architecture Enrichment Patch V1

**Date:** 2026-07-28
**Status:** ENRICHMENT ANALYSIS — FROZEN
**Sources:** MASTER_SPECIFICATION.html §6, §7, ST_LMS_CORE.js (CLONE_SHARED), TRADING_SCHEMA_FREEZE.md, DECISION_TREE_FREEZE.md

---

## 1. PERBEDAAN TRADING LAYER vs TRADING SCHEMA LAYER

| Aspek | TRADING LAYER | TRADING SCHEMA LAYER |
|-------|--------------|---------------------|
| **Fungsi** | Eksekusi trading (ENTRY, EXIT, POSITION) | Definisi kondisi market dan perilaku clone |
| **Runtime** | PER-CLONE, per candle | Definisi statis (blueprint) |
| **Output** | Trade markers, position state | Trading rules, condition matrices |
| **Consumer** | STATISTICS | TRADING LAYER (sebagai acuan) |
| **Pipeline** | Stage 6-12 | Pre-stage (definisi sebelum eksekusi) |

---

## 2. SELURUH TRADING SCHEMA

### 2.1 NO TRADE SCHEMA

```
KONDISI: Clone tidak entry karena kondisi tidak terpenuhi.
OBSERVASI: Mandatory (LAW-MASTER-06).

REASONS:
  - STDIR_OR_DIRBUS_MISMATCH
  - OUT_OF_CORRIDOR
  - EXPECTED_MOVE_LESS_THAN_REQUIRED
  - GLOBAL_RISK_BREACH
  - POSITION_ALREADY_OPEN
  - CAGE_NONE (GRID)
  - WARMUP

ENTRY_ALLOWED: false
NO_ENTRY_REASON: {reason}
SETUP_SCORE: 2500
CONFIDENCE: 2500
```

### 2.2 LONG SCHEMA

```
KONDISI: UPTREND — stDir = +1

ENTRY CONJUNCTION (ALL must be true):
  1. stDir === 1
  2. EMA slope > 0
  3. Volume Delta > 0
  4. corridor.inZone
  5. fee_safe (dist_ceiling ≥ required_move)
  6. global_ok
  7. open_position === false

EXIT PRIORITY:
  1. WRONG_ENTRY_EARLY   (vel < -deadzone ∧ hold ≤ 2)
  2. WRONG_ENTRY_GEOM    (adverse ≥ WRONG_ENTRY_PCT ∧ hold ≤ 2)
  3. HYPOTHESIS_INVALID  (breakout = IMMINENT_DOWN)
  4. SL                  (low ≤ sl)
  5. HOLD-VETO           (MACD expanding → delay TP)
  6. TP                  (high ≥ tp)
  7. EXIT_BUS            (RSI > 70 OR W%R > -20)
  8. TIME_EXIT           (hold ≥ TIME_EXIT ∧ profit < required)

SL: floor (cage.lower ?? nearest.support ?? close)
TP: min(ceiling, cage.upper, entry + TP_ATR_MULT × ATR)
```

### 2.3 SHORT SCHEMA

```
KONDISI: DOWNTREND — stDir = -1

ENTRY CONJUNCTION (ALL must be true):
  1. stDir === -1
  2. EMA slope < 0
  3. Volume Delta < 0
  4. corridor.inZone
  5. fee_safe (dist_floor ≥ required_move)
  6. global_ok
  7. open_position === false

EXIT PRIORITY:
  1. WRONG_ENTRY_EARLY   (vel > +deadzone ∧ hold ≤ 2)
  2. WRONG_ENTRY_GEOM    (adverse ≥ WRONG_ENTRY_PCT ∧ hold ≤ 2)
  3. HYPOTHESIS_INVALID  (breakout = IMMINENT_UP)
  4. SL                  (high ≥ sl)
  5. HOLD-VETO           (MACD expanding → delay TP)
  6. TP                  (low ≤ tp)
  7. EXIT_BUS            (RSI < 30 OR W%R < -80)
  8. TIME_EXIT           (hold ≥ TIME_EXIT ∧ profit < required)

SL: ceiling (cage.upper ?? nearest.resistance ?? close)
TP: max(floor, cage.lower, entry - TP_ATR_MULT × ATR)
```

### 2.4 GRID SCHEMA

```
KONDISI: SIDEWAY — cage.status ≠ NONE

ENTRY CONJUNCTION:
  1. cage_valid (status = VALID_COMPRESSION OR LOOSE_SIDEWAY)
  2. fee_safe (width ≥ 3 × required_move)
  3. breakout_none (breakout = NONE)
  4. pp in BUY_ZONE (pp < GRID_BUY_ZONE_MAX) → LONG fill
  5. pp in SELL_ZONE (pp > GRID_SELL_ZONE_MIN) → SHORT fill
  6. fills_per_side < GRID_MAX_FILLS_PER_SIDE

EXIT:
  1. RANGE_BREAK (cage no longer valid)
  2. RANGE_BREAK (breakout against fill)
  3. WRONG_ENTRY (adverse ≥ WRONG_ENTRY_PCT)
  4. GRID_TP (profit ≥ required_move)
  5. STOP_ALL (¬cage_valid)

RULES:
  - Blind to direction (no stDir, Direction Bus, MTF)
  - Scaling = multiple fills (not pyramiding)
  - Forbidden in trend (cage NONE)
```

### 2.5 WAIT SCHEMA

```
KONDISI: Clone mengamati tanpa entry. Kondisi market tidak mendukung.

WAIT STATES:
  WARMUP           — insufficient data (semua clone)
  TREND_OPPOSITE   — SHORT wait di UPTREND; LONG wait di DOWNTREND
  SIDEWAY_DIRECTIONAL — LONG/SHORT wait di SIDEWAY (GRID active)
  REVERSAL         — trend flipping (semua clone wait)
  CHAOS            — no clear structure (semua clone wait)
  EXHAUSTION       — trend exhausting (opposite clone wait)

OBSERVASI: Mandatory
NO_ENTRY_REASON: Sesuai wait state
```

### 2.6 HOLD SCHEMA

```
KONDISI: Posisi terbuka, tidak ada alasan exit.

HOLD BEHAVIOR:
  - hold_c += 1 per candle
  - Update MAE/MFE
  - HOLD-VETO active: MACD expanding + velocity with trend → delay TP
  - Continue monitoring exit conditions

HOLD-VETO RULES:
  - prevMacdHist != null
  - |macdHist| < |prevMacdHist| (MACD shrinking) → NOT hold
  - |macdHist| > |prevMacdHist| (MACD expanding) → hold possible
  - velocity with trend → HOLD active
  - HOLD delays TP (TP only triggers if HOLD is not active)
```

### 2.7 SKIP SCHEMA

```
KONDISI: Candle tidak valid atau data insufficient.

SKIP CONDITIONS:
  - data_status != "FINAL" (PROVISIONAL candle)
  - gap_flag = 1 (gap detected — quality reduced)
  - data_status = "INVALID" (hygiene failed)

BEHAVIOR:
  - Tidak ada entry
  - Posisi terbuka tetap dimonitor
  - Observasi tetap diproduksi (dengan status data)
```

### 2.8 LONG BREAKOUT SCHEMA

```
KONDISI: UPTREND + cage.breakout = IMMINENT_UP

ENTRY:
  - stDir = +1
  - cage.breakout = IMMINENT_UP
  - pressureUp = true (resistance under pressure)
  - Entry conjunction standard LONG

EXIT:
  - TP: cage.upper (resistance yang akan ditembus)
  - SL: cage.lower (support terdekat)
  - HYPOTHESIS_INVALID if breakout fails

CONFIDENCE: setup_score + breakout boost
```

### 2.9 LONG REVERSAL SCHEMA

```
KONDISI: DOWNTREND → UPTREND flip detected

ENTRY:
  - TREND_FLIP_UP detected (cl > puf)
  - stDir = +1 (baru flip)
  - Wave structure = REVERSAL_UP
  - Entry conjunction standard LONG (dengan konfirmasi tambahan)

CAUTION:
  - hold_c ≤ 2: wrong entry exit lebih agresif
  - false reversal risk: monitor ketat
```

### 2.10 LONG CONTINUATION SCHEMA

```
KONDISI: UPTREND established + wave = CONTINUATION_UP

ENTRY:
  - stDir = +1
  - wave = CONTINUATION_UP or STRONG_ACCUMULATION
  - Entry conjunction standard LONG

CONFIDENCE: Higher — trend established
EXIT: Standard LONG exit priority
```

### 2.11 LONG PULLBACK SCHEMA

```
KONDISI: UPTREND + price pullback ke floor/support

ENTRY:
  - stDir = +1 (trend masih UP)
  - dist_ceiling membesar (pullback dari ceiling)
  - corridor.inZone (price dekat floor)
  - fee_safe (dist_ceiling ≥ required_move — room to ceiling)

OPTIMAL: Pullback ke cage.lower atau nearest.support
CONFIDENCE: setup_score + pullback boost
```

### 2.12 SHORT BREAKOUT SCHEMA

```
KONDISI: DOWNTREND + cage.breakout = IMMINENT_DOWN

ENTRY:
  - stDir = -1
  - cage.breakout = IMMINENT_DOWN
  - pressureDn = true (support under pressure)
  - Entry conjunction standard SHORT

EXIT:
  - TP: cage.lower (support yang akan ditembus)
  - SL: cage.upper (resistance terdekat)
```

### 2.13 SHORT REVERSAL SCHEMA

```
KONDISI: UPTREND → DOWNTREND flip detected

ENTRY:
  - TREND_FLIP_DOWN detected (cl < plf)
  - stDir = -1 (baru flip)
  - Wave structure = REVERSAL_DOWN
  - Entry conjunction standard SHORT

CAUTION:
  - hold_c ≤ 2: wrong entry exit lebih agresif
```

### 2.14 SHORT CONTINUATION SCHEMA

```
KONDISI: DOWNTREND established + wave = CONTINUATION_DOWN

ENTRY:
  - stDir = -1
  - wave = CONTINUATION_DOWN or STRONG_DISTRIBUTION
  - Entry conjunction standard SHORT

CONFIDENCE: Higher — trend established
```

### 2.15 SHORT PULLBACK SCHEMA

```
KONDISI: DOWNTREND + price pullback ke ceiling/resistance

ENTRY:
  - stDir = -1 (trend masih DOWN)
  - dist_floor membesar (pullback dari floor)
  - corridor.inZone (price dekat ceiling)
  - fee_safe (dist_floor ≥ required_move)

OPTIMAL: Pullback ke cage.upper atau nearest.resistance
```

### 2.16 SIDEWAY GRID SCHEMA

```
KONDISI: SIDEWAY_COMPRESSION — cage valid, range stabil

ENTRY: Standard GRID schema
FILLS: Buy di lower zone, sell di upper zone
EXIT: GRID_TP saat profit ≥ required_move per fill
```

### 2.17 RANGE GRID SCHEMA

```
KONDISI: CONFIRMED_RANGE — wave menunjukkan range behavior

ENTRY: Standard GRID schema
WAVE: CONFIRMED_RANGE, RANGE_COMPRESSING, SIDEWAY
FILLS: Multiple fills dalam range
```

### 2.18 COMPRESSION GRID SCHEMA

```
KONDISI: VALID_COMPRESSION — range menyempit

ENTRY: Standard GRID schema
CAGE: VALID_COMPRESSION (tight range)
FILLS: Lebih agresif — kompresi sering menghasilkan breakout
CAUTION: Monitor breakout imminent
```

### 2.19 EXPANSION GRID SCHEMA

```
KONDISI: LOOSE_SIDEWAY — range melebar

ENTRY: Standard GRID schema
CAGE: LOOSE_SIDEWAY (wide range)
FILLS: Lebih konservatif — range lebar = risk lebih besar
```

### 2.20 EXIT SCHEMA (UMUM)

```
KONDISI: Posisi terbuka, alasan exit terpenuhi

EXIT PRIORITY (directional):
  1. WRONG_ENTRY_EARLY
  2. WRONG_ENTRY_GEOM
  3. HYPOTHESIS_INVALID
  4. SL
  5. HOLD-VETO (delay TP)
  6. TP
  7. EXIT_BUS
  8. TIME_EXIT

EXIT PRIORITY (GRID):
  1. RANGE_BREAK
  2. RANGE_BREAK (against fill)
  3. WRONG_ENTRY
  4. GRID_TP
  5. STOP_ALL
```

### 2.21 TIME EXIT SCHEMA

```
KONDISI: Posisi terlalu lama tanpa profit cukup

TRIGGER:
  hold_c ≥ TIME_EXIT_CANDLES (default: 40)
  AND current_profit_pct < required_move

PURPOSE: Menutup posisi stagnant
PRIORITY: Terendah (8) — hanya jika tidak ada alasan exit lain
```

### 2.22 PARTIAL EXIT SCHEMA

```
KONDISI: Profit mencapai threshold partial TP

TRIGGER:
  profit_pct ≥ PARTIAL_TP activation threshold

ACTION:
  - Close PARTIAL_TP_PCT (default: 50%) dari posisi
  - Move SL ke entry (breakeven untuk sisa posisi)
  - Continue holding remainder

STATUS: PARTIAL (position_status)
```

### 2.23 TRAILING EXIT SCHEMA

```
KONDISI: Profit mencapai trailing activation

TRIGGER:
  profit_pct ≥ TRAIL_ACTIVATE_R × ATR (default: 1.0)

ACTION:
  - SL digeser mengikuti price dengan jarak TRAIL_ATR_MULT × ATR
  - LONG: SL = max(SL, price - TRAIL_ATR_MULT × ATR)
  - SHORT: SL = min(SL, price + TRAIL_ATR_MULT × ATR)

STATUS: TRAILING (position_status)
```

### 2.24 WRONG ENTRY EXIT SCHEMA

```
KONDISI: Entry ternyata salah (detected dalam 2 candle pertama)

TRIGGERS:
  EARLY: W%R velocity berlawanan dengan posisi (hold ≤ 2)
  GEOM: adverse price movement ≥ WRONG_ENTRY_PCT (hold ≤ 2)

PRIORITY: Tertinggi (1-2) — exit segera
PURPOSE: Meminimalkan kerugian dari entry yang salah
```

---

## 3. SCHEMA SUMMARY

```
┌──────────────────────────────────────────────────────────────────────────┐
│                        ST-LMS TRADING SCHEMA                              │
│                                                                           │
│  STATE SCHEMAS (5):                                                       │
│    NO TRADE    — Observasi mandatory tanpa entry                          │
│    WAIT        — Menunggu kondisi market yang tepat                       │
│    HOLD        — Menahan posisi terbuka                                   │
│    SKIP        — Candle invalid/tidak lengkap                             │
│    EXIT        — Menutup posisi (8 priority levels)                       │
│                                                                           │
│  DIRECTIONAL SCHEMAS (8):                                                 │
│    LONG              — Standard LONG entry/exit                           │
│    LONG BREAKOUT     — LONG saat resistance breakout                      │
│    LONG REVERSAL     — LONG saat trend flip UP                            │
│    LONG CONTINUATION — LONG saat trend established                        │
│    LONG PULLBACK     — LONG saat pullback ke support                      │
│    SHORT             — Standard SHORT entry/exit                          │
│    SHORT BREAKOUT    — SHORT saat support breakout                        │
│    SHORT REVERSAL    — SHORT saat trend flip DOWN                         │
│    SHORT CONTINUATION— SHORT saat trend established                       │
│    SHORT PULLBACK    — SHORT saat pullback ke resistance                  │
│                                                                           │
│  GRID SCHEMAS (4):                                                        │
│    GRID              — Standard GRID entry/exit                           │
│    SIDEWAY GRID      — GRID di SIDEWAY_COMPRESSION                        │
│    RANGE GRID        — GRID di CONFIRMED_RANGE                            │
│    COMPRESSION GRID  — GRID di VALID_COMPRESSION (tight)                  │
│    EXPANSION GRID    — GRID di LOOSE_SIDEWAY (wide)                       │
│                                                                           │
│  EXIT SCHEMAS (4):                                                        │
│    TIME EXIT         — Exit karena hold terlalu lama                      │
│    PARTIAL EXIT      — Exit sebagian, lock profit                         │
│    TRAILING EXIT     — Exit dengan trailing stop                          │
│    WRONG ENTRY EXIT  — Exit karena entry salah (hold ≤ 2)                 │
│                                                                           │
│  TOTAL: 24 Trading Schemas                                                │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 4. SCHEMA → MARKET CONDITION MAPPING

| Market Condition | Active Schema |
|-----------------|---------------|
| TRENDING_UP | LONG, LONG CONTINUATION |
| TRENDING_DOWN | SHORT, SHORT CONTINUATION |
| SIDEWAY_COMPRESSION | SIDEWAY GRID, COMPRESSION GRID |
| LOOSE_SIDEWAY | EXPANSION GRID |
| REVERSAL_UP | LONG REVERSAL (caution) |
| REVERSAL_DOWN | SHORT REVERSAL (caution) |
| BREAKOUT_UP | LONG BREAKOUT |
| BREAKOUT_DOWN | SHORT BREAKOUT |
| EXHAUSTION_UP | WAIT (LONG exit, SHORT observe) |
| EXHAUSTION_DOWN | WAIT (SHORT exit, LONG observe) |
| RANGE_COMPRESSING | COMPRESSION GRID |
| RANGE_EXPANDING | EXPANSION GRID |
| CONFIRMED_RANGE | RANGE GRID |
| CHAOS | WAIT (semua clone) |
| WARMUP | WAIT (semua clone) |
| PULLBACK_UP | LONG PULLBACK |
| PULLBACK_DOWN | SHORT PULLBACK |

---

## KESIMPULAN PATCH 03

**Trading Schema Layer** mendefinisikan **24 trading schemas** yang mengelompokkan perilaku clone berdasarkan kondisi market. Trading Schema adalah blueprint statis yang diacu oleh Trading Layer saat eksekusi. Ini adalah enrichment logis — tidak menambah komponen baru, hanya mengelompokkan aturan yang sudah ada di MASTER_SPECIFICATION §7 dan ST_LMS_CORE.js CLONE_SHARED.

**Tidak ada perubahan pada:** Konstitusi, spesifikasi, SQLite schema, pipeline stages, layer authority, trading logic.
# TRUTH LAYER ENRICHMENT — Patch 04

## ST-LMS Architecture Enrichment Patch V1

**Date:** 2026-07-28
**Status:** ENRICHMENT ANALYSIS — FROZEN
**Sources:** MASTER_SPECIFICATION.html §4, §5, ST_LMS_CORE.js (TRUTH, STRUCTURE, EVIDENCE, STATISTICS namespaces)

---

## 1. TRUTH LAYER OUTPUT — CURRENT UTILIZATION

### 1.1 Truth Snapshot Fields (W — frozen stored)

| Field | Produced By | Consumed By | Utilization |
|-------|------------|-------------|-------------|
| close | TRUTH.PointBuilder | STRUCTURE, EVIDENCE, CLONE, TRADE | ✅ FULL |
| st | TRUTH.PointBuilder | STRUCTURE (LineBuilder, CageEngine) | ✅ FULL |
| st_canon | TRUTH.PointBuilder | STRUCTURE (LineBuilder key) | ✅ FULL |
| stDir | TRUTH.PointBuilder | CLONE (entry direction), STRUCTURE (phase) | ✅ FULL |
| color | TRUTH.PointBuilder | STRUCTURE (LineBuilder, WaveBuilder) | ✅ FULL |
| atr | TRUTH.PointBuilder | STRUCTURE (CageEngine), CLONE (corridor, TP) | ✅ FULL |
| ema | TRUTH.PointBuilder | EVIDENCE (dir_bus), CLONE (dirOk) | ✅ FULL |
| ema12, ema26 | TRUTH.PointBuilder | Internal (MACD calc) | ✅ FULL |
| macd, macd_signal, macd_hist | TRUTH.PointBuilder | EVIDENCE (exit_bus HOLD-veto) | ✅ FULL |
| rsi | TRUTH.PointBuilder | EVIDENCE (exit_bus), DASHBOARD | ✅ FULL |
| wpr | TRUTH.PointBuilder | EVIDENCE (exit_bus), DASHBOARD | ✅ FULL |
| vel | TRUTH.PointBuilder | CLONE (wrong entry early) | ✅ FULL |
| acc | TRUTH.PointBuilder | EVIDENCE (exit_bus acc_signal) | ✅ FULL |
| volDelta | TRUTH.PointBuilder | EVIDENCE (dir_bus), CLONE (dirOk) | ✅ FULL |
| dist | TRUTH.PointBuilder | DASHBOARD | ⚠️ PARTIAL |
| distAtr | TRUTH.PointBuilder | CLONE (corridor), EVIDENCE (ST_DIST_VOL), KNOWLEDGE (Academy, Oracle) | ✅ FULL |
| point_status | TRUTH.PointBuilder | CLONE (warmup check) | ✅ FULL |
| flip | TRUTH.PointBuilder | DASHBOARD | ⚠️ PARTIAL |

### 1.2 Structure Snapshot Fields

| Field | Produced By | Consumed By | Utilization |
|-------|------------|-------------|-------------|
| cage{status,upper,lower,pp,rangeAtr,breakout} | STRUCTURE.CageEngine | CLONE, GRID, EVIDENCE | ✅ FULL |
| cage{upVi,lowVi,cross,pressureUp,pressureDn} | STRUCTURE.CageEngine | DASHBOARD | ⚠️ PARTIAL |
| cage{versioning} | STRUCTURE.CageEngine | DASHBOARD (versioning panel) | ⚠️ PARTIAL |
| ladder | STRUCTURE.ladder | DASHBOARD | ⚠️ PARTIAL |
| nearest{support,resistance} | STRUCTURE.nearest | CLONE (fallback SL/TP) | ✅ FULL |
| phase | STRUCTURE.phase | CLONE, DASHBOARD | ✅ FULL |
| wave | STRUCTURE.WaveBuilder | EVIDENCE (MTF), KNOWLEDGE (Academy, Oracle) | ✅ FULL |
| pending_wave | STRUCTURE.WaveBuilder | DASHBOARD | ⚠️ PARTIAL |

### 1.3 Distance Fields

| Field | Produced By | Consumed By | Utilization |
|-------|------------|-------------|-------------|
| dist | TRUTH.PointBuilder | DASHBOARD only | ⚠️ LOW |
| distAtr | TRUTH.PointBuilder | CLONE, EVIDENCE, KNOWLEDGE | ✅ FULL |
| dist_ceiling | EVIDENCE.correctionBus | CLONE (LONG: fee_safe, expected_move) | ✅ FULL |
| dist_floor | EVIDENCE.correctionBus | CLONE (SHORT: fee_safe, expected_move) | ✅ FULL |
| sdv (ST_DIST_VOL) | EVIDENCE.StDistVol | CLONE (corridor volatility) | ✅ FULL |
| p90 (ST_DIST_VOL) | EVIDENCE.StDistVol | NOT CONSUMED | ❌ UNUSED |

### 1.4 Statistics Fields

| Field | Produced By | Consumed By | Utilization |
|-------|------------|-------------|-------------|
| distance_health_hist | STATISTICS | NOT CONSUMED | ❌ UNUSED |
| fee_safe_margin_dist | STATISTICS | NOT CONSUMED | ❌ UNUSED |
| wrong_entry_dist | STATISTICS | NOT CONSUMED | ❌ UNUSED |

---

## 2. DATA YANG BELUM DIMANFAATKAN

### 2.1 dist (absolute distance-to-ST)

**Current:** Hanya ditampilkan di DASHBOARD (indicator gauge).
**Potential:** Dapat dikonsumsi oleh:
- **BAG** — mengelompokkan distance-to-ST per kondisi market
- **KNOWLEDGE (Academy)** — distance bucket untuk absolute distance (bukan hanya distAtr)
- **TRADING SCHEMA** — pullback detection (dist mengecil dalam trend = pullback)

### 2.2 p90 (ST_DIST_VOL 90th percentile)

**Current:** Tidak dikonsumsi.
**Potential:** Dapat dikonsumsi oleh:
- **CLONE** — extreme volatility threshold untuk entry delay
- **BAG** — mengelompokkan volatility extremes
- **TRADING SCHEMA** — volatility regime classification

### 2.3 cage versioning (upVi, lowVi, cross, pressureUp, pressureDn)

**Current:** Hanya ditampilkan di DASHBOARD.
**Potential:** Dapat dikonsumsi oleh:
- **CLONE** — escape path confidence (cross-version = escape detected)
- **TRADING SCHEMA** — cluster detection (multiple versions close = strong S/R)
- **BAG** — mengelompokkan versioning patterns

### 2.4 ladder (support_stepped, resistance_stepped)

**Current:** Hanya ditampilkan di DASHBOARD.
**Potential:** Dapat dikonsumsi oleh:
- **TRADING SCHEMA** — stepped ladder = trend strength confirmation
- **CLONE** — confidence adjustment (stepped = stronger trend)

### 2.5 pending_wave

**Current:** Hanya ditampilkan di DASHBOARD.
**Potential:** Dapat dikonsumsi oleh:
- **CLONE** — entry delay jika wave belum complete
- **TRADING SCHEMA** — WARMUP extension logic

### 2.6 flip events

**Current:** Hanya ditampilkan di DASHBOARD.
**Potential:** Dapat dikonsumsi oleh:
- **TRADING SCHEMA** — LONG/SHORT REVERSAL schema activation
- **BAG** — mengelompokkan flip frequency per kondisi
- **KNOWLEDGE (Academy)** — flip sebagai dimensi bucket

### 2.7 distance_health_hist, fee_safe_margin_dist, wrong_entry_dist (Statistics)

**Current:** Tidak dikonsumsi.
**Potential:** Dapat dikonsumsi oleh:
- **BAG** — mengelompokkan distance health per kondisi
- **KNOWLEDGE (Academy)** — distance sebagai dimensi bucket tambahan
- **GOVERNANCE (Darwin)** — proposal berdasarkan distance health

---

## 3. DATA YANG DAPAT DIPERKAYA

### 3.1 Truth Layer Enrichment

| Enrichment | Deskripsi | Consumer |
|-----------|-----------|----------|
| dist_trend | dist dibandingkan dengan moving average dist (apakah distance expanding/contracting) | TRADING SCHEMA |
| distAtr_trend | distAtr dibandingkan dengan moving average distAtr | CLONE, TRADING SCHEMA |
| volDelta_ma | Moving average volDelta untuk mengurangi noise | EVIDENCE (dir_bus) |
| ema_distance | |close - ema| sebagai tambahan distance metric | TRADING SCHEMA |
| flip_history | Jumlah flip dalam N candle terakhir | TRADING SCHEMA (choppiness detection) |

### 3.2 Structure Layer Enrichment

| Enrichment | Deskripsi | Consumer |
|-----------|-----------|----------|
| cage_age | Berapa lama cage sudah dalam status saat ini | TRADING SCHEMA |
| wave_sequence | Urutan wave structures (pattern recognition) | BAG, KNOWLEDGE |
| versioning_cluster | Jarak antar versions (v0, v1, v2) | TRADING SCHEMA |
| ladder_strength | Seberapa kuat ladder pattern | TRADING SCHEMA |

### 3.3 Distance Layer Enrichment

| Enrichment | Deskripsi | Consumer |
|-----------|-----------|----------|
| dist_velocity | Rate of change distAtr | CLONE (acceleration ke arah ST) |
| dist_acceleration | Rate of change dist_velocity | CLONE |
| ceiling_floor_ratio | dist_ceiling / dist_floor (asymmetry detection) | TRADING SCHEMA |
| dist_delta | dist_ceiling - dist_floor (bias detection) | TRADING SCHEMA |

---

## 4. DATA YANG DAPAT DIKONSUMSI BAG

| Data | Bag Kind | Bag Key Dimension |
|------|----------|-------------------|
| dist | behavior, market | distance bucket (absolute) |
| distAtr | behavior, market, entry, exit | distance bucket (normalized) |
| p90 (ST_DIST_VOL) | risk, market | volatility percentile |
| versioning (cross, pressure) | behavior, market | versioning pattern |
| ladder (stepped) | behavior | trend strength |
| flip events | behavior, market | flip frequency |
| pending_wave | market | wave completeness |
| distance_health_hist | risk | distance health |
| fee_safe_margin_dist | risk, entry | fee safety margin |
| wrong_entry_dist | risk, exit | wrong entry distance |
| ema_distance | behavior | EMA distance |
| flip_history | behavior, market | choppiness |
| cage_age | behavior | cage duration |
| wave_sequence | behavior, knowledge | wave pattern |
| versioning_cluster | behavior | S/R cluster |
| dist_velocity | behavior, exit | distance momentum |
| dist_acceleration | behavior, exit | distance force |
| ceiling_floor_ratio | market | price asymmetry |
| dist_delta | market | price bias |

---

## 5. DATA YANG DAPAT DIKONSUMSI KNOWLEDGE

### 5.1 Academy (bucket dimensions enrichment)

Current bucket: `clone | structure | distance_bucket | reason`

Enriched bucket: `clone | structure | distance_bucket | reason | flip | ladder_stepped | versioning_cross`

### 5.2 Oracle (vector dimensions enrichment)

Current vector: `[wave, cage, pp, ema, oi, vd, mtf, rsi, distAtr]`

Enriched vector: `[wave, cage, pp, ema, oi, vd, mtf, rsi, distAtr, dist_velocity, ceiling_floor_ratio, flip_history]`

### 5.3 HiveMind

- evidence_adj dari dist_trend dan dist_velocity
- confidence adjustment berdasarkan versioning_cross

### 5.4 Darwin

- Proposal berdasarkan distance_health_hist
- Proposal berdasarkan wrong_entry_dist

---

## 6. DATA YANG DAPAT DIKONSUMSI PREDICTION

| Data | Prediction Dimension |
|------|---------------------|
| distAtr bucket | empirical_win_rate per distance bucket |
| flip_history | choppiness impact on win_rate |
| ladder_stepped | trend strength impact on win_rate |
| versioning_cross | escape detection impact on win_rate |
| dist_velocity | momentum impact on win_rate |
| ceiling_floor_ratio | asymmetry impact on win_rate |

---

## 7. DATA YANG DAPAT DIKONSUMSI TRADING SCHEMA

| Data | Schema Application |
|------|-------------------|
| dist | Pullback detection (dist mengecil dalam trend) |
| distAtr | Volatility-adjusted pullback detection |
| p90 | Extreme volatility → entry delay |
| versioning_cross | Escape detected → confidence reduction |
| ladder_stepped | Stepped ladder → trend strength confirmation |
| pending_wave | Wave incomplete → WARMUP extension |
| flip | Reversal schema activation |
| flip_history | Choppiness → WAIT schema |
| cage_age | Cage duration → breakout probability |
| dist_velocity | Pullback momentum → entry timing |
| ceiling_floor_ratio | Asymmetry → bias toward one direction |
| dist_delta | Bias → LONG vs SHORT preference |

---

## KESIMPULAN PATCH 04

**Truth Layer Output Utilization:**

| Status | Count | Fields |
|--------|-------|--------|
| ✅ FULLY UTILIZED | 18 | close, st, stDir, color, atr, ema, macd, rsi, wpr, vel, acc, volDelta, distAtr, point_status, cage(status/upper/lower/pp/rangeAtr/breakout), nearest, phase, wave |
| ⚠️ PARTIALLY UTILIZED | 8 | dist, flip, cage(upVi/lowVi/cross/pressure/versioning), ladder, pending_wave |
| ❌ UNUSED | 4 | p90 (ST_DIST_VOL), distance_health_hist, fee_safe_margin_dist, wrong_entry_dist |

**Enrichment Opportunities:**
- 19 data points dapat dikonsumsi BAG
- Academy bucket dapat diperkaya dengan 3 dimensi tambahan
- Oracle vector dapat diperkaya dengan 3 dimensi tambahan
- 12 data points dapat dikonsumsi TRADING SCHEMA

**Tidak ada perubahan pada:** Konstitusi, spesifikasi, SQLite schema, pipeline stages, layer authority. Enrichment bersifat rekomendasi — implementasi tidak wajib.
# STATISTICS LAYER ENRICHMENT — Patch 05

## ST-LMS Architecture Enrichment Patch V1

**Date:** 2026-07-28
**Status:** ENRICHMENT ANALYSIS — FROZEN
**Sources:** ST_LMS_CORE.js (STATISTICS namespace), MASTER_SPECIFICATION.html §6, QWEN_14_DOC.html D5

---

## 1. ANALISIS: Apakah Statistics Layer terlalu sederhana?

### 1.1 Current Statistics Output

```
STATISTICS.tradeStats(markers):
  Per clone (LONG/SHORT/GRID):
    sample, status (CUKUP/BELUM_CUKUP), wins, win_rate, expectancy,
    pf (profit factor), mae, mfe, fee_drag, wrong_rate
```

**Observasi:** Statistics saat ini HANYA menghitung statistik dari trade markers. Tidak ada statistik dari dimensi lain (market, distance, wave, behavior). Statistics adalah pure aggregation — tidak ada klasifikasi atau grouping.

### 1.2 Peran BAG

Dengan adanya BAG, grouping dan classification dipindahkan ke BAG. Statistics tetap sebagai raw aggregator. Ini adalah pembagian yang benar:

```
STATISTICS: Raw aggregation (what happened)
BAG:        Grouped classification (why it happened, under what conditions)
KNOWLEDGE:  Understanding (what it means)
```

---

## 2. STATISTICAL ARTIFACTS

### 2.1 Trade Statistics (EXISTING)

```
Current: tradeStats(markers) per clone

Artifacts:
  - sample, win_rate, expectancy, pf, mae, mfe, fee_drag, wrong_rate
  - status: CUKUP / BELUM_CUKUP

ENRICHMENT:
  - win_rate per market_phase (UPTREND, DOWNTREND, SIDEWAY)
  - win_rate per wave_structure (13 types)
  - win_rate per distance_bucket (OPTIMAL, NEAR, EXTENDED, FAR)
  - win_rate per exit_reason (SL, TP, EXIT_BUS, WRONG_ENTRY, TIME_EXIT)
  - expectancy per hold duration bucket
  - mae/mfe distribution (min, max, median, stddev)
  - consecutive wins/losses (streak analysis)
  - profit per candle held (efficiency)
  - time-of-day performance (if timestamps available)
```

### 2.2 Market Statistics (EXISTING — partial)

```
Current: market_statistics table (phase, wave, support_hits, resistance_hits,
         breakout_count, sideways_count, trend_count)

ENRICHMENT:
  - phase_duration: rata-rata durasi setiap phase
  - phase_transition_matrix: probabilitas transisi antar phase
  - wave_frequency: frekuensi setiap wave structure
  - wave_transition: wave structure sequence patterns
  - cage_lifetime: berapa lama cage bertahan sebelum breakout
  - breakout_direction: arah breakout (UP/DOWN) setelah kompresi
  - range_atr_distribution: distribusi cage.rangeAtr
  - pp_distribution: distribusi price position dalam cage
```

### 2.3 Clone Statistics (EXISTING — per clone tradeStats)

```
ENRICHMENT:
  - observation_to_entry_ratio: berapa banyak observasi yang menghasilkan entry
  - entry_reason_distribution: distribusi alasan entry
  - no_entry_reason_distribution: distribusi alasan tidak entry
  - clone_activation_time: persentase waktu clone aktif vs wait
  - clone_correlation: korelasi performa LONG vs SHORT vs GRID
```

---

## 3. BEHAVIORAL ARTIFACTS

### 3.1 Market Behavior Patterns

```
Artifacts:
  - trend_strength: seberapa kuat trend (distAtr stability)
  - trend_persistence: berapa lama trend bertahan
  - volatility_regime: low/medium/high volatility periods
  - mean_reversion_tendency: seberapa sering price kembali ke mean
  - momentum_persistence: seberapa sering momentum berlanjut
  - gap_frequency: seberapa sering gap terjadi
  - data_quality_score: persentase candle dengan data bersih
```

### 3.2 Clone Behavior Patterns

```
Artifacts:
  - entry_aggressiveness: seberapa sering clone entry saat kondisi terpenuhi
  - exit_aggressiveness: seberapa cepat clone exit
  - hold_patience: distribusi hold duration
  - wrong_entry_frequency: seberapa sering entry salah
  - false_signal_rate: entry yang menghasilkan LOSS dalam 3 candle
```

---

## 4. MARKET ARTIFACTS

```
Artifacts:
  - price_distribution: distribusi price dalam range
  - volume_profile: volume per price level
  - volatility_surface: ATR per market condition
  - support_resistance_strength: berapa kali S/R di-test vs ditembus
  - cage_formation_rate: seberapa sering cage terbentuk
  - trend_vs_range_ratio: persentase waktu trending vs ranging
  - market_regime: klasifikasi regime (trending, ranging, volatile, quiet)
```

---

## 5. TRADING ARTIFACTS

```
Artifacts:
  - trade_frequency: trades per candle/day
  - avg_trade_duration: rata-rata durasi trade (hold candles)
  - profit_distribution: distribusi profit (histogram)
  - loss_distribution: distribusi loss (histogram)
  - risk_reward_ratio: average TP distance / average SL distance
  - fee_impact: persentase profit yang hilang karena fee
  - slippage_impact: estimasi slippage dari data
  - adverse_selection: seberapa sering SL terkena sebelum TP
  - optimal_exit_time: hold duration dengan expectancy tertinggi
```

---

## 6. DISTANCE ARTIFACTS

```
Artifacts:
  - distance_distribution: distribusi distAtr
  - optimal_distance_range: distance_bucket dengan win_rate tertinggi
  - distance_at_entry: distAtr saat entry (korelasi dengan win_rate)
  - distance_at_exit: distAtr saat exit
  - ceiling_test_frequency: seberapa sering price mencapai ceiling
  - floor_test_frequency: seberapa sering price mencapai floor
  - distance_compression_rate: seberapa cepat distance mengecil
  - distance_expansion_rate: seberapa cepat distance membesar
```

---

## 7. WAVE ARTIFACTS

```
Artifacts:
  - wave_lifetime: berapa lama wave structure bertahan
  - wave_stability: seberapa sering wave structure berubah
  - wave_prediction_accuracy: akurasi wave structure dalam memprediksi arah
  - wave_sequence_patterns: urutan wave yang sering muncul
  - optimal_wave_for_entry: wave structure dengan win_rate tertinggi per clone
  - wave_transition_probability: probabilitas transisi antar wave structures
```

---

## 8. KNOWLEDGE ARTIFACTS

```
Artifacts:
  - academy_bucket_growth: pertumbuhan sample per bucket dari waktu ke waktu
  - oracle_match_frequency: seberapa sering Oracle menemukan match
  - oracle_match_accuracy: akurasi Oracle match dalam memprediksi outcome
  - hivemind_accuracy: akurasi HiveMind bias vs actual outcome
  - cermin_calibration_trend: tren calibration error (membaik/memburuk)
  - librarian_lifecycle_distribution: distribusi status artifact
  - darwin_proposal_frequency: seberapa sering Darwin mengusulkan
  - darwin_proposal_acceptance: acceptance rate proposal Darwin
```

---

## 9. PREDICTION ARTIFACTS

```
Artifacts:
  - prediction_accuracy: akurasi empirical_win_rate vs actual
  - prediction_confidence_calibration: seberapa calibrated confidence
  - similarity_score_accuracy: korelasi similarity_score dengan outcome
  - dominant_bias_accuracy: akurasi dominant_bias vs actual direction
  - prediction_timeline: evolusi prediction accuracy dari waktu ke waktu
```

---

## 10. REPLAY ARTIFACTS

```
Artifacts:
  - replay_completeness: persentase frame yang berhasil di-replay
  - replay_determinism: determinism check per replay session
  - replay_performance: waktu yang dibutuhkan untuk replay
  - checkpoint_effectiveness: seberapa sering checkpoint digunakan
```

---

## 11. BENCHMARK ARTIFACTS

```
Artifacts:
  - wasit_pass_rate: persentase proposal yang lulus WASIT
  - gate_failure_distribution: gate mana yang paling sering gagal
  - fold_variance: variasi hasil antar fold
  - benchmark_duration: waktu yang dibutuhkan per benchmark
  - config_change_impact: dampak config change pada metrik
```

---

## 12. STATISTICS → BAG FLOW

```
┌──────────────────────────────────────────────────────────────────┐
│  STATISTICS LAYER                                                 │
│  (Raw Aggregation)                                                │
│                                                                    │
│  Produces:                                                        │
│    Trade Statistics, Market Statistics, Clone Statistics           │
│    Behavioral Artifacts, Distance Artifacts, Wave Artifacts       │
│                                                                    │
│  DOES NOT:                                                        │
│    Group, Classify, Find Patterns, Summarize Insights             │
│                                                                    │
├──────────────────────────────────────────────────────────────────┤
│                         │                                          │
│                         ▼                                          │
├──────────────────────────────────────────────────────────────────┤
│  BAG LAYER                                                        │
│  (Grouped Classification)                                         │
│                                                                    │
│  Consumes: ALL statistics artifacts                               │
│  Produces: bag_artifacts (grouped by bag_kind + bag_key)          │
│                                                                    │
│  DOES: Group, Classify, Count, Compare, Summarize, Score, Tag     │
│  DOES NOT: Raw aggregation (that's STATISTICS)                    │
│                                                                    │
├──────────────────────────────────────────────────────────────────┤
│                         │                                          │
│                         ▼                                          │
├──────────────────────────────────────────────────────────────────┤
│  KNOWLEDGE LAYER                                                  │
│  (Understanding)                                                  │
│                                                                    │
│  Consumes: BAG artifacts + raw statistics                         │
│  Produces: Academy, Oracle, HiveMind, CERMIN, Librarian, Darwin   │
│                                                                    │
│  DOES: Learn, Consume, Summarize, Infer, Recommend                │
│  DOES NOT: Group (that's BAG)                                     │
└──────────────────────────────────────────────────────────────────┘
```

---

## KESIMPULAN PATCH 05

**Statistics Layer** saat ini terlalu sederhana — hanya menghitung 8 metrik dasar dari trade markers. Dengan enrichment, Statistics dapat memproduksi **10 kategori artifacts** (Statistical, Behavioral, Market, Trading, Distance, Wave, Knowledge, Prediction, Replay, Benchmark) yang kemudian dikonsumsi oleh BAG untuk grouping dan classification.

**Pembagian tanggung jawab yang benar:**
- **STATISTICS**: Raw aggregation (WHAT happened)
- **BAG**: Grouped classification (WHY it happened, under WHAT conditions)
- **KNOWLEDGE**: Understanding (WHAT it MEANS)

**Tidak ada perubahan pada:** Konstitusi, spesifikasi, SQLite schema, pipeline stages, layer authority. Enrichment bersifat rekomendasi — implementasi tidak wajib.
# KNOWLEDGE LAYER ENRICHMENT — Patch 06

## ST-LMS Architecture Enrichment Patch V1

**Date:** 2026-07-28
**Status:** ENRICHMENT ANALYSIS — FROZEN
**Sources:** MASTER_SPECIFICATION.html §8, ST_LMS_CORE.js (KNOWLEDGE namespace), BAG_ARCHITECTURE_SPECIFICATION.md

---

## 1. ANALISIS: Grouping dipindahkan ke BAG

### 1.1 Current State

Saat ini, KNOWLEDGE layer melakukan beberapa operasi grouping:

| Entity | Grouping Operation | Should be in BAG? |
|--------|-------------------|-------------------|
| Academy | Group by clone, structure, distance_bucket, reason | ✅ YES — BAG |
| Academy | Count samples, wins, net per bucket | ⚠️ PARTIAL — BAG counts, Academy computes win_rate |
| Oracle | Euclidean similarity matching | ❌ NO — Knowledge-specific |
| HiveMind | Synthesize understanding from Academy + Oracle + Evidence | ❌ NO — Knowledge-specific |
| CERMIN | Calibration error per clone | ❌ NO — Knowledge-specific |
| Librarian | Lifecycle status per bucket | ❌ NO — Knowledge-specific |
| Darwin | Propose parameter mutations | ❌ NO — Knowledge-specific |

### 1.2 Proposed State

```
┌──────────────────────────────────────────────────────────────────┐
│  BAG LAYER (Grouping & Classification)                            │
│                                                                    │
│  DOES:                                                             │
│    - Group trade_markers by dimensions (clone, structure,         │
│      distance_bucket, reason, market_phase, etc.)                 │
│    - Count samples, wins, net per group                           │
│    - Classify into bag_kind (behavior, market, entry, exit,       │
│      risk, knowledge)                                             │
│    - Summarize consensus, conflict_level, confidence              │
│    - Detect patterns (bag_patterns)                               │
│    - Compress redundant artifacts (bag_compression)               │
│                                                                    │
│  DOES NOT:                                                        │
│    - Compute win_rate (that's Academy)                            │
│    - Compute expectancy (that's Academy)                          │
│    - Do similarity matching (that's Oracle)                       │
│    - Synthesize understanding (that's HiveMind)                   │
│    - Manage lifecycle (that's Librarian)                          │
│    - Propose mutations (that's Darwin)                            │
│                                                                    │
├──────────────────────────────────────────────────────────────────┤
│                         │                                          │
│                         ▼                                          │
├──────────────────────────────────────────────────────────────────┤
│  KNOWLEDGE LAYER (Learning & Understanding)                       │
│                                                                    │
│  DOES:                                                             │
│    - Learn from BAG artifacts                                     │
│    - Consume BAG grouped data                                     │
│    - Summarize insights (win_rate, expectancy from BAG counts)    │
│    - Infer patterns (Oracle similarity on BAG vectors)            │
│    - Recommend actions (Darwin proposals from BAG insights)       │
│                                                                    │
│  DOES NOT:                                                        │
│    - Group raw data (that's BAG)                                  │
│    - Classify artifacts (that's BAG)                              │
│    - Count samples per group (that's BAG)                         │
│    - Find consensus/conflict (that's BAG)                         │
└──────────────────────────────────────────────────────────────────┘
```

---

## 2. KNOWLEDGE ENTITY ENRICHMENT

### 2.1 Academy

```
CURRENT:
  Input: markers + snapshots
  Output: win_rate per (clone, structure, distance_bucket, reason)

ENRICHED:
  Input: BAG artifacts (pre-grouped) + raw markers (for verification)
  Output:
    - win_rate per BAG bag_key
    - expectancy per BAG bag_key
    - win_rate_trend (apakah win_rate membaik/memburuk)
    - sample_growth_rate (seberapa cepat sample bertambah)
    - confidence_interval (statistical confidence range)

  DOES: Learn win_rate from BAG groupings
  DOES NOT: Group markers into buckets (BAG does this)
```

### 2.2 River

```
CURRENT:
  Input: all cards
  Output: append + index + chronicle

ENRICHED:
  Input: all cards + BAG artifacts
  Output:
    - chronicle dengan BAG events
    - artifact lineage tracking
    - BAG artifact → knowledge artifact traceability

  DOES: Record everything (including BAG events)
  DOES NOT: Group or classify (BAG does this)
```

### 2.3 Oracle

```
CURRENT:
  Input: vector_now + historical vectors
  Output: oracle_match (euclidean, match > 7500)

ENRICHED:
  Input: vector_now + historical vectors + BAG similarity context
  Output:
    - oracle_match dengan BAG context
    - similarity per BAG bag_kind
    - historical pattern recurrence frequency
    - vector_cluster (kelompok vector yang mirip)

  DOES: Similarity matching (Knowledge-specific)
  DOES NOT: Group vectors (BAG can group Oracle results)
```

### 2.4 HiveMind

```
CURRENT:
  Input: academy_artifacts + oracle_match + evidence_snapshot
  Output: market_understanding (score, bias, boosts)

ENRICHED:
  Input: BAG artifacts + academy_artifacts + oracle_match + evidence_snapshot
  Output:
    - intelligence_score dengan BAG confidence adjustment
    - dominant_bias dengan BAG consensus validation
    - per_bag_kind_understanding (behavior, market, entry, exit, risk)
    - conflict_awareness (jika BAG conflict_level HIGH)

  DOES: Synthesize understanding (Knowledge-specific)
  DOES NOT: Group data (BAG does this)
```

### 2.5 CERMIN

```
CURRENT:
  Input: markers + confidence
  Output: calibration_error per clone

ENRICHED:
  Input: BAG artifacts (grouped confidence) + actual outcomes
  Output:
    - calibration_error per BAG bag_key
    - calibration_trend (apakah kalibrasi membaik)
    - overconfidence_detection (confidence > actual secara konsisten)
    - underconfidence_detection (confidence < actual secara konsisten)

  DOES: Calibrate confidence (Knowledge-specific)
  DOES NOT: Group calibration data (BAG does this)
```

### 2.6 Librarian

```
CURRENT:
  Input: academy_artifacts
  Output: lifecycle events (NEW→OBS→TRUSTED→MATURE/DEAD/DEPRECATED)

ENRICHED:
  Input: BAG artifacts + academy_artifacts
  Output:
    - lifecycle per BAG bag_key
    - lifecycle per BAG bag_kind
    - cross-bag lifecycle (artifact yang related)
    - stability_score (seberapa stabil lifecycle)

  DOES: Manage lifecycle (Knowledge-specific)
  DOES NOT: Group artifacts (BAG does this)
```

### 2.7 Darwin

```
CURRENT:
  Input: academy_artifacts
  Output: proposals (TIGHTEN_ENTRY, TIGHTEN_WRONG)

ENRICHED:
  Input: BAG artifacts + academy_artifacts + librarian_events
  Output:
    - proposals berdasarkan BAG conflict_level
    - proposals berdasarkan BAG consensus
    - per_bag_kind proposals (behavior, market, entry, exit, risk)
    - proposal_priority (berdasarkan BAG confidence)

  DOES: Propose mutations (Knowledge-specific)
  DOES NOT: Group proposal data (BAG does this)
```

---

## 3. KNOWLEDGE → BAG BOUNDARY

```
┌──────────────────────────────────────────────────────────────────┐
│                     KNOWLEDGE LAYER ONLY:                          │
│                                                                    │
│  ✅ LEARN      — Academy learns win_rate from BAG groupings       │
│  ✅ CONSUME    — All entities consume BAG artifacts               │
│  ✅ SUMMARIZE  — HiveMind summarizes market understanding         │
│  ✅ INFER      — Oracle infers similarity from vectors            │
│  ✅ RECOMMEND  — Darwin recommends parameter changes              │
│                                                                    │
│  ❌ GROUP      — MOVED TO BAG                                     │
│  ❌ CLASSIFY   — MOVED TO BAG                                     │
│  ❌ COUNT      — MOVED TO BAG                                     │
│  ❌ COMPARE    — MOVED TO BAG                                     │
│                                                                    │
├──────────────────────────────────────────────────────────────────┤
│                     BAG LAYER ONLY:                                │
│                                                                    │
│  ✅ GROUP      — Group markers by dimensions                     │
│  ✅ CLASSIFY   — Classify into bag_kind                          │
│  ✅ COUNT      — Count samples, wins, net per group              │
│  ✅ COMPARE    — Compare groups, find consensus/conflict          │
│  ✅ SUMMARIZE  — Summarize confidence per group                  │
│  ✅ SCORE      — Score consensus level                            │
│  ✅ TAG        — Tag with bag_key                                 │
│                                                                    │
│  ❌ LEARN      — STAYS IN KNOWLEDGE                               │
│  ❌ INFER      — STAYS IN KNOWLEDGE                               │
│  ❌ RECOMMEND  — STAYS IN KNOWLEDGE                               │
└──────────────────────────────────────────────────────────────────┘
```

---

## 4. KNOWLEDGE ENTITY DEPENDENCY (ENRICHED)

```
┌──────────────────────────────────────────────────────────────────┐
│                         BAG LAYER                                  │
│  bag_artifacts (grouped by bag_kind, bag_key)                     │
│  bag_patterns (detected patterns)                                 │
│  bag_compression (compression metrics)                            │
└──────────────────────────┬───────────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │ ACADEMY  │    │  ORACLE  │    │ HIVEMIND │
    │ (learn   │    │ (infer   │    │(synthesize│
    │ win_rate)│    │similarity│    │understand)│
    └────┬─────┘    └────┬─────┘    └────┬─────┘
         │               │               │
         └───────────────┼───────────────┘
                         │
          ┌──────────────┼──────────────┐
          │              │              │
          ▼              ▼              ▼
    ┌──────────┐  ┌──────────┐  ┌──────────┐
    │  CERMIN  │  │LIBRARIAN │  │  DARWIN  │
    │(calibrate│  │(lifecycle│  │(propose  │
    │confidence│  │ manage)  │  │mutation) │
    └──────────┘  └──────────┘  └──────────┘

    ┌──────────────────────────────────────────┐
    │                 RIVER                     │
    │  (records ALL events: BAG + Knowledge)    │
    └──────────────────────────────────────────┘
```

---

## KESIMPULAN PATCH 06

**Grouping sepenuhnya dipindahkan ke BAG.** Knowledge Layer TIDAK lagi melakukan operasi grouping, classification, counting, atau comparison. Operasi tersebut sepenuhnya menjadi tanggung jawab BAG.

**Knowledge Layer HANYA melakukan:**
- **LEARN** — Academy belajar win_rate dari BAG groupings
- **CONSUME** — Semua entities mengonsumsi BAG artifacts
- **SUMMARIZE** — HiveMind meringkas pemahaman market
- **INFER** — Oracle menginfer similarity dari vectors
- **RECOMMEND** — Darwin merekomendasikan parameter changes

**Pembagian yang jelas:**
- BAG = GROUPING ENGINE (what groups exist, how do they compare)
- KNOWLEDGE = LEARNING ENGINE (what can we learn from these groups)

**Tidak ada perubahan pada:** Konstitusi, spesifikasi, SQLite schema, pipeline stages, layer authority.
# FINAL LOGICAL PIPELINE — Patch 07

## ST-LMS Architecture Enrichment Patch V1

**Date:** 2026-07-28
**Status:** ENRICHMENT ANALYSIS — FROZEN
**Sources:** MASTER_SPECIFICATION.html §6, DOCUMENT_DEPENDENCY.html §4, QWEN_14_DOC.html D5, All Patch 01-06 analyses

---

## 1. FINAL LOGICAL PIPELINE

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    ST-LMS v3 — FINAL LOGICAL PIPELINE                      │
│                 (Enriched — 17 Logical Layers)                              │
└──────────────────────────────────────────────────────────────────────────┘

                                ┌──────────┐
                                │   BOOT   │  ONCE — System initialization
                                └────┬─────┘
                                     │
                          ═══════════╪═══════════
                          SHARED (1×) │
                          ═══════════╪═══════════
                                     │
                                ┌────▼─────┐
                                │  MARKET  │  Raw candle → market_snapshot
                                └────┬─────┘
                                     │
                                ┌────▼─────┐
                                │  TRUTH   │  Pure geometry → truth_snapshot
                                └────┬─────┘
                                     │
                          ┌──────────┼──────────┐
                          │          │          │
                    ┌─────▼─────┐ ┌──▼────────┐ │
                    │ DISTANCE  │ │ STRUCTURE │ │  LOGICAL SUB-LAYERS
                    │ (logical  │ │cage/wave/ │ │  (diproduksi bersama
                    │  sub-layer│ │ladder/    │ │   TRUTH + STRUCTURE)
                    │  of TRUTH │ │phase)     │ │
                    │ +STRUCTURE│ └─────┬─────┘ │
                    └─────┬─────┘       │       │
                          │             │       │
                          └──────┬──────┘       │
                                 │              │
                                ┌▼──────────────▼┐
                                │    EVIDENCE    │  3 buses → evidence_snapshot
                                └───────┬────────┘
                                        │
                          ══════════════╪═════════════
                          PER-CLONE (3×)│
                          ══════════════╪═════════════
                                        │
                    ┌───────────────────┼───────────────────┐
                    │                   │                   │
              ┌─────▼─────┐      ┌─────▼─────┐      ┌─────▼─────┐
              │   LONG    │      │   SHORT   │      │   GRID    │
              │   CLONE   │      │   CLONE   │      │   CLONE   │
              └─────┬─────┘      └─────┬─────┘      └─────┬─────┘
                    │                   │                   │
              ┌─────▼─────┐      ┌─────▼─────┐      ┌─────▼─────┐
              │   TRADE   │      │   TRADE   │      │   TRADE   │
              │ (entry/   │      │ (entry/   │      │ (grid     │
              │  exit)    │      │  exit)    │      │  fills)   │
              └─────┬─────┘      └─────┬─────┘      └─────┬─────┘
                    │                   │                   │
              ┌─────▼─────┐      ┌─────▼─────┐      ┌─────▼─────┐
              │ POSITION  │      │ POSITION  │      │ POSITION  │
              │  MGMT     │      │  MGMT     │      │  MGMT     │
              └─────┬─────┘      └─────┬─────┘      └─────┬─────┘
                    │                   │                   │
                    └───────────────────┼───────────────────┘
                                        │
                          ══════════════╪═════════════
                          SHARED-AGAIN  │
                          ══════════════╪═════════════
                                        │
                                ┌───────▼────────┐
                                │   STATISTICS   │  Raw aggregation
                                └───────┬────────┘
                                        │
                                ┌───────▼────────┐
                                │      BAG       │  Grouped classification
                                │  (grouping)    │
                                └───────┬────────┘
                                        │
                                ┌───────▼────────┐
                                │   KNOWLEDGE    │  Learning & Understanding
                                │ (learn/infer/  │
                                │  recommend)    │
                                └───────┬────────┘
                                        │
                                ┌───────▼────────┐
                                │  PREDICTION    │  Empirical probability
                                └───────┬────────┘
                                        │
                                ┌───────▼────────┐
                                │ TRADING SCHEMA │  Market condition →
                                │   (blueprint)  │  trading behavior mapping
                                └───────┬────────┘
                                        │
                                ┌───────▼────────┐
                                │  GOVERNANCE    │  Rem & kemudi
                                └───────┬────────┘
                                        │
                                ┌───────▼────────┐
                                │   CONSUMER     │  Trade intent (OPTIONAL)
                                └────────────────┘


┌──────────────────────────────────────────────────────────────────────────┐
│                         CROSS-CUTTING LAYERS                               │
│                                                                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐ │
│  │ SNAPSHOT │  │SIMULATION│  │  REPLAY  │  │ BENCHMARK│  │ DASHBOARD  │ │
│  │(immutable│  │(execute  │  │(6 types) │  │(WASIT    │  │(UI render) │ │
│  │ cards)   │  │ trades)  │  │          │  │ 5-gate)  │  │            │ │
│  └──────────┘  └──────────┘  └──────────┘  └────┬─────┘  └────────────┘ │
│                                                  │                        │
│                                            ON-DEMAND                      │
│                                         (tidak per candle)                 │
│                                                                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐                        │
│  │  AUDIT   │  │INTEGRATION│  │FINAL VALIDATION  │                        │
│  │(6 domains│  │(workers,  │  │(12-domain check) │                        │
│  │ verify)  │  │ bridges)  │  │                  │                        │
│  └──────────┘  └──────────┘  └──────────────────┘                        │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 2. PIPELINE STAGE CLASSIFICATION

| Stage | Layer | Type | Description |
|-------|-------|------|-------------|
| 0 | BOOT | ONCE | System initialization |
| 1 | MARKET | SHARED | Raw candle → market_snapshot |
| 2 | TRUTH | SHARED | Pure geometry → truth_snapshot |
| 2.5 | DISTANCE | SHARED (logical) | Distance metrics (sub-layer of TRUTH+STRUCTURE) |
| 3 | STRUCTURE | SHARED | Cage/wave/ladder/phase → structure_snapshot |
| 4 | EVIDENCE | SHARED | 3 buses → evidence_snapshot |
| 5 | CLONE (×3) | PER-CLONE | LONG/SHORT/GRID observation |
| 6 | TRADE (×3) | PER-CLONE | Entry/exit markers |
| 7 | POSITION (×3) | PER-CLONE | Position management |
| 8 | STATISTICS | SHARED-AGAIN | Raw aggregation |
| 9 | BAG | SHARED-AGAIN | Grouped classification |
| 10 | KNOWLEDGE | SHARED-AGAIN | Learning & understanding |
| 11 | PREDICTION | SHARED-AGAIN | Empirical probability |
| 12 | TRADING SCHEMA | SHARED-AGAIN | Market condition → behavior mapping |
| 13 | GOVERNANCE | SHARED-AGAIN | Rem & kemudi |
| — | BENCHMARK | ON-DEMAND | WASIT 5-gate (not per candle) |
| — | CONSUMER | OPTIONAL | Trade intent (terminal) |
| — | SNAPSHOT | CROSS-CUTTING | Immutable cards (all stages) |
| — | SIMULATION | CROSS-CUTTING | Trade execution (all PER-CLONE stages) |
| — | REPLAY | CROSS-CUTTING | 6 replay types (reads all snapshots) |
| — | DASHBOARD | CROSS-CUTTING | UI rendering (reads all cards) |
| — | AUDIT | CROSS-CUTTING | 6 domain verification |
| — | INTEGRATION | CROSS-CUTTING | Worker bridges, orchestration |
| — | FINAL VALIDATION | CROSS-CUTTING | 12-domain check |

---

## 3. PERBANDINGAN DENGAN CONTOH PROMPT

### 3.1 Contoh Prompt Pipeline (SALAH):

```
CANDLE → MARKET → TRUTH → DISTANCE → STRUCTURE → TRADING → STATISTICS
→ SNAPSHOT → SIMULATION → KNOWLEDGE → PREDICTION → TRADING SCHEMA
→ GOVERNANCE → BENCHMARK → DASHBOARD → INTEGRATION → FINAL AUDIT
```

**Koreksi berdasarkan referensi:**

| Contoh Prompt | Final Pipeline | Alasan Koreksi |
|---------------|---------------|----------------|
| CANDLE (terpisah) | MARKET (mencakup candle) | Candle adalah input MARKET, bukan layer terpisah |
| DISTANCE sebelum STRUCTURE | DISTANCE sebagai logical sub-layer | Distance metrics diproduksi di TRUTH (dist) + STRUCTURE (dist_ceiling/floor) |
| TRADING (tunggal) | CLONE → TRADE → POSITION (×3) | Trading adalah 3 stage PER-CLONE |
| SNAPSHOT setelah STATISTICS | SNAPSHOT sebagai CROSS-CUTTING | Snapshot diproduksi di setiap stage, bukan stage terpisah |
| SIMULATION setelah SNAPSHOT | SIMULATION sebagai CROSS-CUTTING | Simulation mengeksekusi seluruh pipeline |
| TRADING SCHEMA setelah PREDICTION | TRADING SCHEMA setelah PREDICTION | ✅ Benar — schema adalah blueprint yang mengonsumsi prediction |
| BENCHMARK setelah GOVERNANCE | BENCHMARK sebagai ON-DEMAND | Benchmark tidak per candle; on-demand saat proposal |
| DASHBOARD sebelum INTEGRATION | DASHBOARD sebagai CROSS-CUTTING | Dashboard membaca semua cards |
| FINAL AUDIT (terpisah) | FINAL VALIDATION (cross-cutting) | Final validation adalah gerbang akhir |

### 3.2 Perbedaan Utama

1. **DISTANCE** — Bukan layer fisik terpisah; logical sub-layer dari TRUTH + STRUCTURE
2. **SNAPSHOT** — Bukan pipeline stage; cross-cutting immutable card system
3. **SIMULATION** — Bukan pipeline stage; cross-cutting execution engine
4. **TRADING** — Dipecah menjadi CLONE → TRADE → POSITION (PER-CLONE ×3)
5. **BAG** — Ditambahkan antara STATISTICS dan KNOWLEDGE
6. **BENCHMARK** — ON-DEMAND, bukan per candle
7. **CONSUMER** — OPTIONAL terminal layer

---

## 4. DATA FLOW SUMMARY

```
MARKET ──market_snapshot──▶ TRUTH ──truth_snapshot──▶ STRUCTURE ──structure_snapshot──▶ EVIDENCE
                                  │                         │
                                  │ dist, distAtr           │ dist_ceiling, dist_floor
                                  ▼                         ▼
                            DISTANCE (logical sub-layer — metrics from TRUTH + STRUCTURE)
                                  │
                                  ▼
                            EVIDENCE ──evidence_snapshot──▶ CLONE (×3)
                                                               │
                                    ┌──────────────────────────┼──────────────────────────┐
                                    │                          │                          │
                                    ▼                          ▼                          ▼
                              LONG CLONE                  SHORT CLONE                 GRID CLONE
                                    │                          │                          │
                                    ▼                          ▼                          ▼
                              TRADE MARKERS              TRADE MARKERS              GRID FILLS
                                    │                          │                          │
                                    ▼                          ▼                          ▼
                              POSITION STATE             POSITION STATE             POSITION STATE
                                    │                          │                          │
                                    └──────────────────────────┼──────────────────────────┘
                                                               │
                                                               ▼
                                                         STATISTICS
                                                               │
                                                               ▼
                                                             BAG
                                                               │
                                                               ▼
                                                          KNOWLEDGE
                                                               │
                                                               ▼
                                                          PREDICTION
                                                               │
                                                               ▼
                                                        TRADING SCHEMA
                                                               │
                                                               ▼
                                                          GOVERNANCE
                                                               │
                                                               ▼
                                                           CONSUMER
```

---

## 5. VALIDATION

### 5.1 Specification Compliance

| Check | Status |
|-------|--------|
| 18 LAW-MASTER compliant | ✅ |
| 16 constitutions frozen | ✅ |
| 22 pipeline stages preserved | ✅ |
| SHARED / PER-CLONE / SHARED-AGAIN / ON-DEMAND preserved | ✅ |
| Card Sharing (1× compute, 3× share) preserved | ✅ |
| Unidirectional flow preserved | ✅ |
| No backward loops to Core | ✅ |
| 10 snapshots preserved | ✅ |
| 6 knowledge entities preserved | ✅ |
| 3 clone types preserved | ✅ |

### 5.2 Enrichment Compliance

| Enrichment | Status |
|-----------|--------|
| Distance as logical sub-layer (not physical) | ✅ No spec change |
| BAG between STATISTICS and KNOWLEDGE | ✅ Consistent with SQLite FK chain |
| Trading Schema as blueprint layer | ✅ No spec change |
| Statistics enrichment (10 artifact categories) | ✅ No spec change |
| Knowledge enrichment (grouping → BAG) | ✅ No spec change |
| 24 trading schemas defined | ✅ Derived from existing rules |

### 5.3 No Violations

- ❌ Tidak ada perubahan konstitusi
- ❌ Tidak ada perubahan spesifikasi
- ❌ Tidak ada perubahan SQLite schema
- ❌ Tidak ada perubahan pipeline stages
- ❌ Tidak ada perubahan layer authority
- ❌ Tidak ada circular dependency
- ❌ Tidak ada specification conflict

---

## KESIMPULAN PATCH 07

**Final Logical Pipeline** mendefinisikan 17 logical layers dengan aliran data yang jelas:

```
BOOT → MARKET → TRUTH (+DISTANCE) → STRUCTURE (+DISTANCE) → EVIDENCE
→ CLONE(×3) → TRADE(×3) → POSITION(×3)
→ STATISTICS → BAG → KNOWLEDGE → PREDICTION → TRADING SCHEMA → GOVERNANCE → CONSUMER
+ BENCHMARK (ON-DEMAND)
+ SNAPSHOT, SIMULATION, REPLAY, DASHBOARD, AUDIT, INTEGRATION, FINAL VALIDATION (CROSS-CUTTING)
```

Pipeline ini diperkaya dengan:
- **DISTANCE** sebagai logical sub-layer (14 metrics)
- **BAG** sebagai grouping layer antara STATISTICS dan KNOWLEDGE
- **TRADING SCHEMA** sebagai blueprint layer (24 schemas)
- **STATISTICS** diperkaya dengan 10 artifact categories
- **KNOWLEDGE** dengan grouping dipindahkan ke BAG

**BUILD CAN PROCEED TO PHASE 1 IMPLEMENTATION.**
