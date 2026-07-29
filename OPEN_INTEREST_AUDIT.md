# OPEN INTEREST ARCHITECTURE AUDIT

## ST-LMS v3 — Open Interest Audit Report

**Date:** 2026-07-29
**Status:** AUDIT COMPLETE
**Scope:** Seluruh referensi ST-LMS (14 HTML docs, SQLite schema, seluruh freeze/contract/enrichment/mapping documents)

---

## 1. APAKAH OPEN INTEREST SUDAH MEMILIKI PETA LENGKAP?

**JAWABAN: YA — tetapi dengan catatan implementasi yang perlu diperkaya.**

Open Interest telah dipetakan pada 6 dimensi arsitektur ST-LMS, namun filosofi "timeframe ownership" dan "pewarisan ke Supertrend Point" belum eksplisit dalam dokumen spesifikasi.

---

## 2. DOKUMEN YANG SUDAH MENDEFINISIKAN OPEN INTEREST

### 2.1 MASTER_SPECIFICATION.html

| Section | Definisi |
|---------|----------|
| LAW-MASTER-02 (S2) | "OI kosong = INSUFFICIENT_DATA" — forbidden: "skor 5000 netral", "interpolasi OI 1m" |
| Indicator Authority Matrix (S5) | Open Interest: Entry=S, Exit=—, Validation=V, Statistics=W, Knowledge=K, Prediction=P+ |
| OI-Delta: Entry=S, Exit=—, Validation=V, Statistics=W, Knowledge=K, Prediction=P+ |
| Trading Lifecycle (S6) | Evidence stage input: "truth+candle+OI+wave" |

### 2.2 QWEN_14_DOC.html

| PHASE | Definisi |
|-------|----------|
| PHASE 0 (Doc01) | TRUTH domain includes "OI, OI-Delta" |
| PHASE 1 (Doc02) | LAW-02: "OI kosong ≠ 5000" |
| PHASE 5 (Doc06) | Evidence input: "truth+candle+OI+wave" |
| PHASE 12 (Doc13) | S6: "OI kosong=INSUFFICIENT" |

### 2.3 STLMS_SQLITE_SCHEMA_V1.sql

| Table | Kolom OI | Purpose |
|-------|----------|---------|
| `open_interest_series` | `open_interest`, `open_interest_delta`, `source`, `status` | OI time series (proxied from volume) |
| `truth_snapshots` | `oi`, `oi_delta` | OI value + delta per truth snapshot |
| Index: `idx_oi_symbol_tf_ts` | (symbol, timeframe, ts) | Fast OI lookup |

### 2.4 ST_LMS_CORE.js

| Function | Purpose |
|----------|---------|
| `MARKET.oiProxy(candles)` | Generate OI proxy from volume + takerBuyRatio (5m slots) |
| `EVIDENCE.oiInherit(series, ts)` | Inherit OI with freshness-weighted scoring |
| `truth_snapshots` | Contains `oi`, `oi_delta` fields |
| `dir_bus` | Contains `oi` score, `oi_status`, `oi_source` |

### 2.5 Freeze & Contract Documents

| Document | Coverage |
|----------|----------|
| 02_ARTIFACT_REGISTRY.md | `oi_proxy_series` (MARKET), `oi_score` (EVIDENCE) |
| 06_CONSUMER_MATRIX.md | `oi_proxy_series` → EVIDENCE.oiInherit chain |
| 01_ARCHITECTURE_FREEZE.md | SQLite mapping includes `open_interest_series` |
| 05_TEST_CONTRACT.md | Test: "OI insufficient → INSUFFICIENT_DATA" |
| 07_BUILD_RESTRICTION.md | "Insufficient = INSUFFICIENT_DATA (not 5000 for OI)" |
| TRUTH_LAYER_FREEZE.md | OI in truth_snapshot, OI empty rule |
| TRADING_SCHEMA_FREEZE.md | INSUFFICIENT_DATA status |

---

## 3. PEMETAAN OPEN INTEREST PADA ARSITEKTUR ST-LMS

