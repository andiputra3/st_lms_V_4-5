# 01_SQLITE_FOUNDATION.md

## ST-LMS — SQLite Foundation Layer Architecture Mapping

**Date:** 2026-07-28
**Status:** ARCHITECTURE MAPPING — FROZEN
**Sources:** stlms_sqlite_schema_v1.sql, MASTER_SPECIFICATION.html, DOCUMENT_DEPENDENCY.html, QWEN_14_DOC.html

---

### 1. Responsibility

SQLite Foundation Layer menyediakan persistence dan data model untuk seluruh ST-LMS. Layer ini adalah fondasi data yang digunakan oleh semua layer di atasnya. Bertanggung jawab untuk menyimpan, mengindeks, dan menyediakan akses ke semua data pipeline, snapshot, trading, knowledge, governance, dan audit.

### 2. Purpose

- Menyediakan schema database yang lengkap untuk seluruh lifecycle ST-LMS
- Menjamin integritas referensial melalui foreign key constraints
- Menyediakan indexing untuk query performant
- Menjadi single source of truth untuk data model
- Mendukung semua operasi CRUD, export, import, backup, restore

### 3. Input

- Data dari seluruh pipeline stages (MARKET hingga GOVERNANCE)
- Config dan settings dari BOOT layer
- Seed data (timeframes, domain dictionary, app settings)

### 4. Output

- Persistent storage untuk 40 tables dalam 17 layer groups
- Data yang dapat di-query oleh SQLite Viewer
- Backup dan export files

### 5. Dependency Layer

- **Upstream**: BOOT (config, initialization)
- **Downstream**: Semua layer (MARKET, TRUTH, STRUCTURE, EVIDENCE, CLONE, TRADE, POSITION, STATISTICS, KNOWLEDGE, PREDICTION, GOVERNANCE, REPLAY, BENCHMARK, AUDIT, CONSUMER, VIEW)

### 6. Previous Pipeline

BOOT — Foundation layer diinisialisasi setelah BOOT.

### 7. Next Pipeline

MARKET — Data market mulai mengisi SQLite tables.

### 8. SQLite Tables yang Digunakan

Semua 40 tables (layer ini adalah pemilik schema):

**CORE METADATA (4):**
- `app_sessions` — session container
- `symbols` — registered trading symbols
- `timeframes` — canonical timeframe registry (9 seed rows)
- `pipeline_runs` — pipeline execution runs

**MARKET (4):**
- `market_candles` — OHLCV candle data
- `market_metadata` — key-value metadata
- `open_interest_series` — OI time series
- `market_gaps` — detected gaps

**TRUTH (2):**
- `truth_snapshots` — per-candle truth physics
- `truth_cache` — key-value cache

**STRUCTURE (3):**
- `structure_snapshots` — per-candle geometry
- `wave_history` — wave line details
- `cage_history` — cage version history

**EVIDENCE (1):**
- `evidence_snapshots` — per-candle evidence buses

**CLONE (2):**
- `clones` — clone runtime entities
- `clone_observations` — per-candle observations

**TRADE (1):**
- `trade_markers` — trade markers (ENTRY/EXIT/...)

**POSITION (2):**
- `positions` — position lifecycle
- `position_timeline` — event timeline

**STATISTICS (2):**
- `trade_statistics` — aggregated trade stats
- `market_statistics` — market-level stats

**BAG (3):**
- `bag_artifacts` — behavior acquisition group
- `bag_patterns` — ranked patterns
- `bag_compression` — compression metrics

**KNOWLEDGE (1):**
- `knowledge_artifacts` — knowledge engine artifacts

**PREDICTION (2):**
- `predictions` — empirical predictions
- `prediction_results` — actual outcomes

**GOVERNANCE (3):**
- `governance_proposals` — Darwin proposals
- `governance_logs` — event timeline
- `rollback_logs` — rollback events

