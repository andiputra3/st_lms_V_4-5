# ST-LMS v3 — MASTER SPECIFICATION PATCH

**Date:** 2026-07-29
**Status:** PATCH — Koreksi MARKET_EVOLUTION_ARCHITECTURAL_REBUILD.md
**Reference:** MASTER_SPECIFICATION.html (APEX)

---

## PATCH SUMMARY

| Sebelum (SALAH) | Sesudah (BENAR) | Alasan |
|-----------------|-----------------|--------|
| 48000 MARKET OBSERVATION MEMORY | **48000 TRUTH OBSERVATION MEMORY** | Truth Layer = Single Source of Truth. Hanya Truth yang punya 48000 fixed buffer. |
| Seluruh layer memiliki 48000 object | **Hanya Truth Layer yang 48000**. Layer lain mengikuti kondisi market. | MASTER_SPECIFICATION: Truth adalah fondasi. |
| Snapshot = 48000 × seluruh layer | Snapshot = 48000 Truth + seluruh artifact turunan (jumlah bervariasi) | Snapshot adalah historical artifact, bukan fixed-size per layer. |
| MTF inheritance = seluruh data | MTF inheritance = **Truth Observation** | Truth adalah unit warisan. |

---

## 1. KOREKSI: 48000 TRUTH OBSERVATION MEMORY

```
┌──────────────────────────────────────────────────────────────────┐
│             48000 TRUTH OBSERVATION MEMORY                         │
│                                                                    │
│  HANYA Truth Layer yang memiliki fixed 48000 buffer.               │
│                                                                    │
│  [SP-1] [SP-2] ... [SP-47999] [SP-48000=LIVE]                    │
│                                                                    │
│  Setiap SP adalah TRUTH OBSERVATION:                               │
│    - 15 indikator (ST, ATR, EMA, RSI, W%R, MACD, dll)            │
│    - Lifecycle state                                               │
│    - Version number                                                │
│    - Mutation delta                                                │
│    - Reliability score                                             │
│    - MTF inheritance context                                       │
│                                                                    │
│  TRUTH ADALAH SINGLE SOURCE OF TRUTH.                              │
│  Semua layer lain MEMBACA dari Truth.                              │
└──────────────────────────────────────────────────────────────────┘
```

---

## 2. KOREKSI: MARKET OBSERVATION OBJECTS (JUMLAH BERVARIASI)

```
┌──────────────────────────────────────────────────────────────────┐
│  48000 TRUTH OBSERVATION ──► MENGHASILKAN (jumlah bervariasi)     │
│                                                                    │
│  Truth Layer:        48000 SP (fixed)                             │
│      │                                                            │
│      ├──► Structure:  ~531 Supertrend Line (tergantung market)    │
│      │    └──► Wave:  ~128 Wave (tergantung market)               │
│      │         └──► Cage: ~37 Cage (tergantung market)            │
│      │                                                            │
│      ├──► Evidence:   48000 × 3 buses (1 per SP)                  │
│      │                                                            │
│      ├──► Clone:      48000 × 3 observations (1 per SP per clone) │
│      │                                                            │
│      ├──► Statistics: bervariasi (agregasi)                       │
│      │                                                            │
│      ├──► Knowledge:  bervariasi (tergantung learning)            │
│      │                                                            │
│      ├──► Prediction: bervariasi (tergantung market condition)    │
│      │                                                            │
│      ├──► Events:     bervariasi (tergantung kejadian market)     │
│      │                                                            │
│      └──► Mutations:  47999 (1 per transisi SP)                   │
│                                                                    │
│  JUMLAH OBJECT TIDAK PERLU 48000.                                  │
│  HANYA TRUTH LAYER YANG FIXED 48000.                               │
└──────────────────────────────────────────────────────────────────┘
```

---

## 3. KOREKSI: SNAPSHOT CONTRACT

```
Snapshot-001 (SP 1 - 48000):
  ├── 48000 × truth_snapshot           (FIXED — Truth Layer)
  ├── 48000 × evidence_snapshot        (FIXED — 1 per SP)
  ├── 48000 × 3 clone_observation      (FIXED — 1 per SP per clone)
  ├── 47999 × mutation_record          (FIXED — 1 per transisi)
  ├── ~531 × structure_snapshot        (VARIABLE — tergantung market)
  ├── ~128 × wave_snapshot             (VARIABLE)
  ├── ~37 × cage_snapshot              (VARIABLE)
  ├── bervariasi × statistics_snapshot (VARIABLE — agregasi)
  ├── bervariasi × knowledge_snapshot  (VARIABLE)
  ├── bervariasi × prediction_snapshot (VARIABLE)
  ├── bervariasi × event_record        (VARIABLE)
  ├── bervariasi × lifecycle_event     (VARIABLE)
  ├── bervariasi × version_record      (VARIABLE)
  └── bervariasi × market_dna          (VARIABLE)

Snapshot ADALAH HISTORICAL MARKET OBSERVATION ARTIFACT.
BUKAN fixed-size container untuk seluruh layer.
```

