# ST-LMS v3 — TRUTH LAYER: INDICATORS & SUPPORTING COMPONENTS

**Date:** 2026-07-29

---

## 1. TRUTH LAYER — CORE: 15 INDIKATOR (PointBuilder)

PointBuilder adalah **jantung ST-LMS**. Satu candle → satu Supertrend Point → 15 indikator.

### PRIMARY INDICATORS (8)

| # | Indikator | Field | Formula | Period | Range | Peran |
|---|-----------|-------|---------|--------|-------|-------|
| 1 | **Supertrend** | `st` | hl2 ± ATR×3, band continuation | — | Harga | **FONDASI** — semua keputusan berbasis ST |
| 2 | **ST Direction** | `st_dir` | 1 (UP) / -1 (DOWN), flip detection | — | ±1 | Arah trend — CLONE entry direction |
| 3 | **ST Color** | `st_color` | close > st → HIJAU, close < st → MERAH | — | HIJAU/MERAH | Visual + Line/Wave classification |
| 4 | **ATR** | `atr` | True Range smoothed: atr + (TR-atr)/10 | 10 | >0 | Volatilitas — corridor width, TP/SL distance |
| 5 | **EMA** | `ema` | ema + (close-ema) × 2/15 | 14 | Harga | Trend — entry direction confirmation |
| 6 | **RSI** | `rsi` | 100 - 100/(1 + avg_gain/avg_loss) | 10 | 0-100 | **EXIT ONLY** — overbought/oversold |
| 7 | **Williams %R** | `wpr` | -100 × (hh-close)/(hh-ll) | 14 | -100 to 0 | **EXIT ONLY** — momentum exit signal |
| 8 | **MACD** | `macd_hist` | (ema12-ema26) - signal | 12/26/9 | — | **EXIT ONLY** — HOLD-veto (MACD expanding delays TP) |

### DERIVATIVE INDICATORS (4)

| # | Indikator | Field | Formula | Parent | Peran |
|---|-----------|-------|---------|--------|-------|
| 9 | **W%R Velocity** | `vel` | wpr - previous_wpr | W%R | **EXIT ONLY** — wrong entry detection (deadzone-bounded) |
| 10 | **W%R Acceleration** | `acc` | vel - previous_vel | W%R Velocity | **EXIT ONLY** — acceleration signal (deadzone-bounded) |
| 11 | **EMA Slope** | `ema_slope` | ema - previous_close | EMA | Entry direction — slope positif = trend UP |
| 12 | **Volume Delta** | `vol_delta` | 2 × takerBuyRatio - 1 | Volume | Entry direction — positif = buying pressure |

### COMPUTED METRICS (3)

| # | Metric | Field | Formula | Peran |
|---|--------|-------|---------|-------|
| 13 | **Distance-to-ST** | `dist` | \|close - st\| | Jarak absolut ke ST |
| 14 | **Distance/ATR** | `dist_atr` | dist / atr | Jarak ternormalisasi — entry corridor, fee_safe |
| 15 | **Trend Flip** | `flip` | TREND_FLIP_UP / TREND_FLIP_DOWN | Event — reversal detection |

### INTERNAL STATE (tidak diekspor sebagai indikator)

| State | Purpose |
|-------|---------|
| `pc` (previous close) | State kontigu untuk ATR, RSI |
| `puf` (previous upper band) | Supertrend band continuation |
| `plf` (previous lower band) | Supertrend band continuation |
| `ag/al` (avg gain/loss) | RSI smoothing |
| `hs/ls` (high/low history) | W%R period window |
| `wp1` (previous W%R) | Velocity calculation |
| `vp` (previous velocity) | Acceleration calculation |
| `mh1` (previous MACD hist) | MACD expanding/contracting detection |

---

## 2. SUPPORTING INDICATORS — KOMPONEN PENDUKUNG

Ini adalah komponen yang **MEMBACA** output PointBuilder (TruthPoint) dan **MENGHASILKAN** metadata tambahan. Mereka TIDAK mengubah indikator.

### 2.1 W%R Velocity

| Aspek | Detail |
|-------|--------|
| **Sumber** | `wpr` (Williams %R) dari PointBuilder |
| **Formula** | `vel = wpr - previous_wpr` |
| **Peran** | **EXIT ONLY.** Mendeteksi wrong entry: jika velocity berlawanan dengan posisi dalam 2 candle pertama → WRONG_ENTRY_EARLY |
| **Deadzone** | `WPR_VELOCITY_DEADZONE = 5` — velocity di bawah threshold diabaikan |
| **Consumer** | CloneEngine.decide_exit() — WRONG_ENTRY_EARLY check |
| **Dilarang** | Entry decision |

**Contoh:**
```
SP #41: wpr = -35
SP #42: wpr = -55
vel = -55 - (-35) = -20  →  SIGNIFIKAN (melebihi deadzone 5)
Jika posisi LONG + vel < -deadzone + hold <= 2 → WRONG_ENTRY_EARLY
```

