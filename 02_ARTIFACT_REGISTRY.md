# 02_ARTIFACT_REGISTRY.md

## ST-LMS Final Freeze Contract V1 — Artifact Registry

**Date:** 2026-07-28
**Status:** CONSTITUTIONALLY FROZEN — FINAL
**Rule:** NO ARTIFACT WITHOUT OWNER.

---

## ARTIFACT INVENTORY

### MARKET LAYER

| Artifact | Owner | Type | Producer | Consumer | SQLite | Snapshot |
|----------|-------|------|----------|----------|--------|----------|
| market_snapshot | MARKET | Immutable Card | MARKET.process | TRUTH, DASHBOARD | market_candles | Market (W) |
| candle_hygiene_report | MARKET | Validation | MARKET.hygiene | MARKET, AUDIT | — | — |
| gap_report | MARKET | Detection | MARKET.gaps | MARKET, EVIDENCE, AUDIT | market_gaps | — |
| oi_proxy_series | MARKET | Derived Data | MARKET.oiProxy | EVIDENCE, TRUTH | open_interest_series | — |
| data_status | MARKET | Status | MARKET | TRUTH, DASHBOARD | market_candles.data_status | Market (W) |

### TRUTH LAYER

| Artifact | Owner | Type | Producer | Consumer | SQLite | Snapshot |
|----------|-------|------|----------|----------|--------|----------|
| truth_snapshot | TRUTH | Immutable Card | TRUTH.PointBuilder | STRUCTURE, EVIDENCE, DISTANCE, CLONE, BAG, KNOWLEDGE, DASHBOARD | truth_snapshots | Truth (W) |
| truth_point | TRUTH | Internal State | TRUTH.PointBuilder.build | STRUCTURE (LineBuilder) | — | — |
| st | TRUTH | Geometry | TRUTH.PointBuilder | STRUCTURE, DASHBOARD | truth_snapshots.st | Truth (W) |
| stDir | TRUTH | Direction | TRUTH.PointBuilder | CLONE, STRUCTURE, TRADING SCHEMA | truth_snapshots.st_dir | Truth (W) |
| atr | TRUTH | Volatility | TRUTH.PointBuilder | STRUCTURE, CLONE, DISTANCE | truth_snapshots.atr | Truth (W) |
| ema | TRUTH | Trend | TRUTH.PointBuilder | EVIDENCE, CLONE | truth_snapshots.ema | Truth (W) |
| macd_hist | TRUTH | Momentum | TRUTH.PointBuilder | EVIDENCE (HOLD-veto) | truth_snapshots.macd_hist | Truth (W) |
| rsi | TRUTH | Oscillator | TRUTH.PointBuilder | EVIDENCE (exit_bus), DASHBOARD | truth_snapshots.rsi | Truth (W) |
| wpr | TRUTH | Oscillator | TRUTH.PointBuilder | EVIDENCE (exit_bus), DASHBOARD | truth_snapshots.wpr | Truth (W) |
| vel | TRUTH | Momentum | TRUTH.PointBuilder | CLONE (wrong entry), EVIDENCE | — | Truth (W) |
| acc | TRUTH | Momentum | TRUTH.PointBuilder | EVIDENCE (acc_signal) | — | Truth (W) |
| volDelta | TRUTH | Volume | TRUTH.PointBuilder | EVIDENCE (dir_bus), CLONE | truth_snapshots.volume_delta | Truth (W) |
| flip | TRUTH | Event | TRUTH.PointBuilder | BAG, TRADING SCHEMA, DASHBOARD | — | Truth (W) |
| point_status | TRUTH | Status | TRUTH.PointBuilder | CLONE, DASHBOARD | truth_snapshots.truth_status | Truth (W) |
| truth_cache | TRUTH | Cache | TRUTH | TRUTH (internal) | truth_cache | — |

### DISTANCE LAYER (Logical Sub-Layer)

