# 05_TEST_CONTRACT.md

## ST-LMS Final Freeze Contract V1 — Test Contract

**Date:** 2026-07-28
**Status:** CONSTITUTIONALLY FROZEN — FINAL

---

## RULE: LAYER TIDAK BOLEH DILANJUTKAN APABILA TEST GAGAL.

---

## TEST REQUIREMENTS PER LAYER

### 1. SQLite Foundation

| Test Type | Test Name | Pass Condition | Fail Consequence |
|-----------|-----------|---------------|-----------------|
| Unit | Schema syntax check | SQL parses without error | STOP BUILD |
| Unit | Table creation | All 40 tables created | STOP BUILD |
| Unit | Index creation | All 9 indexes created | STOP BUILD |
| Unit | Trigger creation | All 4 triggers created | STOP BUILD |
| Unit | Seed data | 9 timeframes, 2 settings, 15 domains | STOP BUILD |
| SQLite | integrity_check | No errors returned | STOP BUILD |
| SQLite | foreign_key_check | No orphaned references | STOP BUILD |
| SQLite | Constraint validation | CHECK, UNIQUE, NOT NULL enforced | STOP BUILD |
| SQLite | CASCADE delete | Session delete cascades to 23 tables | STOP BUILD |
| Benchmark | Query performance | Indexed query < 5ms | SOFT (record) |

### 2. BOOT + Workspace

| Test Type | Test Name | Pass Condition | Fail Consequence |
|-----------|-----------|---------------|-----------------|
| Unit | Namespace initialization | All 26 namespaces present | STOP BUILD |
| Unit | IndexedDB open | Database opens successfully | STOP BUILD |
| Unit | Card storage | Card written and retrieved | STOP BUILD |
| Unit | Card verification | SHA-256 checksum matches | STOP BUILD |
| Integration | Workspace reset | Clean state after reset | STOP BUILD |

### 3. Config + Bounded Registry

| Test Type | Test Name | Pass Condition | Fail Consequence |
|-----------|-----------|---------------|-----------------|
| Unit | Bounded get | Returns current value | STOP BUILD |
| Unit | Bounded set valid | Accepts value in range | STOP BUILD |
| Unit | Bounded set invalid | Rejects value out of range | STOP BUILD |
| Unit | Bounded auto-reject | OUT_OF_RANGE returned | STOP BUILD |
| Unit | Config reset | Returns to defaults | STOP BUILD |

### 4. Market Layer

| Test Type | Test Name | Pass Condition | Fail Consequence |
|-----------|-----------|---------------|-----------------|
| Unit | Fixture generation | Generates valid OHLCV | STOP BUILD |
| Unit | Hygiene valid | H>=O,C; L<=O,C; H>=L | STOP BUILD |
| Unit | Hygiene invalid | Invalid candle rejected | STOP BUILD |
| Unit | Gap detection | Gap between candles detected | STOP BUILD |
| Unit | OI proxy | OI derived from volume+takerBuyRatio | STOP BUILD |
| Snapshot | market_snapshot | All W fields present | STOP BUILD |
| Integration | MARKET -> TRUTH | market_snapshot flows correctly | STOP BUILD |

### 5. Truth Layer

| Test Type | Test Name | Pass Condition | Fail Consequence |
|-----------|-----------|---------------|-----------------|
| Unit | Supertrend computation | st, stDir, color correct | STOP BUILD |
| Unit | ATR computation | ATR matches expected | STOP BUILD |
| Unit | EMA computation | EMA matches expected | STOP BUILD |
| Unit | MACD computation | MACD line + signal + histogram | STOP BUILD |
| Unit | RSI computation | RSI in 0-100 range | STOP BUILD |
| Unit | W%R computation | W%R in -100-0 range | STOP BUILD |
| Unit | Velocity/Acceleration | vel = wpr - prev; acc = vel - prev | STOP BUILD |
| Unit | Distance computation | dist = |close - st|, distAtr = dist/atr | STOP BUILD |
| Unit | Flip detection | TREND_FLIP_UP/DOWN detected | STOP BUILD |
| Unit | WARMUP state | NULL values, WARMUP status | STOP BUILD |
| Snapshot | truth_snapshot | All W fields present | STOP BUILD |
| Determinism | 2-run identical | Same seed -> same checksum | STOP BUILD |

