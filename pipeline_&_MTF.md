# ST-LMS v3 — FINAL PIPELINE & MTF SYSTEM

**Date:** 2026-07-29
**Status:** POST-REBUILD — 131 Python modules, 102 tests PASS

---

## 1. FINAL PIPELINE (23 STAGES)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                    ST-LMS v3 — 23 STAGE PIPELINE (POST-REBUILD)                │
│                 SHARED → PER-CLONE → SHARED-AGAIN → CROSS-CUTTING              │
└──────────────────────────────────────────────────────────────────────────────┘

STAGE  TYPE              NAME                    FILE                          CLASS/FUNCTION
─────  ────────────────  ──────────────────────  ────────────────────────────  ──────────────────
 0     ONCE              BOOT                    stlms/core/shell.py           STLMSShell (init)
                                                 stlms/foundation/             ConfigManager, TimeManager,
                                                                               SymbolManager, Registry
       ═══════════════════════════════════════════════════════════════════════════════════════════
 1     SHARED            MARKET OBSERVATION      stlms/market/collection.py    MarketDataCollector.collect()
                                                 stlms/market/fixture.py       MarketFixture.generate()
       ─────────────────────────────────────────────────────────────────────────────────────────
 2     SHARED            MARKET ARTIFACT         stlms/market/artifact.py      MarketArtifact.produce()
                                                                               → market_snapshot Card
       ─────────────────────────────────────────────────────────────────────────────────────────
 3     SHARED            SUPERTREND POINT        stlms/truth/point.py          PointBuilder.build()
                          (TRUTH LAYER)          stlms/truth/artifact.py       TruthArtifact.produce()
                                                                               → truth_snapshot Card
                          TRUTH ENRICHMENT        stlms/truth/lifecycle.py      SPLifecycleManager
                                                 stlms/truth/timeline.py       TruthTimeline (15 queries)
                                                 stlms/truth/event.py          MarketEventRecorder
                                                 stlms/truth/mutation.py       MutationTracker
                                                 stlms/truth/reliability.py    ReliabilityScorer
                                                 stlms/truth/replay.py         TruthReplay
                                                 stlms/truth/statistics.py     TruthStatistics
       ─────────────────────────────────────────────────────────────────────────────────────────
 4     SHARED            STRUCTURE LAYER         stlms/structure/line.py       LineBuilder.build()
                          (Line, Wave, Cage)     stlms/structure/wave.py       WaveBuilder.build()
                                                 stlms/structure/cage.py       CageEngine.build()
                                                 stlms/structure/artifact.py   StructureArtifact.produce()
                                                                               → structure_snapshot Card
       ─────────────────────────────────────────────────────────────────────────────────────────
 5     SHARED            DISTANCE LAYER          stlms/distance/engine.py      DistanceEngine.compute()
                                                 stlms/distance/artifact.py    DistanceArtifact.produce()
                                                                               → distance_snapshot Card
       ─────────────────────────────────────────────────────────────────────────────────────────
 6     SHARED            EVIDENCE LAYER          stlms/evidence/bus.py         EvidenceEngine (3 buses)
                                                 stlms/evidence/artifact.py    EvidenceArtifact.produce()
                                                                               → evidence_snapshot Card
       ═══════════════════════════════════════════════════════════════════════════════════════════
 7     PER-CLONE ×3      CLONE OBSERVATION       stlms/clone/engine.py         CloneEngine (LONG/SHORT/GRID)
                                                 stlms/clone/artifact.py       CloneArtifact.produce()
                                                                               → clone_observation Card
       ─────────────────────────────────────────────────────────────────────────────────────────
 8     PER-CLONE ×3      ENTRY VALIDATION        stlms/trade/engine.py         TradeEngine.make_entry()
       ─────────────────────────────────────────────────────────────────────────────────────────
 9     PER-CLONE ×3      POSITION MGMT           stlms/position/engine.py      PositionEngine.update_position()
       ─────────────────────────────────────────────────────────────────────────────────────────
10     PER-CLONE ×3      PROFIT MGMT             stlms/position/engine.py      PositionEngine.trailing_stop()
                                                                               PositionEngine.partial_tp()
                                                                               PositionEngine.breakeven()
       ─────────────────────────────────────────────────────────────────────────────────────────
11     PER-CLONE ×3      EXIT VALIDATION         stlms/trade/engine.py         TradeEngine.make_exit()
       ─────────────────────────────────────────────────────────────────────────────────────────
12     PER-CLONE ×3      CLOSE POSITION          stlms/trade/engine.py         TradeEngine.calc_pnl()
       ─────────────────────────────────────────────────────────────────────────────────────────