---

## 4. KOREKSI: MARKET EVOLUTION STATISTICS

Statistics harus menjawab pertanyaan spesifik tentang **apa yang terjadi** di market:

### Truth Statistics

| Pertanyaan | Metrik | Consumer |
|-----------|--------|----------|
| Berapa SP yang berhasil dibuat? | `total_sp` | Dashboard |
| Berapa SP yang masih LIVE? | `live_count` (selalu 1) | Dashboard |
| Berapa SP yang sudah MATURE? | `mature_count` | Evolution |
| Berapa SP yang sudah ARCHIVE? | `archive_count` | Evolution |
| Berapa mutation yang terjadi? | `mutation_count` | Evolution |
| Berapa rata-rata mutation rate? | `mutation_rate = mutations / total_sp` | Knowledge |

### Structure Statistics

| Pertanyaan | Metrik | Consumer |
|-----------|--------|----------|
| Berapa Line yang terbentuk? | `total_lines` | Dashboard |
| Berapa rata-rata member per Line? | `avg_members` | Evolution |
| Berapa rata-rata life Line (candle)? | `avg_life` | Evolution |
| Berapa Flip Rate? | `flip_rate = flips / total_lines` | Knowledge |
| Berapa Mutation Rate? | `mutation_rate` | Knowledge |
| Berapa Survival Rate? | `survival_rate = lines_survived_10 / total_lines` | Evolution |

### Wave Statistics

| Pertanyaan | Metrik | Consumer |
|-----------|--------|----------|
| Berapa Wave yang terbentuk? | `total_waves` | Dashboard |
| Berapa Continuation Rate? | `continuation_rate = continuation_waves / total_waves` | Evolution |
| Berapa Breakout Rate? | `breakout_rate = breakout_waves / total_waves` | Knowledge |
| Berapa Reversal Rate? | `reversal_rate = reversal_waves / total_waves` | Knowledge |

### Prediction Statistics

| Pertanyaan | Metrik | Consumer |
|-----------|--------|----------|
| Berapa prediction yang BENAR? | `correct_predictions` | CERMIN |
| Berapa prediction yang SALAH? | `incorrect_predictions` | CERMIN |
| Berapa prediction accuracy? | `accuracy = correct / total` | Dashboard |

### Clone Statistics

| Pertanyaan | Metrik | Consumer |
|-----------|--------|----------|
| Berapa keputusan LONG? | `long_decisions` | Statistics |
| Berapa keputusan SHORT? | `short_decisions` | Statistics |
| Berapa keputusan NO TRADE? | `no_trade_decisions` | Statistics |
| Berapa observation-to-entry ratio? | `obs_to_entry = entries / observations` | Knowledge |

---

## 5. KOREKSI: MULTI TIMEFRAME INHERITANCE

