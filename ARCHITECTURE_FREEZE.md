# ARCHITECTURE FREEZE — ST-LMS v3

## Native HTML Market Geometry Intelligence Operating System

**Date:** 2026-07-28
**Phase:** PHASE 0 — Prompt 02
**Status:** CONSTITUTIONALLY FROZEN
**Source:** MASTER_SPECIFICATION.html, DOCUMENT_DEPENDENCY.html, QWEN_14_DOC.html, ST_LMS_CORE.js, 01-07_IMPLEMENTATION_AUDIT.md, stlms_sqlite_schema_v1.sql

---

## 1. ARCHITECTURE DIAGRAM

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ST-LMS v3 — 20-Layer Architecture                      │
│                     Native HTML Market Geometry Intelligence OS                │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│  SHARED BLOCK (1× per candle)                                                  │
│                                                                                │
│  ┌──────────┐    ┌───────────┐    ┌──────────┐    ┌───────────┐    ┌─────────┐│
│  │   BOOT   │───▶│  MARKET   │───▶│  TRUTH   │───▶│ STRUCTURE │───▶│EVIDENCE ││
│  │  (once)  │    │observation│    │ geometry │    │cage/wave  │    │ 3-bus   ││
│  └──────────┘    └───────────┘    └──────────┘    └───────────┘    └─────────┘│
│       │               │                │                │               │      │
│       │               ▼                ▼                ▼               ▼      │
│       │         market_snapshot  truth_snapshot  structure_snapshot  evidence │
│       │                                                              _snapshot│
│       │                                                                       │
│       │         ┌─────────────────────────────────────────────────┐          │
│       │         │           CARD SHARING (1× compute, 3× share)   │          │
│       │         └─────────────────────────────────────────────────┘          │
└───────┼───────────────────────────────────────────────────────────────────────┘
        │
        │  SHARED cards flow to all 3 clones
        ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  PER-CLONE BLOCK (3× — isolated sub-ledgers)                                   │
│                                                                                │
│  ┌─────────────────────────────────────────────────────────────────────┐     │
│  │                         LONG CLONE                                    │     │
│  │  ┌──────────┐  ┌─────────┐  ┌──────────┐  ┌───────┐  ┌──────┐  ┌───┐│     │
│  │  │CLONE_OBS │─▶│ ENTRY   │─▶│ POSITION │─▶│PROFIT │─▶│EXIT  │─▶│CL ││     │
│  │  │(observe) │  │VALIDATE │  │  MGMT    │  │ MGMT  │  │VALID │  │MARK││     │
│  │  └──────────┘  └─────────┘  └──────────┘  └───────┘  └──────┘  └───┘│     │
│  │    │                │            │            │          │        │   │     │
│  │    │          ENTRY_MARKER   mae/mfe    partial/lock  EXIT_MARKER   │     │
│  │    └────────────────────────────────────────────────────────────────┘     │
│  │                       ↓                                                    │
│  │              clone_observation → clone_snapshot → trade_snapshot           │
│  └─────────────────────────────────────────────────────────────────────┘     │
│                                                                                │
│  ┌─────────────────────────────────────────────────────────────────────┐     │
│  │                         SHORT CLONE (mirror)                          │     │
│  │  ┌──────────┐  ┌─────────┐  ┌──────────┐  ┌───────┐  ┌──────┐  ┌───┐│     │
│  │  │CLONE_OBS │─▶│ ENTRY   │─▶│ POSITION │─▶│PROFIT │─▶│EXIT  │─▶│CL ││     │
│  │  │(observe) │  │VALIDATE │  │  MGMT    │  │ MGMT  │  │VALID │  │MARK││     │
│  │  └──────────┘  └─────────┘  └──────────┘  └───────┘  └──────┘  └───┘│     │
│  └─────────────────────────────────────────────────────────────────────┘     │
│                                                                                │
│  ┌─────────────────────────────────────────────────────────────────────┐     │
│  │                         GRID CLONE (cage-only)                        │     │
│  │  ┌──────────┐  ┌─────────┐  ┌──────────┐  ┌───────┐  ┌──────┐  ┌───┐│     │
│  │  │CLONE_OBS │─▶│GRID_EVAL│─▶│GRID_FILLS│─▶│FILL   │─▶│BREAK │─▶│CL ││     │
│  │  │(observe) │  │         │  │          │  │MGMT   │  │EXIT  │  │MARK││     │
│  │  └──────────┘  └─────────┘  └──────────┘  └───────┘  └──────┘  └───┘│     │
│  └─────────────────────────────────────────────────────────────────────┘     │
│                                                                                │
│  ┌──────────────────────────────────────────────────────────────┐            │
│  │                    GLOBAL ORCHESTRATOR                         │            │
│  │  Reads 3 ledgers for net/gross exposure limits only            │            │
│  │  Does NOT mix statistics across clones                        │            │
│  └──────────────────────────────────────────────────────────────┘            │
└──────────────────────────────────────────────────────────────────────────────┘
        │
        │  All clone outputs merge
        ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  SHARED-AGAIN BLOCK (1× — card-agnostic, unidirectional)                       │
│                                                                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐                      │
│  │STATISTICS│─▶│KNOWLEDGE │─▶│PREDICTION│─▶│GOVERNANCE│                      │
│  │aggregate │  │6 entities│  │empirical │  │ 3-rem    │                      │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘                      │
│       │              │              │              │                           │
│       ▼              ▼              ▼              ▼                           │
│  statistics_    knowledge_     prediction_    config_version                  │
│  snapshot       snapshot       snapshot      (BOUNDED only)                   │
│                                                                                │
│  ┌──────────────────────────────────────────────────────────────┐            │
│  │                    ON-DEMAND (not per candle)                  │            │
│  │  ┌───────────┐                                                │            │
│  │  │ BENCHMARK │  WASIT 5-gate walk-forward (worker parallel)   │            │
│  │  └───────────┘                                                │            │
│  └──────────────────────────────────────────────────────────────┘            │
│                                                                                │
│  ┌──────────────────────────────────────────────────────────────┐            │
│  │                    OPTIONAL (terminal)                         │            │
│  │  ┌──────────┐                                                │            │
│  │  │ CONSUMER │  fund/veto/intent/paper/live-adapter(DISABLED)  │            │
│  │  └──────────┘                                                │            │
│  └──────────────────────────────────────────────────────────────┘            │
└──────────────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  CROSS-CUTTING LAYERS                                                          │
│                                                                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐              │
│  │  REPLAY  │  │  AUDIT   │  │  VIEW    │  │FINAL_VALIDATION  │              │
│  │ 6 types  │  │6 domains │  │12 panels │  │   12 checks      │              │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘              │
│       │              │              │              │                           │
│       │              │              │              │                           │
│       ▼              ▼              ▼              ▼                           │
│  reads all       audits all      renders        validates all                  │
│  snapshots       domains         all cards      domains                        │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. PIPELINE DIAGRAM

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ST-LMS v3 — 22-Stage Pipeline                              │
│                         Per Closed Candle                                     │
└─────────────────────────────────────────────────────────────────────────────┘

