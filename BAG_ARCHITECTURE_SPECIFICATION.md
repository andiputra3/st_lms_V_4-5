# BAG ARCHITECTURE SPECIFICATION

## ST-LMS — Behavioral Artifact Grouping

**Date:** 2026-07-28
**Status:** ARCHITECTURE SPECIFICATION — FROZEN
**Sources:** STLMS_SQLITE_SCHEMA_V1.sql (lines 410–448), MASTER_SPECIFICATION.html, DOCUMENT_DEPENDENCY.html, QWEN_14_DOC.html, ST_LMS_CORE.js

---

## 1. IDENTITAS BAG

### 1.1 Definisi Formal

**BAG = Behavioral Artifact Grouping** — adalah statistical engine dalam ST-LMS yang bertanggung jawab untuk mengelompokkan, mengklasifikasi, dan meringkas artifact yang dihasilkan oleh pipeline ST-LMS. BAG beroperasi sebagai intermediate aggregation layer antara STATISTICS dan KNOWLEDGE.

### 1.2 BAG BUKAN

- ❌ AI / Machine Learning engine
- ❌ Trading engine / Decision engine
- ❌ Executor / Predictor
- ❌ Governance engine
- ❌ Replacement untuk Knowledge layer

### 1.3 BAG ADALAH

- ✅ Statistical engine
- ✅ Artifact grouping engine
- ✅ Historical grouping engine
- ✅ Knowledge grouping engine
- ✅ Market behavior grouping engine
- ✅ Performance grouping engine

---

## 2. TUJUAN BAG

### 2.1 Tujuan Utama

1. **Mengelompokkan artifact** yang dihasilkan ST-LMS berdasarkan dimensi perilaku
2. **Membangun knowledge statistik** dari pengelompokan historis
3. **Mencari pola perilaku market** melalui agregasi multi-dimensi
4. **Mengelompokkan kondisi market** berdasarkan phase, wave, cage
5. **Mengelompokkan performa trading** per clone, per kondisi, per bucket
6. **Mengelompokkan snapshot** untuk analisis komparatif
7. **Menghasilkan insight statistik** yang dapat dikonsumsi Knowledge layer

### 2.2 Batasan Tujuan

BAG TIDAK BOLEH mengubah hasil analisis ST-LMS. BAG hanya membaca, mengelompokkan, dan meringkas — tidak pernah memodifikasi data sumber.

---

## 3. AUTHORITY MATRIX

### 3.1 Operasi yang DIIZINKAN

| Operasi | Deskripsi | Contoh |
|---------|-----------|--------|
| READ | Membaca data dari layer lain | Membaca trade_statistics, market_statistics |
| COLLECT | Mengumpulkan artifact dari berbagai sumber | Mengumpulkan marker + snapshot |
| GROUP | Mengelompokkan berdasarkan dimensi | Group by market_phase, wave_structure |
| CLASSIFY | Mengklasifikasi ke dalam kategori | behavior, market, entry, exit, risk, knowledge |
| COUNT | Menghitung frekuensi | Sample count per group |
| COMPARE | Membandingkan antar kelompok | Win rate LONG vs SHORT pada kondisi sideways |
| SUMMARIZE | Meringkas statistik | Consensus, conflict_level, confidence |
| SCORE | Memberikan skor konsensus | Confidence score per bag artifact |
| TAG | Memberikan label | bag_kind, bag_key |

### 3.2 Operasi yang DILARANG

| Operasi Terlarang | Alasan |
|-------------------|--------|
| Entry Decision | Melanggar authority CLONE layer |
| Exit Decision | Melanggar authority CLONE layer |
| Trading Decision | Melanggar pipeline unidirectional |
| Prediction Decision | Melanggar authority PREDICTION layer |
| Governance Decision | Melanggar authority GOVERNANCE layer |
| Override Indicator | Melanggar TRUTH authority |
| Override Truth Layer | Melanggar single source of truth |
| Override Market Layer | Melanggar MARKET authority |
| Override Structure Layer | Melanggar STRUCTURE authority |
| Override Trading Layer | Melanggar TRADE authority |
| Override Statistics Layer | Melanggar STATISTICS authority |
| Override Knowledge Layer | Melanggar KNOWLEDGE authority |
| Modify Pipeline | Melanggar arsitektur pipeline |
| Modify Specification | Melanggar konstitusi beku |
| Modify SQLite Schema | Melanggar schema freeze |
| Modify Snapshot | Melanggar immutability card |

