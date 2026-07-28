# 06_CONSUMER_MATRIX.md

## ST-LMS Final Freeze Contract V1 — Consumer Matrix

**Date:** 2026-07-28
**Status:** CONSTITUTIONALLY FROZEN — FINAL

---

## CONSUMER MATRIX: ARTIFACT -> CONSUMER CHAIN

```
FORMAT:
  artifact
    -> consumer_layer
      -> consumer_component
        -> consumer_worker (if applicable)
          -> consumer_schema (if applicable)
```

---

### MARKET LAYER ARTIFACTS

```
market_snapshot
  -> TRUTH
    -> PointBuilder
      -> (main thread)
        -> TRUTH schema

candle_hygiene_report
  -> MARKET (internal)
  -> AUDIT
    -> Pipeline Audit

gap_report
  -> EVIDENCE
    -> maxScore (data quality)
  -> AUDIT
    -> Data Quality Audit

oi_proxy_series
  -> EVIDENCE
    -> oiInherit (OI scoring)
      -> (main thread)
        -> EVIDENCE schema
  -> TRUTH
    -> PointBuilder (OI value)

data_status
  -> TRUTH (point_status propagation)
  -> CLONE (SKIP schema if not FINAL)
  -> DASHBOARD
    -> Market Now Panel
```

### TRUTH LAYER ARTIFACTS

```
truth_snapshot
  -> STRUCTURE
    -> LineBuilder, CageEngine, WaveBuilder, PhaseEngine
      -> (main thread)
        -> STRUCTURE schema
  -> EVIDENCE
    -> dirBus, exitBus, correctionBus
      -> (main thread)
        -> EVIDENCE schema
  -> DISTANCE
    -> dist, distAtr computation
  -> CLONE
    -> dirObserve, gridObserve (via Card Sharing)
      -> (main thread, PER-CLONE)
        -> LONG/SHORT/GRID schema
  -> BAG
    -> Grouping by indicator values
      -> (Knowledge Worker)
        -> BAG schema
  -> KNOWLEDGE
    -> Academy (distance_bucket), Oracle (vector)
      -> (Knowledge Worker)
        -> KNOWLEDGE schema
  -> DASHBOARD
    -> Indicator Gauges, Wave Panel
      -> (main thread, UI render)

stDir
  -> CLONE
    -> dirObserve (entry direction check)
      -> LONG/SHORT schema
  -> STRUCTURE
    -> phase (market phase determination)
  -> TRADING SCHEMA
    -> TREND, REVERSAL, BREAKOUT schemas

atr
  -> STRUCTURE
    -> CageEngine (rangeAtr, wall distance)
  -> CLONE
    -> corridor (volatility adjustment)
    -> dirObserve (TP_ATR_MULT)
  -> DISTANCE
    -> distAtr (normalization)

ema
  -> EVIDENCE
    -> dirBus (ema score)
  -> CLONE
    -> dirObserve (dirOk: ema>5000/ema<5000)

macd_hist
  -> EVIDENCE
    -> exitBus (HOLD-veto: expanding/contracting)
  -> CLONE
    -> decideClose (HOLD-veto check)

rsi
  -> EVIDENCE
    -> exitBus (rsi exit signal)
  -> CLONE
    -> decideClose (EXIT_BUS: RSI>70/RSI<30)
  -> DASHBOARD
    -> Indicator Gauges

wpr
  -> EVIDENCE
    -> exitBus (wpr exit signal)
  -> CLONE
    -> decideClose (EXIT_BUS: WPR>-20/WPR<-80)
  -> DASHBOARD
    -> Indicator Gauges

vel
  -> CLONE
    -> decideClose (WRONG_ENTRY_EARLY: vel against position)
  -> EVIDENCE
    -> exitBus (vel_signal)

acc
  -> EVIDENCE
    -> exitBus (acc_signal)

volDelta
  -> EVIDENCE
    -> dirBus (vd score)
  -> CLONE
    -> dirObserve (dirOk: vd>5000/vd<5000)

flip
  -> TRADING SCHEMA
    -> LONG/SHORT REVERSAL schema activation
  -> BAG
    -> Behavior analysis (flip frequency)
  -> DASHBOARD
    -> Wave Panel

point_status
  -> CLONE
    -> dirObserve (WARMUP -> no entry)
  -> DASHBOARD
    -> Truth Status indicator
```

