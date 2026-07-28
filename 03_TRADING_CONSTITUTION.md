# 03_TRADING_CONSTITUTION.md

## ST-LMS Final Freeze Contract V1 — Trading Constitution

**Date:** 2026-07-28
**Status:** CONSTITUTIONALLY FROZEN — FINAL
**Sources:** MASTER_SPECIFICATION.html S7, ST_LMS_CORE.js CLONE_SHARED, ENRICHMENT_REPORT_V1.md

---

## 1. MARKET SCHEMA (10 schemas)

### TREND

| Aspect | Value |
|--------|-------|
| Required Artifact | truth_snapshot (stDir), structure_snapshot (cage.status) |
| Optional Artifact | evidence_snapshot (dir_bus) |
| Forbidden Artifact | W%R, MACD (for entry) |
| Confidence Source | stDir + EMA direction agreement |
| Minimum Condition | stDir != 0, cage.status = NONE |
| Exit Condition | stDir flip, wave exhaustion |
| Consumer | LONG (UP), SHORT (DOWN) |

### SIDEWAY

| Aspect | Value |
|--------|-------|
| Required Artifact | structure_snapshot (cage.status, cage.pp) |
| Optional Artifact | evidence_snapshot (correction_bus) |
| Forbidden Artifact | stDir (for GRID decision) |
| Confidence Source | cage.rangeAtr stability |
| Minimum Condition | cage.status != NONE |
| Exit Condition | cage becomes NONE, breakout |
| Consumer | GRID |

### RANGE

| Aspect | Value |
|--------|-------|
| Required Artifact | structure_snapshot (wave, cage) |
| Optional Artifact | wave_history |
| Forbidden Artifact | MTF (for GRID) |
| Confidence Source | wave = CONFIRMED_RANGE / SIDEWAY |
| Minimum Condition | wave = CONFIRMED_RANGE or SIDEWAY |
| Exit Condition | wave changes to non-range |
| Consumer | GRID |

### CHAOS

| Aspect | Value |
|--------|-------|
| Required Artifact | structure_snapshot (wave) |
| Optional Artifact | — |
| Forbidden Artifact | — |
| Confidence Source | wave = CHAOS |
| Minimum Condition | wave = CHAOS |
| Exit Condition | wave changes to non-CHAOS |
| Consumer | None (WAIT all clones) |

### COMPRESSION

| Aspect | Value |
|--------|-------|
| Required Artifact | structure_snapshot (cage.status, cage.rangeAtr) |
| Optional Artifact | cage_history |
| Forbidden Artifact | stDir (for GRID) |
| Confidence Source | cage.rangeAtr <= CAGE_TIGHT_ATR |
| Minimum Condition | cage.status = VALID_COMPRESSION |
| Exit Condition | breakout, cage expands |
| Consumer | GRID (aggressive) |

### EXPANSION

| Aspect | Value |
|--------|-------|
| Required Artifact | structure_snapshot (cage.status, cage.rangeAtr) |
| Optional Artifact | cage_history |
| Forbidden Artifact | stDir (for GRID) |
| Confidence Source | cage.rangeAtr > CAGE_TIGHT_ATR |
| Minimum Condition | cage.status = LOOSE_SIDEWAY |
| Exit Condition | breakout, cage compresses |
| Consumer | GRID (conservative) |

### BREAKOUT

| Aspect | Value |
|--------|-------|
| Required Artifact | structure_snapshot (cage.breakout) |
| Optional Artifact | truth_snapshot (stDir) |
| Forbidden Artifact | — |
| Confidence Source | cage.breakout direction + pressure |
| Minimum Condition | cage.breakout != NONE |
| Exit Condition | breakout fails, price reverses |
| Consumer | LONG (IMMINENT_UP), SHORT (IMMINENT_DOWN) |

### REVERSAL

| Aspect | Value |
|--------|-------|
| Required Artifact | truth_snapshot (flip), structure_snapshot (wave) |
| Optional Artifact | wave_history |
| Forbidden Artifact | — |
| Confidence Source | flip event + wave = REVERSAL_UP/DOWN |
| Minimum Condition | TREND_FLIP detected, wave = REVERSAL |
| Exit Condition | reversal fails (false flip) |
| Consumer | LONG (REVERSAL_UP), SHORT (REVERSAL_DOWN) — caution |

### EXHAUSTION

