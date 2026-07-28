# DECISION TREE FREEZE — ST-LMS v3

## Native HTML Market Geometry Intelligence Operating System

**Date:** 2026-07-28
**Phase:** PHASE 0 — Prompt 03
**Status:** CONSTITUTIONALLY FROZEN
**Sources:** MASTER_SPECIFICATION.html, ST_LMS_CORE.js (CLONE_SHARED namespace), QWEN_14_DOC.html

---

## 1. ENTRY DECISION TREE

### 1.1 Directional Entry (LONG/SHORT)

```
                        ┌─────────────────────┐
                        │   NEW CLOSED CANDLE  │
                        └──────────┬──────────┘
                                   │
                        ┌──────────▼──────────┐
                        │   WARMUP PERIOD?    │
                        │ point_status=WARMUP │
                        └──────┬─────────┬────┘
                               │YES      │NO
                               ▼         │
                        ┌──────────┐     │
                        │ NO ENTRY │     │
                        │ OBSERVE  │     │
                        └──────────┘     │
                                         │
                              ┌──────────▼──────────┐
                              │  POSITION ALREADY   │
                              │      OPEN?          │
                              └──────┬─────────┬────┘
                                     │YES      │NO
                                     ▼         │
                              ┌──────────┐     │
                              │ NO ENTRY │     │
                              │ POSITION │     │
                              │  OPEN    │     │
                              └──────────┘     │
                                               │
                                    ┌──────────▼──────────┐
                                    │   stDir CONFIRMS    │
                                    │  LONG: stDir === 1  │
                                    │ SHORT: stDir === -1 │
                                    └──────┬─────────┬────┘
                                           │YES      │NO
                                           │         ▼
                                           │  ┌──────────────┐
                                           │  │  NO ENTRY    │
                                           │  │STDIR_MISMATCH│
                                           │  └──────────────┘
                                           │
                                ┌──────────▼──────────┐
                                │ DIRECTION BUS OK?   │
                                │ LONG: ema>5000 ∧    │
                                │       vd>5000       │
                                │SHORT: ema<5000 ∧    │
                                │       vd<5000       │
                                └──────┬─────────┬────┘
                                       │YES      │NO
                                       │         ▼
                                       │  ┌──────────────┐
                                       │  │  NO ENTRY    │
                                       │  │DIRBUS_MISMATCH│
                                       │  └──────────────┘
                                       │
                            ┌──────────▼──────────┐
                            │  CORRIDOR IN ZONE?  │
                            │  price in adaptive  │
                            │  entry corridor     │
                            └──────┬─────────┬────┘
                                   │YES      │NO
                                   │         ▼
                                   │  ┌──────────────┐
                                   │  │  NO ENTRY    │
                                   │  │OUT_OF_CORRIDOR│
                                   │  └──────────────┘
                                   │
                        ┌──────────▼──────────┐
                        │    FEE SAFE?        │
                        │LONG: dist_ceiling ≥ │
                        │      required_move  │
                        │SHORT: dist_floor ≥  │
                        │      required_move  │
                        └──────┬─────────┬────┘
                               │YES      │NO
                               │         ▼
                               │  ┌──────────────────┐
                               │  │    NO ENTRY      │
                               │  │EXPECTED_MOVE_LESS│
                               │  │_THAN_REQUIRED    │
                               │  └──────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │   GLOBAL RISK OK?   │
                    │   global_ok = true  │
                    └──────┬─────────┬────┘
                           │YES      │NO
                           │         ▼
                           │  ┌──────────────┐
                           │  │  NO ENTRY    │
                           │  │GLOBAL_RISK   │
                           │  │_BREACH       │
                           │  └──────────────┘
                           │
                    ┌──────▼──────┐
                    │   ENTER!    │
                    │  LONG/SHORT │
                    │ ENTRY_MARKER│
                    └─────────────┘
```

### 1.2 GRID Entry

