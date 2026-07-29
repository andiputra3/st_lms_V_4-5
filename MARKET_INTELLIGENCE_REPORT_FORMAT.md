# MARKET INTELLIGENCE REPORT FORMAT

## ST-LMS v3 — Phase 0.5 Implementation Enrichment

**Date:** 2026-07-29
**Status:** FORMAT DEFINITION — FROZEN

---

## FORMAT OVERVIEW

Market Intelligence Report adalah output utama ST-LMS. Report ini menggabungkan seluruh layer menjadi satu laporan utuh yang dapat dibaca manusia maupun mesin.

---

## SECTION 1: HEADER

```
══════════════════════════════════════════════════════════════
  ST-LMS MARKET INTELLIGENCE REPORT
══════════════════════════════════════════════════════════════
  Report ID:    MIR_20260729_113000
  Symbol:       BTCUSDT
  Exchange:     Binance Futures
  Timeframe:    1m
  Session:      2026-07-29 11:00-11:30 WIB
  Generated:    2026-07-29 11:30:00 WIB
  Version:      1.0
  Pipeline:     23 stages | 5 simulators validated
══════════════════════════════════════════════════════════════
```

**Fields:**
| Field | Type | Source |
|-------|------|--------|
| report_id | string | IDGenerator |
| symbol | string | SymbolManager |
| exchange | string | MARKET |
| timeframe | string | MARKET |
| session | string | TimeManager |
| generated_at | string (ISO 8601) | TimeManager |
| version | string | CONFIG |
| pipeline_info | string | INTEGRATION |

---

## SECTION 2: PRESENT

```
──────────────────────────────────────────────────────────────
  PRESENT — Current Market Snapshot
──────────────────────────────────────────────────────────────
  Phase:        SIDEWAY_COMPRESSION
  Price:        62150 USDT
  Range:        61800 - 62500 (700 USDT / 1.12%)
  Volume:       125.3 BTC (last candle)
  OI:           125.6M USDT (+4% accumulation)
  Gap:          None
  Data Quality: OK
```

**Fields:**
| Field | Type | Source |
|-------|------|--------|
| phase | string | STRUCTURE |
| price | float | TRUTH |
| range_low | float | STRUCTURE.cage.lower |
| range_high | float | STRUCTURE.cage.upper |
| range_pct | float | computed |
| volume | float | MARKET |
| oi_value | float | MARKET |
| oi_trend | string | TRUTH |
| gap_flag | boolean | MARKET |
| data_quality | string | EVIDENCE |

---

## SECTION 3: PAST

```
──────────────────────────────────────────────────────────────
  PAST — Historical Context
──────────────────────────────────────────────────────────────
  Session Start:   62300 USDT
  Session High:    62800 USDT
  Session Low:     61750 USDT
  Compression #:   3rd cycle this session
  Previous Cycle:  61800-62600 (wider)
  Pattern Match:   73% similar to historical COMPRESSION_BREAKOUT
  Oracle Match:    YES (similarity 8200)
```

**Fields:**
| Field | Type | Source |
|-------|------|--------|
| session_start_price | float | MARKET |
| session_high | float | MARKET |
| session_low | float | MARKET |
| compression_count | int | BAG |
| previous_range | string | BAG |
| pattern_match | string | KNOWLEDGE.Oracle |
| similarity_score | float | KNOWLEDGE.Oracle |

---

## SECTION 4: FUTURE

```
──────────────────────────────────────────────────────────────
  FUTURE — Market Possibility
──────────────────────────────────────────────────────────────
  Breakout UP:           82%  ████████████████████░
  Continuation Range:    12%  ███░░░░░░░░░░░░░░░░░░
  Reversal DOWN:          4%  █░░░░░░░░░░░░░░░░░░░░
  Fake Breakout:          2%  ░░░░░░░░░░░░░░░░░░░░░░

  OI Context:  ACCUMULATION supports breakout thesis
```

**Fields:**
| Field | Type | Source |
|-------|------|--------|
| possibilities | list[{type, probability}] | PREDICTION |
| oi_context | string | PREDICTION |

---

## SECTION 5: MARKET CHARACTER

```
──────────────────────────────────────────────────────────────
  MARKET CHARACTER
──────────────────────────────────────────────────────────────
  Profile:      MEAN_REVERSION with BREAKOUT tendency
  Behavior:     Range-bound accumulation, building pressure
  DNA:          BTCUSDT favors breakout after 3rd compression
  Biography:    Consistent compression -> breakout pattern
  Evolution:    Range tightening (1.5% -> 1.3% -> 1.12%)
  Confidence:   87/100
```

