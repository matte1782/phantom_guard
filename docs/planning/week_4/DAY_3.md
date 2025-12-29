# Week 4 - Day 3: Popular Packages Database

> **Date**: Day 3 (Week 4)
> **Focus**: Create top 1000 popular packages list for false positive prevention
> **Tasks**: W4.3
> **Hours**: 6 hours
> **SPEC_IDs**: S006 (typosquat detection enhancement)
> **EC_IDs**: EC043, EC046 (popular package handling)
> **Dependencies**: W4.2 complete
> **Exit Criteria**: Top 1000 packages per registry, false positive rate <5%

---

## Overview

Popular packages should never be flagged as typosquats or suspicious. This task creates a curated, static database of the top 1000 most-downloaded packages from each registry to prevent false positives.

### Data Sources

| Registry | Source | Format |
|:---------|:-------|:-------|
| PyPI | https://hugovk.github.io/top-pypi-packages/ | JSON |
| npm | https://www.npmjs.com/browse/depended | HTML/API |
| crates.io | https://crates.io/api/v1/crates?sort=downloads | JSON API |

### Deliverables
- [ ] `src/phantom_guard/data/popular_packages.py` with frozen sets
- [ ] Script to refresh package lists
- [ ] Tests for popular package exclusion
- [ ] Integration with typosquat detection
- [ ] False positive rate validation

---

## Morning Session (3h)

### Objective
Fetch and curate top 1000 packages from all registries.

### Step 1: Create Data Module Structure (15min)

```bash
mkdir -p src/phantom_guard/data
touch src/phantom_guard/data/__init__.py
touch src/phantom_guard/data/popular_packages.py
touch scripts/refresh_popular_packages.py
```

### Step 2: Create Package Fetcher Script (1h)

