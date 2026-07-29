# ST-LMS v3 — PART 0: RENCANA PERBAIKAN & TRUTH LAYER AUDIT

**Date:** 2026-07-29
**Role:** Enterprise Architect + 12 Specialist Architects
**Status:** AUDIT COMPLETE — TRUTH LAYER DEEP DIVE

---

## 1. DEPENDENCY GRAPH — KOREKSI

### Dependency Graph yang Diusulkan (SALAH):

```
Market Collection → Truth → Distance → Structure → Evidence → Trade → Position
→ Snapshot → Statistics → Clone Statistics → Knowledge → Prediction
→ Trading Schema → Recommendation → Simulation → Consumer → SQLite → CLI
```

### Masalah:

1. **Snapshot setelah Position** — Snapshot adalah CROSS-CUTTING. Ia memproduksi immutable cards di SETIAP stage, bukan setelah Position.
2. **Distance sebelum Structure** — Distance membutuhkan cage (dari Structure). Harusnya Distance SETELAH Structure atau berdampingan.
3. **Clone Statistics terpisah** — Clone Statistics adalah BAGIAN dari Statistics System, bukan sistem terpisah.
4. **SQLite di akhir** — SQLite adalah FOUNDATION layer, digunakan oleh semua layer. Harusnya di awal (cross-cutting).
5. **CLI di akhir** — CLI adalah interface, bukan pipeline stage. Harusnya cross-cutting.
6. **BAG hilang** — BAG (antara Statistics dan Knowledge) tidak ada di graph.
7. **Evidence hilang** — Evidence bus tidak muncul di graph user.

### Dependency Graph yang DIBETULKAN:

```
┌──────────────────────────────────────────────────────────────────┐
│  FOUNDATION (cross-cutting, digunakan semua layer)                │
│  SQLite Foundation ───────────────────────────────────────────── │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│  SHARED PIPELINE (1× per candle)                                  │
│                                                                   │
│  MARKET COLLECTION                                                │
│      │                                                            │
│      ▼                                                            │
│  TRUTH LAYER (Supertrend Point)                                   │
│      │                                                            │
│      ├──────────────────────────┐                                 │
│      ▼                          ▼                                 │
│  STRUCTURE LAYER            DISTANCE LAYER                        │
│  (Line, Wave, Cage)         (dist, distAtr, fingerprint)         │
│      │                          │                                 │
│      └──────────┬───────────────┘                                 │
│                 ▼                                                  │
│          EVIDENCE LAYER (3 buses)                                  │
└──────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│  PER-CLONE PIPELINE (3× isolated sub-ledgers)                     │
│                                                                   │
│  CLONE LAYER (LONG/SHORT/GRID observation)                        │
│      │                                                            │
│      ▼                                                            │
│  TRADE LAYER (entry/exit markers, P&L)                            │
│      │                                                            │
│      ▼                                                            │
│  POSITION LAYER (MAE/MFE, hold, trail)                            │
└──────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│  SHARED-AGAIN PIPELINE (1× card-agnostic)                         │
│                                                                   │
│  STATISTICS SYSTEM (10 domains — Market Analyst)                  │
│      │                                                            │
│      ▼                                                            │
│  BAG SYSTEM (grouping, pattern mining, fingerprint)               │
│      │                                                            │
│      ▼                                                            │
│  KNOWLEDGE SYSTEM (7 entities)                                    │
│      │                                                            │
│      ▼                                                            │
│  PREDICTION SYSTEM (Market Possibility)                           │
│      │                                                            │
│      ▼                                                            │
│  TRADING SCHEMA SYSTEM (41 schemas)                               │
│      │                                                            │
│      ▼                                                            │
│  RECOMMENDATION SYSTEM (Market Intelligence Report)               │
│      │                                                            │
│      ▼                                                            │
│  SIMULATION SYSTEM (5 simulators)                                 │
│      │                                                            │
│      ▼                                                            │
│  GOVERNANCE SYSTEM (6 validations)                                │
│      │                                                            │
│      ▼                                                            │
│  CONSUMER SYSTEM (fund, veto, intent)                             │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│  CROSS-CUTTING SYSTEMS (berjalan di semua stage)                   │
│                                                                   │
│  SNAPSHOT SYSTEM — immutable cards di setiap stage                │
│  RUNTIME SYSTEM — monitoring, progress, ETA                       │
│  CLI SYSTEM — per-layer commands                                  │
│  REPLAY SYSTEM — timeline playback                                │
│  AUDIT SYSTEM — validation di setiap stage                        │
│  DASHBOARD SYSTEM — visualization                                 │
└──────────────────────────────────────────────────────────────────┘
```

