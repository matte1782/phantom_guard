# Week 4 - Day 3: Popular Packages Database (OPTIMIZED)

> **Date**: Day 3 (Week 4)
> **Focus**: Expand popular packages from 172 to 3000+
> **Tasks**: W4.3
> **Hours**: 6 hours
> **Status**: OPTIMIZED based on hostile review findings
> **CRITICAL**: Current database is only 172 packages, need 3000+

---

## Pre-Existing State Analysis

### What Already Exists (172 packages)

| Registry | Current Count | Target | Gap |
|:---------|:--------------|:-------|:----|
| PyPI | 97 packages | 1000 | -903 |
| npm | 50 packages | 1000 | -950 |
| crates.io | 25 packages | 1000 | -975 |
| **Total** | **172** | **3000** | **-2828** |

### Current Location
```
src/phantom_guard/core/typosquat.py
  └── POPULAR_PACKAGES dict (lines 45-269)
      ├── pypi: 97 packages
      ├── npm: 50 packages
      └── crates: 25 packages
```

### Issues with Current Implementation
1. **Hardcoded in typosquat.py** - Not in dedicated data module
2. **Only 172 packages** - Far below 3000 target
3. **No refresh mechanism** - Static list, no update script

---

## Revised Task Breakdown

### Morning Session (3h) - Create Data Module + Fetch Scripts

#### Step 1: Create Data Module Structure (15min)

```bash
# Create dedicated data module
mkdir -p src/phantom_guard/data
touch src/phantom_guard/data/__init__.py
touch src/phantom_guard/data/popular_packages.py
mkdir -p scripts
touch scripts/refresh_popular_packages.py
```

#### Step 2: Create Package Fetcher Script (1.5h)

```python
# scripts/refresh_popular_packages.py
"""
Script to refresh the popular packages database.

Run monthly to update the lists:
    python scripts/refresh_popular_packages.py

Sources:
- PyPI: hugovk/top-pypi-packages (30-day downloads)
- npm: npms.io API
- crates.io: Official API (sorted by downloads)
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
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
    packages = [row["project"].lower() for row in data["rows"][:limit]]

    print(f"Fetched {len(packages)} PyPI packages")
    return packages


def fetch_npm_top_packages(limit: int = 1000) -> list[str]:
    """
    Fetch top npm packages using npms.io API.

    Uses quality + popularity scoring.
    """
    packages: list[str] = []
    offset = 0
    size = 250  # Max per request

    while len(packages) < limit:
        url = f"https://api.npms.io/v2/search?q=not:deprecated&size={size}&from={offset}"

        try:
            response = httpx.get(url, timeout=30.0)
            response.raise_for_status()

            data = response.json()
            results = data.get("results", [])

            if not results:
                break

            for item in results:
                pkg_name = item.get("package", {}).get("name", "")
                if pkg_name and pkg_name not in packages:
                    packages.append(pkg_name)

            offset += size
            time.sleep(0.5)  # Rate limiting

        except Exception as e:
            print(f"npm fetch error at offset {offset}: {e}")
            break

    packages = packages[:limit]
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

        try:
            response = httpx.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()

            data = response.json()
            crates = [c["name"].lower() for c in data["crates"]]

            if not crates:
                break

            packages.extend(crates)
            page += 1
            time.sleep(0.5)  # Rate limiting

        except Exception as e:
            print(f"crates.io fetch error at page {page}: {e}")
            break

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
        lines = [f"{name}: frozenset[str] = frozenset(("]
        for i in range(0, len(packages), 8):
            chunk = packages[i:i+8]
            quoted = ", ".join(f'"{p}"' for p in chunk)
            lines.append(f"    {quoted},")
        lines.append("))")
        return "\n".join(lines)

    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    module = f'''"""
Popular packages database for false positive prevention.

IMPLEMENTS: S006 (typosquat detection enhancement)
EC: EC043, EC046

Contains top 1000 packages per registry to prevent false positives
on legitimate popular packages.

Auto-generated by: scripts/refresh_popular_packages.py
Last updated: {date}
Package counts: PyPI={len(pypi)}, npm={len(npm)}, crates={len(crates)}
"""

from __future__ import annotations

# PyPI Top {len(pypi)} (by monthly downloads)
{format_set(pypi, "PYPI_POPULAR")}

# npm Top {len(npm)} (by dependents/downloads)
{format_set(npm, "NPM_POPULAR")}

# crates.io Top {len(crates)} (by downloads)
{format_set(crates, "CRATES_POPULAR")}

# Registry lookup
POPULAR_BY_REGISTRY: dict[str, frozenset[str]] = {{
    "pypi": PYPI_POPULAR,
    "npm": NPM_POPULAR,
    "crates": CRATES_POPULAR,
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
    popular = POPULAR_BY_REGISTRY.get(registry.lower(), PYPI_POPULAR)
    return name.lower() in popular


def get_popular_packages(registry: str = "pypi") -> frozenset[str]:
    """
    Get the set of popular packages for a registry.

    Args:
        registry: Registry name (pypi, npm, crates)

    Returns:
        Frozen set of popular package names
    """
    return POPULAR_BY_REGISTRY.get(registry.lower(), PYPI_POPULAR)
'''

    return module


def main() -> None:
    """Fetch all packages and generate module."""
    print("Fetching popular packages...")
    print("=" * 50)

    pypi = fetch_pypi_top_packages(1000)
    npm = fetch_npm_top_packages(1000)
    crates = fetch_crates_top_packages(1000)

    print("=" * 50)
    print("Generating module...")

    module_content = generate_module(pypi, npm, crates)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(module_content)

    print(f"Written to {OUTPUT_PATH}")
    print()
    print("Summary:")
    print(f"  PyPI:     {len(pypi):>4} packages")
    print(f"  npm:      {len(npm):>4} packages")
    print(f"  crates:   {len(crates):>4} packages")
    print(f"  Total:    {len(pypi) + len(npm) + len(crates):>4} packages")


if __name__ == "__main__":
    main()
```