13     PER-CLONE ×3      TRADE MARKER            stlms/trade/artifact.py       TradeArtifact.produce()
                                                                               → trade_snapshot Card
       ═══════════════════════════════════════════════════════════════════════════════════════════
14     SHARED-AGAIN      STATISTICS              stlms/statistics/artifact.py  StatisticsArtifact.produce()
                          (10 DOMAINS)           stlms/statistics/domains/     6 domain files:
                                                 market_stats.py               phase distribution, wave frequency
                                                 indicator_stats.py            RSI/W%R/MACD distribution
                                                 distance_stats.py             bucket distribution
                                                 clone_stats.py                per-clone metrics
                                                 oi_stats.py                   OI trend, divergence
                                                 correlation_stats.py          indicator correlation matrix
       ─────────────────────────────────────────────────────────────────────────────────────────
15     SHARED-AGAIN      BAG                     stlms/bag/engine.py           BAGEngine.group_by_clone_structure()
                                                 stlms/bag/artifact.py         BAGArtifact.produce()
                                                                               → bag_artifact Card
       ─────────────────────────────────────────────────────────────────────────────────────────
16     SHARED-AGAIN      RIVER (KNOWLEDGE)       stlms/knowledge/river.py      RiverEngine (chronicle)
       ─────────────────────────────────────────────────────────────────────────────────────────
17     ON-DEMAND         BENCHMARK               stlms/bench/engine.py         wasit_5gate()
                                                 stlms/bench/artifact.py       BenchmarkArtifact.produce()
                                                                               → benchmark_snapshot Card
       ─────────────────────────────────────────────────────────────────────────────────────────
18     SHARED-AGAIN      ACADEMY (KNOWLEDGE)     stlms/knowledge/engine.py     AcademyEngine.learn()
       ─────────────────────────────────────────────────────────────────────────────────────────
19     SHARED-AGAIN      ORACLE (KNOWLEDGE)      stlms/knowledge/engine.py     OracleEngine.match()
       ─────────────────────────────────────────────────────────────────────────────────────────
20     SHARED-AGAIN      HIVEMIND (KNOWLEDGE)    stlms/knowledge/engine.py     HiveMindEngine.synthesize()
       ─────────────────────────────────────────────────────────────────────────────────────────
21     SHARED-AGAIN      CERMIN (KNOWLEDGE)      stlms/knowledge/cermin.py     CerminEngine.calibrate()
       ─────────────────────────────────────────────────────────────────────────────────────────
22     SHARED-AGAIN      DARWIN (KNOWLEDGE)      stlms/knowledge/engine.py     DarwinEngine.propose()
       ─────────────────────────────────────────────────────────────────────────────────────────
23     SHARED-AGAIN      LIBRARIAN (KNOWLEDGE)   stlms/knowledge/engine.py     LibrarianEngine.evaluate()
       ─────────────────────────────────────────────────────────────────────────────────────────
24     SHARED-AGAIN      PREDICTION              stlms/prediction/engine.py    PredictionEngine.predict()
                                                 stlms/prediction/artifact.py  PredictionArtifact.produce()
                                                                               → prediction_snapshot Card
       ─────────────────────────────────────────────────────────────────────────────────────────
25     SHARED-AGAIN      TRADING SCHEMA          stlms/schema/engine.py        SchemaEngine
       ─────────────────────────────────────────────────────────────────────────────────────────
26     SHARED-AGAIN      RECOMMENDATION          stlms/recommendation/engine.py RecommendationEngine.build_report()
       ─────────────────────────────────────────────────────────────────────────────────────────
27     SHARED-AGAIN      SIMULATION              stlms/simulation/engine.py    SimulationEngine (5 simulators)
       ─────────────────────────────────────────────────────────────────────────────────────────
28     SHARED-AGAIN      GOVERNANCE              stlms/governance/engine.py    GovernanceEngine
                                                 stlms/governance/artifact.py  GovernanceArtifact.produce()
                                                                               → config_version Card
       ─────────────────────────────────────────────────────────────────────────────────────────
29     SHARED-AGAIN      CONSUMER                stlms/consumer/engine.py      ConsumerEngine
       ═══════════════════════════════════════════════════════════════════════════════════════════
OPT    OPTIONAL          INTEGRATION             stlms/integration/engine.py   IntegrationEngine
                                                                               (pipeline orchestration)
