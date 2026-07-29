# ST-LMS v3 — Fitur Lengkap

**Date:** 2026-07-29
**Version:** v3 FULL REBUILD
**Status:** ALL 20 PHASES IMPLEMENTED — 102/102 tests PASS

---

## Cara Menjalankan

```bash
# Full pipeline (default: BTCUSDT, 200 candles, seed 42)
python run_stlms.py

# Custom
python run_stlms.py --symbol SOLUSDT --candles 500 --seed 123

# Semua unit tests
python -m unittest discover -s stlms/tests -p "test_*.py" -v

# Foundation CLI
python -m stlms.cli.foundation_cli status
python -m stlms.cli.foundation_cli mcp list
```

---

## 1. MARKET COLLECTION (Phase 01-02)

### Pengumpulan Data Market
- **Binance Futures REST API** — kline, open interest, funding rate, long/short ratio, taker buy/sell volume
- **Rate-limited** — 50ms delay antar request, max 1500 candles per batch
- **Multi-symbol** — BTCUSDT, SOLUSDT, AKEUSDT, TLMUSDT (dapat ditambah)
- **Multi-timeframe** — 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 1d

### Fixture Generator (Offline)
- **Deterministic** — seed-based, output identik setiap run
- **4 market phases** — SIDE (sideways), UP (uptrend), DOWN (downtrend), SIDE
- **Realistic** — wick, volume, taker buy ratio bervariasi
- **OI generation** — 1 OI slot = 5 candles (5 menit)

### Market Artifact
- **Immutable cards** — SHA-256 checksum, lineage tracking
- **OI inheritance** — OI disimpan per timeframe asli, tidak diinterpolasi
- **Gap detection** — timestamp sequence integrity

---

## 2. SUPERTREND POINT (Phase 03-04)

### Indikator (15 indikator per SP)
| Indikator | Formula | Period |
|-----------|---------|--------|
| **Supertrend** | hl2 +/- ATR*3, band continuation | — |
| **ATR** | True Range, smoothed | 10 |
| **EMA** | Exponential moving average | 14 |
| **EMA12/26** | Untuk MACD | 12, 26 |
| **MACD** | 12-26, signal 9 | 12/26/9 |
| **RSI** | Smoothed avg gain/loss | 10 |
| **W%R** | Williams %R | 14 |
| **W%R Velocity** | wpr - prev_wpr | — |
| **W%R Acceleration** | vel - prev_vel | — |
| **Volume Delta** | 2 * takerBuyRatio - 1 | — |
| **Distance-to-ST** | abs(close - st) | — |
| **Distance/ATR** | dist / atr | — |
| **Flip Detection** | TREND_FLIP_UP / TREND_FLIP_DOWN | — |

### Filosofi SP
- **Unit truth utama** — setelah Market Collection, sistem bekerja pada level SP, bukan candle
- **State kontigu** — sequential per simbol, tidak bisa diparalelkan per-candle
- **WARMUP handling** — NULL values selama warmup, bukan fake neutral
- **Determinisme** — 2 run seed sama = output identik

---

## 3. STRUCTURE (Phase 05-08)

### Supertrend Line
- **Line = kumpulan SP** dengan st_canon sama (>= 4 members)
- **Support/Resistance** — HIJAU-dominant = SUPPORT, MERAH-dominant = RESISTANCE
- **OI inheritance** — Line.oi_avg, oi_trend (ACCUMULATION/DISTRIBUTION/STABLE)

### Wave (13 struktur)
| Struktur | Kondisi |
|----------|---------|
| STRONG_ACCUMULATION | g >= 5 |
| STRONG_DISTRIBUTION | r >= 5 |
| CONTINUATION_UP | g >= 3, r = 0 |
| CONTINUATION_DOWN | r >= 3, g = 0 |
| CONFIRMED_RANGE | alt >= 4 |
| RANGE_EXPANDING | — |
| RANGE_COMPRESSING | — |
| REVERSAL_UP | 3 MERAH + HIJAU terakhir |
| REVERSAL_DOWN | 3 HIJAU + MERAH terakhir |
| EXHAUSTION_UP | g >= 4, last = MERAH |
| EXHAUSTION_DOWN | r >= 4, last = HIJAU |
| SIDEWAY | g >= 2, r >= 2 |
| CHAOS | default |

- **OI Wave Profile** — OI dari 6 lines, divergence detection (BULLISH/BEARISH)
- **OI Interpretation** — "Smart money accumulating before breakout"

### Cage Engine
- **HUKUM CAGE**: 2 dinding = kompresi, 1 dinding = trend
- **Status**: NONE / VALID_COMPRESSION / LOOSE_SIDEWAY
- **Breakout**: NONE / IMMINENT_UP / IMMINENT_DOWN / SQUEEZE
- **Price Position**: 0-1 dalam cage
- **Versioning**: v0, v1, v2 walls

---

## 4. EVIDENCE (Phase 08)

### 3 Evidence Buses
| Bus | Isi | Penggunaan |
|-----|-----|-----------|
| **Direction Bus** | EMA, OI, VolDelta, MTF | Entry-legal witnesses |
| **Exit Bus** | RSI, W%R, MACD, HOLD-veto, vel, acc | Close-only exit signals |
| **Correction Bus** | pp, phase, distances, wave, cage | Market context |