**REPLAY (2):**
- `replay_sessions` — replay containers
- `replay_frames` — individual frames

**BENCHMARK (2):**
- `benchmark_runs` — benchmark containers
- `benchmark_cases` — test cases

**AUDIT (2):**
- `audit_logs` — audit events
- `audit_issues` — key-value issues

**SETTINGS (2):**
- `app_settings` — key-value settings
- `domain_dictionary` — domain registry (15 seed rows)

**UTILITY (2):**
- `purge_jobs` — deletion tracking
- `row_lifecycle` — generic lifecycle tracking

### 9. SQLite Tables yang Dihasilkan

Seluruh 40 tables di atas dihasilkan oleh layer ini (sebagai schema owner).

### 10. Artifact yang Dihasilkan

- `stlms.db` — SQLite database file
- Schema version: 1.0.0
- 49 foreign key relationships
- 31 CHECK constraints
- 19 UNIQUE constraints
- 9 explicit indexes
- 4 triggers (updated_at maintenance)
- Seed data: 9 timeframes, 2 app_settings, 15 domain_dictionary entries

### 11. Validator yang Dibutuhkan

- **PRAGMA integrity_check** — verifikasi integritas database
- **PRAGMA foreign_key_check** — verifikasi referensi
- **PRAGMA quick_check** — quick integrity scan
- **SQL Syntax Validator** — validasi query sebelum eksekusi
- **Constraint Validator** — CHECK, UNIQUE, NOT NULL enforcement
- **FK Cascade Validator** — memastikan CASCADE bekerja dengan benar

### 12. Knowledge Entity yang Digunakan

- River — mencatat chronicle events ke SQLite
- Academy — membaca/menulis bucket statistics
- Oracle — menyimpan/membaca vector history
- Semua knowledge entities menggunakan `knowledge_artifacts` table

### 13. Trading Entity yang Digunakan

- Trade Markers — disimpan di `trade_markers`
- Positions — disimpan di `positions`
- Clone Observations — disimpan di `clone_observations`

### 14. Snapshot yang Digunakan

- Semua 10 snapshots memiliki corresponding tables:
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

### 15. Benchmark yang Digunakan

- Benchmark runs disimpan di `benchmark_runs`
- Benchmark cases disimpan di `benchmark_cases`
- WASIT 5-gate results di `gates_json`

### 16. Dashboard Component yang Digunakan

- SQLite Viewer — browse tables, execute queries
- SQLite Manager — backup, restore, vacuum, integrity
- Query Console — SQL execution
- Statistics Viewer — database statistics
- Audit Log Viewer — audit events

### 17. Mandatory atau Optional

**MANDATORY** — Foundation layer diperlukan oleh seluruh sistem.

### 18. Specification Reference

- MASTER_SPECIFICATION.html §9 (Snapshot Master)
- DOCUMENT_DEPENDENCY.html §7 (Snapshot Dependency)
- QWEN_14_DOC.html D3 (Workspace Architecture)
- stlms_sqlite_schema_v1.sql (complete schema)

### 19. Build Order Recommendation

```
Build Order: 1 (pertama — foundation)
Dependencies: BOOT (config + initialization)
Build setelah: BOOT
Build sebelum: MARKET
```

### 20. Notes dan Constraint

- **PRAGMA foreign_keys = ON** — wajib di-enable
- **SQLite target: 3.38+**
- **Writer serial** — single writer pada main thread
- **Workers dilarang** — workers tidak boleh mengakses SQLite langsung
- **CASCADE delete** — 23 child tables cascade dari `app_sessions`
- **No views** — schema tidak memiliki views
- **No FTS** — tidak ada full-text search virtual tables
- **39 DEFAULT values** — untuk kolom status, counter, flag
- **BAG layer** — ada di schema tapi tidak di MASTER_SPECIFICATION domain list
- **Platform note** — runtime menggunakan IndexedDB; SQLite adalah reference/audit schema
