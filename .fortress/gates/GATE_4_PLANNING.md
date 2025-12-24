# Gate 4: Planning — COMPLETE

> **Date**: 2025-12-24
> **Approver**: PLANNER
> **Verdict**: GO
> **Output**: docs/planning/ROADMAP.md

---

## Summary

Complete development roadmap created for Phantom Guard with 24 traced tasks across 4 weeks. Every task links to SPEC_IDs, INV_IDs, and TEST_IDs.

### Schedule

| Phase | Weeks | Hours | Focus |
|:------|:------|:------|:------|
| Core Engine | 1 | 40 | Types, scoring, patterns |
| Registry Clients | 2 | 40 | PyPI, npm, crates, cache |
| CLI & Integration | 3 | 40 | Commands, batch, output |
| Polish & Release | 4 | 40 | Perf, docs, PyPI release |
| **Total** | **4** | **160** | MVP Release |

---

## Task Inventory

| Category | Tasks | Hours |
|:---------|:------|:------|
| Core Implementation | 6 | 32 |
| Registry Clients | 5 | 32 |
| CLI Interface | 6 | 32 |
| Polish & Release | 7 | 32 |
| Buffer (20%) | - | 32 |
| **Total** | **24** | **160** |

---

## Critical Path

```
W1.1 → W1.5 → W1.6 → W2.1 → W2.4 → W3.1 → W3.6 → W4.6 → W4.7
```

Critical path duration: ~50 hours (excluding buffer)

---

## Trace Coverage

| Element | Count | Traced |
|:--------|:------|:-------|
| SPEC_IDs | 59 | 100% |
| INV_IDs | 22 | 100% |
| TEST_IDs | 258 | 100% |
| Tasks | 24 | 100% |

---

## Risk Summary

| Risk Level | Count | Mitigation |
|:-----------|:------|:-----------|
| HIGH | 3 | External APIs - heavy mocking |
| MEDIUM | 3 | Algorithm/concurrency - property tests |
| LOW | 18 | Standard patterns |

---

## Design Principles (Simplicity Focus)

1. **One Command**: `phantom-guard validate <pkg>` does everything
2. **Zero Config**: Works immediately after pip install
3. **CI/CD Ready**: Exit codes, JSON output, pre-commit support
4. **Fast**: <200ms per package, batch processing

---

## Artifacts

| Artifact | Location |
|:---------|:---------|
| Development Roadmap | docs/planning/ROADMAP.md |
| This Gate Record | .fortress/gates/GATE_4_PLANNING.md |

---

## Next Steps

1. Run `/hostile-review planning` for validation
2. Begin `/implement W1.1` for first task
3. Follow TDD cycle for each task

---

*Gate 4 is about PLANNING what to build. Implementation follows the traced tasks.*
