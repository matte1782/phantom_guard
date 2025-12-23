---
name: phantom:master
description: Master engineering principles and command index for Phantom Guard. Use at session start to understand project context, commands, and quality gates.
---

# Phantom Guard Engineering Command System

> **Project**: phantom-guard - Slopsquatting Detection for AI-Generated Code
> **Name Status**: AVAILABLE on PyPI, npm, GitHub
> **Version**: 0.0.0 (Pre-Development)

---

## Command Index

Execute these commands by running the skill with the specified name.

### Phase 1: Planning & Architecture

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/phantom:roadmap` | View/update development roadmap | Start of each session |
| `/phantom:architect` | Design system architecture | Before implementing features |
| `/phantom:spec` | Write technical specifications | Before coding a component |

### Phase 2: Implementation

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/phantom:implement` | Guided implementation workflow | When building features |
| `/phantom:checkpoint` | Save progress, validate state | After completing a unit of work |
| `/phantom:debug` | Structured debugging workflow | When stuck or tests fail |

### Phase 3: Quality Assurance

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/phantom:test` | Run and analyze tests | After implementation |
| `/phantom:hostile-review` | **CRITICAL**: Adversarial code review | Before ANY merge/commit |
| `/phantom:security-audit` | Security-focused review | Before release |

### Phase 4: Release

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/phantom:release-check` | Pre-release validation | Before version bump |
| `/phantom:changelog` | Generate changelog | Before release |
| `/phantom:publish` | Publish to PyPI/npm | Release time |

### Monitoring

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/phantom:competitive-watch` | Scan for competition | Weekly |
| `/phantom:validate-technical` | Revalidate technical approach | Monthly |

---

## Engineering Principles

### 1. Hostile-First Development

Every significant change MUST pass hostile review before commit:
- No exceptions for "simple" changes
- Reviewer actively tries to break the code
- Document all attack vectors considered

### 2. MVP Focus

The goal is SHIP, not PERFECT:
- 90-day MVP deadline is sacred
- Cut scope, not quality
- Features require justification against roadmap

### 3. Detection Accuracy Priority

False positives kill adoption:
- Target <5% false positive rate
- Every heuristic must be tested against real-world packages
- User overrides must be trivial

### 4. Performance Budget

Real-time validation requires speed:
- Single package check: <200ms
- Full requirements.txt (50 packages): <5s concurrent
- No network = graceful degradation

---

## Project Status Tracking

### Current Phase: PRE-MVP

```
[x] Research Complete (Fortress v7)
[x] Technical Validation (APIs tested)
[x] Competitive Scan (Window closing - accelerate)
[ ] Architecture Design
[ ] Core Detection Engine
[ ] CLI Tool
[ ] Package Hooks
[ ] GitHub Action
[ ] v0.1.0 Release
```

### Risk Register

| Risk | Status | Mitigation |
|------|--------|------------|
| SlopGuard ships PyPI support | MONITOR | Differentiate on UX/speed |
| Endor Labs adds detection | MONITOR | OSS vs Enterprise positioning |
| High false positive rate | TESTING | Extensive real-world validation |
| Rate limiting by registries | MITIGATED | Caching layer planned |

---

## Quality Gates

### Before ANY Commit

1. All tests pass
2. No new type errors
3. Hostile review completed (for significant changes)
4. Documentation updated

### Before PR Merge

1. CI passes
2. Coverage maintained or improved
3. Hostile review documented
4. Changelog entry added

### Before Release

1. Full hostile review
2. Security audit
3. Performance benchmarks
4. Real-world testing on 5+ projects

---

## Session Start Checklist

Every development session should begin with:

1. Run `/phantom:roadmap` - Know where we are
2. Check TODO.md - What's the immediate priority?
3. Review last hostile review - Any unaddressed issues?
4. Verify tests pass - Clean starting state

---

## File Structure

```
phantom-guard/
├── .claude/
│   ├── skills/           # Command definitions
│   │   ├── 00-master.md  # This file
│   │   ├── 01-architect.md
│   │   ├── 02-implement.md
│   │   ├── 03-test.md
│   │   ├── 04-hostile-review.md
│   │   └── 05-release.md
│   ├── rules/            # Engineering rules
│   └── settings.local.json
├── docs/
│   ├── ROADMAP.md        # Living roadmap
│   ├── ARCHITECTURE.md   # System design
│   └── HOSTILE_REVIEWS/  # Review history
├── src/phantom_guard/    # Main package
├── tests/                # Test suite
├── research-output/      # Research artifacts
└── PROJECT_FOUNDATION.md # Original research
```