### Aturan Penting
- **W%R/MACD/RSI = EXIT ONLY** — forbidden untuk entry
- **OI inheritance** — freshness-weighted scoring
- **MTF Sector** — wave structure ke MTF classification

---

## 5. CLONE + TRADE + POSITION (Phase 09-11)

### 3 Clone Types
| Clone | Bias | Entry Conjunction | Exit Priority |
|-------|------|------------------|---------------|
| **LONG** | EXPANSION_UP | stDir=+1, ema>0, vd>0, corridor, fee_safe, no_position | WRONG_EARLY→WRONG_GEOM→HYPOTHESIS→SL→HOLD→TP→EXIT_BUS→TIME |
| **SHORT** | EXHAUSTION_DOWN | stDir=-1, ema<0, vd<0, corridor, fee_safe, no_position | Mirror LONG |
| **GRID** | COMPRESSION_RANGE | cage_valid, width>=3*req, breakout=NONE, pp in zone, fills<max | RANGE_BREAK→WRONG→GRID_TP→STOP_ALL |

### Fitur Trading
- **1 candle = 3 knowledge** — LONG + SHORT + GRID observasi mandatory
- **Card Sharing** — Truth/Structure/Evidence 1x, shared ke 3 clone
- **Sub-ledger terisolasi** — statistik tidak dicampur
- **Adverse-first** — SL beats TP pada candle yang sama
- **Fee berlapis** — net = gross - fee - slip, WIN hanya jika net > 0
- **HOLD-veto** — MACD expanding + velocity menunda TP
- **Wrong entry detection** — velocity + geometry, hold <= 2
- **MAE/MFE tracking** — per posisi, untuk kalibrasi SL/TP

---

## 6. STATISTICS + BAG (Phase 10-11)

### Statistics
- **Per-clone metrics**: sample, win_rate, expectancy, PF, MAE, MFE, fee_drag, wrong_rate
- **Sample-gated**: CUKUP iff sample >= 30, BELUM_CUKUP jika kurang

### BAG (Behavioral Artifact Grouping)
- **Group by**: (clone, structure, distance_bucket, reason) — 4 dimensi
- **Consensus**: HIGH/MEDIUM/LOW/NONE
- **Conflict**: HIGH/MEDIUM/LOW/NONE
- **Maturity**: 0-10000 berdasarkan sample + consensus + conflict

---

## 7. KNOWLEDGE (Phase 11)

### 7 Knowledge Entities
| Entity | Fungsi |
|--------|--------|
| **Academy** | Win rate empiris per 4-dim bucket |
| **Oracle** | Euclidean similarity matching (vector beku, match > 7500) |
| **HiveMind** | Market understanding (intelligence_score 0-10000, dominant_bias) |
| **CERMIN** | Calibration error (predicted vs actual) |
| **Librarian** | Lifecycle: NEW→OBS→TRUSTED→MATURE/DEAD/DEPRECATED |
| **Darwin** | Parameter proposals (TIGHTEN_ENTRY, TIGHTEN_WRONG) |
| **River** | Chronicle — append-only event log |

### Aturan
- **Unidirectional** — tidak menulis balik ke Core/Clone
- **No-ML** — purely statistical/empirical
- **W%R/MACD NOT in Oracle vector** — sesuai authority matrix
- **Darwin NO auto-execute** — harus melalui WASIT → Human

---

## 8. PREDICTION (Phase 12)

### Market Possibility — BUKAN Trading Signal
- **Output**: "82% Breakout", "67% Continuation", "12% Fake Breakout"
- **BUKAN**: "BUY BTC", "SELL ETH"
- **Empirical only** — no_model = true
- **Supporting factors** — price, structure, volume, OI, knowledge
- **OI context** — accumulation/distribution interpretation

---

## 9. TRADING SCHEMA (Phase 13)

### 41 Trading Schemas (5 kategori)
| Kategori | Jumlah | Contoh |
|----------|--------|--------|
| Market Schema | 10 | TREND, SIDEWAY, COMPRESSION, BREAKOUT, REVERSAL, CHAOS... |
| Trading Schema | 7 | LONG, SHORT, GRID, NO TRADE, WAIT, HOLD, SKIP |
| Entry Schema | 11 | LONG_CONTINUATION, LONG_PULLBACK, GRID_COMPRESSION... |
| Position Schema | 7 | PARTIAL TP, TRAILING TP, BREAKEVEN, TIME EXIT... |
| Exit Schema | 6 | SL, TP, EXIT BUS, MANUAL EXIT, TIME EXIT, EARLY EXIT |

---

## 10. RECOMMENDATION (Phase 15)

### Market Intelligence Report — 20 Sections
- Header, Market Identity, Current State, Market Character
- Truth Summary, Structure Summary, Distance Summary
- Snapshot Summary, Statistics Summary, Knowledge Summary
- Prediction Summary, Trading Schema Summary
- Entry/Position/Exit Truth, Risk Summary, Confidence Summary
- Action Plan, Invalidation Condition, Recommendation Verdict

