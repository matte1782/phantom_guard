# HOSTILE_VALIDATOR Report — Week 9 Planning

> **Date**: 2026-01-06
> **Scope**: Week 9 Day-by-Day Planning (VS Code Extension)
> **Reviewer**: HOSTILE_VALIDATOR
> **Documents Reviewed**: docs/planning/week_9/DAY_0_PREP.md through DAY_6.md
> **Revision**: v2 (P1 fixes applied)

---

## VERDICT: GO

---

## Executive Summary

Week 9 planning documents provide a comprehensive day-by-day breakdown for implementing the VS Code Extension (S120-S126). All SPECs are covered, security considerations are appropriately prioritized, and test traces are present.

**P1 issues RESOLVED:**
- P1-HOUR-001: Fixed by creating DAY_0_PREP.md for scaffold work (2-3h prep day)
- P1-TEST-001: Fixed by updating all test stubs from jest to vitest

All blocking issues addressed. Plan is approved for implementation.

---

## 1. SPEC Coverage Verification

| SPEC_ID | Description | Day | Hours Planned | Tests Traced | Status |
|:--------|:------------|:----|:--------------|:-------------|:-------|
| S120 | Extension activation | Day 1 | 2h (reduced) | T120.01-T120.04 | PASS |
| S121 | Diagnostic provider | Day 2 | 6h | T121.01-T121.05 | PASS |
| S122 | Hover provider | Day 3 | 4h | T122.01-T122.03 | PASS |
| S123 | Code action provider | Day 3 | 4h | T123.01-T123.02 | PASS |
| S124 | Status bar | Day 4 | 3h | T124.01-T124.02 | PASS |
| S125 | Configuration | Day 4 | 3h | T125.01-T125.02 | PASS |
| S126 | Core integration | Day 1 | 4h (reduced) | T126.01-T126.04 | PASS |

**All 7 SPECs covered.**

---

## 2. Invariant Coverage Verification

| INV_ID | Statement | Day | Explicitly Addressed | Status |
|:-------|:----------|:----|:---------------------|:-------|
| INV120 | Never blocks UI thread | Day 1 | Code shows async/await | PASS |
| INV121 | 500ms activation timeout | Day 1 | Timeout wrapper shown | PASS |
| INV122 | Clear diagnostics on close | Day 2 | onDocumentClose handler | PASS |
| INV123 | Null on non-package lines | Day 3 | getPackageAtPosition returns null | PASS |
| INV124 | Only phantom-guard diagnostics | Day 3 | source === 'phantom-guard' check | PASS |
| INV125 | Most recent validation result | Day 4 | update() method | PASS |
| INV126 | Config change triggers revalidate | Day 4 | onConfigChange event | PASS |
| INV127 | Graceful spawn error | Day 1 | try/catch with null return | PASS |
| INV128 | No shell injection | Day 1 | execFile + regex | PASS |

**All 9 invariants addressed.**

---

## 3. Test Count Verification