---

## 4. LAYER AUTHORITY

### 4.1 Layer yang BOLEH menggunakan BAG

| Layer | Alasan |
|-------|--------|
| **STATISTICS** | BAG membaca trade_statistics dan market_statistics sebagai input |
| **KNOWLEDGE** | BAG adalah intermediate layer; knowledge_artifacts membaca bag_id |
| **SNAPSHOT** | BAG dapat mengelompokkan snapshot untuk analisis komparatif |
| **BENCHMARK** | BAG dapat menyediakan grouped statistics untuk WASIT evaluation |
| **DASHBOARD** | BAG dapat menyediakan grouped insights untuk visualisasi |

### 4.2 Layer yang TIDAK BOLEH menggunakan BAG

| Layer | Alasan |
|-------|--------|
| **MARKET** | BAG adalah downstream; MARKET tidak boleh membaca downstream |
| **TRUTH** | BAG adalah downstream; TRUTH tidak boleh membaca downstream |
| **STRUCTURE** | BAG adalah downstream; STRUCTURE tidak boleh membaca downstream |
| **EVIDENCE** | BAG adalah downstream; EVIDENCE tidak boleh membaca downstream |
| **CLONE** | Clone tidak boleh membaca BAG (melanggar unidirectional flow) |
| **TRADE** | Trade tidak boleh membaca BAG (melanggar unidirectional flow) |
| **POSITION** | Position tidak boleh membaca BAG (melanggar unidirectional flow) |
| **GOVERNANCE** | Governance tidak boleh membaca BAG secara langsung (menggunakan Knowledge sebagai perantara) |

### 4.3 Authority Boundary

```
┌──────────────────────────────────────────────────────────────────┐
│  UPSTREAM (tidak boleh membaca BAG):                              │
│  MARKET → TRUTH → STRUCTURE → EVIDENCE → CLONE → TRADE → POSITION│
│                                                                    │
│  ═══════════════════════════════════════════════════════════════ │
│                                                                    │
│  DOWNSTREAM (boleh membaca BAG):                                   │
│  STATISTICS → BAG → KNOWLEDGE → PREDICTION → GOVERNANCE           │
│                                                                    │
│  CROSS-CUTTING (boleh membaca BAG):                                │
│  BENCHMARK, DASHBOARD, AUDIT, SNAPSHOT                             │
└──────────────────────────────────────────────────────────────────┘
```

---

## 5. LIFECYCLE

### 5.1 BAG Lifecycle States

```
┌──────────┐     ┌──────────────┐     ┌──────────┐     ┌──────────┐
│  EMPTY   │────▶│  COLLECTING  │────▶│  ACTIVE  │────▶│  FROZEN  │
│(no data) │     │(gathering    │     │(producing│     │(archived)│
│          │     │ artifacts)   │     │ insights)│     │          │
└──────────┘     └──────────────┘     └──────────┘     └──────────┘
                       │                    │
                       │                    ▼
                       │             ┌──────────┐
                       └────────────▶│  STALE   │
                                     │(outdated)│
                                     └──────────┘
```

| State | Deskripsi | Transisi |
|-------|-----------|----------|
| EMPTY | BAG artifact belum memiliki data | sample_count = 0 → COLLECTING |
| COLLECTING | BAG sedang mengumpulkan artifact | sample_count > 0 → ACTIVE |
| ACTIVE | BAG aktif memproduksi insight | sample_count ≥ threshold |
| FROZEN | BAG artifact diarsipkan (tidak aktif) | Manual freeze |
| STALE | BAG artifact kadaluarsa | Data source berubah signifikan |

