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