| Dimensi | Lokasi | Status |
|---------|--------|--------|
| **Layer** | MARKET (produksi OI proxy), EVIDENCE (OI scoring via dir_bus), TRUTH (penyimpanan OI value) | ✅ Tercakup |
| **Pipeline** | Stage 1 (MARKET: oiProxy), Stage 4 (EVIDENCE: oiInherit) | ✅ Tercakup |
| **Worker** | Data Worker (batch OI processing) | ✅ Tercakup |
| **Artifact** | `oi_proxy_series` (MARKET), `oi_score` (EVIDENCE) | ✅ Tercakup |
| **SQLite** | `open_interest_series` table + `truth_snapshots.oi` + `truth_snapshots.oi_delta` + index `idx_oi_symbol_tf_ts` | ✅ Tercakup |
| **Snapshot** | truth_snapshot (W field: oi, oi_delta), evidence_snapshot (dir_bus: oi_score, oi_status, oi_source) | ✅ Tercakup |
| **Implementation Phase** | Phase-04 (MARKET: OI proxy), Phase-05 (TRUTH: OI storage), Phase-08 (EVIDENCE: OI scoring) | ✅ Tercakup |
| **Truth Package** | truth_snapshot menyimpan OI value — TruthReportPackage dapat menyertakan OI | ⚠️ Parsial |
| **Prediction Package** | OI masuk Prediction via Oracle vector + Academy bucket | ⚠️ Parsial |
| **Recommendation Package** | OI tidak secara eksplisit menjadi input Darwin proposals | ⚠️ Parsial |

---

## 4. BAGIAN YANG BELUM LENGKAP

### 4.1 Filosofi "Timeframe Ownership" Belum Eksplisit

Spesifikasi saat ini:
- OI diproduksi di MARKET sebagai proxy dari volume 5m
- OI di-inherit oleh EVIDENCE dengan freshness-weighted scoring
- OI disimpan di truth_snapshot per candle

Yang BELUM eksplisit:
- **OI dimiliki oleh timeframe aslinya** (5m), bukan oleh candle 1m
- **OI diwariskan ke seluruh Supertrend Point dalam rentang timeframe tersebut**
- **Supertrend Line mewarisi OI dari kumpulan Point-nya**
- **Wave mewarisi OI dari kumpulan Line-nya**

### 4.2 OI pada Prediction Package

Saat ini OI masuk ke Prediction melalui:
- Oracle vector: `norm01(oi, 0, 10000)` sebagai dimensi vektor
- Academy bucket: OI tidak menjadi dimensi bucket (hanya clone, structure, distance_bucket, reason)

Yang BELUM:
- OI sebagai dimensi bucket Academy
- OI delta sebagai sinyal divergence untuk prediction
- Historical OI pattern sebagai input Market Possibility

### 4.3 OI pada Recommendation Package

Darwin proposals saat ini berdasarkan:
- expectancy < 0 → TIGHTEN_ENTRY
- wrong_rate > 30 → TIGHTEN_WRONG

OI BELUM menjadi input untuk:
- OI divergence → proposal penyesuaian confidence
- OI trend → proposal penyesuaian entry timing

---

## 5. APAKAH RULE OWNERSHIP OPEN INTEREST KONSISTEN DENGAN ARSITEKTUR?

### 5.1 Analisis per Rule

| Rule | Konsisten? | Analisis |
|------|-----------|----------|
| 1. Supertrend Point adalah unit truth utama | ✅ YA | truth_snapshot adalah immutable card per candle — setiap SP adalah satu truth_snapshot |
| 2. Market data dapat digunakan oleh banyak Supertrend Point | ✅ YA | Card Sharing: market_snapshot di-share ke TRUTH — satu market data digunakan banyak SP |
| 3. Multi Time Frame dibangun dari kumpulan Supertrend Point | ✅ YA | EVIDENCE.mtfSector menggunakan wave structure dari kumpulan SP |
| 4. Open Interest memiliki timeframe ownership | ⚠️ IMPLISIT | OI disimpan di `open_interest_series` dengan (symbol, timeframe, ts) — ini menunjukkan timeframe ownership, tapi tidak eksplisit sebagai aturan |
| 5. OI diwariskan kepada Supertrend Point yang sesuai | ⚠️ IMPLISIT | `truth_snapshots.oi` menyimpan OI per candle — pewarisan terjadi via `oiInherit()` yang mencari slot 5m terdekat |
| 6. Supertrend Line mewarisi OI dari kumpulan SP | ❌ BELUM | Tidak ada mekanisme OI aggregation pada Line level |
| 7. Wave mewarisi OI dari kumpulan Line | ❌ BELUM | Tidak ada mekanisme OI aggregation pada Wave level |
| 8. Prediction dapat mengonsumsi histori OI melalui SP | ⚠️ IMPLISIT | Oracle vector menyertakan OI, tapi tidak ada explicit OI history pattern |