### 5.2 Lifecycle per Bag Artifact

1. **CREATE** — BAG artifact dibuat dengan bag_key unik per session
2. **COLLECT** — BAG mengumpulkan data dari trade_statistics, market_statistics
3. **CLASSIFY** — BAG mengklasifikasi ke dalam bag_kind
4. **GROUP** — BAG mengelompokkan berdasarkan dimensi
5. **SUMMARIZE** — BAG menghasilkan consensus, conflict_level, confidence
6. **COMPRESS** — BAG mengompresi artifact redundant
7. **ARCHIVE** — BAG artifact di-freeze untuk referensi historis

---

## 6. DEPENDENCY

### 6.1 Upstream Dependencies

| Dependency | Type | Deskripsi |
|-----------|------|-----------|
| STATISTICS | MANDATORY | trade_statistics menyediakan data trading yang dikelompokkan |
| SNAPSHOT | MANDATORY | Snapshot history menyediakan konteks market |
| MARKET | OPTIONAL | market_statistics untuk pengelompokan kondisi market |

### 6.2 Downstream Dependencies

| Consumer | Type | Deskripsi |
|----------|------|-----------|
| KNOWLEDGE | MANDATORY | knowledge_artifacts membaca bag_id untuk referensi |
| BENCHMARK | OPTIONAL | Benchmark dapat menggunakan BAG untuk grouped evaluation |
| DASHBOARD | OPTIONAL | Dashboard dapat menampilkan BAG insights |

### 6.3 Forbidden Dependencies

| Dependency | Alasan |
|-----------|--------|
| TRUTH ← BAG | Upstream tidak boleh membaca downstream |
| STRUCTURE ← BAG | Upstream tidak boleh membaca downstream |
| CLONE ← BAG | Melanggar unidirectional flow |
| TRADE ← BAG | Melanggar unidirectional flow |
| GOVERNANCE ← BAG | Governance menggunakan Knowledge, bukan BAG langsung |

---

## 7. PIPELINE POSITION

### 7.1 Analisis Referensi

Berdasarkan SQLite schema:
- `bag_artifacts` memiliki FK ke `trade_statistics` (stat_id)
- `knowledge_artifacts` memiliki FK ke `bag_artifacts` (bag_id)
- `bag_artifacts` memiliki `bag_kind` termasuk 'knowledge'

Berdasarkan DOCUMENT_DEPENDENCY §3 (Feature Dependency):
- STATISTICS menghasilkan → KNOWLEDGE mengonsumsi
- BAG tidak disebutkan dalam pipeline formal

### 7.2 Pipeline Position yang Direkomendasikan

**OPTION A** — BAG antara STATISTICS dan KNOWLEDGE:

```
STATISTICS
    │
    ▼
   BAG (Behavioral Artifact Grouping)
    │  - Membaca trade_statistics + market_statistics
    │  - Mengelompokkan per bag_kind + bag_key
    │  - Menghasilkan consensus, conflict_level, confidence
    │  - Mengompresi artifact redundant
    │
    ▼
KNOWLEDGE
    │  - Academy: membaca bag_artifacts untuk win_rate per bucket
    │  - Oracle: dapat membaca bag_artifacts untuk similarity context
    │  - HiveMind: dapat membaca bag_artifacts untuk understanding
    │  - Librarian: lifecycle management BAG artifacts
```

**Alasan pemilihan OPTION A:**

1. **SQLite FK chain**: `trade_statistics` → `bag_artifacts` → `knowledge_artifacts`
2. **Data flow**: Statistics (raw aggregation) → BAG (grouped insights) → Knowledge (understanding)
3. **Unidirectional**: STATISTICS → BAG → KNOWLEDGE (tidak ada loop)
4. **Card-agnostic**: BAG membaca card, tidak memodifikasi card
5. **SHARED-AGAIN**: BAG berjalan 1× setelah STATISTICS, sebelum KNOWLEDGE

### 7.3 Pipeline Stage Classification

