# ST-LMS v3 — MARKET OBSERVATION CONTRACT

**Date:** 2026-07-29
**Status:** FINAL ARCHITECTURAL ENRICHMENT — 0 pipeline changes
**Concept:** 1 Candle = 1 Market Observation Object

---

## 1. FILOSOFI BARU: Market Observation Object

### Saat Ini (Candle-Oriented):

```
Candle → Market Snapshot → Truth Snapshot → Structure Snapshot → ...
```

Setiap stage menghasilkan snapshot-nya sendiri. Tidak ada objek yang menyatukan seluruh observasi untuk satu candle.

### Seharusnya (Market Observation Oriented):

```
1 Candle = 1 Market Observation Object
  │
  ├── Market Observation (market_snapshot)
  ├── Truth Observation (truth_snapshot + lifecycle + version + mutation + reliability)
  ├── Structure Observation (structure_snapshot + line_lifecycle + wave_rates)
  ├── Evidence Observation (evidence_snapshot + mtf_context)
  ├── Clone Observation (clone_observation ×3)
  ├── Statistics Observation (statistics_snapshot + evolution_stats)
  ├── BAG Observation (bag_artifact + dna_profile + market_character)
  ├── Knowledge Observation (knowledge_snapshot + evolution_context)
  ├── Prediction Observation (prediction_snapshot)
  ├── Recommendation Observation (MIR report section)
  ├── Simulation Observation (simulation result)
  ├── MTF Context (inherited from higher TFs)
  ├── Timeline Entry (timestamp + all layer versions)
  ├── Reliability Summary (per-layer reliability)
  ├── Lifecycle States (per-object lifecycle)
  ├── Mutation Deltas (per-object changes)
  ├── Historical Index (position in 48000 memory)
  └── Snapshot Metadata (batch_id, lineage)
```

---

## 2. 48000 MARKET OBSERVATION MEMORY

### Koreksi: Truth Observation Memory → Market Observation Memory

| Sebelum | Sesudah |
|---------|---------|
| 48000 Truth Observation Memory | **48000 Market Observation Memory** |
| Hanya Truth Layer yang 48000 | **Setiap layer memiliki 48000 observation** |
| Truth = single source, layer lain bervariasi | **1 candle = 1 observation untuk SEMUA layer** |

### Mengapa 48000 untuk SEMUA layer?

Karena **1 candle = 1 Market Observation Object**. Setiap candle menghasilkan tepat 1 observasi untuk setiap layer:

- 1 candle → 1 Truth Observation (selalu, mandatory)
- 1 candle → 1 Structure Observation (selalu, meskipun Line/Wave belum terbentuk)
- 1 candle → 1 Evidence Observation (selalu)
- 1 candle → 3 Clone Observations (LONG/SHORT/GRID, selalu mandatory)
- 1 candle → 1 Statistics Observation (rolling, selalu)

**Yang TIDAK 48000:** Internal PointBuilder state (`pc`, `puf`, `plf`, `ag`, `al`, `hs`, `ls`, `wp1`, `vp`, `mh1`). Ini adalah state komputasi, bukan observation. State ini hanya dipakai untuk menghitung candle berikutnya.

### Apa yang 48000 vs Tidak:

| Komponen | 48000? | Alasan |
|----------|--------|--------|
| **Candle** | ✅ Ya | 1 candle = 1 observation |
| **Truth Point (15 indikator)** | ✅ Ya | Output observasi, disimpan |
| **Truth Observation (lifecycle, version, mutation, reliability)** | ✅ Ya | Metadata observasi |
| **Structure Observation (line, wave, cage context)** | ✅ Ya | 1 per candle |
| **Evidence Observation (3 buses, MTF context)** | ✅ Ya | 1 per candle |
| **Clone Observation (×3)** | ✅ Ya | 3 per candle (LONG/SHORT/GRID) |
| **Statistics Observation (rolling)** | ✅ Ya | 1 per candle |
| **Knowledge Observation** | ✅ Ya | 1 per candle |
| **Prediction Observation** | ✅ Ya | 1 per candle |
| **Snapshot Metadata** | ✅ Ya | 1 per candle |
| **Timeline Entry** | ✅ Ya | 1 per candle |
| **Internal PointBuilder State** | ❌ Tidak | `pc`, `puf`, `plf`, `ag`, `al`, `hs`, `ls`, `wp1`, `vp`, `mh1` — hanya untuk komputasi |
| **ATR history** | ✅ Ya | Disimpan sebagai bagian Truth Observation |
| **W%R history** | ✅ Ya | Disimpan sebagai bagian Truth Observation |

