# PHASE 0.5 — IMPLEMENTATION ENRICHMENT PATCH

## ST-LMS v3 — Menutup Implementation Gap Sebelum Coding

**Date:** 2026-07-29
**Status:** PHASE 0.5 — FINAL PREREQUISITE BEFORE PHASE 1
**Scope:** 5 contracts — Recommendation, Simulation, OI Ownership, OI Propagation, Prediction OI Dimension

---

## 1. RECOMMENDATION PACKAGE CONTRACT

### 1.1 Output Contract

Recommendation Package WAJIB menghasilkan structured report — BUKAN sinyal BUY/SELL.

```json
{
  "market_identity": {
    "symbol": "BTCUSDT",
    "timeframe": "1m",
    "report_time_wib": "2026-07-29T11:30:00+07:00",
    "report_id": "REC_20260729_1130"
  },
  "current_state": {
    "phase": "SIDEWAY_COMPRESSION",
    "character": "LOW_VOLATILITY_ACCUMULATION",
    "maturity": "81%"
  },
  "truth_summary": {
    "supertrend": {"direction": "UP", "color": "HIJAU"},
    "distance_atr": 0.15,
    "indicators": {
      "rsi": 52,
      "wpr": -35,
      "macd_hist": 0.003
    }
  },
  "structure_summary": {
    "wave": "RANGE_COMPRESSING",
    "cage": {"status": "VALID_COMPRESSION", "upper": 62500, "lower": 61800, "range_atr": 1.8},
    "nearest": {"support": 61800, "resistance": 62500}
  },
  "distance_summary": {
    "dist_atr": 0.15,
    "dist_ceiling": 0.85,
    "dist_floor": 0.15,
    "fingerprint": [0.15, 0.18, 0.14, 0.12, 0.15],
    "trend": "STABLE"
  },
  "wave_summary": {
    "structure": "RANGE_COMPRESSING",
    "oi_behavior": "ACCUMULATION",
    "oi_interpretation": "Smart money accumulating before breakout"
  },
  "knowledge_summary": {
    "similar_pattern": {"type": "COMPRESSION_BREAKOUT", "frequency": "73%", "sample": 47},
    "market_biography": "3rd compression cycle this session",
    "market_character": "MEAN_REVERSION with BREAKOUT tendency"
  },
  "prediction_summary": {
    "breakout_probability": 0.82,
    "continuation_probability": 0.12,
    "reversal_probability": 0.04,
    "fake_breakout_probability": 0.02,
    "supporting_factors": {
      "price": "STRONG — above ST, within cage",
      "structure": "COMPRESSION — range tightening",
      "volume": "INCREASING — building pressure",
      "oi": "ACCUMULATION +4% — smart money entry",
      "knowledge": "Similar pattern 76% win rate"
    }
  },
  "risk_summary": {
    "volatility": "LOW",
    "max_adverse_excursion": 0.8,
    "recommended_position_pct": 15
  },
  "strategy_schema": {
    "primary": "GRID_COMPRESSION",
    "secondary": "LONG_BREAKOUT",
    "confidence": 89
  },
  "action_plan": {
    "prepare": "BUY area at cage.lower (61800-61850)",
    "entry_trigger": "price bounce from support + volume confirmation",
    "invalidation_condition": "close below support (61800)",
    "target": "cage.upper (62500) then breakout target (62800)"
  },
  "confidence": 89
}
```

### 1.2 Package Builder Contract

```
RecommendationPackage.build(inputs):
  Input:
    - truth_package: dict        (dari PHASE-04)
    - structure_package: dict    (dari PHASE-08)
    - distance_package: dict     (dari PHASE-06)
    - knowledge_package: dict    (dari PHASE-11)
    - prediction_package: dict   (dari PHASE-12)
    - trading_schema_package: dict (dari PHASE-13)

  Output: RecommendationReport (dict)

  Rules:
    - NO new computation — hanya agregasi
    - Semua data dari package upstream
    - confidence = weighted average dari semua layer
    - action_plan bersifat "prepare", bukan "execute"
```

### 1.3 Phase Assignment