#### Step 3: Run Script to Generate Data (30min)

```bash
# Run the script
python scripts/refresh_popular_packages.py

# Verify output
python -c "from phantom_guard.data.popular_packages import PYPI_POPULAR; print(len(PYPI_POPULAR))"
# Expected: ~1000
```

#### Step 4: Update Typosquat to Use New Data Module (45min)

```python
# src/phantom_guard/core/typosquat.py - UPDATE IMPORTS

# Replace the hardcoded POPULAR_PACKAGES dict with import:

from phantom_guard.data.popular_packages import (
    get_popular_packages,
    is_popular,
    POPULAR_BY_REGISTRY,
)

# Update get_popular_packages function to use the new module
# (or remove if imported directly)
```

---

### Afternoon Session (3h) - Integration + Validation

#### Step 5: Create Unit Tests for Data Module (1h)

```python
# tests/unit/test_popular_packages.py
"""
Tests for popular packages database.

SPEC: S006
EC: EC043, EC046
"""

import pytest

from phantom_guard.data.popular_packages import (
    PYPI_POPULAR,
    NPM_POPULAR,
    CRATES_POPULAR,
    is_popular,
    get_popular_packages,
)


class TestPopularPackagesData:
    """Tests for static package data."""

    def test_pypi_has_1000_packages(self):
        """PyPI list should have ~1000 packages."""
        assert len(PYPI_POPULAR) >= 900
        assert len(PYPI_POPULAR) <= 1100

    def test_npm_has_packages(self):
        """npm list should have ~1000 packages."""
        assert len(NPM_POPULAR) >= 500

    def test_crates_has_packages(self):
        """crates list should have ~1000 packages."""
        assert len(CRATES_POPULAR) >= 500

    def test_known_pypi_packages_present(self):
        """Well-known PyPI packages should be present."""
        expected = {"requests", "flask", "django", "numpy", "pandas",
                   "pytest", "black", "ruff", "fastapi", "pydantic"}
        for pkg in expected:
            assert pkg in PYPI_POPULAR, f"{pkg} missing from PyPI popular"

    def test_known_npm_packages_present(self):
        """Well-known npm packages should be present."""
        expected = {"react", "lodash", "express", "axios", "typescript"}
        for pkg in expected:
            assert pkg in NPM_POPULAR, f"{pkg} missing from npm popular"

    def test_known_crates_packages_present(self):
        """Well-known crates should be present."""
        expected = {"serde", "tokio", "clap", "rand", "regex"}
        for pkg in expected:
            assert pkg in CRATES_POPULAR, f"{pkg} missing from crates popular"

    def test_packages_are_lowercase(self):
        """All package names should be lowercase."""
        for pkg in PYPI_POPULAR:
            assert pkg == pkg.lower(), f"{pkg} is not lowercase"

    def test_no_empty_names(self):
        """No empty package names."""
        assert "" not in PYPI_POPULAR
        assert "" not in NPM_POPULAR
        assert "" not in CRATES_POPULAR


class TestIsPopular:
    """Tests for is_popular function."""

    def test_popular_package_returns_true(self):
        """EC: EC043 - Popular packages should return True."""
        assert is_popular("flask", "pypi") is True
        assert is_popular("requests", "pypi") is True

    def test_unknown_package_returns_false(self):
        """Unknown packages should return False."""
        assert is_popular("definitely-not-a-real-package-xyz123", "pypi") is False

    def test_case_insensitive(self):
        """EC: EC046 - Lookup should be case-insensitive."""
        assert is_popular("Flask", "pypi") is True
        assert is_popular("REQUESTS", "pypi") is True
```

