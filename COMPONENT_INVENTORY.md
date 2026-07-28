# COMPONENT_INVENTORY.md

## ST-LMS v3 — Complete Component Inventory

**Date:** 2026-07-28
**Phase:** PHASE 0 — Prompt 01
**Source:** All 5 reference files (MASTER_SPECIFICATION, DOCUMENT_DEPENDENCY, QWEN_14_DOC, ST_LMS_CORE, 01-07_IMPLEMENTATION_AUDIT)

---

## INVENTORY LEGEND

| Status | Meaning |
|--------|---------|
| FROZEN | Constitutionally frozen — cannot change |
| IMPLEMENTED | Code exists in ST_LMS_CORE.js |
| PARTIAL | Partially implemented |
| NOT_IMPLEMENTED | Specified but no code yet |
| FIXED | Was broken, now fixed per audit |

---

## 1. BOOT

| Component | Responsibilities | Dependencies | Status | Source File | Implementation Status | Specification Status |
|-----------|-----------------|--------------|--------|-------------|----------------------|---------------------|
| Runtime Initializer | Establish system physics, load config, init workspace | None | FROZEN | MASTER §6, QWEN_DOC D0 | IMPLEMENTED (ST_LMS_CORE: init) | COMPLETE |
| Resource Governor | Monitor RAM/CPU, degrade under pressure | BOOT | FROZEN | QWEN_DOC D4.2 | NOT_IMPLEMENTED | COMPLETE |
| Configuration Manager | Load/apply/store config, bounded registry | BOOT | FROZEN | ST_LMS_CORE: CONFIG | IMPLEMENTED | COMPLETE |
| Workspace Manager | Manage tiered storage, open/close workspaces | BOOT | FROZEN | ST_LMS_CORE: WORKSPACE | PARTIAL | COMPLETE |
| Checkpoint Manager | Save/resume state, hot-window recompute | BOOT | FROZEN | QWEN_DOC D3.3 | NOT_IMPLEMENTED | COMPLETE |

**Total: 5 components** | IMPLEMENTED: 2 | PARTIAL: 1 | NOT_IMPLEMENTED: 2

---

## 2. WORKSPACE

| Component | Responsibilities | Dependencies | Status | Source File | Implementation Status | Specification Status |
|-----------|-----------------|--------------|--------|-------------|----------------------|---------------------|
| IndexedDB Writer (Serial) | Single writer on main thread, append-only cards | BOOT | FROZEN | ST_LMS_CORE: WORKSPACE | IMPLEMENTED | COMPLETE |
| Tiered Storage (L1–L5) | Hot/Warm/Cold/Archive/Evict layers | BOOT | FROZEN | QWEN_DOC D3.1 | NOT_IMPLEMENTED | COMPLETE |
| Object Store Manager | Cards, config_state, checkpoints, governance, audit_log, runs | WORKSPACE | FROZEN | QWEN_DOC D3.2 | PARTIAL | COMPLETE |
| Eviction Manager | Age-based + last-logical-access eviction | WORKSPACE | FROZEN | QWEN_DOC D3.3 | NOT_IMPLEMENTED | COMPLETE |
| Compression Manager | CompressionStream for cold/archive tier writes | WORKSPACE | FROZEN | QWEN_DOC D3.1 | NOT_IMPLEMENTED | COMPLETE |

**Total: 5 components** | IMPLEMENTED: 1 | PARTIAL: 1 | NOT_IMPLEMENTED: 3

---

## 3. MARKET

| Component | Responsibilities | Dependencies | Status | Source File | Implementation Status | Specification Status |
|-----------|-----------------|--------------|--------|-------------|----------------------|---------------------|
| Market Data Layer | Fetch/import OHLCV data, WebSocket feed | BOOT | FROZEN | ST_LMS_CORE: MARKET.fixture | PARTIAL (fixture only) | COMPLETE |
| Market Snapshot Engine | Produce market_snapshot card per closed candle | MARKET | FROZEN | ST_LMS_CORE: process() | IMPLEMENTED | COMPLETE |
| Data Hygiene Validator | Validate candle integrity (H≥O,C; L≤O,C; H≥L) | MARKET | FROZEN | ST_LMS_CORE: MARKET.hygiene | IMPLEMENTED | COMPLETE |
| Gap Detector | Detect time gaps between candles | MARKET | FROZEN | ST_LMS_CORE: MARKET.gaps | IMPLEMENTED | COMPLETE |
| Derived TF Aggregator | Aggregate 1m → higher TF (via worker) | MARKET | FROZEN | QWEN_DOC D5 (data.worker) | NOT_IMPLEMENTED | COMPLETE |
| OI Proxy Generator | Derive OI from volume + takerBuyRatio | MARKET | FROZEN | ST_LMS_CORE: MARKET.oiProxy | IMPLEMENTED | COMPLETE |
| Cascade Handler | Handle missing candles, fill gaps | MARKET | FROZEN | QWEN_DOC D5 | NOT_IMPLEMENTED | COMPLETE |

**Total: 7 components** | IMPLEMENTED: 4 | PARTIAL: 1 | NOT_IMPLEMENTED: 2

---

## 4. TRUTH

