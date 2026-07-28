# 04_WORKER_CONTRACT.md

## ST-LMS Implementation Contract Freeze V1 — Worker Contract

**Date:** 2026-07-28
**Status:** CONSTITUTIONALLY FROZEN

---

## WORKER AUTHORITY RULES

1. Workers are COLD: created on demand, terminated after completion
2. Workers use POSTMESSAGE: send results to main thread
3. Workers DO NOT access IndexedDB directly
4. Workers DO NOT access SQLite directly
5. Main thread PERSISTS: validates and stores worker results
6. Workers are DETERMINISTIC: same input -> same output
7. Workers have TIMEOUT: terminated if exceeding limit

---

## 1. MARKET WORKER (Data Worker)

| Aspect | Value |
|--------|-------|
| Authority | Read raw data, process batches |
| Responsibility | Batch bootstrap, TF aggregation, gap-repair |
| Input | Raw candle data (OHLCV) |
| Output | Processed market data, derived TFs |
| Dependency | MARKET layer |
| Execution Order | After MARKET data available, before TRUTH |
| Thread | Separate (cold) |
| Timeout | 120s |
| Fallback | Sequential on main thread |
| Forbidden | IndexedDB write, SQLite write, trading decisions |

---

## 2. TRUTH WORKER

| Aspect | Value |
|--------|-------|
| Authority | N/A — Truth is main thread only |
| Responsibility | N/A — Truth requires state continuity |
| Input | N/A |
| Output | N/A |
| Dependency | N/A |
| Execution Order | N/A |
| Note | **Truth is NOT a worker.** Truth/Structure/Evidence/Clone per-candle for one symbol MUST be sequential on main thread. Parallelizing per-candle breaks EMA/ATR continuity. |

---

## 3. DISTANCE WORKER

| Aspect | Value |
|--------|-------|
| Authority | N/A — Distance is computed alongside Truth/Structure |
| Responsibility | N/A |
| Input | N/A |
| Output | N/A |
| Dependency | N/A |
| Execution Order | N/A |
| Note | **Distance is NOT a separate worker.** Distance metrics are computed in TRUTH (W fields) and STRUCTURE (OD fields). |

---

## 4. STRUCTURE WORKER

| Aspect | Value |
|--------|-------|
| Authority | N/A — Structure is main thread only |
| Responsibility | N/A — Structure requires state continuity |
| Input | N/A |
| Output | N/A |
| Dependency | N/A |
| Execution Order | N/A |
| Note | **Structure is NOT a worker.** Same as Truth — requires contiguous state. |

---

## 5. TRADING WORKER

| Aspect | Value |
|--------|-------|
| Authority | N/A — Trading is main thread only |
| Responsibility | N/A — Clone execution is PER-CLONE on main thread |
| Input | N/A |
| Output | N/A |
| Dependency | N/A |
| Execution Order | N/A |
| Note | **Trading is NOT a worker.** Clone observation/entry/exit must be sequential per symbol. Parallel across symbols is allowed. |

---

## 6. STATISTICS WORKER

| Aspect | Value |
|--------|-------|
| Authority | Compute statistics from markers |
| Responsibility | Batch aggregation of trade statistics |
| Input | trade_markers array |
| Output | Aggregated statistics (win_rate, expectancy, pf, mae, mfe, fee_drag, wrong_rate) |
| Dependency | STATISTICS layer |
| Execution Order | After TRADE markers available, before BAG |
| Thread | Main thread (lightweight) or Knowledge Worker (batch) |
| Timeout | 30s |
| Fallback | Sequential on main thread |
| Forbidden | IndexedDB write, SQLite write |

---

## 7. BAG WORKER (Knowledge Worker — shared)

| Aspect | Value |
|--------|-------|
| Authority | Group, classify, mine patterns, generate fingerprints |
| Responsibility | BAG artifact generation, pattern mining, behavior analysis |
| Input | trade_statistics, market_statistics, trade_markers, snapshots |
| Output | bag_artifacts, bag_patterns, bag_compression, fingerprints |
| Dependency | BAG layer, STATISTICS |
| Execution Order | After STATISTICS, before KNOWLEDGE |
| Thread | Separate (cold) — shared Knowledge Worker |
| Timeout | 120s |
| Fallback | Sequential on main thread |
| Forbidden | IndexedDB write, SQLite write, Core write |

---

## 8. KNOWLEDGE WORKER

