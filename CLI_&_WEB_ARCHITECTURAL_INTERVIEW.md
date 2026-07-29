# ST-LMS v3 — CLI & WEB ARCHITECTURAL INTERVIEW

**Date:** 2026-07-29
**Role:** Enterprise Architect + CLI Architect + Web Architect
**Status:** AUDIT COMPLETE

---

## 1. CLI ARCHITECTURAL AUDIT

### Current State

| File | Lines | Commands | Interactive | Shared with Web? |
|------|-------|----------|-------------|------------------|
| `foundation_cli.py` | 136 | 7 | ❌ No | ❌ No |
| `mcp_cli.py` | 120 | 5 | ❌ No | ❌ No |
| `mcp_tui.py` | 106 | 1 (TUI) | ✅ Arrow keys | ❌ No |
| `run_stlms.py` | 330 | 1 (pipeline) | ❌ No | ❌ No |

**Verdict: CLI terlalu sederhana.** 4 file terpisah, 14 command total, tidak ada interactive REPL, tidak ada shared core dengan Web, tidak ada akses ke trading data/statistics/prediction/recommendation.

### Masalah Kritis:

1. **CLI dan WEB completely independent** — zero shared code, zero shared imports, zero shared data models
2. **Tidak ada interactive REPL** — semua command fire-and-forget
3. **Tidak ada akses ke pipeline** — tidak bisa lihat trade markers, statistics, prediction dari CLI
4. **FoundationCLI standalone entry point broken** — semua dependencies `None`
5. **mcp_tui unreachable** — `mcp_cli.py` tidak punya handler `tui`
6. **Tidak ada mode interaksi selain positional args** — tidak ada number mode, wizard mode, natural command

---

## 2. CLI IMPROVEMENT PROPOSAL

### Filosofi: CLI = ST-LMS OPERATING CENTER

CLI bukan sekadar command-line tool. CLI adalah pusat kendali ST-LMS.

### 7 Mode Interaksi

| Mode | Cara | Contoh |
|------|------|--------|
| **NUMBER** | Ketik angka | `1` = status, `2` = truth, `3` = statistics |
| **TEXT** | Ketik nama | `truth`, `statistics`, `recommendation` |
| **NATURAL** | Kalimat alami | `show btc statistics`, `replay supertrend point 42` |
| **WIZARD** | Step-by-step | `help` → CLI membimbing |
| **QUICK** | Singkat | `run`, `audit`, `export`, `benchmark` |
| **ADVANCED** | Teknis | `sqlite query "SELECT..."`, `pipeline stage 5` |
| **INTERACTIVE** | Menu dalam menu | Pindah antar menu tanpa keluar |

### 8 Explorer Systems

| Explorer | Akses |
|----------|-------|
| **Statistics Explorer** | Semua 10 domain statistics |
| **Snapshot Explorer** | 10 snapshot types, W/OD fields |
| **SQLite Explorer** | 40 tables, query, export |
| **Truth Explorer** | SP lifecycle, timeline, events |
| **Clone Explorer** | LONG/SHORT/GRID observations |
| **Recommendation Explorer** | Market Intelligence Report 20 sections |
| **Simulation Explorer** | 5 simulator results |
| **Pipeline Explorer** | 23 stage status, progress |

### 15 Report Types dari CLI

| Report | Command |
|--------|---------|
| Market Intelligence Report | `report market` |
| Truth Report | `report truth` |
| Statistics Report | `report statistics` |
| Prediction Report | `report prediction` |
| Recommendation Report | `report recommendation` |
| Simulation Report | `report simulation` |
| Clone Report | `report clone` |
| Governance Report | `report governance` |
| Benchmark Report | `report benchmark` |
| Audit Report | `report audit` |
| Pipeline Report | `report pipeline` |
| Snapshot Report | `report snapshot` |
| SQLite Report | `report sqlite` |
| Runtime Report | `report runtime` |
| Export Report | `export csv/json` |

---

## 3. WEB ARCHITECTURAL AUDIT

### Current State

`data_viewer/server.py` (829 lines) — pure `http.server`, zero external deps, 18+ routes.

**Kelebihan:**
- Zero dependencies
- Read-only documentation portal
- Markdown viewer, SQLite browser, file browser
- API endpoints (JSON)