```
┌──────────────────────────────────────────────────────────────────┐
│              MTF TRUTH OBSERVATION INHERITANCE                      │
│                                                                    │
│  1 Candle 5m (1 Truth Observation 5m)                              │
│      │                                                            │
│      └──► mewarisi ke 5 Truth Observation 1m                       │
│           SP-1, SP-2, SP-3, SP-4, SP-5                            │
│           Setiap SP 1m mendapat KONTEKS 5m:                        │
│             - ST 5m                                                 │
│             - ATR 5m                                                │
│             - Wave structure 5m                                     │
│             - MTF score 5m                                          │
│                                                                    │
│  1 Candle 15m (1 Truth Observation 15m)                            │
│      │                                                            │
│      └──► mewarisi ke 15 Truth Observation 1m                      │
│                                                                    │
│  1 Candle 1H (1 Truth Observation 1h)                              │
│      │                                                            │
│      └──► mewarisi ke 60 Truth Observation 1m                      │
│                                                                    │
│  1 Candle 4H (1 Truth Observation 4h)                              │
│      │                                                            │
│      └──► mewarisi ke 240 Truth Observation 1m                     │
│                                                                    │
│  INHERITANCE = TRUTH OBSERVATION.                                  │
│  BUKAN inheritance seluruh layer.                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 6. KOREKSI: DEPENDENCY GRAPH

```
┌──────────────────────────────────────────────────────────────────┐
│              TRUTH OBSERVATION PIPELINE                             │
│                                                                    │
│  48000 TRUTH OBSERVATION MEMORY                                    │
│      │                                                            │
│      ▼                                                            │
│  TRUTH LAYER (Single Source of Truth)                              │
│      │                                                            │
│      ├──► STRUCTURE LAYER (Line, Wave, Cage — jumlah bervariasi)  │
│      ├──► EVIDENCE LAYER (3 buses per SP)                         │
│      ├──► CLONE LAYER (3 observations per SP)                     │
│      │                                                            │
│      ▼                                                            │
│  STATISTICS LAYER (agregasi dari seluruh data)                     │
│      │                                                            │
│      ▼                                                            │
│  KNOWLEDGE LAYER (belajar dari Statistics + History)               │
│      │                                                            │
│      ▼                                                            │
│  PREDICTION LAYER (Market Possibility)                             │
│      │                                                            │
│      ▼                                                            │
│  SIMULATION LAYER (Professional Futures Trader)                    │
│      │                                                            │
│      ▼                                                            │
│  RECOMMENDATION LAYER (Market Intelligence Report)                 │
│      │                                                            │
│      ▼                                                            │
│  SNAPSHOT LAYER (Historical Market Observation Artifact)           │
│      │                                                            │
│      ▼                                                            │
│  SQLite LAYER (Market Evolution Database)                          │
│      │                                                            │
│      ▼                                                            │
│  HISTORICAL OBSERVATION LAYER                                      │
│                                                                    │
│  ═══════════════════════════════════════════════════════════════  │
│  TRUTH ADALAH FONDASI. SEMUA LAYER MEMBACA DARI TRUTH.            │
└──────────────────────────────────────────────────────────────────┘
```

---

## 7. KOREKSI: FILE INVENTORY

### Yang TETAP (tidak berubah dari Architectural Rebuild):

| File | Status |
|------|--------|
| `stlms/evolution/memory.py` | ✅ MarketObservationMemory → rename ke **TruthObservationMemory** |
| `stlms/evolution/sync.py` | ✅ Tetap — sinkronisasi dari Truth |
| `stlms/evolution/dna.py` | ✅ Tetap — Market DNA dari Truth |
| `stlms/evolution/mtf_inheritance.py` | ✅ Tetap — inheritance Truth Observation |
| `stlms/evolution/statistics.py` | ✅ Tetap — Evolution Statistics |
| `stlms/truth/lifecycle.py` | ✅ Tetap |
| `stlms/structure/lifecycle.py` | ✅ Tetap |
| `stlms/structure/versioning.py` | ✅ Tetap |
| `stlms/statistics/domains/evolution_stats.py` | ✅ Diperbarui — metric names |
| `stlms/simulation/professional.py` | ✅ Tetap |
| `stlms/knowledge/evolution_learner.py` | ✅ Tetap |

### Yang DIUBAH:

| File | Perubahan |
|------|-----------|
| `stlms/evolution/memory.py` | `MarketObservationMemory` → `TruthObservationMemory`. Hanya buffer Truth, bukan seluruh layer. |
| `stlms/evolution/snapshot_batch.py` | SnapshotBatch TIDAK memaksa 48000 per layer. Hanya Truth yang 48000. Layer lain bervariasi. |
| `stlms/statistics/domains/evolution_stats.py` | Metric names: `total_sp`, `live_count`, `mature_count`, `total_lines`, `avg_life`, `flip_rate`, `continuation_rate`, dll. |

### Yang TIDAK JADI dibuat:

| File | Alasan |
|------|--------|
| (tidak ada) | Semua tetap dibuat, hanya koreksi naming dan asumsi jumlah. |

---

## 8. FINAL VERDICT

**Patch ini TIDAK menghapus hasil Architectural Rebuild sebelumnya.** Patch ini HANYA mengoreksi:

1. **48000 MARKET → 48000 TRUTH** — hanya Truth yang fixed 48000
2. **Jumlah object bervariasi** — layer selain Truth mengikuti kondisi market
3. **Snapshot = 48000 Truth + artifact turunan** — bukan fixed-size per layer
4. **MTF inheritance = Truth Observation** — bukan seluruh layer
5. **Statistics metric names** — disesuaikan dengan pertanyaan spesifik

**0 file dihapus. 0 arsitektur berubah. Hanya koreksi asumsi.**
