# 16_INTEGRATION_LAYER.md

## ST-LMS — Integration Layer Architecture Mapping

**Date:** 2026-07-28
**Status:** ARCHITECTURE MAPPING — FROZEN
**Sources:** DOCUMENT_DEPENDENCY.html, QWEN_14_DOC.html D4, ST_LMS_CORE.js

---

### 1. Responsibility

Integration Layer bertanggung jawab untuk mengorkestrasi seluruh aliran data antar layer, mengelola workers, menjembatani komunikasi main thread ↔ workers, dan memastikan integritas data di seluruh sistem. Layer ini adalah "lem" yang menghubungkan seluruh komponen ST-LMS.

### 2. Purpose

- Mengorkestrasi pipeline execution (22 stages)
- Mengelola worker lifecycle (create, postMessage, terminate)
- Menjembatani komunikasi main thread ↔ workers
- Memastikan card sharing berjalan benar (1× compute, 3× share)
- Memastikan unidirectional flow (tidak ada backward loop)
- Mengelola serial writer (single writer, main thread)
- Mengelola IndexedDB persistence

### 3. Input

- Config — bounded parameters
- Candle data — dari MARKET
- Worker results — via postMessage

### 4. Output

- Orchestrated pipeline execution
- Worker lifecycle events
- IndexedDB persistence
- Integration validation results

### 5. Dependency Layer

- **Upstream**: BOOT (initialization)
- **Downstream**: Semua layers (orchestration)

### 6. Previous Pipeline

BOOT — Integration dimulai setelah system initialization.

### 7. Next Pipeline

Semua pipeline stages — Integration mengorkestrasi seluruh pipeline.

### 8. SQLite Tables yang Digunakan

- `pipeline_runs` — run tracking
- `app_sessions` — session context

### 9. SQLite Tables yang Dihasilkan

Tidak langsung — Integration tidak menulis data domain.

### 10. Artifact yang Dihasilkan

- Pipeline execution logs
- Worker lifecycle logs
- Integration validation reports

### 11. Validator yang Dibutuhkan

- **Card Sharing Validator** — Truth/Structure/Evidence 1×, shared to 3 clones
- **Unidirectional Validator** — No backward loops detected
- **Worker Bridge Validator** — Workers send via postMessage; main persists
- **Serial Writer Validator** — Single writer, zero race conditions
- **Pipeline Stage Validator** — Stages in correct order + correct type
- **Integration Contract Validator** — Input/output contracts match

### 12. Knowledge Entity yang Digunakan

Tidak langsung — Integration mengorkestrasi Knowledge layer.

### 13. Trading Entity yang Digunakan

Tidak langsung — Integration mengorkestrasi Trading layer.

### 14. Snapshot yang Digunakan

Semua snapshots — Integration memastikan snapshot flow benar.

### 15. Benchmark yang Digunakan

Tidak langsung — Integration mengorkestrasi Benchmark layer.

### 16. Dashboard Component yang Digunakan

Tidak ada — Integration adalah backend orchestration.

### 17. Mandatory atau Optional

**MANDATORY** — Tanpa Integration, tidak ada orchestration antar layer.

### 18. Specification Reference

- MASTER_SPECIFICATION.html §6 (Master Trading Lifecycle — pipeline stages)
- DOCUMENT_DEPENDENCY.html §4 (Pipeline Dependency Graph)
- DOCUMENT_DEPENDENCY.html §10 (Validation Order)
- QWEN_14_DOC.html D4 (Runtime Architecture — thread topology)
- QWEN_14_DOC.html D5 (Pipeline Architecture)

### 19. Build Order Recommendation

```
Build Order: 16
Dependencies: Semua layers
Build setelah: Semua layers dibangun
Build bersama: Setiap layer (integration points)
```

### 20. Notes dan Constraint

- **Pipeline orchestration**: BOOT → MARKET → TRUTH → STRUCTURE → EVIDENCE → CLONE(×3) → TRADE → POSITION → STATISTICS → BAG → KNOWLEDGE → PREDICTION → GOVERNANCE → CONSUMER
- **ON-DEMAND**: BENCHMARK (tidak per candle)
- **CROSS-CUTTING**: SIMULATION, REPLAY, SNAPSHOT, AUDIT, VIEW
- **Worker integration**: Data Worker, Knowledge Worker, Benchmark Worker, Replay Worker
- **Worker contract**: Workers receive data via postMessage, return results via postMessage, do NOT access IndexedDB directly
- **Serial writer**: Main thread is the single writer to IndexedDB; zero race conditions
- **Card sharing enforcement**: Stages 2-5 run 1×; results shared to 3 clones
- **Unidirectional enforcement**: No data flow from Knowledge/Consumer back to Core/Clone
- **Integration points**: 15 integration points (MARKET→TRUTH, TRUTH→STRUCTURE, etc.)
- **Gate validation**: Each build phase must pass HARD gate before next phase
- **Thread safety**: Truth/Structure/Evidence/Clone per-candle sequential on main; parallel across symbols
- **Resource governor**: RAM threshold 70/85/95%; flush warm, kill idle workers, degrade
- **No setInterval**: Tidak ada idle candle playback loop
