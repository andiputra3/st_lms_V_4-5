# 13_GOVERNANCE_LAYER.md

## ST-LMS — Governance Layer Architecture Mapping

**Date:** 2026-07-28
**Status:** ARCHITECTURE MAPPING — FROZEN
**Sources:** MASTER_SPECIFICATION.html §11, QWEN_14_DOC.html D10, ST_LMS_CORE.js (GOVERNANCE, CONFIG namespaces)

---

### 1. Responsibility

Governance Layer adalah rem & kemudi evolusi ST-LMS. Layer ini memvalidasi konstitusi, proposal, authority matrix, build, runtime — dan mengaudit semuanya. Loop balik hanya ke parameter BOUNDED & PEX, tidak pernah ke Truth/Structure/Evidence/Clone-logic.

### 2. Purpose

- Memvalidasi kepatuhan terhadap 18 hukum dan authority matrix
- Mengelola proposal lifecycle (Darwin → WASIT → Human → apply/rollback)
- Menerapkan bounded auto-reject (nilai di luar rentang = REJECTED)
- Menyediakan rollback deterministik ke config_version sebelumnya
- Mengaudit timeline keputusan governance

### 3. Input

- `knowledge_snapshot` — darwin_proposals, academy_artifacts
- `config` — bounded parameters (current values)
- Human decisions — approve/reject

### 4. Output

- `config_version` update (BOUNDED parameters only)
- Proposal decisions (APPROVED/REJECTED/ROLLED_BACK)
- Governance logs
- Rollback logs

### 5. Dependency Layer

- **Upstream**: KNOWLEDGE (darwin_proposals)
- **Downstream**: CONSUMER (config_version), semua layer (via BOUNDED parameter update)

### 6. Previous Pipeline

KNOWLEDGE — Governance membaca darwin_proposals.

### 7. Next Pipeline

CONSUMER — Config version update mempengaruhi Consumer.

### 8. SQLite Tables yang Digunakan

- `knowledge_artifacts` — membaca darwin proposals
- `app_settings` — membaca config

### 9. SQLite Tables yang Dihasilkan

- `governance_proposals` — proposal lifecycle
- `governance_logs` — event timeline
- `rollback_logs` — rollback events

### 10. Artifact yang Dihasilkan

- 6 validation results (Constitution, Proposal, Authority Matrix, Build, Runtime, Governance Audit)
- Proposal decisions (APPROVED/REJECTED/REJECTED_OUT_OF_RANGE/REJECTED_BY_WASIT)
- Config version updates
- Rollback events

### 11. Validator yang Dibutuhkan

- **Constitution Validator** — 18 laws + authority matrix compliance
- **Proposal Validator** — bounded-check + label-peran + constitutional-atom
- **Authority Matrix Validator** — indicator usage within valid columns
- **Build Validator** — 15 stop-rules + inventory + determinism
- **Runtime Validator** — checksum + lineage + no-race writer + sample-gate
- **Governance Audit Validator** — decision timeline + rollback + deprecated enforcement

### 12. Knowledge Entity yang Digunakan

- Darwin — proposal generation
- Academy — artifacts untuk evaluasi

### 13. Trading Entity yang Digunakan

Tidak langsung — Governance mempengaruhi trading melalui BOUNDED parameter update.

### 14. Snapshot yang Digunakan

- `knowledge_snapshot` — darwin_proposals

### 15. Benchmark yang Digunakan

- WASIT 5-Gate — evaluasi proposal sebelum human approval

### 16. Dashboard Component yang Digunakan

- Governance Validation Panel — 6 validation results
- Proposal Panel — daftar proposal dengan approve/reject buttons
- Rollback Button — revert ke config default
- Config Table — bounded parameters dengan current/min/max values
- Governance Log — event timeline

### 17. Mandatory atau Optional

**MANDATORY** — Governance adalah rem & kemudi evolusi sistem.

### 18. Specification Reference

- MASTER_SPECIFICATION.html §11 (Governance Master Constitution)
- MASTER_SPECIFICATION.html §14 (Human Approval + Bounded LAW-MASTER-14)
- MASTER_SPECIFICATION.html §3 (Constitution Freeze Matrix — Governance constitution)
- QWEN_14_DOC.html D10 (Governance Architecture)
- ST_LMS_CORE.js lines 86-105 (CONFIG), 575-598 (GOVERNANCE)

### 19. Build Order Recommendation

```
Build Order: 13
Dependencies: KNOWLEDGE, BENCHMARK, CONFIG
Build setelah: KNOWLEDGE, BENCHMARK
Build sebelum: CONSUMER
```

### 20. Notes dan Constraint

- **3-Rem**: Darwin (usul), WASIT (saring), Human (putuskan)
- **6 Validasi**: Constitution, Proposal, Authority Matrix, Build, Runtime, Governance Audit
- **Bounded auto-reject**: Nilai di luar [min, max] → REJECTED tanpa compute
- **WASIT 5-Gate**: G1(sample≥30), G2(expectancy>base), G3(worst not worse>10%), G4(win_rate not dropped>2%), G5(fee not increased)
- **Proposal Lifecycle**: PENDING → WASIT → PENDING_HUMAN → APPROVED/REJECTED
- **Kelas-A**: Bounded parameter adjustment (WASIT + Human)
- **Kelas-B**: PEX — constitutional amendment (approval ganda + Chronicle)
- **Rollback**: Tunjuk config_version lama; deterministik
- **Loop ONLY to BOUNDED**: Tidak pernah ke Truth/Structure/Evidence/Clone-logic
- **Darwin NO auto-execute**: Proposal harus melalui WASIT → Human
- **Human approval ganda**: Untuk amandemen konstitusi (§3)
- **Chronicle**: CONSTITUTION_AMENDED tercatat
- **SHARED-AGAIN (1×)**: Governance dijalankan 1× setelah Knowledge
- **Thread**: Main thread
- **Date.now()**: DILARANG — gunakan timestamp dari candle (FIXED per audit H1)
- **24 BOUNDED parameters**: ENTRY_OFFSET_BASE_K, WPR_VELOCITY_DEADZONE, GRID_MIN_NET_PCT_OF_FILL, CAGE_TIGHT_ATR, WRONG_ENTRY_PCT, SAMPLE_GATE, dll.