| Component | Responsibilities | Dependencies | Status | Source File | Implementation Status | Specification Status |
|-----------|-----------------|--------------|--------|-------------|----------------------|---------------------|
| Point Builder | Compute st, atr, ema, macd, rsi, wpr, vel, acc per candle | MARKET | FROZEN | ST_LMS_CORE: TRUTH.PointBuilder | IMPLEMENTED | COMPLETE |
| Supertrend | Directional line (st, stDir, color) | TRUTH | FROZEN | ST_LMS_CORE: TRUTH.PointBuilder | IMPLEMENTED | COMPLETE |
| ATR (Average True Range) | Volatility measure (period 10) | TRUTH | FROZEN | ST_LMS_CORE: TRUTH.PointBuilder | IMPLEMENTED | COMPLETE |
| EMA (Exponential Moving Average) | Trend indicator (period 14) | TRUTH | FROZEN | ST_LMS_CORE: TRUTH.PointBuilder | IMPLEMENTED | COMPLETE |
| MACD | 12/26/9 MACD with signal and histogram | TRUTH | FROZEN | ST_LMS_CORE: TRUTH.PointBuilder | IMPLEMENTED | COMPLETE |
| RSI (Relative Strength Index) | Momentum oscillator (period 10) | TRUTH | FROZEN | ST_LMS_CORE: TRUTH.PointBuilder | IMPLEMENTED | COMPLETE |
| W%R (Williams %R) | Exit-only momentum indicator (period 14) | TRUTH | FROZEN | ST_LMS_CORE: TRUTH.PointBuilder | IMPLEMENTED | COMPLETE |
| W%R Velocity | Rate of change of W%R | TRUTH | FROZEN | ST_LMS_CORE: TRUTH.PointBuilder | IMPLEMENTED | COMPLETE |
| W%R Acceleration | Rate of change of W%R velocity | TRUTH | FROZEN | ST_LMS_CORE: TRUTH.PointBuilder | IMPLEMENTED | COMPLETE |
| Distance-to-ST | Absolute distance from close to supertrend | TRUTH | FROZEN | ST_LMS_CORE: TRUTH.PointBuilder | IMPLEMENTED | COMPLETE |
| Distance-to-ST / ATR | Normalized distance-to-ST | TRUTH | FROZEN | ST_LMS_CORE: TRUTH.PointBuilder | IMPLEMENTED | COMPLETE |
| Volume Delta | Net volume direction (2*takerBuyRatio - 1) | TRUTH | FROZEN | ST_LMS_CORE: TRUTH.PointBuilder | IMPLEMENTED | COMPLETE |
| Line Builder | Build line segments from supertrend points | TRUTH | FROZEN | ST_LMS_CORE: STRUCTURE.LineBuilder | IMPLEMENTED | COMPLETE |
| Slope Builder | Build slope transitions between lines | TRUTH | FROZEN | ST_LMS_CORE: STRUCTURE.SlopeBuilder | IMPLEMENTED | COMPLETE |
| Wave Builder | Classify wave structures (13 types) | TRUTH | FROZEN | ST_LMS_CORE: STRUCTURE.WaveBuilder | IMPLEMENTED (FIXED) | COMPLETE |
| Versioning | Line version tracking (v0→v1→v2) | TRUTH | FROZEN | ST_LMS_CORE: STRUCTURE.CageEngine | IMPLEMENTED | COMPLETE |
| Validation | Point status (WARMUP/VALID) | TRUTH | FROZEN | ST_LMS_CORE: TRUTH.PointBuilder | IMPLEMENTED | COMPLETE |
| Flip Detector | Detect trend flip events (TREND_FLIP_UP/DOWN) | TRUTH | FROZEN | ST_LMS_CORE: TRUTH.PointBuilder | IMPLEMENTED | COMPLETE |

**Total: 18 components** | IMPLEMENTED: 18 | PARTIAL: 0 | NOT_IMPLEMENTED: 0

---

## 5. STRUCTURE

| Component | Responsibilities | Dependencies | Status | Source File | Implementation Status | Specification Status |
|-----------|-----------------|--------------|--------|-------------|----------------------|---------------------|
| Cage Engine | Compute cage (upper/lower/pp/rangeAtr/breakout) | TRUTH | FROZEN | ST_LMS_CORE: STRUCTURE.CageEngine | IMPLEMENTED | COMPLETE |
| Wall Resolver | Resolve support/resistance walls with versioning | TRUTH | FROZEN | ST_LMS_CORE: STRUCTURE.CageEngine._resolve | IMPLEMENTED | COMPLETE |
| Ladder Analyzer | Check stepped support/resistance patterns | STRUCTURE | FROZEN | ST_LMS_CORE: STRUCTURE.ladder | IMPLEMENTED | COMPLETE |
| Nearest Support/Resistance | Find nearest support and resistance lines | STRUCTURE | FROZEN | ST_LMS_CORE: STRUCTURE.nearest | IMPLEMENTED | COMPLETE |
| Escape Path | Find "comfortable" wall (distance ≥ threshold·ATR) | STRUCTURE | FROZEN | ST_LMS_CORE: STRUCTURE.CageEngine._resolve | IMPLEMENTED | COMPLETE |
| Distance Ceiling | Ceiling distance = ceiling - close | STRUCTURE | FROZEN | ST_LMS_CORE: EVIDENCE.correctionBus | IMPLEMENTED | COMPLETE |
| Distance Floor | Floor distance = close - floor | STRUCTURE | FROZEN | ST_LMS_CORE: EVIDENCE.correctionBus | IMPLEMENTED | COMPLETE |
| Price Position (pp) | Position within cage (0–1) | STRUCTURE | FROZEN | ST_LMS_CORE: STRUCTURE.CageEngine | IMPLEMENTED | COMPLETE |
| Market Phase | Determine market phase from cage+wave+stDir | STRUCTURE | FROZEN | ST_LMS_CORE: STRUCTURE.phase | IMPLEMENTED | COMPLETE |
| Cluster Analyzer | 5-day cluster analysis | STRUCTURE | FROZEN | QWEN_DOC D6 (cluster field) | NOT_IMPLEMENTED | COMPLETE |

