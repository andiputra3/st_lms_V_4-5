# TRUTH LAYER ENRICHMENT — Patch 04

## ST-LMS Architecture Enrichment Patch V1

**Date:** 2026-07-28
**Status:** ENRICHMENT ANALYSIS — FROZEN
**Sources:** MASTER_SPECIFICATION.html §4, §5, ST_LMS_CORE.js (TRUTH, STRUCTURE, EVIDENCE, STATISTICS namespaces)

---

## 1. TRUTH LAYER OUTPUT — CURRENT UTILIZATION

### 1.1 Truth Snapshot Fields (W — frozen stored)

| Field | Produced By | Consumed By | Utilization |
|-------|------------|-------------|-------------|
| close | TRUTH.PointBuilder | STRUCTURE, EVIDENCE, CLONE, TRADE | ✅ FULL |
| st | TRUTH.PointBuilder | STRUCTURE (LineBuilder, CageEngine) | ✅ FULL |
| st_canon | TRUTH.PointBuilder | STRUCTURE (LineBuilder key) | ✅ FULL |
| stDir | TRUTH.PointBuilder | CLONE (entry direction), STRUCTURE (phase) | ✅ FULL |
| color | TRUTH.PointBuilder | STRUCTURE (LineBuilder, WaveBuilder) | ✅ FULL |
| atr | TRUTH.PointBuilder | STRUCTURE (CageEngine), CLONE (corridor, TP) | ✅ FULL |
| ema | TRUTH.PointBuilder | EVIDENCE (dir_bus), CLONE (dirOk) | ✅ FULL |
| ema12, ema26 | TRUTH.PointBuilder | Internal (MACD calc) | ✅ FULL |
| macd, macd_signal, macd_hist | TRUTH.PointBuilder | EVIDENCE (exit_bus HOLD-veto) | ✅ FULL |
| rsi | TRUTH.PointBuilder | EVIDENCE (exit_bus), DASHBOARD | ✅ FULL |
| wpr | TRUTH.PointBuilder | EVIDENCE (exit_bus), DASHBOARD | ✅ FULL |
| vel | TRUTH.PointBuilder | CLONE (wrong entry early) | ✅ FULL |
| acc | TRUTH.PointBuilder | EVIDENCE (exit_bus acc_signal) | ✅ FULL |
| volDelta | TRUTH.PointBuilder | EVIDENCE (dir_bus), CLONE (dirOk) | ✅ FULL |
| dist | TRUTH.PointBuilder | DASHBOARD | ⚠️ PARTIAL |
| distAtr | TRUTH.PointBuilder | CLONE (corridor), EVIDENCE (ST_DIST_VOL), KNOWLEDGE (Academy, Oracle) | ✅ FULL |
| point_status | TRUTH.PointBuilder | CLONE (warmup check) | ✅ FULL |
| flip | TRUTH.PointBuilder | DASHBOARD | ⚠️ PARTIAL |

### 1.2 Structure Snapshot Fields

| Field | Produced By | Consumed By | Utilization |
|-------|------------|-------------|-------------|
| cage{status,upper,lower,pp,rangeAtr,breakout} | STRUCTURE.CageEngine | CLONE, GRID, EVIDENCE | ✅ FULL |
| cage{upVi,lowVi,cross,pressureUp,pressureDn} | STRUCTURE.CageEngine | DASHBOARD | ⚠️ PARTIAL |
| cage{versioning} | STRUCTURE.CageEngine | DASHBOARD (versioning panel) | ⚠️ PARTIAL |
| ladder | STRUCTURE.ladder | DASHBOARD | ⚠️ PARTIAL |
| nearest{support,resistance} | STRUCTURE.nearest | CLONE (fallback SL/TP) | ✅ FULL |
| phase | STRUCTURE.phase | CLONE, DASHBOARD | ✅ FULL |
| wave | STRUCTURE.WaveBuilder | EVIDENCE (MTF), KNOWLEDGE (Academy, Oracle) | ✅ FULL |
| pending_wave | STRUCTURE.WaveBuilder | DASHBOARD | ⚠️ PARTIAL |

### 1.3 Distance Fields

| Field | Produced By | Consumed By | Utilization |
|-------|------------|-------------|-------------|
| dist | TRUTH.PointBuilder | DASHBOARD only | ⚠️ LOW |
| distAtr | TRUTH.PointBuilder | CLONE, EVIDENCE, KNOWLEDGE | ✅ FULL |
| dist_ceiling | EVIDENCE.correctionBus | CLONE (LONG: fee_safe, expected_move) | ✅ FULL |
| dist_floor | EVIDENCE.correctionBus | CLONE (SHORT: fee_safe, expected_move) | ✅ FULL |
| sdv (ST_DIST_VOL) | EVIDENCE.StDistVol | CLONE (corridor volatility) | ✅ FULL |
| p90 (ST_DIST_VOL) | EVIDENCE.StDistVol | NOT CONSUMED | ❌ UNUSED |

