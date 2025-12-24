---
name: release
description: Release management workflow. Use before version releases to validate readiness, generate changelog, and publish to PyPI.
---

# GATE 6: RELEASE — RELEASE_GUARDIAN PROTOCOL

> **Agent**: RELEASE_GUARDIAN
> **Gate**: 6 of 6
> **Authority**: **FINAL SIGN-OFF** — Can block release
> **Output**: Release artifacts, CHANGELOG.md, published package

---

## RELEASE_GUARDIAN MANDATE

```
┌────────────────────────────────────────────────────────────────────┐
│                     RELEASE_GUARDIAN                               │
│                                                                    │
│  YOU ARE THE LAST LINE OF DEFENSE.                                 │
│                                                                    │
│  Once released, it's out there. Forever.                           │
│  There is no "oops, let me fix that" in production.                │
│  There is no "we'll patch it tomorrow."                            │
│                                                                    │
│  IF YOU'RE NOT 100% CONFIDENT, DON'T RELEASE.                      │
└────────────────────────────────────────────────────────────────────┘
```

---

## INVOCATION

```
/release prepare    # Prepare release (checks, changelog)
/release validate   # Final validation
/release publish    # Publish to PyPI
/release rollback   # Emergency rollback procedures
```

---

## RELEASE PREPARATION

### Step 1: Pre-Release Checklist

```markdown
## PRE-RELEASE CHECKLIST

### Gate Completion
- [ ] Gate 1 (Architecture) COMPLETE
- [ ] Gate 2 (Specification) COMPLETE
- [ ] Gate 3 (Test Design) COMPLETE
- [ ] Gate 4 (Planning) COMPLETE
- [ ] Gate 5 (Validation) COMPLETE with GO verdict

### Documentation
- [ ] README.md accurate and up-to-date
- [ ] CHANGELOG.md has all changes since last release
- [ ] API documentation generated
- [ ] Installation instructions tested
- [ ] Examples work (`python -m doctest README.md`)

### Testing
- [ ] Full test suite passes
- [ ] Coverage meets targets (90%+ line)
- [ ] Property tests run (10k iterations minimum)
- [ ] Integration tests with live APIs pass
- [ ] Benchmarks recorded

### Security
- [ ] `pip-audit` clean (no known vulnerabilities)
- [ ] No secrets in codebase
- [ ] Dependencies pinned to specific versions

### Versioning
- [ ] Version bumped correctly (semver)
- [ ] Breaking changes documented if major bump
- [ ] Deprecation warnings added for breaking changes
```

---

### Step 2: Generate Changelog

```markdown
# CHANGELOG.md

## [0.1.0] - YYYY-MM-DD

### Added
- Core detection engine for slopsquatting attacks
- PyPI registry client with caching
- npm registry client with caching
- crates.io registry client with caching
- CLI tool: `phantom-guard check requirements.txt`
- Pre-commit hook integration
- Risk scoring based on multiple signals

### Security Signals Detected
- Package age (< 30 days = suspicious)
- Download count (< 100 = suspicious)
- No source repository link
- Maintainer with no other packages
- Name matches hallucination patterns

### Technical Details
- Async HTTP with httpx
- Local SQLite cache for offline mode
- Typer CLI framework
- Pydantic for validation
- 90%+ test coverage

### Known Limitations
- PyPI only in this release (npm/crates in 0.2.0)
- English language patterns only
- Requires Python 3.11+

### Breaking Changes
- N/A (initial release)

---

## [Unreleased]

### Added
### Changed
### Deprecated
### Removed
### Fixed
### Security
```

---

### Step 3: Final Validation

Run complete validation suite:

```bash
# 1. Clean install test
pip install -e . --force-reinstall

# 2. Full test suite
pytest --cov=phantom_guard --cov-report=html

# 3. Type check
mypy src/ --strict

# 4. Lint check
ruff check src/
ruff format --check src/

# 5. Security audit
pip-audit

# 6. Build check
python -m build

# 7. Install from wheel
pip install dist/*.whl --force-reinstall

# 8. Smoke test
phantom-guard --version
phantom-guard check --help
echo "flask" | phantom-guard check -
```

---

### Step 4: External Review (Optional but Recommended)

```markdown
## EXTERNAL REVIEW CHECKLIST

- [ ] Code review by someone outside the project
- [ ] Security review by security-focused person
- [ ] UX review of CLI by target user
- [ ] Documentation review for clarity

### Review Feedback
[Document any external feedback received]

### Actions Taken
[Document actions taken based on feedback]
```