**Total: 10 components** | IMPLEMENTED: 9 | PARTIAL: 0 | NOT_IMPLEMENTED: 1

---

## 6. EVIDENCE

| Component | Responsibilities | Dependencies | Status | Source File | Implementation Status | Specification Status |
|-----------|-----------------|--------------|--------|-------------|----------------------|---------------------|
| Direction Bus | Entry-legal witnesses: EMA, OI, VolDelta, MTF | TRUTH | FROZEN | ST_LMS_CORE: EVIDENCE.dirBus | IMPLEMENTED | COMPLETE |
| Exit Bus | Close-only exit signals: RSI, W%R, MACD, HOLD-veto | TRUTH | FROZEN | ST_LMS_CORE: EVIDENCE.exitBus | IMPLEMENTED | COMPLETE |
| Correction Bus | Market context: pp, phase, distances, wave, cage | TRUTH, STRUCTURE | FROZEN | ST_LMS_CORE: EVIDENCE.correctionBus | IMPLEMENTED (FIXED) | COMPLETE |
| OI Inheritor | Inherit OI from proxy, freshness-weighted score | MARKET | FROZEN | ST_LMS_CORE: EVIDENCE.oiInherit | IMPLEMENTED | COMPLETE |
| Volume Delta Processor | Volume delta for evidence scoring | TRUTH | FROZEN | ST_LMS_CORE: EVIDENCE.dirBus | IMPLEMENTED | COMPLETE |
| MTF Sector | Multi-timeframe sector classification from wave structure | STRUCTURE | FROZEN | ST_LMS_CORE: EVIDENCE.mtfSector | IMPLEMENTED | COMPLETE |
| Max Score | Data quality ceiling for evidence scoring | EVIDENCE | FROZEN | ST_LMS_CORE: EVIDENCE.maxScore | IMPLEMENTED | COMPLETE |
| ST-Dist-Vol | Standard deviation of distance-to-ST (volatility proxy) | TRUTH | FROZEN | ST_LMS_CORE: EVIDENCE.StDistVol | IMPLEMENTED | COMPLETE |

**Total: 8 components** | IMPLEMENTED: 8 | PARTIAL: 0 | NOT_IMPLEMENTED: 0

---

## 7. CLONE (LONG/SHORT/GRID)

| Component | Responsibilities | Dependencies | Status | Source File | Implementation Status | Specification Status |
|-----------|-----------------|--------------|--------|-------------|----------------------|---------------------|
| LONG Clone | Directional LONG observation, entry, exit, ledger | STRUCTURE, EVIDENCE | FROZEN | ST_LMS_CORE: LONG_CLONE, CLONE_SHARED | IMPLEMENTED | COMPLETE |
| SHORT Clone | Directional SHORT observation (mirror of LONG) | STRUCTURE, EVIDENCE | FROZEN | ST_LMS_CORE: SHORT_CLONE, CLONE_SHARED | IMPLEMENTED | COMPLETE |
| GRID Clone | Range-bound GRID fills, entry/exit, ledger | STRUCTURE | FROZEN | ST_LMS_CORE: GRID_CLONE, CLONE_SHARED | IMPLEMENTED | COMPLETE |
| Clone Orchestrator | Manage clone activation, global exposure limits | CLONE | FROZEN | ST_LMS_CORE: CLONE_SHARED | IMPLEMENTED | COMPLETE |
| Adaptive Entry Corridor | Compute corridor zone for directional entries | CLONE | FROZEN | ST_LMS_CORE: CLONE_SHARED.corridor | IMPLEMENTED | COMPLETE |
| Global Risk Validator | Global risk check before entry (gross/net exposure) | CLONE | FROZEN | ST_LMS_CORE: process() (globalOk) | IMPLEMENTED | COMPLETE |
| Observation Card (per clone) | Record hypothesis per candle (including no-trade reasons) | CLONE | FROZEN | ST_LMS_CORE: dirObserve, gridObserve | IMPLEMENTED | COMPLETE |
| Grid State Evaluator | Evaluate grid state: active, bias, fills, range, pp | CLONE | FROZEN | ST_LMS_CORE: CLONE_SHARED.gridObserve | IMPLEMENTED | COMPLETE |

**Total: 8 components** | IMPLEMENTED: 8 | PARTIAL: 0 | NOT_IMPLEMENTED: 0

