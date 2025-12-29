# Week 4: Polish & Release — Overview

> **Status**: PLANNED
> **Duration**: 6 Days
> **Hours**: 40 hours (32 working + 8 buffer)
> **Goal**: Release v0.1.0 to PyPI
> **Prerequisites**: Weeks 1-3 complete, 100% test coverage

---

## Summary

Week 4 focuses on polishing the codebase, ensuring production readiness, and releasing the first public version to PyPI.

### Objectives

1. **Performance**: Validate and optimize for performance budgets
2. **Quality**: False positive prevention with popular packages database
3. **Packaging**: Complete pyproject.toml and build artifacts
4. **Documentation**: Comprehensive README and usage guides
5. **Release**: Final hostile review and PyPI upload

---

## Day-by-Day Schedule

| Day | Task ID | Focus | Hours | Deliverables |
|:----|:--------|:------|:------|:-------------|
| Day 1 | W4.1 | Performance Benchmarks | 6 | Benchmark suite, baseline measurements |
| Day 2 | W4.2 | Performance Optimization | 6 | Optimized patterns, cache, batch |
| Day 3 | W4.3 | Popular Packages Database | 6 | Top 1000 packages per registry |
| Day 4 | W4.4 | Packaging | 6 | pyproject.toml, wheel, sdist |
| Day 5 | W4.5 | Documentation | 6 | README, API docs, guides |
| Day 6 | W4.6 + W4.7 | Hostile Review + Release | 8 | GO verdict, PyPI v0.1.0 |
| Buffer | - | Contingency | 2 | - |
| **Total** | - | - | **40** | - |

---

## Task Details

### W4.1: Performance Benchmarks (Day 1)

**Objective**: Establish comprehensive performance benchmarks

**Deliverables**:
- pytest-benchmark test suite
- P99 latency validation tests
- Memory profiling tests
- CI performance regression tests
- Baseline measurements document

**Performance Budgets**:
| Operation | Budget |
|:----------|:-------|
| Single (cached) | <10ms |
| Single (uncached) | <200ms |
| Batch 50 | <5s |
| Pattern match | <1ms |

---

### W4.2: Performance Optimization (Day 2)

**Objective**: Optimize critical paths to meet budgets

**Deliverables**:
- Pre-compiled regex patterns
- LRU-cached Levenshtein distance
- Optimized MemoryCache with __slots__
- Chunked batch processing
- Updated baseline measurements

---

### W4.3: Popular Packages Database (Day 3)

**Objective**: Prevent false positives on legitimate packages

**Data Sources**:
| Registry | Source |
|:---------|:-------|
| PyPI | hugovk/top-pypi-packages |
| npm | npmjs.com/browse/depended |
| crates.io | crates.io API |

**Deliverables**:
- `src/phantom_guard/data/popular_packages.py`
- Top 1000 packages per registry
- `is_popular()` function
- False positive rate validation (<5%)

---

### W4.4: Packaging (Day 4)

**Objective**: Prepare for PyPI release

**Deliverables**:
- Complete pyproject.toml with all metadata
- LICENSE file (MIT)
- CHANGELOG.md for v0.1.0
- Wheel and sdist builds
- Local installation tests

---

### W4.5: Documentation (Day 5)

**Objective**: Comprehensive user documentation

**Deliverables**:
- README.md with all sections
- docs/USAGE.md usage guide
- docs/API.md Python API reference
- docs/CI_CD.md integration guides
- CONTRIBUTING.md

---

### W4.6 + W4.7: Hostile Review + Release (Day 6)

**Objective**: Validate and release

**Hostile Review Checklist**:
- [ ] All tests passing (835+ tests)
- [ ] Coverage 100%
- [ ] No lint errors
- [ ] No type errors
- [ ] Performance budgets met
- [ ] Security scan clean
- [ ] Documentation complete

**Release Steps**:
1. Final build (wheel + sdist)
2. twine check
3. Upload to PyPI
4. Verify installation
5. Create GitHub release
6. Prepare announcement

---

## Exit Criteria

Before Week 4 is complete:

- [ ] All benchmarks pass performance budget
- [ ] Popular packages list integrated
- [ ] pip install phantom-guard works
- [ ] README complete with examples
- [ ] Hostile review GO verdict
- [ ] Version 0.1.0 released on PyPI

---

## Dependencies

```
W4.1 (Benchmarks)
    │
    ▼
W4.2 (Optimization)
    │
    ▼
W4.3 (Popular Packages) ─────┐
    │                        │
    ▼                        │
W4.4 (Packaging)             │
    │                        │
    ▼                        │
W4.5 (Documentation) ◄───────┘
    │
    ▼
W4.6 + W4.7 (Review + Release)
```

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|:-----|:------------|:-------|:-----------|
| Performance budget missed | Low | High | Profile and optimize |
| PyPI upload issues | Low | Medium | Use TestPyPI first |
| Documentation gaps | Low | Low | Review against checklist |
| Popular packages API down | Medium | Low | Use cached/backup data |

---

## Files to Create/Update

### New Files
- `tests/benchmarks/test_performance_benchmarks.py`
- `tests/benchmarks/test_memory_profile.py`
- `docs/performance/BASELINE_MEASUREMENTS.md`
- `docs/performance/PROFILING_GUIDE.md`
- `src/phantom_guard/data/popular_packages.py`
- `scripts/refresh_popular_packages.py`
- `docs/USAGE.md`
- `docs/API.md`
- `docs/CI_CD.md`
- `CONTRIBUTING.md`

### Updated Files
- `pyproject.toml` - Complete metadata
- `README.md` - Full documentation
- `CHANGELOG.md` - v0.1.0 release notes
- `src/phantom_guard/core/patterns.py` - Optimization
- `src/phantom_guard/core/typosquat.py` - Integration
- `src/phantom_guard/cache/memory.py` - Optimization

---

## Success Metrics

| Metric | Target |
|:-------|:-------|
| Test Coverage | 100% |
| Performance Budget | All met |
| False Positive Rate | <5% |
| Documentation | Complete |
| PyPI Release | v0.1.0 |
| Hostile Review | GO |

---

## Next Phase

After Week 4 completes, Week 5 begins:

**Week 5: Showcase Landing Page**
- Interactive demo website
- Modern UI with animations
- Performance visualization
- Mobile responsive design

---

*Week 4 is about shipping. Quality, polish, and release.*