```
PHASE-15: Recommendation Layer
  ├── recommendation_artifact.py  (RecommendationReport immutable card)
  ├── recommendation_package.py   (RecommendationPackage builder)
  ├── recommendation_validator.py (completeness, consistency checks)
  └── recommendation_consumer.py  (API untuk Simulation, Dashboard)
```

---

## 2. SIMULATION CONTRACT

### 2.1 Input Contract

```json
{
  "simulation_request": {
    "symbol": "BTCUSDT",
    "start_time_ms": 1753500000000,
    "end_time_ms": 1753586400000,
    "initial_balance": 100.0,
    "strategy": "GRID_COMPRESSION",
    "sim_types": ["architecture", "market_possibility", "balance"],
    "config_override": {}
  }
}
```

### 2.2 Output Contract

```json
{
  "simulation_result": {
    "request_id": "SIM_20260729_001",
    "symbol": "BTCUSDT",
    "duration_ms": 86400000,
    "candles_processed": 1440,
    "architecture_validation": {
      "pipeline_stages": "22/22 OK",
      "card_sharing": "PASS",
      "determinism": "PASS",
      "snapshot_count": "10/candle OK",
      "unidirectional": "PASS"
    },
    "market_possibility": {
      "scenarios_tested": 5,
      "breakout_accuracy": 0.78,
      "continuation_accuracy": 0.65,
      "reversal_accuracy": 0.42
    },
    "balance_simulation": {
      "initial_balance": 100.0,
      "final_balance": 103.47,
      "profit_loss": 3.47,
      "trade_count": 12,
      "win_count": 8,
      "loss_count": 4,
      "win_rate": 66.7,
      "max_drawdown": -2.1,
      "max_drawdown_pct": -2.1,
      "sharpe_estimate": 1.8
    },
    "knowledge_score": {
      "pattern_match_quality": 0.82,
      "biography_consistency": 0.91,
      "character_stability": 0.87
    },
    "architecture_report": {
      "all_layers_valid": true,
      "snapshot_lineage_ok": true,
      "no_circular_dependency": true
    }
  }
}
```

### 2.3 5 Simulator Contracts

| Simulator | Input | Output | Phase |
|-----------|-------|--------|-------|
| Architecture Simulator | Pipeline config, all artifacts | Validation report — all layers, stages, snapshots | PHASE-16 |
| Market Possibility Simulator | Prediction package, historical data | Accuracy report per possibility type | PHASE-16 |
| Market Push Simulator | Full market data timeline | How ST-LMS responds to phase transitions | PHASE-16 |
| Knowledge Simulator | Knowledge package, historical patterns | Pattern match quality, biography consistency | PHASE-16 |
| Balance Simulator | Full pipeline + initial balance | Final balance, P&L, drawdown, win_rate | PHASE-16 |

### 2.4 Phase Assignment

```
PHASE-16: Simulation Layer
  ├── simulation_artifact.py     (SimulationResult immutable card)
  ├── simulation_engine.py       (5 simulators)
  ├── simulation_package.py      (SimulationReportPackage)
  ├── simulation_validator.py    (determinism, completeness)
  └── simulation_consumer.py     (API untuk Benchmark, Dashboard)
```

---

## 3. OI OWNERSHIP CONTRACT

### 3.1 OI Artifact Definition

```json
{
  "oi_artifact": {
    "oi_id": "OI_BTCUSDT_5m_20260729_1100",
    "symbol": "BTCUSDT",
    "source": "BINANCE_FUTURES",
    "timeframe": "5m",
    "start_time_ms": 1753500600000,
    "end_time_ms": 1753500840000,
    "value": 125600000.0,
    "delta": 2500000.0,
    "delta_pct": 2.03,
    "status": "OK",
    "owner_count": 5
  }
}
```

### 3.2 Ownership Rules

```
Rule 1: OI dimiliki oleh timeframe aslinya.
  OI 5m mencakup 5 menit (11:00-11:04).
  OI TIDAK diinterpolasi menjadi 1m.

Rule 2: Satu OI value digunakan oleh seluruh SP dalam rentang waktunya.
  SP 11:00 → OI_ID = OI_BTCUSDT_5m_20260729_1100
  SP 11:01 → OI_ID = OI_BTCUSDT_5m_20260729_1100
  SP 11:02 → OI_ID = OI_BTCUSDT_5m_20260729_1100
  SP 11:03 → OI_ID = OI_BTCUSDT_5m_20260729_1100
  SP 11:04 → OI_ID = OI_BTCUSDT_5m_20260729_1100

Rule 3: OI TIDAK dimiliki oleh candle.
  Candle adalah input Market Collection.
  Setelah Market Collection, sistem bekerja pada level SP.
  OI di-attach ke SP, bukan ke candle.

Rule 4: OI kosong = INSUFFICIENT_DATA.
  Tidak ada interpolasi.
  Tidak ada nilai netral (5000).
```