```
                        ┌─────────────────────┐
                        │   NEW CLOSED CANDLE  │
                        └──────────┬──────────┘
                                   │
                        ┌──────────▼──────────┐
                        │    CAGE VALID?      │
                        │status=VALID_COMPRESS│
                        │  OR LOOSE_SIDEWAY   │
                        └──────┬─────────┬────┘
                               │YES      │NO
                               │         ▼
                               │  ┌──────────┐
                               │  │ NO ENTRY │
                               │  │CAGE_NONE │
                               │  └──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   FEE SAFE?         │
                    │ width ≥ 3 × req     │
                    └──────┬─────────┬────┘
                           │YES      │NO
                           │         ▼
                           │  ┌──────────┐
                           │  │ NO ENTRY │
                           │  │CAGE_TIGHT│
                           │  └──────────┘
                           │
                ┌──────────▼──────────┐
                │  BREAKOUT NONE?     │
                │cage.breakout = NONE │
                └──────┬─────────┬────┘
                       │YES      │NO
                       │         ▼
                       │  ┌──────────────────┐
                       │  │    NO ENTRY      │
                       │  │BREAKOUT_IMMINENT │
                       │  └──────────────────┘
                       │
            ┌──────────▼──────────┐
            │  PP IN BUY ZONE?    │
            │  pp < GRID_BUY_ZONE │
            │  _MAX ∧ fills<max   │
            └──────┬─────────┬────┘
                   │YES      │NO
                   │         │
                   ▼         ▼
            ┌──────────┐ ┌──────────┐
            │ENTER LONG│ │ PP IN    │
            │GRID FILL │ │SELL ZONE?│
            └──────────┘ │pp>GRID_  │
                         │SELL_ZONE │
                         │_MIN ∧    │
                         │fills<max │
                         └────┬───┬─┘
                            YES  NO
                             │    │
                             ▼    ▼
                       ┌────────┐┌────────┐
                       │ ENTER  ││  WAIT  │
                       │ SHORT  ││OBSERVE │
                       │GRID FILL│        │
                       └────────┘└────────┘
```

---

## 2. EXIT DECISION TREE

### 2.1 Directional Exit (LONG/SHORT)

```
                        ┌─────────────────────┐
                        │   POSITION OPEN     │
                        │   hold_c, mae, mfe  │
                        └──────────┬──────────┘
                                   │
                        ┌──────────▼──────────┐
                        │  WRONG ENTRY EARLY? │
                        │LONG: vel<-deadzone  │
                        │SHORT: vel>+deadzone │
                        │  ∧ hold_c ≤ 2      │
                        └──────┬─────────┬────┘
                               │YES      │NO
                               ▼         │
                        ┌──────────┐     │
                        │  EXIT    │     │
                        │WRONG_ENTRY│    │
                        │ _EARLY   │     │
                        └──────────┘     │
                                         │
                              ┌──────────▼──────────┐
                              │ WRONG ENTRY GEOM?   │
                              │ adverse ≥ WRONG_PCT  │
                              │  ∧ hold_c ≤ 2       │
                              └──────┬─────────┬────┘
                                     │YES      │NO
                                     ▼         │
                              ┌──────────┐     │
                              │  EXIT    │     │
                              │WRONG_ENTRY│    │
                              │ _GEOM    │     │
                              └──────────┘     │
                                               │
                                    ┌──────────▼──────────┐
                                    │ HYPOTHESIS INVALID? │
                                    │LONG:breakout=IMM_DN │
                                    │SHORT:breakout=IMM_UP│
                                    └──────┬─────────┬────┘
                                           │YES      │NO
                                           ▼         │
                                    ┌──────────┐     │
                                    │  EXIT    │     │
                                    │HYPOTHESIS│     │
                                    │_INVALID  │     │
                                    └──────────┘     │
                                                     │
                                          ┌──────────▼──────────┐
                                          │   STOP LOSS HIT?    │
                                          │LONG: low ≤ sl       │
                                          │SHORT: high ≥ sl     │
                                          └──────┬─────────┬────┘
                                                 │YES      │NO
                                                 ▼         │
                                          ┌──────────┐     │
                                          │  EXIT    │     │
                                          │   SL     │     │
                                          │at sl price│    │
                                          └──────────┘     │
                                                           │
                                                ┌──────────▼──────────┐
                                                │    HOLD VETO?       │
                                                │MACD expanding +     │
                                                │velocity with trend  │
                                                └──────┬─────────┬────┘
                                                       │YES      │NO
                                                       ▼         │
                                                ┌──────────┐     │
                                                │  HOLD    │     │
                                                │(delay TP)│     │
                                                └──────────┘     │
                                                                 │
                                                      ┌──────────▼──────────┐
                                                      │   TAKE PROFIT HIT?  │
                                                      │LONG: high ≥ tp      │
                                                      │SHORT: low ≤ tp      │
                                                      └──────┬─────────┬────┘
                                                             │YES      │NO
                                                             ▼         │
                                                      ┌──────────┐     │
                                                      │  EXIT    │     │
                                                      │   TP     │     │
                                                      │at tp price│    │
                                                      └──────────┘     │
                                                                       │
                                                            ┌──────────▼──────────┐
                                                            │    EXIT BUS?        │
                                                            │LONG: RSI>70 OR      │
                                                            │      W%R>-20        │
                                                            │SHORT: RSI<30 OR     │
                                                            │      W%R<-80        │
                                                            └──────┬─────────┬────┘
                                                                   │YES      │NO
                                                                   ▼         │
                                                            ┌──────────┐     │
                                                            │  EXIT    │     │
                                                            │EXIT_BUS  │     │
                                                            │at close  │     │
                                                            └──────────┘     │
                                                                             │
                                                                  ┌──────────▼──────────┐
                                                                  │    TIME EXIT?       │
                                                                  │hold≥TIME_EXIT ∧     │
                                                                  │profit < required    │
                                                                  └──────┬─────────┬────┘
                                                                         │YES      │NO
                                                                         ▼         │
                                                                  ┌──────────┐     │
                                                                  │  EXIT    │     │
                                                                  │TIME_EXIT │     │
                                                                  │at close  │     │
                                                                  └──────────┘     │
                                                                                   │
                                                                        ┌──────────▼──────────┐
                                                                        │   CONTINUE HOLD     │
                                                                        │  (no exit reason)   │
                                                                        │  update mae/mfe     │
                                                                        └─────────────────────┘
```

