# KNOWLEDGE LAYER ENRICHMENT — Patch 06

## ST-LMS Architecture Enrichment Patch V1

**Date:** 2026-07-28
**Status:** ENRICHMENT ANALYSIS — FROZEN
**Sources:** MASTER_SPECIFICATION.html §8, ST_LMS_CORE.js (KNOWLEDGE namespace), BAG_ARCHITECTURE_SPECIFICATION.md

---

## 1. ANALISIS: Grouping dipindahkan ke BAG

### 1.1 Current State

Saat ini, KNOWLEDGE layer melakukan beberapa operasi grouping:

| Entity | Grouping Operation | Should be in BAG? |
|--------|-------------------|-------------------|
| Academy | Group by clone, structure, distance_bucket, reason | ✅ YES — BAG |
| Academy | Count samples, wins, net per bucket | ⚠️ PARTIAL — BAG counts, Academy computes win_rate |
| Oracle | Euclidean similarity matching | ❌ NO — Knowledge-specific |
| HiveMind | Synthesize understanding from Academy + Oracle + Evidence | ❌ NO — Knowledge-specific |
| CERMIN | Calibration error per clone | ❌ NO — Knowledge-specific |
| Librarian | Lifecycle status per bucket | ❌ NO — Knowledge-specific |
| Darwin | Propose parameter mutations | ❌ NO — Knowledge-specific |

### 1.2 Proposed State

```
┌──────────────────────────────────────────────────────────────────┐
│  BAG LAYER (Grouping & Classification)                            │
│                                                                    │
│  DOES:                                                             │
│    - Group trade_markers by dimensions (clone, structure,         │
│      distance_bucket, reason, market_phase, etc.)                 │
│    - Count samples, wins, net per group                           │
│    - Classify into bag_kind (behavior, market, entry, exit,       │
│      risk, knowledge)                                             │
│    - Summarize consensus, conflict_level, confidence              │
│    - Detect patterns (bag_patterns)                               │
│    - Compress redundant artifacts (bag_compression)               │
│                                                                    │
│  DOES NOT:                                                        │
│    - Compute win_rate (that's Academy)                            │
│    - Compute expectancy (that's Academy)                          │
│    - Do similarity matching (that's Oracle)                       │
│    - Synthesize understanding (that's HiveMind)                   │
│    - Manage lifecycle (that's Librarian)                          │
│    - Propose mutations (that's Darwin)                            │
│                                                                    │
├──────────────────────────────────────────────────────────────────┤
│                         │                                          │
│                         ▼                                          │
├──────────────────────────────────────────────────────────────────┤
│  KNOWLEDGE LAYER (Learning & Understanding)                       │
│                                                                    │
│  DOES:                                                             │
│    - Learn from BAG artifacts                                     │
│    - Consume BAG grouped data                                     │
│    - Summarize insights (win_rate, expectancy from BAG counts)    │
│    - Infer patterns (Oracle similarity on BAG vectors)            │
│    - Recommend actions (Darwin proposals from BAG insights)       │
│                                                                    │
│  DOES NOT:                                                        │
│    - Group raw data (that's BAG)                                  │
│    - Classify artifacts (that's BAG)                              │
│    - Count samples per group (that's BAG)                         │
│    - Find consensus/conflict (that's BAG)                         │
└──────────────────────────────────────────────────────────────────┘
```

---

## 2. KNOWLEDGE ENTITY ENRICHMENT

### 2.1 Academy

```
CURRENT:
  Input: markers + snapshots
  Output: win_rate per (clone, structure, distance_bucket, reason)

ENRICHED:
  Input: BAG artifacts (pre-grouped) + raw markers (for verification)
  Output:
    - win_rate per BAG bag_key
    - expectancy per BAG bag_key
    - win_rate_trend (apakah win_rate membaik/memburuk)
    - sample_growth_rate (seberapa cepat sample bertambah)
    - confidence_interval (statistical confidence range)

  DOES: Learn win_rate from BAG groupings
  DOES NOT: Group markers into buckets (BAG does this)
```

### 2.2 River

```
CURRENT:
  Input: all cards
  Output: append + index + chronicle

ENRICHED:
  Input: all cards + BAG artifacts
  Output:
    - chronicle dengan BAG events
    - artifact lineage tracking
    - BAG artifact → knowledge artifact traceability

  DOES: Record everything (including BAG events)
  DOES NOT: Group or classify (BAG does this)
```

### 2.3 Oracle

```
CURRENT:
  Input: vector_now + historical vectors
  Output: oracle_match (euclidean, match > 7500)

ENRICHED:
  Input: vector_now + historical vectors + BAG similarity context
  Output:
    - oracle_match dengan BAG context
    - similarity per BAG bag_kind
    - historical pattern recurrence frequency
    - vector_cluster (kelompok vector yang mirip)

  DOES: Similarity matching (Knowledge-specific)
  DOES NOT: Group vectors (BAG can group Oracle results)
```

### 2.4 HiveMind

```
CURRENT:
  Input: academy_artifacts + oracle_match + evidence_snapshot
  Output: market_understanding (score, bias, boosts)

ENRICHED:
  Input: BAG artifacts + academy_artifacts + oracle_match + evidence_snapshot
  Output:
    - intelligence_score dengan BAG confidence adjustment
    - dominant_bias dengan BAG consensus validation
    - per_bag_kind_understanding (behavior, market, entry, exit, risk)
    - conflict_awareness (jika BAG conflict_level HIGH)

  DOES: Synthesize understanding (Knowledge-specific)
  DOES NOT: Group data (BAG does this)
```

### 2.5 CERMIN