### BUKAN Sinyal Trading
- Report berisi pemahaman market, kemungkinan, dan rekomendasi
- Disclaimer: "NOT a trading signal. NOT financial advice."

---

## 11. SIMULATION (Phase 16)

### 5 Simulators
| Simulator | Fungsi |
|-----------|--------|
| **Architecture** | Validasi 23 pipeline stages, card sharing, determinisme |
| **Market Possibility** | Validasi prediksi vs aktual |
| **Market Push** | Simulasi phase transition |
| **Knowledge** | Pattern match + biography consistency |
| **Balance** | Simulasi P&L dari initial balance |

---

## 12. CONSUMER (Phase 17)

- **Fund Evaluation** — position sizing berdasarkan confidence
- **Veto Gate** — risk checks sebelum trade intent
- **Intent Builder** — SIDEWAY → GRID_INTENT, TREND → LONG/SHORT
- **CSV Export** — trade markers ke CSV
- **Live Adapter** — DISABLED default (memerlukan governance approval)

---

## 13. BENCHMARK (Phase 18)

### WASIT 5-Gate
| Gate | Kondisi |
|------|---------|
| G1 | candidate exits >= 30 |
| G2 | candidate expectancy > base expectancy |
| G3 | candidate worst-loss not worse > 10% |
| G4 | candidate win_rate not dropped > 2% |
| G5 | candidate fee_drag not increased |

- **Identical config → G2 FAIL** (rubber-stamp detection)
- **Walk-forward** — majority voting per fold

---

## 14. GOVERNANCE (Phase 19)

### 6 Validations
- Constitution, Proposal, Authority Matrix, Build, Runtime, Governance Audit

### Proposal Lifecycle
- **Darwin** → proposal (NO auto-execute)
- **Bounded auto-reject** — nilai di luar [min,max] ditolak otomatis
- **WASIT** → filter (5-gate walk-forward)
- **Human** → approve/reject
- **Rollback** — kembali ke default

---

## 15. INTEGRATION (Phase 20)

- **Pipeline orchestration** — 23 stages sequential
- **Worker bridges** — postMessage protocol
- **Architecture validation** — card sharing, determinism, unidirectional
- **Serial writer** — single writer, zero race

---

## 16. FOUNDATION CORE

### Shared Components
| Komponen | Jumlah | Fungsi |
|----------|--------|--------|
| Types (Enum) | 36 | DataStatus, TradeKind, CloneKind, WaveStructure, dll |
| Constants | 50+ | BOUNDED params, indicator periods, fee, assets |
| Utils | 15+ | Math, hash, PRNG, WIB, Card, ID Generator |
| Validators | 10+ | Bounded, symbol, candle hygiene, sample gate |
| Exceptions | 11 | STLMSError, ValidationError, BoundedRangeError, dll |

### Base Classes
- **BaseArtifact** — semua layer artifact producer
- **BasePackage** — semua layer report package
- **BaseConsumer** — semua layer downstream API
- **BaseValidator** — semua layer quality assurance

### Foundation Managers
- **ConfigurationManager** — 24 BOUNDED parameters
- **TimeManager** — WIB timezone, timestamp utilities
- **SymbolManager** — asset registry (tick, precision)
- **ResourceManager** — VPS 1.5 GB monitoring
- **FoundationRegistry** — central component registry

### CLI
- `status` — Foundation status
- `sqlite` — SQLite status
- `validate` — Foundation validation
- `resource` — Resource status
- `benchmark` — Benchmark results
- `config` — Configuration status
- `mcp` — MCP server management (list/on/off/toggle)

---

## 17. SQLITE FOUNDATION

- **40 tables** — schema dari STLMS_SQLITE_SCHEMA_V1.sql
- **Connection manager** — WAL mode, foreign keys ON, busy timeout
- **Manager** — init, backup, restore, vacuum, analyze, integrity
- **Viewer** — query, select, search, export JSON/CSV, pagination
- **Validator** — schema, integrity, foreign key, seed data checks
- **Query helper** — parameterized CRUD, no string concatenation
- **Benchmark** — insert, select, integrity, vacuum, analyze speed

---

## 18. GITHUB MCP

- **8 MCP tools** — status, test, on, off, setup, pr, token_status, reset
- **Default OFF** — aman dari awal
- **Token masked** — tidak pernah ditampilkan penuh
- **Stop after PR** — merge manual oleh operator
- **Zero dependencies** — bash + curl + git + jq

---

## Ringkasan

| Metrik | Nilai |
|--------|-------|
| Python modules | 52 |
| Total Python lines | ~7,000 |
| Unit tests | 102 (all PASS) |
| Benchmarks | 15 (all PASS) |
| Phases implemented | 20/20 |
| Pipeline stages | 23/23 |
| SQLite tables | 40 |
| Bounded params | 24 |
| Trading schemas | 41 |
| Indicators per SP | 15 |
| Wave structures | 13 |
| Clone types | 3 |
| Knowledge entities | 7 |
| Simulators | 5 |
| Governance validations | 6 |
| WASIT gates | 5 |
| External dependencies | 0 (stdlib only) |
