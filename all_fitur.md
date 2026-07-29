# ST-LMS v3 — ALL FEATURES DETAILED REPORT

**Date:** 2026-07-29
**Version:** v3 FULL REBUILD
**Status:** 102/102 tests PASS | 15/15 benchmarks PASS | 0 external dependencies

---

## 1. MARKET INDICATORS (15)

Dihitung di `stlms/truth/point.py` — PointBuilder. Satu Supertrend Point = satu set 15 indikator per candle.

| # | Indikator | Field | Formula | Period | Range |
|---|-----------|-------|---------|--------|-------|
| 1 | **Supertrend** | `st` | hl2 +/- ATR × 3, band continuation | — | Harga |
| 2 | **ST Direction** | `st_dir` | 1 (UP) / -1 (DOWN), flip detection | — | ±1 |
| 3 | **ST Color** | `st_color` | close > st → HIJAU, close < st → MERAH | — | HIJAU/MERAH |
| 4 | **ATR** | `atr` | True Range smoothed: atr + (TR - atr) / 10 | 10 | >0 |
| 5 | **EMA** | `ema` | ema + (close - ema) × 2/(14+1) | 14 | Harga |
| 6 | **EMA 12** | `ema12` | e12 + (close - e12) × 2/13 (untuk MACD) | 12 | Harga |
| 7 | **EMA 26** | `ema26` | e26 + (close - e26) × 2/27 (untuk MACD) | 26 | Harga |
| 8 | **MACD** | `macd` | ema12 - ema26 | 12/26 | — |
| 9 | **MACD Signal** | `macd_signal` | sig + (macd - sig) × 2/10 | 9 | — |
| 10 | **MACD Histogram** | `macd_hist` | macd - signal | — | — |
| 11 | **RSI** | `rsi` | 100 - 100/(1 + avg_gain/avg_loss) | 10 | 0-100 |
| 12 | **Williams %R** | `wpr` | -100 × (hh - close) / (hh - ll) | 14 | -100 to 0 |
| 13 | **W%R Velocity** | `vel` | wpr - previous_wpr | — | — |
| 14 | **W%R Acceleration** | `acc` | vel - previous_vel | — | — |
| 15 | **Volume Delta** | `vol_delta` | 2 × taker_buy_ratio - 1 | — | -1 to +1 |

**Tambahan (runtime):**
- `dist` = |close - st| — absolute distance to Supertrend
- `dist_atr` = dist / atr — normalized distance
- `flip` = TREND_FLIP_UP / TREND_FLIP_DOWN — trend reversal detection
- `ema_slope` = ema - previous_close — EMA direction
- `oi_value` — inherited Open Interest value
- `oi_delta` — OI change from previous slot

---

## 2. DISTANCE METRICS (8)

Dihitung di TRUTH (W fields) + STRUCTURE (OD fields) + EVIDENCE (runtime).

| # | Metric | Source | Field | Deskripsi |
|---|--------|--------|-------|-----------|
| 1 | **Distance-to-ST** | TRUTH | `dist` | |close - st|, absolute distance |
| 2 | **Distance-to-ST/ATR** | TRUTH | `dist_atr` | dist / atr, normalized |
| 3 | **Distance-Ceiling** | STRUCTURE | `dist_ceiling` | cage.upper - close, NULL on downtrend |
| 4 | **Distance-Floor** | STRUCTURE | `dist_floor` | close - cage.lower, NULL on uptrend |
| 5 | **ST-Dist-Vol (sdv)** | EVIDENCE | `sdv` | Rolling stddev of distAtr, window 96 |
| 6 | **ST-Dist-Vol (p90)** | EVIDENCE | `p90` | 90th percentile of distAtr |
| 7 | **Distance Bucket** | DISTANCE | — | OPTIMAL(≤0.5), NEAR(≤1), EXTENDED(≤2), FAR(>2), WARMUP |
| 8 | **Distance Fingerprint** | BAG | — | [d_entry, d_1, d_2, d_3, d_exit] × 12 dimensi |

---

## 3. WAVE STRUCTURES (13)

Dihitung di `stlms/structure/wave.py` — WaveBuilder. Klasifikasi dari 6 Line.