### 6. Distance Metrics

| Test Type | Test Name | Pass Condition | Fail Consequence |
|-----------|-----------|---------------|-----------------|
| Unit | dist calculation | |close - st| correct | STOP BUILD |
| Unit | distAtr calculation | dist / atr correct | STOP BUILD |
| Unit | dist_ceiling | ceiling - close, NULL on downtrend | STOP BUILD |
| Unit | dist_floor | close - floor, NULL on uptrend | STOP BUILD |
| Unit | ST_DIST_VOL | Rolling stddev correct | STOP BUILD |
| Unit | Distance bucket | OPTIMAL<=0.5, NEAR<=1, EXTENDED<=2, FAR>2 | STOP BUILD |

### 7. Structure Layer

| Test Type | Test Name | Pass Condition | Fail Consequence |
|-----------|-----------|---------------|-----------------|
| Unit | Line building | Lines with >=4 members created | STOP BUILD |
| Unit | Slope building | Transitions between lines | STOP BUILD |
| Unit | Wave classification | All 13 structures reachable | STOP BUILD |
| Unit | Wave < 6 | PENDING_WAVE, not padded | STOP BUILD |
| Unit | HUKUM CAGE 1 wall | cage.status = NONE | STOP BUILD |
| Unit | HUKUM CAGE 2 walls | cage.status = VALID/LOOSE | STOP BUILD |
| Unit | Cage versioning | v0, v1, v2 walls resolved | STOP BUILD |
| Unit | Escape path | Comfortable wall found | STOP BUILD |
| Unit | Market phase | UPTREND/DOWNTREND/SIDEWAY | STOP BUILD |
| Snapshot | structure_snapshot | All W + OD fields present | STOP BUILD |

### 8. Evidence Layer

| Test Type | Test Name | Pass Condition | Fail Consequence |
|-----------|-----------|---------------|-----------------|
| Unit | Direction Bus | ema, oi, vd, mtf scores | STOP BUILD |
| Unit | Exit Bus | rsi, wpr, macd_hist, hold, vel, acc | STOP BUILD |
| Unit | Correction Bus | pp, phase, distances, wave, cage | STOP BUILD |
| Unit | Bus sterility | W%R not in Direction Bus | STOP BUILD |
| Unit | OI insufficient | INSUFFICIENT_DATA when no OI | STOP BUILD |
| Unit | MTF sector | Wave -> MTF mapping correct | STOP BUILD |
| Snapshot | evidence_snapshot | All W fields present | STOP BUILD |

### 9. Clone Layer

| Test Type | Test Name | Pass Condition | Fail Consequence |
|-----------|-----------|---------------|-----------------|
| Unit | LONG observation | 1 obs per candle | STOP BUILD |
| Unit | SHORT observation | 1 obs per candle | STOP BUILD |
| Unit | GRID observation | 1 obs per candle | STOP BUILD |
| Unit | 3 obs/candle | LONG + SHORT + GRID all produce | STOP BUILD |
| Unit | No-trade reason | no_entry_reason populated | STOP BUILD |
| Unit | Entry conjunction | All conditions checked | STOP BUILD |
| Unit | LONG entry | Correct entry when conditions met | STOP BUILD |
| Unit | SHORT entry | Correct entry when conditions met | STOP BUILD |
| Unit | GRID entry | Correct fills when cage valid | STOP BUILD |
| Integration | Card sharing | Shared snapshots read correctly | STOP BUILD |

### 10. Trade Layer