---

## 2. TRUTH LAYER ARCHITECTURAL AUDIT

### Current State

`stlms/truth/point.py` (329 lines) — **PointBuilder** menghasilkan `TruthPoint` per candle dengan 15 indikator. Ini adalah kalkulator indikator yang sangat baik.

**Tapi Truth Layer BUKAN hanya kalkulator indikator.** Truth Layer adalah **Live Market Recorder System** — ia harus merekam, melacak, dan menyimpan seluruh perjalanan market.

### Gap Analysis

| # | Fitur | Current | Target | Gap |
|---|-------|---------|--------|-----|
| 1 | Live SP Cycle | ❌ Tidak ada | OPEN→LIVE→UPDATE→FLIP→CLOSE | CRITICAL |
| 2 | Truth Timeline | ❌ Tidak ada | Query SP per timestamp | CRITICAL |
| 3 | Market Event Recorder | ❌ Tidak ada | Trend Flip, Explosion, Mutation | CRITICAL |
| 4 | Live Market Observation | ❌ Tidak ada | Real-time SP production | HIGH |
| 5 | Truth Replay | ❌ Tidak ada | Go back to candle N | HIGH |
| 6 | Market Mutation | ❌ Tidak ada | Track SP changes candle-to-candle | HIGH |
| 7 | Live Clone Observation | ❌ Tidak ada | Clone observes SP live | MEDIUM |
| 8 | Live Statistics Observation | ❌ Tidak ada | Statistics reads SP live | MEDIUM |
| 9 | Truth Statistics | ❌ Tidak ada | Statistics about Truth itself | HIGH |
| 10 | Truth Reliability | ❌ Tidak ada | Confidence in indicator accuracy | HIGH |

---

## 3. LIVE SUPERTREND POINT CYCLE

**Sanggahan:** Saat ini SP hanya memiliki `PointStatus` (WARMUP/VALID). Itu terlalu sederhana. SP adalah unit truth — ia harus memiliki lifecycle penuh.

### 10 State yang WAJIB ada:

| # | State | Deskripsi | Kapan |
|---|-------|-----------|-------|
| 1 | **OPEN** | SP dibuat dari candle baru | Awal candle |
| 2 | **LIVE** | SP aktif, indikator dihitung | Setelah OPEN |
| 3 | **UPDATE** | SP diperbarui dengan OI, volume, event | Setelah data tambahan masuk |
| 4 | **FLIP** | Trend berubah arah | TREND_FLIP_UP/DOWN |
| 5 | **CLOSE** | SP ditutup, menjadi historis | Candle berikutnya masuk |
| 6 | **SNAPSHOT** | SP dibekukan sebagai immutable card | Setelah CLOSE |
| 7 | **STATISTICS** | Statistik SP dihitung | Setelah SNAPSHOT |
| 8 | **RECOMMENDATION** | Rekomendasi berdasarkan SP | Setelah STATISTICS |
| 9 | **REPLAY** | SP dapat di-replay | Kapan saja |
| 10 | **EXPORT** | SP dapat diekspor | Kapan saja |

### Implementasi:

```python
class SPLifecycle(str, Enum):
    OPEN = "OPEN"
    LIVE = "LIVE"
    UPDATE = "UPDATE"
    FLIP = "FLIP"
    CLOSE = "CLOSE"
    SNAPSHOT = "SNAPSHOT"
    STATISTICS = "STATISTICS"
    RECOMMENDATION = "RECOMMENDATION"
    REPLAY = "REPLAY"
    EXPORT = "EXPORT"

class TruthPoint:
    # ... existing fields ...
    lifecycle: SPLifecycle = SPLifecycle.OPEN
    lifecycle_history: list[dict] = []  # timestamp + state transition
```

**Dampak:** Tidak ada perubahan pipeline. Hanya enrichment pada TruthPoint dataclass.

---

## 4. TRUTH TIMELINE SYSTEM

**Sanggahan:** Saat ini tidak ada cara untuk query "apa SP pada candle ke-50?" atau "bagaimana RSI berubah dari candle 100 ke 200?". Truth Timeline adalah query interface untuk seluruh history SP.

### 15 Timeline yang WAJIB ada:

| # | Timeline | Data | Query Contoh |
|---|----------|------|-------------|
| 1 | Price | close, open, high, low | `timeline.price(start=100, end=200)` |
| 2 | Volume | volume, volume_delta | `timeline.volume()` |
| 3 | OI | oi_value, oi_delta | `timeline.oi()` |
| 4 | RSI | rsi | `timeline.rsi()` |
| 5 | MACD | macd, macd_signal, macd_hist | `timeline.macd()` |
| 6 | W%R | wpr, vel, acc | `timeline.wpr()` |
| 7 | Distance | dist, dist_atr | `timeline.distance()` |
| 8 | Structure | wave, cage, phase | `timeline.structure()` |
| 9 | Clone | LONG/SHORT/GRID observation | `timeline.clone("LONG")` |
| 10 | Statistics | win_rate, expectancy | `timeline.statistics()` |
| 11 | Prediction | possibilities | `timeline.prediction()` |
| 12 | Recommendation | confidence, action | `timeline.recommendation()` |
| 13 | Event | flips, explosions, mutations | `timeline.events()` |
| 14 | Mutation | SP changes candle-to-candle | `timeline.mutation()` |
| 15 | Snapshot | immutable card history | `timeline.snapshot()` |

### Implementasi:

```python
class TruthTimeline:
    def __init__(self, sp_list: list[TruthPoint]):
        self._sp = sp_list
    
    def price(self, start=0, end=None):
        return [{"ts": sp.ts, "close": sp.close, "open": sp._candle.open} for sp in self._sp[start:end]]
    
    def rsi(self, start=0, end=None):
        return [{"ts": sp.ts, "rsi": sp.rsi} for sp in self._sp[start:end]]
    # ... etc
```

**Dampak:** Tidak ada perubahan pipeline. TruthTimeline adalah query layer di atas SP list.

---

## 5. MARKET EVENT SYSTEM

**Sanggahan:** Saat ini Flip Detection ada di PointBuilder sebagai string `"TREND_FLIP_UP"`. Tapi event lain tidak direkam. Market Event harus menjadi first-class entity.

### 12 Event yang WAJIB direkam:

| # | Event | Trigger | Severity |
|---|-------|---------|----------|
| 1 | **Price Explosion** | |close - open| > 3× ATR | HIGH |
| 2 | **Volume Explosion** | volume > 3× avg_volume | HIGH |
| 3 | **OI Explosion** | |oi_delta| > 5% | HIGH |
| 4 | **Trend Flip** | TREND_FLIP_UP/DOWN | CRITICAL |
| 5 | **Structure Mutation** | wave structure berubah | HIGH |
| 6 | **Wave Mutation** | wave classification berubah | MEDIUM |
| 7 | **Distance Mutation** | dist_atr berubah > 2 bucket | MEDIUM |
| 8 | **Prediction Mutation** | dominant_bias berubah | MEDIUM |
| 9 | **Recommendation Mutation** | schema berubah | MEDIUM |
| 10 | **Market Mutation** | market phase berubah | HIGH |
| 11 | **Clone Mutation** | clone entry/exit terjadi | MEDIUM |
| 12 | **Statistics Mutation** | win_rate berubah > 10% | LOW |

### Event tambahan:
- **Gap Detection** — gap antar candle
- **Warmup Complete** — semua indikator VALID
- **Extreme RSI** — RSI > 80 atau < 20
- **Extreme W%R** — W%R > -10 atau < -90
- **MACD Crossover** — MACD cross signal line
- **Volume Divergence** — price up, volume down

### Implementasi:

```python
class MarketEvent:
    ts: int
    event_type: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    sp: TruthPoint
    detail: str

class MarketEventRecorder:
    def __init__(self):
        self.events: list[MarketEvent] = []
    
    def record(self, event_type: str, sp: TruthPoint, detail: str):
        self.events.append(MarketEvent(ts=sp.ts, event_type=event_type, ...))
```

**Dampak:** Tidak ada perubahan pipeline. MarketEventRecorder berjalan paralel dengan PointBuilder.

---

## 6. TRUTH LAYER REBUILD PROPOSAL

### Struktur Baru Truth Layer:

```
stlms/truth/
  __init__.py
  point.py           — PointBuilder (existing, dipertahankan)
  artifact.py        — TruthArtifact → truth_snapshot Card (existing)
  package.py         — TruthPackage → TruthReport (existing)
  validator.py       — TruthValidator (existing)
  consumer.py        — TruthConsumer (existing)
  
  # === BAGIAN BARU ===
  lifecycle.py       — SPLifecycle enum + state machine
  timeline.py        — TruthTimeline (15 timeline queries)
  event.py           — MarketEvent + MarketEventRecorder (12+ event types)
  mutation.py        — MutationTracker (candle-to-candle changes)
  reliability.py     — ReliabilityScorer (indicator confidence)
  statistics.py      — TruthStatistics (statistik tentang Truth sendiri)
  replay.py          — TruthReplay (query SP history)
  live.py            — LiveObserver (real-time SP production)
```