---

## 3. TRUTH LAYER — DARI INDICATOR LAYER KE MARKET TRUTH OBSERVATION LAYER

### Perubahan Filosofi:

| Dulu | Sekarang |
|------|----------|
| Truth Layer = Indicator Calculator | Truth Layer = **Market Truth Observation Layer** |
| Output: 15 indikator | Output: **Truth Observation Object** (indikator + metadata) |
| Fokus: bagaimana menghitung | Fokus: **bagaimana mengobservasi dan merekam** |

### Truth Observation Object:

```
Truth Observation #45673:
  ┌─ Truth Point (15 indikator)
  │   st, st_dir, st_color, atr, ema, rsi, wpr, macd_hist, dist_atr, vol_delta, flip
  │
  ├─ Lifecycle
  │   state: MATURE, age: 73 candles since OPEN
  │
  ├─ Version
  │   v8 (7 mutations since creation)
  │
  ├─ Mutation
  │   delta from prev: price +0.15%, rsi +3.2, wpr -5.0
  │
  ├─ Reliability
  │   rsi: 0.95, wpr: 0.90, atr: 0.98, overall: 0.92
  │
  ├─ Structure Context
  │   line: Support Line #17 (member ke-8)
  │   wave: Wave #3 (RANGE_COMPRESSING)
  │   cage: VALID_COMPRESSION
  │
  ├─ MTF Context (inherited)
  │   5m: ST=62150 UP, Wave=CONTINUATION
  │   15m: ST=62000 UP, Wave=STRONG_ACCUMULATION
  │   1h: ST=61500 UP, Wave=CONTINUATION
  │
  ├─ Clone Context
  │   LONG: WAIT (STDIR_OR_DIRBUS_MISMATCH)
  │   SHORT: WAIT (STDIR_OR_DIRBUS_MISMATCH)
  │   GRID: ACTIVE (fill #2)
  │
  ├─ Statistics Context
  │   win_rate: LONG 62%, SHORT 55%, GRID 71%
  │
  ├─ Historical Index
  │   position: 45673 / 48000
  │   snapshot_batch: Snapshot-001
  │
  └─ Timeline Entry
      timestamp: 2026-07-29 11:30:00 WIB
```

**Pertanyaan yang bisa dijawab:** "Pada 27 hari lalu, Supertrend Line merah dengan 18 anggota, lifetime 74 candle, mutation 4 kali, reliability 92%, continuation rate 81%, wave type expansion, MTF score 86, market character bullish squeeze — berakhir menjadi apa?"

---

## 4. STRUCTURE LAYER — "EMAS" ST-LMS

### Supertrend Line — Observation Object:

```
Line #17:
  ┌─ Identity
  │   line_id: LINE_20260729_0017
  │   role: SUPPORT
  │   st_value: 61800
  │
  ├─ Lifecycle
  │   state: MATURE
  │   age: 74 candles
  │   formed_at: candle 45599
  │
  ├─ Membership
  │   members: 18 SP
  │   first_member: SP #45599
  │   last_member: SP #45673
  │   dominant_color: HIJAU (15/18)
  │
  ├─ Mutation
  │   mutation_count: 4
  │   flip_count: 3
  │   break_events: [candle 45620, candle 45645]
  │
  ├─ Reliability
  │   score: 92%
  │   strength: 0.83 (flip_count / members)
  │
  ├─ OI Profile
  │   oi_avg: 124.5M
  │   oi_trend: ACCUMULATION (+2.5%)
  │
  ├─ Statistics
  │   continuation_rate: 81%
  │   survival_rate: 0.89
  │   avg_lifetime: 68 candles (historical)
  │   frequency_in_48000: 12 occurrences
  │
  ├─ Historical
  │   win_rate_when_present: LONG 68%, SHORT 42%, GRID 73%
  │   best_clone: GRID
  │   worst_clone: SHORT
  │
  ├─ DNA
  │   dna_similarity: 89% match to historical LINE pattern
  │
  ├─ Market Character
  │   profile: BULLISH_SQUEEZE
  │   context: Support in compression, building pressure
  │
  └─ Death
      reason: BREAK (price closed below support)
      ended_at: candle 45673
```

