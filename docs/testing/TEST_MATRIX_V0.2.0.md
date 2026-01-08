# Phantom Guard — Test Matrix v0.2.0

> **Version**: 0.2.0
> **Date**: 2026-01-04
> **Gate**: 3 of 6 - Test Design
> **Status**: STUBS CREATED
> **Base**: Extends TEST_MATRIX.md (v0.1.0)

---

## 1. New Test Inventory Summary (v0.2.0 Additions)

| Category | v0.1.0 | v0.2.0 New | Total | Status |
|:---------|:-------|:-----------|:------|:-------|
| Unit Tests | 145 | 201 | 346 | STUBS |
| Property Tests | 15 | 6 | 21 | STUBS |
| Fuzz Tests | 5 | 5 | 10 | STUBS |
| Integration Tests | 29 | 47 | 76 | STUBS |
| Benchmarks | 10 | 6 | 16 | STUBS |
| Security Tests | 0 | 4 | 4 | STUBS |
| **TOTAL** | **204** | **269** | **473** | STUBS |

---

## 2. New SPEC_ID to Test Matrix (v0.2.0)

### 2.1 GitHub Action (S100-S106)

| SPEC_ID | Description | Unit | Property | Fuzz | Integration | Bench | Security | Total | Status |
|:--------|:------------|:-----|:---------|:-----|:------------|:------|:---------|:------|:-------|
| S100 | Entry point | 8 | 0 | 0 | 8 | 1 | 0 | 17 | STUBS |
| S101 | File discovery | 14 | 0 | 0 | 6 | 0 | 0 | 20 | STUBS |
| S102 | Package extractor | 15 | 0 | 2 | 5 | 1 | 0 | 23 | STUBS |
| S103 | Validation orchestrator | 3 | 0 | 0 | 2 | 1 | 0 | 6 | STUBS |
| S104 | PR comment generator | 12 | 0 | 0 | 7 | 0 | 0 | 19 | STUBS |
| S105 | SARIF generator | 12 | 0 | 0 | 5 | 0 | 0 | 17 | STUBS |
| S106 | Exit code handler | 10 | 0 | 0 | 4 | 0 | 0 | 14 | STUBS |
| **Subtotal** | | **74** | **0** | **2** | **37** | **3** | **0** | **116** | |

### 2.2 VS Code Extension (S120-S126)

| SPEC_ID | Description | Unit | Property | Fuzz | Integration | Bench | Security | Total | Status |
|:--------|:------------|:-----|:---------|:-----|:------------|:------|:---------|:------|:-------|
| S120 | Extension activation | 8 | 0 | 0 | 8 | 1 | 0 | 17 | STUBS |
| S121 | Diagnostic provider | 14 | 0 | 0 | 4 | 0 | 0 | 18 | STUBS |
| S122 | Hover provider | 10 | 0 | 0 | 1 | 0 | 0 | 11 | STUBS |
| S123 | Code action provider | 8 | 0 | 0 | 2 | 0 | 0 | 10 | STUBS |
| S124 | Status bar | 6 | 0 | 0 | 2 | 0 | 0 | 8 | STUBS |
| S125 | Configuration | 8 | 0 | 0 | 2 | 0 | 0 | 10 | STUBS |
| S126 | Core integration | 8 | 0 | 1 | 3 | 1 | 2 | 15 | STUBS |
| **Subtotal** | | **62** | **0** | **1** | **22** | **2** | **2** | **89** | |

### 2.3 New Detection Signals (S060-S080)

| SPEC_ID | Description | Unit | Property | Fuzz | Integration | Bench | Security | Total | Status |
|:--------|:------------|:-----|:---------|:-----|:------------|:------|:---------|:------|:-------|
| S060 | Namespace squatting | 12 | 2 | 0 | 0 | 0 | 0 | 14 | STUBS |
| S065 | Download inflation | 10 | 2 | 1 | 0 | 0 | 0 | 13 | STUBS |
| S070 | Ownership transfer | 8 | 1 | 0 | 0 | 0 | 0 | 9 | STUBS |
| S075 | Version spike | 12 | 1 | 1 | 0 | 0 | 0 | 14 | STUBS |
| S080 | Signal combinations | 7 | 0 | 0 | 0 | 1 | 0 | 8 | STUBS |
| **Subtotal** | | **49** | **6** | **2** | **0** | **1** | **0** | **58** | |

### 2.4 Pattern Database (S058-S059)