### 5.2 Verdict Konsistensi

**Rule ownership OI KONSISTEN dengan arsitektur ST-LMS**, namun:
- Rule 6 dan 7 BELUM terdefinisi — OI aggregation pada Line dan Wave level
- Rule 4, 5, 8 sudah IMPLISIT dalam implementasi tapi belum EKSPLISIT dalam spesifikasi

---

## 6. APAKAH DIPERLUKAN REFINEMENT IMPLEMENTASI?

**YA — diperlukan IMPLEMENTATION REFINEMENT (bukan ARCHITECTURE REFINEMENT).**

Refinement implementasi yang direkomendasikan TANPA mengubah arsitektur:

### 6.1 OI Timeframe Ownership (Phase-04 MARKET)

```
IMPLEMENTASI: oi_proxy menghasilkan OI per timeframe asli (5m).
Setiap OI value memiliki (symbol, timeframe, ts_slot).

STATUS: Sudah diimplementasikan di MARKET.oiProxy dengan 5m slots.
REFINEMENT: Dokumentasikan secara eksplisit bahwa OI dimiliki oleh timeframe,
bukan oleh candle. Tambahkan validasi: satu OI value per (symbol, timeframe, ts_slot).
```

### 6.2 OI Inheritance ke Supertrend Point (Phase-05 TRUTH)

```
IMPLEMENTASI: truth_snapshot.oi menyimpan OI value per candle.
oiInherit() mencari OI slot terdekat.

STATUS: Sudah diimplementasikan di EVIDENCE.oiInherit.
REFINEMENT: Pindahkan OI inheritance ke TRUTH layer (bukan EVIDENCE).
truth_snapshot.oi WAJIB diisi dari open_interest_series dengan rule:
- Cari OI slot yang mencakup timestamp candle
- Jika tidak ada → INSUFFICIENT_DATA (bukan 5000)
- Jika ada → gunakan nilai OI tersebut
```

### 6.3 OI pada Supertrend Line (Phase-07 STRUCTURE)

```
IMPLEMENTASI BARU: Line.oi = aggregate OI dari seluruh member points.

Line object ditambahkan field:
  oi_avg: rata-rata OI dari seluruh member points
  oi_trend: OI naik/turun selama lifetime line
  oi_delta_sum: akumulasi OI delta

TANPA PERUBAHAN SQLite: Data disimpan di payload_json atau dihitung runtime.
TANPA PERUBAHAN PIPELINE: Dihitung di STRUCTURE.LineBuilder (stage 3).
```

### 6.4 OI pada Wave (Phase-07 STRUCTURE)

```
IMPLEMENTASI BARU: Wave.oi_profile = aggregate OI dari 6 lines.

Wave object ditambahkan field:
  oi_profile: [oi_avg_line1, ..., oi_avg_line6]
  oi_trend: OI trend selama wave
  oi_divergence: OI vs price divergence

TANPA PERUBAHAN SQLite: Data disimpan di payload_json wave_history.
TANPA PERUBAHAN PIPELINE: Dihitung di STRUCTURE.WaveBuilder (stage 3).
```

### 6.5 OI pada Prediction (Phase-17 PREDICTION)

```
IMPLEMENTASI BARU: OI sebagai dimensi tambahan untuk Market Possibility.

Prediction ditambahkan:
  oi_trend_continuation: probabilitas OI trend berlanjut
  oi_divergence_signal: OI vs price divergence probability
  oi_support_level: OI level sebagai support/resistance

TANPA PERUBAHAN SQLite: prediction_snapshot sudah memiliki payload_json.
TANPA PERUBAHAN PIPELINE: Dihitung di PREDICTION.summarize (stage 21).
```