---

## 8. TRADE

| Component | Responsibilities | Dependencies | Status | Source File | Implementation Status | Specification Status |
|-----------|-----------------|--------------|--------|-------------|----------------------|---------------------|
| Entry Marker | Create ENTRY marker with price, SL, TP | CLONE | FROZEN | ST_LMS_CORE: TRADE.mkEntry | IMPLEMENTED | COMPLETE |
| Exit Marker | Create EXIT marker with P&L (after-fee, adverse-first) | CLONE, POSITION | FROZEN | ST_LMS_CORE: TRADE.mkExit | IMPLEMENTED (FIXED) | COMPLETE |
| Adaptive TP | Compute adaptive take-profit level (ATR-based, cage-bounded) | CLONE | FROZEN | ST_LMS_CORE: dirObserve (tp calc) | IMPLEMENTED | COMPLETE |
| Wrong Entry Guard | Detect and flag wrong entry (velocity/geometry based) | CLONE | FROZEN | ST_LMS_CORE: CLONE_SHARED.decideClose | IMPLEMENTED | COMPLETE |
| Trade Marker | Aggregate markers per candle per clone | TRADE | FROZEN | ST_LMS_CORE: process() | IMPLEMENTED | COMPLETE |

**Total: 5 components** | IMPLEMENTED: 5 | PARTIAL: 0 | NOT_IMPLEMENTED: 0

---

## 9. POSITION

| Component | Responsibilities | Dependencies | Status | Source File | Implementation Status | Specification Status |
|-----------|-----------------|--------------|--------|-------------|----------------------|---------------------|
| Position Manager | Track open positions (entry, SL, TP) | TRADE | FROZEN | ST_LMS_CORE: POSITION | IMPLEMENTED | COMPLETE |
| MAE/MFE Tracker | Track Maximum Adverse/ Favorable Excursion | POSITION | FROZEN | ST_LMS_CORE: POSITION.update | IMPLEMENTED | COMPLETE |
| Profit Lock | Partial take-profit management | POSITION | FROZEN | QWEN_DOC D8.2 | NOT_IMPLEMENTED | COMPLETE |
| Trailing Stop | ATR-based trailing stop | POSITION | FROZEN | QWEN_DOC D8.2 | NOT_IMPLEMENTED | COMPLETE |
| Breakeven Manager | Move SL to breakeven after profit threshold | POSITION | FROZEN | QWEN_DOC D8.2 | NOT_IMPLEMENTED | COMPLETE |
| Forced/Emergency Exit | Force close positions under extreme conditions | POSITION | FROZEN | QWEN_DOC D0 (Position domain) | NOT_IMPLEMENTED | COMPLETE |
| Risk Validator | Validate position risk (size, leverage, drawdown) | POSITION | FROZEN | QWEN_DOC D0 (Position domain) | NOT_IMPLEMENTED | COMPLETE |
| Liquidation Avoidance | Prevent liquidation via early exit | POSITION | FROZEN | QWEN_DOC D0 (Position domain) | NOT_IMPLEMENTED | COMPLETE |

**Total: 8 components** | IMPLEMENTED: 2 | PARTIAL: 0 | NOT_IMPLEMENTED: 6

---

## 10. STATISTICS

| Component | Responsibilities | Dependencies | Status | Source File | Implementation Status | Specification Status |
|-----------|-----------------|--------------|--------|-------------|----------------------|---------------------|
| Trade Statistics | Compute win_rate, expectancy, PF, MAE, MFE, fee_drag, wrong_rate | TRADE | FROZEN | ST_LMS_CORE: STATISTICS.tradeStats | IMPLEMENTED | COMPLETE |
| Market Statistics | Market-level statistics aggregation | STATISTICS | FROZEN | QWEN_DOC D0 (Statistics domain) | NOT_IMPLEMENTED | COMPLETE |
| Clone Statistics | Per-clone statistics with sample-gating | STATISTICS | FROZEN | ST_LMS_CORE: STATISTICS.tradeStats | IMPLEMENTED | COMPLETE |
| Sample Gate | Enforce sample≥30 threshold for confidence | STATISTICS | FROZEN | ST_LMS_CORE: STATISTICS.tradeStats | IMPLEMENTED | COMPLETE |

**Total: 4 components** | IMPLEMENTED: 3 | PARTIAL: 0 | NOT_IMPLEMENTED: 1

---

## 11. KNOWLEDGE