### Yang Dipertahankan:
- `point.py` — PointBuilder TIDAK diubah. Ini sudah production-quality.
- `artifact.py`, `package.py`, `validator.py`, `consumer.py` — tetap.

### Yang Ditambahkan:
- `lifecycle.py` — 10-state SP lifecycle
- `timeline.py` — 15 timeline queries
- `event.py` — MarketEventRecorder
- `mutation.py` — MutationTracker
- `reliability.py` — ReliabilityScorer
- `statistics.py` — TruthStatistics
- `replay.py` — TruthReplay
- `live.py` — LiveObserver

---

## 7. STATISTICS DEPENDENCY AUDIT

**Apakah Statistics System membutuhkan:**

| # | Dependency | Butuh? | Alasan |
|---|-----------|--------|--------|
| 1 | Truth Timeline | ✅ YES | Statistics perlu query SP history untuk distribusi |
| 2 | Live Supertrend Point | ✅ YES | Statistics membaca SP untuk indicator statistics |
| 3 | Market Event | ✅ YES | Event frequency = statistik penting |
| 4 | Clone Observation | ✅ YES | Clone statistics dari observasi |
| 5 | Distance Layer | ✅ YES | Distance statistics (bucket distribution) |
| 6 | Snapshot System | ✅ YES | Statistics membaca immutable cards |
| 7 | Market Mutation | ✅ YES | Mutation frequency = market volatility metric |
| 8 | Historical Market Behavior | ✅ YES | Semua statistik butuh data historis |
| 9 | Reliability Statistics | ✅ YES | Meta-statistik tentang akurasi |
| 10 | Replay Statistics | ✅ YES | Statistik dari replay session |

**Kesimpulan:** Statistics System membutuhkan **semua 10 dependency**. Statistics adalah konsumen universal — ia membaca dari seluruh pipeline.

---

## 8. SNAPSHOT DEPENDENCY AUDIT

**Snapshot System harus memproduksi immutable cards untuk:**

| Layer | Snapshot | Status |
|-------|----------|--------|
| MARKET | market_snapshot | ✅ Sudah |
| TRUTH | truth_snapshot | ✅ Sudah |
| DISTANCE | distance_snapshot | ❌ Belum (layer belum ada) |
| STRUCTURE | structure_snapshot | ❌ Belum |
| EVIDENCE | evidence_snapshot | ❌ Belum |
| CLONE | clone_observation | ❌ Belum |
| TRADE | trade_snapshot | ❌ Belum |
| POSITION | position_snapshot | ❌ Belum |
| STATISTICS | statistics_snapshot | ❌ Belum |
| BAG | bag_artifact | ❌ Belum |
| KNOWLEDGE | knowledge_snapshot | ❌ Belum |
| PREDICTION | prediction_snapshot | ❌ Belum |
| BENCHMARK | benchmark_snapshot | ❌ Belum |
| GOVERNANCE | config_version | ❌ Belum |

**10/14 snapshot belum diproduce sebagai immutable Card.**

---

## 9. CLONE DEPENDENCY AUDIT

**Clone System membutuhkan:**
- Truth Timeline — untuk melihat history SP sebelum entry
- Market Event — untuk tahu apakah ada explosion sebelum entry
- Distance Layer — untuk corridor dan fee_safe
- Snapshot System — untuk membaca immutable cards

**Clone System harus menghasilkan:**
- Clone observation per candle (termasuk NO_TRADE)
- Clone statistics (observation-to-entry ratio, no-entry reason distribution)
- Clone timeline (semua observasi dari waktu ke waktu)

---

## 10. RECOMMENDATION DEPENDENCY AUDIT

**Recommendation System membutuhkan:**
- Truth Timeline — untuk truth summary
- Structure — untuk cage, wave, phase
- Distance — untuk distance metrics
- Statistics — untuk confidence score
- Knowledge — untuk pattern, biography
- Prediction — untuk market possibility
- Trading Schema — untuk schema selection
- Market Event — untuk alert

**Recommendation TIDAK membuat keputusan trading.** Ia menghasilkan Market Intelligence Report.

---

## 11. MARKET MUTATION PROPOSAL

**Market Mutation = perubahan SP dari candle ke candle.**

