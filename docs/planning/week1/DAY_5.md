# Week 1 — Day 5: Detector Orchestrator

> **Date**: Day 5
> **Focus**: Detector orchestrator + Week 1 integration
> **Tasks**: W1.6, Week 1 Review
> **Hours**: 6-8 hours

---

## Morning Session (3h)

### Objective
Implement the detector orchestrator that wires all components together.

### Task: W1.6 — Detector Orchestrator

#### Step 1: Enable Test Stubs (15min)

```python
# tests/unit/test_detector.py
# Enable orchestrator tests:
# - test_validate_package_full_flow
# - test_validate_package_not_found
# - test_validate_package_typosquat
# - test_validate_package_popular
# - test_validate_batch
# - test_validate_with_registry_mock
```

#### Step 2: Implement Core Detector (1.5h)

```python
# src/phantom_guard/core/detector.py
"""
IMPLEMENTS: S001, S002, S003
INVARIANTS: INV001-INV006, INV019-INV021
Main detection orchestrator.
"""

from __future__ import annotations

import re
import time
from typing import Protocol

from phantom_guard.core.patterns import match_patterns
from phantom_guard.core.scorer import build_package_risk, calculate_risk_score
from phantom_guard.core.signals import extract_signals, merge_signals
from phantom_guard.core.typosquat import detect_typosquat
from phantom_guard.core.types import (
    PackageMetadata,
    PackageRisk,
    Registry,
    Signal,
)


# Package name validation regex
# IMPLEMENTS: S001, INV019, INV020
PACKAGE_NAME_PATTERN = re.compile(r"^[a-zA-Z0-9]([a-zA-Z0-9._-]*[a-zA-Z0-9])?$")
MAX_PACKAGE_NAME_LENGTH = 214  # npm limit, strictest


class RegistryClient(Protocol):
    """
    Protocol for registry clients.
    Allows dependency injection for testing.
    """
    async def get_package_metadata(self, name: str) -> PackageMetadata:
        """Fetch package metadata from registry."""
        ...


def validate_package_name(name: str) -> tuple[bool, str]:
    """
    IMPLEMENTS: S001
    INVARIANTS: INV019, INV020, INV021

    Validate package name format.

    Args:
        name: Package name to validate

    Returns:
        (is_valid, error_message)
    """
    # INV019: Non-empty
    if not name or not name.strip():
        return False, "Package name cannot be empty"

    name = name.strip()

    # INV020: Length check
    if len(name) > MAX_PACKAGE_NAME_LENGTH:
        return False, f"Package name too long (max {MAX_PACKAGE_NAME_LENGTH})"

    # INV021: ASCII only
    if not name.isascii():
        return False, "Package name must be ASCII only"

    # Format check
    if not PACKAGE_NAME_PATTERN.match(name):
        return False, "Invalid package name format"

    return True, ""


def normalize_package_name(name: str) -> str:
    """
    Normalize package name for comparison.
    - Lowercase
    - Replace underscores with hyphens
    - Strip whitespace
    """
    return name.lower().strip().replace("_", "-")


async def validate_package(
    name: str,
    registry: Registry = "pypi",
    client: RegistryClient | None = None,
) -> PackageRisk:
    """
    IMPLEMENTS: S001, S002, S003
    INVARIANTS: INV001-INV006

    Validate a single package for slopsquatting risk.

    This is the main entry point for package validation.

    Args:
        name: Package name to validate
        registry: Target registry (pypi, npm, crates)
        client: Optional registry client (for testing)

    Returns:
        PackageRisk with complete assessment

    Raises:
        ValueError: If package name is invalid
    """
    start_time = time.perf_counter()

    # Step 1: Validate input
    # INV019, INV020, INV021
    is_valid, error = validate_package_name(name)
    if not is_valid:
        raise ValueError(error)

    normalized_name = normalize_package_name(name)

    # Step 2: Gather signals from static analysis
    pattern_signals = match_patterns(normalized_name)
    typosquat_signals = detect_typosquat(normalized_name, registry)

    # Step 3: Fetch metadata and extract signals
    if client is not None:
        metadata = await client.get_package_metadata(normalized_name)
        metadata_signals = extract_signals(metadata)
        exists = metadata.exists
    else:
        # No client = offline mode, use only static analysis
        metadata_signals = ()
        exists = True  # Assume exists if we can't check

    # Step 4: Merge all signals
    all_signals = merge_signals(
        pattern_signals,
        typosquat_signals,
        metadata_signals,
    )

    # Step 5: Build final result
    latency_ms = (time.perf_counter() - start_time) * 1000

    return build_package_risk(
        name=normalized_name,
        registry=registry,
        exists=exists,
        signals=all_signals,
        latency_ms=latency_ms,
    )


async def validate_batch(
    names: list[str],
    registry: Registry = "pypi",
    client: RegistryClient | None = None,
    concurrency: int = 10,
) -> list[PackageRisk]:
    """
    IMPLEMENTS: S002
    INVARIANTS: INV004, INV005

    Validate multiple packages concurrently.

    Args:
        names: List of package names
        registry: Target registry
        client: Optional registry client
        concurrency: Max concurrent validations

    Returns:
        List of PackageRisk in same order as input
    """
    import asyncio

    semaphore = asyncio.Semaphore(concurrency)

    async def validate_with_semaphore(name: str) -> PackageRisk:
        async with semaphore:
            try:
                return await validate_package(name, registry, client)
            except ValueError as e:
                # Return error as high-risk result
                return PackageRisk(
                    name=name,
                    registry=registry,
                    exists=False,
                    risk_score=1.0,
                    signals=(),
                    recommendation=Recommendation.HIGH_RISK,
                    latency_ms=0.0,
                )

    from phantom_guard.core.types import Recommendation

    tasks = [validate_with_semaphore(name) for name in names]
    return await asyncio.gather(*tasks)
```