---

## RELEASE VALIDATION

### Final Verification

```markdown
## RELEASE VALIDATION

### Package Metadata
- Name: phantom-guard
- Version: X.Y.Z
- Author: [author]
- License: MIT
- Python requires: >=3.11

### Test Results
| Suite | Passed | Failed | Skipped |
|:------|:-------|:-------|:--------|
| Unit | X | 0 | 0 |
| Property | X | 0 | 0 |
| Integration | X | 0 | 0 |
| **Total** | X | 0 | 0 |

### Coverage
| Metric | Value | Target | Status |
|:-------|:------|:-------|:-------|
| Line | X% | 90% | ✅ |
| Branch | X% | 85% | ✅ |

### Performance
| Benchmark | Value | Budget | Status |
|:----------|:------|:-------|:-------|
| validate_pkg | Xms | 200ms | ✅ |
| batch_50 | Xs | 5s | ✅ |

### Security
- pip-audit: CLEAN
- Secrets scan: CLEAN
- Dependency check: CLEAN

### Build Artifacts
- [ ] Source distribution built
- [ ] Wheel built
- [ ] Both install correctly
- [ ] CLI works after install
```

---

## RELEASE PUBLISH

### Publishing Procedure

```bash
# 1. Ensure clean git state
git status  # Should be clean

# 2. Tag the release
git tag -a v0.1.0 -m "Release v0.1.0"

# 3. Push tag
git push origin v0.1.0

# 4. Build distributions
python -m build

# 5. Upload to PyPI (use trusted publishing if configured)
python -m twine upload dist/*

# 6. Verify on PyPI
pip install phantom-guard==0.1.0

# 7. Test installed package
phantom-guard --version
```

---

### Post-Release Checklist

```markdown
## POST-RELEASE CHECKLIST

- [ ] Package visible on PyPI
- [ ] `pip install phantom-guard` works
- [ ] GitHub release created
- [ ] Announcement posted (HN, Reddit, Twitter)
- [ ] Documentation updated
- [ ] Next version milestone created

### Links
- PyPI: https://pypi.org/project/phantom-guard/
- GitHub: https://github.com/[owner]/phantom-guard/releases/tag/v0.1.0
```

---

## ROLLBACK PROCEDURES

If critical issue discovered post-release:

```markdown
## EMERGENCY ROLLBACK

### Step 1: Assess Severity
- Security vulnerability → YANK IMMEDIATELY
- Critical bug → YANK + PATCH RELEASE
- Non-critical → PATCH RELEASE ONLY

### Step 2: Yank Release (if needed)
```bash
# This removes the release from PyPI index
# Users with pinned version can still download
twine yank phantom-guard 0.1.0
```

### Step 3: Communicate
- Post issue on GitHub
- Tweet about the problem
- Email known users (if applicable)

### Step 4: Fix and Re-release
- Create hotfix branch
- Fix issue with tests
- Run full validation
- Release as 0.1.1

### Rollback Reason Log
| Date | Version | Reason | Action |
|:-----|:--------|:-------|:-------|
| YYYY-MM-DD | 0.1.0 | [reason] | YANKED + 0.1.1 |
```

---

## GATE 6 EXIT CRITERIA

Release is complete when:

- [ ] Package published to PyPI
- [ ] GitHub release created
- [ ] CHANGELOG updated
- [ ] Documentation deployed
- [ ] Announcement made
- [ ] Next version planned

---

## RECORDING RELEASE

```markdown
# .fortress/gates/GATE_6_RELEASE.md

## Gate 6: Release v0.1.0 — COMPLETE

**Date**: YYYY-MM-DD
**Version**: 0.1.0
**Approver**: RELEASE_GUARDIAN

### Summary
- First public release
- Core detection engine
- PyPI client
- CLI tool

### Metrics
- Test coverage: X%
- Performance: within budget
- Security: clean

### Links
- PyPI: [link]
- GitHub: [link]

### Next Version
- 0.2.0: npm + crates.io support
```

---

## VERSION NUMBERING

Follow Semantic Versioning (semver):

```
MAJOR.MINOR.PATCH

MAJOR: Breaking API changes
MINOR: New features, backwards compatible
PATCH: Bug fixes, backwards compatible
```

### Pre-release Versions

```
0.1.0-alpha.1  # Alpha testing
0.1.0-beta.1   # Beta testing
0.1.0-rc.1     # Release candidate
0.1.0          # Stable release
```

---

*RELEASE_GUARDIAN: Because "it works on my machine" is not a shipping criteria.*