| # | Structure | Kondisi | MTF Sector | MTF Score |
|---|-----------|---------|------------|-----------|
| 1 | **STRONG_ACCUMULATION** | g >= 5 (5+ HIJAU) | BULLISH_TREND | 8500 |
| 2 | **STRONG_DISTRIBUTION** | r >= 5 (5+ MERAH) | BEARISH_TREND | 8500 |
| 3 | **CONTINUATION_UP** | g >= 3, r = 0 | BULLISH_TREND | 7000 |
| 4 | **CONTINUATION_DOWN** | r >= 3, g = 0 | BEARISH_TREND | 7000 |
| 5 | **CONFIRMED_RANGE** | alt >= 4 (4+ alternations) | RANGE | 7500 |
| 6 | **RANGE_EXPANDING** | Range melebar | RANGE | 6500 |
| 7 | **RANGE_COMPRESSING** | Range menyempit | COMPRESSION | 7000 |
| 8 | **REVERSAL_UP** | 3 MERAH pertama + HIJAU terakhir | REVERSAL_UP | 6500 |
| 9 | **REVERSAL_DOWN** | 3 HIJAU pertama + MERAH terakhir | REVERSAL_DOWN | 6500 |
| 10 | **EXHAUSTION_UP** | g >= 4, last = MERAH | EXHAUSTION | 5500 |
| 11 | **EXHAUSTION_DOWN** | r >= 4, last = HIJAU | EXHAUSTION | 5500 |
| 12 | **SIDEWAY** | g >= 2, r >= 2 | RANGE | 7000 |
| 13 | **CHAOS** | Default (fallback) | CHAOS | 3000 |

---

## 4. CLONE TYPES (3)

Dihitung di `stlms/clone/engine.py` — CloneEngine. PER-CLONE ×3.

| # | Clone | Bias | Entry Conjunction (5-7 kondisi) | Exit Priority (8 level) |
|---|-------|------|--------------------------------|------------------------|
| 1 | **LONG** | EXPANSION_UP | stDir=+1, ema>0, vd>0, corridor.inZone, fee_safe, global_ok, open==null | WRONG_EARLY→WRONG_GEOM→HYPOTHESIS→SL→HOLD→TP→EXIT_BUS→TIME |
| 2 | **SHORT** | EXHAUSTION_DOWN | stDir=-1, ema<0, vd<0, corridor.inZone, fee_safe, global_ok, open==null | Mirror LONG (cermin) |
| 3 | **GRID** | COMPRESSION_RANGE | cage_valid, width≥3×req, breakout=NONE, pp in zone, fills<max | RANGE_BREAK→WRONG→GRID_TP→STOP_ALL |

---

## 5. TRADING SCHEMAS (41 — 5 Kategori)

Didefinisikan di `stlms/schema/engine.py` dan `03_TRADING_CONSTITUTION.md`.

### Market Schema (10)
| # | Schema | Kondisi | Clone Aktif |
|---|--------|---------|-------------|
| 1 | TREND | stDir ≠ 0, cage = NONE | LONG/SHORT |
| 2 | SIDEWAY | cage.status ≠ NONE | GRID |
| 3 | RANGE | wave = CONFIRMED_RANGE/SIDEWAY | GRID |
| 4 | CHAOS | wave = CHAOS | None |
| 5 | COMPRESSION | cage = VALID_COMPRESSION | GRID |
| 6 | EXPANSION | cage = LOOSE_SIDEWAY | GRID |
| 7 | BREAKOUT | cage.breakout ≠ NONE | LONG/SHORT |
| 8 | REVERSAL | wave = REVERSAL_UP/DOWN | LONG/SHORT |
| 9 | EXHAUSTION | wave = EXHAUSTION_UP/DOWN | None |
| 10 | WARMUP | point_status = WARMUP | None |

### Trading Schema (7)
| # | Schema | State | Observasi |
|---|--------|-------|-----------|
| 1 | LONG | Directional UP entry + position | Mandatory |
| 2 | SHORT | Directional DOWN entry + position | Mandatory |
| 3 | GRID | Range-bound fills | Mandatory |
| 4 | NO TRADE | Observasi tanpa entry | Mandatory |
| 5 | WAIT | Menunggu kondisi market | Mandatory |
| 6 | HOLD | Menahan posisi terbuka | Mandatory |
| 7 | SKIP | Candle invalid/data insufficient | Mandatory |