STAGE  TYPE              NAME                    INPUT → OUTPUT
─────  ────────────────  ──────────────────────  ──────────────────────────────
 1     ONCE              BOOT                    config/registry → SYSTEM_BOOT
                          (establish physics)    (hard fail if registry broken)
       ═══════════════════════════════════════════════════════════════════════
 2     SHARED            MARKET OBSERVATION      candle_raw → market_snapshot
                          (quarantine/canonize)  CLOSED + hygiene → Truth
       ───────────────────────────────────────────────────────────────────────
 3     SHARED            TRUTH LAYER             market_snapshot + ckpt →
                          (pure geometry)        truth_snapshot
                                                 (st,atr,ema,macd,rsi,wpr,
                                                  vel,acc,dist,distAtr)
       ───────────────────────────────────────────────────────────────────────
 4     SHARED            STRUCTURE LAYER         truth + lines →
                          (cage/ladder/phase)    structure_snapshot
                                                 (cage,wave,ladder,nearest,
                                                  pp,dist_ceiling,dist_floor)
       ───────────────────────────────────────────────────────────────────────
 5     SHARED            EVIDENCE LAYER          truth + candle + OI + wave →
                          (3 independent buses)  evidence_snapshot
                                                 (dir_bus,exit_bus,
                                                  correction_bus,OI,MTF,
                                                  max_score)
       ═══════════════════════════════════════════════════════════════════════
       CARD SHARING: stages 2-5 run 1×. Results shared to all 3 clones.
       ═══════════════════════════════════════════════════════════════════════

 6     PER-CLONE ×3      CLONE OBSERVATION       snapshot + ledger →
                          (record hypothesis)    clone_observation
                          (mandatory per candle, also no-trade)
       ───────────────────────────────────────────────────────────────────────
 7     PER-CLONE ×3      ENTRY VALIDATION        observation + global →
                          (conjunction gate)     ENTRY_MARKER / no-trade
                                                 (must have reason if no-trade)
       ───────────────────────────────────────────────────────────────────────
 8     PER-CLONE ×3      POSITION MGMT           position + candle + exit_bus
                          (manage live position) → mae/mfe/trail update
       ───────────────────────────────────────────────────────────────────────
 9     PER-CLONE ×3      PROFIT MGMT             unreal + ATR + exit_bus →
                          (secure profit)        partial/lock/trail
                                                 (HOLD-veto: 6-7 > others)
       ───────────────────────────────────────────────────────────────────────
10     PER-CLONE ×3      EXIT VALIDATION         position + guard + cage →
                          (decide close + why)   exit_reason / null
                                                 (priority: 1-5 > 6-7)
       ───────────────────────────────────────────────────────────────────────
11     PER-CLONE ×3      CLOSE POSITION          reason + price (adverse-first)
                          (after-fee result)     → EXIT_MARKER
                                                 (WIN only if net > 0)
       ───────────────────────────────────────────────────────────────────────
12     PER-CLONE ×3      TRADE MARKER            entry + exit this candle →
                          (aggregate markers)    trade_snapshot
       ═══════════════════════════════════════════════════════════════════════
       PER-CLONE SUB-LEDGERS: LONG/SHORT/GRID isolated. No stat mixing.
       ═══════════════════════════════════════════════════════════════════════

13     SHARED-AGAIN      STATISTICS              marker + snapshot →
                          (aggregate, sample-gated) statistics_snapshot
                                                 (CUKUP iff sample ≥ 30)
       ───────────────────────────────────────────────────────────────────────
14     SHARED-AGAIN      RIVER (KNOWLEDGE)       all cards →
                          (append-only archivist) store + index + chronicle
       ───────────────────────────────────────────────────────────────────────
15     ON-DEMAND         BENCHMARK               2 configs + replay →
                          (WASIT 5-gate)         benchmark_snapshot
                          (NOT per candle — on-demand only)
       ───────────────────────────────────────────────────────────────────────
16     SHARED-AGAIN      ACADEMY (KNOWLEDGE)      marker + snapshot (join) →
                          (empirical win_rate)    academy_artifacts
                          (per clone/structure/distance_bucket/reason)
       ───────────────────────────────────────────────────────────────────────
17     SHARED-AGAIN      ORACLE (KNOWLEDGE)       vector_now + historical →
                          (similarity match)      oracle_match
                          (euclidean; match > 7500)
       ───────────────────────────────────────────────────────────────────────
18     SHARED-AGAIN      HIVEMIND (KNOWLEDGE)     artifacts + oracle +
                          (understand market)     evidence_snapshot →
                                                  market_understanding
                                                  (not a signal)
       ───────────────────────────────────────────────────────────────────────
19     SHARED-AGAIN      CERMIN (KNOWLEDGE)       markers + confidence →
                          (calibrate)             calibration_error
       ───────────────────────────────────────────────────────────────────────
20     SHARED-AGAIN      DARWIN (KNOWLEDGE)       artifacts + bounded + PEX →
                          (propose mutation)      darwin_proposals
                                                  (no auto-execute)
       ───────────────────────────────────────────────────────────────────────
21     SHARED-AGAIN      PREDICTION               understanding + academy +
                          (empirical + similarity) oracle →
                                                  prediction_snapshot
                                                  (no model; empirical only)
       ───────────────────────────────────────────────────────────────────────
22     SHARED-AGAIN      GOVERNANCE               proposal + verdict + human →
                          (rem & kemudi)          decision + config_version
                          (loop ONLY to BOUNDED params)
       ═══════════════════════════════════════════════════════════════════════

OPT    OPTIONAL         CONSUMER                  understanding + report →
                          (trade is optional)     intent/report
                          (live-adapter DISABLED default)