```

### CROSS-CUTTING SYSTEMS

```
┌──────────────────────────────────────────────────────────────────┐
│ SYSTEM              FILE                        FUNCTION          │
├──────────────────────────────────────────────────────────────────┤
│ SNAPSHOT            stlms/snapshot/manager.py   SnapshotManager   │
│                     stlms/snapshot/registry.py  SnapshotRegistry  │
│                     stlms/snapshot/validator.py SnapshotValidator │
│                     stlms/snapshot/consumer.py  SnapshotConsumer  │
│                                                                   │
│ SHARED CORE         stlms/core/shell.py         STLMSShell        │
│                                                                   │
│ CLI                 stlms/cli/interactive.py     InteractiveCLI    │
│                                                                   │
│ WEB                 data_viewer/server.py       Handler           │
│                                                                   │
│ SQLite              stlms/sqlite/connection.py  SQLiteConnection  │
│                     stlms/sqlite/manager.py     SQLiteManager     │
│                     stlms/sqlite/viewer.py      SQLiteViewer      │
│                     stlms/sqlite/validator.py   SQLiteValidator   │
│                     stlms/sqlite/query.py       QueryHelper       │
└──────────────────────────────────────────────────────────────────┘
```

---

## 2. MTF (MULTI-TIME FRAME) SYSTEM

### Filosofi MTF

```
MTF BUKAN dibangun dari candle.
MTF dibangun dari kumpulan Supertrend Point dan seluruh artifact yang dimilikinya.

Satu Wave = 6 Line = banyak SP.
Wave structure → MTF Sector classification.
```

### Cara Kerja MTF

```
┌──────────────────────────────────────────────────────────────────┐
│                      MTF FLOW                                     │
│                                                                   │
│  SP (100 candle)                                                  │
│      │                                                            │
│      ▼                                                            │
│  LineBuilder ──► 18 Lines (support/resistance walls)             │
│      │                                                            │
│      ▼                                                            │
│  WaveBuilder ──► 3 Waves (masing-masing 6 Line)                  │
│      │                                                            │
│      ▼                                                            │
│  Wave.classify() ──► 13 possible structures                      │
│      │                                                            │
│      ▼                                                            │
│  EvidenceEngine.mtf_sector(wave_structure, st_dir)                │
│      │                                                            │
│      ▼                                                            │
│  MTF Output: (sector, long_score, short_score)                    │
└──────────────────────────────────────────────────────────────────┘
```

### MTF Score Calculation

MTF score dihitung dari **wave structure classification**. Setiap wave structure memiliki base score yang mencerminkan kejelasan struktur market:

```
┌──────────────────────────────────────────────────────────────────────────┐
│ WAVE STRUCTURE           MTF SECTOR        BASE SCORE    INTERPRETASI    │
├──────────────────────────────────────────────────────────────────────────┤
│ STRONG_ACCUMULATION      BULLISH_TREND     8500          Trend kuat UP   │
│ STRONG_DISTRIBUTION      BEARISH_TREND     8500          Trend kuat DOWN │
│ CONTINUATION_UP          BULLISH_TREND     7000          Trend lanjut UP │
│ CONTINUATION_DOWN        BEARISH_TREND     7000          Trend lanjut DN │
│ CONFIRMED_RANGE          RANGE             7500          Range jelas     │
│ RANGE_EXPANDING          RANGE             6500          Range melebar   │
│ RANGE_COMPRESSING        COMPRESSION       7000          Range menyempit │
│ REVERSAL_UP              REVERSAL_UP       6500          Pembalikan UP   │
│ REVERSAL_DOWN            REVERSAL_DOWN     6500          Pembalikan DOWN │
│ EXHAUSTION_UP            EXHAUSTION        5500          Trend lelah UP  │
│ EXHAUSTION_DOWN          EXHAUSTION        5500          Trend lelah DN  │
│ SIDEWAY                  RANGE             7000          Sideways        │
│ CHAOS                    CHAOS             3000          Tidak jelas     │
└──────────────────────────────────────────────────────────────────────────┘
```

### Score Formula

```python
# Step 1: Dapatkan base score dari wave structure
sector, base_score = WAVE_MTF_TABLE[wave_structure]

# Step 2: Hitung directional score berdasarkan st_dir
# LONG: jika st_dir = 1 (UP), score tetap. Jika st_dir = -1, score dibalik.
# SHORT: jika st_dir = -1 (DOWN), score tetap. Jika st_dir = 1, score dibalik.

long_score = base_score if st_dir == 1 else 10000 - base_score
short_score = base_score if st_dir == -1 else 10000 - base_score

# Step 3: Score masuk ke Direction Bus
dir_bus.mtf_long = long_score   # 0-10000
dir_bus.mtf_short = short_score  # 0-10000

# Step 4: Direction Bus digunakan oleh Clone untuk entry decision
# LONG clone: dir_bus.mtf_long > 5000 → trend mendukung LONG
# SHORT clone: dir_bus.mtf_short > 5000 → trend mendukung SHORT
```

### Contoh Perhitungan

**Contoh 1: BTCUSDT, Wave = CONTINUATION_UP, st_dir = 1 (UP)**

```
base_score = 7000
long_score = 7000 (st_dir=1, tetap)
short_score = 10000 - 7000 = 3000 (st_dir=1, dibalik)

