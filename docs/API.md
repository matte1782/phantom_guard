# Phantom Guard API Reference

Python API reference for Phantom Guard - the slopsquatting detection library.

---

## Quick Start

### Async Usage (Recommended)

```python
import asyncio
from phantom_guard.core import validate_package, PackageRisk, Recommendation

async def main():
    # Validate a single package
    result: PackageRisk = await validate_package("reqeusts", registry="pypi")

    print(f"Package: {result.name}")
    print(f"Risk Score: {result.risk_score:.2f}")
    print(f"Recommendation: {result.recommendation.value}")

    for signal in result.signals:
        print(f"  - {signal.type.value}: {signal.message}")

asyncio.run(main())
```

### Sync Usage (Simple Scripts)

```python
from phantom_guard.core import validate_package_sync, validate_batch_sync

# Single package validation
result = validate_package_sync("requests", registry="pypi")
print(f"{result.name}: {result.recommendation.value}")

# Batch validation
packages = ["flask", "djang0", "reqeusts", "numpy"]
results = validate_batch_sync(packages, registry="pypi")

for r in results:
    if r.recommendation != Recommendation.SAFE:
        print(f"WARNING: {r.name} - {r.recommendation.value}")
```

---

## Core Types

### PackageRisk

Complete risk assessment result for a package.

```python
from dataclasses import dataclass
from typing import Literal

@dataclass(frozen=True, slots=True)
class PackageRisk:
    name: str                                    # Normalized package name
    registry: Literal["pypi", "npm", "crates"]   # Target registry
    exists: bool                                 # Whether package exists on registry
    risk_score: float                            # Risk score in [0.0, 1.0]
    signals: tuple[Signal, ...]                  # Detected risk signals
    recommendation: Recommendation               # Safety recommendation
    latency_ms: float = 0.0                      # Detection latency
```

**Example:**

```python
result = validate_package_sync("reqeusts")
assert 0.0 <= result.risk_score <= 1.0
assert result.signals is not None  # Never None, use empty tuple
```

### Recommendation

Package safety recommendation levels.

```python
from enum import Enum

class Recommendation(Enum):
    SAFE = "safe"              # score <= 0.30
    SUSPICIOUS = "suspicious"  # 0.30 < score <= 0.60
    HIGH_RISK = "high_risk"    # score > 0.60
    NOT_FOUND = "not_found"    # Package does not exist
```

**Example:**

```python
from phantom_guard.core import Recommendation

result = validate_package_sync("flask")
if result.recommendation == Recommendation.SAFE:
    print("Package is safe to use")
elif result.recommendation == Recommendation.HIGH_RISK:
    print("WARNING: Potential slopsquatting attack!")
```

### Signal

A detected risk signal with optional metadata.

```python
@dataclass(frozen=True, slots=True)
class Signal:
    type: SignalType                             # Signal type
    weight: float                                # Weight in [-1.0, 1.0]
    message: str                                 # Human-readable message
    metadata: dict[str, str | int | float | bool]  # Optional metadata
```

**Weight Semantics:**
- Positive weights (0.0 to 1.0) increase risk
- Negative weights (-1.0 to 0.0) decrease risk
- Example: `POPULAR_PACKAGE` has weight `-0.5` (reduces risk)

### SignalType

Types of risk signals detected during package analysis.

```python
class SignalType(Enum):
    # Existence signals (increase risk)
    NOT_FOUND = "not_found"
    RECENTLY_CREATED = "recently_created"
    LOW_DOWNLOADS = "low_downloads"
    NO_REPOSITORY = "no_repository"
    NO_MAINTAINER = "no_maintainer"
    FEW_RELEASES = "few_releases"
    SHORT_DESCRIPTION = "short_description"

    # Pattern signals (increase risk)
    HALLUCINATION_PATTERN = "hallucination_pattern"
    TYPOSQUAT = "typosquat"
    KNOWN_MALICIOUS = "known_malicious"

    # Positive signals (decrease risk)
    POPULAR_PACKAGE = "popular_package"
    VERIFIED_PUBLISHER = "verified_publisher"
    LONG_HISTORY = "long_history"
```

**Example:**