### 2.2 GRID Exit

```
                        ┌─────────────────────┐
                        │   GRID FILLS OPEN   │
                        │  per fill: side,    │
                        │  entry, oi_idx      │
                        └──────────┬──────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │     CAGE NO LONGER VALID?   │
                    │  status ≠ VALID_COMPRESSION │
                    │  AND ≠ LOOSE_SIDEWAY        │
                    └──────────────┬─────────────┘
                                   │YES
                                   ▼
                            ┌──────────────┐
                            │ CLOSE ALL    │
                            │RANGE_BREAK   │
                            └──────────────┘
                                   │NO
                                   │
                    ┌──────────────▼──────────────┐
                    │  BREAKOUT AGAINST FILL?     │
                    │LONG fill ∧ IMMINENT_DOWN    │
                    │SHORT fill ∧ IMMINENT_UP     │
                    └──────────────┬─────────────┘
                                   │YES
                                   ▼
                            ┌──────────────┐
                            │CLOSE THAT FILL│
                            │RANGE_BREAK   │
                            └──────────────┘
                                   │NO
                                   │
                    ┌──────────────▼──────────────┐
                    │    WRONG ENTRY?             │
                    │  adverse ≥ WRONG_ENTRY_PCT  │
                    └──────────────┬─────────────┘
                                   │YES
                                   ▼
                            ┌──────────────┐
                            │CLOSE THAT FILL│
                            │WRONG_ENTRY   │
                            └──────────────┘
                                   │NO
                                   │
                    ┌──────────────▼──────────────┐
                    │     GRID TP HIT?            │
                    │  profit ≥ required_move     │
                    └──────────────┬─────────────┘
                                   │YES
                                   ▼
                            ┌──────────────┐
                            │CLOSE THAT FILL│
                            │GRID_TP       │
                            └──────────────┘
                                   │NO
                                   ▼
                            ┌──────────────┐
                            │ CONTINUE HOLD│
                            │  all fills   │
                            └──────────────┘
```

---

## 3. POSITION DECISION TREE