**Kekurangan:**
- **Tidak terhubung ke pipeline engine** — hanya baca file statis
- **Tidak ada trading data** — tidak bisa lihat markers, statistics, prediction
- **Tidak ada live data** — semua statis
- **Tidak shared core dengan CLI** — logic terpisah total

---

## 4. SHARED CORE PROPOSAL

### Masalah: CLI dan WEB zero shared logic

```
SAAT INI:
  CLI (foundation_cli.py) ── imports stlms.* ──► Foundation objects
  WEB (server.py) ── raw sqlite3, raw filesystem ──► Static data
  
  GAP: Tidak ada jembatan antara CLI dan WEB
```

### Solusi: SHARED CORE ARCHITECTURE

```
TARGET:
  ┌─────────────────────────────────────────────┐
  │              SHARED CORE                     │
  │  stlms/core/shell.py                         │
  │                                              │
  │  Class: STLMSShell                           │
  │  - status() → dict                           │
  │  - truth_summary() → dict                    │
  │  - statistics_summary() → dict               │
  │  - prediction_summary() → dict               │
  │  - recommendation_report() → dict            │
  │  - simulation_results() → dict               │
  │  - sqlite_query(sql) → list[dict]            │
  │  - pipeline_status() → dict                  │
  │  - export(format) → str                      │
  │  - ... semua query methods                   │
  └──────┬──────────────────┬───────────────────┘
         │                  │
         ▼                  ▼
  ┌─────────────┐    ┌─────────────┐
  │  CLI Layer  │    │  WEB Layer  │
  │  (terminal) │    │  (HTTP)     │
  │             │    │             │
  │  Membaca    │    │  Membaca    │
  │  STLMSShell │    │  STLMSShell │
  │  → print    │    │  → JSON/HTML│
  └─────────────┘    └─────────────┘
  
  CLI dan WEB TIDAK saling bergantung.
  Keduanya bergantung pada SHARED CORE.
```

### Shared Core API:

```python
class STLMSShell:
    """Shared core untuk CLI dan WEB. Zero presentation logic."""
    
    # Foundation
    def status(self) -> dict
    def health(self) -> dict
    
    # Truth
    def truth_current(self) -> dict
    def truth_timeline(self, start, end) -> list[dict]
    def truth_events(self) -> list[dict]
    
    # Structure
    def structure_summary(self) -> dict
    def wave_current(self) -> dict
    def cage_current(self) -> dict
    
    # Statistics (10 domains)
    def statistics_market(self) -> dict
    def statistics_clone(self, clone_id) -> dict
    def statistics_indicator(self, name) -> dict
    
    # Knowledge
    def knowledge_academy(self) -> list[dict]
    def knowledge_oracle(self) -> dict
    def knowledge_hivemind(self) -> dict
    
    # Prediction
    def prediction_current(self) -> dict
    
    # Recommendation
    def recommendation_report(self) -> dict
    
    # Simulation
    def simulation_results(self) -> dict
    
    # SQLite
    def sqlite_tables(self) -> list[dict]
    def sqlite_query(self, sql) -> list[dict]
    
    # Pipeline
    def pipeline_status(self) -> dict
    
    # Export
    def export(self, format="json") -> str
```

---

## 5. WEB IMPROVEMENT PROPOSAL

### Target: WEB = Full Dashboard (bukan hanya doc viewer)

Saat ini WEB hanya documentation portal. Harusnya full dashboard yang menampilkan:

| Halaman | Konten |
|---------|--------|
| `/` | Dashboard — semua summary |
| `/truth` | Truth Layer — SP, indicators, timeline |
| `/structure` | Structure — wave, cage, lines |
| `/statistics` | Statistics — 10 domain |
| `/prediction` | Prediction — market possibilities |
| `/recommendation` | Recommendation — MIR 20 sections |
| `/simulation` | Simulation — 5 simulators |
| `/clone` | Clone — LONG/SHORT/GRID |
| `/sqlite` | SQLite Explorer — tables, query |
| `/pipeline` | Pipeline — 23 stage status |
| `/replay` | Replay — timeline playback |
| `/governance` | Governance — validations, proposals |
| `/audit` | Audit — test results, issues |
| `/api/*` | JSON API — semua data |