| Test Type | Test Name | Pass Condition | Fail Consequence |
|-----------|-----------|---------------|-----------------|
| Unit | Entry marker | ENTRY_MARKER with sl, tp | STOP BUILD |
| Unit | Exit marker | EXIT_MARKER with P&L | STOP BUILD |
| Unit | P&L LONG | gross = (exit-entry)/entry*100 | STOP BUILD |
| Unit | P&L SHORT | gross = (entry-exit)/entry*100 | STOP BUILD |
| Unit | WIN condition | net > 0 = WIN | STOP BUILD |
| Unit | LOSS condition | net < 0 = LOSS | STOP BUILD |
| Unit | Fee layered | net = gross - fee - slip | STOP BUILD |
| Unit | Adverse-first | SL beats TP on same candle | STOP BUILD |
| Unit | GRID fills | Multiple fills managed | STOP BUILD |

### 11. Position Layer

| Test Type | Test Name | Pass Condition | Fail Consequence |
|-----------|-----------|---------------|-----------------|
| Unit | Position update | hold_c incremented | STOP BUILD |
| Unit | MAE tracking | mae = min(mae, -adverse) | STOP BUILD |
| Unit | MFE tracking | mfe = max(mfe, favorable) | STOP BUILD |
| Unit | Exit decision | Correct priority order | STOP BUILD |
| Unit | Wrong entry early | vel wrong + hold<=2 | STOP BUILD |
| Unit | Wrong entry geom | adverse>=WRONG_PCT + hold<=2 | STOP BUILD |
| Unit | SL hit | Exit at SL price | STOP BUILD |
| Unit | TP hit | Exit at TP price | STOP BUILD |
| Unit | HOLD-veto | MACD expanding delays TP | STOP BUILD |
| Unit | TIME_EXIT | hold>=TIME_EXIT + profit<req | STOP BUILD |

### 12. Simulation Engine

| Test Type | Test Name | Pass Condition | Fail Consequence |
|-----------|-----------|---------------|-----------------|
| Unit | freshState | State created correctly | STOP BUILD |
| Unit | process | 1 candle processed | STOP BUILD |
| Unit | computeAll | All candles processed | STOP BUILD |
| Unit | pipeline stages | All 22 stages executed | STOP BUILD |
| Unit | Card sharing | SHARED stages 1x | STOP BUILD |
| Determinism | 2-run hash | Identical checksums | STOP BUILD |
| Integration | Full pipeline | market->truth->...->governance | STOP BUILD |

### 13. Replay Engine

| Test Type | Test Name | Pass Condition | Fail Consequence |
|-----------|-----------|---------------|-----------------|
| Unit | Candle replay | Candle sequence correct | STOP BUILD |
| Unit | Snapshot replay | Full frame correct | STOP BUILD |
| Unit | Trade replay | Markers correct | STOP BUILD |
| Unit | Clone replay | Observations correct | STOP BUILD |
| Unit | Knowledge replay | Artifacts correct | STOP BUILD |
| Unit | Governance replay | Timeline correct | STOP BUILD |
| Determinism | Replay bit-per-bit | Identical to original | STOP BUILD |

### 14. Statistics Layer

| Test Type | Test Name | Pass Condition | Fail Consequence |
|-----------|-----------|---------------|-----------------|
| Unit | Trade stats | Per-clone metrics correct | STOP BUILD |
| Unit | Sample gate | >=30 = CUKUP, <30 = BELUM_CUKUP | STOP BUILD |
| Unit | Win rate | wins/sample * 100 | STOP BUILD |
| Unit | Expectancy | sum(net)/sample | STOP BUILD |
| Unit | PF | sum(gross_pos)/sum(abs(gross_neg)) | STOP BUILD |
| Unit | Fee drag | sum(fee)/sample | STOP BUILD |
| Unit | Wrong rate | wrong/sample * 100 | STOP BUILD |

### 15. BAG Layer