| Artifact | Owner | Type | Producer | Consumer | SQLite | Snapshot |
|----------|-------|------|----------|----------|--------|----------|
| dist | TRUTH | Distance | TRUTH.PointBuilder | DASHBOARD, BAG | truth_snapshots.dist_to_st | Truth (W) |
| distAtr | TRUTH | Distance | TRUTH.PointBuilder | CLONE, EVIDENCE, BAG, KNOWLEDGE, ORACLE | truth_snapshots.dist_atr | Truth (W) |
| dist_ceiling | STRUCTURE | Distance | EVIDENCE.correctionBus | CLONE (LONG: fee_safe), BAG | structure_snapshots.dist_ceiling | Structure (OD) |
| dist_floor | STRUCTURE | Distance | EVIDENCE.correctionBus | CLONE (SHORT: fee_safe), BAG | structure_snapshots.dist_floor | Structure (OD) |
| sdv | EVIDENCE | Volatility | EVIDENCE.StDistVol | CLONE (corridor) | — | — |
| p90 | EVIDENCE | Volatility | EVIDENCE.StDistVol | BAG | — | — |
| distance_fingerprint | BAG | Fingerprint | BAG.fingerprint | KNOWLEDGE, ORACLE, PREDICTION | bag_artifacts.payload_json | — |
| dist_trend | DISTANCE | Derived | DISTANCE | BAG, TRADING SCHEMA | — | — |
| dist_velocity | DISTANCE | Derived | DISTANCE | CLONE, BAG | — | — |
| dist_acceleration | DISTANCE | Derived | DISTANCE | CLONE, BAG | — | — |
| ceiling_floor_ratio | DISTANCE | Derived | DISTANCE | BAG, TRADING SCHEMA | — | — |
| dist_delta | DISTANCE | Derived | DISTANCE | BAG, TRADING SCHEMA | — | — |
| distance_bucket | DISTANCE | Classification | DISTANCE | KNOWLEDGE (Academy), BAG | — | — |

### STRUCTURE LAYER

| Artifact | Owner | Type | Producer | Consumer | SQLite | Snapshot |
|----------|-------|------|----------|----------|--------|----------|
| structure_snapshot | STRUCTURE | Immutable Card | STRUCTURE.compute | EVIDENCE, CLONE, BAG, KNOWLEDGE, TRADING SCHEMA, DASHBOARD | structure_snapshots | Structure |
| lines | STRUCTURE | Geometry | STRUCTURE.LineBuilder | STRUCTURE (WaveBuilder, CageEngine) | — | — |
| slopes | STRUCTURE | Geometry | STRUCTURE.SlopeBuilder | STRUCTURE (WaveBuilder) | — | — |
| waves | STRUCTURE | Classification | STRUCTURE.WaveBuilder | EVIDENCE (MTF), KNOWLEDGE, BAG | wave_history | Structure (W) |
| cage | STRUCTURE | Geometry | STRUCTURE.CageEngine | CLONE, GRID, EVIDENCE, BAG, TRADING SCHEMA | structure_snapshots, cage_history | Structure (W) |
| ladder | STRUCTURE | Pattern | STRUCTURE.ladder | DASHBOARD, BAG, TRADING SCHEMA | — | Structure (W) |
| nearest_support | STRUCTURE | Level | STRUCTURE.nearest | CLONE (SL fallback) | — | Structure (W) |
| nearest_resistance | STRUCTURE | Level | STRUCTURE.nearest | CLONE (SL fallback) | — | Structure (W) |
| market_phase | STRUCTURE | Classification | STRUCTURE.phase | CLONE, BAG, TRADING SCHEMA, DASHBOARD | — | Structure (W) |
| pending_wave | STRUCTURE | Status | STRUCTURE.WaveBuilder | DASHBOARD, TRADING SCHEMA | — | Structure (W) |

### EVIDENCE LAYER

| Artifact | Owner | Type | Producer | Consumer | SQLite | Snapshot |
|----------|-------|------|----------|----------|--------|----------|
| evidence_snapshot | EVIDENCE | Immutable Card | EVIDENCE | CLONE, HIVEMIND, BAG, DASHBOARD | evidence_snapshots | Evidence (W) |
| dir_bus | EVIDENCE | Bus | EVIDENCE.dirBus | CLONE, BAG, DASHBOARD | evidence_snapshots.direction_bus_json | Evidence (W) |
| exit_bus | EVIDENCE | Bus | EVIDENCE.exitBus | CLONE, BAG, DASHBOARD | evidence_snapshots.exit_bus_json | Evidence (W) |
| correction_bus | EVIDENCE | Bus | EVIDENCE.correctionBus | BAG, TRADING SCHEMA, DASHBOARD | evidence_snapshots.correction_bus_json | Evidence (W) |
| oi_score | EVIDENCE | Score | EVIDENCE.oiInherit | EVIDENCE (dir_bus), BAG | — | Evidence (W) |
| mtf_sector | EVIDENCE | Classification | EVIDENCE.mtfSector | EVIDENCE (dir_bus), BAG | — | Evidence (W) |
| max_score | EVIDENCE | Ceiling | EVIDENCE.maxScore | DASHBOARD | evidence_snapshots.max_score | Evidence (W) |
| data_quality | EVIDENCE | Quality | EVIDENCE | CLONE, AUDIT, DASHBOARD | evidence_snapshots.data_quality_json | Evidence (W) |