| Source | Total Tests | Status |
|:-------|:------------|:-------|
| TEST_MATRIX_V0.2.0 (S120-S126) | 89 | Target |
| Explicit in Day Plans | 22 | Documented |
| Test Stubs Created | 62+ | In vscode/tests/*.test.ts |

**Gap**: Day plans mention only 22 tests explicitly (T120.01-T126.04). The remaining 67 tests are in the stubs but not explicitly planned for which day they'll be implemented.

---

## 4. Hour Budget Verification

### ROADMAP_V0.2.0 Allocation:

| Task | SPEC | ROADMAP Hours |
|:-----|:-----|:--------------|
| W9.1 | S120 | 6 |
| W9.2 | S121 | 6 |
| W9.3 | S122 | 4 |
| W9.4 | S123 | 4 |
| W9.5 | S124, S125 | 4 |
| W9.6 | S126 | 6 |
| W9.7 | Integration | 8 |
| Buffer | - | 10 |
| **Total** | | **48** |

### Week 9 Day Plan Allocation (REVISED):

| Day | Focus | Hours |
|:----|:------|:------|
| Day 0 (Prep) | Project scaffold | 2-3 |
| Day 1 | W9.1 + W9.6 | 8 |
| Day 2 | W9.2 | 6 |
| Day 3 | W9.3 + W9.4 | 8 |
| Day 4 | W9.5 | 6 |
| Day 5 | W9.7 Part 1 | 8 |
| Day 6 | W9.7 Part 2 + Review | 8 |
| **Total** | | **46-47** |
| **Buffer** | | **1-2** |

**Finding**: Day 0 prep day now handles scaffold setup, allowing Day 1 to focus on W9.1 (4h) + W9.6 (4h) = 8h. **RESOLVED**.

---

## 5. Security Verification

| Requirement | Day | Implementation | Status |
|:------------|:----|:---------------|:-------|
| Shell injection prevention | Day 1 | execFile + PACKAGE_NAME_REGEX | PASS |
| Package name validation | Day 1 | SHELL_METACHARACTERS check | PASS |
| No shell interpolation | Day 1 | Array args to execFile | PASS |
| Security tests traced | Day 1 | T126.02, T126.03 explicit | PASS |

**Security considerations appropriately prioritized in Day 1.**

---

## 6. Issues Found

### P1 — Critical (RESOLVED)

| ID | Issue | Resolution | Status |
|:---|:------|:-----------|:-------|
| P1-HOUR-001 | Day 1 severely under-budgeted | Created DAY_0_PREP.md for scaffold work | **FIXED** |
| P1-TEST-001 | Test framework mismatch | Updated all test stubs to use vitest imports | **FIXED** |

### P2 — Important (Should fix)

| ID | Issue | Impact | Required Action |
|:---|:------|:-------|:----------------|
| P2-TEST-002 | Only 22/89 tests explicitly scheduled | Unclear test implementation plan | Add test count targets to Day 5/6 acceptance criteria |
| P2-ERROR-001 | Error types not explicitly scheduled | Missing error.ts implementation | Add to Day 1 scaffold or Day 2 |
| P2-TYPES-001 | types.ts not explicitly scheduled | Missing type definitions | Add to Day 1 scaffold |

### P3 — Minor (Track)

| ID | Issue | Impact |
|:---|:------|:-------|
| P3-DOC-001 | README.md for extension not planned | Missing user documentation |
| P3-ICON-001 | Extension icon not mentioned | Marketplace requirement |

---

## 7. Risk Assessment

| Risk | Likelihood | Impact | Mitigation in Plan |
|:-----|:-----------|:-------|:-------------------|
| Day 1 overrun | LOW | Schedule slip | Day 0 prep handles scaffold |
| Test framework confusion | LOW | Test failures | Standardized on vitest |
| Integration test flakiness | MEDIUM | CI failures | Day 5/6 has retry strategy |
| Security vulnerability | LOW | Critical | Day 1 prioritizes security |

---

## 8. Required Actions Before GO

### Immediate (Before implementation starts): **ALL COMPLETE**

1. **P1-HOUR-001**: ✅ Created DAY_0_PREP.md with scaffold work (2-3h prep day)

2. **P1-TEST-001**: ✅ Updated all 7 test files to use vitest imports

### Before Day 5 (Testing phase):

3. **P2-TEST-002**: Add to Day 5/6:
   - "Exit Criteria: 62+ unit tests passing"
   - "Exit Criteria: 22+ integration tests passing"

4. **P2-ERROR-001, P2-TYPES-001**: ✅ DAY_0_PREP.md includes errors.ts and types.ts

---

## 9. Positive Findings

1. **Security-first approach**: Core integration (W9.6) with security focus on Day 1
2. **Clear invariant mapping**: Each day references specific INV_IDs
3. **Test stubs ready**: 62+ test stubs already exist in vscode/tests/
4. **Dependency awareness**: Days correctly identify prerequisites
5. **TDD workflow**: Each day includes "Tests to Enable" section
6. **Commit templates**: Each day includes proper commit message format

---

## 10. Final Approval

### Conditions for GO: **ALL MET**

- [x] Resolve P1-HOUR-001: Created DAY_0_PREP.md
- [x] Resolve P1-TEST-001: Updated test stubs to vitest

### Implementation Ready:

1. ✅ P1 issues resolved
2. ✅ Final review complete
3. **BEGIN IMPLEMENTATION** - Start with Day 0 prep

---

## Sign-off

**HOSTILE_VALIDATOR**: GO

**Date**: 2026-01-06

**Verdict**: Week 9 planning is APPROVED. All P1 issues resolved. Implementation may begin.

**Re-review required**: NO

---

*HOSTILE_VALIDATOR: The plan that ships is the plan that's been attacked.*