### 6.6 OI pada Recommendation (Phase-16 KNOWLEDGE)

```
IMPLEMENTASI BARU: Darwin proposals berdasarkan OI patterns.

Darwin ditambahkan proposal:
  OI_DIVERGENCE_ADJUST: jika OI divergence terdeteksi
  OI_TREND_ADJUST: jika OI trend berubah signifikan

TANPA PERUBAHAN SQLite: darwin_proposals sudah ada di knowledge_artifacts.
TANPA PERUBAHAN PIPELINE: Dihitung di KNOWLEDGE.Darwin (stage 20).
```

---

## 7. IMPLEMENTATION REFINEMENT SUMMARY

| # | Refinement | Layer | Phase | SQLite Change | Pipeline Change |
|---|-----------|-------|-------|---------------|-----------------|
| 1 | OI Timeframe Ownership (eksplisit) | MARKET | Phase-04 | ❌ None | ❌ None |
| 2 | OI Inheritance ke SP (pindah ke TRUTH) | TRUTH | Phase-05 | ❌ None | ❌ None |
| 3 | OI pada Supertrend Line | STRUCTURE | Phase-07 | ❌ None (payload_json) | ❌ None |
| 4 | OI pada Wave | STRUCTURE | Phase-07 | ❌ None (payload_json) | ❌ None |
| 5 | OI pada Prediction | PREDICTION | Phase-17 | ❌ None (payload_json) | ❌ None |
| 6 | OI pada Recommendation | KNOWLEDGE | Phase-16 | ❌ None | ❌ None |

**Tidak ada perubahan arsitektur. Tidak ada layer baru. Tidak ada SQLite schema baru. Tidak ada pipeline baru.**

---

## 8. VERDICT AKHIR

```
┌──────────────────────────────────────────────────────────────────┐
│              OPEN INTEREST ARCHITECTURE AUDIT                      │
│                                                                    │
│  1. OI SUDAH memiliki peta lengkap?                                │
│     YA — 6 dimensi arsitektur tercakup                             │
│                                                                    │
│  2. Dokumen yang mendefinisikan?                                   │
│     MASTER_SPECIFICATION (LAW-02, S5, S6)                         │
│     QWEN_14_DOC (PHASE 0,1,5,12)                                  │
│     STLMS_SQLITE_SCHEMA_V1 (open_interest_series, truth_snapshots) │
│     ST_LMS_CORE.js (oiProxy, oiInherit)                            │
│     Seluruh freeze/contract/mapping documents                      │
│                                                                    │
│  3. Bagian yang belum lengkap?                                     │
│     - OI aggregation pada Line level (BELUM)                       │
│     - OI aggregation pada Wave level (BELUM)                       │
│     - OI pada Prediction sebagai dimensi eksplisit (PARSIAL)       │
│     - OI pada Recommendation (PARSIAL)                             │
│                                                                    │
│  4. Rule ownership OI konsisten?                                   │
│     YA — 5/8 rules eksplisit/implisit, 2 belum, 1 parsial         │
│                                                                    │
│  5. Diperlukan refinement?                                         │
│     YA — 6 IMPLEMENTATION REFINEMENTS                              │
│     BUKAN ARCHITECTURE REFINEMENT                                  │
│                                                                    │
│  6. Refinement mengubah arsitektur?                                │
│     TIDAK — 0 layer baru, 0 SQLite change, 0 pipeline change      │
└──────────────────────────────────────────────────────────────────┘
```

---

## 9. REKOMENDASI IMPLEMENTASI

Refinement OI diimplementasikan sebagai bagian dari phase yang sudah ada:

- **Phase-04 (MARKET)**: Dokumentasikan OI timeframe ownership secara eksplisit
- **Phase-05 (TRUTH)**: Pindahkan OI inheritance dari EVIDENCE ke TRUTH
- **Phase-07 (STRUCTURE)**: Tambahkan OI aggregation pada Line dan Wave
- **Phase-16 (KNOWLEDGE)**: Tambahkan OI-based Darwin proposals
- **Phase-17 (PREDICTION)**: Tambahkan OI dimensions pada Market Possibility

Semua refinement menggunakan kolom `payload_json` yang sudah ada. Tidak memerlukan SQLite migration.