### 1.4 Statistics Fields

| Field | Produced By | Consumed By | Utilization |
|-------|------------|-------------|-------------|
| distance_health_hist | STATISTICS | NOT CONSUMED | ❌ UNUSED |
| fee_safe_margin_dist | STATISTICS | NOT CONSUMED | ❌ UNUSED |
| wrong_entry_dist | STATISTICS | NOT CONSUMED | ❌ UNUSED |

---

## 2. DATA YANG BELUM DIMANFAATKAN

### 2.1 dist (absolute distance-to-ST)

**Current:** Hanya ditampilkan di DASHBOARD (indicator gauge).
**Potential:** Dapat dikonsumsi oleh:
- **BAG** — mengelompokkan distance-to-ST per kondisi market
- **KNOWLEDGE (Academy)** — distance bucket untuk absolute distance (bukan hanya distAtr)
- **TRADING SCHEMA** — pullback detection (dist mengecil dalam trend = pullback)

### 2.2 p90 (ST_DIST_VOL 90th percentile)

**Current:** Tidak dikonsumsi.
**Potential:** Dapat dikonsumsi oleh:
- **CLONE** — extreme volatility threshold untuk entry delay
- **BAG** — mengelompokkan volatility extremes
- **TRADING SCHEMA** — volatility regime classification

### 2.3 cage versioning (upVi, lowVi, cross, pressureUp, pressureDn)

**Current:** Hanya ditampilkan di DASHBOARD.
**Potential:** Dapat dikonsumsi oleh:
- **CLONE** — escape path confidence (cross-version = escape detected)
- **TRADING SCHEMA** — cluster detection (multiple versions close = strong S/R)
- **BAG** — mengelompokkan versioning patterns

### 2.4 ladder (support_stepped, resistance_stepped)

**Current:** Hanya ditampilkan di DASHBOARD.
**Potential:** Dapat dikonsumsi oleh:
- **TRADING SCHEMA** — stepped ladder = trend strength confirmation
- **CLONE** — confidence adjustment (stepped = stronger trend)

### 2.5 pending_wave

**Current:** Hanya ditampilkan di DASHBOARD.
**Potential:** Dapat dikonsumsi oleh:
- **CLONE** — entry delay jika wave belum complete
- **TRADING SCHEMA** — WARMUP extension logic

### 2.6 flip events

**Current:** Hanya ditampilkan di DASHBOARD.
**Potential:** Dapat dikonsumsi oleh:
- **TRADING SCHEMA** — LONG/SHORT REVERSAL schema activation
- **BAG** — mengelompokkan flip frequency per kondisi
- **KNOWLEDGE (Academy)** — flip sebagai dimensi bucket

### 2.7 distance_health_hist, fee_safe_margin_dist, wrong_entry_dist (Statistics)

**Current:** Tidak dikonsumsi.
**Potential:** Dapat dikonsumsi oleh:
- **BAG** — mengelompokkan distance health per kondisi
- **KNOWLEDGE (Academy)** — distance sebagai dimensi bucket tambahan
- **GOVERNANCE (Darwin)** — proposal berdasarkan distance health

---

## 3. DATA YANG DAPAT DIPERKAYA

### 3.1 Truth Layer Enrichment

| Enrichment | Deskripsi | Consumer |
|-----------|-----------|----------|
| dist_trend | dist dibandingkan dengan moving average dist (apakah distance expanding/contracting) | TRADING SCHEMA |
| distAtr_trend | distAtr dibandingkan dengan moving average distAtr | CLONE, TRADING SCHEMA |
| volDelta_ma | Moving average volDelta untuk mengurangi noise | EVIDENCE (dir_bus) |
| ema_distance | |close - ema| sebagai tambahan distance metric | TRADING SCHEMA |
| flip_history | Jumlah flip dalam N candle terakhir | TRADING SCHEMA (choppiness detection) |

### 3.2 Structure Layer Enrichment

| Enrichment | Deskripsi | Consumer |
|-----------|-----------|----------|
| cage_age | Berapa lama cage sudah dalam status saat ini | TRADING SCHEMA |
| wave_sequence | Urutan wave structures (pattern recognition) | BAG, KNOWLEDGE |
| versioning_cluster | Jarak antar versions (v0, v1, v2) | TRADING SCHEMA |
| ladder_strength | Seberapa kuat ladder pattern | TRADING SCHEMA |

### 3.3 Distance Layer Enrichment

| Enrichment | Deskripsi | Consumer |
|-----------|-----------|----------|
| dist_velocity | Rate of change distAtr | CLONE (acceleration ke arah ST) |
| dist_acceleration | Rate of change dist_velocity | CLONE |
| ceiling_floor_ratio | dist_ceiling / dist_floor (asymmetry detection) | TRADING SCHEMA |
| dist_delta | dist_ceiling - dist_floor (bias detection) | TRADING SCHEMA |