---

### 2.2 W%R Acceleration

| Aspek | Detail |
|-------|--------|
| **Sumber** | `vel` (W%R Velocity) |
| **Formula** | `acc = vel - previous_vel` |
| **Peran** | **EXIT ONLY.** Mendeteksi akselerasi momentum. `acc_signal = ACTIVE` jika |acc| > deadzone |
| **Deadzone** | `WPR_ACCEL_DEADZONE = 8` |
| **Consumer** | EvidenceEngine.exit_bus() — acc_signal; HiveMind — evidence_adj |
| **Dilarang** | Entry decision |

**Contoh:**
```
SP #41: vel = -5
SP #42: vel = -20
acc = -20 - (-5) = -15  →  SIGNIFIKAN (melebihi deadzone 8)
acc_signal = "ACTIVE" → momentum accelerating downward
```

---

### 2.3 MACD (Moving Average Convergence Divergence)

| Aspek | Detail |
|-------|--------|
| **Sumber** | `ema12`, `ema26` dari PointBuilder |
| **Komponen** | MACD Line = ema12 - ema26, Signal Line = smoothed MACD, Histogram = MACD - Signal |
| **Peran** | **EXIT ONLY.** HOLD-veto: jika MACD histogram expanding (|current| > |previous|) + velocity searah trend → TAHAN TP |
| **Consumer** | EvidenceEngine.exit_bus() — hold flag; CloneEngine.decide_exit() — HOLD-veto check |
| **Dilarang** | Entry decision (X di Authority Matrix) |

**Contoh:**
```
SP #41: macd_hist = 2.0
SP #42: macd_hist = 3.5
|3.5| > |2.0| → MACD expanding
Jika velocity searah trend → HOLD = True → TP ditunda
```

---

### 2.4 RSI (Relative Strength Index)

| Aspek | Detail |
|-------|--------|
| **Sumber** | `ag` (avg gain), `al` (avg loss) dari PointBuilder |
| **Formula** | 100 - 100/(1 + ag/al) |
| **Peran** | **EXIT ONLY.** RSI > 70 → overbought → EXIT_BUS signal untuk LONG. RSI < 30 → oversold → EXIT_BUS signal untuk SHORT |
| **Consumer** | EvidenceEngine.exit_bus() — rsi; CloneEngine.decide_exit() — EXIT_BUS check |
| **Dilarang** | Entry decision |

---

### 2.5 EMA (Exponential Moving Average)

| Aspek | Detail |
|-------|--------|
| **Sumber** | PointBuilder state |
| **Formula** | ema + (close - ema) × 2/(14+1) |
| **Peran** | **ENTRY.** Entry direction confirmation: EMA slope > 0 → trend UP (LONG). EMA slope < 0 → trend DOWN (SHORT) |
| **Consumer** | EvidenceEngine.dir_bus() — ema score; CloneEngine.observe_long/short() — dirOk check |
| **Turunan** | EMA 12 + EMA 26 → MACD |

---

### 2.6 Volume Delta

| Aspek | Detail |
|-------|--------|
| **Sumber** | `taker_buy_ratio` dari candle |
| **Formula** | 2 × takerBuyRatio - 1 |
| **Peran** | **ENTRY.** Volume delta > 0 → buying pressure (LONG). Volume delta < 0 → selling pressure (SHORT) |
| **Consumer** | EvidenceEngine.dir_bus() — vd score; CloneEngine.observe_long/short() — dirOk check |

---

### 2.7 Distance-to-ST / ATR

| Aspek | Detail |
|-------|--------|
| **Sumber** | `st`, `close`, `atr` dari PointBuilder |
| **Formula** | dist = \|close - st\|, distAtr = dist / atr |
| **Peran** | **ENTRY.** Menentukan corridor width, fee_safe check. Distance bucket: OPTIMAL(≤0.5), NEAR(≤1), EXTENDED(≤2), FAR(>2) |
| **Consumer** | CloneEngine (corridor, fee_safe), BAG (distance bucket), Academy (bucket dimension), Oracle (vector dimension) |

---

### 2.8 Trend Flip

| Aspek | Detail |
|-------|--------|
| **Sumber** | `puf`, `plf`, `trend` dari PointBuilder |
| **Formula** | close > puf (trend=-1) → TREND_FLIP_UP. close < plf (trend=1) → TREND_FLIP_DOWN |
| **Peran** | **EVENT.** Menandai perubahan arah trend |
| **Consumer** | MarketEventRecorder (TREND_FLIP event), TruthTimeline, Statistics (flip frequency), Knowledge (pattern) |

---

## 3. INDIKATOR AUTHORITY MATRIX