### Entry Schema (11)
| # | Schema | Confidence | Risk |
|---|--------|-----------|------|
| 1 | LONG_CONTINUATION | HIGH | LOW |
| 2 | LONG_PULLBACK | MEDIUM | MEDIUM |
| 3 | LONG_BREAKOUT | MEDIUM | HIGH |
| 4 | LONG_REVERSAL | LOW | HIGH |
| 5 | SHORT_CONTINUATION | HIGH | LOW |
| 6 | SHORT_PULLBACK | MEDIUM | MEDIUM |
| 7 | SHORT_BREAKOUT | MEDIUM | HIGH |
| 8 | SHORT_REVERSAL | LOW | HIGH |
| 9 | GRID_COMPRESSION | HIGH | LOW |
| 10 | GRID_RANGE | MEDIUM | MEDIUM |
| 11 | GRID_EXPANSION | LOW | HIGH |

### Position Schema (7)
| # | Schema | Trigger | Action |
|---|--------|---------|--------|
| 1 | ADD POSITION | GRID: pp in zone, fills < max | Tambah fill |
| 2 | PARTIAL TP | profit ≥ threshold | Close sebagian, SL ke entry |
| 3 | TRAILING TP | profit ≥ TRAIL_ACTIVATE_R × ATR | SL ikuti price |
| 4 | BREAKEVEN | profit ≥ threshold | SL = entry_price |
| 5 | TIME EXIT | hold ≥ TIME_EXIT, profit < req | Close position |
| 6 | WRONG ENTRY | vel/price adverse, hold ≤ 2 | Close immediately |
| 7 | LOCK PROFIT | profit ≥ threshold | Disable EXIT_BUS |

### Exit Schema (6)
| # | Schema | Priority | Trigger |
|---|--------|----------|---------|
| 1 | SL | 4 | Price crosses SL |
| 2 | TP | 6 | Price crosses TP (HOLD-veto at 5) |
| 3 | EXIT BUS | 7 | RSI>70/WPR>-20 (LONG), RSI<30/WPR<-80 (SHORT) |
| 4 | MANUAL EXIT | 0 | Human override |
| 5 | TIME EXIT | 8 | hold ≥ TIME_EXIT, profit < req |
| 6 | EARLY EXIT | 1-2 | Wrong entry in first 2 candles |

---

## 6. KNOWLEDGE ENTITIES (7)

Dihitung di `stlms/knowledge/engine.py`.

| # | Entity | Fungsi | Lifecycle | Sample Gate |
|---|--------|-------|-----------|-------------|
| 1 | **Academy** | Win rate empiris per 4-dim bucket (clone, structure, distance, reason) | Per cycle | ≥30 = CUKUP |
| 2 | **Oracle** | Euclidean similarity matching, vector beku 9 dimensi | Per cycle | Match > 7500 |
| 3 | **HiveMind** | Market understanding: intelligence_score 0-10000, dominant_bias | Per cycle | — |
| 4 | **CERMIN** | Calibration error: predicted vs actual win_rate | Per cycle | — |
| 5 | **Librarian** | Lifecycle: NEW→OBS→TRUSTED→MATURE/DEAD/DEPRECATED | Per evaluation | 6 statuses |
| 6 | **Darwin** | Parameter proposals: TIGHTEN_ENTRY, TIGHTEN_WRONG | Per cycle | NO auto-execute |
| 7 | **River** | Chronicle: append-only event log | Continuous | — |

---

## 7. SIMULATORS (5)

Dihitung di `stlms/simulation/engine.py`.

| # | Simulator | Input | Output | Consumer |
|---|-----------|-------|--------|----------|
| 1 | **Architecture** | Pipeline config | 23 stages, card sharing, determinism | AUDIT |
| 2 | **Market Possibility** | Prediction + actual | Accuracy per possibility type | PREDICTION |
| 3 | **Market Push** | Phase transitions | Schema switch correctness | TRADING SCHEMA |
| 4 | **Knowledge** | Knowledge package + history | Pattern match, biography consistency | KNOWLEDGE |
| 5 | **Balance** | Full pipeline + initial balance | P&L, win_rate, drawdown | CONSUMER |

