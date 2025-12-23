# Roadmap Audit: Phantom Guard

**Date**: 2025-12-23
**Objective**: Identify feasibility issues, over-engineering risks, and optimize for user value

---

## Executive Summary

**Current Plan**: 90 days, 7 phases, extensive feature set
**Recommended Plan**: 21 days, 3 focused phases, ship-then-iterate

**Key Finding**: The current roadmap is over-engineered. We're building features before validating the core delivers value.

---

## Part 1: What Exists vs What's Planned

### Already Built (60% of Core)

| Component | Status | Quality |
|-----------|--------|---------|
| `types.py` | Complete | Good - frozen dataclasses |
| `scorer.py` | Complete | Good - simple additive scoring |
| `patterns.py` | Complete | Good - 10 patterns, regex |
| `detector.py` | Complete | Good - async, concurrent |
| `base.py` | Complete | Good - validation, error handling |
| `pypi.py` | Complete | Good - full implementation |
| `npm.py` | Stub | Needs implementation |
| `crates.py` | Stub | Needs implementation |
| CLI | Missing | Not started |
| Tests | Skipped | Framework ready, tests not wired |

### Roadmap Alignment Issues

| Planned | Reality |
|---------|---------|
| P1: 18 days for "Core Detection Engine" | Core is already 60% done, needs ~3 days |
| P2: 14 days for CLI | CLI is simple, needs ~4 days max |
| P3: 14 days for Caching | Premature optimization - skip for MVP |
| P4: 14 days for GitHub Action | Nice-to-have, not MVP critical |
| P5: 14 days for Hooks | Post-MVP feature |
| P6-P7: 13 days hardening/release | Too much time, 5 days sufficient |

**Total bloat**: 77 days of planned work that doesn't deliver user value.

---

## Part 2: Over-Engineering Risks

### CRITICAL ISSUES

#### 1. Caching Before Validation
```
Current: Phase 3 dedicates 14 days to caching
Problem: We don't know if performance is a problem yet
Reality: 50 packages in <5 seconds works without caching (validated in TECHNICAL_VALIDATION.md)
Action: DELETE Phase 3 from MVP
```

#### 2. Three Registries Before One Works
```
Current: Build PyPI, npm, crates.io in parallel
Problem: npm/crates.io have different APIs, different issues
Reality: 80%+ of users are Python developers checking requirements.txt
Action: MVP = PyPI only. Add npm in v0.2.0, crates.io in v0.3.0
```

#### 3. GitHub Action Before CLI Adoption
```
Current: Phase 4 builds GitHub Action before anyone uses CLI
Problem: No feedback on core product before building integrations
Reality: GitHub Action is a distribution channel, not the product
Action: CLI first. GitHub Action after 100+ PyPI downloads.
```

#### 4. Hooks Before Product-Market Fit
```
Current: Phase 5 builds pip/npm hooks
Problem: Hooks are complex, platform-specific, high maintenance
Reality: <1% of potential users want automatic interception
Action: DELETE from v0.1.0 entirely. Consider for v1.0.0.
```

### MEDIUM ISSUES

#### 5. Too Many File Parsers
```
Current: requirements.txt, package.json, pyproject.toml, Cargo.toml
Problem: Each parser has edge cases, takes time
Reality: requirements.txt covers 90% of use cases
Action: MVP = requirements.txt only. Others are 30-minute additions.
```

#### 6. Over-Specified Data Models
```
Current: PackageMetadata has 9 fields
Reality: Only 5 are used by scorer (exists, release_count, has_repository, has_author, has_description)
Risk: Low - frozen dataclasses are fine
Action: Keep as-is, but don't add more fields without need
```

---

## Part 3: What Users Actually Need

### User Journey Analysis

```
User has AI-generated code with:
  import flask
  from flask_gpt_helper import something  # <-- This doesn't exist

User wants to:
  1. Check if their dependencies are real
  2. Get a clear YES/NO answer
  3. Maybe understand why something is flagged

User does NOT want to:
  - Configure complex settings
  - Set up GitHub Actions
  - Install pip hooks
  - Wait for caching to warm up
```

### Minimum Viable Product

```bash
# This is the ONLY thing MVP needs to do:
$ pip install phantom-guard
$ phantom-guard check requirements.txt

Checking 15 packages...

✓ flask (safe)
✓ requests (safe)
✗ flask-gpt-helper (NOT FOUND - likely hallucinated)
⚠ gpt4-api (suspicious: 3 releases, no repository)

RESULT: 2 packages blocked/flagged. Review before installing.
```

That's it. Everything else is scope creep.

---

## Part 4: Optimized 21-Day Plan

### Week 1: Core Works (Days 1-7)

**Goal**: All critical path tests pass with real API calls

| Day | Task | Exit Criteria |
|-----|------|---------------|
| 1 | Wire scorer to detector | `detector.check_package("flask")` returns SAFE |
| 2 | Enable critical tests | 12 critical tests pass (not skipped) |
| 3 | Integration test with PyPI | Real API calls work for flask, requests, numpy |
| 4 | Test hallucination patterns | flask-gpt-helper detected as suspicious |
| 5 | Test non-existent packages | fake-package-xyz blocked |
| 6 | Error handling tests | Timeouts, malformed JSON handled |
| 7 | **HOSTILE REVIEW** | Security audit of core |

**Deliverable**: Core detection engine verified to work correctly.

### Week 2: CLI Works (Days 8-14)

**Goal**: `phantom-guard check requirements.txt` works end-to-end