```
STAGE  TYPE              NAME                    DESCRIPTION
─────  ────────────────  ──────────────────────  ──────────────────────────
13     SHARED-AGAIN      STATISTICS              Aggregate trade/market stats
13.5   SHARED-AGAIN      BAG                     Group & classify artifacts
14     SHARED-AGAIN      KNOWLEDGE               Academy, Oracle, HiveMind...
```

---

## 8. SQLITE MAPPING

### 8.1 SQLite Tables yang Digunakan BAG

| Table | Access | Purpose |
|-------|--------|---------|
| `trade_statistics` | READ | Sumber data trading untuk pengelompokan |
| `market_statistics` | READ | Sumber data market untuk pengelompokan |
| `trade_markers` | READ | Data marker untuk analisis detail |
| `positions` | READ | Data posisi untuk pengelompokan |
| `structure_snapshots` | READ | Konteks market (phase, wave, cage) |
| `evidence_snapshots` | READ | Konteks evidence (bus data) |
| `truth_snapshots` | READ | Konteks truth (indicator values) |

### 8.2 SQLite Tables yang Ditulis BAG

| Table | Access | Purpose |
|-------|--------|---------|
| `bag_artifacts` | WRITE | Hasil pengelompokan BAG |
| `bag_patterns` | WRITE | Pola yang ditemukan dalam artifact |
| `bag_compression` | WRITE | Metrik kompresi artifact |

### 8.3 SQLite Tables yang Tidak Boleh Disentuh BAG

| Table | Alasan |
|-------|--------|
| `market_candles` | MARKET layer authority |
| `truth_snapshots` | TRUTH layer authority (read-only) |
| `structure_snapshots` | STRUCTURE layer authority (read-only) |
| `evidence_snapshots` | EVIDENCE layer authority (read-only) |
| `clone_observations` | CLONE layer authority (read-only) |
| `trade_markers` | TRADE layer authority (read-only) |
| `positions` | POSITION layer authority (read-only) |
| `governance_proposals` | GOVERNANCE layer authority |
| `predictions` | PREDICTION layer authority |
| `knowledge_artifacts` | KNOWLEDGE layer authority (BAG tidak menulis knowledge) |

### 8.4 Artifact yang Disimpan BAG

| Artifact | Table | Kolom Kunci |
|----------|-------|-------------|
| Bag Artifact | `bag_artifacts` | bag_id, bag_kind, bag_key, consensus, conflict_level, confidence, sample_count |
| Bag Pattern | `bag_patterns` | pattern_id, pattern_rank, pattern_key, pattern_value |
| Bag Compression | `bag_compression` | compression_id, source_count, compressed_count, compression_ratio |

### 8.5 Artifact yang Tidak Boleh Disimpan BAG

- ❌ Raw market data (milik MARKET)
- ❌ Truth indicators (milik TRUTH)
- ❌ Structure geometry (milik STRUCTURE)
- ❌ Clone observations (milik CLONE)
- ❌ Trade markers (milik TRADE)
- ❌ Governance decisions (milik GOVERNANCE)

### 8.6 Lifecycle Penyimpanan BAG

```
1. CREATE bag_artifact dengan bag_key unik
2. COLLECT data dari trade_statistics + market_statistics
3. UPDATE bag_artifact dengan consensus, confidence
4. CREATE bag_patterns untuk pola yang ditemukan
5. CREATE bag_compression untuk metrik kompresi
6. ARCHIVE — bag_artifact dipertahankan untuk referensi historis
7. DELETE — hanya melalui CASCADE dari app_sessions
```

---

## 9. ARTIFACT MAPPING

### 9.1 Bag Kinds (6 jenis)

| bag_kind | Deskripsi | Sumber Data |
|----------|-----------|-------------|
| `behavior` | Pengelompokan perilaku market | market_statistics + structure_snapshots |
| `market` | Pengelompokan kondisi market | market_statistics + truth_snapshots |
| `entry` | Pengelompokan entry patterns | trade_markers (kind=ENTRY) |
| `exit` | Pengelompokan exit patterns | trade_markers (kind=EXIT) |
| `risk` | Pengelompokan risk metrics | positions + trade_statistics |
| `knowledge` | Pengelompokan knowledge patterns | knowledge_artifacts (read-only input) |