### 3.3 Implementation Location

```
PHASE-01 (Market Collection):
  - Kumpulkan OI dari source (Binance Futures API / fixture)
  - Simpan di open_interest_series dengan timeframe asli
  - Tandai status: OK / PROXY / MISSING / WARMUP

PHASE-03 (Supertrend Point):
  - truth_snapshot.oi = OI value dari slot yang mencakup timestamp SP
  - truth_snapshot.oi_delta = delta dari slot sebelumnya
  - truth_snapshot.oi_status = status OI (OK/INSUFFICIENT_DATA)
  - truth_snapshot.oi_source = source OI (EXCHANGE/PROXY)
```

---

## 4. OI PROPAGATION CONTRACT

### 4.1 OI → Supertrend Line

```
Line.oi_profile:
  oi_avg: float              — rata-rata OI dari seluruh member SP
  oi_start: float            — OI saat line dimulai
  oi_end: float              — OI saat line berakhir
  oi_trend: str              — ACCUMULATION / DISTRIBUTION / STABLE
  oi_delta_sum: float        — akumulasi delta selama lifetime line
  oi_delta_pct: float        — persentase perubahan OI

Perhitungan:
  oi_avg = mean([sp.oi for sp in line.members if sp.oi is not None])
  oi_trend = "ACCUMULATION" if oi_end > oi_start * 1.02
             "DISTRIBUTION" if oi_end < oi_start * 0.98
             "STABLE"

Penyimpanan:
  TANPA SQLite baru — gunakan payload_json di wave_history / cage_history
  Atau: computed runtime saat dibutuhkan
```

### 4.2 OI → Wave

```
Wave.oi_profile:
  oi_line_profile: [float x6]  — OI average dari 6 lines
  oi_trend: str                 — ACCUMULATION / DISTRIBUTION / MIXED
  oi_divergence: str            — OI vs PRICE divergence
  oi_interpretation: str        — interpretasi perilaku OI

Perhitungan:
  oi_line_profile = [line1.oi_avg, ..., line6.oi_avg]
  oi_trend = "ACCUMULATION" if majority lines accumulating
  oi_divergence = "BULLISH" if price flat/down + OI up
                  "BEARISH" if price flat/up + OI down
                  "NONE"

Interpretasi:
  ACCUMULATION + price flat → "Smart money accumulating before breakout"
  DISTRIBUTION + price flat → "Smart money distributing before breakdown"
  ACCUMULATION + price up   → "Strong trend with institutional support"
  DISTRIBUTION + price down → "Trend weakening, institutional exit"

Penyimpanan:
  TANPA SQLite baru — gunakan payload_json di wave_history
```

### 4.3 OI → Prediction

```
Prediction OI Dimensions:
  oi_trend_continuation: float    — probabilitas OI trend berlanjut
  oi_divergence_signal: float     — kekuatan sinyal divergence
  oi_support_level: float         — level OI sebagai support/resistance
  oi_context: str                 — ringkasan konteks OI

Perhitungan:
  oi_trend_continuation = berdasarkan historical OI trend persistence
  oi_divergence_signal = 0.0-1.0 berdasarkan kekuatan divergence
  oi_support_level = OI level dengan akumulasi tertinggi

Integration ke Market Possibility:
  Breakout probability += oi_boost jika OI akumulasi + kompresi
  Fake breakout probability += oi_penalty jika OI distribusi + kompresi

Penyimpanan:
  TANPA SQLite baru — gunakan payload_json di predictions
```

### 4.4 Implementation Location