| Test Type | Test Name | Pass Condition | Fail Consequence |
|-----------|-----------|---------------|-----------------|
| Unit | Grouping | Artifacts grouped by bag_key | STOP BUILD |
| Unit | Classification | bag_kind assigned correctly | STOP BUILD |
| Unit | Consensus | HIGH/MEDIUM/LOW/NONE calculated | STOP BUILD |
| Unit | Conflict | conflict_level calculated | STOP BUILD |
| Unit | Pattern mining | Patterns detected | SOFT |
| Unit | Fingerprint | Distance fingerprint generated | STOP BUILD |
| Unit | Compression | Redundant artifacts compressed | SOFT |
| Unit | No write-back | BAG does not write to upstream | STOP BUILD |

### 16. Knowledge Layer

| Test Type | Test Name | Pass Condition | Fail Consequence |
|-----------|-----------|---------------|-----------------|
| Unit | Academy | win_rate per 4-dim bucket | STOP BUILD |
| Unit | Oracle | Euclidean similarity match | STOP BUILD |
| Unit | HiveMind | intelligence_score 0-10000 | STOP BUILD |
| Unit | CERMIN | calibration_error per clone | STOP BUILD |
| Unit | Librarian | 6 lifecycle statuses | STOP BUILD |
| Unit | Darwin | Proposals generated | STOP BUILD |
| Unit | River | Chronicle appended | STOP BUILD |
| Unit | Unidirectional | No write-back to Core | STOP BUILD |
| Unit | No-ML | No ML detected | STOP BUILD |
| Unit | Oracle vector | W%R/MACD not in vector | STOP BUILD |

### 17. Prediction Layer

| Test Type | Test Name | Pass Condition | Fail Consequence |
|-----------|-----------|---------------|-----------------|
| Unit | Empirical only | no_model = true | STOP BUILD |
| Unit | Sample gate | BELUM_CUKUP -> NULL | STOP BUILD |
| Unit | Intelligence score | 0-10000 range | STOP BUILD |
| Unit | No forecast model | No predictive model detected | STOP BUILD |

### 18. Trading Schema Layer

| Test Type | Test Name | Pass Condition | Fail Consequence |
|-----------|-----------|---------------|-----------------|
| Unit | Market schemas | 10 schemas defined | STOP BUILD |
| Unit | Trading schemas | 7 schemas defined | STOP BUILD |
| Unit | Entry schemas | 11 schemas defined | STOP BUILD |
| Unit | Position schemas | 7 schemas defined | STOP BUILD |
| Unit | Exit schemas | 6 schemas defined | STOP BUILD |
| Unit | Schema completeness | All required fields per schema | STOP BUILD |
| Unit | No spec override | Schema does not modify spec | STOP BUILD |

### 19. Governance Layer

| Test Type | Test Name | Pass Condition | Fail Consequence |
|-----------|-----------|---------------|-----------------|
| Unit | Constitution validation | 18 laws checked | STOP BUILD |
| Unit | Proposal validation | Bounded-check enforced | STOP BUILD |
| Unit | Authority matrix | Indicator usage checked | STOP BUILD |
| Unit | Bounded auto-reject | Out-of-range rejected | STOP BUILD |
| Unit | Rollback | Config reverted | STOP BUILD |
| Unit | No auto-execute | Darwin does not auto-execute | STOP BUILD |
| Unit | No Core write | Governance only writes BOUNDED | STOP BUILD |

### 20. Benchmark Layer

| Test Type | Test Name | Pass Condition | Fail Consequence |
|-----------|-----------|---------------|-----------------|
| Unit | WASIT 5-gate | All gates evaluated | STOP BUILD |
| Unit | Identical -> G2 FAIL | Same config fails G2 | STOP BUILD |
| Unit | Majority vote | Per-gate majority of folds | STOP BUILD |
| Unit | Parallel worker | Worker executes | SOFT |
| Unit | Fallback sequential | Sequential if worker fails | STOP BUILD |

### 21. Consumer Layer

| Test Type | Test Name | Pass Condition | Fail Consequence |
|-----------|-----------|---------------|-----------------|
| Unit | Fund evaluation | Position size, drawdown | STOP BUILD |
| Unit | Veto gate | Risk checks | STOP BUILD |
| Unit | Intent builder | Trade intent constructed | STOP BUILD |
| Unit | CSV export | Markers exported correctly | STOP BUILD |
| Unit | Live adapter disabled | Cannot enable without approval | STOP BUILD |