### 9.2 Bag Key Structure

```
bag_key = "{bag_kind}|{dimension_1}|{dimension_2}|...|{dimension_n}"

Contoh:
  "behavior|UPTREND|STRONG_ACCUMULATION|LONG"
  "market|SIDEWAY_COMPRESSION|CONFIRMED_RANGE|0.65"
  "entry|LONG|CORRIDOR|OPTIMAL"
  "exit|SHORT|WRONG_ENTRY_EARLY|NEAR"
  "risk|GRID|VALID_COMPRESSION|2"
```

### 9.3 Bag Consensus & Conflict

| Field | Deskripsi | Nilai |
|-------|-----------|-------|
| `consensus` | Tingkat kesepakatan antar artifact | "HIGH", "MEDIUM", "LOW", "NONE" |
| `conflict_level` | Tingkat konflik dalam kelompok | "NONE", "LOW", "MEDIUM", "HIGH" |
| `confidence` | Confidence score (0-10000) | Berdasarkan sample_count + consensus |

### 9.4 Bag Patterns

| Field | Deskripsi |
|-------|-----------|
| `pattern_rank` | Urutan pola (1 = dominan) |
| `pattern_key` | Kunci pola (mis: "WIN_RATE", "EXPECTANCY", "FREQUENCY") |
| `pattern_value` | Nilai pola (mis: "65.5", "0.023", "142") |

### 9.5 Bag Compression

| Field | Deskripsi |
|-------|-----------|
| `source_count` | Jumlah artifact sumber sebelum kompresi |
| `compressed_count` | Jumlah artifact setelah kompresi |
| `compression_ratio` | Rasio kompresi (compressed / source) |

---

## 10. SNAPSHOT MAPPING

### 10.1 Snapshot yang Dibaca BAG

| Snapshot | Data yang Digunakan | Purpose |
|----------|-------------------|---------|
| Market Snapshot | OHLCV, data_status, gap_flag | Data quality grouping |
| Truth Snapshot | stDir, color, distAtr, rsi, wpr | Indicator grouping |
| Structure Snapshot | cage_status, wave_structure, market_phase, pp | Market condition grouping |
| Evidence Snapshot | dir_bus, exit_bus, correction_bus | Evidence grouping |
| Trade Snapshot | markers (kind, reason, result, net) | Trade performance grouping |
| Statistics Snapshot | win_rate, expectancy, pf, mae, mfe | Statistics grouping |
| Knowledge Snapshot | academy_artifacts, oracle_match, hivemind | Knowledge grouping |

### 10.2 Snapshot yang Dihasilkan BAG

BAG TIDAK menghasilkan snapshot sendiri. BAG menyimpan hasil ke `bag_artifacts`, `bag_patterns`, `bag_compression`. Knowledge Snapshot dapat merujuk BAG artifacts melalui `bag_id`.

---

## 11. STATISTICS MAPPING

### 11.1 Statistics yang Dibaca BAG

| Statistics | Purpose |
|-----------|---------|
| trade_statistics.win_rate | Pengelompokan win rate per kondisi |
| trade_statistics.expectancy | Pengelompokan expectancy per clone |
| trade_statistics.profit_factor | Pengelompokan PF per kondisi |
| trade_statistics.mae / mfe | Pengelompokan excursion per bucket |
| trade_statistics.fee_drag | Pengelompokan fee impact |
| trade_statistics.wrong_rate | Pengelompokan wrong entry frequency |
| market_statistics.phase | Pengelompokan market phase distribution |
| market_statistics.wave_structure | Pengelompokan wave structure distribution |
| market_statistics.support_hits / resistance_hits | Pengelompokan S/R interaction |

### 11.2 Statistics yang Dihasilkan BAG

