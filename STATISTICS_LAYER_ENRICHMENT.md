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
