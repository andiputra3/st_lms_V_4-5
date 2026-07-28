# 03_COMPONENT_CONTRACT.md

## ST-LMS Implementation Contract Freeze V1 — Component Contract

**Date:** 2026-07-28
**Status:** CONSTITUTIONALLY FROZEN
**Audit:** Components inventoried in 02_ARTIFACT_REGISTRY.md (145 artifacts). This document formalizes component contracts.

---

## COMPONENT RESTRICTION RULE

DILARANG MEMBUAT COMPONENT BARU. Component baru hanya boleh dibuat apabila:
1. Belum pernah didefinisikan dalam registry
2. Wajib untuk BAG, Distance, Trading Schema, atau SQLite
3. Tidak konflik dengan MASTER_SPECIFICATION

---

## 1. TRUTH COMPONENTS

| Component | Owner | Input | Output | Consumer | SQLite | Snapshot | Tests |
|-----------|-------|-------|--------|----------|--------|----------|-------|
| PointBuilder | TRUTH | market_snapshot | truth_point | STRUCTURE, EVIDENCE | truth_snapshots | Truth (W) | indicator accuracy, determinism |
| Supertrend | TRUTH | PointBuilder state | st, stDir, color | STRUCTURE, CLONE | truth_snapshots.st, .st_dir, .st_color | Truth (W) | st computation, flip detection |
| ATR | TRUTH | PointBuilder state | atr | STRUCTURE, CLONE, DISTANCE | truth_snapshots.atr | Truth (W) | ATR period 10 accuracy |
| EMA | TRUTH | PointBuilder state | ema, ema12, ema26 | EVIDENCE, CLONE | truth_snapshots.ema, .ema12, .ema26 | Truth (W) | EMA period 14 accuracy |
| MACD | TRUTH | PointBuilder state | macd, signal, histogram | EVIDENCE | truth_snapshots.macd, .macd_signal, .macd_hist | Truth (W) | MACD 12/26/9 accuracy |
| RSI | TRUTH | PointBuilder state | rsi | EVIDENCE, DASHBOARD | truth_snapshots.rsi | Truth (W) | RSI 0-100 range |
| W%R | TRUTH | PointBuilder state | wpr, vel, acc | EVIDENCE, CLONE | truth_snapshots.wpr | Truth (W) | W%R -100-0 range, exit-only |
| Volume Delta | TRUTH | PointBuilder state | volDelta | EVIDENCE, CLONE | truth_snapshots.volume_delta | Truth (W) | -1 to +1 range |
| Flip Detector | TRUTH | PointBuilder state | flip events | BAG, TRADING SCHEMA | — | Truth (W) | TREND_FLIP detection |

---

## 2. DISTANCE COMPONENTS

| Component | Owner | Input | Output | Consumer | SQLite | Snapshot | Tests |
|-----------|-------|-------|--------|----------|--------|----------|-------|
| Distance-to-ST | TRUTH | close, st | dist, distAtr | CLONE, BAG, KNOWLEDGE | truth_snapshots.dist_to_st, .dist_atr | Truth (W) | NULL during warmup |
| Distance-Ceiling | STRUCTURE | cage.upper, close | dist_ceiling | CLONE (LONG), BAG | structure_snapshots.dist_ceiling | Structure (OD) | NULL on downtrend |
| Distance-Floor | STRUCTURE | cage.lower, close | dist_floor | CLONE (SHORT), BAG | structure_snapshots.dist_floor | Structure (OD) | NULL on uptrend |
| ST_DIST_VOL | EVIDENCE | distAtr series | sdv, p90 | CLONE, BAG | — | — | rolling stddev accuracy |
| Distance Fingerprint | BAG | distAtr trajectory | fingerprint vector | KNOWLEDGE, ORACLE | bag_artifacts.payload_json | — | 12 dimensions present |
| Distance Bucket | DISTANCE | distAtr | bucket label | KNOWLEDGE, BAG | — | — | 5 buckets correct |
| Distance Trend | DISTANCE | distAtr series | trend label | BAG, TRADING SCHEMA | — | — | expanding/contracting/stable |
| Distance Velocity | DISTANCE | distAtr series | velocity | CLONE, BAG | — | — | rate of change correct |