| Aspect | Value |
|--------|-------|
| Required Artifact | structure_snapshot (wave), truth_snapshot (distAtr) |
| Optional Artifact | truth_snapshot (vel, acc) |
| Forbidden Artifact | — |
| Confidence Source | wave = EXHAUSTION + distAtr expanding |
| Minimum Condition | wave = EXHAUSTION_UP/DOWN |
| Exit Condition | trend resumes or reverses |
| Consumer | Opposite clone (observe), existing positions exit |

### WARMUP

| Aspect | Value |
|--------|-------|
| Required Artifact | truth_snapshot (point_status) |
| Optional Artifact | — |
| Forbidden Artifact | — |
| Confidence Source | N/A (no confidence during warmup) |
| Minimum Condition | point_status = WARMUP |
| Exit Condition | point_status = VALID |
| Consumer | None (WAIT all clones) |

---

## 2. TRADING SCHEMA (7 schemas)

### LONG

| Aspect | Value |
|--------|-------|
| Required Artifact | truth_snapshot (stDir, emaSlope, volDelta, close), structure_snapshot (cage, nearest), evidence_snapshot (dir_bus), clone_ledger |
| Optional Artifact | distance_metrics (dist_ceiling) |
| Forbidden Artifact | W%R, MACD, RSI (for entry) |
| Confidence Source | setup_score (5000 + expected_move * 400) |
| Minimum Condition | stDir=+1, ema>0, vd>0, corridor.inZone, fee_safe, global_ok, open=null |
| Exit Condition | WRONG_ENTRY_EARLY -> WRONG_ENTRY_GEOM -> HYPOTHESIS_INVALID -> SL -> HOLD-VETO -> TP -> EXIT_BUS -> TIME_EXIT |
| Consumer | TRADE (LONG entry/exit markers) |

### SHORT

| Aspect | Value |
|--------|-------|
| Required Artifact | truth_snapshot (stDir, emaSlope, volDelta, close), structure_snapshot (cage, nearest), evidence_snapshot (dir_bus), clone_ledger |
| Optional Artifact | distance_metrics (dist_floor) |
| Forbidden Artifact | W%R, MACD, RSI (for entry) |
| Confidence Source | setup_score (5000 + expected_move * 400) |
| Minimum Condition | stDir=-1, ema<0, vd<0, corridor.inZone, fee_safe, global_ok, open=null |
| Exit Condition | Mirror LONG exit priority |
| Consumer | TRADE (SHORT entry/exit markers) |

### GRID

| Aspect | Value |
|--------|-------|
| Required Artifact | structure_snapshot (cage), clone_ledger (gridFills) |
| Optional Artifact | — |
| Forbidden Artifact | stDir, dir_bus, MTF, W%R, MACD, RSI |
| Confidence Source | active ? 7000 : 2000 |
| Minimum Condition | cage_valid, width>=3*req, breakout=NONE, pp in zone, fills<max |
| Exit Condition | RANGE_BREAK -> WRONG_ENTRY -> GRID_TP -> STOP_ALL |
| Consumer | TRADE (GRID fill markers) |

### NO TRADE

| Aspect | Value |
|--------|-------|
| Required Artifact | clone_observation |
| Optional Artifact | — |
| Forbidden Artifact | — |
| Confidence Source | setup_score = 2500 |
| Minimum Condition | Entry conditions not met |
| Exit Condition | N/A (no position) |
| Consumer | STATISTICS (observation recorded) |

### WAIT

| Aspect | Value |
|--------|-------|
| Required Artifact | structure_snapshot (phase, wave), truth_snapshot (point_status) |
| Optional Artifact | — |
| Forbidden Artifact | — |
| Confidence Source | setup_score = 2500 |
| Minimum Condition | Market condition not favorable for clone |
| Exit Condition | Market condition becomes favorable |
| Consumer | STATISTICS (observation recorded) |

### HOLD

| Aspect | Value |
|--------|-------|
| Required Artifact | position_state, truth_snapshot, structure_snapshot, evidence_snapshot (exit_bus) |
| Optional Artifact | distance_metrics |
| Forbidden Artifact | — |
| Confidence Source | Position PnL |
| Minimum Condition | Position open, no exit reason triggered |
| Exit Condition | Any exit reason triggered |
| Consumer | POSITION (update mae/mfe/hold_c) |

### SKIP