```python
class MutationTracker:
    def track(self, prev_sp: TruthPoint, curr_sp: TruthPoint) -> dict:
        return {
            "price_change_pct": (curr_sp.close - prev_sp.close) / prev_sp.close * 100,
            "st_change": curr_sp.st - prev_sp.st,
            "atr_change_pct": (curr_sp.atr - prev_sp.atr) / prev_sp.atr * 100 if prev_sp.atr else 0,
            "rsi_change": curr_sp.rsi - prev_sp.rsi if curr_sp.rsi and prev_sp.rsi else 0,
            "wpr_change": curr_sp.wpr - prev_sp.wpr if curr_sp.wpr and prev_sp.wpr else 0,
            "macd_hist_change": curr_sp.macd_hist - prev_sp.macd_hist if curr_sp.macd_hist and prev_sp.macd_hist else 0,
            "dist_atr_change": curr_sp.dist_atr - prev_sp.dist_atr if curr_sp.dist_atr and prev_sp.dist_atr else 0,
            "flip": curr_sp.flip,
            "oi_change_pct": (curr_sp.oi_value - prev_sp.oi_value) / prev_sp.oi_value * 100 if curr_sp.oi_value and prev_sp.oi_value else 0,
        }
```

---

## 12. REPLAY SYSTEM PROPOSAL

**Truth Replay = kemampuan untuk kembali ke SP sebelumnya.**

```python
class TruthReplay:
    def __init__(self, sp_list: list[TruthPoint]):
        self._sp = sp_list
        self._cursor = len(sp_list) - 1
    
    def goto(self, index: int) -> TruthPoint:
        """Lompat ke SP tertentu"""
        self._cursor = max(0, min(index, len(self._sp) - 1))
        return self._sp[self._cursor]
    
    def step_forward(self) -> TruthPoint:
        """Maju satu SP"""
        return self.goto(self._cursor + 1)
    
    def step_back(self) -> TruthPoint:
        """Mundur satu SP"""
        return self.goto(self._cursor - 1)
    
    def replay_range(self, start: int, end: int) -> list[TruthPoint]:
        """Replay rentang SP"""
        return self._sp[start:end]
```

---

## 13. RELIABILITY SYSTEM PROPOSAL

**Reliability = seberapa percaya diri kita terhadap indikator.**

```python
class ReliabilityScorer:
    def score(self, sp: TruthPoint) -> dict:
        scores = {}
        # WARMUP → reliability rendah
        if sp.point_status == PointStatus.WARMUP:
            return {"overall": 0.3, "reason": "WARMUP"}
        
        # RSI reliability: berdasarkan sample size
        scores["rsi"] = min(1.0, sp._builder.hs_len / 30) if hasattr(sp, '_builder') else 0.8
        
        # W%R reliability: berdasarkan period completeness
        scores["wpr"] = min(1.0, sp._builder.hs_len / 14) if hasattr(sp, '_builder') else 0.8
        
        # ATR reliability: selalu tinggi setelah warmup
        scores["atr"] = 0.95
        
        # Overall: rata-rata
        scores["overall"] = sum(scores.values()) / len(scores)
        return scores
```

---

## 14. FINAL TRUTH LAYER IMPROVEMENT PROPOSAL

### Ringkasan:

| Proposal | File Baru | Impact |
|----------|-----------|--------|
| Live SP Cycle | `truth/lifecycle.py` | 10-state enum + state machine |
| Truth Timeline | `truth/timeline.py` | 15 timeline queries |
| Market Event | `truth/event.py` | 12+ event types + recorder |
| Market Mutation | `truth/mutation.py` | Candle-to-candle tracking |
| Truth Reliability | `truth/reliability.py` | Indicator confidence scoring |
| Truth Statistics | `truth/statistics.py` | Statistics about Truth |
| Truth Replay | `truth/replay.py` | SP history playback |
| Live Observer | `truth/live.py` | Real-time SP production |

### Yang TIDAK berubah:
- `point.py` — PointBuilder tetap (production-quality)
- `artifact.py`, `package.py`, `validator.py`, `consumer.py` — tetap

### Total file Truth Layer: 4 → 12

### 0 perubahan pipeline. 0 perubahan SQLite. 0 perubahan arsitektur.

---

## FINAL VERDICT

**Truth Layer saat ini adalah kalkulator indikator yang sangat baik — tapi BUKAN Live Market Recorder System.**

**8 proposal enrichment diperlukan untuk menjadikan Truth Layer sebagai Live Market Recorder:**
1. Lifecycle (10-state SP)
2. Timeline (15 query types)
3. Market Event (12+ event types)
4. Mutation (candle-to-candle tracking)
5. Reliability (indicator confidence)
6. Statistics (meta-statistics)
7. Replay (history playback)
8. Live Observer (real-time)

**0 arsitektur berubah. 0 pipeline berubah. 0 SQLite berubah.**
