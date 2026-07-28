# 10_KNOWLEDGE_LAYER.md

## ST-LMS — Knowledge Layer Architecture Mapping

**Date:** 2026-07-28
**Status:** ARCHITECTURE MAPPING — FROZEN
**Sources:** MASTER_SPECIFICATION.html §8, QWEN_14_DOC.html D7, ST_LMS_CORE.js (KNOWLEDGE namespace)

---

### 1. Responsibility

Knowledge Layer bertanggung jawab untuk mengekstrak pemahaman empiris dari trade outcomes. Layer ini terdiri dari 6 entitas pengetahuan (River, Academy, Oracle, HiveMind, Darwin, Librarian) + CERMIN, yang beroperasi secara unidirectional, card-agnostic, dan no-ML. Knowledge tidak mengalir balik ke Core/Clone.

### 2. Purpose

- Mencatat seluruh card secara append-only (River)
- Menghitung win_rate empiris bersyarat per bucket (Academy)
- Mencari kemiripan market state via euclidean similarity (Oracle)
- Mensintesis pemahaman market (HiveMind)
- Mengkalibrasi confidence vs actual (CERMIN)
- Mengusulkan mutasi parameter (Darwin)
- Mengelola lifecycle artifact (Librarian)

### 3. Input

- Semua cards (card-agnostic) — dari seluruh pipeline
- Trade markers + snapshots — untuk Academy
- Vector sekarang + historis — untuk Oracle
- Academy artifacts + Oracle match + evidence_snapshot — untuk HiveMind

### 4. Output

- `knowledge_snapshot` card (immutable)
- academy_artifacts[] — win_rate per 4-dim bucket
- oracle_match — similarity match result
- hivemind — intelligence_score, dominant_bias, pattern_boost, oracle_boost, evidence_adj
- cermin — calibration_error per clone
- librarian_events[] — lifecycle status changes
- darwin_proposals[] — parameter mutation proposals

### 5. Dependency Layer

- **Upstream**: STATISTICS (trade statistics), BAG (bag_artifacts), semua SNAPSHOT
- **Downstream**: PREDICTION (knowledge_snapshot), GOVERNANCE (darwin_proposals)

### 6. Previous Pipeline

STATISTICS — Knowledge membaca statistics_snapshot.
BAG — Knowledge membaca bag_artifacts.

### 7. Next Pipeline

PREDICTION — Knowledge snapshot mengalir ke Prediction.
GOVERNANCE — Darwin proposals mengalir ke Governance.

### 8. SQLite Tables yang Digunakan

- `trade_statistics` — membaca stat_id reference
- `bag_artifacts` — membaca bag_id reference
- `trade_markers` — membaca marker data
- Semua snapshot tables — membaca untuk Academy join

### 9. SQLite Tables yang Dihasilkan

- `knowledge_artifacts` — knowledge engine artifacts (7 entity types)

### 10. Artifact yang Dihasilkan

- **Academy**: win_rate per (clone, structure, distance_bucket, reason) bucket
- **River**: append-only chronicle events
- **Oracle**: euclidean similarity match (score > 7500 = match)
- **HiveMind**: market_understanding (intelligence_score 0-10000, dominant_bias BULLISH/BEARISH/NEUTRAL)
- **CERMIN**: calibration_error per clone (predicted vs actual)
- **Librarian**: lifecycle events (NEW→OBS→TRUSTED→MATURE/DEAD/DEPRECATED)
- **Darwin**: proposals (TIGHTEN_ENTRY, TIGHTEN_WRONG)

### 11. Validator yang Dibutuhkan

- **Unidirectional Validator** — tidak ada write-back ke Core/Clone
- **No-ML Validator** — tidak ada machine learning
- **Sample Gate Validator** — Academy: CUKUP iff sample ≥ 30
- **Oracle Vector Validator** — W%R/MACD tidak masuk vektor
- **HiveMind Evidence Validator** — currentEvidence wajib dari evidence_snapshot
- **Darwin No-Auto-Execute Validator** — Darwin tidak auto-execute
- **Librarian Lifecycle Validator** — DEAD/DEPRECATED tidak aktif

