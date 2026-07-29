# RECOMMENDATION LAYER OUTPUT CONTRACT

## ST-LMS v3 — Phase 0.5 Implementation Enrichment

**Date:** 2026-07-29
**Status:** CONTRACT DEFINITION — FROZEN
**Phase:** PHASE-15 (Recommendation Layer)

---

## CONTRACT IDENTITY

Recommendation Layer adalah output akhir Market Intelligence System. Ia TIDAK menghasilkan sinyal trading. Ia menghasilkan **Market Intelligence Report Package** — laporan utuh tentang kondisi market, kemungkinan masa depan, dan rekomendasi berbasis data.

---

## 1. PACKAGE HEADER

```
┌──────────────────────────────────────────────────────────────┐
│  ST-LMS MARKET INTELLIGENCE REPORT                            │
│  =====================================                        │
│  Report ID:    MIR_20260729_113000                           │
│  Generated:    2026-07-29 11:30:00 WIB                       │
│  Version:      1.0                                            │
│  Pipeline:     23 stages complete                             │
│  Simulators:   5/5 validated                                  │
└──────────────────────────────────────────────────────────────┘
```

**Contract:**
```json
{
  "header": {
    "report_id": "string — unique report identifier",
    "generated_at_wib": "string — ISO 8601 with +07:00",
    "version": "string — report format version",
    "pipeline_stages": "int — number of stages executed",
    "simulators_validated": "int — number of simulators passed"
  }
}
```

---

## 2. MARKET IDENTITY

```
MARKET IDENTITY
═══════════════
Symbol:       BTCUSDT
Exchange:     Binance Futures
Timeframe:    1m
Session:      UTC 03:00 - 03:30
Market Type:  Crypto Perpetual
Quote Asset:  USDT
```

**Contract:**
```json
{
  "market_identity": {
    "symbol": "string — trading pair",
    "exchange": "string — data source",
    "timeframe": "string — primary timeframe",
    "session_start_wib": "string — session start",
    "session_end_wib": "string — session end",
    "market_type": "string — spot/futures/perpetual",
    "quote_asset": "string — quote currency"
  }
}
```

---

## 3. CURRENT MARKET STATE

```
CURRENT STATE
═════════════
Phase:        SIDEWAY_COMPRESSION
Character:    LOW_VOLATILITY_ACCUMULATION
Maturity:     81%
Trend:        NEUTRAL (compressing)
Volatility:   LOW (ATR 0.15%)
```

**Contract:**
```json
{
  "current_state": {
    "phase": "string — UPTREND | DOWNTREND | SIDEWAY_COMPRESSION | TRANSITION | CHAOS",
    "character": "string — behavior profile from BAG",
    "maturity_pct": "float — compression maturity 0-100",
    "trend_bias": "string — BULLISH | BEARISH | NEUTRAL",
    "volatility_regime": "string — LOW | MEDIUM | HIGH"
  }
}
```

---

## 4. MARKET CHARACTER

```
MARKET CHARACTER
════════════════
Profile:      MEAN_REVERSION with BREAKOUT tendency
Behavior:     Range-bound accumulation, building pressure
DNA Pattern:  Compression -> Breakout (73% historical)
Biography:    3rd compression cycle this session
Evolution:    Range tightening over last 30 minutes
```

**Contract:**
```json
{
  "market_character": {
    "profile": "string — from BAG behavior_profile",
    "behavior_description": "string — human-readable behavior",
    "dna_pattern": "string — recurring pattern from BAG sequence_analysis",
    "biography": "string — session-level narrative",
    "evolution": "string — how market is evolving"
  }
}
```

---

## 5. TRUTH SUMMARY

```
TRUTH
═════
Supertrend:   UP (62150)
Direction:    BULLISH
Color:        HIJAU
Distance:     0.15 ATR (very close to ST)
EMA:          62200 (above ST, rising)
RSI:          52 (neutral)
W%R:          -35 (neutral)
MACD:         +3.2 (bullish, expanding)
Volume Delta: +0.15 (buying pressure)
```

**Contract:**
```json
{
  "truth_summary": {
    "supertrend": {"value": "float", "direction": "string", "color": "string"},
    "distance_atr": "float",
    "ema": {"value": "float", "slope": "string"},
    "rsi": "float",
    "wpr": "float",
    "macd": {"histogram": "float", "trend": "string"},
    "volume_delta": "float"
  }
}
```