```
                        ┌─────────────────────┐
                        │   POSITION OPEN     │
                        │ entry, sl, tp,      │
                        │ hold_c=0            │
                        └──────────┬──────────┘
                                   │
                        ┌──────────▼──────────┐
                        │  PER CANDLE UPDATE  │
                        │ hold_c += 1         │
                        │ mae = min(mae,adv)  │
                        │ mfe = max(mfe,fav)  │
                        └──────────┬──────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
    ┌─────────▼─────────┐ ┌───────▼───────┐ ┌─────────▼─────────┐
    │  PROFIT LOCK?     │ │ TRAILING?     │ │  BREAKEVEN?       │
    │ profit ≥ threshold│ │ATR trail act. │ │ profit ≥ activate  │
    └────────┬──────────┘ └───────┬───────┘ └────────┬──────────┘
             │YES                 │YES                │YES
             ▼                    ▼                   ▼
    ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
    │ PARTIAL CLOSE  │  │ MOVE SL BY ATR │  │ MOVE SL TO     │
    │ (PARTIAL_TP_PCT)│ │ BEHIND PRICE   │  │ ENTRY PRICE    │
    │ MOVE SL TO     │  │                │  │                │
    │ ENTRY          │  │                │  │                │
    └────────────────┘  └────────────────┘  └────────────────┘
             │NO                  │NO                 │NO
             │                    │                   │
             └────────────────────┼───────────────────┘
                                  │
                       ┌──────────▼──────────┐
                       │  CHECK EXIT TREE    │
                       │  (see §2 above)     │
                       └──────────┬──────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │EXIT         │             │NO EXIT
                    ▼             │             ▼
             ┌──────────┐        │      ┌──────────────┐
             │  CLOSE   │        │      │CONTINUE HOLD │
             │ POSITION │        │      │(next candle) │
             │EXIT_MARKER│       │      └──────────────┘
             └──────────┘        │
                                 │
                    ┌────────────▼────────────┐
                    │   COMPUTE P&L           │
                    │ gross = (exit-entry)/   │
                    │         entry × 100     │
                    │ net = gross - fee - slip│
                    │ result = WIN/LOSS/BREAK │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   UPDATE STATISTICS     │
                    │   UPDATE ACADEMY        │
                    │   UPDATE EQUITY CURVE   │
                    └─────────────────────────┘
```

---

## 4. CORRECTION DECISION TREE

```
                        ┌─────────────────────┐
                        │   MARKET CONTEXT    │
                        │ (per candle, per    │
                        │  clone observation) │
                        └──────────┬──────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
    ┌─────────▼─────────┐ ┌───────▼───────┐ ┌─────────▼─────────┐
    │ PRICE POSITION?   │ │MARKET PHASE?  │ │ WAVE STRUCTURE?   │
    │ pp = (close-lower)│ │TREND / SIDEWAY│ │ 13 wave types     │
    │ / (upper-lower)   │ │               │ │                   │
    └────────┬──────────┘ └───────┬───────┘ └────────┬──────────┘
             │                    │                    │
             └────────────────────┼────────────────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
          ┌─────────▼──┐  ┌──────▼──────┐ ┌────▼──────────┐
          │DIST CEILING│  │ DIST FLOOR  │ │CAGE BREAKOUT  │
          │upper-close │  │close-lower  │ │NONE/IMM_UP/   │
          │NULL if no  │  │NULL if no   │ │IMM_DN/SQUEEZE │
          │upper wall  │  │lower wall   │ │               │
          └────────────┘  └─────────────┘ └───────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │  CORRECTION DECISION      │
                    │                           │
                    │  TREND:                   │
                    │    - No GRID entry        │
                    │    - Directional active   │
                    │    - Watch for exhaustion │
                    │                           │
                    │  SIDEWAY:                 │
                    │    - GRID active          │
                    │    - Directional observe  │
                    │    - Watch for breakout   │
                    │                           │
                    │  REVERSAL:                │
                    │    - No entry             │
                    │    - Close existing       │
                    │    - Observe new trend    │
                    └───────────────────────────┘
```

---

## 5. REENTRY DECISION TREE

```
                        ┌─────────────────────┐
                        │  POSITION CLOSED    │
                        │  (WIN / LOSS / BREAK│
                        │   EVEN)             │
                        └──────────┬──────────┘
                                   │
                        ┌──────────▼──────────┐
                        │   SAME CANDLE?      │
                        │(entry + exit same   │
                        │     candle)         │
                        └──────┬─────────┬────┘
                               │YES      │NO
                               ▼         │
                        ┌──────────┐     │
                        │NO REENTRY│     │
                        │(1 pos per │     │
                        │ candle)   │     │
                        └──────────┘     │
                                         │
                              ┌──────────▼──────────┐
                              │   NEXT CANDLE       │
                              │ (new evaluation)    │
                              └──────────┬──────────┘
                                         │
                              ┌──────────▼──────────┐
                              │  CHECK ENTRY TREE   │
                              │  (see §1 above)     │
                              └──────────┬──────────┘
                                         │
                           ┌─────────────┼─────────────┐
                           │ALL PASS     │             │ANY FAIL
                           ▼             │             ▼
                    ┌──────────────┐     │      ┌──────────────┐
                    │   REENTER    │     │      │    WAIT      │
                    │ NEW POSITION │     │      │  (observe)   │
                    └──────────────┘     │      └──────────────┘
                                         │
                    ┌────────────────────▼────────────────────┐
                    │  REENTRY RULES:                          │
                    │  - No cooldown period enforced           │
                    │  - Entry conditions re-evaluated fresh   │
                    │  - Previous trade outcome recorded in    │
                    │    statistics (does not affect reentry)  │
                    │  - Only 1 position per clone at a time   │
                    └─────────────────────────────────────────┘
```