| Component | Responsibilities | Dependencies | Status | Source File | Implementation Status | Specification Status |
|-----------|-----------------|--------------|--------|-------------|----------------------|---------------------|
| Academy | Build empirical win_rate per (clone, structure, distance_bucket, reason) | STATISTICS | FROZEN | ST_LMS_CORE: KNOWLEDGE.ACADEMY | IMPLEMENTED (FIXED) | COMPLETE |
| River | Append-only archivist + index + chronicle | All cards | FROZEN | ST_LMS_CORE: WORKSPACE (River via chronicle) | IMPLEMENTED | COMPLETE |
| Oracle | Euclidean similarity matching (vector beku, match>7500) | TRUTH, STRUCTURE, EVIDENCE | FROZEN | ST_LMS_CORE: KNOWLEDGE.ORACLE | IMPLEMENTED | COMPLETE |
| HiveMind | Synthesize market understanding (score+bias+boost) | Academy, Oracle, EVIDENCE | FROZEN | ST_LMS_CORE: KNOWLEDGE.HIVEMIND | IMPLEMENTED | COMPLETE |
| Darwin | Propose parameter mutations (Kelas-A bounded / Kelas-B PEX) | Academy | FROZEN | ST_LMS_CORE: KNOWLEDGE.DARWIN | IMPLEMENTED | COMPLETE |
| Librarian | Lifecycle management (NEW→OBS→TRUSTED→MATURE/DEAD/DEPRECATED) | Academy | FROZEN | ST_LMS_CORE: KNOWLEDGE.LIBRARIAN | IMPLEMENTED (FIXED) | COMPLETE |
| CERMIN | Calibration error tracking (predicted vs actual per clone) | STATISTICS | FROZEN | ST_LMS_CORE: KNOWLEDGE.CERMIN | IMPLEMENTED | COMPLETE |

**Total: 7 components** | IMPLEMENTED: 7 | PARTIAL: 0 | NOT_IMPLEMENTED: 0

---

## 12. PREDICTION

| Component | Responsibilities | Dependencies | Status | Source File | Implementation Status | Specification Status |
|-----------|-----------------|--------------|--------|-------------|----------------------|---------------------|
| Historical Similarity | Oracle-based similarity score | KNOWLEDGE (Oracle) | FROZEN | ST_LMS_CORE: PREDICTION.summarize | IMPLEMENTED | COMPLETE |
| Market Probability | Empirical win_rate from Academy per clone per bucket | KNOWLEDGE (Academy) | FROZEN | ST_LMS_CORE: PREDICTION.summarize | IMPLEMENTED | COMPLETE |
| Market Intelligence | HiveMind understanding as prediction input | KNOWLEDGE (HiveMind) | FROZEN | ST_LMS_CORE: PREDICTION.summarize | IMPLEMENTED | COMPLETE |
| CERMIN Calibration | Calibration error for confidence honesty | KNOWLEDGE (CERMIN) | FROZEN | ST_LMS_CORE: PREDICTION.summarize | IMPLEMENTED | COMPLETE |

**Total: 4 components** | IMPLEMENTED: 4 | PARTIAL: 0 | NOT_IMPLEMENTED: 0

---

## 13. REPLAY

| Component | Responsibilities | Dependencies | Status | Source File | Implementation Status | Specification Status |
|-----------|-----------------|--------------|--------|-------------|----------------------|---------------------|
| Candle Replay | Replay market_snapshot sequence | MARKET | FROZEN | ST_LMS_CORE: REPLAY.create | IMPLEMENTED | COMPLETE |
| Snapshot Replay | Replay full 10-snapshot frame per candle | All snapshots | FROZEN | ST_LMS_CORE: REPLAY.create | IMPLEMENTED | COMPLETE |
| Trade Replay | Replay trade markers + equity per clone | TRADE | FROZEN | ST_LMS_CORE: REPLAY.create | IMPLEMENTED | COMPLETE |
| Clone Replay | Replay clone observations + positions + grid | CLONE | FROZEN | ST_LMS_CORE: REPLAY.create | IMPLEMENTED | COMPLETE |
| Knowledge Replay | Replay knowledge artifact evolution | KNOWLEDGE | FROZEN | ST_LMS_CORE: REPLAY.create | IMPLEMENTED | COMPLETE |
| Governance Replay | Replay governance decisions + rollback timeline | GOVERNANCE | FROZEN | ST_LMS_CORE: REPLAY.create | IMPLEMENTED | COMPLETE |

**Total: 6 components** | IMPLEMENTED: 6 | PARTIAL: 0 | NOT_IMPLEMENTED: 0

---

## 14. SIMULATION

| Component | Responsibilities | Dependencies | Status | Source File | Implementation Status | Specification Status |
|-----------|-----------------|--------------|--------|-------------|----------------------|---------------------|
| Simulation Engine | Execute clone intent against candles (adverse-first) | All pipeline | FROZEN | ST_LMS_CORE: SIMULATION | IMPLEMENTED | COMPLETE |
| Historical Simulation | Replay fixture/IndexedDB deterministically | SIMULATION | FROZEN | ST_LMS_CORE: SIMULATION.computeAll | IMPLEMENTED | COMPLETE |
| Live Simulation | Feed 1m real-time (fetch/WS with offline fallback) | SIMULATION | FROZEN | QWEN_DOC D8.1 | NOT_IMPLEMENTED | COMPLETE |
| Strategy Simulation | Isolate one clone for study | SIMULATION | FROZEN | ST_LMS_CORE: VIEW.runSim | PARTIAL | COMPLETE |
| Clone Simulation | 3 clones simultaneously with isolated ledgers | SIMULATION | FROZEN | ST_LMS_CORE: SIMULATION.computeAll | IMPLEMENTED | COMPLETE |
| Determinism Verifier | Verify determinism with dual-run hash comparison | SIMULATION | FROZEN | ST_LMS_CORE: SIMULATION.determinismHash | IMPLEMENTED | COMPLETE |