| SPEC_ID | Description | Unit | Property | Fuzz | Integration | Bench | Security | Total | Status |
|:--------|:------------|:-----|:---------|:-----|:------------|:------|:---------|:------|:-------|
| S058 | Community patterns | 10 | 0 | 0 | 5 | 0 | 2 | 17 | STUBS |
| S059 | Pattern validation | 6 | 0 | 0 | 3 | 0 | 0 | 9 | STUBS |
| **Subtotal** | | **16** | **0** | **0** | **8** | **0** | **2** | **26** | |

---

## 3. New Invariant to Test Matrix (v0.2.0)

| INV_ID | Statement | Test Type | Test File | Status |
|:-------|:----------|:----------|:----------|:-------|
| INV058 | Pattern database never modifies user config | unit | test_patterns_community.py | STUB |
| INV058a | Community pattern load < 100ms | bench | test_patterns_community.py | STUB |
| INV059 | Invalid patterns rejected during load, not at runtime | unit | test_patterns_validate.py | STUB |
| INV059a | All patterns have 0.0 ≤ confidence ≤ 1.0 | unit | test_patterns_validate.py | STUB |
| INV060 | Namespace signal weight ≤ 0.25 | proptest | test_signals_namespace.py | STUB |
| INV061 | Verified scopes skip API check entirely | unit | test_signals_namespace.py | STUB |
| INV062 | Unknown scope defaults to 0.0 weight | unit | test_signals_namespace.py | STUB |
| INV065 | Download signal weight ≤ 0.20 | proptest | test_signals_downloads.py | STUB |
| INV066 | Libraries.io fallback used when PyPI unavailable | unit | test_signals_downloads.py | STUB |
| INV067 | No weight contribution if data unavailable | unit | test_signals_downloads.py | STUB |
| INV070 | Ownership signal weight ≤ 0.15 | proptest | test_signals_ownership.py | STUB |
| INV071 | Missing history defaults to safe (0.0) | unit | test_signals_ownership.py | STUB |
| INV072 | Recent transfers only count within 90 days | unit | test_signals_ownership.py | STUB |
| INV075 | Version spike weight ≤ 0.20 | proptest | test_signals_versions.py | STUB |
| INV076 | CI/CD packages exempt from spike detection | unit | test_signals_versions.py | STUB |
| INV077 | Legitimate rapid release patterns excluded | unit | test_signals_versions.py | STUB |
| INV100 | GitHub Action runs to completion without uncaught exceptions | unit | index.test.ts | STUB |
| INV101 | All exit codes are in set {0, 1, 2, 3, 4, 5} | unit | exit.test.ts | STUB |
| INV102 | SARIF output always valid | integration | sarif.test.ts | STUB |
| INV103 | Package list extracted deterministically | unit | extract.test.ts | STUB |
| INV104 | Validation batch completes in < 30s OR times out gracefully | integration | validate.test.ts | STUB |
| INV105 | PR comment length never exceeds 65535 characters | unit | comment.test.ts | STUB |
| INV106 | Existing Phantom Guard comment updated, not duplicated | integration | comment.test.ts | STUB |
| INV107 | SARIF version is always "2.1.0" | unit | sarif.test.ts | STUB |
| INV108 | Exit code deterministic for same input | unit | exit.test.ts | STUB |
| INV120 | Extension never blocks UI thread (all I/O is async) | integration | extension.test.ts | STUB |
| INV121 | Activation completes within 500ms or times out gracefully | integration | extension.test.ts | STUB |
| INV122 | Diagnostics are cleared when document is closed | unit | diagnostics.test.ts | STUB |
| INV123 | Hover provider returns null on non-package lines | unit | hover.test.ts | STUB |
| INV124 | Code actions only appear for Phantom Guard diagnostics | unit | actions.test.ts | STUB |
| INV125 | Status bar reflects most recent validation result | unit | statusbar.test.ts | STUB |
| INV126 | Configuration changes trigger re-validation of open documents | integration | config.test.ts | STUB |
| INV127 | Core integration fails gracefully on subprocess spawn error | unit | core.test.ts | STUB |
| INV128 | No shell injection via package names | security | core.test.ts | STUB |

---

## 4. New Edge Case to Test Matrix (v0.2.0)