---

## 6. NO TRADE DECISION TREE

```
                        ┌─────────────────────┐
                        │   NEW CLOSED CANDLE  │
                        └──────────┬──────────┘
                                   │
                        ┌──────────▼──────────┐
                        │  ENTRY CONDITIONS   │
                        │  EVALUATED          │
                        └──────────┬──────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
    ┌─────────▼─────────┐        ...         ┌─────────▼─────────┐
    │ ANY CONDITION     │                    │ ALL CONDITIONS    │
    │ FAILED            │                    │ PASSED            │
    └────────┬──────────┘                    └────────┬──────────┘
             │                                        │
             ▼                                        ▼
    ┌────────────────┐                      ┌────────────────┐
    │   NO TRADE     │                      │    ENTER       │
    │                │                      │   TRADE        │
    └───────┬────────┘                      └────────────────┘
            │
            ▼
    ┌────────────────────────────────────────────┐
    │  PRODUCE OBSERVATION CARD (MANDATORY)       │
    │                                              │
    │  entry_allowed = false                       │
    │  no_entry_reason = {reason}                  │
    │  setup_score = 2500 (reduced)                │
    │  confidence = 2500                           │
    │                                              │
    │  REASONS:                                    │
    │  - STDIR_OR_DIRBUS_MISMATCH                  │
    │  - OUT_OF_CORRIDOR                           │
    │  - EXPECTED_MOVE_LESS_THAN_REQUIRED          │
    │  - GLOBAL_RISK_BREACH                        │
    │  - POSITION_ALREADY_OPEN                     │
    │  - CAGE_NONE (GRID)                          │
    │  - WARMUP                                    │
    └────────────────────────────────────────────┘

    NO TRADE ≠ SKIP:
    - Observation is MANDATORY per LAW-MASTER-06
    - 1 candle = 3 knowledge events (LONG + SHORT + GRID)
    - Even if all 3 clones have no trade, all 3 produce observation cards
```

---

## 7. WAIT DECISION TREE

```
                        ┌─────────────────────┐
                        │  POSITION CLOSED    │
                        │  OR NO POSITION     │
                        └──────────┬──────────┘
                                   │
                        ┌──────────▼──────────┐
                        │  MARKET STATE       │
                        │  EVALUATED          │
                        └──────────┬──────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
    ┌─────────▼─────────┐ ┌───────▼───────┐ ┌─────────▼─────────┐
    │    WARMUP         │ │   TRENDING    │ │    SIDEWAY        │
    │insufficient data  │ │cage = NONE    │ │cage = VALID/LOOSE │
    └────────┬──────────┘ └───────┬───────┘ └────────┬──────────┘
             │                    │                    │
             ▼                    ▼                    ▼
    ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
    │   WAIT         │  │ DIRECTIONAL    │  │  GRID ACTIVE   │
    │ all clones     │  │ CLONES ACTIVE  │  │  DIRECTIONAL   │
    │ observe only   │  │ GRID WAITS     │  │  WAITS         │
    └────────────────┘  └────────────────┘  └────────────────┘

    WAIT STATES:
    ┌──────────────────────────────────────────────────────────────┐
    │ STATE           │ LONG  │ SHORT │ GRID  │ REASON            │
    ├──────────────────┼───────┼───────┼───────┼───────────────────┤
    │ WARMUP          │ WAIT  │ WAIT  │ WAIT  │ Insufficient data │
    │ UPTREND         │ ACTIVE│ WAIT  │ WAIT  │ stDir = +1        │
    │ DOWNTREND       │ WAIT  │ ACTIVE│ WAIT  │ stDir = -1        │
    │ SIDEWAY_COMPRES │ WAIT  │ WAIT  │ ACTIVE│ cage valid        │
    │ REVERSAL        │ WAIT  │ WAIT  │ WAIT  │ trend flipping    │
    │ CHAOS           │ WAIT  │ WAIT  │ WAIT  │ no clear structure│
    │ EXHAUSTION_UP   │ WAIT  │ WAIT  │ WAIT  │ trend exhausting  │
    │ EXHAUSTION_DOWN │ WAIT  │ WAIT  │ WAIT  │ trend exhausting  │
    │ BREAKOUT        │ ACTIVE│ ACTIVE│ WAIT  │ cage breaking     │
    └──────────────────┴───────┴───────┴───────┴───────────────────┘

    WAIT RULES:
    - Observation still produced (mandatory)
    - no_entry_reason explains why waiting
    - setup_score and confidence still computed
    - Wait is NOT passive — it's active observation
```