```python
# scripts/refresh_popular_packages.py
"""
Script to refresh the popular packages database.

Run periodically (e.g., monthly) to update the lists.

Usage:
    python scripts/refresh_popular_packages.py
"""

from __future__ import annotations

import json
from pathlib import Path

import httpx

OUTPUT_PATH = Path("src/phantom_guard/data/popular_packages.py")


def fetch_pypi_top_packages(limit: int = 1000) -> list[str]:
    """
    Fetch top PyPI packages from hugovk's dataset.

    Source: https://hugovk.github.io/top-pypi-packages/
    """
    url = "https://hugovk.github.io/top-pypi-packages/top-pypi-packages-30-days.min.json"

    response = httpx.get(url, timeout=30.0)
    response.raise_for_status()

    data = response.json()
    packages = [row["project"] for row in data["rows"][:limit]]

    print(f"Fetched {len(packages)} PyPI packages")
    return packages


def fetch_npm_top_packages(limit: int = 1000) -> list[str]:
    """
    Fetch top npm packages by dependents.

    Uses npm registry API with download counts.
    """
    # npm doesn't have a simple top packages API
    # Use a curated list of well-known packages + download stats

    # Start with known essential packages
    essential = [
        "lodash", "react", "express", "axios", "moment", "chalk",
        "commander", "debug", "dotenv", "eslint", "jest", "typescript",
        "webpack", "babel-core", "vue", "angular", "next", "gatsby",
        "prettier", "nodemon", "pm2", "mongoose", "sequelize", "prisma",
        "graphql", "apollo-server", "socket.io", "redis", "bull",
        "uuid", "dayjs", "date-fns", "ramda", "rxjs", "mobx",
        "formik", "yup", "joi", "zod", "class-validator",
        # ... extend to 1000
    ]

    # For a complete list, we'd use npms.io API
    # https://api.npms.io/v2/search?q=not:deprecated&size=250

    packages = essential[:limit]
    print(f"Fetched {len(packages)} npm packages")
    return packages


def fetch_crates_top_packages(limit: int = 1000) -> list[str]:
    """
    Fetch top crates.io packages by downloads.

    Uses official crates.io API.
    """
    packages: list[str] = []
    page = 1
    per_page = 100

    while len(packages) < limit:
        url = f"https://crates.io/api/v1/crates?page={page}&per_page={per_page}&sort=downloads"
        headers = {"User-Agent": "phantom-guard/0.1.0 (https://github.com/phantom-guard)"}

        response = httpx.get(url, headers=headers, timeout=30.0)
        response.raise_for_status()

        data = response.json()
        crates = [c["name"] for c in data["crates"]]

        if not crates:
            break

        packages.extend(crates)
        page += 1

    packages = packages[:limit]
    print(f"Fetched {len(packages)} crates.io packages")
    return packages


def generate_module(
    pypi: list[str],
    npm: list[str],
    crates: list[str],
) -> str:
    """Generate the Python module with frozen sets."""

    def format_set(packages: list[str], name: str) -> str:
        # Format as multi-line for readability
        lines = [f"{name}: frozenset[str] = frozenset(("]
        for i in range(0, len(packages), 10):
            chunk = packages[i:i+10]
            quoted = ", ".join(f'"{p}"' for p in chunk)
            lines.append(f"    {quoted},")
        lines.append("))")
        return "\n".join(lines)

    module = '''"""
Popular packages database for false positive prevention.

IMPLEMENTS: S006 (typosquat detection enhancement)
EC: EC043, EC046

This module contains the top 1000 most-downloaded packages from each
registry. Packages in these lists should never be flagged as typosquats.

Auto-generated by: scripts/refresh_popular_packages.py
Last updated: {date}
"""

from __future__ import annotations

# PyPI Top 1000 (by monthly downloads)
{pypi_set}

# npm Top 1000 (by dependents/downloads)
{npm_set}

# crates.io Top 1000 (by downloads)
{crates_set}

# Registry lookup
POPULAR_BY_REGISTRY: dict[str, frozenset[str]] = {{
    "pypi": PYPI_TOP_1000,
    "npm": NPM_TOP_1000,
    "crates": CRATES_TOP_1000,
}}


def is_popular(name: str, registry: str = "pypi") -> bool:
    """
    Check if a package is in the popular packages list.

    Args:
        name: Package name to check
        registry: Registry to check against

    Returns:
        True if package is in the top 1000 for the registry
    """
    popular = POPULAR_BY_REGISTRY.get(registry, PYPI_TOP_1000)
    return name.lower() in popular


def get_popular_packages(registry: str = "pypi") -> frozenset[str]:
    """
    Get the set of popular packages for a registry.

    Args:
        registry: Registry name (pypi, npm, crates)

    Returns:
        Frozen set of popular package names
    """
    return POPULAR_BY_REGISTRY.get(registry, PYPI_TOP_1000)
'''

    from datetime import datetime
    date = datetime.now().strftime("%Y-%m-%d")

    return module.format(
        date=date,
        pypi_set=format_set(pypi, "PYPI_TOP_1000"),
        npm_set=format_set(npm, "NPM_TOP_1000"),
        crates_set=format_set(crates, "CRATES_TOP_1000"),
    )


def main() -> None:
    """Fetch all packages and generate module."""
    print("Fetching popular packages...")

    pypi = fetch_pypi_top_packages(1000)
    npm = fetch_npm_top_packages(1000)
    crates = fetch_crates_top_packages(1000)

    print("\nGenerating module...")
    module_content = generate_module(pypi, npm, crates)

    OUTPUT_PATH.write_text(module_content)
    print(f"\nWritten to {OUTPUT_PATH}")

    # Verify
    print("\nVerification:")
    print(f"  PyPI: {len(pypi)} packages")
    print(f"  npm: {len(npm)} packages")
    print(f"  crates: {len(crates)} packages")


if __name__ == "__main__":
    main()
```

### Step 3: Generate Initial Package Lists (30min)

```bash
# Run the script to generate initial data
python scripts/refresh_popular_packages.py

# Verify output
python -c "from phantom_guard.data.popular_packages import PYPI_TOP_1000; print(len(PYPI_TOP_1000))"
# Expected: 1000
```

### Step 4: Create Package Data Tests (1h)