BAG TIDAK menghasilkan statistics baru. BAG mengelompokkan statistics yang sudah ada.

---

## 12. KNOWLEDGE MAPPING

### 12.1 Hubungan BAG → Knowledge

```
BAG menghasilkan:
  bag_artifacts (bag_id, bag_kind, bag_key, consensus, confidence)
        │
        ▼
KNOWLEDGE membaca:
  knowledge_artifacts.bag_id → REFERENCES bag_artifacts
        │
        ▼
KNOWLEDGE entities:
  - Academy: dapat membaca BAG untuk win_rate grouping
  - Oracle: dapat membaca BAG untuk similarity context
  - HiveMind: dapat membaca BAG untuk understanding synthesis
  - Librarian: lifecycle management untuk BAG artifacts
  - Darwin: dapat membaca BAG untuk proposal generation
```

### 12.2 BAG → Knowledge Flow

```
STATISTICS
    │
    ▼
  BAG ──── bag_artifacts ────▶ KNOWLEDGE
    │                              │
    │                              ├── Academy (win_rate per bag_key)
    │                              ├── Oracle (similarity per bag_kind)
    │                              ├── HiveMind (understanding per consensus)
    │                              ├── Darwin (proposals per conflict_level)
    │                              └── Librarian (lifecycle per bag_artifact)
```

---

## 13. BENCHMARK MAPPING

### 13.1 Benchmark yang Dapat Menggunakan BAG

| Benchmark | Penggunaan BAG |
|-----------|---------------|
| WASIT 5-Gate | BAG dapat menyediakan grouped statistics untuk evaluasi per-fold |
| Clone Benchmark | BAG dapat membandingkan performa LONG vs SHORT vs GRID |
| Trade Benchmark | BAG dapat mengelompokkan trade per kondisi market |
| Market Benchmark | BAG dapat mengelompokkan market phase distribution |

### 13.2 Batasan Benchmark

BAG TIDAK BOLEH:
- Menggantikan WASIT evaluation
- Membuat keputusan benchmark
- Mengubah benchmark verdict

---

## 14. DASHBOARD MAPPING

### 14.1 Dashboard Components yang Dapat Menggunakan BAG

| Component | Penggunaan BAG |
|-----------|---------------|
| Behavior Panel | Menampilkan consensus dan conflict_level per bag_kind |
| Market Condition Panel | Menampilkan distribusi market phase dari BAG |
| Performance Panel | Menampilkan grouped win_rate dan expectancy |
| Pattern Panel | Menampilkan bag_patterns yang ditemukan |
| Compression Panel | Menampilkan metrik kompresi artifact |

### 14.2 Batasan Dashboard

Dashboard TIDAK BOLEH:
- Menggunakan BAG sebagai pengganti data pipeline
- Menampilkan BAG insights sebagai trading signals

---

## 15. TRADING SCHEMA MAPPING

### 15.1 Apakah BAG Boleh Membaca Trading Data?

| Data | Boleh? | Alasan |
|------|--------|--------|
| Trade History (trade_markers) | ✅ YES | BAG mengelompokkan trade untuk analisis statistik |
| Position History (positions) | ✅ YES | BAG mengelompokkan posisi untuk risk analysis |
| Market State (market_statistics) | ✅ YES | BAG mengelompokkan kondisi market |
| Clone History (clone_observations) | ✅ YES | BAG mengelompokkan observasi clone |
| Distance History (dist_to_st, distAtr) | ✅ YES | BAG mengelompokkan distance metrics |
| Snapshot History (all snapshots) | ✅ YES | BAG mengelompokkan snapshot untuk analisis |
| Knowledge History (knowledge_artifacts) | ✅ YES | BAG membaca knowledge untuk bag_kind='knowledge' |
| Prediction History (predictions) | ✅ YES | BAG mengelompokkan prediksi untuk kalibrasi |
| Benchmark History (benchmark_runs) | ✅ YES | BAG mengelompokkan benchmark results |

### 15.2 Apakah BAG Boleh Mempengaruhi Trading?