**Fields:**
| Field | Type | Source |
|-------|------|--------|
| profile | string | BAG.behavior_profile |
| behavior | string | BAG |
| dna | string | KNOWLEDGE |
| biography | string | KNOWLEDGE.River |
| evolution | string | BAG.sequence_analysis |
| confidence | float | BAG.maturity_score |

---

## SECTION 6: SUPERTREND INFORMATION

```
──────────────────────────────────────────────────────────────
  SUPERTREND
──────────────────────────────────────────────────────────────
  Value:        62150
  Direction:    UP (+1)
  Color:        HIJAU
  Distance:     0.15 ATR (NEAR — very close to ST)
  EMA:          62200 (above ST, rising)
  ATR:          95 USDT (0.15%)
  RSI:          52 (neutral)
  W%R:          -35 (neutral)
  MACD:         +3.2 (bullish, expanding)
  Volume Delta: +0.15 (buying pressure)
  Status:       VALID (not warmup)
```

**Fields:**
| Field | Type | Source |
|-------|------|--------|
| st_value | float | TRUTH |
| st_direction | int | TRUTH |
| st_color | string | TRUTH |
| dist_atr | float | TRUTH |
| dist_bucket | string | DISTANCE |
| ema | float | TRUTH |
| atr | float | TRUTH |
| rsi | float | TRUTH |
| wpr | float | TRUTH |
| macd_hist | float | TRUTH |
| volume_delta | float | TRUTH |
| point_status | string | TRUTH |

---

## SECTION 7: LINE INFORMATION

```
──────────────────────────────────────────────────────────────
  SUPERTREND LINES
──────────────────────────────────────────────────────────────
  Active Line:  Support at 61800 (5 candles, strong)
  Previous:     Support at 61750 (broken)
  Next:         Resistance at 62500 (testing)
  OI Profile:   Avg 124M, ACCUMULATION (+2.5%)
  Line Count:   3 lines formed
```

**Fields:**
| Field | Type | Source |
|-------|------|--------|
| active_lines | list[{role, value, members, strength}] | STRUCTURE.LineBuilder |
| oi_profile | {avg, trend, delta_pct} | STRUCTURE (payload_json) |
| line_count | int | STRUCTURE |

---

## SECTION 8: WAVE INFORMATION

```
──────────────────────────────────────────────────────────────
  WAVE
──────────────────────────────────────────────────────────────
  Structure:    RANGE_COMPRESSING
  Lines:        6 (3 support, 3 resistance)
  Status:       CLOSED_WAVE
  OI Behavior:  ACCUMULATION
  OI Interpret: Smart money accumulating before breakout
  MTF Sector:   COMPRESSION (7000)
```

**Fields:**
| Field | Type | Source |
|-------|------|--------|
| structure | string | STRUCTURE.WaveBuilder |
| line_count | int | STRUCTURE |
| status | string | STRUCTURE |
| oi_behavior | string | STRUCTURE (payload_json) |
| oi_interpretation | string | STRUCTURE (payload_json) |
| mtf_sector | string | EVIDENCE |

---

## SECTION 9: OPEN INTEREST INFORMATION

```
──────────────────────────────────────────────────────────────
  OPEN INTEREST
──────────────────────────────────────────────────────────────
  Current:      125.6M USDT
  Delta:        +2.5M (+2.03%)
  Trend:        ACCUMULATION (rising over last 30 min)
  Source:       Binance Futures API
  Timeframe:    5m
  Ownership:    1 OI slot covers 5 Supertrend Points
  Status:       OK
```

**Fields:**
| Field | Type | Source |
|-------|------|--------|
| current_value | float | MARKET |
| delta | float | MARKET |
| delta_pct | float | MARKET |
| trend | string | TRUTH |
| source | string | MARKET |
| timeframe | string | MARKET |
| ownership_model | string | OI Ownership Contract |
| status | string | MARKET |

---

## SECTION 10: SNAPSHOT INFORMATION

```
──────────────────────────────────────────────────────────────
  SNAPSHOTS
──────────────────────────────────────────────────────────────
  Total:        1000 snapshots (100 SP x 10 types)
  Market:       100 (OK)
  Truth:        100 (VALID)
  Structure:    100 (cage=COMPRESSION, wave=RANGE)
  Evidence:     100 (3 buses active)
  Clone:        300 (LONG+SHORT+GRID)
  Trade:        12 markers
  Statistics:   100 (all CUKUP)
  Knowledge:    100 (7 entities)
  Benchmark:    0 (on-demand)
  Prediction:   100 (no-model, empirical)
```