| Aspect | Value |
|--------|-------|
| Authority | Learn from BAG, compute knowledge entities |
| Responsibility | Academy, Oracle, Darwin, Librarian computation |
| Input | BAG artifacts, trade_markers, snapshots |
| Output | academy_artifacts, oracle_match, darwin_proposals, librarian_events |
| Dependency | KNOWLEDGE layer, BAG |
| Execution Order | After BAG, before PREDICTION |
| Thread | Separate (cold) |
| Timeout | 300s |
| Fallback | Sequential on main thread |
| Forbidden | IndexedDB write, SQLite write, Core write, grouping (BAG does that) |

---

## 9. PREDICTION WORKER

| Aspect | Value |
|--------|-------|
| Authority | N/A — Prediction is main thread only |
| Responsibility | N/A — Prediction is lightweight aggregation |
| Input | N/A |
| Output | N/A |
| Dependency | N/A |
| Execution Order | N/A |
| Note | **Prediction is NOT a separate worker.** Lightweight aggregation on main thread. |

---

## 10. GOVERNANCE WORKER

| Aspect | Value |
|--------|-------|
| Authority | N/A — Governance is main thread only |
| Responsibility | N/A — Governance decisions require human interaction |
| Input | N/A |
| Output | N/A |
| Dependency | N/A |
| Execution Order | N/A |
| Note | **Governance is NOT a worker.** Requires human approval. WASIT benchmark uses Benchmark Worker. |

---

## 11. SIMULATION WORKER

| Aspect | Value |
|--------|-------|
| Authority | N/A — Simulation orchestrates main thread pipeline |
| Responsibility | N/A — Simulation state management is on main thread |
| Input | N/A |
| Output | N/A |
| Dependency | N/A |
| Execution Order | N/A |
| Note | **Simulation is NOT a separate worker.** Orchestrates main thread pipeline execution. Replay uses Replay Worker. |

---

## 12. BENCHMARK WORKER

| Aspect | Value |
|--------|-------|
| Authority | Evaluate config changes via WASIT walk-forward |
| Responsibility | Parallel WASIT 5-gate walk-forward validation |
| Input | Base markers, candidate markers, fold count |
| Output | WASIT result (gates, per_fold, verdict) |
| Dependency | BENCHMARK layer |
| Execution Order | ON-DEMAND — when governance proposal needs evaluation |
| Thread | Separate (cold) — parallel base vs candidate |
| Timeout | 300s |
| Fallback | Sequential on main thread (deterministic) |
| Forbidden | IndexedDB write, SQLite write, approve proposals |

---

## 13. DASHBOARD WORKER

| Aspect | Value |
|--------|-------|
| Authority | N/A — Dashboard is UI rendering on main thread |
| Responsibility | N/A — UI must be on main thread |
| Input | N/A |
| Output | N/A |
| Dependency | N/A |
| Execution Order | N/A |
| Note | **Dashboard is NOT a worker.** UI rendering on main thread. Long queries use Query Worker. |

---

## 14. INTEGRATION WORKER (Replay Worker)

| Aspect | Value |
|--------|-------|
| Authority | Replay snapshots deterministically |
| Responsibility | Parallel replay across symbols |
| Input | Snapshot sequences from IndexedDB |
| Output | Replay frames |
| Dependency | REPLAY layer |
| Execution Order | On-demand — when user requests replay |
| Thread | Separate (cold) — parallel across symbols |
| Timeout | 600s |
| Fallback | Sequential on main thread |
| Forbidden | IndexedDB write, SQLite write, modify cards |

---

## WORKER EXECUTION ORDER

```
1. Data Worker        — MARKET batch processing (cold, dies after)
2. (Main Thread)      — TRUTH, STRUCTURE, EVIDENCE (hot, sequential)
3. (Main Thread)      — CLONE, TRADE, POSITION (hot, PER-CLONE)
4. (Main Thread)      — STATISTICS (lightweight aggregation)
5. Knowledge Worker   — BAG + KNOWLEDGE (cold, batch, dies after)
6. (Main Thread)      — PREDICTION, GOVERNANCE (lightweight)
7. Benchmark Worker   — WASIT evaluation (cold, on-demand, dies after)
8. Replay Worker      — Replay across symbols (cold, on-demand, dies after)
9. (Main Thread)      — DASHBOARD, CONSUMER (UI, terminal)
```

---

## WORKER CONTRACT STATUS: LOCKED

All 14 worker contracts are constitutionally frozen. Only 4 workers are actual separate-thread workers (Data, Knowledge/BAG, Benchmark, Replay). Truth, Structure, Trading, Prediction, Governance, Dashboard are main-thread only. Each worker defines authority, responsibility, input, output, dependency, execution order, timeout, fallback, and forbidden operations. No new worker may be created without Architecture Approval.
