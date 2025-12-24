# Week 1 — Day 1: Foundation

> **Date**: Day 1
> **Focus**: Project setup + Core types
> **Tasks**: W1.1
> **Hours**: 4-6 hours

---

## Morning Session (2-3h)

### Objective
Set up the Python project structure with proper packaging, type hints, and development tooling.

### Tasks

#### 1. Project Scaffold (30min)

```bash
# Create package structure
src/
└── phantom_guard/
    ├── __init__.py
    ├── py.typed              # PEP 561 marker
    ├── core/
    │   ├── __init__.py
    │   ├── types.py          # W1.1 - Core types
    │   ├── signals.py        # W1.2 - Signal logic
    │   ├── patterns.py       # W1.3 - Pattern matching
    │   ├── typosquat.py      # W1.4 - Typosquat detection
    │   ├── scorer.py         # W1.5 - Risk scoring
    │   └── detector.py       # W1.6 - Orchestrator
    ├── registry/
    │   ├── __init__.py
    │   ├── base.py           # Abstract client
    │   ├── pypi.py           # W2.1
    │   ├── npm.py            # W2.2
    │   └── crates.py         # W2.3
    ├── cache/
    │   ├── __init__.py
    │   └── store.py          # W2.4
    └── cli/
        ├── __init__.py
        └── main.py           # W3.1
```

**Acceptance Criteria:**
- [ ] `pip install -e .` works
- [ ] `python -c "import phantom_guard"` works
- [ ] All `__init__.py` files exist

#### 2. pyproject.toml Setup (30min)

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "phantom-guard"
version = "0.1.0"
description = "Detect AI-hallucinated package attacks"
readme = "README.md"
requires-python = ">=3.11"
license = "MIT"
authors = [{ name = "Your Name" }]
keywords = ["security", "supply-chain", "slopsquatting"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Security",
]

dependencies = [
    "httpx>=0.25.0",
    "pydantic>=2.5.0",
    "typer>=0.9.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "pytest-asyncio>=0.21.0",
    "hypothesis>=6.92.0",
    "mypy>=1.8.0",
    "ruff>=0.1.0",
    "respx>=0.20.0",
]

[project.scripts]
phantom-guard = "phantom_guard.cli.main:app"

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_ignores = true

[tool.ruff]
target-version = "py311"
line-length = 100
select = ["E", "F", "I", "N", "W", "UP", "B", "C4", "SIM"]

[tool.pytest.ini_options]
testpaths = ["tests"]
markers = [
    "unit: Unit tests",
    "property: Property-based tests",
    "integration: Integration tests",
    "benchmark: Performance benchmarks",
]
```

**Acceptance Criteria:**
- [ ] `pip install -e ".[dev]"` works
- [ ] `mypy src/` runs (even with errors)
- [ ] `ruff check src/` runs

#### 3. Development Environment (30min)

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install in editable mode
pip install -e ".[dev]"

# Verify tools
mypy --version
ruff --version
pytest --version
```

**Acceptance Criteria:**
- [ ] All dev dependencies installed
- [ ] No version conflicts

---

## Afternoon Session (2-3h)

### Objective
Implement core types following TDD — tests first, then implementation.

### Task: W1.1 — Core Types

#### Step 1: Remove Skip from Test Stubs (15min)

```python
# tests/unit/test_detector.py
# Remove @pytest.mark.skip from these tests:
# - test_package_risk_structure
# - test_package_risk_score_bounds
# - test_recommendation_enum_values
# - test_signal_structure
```

#### Step 2: Run Tests — Must FAIL (5min)

```bash
pytest tests/unit/test_detector.py -v
# Expected: FAILED (imports fail, no types exist)
```

#### Step 3: Implement Types (1.5h)