```
PHASE-05 (Supertrend Line):
  - Line.oi_profile dihitung di LineBuilder
  - Disimpan di payload_json structure_snapshots / wave_history

PHASE-07 (Wave):
  - Wave.oi_profile dihitung di WaveBuilder
  - Disimpan di payload_json wave_history

PHASE-12 (Prediction):
  - OI dimensions ditambahkan ke prediction_snapshot
  - Disimpan di payload_json predictions
```

---

## 5. PREDICTION OI DIMENSION CONTRACT

### 5.1 Market Possibility Structure (Enriched)

```json
{
  "market_possibility": {
    "symbol": "BTCUSDT",
    "timestamp_wib": "2026-07-29T11:30:00+07:00",
    "possibilities": [
      {
        "type": "BREAKOUT_UP",
        "probability": 0.82,
        "confidence": "HIGH",
        "supporting_factors": {
          "price": {"signal": "STRONG", "detail": "above ST, near resistance"},
          "structure": {"signal": "STRONG", "detail": "VALID_COMPRESSION, range tightening"},
          "volume": {"signal": "MODERATE", "detail": "increasing, building pressure"},
          "oi": {"signal": "STRONG", "detail": "accumulation +4%, institutional support"},
          "knowledge": {"signal": "STRONG", "detail": "similar pattern 76% win rate"}
        }
      },
      {
        "type": "CONTINUATION_COMPRESSION",
        "probability": 0.12,
        "confidence": "LOW"
      },
      {
        "type": "REVERSAL_DOWN",
        "probability": 0.04,
        "confidence": "LOW"
      },
      {
        "type": "FAKE_BREAKOUT",
        "probability": 0.02,
        "confidence": "LOW",
        "oi_warning": "OI not confirming — watch for fake breakout"
      }
    ],
    "oi_context": {
      "trend": "ACCUMULATION",
      "strength": 0.78,
      "divergence": "NONE",
      "interpretation": "Institutional accumulation supports breakout thesis"
    }
  }
}
```

### 5.2 OI Boost/Penalty Rules

```
OI_BOOST:
  OI accumulation + price compression → +8% breakout probability
  OI accumulation + price near support → +5% reversal probability
  OI stable + strong trend → +3% continuation probability

OI_PENALTY:
  OI distribution + price compression → +10% fake breakout probability
  OI divergence (price up, OI down) → -5% continuation probability
  OI flat + low volume → -3% all probabilities (uncertainty)

OI_NEUTRAL:
  OI INSUFFICIENT_DATA → no boost, no penalty
  OI WARMUP → no boost, no penalty
```

---

## 6. IMPLEMENTATION IMPACT

| Contract | Phase Impacted | New Tables | New Pipeline | New Layer |
|----------|---------------|------------|-------------|-----------|
| Recommendation Package | PHASE-15 | ❌ None | ❌ None | ❌ None |
| Simulation Contract | PHASE-16 | ❌ None | ❌ None | ❌ None |
| OI Ownership | PHASE-01,03 | ❌ None | ❌ None | ❌ None |
| OI Propagation | PHASE-05,07,12 | ❌ None (payload_json) | ❌ None | ❌ None |
| Prediction OI Dimension | PHASE-12 | ❌ None (payload_json) | ❌ None | ❌ None |

**0 perubahan arsitektur. 0 SQLite baru. 0 pipeline baru. 0 layer baru.**

---

## 7. VERDICT

```
┌──────────────────────────────────────────────────────────────────┐
│              PHASE 0.5 — IMPLEMENTATION ENRICHMENT                │
│                                                                    │
│  5 contracts filled:                                               │
│    ✅ Recommendation Package — structured report, bukan sinyal    │
│    ✅ Simulation Contract — 5 simulators, input/output defined    │
│    ✅ OI Ownership — timeframe ownership, SP inheritance          │
│    ✅ OI Propagation — Line → Wave → Prediction chain             │
│    ✅ Prediction OI Dimension — boost/penalty rules               │
│                                                                    │
│  Architecture Impact: ZERO                                         │
│    ❌ 0 new layers                                                 │
│    ❌ 0 new SQLite tables                                          │
│    ❌ 0 new pipeline stages                                        │
│    ❌ 0 architecture changes                                       │
│                                                                    │
│  Implementation: payload_json + structured contracts               │
│                                                                    │
│  STATUS: READY FOR PHASE 1                                        │
└──────────────────────────────────────────────────────────────────┘
```