### CLONE LAYER

| Artifact | Owner | Type | Producer | Consumer | SQLite | Snapshot |
|----------|-------|------|----------|----------|--------|----------|
| clone_observation | CLONE | Immutable Card | CLONE_SHARED.dirObserve/gridObserve | TRADE, STATISTICS, BAG, DASHBOARD | clone_observations | Clone (W) |
| clone_ledger | CLONE | Internal State | CLONE_SHARED.freshClone | CLONE (internal) | — | — |
| corridor | CLONE | Zone | CLONE_SHARED.corridor | CLONE (entry check) | — | — |
| entry_allowed | CLONE | Boolean | CLONE_SHARED | TRADE | — | Clone (W) |
| no_entry_reason | CLONE | String | CLONE_SHARED | BAG, DASHBOARD | — | Clone (W) |
| setup_score | CLONE | Score | CLONE_SHARED | BAG, DASHBOARD | — | Clone (W) |
| confidence | CLONE | Score | CLONE_SHARED | BAG, KNOWLEDGE (CERMIN), DASHBOARD | — | Clone (W) |

### TRADE LAYER

| Artifact | Owner | Type | Producer | Consumer | SQLite | Snapshot |
|----------|-------|------|----------|----------|--------|----------|
| entry_marker | TRADE | Marker | TRADE.mkEntry | POSITION, STATISTICS, BAG, DASHBOARD | trade_markers | Trade (W) |
| exit_marker | TRADE | Marker | TRADE.mkExit | POSITION, STATISTICS, BAG, KNOWLEDGE, DASHBOARD, REPLAY | trade_markers | Trade (W) |
| trade_snapshot | TRADE | Immutable Card | SIMULATION.process | STATISTICS, BAG | trade_markers | Trade (W) |
| gross | TRADE | PnL | TRADE.mkExit | STATISTICS, BAG | trade_markers.gross | Trade (W) |
| net | TRADE | PnL | TRADE.mkExit | STATISTICS, BAG, KNOWLEDGE | trade_markers.net | Trade (W) |
| result | TRADE | Outcome | TRADE.mkExit | STATISTICS, BAG, KNOWLEDGE, ACADEMY | trade_markers.result | Trade (W) |
| fee | TRADE | Cost | TRADE.mkExit | STATISTICS, BAG, BENCHMARK | trade_markers.fee | Trade (W) |
| slip | TRADE | Cost | TRADE.mkExit | STATISTICS, BAG | trade_markers.slip | Trade (W) |

### POSITION LAYER

| Artifact | Owner | Type | Producer | Consumer | SQLite | Snapshot |
|----------|-------|------|----------|----------|--------|----------|
| position_state | POSITION | State | POSITION.update | STATISTICS, BAG, DASHBOARD | positions | — |
| mae | POSITION | Excursion | POSITION.update | STATISTICS, BAG | positions.mae | Trade (W) |
| mfe | POSITION | Excursion | POSITION.update | STATISTICS, BAG | positions.mfe | Trade (W) |
| hold_count | POSITION | Counter | POSITION.update | STATISTICS, BAG, PREDICTION | positions.hold_count | Trade (W) |
| position_timeline | POSITION | History | POSITION | BAG, DASHBOARD, REPLAY | position_timeline | — |

### STATISTICS LAYER