```python
from phantom_guard.core import SignalType, has_signal_type

result = validate_package_sync("reqeusts")
if has_signal_type(result.signals, SignalType.TYPOSQUAT):
    print("Potential typosquatting detected!")
```

---

## Main Functions

### validate_package

Async validation of a single package.

```python
async def validate_package(
    name: str,
    registry: Registry = "pypi",
    client: RegistryClient | None = None,
) -> PackageRisk
```

**Parameters:**
- `name`: Package name to validate
- `registry`: Target registry (`"pypi"`, `"npm"`, `"crates"`)
- `client`: Optional registry client for API calls

**Returns:** `PackageRisk` with complete assessment

**Raises:** `InvalidPackageNameError` if name is invalid

**Example:**

```python
import asyncio
from phantom_guard.core import validate_package

async def check_package():
    result = await validate_package("flask", registry="pypi")
    return result.recommendation

recommendation = asyncio.run(check_package())
```

### validate_package_sync

Synchronous wrapper for `validate_package`.

```python
def validate_package_sync(
    name: str,
    registry: Registry = "pypi",
    client: RegistryClient | None = None,
) -> PackageRisk
```

**Example:**

```python
from phantom_guard.core import validate_package_sync

# Quick validation in scripts
result = validate_package_sync("numpy", registry="pypi")
print(f"Score: {result.risk_score}")
```

### validate_batch

Async validation of multiple packages with concurrency control.

```python
async def validate_batch(
    names: list[str],
    registry: Registry = "pypi",
    client: RegistryClient | None = None,
    concurrency: int = 10,
) -> list[PackageRisk]
```

**Parameters:**
- `names`: List of package names to validate
- `registry`: Target registry
- `client`: Optional registry client
- `concurrency`: Max concurrent validations (default: 10)

**Returns:** List of `PackageRisk` in same order as input

**Example:**

```python
import asyncio
from phantom_guard.core import validate_batch, Recommendation

async def scan_dependencies():
    packages = ["flask", "django", "requests", "numpy", "pandas"]
    results = await validate_batch(packages, registry="pypi")

    risky = [r for r in results if r.recommendation != Recommendation.SAFE]
    return risky

risky_packages = asyncio.run(scan_dependencies())
```

### validate_batch_sync

Synchronous wrapper for `validate_batch`.

```python
def validate_batch_sync(
    names: list[str],
    registry: Registry = "pypi",
    client: RegistryClient | None = None,
    concurrency: int = 10,
) -> list[PackageRisk]
```

**Example:**

```python
from phantom_guard.core import validate_batch_sync

# Parse requirements.txt
packages = ["flask", "django", "reqeusts", "numpyy"]
results = validate_batch_sync(packages)

for r in results:
    print(f"{r.name}: {r.recommendation.value} ({r.risk_score:.2f})")
```

### detect_typosquat

Check if a package name is a potential typosquat.

```python
def detect_typosquat(
    name: str,
    registry: Registry = "pypi",
) -> tuple[Signal, ...]
```

**Parameters:**
- `name`: Package name to check
- `registry`: Registry to check against

**Returns:** Tuple of typosquat signals (empty if no match)

**Example:**

```python
from phantom_guard.core import detect_typosquat

signals = detect_typosquat("reqeusts", registry="pypi")
if signals:
    for s in signals:
        print(f"Typosquat of: {s.metadata.get('target')}")
        print(f"Similarity: {s.metadata.get('similarity')}")
```

---

## Advanced Classes

### TyposquatDetector

Customizable typosquat detection with configurable thresholds.

```python
class TyposquatDetector:
    def __init__(
        self,
        threshold: float = 0.65,   # Similarity threshold (0.0, 1.0) exclusive
        max_distance: int = 2,     # Maximum edit distance
    ) -> None

    def find_matches(
        self,
        name: str,
        registry: Registry,
    ) -> list[TyposquatMatch]
```

**Example:**

```python
from phantom_guard.core import TyposquatDetector

# Stricter detection (fewer false positives)
detector = TyposquatDetector(threshold=0.80, max_distance=1)
matches = detector.find_matches("reqeusts", registry="pypi")

for match in matches:
    print(f"Target: {match.target}")
    print(f"Distance: {match.distance}")
    print(f"Similarity: {match.similarity:.2%}")
```

