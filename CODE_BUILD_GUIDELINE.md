# CODE_BUILD_GUIDELINE.md

## ST-LMS v3 — Code Build Guideline

**Date:** 2026-07-29
**Phase:** 0 → 1 Transition
**Status:** FROZEN — All code MUST follow these rules

---

## 1. PURE FUNCTION

- Every function must be pure: same input = same output
- No side effects in read operations
- State mutation only in designated state managers
- No global mutable state outside CONFIG and WORKSPACE
- No Date.now() in logic — use candle timestamp
- No Math.random() in logic — use seeded PRNG (Mulberry32)

---

## 2. MODULAR ARCHITECTURE

- Setiap layer menghasilkan 4 file: `{layer}_artifact.py`, `{layer}_package.py`, `{layer}_validator.py`, `{layer}_consumer.py`
- **Artifact**: Raw data/snapshot — immutable card production
- **Package**: Structured report — menggabungkan multiple artifacts menjadi laporan
- **Validator**: Quality assurance — determinism, range, completeness checks
- **Consumer**: Downstream interface — API untuk layer berikutnya atau Dashboard
- Dashboard TIDAK melakukan analisis — hanya menggabungkan report packages dari semua layer
- One file per layer (market.py, truth.py, structure.py, etc.)
- One file per worker (data_worker.py, knowledge_worker.py, etc.)
- Shared utilities in core.py (decimal, canonical, hash, PRNG, WIB)
- Clear import hierarchy — no circular imports
- Each module exposes a single public API surface
- Internal helpers prefixed with `_`

---

## 3. LIGHTWEIGHT

- No frameworks (no Django, no Flask, no FastAPI)
- No ORM — raw SQLite queries only
- No external dependencies beyond Python stdlib + sqlite3
- Target: entire system < 10,000 lines of Python
- Target: startup < 1 second
- Target: memory < 500 MB

---

## 4. SQLITE ONLY

- sqlite3 from Python stdlib
- PRAGMA foreign_keys = ON at every connection
- WAL mode for concurrent read/write
- Parameterized queries only — no string concatenation
- Single writer pattern (serial writes from main thread)
- Workers do NOT open SQLite connections

---

## 5. PYTHON ONLY

- Python 3.10+
- Type hints on all public functions
- Dataclasses for data structures
- Enum for constrained values (status, kind, phase)
- No async unless required for worker communication
- Standard library only (sqlite3, json, hashlib, struct, math, enum, dataclasses, typing, unittest, multiprocessing)

---

## 6. NO HIDDEN LOGIC

- Every computation must have a specification reference in docstring
- Every decision must produce a card (immutable record)
- Every value must have a traceable source
- No magic numbers — use CONFIG constants
- No implicit defaults — explicit is better
- All edge cases must be handled (NULL, WARMUP, INSUFFICIENT_DATA)

---

## 7. NO CIRCULAR DEPENDENCY

- Imports must form a DAG (Directed Acyclic Graph)
- Layer A can import Layer B only if A is downstream of B
- core.py has zero internal dependencies
- config.py only depends on core.py
- market.py only depends on core.py + config.py
- truth.py only depends on core.py + config.py + market.py
- And so on, following the pipeline order

---

## 8. TYPE SAFE

- Type hints on ALL public function signatures
- TypedDict or dataclass for all data structures
- Enum for all constrained string values
- Optional[T] for nullable fields
- Union types for variant returns
- mypy --strict must pass

---

## 9. EASY AUDIT

- Every module has a docstring with specification reference
- Every function has a docstring with input/output contract
- Every card has checksum + lineage
- Every SQLite write is logged (implicit via triggers)
- Self-test suite in audit.py covers all domains
- Determinism verifiable: 2 runs with same seed = identical

---

## 10. RESOURCE FRIENDLY

- Target VPS: 1.5 GB RAM, 1 vCPU
- Workers are cold (spawned on demand, terminated after)
- No persistent processes (except main pipeline)
- Indexed queries only — no full table scans
- Result set limits (default 10,000 rows)
- Memory: stream large results, don't buffer

---

## 11. PULL REQUEST WORKFLOW