#### Step 6: Validate False Positive Rate (1h)

```python
# tests/integration/test_false_positive_rate.py
"""
False positive rate validation tests.

REQUIREMENT: False positive rate <5%
"""

import pytest
from phantom_guard.core.detector import Detector
from phantom_guard.core.types import Recommendation
from phantom_guard.data.popular_packages import PYPI_POPULAR


class TestFalsePositiveRate:
    """Validate false positive rate is under 5%."""

    @pytest.fixture
    def detector(self):
        return Detector()

    @pytest.mark.slow
    def test_top_100_pypi_not_flagged(self, detector):
        """
        Top 100 PyPI packages should all be SAFE.
        """
        sample = list(PYPI_POPULAR)[:100]
        false_positives = 0

        for package in sample:
            result = detector.validate_sync(package, registry="pypi")

            if result.recommendation in (
                Recommendation.SUSPICIOUS,
                Recommendation.HIGH_RISK,
            ):
                false_positives += 1
                print(f"False positive: {package}")

        rate = false_positives / len(sample) * 100
        print(f"False positive rate: {rate:.1f}%")

        assert rate < 5.0, f"False positive rate {rate:.1f}% exceeds 5%"
```

#### Step 7: Update Detector Integration (30min)

```python
# src/phantom_guard/core/detector.py - UPDATE

# Add fast-path for popular packages:
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

#### Step 8: Run All Tests (30min)

```bash
# Run unit tests
pytest tests/unit/test_popular_packages.py -v

# Run false positive validation
pytest tests/integration/test_false_positive_rate.py -v --tb=short

# Verify no regressions
pytest tests/ -v --tb=short
```

---

## End of Day Checklist

### Data Created
- [ ] `src/phantom_guard/data/__init__.py` created
- [ ] `src/phantom_guard/data/popular_packages.py` generated
- [ ] `scripts/refresh_popular_packages.py` created

### Package Counts Verified
- [ ] PyPI: ~1000 packages
- [ ] npm: ~1000 packages
- [ ] crates: ~1000 packages
- [ ] Total: ~3000 packages

### Integration Complete
- [ ] typosquat.py updated to use new data module
- [ ] Detector uses is_popular() fast path
- [ ] All tests passing

### False Positive Prevention
- [ ] Top 100 PyPI packages: All SAFE
- [ ] False positive rate: <5%

### Git Commit

```bash
git add src/phantom_guard/data/ scripts/ tests/
git commit -m "feat(data): Add popular packages database (3000+ packages)

W4.3: Popular packages database COMPLETE

- Create src/phantom_guard/data/popular_packages.py
- Add refresh script for monthly updates
- Expand from 172 → 3000+ packages:
  - PyPI: 97 → 1000
  - npm: 50 → 1000
  - crates: 25 → 1000
- Add fast-path in Detector for popular packages
- Validate false positive rate <5%

IMPLEMENTS: S006
EC: EC043, EC046"
```

---

## Day 3 Success Metrics

| Metric | Target | Actual |
|:-------|:-------|:-------|
| Tasks Complete | W4.3 | |
| PyPI Packages | 1000 | |
| npm Packages | 1000 | |
| crates Packages | 1000 | |
| False Positive Rate | <5% | |

---

## Key Insight from Hostile Review

**CRITICAL GAP IDENTIFIED**: The existing typosquat.py only has 172 packages:
- PyPI: 97 (need 903 more)
- npm: 50 (need 950 more)
- crates: 25 (need 975 more)

This task is about **expanding coverage**, not creating from scratch.

---

## Tomorrow Preview

**Day 4 Focus**: Packaging (W4.4)
- Fix pyproject.toml URLs (placeholder → real)
- Create LICENSE file
- Create CHANGELOG.md
- Build and test wheel/sdist