---

## 6. STRUCTURE SUMMARY

```
STRUCTURE
═════════
Wave:         RANGE_COMPRESSING
Cage:         VALID_COMPRESSION
  Upper:      62500
  Lower:      61800
  Range:      700 (1.12%)
  Range ATR:  1.8
Breakout:     NONE (building)
Support v0:   61800 (strong)
Resistance v0: 62500 (strong)
Ladder:       Not stepped
```

**Contract:**
```json
{
  "structure_summary": {
    "wave": "string — 13 wave structures",
    "cage": {
      "status": "string — NONE | VALID_COMPRESSION | LOOSE_SIDEWAY",
      "upper": "float",
      "lower": "float",
      "range": "float",
      "range_atr": "float",
      "breakout": "string — NONE | IMMINENT_UP | IMMINENT_DOWN | SQUEEZE"
    },
    "support": {"v0": "float", "strength": "string"},
    "resistance": {"v0": "float", "strength": "string"},
    "ladder": {"stepped": "boolean"}
  }
}
```

---

## 7. DISTANCE SUMMARY

```
DISTANCE
════════
Distance to ST:      0.15 ATR (NEAR)
Distance to Ceiling: 0.85 ATR (room to move)
Distance to Floor:   0.15 ATR (tight support)
Fingerprint:         [0.15, 0.18, 0.14, 0.12, 0.15]
Trend:               STABLE
Velocity:            -0.01/candle (slowly approaching ST)
```

**Contract:**
```json
{
  "distance_summary": {
    "dist_atr": "float",
    "dist_atr_bucket": "string — OPTIMAL | NEAR | EXTENDED | FAR",
    "dist_ceiling": "float",
    "dist_floor": "float",
    "fingerprint": ["float x5 — distance trajectory"],
    "trend": "string — STABLE | EXPANDING | CONTRACTING",
    "velocity": "float — rate of change"
  }
}
```

---

## 8. SNAPSHOT SUMMARY

```
SNAPSHOT
════════
Present:   SP at 11:30 — compression, low vol, accumulation
Past:      73% similar patterns resulted in breakout
Future:    82% breakout probability
Character: MEAN_REVERSION with BREAKOUT tendency
Count:     1000 snapshots produced (100 SP x 10 types)
```

**Contract:**
```json
{
  "snapshot_summary": {
    "present": "string — current SP state",
    "past": "string — historical pattern summary",
    "future": "string — prediction summary",
    "character": "string — behavior profile",
    "total_snapshots": "int",
    "sp_count": "int"
  }
}
```

---

## 9. STATISTICS SUMMARY

```
STATISTICS
══════════
LONG Clone:   Sample=45, Win=62%, Expectancy=+0.023, PF=1.8
SHORT Clone:  Sample=38, Win=55%, Expectancy=+0.015, PF=1.5
GRID Clone:   Sample=52, Win=71%, Expectancy=+0.031, PF=2.1
Status:       All CUKUP (sample >= 30)
```

**Contract:**
```json
{
  "statistics_summary": {
    "long": {"sample": "int", "win_rate": "float", "expectancy": "float", "pf": "float"},
    "short": {"sample": "int", "win_rate": "float", "expectancy": "float", "pf": "float"},
    "grid": {"sample": "int", "win_rate": "float", "expectancy": "float", "pf": "float"},
    "status": "string — CUKUP | BELUM_CUKUP per clone"
  }
}
```

---

## 10. KNOWLEDGE SUMMARY

```
KNOWLEDGE
═════════
Similar Pattern:   COMPRESSION_BREAKOUT (73% win, 47 samples)
Market Biography:  3rd compression cycle — each tighter than last
Market DNA:        BTCUSDT favors breakout after 3rd compression
Oracle Match:      YES (similarity 8200)
HiveMind Bias:     BULLISH (intelligence 7200)
CERMIN Error:      +3% (slightly overconfident)
Librarian Status:  COMPRESSION_BREAKOUT = MATURE
```