| Aspect | Value |
|--------|-------|
| Required Artifact | market_snapshot (data_status, gap_flag) |
| Optional Artifact | — |
| Forbidden Artifact | — |
| Confidence Source | N/A |
| Minimum Condition | data_status != FINAL or gap_flag = 1 |
| Exit Condition | data_status = FINAL |
| Consumer | STATISTICS (observation recorded with data issue) |

---

## 3. ENTRY SCHEMA (11 schemas)

### LONG CONTINUATION

| Aspect | Value |
|--------|-------|
| Required Artifact | truth_snapshot (stDir, ema, volDelta), structure_snapshot (wave, cage), evidence_snapshot (dir_bus) |
| Optional Artifact | bag_artifacts (behavior_profile) |
| Forbidden Artifact | W%R, MACD (for entry) |
| Confidence Source | HIGH (trend established) |
| Minimum Condition | stDir=+1, wave=CONTINUATION_UP or STRONG_ACCUMULATION, standard LONG conjunction |
| Exit Condition | Standard LONG exit priority |
| Consumer | TRADE (LONG entry) |

### LONG PULLBACK

| Aspect | Value |
|--------|-------|
| Required Artifact | truth_snapshot (stDir, distAtr), structure_snapshot (cage, nearest), evidence_snapshot (dir_bus) |
| Optional Artifact | distance_fingerprint |
| Forbidden Artifact | — |
| Confidence Source | MEDIUM |
| Minimum Condition | stDir=+1, dist_ceiling expanding (pullback), corridor.inZone near floor, fee_safe |
| Exit Condition | Standard LONG exit priority |
| Consumer | TRADE (LONG entry) |

### LONG BREAKOUT

| Aspect | Value |
|--------|-------|
| Required Artifact | structure_snapshot (cage.breakout, cage.pressureUp), truth_snapshot (stDir) |
| Optional Artifact | cage_history |
| Forbidden Artifact | — |
| Confidence Source | MEDIUM |
| Minimum Condition | stDir=+1, cage.breakout=IMMINENT_UP, standard LONG conjunction |
| Exit Condition | TP=cage.upper, HYPOTHESIS_INVALID if breakout fails |
| Consumer | TRADE (LONG entry) |

### LONG REVERSAL

| Aspect | Value |
|--------|-------|
| Required Artifact | truth_snapshot (flip, stDir), structure_snapshot (wave) |
| Optional Artifact | wave_history |
| Forbidden Artifact | — |
| Confidence Source | LOW (false reversal risk) |
| Minimum Condition | TREND_FLIP_UP, wave=REVERSAL_UP, standard LONG conjunction |
| Exit Condition | Aggressive wrong entry exit (hold<=2), standard LONG exit |
| Consumer | TRADE (LONG entry) |

### SHORT CONTINUATION

| Aspect | Value |
|--------|-------|
| Required Artifact | truth_snapshot (stDir, ema, volDelta), structure_snapshot (wave, cage), evidence_snapshot (dir_bus) |
| Optional Artifact | bag_artifacts (behavior_profile) |
| Forbidden Artifact | W%R, MACD (for entry) |
| Confidence Source | HIGH |
| Minimum Condition | stDir=-1, wave=CONTINUATION_DOWN or STRONG_DISTRIBUTION, standard SHORT conjunction |
| Exit Condition | Standard SHORT exit priority |
| Consumer | TRADE (SHORT entry) |

### SHORT PULLBACK

| Aspect | Value |
|--------|-------|
| Required Artifact | truth_snapshot (stDir, distAtr), structure_snapshot (cage, nearest), evidence_snapshot (dir_bus) |
| Optional Artifact | distance_fingerprint |
| Forbidden Artifact | — |
| Confidence Source | MEDIUM |
| Minimum Condition | stDir=-1, dist_floor expanding (pullback), corridor.inZone near ceiling, fee_safe |
| Exit Condition | Standard SHORT exit priority |
| Consumer | TRADE (SHORT entry) |

### SHORT BREAKOUT

| Aspect | Value |
|--------|-------|
| Required Artifact | structure_snapshot (cage.breakout, cage.pressureDn), truth_snapshot (stDir) |
| Optional Artifact | cage_history |
| Forbidden Artifact | — |
| Confidence Source | MEDIUM |
| Minimum Condition | stDir=-1, cage.breakout=IMMINENT_DOWN, standard SHORT conjunction |
| Exit Condition | TP=cage.lower, HYPOTHESIS_INVALID if breakout fails |
| Consumer | TRADE (SHORT entry) |