---

## 8. LEARNING DECISION TREE

```
                        ┌─────────────────────┐
                        │   TRADE COMPLETED   │
                        │  (EXIT_MARKER)      │
                        └──────────┬──────────┘
                                   │
                        ┌──────────▼──────────┐
                        │  RECORD TO RIVER    │
                        │  (append-only)      │
                        └──────────┬──────────┘
                                   │
                        ┌──────────▼──────────┐
                        │  ACADEMY UPDATE     │
                        │  bucket = clone |   │
                        │  structure |        │
                        │  dist_bucket |      │
                        │  reason             │
                        └──────────┬──────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
    ┌─────────▼─────────┐ ┌───────▼───────┐ ┌─────────▼─────────┐
    │ ORACLE UPDATE     │ │HIVEMIND UPDATE│ │ LIBRARIAN UPDATE  │
    │ push vector +     │ │ synthesize    │ │ evaluate bucket   │
    │ outcome to hist   │ │ understanding │ │ lifecycle status  │
    └────────┬──────────┘ └───────┬───────┘ └────────┬──────────┘
             │                    │                    │
             └────────────────────┼────────────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │     CERMIN UPDATE         │
                    │ calibration_error =       │
                    │ actual_win_rate -         │
                    │ predicted_confidence      │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │     DARWIN CHECK          │
                    │ if expectancy < 0 →       │
                    │   propose TIGHTEN_ENTRY   │
                    │ if wrong_rate > 30 →      │
                    │   propose TIGHTEN_WRONG   │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │     PREDICTION UPDATE     │
                    │ empirical_win_rate per    │
                    │ clone from Academy        │
                    │ similarity_score from     │
                    │ Oracle                    │
                    │ intelligence_score from   │
                    │ HiveMind                  │
                    └───────────────────────────┘

    LEARNING RULES:
    - All learning is AFTER trade completion (not during)
    - Unidirectional: no write-back to Core/Clone
    - No ML: purely statistical/empirical
    - Sample-gated: BELUM_CUKUP if sample < 30
```

---

## 9. STATISTICS DECISION TREE

```
                        ┌─────────────────────┐
                        │  ALL TRADE MARKERS  │
                        │  (EXIT kind only)   │
                        └──────────┬──────────┘
                                   │
                        ┌──────────▼──────────┐
                        │  GROUP BY CLONE     │
                        │  LONG / SHORT / GRID│
                        └──────────┬──────────┘
                                   │
                        ┌──────────▼──────────┐
                        │  COUNT SAMPLE       │
                        │  n = count of exits │
                        └──────────┬──────────┘
                                   │
                        ┌──────────▼──────────┐
                        │  SAMPLE GATE        │
                        │  n ≥ SAMPLE_GATE?   │
                        └──────┬─────────┬────┘
                               │YES      │NO
                               │         ▼
                               │  ┌──────────────┐
                               │  │ BELUM_CUKUP  │
                               │  │ no confidence│
                               │  │ expressed    │
                               │  └──────────────┘
                               │
                    ┌──────────▼──────────┐
                    │  COMPUTE METRICS    │
                    │                     │
                    │ win_rate = wins/n   │
                    │ expectancy = Σnet/n │
                    │ pf = Σgross_pos /   │
                    │      Σ|gross_neg|   │
                    │ mae = Σ|mae|/n      │
                    │ mfe = Σmfe/n        │
                    │ fee_drag = Σfee/n   │
                    │ wrong_rate = wrong/n│
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   STATUS = CUKUP    │
                    │   statistics valid  │
                    │   for decision use  │
                    └─────────────────────┘

    STATISTICS RULES:
    - Per clone, not mixed across clones
    - Sample-gated (≥ 30 for CUKUP)
    - WIN only if net > 0
    - PF = null if no losses (no denominator)
    - Below gate → BELUM_CUKUP (not expressed as confidence)
```

---

## 10. KNOWLEDGE DECISION TREE