**Contract:**
```json
{
  "knowledge_summary": {
    "academy": {"top_pattern": "string", "win_rate": "float", "sample": "int"},
    "oracle": {"match": "boolean", "similarity_score": "float"},
    "hivemind": {"intelligence_score": "float", "dominant_bias": "string"},
    "cermin": {"calibration_error": "float", "interpretation": "string"},
    "librarian": {"top_artifact_status": "string"},
    "biography": "string — session narrative",
    "dna": "string — symbol-level pattern"
  }
}
```

---

## 11. PREDICTION SUMMARY

```
PREDICTION (Market Possibility)
════════════════════════════════
Breakout UP:           82%  ████████████████████░
Continuation Range:    12%  ███░░░░░░░░░░░░░░░░░░
Reversal DOWN:          4%  █░░░░░░░░░░░░░░░░░░░░
Fake Breakout:          2%  ░░░░░░░░░░░░░░░░░░░░░░

Supporting Factors:
  Price:      STRONG — above ST, within cage
  Structure:  STRONG — compression tightening
  Volume:     MODERATE — building pressure
  OI:         STRONG — accumulation +4%
  Knowledge:  STRONG — similar pattern 76% win rate

OI Context:
  Trend:      ACCUMULATION (+4%)
  Signal:     Institutional support for breakout
```

**Contract:**
```json
{
  "prediction_summary": {
    "possibilities": [
      {"type": "string", "probability": "float", "confidence": "string"}
    ],
    "supporting_factors": {
      "price": {"signal": "string", "detail": "string"},
      "structure": {"signal": "string", "detail": "string"},
      "volume": {"signal": "string", "detail": "string"},
      "oi": {"signal": "string", "detail": "string"},
      "knowledge": {"signal": "string", "detail": "string"}
    },
    "oi_context": {"trend": "string", "strength": "float", "interpretation": "string"}
  }
}
```

---

## 12. TRADING SCHEMA SUMMARY

```
TRADING SCHEMA
══════════════
Primary:      GRID_COMPRESSION (confidence: 89)
Secondary:    LONG_BREAKOUT (confidence: 72)
Active Clone: GRID (LONG observing, SHORT waiting)
Schema Match: Market condition -> GRID_COMPRESSION schema
```

**Contract:**
```json
{
  "trading_schema_summary": {
    "primary": {"schema": "string", "confidence": "float"},
    "secondary": {"schema": "string", "confidence": "float"},
    "active_clones": ["string — LONG | SHORT | GRID"],
    "schema_match_reason": "string"
  }
}
```

---

## 13. ENTRY TRUTH

```
ENTRY TRUTH
═══════════
Strategy:     GRID_COMPRESSION
Entry Zone:   BUY at 61800-61850 (cage.lower zone)
Condition:    price bounce from support + volume confirmation
Fee Safe:     YES (width 1.12% >= 3x required 0.7%)
Corridor:     In zone (pp=0.25, BUY zone < 0.30)
Confidence:   89/100
```

**Contract:**
```json
{
  "entry_truth": {
    "strategy": "string",
    "entry_zone": "string",
    "entry_condition": "string",
    "fee_safe": "boolean",
    "corridor_in_zone": "boolean",
    "confidence": "float — 0-100"
  }
}
```

---

## 14. POSITION TRUTH

```
POSITION TRUTH
══════════════
Max Fills:    2 per side
Current:      0 fills (preparing)
Stop Loss:    Below cage.lower (61750)
Take Profit:  cage.upper (62500)
Risk/Reward:  1:4.6
Hold Target:  5-15 candles
```

**Contract:**
```json
{
  "position_truth": {
    "max_fills": "int",
    "current_fills": "int",
    "stop_loss": "float",
    "take_profit": "float",
    "risk_reward_ratio": "float",
    "hold_target": "string"
  }
}
```

---

## 15. EXIT TRUTH

```
EXIT TRUTH
══════════
GRID TP:      profit >= 0.7% per fill
RANGE BREAK:  cage becomes NONE
WRONG ENTRY:  adverse >= 2.0% (hold <= 2)
STOP ALL:     cage invalid
Priority:     1=RANGE_BREAK, 2=WRONG_ENTRY, 3=GRID_TP, 4=STOP_ALL
```

**Contract:**
```json
{
  "exit_truth": {
    "exit_conditions": [
      {"reason": "string", "trigger": "string", "priority": "int"}
    ],
    "primary_exit": "string"
  }
}
```