```
┌─────────────────────────┬───────┬──────┬───────────┬───────────┬──────────┬───────────┬───────────┐
│ INDIKATOR               │ ENTRY │ EXIT │VALIDATION │STATISTICS │KNOWLEDGE │PREDICTION │GOVERNANCE │
├─────────────────────────┼───────┼──────┼───────────┼───────────┼──────────┼───────────┼───────────┤
│ Supertrend              │   T   │  T   │     V     │     W     │    K     │    P−     │  amend    │
│ Distance-to-ST          │   S   │  —   │     V     │   W,K     │    K     │    P+     │    —      │
│ Distance-Ceiling        │   T   │  T   │     V     │     W     │    K     │    P−     │    B      │
│ Distance-Floor          │   T   │  T   │     V     │     W     │    K     │    P−     │    B      │
│ ATR                     │   T   │  T   │     —     │   W,K     │    K     │    P−     │    B      │
│ EMA                     │   T   │  —   │     V     │     S     │    K     │    P+     │    —      │
│ EMA Slope               │   T   │  —   │     —     │     W     │    K     │    P+     │    —      │
│ MACD                    │   X   │  T   │     X     │     W     │    K     │    P−     │    —      │
│ RSI                     │   X   │  T   │     —     │     W     │    K     │    P−     │    —      │
│ W%R                     │   X   │  T   │     —     │     W     │    K     │    P−     │    —      │
│ W%R Velocity            │   X   │  T   │     —     │     W     │    K     │    P−     │    B      │
│ W%R Acceleration        │   X   │  T   │     —     │     W     │    K     │    P−     │    B      │
│ Volume                  │   —   │  —   │     —     │     W     │    —     │    P−     │    —      │
│ Volume Delta            │   T   │  —   │     V     │     W     │    K     │    P+     │    —      │
│ Open Interest           │   S   │  —   │     V     │     W     │    K     │    P+     │    —      │
│ OI Delta                │   S   │  —   │     V     │     W     │    K     │    P+     │    —      │
└─────────────────────────┴───────┴──────┴───────────┴───────────┴──────────┴───────────┴───────────┘

T = Trigger/Authority   V = Validation-only   S = Strengthening
W = Witness/Behavior    K = Knowledge         P+ = Prediction contributor
P− = No prediction      X = FORBIDDEN         B = Benchmark
```

---

## 4. KOMPONEN PENDUKUNG — BAGAIMANA DIPERLAKUKAN

```
┌──────────────────────────────────────────────────────────────────────────┐
│  TRUTH LAYER — INDIKATOR + PENDUKUNG                                      │
│                                                                           │
│  PRIMARY (PointBuilder):                                                  │
│    ST, ATR, EMA, RSI, W%R, MACD, VolDelta, dist, distAtr, flip          │
│    → Dihitung SETIAP candle, state kontigu                                │
│                                                                           │
│  DERIVATIVE (dari Primary):                                               │
│    W%R Velocity = wpr - prev_wpr                                         │
│    W%R Acceleration = vel - prev_vel                                      │
│    EMA Slope = ema - prev_close                                           │
│    → Dihitung dari indikator primary, tidak butuh data tambahan           │
│                                                                           │
│  SUPPORTING (metadata, READ-ONLY):                                        │
│    Lifecycle Manager → tracking state SP                                  │
│    Timeline → query history                                               │
│    Event Recorder → record kejadian penting                               │
│    Mutation Tracker → delta candle-to-candle                              │
│    Reliability Scorer → confidence 0-1 per indikator                      │
│    Replay → playback history                                              │
│    Truth Statistics → aggregate statistics                                 │
│    → MEMBACA TruthPoint, TIDAK mengubah indikator                         │
│                                                                           │
│  CONSUMER (membaca indikator + pendukung):                                │
│    Structure → ST, color → Line, Wave                                     │
│    Evidence → RSI, W%R, MACD, EMA, VolDelta → 3 buses                    │
│    Clone → ST dir, EMA slope, VolDelta, distAtr → entry/exit             │
│    Statistics → semua indikator → distribution, correlation               │
│    Knowledge → semua → Academy, Oracle, HiveMind                          │
│    Prediction → Knowledge → Market Possibility                            │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 5. RINGKASAN

| Kategori | Komponen | Jumlah |
|----------|----------|--------|
| **Primary Indicators** | ST, ST dir, ST color, ATR, EMA, RSI, W%R, MACD | 8 |
| **Derivative Indicators** | W%R Velocity, W%R Acceleration, EMA Slope, Volume Delta | 4 |
| **Computed Metrics** | dist, distAtr, flip | 3 |
| **TOTAL INDIKATOR** | | **15** |
| **Supporting Components** | Lifecycle, Timeline, Event, Mutation, Reliability, Replay, Statistics | 7 |
| **Forbidden for Entry** | MACD (X), RSI (X), W%R (X), W%R Velocity (X), W%R Acceleration (X) | 5 |
| **Entry Authorities** | ST (T), ATR (T), EMA (T), VolDelta (T), Dist-Ceiling (T), Dist-Floor (T) | 6 |
| **Exit Only** | MACD, RSI, W%R, W%R Velocity, W%R Acceleration | 5 |