### 22. Dashboard Layer

| Test Type | Test Name | Pass Condition | Fail Consequence |
|-----------|-----------|---------------|-----------------|
| Unit | No-mock render | Empty = N/A, not placeholder | STOP BUILD |
| Unit | Geometry chart | Candle + ST + cage rendered | STOP BUILD |
| Unit | Clone cards | 3 clone cards rendered | STOP BUILD |
| Unit | Trade history | Table rendered | STOP BUILD |
| Unit | Equity curve | Chart rendered | STOP BUILD |
| Unit | All panels | 20+ panels render without error | STOP BUILD |
| Unit | Read-only | Dashboard does not compute logic | STOP BUILD |

### 23. Integration Layer

| Test Type | Test Name | Pass Condition | Fail Consequence |
|-----------|-----------|---------------|-----------------|
| Unit | Worker bridge | postMessage protocol works | STOP BUILD |
| Unit | Pipeline orchestration | 22 stages in order | STOP BUILD |
| Unit | Card sharing | SHARED 1x, PER-CLONE 3x | STOP BUILD |
| Unit | Serial writer | Single writer, zero race | STOP BUILD |
| Unit | Worker no-direct-DB | Workers do not access IndexedDB | STOP BUILD |

### 24. Audit Layer

| Test Type | Test Name | Pass Condition | Fail Consequence |
|-----------|-----------|---------------|-----------------|
| Unit | 16 self-tests | All pass | STOP BUILD |
| Unit | Pipeline audit | 22 stages verified | STOP BUILD |
| Unit | Snapshot audit | 10 snapshots verified | STOP BUILD |
| Unit | Clone audit | 3 clones, 3 obs/candle | STOP BUILD |
| Unit | Trade audit | P&L, after-fee, adverse-first | STOP BUILD |
| Unit | Knowledge audit | Unidirectional, no-ML | STOP BUILD |
| Unit | Governance audit | Timeline, rollback | STOP BUILD |
| Unit | Fingerprint | Deterministic hash | STOP BUILD |

### 25. Final Validation

| Test Type | Test Name | Pass Condition | Fail Consequence |
|-----------|-----------|---------------|-----------------|
| Unit | Runtime check | State + frames + snapshots | STOP BUILD |
| Unit | Pipeline check | Snapshots per frame | STOP BUILD |
| Unit | Namespace check | 26 namespaces present | STOP BUILD |
| Unit | Feature check | 9 snapshot partitions | STOP BUILD |
| Unit | Truth check | st/stDir/color/atr/ema/rsi/wpr/macd | STOP BUILD |
| Unit | Clone check | LONG/SHORT/GRID present | STOP BUILD |
| Unit | Trading check | entry->position->exit->marker | STOP BUILD |
| Unit | Knowledge check | 7 entities present | STOP BUILD |
| Unit | Replay check | 6 replay types | STOP BUILD |
| Unit | Governance check | 6 validations | STOP BUILD |
| Unit | Constitution check | Audit tests pass | STOP BUILD |
| Unit | Console check | No swallowed errors | STOP BUILD |

### 26. BUILD APPROVAL

| Test Type | Test Name | Pass Condition | Fail Consequence |
|-----------|-----------|---------------|-----------------|
| Integration | 15 stop-rule | All PASS | STOP BUILD |
| Integration | 18 LAW-MASTER | All compliant | STOP BUILD |
| Integration | Determinism | 2-run identical | STOP BUILD |
| Integration | No spec conflict | Zero conflicts | STOP BUILD |
| Integration | No missing component | All components present | STOP BUILD |

---

## TEST CONTRACT STATUS: LOCKED

All test requirements for all 26 phases are constitutionally frozen. LAYER TIDAK BOLEH DILANJUTKAN APABILA TEST GAGAL. Every HARD gate must PASS before proceeding to the next phase.
