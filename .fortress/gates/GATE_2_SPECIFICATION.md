# Gate 2: Specification — COMPLETE

> **Date**: 2025-12-24
> **Approver**: HOSTILE_VALIDATOR (as SPEC_VALIDATOR)
> **Verdict**: GO
> **Output**: docs/specification/SPECIFICATION.md

---

## Summary

Complete specification created for Phantom Guard with full traceability from requirements to test cases.

### Metrics

| Metric | Count |
|:-------|:------|
| Invariants (INV_ID) | 22 |
| Edge Cases (EC_ID) | 85 |
| Test IDs (TEST_ID) | 204 |
| Error Types | 9 |
| Failure Modes | 11 |

### P1 Issues Resolved (from Gate 1)

| Issue ID | Description | Resolution |
|:---------|:------------|:-----------|
| P1-SPEC-001 | CLI not specified | Section 6: Full CLI spec |
| P1-INV-002 | Signal ordering | Section 1.4: Weights defined |
| P1-PERF-001 | pypistats optional | Section 5: Graceful degradation |
| P1-DESIGN-001 | Error types | Section 2: Exception hierarchy |
| P1-DESIGN-002 | Popular packages | Section 4: Data sources |

---

## Specification Highlights

### Invariant Registry

22 invariants covering:
- Core scoring (INV001-INV012)
- Registry clients (INV013-INV018)
- Input validation (INV019-INV022)

All invariants have defined test types (unit, property, integration).

### Edge Case Catalog

85 edge cases organized by category:
- Package name input (15 cases)
- Registry responses (16 cases)
- Risk scoring (16 cases)
- Cache behavior (11 cases)
- CLI behavior (16 cases)
- Pattern matching (11 cases)

### Acceptance Matrix

204 tests planned:
- 145 unit tests
- 15 property tests
- 5 fuzz tests
- 29 integration tests
- 10 benchmarks

### Error Hierarchy

```
PhantomGuardError
├── ValidationError
│   ├── InvalidPackageNameError
│   ├── InvalidRegistryError
│   └── InvalidConfigError
├── RegistryError
│   ├── RegistryTimeoutError
│   ├── RegistryRateLimitError
│   ├── RegistryUnavailableError
│   └── RegistryParseError
├── CacheError
└── PatternError
```

---

## Hostile Review Results

**Verdict**: GO

### P2 Issues Identified (for Gate 3)

| Issue | Description |
|:------|:------------|
| P2-EC-001 | EC_ID numbering gaps |
| P2-EC-002 | Missing npm scoped package cases |
| P2-EC-003 | Boundary condition precision |
| P2-CONS-001 | Registry-specific name rules |
| P2-CONS-002 | Exit code priority |
| P2-CONS-003 | Neutral score precision |

These are minor and will be addressed in Gate 3.

---

## Coverage Targets

| Metric | Target | Minimum |
|:-------|:-------|:--------|
| Line coverage | 90% | 85% |
| Branch coverage | 85% | 80% |
| Property tests | 10,000 | 1,000 |
| Fuzz duration | 1 hour | 10 min |
| Mutation score | 80% | 70% |

---

## Artifacts

| Artifact | Location |
|:---------|:---------|
| Specification Document | docs/specification/SPECIFICATION.md |
| Hostile Review Report | .fortress/reports/validation/HOSTILE_REVIEW_GATE2_2025-12-24.md |
| This Gate Record | .fortress/gates/GATE_2_SPECIFICATION.md |

---

## Next Gate

**Gate 3: Test Design**

Command: `/test`

Required outputs:
- Test stubs for all 204 TEST_IDs
- tests/unit/, tests/integration/, tests/property/ structure
- TEST_MATRIX.md with full test registry
- Pytest configuration

P2 issues from Gate 2 should be addressed in test design.