| Day | Task | Exit Criteria |
|-----|------|---------------|
| 8 | CLI skeleton (Typer) | `phantom-guard --version` works |
| 9 | `check` command | Reads file, calls detector |
| 10 | requirements.txt parser | Parses pins, extras, comments |
| 11 | Pretty output (Rich) | Colors, tables, clear verdicts |
| 12 | JSON output | `--json` flag produces valid JSON |
| 13 | Error messages | Clear errors for file not found, network issues |
| 14 | **HOSTILE REVIEW** | CLI security, UX review |

**Deliverable**: Usable CLI tool.

### Week 3: Ship (Days 15-21)

**Goal**: Available on PyPI, documented, announced

| Day | Task | Exit Criteria |
|-----|------|---------------|
| 15 | README polish | Clear install, usage, examples |
| 16 | CHANGELOG, version bump | v0.1.0 ready |
| 17 | Build & TestPyPI | Installs from TestPyPI |
| 18 | Production PyPI | `pip install phantom-guard` works |
| 19 | GitHub release | Tag, release notes, badges |
| 20 | Launch posts | HN, Reddit, Twitter drafts |
| 21 | **LAUNCH** | Posts published, monitoring |

**Deliverable**: Public v0.1.0 release.

---

## Part 5: What to Cut

### DELETE from v0.1.0

| Feature | Reason | When to Add |
|---------|--------|-------------|
| npm registry support | Focus, PyPI covers 80% of users | v0.2.0 |
| crates.io support | Even smaller market | v0.3.0 |
| SQLite caching | Premature optimization | v0.2.0 if needed |
| In-memory caching | Premature optimization | v0.2.0 if needed |
| GitHub Action | Distribution, not product | v0.2.0 |
| pip hooks | Complex, low demand | v1.0.0 |
| npm hooks | Complex, low demand | v1.0.0 |
| pyproject.toml parser | 30-min addition later | v0.1.1 |
| package.json parser | npm not supported yet | v0.2.0 |
| Cargo.toml parser | crates.io not supported yet | v0.3.0 |
| Configuration file | Not needed for MVP | v0.2.0 |

### KEEP in v0.1.0

| Feature | Reason |
|---------|--------|
| PyPI detection | Core value prop |
| Risk scoring | Core value prop |
| Hallucination patterns | Key differentiator |
| CLI check command | Primary interface |
| requirements.txt parser | Primary use case |
| JSON output | Automation-friendly |
| Pretty terminal output | Good UX |

---

## Part 6: Traps to Avoid

### Technical Traps

| Trap | Why It's Tempting | Reality |
|------|-------------------|---------|
| "Let's add npm support" | More market! | Different API, different bugs, 2x work |
| "We need caching" | Performance! | 50 packages in 5s is fine |
| "GitHub Action first" | Automation! | No one uses a tool they haven't tried |
| "More patterns!" | Better detection! | 10 patterns is enough for MVP |
| "Type every function" | Quality! | Strict mypy on tests wastes time |

### Process Traps

| Trap | Why It's Tempting | Reality |
|------|-------------------|---------|
| "90-day roadmap" | Thorough planning! | 21 days or we never ship |
| "7 phases" | Organized! | 3 phases: Build, Polish, Ship |
| "Hostile review every phase" | Quality! | 2 reviews: after core, before ship |
| "Perfect documentation" | Professional! | README + examples is enough |
| "Wait for feature X" | Completeness! | Ship now, iterate later |

### Psychological Traps

| Trap | Why It's Tempting | Reality |
|------|-------------------|---------|
| "But competitors..." | Fear of losing | Window is open, ship fast |
| "Just one more feature" | Perfectionism | MVP means minimum |
| "It's not ready" | Imposter syndrome | It works, ship it |
| "What if it fails" | Risk aversion | Failure = feedback |

---

## Part 7: Decision Matrix

### Should We Build This for MVP?

```
Does it help users detect hallucinated packages?
├── YES → Is it essential for the core loop?
│   ├── YES → BUILD IT
│   └── NO  → ADD TO v0.2.0 BACKLOG
└── NO  → DELETE FROM ROADMAP
```

### Applied to Current Features

| Feature | Helps Detection? | Essential? | Verdict |
|---------|------------------|------------|---------|
| PyPI client | YES | YES | BUILD |
| Risk scorer | YES | YES | BUILD |
| Pattern matcher | YES | YES | BUILD |
| CLI check | YES | YES | BUILD |
| requirements.txt parser | YES | YES | BUILD |
| JSON output | YES | NO | BUILD (trivial) |
| npm client | YES | NO | v0.2.0 |
| Caching | NO | NO | v0.2.0 |
| GitHub Action | NO | NO | v0.2.0 |
| Hooks | NO | NO | v1.0.0 |

---

## Part 8: Recommended Next Steps

### Immediate (Today)

1. **Accept this analysis** or challenge specific points
2. **Commit to 21-day timeline** or propose alternative
3. **Delete cut features** from mental roadmap

### Week 1 Start

1. Write ONE integration test that calls real PyPI
2. Make it pass
3. Repeat for each critical path

### Success Metrics

| Metric | Target | Why |
|--------|--------|-----|
| Days to PyPI release | ≤21 | Speed to market |
| Critical tests passing | 12/12 | Quality gate |
| False positive rate | <5% | User trust |
| Real projects tested | 5+ | Validation |
| Lines of code | <2000 | Simplicity |

---

## Conclusion

**Current roadmap**: Well-intentioned but over-engineered. 90 days of work for a product that could ship in 21.

**Recommended action**:
1. Adopt 21-day plan
2. Cut npm, crates.io, caching, GitHub Action, hooks from v0.1.0
3. Ship to PyPI in 3 weeks
4. Iterate based on real user feedback

**The best roadmap is the one that gets a working product into users' hands fastest.**