### DISTANCE LAYER ARTIFACTS

```
distAtr
  -> CLONE
    -> corridor (volatility-adjusted width)
      -> LONG/SHORT schema
  -> EVIDENCE
    -> StDistVol (rolling stddev)
  -> BAG
    -> Fingerprint (d_entry..d_exit dimensions)
    -> Grouping (distance_bucket)
  -> KNOWLEDGE
    -> Academy (distance_bucket: OPTIMAL/NEAR/EXTENDED/FAR)
    -> Oracle (norm01(distAtr,0,3) as vector dimension)
  -> PREDICTION
    -> empirical_win_rate per distance_bucket

dist_ceiling
  -> CLONE
    -> dirObserve (LONG: fee_safe, expected_move)
      -> LONG schema
  -> BAG
    -> Fingerprint, Grouping
  -> TRADING SCHEMA
    -> LONG PULLBACK (ceiling distance for pullback detection)

dist_floor
  -> CLONE
    -> dirObserve (SHORT: fee_safe, expected_move)
      -> SHORT schema
  -> BAG
    -> Fingerprint, Grouping
  -> TRADING SCHEMA
    -> SHORT PULLBACK (floor distance for pullback detection)

sdv (ST_DIST_VOL)
  -> CLONE
    -> corridor (volatility adjustment)
      -> (main thread)
        -> LONG/SHORT schema

p90 (ST_DIST_VOL)
  -> BAG
    -> Behavior analysis (extreme volatility)
  -> TRADING SCHEMA
    -> Volatility regime classification

distance_fingerprint
  -> BAG
    -> Pattern mining (fingerprint clustering)
  -> KNOWLEDGE
    -> Oracle (fingerprint similarity matching)
  -> PREDICTION
    -> empirical_win_rate per fingerprint cluster

distance_bucket
  -> KNOWLEDGE
    -> Academy (bucket dimension)
  -> BAG
    -> Grouping (bag_key dimension)
```

### STRUCTURE LAYER ARTIFACTS

```
structure_snapshot
  -> EVIDENCE
    -> correctionBus, mtfSector
  -> CLONE
    -> dirObserve, gridObserve (via Card Sharing)
      -> LONG/SHORT/GRID schema
  -> BAG
    -> Grouping by market condition
  -> KNOWLEDGE
    -> Academy (structure dimension)
  -> TRADING SCHEMA
    -> All market schemas
  -> DASHBOARD
    -> Cage, Wave, Versioning, Ladder panels

cage
  -> CLONE
    -> dirObserve (floor/ceiling for SL/TP)
    -> gridObserve (cage_valid, width, breakout, pp)
      -> GRID schema
  -> EVIDENCE
    -> correctionBus (pp, phase, distances)
  -> BAG
    -> Grouping (cage status, rangeAtr, breakout)
    -> Behavior analysis (compression/expansion patterns)
  -> TRADING SCHEMA
    -> COMPRESSION, EXPANSION, BREAKOUT, SIDEWAY schemas

wave
  -> EVIDENCE
    -> mtfSector (wave -> MTF mapping)
  -> KNOWLEDGE
    -> Academy (structure dimension)
    -> Oracle (normCodeWave as vector dimension)
  -> BAG
    -> Sequence analysis (wave sequence patterns)
  -> TRADING SCHEMA
    -> CONTINUATION, REVERSAL, EXHAUSTION, RANGE, CHAOS schemas

market_phase
  -> CLONE
    -> Clone activation (which clone is active)
  -> BAG
    -> Grouping (phase distribution)
  -> TRADING SCHEMA
    -> TREND, SIDEWAY schema selection
  -> DASHBOARD
    -> Phase indicator

nearest_support / nearest_resistance
  -> CLONE
    -> dirObserve (fallback SL/TP when cage absent)
      -> LONG/SHORT schema

ladder
  -> BAG
    -> Behavior analysis (trend strength)
  -> TRADING SCHEMA
    -> Trend strength confirmation
  -> DASHBOARD
    -> Ladder Panel
```