| Artifact | Owner | Type | Producer | Consumer | SQLite | Snapshot |
|----------|-------|------|----------|----------|--------|----------|
| statistics_snapshot | STATISTICS | Immutable Card | STATISTICS.tradeStats | BAG, KNOWLEDGE, PREDICTION, BENCHMARK, DASHBOARD | trade_statistics | Statistics |
| win_rate | STATISTICS | Metric | STATISTICS.tradeStats | BAG, KNOWLEDGE, PREDICTION, DASHBOARD | trade_statistics.win_rate | Statistics (W) |
| expectancy | STATISTICS | Metric | STATISTICS.tradeStats | BAG, KNOWLEDGE, BENCHMARK, DASHBOARD | trade_statistics.expectancy | Statistics (W) |
| pf | STATISTICS | Metric | STATISTICS.tradeStats | BAG, KNOWLEDGE, DASHBOARD | trade_statistics.profit_factor | Statistics (W) |
| fee_drag | STATISTICS | Metric | STATISTICS.tradeStats | BAG, KNOWLEDGE, BENCHMARK | trade_statistics.fee_drag | Statistics (W) |
| wrong_rate | STATISTICS | Metric | STATISTICS.tradeStats | BAG, KNOWLEDGE, DARWIN | trade_statistics.wrong_rate | Statistics (W) |
| sample_status | STATISTICS | Status | STATISTICS.tradeStats | BAG, KNOWLEDGE, DASHBOARD | — | Statistics (W) |
| market_statistics | STATISTICS | Aggregation | STATISTICS | BAG, DASHBOARD | market_statistics | — |

### BAG LAYER

| Artifact | Owner | Type | Producer | Consumer | SQLite | Snapshot |
|----------|-------|------|----------|----------|--------|----------|
| bag_artifact | BAG | Grouped Data | BAG | KNOWLEDGE, PREDICTION, TRADING SCHEMA, BENCHMARK, DASHBOARD | bag_artifacts | — |
| bag_pattern | BAG | Pattern | BAG.pattern_mining | KNOWLEDGE, DASHBOARD | bag_patterns | — |
| bag_compression | BAG | Metric | BAG.compress | DASHBOARD | bag_compression | — |
| consensus | BAG | Score | BAG.consensus | KNOWLEDGE (HiveMind), DASHBOARD | bag_artifacts.consensus | — |
| conflict_level | BAG | Score | BAG.conflict | KNOWLEDGE (Darwin), DASHBOARD | bag_artifacts.conflict_level | — |
| maturity_score | BAG | Score | BAG.maturity | KNOWLEDGE (Librarian), DASHBOARD | bag_artifacts.payload_json | — |
| behavior_profile | BAG | Profile | BAG.behavior_analysis | KNOWLEDGE, TRADING SCHEMA, DASHBOARD | bag_artifacts.payload_json | — |
| sequence_pattern | BAG | Pattern | BAG.sequence_analysis | KNOWLEDGE, DASHBOARD | bag_patterns | — |
| temporal_pattern | BAG | Pattern | BAG.temporal_analysis | KNOWLEDGE, DASHBOARD | bag_patterns | — |
| distance_fingerprint | BAG | Fingerprint | BAG.fingerprint | KNOWLEDGE, ORACLE, PREDICTION | bag_artifacts.payload_json | — |

### KNOWLEDGE LAYER

| Artifact | Owner | Type | Producer | Consumer | SQLite | Snapshot |
|----------|-------|------|----------|----------|--------|----------|
| knowledge_snapshot | KNOWLEDGE | Immutable Card | KNOWLEDGE | PREDICTION, GOVERNANCE, DASHBOARD | knowledge_artifacts | Knowledge (W) |
| academy_artifacts | KNOWLEDGE | Learning | KNOWLEDGE.ACADEMY | PREDICTION, GOVERNANCE, DARWIN, DASHBOARD | knowledge_artifacts | Knowledge (W) |
| oracle_match | KNOWLEDGE | Similarity | KNOWLEDGE.ORACLE | HIVEMIND, PREDICTION, DASHBOARD | knowledge_artifacts | Knowledge (W) |
| hivemind_understanding | KNOWLEDGE | Understanding | KNOWLEDGE.HIVEMIND | PREDICTION, DASHBOARD | knowledge_artifacts | Knowledge (W) |
| cermin_calibration | KNOWLEDGE | Calibration | KNOWLEDGE.CERMIN | PREDICTION, GOVERNANCE, DASHBOARD | knowledge_artifacts | Knowledge (W) |
| librarian_events | KNOWLEDGE | Lifecycle | KNOWLEDGE.LIBRARIAN | DASHBOARD, AUDIT | knowledge_artifacts | Knowledge (W) |
| darwin_proposals | KNOWLEDGE | Proposal | KNOWLEDGE.DARWIN | GOVERNANCE, DASHBOARD | knowledge_artifacts | Knowledge (W) |
| chronicle | KNOWLEDGE | History | KNOWLEDGE.River | AUDIT, DASHBOARD | — | — |