---

## 3. STRUCTURE COMPONENTS

| Component | Owner | Input | Output | Consumer | SQLite | Snapshot | Tests |
|-----------|-------|-------|--------|----------|--------|----------|-------|
| LineBuilder | STRUCTURE | truth_points | line segments | WaveBuilder, CageEngine | — | — | >=4 members per line |
| SlopeBuilder | STRUCTURE | points, lines | slope transitions | WaveBuilder | — | — | 6 pattern types |
| WaveBuilder | STRUCTURE | lines, slopes | wave structures (13) | EVIDENCE, KNOWLEDGE, BAG | wave_history | Structure (W) | all 13 reachable, <6=PENDING |
| CageEngine | STRUCTURE | lineage, price, atr | cage object | CLONE, GRID, BAG | structure_snapshots, cage_history | Structure (W) | HUKUM CAGE, versioning |
| Ladder | STRUCTURE | lines, price | ladder analysis | BAG, TRADING SCHEMA | — | Structure (W) | stepped detection |
| Nearest | STRUCTURE | lines, price | nearest S/R | CLONE | — | Structure (W) | correct nearest |
| Phase | STRUCTURE | cage, wave, stDir | market_phase | CLONE, BAG, TRADING SCHEMA | — | Structure (W) | 4 phases correct |

---

## 4. TRADING COMPONENTS

| Component | Owner | Input | Output | Consumer | SQLite | Snapshot | Tests |
|-----------|-------|-------|--------|----------|--------|----------|-------|
| LONG Clone | CLONE | shared snapshots | LONG observation | TRADE | clone_observations | Clone (W) | entry conjunction, 1 obs/candle |
| SHORT Clone | CLONE | shared snapshots | SHORT observation | TRADE | clone_observations | Clone (W) | mirror LONG, 1 obs/candle |
| GRID Clone | CLONE | structure_snapshot | GRID observation | TRADE | clone_observations | Clone (W) | cage-only, 1 obs/candle |
| Entry Corridor | CLONE | floor, ceiling, close, atr, sdv | corridor zone | CLONE | — | — | adaptive width |
| Entry Marker | TRADE | clone_obs | ENTRY_MARKER | POSITION | trade_markers | Trade (W) | sl, tp calculated |
| Exit Marker | TRADE | position, reason, prices | EXIT_MARKER | STATISTICS | trade_markers | Trade (W) | P&L, after-fee, adverse-first |
| Position Manager | POSITION | entry_marker | position_state | TRADE | positions | — | mae, mfe, hold_c |
| Exit Decider | TRADE | position, market | exit_reason | TRADE | — | — | priority order correct |
| Fee Calculator | TRADE | gross, kind | net, result | STATISTICS | trade_markers.net, .result | Trade (W) | WIN only net>0 |
| Global Risk | CLONE | positions | global_ok | CLONE | — | — | exposure limits |
| Grid Evaluator | CLONE | cage, price, fills | grid_state | TRADE | — | — | fills management |
| Wrong Entry Guard | TRADE | position(hold<=2), truth(vel,close) | wrong_entry flag | TRADE | — | — | early detection |

---

## 5. STATISTICS COMPONENTS

| Component | Owner | Input | Output | Consumer | SQLite | Snapshot | Tests |
|-----------|-------|-------|--------|----------|--------|----------|-------|
| TradeStats | STATISTICS | trade_markers | per-clone metrics | BAG, KNOWLEDGE | trade_statistics | Statistics | sample gate, accuracy |
| MarketStats | STATISTICS | structure, market | market-level metrics | BAG | market_statistics | — | phase distribution |
| Sample Gate | STATISTICS | sample count | CUKUP/BELUM_CUKUP | BAG, KNOWLEDGE | — | Statistics (W) | >=30 = CUKUP |

---

## 6. BAG COMPONENTS