```
                        ┌─────────────────────┐
                        │  STATISTICS READY   │
                        │  + TRADE MARKERS    │
                        └──────────┬──────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
    ┌─────────▼─────────┐ ┌───────▼───────┐ ┌─────────▼─────────┐
    │    ACADEMY        │ │    ORACLE     │ │    HIVEMIND      │
    │ win_rate per      │ │ similarity    │ │ understanding    │
    │ 4-dim bucket      │ │ euclidean     │ │ synthesis        │
    └────────┬──────────┘ └───────┬───────┘ └────────┬──────────┘
             │                    │                    │
             │           ┌────────▼────────┐          │
             │           │  MATCH > 7500?  │          │
             │           └────┬───────┬────┘          │
             │                │YES    │NO             │
             │                ▼       ▼               │
             │         ┌─────────┐ ┌─────────┐       │
             │         │MATCH    │ │NO MATCH │       │
             │         │score    │ │score<   │       │
             │         │>7500   │ │7500    │       │
             │         └─────────┘ └─────────┘       │
             │                                       │
             └───────────────────┬───────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │  KNOWLEDGE DECISION     │
                    │                         │
                    │  Academy CUKUP?         │
                    │    YES → use win_rate   │
                    │    NO → BELUM_CUKUP     │
                    │                         │
                    │  Oracle match?          │
                    │    YES → pattern_boost  │
                    │    NO → no boost        │
                    │                         │
                    │  HiveMind score?        │
                    │    > 6500 → BULLISH     │
                    │    < 3500 → BEARISH     │
                    │    else → NEUTRAL       │
                    │                         │
                    │  CERMIN calibration?    │
                    │    error tracked        │
                    │    for confidence       │
                    │    honesty              │
                    │                         │
                    │  Librarian lifecycle?   │
                    │    NEW → OBS → TRUSTED  │
                    │    → MATURE / DEAD /    │
                    │    DEPRECATED           │
                    └─────────────────────────┘
```

---

## 11. PREDICTION DECISION TREE

```
                        ┌─────────────────────┐
                        │  KNOWLEDGE READY    │
                        │  (Academy + Oracle  │
                        │   + HiveMind +      │
                        │   CERMIN)           │
                        └──────────┬──────────┘
                                   │
                        ┌──────────▼──────────┐
                        │  ACADEMY CUKUP?     │
                        │  sample ≥ 30 per    │
                        │  clone              │
                        └──────┬─────────┬────┘
                               │YES      │NO
                               │         ▼
                               │  ┌──────────────┐
                               │  │ BELUM_CUKUP  │
                               │  │ win_rate =   │
                               │  │ NULL         │
                               │  └──────────────┘
                               │
                    ┌──────────▼──────────┐
                    │  COMPUTE PREDICTION │
                    │                     │
                    │ intelligence_score  │
                    │  = 5000             │
                    │  + pattern_boost    │
                    │  + oracle_boost     │
                    │  + evidence_adj     │
                    │                     │
                    │ dominant_bias =     │
                    │  score>6500→BULLISH │
                    │  score<3500→BEARISH │
                    │  else→NEUTRAL       │
                    │                     │
                    │ empirical_win_rate  │
                    │  per clone from     │
                    │  Academy            │
                    │                     │
                    │ similarity_score    │
                    │  from Oracle        │
                    │                     │
                    │ no_model = true     │
                    │  (always)           │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  PREDICTION OUTPUT  │
                    │  (prediction_snap)  │
                    └─────────────────────┘

    PREDICTION RULES:
    - Empirical only (no forecasting model)
    - no_model = true (always)
    - NULL if sample insufficient
    - calibration_error from CERMIN included
    - Forbidden: predictive model output
```

---

## 12. STATE TRANSITION DIAGRAM