### Web Explorer Systems:

| Explorer | Fungsi |
|----------|--------|
| Statistics Explorer | Chart + tabel 10 domain |
| Truth Explorer | SP lifecycle viewer |
| Snapshot Explorer | 10 snapshot types browser |
| Clone Explorer | Observation log viewer |
| Recommendation Explorer | MIR report viewer |
| Simulation Explorer | Simulator results |
| SQLite Explorer | Table browser + query |
| Pipeline Explorer | Stage progress |
| Replay Explorer | Timeline scrubber |

---

## 6. DEPENDENCY GRAPH

### CLI Dependency:

```
CLI (terminal)
  │
  ├── stlms/core/shell.py (STLMSShell) ← SHARED CORE
  │     ├── stlms/truth/*
  │     ├── stlms/structure/*
  │     ├── stlms/statistics/*
  │     ├── stlms/knowledge/*
  │     ├── stlms/prediction/*
  │     ├── stlms/recommendation/*
  │     ├── stlms/simulation/*
  │     ├── stlms/sqlite/*
  │     └── stlms/foundation/*
  │
  └── Presentasi: print, table, color
```

### WEB Dependency:

```
WEB (HTTP server)
  │
  ├── stlms/core/shell.py (STLMSShell) ← SHARED CORE (SAMA)
  │     └── (same as CLI)
  │
  └── Presentasi: HTML, JSON, Chart
```

**CLI dan WEB menggunakan STLMSShell yang SAMA. Tidak saling bergantung.**

---

## 7. FEATURE DIFF REPORT

| Fitur | Current CLI | Current WEB | Target |
|-------|------------|-------------|--------|
| Foundation status | ✅ | ✅ | ✅ |
| Truth Layer | ❌ | ❌ | ✅ |
| Structure | ❌ | ❌ | ✅ |
| Statistics (10 domain) | ❌ | ❌ | ✅ |
| Knowledge (7 entity) | ❌ | ❌ | ✅ |
| Prediction | ❌ | ❌ | ✅ |
| Recommendation | ❌ | ❌ | ✅ |
| Simulation | ❌ | ❌ | ✅ |
| Clone observation | ❌ | ❌ | ✅ |
| SQLite Explorer | Partial | ✅ | ✅ |
| Pipeline status | ❌ | ❌ | ✅ |
| Replay | ❌ | ❌ | ✅ |
| Governance | ❌ | ❌ | ✅ |
| Audit | Partial | ❌ | ✅ |
| Export | ❌ | ❌ | ✅ |
| Interactive REPL | ❌ | N/A | ✅ |
| 7 interaction modes | 2/7 | N/A | ✅ |
| Shared Core | ❌ | ❌ | ✅ |

---

## 8. IMPLEMENTATION PRIORITY

| Priority | Task | Effort |
|----------|------|--------|
| **P0** | `stlms/core/shell.py` — STLMSShell shared core | 2 hari |
| **P1** | CLI interactive REPL + 7 modes | 2 hari |
| **P1** | WEB dashboard pages (truth, statistics, prediction, etc.) | 3 hari |
| **P2** | CLI explorers (8 systems) | 2 hari |
| **P2** | WEB explorers + visualization | 2 hari |
| **P3** | CLI reports (15 types) | 1 hari |
| **P3** | WEB API endpoints (JSON) | 1 hari |
| **P4** | WEB charts + timeline | 1 hari |

**Total: ~14 hari untuk full CLI + WEB rebuild dengan shared core.**

---

## 9. FINAL PROPOSAL

**CLI = ST-LMS Operating Center.** Bukan sekadar command-line tool.

**WEB = ST-LMS Dashboard.** Bukan sekadar documentation viewer.

**SHARED CORE = `stlms/core/shell.py`.** Satu sumber kebenaran untuk CLI dan WEB.

**Arsitektur:**
```
SHARED CORE (STLMSShell)
    ├── CLI (terminal, 7 modes, 8 explorers, 15 reports)
    └── WEB (HTTP, dashboard pages, JSON API, charts)
```

**CLI dan WEB independen — tidak saling bergantung. Keduanya bergantung pada Shared Core.**