```

---

## 3. DATA FLOW DIAGRAM

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ST-LMS v3 — Complete Data Flow                              │
│                   Immutable Cards · Unidirectional                              │
└─────────────────────────────────────────────────────────────────────────────┘

                              RAW CANDLE DATA
                              (OHLCV + takerBuyRatio)
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │          MARKET LAYER          │
                    │  hygiene → gaps → OI proxy     │
                    │  produces: market_snapshot     │
                    └───────────────┬───────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │          TRUTH LAYER           │
                    │  st, atr, ema, macd, rsi,     │
                    │  wpr, vel, acc, dist, distAtr │
                    │  produces: truth_snapshot      │
                    └───────────────┬───────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               │
        ┌───────────────────┐ ┌───────────────────┐ │
        │  STRUCTURE LAYER   │ │  EVIDENCE LAYER   │ │
        │  cage, wave,       │ │  dir_bus, exit_   │ │
        │  ladder, nearest,  │ │  bus, correction_ │ │
        │  phase, pp,        │ │  bus, OI, MTF,    │ │
        │  dist_ceiling,     │ │  max_score        │ │
        │  dist_floor        │ │                   │ │
        │  → structure_snap  │ │  → evidence_snap  │ │
        └─────────┬─────────┘ └─────────┬─────────┘ │
                  │                     │           │
                  └──────────┬──────────┘           │
                             │                      │
                             ▼                      │
              ┌──────────────────────────────┐      │
              │    CARD SHARING TO CLONES     │◄─────┘
              │  truth + structure + evidence │
              │  (shared 1×, read 3×)        │
              └──────────────┬───────────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
          ▼                  ▼                  ▼
  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
  │  LONG CLONE  │  │ SHORT CLONE  │  │  GRID CLONE  │
  │  bias:       │  │ bias:        │  │ bias:        │
  │  EXPANSION_UP│  │EXHAUSTION_DN │  │COMPRESSION   │
  │              │  │              │  │_RANGE        │
  │  entry if:   │  │ entry if:    │  │ entry if:    │
  │  stDir=+1 ∧  │  │ stDir=-1 ∧  │  │ cage_valid ∧ │
  │  ema>0 ∧     │  │ ema<0 ∧     │  │ width≥3·req  │
  │  vd>0 ∧      │  │ vd<0 ∧      │  │ ∧ breakout=  │
  │  corridor ∧  │  │ corridor ∧  │  │ NONE ∧ pp    │
  │  fee_safe ∧  │  │ fee_safe ∧  │  │ in zone      │
  │  global_ok   │  │ global_ok   │  │              │
  │              │  │              │  │              │
  │  exit:       │  │ exit:       │  │ exit:        │
  │  SL=floor    │  │ SL=ceiling  │  │ GRID_TP,     │
  │  TP=ceiling  │  │ TP=floor    │  │ RANGE_BREAK, │
  │  wrong-entry │  │ wrong-entry │  │ WRONG_ENTRY, │
  │  exit-bus    │  │ exit-bus    │  │ STOP-ALL     │
  │              │  │              │  │              │
  │  → clone_obs │  │ → clone_obs │  │ → grid_state │
  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
         │                 │                 │
         │    ┌────────────┼────────────┐    │
         │    │            │            │    │
         ▼    ▼            ▼            ▼    ▼
  ┌──────────────────────────────────────────────┐
  │               TRADE + POSITION               │
  │  ENTRY_MARKER → position open                │
  │  POSITION.update(mae/mfe)                    │
  │  decideClose → EXIT_MARKER                   │
  │  after-fee: net = gross - fee - slip         │
  │  WIN only if net > 0 (adverse-first)         │
  │  → trade_snapshot                            │
  └──────────────────┬───────────────────────────┘
                     │
                     ▼
  ┌──────────────────────────────────────────────┐
  │                STATISTICS                    │
  │  tradeStats(markers) per clone               │
  │  sample-gated: CUKUP iff sample ≥ 30         │
  │  win_rate, expectancy, PF, MAE, MFE,         │
  │  fee_drag, wrong_rate                       │
  │  → statistics_snapshot                       │
  └──────────────────┬───────────────────────────┘
                     │
                     ▼
  ┌──────────────────────────────────────────────┐
  │                KNOWLEDGE                     │
  │  River: append all cards → chronicle         │
  │  Academy: win_rate per 4-dim bucket          │
  │  Oracle: euclidean similarity (vector beku)  │
  │  HiveMind: synthesize understanding          │
  │  CERMIN: calibration error tracking          │
  │  Librarian: lifecycle management             │
  │  Darwin: propose parameter mutations         │
  │  → knowledge_snapshot                        │
  └──────────────────┬───────────────────────────┘
                     │
                     ▼
  ┌──────────────────────────────────────────────┐
  │               PREDICTION                     │
  │  empirical win_rate (from Academy)           │
  │  similarity_score (from Oracle)              │
  │  calibration_error (from CERMIN)             │
  │  NO MODEL — purely empirical                 │
  │  → prediction_snapshot                       │
  └──────────────────┬───────────────────────────┘
                     │
                     ▼
  ┌──────────────────────────────────────────────┐
  │              GOVERNANCE                      │
  │  Darwin → WASIT → Human                     │
  │  6 validations                               │
  │  bounded auto-reject                         │
  │  rollback deterministik                      │
  │  → config_version (BOUNDED params only)      │
  └──────────────────┬───────────────────────────┘
                     │
                     ▼
  ┌──────────────────────────────────────────────┐
  │               CONSUMER (OPTIONAL)             │
  │  fundEval → vetoGate → intentBuilder         │
  │  live-adapter: DISABLED default              │
  │  SIDEWAY → GRID_INTENT (not LONG)            │
  └──────────────────────────────────────────────┘

  ═══════════════════════════════════════════════════════════════

  CROSS-CUTTING:

  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
  │    REPLAY    │  │    AUDIT     │  │     VIEW     │
  │  reads all   │  │  verifies    │  │  renders     │
  │  snapshots   │  │  all domains │  │  all cards   │
  └──────────────┘  └──────────────┘  └──────────────┘

  ┌──────────────────────────────────┐
  │       FINAL VALIDATION           │
  │  12 checks across all domains    │
  └──────────────────────────────────┘

  ═══════════════════════════════════════════════════════════════

  IMMUTABLE CARD RULE:
  Every snapshot = frozen card with checksum + lineage.
  card = Object.freeze + SHA-256 checksum + dependencies + audit-ID.
  Update = new card version, never mutation in-place.
```

---

