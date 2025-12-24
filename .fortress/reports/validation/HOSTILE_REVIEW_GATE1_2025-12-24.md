# HOSTILE_VALIDATOR Report — Gate 1 Architecture

> **Date**: 2025-12-24
> **Scope**: Architecture (Gate 1)
> **Reviewer**: HOSTILE_VALIDATOR
> **Document**: docs/architecture/ARCHITECTURE.md

---

## VERDICT: CONDITIONAL_GO

The architecture is **fundamentally sound** but has **12 issues** that must be addressed before Gate 2.

- **Critical (P0)**: 2 issues — Must fix immediately
- **Major (P1)**: 5 issues — Must fix before Gate 2
- **Minor (P2)**: 5 issues — Can fix during implementation

---

## 1. Specification Verification

### SPEC_ID Coverage

| Range | Description | Status | Issue |
|:------|:------------|:-------|:------|
| S001-S009 | Core Layer | PASS | Fully specified |
| S010-S019 | CLI Layer | PARTIAL | Commands listed, not fully specified |
| S020-S026 | PyPI Client | PASS | Well documented |
| S027-S032 | npm Client | PARTIAL | Less detail than PyPI |
| S033-S039 | crates.io Client | PASS | Includes User-Agent requirement |
| S040-S049 | Cache Layer | PASS | Two-tier design clear |
| S050-S059 | Patterns Layer | PASS | Pattern types documented |

### Issues Found

**P1-SPEC-001**: CLI Layer (S010-S019) not fully specified
- Commands listed but no argument validation, error handling, or output format specified
- **Required**: Add CLI specification in Gate 2

**P2-SPEC-002**: npm Client has less detail than PyPI
- Missing specific endpoint paths for downloads
- **Required**: Add during implementation

---

## 2. Invariant Verification

### INV_ID Coverage

| INV_ID | Statement | Enforceable? | Issue |
|:-------|:----------|:-------------|:------|
| INV001 | risk_score in [0,1] | YES | But normalization unclear |
| INV002 | signals never None | YES | Type system |
| INV003 | cached = uncached | YES | Integration test |
| INV004 | batch contains all | YES | Set equality |
| INV005 | fail_fast stops | YES | Order check |
| INV006 | returns PackageRisk | YES | mypy |
| INV007 | extract_signals pure | YES | No I/O |
| INV008 | pattern_match valid | YES | Type check |
| INV009 | threshold in (0,1) | YES | assert |
| INV010 | higher risk = higher score | UNCLEAR | Needs definition |
| INV011 | thresholds ordered | YES | Unit test |
| INV012 | aggregate preserves | YES | Count check |
| INV013-018 | Various | YES | Testable |

### Issues Found

**P0-INV-001**: Scoring algorithm normalization undefined
- S007 uses additive points (+40, -30, etc.) but must return [0,1]
- How are points normalized? Min/max? Sigmoid? Clamping?
- **CRITICAL**: Without this, INV001 cannot be enforced
- **Required**: Define normalization formula explicitly

**P1-INV-002**: INV010 "higher risk = higher score" is ambiguous
- What constitutes "higher risk"? More signals? Worse signals?
- Monotonicity needs precise definition for property testing
- **Required**: Define partial ordering on signals

---

## 3. Performance Verification

### Budget Analysis

| Operation | Budget | Achievable? | Issue |
|:----------|:-------|:------------|:------|
| validate_package (uncached) | <200ms | YES | Network dependent |
| validate_package (cached) | <10ms | MAYBE | SQLite is blocking |
| batch_validate (50) | <5s | YES | With concurrency |
| pattern_match | <1ms | YES | String ops |
| cache_get | <0.5ms | MAYBE | SQLite issue |

### Issues Found

**P0-INV-003**: SQLite is blocking, not async
- Architecture states "async-first" (ADR-002)
- Standard `sqlite3` is synchronous
- `<10ms` cached lookup may fail if SQLite blocks
- **CRITICAL**: Either use `aiosqlite` or run in executor
- **Required**: Specify async SQLite strategy

**P1-PERF-001**: pypistats.org is separate from PyPI
- Not owned by PyPI, could have different rate limits
- Could be unavailable when PyPI is available
- **Required**: Make download stats optional, not blocking

---

## 4. Design Gap Analysis

### Missing Specifications