**Fields:**
| Field | Type | Source |
|-------|------|--------|
| total | int | SNAPSHOT |
| per_type | dict[string, int] | SNAPSHOT |
| sp_count | int | TRUTH |
| trade_marker_count | int | TRADE |

---

## SECTION 11: KNOWLEDGE INFORMATION

```
──────────────────────────────────────────────────────────────
  KNOWLEDGE
──────────────────────────────────────────────────────────────
  Academy:      COMPRESSION_BREAKOUT = 73% win (47 samples)
  Oracle:       Match found (similarity 8200)
  HiveMind:     BULLISH bias (intelligence 7200)
  CERMIN:       +3% overconfident (acceptable)
  Librarian:    COMPRESSION_BREAKOUT = MATURE
  Darwin:       No proposals (performance healthy)
```

**Fields:**
| Field | Type | Source |
|-------|------|--------|
| academy_top | {pattern, win_rate, sample} | KNOWLEDGE.Academy |
| oracle | {match, score} | KNOWLEDGE.Oracle |
| hivemind | {score, bias} | KNOWLEDGE.HiveMind |
| cermin | {error, interpretation} | KNOWLEDGE.CERMIN |
| librarian | {top_status} | KNOWLEDGE.Librarian |
| darwin | {proposal_count} | KNOWLEDGE.Darwin |

---

## SECTION 12: PREDICTION INFORMATION

```
──────────────────────────────────────────────────────────────
  PREDICTION (Market Possibility — NOT Trading Signal)
──────────────────────────────────────────────────────────────
  Primary:      Breakout UP (82%)
  Secondary:    Continuation Range (12%)
  Tertiary:     Reversal DOWN (4%)
  Warning:      Fake Breakout (2%)

  Supporting:
    Price:      STRONG
    Structure:  STRONG
    Volume:     MODERATE
    OI:         STRONG
    Knowledge:  STRONG

  Model:        EMPIRICAL (no AI/ML)
  Confidence:   82/100
```

**Fields:**
| Field | Type | Source |
|-------|------|--------|
| possibilities | list[{type, probability}] | PREDICTION |
| supporting_factors | dict | PREDICTION |
| model_type | string = "EMPIRICAL" | PREDICTION |
| confidence | float | PREDICTION |

---

## SECTION 13: TRADING SCHEMA INFORMATION

```
──────────────────────────────────────────────────────────────
  TRADING SCHEMA
──────────────────────────────────────────────────────────────
  Market:       SIDEWAY_COMPRESSION
  Primary:      GRID_COMPRESSION (89% confidence)
  Secondary:    LONG_BREAKOUT (72% confidence)
  Active:       GRID (LONG observing, SHORT waiting)
  Category:     Market=SIDEWAY, Trading=GRID, Entry=COMPRESSION
```

**Fields:**
| Field | Type | Source |
|-------|------|--------|
| market_schema | string | TRADING_SCHEMA |
| primary_schema | string | TRADING_SCHEMA |
| secondary_schema | string | TRADING_SCHEMA |
| active_clones | list[string] | CLONE |
| schema_category | string | TRADING_SCHEMA |

---

## SECTION 14: ENTRY TRUTH

```
──────────────────────────────────────────────────────────────
  ENTRY TRUTH
──────────────────────────────────────────────────────────────
  Strategy:     GRID_COMPRESSION
  Zone:         BUY at 61800-61850
  Condition:    Bounce from support + volume confirmation
  Fee Safe:     YES (1.12% >= 3x 0.7%)
  Corridor:     In zone (pp=0.25)
  Confidence:   89/100
```

**Fields:**
| Field | Type | Source |
|-------|------|--------|
| strategy | string | TRADING_TRUTH |
| entry_zone | string | TRADING_TRUTH |
| condition | string | TRADING_TRUTH |
| fee_safe | boolean | TRADE |
| corridor_ok | boolean | CLONE |
| confidence | float | TRADING_TRUTH |

---

## SECTION 15: POSITION TRUTH

```
──────────────────────────────────────────────────────────────
  POSITION TRUTH
──────────────────────────────────────────────────────────────
  Max Fills:    2 per side
  Current:      0 (preparing)
  Stop Loss:    61750 (below support)
  Take Profit:  62500 (cage.upper)
  Risk/Reward:  1:4.6
  Hold Target:  5-15 candles
```