## 4. SNAPSHOT FLOW DIAGRAM

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ST-LMS v3 — 10 Snapshots Per Closed Candle                 │
│                         W = Frozen Stored · OD = On-Demand                    │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌───────────────────────────────────────────────────────────────────────┐
  │ 1. MARKET SNAPSHOT                                                     │
  │    Producer: MARKET layer                                              │
  │    Consumer: TRUTH                                                     │
  │    W fields: ts, symbol, tf, OHLCV(o,h,l,c,v), taker_buy_ratio,       │
  │              taker_sell_volume, data_status, gap_flag, wib_iso         │
  │    OD fields: —                                                        │
  │    Status: CLOSED + hygiene → FINAL; else PROVISIONAL                  │
  └───────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
  ┌───────────────────────────────────────────────────────────────────────┐
  │ 2. TRUTH SNAPSHOT                                                      │
  │    Producer: TRUTH layer (PointBuilder)                                │
  │    Consumer: STRUCTURE, EVIDENCE                                       │
  │    W fields: close, st, st_canon, stDir, color, atr, ema, ema12,      │
  │              ema26, macd, macd_signal, macd_hist, dist, distAtr,       │
  │              rsi, wpr, vel, acc, volDelta, point_status                │
  │    OD fields: —                                                        │
  │    Status: WARMUP (during warmup) / VALID (after warmup)               │
  └───────────────────────────────────────────────────────────────────────┘
                          │
              ┌───────────┼───────────┐
              ▼                       ▼
  ┌──────────────────────┐  ┌──────────────────────┐
  │ 3. STRUCTURE SNAPSHOT│  │ 4. EVIDENCE SNAPSHOT │
  │    Producer:         │  │    Producer:         │
  │      STRUCTURE layer │  │      EVIDENCE layer  │
  │    Consumer: CLONE,  │  │    Consumer: CLONE,  │
  │      GRID            │  │      HIVEMIND        │
  │    W fields:         │  │    W fields:         │
  │      cage{status,    │  │      dir_bus{ema,oi, │
  │        upper,lower,  │  │        vd,mtf_long,  │
  │        pp,rangeAtr,  │  │        mtf_short},   │
  │        breakout,     │  │      exit_bus{rsi,   │
  │        upVi,lowVi,   │  │        wpr,macd_hist,│
  │        cross,        │  │        hold,vel,acc, │
  │        pressure*},   │  │        vel_signal,   │
  │      ladder, nearest,│  │        acc_signal,   │
  │      phase, wave     │  │        early_inval}, │
  │    OD fields:        │  │      correction_bus{ │
  │      dist_ceiling,   │  │        pp,phase,     │
  │      dist_floor      │  │        dist_ceiling, │
  │                      │  │        dist_floor,   │
  │                      │  │        wave_struct,  │
  │                      │  │        cage_status,  │
  │                      │  │        cage_range,   │
  │                      │  │        breakout},    │
  │                      │  │      mtf{sector,raw, │
  │                      │  │        max,final,    │
  │                      │  │        long,short,   │
  │                      │  │        range},       │
  │                      │  │      max_score,      │
  │                      │  │      data_quality    │
  │                      │  │    OD fields: —      │
  └──────────┬───────────┘  └──────────┬───────────┘
             │                         │
             └──────────┬──────────────┘
                        │
                        ▼
  ┌───────────────────────────────────────────────────────────────────────┐
  │ 5. CLONE SNAPSHOT                                                      │
  │    Producer: CLONE layer (×3: LONG/SHORT/GRID)                         │
  │    Consumer: STATISTICS                                                │
  │    W fields: per_clone{clone_id, bias,                                 │
  │              observation{setup_score, entry_allowed, entry_reason,     │
  │                no_entry_reason, confidence, corridor|grid_state,       │
  │                expected_move, required_move, fee_safe, mtf_conflict},  │
  │              open_position|null, grid_fills[]}                         │
  │    OD fields: —                                                        │
  │    Rule: 3 observations per closed candle (mandatory, even if no-trade)│
  └───────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
  ┌───────────────────────────────────────────────────────────────────────┐
  │ 6. TRADE SNAPSHOT                                                      │
  │    Producer: SIM (executes clone intent against candle)                │
  │    Consumer: STATISTICS                                                │
  │    W fields: markers[{kind, clone, side, reason, entry, exit,         │
  │              gross, fee, slip, net, result, mae, mfe, hold}],         │
  │              running_per_clone{mae, mfe}                               │
  │    OD fields: —                                                        │
  │    Rule: after-fee adverse-first; WIN only if net > 0                  │
  └───────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
  ┌───────────────────────────────────────────────────────────────────────┐
  │ 7. STATISTICS SNAPSHOT                                                 │
  │    Producer: STATISTICS layer                                          │
  │    Consumer: KNOWLEDGE                                                 │
  │    W fields: per_clone{sample, win_rate_net, expectancy_net, pf,      │
  │              mae, mfe, fee_drag, wrong_rate, coverage},               │
  │              distance_health_hist, fee_safe_margin_dist,               │
  │              wrong_entry_dist                                          │
  │    OD fields: all fields (derived from Trade)                          │
  │    Rule: CUKUP iff sample ≥ 30 (SAMPLE_GATE)                           │
  └───────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
  ┌───────────────────────────────────────────────────────────────────────┐
  │ 8. KNOWLEDGE SNAPSHOT                                                  │
  │    Producer: KNOWLEDGE layer (6 entities)                              │
  │    Consumer: PREDICTION, GOVERNANCE                                    │
  │    W fields: academy_artifacts[], oracle_match,                        │
  │              hivemind{intelligence_score, dominant_bias, *_boost,      │
  │                evidence_adj},                                          │
  │              cermin{band, predicted, actual, calibration_error},       │
  │              librarian_events[], darwin_proposals[]                    │
  │    OD fields: —                                                        │
  │    Rule: unidirectional; no-ML; HiveMind reads currentEvidence from    │
  │           evidence_snapshot (not constant)                              │
  └───────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
  ┌───────────────────────────────────────────────────────────────────────┐
  │ 9. BENCHMARK SNAPSHOT                                                  │
  │    Producer: BENCHMARK layer (WASIT worker)                            │
  │    Consumer: GOVERNANCE                                                │
  │    W fields: param, base, cand, folds, totals, gates{G1..G5},         │
  │              per_fold[], verdict                                       │
  │    OD fields: —                                                        │
  │    Rule: ON-DEMAND only (absent on normal closed candles)              │
  └───────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
  ┌───────────────────────────────────────────────────────────────────────┐
  │ 10. PREDICTION SNAPSHOT                                                │
  │    Producer: PREDICTION layer                                          │
  │    Consumer: CONSUMER                                                  │
  │    W fields: intelligence_score, dominant_bias,                        │
  │              empirical_win_rate_per_clone{LONG, SHORT, GRID},          │
  │              similarity_score, pattern_boost, oracle_boost,            │
  │              no_model=true                                             │
  │    OD fields: empirical_win_rate (from Academy)                        │
  │    Rule: no forecast model; NULL if sample insufficient                │
  │    Forbidden: output of predictive model                               │
  └───────────────────────────────────────────────────────────────────────┘


  ═══════════════════════════════════════════════════════════════════════════

  SNAPSHOT LIFECYCLE:
  1. PRODUCE  at valid pipeline stage (one source per quantity)
  2. FREEZE   Object.freeze + checksum + dependencies=[candle_id, config_version]
  3. STORE    append-only IndexedDB (cold/warm); index by type+ts & config+ts
  4. CONSUME  read-only by downstream layers & Consumer/Visualization
  5. REPLAY   read snapshot sequence; RE-VALIDATE checksum+lineage on load

  FREEZE RULE:
  - Snapshot FINAL only from CLOSED candle
  - PROVISIONAL does not produce final snapshot
  - Benchmark Snapshot absent on normal closed candles (on-demand only)
  - Prediction Snapshot forbidden to contain predictive model output
  - Adding/removing snapshot fields = constitution amendment (§3)