### TyposquatMatch

Result of typosquat detection.

```python
@dataclass(frozen=True, slots=True)
class TyposquatMatch:
    target: str        # The popular package this might be typosquatting
    distance: int      # Edit distance
    similarity: float  # Similarity score (1.0 = identical)
```

### BatchValidator

High-performance batch validation with advanced features.

```python
class BatchValidator:
    def __init__(self, config: BatchConfig | None = None) -> None

    async def validate_batch(
        self,
        packages: list[str],
        registry: RegistryType,
        client: RegistryClientProtocol,
        on_progress: Callable[[int, int], None] | None = None,
        on_result: Callable[[PackageRisk], Awaitable[None] | None] | None = None,
    ) -> BatchResult

    def cancel(self) -> None
```

**Example:**

```python
import asyncio
from phantom_guard.core import BatchValidator, BatchConfig

async def validate_with_progress():
    config = BatchConfig(
        max_concurrent=20,
        fail_fast=True,        # Stop on first HIGH_RISK
        timeout_per_package=30.0,
        retry_count=2,
    )
    validator = BatchValidator(config)

    def on_progress(done: int, total: int):
        print(f"Progress: {done}/{total}")

    result = await validator.validate_batch(
        packages=["flask", "django", "requests"],
        registry="pypi",
        client=my_client,
        on_progress=on_progress,
    )

    print(f"Success: {result.success_count}")
    print(f"Errors: {result.error_count}")
    print(f"Has HIGH_RISK: {result.has_high_risk}")

    return result
```

### BatchConfig

Configuration for batch validation.

```python
@dataclass
class BatchConfig:
    max_concurrent: int = 10       # Max concurrent validations
    fail_fast: bool = False        # Stop on first HIGH_RISK
    timeout_per_package: float = 30.0  # Per-package timeout (seconds)
    retry_count: int = 2           # Retries on transient errors
```

### BatchResult

Result of batch validation.

```python
@dataclass
class BatchResult:
    results: list[PackageRisk]         # Successful validations
    errors: dict[str, Exception]       # Failed packages
    total_time_ms: float               # Total validation time
    was_cancelled: bool                # True if fail_fast triggered

    @property
    def success_count(self) -> int

    @property
    def error_count(self) -> int

    @property
    def has_high_risk(self) -> bool

    @property
    def has_suspicious(self) -> bool

    def get_by_recommendation(self, rec: Recommendation) -> list[PackageRisk]
```

---

## Constants

### Threshold Values

```python
from phantom_guard.core import (
    # Scoring thresholds
    THRESHOLD_SAFE,         # 0.30 - Below this = SAFE
    THRESHOLD_SUSPICIOUS,   # 0.60 - Above this = HIGH_RISK

    # Signal thresholds
    AGE_THRESHOLD_NEW_DAYS,       # 30 - Days to consider "new"
    DOWNLOAD_THRESHOLD_LOW,       # 1,000 - Low download count
    DOWNLOAD_THRESHOLD_POPULAR,   # 1,000,000 - Popular threshold
    RELEASE_THRESHOLD_FEW,        # 3 - Few releases
    DESCRIPTION_THRESHOLD_SHORT,  # 10 - Short description (chars)

    # Typosquat thresholds
    DEFAULT_SIMILARITY_THRESHOLD,  # 0.65 - Similarity threshold
    MAX_EDIT_DISTANCE,             # 2 - Max Levenshtein distance
    MIN_NAME_LENGTH,               # 4 - Min name length for detection
)
```

### Popular Packages

Dictionary of popular packages by registry for false positive prevention.

```python
from phantom_guard.core import POPULAR_PACKAGES

# Access by registry
pypi_packages: frozenset[str] = POPULAR_PACKAGES["pypi"]      # 1000 packages
npm_packages: frozenset[str] = POPULAR_PACKAGES["npm"]        # 1000 packages
crates_packages: frozenset[str] = POPULAR_PACKAGES["crates"]  # 1000 packages

# Check if package is popular
is_popular = "requests" in POPULAR_PACKAGES["pypi"]  # True
```

---

## Exceptions

### PhantomGuardError

Base exception for all Phantom Guard errors.

```python
class PhantomGuardError(Exception):
    """Base exception for all Phantom Guard errors."""
```