- One PR per build phase
- Branch: `build/phase-XX`
- PR title: `[ST-LMS] Phase-XX: Component Name`
- All tests must pass before PR
- No merge without review
- Use stlms-github MCP for PR creation
- After merge, proceed to next phase

---

## 12. NAMING CONVENTION

- Files: `snake_case.py` (truth_layer.py, cage_engine.py)
- Classes: `PascalCase` (PointBuilder, CageEngine)
- Functions: `snake_case` (compute_atr, build_wave)
- Constants: `UPPER_SNAKE_CASE` (ATR_PERIOD, ST_MULTIPLIER)
- Private: `_prefix` (_resolve_wall, _compute_bands)
- Test files: `test_<module>.py` (test_truth_layer.py)

---

## 13. ERROR HANDLING

- No swallowed exceptions — log and propagate
- ValidationError for invalid inputs
- ConstraintError for SQLite constraint violations
- WarmupError for operations during WARMUP state
- InsufficientDataError for missing required data
- All errors produce audit log entries

---

## 14. TESTING

- Unit tests per module (test_<module>.py)
- Integration tests per phase (test_integration_phase_XX.py)
- Determinism tests (test_determinism.py)
- SQLite tests (test_sqlite.py)
- All tests must pass before phase gate
- Test coverage target: > 90%

---

## 15. DOCUMENTATION

- Every file: module docstring with specification reference
- Every public function: docstring with Parameters/Returns/Raises
- Every class: docstring with purpose and usage
- Every constant: comment with source specification section
- README.md updated per phase
- No TODO comments — complete or don't commit

---

## 16. REFINEMENT IMPLEMENTATION RULES

Refinements are implementation enrichments within existing layers. They do NOT create new layers, phases, or SQLite tables.

| Rule | Description |
|------|-------------|
| WITHIN LAYER | Implement refinement in its designated layer only |
| NO NEW PHASE | Do not create separate build phases for refinements |
| NO NEW TABLE | Use existing SQLite columns or payload_json for refinement data |
| NO NEW PIPELINE | Refinements execute within existing pipeline stages |
| NO OVERRIDE | Refinements enrich — they do not override existing logic |
| EXISTING OUTPUT | Refinements use existing snapshot fields where available |
| PAYLOAD JSON | New refinement data stored in existing payload_json columns |
| SPEC REFERENCE | Every refinement must reference a specification section |

### Refinement Implementation Locations

| Refinement | File | Function/Class |
|-----------|------|---------------|
| Present Dimension | truth.py | PointBuilder.build() — ensure all W fields populated |
| Past Dimension | bag.py | Grouper, Academy — historical artifact access |
| Future Dimension | prediction.py | Summarizer — empirical_win_rate only |
| Character Dimension | bag.py | BehaviorAnalyzer — behavior_profile output |
| Trading Truth | clone.py, trade.py | dirObserve, mkEntry, mkExit |
| Entry Truth | trade.py | mkEntry — reason, sl, tp mandatory |
| Position Truth | position.py | update — mae, mfe, hold_c tracking |
| Exit Truth | trade.py | mkExit — reason, net, result mandatory |
| Market Intelligence | knowledge.py | HiveMind.synth — intelligence_score, bias |
| Living Market State | market.py, truth.py | Per-candle snapshot pipeline |
| Market Character | bag.py | BehaviorAnalyzer — 6 profile types |
| Market Biography | bag.py | SequenceAnalyzer — wave/cage/trade sequences |
| Compression Maturity | bag.py | MaturityAssessor — cage compression scoring |
| Supertrend Snapshot | truth.py | PointBuilder — st, stDir, color |
| MTF Report | evidence.py | mtfSector — wave to MTF mapping |
| W%R Integration | truth.py, evidence.py | PointBuilder (wpr), exitBus (exit-only) |
| Market Timeline | knowledge.py | River — chronicle append |
| Expensive Data | bag.py | Classifier — bag_kind=risk |
| Critical Data | audit.py | AuditLogger — severity levels |
| Recommendation | knowledge.py | Darwin.propose — TIGHTEN_ENTRY, TIGHTEN_WRONG |
