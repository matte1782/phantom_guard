# Gate 0: Problem Definition — COMPLETE

> **Date**: 2025-12-22
> **Approver**: Research Fortress v7
> **Output**: PROJECT_FOUNDATION.md, docs/PROBLEM_STATEMENT.md

---

## Summary

Phantom Guard addresses **slopsquatting** — a new attack vector where AI coding assistants hallucinate package names that attackers register with malware.

### Problem Statement

AI tools hallucinate package names at a 20% rate. No tool specifically detects these phantom packages before installation.

### Success Criteria

1. **False Positive Rate**: <5%
2. **True Positive Rate**: >95%
3. **Detection Latency**: <200ms per package
4. **Adoption**: 5K+ GitHub stars (6 months)
5. **Revenue**: $500K ARR (12 months)

### Anti-Goals

- Not a general SCA tool (Snyk exists)
- Not a CVE database
- Not an SBOM solution (Endor Labs has $188M)
- Not an IDE plugin initially

### Key Assumptions

| Assumption | Validation |
|:-----------|:-----------|
| AI patterns are consistent | Test multiple AI tools |
| Attackers register phantoms | Monitor PyPI |
| Developers will install tool | User research |
| Registry APIs stable | Monthly validation |

---

## Research Backing

**Source**: Research Fortress v7
- 7 iterations
- 40+ domains analyzed
- 40+ web searches
- Score: 51/55 (WINNER)

**Competitive Window**: 12-18 months before VC-funded competition

---

## Artifacts

| Artifact | Location |
|:---------|:---------|
| Original Research | PROJECT_FOUNDATION.md |
| Problem Statement | docs/PROBLEM_STATEMENT.md |
| Framework Config | .fortress/FORTRESS.md |

---

## Next Gate

**Gate 1: Architecture**

Command: `/architect`

Required outputs:
- docs/architecture/ARCHITECTURE.md
- Invariant registry
- Performance budget
- SPEC_ID assignments