MTF Sector: BULLISH_TREND
MTF Long: 7000 → mendukung LONG entry
MTF Short: 3000 → tidak mendukung SHORT entry
```

**Contoh 2: BTCUSDT, Wave = RANGE_COMPRESSING, st_dir = 1 (UP)**

```
base_score = 7000
long_score = 7000
short_score = 3000

MTF Sector: COMPRESSION
MTF Long: 7000 → range menyempit, potensi breakout
MTF Short: 3000 → tidak mendukung SHORT
```

**Contoh 3: BTCUSDT, Wave = CHAOS, st_dir = 0**

```
base_score = 3000
long_score = 3000 (st_dir != 1, tetap rendah)
short_score = 3000 (st_dir != -1, tetap rendah)

MTF Sector: CHAOS
MTF Long: 3000 → tidak jelas, tidak entry
MTF Short: 3000 → tidak jelas, tidak entry
```

**Contoh 4: BTCUSDT, Wave = STRONG_DISTRIBUTION, st_dir = -1 (DOWN)**

```
base_score = 8500
long_score = 10000 - 8500 = 1500 (st_dir=-1, dibalik)
short_score = 8500 (st_dir=-1, tetap)

MTF Sector: BEARISH_TREND
MTF Long: 1500 → sangat tidak mendukung LONG
MTF Short: 8500 → sangat mendukung SHORT
```

### Penggunaan MTF di Pipeline

```
1. STRUCTURE (WaveBuilder) → klasifikasi wave structure
2. EVIDENCE (mtf_sector) → konversi ke MTF sector + score
3. EVIDENCE (dir_bus) → MTF score masuk Direction Bus
4. CLONE (observe_long/short) → baca dir_bus.mtf_long/short
5. CLONE (dirOk check) → mtf_long > 5000 untuk LONG, mtf_short > 5000 untuk SHORT
6. ORACLE (vectorize) → norm01(mtf_final, 0, 9000) sebagai dimensi vektor
```

### Aturan Penting

1. **MTF BUKAN untuk GRID** — GRID buta arah, tidak menggunakan MTF
2. **MTF = konfirmasi, bukan trigger** — MTF mengkonfirmasi arah, tidak memicu entry sendiri
3. **Score 0-10000** — semakin tinggi semakin mendukung arah tersebut
4. **CHAOS = 3000** — tidak ada struktur jelas, semua clone WAIT
5. **GRID TIDAK menggunakan stDir/MTF** — authority matrix violation jika digunakan

---

## 3. PIPELINE DATA FLOW (PER CANDLE)

```
CANDLE (OHLCV + takerBuyRatio)
  │
  ▼
MARKET COLLECTION ──► market_snapshot Card
  │
  ▼
TRUTH LAYER ──► truth_snapshot Card (15 indicators)
  │                + SPLifecycle (OPEN→LIVE→...→EXPORT)
  │                + TruthTimeline (15 queries)
  │                + MarketEvent (18 event types)
  │                + MutationTracker (candle-to-candle)
  │
  ├────────────────────────────┬──────────────────────────┐
  ▼                            ▼                          ▼
STRUCTURE                    DISTANCE                   EVIDENCE
structure_snapshot Card      distance_snapshot Card     evidence_snapshot Card
(Line, Wave, Cage)           (dist, distAtr, bucket,    (3 buses + MTF)
                               fingerprint)
  │                            │                          │
  └────────────────────────────┴──────────────────────────┘
                               │
                               ▼
                          CLONE ×3
                          clone_observation Card (LONG/SHORT/GRID)
                               │
                               ▼
                          TRADE
                          trade_snapshot Card (ENTRY/EXIT markers)
                               │
                               ▼
                          POSITION
                          position_snapshot Card (MAE/MFE/hold)
                               │
                               ▼
                          STATISTICS (10 domains)
                          statistics_snapshot Card
                               │
                               ▼
                          BAG
                          bag_artifact Card
                               │
                               ▼
                          KNOWLEDGE (7 entities)
                          knowledge_snapshot Card
                               │
                               ▼
                          PREDICTION
                          prediction_snapshot Card
                               │
                               ▼
                          TRADING SCHEMA → RECOMMENDATION → SIMULATION
                               │
                               ▼
                          GOVERNANCE → CONSUMER

  ═══════════════════════════════════════════════════════════════
  CROSS-CUTTING: SNAPSHOT (semua Card) + CLI + WEB + SQLite
  ═══════════════════════════════════════════════════════════════
```