| EC_ID Range | Category | Count | Test File | Status |
|:------------|:---------|:------|:----------|:-------|
| EC200-EC215 | GitHub Action file discovery | 16 | files.test.ts | STUB |
| EC220-EC235 | GitHub Action package extraction | 16 | extract.test.ts | STUB |
| EC240-EC255 | GitHub Action PR comments | 16 | comment.test.ts | STUB |
| EC260-EC270 | GitHub Action SARIF output | 11 | sarif.test.ts | STUB |
| EC300-EC315 | VS Code activation | 16 | extension.test.ts | STUB |
| EC320-EC335 | VS Code diagnostics | 16 | diagnostics.test.ts | STUB |
| EC340-EC350 | VS Code hover | 11 | hover.test.ts | STUB |
| EC400-EC415 | Namespace squatting | 16 | test_signals_namespace.py | STUB |
| EC420-EC435 | Download inflation | 16 | test_signals_downloads.py | STUB |
| EC440-EC455 | Ownership transfer | 16 | test_signals_ownership.py | STUB |
| EC460-EC475 | Version spike | 16 | test_signals_versions.py | STUB |
| EC480-EC495 | Community patterns | 16 | test_patterns_community.py | STUB |
| EC500-EC510 | Signal combinations | 11 | test_signals_combination.py | STUB |

---

## 5. New Test File Registry (v0.2.0)

### 5.1 Python Unit Tests

| File | SPEC_IDs | Test Count | Status |
|:-----|:---------|:-----------|:-------|
| tests/unit/test_signals_namespace.py | S060 | 12 | STUBS |
| tests/unit/test_signals_downloads.py | S065 | 10 | STUBS |
| tests/unit/test_signals_ownership.py | S070 | 8 | STUBS |
| tests/unit/test_signals_versions.py | S075 | 12 | STUBS |
| tests/unit/test_signals_combination.py | S080 | 7 | STUBS |
| tests/unit/test_patterns_community.py | S058 | 10 | STUBS |
| tests/unit/test_patterns_validate.py | S059 | 6 | STUBS |

### 5.2 TypeScript Unit Tests (GitHub Action)

| File | SPEC_IDs | Test Count | Status |
|:-----|:---------|:-----------|:-------|
| action/tests/index.test.ts | S100 | 8 | STUBS |
| action/tests/files.test.ts | S101 | 14 | STUBS |
| action/tests/extract.test.ts | S102 | 15 | STUBS |
| action/tests/validate.test.ts | S103 | 3 | STUBS |
| action/tests/comment.test.ts | S104 | 12 | STUBS |
| action/tests/sarif.test.ts | S105 | 12 | STUBS |
| action/tests/exit.test.ts | S106 | 10 | STUBS |

### 5.3 TypeScript Unit Tests (VS Code Extension)

| File | SPEC_IDs | Test Count | Status |
|:-----|:---------|:-----------|:-------|
| vscode/tests/extension.test.ts | S120 | 8 | STUBS |
| vscode/tests/diagnostics.test.ts | S121 | 14 | STUBS |
| vscode/tests/hover.test.ts | S122 | 10 | STUBS |
| vscode/tests/actions.test.ts | S123 | 8 | STUBS |
| vscode/tests/statusbar.test.ts | S124 | 6 | STUBS |
| vscode/tests/config.test.ts | S125 | 8 | STUBS |
| vscode/tests/core.test.ts | S126 | 8 | STUBS |

---

## 6. Security Test Registry

| TEST_ID | SPEC_ID | INV_ID | Attack Vector | Test File | Status |
|:--------|:-------|:-------|:--------------|:----------|:-------|
| T126.02 | S126 | INV128 | Shell injection via package name | core.test.ts | STUB |
| T126.03 | S126 | INV128 | Command injection validation | core.test.ts | STUB |
| T058.04 | S058 | - | Malicious pattern file | test_patterns_community.py | STUB |
| T058.05 | S058 | - | Signature verification | test_patterns_community.py | STUB |

---

## 7. Coverage Targets (v0.2.0 Updated)

| Metric | Target | Minimum | Current | Status |
|:-------|:-------|:--------|:--------|:-------|
| Line coverage (Python) | 90% | 85% | 0% | STUBS ONLY |
| Line coverage (TypeScript) | 90% | 85% | 0% | STUBS ONLY |
| Branch coverage | 85% | 80% | 0% | STUBS ONLY |
| SPEC coverage | 100% | 100% | 100% | STUBS ONLY |
| Property tests | 10,000 cases | 1,000 | 0 | STUBS ONLY |
| Fuzz duration | 1 hour | 10 min | 0 | STUBS ONLY |

---

## 8. Test Commands (v0.2.0)

