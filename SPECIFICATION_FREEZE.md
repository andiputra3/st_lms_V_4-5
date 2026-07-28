# ST-LMS v3 · SPECIFICATION FREEZE
## Native HTML Market Geometry Intelligence Operating System

```
================================================================================
DOCUMENT IDENTITY
================================================================================
Title:       SPECIFICATION_FREEZE.md
Project:     ST-LMS v3 — Native HTML Market Geometry Intelligence Operating System
Version:     1.0
Status:      CONSTITUTIONALLY FROZEN — NO MODIFICATION WITHOUT GOVERNANCE AMENDMENT
Author:      ST-LMS Project
Date:        2025-07-28
Supersedes:  MASTER_SPECIFICATION.html, DOCUMENT_DEPENDENCY.html, QWEN_14_DOC.html,
             01-07_IMPLEMENTATION_AUDIT.md, ST_LMS_CORE.js (as implementation target)
On Conflict: MASTER_SPECIFICATION.html wins on content; DOCUMENT_DEPENDENCY.html wins on order
================================================================================
```

```
                              ┌──────────────────────┐
                              │  MASTER_SPECIFICATION │  ← APEX (Highest Authority)
                              │      (Sections S0–S14) │
                              └──────────┬───────────┘
                                         │
                     ┌───────────────────┼───────────────────┐
                     ▼                   ▼                   ▼
          ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
          │ DOCUMENT_       │  │ QWEN_14_DOC     │  │ 01-07_IMPL_AUDIT│
          │ DEPENDENCY      │  │ (PHASE 0–13)    │  │ (Bug Fix Report)│
          │ (Sections D0–D12)│  │                 │  │                 │
          └────────┬────────┘  └────────┬────────┘  └────────┬────────┘
                   │                    │                     │
                   └────────────────────┼─────────────────────┘
                                        │
                                        ▼
                             ┌─────────────────────┐
                             │    ST_LMS_CORE.js   │  ← Implementation Target
                             │ (842 lines, 26 mod) │
                             └─────────────────────┘
```

---

## TABLE OF CONTENTS