---

## 4. DATA YANG DAPAT DIKONSUMSI BAG

| Data | Bag Kind | Bag Key Dimension |
|------|----------|-------------------|
| dist | behavior, market | distance bucket (absolute) |
| distAtr | behavior, market, entry, exit | distance bucket (normalized) |
| p90 (ST_DIST_VOL) | risk, market | volatility percentile |
| versioning (cross, pressure) | behavior, market | versioning pattern |
| ladder (stepped) | behavior | trend strength |
| flip events | behavior, market | flip frequency |
| pending_wave | market | wave completeness |
| distance_health_hist | risk | distance health |
| fee_safe_margin_dist | risk, entry | fee safety margin |
| wrong_entry_dist | risk, exit | wrong entry distance |
| ema_distance | behavior | EMA distance |
| flip_history | behavior, market | choppiness |
| cage_age | behavior | cage duration |
| wave_sequence | behavior, knowledge | wave pattern |
| versioning_cluster | behavior | S/R cluster |
| dist_velocity | behavior, exit | distance momentum |
| dist_acceleration | behavior, exit | distance force |
| ceiling_floor_ratio | market | price asymmetry |
| dist_delta | market | price bias |

---

## 5. DATA YANG DAPAT DIKONSUMSI KNOWLEDGE

### 5.1 Academy (bucket dimensions enrichment)

Current bucket: `clone | structure | distance_bucket | reason`

Enriched bucket: `clone | structure | distance_bucket | reason | flip | ladder_stepped | versioning_cross`

### 5.2 Oracle (vector dimensions enrichment)

Current vector: `[wave, cage, pp, ema, oi, vd, mtf, rsi, distAtr]`

Enriched vector: `[wave, cage, pp, ema, oi, vd, mtf, rsi, distAtr, dist_velocity, ceiling_floor_ratio, flip_history]`

### 5.3 HiveMind

- evidence_adj dari dist_trend dan dist_velocity
- confidence adjustment berdasarkan versioning_cross

### 5.4 Darwin

- Proposal berdasarkan distance_health_hist
- Proposal berdasarkan wrong_entry_dist

---

## 6. DATA YANG DAPAT DIKONSUMSI PREDICTION

| Data | Prediction Dimension |
|------|---------------------|
| distAtr bucket | empirical_win_rate per distance bucket |
| flip_history | choppiness impact on win_rate |
| ladder_stepped | trend strength impact on win_rate |
| versioning_cross | escape detection impact on win_rate |
| dist_velocity | momentum impact on win_rate |
| ceiling_floor_ratio | asymmetry impact on win_rate |

---

## 7. DATA YANG DAPAT DIKONSUMSI TRADING SCHEMA

| Data | Schema Application |
|------|-------------------|
| dist | Pullback detection (dist mengecil dalam trend) |
| distAtr | Volatility-adjusted pullback detection |
| p90 | Extreme volatility → entry delay |
| versioning_cross | Escape detected → confidence reduction |
| ladder_stepped | Stepped ladder → trend strength confirmation |
| pending_wave | Wave incomplete → WARMUP extension |
| flip | Reversal schema activation |
| flip_history | Choppiness → WAIT schema |
| cage_age | Cage duration → breakout probability |
| dist_velocity | Pullback momentum → entry timing |
| ceiling_floor_ratio | Asymmetry → bias toward one direction |
| dist_delta | Bias → LONG vs SHORT preference |

---

## KESIMPULAN PATCH 04

**Truth Layer Output Utilization:**

| Status | Count | Fields |
|--------|-------|--------|
| ✅ FULLY UTILIZED | 18 | close, st, stDir, color, atr, ema, macd, rsi, wpr, vel, acc, volDelta, distAtr, point_status, cage(status/upper/lower/pp/rangeAtr/breakout), nearest, phase, wave |
| ⚠️ PARTIALLY UTILIZED | 8 | dist, flip, cage(upVi/lowVi/cross/pressure/versioning), ladder, pending_wave |
| ❌ UNUSED | 4 | p90 (ST_DIST_VOL), distance_health_hist, fee_safe_margin_dist, wrong_entry_dist |

**Enrichment Opportunities:**
- 19 data points dapat dikonsumsi BAG
- Academy bucket dapat diperkaya dengan 3 dimensi tambahan
- Oracle vector dapat diperkaya dengan 3 dimensi tambahan
- 12 data points dapat dikonsumsi TRADING SCHEMA

**Tidak ada perubahan pada:** Konstitusi, spesifikasi, SQLite schema, pipeline stages, layer authority. Enrichment bersifat rekomendasi — implementasi tidak wajib.