```bash
# === Python Tests ===

# Run all Python tests
pytest tests/

# Run v0.2.0 signal tests
pytest tests/unit/test_signals_*.py

# Run v0.2.0 pattern tests
pytest tests/unit/test_patterns_*.py

# Run with coverage
pytest --cov=phantom_guard --cov-report=html

# Collect all tests (verify stubs compile)
pytest --collect-only


# === TypeScript Tests (GitHub Action) ===

# Navigate to action directory
cd action

# Install dependencies
npm install

# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Collect tests only
npx jest --listTests


# === TypeScript Tests (VS Code Extension) ===

# Navigate to vscode directory
cd vscode

# Install dependencies
npm install

# Run all tests
npm test

# Run integration tests
npm run test:integration
```

---

## 9. Test Stub Compilation Verification

```bash
# Python: Should complete without errors
pytest --collect-only tests/unit/test_signals_*.py tests/unit/test_patterns_*.py

# Expected: ~65 tests collected (all skipped)


# GitHub Action: Should complete without errors
cd action && npx jest --listTests

# Expected: 7 test files listed


# VS Code Extension: Should complete without errors
cd vscode && npx jest --listTests

# Expected: 7 test files listed
```

---

## 10. TDD Workflow (v0.2.0)

During Gate 4-5 implementation:

```
1. Pick a test stub from this matrix
2. For Python: Remove @pytest.mark.skip
   For TypeScript: Remove it.skip → it
3. Run test → MUST FAIL (Red)
4. Write minimal code to pass
5. Run test → MUST PASS (Green)
6. Refactor if needed
7. Update this matrix (Status → COMPLETE)
8. Commit with trace: IMPLEMENTS: SXXX, TESTS: TXXX.YY
```

---

## 11. Trace Links (v0.2.0 Additions)

| SPEC_ID | INV_IDs | EC_IDs | TEST_IDs | Code Location |
|:--------|:--------|:-------|:---------|:--------------|
| S058 | INV058, INV058a | EC480-EC495 | T058.* | phantom_guard/patterns/community.py |
| S059 | INV059, INV059a | EC483-EC488 | T059.* | phantom_guard/patterns/validator.py |
| S060 | INV060-INV062 | EC400-EC415 | T060.* | phantom_guard/signals/namespace.py |
| S065 | INV065-INV067 | EC420-EC435 | T065.* | phantom_guard/signals/downloads.py |
| S070 | INV070-INV072 | EC440-EC455 | T070.* | phantom_guard/signals/ownership.py |
| S075 | INV075-INV077 | EC460-EC475 | T075.* | phantom_guard/signals/versions.py |
| S080 | - | EC500-EC510 | T080.* | phantom_guard/signals/combination.py |
| S100 | INV100 | - | T100.* | action/src/index.ts |
| S101 | - | EC200-EC215 | T101.* | action/src/files.ts |
| S102 | INV103 | EC220-EC235 | T102.* | action/src/extract.ts |
| S103 | INV104 | - | T103.* | action/src/validate.ts |
| S104 | INV105, INV106 | EC240-EC255 | T104.* | action/src/comment.ts |
| S105 | INV102, INV107 | EC260-EC270 | T105.* | action/src/sarif.ts |
| S106 | INV101, INV108 | - | T106.* | action/src/exit.ts |
| S120 | INV120, INV121 | EC300-EC315 | T120.* | vscode/src/extension.ts |
| S121 | INV122 | EC320-EC335 | T121.* | vscode/src/diagnostics.ts |
| S122 | INV123 | EC340-EC350 | T122.* | vscode/src/hover.ts |
| S123 | INV124 | - | T123.* | vscode/src/actions.ts |
| S124 | INV125 | - | T124.* | vscode/src/statusbar.ts |
| S125 | INV126 | - | T125.* | vscode/src/config.ts |
| S126 | INV127, INV128 | - | T126.* | vscode/src/core.ts |

---

## Appendix A: P0 Fixes Applied from Gate 2

| Issue ID | Description | Resolution |
|:---------|:------------|:-----------|
| P0-INV-001 | INV104 timeout inconsistency | Fixed: batch <30s, 60s circuit breaker |
| P0-EC-001 | Missing signal combination edge cases | Added EC500-EC510 |

---

**Gate 3 Status**: STUBS COMPLETE

**Total New Tests**: 269 test stubs created

**Test Files Created**: 21 new files (7 Python, 7 TypeScript Action, 7 TypeScript VS Code)

**Next Step**: Run stub compilation verification, then hostile review

**Next Gate**: Gate 4 (Planning) after TEST_ARCHITECT approval