---

## 8. EVIDENCE BUSES (3)

Dihitung di `stlms/evidence/bus.py`.

| # | Bus | Isi | Penggunaan | Dilarang |
|---|-----|-----|-----------|----------|
| 1 | **Direction Bus** | EMA(0-10000), OI(score,status,source), VolDelta(0-10000), MTF(long,short) | Entry-legal witnesses | W%R, MACD, RSI |
| 2 | **Exit Bus** | RSI, W%R, MACD_hist, HOLD-veto, vel, acc, vel_signal, acc_signal, early_invalidation | Close-only exit signals | Entry decisions |
| 3 | **Correction Bus** | price_position, market_phase, dist_ceiling, dist_floor, wave_structure, cage_status, cage_range_atr, breakout | Market context | — |

---

## 9. GOVERNANCE VALIDATIONS (6)

Dihitung di `stlms/governance/engine.py`.

| # | Validation | Memeriksa | Failure |
|---|-----------|-----------|---------|
| 1 | **Constitution** | 18 LAW-MASTER, namespaces | BUILD STOP |
| 2 | **Proposal** | Bounded-check, label-peran | AUTO-REJECT |
| 3 | **Authority Matrix** | Indicator usage in valid columns | BUILD STOP |
| 4 | **Build** | 15 stop-rules, determinism | BUILD STOP |
| 5 | **Runtime** | Checksum, lineage, writer | Card rejected |
| 6 | **Governance Audit** | Decision timeline, rollback | ANOMALY |

---

## 10. WASIT GATES (5)

Dihitung di `stlms/bench/engine.py`.

| # | Gate | Kondisi | Majority |
|---|------|---------|----------|
| 1 | **G1** | candidate exits ≥ 30 | — |
| 2 | **G2** | candidate expectancy > base expectancy | Folds majority |
| 3 | **G3** | candidate worst-loss not worse > 10% vs base | Folds majority |
| 4 | **G4** | candidate win_rate not dropped > 2% vs base | Folds majority |
| 5 | **G5** | candidate fee_drag not increased > 0.001 vs base | Folds majority |

---

## 11. PIPELINE STAGES (23)

| Stage | Type | Name | Owner |
|-------|------|------|-------|
| 0 | ONCE | BOOT | BOOT |
| 1 | SHARED | MARKET OBSERVATION | MARKET |
| 2 | SHARED | TRUTH LAYER | TRUTH |
| 3 | SHARED | STRUCTURE LAYER | STRUCTURE |
| 4 | SHARED | EVIDENCE LAYER | EVIDENCE |
| 5 | PER-CLONE ×3 | CLONE OBSERVATION | CLONE |
| 6 | PER-CLONE ×3 | ENTRY VALIDATION | TRADE |
| 7 | PER-CLONE ×3 | POSITION MGMT | POSITION |
| 8 | PER-CLONE ×3 | PROFIT MGMT | POSITION |
| 9 | PER-CLONE ×3 | EXIT VALIDATION | TRADE |
| 10 | PER-CLONE ×3 | CLOSE POSITION | TRADE |
| 11 | PER-CLONE ×3 | TRADE MARKER | TRADE |
| 12 | SHARED-AGAIN | STATISTICS | STATISTICS |
| 13 | SHARED-AGAIN | BAG | BAG |
| 14 | SHARED-AGAIN | RIVER | KNOWLEDGE |
| 15 | ON-DEMAND | BENCHMARK | BENCHMARK |
| 16 | SHARED-AGAIN | ACADEMY | KNOWLEDGE |
| 17 | SHARED-AGAIN | ORACLE | KNOWLEDGE |
| 18 | SHARED-AGAIN | HIVEMIND | KNOWLEDGE |
| 19 | SHARED-AGAIN | CERMIN | KNOWLEDGE |
| 20 | SHARED-AGAIN | DARWIN | KNOWLEDGE |
| 21 | SHARED-AGAIN | PREDICTION | PREDICTION |
| 22 | SHARED-AGAIN | GOVERNANCE | GOVERNANCE |
| OPT | OPTIONAL | CONSUMER | CONSUMER |

