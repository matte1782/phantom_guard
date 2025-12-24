# Gate 1: Architecture — COMPLETE

> **Date**: 2025-12-24
> **Approver**: HOSTILE_VALIDATOR
> **Verdict**: CONDITIONAL_GO (P0 fixes applied)
> **Output**: docs/architecture/ARCHITECTURE.md

---

## Summary

System architecture designed for Phantom Guard slopsquatting detection library. Architecture follows async-first, layered design with comprehensive specification traceability.

### Components Defined

| Layer | SPEC_IDs | Purpose |
|:------|:---------|:--------|
| CLI | S010-S019 | User interface (phantom-guard command) |
| Core | S001-S009 | Detection orchestration, analysis, scoring |
| Registry | S020-S039 | PyPI, npm, crates.io API clients |
| Cache | S040-S049 | Two-tier caching (memory + SQLite) |
| Patterns | S050-S059 | Hallucination pattern matching |

### Key Decisions

| ADR | Decision | Rationale |
|:----|:---------|:----------|
| ADR-001 | Python 3.11+ | Adoption over raw performance |
| ADR-002 | Async-first (asyncio) | I/O concurrency for registry calls |
| ADR-003 | Two-tier cache | Fast reads + persistence |
| ADR-004 | Frozen dataclasses | Immutability for safety |
| ADR-005 | Weighted additive scoring | Interpretable, configurable |

### Invariants Defined

18 invariants defined in registry (INV001-INV018):
- Core safety (risk_score bounds, null checks)
- Performance (timeouts, caching correctness)
- Registry behavior (error handling, headers)
- Cache behavior (TTL, size limits)

---

## Hostile Review Results

**Verdict**: CONDITIONAL_GO

### P0 Issues (Fixed)

| Issue | Description | Resolution |
|:------|:------------|:-----------|
| P0-INV-001 | Score normalization undefined | Added formula: `(raw + 100) / 260` |
| P0-INV-003 | SQLite blocking in async | Added aiosqlite to dependencies |

### P1 Issues (Deferred to Gate 2)

| Issue | Description |
|:------|:------------|
| P1-SPEC-001 | CLI layer not fully specified |
| P1-INV-002 | Signal ordering for INV010 ambiguous |
| P1-PERF-001 | pypistats.org should be optional |
| P1-DESIGN-001 | Error types not defined |
| P1-DESIGN-002 | Popular packages source undefined |

### P2 Issues (Deferred to Implementation)

5 minor issues tracked in hostile review report.

---

## Performance Budgets

| Operation | Budget | Validated |
|:----------|:-------|:----------|
| validate_package (uncached) | <200ms | Yes (TECHNICAL_VALIDATION.md) |
| validate_package (cached) | <10ms | Pending (aiosqlite) |
| batch (50 packages) | <5s | Yes (concurrent) |
| pattern_match | <1ms | Pending |

---

## Artifacts

| Artifact | Location |
|:---------|:---------|
| Architecture Document | docs/architecture/ARCHITECTURE.md |
| Hostile Review Report | .fortress/reports/validation/HOSTILE_REVIEW_GATE1_2025-12-24.md |
| This Gate Record | .fortress/gates/GATE_1_ARCHITECTURE.md |

---

## Next Gate

**Gate 2: Specification**

Command: `/spec`

Required outputs:
- docs/specification/SPECIFICATION.md
- Invariant enforcement details
- Edge case catalog
- Test requirements matrix (SPEC_ID → TEST_ID)

P1 issues from Gate 1 must be addressed in Gate 2.