**TIDAK.** BAG adalah read-only aggregator. BAG tidak boleh mempengaruhi keputusan trading. Data BAG hanya dikonsumsi oleh Knowledge layer yang kemudian dapat mempengaruhi Governance (melalui bounded parameter proposals), tetapi tidak pernah langsung ke Clone/Trade.

---

## 16. INTEGRATION MAPPING

### 16.1 Integration Points

| Integration | From | To | Direction | Type |
|-------------|------|----|-----------|------|
| I-BAG-01 | STATISTICS | BAG | → | MANDATORY |
| I-BAG-02 | BAG | KNOWLEDGE | → | MANDATORY |
| I-BAG-03 | SNAPSHOT | BAG | → | OPTIONAL |
| I-BAG-04 | BAG | BENCHMARK | → | OPTIONAL |
| I-BAG-05 | BAG | DASHBOARD | → | OPTIONAL |
| I-BAG-06 | BAG | AUDIT | → | OPTIONAL |

### 16.2 Integration Rules

1. **BAG membaca dari STATISTICS** — wajib, tanpa ini BAG tidak memiliki data
2. **BAG menulis ke KNOWLEDGE** — melalui bag_id FK di knowledge_artifacts
3. **BAG tidak menulis ke STATISTICS** — unidirectional flow
4. **BAG tidak menulis ke TRADE/CLONE** — forbidden
5. **BAG dapat dibaca oleh BENCHMARK** — opsional, untuk grouped evaluation

---

## 17. GOVERNANCE CONSTRAINT

### 17.1 Batasan Governance

| Aturan | Deskripsi |
|--------|-----------|
| BAG tidak boleh membuat proposal governance | Proposal hanya dari Darwin |
| BAG tidak boleh memodifikasi bounded parameters | Hanya GOVERNANCE yang boleh |
| BAG tidak boleh meng-override keputusan governance | Governance adalah otoritas tertinggi |
| BAG dapat menjadi input untuk Darwin | Melalui Knowledge layer (tidak langsung) |
| BAG artifacts dapat di-audit | Audit logs dapat mencatat BAG events |

### 17.2 Governance → BAG Flow

```
GOVERNANCE (config_version, bounded params)
    │
    │ (tidak langsung — melalui STATISTICS yang menggunakan config)
    ▼
STATISTICS (trade_statistics dengan config_version)
    │
    ▼
  BAG (mengelompokkan statistics yang dipengaruhi config)
    │
    ▼
KNOWLEDGE (Darwin membaca BAG artifacts via Knowledge)
    │
    ▼
GOVERNANCE (Darwin proposals berdasarkan BAG insights)
```

---

## 18. VALIDATION RULE

### 18.1 Validator untuk BAG

| Validator | Purpose | Gate |
|-----------|---------|------|
| Sample Gate | bag_artifact.sample_count ≥ threshold | HARD |
| Confidence Validator | confidence dalam range 0-10000 | HARD |
| Uniqueness Validator | bag_key unik per session | HARD |
| FK Validator | stat_id references valid | HARD |
| Bag Kind Validator | bag_kind dalam CHECK constraint | HARD |
| Consensus Validator | consensus dalam nilai yang valid | SOFT |
| Compression Validator | compression_ratio dalam range 0-1 | SOFT |

### 18.2 Validation Rules

1. **Sample Gate**: BAG artifact hanya valid jika sample_count ≥ threshold (direkomendasikan: 30, sama dengan SAMPLE_GATE)
2. **Confidence Range**: confidence harus dalam 0-10000
3. **Unique Key**: bag_key harus unik per session
4. **FK Integrity**: stat_id harus merujuk trade_statistics yang valid
5. **Bag Kind**: bag_kind harus salah satu dari 6 nilai yang diizinkan
6. **No Write-back**: BAG tidak boleh menulis ke tabel upstream

---

## 19. BUILD RECOMMENDATION

### 19.1 Build Order