### SHORT REVERSAL

| Aspect | Value |
|--------|-------|
| Required Artifact | truth_snapshot (flip, stDir), structure_snapshot (wave) |
| Optional Artifact | wave_history |
| Forbidden Artifact | — |
| Confidence Source | LOW |
| Minimum Condition | TREND_FLIP_DOWN, wave=REVERSAL_DOWN, standard SHORT conjunction |
| Exit Condition | Aggressive wrong entry exit (hold<=2) |
| Consumer | TRADE (SHORT entry) |

### GRID COMPRESSION

| Aspect | Value |
|--------|-------|
| Required Artifact | structure_snapshot (cage.status, cage.rangeAtr, cage.pp) |
| Optional Artifact | cage_history, bag_artifacts (compression pattern) |
| Forbidden Artifact | stDir, dir_bus, MTF |
| Confidence Source | HIGH (tight range) |
| Minimum Condition | cage.status=VALID_COMPRESSION, standard GRID conjunction |
| Exit Condition | Standard GRID exit priority (aggressive) |
| Consumer | TRADE (GRID fills) |

### GRID RANGE

| Aspect | Value |
|--------|-------|
| Required Artifact | structure_snapshot (cage, wave) |
| Optional Artifact | wave_history |
| Forbidden Artifact | stDir, dir_bus, MTF |
| Confidence Source | MEDIUM |
| Minimum Condition | wave=CONFIRMED_RANGE or SIDEWAY, standard GRID conjunction |
| Exit Condition | Standard GRID exit priority |
| Consumer | TRADE (GRID fills) |

### GRID EXPANSION

| Aspect | Value |
|--------|-------|
| Required Artifact | structure_snapshot (cage.status, cage.rangeAtr, cage.pp) |
| Optional Artifact | cage_history |
| Forbidden Artifact | stDir, dir_bus, MTF |
| Confidence Source | LOW (wide range, higher risk) |
| Minimum Condition | cage.status=LOOSE_SIDEWAY, standard GRID conjunction |
| Exit Condition | Standard GRID exit priority (conservative) |
| Consumer | TRADE (GRID fills) |

---

## 4. POSITION SCHEMA (7 schemas)

### ADD POSITION

| Aspect | Value |
|--------|-------|
| Required Artifact | position_state (fills count), structure_snapshot (cage.pp) |
| Optional Artifact | — |
| Forbidden Artifact | — |
| Confidence Source | GRID active confidence |
| Minimum Condition | GRID only: pp in zone, fills_per_side < GRID_MAX_FILLS_PER_SIDE |
| Exit Condition | Per-fill exit rules |
| Consumer | TRADE (GRID fill marker) |

### PARTIAL TP

| Aspect | Value |
|--------|-------|
| Required Artifact | position_state (profit_pct) |
| Optional Artifact | bag_artifacts (optimal_partial_level) |
| Forbidden Artifact | — |
| Confidence Source | Position profit percentage |
| Minimum Condition | profit_pct >= PARTIAL_TP activation |
| Exit Condition | Close PARTIAL_TP_PCT, SL to entry for remainder |
| Consumer | TRADE (PARTIAL marker) |

### TRAILING TP

| Aspect | Value |
|--------|-------|
| Required Artifact | position_state (profit_pct), truth_snapshot (atr) |
| Optional Artifact | distance_metrics |
| Forbidden Artifact | — |
| Confidence Source | Position profit percentage |
| Minimum Condition | profit_pct >= TRAIL_ACTIVATE_R * ATR |
| Exit Condition | SL trails behind price by TRAIL_ATR_MULT * ATR |
| Consumer | POSITION (trailing_stop update) |

### BREAKEVEN

| Aspect | Value |
|--------|-------|
| Required Artifact | position_state (profit_pct, entry_price) |
| Optional Artifact | — |
| Forbidden Artifact | — |
| Confidence Source | Position profit percentage |
| Minimum Condition | profit_pct >= BREAKEVEN threshold |
| Exit Condition | SL moved to entry_price |
| Consumer | POSITION (stop_loss update) |

### TIME EXIT

| Aspect | Value |
|--------|-------|
| Required Artifact | position_state (hold_count, profit_pct) |
| Optional Artifact | bag_artifacts (optimal_hold_duration) |
| Forbidden Artifact | — |
| Confidence Source | N/A (exit trigger) |
| Minimum Condition | hold_count >= TIME_EXIT_CANDLES AND profit_pct < required_move |
| Exit Condition | Close at market |
| Consumer | TRADE (TIME_EXIT marker) |