| Component | Owner | Input | Output | Consumer | SQLite | Snapshot | Tests |
|-----------|-------|-------|--------|----------|--------|----------|-------|
| Grouper | BAG | statistics, snapshots | bag_artifacts | KNOWLEDGE | bag_artifacts | — | bag_key unique per session |
| Classifier | BAG | bag_artifacts | bag_kind assignment | KNOWLEDGE | bag_artifacts.bag_kind | — | 6 kinds correct |
| Pattern Miner | BAG | bag_artifacts | bag_patterns | KNOWLEDGE, DASHBOARD | bag_patterns | — | patterns detected |
| Fingerprint Generator | BAG | distance metrics | distance_fingerprint | KNOWLEDGE, ORACLE | bag_artifacts.payload_json | — | 12 dimensions |
| Consensus Engine | BAG | grouped artifacts | consensus score | KNOWLEDGE | bag_artifacts.consensus | — | HIGH/MEDIUM/LOW/NONE |
| Conflict Detector | BAG | grouped artifacts | conflict_level | KNOWLEDGE | bag_artifacts.conflict_level | — | NONE/LOW/MEDIUM/HIGH |
| Maturity Assessor | BAG | artifact stats | maturity_score | KNOWLEDGE | bag_artifacts.payload_json | — | 0-10000 range |
| Behavior Analyzer | BAG | bag_artifacts | behavior_profiles | KNOWLEDGE, TRADING SCHEMA | bag_artifacts.payload_json | — | 6 profiles |
| Compressor | BAG | redundant artifacts | bag_compression | DASHBOARD | bag_compression | — | compression_ratio 0-1 |
| Sequence Analyzer | BAG | wave_history, cage_history | sequence_patterns | KNOWLEDGE | bag_patterns | — | patterns detected |
| Temporal Analyzer | BAG | timestamped artifacts | temporal_patterns | KNOWLEDGE | bag_patterns | — | time patterns |

---

## 7. KNOWLEDGE COMPONENTS

| Component | Owner | Input | Output | Consumer | SQLite | Snapshot | Tests |
|-----------|-------|-------|--------|----------|--------|----------|-------|
| Academy | KNOWLEDGE | BAG + markers + snapshots | win_rate per bucket | PREDICTION, DARWIN | knowledge_artifacts | Knowledge (W) | 4-dim bucket, sample-gated |
| Oracle | KNOWLEDGE | vectors (now + historical) | oracle_match | HIVEMIND, PREDICTION | knowledge_artifacts | Knowledge (W) | euclidean, match>7500 |
| HiveMind | KNOWLEDGE | academy + oracle + evidence | understanding | PREDICTION | knowledge_artifacts | Knowledge (W) | score 0-10000, bias |
| CERMIN | KNOWLEDGE | markers + confidence | calibration_error | PREDICTION, GOVERNANCE | knowledge_artifacts | Knowledge (W) | predicted vs actual |
| Librarian | KNOWLEDGE | academy_artifacts | lifecycle events | DASHBOARD, AUDIT | knowledge_artifacts | Knowledge (W) | 6 statuses |
| Darwin | KNOWLEDGE | academy + BAG | proposals | GOVERNANCE | knowledge_artifacts | Knowledge (W) | no auto-execute |
| River | KNOWLEDGE | all cards | chronicle | AUDIT | — | — | append-only |

---

## 8. PREDICTION COMPONENTS

| Component | Owner | Input | Output | Consumer | SQLite | Snapshot | Tests |
|-----------|-------|-------|--------|----------|--------|----------|-------|
| Summarizer | PREDICTION | knowledge_snapshot | prediction_snapshot | TRADING SCHEMA, CONSUMER | predictions | Prediction | no-model, empirical |
| Empirical Agg | PREDICTION | academy_artifacts | empirical_win_rate | TRADING SCHEMA, CONSUMER | predictions.empirical_win_rate | Prediction (OD) | per clone accuracy |
| Similarity Agg | PREDICTION | oracle_match | similarity_score | TRADING SCHEMA, CONSUMER | predictions.similarity_score | Prediction (W) | 0-10000 range |
| Intelligence Agg | PREDICTION | hivemind | intelligence_score, bias | TRADING SCHEMA, CONSUMER | predictions.confidence | Prediction (W) | 0-10000 range |