```python
# src/phantom_guard/core/types.py
"""
IMPLEMENTS: S001
INVARIANTS: INV001, INV002, INV006
Core data structures for Phantom Guard.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Literal


class Recommendation(Enum):
    """
    IMPLEMENTS: S001
    Package safety recommendation.
    """
    SAFE = "safe"
    SUSPICIOUS = "suspicious"
    HIGH_RISK = "high_risk"
    NOT_FOUND = "not_found"


class SignalType(Enum):
    """
    IMPLEMENTS: S004
    Types of risk signals detected.
    """
    # Existence signals
    NOT_FOUND = "not_found"
    RECENTLY_CREATED = "recently_created"
    LOW_DOWNLOADS = "low_downloads"
    NO_REPOSITORY = "no_repository"
    NO_MAINTAINER = "no_maintainer"

    # Pattern signals
    HALLUCINATION_PATTERN = "hallucination_pattern"
    TYPOSQUAT = "typosquat"
    KNOWN_MALICIOUS = "known_malicious"

    # Positive signals (reduce risk)
    POPULAR_PACKAGE = "popular_package"
    VERIFIED_PUBLISHER = "verified_publisher"


@dataclass(frozen=True, slots=True)
class Signal:
    """
    IMPLEMENTS: S004
    INVARIANT: INV007 - Signals are immutable
    A detected risk signal with optional metadata.
    """
    type: SignalType
    weight: float  # Contribution to risk score
    message: str
    metadata: dict[str, str | int | float | bool] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # INV007: Validate weight bounds
        if not -1.0 <= self.weight <= 1.0:
            raise ValueError(f"Signal weight must be in [-1.0, 1.0], got {self.weight}")


@dataclass(frozen=True, slots=True)
class PackageRisk:
    """
    IMPLEMENTS: S001
    INVARIANTS: INV001, INV002
    Complete risk assessment for a package.
    """
    name: str
    registry: Literal["pypi", "npm", "crates"]
    exists: bool
    risk_score: float
    signals: tuple[Signal, ...]  # INV002: Never None, use empty tuple
    recommendation: Recommendation
    latency_ms: float = 0.0

    def __post_init__(self) -> None:
        # INV001: Risk score must be in [0.0, 1.0]
        if not 0.0 <= self.risk_score <= 1.0:
            raise ValueError(f"risk_score must be in [0.0, 1.0], got {self.risk_score}")

        # INV002: Signals must not be None
        if self.signals is None:
            raise ValueError("signals cannot be None, use empty tuple")

        # INV019: Package name validation
        if not self.name or not self.name.strip():
            raise ValueError("Package name cannot be empty")


# Type aliases for convenience
Registry = Literal["pypi", "npm", "crates"]
```

#### Step 4: Run Tests — Must PASS (5min)

```bash
pytest tests/unit/test_detector.py::TestPackageRiskStructure -v
# Expected: PASSED
```

#### Step 5: Run Type Checker (10min)

```bash
mypy src/phantom_guard/core/types.py --strict
# Expected: Success, no errors
```

#### Step 6: Run All Related Tests (10min)

```bash
pytest tests/unit/test_detector.py -v --tb=short
# Expected: All W1.1 tests pass, others still skipped
```

---

## End of Day Checklist

### Code Quality
- [ ] `ruff check src/` — No lint errors
- [ ] `ruff format src/` — Code formatted
- [ ] `mypy src/` — No type errors
- [ ] `pytest tests/unit/test_detector.py` — W1.1 tests pass

### Documentation
- [ ] Types have docstrings with IMPLEMENTS tags
- [ ] Invariants documented in code

### Git Commit

```bash
git add src/phantom_guard/core/types.py pyproject.toml
git commit -m "$(cat <<'EOF'
feat(core): Implement core types for package risk assessment

IMPLEMENTS: S001
INVARIANTS: INV001, INV002, INV006, INV007

- Add PackageRisk dataclass with validation
- Add Signal dataclass with weight bounds
- Add Recommendation and SignalType enums
- Add dataclass validation for invariants

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Day 1 Success Metrics

| Metric | Target | Actual |
|:-------|:-------|:-------|
| Tasks Complete | W1.1 | |
| Tests Passing | 5+ | |
| Type Coverage | 100% | |
| Lint Errors | 0 | |

---

## Tomorrow Preview

**Day 2 Focus**: Signal extraction logic (W1.2)
- Implement signal extraction from package metadata
- Property tests for signal generation