**Total: 6 components** | IMPLEMENTED: 4 | PARTIAL: 1 | NOT_IMPLEMENTED: 1

---

## 15. GOVERNANCE

| Component | Responsibilities | Dependencies | Status | Source File | Implementation Status | Specification Status |
|-----------|-----------------|--------------|--------|-------------|----------------------|---------------------|
| Constitution Validation | Validate 18 laws + authority matrix compliance | All domains | FROZEN | ST_LMS_CORE: GOVERNANCE.validations | IMPLEMENTED | COMPLETE |
| Proposal Validation | Bounded-check + label-peran + constitutional-atom | GOVERNANCE | FROZEN | ST_LMS_CORE: GOVERNANCE | IMPLEMENTED | COMPLETE |
| Authority Matrix Validation | Verify indicators used only in valid columns | All domains | FROZEN | ST_LMS_CORE: GOVERNANCE.validations | IMPLEMENTED | COMPLETE |
| Build Validation | Verify 15 build-stop rules + inventory + determinism | All domains | FROZEN | ST_LMS_CORE: GOVERNANCE.validations | IMPLEMENTED | COMPLETE |
| Runtime Validation | Checksum cards, lineage, no-race writer, sample-gate | All domains | FROZEN | ST_LMS_CORE: GOVERNANCE.validations | IMPLEMENTED | COMPLETE |
| Governance Audit | Decision timeline, rollback, deprecated enforcement | GOVERNANCE | FROZEN | ST_LMS_CORE: GOVERNANCE.validations | IMPLEMENTED | COMPLETE |
| Proposal Engine | Darwin writes, WASIT filters, human approves | GOVERNANCE | FROZEN | ST_LMS_CORE: GOVERNANCE.decide | IMPLEMENTED | COMPLETE |
| Bounded Registry | Auto-reject values outside range | CONFIG | FROZEN | ST_LMS_CORE: CONFIG | IMPLEMENTED | COMPLETE |
| Rollback Manager | Deterministic rollback to previous config_version | GOVERNANCE | FROZEN | ST_LMS_CORE: GOVERNANCE.rollback | IMPLEMENTED | COMPLETE |

**Total: 9 components** | IMPLEMENTED: 9 | PARTIAL: 0 | NOT_IMPLEMENTED: 0

---

## 16. CONSUMER

| Component | Responsibilities | Dependencies | Status | Source File | Implementation Status | Specification Status |
|-----------|-----------------|--------------|--------|-------------|----------------------|---------------------|
| API Layer | Internal query API for IndexedDB cards | All domains | FROZEN | ST_LMS_CORE: CONSUMER | PARTIAL | COMPLETE |
| Dashboard | Market Intelligence, Pattern Recognition, Volatility Regime | PREDICTION, KNOWLEDGE | FROZEN | ST_LMS_CORE: VIEW | IMPLEMENTED | COMPLETE |
| Research Tool | Query knowledge artifacts, replay sessions | KNOWLEDGE, REPLAY | FROZEN | QWEN_DOC D0 (Consumer domain) | NOT_IMPLEMENTED | COMPLETE |
| Paper Trading | Fund evaluation, veto gate, intent builder | CONSUMER | FROZEN | ST_LMS_CORE: CONSUMER | IMPLEMENTED | COMPLETE |
| Live Adapter | Live trading adapter (disabled default) | CONSUMER | FROZEN | ST_LMS_CORE: CONSUMER.liveAdapter | IMPLEMENTED | COMPLETE |
| Fund Manager | Account/Equity/Margin/Available management | CONSUMER | FROZEN | ST_LMS_CORE: CONSUMER.fundEval | PARTIAL | COMPLETE |
| Veto Gate | Risk checks before trade intent | CONSUMER | FROZEN | ST_LMS_CORE: CONSUMER.vetoGate | IMPLEMENTED | COMPLETE |
| Intent Builder | Build trade intent from understanding | CONSUMER | FROZEN | ST_LMS_CORE: CONSUMER.intentBuilder | IMPLEMENTED | COMPLETE |
| CSV Exporter | Export trade markers as CSV | CONSUMER | FROZEN | ST_LMS_CORE: CONSUMER.exportCSV | IMPLEMENTED | COMPLETE |
| SimPlugin | Connect consumer to simulation engine | CONSUMER | FROZEN | QWEN_DOC D0 (Consumer domain) | NOT_IMPLEMENTED | COMPLETE |

**Total: 10 components** | IMPLEMENTED: 6 | PARTIAL: 2 | NOT_IMPLEMENTED: 2

---

## 17. AUDIT