---

## 12. LOGICAL LAYERS (26)

| # | Layer | Type | Mandatory |
|---|-------|------|-----------|
| 1 | BOOT | ONCE | YES |
| 2 | WORKSPACE | FOUNDATION | YES |
| 3 | SQLITE FOUNDATION | FOUNDATION | YES |
| 4 | MARKET | SHARED | YES |
| 5 | TRUTH | SHARED | YES |
| 6 | DISTANCE | LOGICAL SUB | YES |
| 7 | STRUCTURE | SHARED | YES |
| 8 | EVIDENCE | SHARED | YES |
| 9 | CLONE | PER-CLONE ×3 | YES |
| 10 | TRADE | PER-CLONE ×3 | YES |
| 11 | POSITION | PER-CLONE ×3 | YES |
| 12 | STATISTICS | SHARED-AGAIN | YES |
| 13 | BAG | SHARED-AGAIN | YES |
| 14 | KNOWLEDGE | SHARED-AGAIN | YES |
| 15 | PREDICTION | SHARED-AGAIN | YES |
| 16 | TRADING SCHEMA | SHARED-AGAIN | YES |
| 17 | GOVERNANCE | SHARED-AGAIN | YES |
| 18 | BENCHMARK | ON-DEMAND | YES |
| 19 | CONSUMER | OPTIONAL | NO |
| 20 | SNAPSHOT | CROSS-CUTTING | YES |
| 21 | SIMULATION | CROSS-CUTTING | YES |
| 22 | REPLAY | CROSS-CUTTING | YES |
| 23 | DASHBOARD | CROSS-CUTTING | YES |
| 24 | AUDIT | CROSS-CUTTING | YES |
| 25 | INTEGRATION | CROSS-CUTTING | YES |
| 26 | FINAL VALIDATION | CROSS-CUTTING | YES |

---

## 13. SQLITE TABLES (40)

| # | Table | Layer | Purpose |
|---|-------|-------|---------|
| 1 | app_sessions | Core | Session container |
| 2 | symbols | Core | Trading symbols |
| 3 | timeframes | Core | Timeframe registry (9 seed) |
| 4 | pipeline_runs | Core | Pipeline execution runs |
| 5 | market_candles | Market | OHLCV data |
| 6 | market_metadata | Market | Key-value metadata |
| 7 | open_interest_series | Market | OI time series |
| 8 | market_gaps | Market | Detected gaps |
| 9 | truth_snapshots | Truth | Per-candle truth physics |
| 10 | truth_cache | Truth | Key-value cache |
| 11 | structure_snapshots | Structure | Market geometry |
| 12 | wave_history | Structure | Wave line details |
| 13 | cage_history | Structure | Cage version history |
| 14 | evidence_snapshots | Evidence | Evidence buses |
| 15 | clones | Clone | Clone entities |
| 16 | clone_observations | Clone | Per-candle observations |
| 17 | trade_markers | Trade | Trade markers |
| 18 | positions | Position | Position lifecycle |
| 19 | position_timeline | Position | Event timeline |
| 20 | trade_statistics | Statistics | Aggregated stats |
| 21 | market_statistics | Statistics | Market-level stats |
| 22 | bag_artifacts | BAG | Grouped artifacts |
| 23 | bag_patterns | BAG | Detected patterns |
| 24 | bag_compression | BAG | Compression metrics |
| 25 | knowledge_artifacts | Knowledge | Knowledge entities |
| 26 | predictions | Prediction | Empirical predictions |
| 27 | prediction_results | Prediction | Actual outcomes |
| 28 | governance_proposals | Governance | Darwin proposals |
| 29 | governance_logs | Governance | Event timeline |
| 30 | rollback_logs | Governance | Rollback events |
| 31 | replay_sessions | Replay | Replay containers |
| 32 | replay_frames | Replay | Individual frames |
| 33 | benchmark_runs | Benchmark | Benchmark containers |
| 34 | benchmark_cases | Benchmark | Test cases |
| 35 | audit_logs | Audit | Audit events |
| 36 | audit_issues | Audit | Key-value issues |
| 37 | app_settings | Settings | Key-value settings (2 seed) |
| 38 | domain_dictionary | Settings | Domain registry (15 seed) |
| 39 | purge_jobs | Utility | Deletion tracking |
| 40 | row_lifecycle | Utility | Generic lifecycle |

