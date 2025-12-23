---
name: phantom:release
description: Release management workflow. Use before version releases to validate readiness, generate changelog, and publish to PyPI.
---

# Skill: Release Management

> **Purpose**: Structured release process from pre-release checks to launch
> **Philosophy**: Releases should be boring (predictable, automated)

---

## Release Commands

| Command | Purpose |
|---------|---------|
| `/phantom:release-check` | Validate ready for release |
| `/phantom:changelog` | Generate changelog |
| `/phantom:publish` | Publish to registries |

---

## Pre-Release Checklist

### Code Quality

- [ ] All tests pass
- [ ] Coverage > 80%
- [ ] No type errors (mypy)
- [ ] No lint errors (ruff)
- [ ] No security issues (bandit)

### Documentation

- [ ] README is current
- [ ] CHANGELOG updated
- [ ] API docs generated
- [ ] Migration guide (if breaking changes)

### Testing

- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] E2E tests pass
- [ ] Tested on real projects (5+ minimum)
- [ ] Performance benchmarks acceptable

### Review

- [ ] Hostile review passed
- [ ] Security audit passed
- [ ] All issues from reviews addressed

---

## Version Numbering

We follow [Semantic Versioning](https://semver.org/):

```
MAJOR.MINOR.PATCH

MAJOR: Breaking API changes
MINOR: New features (backward compatible)
PATCH: Bug fixes (backward compatible)
```

### Pre-1.0 Rules

While version < 1.0.0:
- MINOR can include breaking changes
- Focus on rapid iteration
- Clearly document any breaking changes

### Version History Targets

| Version | Focus |
|---------|-------|
| 0.1.0 | MVP - Core detection, CLI |
| 0.2.0 | Enhanced patterns, GitHub Action |
| 0.3.0 | Performance, caching |
| 0.4.0 | Hooks (pip, npm) |
| 0.5.0 | Enterprise features preview |
| 1.0.0 | Stable API, production ready |

---

## Changelog Format

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Added
- New hallucination patterns for AI package names

### Changed
- Improved scoring algorithm accuracy

### Fixed
- False positive on django-rest-framework

## [0.1.0] - 2025-XX-XX

### Added
- Initial release
- Core detection engine for PyPI, npm, crates.io
- CLI tool with `check` command
- Risk scoring with configurable thresholds
- Hallucination pattern matching
- SQLite caching for performance
- JSON output format

### Security
- Input validation for package names
- No shell command execution

[Unreleased]: https://github.com/username/phantom-guard/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/username/phantom-guard/releases/tag/v0.1.0
```

---

## Release Process

### Step 1: Prepare Release Branch

```bash
# Create release branch
git checkout -b release/v0.1.0

# Update version
# Edit pyproject.toml: version = "0.1.0"
# Edit src/phantom_guard/__init__.py: __version__ = "0.1.0"
```

### Step 2: Final Checks

```bash
# Run full test suite
pytest --cov

# Type checking
mypy src/

# Linting
ruff check src/

# Security scan
bandit -r src/

# Build package
python -m build

# Test installation
pip install dist/phantom_guard-0.1.0-py3-none-any.whl
phantom-guard --version
```

### Step 3: Hostile Review

Run `/phantom:hostile-review` with focus on:
- Security vulnerabilities
- Breaking changes
- Missing documentation
- Edge cases

### Step 4: Create Release

```bash
# Commit version bump
git add pyproject.toml src/phantom_guard/__init__.py CHANGELOG.md
git commit -m "Release v0.1.0"

# Merge to main
git checkout main
git merge release/v0.1.0

# Tag release
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin main --tags
```

### Step 5: Publish to PyPI

```bash
# Test PyPI first
twine upload --repository testpypi dist/*

# Verify on TestPyPI
pip install --index-url https://test.pypi.org/simple/ phantom-guard

# Production PyPI
twine upload dist/*
```

### Step 6: GitHub Release

1. Go to GitHub Releases
2. Create new release from tag v0.1.0
3. Add release notes (copy from CHANGELOG)
4. Attach dist files
5. Publish

### Step 7: Announce

- [ ] Hacker News post
- [ ] Reddit r/Python and r/programming
- [ ] Twitter/X thread
- [ ] LinkedIn post
- [ ] Dev.to article (optional)

---

## Launch Posts Templates

### Hacker News

```
Title: Show HN: Phantom Guard – Detect AI-hallucinated package attacks before they compromise your code

Body:
I built Phantom Guard after reading about slopsquatting attacks – where AI coding assistants hallucinate package names that attackers then register with malware.

The tool checks your requirements.txt or package.json against PyPI/npm to detect:
- Non-existent packages (hallucinations)
- Suspiciously new packages
- Packages matching known hallucination patterns

Usage:
  pip install phantom-guard
  phantom-guard check requirements.txt

GitHub: [link]
PyPI: [link]

Technical details:
- Checks package age, download count, repository presence
- <5 second validation for 50 packages
- 0% false positive rate on tested OSS projects
- MIT licensed

Would love feedback, especially from security researchers and teams using AI coding tools.
```

### Twitter/X Thread

```
1/ Introducing Phantom Guard: protect your code from AI hallucination attacks

When AI suggests "pip install flask-redis-helper", how do you know it's real?

Attackers are registering fake package names that AI commonly hallucinates. This is called slopsquatting.

2/ The stats are alarming:
- 20% of AI-generated code references non-existent packages
- Attackers register these phantom names with malware
- One install = compromised

3/ Phantom Guard detects slopsquatting BEFORE you install:

  phantom-guard check requirements.txt

It checks:
✓ Package exists?
✓ Suspiciously new?
✓ Matches hallucination patterns?
✓ Has repository link?

4/ Works with:
- PyPI (Python)
- npm (JavaScript)
- crates.io (Rust)

Validates 50 packages in <5 seconds.
Zero false positives on tested projects.

5/ Get it now:
  pip install phantom-guard

MIT licensed.
GitHub: [link]

Built this as a solo project. Feedback welcome!
```

---

## Post-Release

### Monitor

- [ ] Watch for issues on GitHub
- [ ] Monitor PyPI download stats
- [ ] Check for negative feedback
- [ ] Respond to questions quickly

### Hotfix Process

If critical bug found:

```bash
# Create hotfix branch
git checkout -b hotfix/v0.1.1 v0.1.0

# Fix the bug
# Update version to 0.1.1
# Update CHANGELOG

# Merge and tag
git checkout main
git merge hotfix/v0.1.1
git tag -a v0.1.1 -m "Hotfix v0.1.1"
git push origin main --tags

# Publish
python -m build
twine upload dist/*
```

---

## Rollback Plan

If release has critical issues:

1. **Yank from PyPI** (makes version uninstallable for new users)
   ```bash
   pip install twine
   twine yank phantom-guard 0.1.0 --reason "Critical bug in X"
   ```

2. **GitHub Release** - Mark as pre-release or delete

3. **Communicate** - Post on GitHub issues, Twitter

4. **Hotfix** - Follow hotfix process above