**Fields:**
| Field | Type | Source |
|-------|------|--------|
| max_fills | int | CONFIG |
| current_fills | int | POSITION |
| stop_loss | float | POSITION |
| take_profit | float | POSITION |
| risk_reward | float | computed |
| hold_target | string | TRADING_TRUTH |

---

## SECTION 16: EXIT TRUTH

```
──────────────────────────────────────────────────────────────
  EXIT TRUTH
──────────────────────────────────────────────────────────────
  Primary:      GRID_TP (profit >= 0.7%)
  Secondary:    RANGE_BREAK (cage becomes NONE)
  Fallback:     WRONG_ENTRY (adverse >= 2.0%)
  Emergency:    STOP_ALL (cage invalid)
```

**Fields:**
| Field | Type | Source |
|-------|------|--------|
| exit_conditions | list[{reason, trigger, priority}] | TRADING_TRUTH |
| primary_exit | string | TRADING_TRUTH |

---

## SECTION 17: SIMULATION RESULT

```
──────────────────────────────────────────────────────────────
  SIMULATION
──────────────────────────────────────────────────────────────
  Architecture:  PASS (23/23 stages, determinism OK)
  Possibility:   PASS (82% accuracy, OI adds +7%)
  Market Push:   PASS (85% correct transitions)
  Knowledge:     PASS (87% knowledge score)
  Balance:       PASS (100 -> 103.47 USDT, 66.7% win)
  Simulators:    5/5 validated
```

**Fields:**
| Field | Type | Source |
|-------|------|--------|
| simulator_results | list[{name, verdict, score}] | SIMULATION |
| simulators_passed | int | SIMULATION |

---

## SECTION 18: RISK INFORMATION

```
──────────────────────────────────────────────────────────────
  RISK
──────────────────────────────────────────────────────────────
  Volatility:   LOW (ATR 0.15%)
  Max Drawdown: -2.1% (simulated)
  Exposure:     15% recommended
  Fee Impact:   0.12% per round trip
  Risk Level:   LOW
```

**Fields:**
| Field | Type | Source |
|-------|------|--------|
| volatility | string | TRUTH (ATR) |
| max_drawdown | float | SIMULATION |
| exposure_pct | float | CONSUMER |
| fee_impact | float | FEE |
| risk_level | string | computed |

---

## SECTION 19: FINAL RECOMMENDATION

```
══════════════════════════════════════════════════════════════
  FINAL RECOMMENDATION
══════════════════════════════════════════════════════════════
  Symbol:       BTCUSDT
  State:        SIDEWAY_COMPRESSION (81% maturity)
  Character:    LOW VOLATILITY ACCUMULATION
  Prediction:   82% Breakout UP
  Schema:       GRID_COMPRESSION
  Action:       Prepare buy area at 61800-61850
  Invalidation: Close below 61800
  Risk:         LOW
  Confidence:   89/100 (HIGH)
══════════════════════════════════════════════════════════════
```

**Fields:**
| Field | Type | Source |
|-------|------|--------|
| symbol | string | MARKET |
| state | string | STRUCTURE |
| character | string | BAG |
| prediction | string | PREDICTION |
| schema | string | TRADING_SCHEMA |
| action | string | RECOMMENDATION |
| invalidation | string | RECOMMENDATION |
| risk | string | computed |
| confidence | float | RECOMMENDATION |

---

## SECTION 20: CONSUMER INFORMATION

```
──────────────────────────────────────────────────────────────
  CONSUMER
──────────────────────────────────────────────────────────────
  Fund Status:  OK (drawdown 0%, daily loss 0%)
  Veto Gate:    ALLOW
  Intent:       GRID_INTENT (SIDEWAY -> GRID)
  Live Adapter: DISABLED (default)
  Export:       CSV available (12 markers)
  Disclaimer:   NOT a trading signal. NOT financial advice.
```

**Fields:**
| Field | Type | Source |
|-------|------|--------|
| fund_status | string | CONSUMER.fundEval |
| veto_decision | string | CONSUMER.vetoGate |
| intent_status | string | CONSUMER.intentBuilder |
| live_adapter | string | CONSUMER.liveAdapter |
| export_available | boolean | CONSUMER.exportCSV |
| disclaimer | string | fixed |

---

## FORMAT STATUS: FROZEN

Market Intelligence Report memiliki 20 sections. Setiap section memiliki field, type, dan source layer yang jelas. Report adalah output utama ST-LMS — BUKAN sinyal trading.