---

## 14. BOUNDED PARAMETERS (24)

Dikelola di `stlms/foundation/config_manager.py`.

| # | Parameter | Default | Min | Max | Purpose |
|---|-----------|---------|-----|-----|---------|
| 1 | ENTRY_OFFSET_BASE_K | 1.0 | 0.3 | 3.0 | Corridor base multiplier |
| 2 | ENTRY_OFFSET_MIN_ATR | 0.15 | 0.05 | 0.5 | Corridor minimum ATR |
| 3 | ENTRY_OFFSET_MAX_CAP_PCT | 0.30 | 0.10 | 1.0 | Corridor max cap % |
| 4 | WPR_VELOCITY_DEADZONE | 5 | 1 | 20 | W%R velocity deadzone |
| 5 | WPR_ACCEL_DEADZONE | 8 | 2 | 40 | W%R acceleration deadzone |
| 6 | GRID_MIN_NET_PCT_OF_FILL | 0.50 | 0.20 | 1.5 | GRID minimum net % |
| 7 | CAGE_TIGHT_ATR | 2.0 | 1.0 | 4.0 | Tight cage threshold |
| 8 | CAGE_LOOSE_ATR | 4.0 | 2.0 | 8.0 | Loose cage threshold |
| 9 | CAGE_WALL_MIN_DISTANCE_ATR | 0.25 | 0.10 | 0.50 | Wall minimum distance |
| 10 | WRONG_ENTRY_PCT | 2.0 | 0.5 | 6.0 | Wrong entry threshold % |
| 11 | FEE_SAFETY_BUFFER_PCT | 0.10 | 0.0 | 0.5 | Fee safety buffer |
| 12 | FEE_DISCOUNT_PCT | 0.0 | 0.0 | 0.25 | Fee discount |
| 13 | GRID_BUY_ZONE_MAX | 0.30 | 0.10 | 0.45 | GRID buy zone max pp |
| 14 | GRID_SELL_ZONE_MIN | 0.70 | 0.55 | 0.90 | GRID sell zone min pp |
| 15 | GRID_MAX_FILLS_PER_SIDE | 2 | 1 | 4 | GRID max fills per side |
| 16 | TP_ATR_MULT | 2.0 | 1.0 | 5.0 | Take profit ATR multiplier |
| 17 | TRAIL_ATR_MULT | 1.5 | 0.5 | 4.0 | Trailing stop ATR multiplier |
| 18 | TRAIL_ACTIVATE_R | 1.0 | 0.5 | 3.0 | Trailing activation R |
| 19 | PARTIAL_TP_PCT | 0.5 | 0.0 | 0.8 | Partial TP percentage |
| 20 | TIME_EXIT_CANDLES | 40 | 5 | 200 | Time exit threshold |
| 21 | SAMPLE_GATE | 30 | 10 | 200 | Statistics sample gate |
| 22 | ST_DIST_VOL_WINDOW | 96 | 24 | 240 | Distance volatility window |

---

## 15. PYTHON ENUMS (26)

Didefinisikan di `stlms/core/types.py`.

