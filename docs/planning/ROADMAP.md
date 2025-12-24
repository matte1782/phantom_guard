# Phantom Guard — Development Roadmap

> **Version**: 0.1.0
> **Created**: 2025-12-24
> **Last Updated**: 2025-12-24
> **Status**: ACTIVE
> **Gate**: 4 of 6

---

## Overview

### MVP Target
- **Scope**: Core detection + CLI + 3 registries (PyPI, npm, crates.io)
- **Goal**: Simple, pip-installable tool that works in any workflow
- **Showcase**: High-end landing page with interactive demo

### Total Effort
- **Planned**: 5 weeks (compact implementation + showcase)
- **Buffer**: 20% contingency per week
- **Total Tasks**: 32 tasks
- **Total Hours**: ~200 hours (with buffer)

### Design Principles
1. **Simple API**: `phantom-guard validate <package>` - that's it
2. **Zero Config**: Works out of the box
3. **Fast Feedback**: <200ms per package
4. **Easy Integration**: pip install, CI/CD friendly, exit codes

---

## Phase 1: Core Engine (Week 1)

### Goals
- Implement core types and data structures
- Implement risk scoring algorithm
- Implement pattern matching
- All core unit tests passing

### Tasks

| Task | SPEC | Description | Hours | Status |
|:-----|:-----|:------------|:------|:-------|
| W1.1 | S001 | Core types (PackageRisk, Signal, etc.) | 4 | ✅ COMPLETE |
| W1.2 | S004 | Signal extraction logic | 6 | ✅ COMPLETE |
| W1.3 | S005, S050-S059 | Pattern matching engine | 6 | ✅ COMPLETE |
| W1.4 | S006 | Typosquat detection | 6 | ✅ COMPLETE |
| W1.5 | S007-S009 | Risk scoring and thresholds | 6 | ✅ COMPLETE |
| W1.6 | S001-S003 | Detector orchestrator | 4 | ✅ COMPLETE |
| **Buffer** | - | Contingency (20%) | 8 | - |
| **Total** | - | Week 1 | **40** | - |

### Exit Criteria
- [x] All W1.* tasks complete
- [x] T001-T009 unit tests passing (348 tests)
- [x] Property tests for INV001, INV010 passing
- [x] mypy --strict passes
- [x] Coverage ≥90% on core/ (99% achieved)

---

## Phase 2: Registry Clients (Week 2)

### Goals
- Implement all three registry clients
- Implement two-tier cache
- Integration tests with mocked APIs

### Tasks

| Task | SPEC | Description | Hours | Status |
|:-----|:-----|:------------|:------|:-------|
| W2.1 | S020-S026 | PyPI client + pypistats | 8 | PENDING |
| W2.2 | S027-S032 | npm client | 6 | PENDING |
| W2.3 | S033-S039 | crates.io client | 6 | PENDING |
| W2.4 | S040-S049 | Two-tier cache (memory + SQLite) | 8 | PENDING |
| W2.5 | - | Error handling and retries | 4 | PENDING |
| **Buffer** | - | Contingency (20%) | 8 | - |
| **Total** | - | Week 2 | **40** | - |

### Exit Criteria
- [ ] All W2.* tasks complete
- [ ] T020-T050 tests passing
- [ ] Live integration tests passing
- [ ] Cache TTL/LRU tests passing
- [ ] Coverage ≥90% on registry/

---

## Phase 3: CLI & Integration (Week 3)

### Goals
- Implement CLI interface
- End-to-end workflow working
- Batch validation support

### User Experience Focus
- **Beautiful CLI**: ASCII art logo on startup (inspired by Claude Code)
- **Animated Ghost**: Terminal spinner/animation featuring phantom ghost character
- **Clear output**: Color-coded results, progress indicators
- **Helpful errors**: Actionable error messages with suggestions
- **Discoverability**: Rich `--help` with examples

### CLI Branding Concept