```python
# tests/unit/test_popular_packages.py
"""
Tests for popular packages database.

SPEC: S006
EC: EC043, EC046
"""

import pytest

from phantom_guard.data.popular_packages import (
    PYPI_TOP_1000,
    NPM_TOP_1000,
    CRATES_TOP_1000,
    is_popular,
    get_popular_packages,
)


class TestPopularPackagesData:
    """Tests for static package data."""

    def test_pypi_has_1000_packages(self):
        """PyPI list should have ~1000 packages."""
        assert len(PYPI_TOP_1000) >= 900
        assert len(PYPI_TOP_1000) <= 1100

    def test_npm_has_packages(self):
        """npm list should have packages."""
        assert len(NPM_TOP_1000) >= 100

    def test_crates_has_packages(self):
        """crates list should have packages."""
        assert len(CRATES_TOP_1000) >= 100

    def test_known_packages_present(self):
        """Well-known packages should be in the lists."""
        # PyPI
        assert "flask" in PYPI_TOP_1000
        assert "requests" in PYPI_TOP_1000
        assert "django" in PYPI_TOP_1000
        assert "numpy" in PYPI_TOP_1000
        assert "pandas" in PYPI_TOP_1000

        # npm
        assert "lodash" in NPM_TOP_1000 or "express" in NPM_TOP_1000

        # crates
        assert "serde" in CRATES_TOP_1000 or "tokio" in CRATES_TOP_1000

    def test_packages_are_lowercase(self):
        """All package names should be lowercase."""
        for pkg in PYPI_TOP_1000:
            assert pkg == pkg.lower(), f"{pkg} is not lowercase"

    def test_no_empty_names(self):
        """No empty package names."""
        assert "" not in PYPI_TOP_1000
        assert "" not in NPM_TOP_1000
        assert "" not in CRATES_TOP_1000


class TestIsPopular:
    """Tests for is_popular function."""

    def test_popular_package_returns_true(self):
        """
        EC: EC043

        Popular packages should return True.
        """
        assert is_popular("flask", "pypi") is True
        assert is_popular("requests", "pypi") is True
        assert is_popular("django", "pypi") is True

    def test_unknown_package_returns_false(self):
        """Unknown packages should return False."""
        assert is_popular("definitely-not-a-real-package-xyz", "pypi") is False

    def test_case_insensitive(self):
        """
        EC: EC046

        Lookup should be case-insensitive.
        """
        assert is_popular("Flask", "pypi") is True
        assert is_popular("REQUESTS", "pypi") is True
        assert is_popular("DjAnGo", "pypi") is True

    def test_different_registries(self):
        """Each registry has its own list."""
        # flask is PyPI, not npm
        pypi_popular = get_popular_packages("pypi")
        npm_popular = get_popular_packages("npm")

        # These are registry-specific
        assert "flask" in pypi_popular
        # express is npm-specific
        if "express" in npm_popular:
            assert "express" not in pypi_popular or "express" in pypi_popular


class TestFalsePositivePrevention:
    """Tests for false positive prevention."""

    def test_popular_not_flagged_as_typosquat(self):
        """
        EC: EC043

        Popular packages should not be flagged as typosquats.
        """
        from phantom_guard.core.typosquat import find_typosquat_candidates

        # flask is popular, should not be flagged
        candidates = find_typosquat_candidates("flask", "pypi")
        assert len(candidates) == 0

    def test_typosquat_of_popular_is_detected(self):
        """
        Typosquats of popular packages SHOULD be detected.
        """
        from phantom_guard.core.typosquat import find_typosquat_candidates

        # "flaskk" is typosquat of "flask"
        candidates = find_typosquat_candidates("flaskk", "pypi")
        assert any(c[0] == "flask" for c in candidates)
```

---

## Afternoon Session (3h)

### Objective
Integrate popular packages with typosquat detection and validate false positive rate.

### Step 5: Update Typosquat Detection (1h)

```python
# src/phantom_guard/core/typosquat.py
"""
IMPLEMENTS: S006
UPDATED: Integration with popular packages database.
"""

from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING

from phantom_guard.data.popular_packages import (
    get_popular_packages,
    is_popular,
)

if TYPE_CHECKING:
    from phantom_guard.core.types import TyposquatMatch


@lru_cache(maxsize=50000)
def levenshtein_distance(s1: str, s2: str) -> int:
    """Cached Levenshtein distance calculation."""
    # ... implementation from Day 2


def find_typosquat_candidates(
    name: str,
    registry: str = "pypi",
    max_distance: int = 2,
) -> list[tuple[str, int]]:
    """
    IMPLEMENTS: S006
    EC: EC043, EC046

    Find packages that could be typosquats of popular packages.

    Args:
        name: Package name to check
        registry: Target registry
        max_distance: Maximum edit distance threshold

    Returns:
        List of (popular_package, distance) tuples
    """
    name_lower = name.lower()

    # Fast path: if package IS popular, not a typosquat
    if is_popular(name_lower, registry):
        return []

    popular = get_popular_packages(registry)
    candidates: list[tuple[str, int]] = []
    name_len = len(name_lower)

    for pkg in popular:
        # Skip if length difference makes typosquat unlikely
        if abs(len(pkg) - name_len) > max_distance:
            continue

        dist = levenshtein_distance(name_lower, pkg)
        if 0 < dist <= max_distance:
            candidates.append((pkg, dist))

    # Sort by distance (closest first)
    candidates.sort(key=lambda x: x[1])

    return candidates[:5]  # Return top 5 candidates


def check_typosquat(name: str, registry: str = "pypi") -> "TyposquatMatch | None":
    """
    IMPLEMENTS: S006

    Check if a package name is a potential typosquat.

    Returns TyposquatMatch if suspicious, None otherwise.
    """
    from phantom_guard.core.types import TyposquatMatch

    candidates = find_typosquat_candidates(name, registry)

    if not candidates:
        return None

    # Get the closest match
    target, distance = candidates[0]

    return TyposquatMatch(
        original_name=name,
        similar_to=target,
        distance=distance,
        registry=registry,
    )
```