**P1-DESIGN-001**: Error types not defined
- `ValidationError` and `RegistryError` mentioned but not in data structures
- Need exception hierarchy for proper error handling
- **Required**: Add error types to Section 4

**P1-DESIGN-002**: Popular packages source undefined
- `detect_typosquat` needs `popular_packages: set[str]`
- Where does this set come from? How is it updated?
- **Required**: Specify popular packages data source

**P2-DESIGN-003**: Cache key includes `version_hash`
- But version isn't known at validation time
- Key format: `{registry}:{package_name}:{version_hash}`
- **Required**: Clarify cache key strategy

**P2-DESIGN-004**: Pattern database update mechanism missing
- Built-in patterns are static
- How do user/community patterns get added at runtime?
- **Required**: Specify pattern update API

**P2-DESIGN-005**: Rate limiting mechanism unspecified
- Concurrency limit is 10, but how is it enforced?
- Need semaphore or similar mechanism
- **Required**: Specify rate limiting implementation

---

## 5. Security Scan

### Vulnerabilities: NONE FOUND

The security section is well-considered:
- No shell execution
- HTTPS only
- Input validation specified
- Minimal dependencies

### Observations

- Good: API responses validated against schema
- Good: Timeout on all requests
- Good: No arbitrary file access

---

## 6. Consistency Check

### Internal Consistency Issues

**P2-CONS-001**: NOT_FOUND handling inconsistent
- `Recommendation` enum has `NOT_FOUND`
- But also appears in `ValidationResult.not_found: tuple[str, ...]`
- Is NOT_FOUND a recommendation or a separate category?
- **Required**: Clarify NOT_FOUND semantics

---

## Required Actions

| Priority | Issue ID | Description | Deadline |
|:---------|:---------|:------------|:---------|
| **P0** | P0-INV-001 | Define score normalization formula | Before Gate 2 |
| **P0** | P0-INV-003 | Specify async SQLite strategy | Before Gate 2 |
| **P1** | P1-SPEC-001 | Add CLI specification | Gate 2 |
| **P1** | P1-INV-002 | Define signal ordering | Gate 2 |
| **P1** | P1-PERF-001 | Make pypistats optional | Gate 2 |
| **P1** | P1-DESIGN-001 | Add error type definitions | Gate 2 |
| **P1** | P1-DESIGN-002 | Specify popular packages source | Gate 2 |
| **P2** | P2-SPEC-002 | Complete npm client details | Implementation |
| **P2** | P2-DESIGN-003 | Clarify cache key format | Implementation |
| **P2** | P2-DESIGN-004 | Specify pattern update API | Implementation |
| **P2** | P2-DESIGN-005 | Specify rate limiting | Implementation |
| **P2** | P2-CONS-001 | Clarify NOT_FOUND semantics | Implementation |

---

## Strengths Noted

Despite the issues, the architecture has significant strengths:

1. **Comprehensive SPEC_ID coverage** — Every component traced
2. **Clear performance budgets** — Measurable targets
3. **Good invariant registry** — 18 invariants defined
4. **Solid ADRs** — Decisions documented with rationale
5. **Appropriate technology choices** — Python, httpx, asyncio
6. **Security-conscious design** — No obvious vulnerabilities
7. **Memory budgets defined** — Resource limits clear

---

## Remediation Plan

### Immediate (Before Gate 1 can close)

1. **Add scoring normalization to S007**:
```python
def calculate_risk_score(signals: list[Signal]) -> float:
    """
    Raw score range: [-100, +160]
    Normalization: (raw + 100) / 260, clamped to [0, 1]
    """
```

2. **Add async SQLite note to ADR-003**:
```markdown
#### Implementation Note
Use `aiosqlite` for async SQLite access, or run blocking
operations in `asyncio.to_thread()` executor.
```

### Gate 2 (Required before specification)

3. Add error type definitions
4. Specify popular packages data source
5. Complete CLI specification
6. Make pypistats.org optional

---

## Sign-off

**HOSTILE_VALIDATOR**: CONDITIONAL_GO

**Conditions**:
1. P0 issues must be fixed in ARCHITECTURE.md
2. P1 issues must be addressed in Gate 2 specification
3. P2 issues tracked for implementation

**Date**: 2025-12-24

---

*HOSTILE_VALIDATOR: The architecture that ships is the architecture that survives attack.*