| # | Enum | Values | Count |
|---|------|--------|-------|
| 1 | DataStatus | ok, warmup, provisional, insufficient, gap, invalid | 6 |
| 2 | PointStatus | WARMUP, VALID | 2 |
| 3 | SampleStatus | CUKUP, BELUM_CUKUP | 2 |
| 4 | TradeKind | ENTRY, EXIT, PARTIAL, BREAKEVEN, TRAILING, HOLD, PASS, NO_TRADE | 8 |
| 5 | TradeSide | LONG, SHORT, GRID | 3 |
| 6 | TradeResult | WIN, LOSS, BREAKEVEN, OPEN, PASS, NA | 6 |
| 7 | PositionStatus | OPEN, HOLD, CLOSED, BREAKEVEN, TRAILING, PARTIAL | 6 |
| 8 | CloneKind | LONG, SHORT, GRID | 3 |
| 9 | BagKind | behavior, market, entry, exit, risk, knowledge | 6 |
| 10 | KnowledgeEntity | ACADEMY, RIVER, ORACLE, HIVEMIND, DARWIN, LIBRARIAN, CERMIN | 7 |
| 11 | SessionKind | build, simulation, replay, benchmark, analysis, manual | 6 |
| 12 | RunKind | collector, simulation, replay, benchmark, audit, build | 6 |
| 13 | Severity | CRITICAL, HIGH, MEDIUM, LOW, INFO | 5 |
| 14 | SupertrendColor | HIJAU, MERAH | 2 |
| 15 | SupertrendDirection | UP=1, DOWN=-1 | 2 |
| 16 | LineRole | SUPPORT, RESISTANCE | 2 |
| 17 | WaveStructure | 13 structures | 13 |
| 18 | CageStatus | NONE, VALID_COMPRESSION, LOOSE_SIDEWAY | 3 |
| 19 | CageBreakout | NONE, IMMINENT_UP, IMMINENT_DOWN, SQUEEZE | 4 |
| 20 | MarketPhase | UPTREND, DOWNTREND, TRANSITION, SIDEWAY_COMPRESSION | 4 |
| 21 | ConsensusLevel | HIGH, MEDIUM, LOW, NONE | 4 |
| 22 | ConflictLevel | NONE, LOW, MEDIUM, HIGH | 4 |
| 23 | LibrarianStatus | NEW, OBSERVATION, TRUSTED, MATURE, DEAD, DEPRECATED | 6 |
| 24 | ReplayKind | candle, snapshot, trade, clone, knowledge, governance | 6 |
| 25 | BenchmarkRunKind | wasit, walk_forward, clone, trade, market | 5 |
| 26 | SupertrendDirection | UP=1, DOWN=-1 | 2 |

---

## 16. BASE CLASSES (4)

Didefinisikan di `stlms/foundation/`.

| # | Class | Purpose | Methods |
|---|-------|---------|---------|
| 1 | **BaseArtifact** | Immutable card production | produce(), validate_input(), make_card(), reset_ids() |
| 2 | **BasePackage** | Structured report building | build(), summary(), merge_reports() |
| 3 | **BaseConsumer** | Downstream API interface | consume(), query(), export() |
| 4 | **BaseValidator** | Quality assurance | validate(), run_all(), is_valid(), summary() |

---

## 17. FOUNDATION MANAGERS (5)

| # | Manager | Purpose | Methods |
|---|---------|---------|---------|
| 1 | **ConfigurationManager** | 24 BOUNDED parameters | get(), set(), valid(), all_params(), reset(), snapshot(), restore() |
| 2 | **TimeManager** | WIB timezone | now_ms(), wib_iso(), wib_ymd(), wib_hhmm(), candle_timestamp(), is_valid_sequence() |
| 3 | **SymbolManager** | Asset registry | get(), exists(), tick_size(), precision(), base_price(), all_symbols() |
| 4 | **ResourceManager** | VPS monitoring | memory_usage_mb(), cpu_usage(), disk_usage(), is_vps_friendly(), status() |
| 5 | **FoundationRegistry** | Component registry | register_layer/component/worker/artifact/schema/validator(), get(), list(), count(), summary() |

---

## 18. SQLITE COMPONENTS (6)

| # | Component | Purpose | Key Methods |
|---|-----------|---------|-------------|
| 1 | **SQLiteConnection** | Connection manager | open(), close(), execute(), commit(), rollback(), cursor() |
| 2 | **SQLiteManager** | Admin operations | init_schema(), integrity_check(), vacuum(), backup(), restore(), analyze(), stats |
| 3 | **SQLiteViewer** | Data browser | query(), select_table(), search_table(), export_json(), export_csv(), get_schema() |
| 4 | **SQLiteValidator** | Schema validation | run_all() — tables, indexes, triggers, integrity, FK, seed data |
| 5 | **QueryHelper** | Parameterized CRUD | insert(), update(), delete(), select_one(), select_all(), exists(), count() |
| 6 | **SQLiteBenchmark** | Performance tests | run_all() — insert, select, integrity, vacuum, analyze |

