# SQLite Data Storage Report — ST-LMS v3

**Date:** 2026-07-29
**Status:** AUDIT — Data NOT persisted to SQLite

---

## Current State

Hanya **3 tabel** yang memiliki data (seed data dari schema):

| Table | Rows | Source |
|-------|------|--------|
| `app_settings` | 2 | Schema seed |
| `domain_dictionary` | 15 | Schema seed |
| `timeframes` | 9 | Schema seed |

**37 tabel lainnya KOSONG (0 rows).**

---

## Why Data Is Not Saved

1. **`run_stlms.py`** — menggunakan `MarketFixture.generate()` in-memory, tidak ada SQLite write
2. **`STLMSShell`** — menggunakan fixture in-memory, tidak ada SQLite write
3. **`PointBuilder`** — state in-memory, tidak persist ke `truth_snapshots`
4. **Semua layer** — data diproses di memori, tidak ada yang menulis ke SQLite

## What Should Be Saved

| Table | Data | Producer | Priority |
|-------|------|----------|----------|
| `app_sessions` | Session info | BOOT | HIGH |
| `pipeline_runs` | Run tracking | INTEGRATION | HIGH |
| `market_candles` | OHLCV per candle | MARKET | HIGH |
| `open_interest_series` | OI time series | MARKET | HIGH |
| `market_gaps` | Detected gaps | MARKET | MEDIUM |
| `truth_snapshots` | SP per candle | TRUTH | HIGH |
| `structure_snapshots` | Cage, wave, phase | STRUCTURE | HIGH |
| `wave_history` | Wave line details | STRUCTURE | MEDIUM |
| `cage_history` | Cage versions | STRUCTURE | MEDIUM |
| `evidence_snapshots` | 3 buses | EVIDENCE | HIGH |
| `clones` | Clone entities | CLONE | HIGH |
| `clone_observations` | Per-candle observations | CLONE | HIGH |
| `trade_markers` | Entry/exit markers | TRADE | HIGH |
| `positions` | Position lifecycle | POSITION | HIGH |
| `position_timeline` | Event timeline | POSITION | MEDIUM |
| `trade_statistics` | Aggregated stats | STATISTICS | HIGH |
| `market_statistics` | Market-level stats | STATISTICS | MEDIUM |
| `bag_artifacts` | Grouped data | BAG | MEDIUM |
| `knowledge_artifacts` | Knowledge entities | KNOWLEDGE | HIGH |
| `predictions` | Market possibilities | PREDICTION | HIGH |
| `governance_proposals` | Darwin proposals | GOVERNANCE | MEDIUM |
| `audit_logs` | Audit events | AUDIT | MEDIUM |

---

## Solution

Data harus dipersist ke SQLite melalui `SQLiteConnection` + `QueryHelper` yang sudah ada di `stlms/sqlite/`. Setiap layer yang produce artifact harus menyimpan Card ke SQLite.

**Contoh untuk TRUTH layer:**

```python
from stlms.sqlite.connection import SQLiteConnection
from stlms.sqlite.query import QueryHelper

conn = SQLiteConnection('stlms.db')
qh = QueryHelper(conn)

# Simpan truth_snapshot
qh.insert('truth_snapshots', {
    'truth_id': card.entity_id,
    'session_id': session_id,
    'candle_id': candle_id,
    'symbol': 'BTCUSDT',
    'timeframe': '1m',
    'ts': sp.ts,
    'close': sp.close,
    'st': sp.st,
    'st_dir': sp.st_dir,
    'st_color': sp.st_color,
    'atr': sp.atr,
    'ema': sp.ema,
    'rsi': sp.rsi,
    'wpr': sp.wpr,
    'dist_atr': sp.dist_atr,
    'truth_status': sp.point_status.value,
    'created_at': int(time.time())
})
```

**Atau via SnapshotManager:**

```python
from stlms.snapshot.manager import SnapshotManager
sm = SnapshotManager()
sm.store(card)  # Auto-persist ke SQLite
```