#### Step 3: Create Mock Client for Testing (30min)

```python
# tests/conftest.py (add to existing)

from phantom_guard.core.types import PackageMetadata, Registry
from datetime import datetime, timezone


class MockRegistryClient:
    """Mock registry client for testing."""

    def __init__(self, packages: dict[str, PackageMetadata] | None = None):
        self.packages = packages or {}
        self.call_count = 0

    async def get_package_metadata(self, name: str) -> PackageMetadata:
        self.call_count += 1

        if name in self.packages:
            return self.packages[name]

        # Default: package not found
        return PackageMetadata(
            name=name,
            exists=False,
            registry="pypi",
        )


@pytest.fixture
def mock_client():
    """Create a mock registry client with test data."""
    return MockRegistryClient({
        "flask": PackageMetadata(
            name="flask",
            exists=True,
            created_at=datetime(2010, 4, 1, tzinfo=timezone.utc),
            downloads_last_month=15_000_000,
            repository_url="https://github.com/pallets/flask",
            maintainer_count=5,
            registry="pypi",
        ),
        "requests": PackageMetadata(
            name="requests",
            exists=True,
            created_at=datetime(2011, 2, 13, tzinfo=timezone.utc),
            downloads_last_month=50_000_000,
            repository_url="https://github.com/psf/requests",
            maintainer_count=3,
            registry="pypi",
        ),
    })
```

#### Step 4: Run Tests (30min)

```bash
# Run detector tests
pytest tests/unit/test_detector.py -v

# Run with coverage
pytest tests/unit/ --cov=phantom_guard.core --cov-report=term-missing
```

---

## Afternoon Session (3h)

### Objective
Week 1 integration and review.

#### Step 1: End-to-End Integration Test (1h)

```python
# tests/integration/test_core_e2e.py
"""
End-to-end tests for core detection flow.
"""

import pytest
from phantom_guard.core.detector import validate_package, validate_batch
from phantom_guard.core.types import Recommendation


@pytest.mark.asyncio
class TestCoreE2E:
    """End-to-end tests without network."""

    async def test_validate_known_safe_package(self, mock_client):
        """Flask should be safe."""
        result = await validate_package("flask", client=mock_client)

        assert result.name == "flask"
        assert result.exists is True
        assert result.risk_score < 0.3
        assert result.recommendation == Recommendation.SAFE

    async def test_validate_typosquat(self, mock_client):
        """reqeusts should be detected as typosquat."""
        result = await validate_package("reqeusts", client=mock_client)

        assert result.exists is False
        assert result.risk_score > 0.6
        assert result.recommendation in (Recommendation.SUSPICIOUS, Recommendation.HIGH_RISK)

        # Should have typosquat signal
        typosquat_signals = [s for s in result.signals if s.type.value == "typosquat"]
        assert len(typosquat_signals) > 0

    async def test_validate_hallucination_pattern(self, mock_client):
        """flask-gpt-helper should trigger pattern detection."""
        result = await validate_package("flask-gpt-helper", client=mock_client)

        assert result.risk_score > 0.5

        # Should have hallucination pattern signal
        pattern_signals = [s for s in result.signals if s.type.value == "hallucination_pattern"]
        assert len(pattern_signals) > 0

    async def test_validate_batch_ordering(self, mock_client):
        """Batch results should maintain input order."""
        names = ["flask", "reqeusts", "requests", "flask-gpt-helper"]
        results = await validate_batch(names, client=mock_client)

        assert len(results) == 4
        assert results[0].name == "flask"
        assert results[1].name == "reqeusts"
        assert results[2].name == "requests"
        assert results[3].name == "flask-gpt-helper"

    async def test_validate_invalid_name_raises(self):
        """Invalid names should raise ValueError."""
        with pytest.raises(ValueError, match="empty"):
            await validate_package("")

        with pytest.raises(ValueError, match="ASCII"):
            await validate_package("flask-помощник")
```