### Wave — Observation Object:

```
Wave #183:
  ┌─ Identity
  │   wave_id: WAVE_20260729_0183
  │   structure: RANGE_COMPRESSING
  │
  ├─ Lifecycle
  │   state: LIVE (expanding)
  │   age: 73 candles
  │
  ├─ Membership
  │   lines: 19
  │   support_lines: 10
  │   resistance_lines: 9
  │
  ├─ Evolution
  │   breakout_count: 4
  │   continuation_count: 8
  │   reversal_count: 2
  │   compression_count: 3
  │   expansion_count: 6
  │
  ├─ Rates
  │   continuation_rate: 42% (8/19)
  │   breakout_rate: 21% (4/19)
  │   reversal_rate: 11% (2/19)
  │
  ├─ Reliability
  │   score: 93%
  │
  ├─ OI Profile
  │   oi_trend: ACCUMULATION
  │   oi_divergence: BULLISH
  │
  ├─ Historical
  │   total_occurrences: 217 (in all history)
  │   occurrences_in_48000: 3
  │   dna_similarity: 89%
  │
  ├─ Profit Profile
  │   dominant_clone: LONG
  │   best_clone: LONG
  │   worst_clone: SHORT
  │   historical_expectancy: +0.84%
  │
  ├─ Market Character
  │   profile: BULL_SQUEEZE
  │   context: Accumulation before breakout
  │
  └─ Prediction Context
      breakout_probability: 82%
      continuation_probability: 12%
      reversal_probability: 4%
```

---

## 5. BAG — Market Intelligence Compression Layer

### BAG BUKAN hanya Stage 13. BAG adalah sumber:

| Output BAG | Consumer |
|-----------|----------|
| Grouped artifacts (4-dim bucket) | Academy (Stage 16) |
| **Market DNA** (compressed fingerprint) | HiveMind (Stage 18), Simulation, Recommendation |
| **Historical Market Character** | HiveMind, Prediction, Recommendation |
| **Pattern Mining** (association rules) | Knowledge |
| **Sequence Analysis** (wave/cage sequences) | Prediction |
| **Behavior Analysis** (6 profiles) | Recommendation |
| **Consensus + Conflict** | Darwin (Stage 20) |
| **Maturity Scoring** | Librarian |

### Market DNA (dari BAG):

```
Market DNA Profile (Snapshot-001, SP 1-48000):
  ┌─ Wave Distribution (13-bin)
  │   STRONG_ACCUMULATION: 12%
  │   CONTINUATION_UP: 18%
  │   RANGE_COMPRESSING: 25%
  │   REVERSAL_UP: 5%
  │   ...
  │
  ├─ Cage Distribution
  │   NONE: 45%
  │   VALID_COMPRESSION: 30%
  │   LOOSE_SIDEWAY: 25%
  │
  ├─ Average Metrics
  │   avg_dist_atr: 0.35
  │   avg_atr: 95 USDT
  │   avg_rsi: 52
  │
  ├─ Dominant Character
  │   profile: MEAN_REVERSION with BREAKOUT tendency
  │   stability: 0.87
  │
  ├─ Evolution Trend
  │   volatility: DECREASING
  │   range: TIGHTENING
  │   trend_strength: INCREASING
  │
  └─ MTF Summary
      5m: BULLISH dominant
      15m: BULLISH dominant
      1h: NEUTRAL
      4h: BULLISH
```

---

## 6. KNOWLEDGE LAYER — DARI PASIF KE AKTIF

### Historical Market Learning (dalam HiveMind):

```
HiveMind.synthesize() — ENRICHED:

  INPUT:
    - Academy: win_rate per bucket (existing)
    - Oracle: similarity match (existing)
    - Evidence: current evidence (existing)
    - BAG DNA: market DNA profile (NEW)
    - BAG Character: historical market character (NEW)
    - Structure: wave #183 context (NEW)
    - Statistics: evolution stats (NEW)

  OUTPUT:
    - intelligence_score: 7200
    - dominant_bias: BULLISH
    - evolution_context:
        wave_type: RANGE_COMPRESSING
        wave_age: 73 candles
        historical_occurrences: 217
        dna_similarity: 89%
        best_historical_clone: LONG (68% win)
        historical_expectancy: +0.84%
        prediction: "82% mirip dengan wave #731 yang menghasilkan LONG dominant"
```