### EVIDENCE LAYER ARTIFACTS

```
evidence_snapshot
  -> CLONE
    -> dirObserve, decideClose (via Card Sharing)
      -> LONG/SHORT/GRID schema
  -> HIVEMIND
    -> synth (currentEvidence from evidence_snapshot)
  -> BAG
    -> Grouping by bus values
  -> DASHBOARD
    -> Direction Bus, Exit Bus panels

dir_bus
  -> CLONE
    -> dirObserve (dirOk: ema, vd, mtf_long, mtf_short)
      -> LONG/SHORT schema
  -> BAG
    -> Grouping (direction strength)
  -> DASHBOARD
    -> Direction Bus gauges

exit_bus
  -> CLONE
    -> decideClose (HOLD-veto, EXIT_BUS)
      -> LONG/SHORT schema
  -> BAG
    -> Grouping (exit signal frequency)
  -> DASHBOARD
    -> Exit Bus panel

correction_bus
  -> BAG
    -> Grouping (market context)
  -> TRADING SCHEMA
    -> Market condition validation
  -> DASHBOARD
    -> Correction indicators

oi_score
  -> EVIDENCE
    -> dirBus (oi dimension)
  -> BAG
    -> Grouping (OI patterns)

mtf_sector
  -> EVIDENCE
    -> dirBus (mtf_long, mtf_short)
  -> CLONE
    -> dirObserve (mtf_conflict detection)
  -> BAG
    -> Grouping (MTF patterns)

max_score / data_quality
  -> CLONE
    -> SKIP schema (if quality degraded)
  -> AUDIT
    -> Data Quality Audit
  -> DASHBOARD
    -> Data quality indicator
```

### CLONE LAYER ARTIFACTS

```
clone_observation
  -> TRADE
    -> mkEntry (if entry_allowed)
      -> LONG/SHORT/GRID schema
  -> STATISTICS
    -> tradeStats (observation counting)
  -> BAG
    -> Grouping (observation patterns)
  -> DASHBOARD
    -> Clone Cards

entry_allowed / no_entry_reason
  -> TRADE (entry decision)
  -> BAG
    -> Grouping (entry frequency, rejection reasons)
  -> DASHBOARD
    -> Clone Cards (reason display)

setup_score / confidence
  -> BAG
    -> Grouping (score distribution)
  -> KNOWLEDGE
    -> CERMIN (calibration: predicted vs actual)
  -> DASHBOARD
    -> Clone Cards (score display)
```

### TRADE LAYER ARTIFACTS

```
trade_markers
  -> POSITION
    -> update (mae/mfe/hold_c)
  -> STATISTICS
    -> tradeStats (aggregation)
  -> BAG
    -> Grouping (entry/exit patterns)
    -> Fingerprint (distance at entry/exit)
  -> KNOWLEDGE
    -> Academy (win_rate per bucket)
    -> CERMIN (calibration)
  -> DASHBOARD
    -> Trade History Table, Equity Curve
  -> REPLAY
    -> Trade Replay

entry_marker
  -> POSITION
    -> Position open (entry_price, sl, tp)
  -> BAG
    -> Grouping (entry conditions)

exit_marker
  -> POSITION
    -> Position close (exit_price, P&L)
  -> STATISTICS
    -> tradeStats (win/loss counting)
  -> BAG
    -> Grouping (exit reasons)
    -> Pattern mining (win/loss patterns)
  -> KNOWLEDGE
    -> Academy (outcome per bucket)

result (WIN/LOSS/BREAKEVEN)
  -> STATISTICS
    -> tradeStats (win_rate)
  -> BAG
    -> Consensus (outcome agreement)
  -> KNOWLEDGE
    -> Academy (win counting)
```