### WRONG ENTRY

| Aspect | Value |
|--------|-------|
| Required Artifact | position_state (hold_count, entry_price), truth_snapshot (vel, close) |
| Optional Artifact | distance_metrics (adverse) |
| Forbidden Artifact | — |
| Confidence Source | N/A (exit trigger) |
| Minimum Condition | (vel wrong direction OR adverse >= WRONG_ENTRY_PCT) AND hold_count <= 2 |
| Exit Condition | Close immediately at market |
| Consumer | TRADE (WRONG_ENTRY marker) |

### LOCK PROFIT

| Aspect | Value |
|--------|-------|
| Required Artifact | position_state (profit_pct) |
| Optional Artifact | — |
| Forbidden Artifact | — |
| Confidence Source | Position profit percentage |
| Minimum Condition | profit_pct >= LOCK_PROFIT threshold |
| Exit Condition | Disable EXIT_BUS, hold to TP |
| Consumer | POSITION (exit_bus disabled) |

---

## 5. EXIT SCHEMA (6 schemas)

### SL

| Aspect | Value |
|--------|-------|
| Required Artifact | position_state (sl), market_snapshot (high, low) |
| Optional Artifact | — |
| Forbidden Artifact | — |
| Confidence Source | N/A |
| Minimum Condition | LONG: low <= sl; SHORT: high >= sl |
| Exit Condition | Exit at sl price |
| Consumer | TRADE (SL exit marker) |
| Priority | 4 |

### TP

| Aspect | Value |
|--------|-------|
| Required Artifact | position_state (tp), market_snapshot (high, low), evidence_snapshot (exit_bus.hold) |
| Optional Artifact | — |
| Forbidden Artifact | — |
| Confidence Source | N/A |
| Minimum Condition | LONG: high >= tp AND NOT hold; SHORT: low <= tp AND NOT hold |
| Exit Condition | Exit at tp price |
| Consumer | TRADE (TP exit marker) |
| Priority | 6 (delayed by HOLD-veto at priority 5) |

### EXIT BUS

| Aspect | Value |
|--------|-------|
| Required Artifact | truth_snapshot (rsi, wpr) |
| Optional Artifact | — |
| Forbidden Artifact | W%R, MACD (for entry — exit only is OK) |
| Confidence Source | RSI/W%R signal strength |
| Minimum Condition | LONG: RSI>70 OR W%R>-20; SHORT: RSI<30 OR W%R<-80 |
| Exit Condition | Exit at close price |
| Consumer | TRADE (EXIT_BUS marker) |
| Priority | 7 |

### MANUAL EXIT

| Aspect | Value |
|--------|-------|
| Required Artifact | position_state |
| Optional Artifact | — |
| Forbidden Artifact | — |
| Confidence Source | Human decision |
| Minimum Condition | Human approves exit |
| Exit Condition | Exit at close price |
| Consumer | TRADE (MANUAL exit marker) |
| Priority | 0 (override all) |

### TIME EXIT

| Aspect | Value |
|--------|-------|
| Required Artifact | position_state (hold_count, profit_pct) |
| Optional Artifact | — |
| Forbidden Artifact | — |
| Confidence Source | N/A |
| Minimum Condition | hold_count >= TIME_EXIT_CANDLES AND profit_pct < required_move |
| Exit Condition | Exit at close price |
| Consumer | TRADE (TIME_EXIT marker) |
| Priority | 8 |

### EARLY EXIT

| Aspect | Value |
|--------|-------|
| Required Artifact | position_state (hold_count), truth_snapshot (vel, close) |
| Optional Artifact | distance_metrics (adverse) |
| Forbidden Artifact | — |
| Confidence Source | N/A |
| Minimum Condition | Wrong entry detected in first 2 candles |
| Exit Condition | Exit at close price |
| Consumer | TRADE (WRONG_ENTRY marker) |
| Priority | 1-2 |

---

## TRADING CONSTITUTION STATUS: LOCKED

All 41 trading schemas across 5 categories are constitutionally frozen. Each schema defines required artifacts, optional artifacts, forbidden artifacts, confidence source, minimum condition, exit condition, and consumer. No trading logic may be implemented outside these schemas.