| Component | Responsibilities | Dependencies | Status | Source File | Implementation Status | Specification Status |
|-----------|-----------------|--------------|--------|-------------|----------------------|---------------------|
| Pipeline Audit | Verify pipeline stages, card sharing, unidirectional flow | All pipeline | FROZEN | ST_LMS_CORE: AUDIT | IMPLEMENTED | COMPLETE |
| Snapshot Audit | Verify 10 snapshots, W/OD, NULL+status | All snapshots | FROZEN | ST_LMS_CORE: AUDIT | IMPLEMENTED | COMPLETE |
| Clone Audit | Verify 3 clones, 3 obs/candle, sub-ledgers | CLONE | FROZEN | ST_LMS_CORE: AUDIT | IMPLEMENTED | COMPLETE |
| Trade Audit | Verify P&L, after-fee, adverse-first | TRADE | FROZEN | ST_LMS_CORE: AUDIT | IMPLEMENTED | COMPLETE |
| Knowledge Audit | Verify unidirectional, no-ML, sample-gated | KNOWLEDGE | FROZEN | ST_LMS_CORE: AUDIT | IMPLEMENTED | COMPLETE |
| Governance Audit | Verify decision timeline, rollback, deprecated | GOVERNANCE | FROZEN | ST_LMS_CORE: AUDIT | IMPLEMENTED | COMPLETE |
| Self-Test Suite | 16 automated audit tests | All domains | FROZEN | ST_LMS_CORE: AUDIT.run | IMPLEMENTED | COMPLETE |
| Fingerprint Generator | Deterministic system fingerprint | All domains | FROZEN | ST_LMS_CORE: AUDIT.fingerprint | IMPLEMENTED | COMPLETE |
| Domain Auditor | Per-domain audit with pass/fail | All domains | FROZEN | ST_LMS_CORE: AUDIT.domains | IMPLEMENTED | COMPLETE |

**Total: 9 components** | IMPLEMENTED: 9 | PARTIAL: 0 | NOT_IMPLEMENTED: 0

---

## 18. BENCHMARK

| Component | Responsibilities | Dependencies | Status | Source File | Implementation Status | Specification Status |
|-----------|-----------------|--------------|--------|-------------|----------------------|---------------------|
| WASIT 5-Gate | Walk-forward validation with 5 gates | SIMULATION | FROZEN | ST_LMS_CORE: BENCHMARK.wasit | IMPLEMENTED | COMPLETE |
| WASIT Parallel | Worker-based parallel walk-forward | BENCHMARK | FROZEN | ST_LMS_CORE: BENCHMARK.wasitParallel | IMPLEMENTED | COMPLETE |
| Walk-Forward Engine | Full walk-forward with base vs candidate | BENCHMARK | FROZEN | ST_LMS_CORE: BENCHMARK.walkForward | IMPLEMENTED | COMPLETE |
| Fold Metrics | Per-fold statistics aggregation | BENCHMARK | FROZEN | ST_LMS_CORE: BENCHMARK.foldMetrics | IMPLEMENTED | COMPLETE |
| Gate Evaluator | G1–G5 gate logic | BENCHMARK | FROZEN | ST_LMS_CORE: BENCHMARK.gates | IMPLEMENTED | COMPLETE |

**Total: 5 components** | IMPLEMENTED: 5 | PARTIAL: 0 | NOT_IMPLEMENTED: 0

---

## 19. VISUALIZATION

| Component | Responsibilities | Dependencies | Status | Source File | Implementation Status | Specification Status |
|-----------|-----------------|--------------|--------|-------------|----------------------|---------------------|
| Geometry Viewer | Candle chart + supertrend + cage + markers | TRUTH, STRUCTURE | FROZEN | ST_LMS_CORE: VIEW.drawGeom | IMPLEMENTED | COMPLETE |
| Clone Viewer | 3 clone cards with observations + positions | CLONE | FROZEN | ST_LMS_CORE: VIEW.renderClone | IMPLEMENTED | COMPLETE |
| Trade Viewer | Trade history table + equity curve | TRADE, STATISTICS | FROZEN | ST_LMS_CORE: VIEW (renderTrade, drawEq) | IMPLEMENTED | COMPLETE |
| Replay Viewer | Scrubber + step + auto-play for replay | REPLAY | FROZEN | ST_LMS_CORE: VIEW (renderReplay, step, play) | IMPLEMENTED | COMPLETE |
| Knowledge Viewer | Academy table, Oracle match, HiveMind, CERMIN, Librarian | KNOWLEDGE | FROZEN | ST_LMS_CORE: VIEW.renderKnow | IMPLEMENTED | COMPLETE |
| Panel Renderer | Indicator gauges, wave, cage, versioning, direction, exit | All domains | FROZEN | ST_LMS_CORE: VIEW.renderPanels | IMPLEMENTED | COMPLETE |
| Governance UI | Proposal list + approve/reject buttons + rollback | GOVERNANCE | FROZEN | ST_LMS_CORE: VIEW.renderGov | IMPLEMENTED | COMPLETE |
| Simulation UI | Simulation type selector + results display | SIMULATION | FROZEN | ST_LMS_CORE: VIEW.renderSim | IMPLEMENTED | COMPLETE |
| Prediction Display | Prediction summary with calibration | PREDICTION | FROZEN | ST_LMS_CORE: VIEW.renderPred | IMPLEMENTED | COMPLETE |
| Consumer Display | Trade intent preview + live-adapter status | CONSUMER | FROZEN | ST_LMS_CORE: VIEW.renderConsumer | IMPLEMENTED | COMPLETE |
| Audit Display | Self-test results + domain audit + fingerprint | AUDIT | FROZEN | ST_LMS_CORE: VIEW.renderAudit | IMPLEMENTED | COMPLETE |
| Final Validation Display | 12-domain final validation results | FINAL_VALIDATION | FROZEN | ST_LMS_CORE: VIEW.renderFinalValidation | IMPLEMENTED | COMPLETE |