### 12. Knowledge Entity yang Digunakan

| Entity | Deskripsi | Lifecycle |
|--------|-----------|-----------|
| Academy | win_rate empiris bersyarat | per cycle, sample-gated |
| River | archivist append-only | terus-menerus |
| Oracle | similarity euclidean | per cycle |
| HiveMind | market understanding | per cycle |
| Darwin | proposal mutasi | per cycle |
| Librarian | lifecycle management | per evaluasi |
| CERMIN | calibration error | per cycle |

### 13. Trading Entity yang Digunakan

Knowledge TIDAK membuat keputusan trading. Knowledge membaca trade_markers untuk analisis.

### 14. Snapshot yang Digunakan

- Semua snapshots (card-agnostic reading)
- evidence_snapshot — wajib untuk HiveMind

### 15. Benchmark yang Digunakan

Tidak langsung — Knowledge data dapat digunakan untuk benchmark context.

### 16. Dashboard Component yang Digunakan

- Academy Table — menampilkan bucket key, sample, win_rate, expectancy, status
- Oracle Panel — menampilkan match, similarity score
- HiveMind Panel — menampilkan intelligence_score, dominant_bias
- CERMIN Panel — menampilkan calibration_error per clone
- Librarian Feed — menampilkan lifecycle events
- Darwin Panel — menampilkan proposals

### 17. Mandatory atau Optional

**MANDATORY** — Knowledge adalah inti pembelajaran ST-LMS. "Learning is Mandatory."

### 18. Specification Reference

- MASTER_SPECIFICATION.html §8 (Knowledge Master Constitution)
- MASTER_SPECIFICATION.html §4 (Unidirectional LAW-MASTER-04)
- MASTER_SPECIFICATION.html §13 (Prediction = Empiris LAW-MASTER-13)
- QWEN_14_DOC.html D7 (Knowledge Architecture)
- ST_LMS_CORE.js lines 385-407 (KNOWLEDGE namespace)

### 19. Build Order Recommendation

```
Build Order: 10
Dependencies: STATISTICS, BAG, semua SNAPSHOT
Build setelah: STATISTICS, BAG
Build sebelum: PREDICTION, GOVERNANCE
```

### 20. Notes dan Constraint

- **Unidirectional**: Knowledge TIDAK mengalir balik ke Core/Clone (LAW-MASTER-04)
- **Card-agnostic**: Knowledge membaca cards tanpa mengetahui clone logic
- **No-ML**: Tidak ada machine learning; purely statistical/empirical
- **Academy bucket**: 4 dimensi — clone | structure | distance_bucket | reason
- **Oracle vector**: [normCodeWave, normCodeCage, pp, norm(ema), norm(oi), norm(vd), norm(mtf), norm(rsi), norm(distAtr)] — FROZEN
- **W%R/MACD NOT in vector**: Sesuai authority matrix
- **Oracle match**: score > 7500 → match; tie-break terbaru
- **HiveMind currentEvidence**: Wajib dari evidence_snapshot (bukan konstanta)
- **HiveMind NOT signal**: Pemahaman, bukan BUY/SELL
- **Librarian 6 statuses**: NEW, OBSERVATION, TRUSTED, MATURE, DEAD, DEPRECATED
- **DEAD/DEPRECATED**: Tidak jadi boost/entry-PEX
- **Darwin NO auto-execute**: Proposal harus melalui WASIT → Human
- **CERMIN calibration**: predicted vs actual win_rate; error untuk confidence honesty
- **Knowledge Worker**: Cold worker untuk batch Academy, Oracle, Darwin, Librarian
- **Thread**: Knowledge Worker (cold, batch); Main thread untuk HiveMind
- **Canonical chain**: River → Academy → (Oracle ∥) → HiveMind → Darwin → Librarian → Chronicle