### POSITION LAYER ARTIFACTS

```
mae / mfe
  -> STATISTICS
    -> tradeStats (avg mae/mfe)
  -> BAG
    -> Grouping (excursion patterns)
  -> KNOWLEDGE
    -> CERMIN (SL/TP calibration)

hold_count
  -> CLONE
    -> decideClose (TIME_EXIT, WRONG_ENTRY)
  -> STATISTICS
    -> tradeStats (avg_hold)
  -> BAG
    -> Temporal analysis (hold duration patterns)
  -> PREDICTION
    -> Optimal hold duration
```

### STATISTICS LAYER ARTIFACTS

```
statistics_snapshot
  -> BAG
    -> Grouping (all statistics dimensions)
    -> Pattern mining (win_rate patterns)
  -> KNOWLEDGE
    -> Academy (win_rate per bucket)
    -> CERMIN (calibration)
    -> Darwin (proposals)
  -> PREDICTION
    -> empirical_win_rate
  -> BENCHMARK
    -> WASIT (base metrics)
  -> DASHBOARD
    -> Rapor Table

win_rate
  -> KNOWLEDGE
    -> Academy (per bucket)
    -> CERMIN (calibration)
  -> PREDICTION
    -> empirical_win_rate per clone
  -> BAG
    -> Consensus (win_rate agreement)
  -> BENCHMARK
    -> WASIT G4 (win_rate comparison)

expectancy
  -> KNOWLEDGE
    -> Academy (per bucket)
    -> Darwin (TIGHTEN_ENTRY if < 0)
  -> BENCHMARK
    -> WASIT G2 (expectancy comparison)

fee_drag
  -> BENCHMARK
    -> WASIT G5 (fee comparison)
  -> BAG
    -> Grouping (fee impact)

wrong_rate
  -> KNOWLEDGE
    -> Darwin (TIGHTEN_WRONG if > 30)
  -> BAG
    -> Grouping (wrong entry patterns)
```

### BAG LAYER ARTIFACTS

```
bag_artifacts
  -> KNOWLEDGE
    -> Academy (learn from BAG groupings)
    -> Oracle (similarity context)
    -> HiveMind (understanding synthesis)
    -> CERMIN (calibration per bag_key)
    -> Librarian (lifecycle per bag_artifact)
    -> Darwin (proposals from BAG insights)
      -> (Knowledge Worker)
        -> KNOWLEDGE schema
  -> PREDICTION
    -> empirical_win_rate (from BAG groupings)
  -> TRADING SCHEMA
    -> Schema confidence (from BAG consensus)
  -> BENCHMARK
    -> WASIT (grouped evaluation)
  -> DASHBOARD
    -> BAG panels (behavior, patterns)

bag_patterns
  -> KNOWLEDGE
    -> HiveMind (pattern-aware understanding)
  -> DASHBOARD
    -> Pattern Panel

consensus / conflict_level
  -> KNOWLEDGE
    -> HiveMind (conflict-aware synthesis)
    -> Darwin (proposal priority)
  -> TRADING SCHEMA
    -> Schema confidence adjustment

distance_fingerprint
  -> KNOWLEDGE
    -> Oracle (fingerprint similarity)
  -> PREDICTION
    -> empirical_win_rate per fingerprint

behavior_profile
  -> KNOWLEDGE
    -> HiveMind (behavior-aware understanding)
  -> TRADING SCHEMA
    -> Schema selection (based on behavior profile)
```

### KNOWLEDGE LAYER ARTIFACTS