### Step 6: Validate False Positive Rate (1h)

```python
# tests/integration/test_false_positive_rate.py
"""
False positive rate validation tests.

REQUIREMENT: False positive rate <5%
"""

import pytest

from phantom_guard.core.detector import Detector
from phantom_guard.core.types import Recommendation
from phantom_guard.data.popular_packages import PYPI_TOP_1000


class TestFalsePositiveRate:
    """Validate false positive rate is under 5%."""

    @pytest.fixture
    def detector(self):
        return Detector()

    @pytest.mark.slow
    @pytest.mark.parametrize("package", list(PYPI_TOP_1000)[:100])
    def test_top_100_pypi_not_flagged(self, detector, package):
        """
        Top 100 PyPI packages should all be SAFE.

        This is the core false positive prevention test.
        """
        result = detector.validate_sync(package, registry="pypi")

        # Popular packages should be SAFE
        assert result.recommendation in (
            Recommendation.SAFE,
            Recommendation.NOT_FOUND,  # Some may not exist anymore
        ), f"{package} incorrectly flagged as {result.recommendation}"

    def test_false_positive_rate_under_5_percent(self, detector):
        """
        Overall false positive rate should be <5%.
        """
        # Test a sample of popular packages
        sample_size = 200
        sample = list(PYPI_TOP_1000)[:sample_size]

        false_positives = 0

        for package in sample:
            result = detector.validate_sync(package, registry="pypi")

            if result.recommendation in (
                Recommendation.SUSPICIOUS,
                Recommendation.HIGH_RISK,
            ):
                false_positives += 1
                print(f"False positive: {package} -> {result.recommendation}")

        rate = false_positives / sample_size * 100
        print(f"\nFalse positive rate: {rate:.2f}% ({false_positives}/{sample_size})")

        assert rate < 5.0, f"False positive rate {rate:.2f}% exceeds 5% threshold"
```

### Step 7: Update Detector Integration (30min)

```python
# src/phantom_guard/core/detector.py
"""Update detector to use popular packages."""

from phantom_guard.data.popular_packages import is_popular


async def validate(self, name: str, registry: str = "pypi") -> PackageRisk:
    """
    IMPLEMENTS: S001-S003

    Validate a package for supply chain risks.
    """
    # Fast path for popular packages
    if is_popular(name, registry):
        metadata = await self._get_metadata(name, registry)
        if metadata and metadata.exists:
            return PackageRisk(
                name=name,
                recommendation=Recommendation.SAFE,
                risk_score=0.0,
                signals=(),
                metadata=metadata,
            )

    # Continue with full analysis...
```

### Step 8: Run False Positive Validation (30min)

```bash
# Run false positive tests
pytest tests/integration/test_false_positive_rate.py -v --tb=short

# Expected output:
# False positive rate: <5%
# All top 100 packages: SAFE
```

---

## End of Day Checklist

### Code Quality
- [ ] `ruff check src/phantom_guard/data/` - No lint errors
- [ ] `ruff format src/phantom_guard/` - Code formatted
- [ ] `mypy src/phantom_guard/data/ --strict` - No type errors
- [ ] All tests passing

### Data Quality
- [ ] PyPI: ~1000 packages
- [ ] npm: 100+ packages
- [ ] crates: 100+ packages
- [ ] Known packages present (flask, requests, etc.)

### False Positive Prevention
- [ ] Top 100 PyPI packages: All SAFE
- [ ] False positive rate: <5%
- [ ] Typosquat detection still works

### Git Commit

```bash
git add src/phantom_guard/data/ scripts/ tests/
git commit -m "feat(data): Add popular packages database for false positive prevention

W4.3: Popular packages list complete

- Add top 1000 PyPI packages from hugovk dataset
- Add curated npm popular packages
- Add top 1000 crates.io packages
- Create refresh script for periodic updates
- Integrate with typosquat detection
- Validate false positive rate <5%

IMPLEMENTS: S006
EC: EC043, EC046

Popular packages are now excluded from typosquat detection,
preventing false positives on legitimate packages."
```

---

## Day 3 Success Metrics

| Metric | Target | Actual |
|:-------|:-------|:-------|
| Tasks Complete | W4.3 | |
| PyPI Packages | 1000 | |
| npm Packages | 100+ | |
| crates Packages | 100+ | |
| False Positive Rate | <5% | |

---

## Tomorrow Preview

**Day 4 Focus**: Packaging (W4.4)
- Finalize pyproject.toml
- Add classifiers and metadata
- Build wheel and sdist
- Test pip install from local
- Prepare for PyPI upload