1. [LAW MASTER — 18 Hukum Tertinggi](#1-law-master--18-hukum-tertinggi)
2. [SOURCE OF TRUTH — Hierarki Dokumen](#2-source-of-truth--hierarki-dokumen)
3. [INDICATOR AUTHORITY MATRIX — 29 Indikator](#3-indicator-authority-matrix--29-indikator)
4. [PIPELINE RULES — 22 Tahap](#4-pipeline-rules--22-tahap)
5. [KNOWLEDGE RULES — 6 Entitas](#5-knowledge-rules--6-entitas)
6. [GOVERNANCE RULES — 3-Rem, 6 Validasi, Proposal Lifecycle, Bounded Registry](#6-governance-rules--3-rem-6-validasi-proposal-lifecycle-bounded-registry)
7. [FORBIDDEN RULES — Comprehensive List](#7-forbidden-rules--comprehensive-list)
8. [IMPLEMENTATION RULES — Platform Binding, Determinism, Storage, Workers](#8-implementation-rules--platform-binding-determinism-storage-workers)

---

## 1. LAW MASTER — 18 HUKUM TERTINGGI

*Sumber: MASTER_SPECIFICATION.html §2 | Status: FROZEN | Kekuatan: Mengikat seluruh implementasi*

Setiap hukum memiliki 4 komponen: **Nama**, **Deskripsi**, **Implementasi operasional**, **Perilaku terlarang**.
Hukum ini **tidak boleh dilunakkan** oleh dokumen turunan mana pun.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                      18 MASTER LAWS — COMPLETE INDEX                          │
├──────┬─────────────────────────┬──────────────────────────────────────────────┤
│  #   │ LAW ID                  │ SHORT DESCRIPTION                            │
├──────┼─────────────────────────┼──────────────────────────────────────────────┤
│  01  │ LAW-MASTER-01           │ DETERMINISME MUTLAK                           │
│  02  │ LAW-MASTER-02           │ KEJUJURAN DATA (NO-FAKE)                      │
│  03  │ LAW-MASTER-03           │ IMMUTABILITY CARD                             │
│  04  │ LAW-MASTER-04           │ ALIRAN UNIDIRECTIONAL                         │
│  05  │ LAW-MASTER-05           │ CARD SHARING                                  │
│  06  │ LAW-MASTER-06           │ 1 CANDLE = 3 KNOWLEDGE                        │
│  07  │ LAW-MASTER-07           │ NO-REDUCTION                                  │
│  08  │ LAW-MASTER-08           │ W%R TERBATAS                                  │
│  09  │ LAW-MASTER-09           │ FEE BERLAPIS JUJUR                            │
│  10  │ LAW-MASTER-10           │ HUKUM CAGE                                    │
│  11  │ LAW-MASTER-11           │ CLONE = RUNTIME                               │
│  12  │ LAW-MASTER-12           │ SAMPLE-GATED                                  │
│  13  │ LAW-MASTER-13           │ PREDICTION = EMPIRIS                          │
│  14  │ LAW-MASTER-14           │ HUMAN APPROVAL + BOUNDED                      │
│  15  │ LAW-MASTER-15           │ STERILNYA EVIDENCE                            │
│  16  │ LAW-MASTER-16           │ SNAPSHOT LENGKAP & IMMUTABLE                  │
│  17  │ LAW-MASTER-17           │ NATIVE-HTML BINDING                           │
│  18  │ LAW-MASTER-18           │ AUDIT MENYELURUH                              │
└──────┴─────────────────────────┴──────────────────────────────────────────────┘
```

### LAW-MASTER-01: Determinisme Mutlak
| Aspek | Detail |
|--------|--------|
| **Deskripsi** | Output identik bit-per-bit untuk input+config sama, kapan pun, di tab mana pun. |
| **IMPLEMENTASI** | Waktu dari candle; PRNG Mulberry32 seeded `ts+config_version`; tie-break deterministik; BigInt integer-tick per-aset + canonical string. |
| **FORBIDDEN** | `Date.now()`/`random` bebas di logika; float biner di representasi kebenaran. |
| **Verifikasi** | `determinismHash()` — dua run dengan seed identik → checksum card identik. |

### LAW-MASTER-02: Kejujuran Data (No-Fake)
| Aspek | Detail |
|--------|--------|
| **Deskripsi** | Sistem lebih memilih NULL+status daripada nilai netral palsu. |
| **IMPLEMENTASI** | OI kosong = `INSUFFICIENT_DATA`; wave < 6 = `PENDING_WAVE`; sample kurang = `BELUM_CUKUP`; panel kosong = `N/A`. |
| **FORBIDDEN** | Skor 5000 netral; padding wave; mock dashboard; interpolasi OI 1m. |

### LAW-MASTER-03: Immutability Card
| Aspek | Detail |
|--------|--------|
| **Deskripsi** | Setiap fakta = card beku + checksum + lineage. |
| **IMPLEMENTASI** | `Object.freeze`; update = card versi baru; audit-ID `YYYYMMDD_HHMM_KOMP_FILE_SEQ_HEX` (WIB). |
| **FORBIDDEN** | Mutasi card in-place; UUID acak. |

### LAW-MASTER-04: Aliran Unidirectional
| Aspek | Detail |
|--------|--------|
| **Deskripsi** | Data → Truth → Structure → Evidence → Clone → Sim → Knowledge → Consumer; tanpa loop mundur ke Core. |
| **IMPLEMENTASI** | Knowledge/Consumer hanya membaca card. |
| **FORBIDDEN** | Oracle/HiveMind menulis Truth/Clone; Consumer memodifikasi Core. |

```
   DATA ──► TRUTH ──► STRUCTURE ──► EVIDENCE ──► CLONE ──► SIM ──► KNOWLEDGE ──► CONSUMER
     │         │          │            │           │         │         │             │
     │         │          │            │           │         │         │             │
     └─────────┴──────────┴────────────┴───────────┴─────────┘         │             │
                                                                        │             │
                                          GOVERNANCE ◄─────────────────┘             │
                                          (only to BOUNDED params)                   │
                                                                                     │
                                          ┌──────────────────────────────────────────┘
                                          │
                                          ▼
                                     No loop back to Core-logic allowed
```

### LAW-MASTER-05: Card Sharing
| Aspek | Detail |
|--------|--------|
| **Deskripsi** | Truth/Structure/Evidence dihitung 1×/candle, di-share ke 3 clone. |
| **IMPLEMENTASI** | Tahap SHARED di luar loop clone. |
| **FORBIDDEN** | Clone menghitung geometri/indikator mentah. |

### LAW-MASTER-06: 1 Candle = 3 Knowledge
| Aspek | Detail |
|--------|--------|
| **Deskripsi** | LONG/SHORT/GRID masing-masing menulis observasi tiap closed candle. |
| **IMPLEMENTASI** | Observasi wajib walau no-trade (beralasan). |
| **FORBIDDEN** | Melewatkan observasi saat tak entry. |

### LAW-MASTER-07: No-Reduction
| Aspek | Detail |
|--------|--------|
| **Deskripsi** | Dilarang mereduksi kecerdasan ke satu skor/sinyal. |
| **IMPLEMENTASI** | MIB = pemahaman multi-lensa. |
| **FORBIDDEN** | Satu angka BUY/SELL sebagai output inti. |

### LAW-MASTER-08: W%R Terbatas
| Aspek | Detail |
|--------|--------|
| **Deskripsi** | W%R/Vel/Acc = exit/early-wrong/CERMIN; akurat hanya pasca-close. |
| **IMPLEMENTASI** | Masuk Exit Bus + CERMIN-EXIT; dead-zone bounded. |
| **FORBIDDEN** | W%R sebagai entry; W%R dalam vektor Oracle. |

### LAW-MASTER-09: Fee Berlapis Jujur
| Aspek | Detail |
|--------|--------|
| **Deskripsi** | 0.7% = `REQUIRED_MOVE`; fee murni 0.04–0.10%; WIN hanya bila net > 0; adverse-first. |
| **IMPLEMENTASI** | `required = GRID_MIN_NET + fee_murni + slip_seeded + safety`. |
| **FORBIDDEN** | 0.04% sebagai fee total; TP menang atas SL se-candle. |

```
Fee Structure:
  ┌─────────────────────────────────────────────────────────────┐
  │ REQUIRED_MOVE = GRID_MIN_NET_PCT_OF_FILL (0.50%)            │
  │               + FEE_MURNI (0.04-0.10%, maker/mixed/taker)  │
  │               + SLIP_SEEDED (0.05%)                         │
  │               + FEE_SAFETY_BUFFER_PCT (0.10%)               │
  │               ──────────────────────────────────            │
  │               ≈ 0.70% total                                 │
  │                                                             │
  │ WIN condition: net = gross - fee_murni - slip > 0           │
  │ ADVERSE-FIRST: SL & TP same candle → SL wins                │
  └─────────────────────────────────────────────────────────────┘
```

### LAW-MASTER-10: HUKUM CAGE
| Aspek | Detail |
|--------|--------|
| **Deskripsi** | 2 dinding valid ⇔ kompresi/sideway; 1 dinding ⇔ trend. |
| **IMPLEMENTASI** | Jarak seberang NULL pada trend; escape v0→v1→v2; boundary max-2 vs internal banyak. |
| **FORBIDDEN** | Kompresi dari line searah; GRID aktif di tren. |

```
  CAGE States:
  ┌──────────────────┬─────────────────────────────────────────────┐
  │ NONE             │ 1 dinding valid → trend (jarak seberang =   │
  │                  │ NULL)                                       │
  ├──────────────────┼─────────────────────────────────────────────┤
  │ VALID_COMPRESSION│ 2 dinding valid, rangeAtr ≤ CAGE_TIGHT_ATR  │
  ├──────────────────┼─────────────────────────────────────────────┤
  │ LOOSE_SIDEWAY    │ 2 dinding valid, rangeAtr ≤ CAGE_LOOSE_ATR  │
  ├──────────────────┼─────────────────────────────────────────────┤
  │ Breakout         │ SQUEEZE / IMMINENT_UP / IMMINENT_DOWN / NONE│
  └──────────────────┴─────────────────────────────────────────────┘

  Escape Path: v0 (FINAL/nearest) → v1 (2nd nearest) → v2 (3rd nearest)
  Dinding "nempel" (jarak < CAGE_WALL_MIN_DISTANCE_ATR × ATR) ditolak.
```

### LAW-MASTER-11: Clone = Runtime
| Aspek | Detail |
|--------|--------|
| **Deskripsi** | Clone adalah entitas hidup ber-ledger/ber-statistik/ber-config, bukan fungsi sinyal. |
| **IMPLEMENTASI** | 3 sub-ledger terisolasi; statistik per-clone. |
| **FORBIDDEN** | Mencampur statistik LONG/SHORT; SIDEWAY→LONG. |

### LAW-MASTER-12: Sample-Gated
| Aspek | Detail |
|--------|--------|
| **Deskripsi** | Statistik/knowledge di bawah ambang sample tidak menyatakan keyakinan. |
| **IMPLEMENTASI** | `CUKUP` iff sample ≥ 30 (ambang bounded: `SAMPLE_GATE` [30, 10, 200]). |
| **FORBIDDEN** | `win_rate` dari < ambang sebagai kebenaran. |

### LAW-MASTER-13: Prediction = Empiris
| Aspek | Detail |
|--------|--------|
| **Deskripsi** | Probabilitas = frekuensi bersyarat (Academy) + similarity (Oracle); bukan forecast. |
| **IMPLEMENTASI** | `prediction_snapshot` membungkus empiris + `calibration_error`. |
| **FORBIDDEN** | Model prediktif; P(harga) tanpa basis empiris. |

### LAW-MASTER-14: Human Approval + Bounded
| Aspek | Detail |
|--------|--------|
| **Deskripsi** | Darwin mengusulkan; WASIT menyaring; manusia memutus; nilai luar rentang = auto-reject. |
| **IMPLEMENTASI** | `BOUNDED` registry; 5-gate walk-forward paralel; `config_version` baru + rollback. |
| **FORBIDDEN** | Darwin auto-execute; mengubah batas min/max via proposal biasa. |

### LAW-MASTER-15: Sterilnya Evidence
| Aspek | Detail |
|--------|--------|
| **Deskripsi** | Evidence = saksi independen; Truth buta terhadap indikator; indikator buta terhadap geometri sebagai keputusan. |
| **IMPLEMENTASI** | 3 bus terpisah (Direction/Exit/Correction); jarak tidak masuk skor Evidence. |
| **FORBIDDEN** | Evidence menulis Truth; RSI/W%R/MACD di Direction/entry. |

```
  3 Evidence Buses (Sterile Separation):
  ┌──────────────────┬───────────────────────────────────────────┐
  │ DIRECTION BUS    │ EMA, OI, VolDelta, MTF (entry-legal)     │
  │ (dir_bus)        │ DILARANG: RSI, W%R, MACD                  │
  ├──────────────────┼───────────────────────────────────────────┤
  │ CORRECTION BUS   │ price_position, market_phase,             │
  │ (correction_bus) │ dist_ceiling, dist_floor, wave_structure, │
  │                  │ cage_status, cage_range_atr, breakout     │
  ├──────────────────┼───────────────────────────────────────────┤
  │ EXIT BUS         │ RSI, W%R, MACD_hist, HOLD-veto,          │
  │ (exit_bus)       │ vel, acc, vel_signal, acc_signal,         │
  │                  │ early_invalidation                        │
  └──────────────────┴───────────────────────────────────────────┘
```

### LAW-MASTER-16: Snapshot Lengkap & Immutable
| Aspek | Detail |
|--------|--------|
| **Deskripsi** | 10 snapshot per closed candle; deterministik, replayable, auditable. |
| **IMPLEMENTASI** | Field W beku + OD on-demand; `dependencies=[candle_id,config_version]`. |
| **FORBIDDEN** | Snapshot parsial tanpa status; turunan disimpan ganda. |

### LAW-MASTER-17: Native-HTML Binding
| Aspek | Detail |
|--------|--------|
| **Deskripsi** | Platform = browser native; translasi setia, bukan redesign filosofi. |
| **IMPLEMENTASI** | IndexedDB append-only; Web Worker dingin (mati setelah selesai); writer serial main thread; CompressionStream. |
| **FORBIDDEN** | Backend; worker menulis IndexedDB langsung; `setInterval` pemutar candle di idle. |

### LAW-MASTER-18: Audit Menyeluruh
| Aspek | Detail |
|--------|--------|
| **Deskripsi** | Setiap domain dapat diaudit: pipeline/snapshot/clone/trade/knowledge/governance. |
| **IMPLEMENTASI** | Checksum+lineage per card; Chronicle; 6 audit domain. |
| **FORBIDDEN** | Logika tanpa jejak card; keputusan tanpa dependency. |

### Post-Fix Compliance (from 01-07_IMPLEMENTATION_AUDIT.md)

```
LAW-MASTER Compliance Summary (Before → After Fix Phase 1):
┌─────────────────┬──────────┬──────────┬──────────┐
│ Law             │ Before   │ After    │ Status   │
├─────────────────┼──────────┼──────────┼──────────┤
│ LAW-01 (Det.)   │ FAIL     │ PASS     │ FIXED    │
│ LAW-02 (No-Fake)│ PASS     │ PASS     │ UNCHANGED│
│ LAW-03 (Imm.)   │ PASS     │ PASS     │ UNCHANGED│
│ LAW-04 (Uni.)   │ PASS     │ PASS     │ UNCHANGED│
│ LAW-05 (Share)  │ PASS     │ PASS     │ UNCHANGED│
│ LAW-06 (3-Know) │ PASS     │ PASS     │ UNCHANGED│
│ LAW-07 (No-Red.)│ PASS     │ PASS     │ UNCHANGED│
│ LAW-08 (W%R)    │ PASS     │ PASS     │ UNCHANGED│
│ LAW-09 (Fee)    │ FAIL     │ PASS     │ FIXED    │
│ LAW-10 (CAGE)   │ PASS     │ PASS     │ UNCHANGED│
│ LAW-11 (Clone)  │ PASS     │ PASS     │ UNCHANGED│
│ LAW-12 (Sample) │ PASS     │ PASS     │ UNCHANGED│
│ LAW-13 (Pred.)  │ PASS     │ PASS     │ UNCHANGED│
│ LAW-14 (Human)  │ PASS     │ PASS     │ UNCHANGED│
│ LAW-15 (Evid.)  │ PARTIAL  │ PASS     │ FIXED    │
│ LAW-16 (Snap.)  │ PARTIAL  │ PASS     │ FIXED    │
│ LAW-17 (Native) │ PASS     │ PASS     │ UNCHANGED│
│ LAW-18 (Audit)  │ PASS     │ PASS     │ UNCHANGED│
├─────────────────┼──────────┼──────────┼──────────┤
│ TOTAL           │ 14/18    │ 18/18    │ 100%     │
└─────────────────┴──────────┴──────────┴──────────┘
```

---

## 2. SOURCE OF TRUTH — HIERARKI DOKUMEN

*Sumber: MASTER_SPECIFICATION.html §0, DOCUMENT_DEPENDENCY.html §0–§1*

### 2.1 Document Hierarchy

```
Level 0 (APEX):
  ┌──────────────────────────────────────────┐
  │ MASTER_SPECIFICATION.html                │
  │ · 18 Master Laws (§2)                    │
  │ · 16 Frozen Constitutions (§3)           │
  │ · Market Geometry Master (§4)            │
  │ · Indicator Authority Matrix (§5)        │
  │ · Trading Lifecycle (§6)                 │
  │ · Clone Master (§7)                      │
  │ · Knowledge Master (§8)                  │
  │ · Snapshot Master (§9)                   │
  │ · Prediction Master (§10)                │
  │ · Governance Master (§11)                │
  │ · Build Stop Master (§12)                │
  │ · Implementation Checklist (§13)         │
  │ · Readiness Self-Audit (§14)             │
  └──────────────────┬───────────────────────┘
                     │ Menang pada KONFLIK ISI
                     ▼
Level 1 (BUILD GRAPH):
  ┌──────────────────────────────────────────┐
  │ DOCUMENT_DEPENDENCY.html                 │
  │ · Reading Order (§1)                     │
  │ · Document Dependency Graph (§2)         │
  │ · Feature Dependency Graph (§3)          │
  │ · Pipeline Dependency Graph (§4)         │
  │ · Clone Dependency Graph (§5)            │
  │ · Knowledge Dependency Graph (§6)        │
  │ · Snapshot Dependency Graph (§7)         │
  │ · Implementation Order (§8)              │
  │ · Build Graph PHASE 0-12 (§9)            │
  │ · Validation Order (§10)                 │
  │ · Build Stop Rule (§11)                  │
  │ · Readiness Graph (§12)                  │
  └──────────────────┬───────────────────────┘
                     │ Menang pada KONFLIK URUTAN
                     ▼
Level 2 (IMPLEMENTATION DOCUMENTS):
  ┌──────────────────────────────────────────┐
  │ QWEN_14_DOC.html (PHASE 0–13)           │
  │ · Doc01 Feature Inventory Audit          │
  │ · Doc02 Implementation Constitution      │
  │ · Doc03 Program Target & Benchmark       │
  │ · Doc04 Workspace Architecture           │
  │ · Doc05 Runtime Architecture             │
  │ · Doc06 Pipeline Architecture            │
  │ · Doc07 Market Snapshot Architecture     │
  │ · Doc08 Knowledge Architecture           │
  │ · Doc09 Simulation Architecture          │
  │ · Doc10 Replay Architecture              │
  │ · Doc11 Governance Architecture          │
  │ · Doc12 HTML OS Blueprint                │
  │ · Doc13 Implementation Plan              │
  │ · Doc14 Build Approval Report            │
  └──────────────────┬───────────────────────┘
                     │
                     ▼
Level 3 (IMPLEMENTATION TARGET):
  ┌──────────────────────────────────────────┐
  │ ST_LMS_CORE.js (842 lines, 26 modules)   │
  │ · BOOT → WORKSPACE → MARKET → TRUTH      │
  │ · STRUCTURE → EVIDENCE → FEE             │
  │ · TRADE → POSITION → CLONE_SHARED        │
  │ · LONG/SHORT/GRID CLONE                  │
  │ · STATISTICS → KNOWLEDGE                 │
  │ · ACADEMY → RIVER → ORACLE → HIVEMIND    │
  │ · DARWIN → LIBRARIAN → PREDICTION        │
  │ · REPLAY → SIMULATION → GOVERNANCE       │
  │ · CONSUMER → AUDIT → BENCHMARK           │
  │ · FINAL_VALIDATION → VIEW                │
  └──────────────────────────────────────────┘
```

### 2.2 Reading Order (Mandatory)

| # | Document | Provides | Prerequisite |
|---|----------|----------|-------------|
| 0 | **MASTER_SPECIFICATION.html** | Highest laws, matrices, snapshots, stop-rules | — (APEX) |
| 1 | **DOCUMENT_DEPENDENCY.html** | Order & dependencies | MASTER |
| 2 | Doc01 Feature Inventory Audit | 19 domains + 82 components | MASTER |
| 3 | Doc02 Implementation Constitution | 15 implementation laws + platform-binding | MASTER, Doc01 |
| 4 | Doc03 Program Target & Benchmark | PASS/FAIL targets | Doc02 |
| 5 | Doc04 Workspace Architecture | Tiered storage browser | Doc02 |
| 6 | Doc05 Runtime Architecture | Thread topology | Doc04 |
| 7 | Doc06 Pipeline Architecture | 22 stages SHARED/PER-CLONE/ON-DEMAND | Doc02, MASTER §6 |
| 8 | Doc07 Market Snapshot Architecture | 10 snapshots W/OD | Doc06, MASTER §9 |
| 9 | Doc08 Knowledge Architecture | 6 unidirectional entities | Doc07 |
| 10 | Doc09 Simulation Architecture | Sim first-class | Doc06, Doc07 |
| 11 | Doc10 Replay Architecture | 6 replay types | Doc07, Doc09 |
| 12 | Doc11 Governance Architecture | 6 validations + 3 rem | MASTER §11 |
| 13 | Doc12 HTML OS Blueprint | Module → thread → store | Doc04–11 |
| 14 | Doc13 Implementation Plan | Steps S1–S15 | Doc01–12 |
| 15 | Doc14 Build Approval Report | 15 stop-rule PASS | Doc01–13 |

### 2.3 The 16 Frozen Constitutions

| # | Constitution | Frozen Core | Reference | Status |
|---|-------------|-------------|-----------|--------|
| 01 | System Identity | Not bot/AI/scanner; geometry-OS native | §1, Doc02 | FROZEN |
| 02 | Master Implementation Law | 18 highest laws | §2 | FROZEN |
| 03 | Trading Lifecycle | 22 stages SHARED/PER-CLONE/ON-DEMAND | §6, Doc05 | FROZEN |
| 04 | Market Geometry | Supertrend/cage/wave/ladder/escape/phase/required | §4, Doc06 | FROZEN |
| 05 | Market Intelligence | HiveMind understanding; Oracle similarity; Academy empirical | §8, Doc07 | FROZEN |
| 06 | Indicator Authority | Per-role matrix per indicator | §5 | FROZEN |
| 07 | Clone | LONG/SHORT/GRID isolated runtime | §7 | FROZEN |
| 08 | Knowledge | Academy/River/Oracle/HiveMind/Darwin/Librarian unidirectional no-ML | §8, Doc07 | FROZEN |
| 09 | Prediction | Empirical + similarity; not forecast | §10 | FROZEN |
| 10 | Governance | 3-rem + bounded + 6 validations + rollback | §11, Doc10 | FROZEN |
| 11 | Snapshot | 10 snapshots W/OD immutable | §9, Doc06 | FROZEN |
| 12 | Consumer | API/Dashboard/Research/Paper/Live-adapter; live disabled default | Doc11 | FROZEN |
| 13 | Simulation | First-class; adverse-first; 4 types | Doc08 | FROZEN |
| 14 | Replay | 6 reproducible replays | Doc09 | FROZEN |
| 15 | Native HTML | IndexedDB/Worker/CompressionStream/BigInt-tick | Doc03/04 | FROZEN |
| 16 | Build | 15 build-stop-rules | §12, Doc13 | FROZEN |

### 2.4 Amendment Rules

Mengubah baris mana pun di atas = **amandemen konstitusi**: wajib proposal Darwin Kelas-B atau perubahan batas → WASIT → approval manusia ganda → `config_version`/`constitution_version` baru → tercatat Chronicle sebagai `CONSTITUTION_AMENDED`. Dokumen turunan **dilarang** melunakkan baris ini secara diam-diam.

---

## 3. INDICATOR AUTHORITY MATRIX — 29 INDIKATOR

*Sumber: MASTER_SPECIFICATION.html §5 | Status: FROZEN*

### 3.1 Legend

| Symbol | Meaning | Role |
|--------|---------|------|
| **T** | Trigger/Authority | Decision-maker for Entry/Exit |
| **V** | Validation-only | Confirms but does not trigger |
| **S** | Strengthening/Context | Adds weight, not authority |
| **W** | Behavior/Statistics Witness | Observed and recorded |
| **W,K** | Witness + Knowledge | Observed AND feeds Knowledge |
| **K** | Knowledge Material | Feeds Academy/Oracle/HiveMind |
| **B** | Benchmark Material | Used by WASIT governance |
| **P+** | Prediction contributor | Empirical probability contributor |
| **P−** | No prediction | Excluded from prediction |
| **X** | FORBIDDEN | Prohibited in that role |
| **—** | Unused | Not applicable |

### 3.2 Complete Authority Matrix (29 Indicators)

| # | Indicator / Primitive | Entry | Exit | Validation | Statistics | Knowledge | Prediction | Governance |
|---|----------------------|-------|------|------------|------------|-----------|------------|------------|
| 1 | **Supertrend** | T | T | V | W | K | P− | amend |
| 2 | **Distance-to-ST** | S | — | V | W,K | K | P+ | — |
| 3 | **Distance-Ceiling** | T | T | V | W | K | P− | B |
| 4 | **Distance-Floor** | T | T | V | W | K | P− | B |
| 5 | **Price-Position** | T | T | S | W | K | P+ | B |
| 6 | **Required-Move** | T | T | V | W | — | P− | B |
| 7 | **Wave** | S | — | — | W,K | K | P+ | — |
| 8 | **Cage** | T | T | V | W | K | P+ | B |
| 9 | **Ladder** | S | S | S | W | K | P− | — |
| 10 | **Escape-Path** | T | T | V | S | — | P− | B |
| 11 | **ATR** | T | T | — | W,K | K | P− | B |
| 12 | **EMA** | T | — | V | S | K | P+ | — |
| 13 | **MACD** | X | T | X | W | K | P− | — |
| 14 | **Open Interest** | S | — | V | W | K | P+ | — |
| 15 | **OI-Delta** | S | — | V | W | K | P+ | — |
| 16 | **Volume** | — | — | — | W | — | P− | — |
| 17 | **Volume-Delta** | T | — | V | W | K | P+ | — |
| 18 | **W%R** | X | T | — | W | K | P− | — |
| 19 | **W%R-Velocity** | X | T | — | W | K | P− | B |
| 20 | **W%R-Acceleration** | X | T | — | W | K | P− | B |
| 21 | **Adaptive-Entry-Corridor** | T | T | V | W | — | P− | B |
| 22 | **Adaptive-TP** | — | T | — | W | K | P− | B |
| 23 | **Wrong-Entry-Guard** | — | T | — | W | K | P− | B |
| 24 | **Trade-Marker** | — | — | — | sumber | sumber | P− | konteks |
| 25 | **Structure-Score** | S | — | S | W,K | K | P− | — |
| 26 | **Evidence-Score** | T | — | V | S | K | P− | — |
| 27 | **Confidence-Score** | S | — | V | W | K | P− | — |
| 28 | **Market-Phase** | S | S | S | W,K | K | P+ | — |
| 29 | **Clone-Observation-Card** | — | — | — | sumber | sumber | P− | konteks |

### 3.3 Critical Matrix Rules

| Rule | Description | Violation Consequence |
|------|-------------|----------------------|
| **R1: W%R/MACD = X at Entry** | W%R, W%R-Vel, W%R-Acc, MACD **dilarang keras** memicu/menguatkan entry | BUILD STOP (LAW-MASTER-08/15) |
| **R2: Governance = amend/B only** | Kolom Governance hanya berisi komponen ber-parameter `BOUNDED` (target WASIT) atau `amend` (konstitusional, mis. Supertrend) | BUILD STOP |
| **R3: Oracle vector exclusion** | W%R/MACD **tidak** masuk vektor Oracle | Specification violation |
| **R4: Entry Bus sterility** | Direction Bus tidak boleh mengandung RSI/W%R/MACD | BUILD STOP |
| **R5: Prediction = empirical only** | Kolom Prediction selalu bermakna empiris (dimensi bucket/vektor/similarity), bukan model | BUILD STOP (LAW-MASTER-13) |

### 3.4 Roles by Function

```
ENTRY AUTHORITIES (T = Trigger):
  Supertrend, Distance-Ceiling, Distance-Floor, Price-Position, Required-Move,
  Cage, Escape-Path, ATR, EMA, Volume-Delta, Adaptive-Entry-Corridor, Evidence-Score

ENTRY STRENGTHENERS (S = Strengthening):
  Distance-to-ST, Wave, Ladder, Open Interest, OI-Delta,
  Structure-Score, Confidence-Score, Market-Phase

ENTRY FORBIDDEN (X = Forbidden):
  MACD, W%R, W%R-Velocity, W%R-Acceleration

EXIT AUTHORITIES (T = Trigger):
  Supertrend, Distance-Ceiling, Distance-Floor, Price-Position, Required-Move,
  Cage, Escape-Path, ATR, MACD, W%R, W%R-Velocity, W%R-Acceleration,
  Adaptive-Entry-Corridor, Adaptive-TP, Wrong-Entry-Guard
```

---

## 4. PIPELINE RULES — 22 TAHAP

*Sumber: MASTER_SPECIFICATION.html §6, QWEN_14_DOC.html PHASE 5 (Doc06)*

### 4.1 Classification Legend

| Type | Description | Execution |
|------|-------------|-----------|
| **once** | Executed exactly once at system boot | 1× |
| **SHARED** | Computed once, shared to all clones | 1× per candle |
| **PER-CLONE** | Computed independently for each clone (LONG/SHORT/GRID) | 3× per candle |
| **SHARED-AGAIN** | Card-agnostic, runs after all clones complete | 1× per candle |
| **ON-DEMAND** | Not per-candle; triggered by governance/benchmark | As needed |
| **opsional** | Consumer layer; not required for core operation | Optional |

### 4.2 Complete Pipeline (22 Stages)

```
┌─────┬──────────────────────────┬───────────────┬───────────────────────────────────────────────┐
│  #  │ Stage                    │ Type          │ Input → Output                                │
├─────┼──────────────────────────┼───────────────┼───────────────────────────────────────────────┤
│  1  │ BOOT                     │ once          │ config/registry → SYSTEM_BOOT                  │
│  2  │ Market Observation       │ SHARED        │ candle mentah → market_snapshot               │
│  3  │ Truth Layer              │ SHARED        │ market_snapshot+ckpt → truth_snapshot          │
│  4  │ Structure Layer          │ SHARED        │ truth+lines → structure_snapshot               │
│  5  │ Evidence Layer           │ SHARED        │ truth+candle+OI+wave → evidence_snapshot       │
├─────┼──────────────────────────┼───────────────┼───────────────────────────────────────────────┤
│  6  │ Clone Observation        │ PER-CLONE ×3  │ snapshot+ledger → clone_observation+snapshot   │
│  7  │ Entry Validation         │ PER-CLONE     │ observasi+global → ENTRY_MARKER / no-trade     │
│  8  │ Position Management      │ PER-CLONE     │ posisi+candle+exit_bus → mae/mfe/trail update  │
│  9  │ Profit Management        │ PER-CLONE     │ unreal+ATR+exit_bus → partial/lock/trail       │
│ 10  │ Exit Validation          │ PER-CLONE     │ posisi+guard+cage → alasan exit / null         │
│ 11  │ Close Position           │ PER-CLONE     │ alasan+harga(adverse-first) → EXIT_MARKER      │
│ 12  │ Trade Marker             │ PER-CLONE     │ entry/exit candle ini → trade_snapshot         │
├─────┼──────────────────────────┼───────────────┼───────────────────────────────────────────────┤
│ 13  │ Statistics               │ SHARED-AGAIN  │ marker+snapshot → statistics_snapshot          │
│ 14  │ Knowledge (River→…)      │ SHARED-AGAIN  │ card-agnostic → knowledge_snapshot             │
│ 15  │ Benchmark                │ ON-DEMAND     │ 2 config+replay → benchmark_snapshot           │
│ 16  │ Oracle                   │ SHARED-AGAIN  │ vektor kini+historis → oracle_match            │
│ 17  │ HiveMind                 │ SHARED-AGAIN  │ artifact+oracle+evidence → market_understanding│
│ 18  │ Academy                  │ SHARED-AGAIN  │ marker+bucket → academy_artifacts              │
│ 19  │ River                    │ SHARED-AGAIN  │ seluruh card → append+index+chronicle          │
│ 20  │ Darwin                   │ SHARED-AGAIN  │ artifact+bounded → darwin_proposals            │
│ 21  │ Prediction               │ SHARED-AGAIN  │ understanding+academy+oracle → prediction_snap │
│ 22  │ Governance               │ SHARED-AGAIN  │ proposal+verdict+human → config_version        │
└─────┴──────────────────────────┴───────────────┴───────────────────────────────────────────────┘
```

### 4.3 Visual Pipeline Flow

```
BOOT (once)
  │
  ▼
┌──────────────────────────────────────────────────────────┐
│                    SHARED (1× per candle)                 │
│                                                          │
│  MARKET ──► TRUTH ──► STRUCTURE ──► EVIDENCE             │
│                                                          │
│  [DILARANG dibungkus loop clone]                         │
└──────────────────────┬───────────────────────────────────┘
                       │ Card Sharing
                       ▼
       ┌───────────────┼───────────────┐
       ▼               ▼               ▼
  ┌─────────┐    ┌─────────┐    ┌─────────┐
  │  LONG   │    │  SHORT  │    │  GRID   │
  │  CLONE  │    │  CLONE  │    │  CLONE  │
  │         │    │         │    │         │
  │ Observe │    │ Observe │    │ Observe │
  │  Entry  │    │  Entry  │    │  Entry  │
  │Position │    │Position │    │  Grid   │
  │ Profit  │    │ Profit  │    │  Eval   │
  │  Exit   │    │  Exit   │    │  Exit   │
  │  Close  │    │  Close  │    │  Close  │
  │ Marker  │    │ Marker  │    │ Marker  │
  └────┬────┘    └────┬────┘    └────┬────┘
       │              │              │
       └──────────────┼──────────────┘
                      │ Sub-ledger terisolasi
                      ▼
┌──────────────────────────────────────────────────────────┐
│              SHARED-AGAIN (1×, card-agnostic)             │
│                                                          │
│  STATISTICS → KNOWLEDGE (River/Academy/Oracle/HiveMind/  │
│               Darwin/Librarian) → PREDICTION → GOVERNANCE│
│                                                          │
│  [UNIDIRECTIONAL — no write-back to Core]                │
│                                                          │
│  ON-DEMAND: BENCHMARK (tidak per-candle)                 │
│  OPSIONAL:  CONSUMER                                     │
└──────────────────────────────────────────────────────────┘
```

### 4.4 Pipeline Invariants

| Invariant | Rule |
|-----------|------|
| **I1** | Stages 2–5 **dilarang** dibungkus loop clone (Card Sharing violation) |
| **I2** | Stages 6–12 **wajib** per-clone dengan sub-ledger terisolasi |
| **I3** | Stages 13–22 **card-agnostic** & unidirectional (no write-back to 2–12 except bounded params via 22) |
| **I4** | Stage 15 (Benchmark) **tidak** per-candle |
| **I5** | Clone **tidak** menghitung geometri/indikator mentah (Card Sharing) |
| **I6** | Knowledge/Consumer hanya **membaca** card (unidirectional) |

---

## 5. KNOWLEDGE RULES — 6 ENTITAS

*Sumber: MASTER_SPECIFICATION.html §8, QWEN_14_DOC.html PHASE 7 (Doc08)*

### 5.1 Six Knowledge Entities

```
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│                           KNOWLEDGE ENTITY SYSTEM                                           │
│                                                                                           │
│  ┌──────────┐                                                                              │
│  │  RIVER   │ ← Seluruh card → append+index+chronicle                                     │
│  │ (dasar)  │   Archivist; tidak berpikir; no-ML                                          │
│  └────┬─────┘                                                                              │
│       │                                                                                    │
│       ├────► ┌──────────┐                                                                  │
│       │      │ ACADEMY   │ ← Marker+snapshot (join on ts) → academy_artifacts             │
│       │      │           │   win_rate empiris bersyarat per (clone, structure,             │
│       │      │           │   distance_bucket, reason) — 4 DIMENSI                         │
│       │      │           │   Sample-gated; bahan CERMIN; no-ML                            │
│       │      └────┬──────┘                                                                 │
│       │           │                                                                        │
│       │      ┌────┴──────┐  ┌──────────┐                                                  │
│       │      │  ORACLE   │  │ HIVEMIND │                                                  │
│       │      │  (paralel)│  │          │                                                  │
│       │      │           │  │ Membaca: │                                                  │
│       │      │ Vektor    │  │ artifacts│                                                  │
│       │      │ kini +    │  │ + oracle │                                                  │
│       │      │ historis  │  │ + current│                                                  │
│       │      │           │  │ Evidence │                                                  │
│       │      │ Euclidean │  │ (wajib   │                                                  │
│       │      │ + tie-break│ │ dari     │                                                  │
│       │      │ terbaru   │  │ snapshot)│                                                  │
│       │      │           │  │          │                                                  │
│       │      │ Match >   │  │ Output:  │                                                  │
│       │      │ 7500      │  │ market_  │                                                  │
│       │      │           │  │ under-   │                                                  │
│       │      │ W%R/MACD  │  │ standing │                                                  │
│       │      │ NOT in    │  │          │                                                  │
│       │      │ vector    │  │ Bukan    │                                                  │
│       │      │           │  │ sinyal;  │                                                  │
│       │      │ Vektor    │  │ tak      │                                                  │
│       │      │ beku =    │  │ mengalir │                                                  │
│       │      │ versioned │  │ balik    │                                                  │
│       │      └────┬──────┘  └────┬─────┘                                                  │
│       │           │              │                                                         │
│       │           └──────┬───────┘                                                         │
│       │                  │                                                                 │
│       │                  ▼                                                                 │
│       │           ┌──────────┐                                                             │
│       │           │  DARWIN  │ ← Artifacts + bounded + PEX → darwin_proposals              │
│       │           │          │   Kelas-A (bounded) / Kelas-B (PEX)                         │
│       │           │          │   Tak auto-execute; validator tolak campur-peran             │
│       │           └────┬─────┘                                                             │
│       │                │                                                                   │
│       │           ┌────┴──────┐                                                            │
│       │           │ LIBRARIAN │ ← Artifacts → lifecycle events                             │
│       │           │           │   NEW → OBSERVATION → TRUSTED → MATURE / DEAD / DEPRECATED │
│       │           │           │   DEAD/DEPRECATED non-aktif                                │
│       │           │           │   Sample + stability gated                                 │
│       │           └──────────┘                                                             │
│       │                                                                                    │
│       └────► CHRONICLE (audit trail)                                                       │
│                                                                                           │
│  Canonical Chain: River → Academy → (Oracle ∥) → HiveMind → Darwin → Librarian → Chronicle│
└───────────────────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Entity Detail

#### ACADEMY
| Attribute | Value |
|-----------|-------|
| **Authority** | `win_rate` empiris bersyarat per `(clone, structure, distance_bucket, reason)` |
| **Lifecycle** | Tiap EXIT marker → inkremen; sample-gated |
| **Contribution** | `academy_artifacts` + bahan CERMIN |
| **Governance** | Librarian set status |
| **Limitation** | No-ML; tidak meramal |
| **Bucket key format** | `clone|structure|distance_bucket|reason` (4 dimensions) |
| **Bucket dimensions** | clone: LONG/SHORT/GRID, structure: 13 wave types, distance_bucket: WARMUP/OPTIMAL/NEAR/EXTENDED/FAR, reason: WRONG_ENTRY_EARLY/SL/TP/EXIT_BUS/etc. |

#### RIVER
| Attribute | Value |
|-----------|-------|
| **Authority** | Archivist append-only + index |
| **Lifecycle** | Terus mencatat |
| **Contribution** | Store + Chronicle |
| **Governance** | Audit write |
| **Limitation** | Tidak berpikir; no-ML |

#### ORACLE
| Attribute | Value |
|-----------|-------|
| **Authority** | Similarity Euclidean deterministik + tie-break terbaru; match > 7500 |
| **Lifecycle** | Per knowledge cycle |
| **Contribution** | `oracle_match` |
| **Governance** | Vektor beku = versioned |
| **Limitation** | W%R/MACD tidak masuk vektor |

**Oracle Frozen Vector (9 dimensions):**
```
[
  normCodeWave(wave_structure),   // 0-1 from 13 wave types
  normCodeCage(cage_status),      // 0-1 from NONE/LOOSE_SIDEWAY/VALID_COMPRESSION
  cage.pp,                        // 0-1 price position
  norm01(dir_bus.ema, 0, 10000),  // 0-1 EMA direction
  norm01(dir_bus.oi, 0, 10000),   // 0-1 Open Interest
  norm01(dir_bus.vd, 0, 10000),   // 0-1 Volume Delta
  norm01(mtf.final, 0, 9000),     // 0-1 MTF sector
  norm01(truth.rsi, 0, 100),      // 0-1 RSI
  norm01(truth.distAtr, 0, 3)     // 0-1 Distance/ATR
]
// W%R and MACD are FORBIDDEN from Oracle vector
```

#### HIVEMIND
| Attribute | Value |
|-----------|-------|
| **Authority** | Memahami (score + bias); `currentEvidence` **wajib** dari snapshot |
| **Lifecycle** | Per cycle |
| **Contribution** | `market_understanding` |
| **Governance** | — |
| **Limitation** | Bukan sinyal; tidak mengalir balik |

#### DARWIN
| Attribute | Value |
|-----------|-------|
| **Authority** | Usul mutasi Kelas-A (bounded) / Kelas-B (PEX); validator tolak campur-peran |
| **Lifecycle** | Usul → PENDING / auto-reject |
| **Contribution** | `darwin_proposals` |
| **Governance** | WASIT + human; bounded auto-reject |
| **Limitation** | Tidak auto-execute |

#### LIBRARIAN
| Attribute | Value |
|-----------|-------|
| **Authority** | Lifecycle NEW → OBS → TRUSTED → MATURE / DEAD / DEPRECATED |
| **Lifecycle** | Per evaluasi |
| **Contribution** | Lifecycle events |
| **Governance** | DEAD/DEPRECATED non-aktif |
| **Limitation** | Sample + stability gated |

**Librarian Status Thresholds:**
| Status | Sample (n) | Win Rate (wr) | Priority |
|--------|-----------|---------------|----------|
| NEW | n < 10 | any | 1st |
| DEAD | n ≥ 50 | wr < 3000 | 2nd |
| MATURE | n ≥ 30 | wr ≥ 6500 | 3rd |
| TRUSTED | n ≥ 30 | 5500 ≤ wr < 6500 | 4th |
| DEPRECATED | n ≥ 50 | 3000 ≤ wr < 4000 | 5th |
| OBSERVATION | fallback | — | last |

---

## 6. GOVERNANCE RULES — 3-REM, 6 VALIDASI, PROPOSAL LIFECYCLE, BOUNDED REGISTRY

*Sumber: MASTER_SPECIFICATION.html §11, QWEN_14_DOC.html PHASE 10 (Doc11)*

### 6.1 Three Brakes (3-Rem)

```
┌──────────────────────────────────────────────────────────────────────┐
│                         3-REM GOVERNANCE                             │
│                                                                      │
│  ┌─────────┐     ┌─────────┐     ┌─────────┐                        │
│  │ DARWIN  │────►│  WASIT  │────►│  HUMAN  │                        │
│  │ (Usul)  │     │ (Saring)│     │ (Putus) │                        │
│  │         │     │         │     │         │                        │
│  │ Kelas-A │     │ 5-gate  │     │ Approve │                        │
│  │ bounded │     │ walk-   │     │ /Reject │                        │
│  │ Kelas-B │     │ forward │     │         │                        │
│  │ PEX     │     │ paralel │     │ Approval│                        │
│  │         │     │         │     │ ganda   │                        │
│  └─────────┘     └─────────┘     └─────────┘                        │
│                                                                      │
│  ┌──────────────────────────────┐                                    │
│  │ BOUNDED REGISTRY (Auto-Reject)│ ← Rem ke-0 (otomatis)            │
│  │ Nilai luar rentang → REJECTED│                                    │
│  │ tanpa komputasi WASIT        │                                    │
│  └──────────────────────────────┘                                    │
│                                                                      │
│  ┌──────────────────────────────┐                                    │
│  │ RUNTIME (Rollback)           │ ← Rem ke-4 (setelah deploy)       │
│  │ Monitor pasca-deploy;        │                                    │
│  │ bila memburuk → rollback     │                                    │
│  │ deterministik                │                                    │
│  └──────────────────────────────┘                                    │
└──────────────────────────────────────────────────────────────────────┘
```

### 6.2 Six Mandatory Validations

| # | Validation | Checks | If Failed |
|---|-----------|--------|-----------|
| 1 | **Constitution Validation** | 15 implementation laws + authority matrix + W%R/clone/snapshot contract | BUILD STOP |
| 2 | **Proposal Validation** | bounded-check + label-peran PEX + constitutional-atom | auto-reject (OUT_OF_RANGE / VIOLATION) |
| 3 | **Authority Matrix Validation** | Component not used outside valid column (e.g. W%R ≠ entry) | BUILD STOP |
| 4 | **Build Validation** | 15 build-stop-rules + inventory complete + determinism build | BUILD STOP |
| 5 | **Runtime Validation** | Checksum card, lineage, no-race writer, sample-gate, no-mock | Card rejected / panel N/A |
| 6 | **Governance Audit** | Timeline decisions, rollback deterministic, deprecated not alive | ANOMALY event |

### 6.3 Proposal Lifecycle (4 Steps)

```
Step 1: DARWIN writes proposal
  ┌──────────────────────────────────────────┐
  │ Status: PENDING                          │
  │ OR auto REJECTED_OUT_OF_RANGE            │
  │ OR auto VIOLATION                        │
  └──────────────────┬───────────────────────┘
                     │
                     ▼
Step 2: WASIT walk-forward (parallel)
  ┌──────────────────────────────────────────┐
  │ 5 gates (G1–G5)                          │
  │ All PASS → continue                      │
  │ Any FAIL → REJECTED_BY_WASIT             │
  └──────────────────┬───────────────────────┘
                     │
                     ▼
Step 3: Human Approval
  ┌──────────────────────────────────────────┐
  │ Status: PENDING_HUMAN_APPROVAL           │
  │ Human: APPROVE or REJECT                 │
  └──────────────────┬───────────────────────┘
                     │
                     ▼
Step 4: Apply or Rollback
  ┌──────────────────────────────────────────┐
  │ APPROVE → config_version baru + audit    │
  │ ROLLBACK → tunjuk version lama           │
  │ Constitutional amendment → approval      │
  │ GANDA + Chronicle CONSTITUTION_AMENDED   │
  └──────────────────────────────────────────┘
```

### 6.4 WASIT 5-Gate Walk-Forward

| Gate | Meaning | Condition |
|------|---------|-----------|
| **G1** | Sample sufficiency | candidate exits ≥ 30 |
| **G2** | Expectancy improvement | candidate expectancy > base expectancy |
| **G3** | Worst-loss not worsening | candidate worst ≥ base worst × 1.1 (if base worst < 0) |
| **G4** | Win-rate stability | candidate win_rate ≥ base win_rate − 2 |
| **G5** | Fee-drag not increasing | candidate fee ≤ base fee + 0.001 |

All 5 gates must pass majority of folds (floor(folds/2) + 1) for verdict = PASS.

**Critical rule:** Identical config → G2 FAIL (not rubber-stamp).

### 6.5 Bounded Registry (20 Parameters)

| Parameter | Default | Min | Max |
|-----------|---------|-----|-----|
| ENTRY_OFFSET_BASE_K | 1.0 | 0.3 | 3.0 |
| ENTRY_OFFSET_MIN_ATR | 0.15 | 0.05 | 0.5 |
| ENTRY_OFFSET_MAX_CAP_PCT | 0.30 | 0.10 | 1.0 |
| WPR_VELOCITY_DEADZONE | 5 | 1 | 20 |
| WPR_ACCEL_DEADZONE | 8 | 2 | 40 |
| GRID_MIN_NET_PCT_OF_FILL | 0.50 | 0.20 | 1.5 |
| CAGE_TIGHT_ATR | 2.0 | 1.0 | 4.0 |
| CAGE_LOOSE_ATR | 4.0 | 2.0 | 8.0 |
| CAGE_WALL_MIN_DISTANCE_ATR | 0.25 | 0.10 | 0.50 |
| WRONG_ENTRY_PCT | 2.0 | 0.5 | 6.0 |
| FEE_SAFETY_BUFFER_PCT | 0.10 | 0.0 | 0.5 |
| FEE_DISCOUNT_PCT | 0.0 | 0.0 | 0.25 |
| GRID_BUY_ZONE_MAX | 0.30 | 0.10 | 0.45 |
| GRID_SELL_ZONE_MIN | 0.70 | 0.55 | 0.90 |
| GRID_MAX_FILLS_PER_SIDE | 2 | 1 | 4 |
| TP_ATR_MULT | 2.0 | 1.0 | 5.0 |
| TRAIL_ATR_MULT | 1.5 | 0.5 | 4.0 |
| TRAIL_ACTIVATE_R | 1.0 | 0.5 | 3.0 |
| PARTIAL_TP_PCT | 0.5 | 0.0 | 0.8 |
| TIME_EXIT_CANDLES | 40 | 5 | 200 |
| SAMPLE_GATE | 30 | 10 | 200 |
| ST_DIST_VOL_WINDOW | 96 | 24 | 240 |

### 6.6 Governance Authority Matrix

| Actor | Allowed | Forbidden |
|-------|---------|-----------|
| **Darwin** | Propose Kelas-A/B; read artifact+bounded | Auto-execute; change min/max bounds; touch constitutional atom |
| **WASIT** | Walk-forward parallel; 5-gate; auto-reject FAIL | Approve (filter only) |
| **Human** | Approve/reject WASIT-passed proposals | — (last brake) |
| **Bounded Registry** | Auto-reject out-of-range values | Accept insane values |
| **Runtime** | Apply config_version on boundary; deterministic rollback | Hot-swap randomly; loop back to Core-logic |

---

## 7. FORBIDDEN RULES — COMPREHENSIVE LIST

*Sumber: All specification sources — MASTER_SPECIFICATION, DOCUMENT_DEPENDENCY, QWEN_14_DOC, 01-07_AUDIT, ST_LMS_CORE.js*

### 7.1 Forbidden by LAW-MASTER (18 items)

| # | Law | Forbidden Behavior | Detection |
|---|-----|-------------------|-----------|
| F01 | LAW-01 | `Date.now()` / `Math.random()` in logic | Runtime check |
| F02 | LAW-01 | Float binary in truth representation | Canonical check |
| F03 | LAW-02 | Score 5000 neutral | Snapshot audit |
| F04 | LAW-02 | Wave padding (< 6 members) | Wave audit |
| F05 | LAW-02 | Mock dashboard values | UI audit |
| F06 | LAW-02 | OI interpolation at 1m | Evidence audit |
| F07 | LAW-03 | Mutate card in-place | Card verify |
| F08 | LAW-03 | Random UUID | ID audit |
| F09 | LAW-04 | Oracle/HiveMind writing Truth/Clone | Pipeline audit |
| F10 | LAW-04 | Consumer modifying Core | Unidirectional check |
| F11 | LAW-05 | Clone computing geometry/raw indicators | Card Sharing check |
| F12 | LAW-06 | Skipping observation when no trade | 3-obs check |
| F13 | LAW-07 | Reducing intelligence to one score/signal | MIB audit |
| F14 | LAW-08 | W%R as entry | Authority matrix check |
| F15 | LAW-08 | W%R in Oracle vector | Oracle vector check |
| F16 | LAW-09 | 0.04% as total fee | Fee check |
| F17 | LAW-09 | TP wins over SL same-candle | Adverse-first check |
| F18 | LAW-10 | Compression from same-direction lines | HUKUM CAGE check |
| F19 | LAW-10 | GRID active in trend | Grid check |
| F20 | LAW-11 | Mixing LONG/SHORT statistics | Statistics check |
| F21 | LAW-11 | SIDEWAY → LONG | Clone check |
| F22 | LAW-12 | win_rate from < threshold as truth | Sample-gate check |
| F23 | LAW-13 | Predictive model | Prediction audit |
| F24 | LAW-13 | P(price) without empirical basis | Prediction audit |
| F25 | LAW-14 | Darwin auto-execute | Governance check |
| F26 | LAW-14 | Changing min/max bounds via normal proposal | Bounded check |
| F27 | LAW-15 | Evidence writing Truth | Unidirectional check |
| F28 | LAW-15 | RSI/W%R/MACD in Direction/entry | Authority matrix check |
| F29 | LAW-16 | Partial snapshot without status | Snapshot audit |
| F30 | LAW-16 | Derivatives stored twice | Storage audit |
| F31 | LAW-17 | Backend | Platform check |
| F32 | LAW-17 | Worker writing IndexedDB directly | Runtime check |
| F33 | LAW-17 | `setInterval` candle driver at idle | Runtime check |
| F34 | LAW-18 | Logic without card trail | Audit check |
| F35 | LAW-18 | Decision without dependency | Audit check |

### 7.2 Forbidden by Constitution (16 items)

| # | Constitution | Forbidden |
|---|-------------|-----------|
| FC01 | System Identity | Being a trading bot, AI assistant, market scanner, or research tool |
| FC02 | Trading Lifecycle | Wrapping stages 2–5 inside clone loop |
| FC03 | Trading Lifecycle | Skipping observation when not entering |
| FC04 | Market Geometry | Distance determining trend/strength (only context) |
| FC05 | Market Geometry | Mixing distance-as-determiner with direction/warna |
| FC06 | Market Intelligence | ML-based prediction |
| FC07 | Indicator Authority | Any indicator outside its valid column |
| FC08 | Clone | Mixing clone statistics |
| FC09 | Clone | GRID using stDir/Direction/MTF/RSI/W%R/MACD for decisions |
| FC10 | Clone | GRID using MTF as veto |
| FC11 | Clone | GRID trailing ATR per fill |
| FC12 | Knowledge | ML-based learning |
| FC13 | Knowledge | Knowledge flowing back to Core/Clone |
| FC14 | Prediction | Forecasting price/direction from model |
| FC15 | Prediction | Hidden AI prediction (no black-box) |
| FC16 | Prediction | Unsupported prediction below sample threshold |

### 7.3 Forbidden by Build Stop (15 items)

| # | Condition | Detection |
|---|-----------|-----------|
| B01 | Specification conflict | Cross-document contradiction unresolved |
| B02 | Hidden assumption | Value without source / without NULL+status |
| B03 | Missing feature | Constitutional feature not implemented |
| B04 | Missing domain | Required domain absent from inventory |
| B05 | Missing pipeline | Lifecycle stage absent / wrong type (SHARED/PER-CLONE) |
| B06 | Missing authority matrix | Indicator used outside valid column |
| B07 | Missing market logic | corridor/TP/wrong/grid/cage not specified |
| B08 | Governance conflict | Loop back to Core / auto-execute / bounded violated |
| B09 | Constitution conflict | Violation of LAW-MASTER-01..18 |
| B10 | Undefined behavior | adverse-first/tie-break/escape/no-trade/HOLD-veto undefined |
| B11 | Undefined snapshot | Snapshot/field W-OD undefined |
| B12 | Undefined clone lifecycle | Lifecycle/3-obs/sub-ledger undefined |
| B13 | Undefined knowledge lifecycle | Librarian/unidirectional undefined |
| B14 | Undefined simulation lifecycle | 4 sim types / 5 execution laws undefined |
| B15 | Undefined implementation contract | native-binding/writer-serial undefined |

### 7.4 Forbidden by Implementation (from Audit)

| # | Forbidden | Status |
|---|-----------|--------|
| FI01 | `Date.now()` in GOVERNANCE.decide() and rollback() | FIXED (Patch 3) |
| FI02 | mkExit() wrong argument order (P&L garbled) | FIXED (Patch 1) |
| FI03 | REVERSAL_UP wave typo ("MERAHMAERAHMERAH") | FIXED (Patch 2) |
| FI04 | Academy 2-dim bucket (should be 4-dim) | FIXED (Patch 5) |
| FI05 | Librarian missing DEPRECATED status | FIXED (Patch 6) |
| FI06 | Missing correction_bus in Evidence | FIXED (Patch 4) |
| FI07 | RSI ~99 instead of 100 | KNOWN (M2) |
| FI08 | Hardcoded 60000ms gap | KNOWN (M3) |
| FI09 | cageHist orphaned state | KNOWN (M4) |
| FI10 | rapor not in freshState() | KNOWN (M5) |
| FI11 | No chronological candle sort | KNOWN (M6) |
| FI12 | Oracle self-prediction feedback | KNOWN (M7) |
| FI13 | CERMIN fallback 5000 arbitrary | KNOWN (M8) |
| FI14 | DARWIN no .id field | KNOWN (M9) |
| FI15 | FEE grid-specific param for all | KNOWN (M10) |
| FI16 | WASIT G1 aggregate vs per-fold | KNOWN (M11) |
| FI17 | rollback() doesn't clear log | KNOWN (M12) |
| FI18 | Constitution gate non-deterministic | KNOWN (M13) |
| FI19 | TIME_EXIT always true for losers | KNOWN (M14) |

### 7.5 Forbidden Dependency Cycles

```
FORBIDDEN CYCLE (BUILD STOP):
  KNOWLEDGE ──► TRUTH/STRUCTURE/EVIDENCE/CLONE-logic

ALLOWED CYCLE (only path):
  GOVERNANCE ──► BOUNDED parameters (Kelas-A) & PEX (Kelas-B via WASIT)
```

---

## 8. IMPLEMENTATION RULES — PLATFORM BINDING, DETERMINISM, STORAGE, WORKERS

*Sumber: QWEN_14_DOC.html PHASE 1–4 (Doc02–05), ST_LMS_CORE.js*

### 8.1 Platform Binding (Native-HTML)

```
┌──────────────────────────────────────────────────────────────────┐
│                   PLATFORM TRANSLATION MAP                       │
│                                                                  │
│  Constitutional Concept  →  Browser-Native Implementation        │
│  ───────────────────────────────────────────────────────────────│
│  SQLite                  →  IndexedDB (append-only card store)   │
│  ProcessPool             →  Web Worker (cold jobs)               │
│  File LZMA               →  CompressionStream + IndexedDB blob   │
│  Float                   →  BigInt integer-tick per-asset (hot)  │
│                             + canonical string (audit)           │
│  PRNG Mulberry32         →  JavaScript-native (no change)        │
│                                                                  │
│  THIS IS PLATFORM-BINDING, NOT PHILOSOPHY REDESIGN               │
│  Constitutional authority/lifecycle/authority matrix UNCHANGED   │
└──────────────────────────────────────────────────────────────────┘
```

### 8.2 Determinism Contract

| Rule | Implementation |
|------|---------------|
| **PRNG** | Mulberry32 seeded `ts + config_version` |
| **Time** | From candle timestamp, NOT `Date.now()` |
| **Tie-break** | Deterministic (alphabetical/canonical sort) |
| **Canonical representation** | `canon(value, precision)` → fixed-decimal string |
| **Integer-tick** | `toTick(value, symbol)` → BigInt for hot path |
| **No `Math.random()`** | Only PRNG in logic |
| **No `Date.now()`** | In logic (allowed in UI clock only) |
| **Verification** | `determinismHash()` → two runs same seed = identical checksums |

### 8.3 Storage Architecture (Tiered)

```
┌──────────┬─────────────────┬─────────────────────────────────────┐
│  Tier    │  Media           │  Content                            │
├──────────┼─────────────────┼─────────────────────────────────────┤
│  L1 Hot  │  JS memory       │  State builder, clone positions,    │
│          │  (per symbol)    │  current candle, grid_fills         │
│          │                  │  (few KB; discarded on idle)        │
├──────────┼─────────────────┼─────────────────────────────────────┤
│  L2 Warm │  IndexedDB       │  Enriched 7h, materialized rapor,   │
│          │  "warm"          │  active config                      │
│          │                  │  (fast panel access)                │
├──────────┼─────────────────┼─────────────────────────────────────┤
│  L3 Cold │  IndexedDB       │  Card history > 7h, markers,        │
│          │  "cold" + blob   │  snapshots                          │
│          │                  │  (CompressionStream on write)       │
├──────────┼─────────────────┼─────────────────────────────────────┤
│  L4 Arch │  IndexedDB       │  Old runs, raw compressed fixtures  │
│          │  "archive"/export│  (export .json.gz / .lzma)          │
├──────────┼─────────────────┼─────────────────────────────────────┤
│  L5 Evict│  —               │  > retention                        │
│          │                  │  (deterministic deletion)           │
└──────────┴─────────────────┴─────────────────────────────────────┘

Object Stores:
  cards (PK=entity_id, idx: type+ts, config+ts)
  config_state
  checkpoints (per symbol: last_processed_1m + indicator state)
  governance (proposals + decisions)
  audit_log
  runs
```

### 8.4 Thread Topology (Worker Architecture)

```
┌────────────────────────────────────────────────────────────────────────────┐
│                          THREAD TOPOLOGY                                    │
│                                                                            │
│  ┌──────────────────────────────────────────────────────────────────┐     │
│  │ MAIN THREAD (hot monolith)                                        │     │
│  │ · BOOT, event loop, Truth/Structure/Evidence/Clone per-candle     │     │
│  │ · Sequential (state continuity: EMA/ATR/positions)                │     │
│  │ · IndexedDB writer SERIAL (single writer = zero race)             │     │
│  │ · UI render, WIB clock                                            │     │
│  └────────────────────────────┬─────────────────────────────────────┘     │
│                               │ postMessage                                │
│           ┌───────────────────┼───────────────────┐                       │
│           ▼                   ▼                   ▼                        │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                    │
│  │ Worker·Data │    │Worker·Knowl │    │Worker·Bench │                    │
│  │             │    │             │    │             │                    │
│  │ Bootstrap   │    │ Academy     │    │ WASIT walk- │                    │
│  │ batch       │    │ batch       │    │ forward     │                    │
│  │ Derived TF  │    │ Oracle      │    │ base & cand │                    │
│  │ aggregation │    │ similarity  │    │ PARALLEL    │                    │
│  │ Gap-repair  │    │ Darwin      │    │ (2 sub-task)│                    │
│  │             │    │ proposals   │    │             │                    │
│  │ I/O-bound   │    │ Librarian   │    │ Multi-core  │                    │
│  │             │    │             │    │             │                    │
│  │ Mati setelah│    │ CPU-bound   │    │ Mati setelah│                    │
│  │ batch       │    │ jarang      │    │ selesai     │                    │
│  │             │    │ Mati setelah│    │             │                    │
│  │             │    │ selesai     │    │             │                    │
│  └─────────────┘    └─────────────┘    └─────────────┘                    │
│                                                                            │
│  ┌─────────────┐                                                          │
│  │Worker·Replay│                                                          │
│  │             │                                                          │
│  │ Replay      │                                                          │
│  │ panjang     │                                                          │
│  │ per simbol  │                                                          │
│  │ (paralel    │                                                          │
│  │ antar-      │                                                          │
│  │ simbol)     │                                                          │
│  └─────────────┘                                                          │
└────────────────────────────────────────────────────────────────────────────┘

FORBIDDEN:
  · Worker writing IndexedDB directly (must postMessage to main)
  · Parallelizing Truth/Structure/Evidence/Clone per-candle for one symbol
    (breaks EMA/ATR continuity)
  · setInterval candle driver at idle (system is demand/replay-driven)

ALLOWED PARALLELISM:
  · Across symbols
  · Base vs candidate (WASIT)
  · Batch knowledge jobs
```

### 8.5 Implementation Order (S1–S15)

| Step | Builds | Honors |
|------|--------|--------|
| **S1** | Bedrock: decimal(int-tick+canonical), id, wib, hash, prng, lifecycle, card, validator, bus, bounded, governor, store(IndexedDB writer serial) | LAW-01/03/17 |
| **S2** | BOOT + Workspace + Checkpoint + Config | LAW-17 |
| **S3** | MARKET (data.worker, hygiene, derived, cascade, gap) | LAW-02 |
| **S4** | TRUTH (point→line→slope→wave→versioning→validation→flip) | LAW-08/15, HUKUM wave |
| **S5** | STRUCTURE (cage+wall+ladder+nearest+cluster) | HUKUM CAGE |
| **S6** | EVIDENCE (3-bus+oi+voldelta+mtf+maxscore) | LAW-08/15 |
| **S7** | CLONE + TRADE + POSITION + GRID (3 ledger, orchestrator, grid_eval) | LAW-05/06/11, adverse-first |
| **S8** | SIM + REPLAY (6 replay) | LAW-09/16 |
| **S9** | STATISTICS + KNOWLEDGE (river→academy→oracle→hivemind→darwin→librarian→cermin) | LAW-04/12/13 |
| **S10** | BENCHMARK (wasit worker parallel) | LAW-14 |
| **S11** | PREDICTION (empirical) | LAW-13 |
| **S12** | GOVERNANCE (6 validations + workflow + rollback) | LAW-14 |
| **S13** | CONSUMER (fund/veto/intent/simplugin/liveadapter-off) + API internal | Consumer const. |
| **S14** | AUDIT + VISUALIZATION (5 viewer) | LAW-18, no-mock |
| **S15** | Runtime/Build/Constitution final validation → BUILD_APPROVAL | 15 stop-rule PASS |

### 8.6 10 Immutable Snapshots

| # | Snapshot | Producer | Type | Key Fields |
|---|----------|----------|------|------------|
| 1 | **Market** | MARKET | W | ts, symbol, tf, OHLCV, taker_buy_ratio, data_status, gap_flag, wib_iso |
| 2 | **Truth** | TRUTH | W | close, st, stDir, color, atr, ema, macd_hist, dist, distAtr, rsi, wpr, point_status |
| 3 | **Structure** | STRUCTURE | W/OD | cage{status,upper,lower,pp,rangeAtr,breakout}, ladder, nearest, wave, phase |
| 4 | **Evidence** | EVIDENCE | W | dir_bus, exit_bus, correction_bus, mtf, max_score, data_quality |
| 5 | **Clone** | CLONE ×3 | W | per_clone{clone_id,bias,observation,open_position,grid_fills} |
| 6 | **Trade** | SIM | W | markers[{kind,clone,side,reason,entry,exit,gross,fee,slip,net,result,mae,mfe,hold}] |
| 7 | **Statistics** | STATISTICS | OD | per_clone{sample,win_rate_net,expectancy,pf,mae,mfe,fee_drag,wrong_rate} |
| 8 | **Knowledge** | KNOWLEDGE | W | academy_artifacts, oracle_match, hivemind, cermin, librarian, darwin_proposals |
| 9 | **Benchmark** | BENCHMARK | OD | param, base, cand, folds, gates{G1..G5}, per_fold, verdict (on-demand only) |
| 10 | **Prediction** | PREDICTION | W/OD | intelligence_score, dominant_bias, empirical_win_rate, similarity_score, no_model:true |

**Snapshot Rules:**
- W = Stored frozen (immutable once written)
- OD = On-demand (deterministic from frozen source; not stored to prevent drift)
- Only from CLOSED candles (PROVISIONAL rejected)
- Benchmark absent on normal candles (on-demand only)
- Prediction **dilarang** containing predictive model output
- Adding/removing snapshot fields = constitutional amendment (§3)

### 8.7 Feature Inventory (19 Domains + 82 Core Components)

```
┌───────────────────────────────────────────────────────────────────┐
│ 01 BOOT         Runtime/Resource/Configuration/Workspace/         │
│                 Checkpoint Manager                                │
│ 02 MARKET       Market Data Layer, Market Snapshot Engine         │
│ 03 TRUTH        Supertrend, Distance-to-ST, EMA, ATR, Volume,     │
│                 OI, OI-Delta, W%R, W%R-Vel, W%R-Acc              │
│ 04 STRUCTURE    Wave, Cage, Support, Resistance, Ladder,          │
│                 Escape Path, Price Position, Dist-Ceiling,        │
│                 Dist-Floor, Market Phase                          │
│ 05 EVIDENCE     Direction Bus, Exit Bus, Correction Bus,          │
│                 Evidence/Max/Confidence Score                     │
│ 06 CLONE        LONG/SHORT/GRID, Observation Card, Statistics,    │
│                 Benchmark, Simulation                             │
│ 07 TRADE        Adaptive Entry Corridor, Adaptive TP,             │
│                 Wrong Entry Guard, Trade Marker                   │
│ 08 POSITION     Mgmt, Profit Lock, Trailing, Breakeven,           │
│                 Forced/Emergency Exit, Risk Validation,           │
│                 Liquidation Avoidance                             │
│ 09 GRID         Boundary, Fee-Safe, Breakout-NONE,                │
│                 Entry/Exit/Validation, Range Validation, Spacing  │
│ 10 STATISTICS   Market/Trade/Clone Statistics                     │
│ 11 KNOWLEDGE    Academy, River, Oracle, HiveMind, Darwin,         │
│                 Librarian                                         │
│ 12 PREDICTION   Historical Similarity, Market Probability,        │
│                 Market Intelligence                               │
│ 13 BENCHMARK    Clone/Trade/Market Benchmark (WASIT 5-gate)       │
│ 14 SIMULATION   Historical/Live/Strategy/Clone Simulation         │
│ 15 REPLAY       Candle/Snapshot/Trade/Clone/Knowledge/            │
│                 Governance Replay                                 │
│ 16 GOVERNANCE   Authority Matrix, Proposal Engine,                │
│                 Constitution/Build/Runtime Validation,            │
│                 Governance Audit                                  │
│ 17 CONSUMER     API/Dashboard/Research/Paper/Live-Adapter Layer   │
│ 18 AUDIT        Pipeline/Snapshot/Clone/Trade/Knowledge/          │
│                 Governance Audit                                  │
│ 19 VISUALIZATION Geometry/Clone/Trade/Replay/Knowledge Viewer     │
└───────────────────────────────────────────────────────────────────┘
```

### 8.8 Final Audit Verdict (from 01-07_IMPLEMENTATION_AUDIT.md)

```
================================================================================
FINAL AUDIT RESULT: ALL CHECKS PASSED

- Specification Compliance: 100% (was 78%)
- Build Stop Rules: 15/15 PASS (was 9/15)
- LAW-MASTER Compliance: 18/18 (was 14/18)
- Pipeline: 100% (was 95%)
- Clone: 100% (was 98%)
- Knowledge: 100% (was 90%)
- Trading: 100% (was 90%)
- Governance: 100% (was 92%)
- Determinism: 100% (was 83%)

7 bugs fixed: 2 CRITICAL, 4 HIGH, 1 MEDIUM
0 regressions introduced
21 non-critical bugs remain (out of scope for this phase)

BUILD CAN NOW PROCEED TO NEXT PHASE.
================================================================================
```

---

## APPENDIX A: WAVE STRUCTURE CLASSIFICATION (13 Types)

| # | Structure | Condition | MTF Sector |
|---|-----------|-----------|------------|
| 1 | STRONG_ACCUMULATION | g ≥ 5 | BULLISH_TREND (8500) |
| 2 | STRONG_DISTRIBUTION | r ≥ 5 | BEARISH_TREND (8500) |
| 3 | REVERSAL_UP | 3 MERAH + HIJAU last | REVERSAL_UP (6500) |
| 4 | REVERSAL_DOWN | 3 HIJAU + MERAH last | REVERSAL_DOWN (6500) |
| 5 | EXHAUSTION_UP | g ≥ 4, last MERAH | EXHAUSTION (5500) |
| 6 | EXHAUSTION_DOWN | r ≥ 4, last HIJAU | EXHAUSTION (5500) |
| 7 | CONFIRMED_RANGE | alt ≥ 4 | RANGE (7500) |
| 8 | RANGE_EXPANDING | range expanding | RANGE (6500) |
| 9 | RANGE_COMPRESSING | range compressing | COMPRESSION (7000) |
| 10 | CONTINUATION_UP | g ≥ 3, r = 0 | BULLISH_TREND (7000) |
| 11 | CONTINUATION_DOWN | r ≥ 3, g = 0 | BEARISH_TREND (7000) |
| 12 | SIDEWAY | g ≥ 2, r ≥ 2 | RANGE (7000) |
| 13 | CHAOS | default | CHAOS (3000) |

---

## APPENDIX B: LONG/SHORT CLONE AUTHORITY

### LONG Clone
| Aspect | Provision |
|--------|-----------|
| **Entry authority** | stDir = +1 ∧ dir_ok(EMA-slope > 0 ∧ vd > 0) ∧ corridor.inZone ∧ fee_safe(dist_ceiling ≥ required) ∧ global_ok ∧ open == null |
| **Exit authority** | SL = floor; TP = min(ceiling, cage.upper, entry + TP_ATR·ATR); trailing ATR; wrong-entry(floor breach/adv/vel); hold-veto |
| **Forbidden** | Reading Oracle/HiveMind directly; writing Truth; entry when fee-unsafe |

### SHORT Clone (mirror)
| Aspect | Provision |
|--------|-----------|
| **Entry authority** | stDir = −1 ∧ dir_ok(EMA-slope < 0 ∧ vd < 0) ∧ corridor.inZone ∧ fee_safe(dist_floor ≥ required) ∧ global_ok ∧ open == null |
| **Exit authority** | SL = ceiling; TP = max(floor, cage.lower, entry − TP_ATR·ATR); trailing ATR; wrong-entry(ceiling breach/adv/vel); hold-veto |
| **Forbidden** | Same as LONG (mirrored) |

### GRID Clone
| Aspect | Provision |
|--------|-----------|
| **Entry authority** | cage_valid ∧ fee_safe(width ≥ 3·required) ∧ breakout_none ∧ pp ∈ {BUY,SELL}_ZONE ∧ fills_per_side < max |
| **Exit authority** | GRID_TP(prof ≥ required); RANGE_BREAK(breakout opposite); WRONG_ENTRY(adv ≥ WRONG_PCT); stop-all when ¬cage_valid |
| **Forbidden** | Active in trend (cage NONE); MTF as veto; trailing ATR per fill |

---

## APPENDIX C: FROZEN ORACLE VECTOR DIMENSIONS

```javascript
// Frozen Oracle Vector (9 dimensions)
// Changing this vector = config_version baru (Governance amendment)

var ORACLE_VECTOR = [
  normCodeWave(snap.structure.wave),    // [0] Wave structure → 0-1
  normCodeCage(cage.status),            // [1] Cage status → 0-1
  cage.pp,                              // [2] Price position → 0-1
  norm01(dir_bus.ema, 0, 10000),        // [3] EMA direction → 0-1
  norm01(dir_bus.oi, 0, 10000),         // [4] OI score → 0-1
  norm01(dir_bus.vd, 0, 10000),         // [5] Volume delta → 0-1
  norm01(mtf.final, 0, 9000),           // [6] MTF sector → 0-1
  norm01(truth.rsi, 0, 100),            // [7] RSI → 0-1
  norm01(truth.distAtr, 0, 3)           // [8] Distance/ATR → 0-1
];

// FORBIDDEN in vector: W%R, MACD (LAW-MASTER-08/15)
// normCodeWave: idx / 12 (from 13 WAVE_STRUCTS)
// normCodeCage: VALID_COMPRESSION=1, LOOSE_SIDEWAY=0.66, NONE=0, else=0.33
```

---

## APPENDIX D: FROZEN AUDIT-ID FORMAT

```
YYYYMMDD_HHMM_KOMP_FILE_SEQ_HEX
│       │    │    │    │   │
│       │    │    │    │   └─ SHA-256 first 8 chars (uppercase)
│       │    │    │    └───── Sequence number (6-digit, padded)
│       │    │    └────────── Source file (max 12 chars)
│       │    └─────────────── Component name (max 12 chars)
│       └──────────────────── WIB time (hours + minutes)
└──────────────────────────── WIB date (year + month + day)

Example: 20250728_1430_MARKET_SNAP_OS_000001_A3F2B9C1
```

---

## APPENDIX E: DOCUMENT CROSS-REFERENCE MAP

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ SPECIFICATION_FREEZE.md Section  →  Source Document & Section               │
├──────────────────────────────────────────────────────────────────────────────┤
│ §1 LAW MASTER (18 Laws)          →  MASTER_SPECIFICATION §2                  │
│ §2 SOURCE OF TRUTH               →  MASTER_SPECIFICATION §0, §3              │
│                                  →  DOCUMENT_DEPENDENCY §0, §1               │
│ §3 INDICATOR AUTHORITY MATRIX    →  MASTER_SPECIFICATION §5                  │
│ §4 PIPELINE RULES (22 stages)    →  MASTER_SPECIFICATION §6                  │
│                                  →  QWEN_14_DOC PHASE 5 (Doc06)              │
│ §5 KNOWLEDGE RULES (6 entities)  →  MASTER_SPECIFICATION §8                  │
│                                  →  QWEN_14_DOC PHASE 7 (Doc08)              │
│ §6 GOVERNANCE RULES              →  MASTER_SPECIFICATION §11                 │
│                                  →  QWEN_14_DOC PHASE 10 (Doc11)             │
│ §7 FORBIDDEN RULES               →  All sources (comprehensive)              │
│ §8 IMPLEMENTATION RULES          →  QWEN_14_DOC PHASE 1–4 (Doc02–05)         │
│                                  →  ST_LMS_CORE.js                           │
│ Appendix A (Wave Structures)     →  ST_LMS_CORE.js (WAVE_STRUCTS)            │
│ Appendix B (Clone Authority)     →  MASTER_SPECIFICATION §7                  │
│ Appendix C (Oracle Vector)       →  ST_LMS_CORE.js (ORACLE.vec)             │
│ Appendix D (Audit-ID Format)     →  ST_LMS_CORE.js (ID.gen)                  │
│ Post-Fix Compliance              →  01-07_IMPLEMENTATION_AUDIT.md            │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

```
================================================================================
                           END OF SPECIFICATION FREEZE
================================================================================

This document is CONSTITUTIONALLY FROZEN.
No modification is permitted without Governance amendment (approval ganda +
Chronicle CONSTITUTION_AMENDED).

On any conflict between this document and MASTER_SPECIFICATION.html:
  MASTER_SPECIFICATION.html wins on CONTENT.

On any conflict between this document and DOCUMENT_DEPENDENCY.html:
  DOCUMENT_DEPENDENCY.html wins on ORDER.

This document supersedes:
  - 01-07_IMPLEMENTATION_AUDIT.md (as comprehensive freeze)
  - ST_LMS_CORE.js (as specification target)

References incorporated:
  - MASTER_SPECIFICATION.html  (Sections S0–S14, 687 lines)
  - DOCUMENT_DEPENDENCY.html   (Sections D0–D12, 611 lines)
  - QWEN_14_DOC.html           (PHASE 0–13, 733 lines)
  - 01-07_IMPLEMENTATION_AUDIT.md.md (1087 lines)
  - ST_LMS_CORE.js             (842 lines, 26 modules)

================================================================================