---

## 9. BENCHMARK COMPONENTS

| Component | Owner | Input | Output | Consumer | SQLite | Snapshot | Tests |
|-----------|-------|-------|--------|----------|--------|----------|-------|
| WASIT 5-Gate | BENCHMARK | base + cand markers | gates, verdict | GOVERNANCE | benchmark_runs | Benchmark (W) | identical->G2 FAIL |
| Fold Metrics | BENCHMARK | per-fold markers | per-fold stats | GOVERNANCE | benchmark_cases | Benchmark (W) | metrics accuracy |
| Walk-Forward | BENCHMARK | configs, markers | benchmark_snapshot | GOVERNANCE | benchmark_runs | Benchmark (W) | majority vote |
| Parallel Worker | BENCHMARK | base, cand, folds | wasit result | GOVERNANCE | — | — | worker executes |

---

## 10. DASHBOARD COMPONENTS

| Component | Owner | Input | Output | Consumer | SQLite | Tests |
|-----------|-------|-------|--------|----------|--------|-------|
| Geometry Viewer | DASHBOARD | truth + structure + markers | candle chart | Human | — | no-mock render |
| Clone Cards | DASHBOARD | clone_observations | 3 clone panels | Human | — | all 3 rendered |
| Trade History | DASHBOARD | trade_markers | history table | Human | trade_markers | correct P&L display |
| Equity Curve | DASHBOARD | clone.equity | equity chart | Human | — | correct rendering |
| Rapor Table | DASHBOARD | statistics_snapshot | stats table | Human | trade_statistics | sample gate display |
| Academy Table | DASHBOARD | academy_artifacts | bucket table | Human | knowledge_artifacts | 4-dim key display |
| Knowledge Panels | DASHBOARD | oracle, hivemind, cermin | knowledge panels | Human | knowledge_artifacts | all entities displayed |
| Governance UI | DASHBOARD | proposals, validations | proposal management | Human | governance_proposals | approve/reject/rollback |
| Replay Viewer | DASHBOARD | replay_frames | scrubber + playback | Human | replay_frames | 6 kinds supported |
| Prediction Panel | DASHBOARD | prediction_snapshot | prediction display | Human | predictions | no-model indicator |
| Consumer Panel | DASHBOARD | trade_intent | intent preview | Human | — | live-adapter disabled |
| Audit Panel | DASHBOARD | audit_logs, self-tests | audit display | Human | audit_logs | pass/fail indicators |
| SQLite Viewer | DASHBOARD | all tables | table browser | Human | all tables | CRUD operations |
| SQLite Manager | DASHBOARD | database | admin operations | Human | — | backup/restore/vacuum |
| Query Console | DASHBOARD | user SQL | query results | Human | all tables | readonly/transaction/write |

---

## 11. INTEGRATION COMPONENTS

| Component | Owner | Input | Output | Consumer | SQLite | Tests |
|-----------|-------|-------|--------|----------|--------|-------|
| Pipeline Orchestrator | INTEGRATION | pipeline config | execution order | All layers | pipeline_runs | 22 stages in order |
| Worker Bridge | INTEGRATION | worker messages | postMessage results | Main thread | — | protocol correct |
| Card Sharing Enforcer | INTEGRATION | pipeline stages | shared cards | CLONE x3 | — | SHARED 1x, PER-CLONE 3x |
| Unidirectional Guard | INTEGRATION | data flow | violation alerts | AUDIT | — | no backward loops |
| Serial Writer | INTEGRATION | write requests | IndexedDB writes | WORKSPACE | — | single writer, zero race |
| Resource Governor | INTEGRATION | performance.memory | degrade actions | All layers | — | 70/85/95% thresholds |

---

## COMPONENT CONTRACT STATUS: LOCKED

All components across 11 categories are constitutionally frozen. Each component defines owner, responsibility, input, output, consumer, dependency, SQLite table, snapshot usage, and required tests. No new component may be created without Architecture Approval.