### PREDICTION LAYER

| Artifact | Owner | Type | Producer | Consumer | SQLite | Snapshot |
|----------|-------|------|----------|----------|--------|----------|
| prediction_snapshot | PREDICTION | Immutable Card | PREDICTION.summarize | TRADING SCHEMA, CONSUMER, DASHBOARD | predictions | Prediction |
| intelligence_score | PREDICTION | Score | PREDICTION | TRADING SCHEMA, CONSUMER, DASHBOARD | predictions.confidence | Prediction (W) |
| dominant_bias | PREDICTION | Direction | PREDICTION | TRADING SCHEMA, CONSUMER, DASHBOARD | predictions.predicted_side | Prediction (W) |
| empirical_win_rate | PREDICTION | Probability | PREDICTION | TRADING SCHEMA, CONSUMER, GOVERNANCE | predictions.empirical_win_rate | Prediction (OD) |
| similarity_score | PREDICTION | Score | PREDICTION | TRADING SCHEMA, CONSUMER | predictions.similarity_score | Prediction (W) |
| cermin_error | PREDICTION | Error | PREDICTION | GOVERNANCE, CONSUMER | predictions.cermin_error | Prediction (W) |
| no_model | PREDICTION | Flag | PREDICTION | AUDIT | — | Prediction (W) |

### TRADING SCHEMA LAYER

| Artifact | Owner | Type | Producer | Consumer | SQLite | Snapshot |
|----------|-------|------|----------|----------|--------|----------|
| market_schema_defs | TRADING SCHEMA | Blueprint | TRADING SCHEMA | GOVERNANCE, DASHBOARD | — | — |
| trading_schema_defs | TRADING SCHEMA | Blueprint | TRADING SCHEMA | GOVERNANCE, DASHBOARD | — | — |
| entry_schema_defs | TRADING SCHEMA | Blueprint | TRADING SCHEMA | GOVERNANCE, DASHBOARD | — | — |
| position_schema_defs | TRADING SCHEMA | Blueprint | TRADING SCHEMA | GOVERNANCE, DASHBOARD | — | — |
| exit_schema_defs | TRADING SCHEMA | Blueprint | TRADING SCHEMA | GOVERNANCE, DASHBOARD | — | — |
| schema_confidence_map | TRADING SCHEMA | Mapping | TRADING SCHEMA | GOVERNANCE | — | — |

### GOVERNANCE LAYER

| Artifact | Owner | Type | Producer | Consumer | SQLite | Snapshot |
|----------|-------|------|----------|----------|--------|----------|
| config_version | GOVERNANCE | Config | GOVERNANCE.decide | All layers (BOUNDED params) | app_settings | — |
| proposal | GOVERNANCE | Proposal | GOVERNANCE | BENCHMARK, DASHBOARD | governance_proposals | — |
| governance_log | GOVERNANCE | Log | GOVERNANCE | AUDIT, DASHBOARD | governance_logs | — |
| rollback_log | GOVERNANCE | Log | GOVERNANCE.rollback | AUDIT, DASHBOARD | rollback_logs | — |
| validation_results | GOVERNANCE | Validation | GOVERNANCE.validations | DASHBOARD, AUDIT | — | — |

### BENCHMARK LAYER

| Artifact | Owner | Type | Producer | Consumer | SQLite | Snapshot |
|----------|-------|------|----------|----------|--------|----------|
| benchmark_snapshot | BENCHMARK | Immutable Card | BENCHMARK.wasit | GOVERNANCE, DASHBOARD | benchmark_runs | Benchmark (W) |
| wasit_verdict | BENCHMARK | Verdict | BENCHMARK.wasit | GOVERNANCE | benchmark_runs.verdict | Benchmark (W) |
| gates_G1_G5 | BENCHMARK | Gates | BENCHMARK.wasit | GOVERNANCE, DASHBOARD | benchmark_runs.gates_json | Benchmark (W) |
| per_fold_metrics | BENCHMARK | Metrics | BENCHMARK.wasit | GOVERNANCE, DASHBOARD | benchmark_cases | Benchmark (W) |

### SIMULATION LAYER