---

## 7. MARKET OBSERVATION TIMELINE

```
Candle 45673:
  Truth:        v8 (MATURE, reliability 92%)
  Structure:    v13 (Line #17 member 18/?, Wave #183 LIVE)
  Clone:        v4 (LONG WAIT, SHORT WAIT, GRID ACTIVE fill #2)
  Prediction:   v9 (82% Breakout UP)
  Knowledge:    v3 (HiveMind BULLISH 7200)
  Character:    BULL_SQUEEZE
  Similarity:   89% match to wave #731
  Reliability:  94% overall

Candle 45674:
  Truth:        v8 (UPDATE, price +0.15%)
  Structure:    v14 (Wave mutation: RANGE_COMPRESSING → BREAKOUT_UP)
  Clone:        v5 (LONG ENTRY at 62550)
  Prediction:   v10 (BREAKOUT_UP confirmed, confidence 89→94)
  Knowledge:    v3 (HiveMind BULLISH 7800, +600)
  Character:    BREAKOUT (changed from BULL_SQUEEZE)
  Similarity:   91% match (increased)
  Reliability:  95% (increased)

  Events:
    - WAVE_MUTATION: RANGE_COMPRESSING → BREAKOUT_UP
    - CLONE_MUTATION: LONG WAIT → LONG ENTRY
    - MARKET_CHARACTER_CHANGE: BULL_SQUEEZE → BREAKOUT
    - PREDICTION_CONFIRMED: breakout probability validated
```

---

## 8. IMPLEMENTASI — 0 PIPELINE CHANGES

### Market Observation Object — Implementasi:

```
TIDAK ada pipeline stage baru.
TIDAK ada layer baru.
TIDAK ada snapshot type baru.

MarketObservationObject adalah VIEW / AGGREGATOR di atas existing 22-stage pipeline.

Implementasi:
  stlms/core/shell.py → tambah method:
    get_observation(candle_index) → MarketObservationObject
    
  MarketObservationObject mengumpulkan data dari:
    - truth_snapshots (SQLite)
    - structure_snapshots (SQLite)
    - evidence_snapshots (SQLite)
    - clone_observations (SQLite)
    - trade_markers (SQLite)
    - statistics (in-memory)
    - bag_artifacts (SQLite)
    - knowledge_artifacts (SQLite)
    - predictions (SQLite)
    
  Untuk candle N, query semua tabel di atas WHERE ts = candle_N.ts
  Gabungkan menjadi satu MarketObservationObject.
```

### 48000 Market Observation Memory — Implementasi:

```
48000 = ukuran buffer di Truth Layer.

SETIAP layer menyimpan 48000 observation:
  - Truth: 48000 truth_snapshots di SQLite
  - Structure: 48000 structure_snapshots di SQLite
  - Evidence: 48000 evidence_snapshots di SQLite
  - Clone: 48000 × 3 clone_observations di SQLite
  - Statistics: 48000 statistics_snapshots (rolling) di SQLite
  - Dst.

MarketObservationMemory adalah QUERY LAYER di atas SQLite:
  - Bukan buffer terpisah
  - Bukan sistem baru
  - Hanya query interface: "beri saya observation #45673"
```

---

## 9. FINAL VERDICT

**ST-LMS v3 dengan Market Observation Contract:**

| Aspek | Status |
|-------|--------|
| Pipeline stages | 22 (TIDAK BERUBAH) |
| Layers | 26 (TIDAK BERUBAH) |
| Snapshot types | 10 (TIDAK BERUBAH) |
| SQLite tables | 40 (TIDAK BERUBAH) |
| 1 Candle = 1 Market Observation Object | ✅ Implemented as cross-cutting view |
| 48000 Market Observation Memory | ✅ Query layer di atas SQLite |
| Truth Layer → Market Truth Observation Layer | ✅ Filosofi berubah, kode enrichment |
| Structure Layer = "Emas" ST-LMS | ✅ Line/Wave Observation Objects |
| BAG = Market Intelligence Compression | ✅ DNA + Character + Pattern Mining |
| Knowledge = Historical Market Learning | ✅ HiveMind enrichment |
| Market Observation Timeline | ✅ Query interface |
| Historical Observation untuk semua layer | ✅ Via SQLite query |

**0 pipeline changes. 0 layer changes. 0 snapshot changes. 0 SQLite changes.**