```
Build Order: 9.5 (antara STATISTICS dan KNOWLEDGE)
Dependencies: STATISTICS (trade_statistics, market_statistics)
Build setelah: STATISTICS
Build sebelum: KNOWLEDGE
```

### 19.2 Build Sequence

```
S9: STATISTICS + KNOWLEDGE
  ├── 9.1: Trade Statistics
  ├── 9.2: Market Statistics
  ├── 9.3: Sample Gate
  ├── 9.4: BAG Engine ← (ditambahkan di sini)
  │     ├── bag_artifacts (grouping)
  │     ├── bag_patterns (pattern detection)
  │     └── bag_compression (compression)
  ├── 9.5: River
  ├── 9.6: Academy (membaca bag_artifacts)
  ├── 9.7: Oracle
  ├── 9.8: HiveMind
  ├── 9.9: CERMIN
  ├── 9.10: Librarian
  └── 9.11: Darwin
```

### 19.3 Implementation Priority

| Priority | Component | Reason |
|----------|-----------|--------|
| HIGH | bag_artifacts table | Fondasi penyimpanan BAG |
| HIGH | BAG grouping engine | Core functionality |
| MEDIUM | bag_patterns detection | Pattern recognition |
| LOW | bag_compression | Optimization |
| LOW | BAG Dashboard panels | Visualization |

---

## 20. FUTURE EXTENSION RECOMMENDATION

### 20.1 Extensions yang Konsisten dengan Arsitektur

| Extension | Deskripsi | Impact |
|-----------|-----------|--------|
| BAG Cross-Session Analysis | Membandingkan BAG artifacts antar session | LOW — read-only |
| BAG Trend Detection | Mendeteksi tren dalam BAG artifacts dari waktu ke waktu | MEDIUM — perlu time-series analysis |
| BAG Anomaly Detection | Mendeteksi anomali dalam BAG groupings | MEDIUM — perlu threshold definition |
| BAG Correlation Engine | Mencari korelasi antar bag_kind | HIGH — perlu statistical framework |
| BAG Export/Import | Export BAG artifacts untuk analisis eksternal | LOW — format JSON/CSV |

### 20.2 Extensions yang DILARANG

| Extension | Alasan |
|-----------|--------|
| BAG Auto-Trading | Melanggar authority CLONE layer |
| BAG Prediction Engine | Melanggar authority PREDICTION layer |
| BAG Governance Engine | Melanggar authority GOVERNANCE layer |
| BAG ML Model | Melanggar no-ML rule (LAW-MASTER-13) |
| BAG Signal Generator | Melanggar no-reduction rule (LAW-MASTER-07) |
| BAG Real-time Engine | Melanggar SHARED-AGAIN pipeline stage |

---

## FINAL VERDICT

**BAG = Behavioral Artifact Grouping** didefinisikan sebagai statistical engine yang:

1. **POSISI**: Intermediate layer antara STATISTICS dan KNOWLEDGE (OPTION A)
2. **PIPELINE**: SHARED-AGAIN stage (13.5), berjalan 1× per cycle
3. **AUTHORITY**: Read-only aggregator; tidak boleh memodifikasi data sumber
4. **DATA**: Membaca trade_statistics, market_statistics; menulis bag_artifacts
5. **OUTPUT**: bag_artifacts (grouped insights), bag_patterns (detected patterns), bag_compression (metrics)
6. **CONSUMER**: KNOWLEDGE layer (via bag_id FK), BENCHMARK (optional), DASHBOARD (optional)
7. **CONSTRAINT**: Tidak boleh entry/exit/trading/prediction/governance decisions
8. **LIFECYCLE**: EMPTY → COLLECTING → ACTIVE → FROZEN/STALE
9. **VALIDATION**: Sample-gated (≥30), confidence range (0-10000), unique key per session
10. **EXTENSION**: Cross-session analysis, trend detection, anomaly detection diizinkan; ML/auto-trading/signal dilarang

**BAG adalah komponen tambahan yang menyesuaikan diri dengan ST-LMS. ST-LMS tidak berubah karena BAG.**