| Artifact | Owner | Type | Producer | Consumer | SQLite | Snapshot |
|----------|-------|------|----------|----------|--------|----------|
| simulation_state | SIMULATION | State | SIMULATION.freshState | REPLAY, AUDIT, DASHBOARD | pipeline_runs | — |
| determinism_hash | SIMULATION | Hash | SIMULATION.determinismHash | AUDIT | — | — |
| pipeline_run | SIMULATION | Run | SIMULATION.computeAll | AUDIT, DASHBOARD | pipeline_runs | — |

### REPLAY LAYER

| Artifact | Owner | Type | Producer | Consumer | SQLite | Snapshot |
|----------|-------|------|----------|----------|--------|----------|
| replay_session | REPLAY | Session | REPLAY.create | DASHBOARD, AUDIT | replay_sessions | — |
| replay_frames | REPLAY | Frames | REPLAY | DASHBOARD, AUDIT | replay_frames | — |

### DASHBOARD LAYER

| Artifact | Owner | Type | Producer | Consumer | SQLite | Snapshot |
|----------|-------|------|----------|----------|--------|----------|
| geometry_chart | DASHBOARD | UI | VIEW.drawGeom | Human | — | — |
| clone_cards | DASHBOARD | UI | VIEW.renderClone | Human | — | — |
| trade_history | DASHBOARD | UI | VIEW.renderTrade | Human | — | — |
| equity_curve | DASHBOARD | UI | VIEW.drawEq | Human | — | — |
| rapor_table | DASHBOARD | UI | VIEW (renderTrade) | Human | — | — |
| academy_table | DASHBOARD | UI | VIEW.renderKnow | Human | — | — |
| knowledge_panels | DASHBOARD | UI | VIEW.renderKnow | Human | — | — |
| governance_ui | DASHBOARD | UI | VIEW.renderGov | Human | — | — |
| simulation_ui | DASHBOARD | UI | VIEW.renderSim | Human | — | — |
| replay_viewer | DASHBOARD | UI | VIEW.renderReplay | Human | — | — |
| prediction_panel | DASHBOARD | UI | VIEW.renderPred | Human | — | — |
| consumer_panel | DASHBOARD | UI | VIEW.renderConsumer | Human | — | — |
| audit_panel | DASHBOARD | UI | VIEW.renderAudit | Human | — | — |
| final_validation | DASHBOARD | UI | VIEW.renderFinalValidation | Human | — | — |
| csv_export | DASHBOARD | Export | CONSUMER.exportCSV | Human | — | — |

### INTEGRATION LAYER

| Artifact | Owner | Type | Producer | Consumer | SQLite | Snapshot |
|----------|-------|------|----------|----------|--------|----------|
| worker_bridge | INTEGRATION | Bridge | INTEGRATION | All workers | — | — |
| pipeline_orchestrator | INTEGRATION | Orchestrator | INTEGRATION | All layers | — | — |

### FINAL VALIDATION LAYER

| Artifact | Owner | Type | Producer | Consumer | SQLite | Snapshot |
|----------|-------|------|----------|----------|--------|----------|
| validation_results | FINAL VALIDATION | Report | FINAL_VALIDATION.runAll | DASHBOARD, GOVERNANCE | — | — |
| self_test_results | FINAL VALIDATION | Report | AUDIT.run | DASHBOARD, GOVERNANCE | — | — |
| domain_audit | FINAL VALIDATION | Report | AUDIT.domains | DASHBOARD, GOVERNANCE | audit_logs | — |
| fingerprint | FINAL VALIDATION | Hash | AUDIT.fingerprint | DASHBOARD | — | — |

---

## ARTIFACT SUMMARY

| Layer | Artifact Count |
|-------|---------------|
| MARKET | 5 |
| TRUTH | 15 |
| DISTANCE | 13 |
| STRUCTURE | 10 |
| EVIDENCE | 8 |
| CLONE | 7 |
| TRADE | 8 |
| POSITION | 5 |
| STATISTICS | 8 |
| BAG | 10 |
| KNOWLEDGE | 8 |
| PREDICTION | 7 |
| TRADING SCHEMA | 6 |
| GOVERNANCE | 5 |
| BENCHMARK | 4 |
| SIMULATION | 3 |
| REPLAY | 2 |
| DASHBOARD | 15 |
| INTEGRATION | 2 |
| FINAL VALIDATION | 4 |
| **TOTAL** | **145** |

---

## ARTIFACT REGISTRY STATUS: LOCKED

All 145 artifacts across 20 layers are registered with owner, type, producer, consumer, SQLite mapping, and snapshot mapping. NO ARTIFACT WITHOUT OWNER.