**Total: 12 components** | IMPLEMENTED: 12 | PARTIAL: 0 | NOT_IMPLEMENTED: 0

---

## 20. FINAL VALIDATION

| Component | Responsibilities | Dependencies | Status | Source File | Implementation Status | Specification Status |
|-----------|-----------------|--------------|--------|-------------|----------------------|---------------------|
| Runtime Check | Verify state, frames, snapshots | All domains | FROZEN | ST_LMS_CORE: FINAL_VALIDATION.runAll | IMPLEMENTED | COMPLETE |
| Pipeline Check | Verify snapshots per frame | SIMULATION | FROZEN | ST_LMS_CORE: FINAL_VALIDATION.runAll | IMPLEMENTED | COMPLETE |
| Namespace Check | Verify all 26 namespaces present | All domains | FROZEN | ST_LMS_CORE: FINAL_VALIDATION.checkNamespaces | IMPLEMENTED | COMPLETE |
| Feature Check | Verify 9 snapshot partitions per candle | All domains | FROZEN | ST_LMS_CORE: FINAL_VALIDATION.checkFeatures | IMPLEMENTED | COMPLETE |
| Truth Layer Check | Verify st/stDir/color/atr/ema/rsi/wpr/macd/distAtr | TRUTH | FROZEN | ST_LMS_CORE: FINAL_VALIDATION.checkTruth | IMPLEMENTED | COMPLETE |
| Clone Check | Verify LONG/SHORT/GRID present | CLONE | FROZEN | ST_LMS_CORE: FINAL_VALIDATION.checkClones | IMPLEMENTED | COMPLETE |
| Trading Check | Verify entry→position→profit→exit→marker | TRADE | FROZEN | ST_LMS_CORE: FINAL_VALIDATION.checkTrading | IMPLEMENTED | COMPLETE |
| Knowledge Check | Verify academy/oracle/hivemind/cermin/librarian/darwin | KNOWLEDGE | FROZEN | ST_LMS_CORE: FINAL_VALIDATION.checkKnowledge | IMPLEMENTED | COMPLETE |
| Replay Check | Verify 6 replay types | REPLAY | FROZEN | ST_LMS_CORE: FINAL_VALIDATION.runAll | IMPLEMENTED | COMPLETE |
| Governance Check | Verify 6 validations + WASIT + rollback | GOVERNANCE | FROZEN | ST_LMS_CORE: FINAL_VALIDATION.runAll | IMPLEMENTED | COMPLETE |
| Constitution Check | Verify all audit tests pass | All domains | FROZEN | ST_LMS_CORE: FINAL_VALIDATION.checkConstitution | IMPLEMENTED | COMPLETE |
| Console Error Check | Verify no swallowed errors | All domains | FROZEN | ST_LMS_CORE: FINAL_VALIDATION.runAll | IMPLEMENTED | COMPLETE |

**Total: 12 components** | IMPLEMENTED: 12 | PARTIAL: 0 | NOT_IMPLEMENTED: 0

---

## INVENTORY SUMMARY

| Domain | Total Components | IMPLEMENTED | PARTIAL | NOT_IMPLEMENTED |
|--------|-----------------|-------------|---------|-----------------|
| BOOT | 5 | 2 | 1 | 2 |
| WORKSPACE | 5 | 1 | 1 | 3 |
| MARKET | 7 | 4 | 1 | 2 |
| TRUTH | 18 | 18 | 0 | 0 |
| STRUCTURE | 10 | 9 | 0 | 1 |
| EVIDENCE | 8 | 8 | 0 | 0 |
| CLONE | 8 | 8 | 0 | 0 |
| TRADE | 5 | 5 | 0 | 0 |
| POSITION | 8 | 2 | 0 | 6 |
| STATISTICS | 4 | 3 | 0 | 1 |
| KNOWLEDGE | 7 | 7 | 0 | 0 |
| PREDICTION | 4 | 4 | 0 | 0 |
| REPLAY | 6 | 6 | 0 | 0 |
| SIMULATION | 6 | 4 | 1 | 1 |
| GOVERNANCE | 9 | 9 | 0 | 0 |
| CONSUMER | 10 | 6 | 2 | 2 |
| AUDIT | 9 | 9 | 0 | 0 |
| BENCHMARK | 5 | 5 | 0 | 0 |
| VISUALIZATION | 12 | 12 | 0 | 0 |
| FINAL_VALIDATION | 12 | 12 | 0 | 0 |
| **TOTAL** | **158** | **134 (85%)** | **6 (4%)** | **18 (11%)** |

---

## NOTES

1. All components listed above are FROZEN per MASTER_SPECIFICATION §3 (Constitution Freeze Matrix)
2. Implementation status reflects ST_LMS_CORE.js as-is at freeze time (post 6 audit patches)
3. PARTIAL components exist in code but lack full specification implementation
4. NOT_IMPLEMENTED components are specified in the documentation but have no code in ST_LMS_CORE.js
5. POSITION domain has the largest implementation gap (6/8 not implemented)
6. TRUTH and EVIDENCE domains are the most complete (100% implemented)