```

---

## 5. LAYER CONTRACTS

### 5.1 BOOT

**Responsibilities:**
- Initialize runtime environment (Native HTML OS)
- Load configuration (bounded registry defaults)
- Establish workspace (IndexedDB + memory)
- Set up checkpoint system
- Start resource governor

**Authority Contracts:**
- May: initialize all namespaces, load config, open IndexedDB
- Must NOT: modify configuration, start pipeline without config validation

**Component Contracts:**
- Runtime Initializer: set up JavaScript namespaces
- Configuration Manager: load bounded parameters from CONFIG
- Workspace Manager: open IndexedDB, create object stores
- Checkpoint Manager: load/save checkpoint state
- Resource Governor: monitor RAM/CPU

**Pipeline Contracts:** Stage 1 — ONCE (not per candle)

**Snapshot Contracts:** Produces SYSTEM_BOOT card

**Worker Contracts:** Main thread only

**Input:** Config, registry
**Output:** SYSTEM_BOOT (all namespaces ready)
**Forbidden:** Starting without complete registry; silent failure

---

### 5.2 WORKSPACE

**Responsibilities:**
- Manage tiered storage (L1 Hot / L2 Warm / L3 Cold / L4 Archive / L5 Evict)
- Provide append-only card storage via IndexedDB
- Maintain card index (by type+ts, config+ts)
- Run serial writer on main thread (zero race conditions)
- Compress cold/archive tier with CompressionStream
- Evict old data based on age + last-logical-access

**Authority Contracts:**
- May: store cards, query cards, compress, evict
- Must NOT: modify cards (append-only), allow concurrent writes

**Component Contracts:**
- IndexedDB Writer: serial, main thread, append-only
- Tiered Storage Manager: L1–L5 management
- Object Store Manager: cards, config_state, checkpoints, governance, audit_log, runs
- Compression Manager: CompressionStream for cold/archive
- Eviction Manager: age-based + last-logical-access

**Pipeline Contracts:** Foundation layer — used by all pipeline stages

**Snapshot Contracts:** Stores all snapshots as immutable cards

**Worker Contracts:** Main thread only for writes; workers send results via postMessage

**Input:** Cards from pipeline stages
**Output:** Persistent card storage
**Forbidden:** Concurrent writes; worker-direct IndexedDB access

---

### 5.3 MARKET

**Responsibilities:**
- Ingest raw OHLCV candle data (fixture or live feed)
- Validate candle hygiene (H ≥ O,C; L ≤ O,C; H ≥ L)
- Detect time gaps between candles
- Generate OI proxy from volume + takerBuyRatio
- Aggregate 1m → higher TF (via Data Worker)
- Produce market_snapshot card

**Authority Contracts:**
- May: read raw data, validate hygiene, detect gaps, proxy OI
- Must NOT: compute geometry (that's TRUTH's job)

**Component Contracts:**
- Market Data Layer: fetch/import/WebSocket feed
- Market Snapshot Engine: produce market_snapshot card
- Data Hygiene Validator: validate candle integrity
- Gap Detector: detect time gaps
- Derived TF Aggregator: aggregate to higher timeframes (worker)
- OI Proxy Generator: derive OI from volume data
- Cascade Handler: handle missing candles

**Pipeline Contracts:** Stage 2 — SHARED (1× per candle)

**Snapshot Contracts:** Produces market_snapshot

**Worker Contracts:** Data Worker for batch bootstrap, derived-TF aggregation, gap-repair

**Input:** Raw candle (OHLCV + takerBuyRatio)
**Output:** market_snapshot card
**Forbidden:** Computing indicators (TRUTH domain)

---

### 5.4 TRUTH

**Responsibilities:**
- Compute Supertrend (st, stDir, color) — single source of truth
- Compute ATR (period 10), EMA (period 14), EMA12, EMA26
- Compute MACD (12/26/9) with signal and histogram
- Compute RSI (period 10), W%R (period 14)
- Compute W%R Velocity and Acceleration
- Compute Distance-to-ST (dist) and distAtr
- Compute Volume Delta (2*takerBuyRatio - 1)
- Detect trend flips (TREND_FLIP_UP/DOWN)
- Set point status (WARMUP/VALID)
- Produce truth_snapshot card

**Authority Contracts:**
- May: compute all geometry primitives, detect flips
- Must NOT: be influenced by indicators (Truth is blind to indicators per LAW-MASTER-15)

**Component Contracts:**
- Point Builder: per-candle indicator computation
- Supertrend: directional line with flip detection
- ATR: volatility measure
- EMA: trend indicator
- MACD: momentum oscillator
- RSI: relative strength
- W%R: Williams %R (exit-only per authority matrix)
- W%R Velocity/Acceleration: rate of change
- Distance-to-ST: normalized distance
- Volume Delta: net volume direction

**Pipeline Contracts:** Stage 3 — SHARED (1× per candle)

**Snapshot Contracts:** Produces truth_snapshot

**Worker Contracts:** Main thread (hot, sequential — state continuity required)

**Input:** market_snapshot + checkpoint
**Output:** truth_snapshot card
**Forbidden:** Computing structure/cage (STRUCTURE domain); using indicators as decision input

---

### 5.5 STRUCTURE

**Responsibilities:**
- Build line segments from Supertrend points (LineBuilder)
- Build slope transitions between lines (SlopeBuilder)
- Classify wave structures (13 types via WaveBuilder)
- Compute cage (upper/lower/pp/rangeAtr/breakout) via CageEngine
- Resolve support/resistance walls with versioning (v0→v1→v2)
- Find escape path (comfortable wall with distance ≥ threshold·ATR)
- Compute ladder (stepped support/resistance patterns)
- Find nearest support and resistance
- Determine market phase from cage+wave+stDir
- Compute distance ceiling (ceiling - close) and distance floor (close - floor)
- Produce structure_snapshot card

**Authority Contracts:**
- May: compute all structure geometry, classify wave/cage/phase
- Must NOT: use indicators for decisions (structure is geometry-only)

**Component Contracts:**
- Line Builder: extract line segments from ST points
- Slope Builder: extract slope transitions
- Wave Builder: classify into 13 wave structures
- Cage Engine: compute cage with wall resolution and versioning
- Wall Resolver: resolve support/resistance with escape path
- Ladder Analyzer: check stepped patterns
- Nearest Finder: find nearest S/R
- Phase Determiner: compute market phase
- Distance Calculator: dist_ceiling, dist_floor

**Pipeline Contracts:** Stage 4 — SHARED (1× per candle)

**Snapshot Contracts:** Produces structure_snapshot

**Worker Contracts:** Main thread (hot, sequential)

**Input:** truth_snapshot + line data
**Output:** structure_snapshot card
**Forbidden:** Computing indicators; using indicator data

---

### 5.6 EVIDENCE

**Responsibilities:**
- Build Direction Bus: entry-legal witnesses (EMA, OI, VolDelta, MTF)
- Build Exit Bus: close-only exit signals (RSI, W%R, MACD, HOLD-veto)
- Build Correction Bus: market context (pp, phase, distances, wave, cage)
- Inherit OI from proxy with freshness-weighted scoring
- Compute MTF sector from wave structure
- Compute max score (data quality ceiling)
- Track ST-Dist-Vol (standard deviation of distance-to-ST)
- Produce evidence_snapshot card

**Authority Contracts:**
- May: witness market state independently, score data quality
- Must NOT: use W%R/MACD/RSI for entry direction (per authority matrix)
- Must NOT: write to Truth or Structure (unidirectional)

**Component Contracts:**
- Direction Bus: EMA, OI, VolDelta, MTF scores
- Exit Bus: RSI, W%R, MACD, HOLD-veto, early invalidation
- Correction Bus: pp, phase, distances, wave, cage
- OI Inheritor: freshness-weighted OI score
- MTF Sector: wave-structure-based sector classification
- Max Score: data quality ceiling
- ST-Dist-Vol: volatility proxy from distance-to-ST

**Pipeline Contracts:** Stage 5 — SHARED (1× per candle)

**Snapshot Contracts:** Produces evidence_snapshot

**Worker Contracts:** Main thread (hot, sequential)

**Input:** truth_snapshot + structure_snapshot + candle + OI + wave
**Output:** evidence_snapshot card
**Forbidden:** W%R/RSI/MACD in Direction Bus; writing to Truth/Structure

---

### 5.7 CLONE (LONG/SHORT/GRID)

**Responsibilities:**
- LONG Clone: directional upward bias (EXPANSION_UP)
- SHORT Clone: directional downward bias (EXHAUSTION_DOWN) — mirror of LONG
- GRID Clone: range-bound bias (COMPRESSION_RANGE) — cage-only
- Produce clone_observation card per candle (mandatory, even if no-trade)
- Manage isolated sub-ledgers per clone
- Compute adaptive entry corridor
- Validate global risk limits
- Orchestrate clone activation

**Authority Contracts:**
- LONG: entry if stDir=+1 ∧ EMA-slope>0 ∧ vd>0 ∧ corridor.inZone ∧ fee_safe(dist_ceiling≥required) ∧ global_ok ∧ open==null
- SHORT: entry if stDir=-1 ∧ EMA-slope<0 ∧ vd<0 ∧ corridor.inZone ∧ fee_safe(dist_floor≥required) ∧ global_ok ∧ open==null
- GRID: entry if cage_valid ∧ fee_safe(width≥3·required) ∧ breakout==NONE ∧ pp in zone ∧ fills_per_side<max
- All: must NOT compute geometry (read from shared cards)
- All: must NOT use RSI/W%R/MACD for entry decisions
- All: must NOT read Oracle/HiveMind directly
- All: must NOT write to Truth

**Component Contracts:**
- LONG Clone: directional observation + entry + exit
- SHORT Clone: mirror of LONG
- GRID Clone: range observation + grid fills
- Clone Orchestrator: manage activation, global exposure
- Adaptive Entry Corridor: compute zone
- Global Risk Validator: check gross/net exposure
- Observation Card: record hypothesis per candle
- Grid State Evaluator: evaluate grid state

**Pipeline Contracts:** Stage 6 — PER-CLONE (3×)

**Snapshot Contracts:** Produces clone_snapshot (×3)

**Worker Contracts:** Main thread (hot, sequential)

**Input:** Shared snapshots (truth + structure + evidence) + own ledger
**Output:** clone_observation + clone_snapshot (per clone)
**Forbidden:** Computing geometry; reading Oracle/HiveMind; writing Truth; mixing stats across clones

---

### 5.8 TRADE

**Responsibilities:**
- Create ENTRY marker when clone entry conditions met
- Create EXIT marker when position closes
- Compute P&L: gross, fee, slip, net, result (WIN/LOSS/BREAKEVEN)
- Apply adverse-first rule (SL beats TP on same candle)
- Apply fee berlapis (murni + slip + safety)
- Compute adaptive TP (ATR-based, cage-bounded)
- Detect wrong entry (velocity/geometry based)
- Produce trade_snapshot card

**Authority Contracts:**
- May: create markers, compute P&L
- Must NOT: decide entry/exit (that's CLONE's job)

**Component Contracts:**
- Entry Marker: create ENTRY with price, SL, TP
- Exit Marker: create EXIT with full P&L
- Adaptive TP: compute take-profit level
- Wrong Entry Guard: detect wrong entry conditions
- Trade Marker Aggregator: collect markers per candle

**Pipeline Contracts:** Stages 7, 10, 11, 12 — PER-CLONE

**Snapshot Contracts:** Produces trade_snapshot

**Worker Contracts:** Main thread

**Input:** Clone intent + candle data
**Output:** ENTRY_MARKER / EXIT_MARKER + trade_snapshot
**Forbidden:** Making entry/exit decisions independently of CLONE

---

### 5.9 POSITION

**Responsibilities:**
- Track open positions (entry, SL, TP, side)
- Update MAE/MFE per candle
- Manage profit lock (partial TP)
- Manage trailing stop (ATR-based)
- Manage breakeven (move SL to entry after profit)
- Handle forced/emergency exit
- Validate position risk
- Prevent liquidation

**Authority Contracts:**
- May: track position state, update MAE/MFE
- Must NOT: decide entry (CLONE domain); decide exit (CLONE domain)

**Component Contracts:**
- Position Manager: track open positions
- MAE/MFE Tracker: excursion tracking
- Profit Lock: partial take-profit
- Trailing Stop: ATR-based trailing
- Breakeven Manager: SL to entry
- Forced Exit: emergency close
- Risk Validator: position risk checks
- Liquidation Avoidance: prevent liquidation

**Pipeline Contracts:** Stages 8, 9 — PER-CLONE

**Snapshot Contracts:** Consumes trade_snapshot (position state in clone_snapshot)

**Worker Contracts:** Main thread

**Input:** Open position + candle data
**Output:** Updated position state (mae, mfe, hold_count)
**Forbidden:** Entry/exit decisions

---

### 5.10 STATISTICS

**Responsibilities:**
- Aggregate trade statistics per clone
- Compute win_rate, expectancy, profit factor, MAE, MFE, fee_drag, wrong_rate
- Apply sample gate (CUKUP iff sample ≥ 30)
- Aggregate market-level statistics
- Produce statistics_snapshot card

**Authority Contracts:**
- May: aggregate statistics, apply sample gate
- Must NOT: express confidence below sample threshold (BELUM_CUKUP)

**Component Contracts:**
- Trade Statistics: per-clone aggregation
- Market Statistics: market-level aggregation
- Clone Statistics: per-clone with sample-gating
- Sample Gate: enforce sample≥30

**Pipeline Contracts:** Stage 13 — SHARED-AGAIN (1×)

**Snapshot Contracts:** Produces statistics_snapshot

**Worker Contracts:** Main thread + worker (for batch)

**Input:** Trade markers + snapshots
**Output:** statistics_snapshot card
**Forbidden:** Expressing confidence below sample threshold

---

### 5.11 KNOWLEDGE

**Responsibilities:**
- River: append-only archivist + index + chronicle
- Academy: empirical win_rate per (clone, structure, distance_bucket, reason)
- Oracle: euclidean similarity matching (vector beku, match>7500)
- HiveMind: synthesize market understanding (score+bias+boost)
- CERMIN: calibration error tracking (predicted vs actual)
- Librarian: lifecycle management (NEW→OBS→TRUSTED→MATURE/DEAD/DEPRECATED)
- Darwin: propose parameter mutations (Kelas-A bounded / Kelas-B PEX)
- Produce knowledge_snapshot card

**Authority Contracts:**
- All: unidirectional (no write-back to Core)
- All: no-ML (purely statistical/empirical)
- Oracle: vector frozen (W%R/MACD not in vector)
- HiveMind: reads currentEvidence from evidence_snapshot (not constant)
- Darwin: no auto-execute
- Librarian: DEAD/DEPRECATED not active

**Component Contracts:**
- Academy: win_rate per 4-dim bucket
- River: append-only archivist
- Oracle: euclidean similarity
- HiveMind: market understanding synthesis
- CERMIN: calibration error
- Librarian: lifecycle management (6 statuses)
- Darwin: parameter proposal

**Pipeline Contracts:** Stages 14, 16, 17, 18, 19, 20 — SHARED-AGAIN

**Snapshot Contracts:** Produces knowledge_snapshot

**Worker Contracts:** Knowledge Worker (cold, batch)

**Input:** All cards (card-agnostic)
**Output:** knowledge_snapshot card
**Forbidden:** Writing to Core/Clone; using ML; auto-executing proposals

---

### 5.12 PREDICTION

**Responsibilities:**
- Aggregate empirical win_rate from Academy
- Incorporate similarity_score from Oracle
- Include calibration_error from CERMIN
- Produce prediction_snapshot (no model — empirical only)
- Return NULL/BELUM_CUKUP if sample insufficient

**Authority Contracts:**
- May: aggregate empirical probabilities
- Must NOT: use predictive models, forecast prices
- Must NOT: output unsupported predictions (below sample threshold)

**Component Contracts:**
- Historical Similarity: Oracle-based
- Market Probability: Academy-based
- Market Intelligence: HiveMind-based
- CERMIN Calibration: calibration error

**Pipeline Contracts:** Stage 21 — SHARED-AGAIN (1×)

**Snapshot Contracts:** Produces prediction_snapshot

**Worker Contracts:** Main thread

**Input:** knowledge_snapshot (academy + oracle + hivemind + cermin)
**Output:** prediction_snapshot card
**Forbidden:** Predictive models; hidden AI; unsupported predictions

---

### 5.13 REPLAY

**Responsibilities:**
- 6 replay types: candle, snapshot, trade, clone, knowledge, governance
- Read snapshot sequence deterministically
- Re-validate checksum+lineage on load
- Resume via checkpoints (recompute hot-window 3h if checkpoint absent)
- Provide scrubber/step/auto-play interface

**Authority Contracts:**
- May: read all snapshots, replay deterministically
- Must NOT: compute new data; modify cards

**Component Contracts:**
- Candle Replay: market_snapshot sequence
- Snapshot Replay: full 10-snapshot frame
- Trade Replay: trade markers + equity
- Clone Replay: clone observations + positions
- Knowledge Replay: knowledge artifacts
- Governance Replay: governance timeline

**Pipeline Contracts:** Cross-cutting — reads all snapshots

**Snapshot Contracts:** Consumes all snapshots

**Worker Contracts:** Replay Worker (parallel across symbols)

**Input:** Snapshot sequence from IndexedDB
**Output:** Deterministic replay frames
**Forbidden:** Modifying cards; non-deterministic replay

---

### 5.14 SIMULATION

**Responsibilities:**
- Execute clone intent against candles (adverse-first)
- 4 simulation types: historical, live, strategy, clone
- Persist simulation state (writer serial via main thread)
- Verify determinism with dual-run hash comparison
- Produce trade markers and snapshots

**Authority Contracts:**
- May: execute clone intent, simulate P&L
- Must NOT: alter clone logic; bypass fee rules

**Component Contracts:**
- Simulation Engine: execute intent against candles
- Historical Simulation: replay fixture/IndexedDB
- Live Simulation: feed 1m (fetch/WS, offline fallback)
- Strategy Simulation: isolate one clone
- Clone Simulation: 3 clones simultaneously
- Determinism Verifier: dual-run hash comparison

**Pipeline Contracts:** Cross-cutting — uses pipeline stages 7–12

**Snapshot Contracts:** Produces trade_snapshot (via pipeline)

**Worker Contracts:** Main thread + worker

**Input:** Clone intent + candle data
**Output:** Trade markers + trade_snapshot
**Forbidden:** Non-adverse-first execution; bypassing fee

---

### 5.15 GOVERNANCE

**Responsibilities:**
- 6 validations: Constitution, Proposal, Authority Matrix, Build, Runtime, Governance Audit
- Proposal lifecycle: Darwin → WASIT → Human → apply/rollback
- Bounded auto-reject: values outside range = REJECTED without compute
- Rollback: deterministic revert to previous config_version
- Only loop back to BOUNDED parameters (not Core logic)

**Authority Contracts:**
- Darwin: propose Kelas-A (bounded) / Kelas-B (PEX); no auto-execute
- WASIT: 5-gate walk-forward filter; no approve (only filter)
- Human: final approve/reject
- Bounded Registry: auto-reject out-of-range values
- Runtime: apply config_version at boundary; rollback

**Component Contracts:**
- Constitution Validation: 18 laws + authority matrix
- Proposal Validation: bounded-check + label-peran
- Authority Matrix Validation: indicator usage check
- Build Validation: 15 stop-rules + determinism
- Runtime Validation: checksum + lineage + writer
- Governance Audit: decision timeline + deprecated
- Proposal Engine: Darwin→WASIT→Human workflow
- Bounded Registry: auto-reject
- Rollback Manager: deterministic revert

**Pipeline Contracts:** Stage 22 — SHARED-AGAIN (1×)

**Snapshot Contracts:** Consumes knowledge_snapshot

**Worker Contracts:** Benchmark Worker (WASIT walk-forward)

**Input:** knowledge_snapshot + proposals + human decisions
**Output:** config_version update (BOUNDED params only)
**Forbidden:** Writing to Core logic; auto-executing; bypassing bounded

---

### 5.16 CONSUMER

**Responsibilities:**
- Fund evaluation: position sizing, drawdown limits
- Veto gate: risk checks before trade intent
- Intent builder: construct trade intent from understanding
- Paper trading: simulated execution
- Live adapter: DISABLED default (requires governance approval)
- Export CSV from trade markers
- Dashboard: market intelligence, pattern recognition, volatility regime

**Authority Contracts:**
- May: build trade intent, evaluate risk
- Must NOT: modify Core pipeline; bypass governance
- Live adapter: DISABLED default

**Component Contracts:**
- Fund Manager: equity/margin/available
- Veto Gate: risk checks
- Intent Builder: construct intent
- Paper Trading: simulated execution
- Live Adapter: disabled default
- CSV Exporter: export markers
- API Layer: internal query interface

**Pipeline Contracts:** OPTIONAL (terminal — no downstream)

**Snapshot Contracts:** Consumes prediction_snapshot + knowledge_snapshot

**Worker Contracts:** Main thread

**Input:** prediction_snapshot + knowledge_snapshot
**Output:** Trade intent / report
**Forbidden:** Modifying Core; enabling live without approval

---

### 5.17 AUDIT

**Responsibilities:**
- 6 audit domains: Pipeline, Snapshot, Clone, Trade, Knowledge, Governance
- Self-test suite (16 automated tests)
- Deterministic fingerprint generation
- Per-domain audit with pass/fail
- Issue tracking (CRITICAL/HIGH/MEDIUM/LOW/INFO)

**Authority Contracts:**
- May: audit all domains, verify compliance
- Must NOT: modify audited domains

**Component Contracts:**
- Pipeline Audit: stages + card sharing
- Snapshot Audit: 10 snapshots + W/OD
- Clone Audit: 3 clones + 3 obs/candle
- Trade Audit: P&L + after-fee + adverse-first
- Knowledge Audit: unidirectional + no-ML
- Governance Audit: decisions + rollback
- Self-Test Suite: 16 automated tests
- Fingerprint Generator: deterministic hash
- Domain Auditor: per-domain pass/fail

**Pipeline Contracts:** Cross-cutting — audits all domains

**Snapshot Contracts:** Verifies all snapshots

**Worker Contracts:** Main thread

**Input:** All cards + all domains
**Output:** Audit report (pass/fail per domain)
**Forbidden:** Modifying audited domains

---

### 5.18 BENCHMARK

**Responsibilities:**
- WASIT 5-gate walk-forward validation (G1–G5)
- Parallel execution via Web Worker (fallback: sequential deterministic)
- Fold-based evaluation with majority voting
- Base vs candidate comparison
- Produce benchmark_snapshot (on-demand)

**Authority Contracts:**
- May: evaluate config changes, filter proposals
- Must NOT: approve (only filter for WASIT)

**Component Contracts:**
- WASIT 5-Gate: walk-forward validation
- WASIT Parallel: worker-based parallel execution
- Walk-Forward Engine: base vs candidate
- Fold Metrics: per-fold statistics
- Gate Evaluator: G1–G5 logic

**Pipeline Contracts:** Stage 15 — ON-DEMAND (not per candle)

**Snapshot Contracts:** Produces benchmark_snapshot (on-demand only)

**Worker Contracts:** Benchmark Worker (parallel base vs candidate)

**Input:** 2 configs + replay data
**Output:** benchmark_snapshot + verdict (PASS/FAIL)
**Forbidden:** Approving proposals (filter only)

---

### 5.19 VIEW

**Responsibilities:**
- Geometry Viewer: candle chart + supertrend + cage + markers
- Clone Viewer: 3 clone cards with observations + positions
- Trade Viewer: trade history table + equity curve
- Replay Viewer: scrubber + step + auto-play
- Knowledge Viewer: academy, oracle, hivemind, cermin, librarian
- Panel Renderer: indicator gauges, wave, cage, versioning
- Governance UI: proposals + approve/reject + rollback
- Simulation UI: type selector + results
- Prediction Display: empirical probabilities
- Consumer Display: trade intent + live-adapter status
- Audit Display: self-test + domain audit + fingerprint
- Final Validation Display: 12-domain validation

**Authority Contracts:**
- May: read all cards, render UI
- Must NOT: compute market logic; store truth in localStorage
- Empty = N/A (no mock values)

**Component Contracts:**
- Geometry Viewer: candle + ST + cage chart
- Clone Viewer: 3 clone cards
- Trade Viewer: table + equity curve
- Replay Viewer: scrubber + playback
- Knowledge Viewer: academy + oracle + cermin
- Panel Renderer: all indicator gauges
- Governance UI: proposal management
- Simulation UI: config + results
- Prediction Display: empirical summary
- Consumer Display: intent preview
- Audit Display: test results
- Final Validation: 12 checks

**Pipeline Contracts:** Cross-cutting — reads all cards

**Snapshot Contracts:** Reads all snapshots

**Worker Contracts:** Main thread (UI rendering)

**Input:** All cards via IndexedDB query
**Output:** Rendered UI
**Forbidden:** Computing market logic; mock values; storing truth in localStorage

---

### 5.20 FINAL VALIDATION

**Responsibilities:**
- 12 validation checks across all domains
- Runtime: state + frames + snapshots
- Pipeline: snapshots per frame
- Namespace: all 26 namespaces present
- Feature: 9 snapshot partitions per candle
- Truth Layer: st/stDir/color/atr/ema/rsi/wpr/macd/distAtr
- Clone: LONG/SHORT/GRID present
- Trading: entry→position→profit→exit→marker
- Knowledge: academy/oracle/hivemind/cermin/librarian/darwin
- Replay: 6 replay types
- Governance: 6 validations + WASIT + rollback
- Constitution: all audit tests pass
- Console Error: no swallowed errors

**Authority Contracts:**
- May: validate all domains
- Must NOT: modify validated domains

**Component Contracts:**
- Runtime Check: state/frames/snapshots
- Pipeline Check: snapshots per frame
- Namespace Check: 26 namespaces
- Feature Check: 9 snapshot partitions
- Truth Layer Check: geometry indicators
- Clone Check: 3 clones present
- Trading Check: entry→marker chain
- Knowledge Check: 6 entities
- Replay Check: 6 types
- Governance Check: 6 validations
- Constitution Check: audit tests
- Console Error Check: no swallowed errors

**Pipeline Contracts:** Cross-cutting — validates all domains

**Snapshot Contracts:** Verifies all snapshots

**Worker Contracts:** Main thread

**Input:** State + all domains
**Output:** 12 pass/fail results
**Forbidden:** Modifying validated domains

---

## 6. CROSS-CUTTING RULES

### 6.1 Unidirectional Flow
```
Data → Truth → Structure → Evidence → Clone → Sim → Knowledge → Consumer
```
- No backward loops to Core logic (LAW-MASTER-04)
- Only GOVERNANCE can write to BOUNDED parameters
- Knowledge/Consumer only read cards

### 6.2 Card Sharing
- Truth/Structure/Evidence computed 1× per candle
- Results shared to all 3 clones
- Clones do NOT compute geometry or raw indicators

### 6.3 Immutable Cards
- Every fact = frozen card + SHA-256 checksum + lineage
- Object.freeze on creation
- Update = new card version, never mutation in-place

### 6.4 Worker Architecture
- Main thread: hot, sequential per symbol (Truth/Structure/Evidence/Clone)
- Data Worker: batch bootstrap, TF aggregation (cold, dies after completion)
- Knowledge Worker: Academy batch, Oracle, Darwin, Librarian (cold)
- Benchmark Worker: WASIT walk-forward parallel (cold)
- Replay Worker: replay per symbol parallel (cold)
- Workers send results via postMessage; main thread persists to IndexedDB
- Workers MUST NOT write IndexedDB directly
- No setInterval for idle candle playback

### 6.5 Platform Binding
- SQLite → IndexedDB (append-only card store)
- ProcessPool → Web Worker (cold, dies after completion)
- File LZMA → CompressionStream + IndexedDB blob
- Float → BigInt integer-tick per-asset + canonical string (audit)
- PRNG → Mulberry32 seeded (ts + config_version)

### 6.6 Determinism
- No Date.now() in logic (time from candle timestamp)
- No Math.random() in logic (use seeded PRNG)
- Tie-break deterministic
- 2 runs with same seed → identical checksums

### 6.7 No-Fake Data
- NULL + status preferred over neutral fake values
- OI empty = INSUFFICIENT_DATA (not 5000)
- Wave < 6 = PENDING_WAVE (not padded)
- Sample insufficient = BELUM_CUKUP (not expressed confidence)
- Panel empty = N/A (not placeholder)

---

## ARCHITECTURE FREEZE STATUS: LOCKED

All 20 layers, their contracts, and their relationships are constitutionally frozen. No modification, addition, or removal of layers, components, contracts, or data flows is permitted without governance amendment per MASTER_SPECIFICATION §3.