> **Full Design Guide**: See `docs/design/BRANDING_GUIDE.md`

```
┌───────────────────────────────────────────────────────────────┐
│                                                               │
│   ▄▀▀▀▀▀▄    PHANTOM GUARD                                   │
│  █  ◉ ◉  █   Supply Chain Security                           │
│  █   ▽   █   v0.1.0                                           │
│   ▀█▀▀▀█▀                                                     │
│                                                               │
└───────────────────────────────────────────────────────────────┘

  👻 Scanning requirements.txt...

  ✓ flask              SAFE         [0.05]
  ✓ requests           SAFE         [0.03]
  ⚠ flask-utils        SUSPICIOUS   [0.42]
  ✗ reqeusts           HIGH_RISK    [0.89]

  ──────────────────────────────────────────────────────────────
  Summary: 4 packages | 2 safe | 1 suspicious | 1 high-risk
  ──────────────────────────────────────────────────────────────

  👻 Completed in 234ms
```

**Technology**: Uses [Rich library](https://github.com/Textualize/rich) for beautiful terminal output

### Tasks

| Task | SPEC | Description | Hours | Status |
|:-----|:-----|:------------|:------|:-------|
| W3.1 | S010-S012 | CLI: validate command + branding | 6 | PENDING |
| W3.2 | S013-S015 | CLI: check command (files) | 6 | PENDING |
| W3.3 | S016-S017 | CLI: cache management | 4 | PENDING |
| W3.4 | S002 | Batch validation (concurrent) | 6 | PENDING |
| W3.5 | S018-S019 | Output formats (text, JSON) | 4 | PENDING |
| W3.6 | - | End-to-end integration | 6 | PENDING |
| **Buffer** | - | Contingency (20%) | 8 | - |
| **Total** | - | Week 3 | **40** | - |

### Exit Criteria
- [ ] All W3.* tasks complete
- [ ] T010-T019 tests passing
- [ ] CLI integration tests passing
- [ ] `phantom-guard validate flask` works
- [ ] `phantom-guard check requirements.txt` works

---

## Phase 4: Polish & Release (Week 4)

### Goals
- Performance optimization
- Documentation
- Package for PyPI release

### Tasks

| Task | SPEC | Description | Hours | Status |
|:-----|:-----|:------------|:------|:-------|
| W4.1 | - | Performance benchmarks | 4 | PENDING |
| W4.2 | - | Performance optimization | 6 | PENDING |
| W4.3 | - | Popular packages list (top 1000) | 4 | PENDING |
| W4.4 | - | pyproject.toml + packaging | 4 | PENDING |
| W4.5 | - | README + usage docs | 4 | PENDING |
| W4.6 | - | Final hostile review | 6 | PENDING |
| W4.7 | - | Release to PyPI | 4 | PENDING |
| **Buffer** | - | Contingency (20%) | 8 | - |
| **Total** | - | Week 4 | **40** | - |

### Exit Criteria
- [ ] All benchmarks pass performance budget
- [ ] pip install phantom-guard works
- [ ] README complete with examples
- [ ] Hostile review GO verdict
- [ ] Version 0.1.0 released

---

## Phase 5: Showcase Landing Page (Week 5)

### Goals
- Build impressive, high-end landing page
- Interactive real-time demo of package validation
- Modern UI/UX with fluid animations
- Modular, maintainable frontend architecture

### Design Philosophy
```
┌─────────────────────────────────────────────────────────────────┐
│                    SHOWCASE PRINCIPLES                          │
├─────────────────────────────────────────────────────────────────┤
│  1. SPEED IS THE FEATURE                                        │
│     - Show <200ms validation in real-time                       │
│     - Animated progress that feels instant                      │
│                                                                 │
│  2. LESS IS MORE                                                │
│     - Minimal UI, maximum impact                                │
│     - Every element serves a purpose                            │
│                                                                 │
│  3. MOTION WITH MEANING                                         │
│     - Animations guide attention                                │
│     - No gratuitous effects                                     │
│                                                                 │
│  4. DEVELOPER-FIRST AESTHETIC                                   │
│     - Dark mode default                                         │
│     - Monospace where it matters                                │
│     - Terminal-inspired interactions                            │
└─────────────────────────────────────────────────────────────────┘
```

### Technical Stack
| Component | Technology | Rationale |
|:----------|:-----------|:----------|
| Framework | Vanilla JS + Web Components | Zero dependencies, fast load |
| Bundler | Vite | Lightning-fast HMR, ESM native |
| Animations | GSAP + CSS | Industry standard, 60fps |
| Styling | CSS Custom Properties | Themeable, no runtime cost |
| Icons | Lucide (tree-shaken) | Lightweight, consistent |
| Hosting | GitHub Pages / Vercel | Free, fast CDN |

### Tasks

| Task | Description | Hours | Status |
|:-----|:------------|:------|:-------|
| W5.1 | Project scaffold (Vite + structure) | 2 | PENDING |
| W5.2 | Design system (tokens, typography, colors) | 4 | PENDING |
| W5.3 | Hero section with animated terminal demo | 6 | PENDING |
| W5.4 | Live validation playground (WebSocket/fetch mock) | 8 | PENDING |
| W5.5 | Feature cards with scroll-triggered animations | 4 | PENDING |
| W5.6 | Integration examples section (copy-paste snippets) | 4 | PENDING |
| W5.7 | Performance metrics visualization | 4 | PENDING |
| W5.8 | Mobile responsive + touch interactions | 4 | PENDING |
| **Buffer** | Contingency (20%) | 8 | - |
| **Total** | Week 5 | **44** | - |

### W5.3: Hero Section — Detailed Spec

```
┌─────────────────────────────────────────────────────────────────┐
│  PHANTOM GUARD                                          [★ GitHub] │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│     Detect AI-Hallucinated                                      │
│     Package Attacks                                             │
│     ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀                                       │
│                                                                 │
│     ┌─────────────────────────────────────────────────────┐    │
│     │ $ phantom-guard validate flask-gpt-helper            │    │
│     │                                                     │    │
│     │ ⠋ Checking PyPI...                                  │    │
│     │ ✗ Package not found on PyPI                        │    │
│     │ ⚠ Matches hallucination pattern                    │    │
│     │ ⚠ AI-related suffix detected                       │    │
│     │                                                     │    │
│     │ flask-gpt-helper       HIGH_RISK    [0.82]         │    │
│     │ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 147ms           │    │
│     └─────────────────────────────────────────────────────┘    │
│                                                                 │
│     [Try it Live]              [pip install phantom-guard]     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Animation Sequence:**
1. Terminal fades in with subtle glow (0.3s)
2. Command types character by character (0.8s)
3. Spinner animates during "check" (0.5s)
4. Results appear line by line with stagger (0.6s)
5. Final verdict slides in with color flash (0.3s)
6. Progress bar fills to show speed (0.2s)

### W5.4: Live Playground — Detailed Spec

```
┌─────────────────────────────────────────────────────────────────┐
│  TRY IT NOW                                                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Package name:  [reqeusts                           ] 🔍 │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                         │   │
│  │  ⚠️  HIGH RISK                                          │   │
│  │                                                         │   │
│  │  ┌─────────────────────────────────────────────────┐   │   │
│  │  │ Signals Detected                                │   │   │
│  │  ├─────────────────────────────────────────────────┤   │   │
│  │  │ ⚠ Typosquat of "requests" (edit distance: 1)   │   │   │
│  │  │ ⚠ Package does not exist on PyPI               │   │   │
│  │  │ ⚠ Matches hallucination pattern                │   │   │
│  │  └─────────────────────────────────────────────────┘   │   │
│  │                                                         │   │
│  │  Risk Score: ████████████████████░░░░ 0.89             │   │
│  │                                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                        │
│  │  PyPI    │ │   npm    │ │ crates   │                        │
│  └──────────┘ └──────────┘ └──────────┘                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Interaction Design:**
- Real-time validation as user types (debounced 300ms)
- Registry switcher with instant re-validation
- Risk score bar animates smoothly
- Signal cards stagger in with micro-animations
- Keyboard accessible (Tab, Enter, Escape)

### W5.7: Performance Visualization

```
┌─────────────────────────────────────────────────────────────────┐
│  BLAZING FAST                                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│     Single Package                    Batch (50 packages)       │
│                                                                 │
│     ┌────────────────┐               ┌────────────────┐        │
│     │                │               │                │        │
│     │    < 200ms     │               │     < 5s       │        │
│     │    ━━━━━━━     │               │    ━━━━━━━     │        │
│     │    uncached    │               │   concurrent   │        │
│     │                │               │                │        │
│     │    < 10ms      │               │                │        │
│     │    ━━         │               │                │        │
│     │    cached      │               │                │        │
│     │                │               │                │        │
│     └────────────────┘               └────────────────┘        │
│                                                                 │
│     ┌─────────────────────────────────────────────────────┐    │
│     │ Live Benchmark: ████████░░ 156ms                    │    │
│     └─────────────────────────────────────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Module Architecture

```
showcase/
├── index.html                    # Entry point
├── vite.config.js               # Build config
├── src/
│   ├── main.js                  # Bootstrap
│   ├── styles/
│   │   ├── tokens.css           # Design tokens
│   │   ├── reset.css            # Modern reset
│   │   ├── typography.css       # Font system
│   │   └── animations.css       # Keyframes
│   ├── components/
│   │   ├── terminal.js          # <pg-terminal>
│   │   ├── playground.js        # <pg-playground>
│   │   ├── risk-meter.js        # <pg-risk-meter>
│   │   ├── signal-card.js       # <pg-signal-card>
│   │   ├── code-block.js        # <pg-code-block>
│   │   └── perf-chart.js        # <pg-perf-chart>
│   ├── animations/
│   │   ├── timeline.js          # GSAP timelines
│   │   ├── scroll-triggers.js   # Scroll animations
│   │   └── micro.js             # Micro-interactions
│   ├── services/
│   │   ├── validator.js         # Mock API / real API
│   │   └── analytics.js         # Privacy-first tracking
│   └── utils/
│       ├── debounce.js
│       ├── typewriter.js
│       └── accessibility.js
├── public/
│   ├── fonts/                   # JetBrains Mono, Inter
│   └── og-image.png             # Social preview
└── tests/
    └── e2e/                     # Playwright tests
```

### Exit Criteria
- [ ] Lighthouse score ≥95 (Performance, Accessibility)
- [ ] First Contentful Paint <1s
- [ ] Time to Interactive <2s
- [ ] Works offline (PWA ready)
- [ ] Mobile responsive (320px-2560px)
- [ ] WCAG 2.1 AA compliant
- [ ] Cross-browser (Chrome, Firefox, Safari, Edge)
- [ ] E2E tests passing

---

## Task Registry (Full Trace Matrix)

| Task ID | SPEC_IDs | INV_IDs | TEST_IDs | Hours |
|:--------|:---------|:--------|:---------|:------|
| W1.1 | S001 | INV002, INV006 | T001.05, T001.15, T001.16 | 4 |
| W1.2 | S004 | INV007 | T004.01-T004.20 | 6 |
| W1.3 | S005, S050-S059 | INV008, INV018 | T005.01-T005.17, T050.* | 6 |
| W1.4 | S006 | INV009 | T006.01-T006.19 | 6 |
| W1.5 | S007-S009 | INV001, INV010, INV011, INV012 | T007.*, T008.*, T009.* | 6 |
| W1.6 | S001-S003 | INV001-INV006, INV019-INV021 | T001.*, T002.*, T003.* | 4 |
| W2.1 | S020-S026 | INV013, INV014 | T020.01-T020.15 | 8 |
| W2.2 | S027-S032 | INV013, INV014 | T027.01-T027.12 | 6 |
| W2.3 | S033-S039 | INV013, INV014, INV015 | T033.01-T033.13 | 6 |
| W2.4 | S040-S049 | INV016, INV017 | T040.01-T040.17 | 8 |
| W2.5 | S020+ | INV013 | Error handling tests | 4 |
| W3.1 | S010-S012 | - | T010.01-T010.12 | 6 |
| W3.2 | S013-S015 | - | T010.13-T010.18 | 6 |
| W3.3 | S016-S017 | - | T010.19-T010.20 | 4 |
| W3.4 | S002 | INV004, INV005 | T002.01-T002.08 | 6 |
| W3.5 | S018-S019 | - | T010.02-T010.03, EC089 | 4 |
| W3.6 | All | All | Integration tests | 6 |
| W4.1 | Perf | - | Benchmark tests | 4 |
| W4.2 | Perf | - | - | 6 |
| W4.3 | S006 | - | EC043, EC046 | 4 |
| W4.4 | - | - | - | 4 |
| W4.5 | - | - | - | 4 |
| W4.6 | All | All | All | 6 |
| W4.7 | - | - | - | 4 |
| W5.1 | SHOW001 | - | TW5.01 | 2 |
| W5.2 | SHOW002 | - | TW5.02-04 | 4 |
| W5.3 | SHOW003 | - | TW5.05-10 | 6 |
| W5.4 | SHOW004 | - | TW5.11-18 | 8 |
| W5.5 | SHOW005 | - | TW5.19-22 | 4 |
| W5.6 | SHOW006 | - | TW5.23-26 | 4 |
| W5.7 | SHOW007 | - | TW5.27-30 | 4 |
| W5.8 | SHOW008 | - | TW5.31-35 | 4 |

---

## Dependency Graph

```
                    W1.1 (Core Types)
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
    W1.2 (Signals)    W1.3 (Patterns)   W1.4 (Typosquat)
         │                 │                 │
         └─────────────────┼─────────────────┘
                           │
                           ▼
                    W1.5 (Scoring)
                           │
                           ▼
                    W1.6 (Detector)
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
    W2.1 (PyPI)      W2.2 (npm)       W2.3 (crates)
         │                 │                 │
         └─────────────────┼─────────────────┘
                           │
                           ▼
                    W2.4 (Cache)
                           │
                           ▼
                    W2.5 (Error Handling)
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
    W3.1 (validate)   W3.2 (check)    W3.3 (cache cmd)
         │                 │                 │
         └─────────────────┼─────────────────┘
                           │
                    ┌──────┴──────┐
                    ▼             ▼
              W3.4 (Batch)   W3.5 (Output)
                    │             │
                    └──────┬──────┘
                           │
                           ▼
                    W3.6 (Integration)
                           │
                           ▼
                    W4.1-W4.7 (Polish & Release)
                           │
                           ▼
         ┌─────────────────┴─────────────────┐
         │                                   │
         ▼                                   ▼
    W5.1 (Scaffold)                    W5.2 (Design System)
         │                                   │
         └─────────────────┬─────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
    W5.3 (Hero)      W5.5 (Features)   W5.6 (Examples)
         │                 │                 │
         └─────────────────┼─────────────────┘
                           │
                           ▼
                    W5.4 (Playground)
                           │
                           ▼
                    W5.7 (Performance Viz)
                           │
                           ▼
                    W5.8 (Mobile/Responsive)
```

### Critical Path
```
W1.1 → W1.5 → W1.6 → W2.1 → W2.4 → W3.1 → W3.6 → W4.6 → W4.7 → W5.1 → W5.4 → W5.8
```

**Total Critical Path**: ~60 hours (without buffer)

---

## Risk Assessment

| Task | Risk | Factor | Mitigation |
|:-----|:-----|:-------|:-----------|
| W1.5 | MEDIUM | Algorithm complexity | Property tests, extensive edge cases |
| W2.1-W2.3 | HIGH | External API changes | Mock heavily, cache aggressively |
| W2.4 | MEDIUM | SQLite async | Use aiosqlite, test concurrency |
| W3.4 | MEDIUM | Concurrency bugs | Integration tests, race condition checks |
| W4.2 | LOW | Performance | Budget is generous (200ms) |

### Contingency Plans

**If Registry API Changes:**
1. Update parser to match new format
2. Fall back to cached data
3. Issue patch release

**If Performance Budget Exceeded:**
1. Profile hotspots
2. Add more caching layers
3. Reduce signal complexity

**If False Positive Rate Too High:**
1. Tune thresholds
2. Expand popular packages list
3. Add manual allowlist

---

## Progress Tracking

### Week 1
- [x] W1.1 Complete
- [x] W1.2 Complete
- [x] W1.3 Complete
- [x] W1.4 Complete
- [x] W1.5 Complete
- [x] W1.6 Complete
- [x] Week 1 hostile review (GO verdict)

### Week 2
- [ ] W2.1 Complete
- [ ] W2.2 Complete
- [ ] W2.3 Complete
- [ ] W2.4 Complete
- [ ] W2.5 Complete
- [ ] Week 2 hostile review

### Week 3
- [ ] W3.1 Complete
- [ ] W3.2 Complete
- [ ] W3.3 Complete
- [ ] W3.4 Complete
- [ ] W3.5 Complete
- [ ] W3.6 Complete
- [ ] Week 3 hostile review

### Week 4
- [ ] W4.1-W4.7 Complete
- [ ] Final hostile review
- [ ] Release 0.1.0

### Week 5
- [ ] W5.1 Complete (Scaffold)
- [ ] W5.2 Complete (Design System)
- [ ] W5.3 Complete (Hero)
- [ ] W5.4 Complete (Playground)
- [ ] W5.5 Complete (Features)
- [ ] W5.6 Complete (Examples)
- [ ] W5.7 Complete (Performance)
- [ ] W5.8 Complete (Mobile)
- [ ] Lighthouse ≥95
- [ ] Showcase live

---

## Quick Start After Planning

```bash
# Start implementation with TDD
/implement W1.1

# For each task:
# 1. Remove @pytest.mark.skip from relevant tests
# 2. Run tests → MUST FAIL (Red)
# 3. Write minimal code to pass
# 4. Run tests → MUST PASS (Green)
# 5. Commit with IMPLEMENTS: SPEC_ID
```

---

## Integration Points (Key for Adoption)

### pip install
```bash
pip install phantom-guard
```

### CLI Usage
```bash
# Single package
phantom-guard validate flask

# Requirements file
phantom-guard check requirements.txt

# JSON output for CI
phantom-guard check requirements.txt --output json
```

### Exit Codes (CI/CD friendly)
| Code | Meaning | CI Action |
|:-----|:--------|:----------|
| 0 | All SAFE | Continue |
| 1 | SUSPICIOUS found | Warn |
| 2 | HIGH_RISK found | Fail build |
| 3 | NOT_FOUND | Warn |
| 4 | Input error | Fail |

### Pre-commit Hook
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: phantom-guard
        name: Check for suspicious packages
        entry: phantom-guard check requirements.txt --fail-on suspicious
        language: system
        pass_filenames: false
```

### GitHub Actions
```yaml
- name: Check dependencies
  run: |
    pip install phantom-guard
    phantom-guard check requirements.txt --output json > security-report.json
```

---

**Gate 4 Status**: COMPLETE

**Next Step**: Run hostile review, then begin `/implement W1.1`