```
                    ┌─────────────────────────────────────────┐
                    │           ST-LMS TRADING STATES          │
                    └─────────────────────────────────────────┘

                                    ┌──────────┐
                                    │  WARMUP  │
                                    │(no entry)│
                                    └────┬─────┘
                                         │ indicators ready
                                         ▼
                              ┌─────────────────────┐
                              │     OBSERVING       │◄──────────────────────┐
                              │ (evaluating market) │                       │
                              └──────────┬──────────┘                       │
                                         │                                  │
                    ┌────────────────────┼────────────────────┐             │
                    │ENTRY               │                    │NO ENTRY     │
                    ▼                    │                    ▼             │
            ┌──────────────┐            │            ┌──────────────┐      │
            │  POSITION    │            │            │  NO TRADE    │      │
            │   OPEN       │            │            │(observation  │      │
            │ LONG/SHORT/  │            │            │  recorded)   │──────┘
            │   GRID       │            │            └──────────────┘
            └──────┬───────┘            │
                   │                    │
    ┌──────────────┼──────────────┐     │
    │EXIT          │              │     │
    ▼              ▼              ▼     │
┌────────┐  ┌──────────┐  ┌──────────┐ │
│  WIN   │  │  LOSS    │  │BREAKEVEN │ │
│net > 0│  │ net < 0  │  │ net = 0  │ │
└───┬────┘  └────┬─────┘  └────┬─────┘ │
    │            │              │       │
    └────────────┼──────────────┘       │
                 │                      │
                 ▼                      │
        ┌────────────────┐             │
        │   STATISTICS   │             │
        │   UPDATED      │             │
        └───────┬────────┘             │
                │                      │
        ┌───────▼────────┐             │
        │   KNOWLEDGE    │             │
        │   UPDATED      │             │
        └───────┬────────┘             │
                │                      │
        ┌───────▼────────┐             │
        │  NEXT CANDLE   │─────────────┘
        │ (back to       │
        │  OBSERVING)    │
        └────────────────┘
```

---

## 13. TRADING STATE DIAGRAM (PER CLONE)

```
┌──────────────────────────────────────────────────────────────────────────┐
│                        CLONE TRADING STATE MACHINE                        │
│                        (LONG / SHORT / GRID)                              │
└──────────────────────────────────────────────────────────────────────────┘

                              ┌─────────────┐
                              │   WARMUP    │
                              │ (no entry)  │
                              └──────┬──────┘
                                     │ indicators valid
                                     ▼
                    ┌────────────────────────────────┐
                    │           OBSERVING            │◄─────────────────────┐
                    │  ┌──────────┐ ┌─────────────┐ │                      │
                    │  │TRENDING  │ │  SIDEWAY    │ │                      │
                    │  │UP (LONG  │ │COMPRESSION  │ │                      │
                    │  │ active)  │ │(GRID active)│ │                      │
                    │  └──────────┘ └─────────────┘ │                      │
                    └───────────────┬────────────────┘                      │
                                    │                                       │
                         ┌──────────┼──────────┐                            │
                         │ENTRY     │          │NO ENTRY                    │
                         ▼          │          ▼                            │
                  ┌─────────────┐  │   ┌─────────────┐                     │
                  │  POSITION   │  │   │  NO TRADE   │                     │
                  │    OPEN     │  │   │ (observation │                     │
                  │             │  │   │  recorded)  │─────────────────────┘
                  │ hold_c = 0  │  │   └─────────────┘
                  └──────┬──────┘  │
                         │         │
                  ┌──────▼──────┐  │
                  │  MANAGING   │  │
                  │  POSITION   │  │
                  │             │  │
                  │ hold_c += 1 │  │
                  │ mae/mfe upd │  │
                  └──────┬──────┘  │
                         │         │
            ┌────────────┼─────────┼────────────┐
            │EXIT        │         │            │
            ▼            ▼         ▼            │
    ┌───────────┐ ┌──────────┐ ┌──────────┐    │
    │ WRONG     │ │  NORMAL  │ │  TIME    │    │
    │ ENTRY     │ │  EXIT    │ │  EXIT    │    │
    │ (hold≤2)  │ │(SL/TP/   │ │(hold≥    │    │
    │           │ │ EXIT_BUS)│ │ TIME_EXIT│    │
    └─────┬─────┘ └────┬─────┘ └────┬─────┘    │
          │            │            │           │
          └────────────┼────────────┘           │
                       │                        │
                       ▼                        │
              ┌────────────────┐               │
              │  POSITION      │               │
              │  CLOSED        │               │
              │  (P&L computed)│               │
              └───────┬────────┘               │
                      │                        │
                      ▼                        │
              ┌────────────────┐               │
              │  NEXT CANDLE   │───────────────┘
              │  (re-evaluate  │
              │   entry conds) │
              └────────────────┘
```

---

## DECISION TREE FREEZE STATUS: LOCKED

All 11 decision trees, all trading states, and all state transitions are constitutionally frozen. No new decision logic may be added. No existing decision logic may be modified. This document reflects the complete trading decision architecture as specified in MASTER_SPECIFICATION.html, QWEN_14_DOC.html, and implemented in ST_LMS_CORE.js (CLONE_SHARED namespace).