```
CURRENT:
  Input: markers + confidence
  Output: calibration_error per clone

ENRICHED:
  Input: BAG artifacts (grouped confidence) + actual outcomes
  Output:
    - calibration_error per BAG bag_key
    - calibration_trend (apakah kalibrasi membaik)
    - overconfidence_detection (confidence > actual secara konsisten)
    - underconfidence_detection (confidence < actual secara konsisten)

  DOES: Calibrate confidence (Knowledge-specific)
  DOES NOT: Group calibration data (BAG does this)
```

### 2.6 Librarian

```
CURRENT:
  Input: academy_artifacts
  Output: lifecycle events (NEW→OBS→TRUSTED→MATURE/DEAD/DEPRECATED)

ENRICHED:
  Input: BAG artifacts + academy_artifacts
  Output:
    - lifecycle per BAG bag_key
    - lifecycle per BAG bag_kind
    - cross-bag lifecycle (artifact yang related)
    - stability_score (seberapa stabil lifecycle)

  DOES: Manage lifecycle (Knowledge-specific)
  DOES NOT: Group artifacts (BAG does this)
```

### 2.7 Darwin

```
CURRENT:
  Input: academy_artifacts
  Output: proposals (TIGHTEN_ENTRY, TIGHTEN_WRONG)

ENRICHED:
  Input: BAG artifacts + academy_artifacts + librarian_events
  Output:
    - proposals berdasarkan BAG conflict_level
    - proposals berdasarkan BAG consensus
    - per_bag_kind proposals (behavior, market, entry, exit, risk)
    - proposal_priority (berdasarkan BAG confidence)

  DOES: Propose mutations (Knowledge-specific)
  DOES NOT: Group proposal data (BAG does this)
```

---

## 3. KNOWLEDGE → BAG BOUNDARY

```
┌──────────────────────────────────────────────────────────────────┐
│                     KNOWLEDGE LAYER ONLY:                          │
│                                                                    │
│  ✅ LEARN      — Academy learns win_rate from BAG groupings       │
│  ✅ CONSUME    — All entities consume BAG artifacts               │
│  ✅ SUMMARIZE  — HiveMind summarizes market understanding         │
│  ✅ INFER      — Oracle infers similarity from vectors            │
│  ✅ RECOMMEND  — Darwin recommends parameter changes              │
│                                                                    │
│  ❌ GROUP      — MOVED TO BAG                                     │
│  ❌ CLASSIFY   — MOVED TO BAG                                     │
│  ❌ COUNT      — MOVED TO BAG                                     │
│  ❌ COMPARE    — MOVED TO BAG                                     │
│                                                                    │
├──────────────────────────────────────────────────────────────────┤
│                     BAG LAYER ONLY:                                │
│                                                                    │
│  ✅ GROUP      — Group markers by dimensions                     │
│  ✅ CLASSIFY   — Classify into bag_kind                          │
│  ✅ COUNT      — Count samples, wins, net per group              │
│  ✅ COMPARE    — Compare groups, find consensus/conflict          │
│  ✅ SUMMARIZE  — Summarize confidence per group                  │
│  ✅ SCORE      — Score consensus level                            │
│  ✅ TAG        — Tag with bag_key                                 │
│                                                                    │
│  ❌ LEARN      — STAYS IN KNOWLEDGE                               │
│  ❌ INFER      — STAYS IN KNOWLEDGE                               │
│  ❌ RECOMMEND  — STAYS IN KNOWLEDGE                               │
└──────────────────────────────────────────────────────────────────┘
```

---

## 4. KNOWLEDGE ENTITY DEPENDENCY (ENRICHED)

```
┌──────────────────────────────────────────────────────────────────┐
│                         BAG LAYER                                  │
│  bag_artifacts (grouped by bag_kind, bag_key)                     │
│  bag_patterns (detected patterns)                                 │
│  bag_compression (compression metrics)                            │
└──────────────────────────┬───────────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │ ACADEMY  │    │  ORACLE  │    │ HIVEMIND │
    │ (learn   │    │ (infer   │    │(synthesize│
    │ win_rate)│    │similarity│    │understand)│
    └────┬─────┘    └────┬─────┘    └────┬─────┘
         │               │               │
         └───────────────┼───────────────┘
                         │
          ┌──────────────┼──────────────┐
          │              │              │
          ▼              ▼              ▼
    ┌──────────┐  ┌──────────┐  ┌──────────┐
    │  CERMIN  │  │LIBRARIAN │  │  DARWIN  │
    │(calibrate│  │(lifecycle│  │(propose  │
    │confidence│  │ manage)  │  │mutation) │
    └──────────┘  └──────────┘  └──────────┘

    ┌──────────────────────────────────────────┐
    │                 RIVER                     │
    │  (records ALL events: BAG + Knowledge)    │
    └──────────────────────────────────────────┘
```

---

## KESIMPULAN PATCH 06

**Grouping sepenuhnya dipindahkan ke BAG.** Knowledge Layer TIDAK lagi melakukan operasi grouping, classification, counting, atau comparison. Operasi tersebut sepenuhnya menjadi tanggung jawab BAG.

**Knowledge Layer HANYA melakukan:**
- **LEARN** — Academy belajar win_rate dari BAG groupings
- **CONSUME** — Semua entities mengonsumsi BAG artifacts
- **SUMMARIZE** — HiveMind meringkas pemahaman market
- **INFER** — Oracle menginfer similarity dari vectors
- **RECOMMEND** — Darwin merekomendasikan parameter changes

**Pembagian yang jelas:**
- BAG = GROUPING ENGINE (what groups exist, how do they compare)
- KNOWLEDGE = LEARNING ENGINE (what can we learn from these groups)

**Tidak ada perubahan pada:** Konstitusi, spesifikasi, SQLite schema, pipeline stages, layer authority.