---

## 16. RISK SUMMARY

```
RISK
════
Volatility:      LOW (ATR 0.15%)
Max Drawdown:    -2.1% (simulated)
Exposure:        15% of capital
Liquidation:     Not applicable (futures leverage=1x)
Fee Impact:      0.12% per round trip
Risk Level:      LOW
```

**Contract:**
```json
{
  "risk_summary": {
    "volatility": "string — LOW | MEDIUM | HIGH",
    "max_drawdown_pct": "float",
    "recommended_exposure_pct": "float",
    "liquidation_risk": "string",
    "fee_impact_pct": "float",
    "risk_level": "string — LOW | MEDIUM | HIGH | CRITICAL"
  }
}
```

---

## 17. CONFIDENCE SUMMARY

```
CONFIDENCE
══════════
Overall:       89/100 (HIGH)
Truth:         95/100 (all indicators valid, not warmup)
Structure:     90/100 (cage valid, wave classified)
Knowledge:     85/100 (pattern MATURE, sample CUKUP)
Prediction:    82/100 (breakout probability)
Schema Match:  89/100 (market fits GRID_COMPRESSION)
CERMIN Adj:    -3 (slight overconfidence correction)
```

**Contract:**
```json
{
  "confidence_summary": {
    "overall": "float — 0-100",
    "breakdown": {
      "truth": "float",
      "structure": "float",
      "knowledge": "float",
      "prediction": "float",
      "schema_match": "float"
    },
    "cermin_adjustment": "float"
  }
}
```

---

## 18. ACTION PLAN

```
ACTION PLAN
═══════════
1. PREPARE:     Set buy orders at 61800-61850 zone
2. MONITOR:     Wait for price bounce + volume confirmation
3. ENTER:       GRID_COMPRESSION — LONG fill at bounce
4. MANAGE:      Set SL below 61750, TP at 62500
5. EXIT:        GRID_TP at 62500 or RANGE_BREAK
6. SECONDARY:   If breakout -> switch to LONG_BREAKOUT schema
```

**Contract:**
```json
{
  "action_plan": {
    "steps": [
      {"order": "int", "action": "string", "detail": "string"}
    ],
    "primary_schema": "string",
    "fallback_schema": "string"
  }
}
```

---

## 19. INVALIDATION CONDITION

```
INVALIDATION
════════════
Condition:     Close below cage.lower (61800)
Consequence:   GRID schema invalidated
Next Action:   Switch to WAIT, reassess market
Recovery:      Wait for new cage formation or trend confirmation
```

**Contract:**
```json
{
  "invalidation": {
    "condition": "string — what invalidates this recommendation",
    "consequence": "string — what happens if invalidated",
    "next_action": "string — what to do after invalidation",
    "recovery": "string — how to re-enter"
  }
}
```

---

## 20. RECOMMENDATION VERDICT

```
══════════════════════════════════════════════════════════════
  ST-LMS RECOMMENDATION VERDICT
══════════════════════════════════════════════════════════════
  Symbol:       BTCUSDT
  State:        SIDEWAY_COMPRESSION (81% maturity)
  Prediction:   82% Breakout UP
  Schema:       GRID_COMPRESSION (confidence: 89)
  Action:       Prepare buy area at 61800-61850
  Invalidation: Close below 61800
  Risk:         LOW
  Confidence:   89/100 (HIGH)
══════════════════════════════════════════════════════════════
  Report ID:    MIR_20260729_113000
  Generated:    2026-07-29 11:30:00 WIB
  DISCLAIMER:  This is a Market Intelligence Report.
               NOT a trading signal. NOT financial advice.
══════════════════════════════════════════════════════════════
```

**Contract:**
```json
{
  "verdict": {
    "symbol": "string",
    "state": "string",
    "prediction": "string",
    "schema": "string",
    "action": "string",
    "invalidation": "string",
    "risk": "string",
    "confidence": "float",
    "disclaimer": "string — NOT a trading signal, NOT financial advice"
  }
}
```

---

## CONTRACT STATUS: FROZEN

Recommendation Layer menghasilkan Market Intelligence Report Package — 20 sections. BUKAN sinyal BUY/SELL. Phase-15 implementation mengacu pada contract ini.