#### Step 2: Run Full Test Suite (30min)

```bash
# All tests
pytest tests/ -v --tb=short

# With coverage
pytest tests/ --cov=phantom_guard --cov-report=html
open htmlcov/index.html
```

#### Step 3: Code Quality Check (30min)

```bash
# Lint
ruff check src/ tests/

# Format
ruff format src/ tests/

# Type check
mypy src/phantom_guard/ --strict

# All should pass with no errors
```

#### Step 4: Week 1 Hostile Review (1h)

Run self-review against checklist:

```markdown
## Week 1 Exit Checklist

### Implementation
- [ ] W1.1 Core types — COMPLETE
- [ ] W1.2 Signal extraction — COMPLETE
- [ ] W1.3 Pattern matching — COMPLETE
- [ ] W1.4 Typosquat detection — COMPLETE
- [ ] W1.5 Risk scoring — COMPLETE
- [ ] W1.6 Detector orchestrator — COMPLETE

### Quality
- [ ] All unit tests passing
- [ ] Property tests for invariants passing
- [ ] mypy --strict passes
- [ ] ruff check passes
- [ ] Coverage ≥90% on core/

### Documentation
- [ ] All functions have IMPLEMENTS tags
- [ ] All invariants documented
- [ ] README updated with core usage

### Performance
- [ ] Single validation <1ms (static only)
- [ ] Pattern matching <1ms
- [ ] Typosquat detection <1ms
```

---

## End of Day Checklist

### Final Quality Gate

```bash
# Full quality check
ruff check src/ tests/ && \
ruff format --check src/ tests/ && \
mypy src/phantom_guard/ --strict && \
pytest tests/ --cov=phantom_guard.core --cov-fail-under=90
```

### Git Commit (W1.6)

```bash
git add src/phantom_guard/core/detector.py tests/integration/test_core_e2e.py
git commit -m "$(cat <<'EOF'
feat(core): Implement detector orchestrator

IMPLEMENTS: S001, S002, S003
INVARIANTS: INV001-INV006, INV019-INV021

- Add validate_package as main entry point
- Add validate_batch for concurrent validation
- Add package name validation
- Wire all core components together
- Add end-to-end integration tests

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

### Git Tag (Week 1)

```bash
git tag -a v0.0.1-alpha.1 -m "Week 1 Complete: Core Engine"
```

---

## Week 1 Final Metrics

| Metric | Target | Actual |
|:-------|:-------|:-------|
| Tasks Complete | 6/6 | |
| Unit Tests | 45+ | |
| Property Tests | 10+ | |
| Coverage | 90%+ | |
| Type Errors | 0 | |
| Lint Errors | 0 | |

---

## Week 2 Preview

**Week 2 Focus**: Registry Clients

| Day | Task | Description |
|:----|:-----|:------------|
| Day 6 | W2.1 | PyPI client + pypistats |
| Day 7 | W2.2 | npm client |
| Day 8 | W2.3 | crates.io client |
| Day 9 | W2.4 | Two-tier cache |
| Day 10 | W2.5 | Error handling + retries |

---

## Celebration Checkpoint 🎉

Week 1 complete! The core detection engine is working:

```python
# You can now run (in offline mode):
import asyncio
from phantom_guard.core.detector import validate_package

result = asyncio.run(validate_package("flask-gpt-helper"))
print(f"{result.name}: {result.recommendation.value} ({result.risk_score:.2f})")
# flask-gpt-helper: suspicious (0.58)
```

The foundation is solid. Week 2 adds the registry clients to fetch real data.