```
knowledge_snapshot
  -> PREDICTION
    -> summarize (empirical + similarity)
  -> GOVERNANCE
    -> validations, decide (from darwin_proposals)
  -> DASHBOARD
    -> Academy Table, Oracle Panel, HiveMind Panel, CERMIN Panel, Librarian Feed

academy_artifacts
  -> PREDICTION
    -> empirical_win_rate per clone per bucket
  -> GOVERNANCE
    -> Darwin proposals (from win_rate/expectancy)
  -> DASHBOARD
    -> Academy Table

oracle_match
  -> HIVEMIND
    -> synth (oracle_boost)
  -> PREDICTION
    -> similarity_score
  -> DASHBOARD
    -> Oracle Panel

hivemind_understanding
  -> PREDICTION
    -> intelligence_score, dominant_bias
  -> DASHBOARD
    -> HiveMind Panel

cermin_calibration
  -> PREDICTION
    -> calibration_error
  -> GOVERNANCE
    -> Runtime validation
  -> DASHBOARD
    -> CERMIN Panel

darwin_proposals
  -> GOVERNANCE
    -> decide (proposal lifecycle)
  -> DASHBOARD
    -> Governance Proposal Panel
```

### PREDICTION LAYER ARTIFACTS

```
prediction_snapshot
  -> TRADING SCHEMA
    -> Schema confidence adjustment
  -> CONSUMER
    -> intentBuilder (trade intent)
  -> DASHBOARD
    -> Prediction Panel

intelligence_score / dominant_bias
  -> TRADING SCHEMA
    -> Schema selection (based on bias)
  -> CONSUMER
    -> intentBuilder (side determination)
  -> DASHBOARD
    -> Prediction Panel

empirical_win_rate
  -> TRADING SCHEMA
    -> Schema confidence (per clone)
  -> CONSUMER
    -> fundEval (position sizing)
  -> GOVERNANCE
    -> Build validation

cermin_error
  -> GOVERNANCE
    -> Runtime validation (calibration check)
  -> CONSUMER
    -> Confidence honesty display
```

### GOVERNANCE LAYER ARTIFACTS

```
config_version
  -> All layers
    -> BOUNDED parameter update
      -> (main thread, boundary application)

proposal
  -> BENCHMARK
    -> WASIT (walk-forward evaluation)
      -> (Benchmark Worker)
        -> BENCHMARK schema

governance_log / rollback_log
  -> AUDIT
    -> Governance Audit
  -> DASHBOARD
    -> Governance Log Panel

validation_results
  -> DASHBOARD
    -> Governance Validation Panel
  -> AUDIT
    -> Constitution Audit
```

### BENCHMARK LAYER ARTIFACTS

```
benchmark_snapshot
  -> GOVERNANCE
    -> decide (WASIT verdict -> proposal decision)
  -> DASHBOARD
    -> WASIT Panel

wasit_verdict / gates_G1_G5
  -> GOVERNANCE
    -> decide (PASS -> PENDING_HUMAN, FAIL -> REJECTED)
  -> DASHBOARD
    -> WASIT Panel (gate details)

per_fold_metrics
  -> GOVERNANCE
    -> decide (per-fold analysis)
  -> DASHBOARD
    -> Per-Fold Panel
```

### SIMULATION + REPLAY ARTIFACTS

```
simulation_state
  -> REPLAY
    -> create (replay session)
  -> AUDIT
    -> Pipeline Audit
  -> DASHBOARD
    -> Simulation UI

replay_frames
  -> DASHBOARD
    -> Replay Viewer (scrubber + playback)
  -> AUDIT
    -> Replay Determinism Audit

determinism_hash
  -> AUDIT
    -> Determinism verification
  -> DASHBOARD
    -> Audit Panel
```

---

## CONSUMER MATRIX STATUS: LOCKED

Complete artifact-to-consumer chain is frozen. Every artifact has a defined consumer path through layers, components, workers, and schemas. No artifact is left unconsumed.