### InvalidPackageNameError

Raised when a package name fails validation.

```python
class InvalidPackageNameError(ValidationError):
    name: str      # The invalid name
    reason: str    # Why it failed
```

**Example:**

```python
from phantom_guard.core import validate_package_sync, InvalidPackageNameError

try:
    result = validate_package_sync("")
except InvalidPackageNameError as e:
    print(f"Invalid name '{e.name}': {e.reason}")
```

### InvalidRegistryError

Raised when an unsupported registry is specified.

```python
class InvalidRegistryError(ValidationError):
    registry: str  # The invalid registry
```

---

## Helper Functions

### Similarity Functions

```python
from phantom_guard.core import (
    levenshtein_distance,  # Calculate edit distance
    normalized_distance,   # Normalized distance (0.0-1.0)
    similarity,           # Similarity score (1.0 = identical)
)

# Edit distance
dist = levenshtein_distance("requests", "reqeusts")  # 2

# Normalized (0.0 to 1.0, where 0.0 = identical)
norm = normalized_distance("requests", "reqeusts")   # 0.25

# Similarity (1.0 = identical, 0.0 = completely different)
sim = similarity("requests", "reqeusts")             # 0.75
```

### Signal Helpers

```python
from phantom_guard.core import (
    has_signal_type,        # Check if signal type exists
    get_signal_by_type,     # Get signal by type
    calculate_total_weight, # Sum of all weights
    merge_signals,          # Merge signal tuples
)

result = validate_package_sync("reqeusts")

# Check for specific signal
if has_signal_type(result.signals, SignalType.TYPOSQUAT):
    typo_signal = get_signal_by_type(result.signals, SignalType.TYPOSQUAT)
    print(typo_signal.message)

# Calculate total weight
total = calculate_total_weight(result.signals)
```

---

## Complete Example

```python
"""
Full example: Scan requirements.txt for risky packages.
"""
import asyncio
from pathlib import Path
from phantom_guard.core import (
    validate_batch,
    PackageRisk,
    Recommendation,
    SignalType,
    has_signal_type,
)

async def scan_requirements(file_path: str) -> None:
    # Parse requirements.txt
    packages = []
    for line in Path(file_path).read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            # Extract package name (before ==, >=, etc.)
            name = line.split("==")[0].split(">=")[0].split("<=")[0].strip()
            if name:
                packages.append(name)

    print(f"Scanning {len(packages)} packages...")

    # Validate all packages
    results = await validate_batch(packages, registry="pypi")

    # Group by recommendation
    safe = []
    suspicious = []
    high_risk = []

    for r in results:
        match r.recommendation:
            case Recommendation.SAFE:
                safe.append(r)
            case Recommendation.SUSPICIOUS:
                suspicious.append(r)
            case Recommendation.HIGH_RISK | Recommendation.NOT_FOUND:
                high_risk.append(r)

    # Report
    print(f"\nResults: {len(safe)} safe, {len(suspicious)} suspicious, {len(high_risk)} high-risk\n")

    if high_risk:
        print("HIGH RISK PACKAGES:")
        for r in high_risk:
            print(f"  - {r.name} (score: {r.risk_score:.2f})")
            for s in r.signals:
                print(f"      {s.type.value}: {s.message}")

    if suspicious:
        print("\nSUSPICIOUS PACKAGES:")
        for r in suspicious:
            typo = has_signal_type(r.signals, SignalType.TYPOSQUAT)
            flag = " [TYPOSQUAT]" if typo else ""
            print(f"  - {r.name} (score: {r.risk_score:.2f}){flag}")

if __name__ == "__main__":
    asyncio.run(scan_requirements("requirements.txt"))
```

---

## Performance Notes

| Operation | Budget | Constraint |
|-----------|--------|------------|
| Single package (cached) | <10ms | P99 |
| Single package (uncached) | <200ms | P99 |
| 50 packages (concurrent) | <5s | P99 |
| Pattern matching | <1ms | P99 |

For best performance:
- Use async APIs (`validate_package`, `validate_batch`) in async contexts
- Adjust `concurrency` parameter based on your rate limits
- Use `BatchValidator` with `fail_fast=True` for CI/CD pipelines