---

## 19. CLI COMMANDS (7)

| # | Command | Fungsi |
|---|---------|--------|
| 1 | `status` | Foundation status (layers, components, SQLite, memory) |
| 2 | `sqlite` | SQLite status (tables, indexes, size) |
| 3 | `validate` | Foundation validation (schema, integrity, FK, seed) |
| 4 | `resource` | Resource status (memory, CPU, disk) |
| 5 | `benchmark` | Benchmark results (SQLite speed tests) |
| 6 | `config` | Configuration status (24 bounded params) |
| 7 | `mcp` | MCP server management (list, status, on, off, toggle) |

---

## 20. MCP TOOLS (8)

| # | Tool | Fungsi |
|---|------|--------|
| 1 | `stlms_github_status` | Cek status GitHub (mode, repo, token, internet) |
| 2 | `stlms_github_test` | Connection test (5 checks: internet, token, repo, branch, API) |
| 3 | `stlms_github_on` | Enable GitHub (PR mode) |
| 4 | `stlms_github_off` | Disable GitHub |
| 5 | `stlms_github_setup` | Setup wizard (username, repo, branch, token) |
| 6 | `stlms_github_pr` | Create Pull Request (stage→commit→push→PR→STOP) |
| 7 | `stlms_github_token_status` | Token status (masked) |
| 8 | `stlms_github_reset` | Reset all config to OFF |

---

## 21. EXCEPTIONS (11)

| # | Exception | Parent | Purpose |
|---|-----------|--------|---------|
| 1 | STLMSError | Exception | Base exception |
| 2 | ValidationError | STLMSError | Data validation failure |
| 3 | ConstraintError | STLMSError | SQLite constraint violation |
| 4 | WarmupError | STLMSError | Operation during WARMUP |
| 5 | InsufficientDataError | STLMSError | Missing required data |
| 6 | ConfigurationError | STLMSError | Invalid configuration |
| 7 | BoundedRangeError | ConfigurationError | Value outside [min,max] |
| 8 | DeterminismError | STLMSError | Determinism check failure |
| 9 | CardVerificationError | STLMSError | Card checksum mismatch |
| 10 | PipelineError | STLMSError | Pipeline stage violation |
| 11 | WorkerError | STLMSError | Worker communication failure |

---

## 22. ASSETS (4)

| # | Symbol | Base Price | Tick Size | Precision |
|---|--------|-----------|-----------|-----------|
| 1 | BTCUSDT | 61,750 | 0.1 | 1 |
| 2 | SOLUSDT | 71.84 | 0.01 | 2 |
| 3 | AKEUSDT | 0.0031760 | 0.0000001 | 7 |
| 4 | TLMUSDT | 0.004043 | 0.0000001 | 7 |

---

## TOTAL FITUR

| Kategori | Jumlah |
|----------|--------|
| Market Indicators | 15 |
| Distance Metrics | 8 |
| Wave Structures | 13 |
| Clone Types | 3 |
| Trading Schemas | 41 |
| Knowledge Entities | 7 |
| Simulators | 5 |
| Evidence Buses | 3 |
| Governance Validations | 6 |
| WASIT Gates | 5 |
| Pipeline Stages | 23 |
| Logical Layers | 26 |
| SQLite Tables | 40 |
| Bounded Parameters | 24 |
| Python Enums | 26 |
| Base Classes | 4 |
| Foundation Managers | 5 |
| SQLite Components | 6 |
| CLI Commands | 7 |
| MCP Tools | 8 |
| Exceptions | 11 |
| Assets | 4 |
| **DOMAIN TOTAL** | **289** |
| | |
| Classes | 94 |
| Methods | 396 |
| Standalone Functions | 39 |
| Constants | 60+ |
| Unit Tests | 102 |
| Benchmarks | 15 |
| **CODE TOTAL** | **706** |
| | |
| **GRAND TOTAL** | **~995 fitur** |
