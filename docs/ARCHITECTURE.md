# Phantom Guard Architecture

> **Version**: 0.1.0 (MVP)
> **Last Updated**: 2025-12-23

---

## Overview

Phantom Guard detects AI-hallucinated package attacks (slopsquatting) by validating packages against registry APIs and scoring their risk based on multiple signals.

```
┌─────────────────────────────────────────────────────────────────┐
│                         Entry Points                            │
│  CLI (`phantom-guard check`)  │  Python API  │  Install Hooks  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                          Detector                               │
│              Orchestrates validation pipeline                   │
└─────────────────────────────────────────────────────────────────┘
                                │
              ┌─────────────────┼─────────────────┐
              ▼                 ▼                 ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│     Cache       │  │     Scorer      │  │    Patterns     │
│  Memory/SQLite  │  │  Risk scoring   │  │  Name matching  │
└─────────────────┘  └─────────────────┘  └─────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Registry Clients                           │
│         PyPI          │        npm          │     crates.io    │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      ValidationResult                           │
│    safe: List[str]  │  suspicious: List[PackageRisk]  │  ...   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Core Detection Engine

### Problem Statement

**What are we building?**
The core detection engine that validates packages against registry APIs and scores their slopsquatting risk.

**Why is this needed?**
AI coding assistants hallucinate package names. Attackers register these names with malware. Developers blindly install what AI suggests.

**Constraints:**
- Performance: Single package < 200ms uncached, < 10ms cached
- Security: No command injection, no path traversal
- Compatibility: Python 3.11+
- Dependencies: httpx, pydantic (already in pyproject.toml)

**Non-goals (P1):**
- Caching (P3)
- CLI interface (P2)
- Install hooks (P5)

---

## Component Specifications

### 1. Data Models (`src/phantom_guard/core/types.py`)

**Responsibility:** Define all data structures used throughout the system.

```python
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

class Registry(str, Enum):
    """Supported package registries."""
    PYPI = "pypi"
    NPM = "npm"
    CRATES = "crates"

class RiskLevel(str, Enum):
    """Risk classification levels."""
    SAFE = "safe"           # Score >= 60
    SUSPICIOUS = "suspicious"  # Score 30-59
    HIGH_RISK = "high_risk"    # Score < 30
    NOT_FOUND = "not_found"    # Package doesn't exist

class SignalType(str, Enum):
    """Types of risk signals detected."""
    NOT_FOUND = "not_found"
    FEW_RELEASES = "few_releases"
    NO_REPOSITORY = "no_repository"
    NO_AUTHOR = "no_author"
    NO_DESCRIPTION = "no_description"
    LOW_DOWNLOADS = "low_downloads"
    NEW_PACKAGE = "new_package"
    HALLUCINATION_PATTERN = "hallucination_pattern"

@dataclass(frozen=True)
class PackageMetadata:
    """Metadata fetched from registry."""
    name: str
    registry: Registry
    exists: bool
    release_count: int = 0
    has_repository: bool = False
    has_author: bool = False
    has_description: bool = False
    downloads_last_month: Optional[int] = None
    created_at: Optional[datetime] = None

@dataclass(frozen=True)
class RiskSignal:
    """Individual risk signal with weight."""
    signal_type: SignalType
    weight: int  # Points deducted (negative) or added (positive)
    details: str

@dataclass(frozen=True)
class PackageRisk:
    """Complete risk assessment for a package."""
    package_name: str
    registry: Registry
    risk_level: RiskLevel
    risk_score: int  # 0-100
    signals: tuple[RiskSignal, ...]
    recommendation: str
    metadata: Optional[PackageMetadata] = None

@dataclass(frozen=True)
class ValidationResult:
    """Result of validating multiple packages."""
    safe: tuple[str, ...]
    suspicious: tuple[PackageRisk, ...]
    blocked: tuple[PackageRisk, ...]
    errors: tuple[str, ...]
    validation_time_ms: int
```

**Design Decisions:**
- Use `frozen=True` for immutability (security, hashability)
- Use `tuple` instead of `list` for immutable collections
- Use `str, Enum` for JSON serialization compatibility

---

### 2. Registry Base (`src/phantom_guard/registry/base.py`)

**Responsibility:** Define interface for all registry clients.

```python
from abc import ABC, abstractmethod
from typing import Optional
import httpx

from phantom_guard.core.types import PackageMetadata, Registry

class RegistryClient(ABC):
    """Abstract base class for registry clients."""

    registry: Registry
    base_url: str
    timeout: float = 10.0

    def __init__(self, client: Optional[httpx.AsyncClient] = None):
        self._client = client
        self._owns_client = client is None

    async def __aenter__(self) -> "RegistryClient":
        if self._owns_client:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self

    async def __aexit__(self, *args) -> None:
        if self._owns_client and self._client:
            await self._client.aclose()

    @abstractmethod
    async def fetch_metadata(self, package_name: str) -> PackageMetadata:
        """Fetch package metadata from registry.

        Args:
            package_name: Name of the package to look up.

        Returns:
            PackageMetadata with exists=False if not found.

        Raises:
            RegistryError: On network/API errors.
        """
        ...

    @abstractmethod
    async def package_exists(self, package_name: str) -> bool:
        """Check if package exists (faster than full metadata)."""
        ...

class RegistryError(Exception):
    """Error communicating with package registry."""
    pass
```

**Design Decisions:**
- Async-first for concurrent validation
- Context manager for resource cleanup
- Allow injecting httpx client for testing
- Separate `package_exists` for fast checks

---

### 3. PyPI Client (`src/phantom_guard/registry/pypi.py`)

**Responsibility:** Fetch package metadata from PyPI.

```python
from datetime import datetime
from typing import Any, Optional
import httpx

from phantom_guard.core.types import PackageMetadata, Registry
from phantom_guard.registry.base import RegistryClient, RegistryError

class PyPIClient(RegistryClient):
    """Client for PyPI package registry."""

    registry = Registry.PYPI
    base_url = "https://pypi.org/pypi"

    async def package_exists(self, package_name: str) -> bool:
        url = f"{self.base_url}/{package_name}/json"
        try:
            response = await self._client.head(url)
            return response.status_code == 200
        except httpx.HTTPError:
            return False

    async def fetch_metadata(self, package_name: str) -> PackageMetadata:
        url = f"{self.base_url}/{package_name}/json"

        try:
            response = await self._client.get(url)
        except httpx.TimeoutException as e:
            raise RegistryError(f"Timeout fetching {package_name}") from e
        except httpx.HTTPError as e:
            raise RegistryError(f"HTTP error for {package_name}: {e}") from e

        if response.status_code == 404:
            return PackageMetadata(
                name=package_name,
                registry=Registry.PYPI,
                exists=False,
            )

        if response.status_code != 200:
            raise RegistryError(
                f"Unexpected status {response.status_code} for {package_name}"
            )

        return self._parse_response(package_name, response.json())

    def _parse_response(self, name: str, data: dict[str, Any]) -> PackageMetadata:
        info = data.get("info", {})
        releases = data.get("releases", {})

        # Extract repository URL
        project_urls = info.get("project_urls") or {}
        has_repo = any(
            "github" in (url or "").lower() or "gitlab" in (url or "").lower()
            for url in project_urls.values()
        )

        # Get description
        description = info.get("description") or info.get("summary") or ""

        return PackageMetadata(
            name=name,
            registry=Registry.PYPI,
            exists=True,
            release_count=len(releases),
            has_repository=has_repo,
            has_author=bool(info.get("author") or info.get("author_email")),
            has_description=len(description) > 20,
        )
```

**API Endpoint:** `https://pypi.org/pypi/{package}/json`

---

### 4. npm Client (`src/phantom_guard/registry/npm.py`)

**Responsibility:** Fetch package metadata from npm registry.

```python
class NpmClient(RegistryClient):
    """Client for npm package registry."""

    registry = Registry.NPM
    base_url = "https://registry.npmjs.org"

    async def fetch_metadata(self, package_name: str) -> PackageMetadata:
        url = f"{self.base_url}/{package_name}"
        # Similar implementation to PyPI
        # Parse: versions, repository, author, description
```

**API Endpoint:** `https://registry.npmjs.org/{package}`

---

### 5. crates.io Client (`src/phantom_guard/registry/crates.py`)

**Responsibility:** Fetch package metadata from crates.io.

```python
class CratesClient(RegistryClient):
    """Client for crates.io package registry."""

    registry = Registry.CRATES
    base_url = "https://crates.io/api/v1/crates"

    def __init__(self, client: Optional[httpx.AsyncClient] = None):
        super().__init__(client)
        # crates.io requires User-Agent
        if self._owns_client:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                headers={"User-Agent": "PhantomGuard/0.1.0"}
            )
```

**API Endpoint:** `https://crates.io/api/v1/crates/{package}`
**Note:** Requires `User-Agent` header.

---

### 6. Risk Scorer (`src/phantom_guard/core/scorer.py`)

**Responsibility:** Calculate risk score from metadata and signals.

```python
from phantom_guard.core.types import (
    PackageMetadata, PackageRisk, RiskLevel, RiskSignal, SignalType
)

# Scoring weights (validated in TECHNICAL_VALIDATION.md)
SCORE_WEIGHTS = {
    "releases_10_plus": 30,
    "releases_3_to_9": 15,
    "has_repository": 30,
    "has_author": 20,
    "has_description": 20,
}

THRESHOLDS = {
    "safe": 60,
    "suspicious": 30,
}

class RiskScorer:
    """Calculate risk scores for packages."""

    def score(self, metadata: PackageMetadata) -> PackageRisk:
        """Calculate risk score from package metadata."""
        if not metadata.exists:
            return self._not_found_result(metadata)

        signals: list[RiskSignal] = []
        score = 0

        # Release count signal
        if metadata.release_count >= 10:
            score += SCORE_WEIGHTS["releases_10_plus"]
        elif metadata.release_count >= 3:
            score += SCORE_WEIGHTS["releases_3_to_9"]
            signals.append(RiskSignal(
                SignalType.FEW_RELEASES,
                weight=-15,
                details=f"Only {metadata.release_count} releases"
            ))
        else:
            signals.append(RiskSignal(
                SignalType.FEW_RELEASES,
                weight=-30,
                details=f"Only {metadata.release_count} releases"
            ))

        # Repository signal
        if metadata.has_repository:
            score += SCORE_WEIGHTS["has_repository"]
        else:
            signals.append(RiskSignal(
                SignalType.NO_REPOSITORY,
                weight=-30,
                details="No repository URL found"
            ))

        # Author signal
        if metadata.has_author:
            score += SCORE_WEIGHTS["has_author"]
        else:
            signals.append(RiskSignal(
                SignalType.NO_AUTHOR,
                weight=-20,
                details="No author information"
            ))

        # Description signal
        if metadata.has_description:
            score += SCORE_WEIGHTS["has_description"]
        else:
            signals.append(RiskSignal(
                SignalType.NO_DESCRIPTION,
                weight=-20,
                details="No or minimal description"
            ))

        # Determine risk level
        risk_level = self._score_to_level(score)

        return PackageRisk(
            package_name=metadata.name,
            registry=metadata.registry,
            risk_level=risk_level,
            risk_score=min(100, max(0, score)),
            signals=tuple(signals),
            recommendation=self._get_recommendation(risk_level),
            metadata=metadata,
        )

    def _score_to_level(self, score: int) -> RiskLevel:
        if score >= THRESHOLDS["safe"]:
            return RiskLevel.SAFE
        elif score >= THRESHOLDS["suspicious"]:
            return RiskLevel.SUSPICIOUS
        else:
            return RiskLevel.HIGH_RISK

    def _not_found_result(self, metadata: PackageMetadata) -> PackageRisk:
        return PackageRisk(
            package_name=metadata.name,
            registry=metadata.registry,
            risk_level=RiskLevel.NOT_FOUND,
            risk_score=0,
            signals=(RiskSignal(
                SignalType.NOT_FOUND,
                weight=-100,
                details="Package does not exist in registry"
            ),),
            recommendation="BLOCK: Package not found. Likely hallucinated by AI.",
            metadata=metadata,
        )

    def _get_recommendation(self, level: RiskLevel) -> str:
        recommendations = {
            RiskLevel.SAFE: "Package appears legitimate.",
            RiskLevel.SUSPICIOUS: "CAUTION: Package has suspicious characteristics. Verify before installing.",
            RiskLevel.HIGH_RISK: "WARNING: High risk package. Do not install without thorough review.",
            RiskLevel.NOT_FOUND: "BLOCK: Package not found. Likely hallucinated by AI.",
        }
        return recommendations[level]
```

---

### 7. Pattern Matcher (`src/phantom_guard/core/patterns.py`)

**Responsibility:** Detect hallucination patterns in package names.

```python
import re
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class HallucinationPattern:
    """Pattern that suggests AI hallucination."""
    pattern: str
    description: str
    examples: tuple[str, ...]

# Common hallucination patterns
HALLUCINATION_PATTERNS: tuple[HallucinationPattern, ...] = (
    HallucinationPattern(
        pattern=r"^(flask|django|fastapi|express|react|vue|angular)-?(gpt|ai|chatgpt|openai|llm|ml)",
        description="Popular framework + AI suffix",
        examples=("flask-gpt", "django-chatgpt", "react-ai"),
    ),
    HallucinationPattern(
        pattern=r"^(gpt|chatgpt|openai|claude|anthropic)-?(api|client|sdk|wrapper|helper|utils)",
        description="AI provider + generic suffix",
        examples=("gpt-api", "openai-helper", "chatgpt-wrapper"),
    ),
    HallucinationPattern(
        pattern=r"^py(gpt|openai|chatgpt|claude|anthropic)",
        description="py + AI provider name",
        examples=("pygpt", "pyopenai", "pychatgpt"),
    ),
    HallucinationPattern(
        pattern=r"^(easy|simple|quick|fast|super|auto)-?(gpt|ai|openai|chatgpt)",
        description="Simplicity prefix + AI term",
        examples=("easy-gpt", "simple-ai", "auto-chatgpt"),
    ),
)

class PatternMatcher:
    """Match package names against hallucination patterns."""

    def __init__(self, patterns: Optional[tuple[HallucinationPattern, ...]] = None):
        self.patterns = patterns or HALLUCINATION_PATTERNS
        self._compiled = [
            (re.compile(p.pattern, re.IGNORECASE), p)
            for p in self.patterns
        ]

    def match(self, package_name: str) -> Optional[HallucinationPattern]:
        """Check if package name matches any hallucination pattern.

        Returns:
            Matching pattern, or None if no match.
        """
        for regex, pattern in self._compiled:
            if regex.match(package_name):
                return pattern
        return None

    def is_suspicious_name(self, package_name: str) -> bool:
        """Quick check if name is suspicious."""
        return self.match(package_name) is not None
```

---

### 8. Detector (`src/phantom_guard/core/detector.py`)

**Responsibility:** Orchestrate the complete validation pipeline.

```python
import asyncio
from typing import Sequence
import time

from phantom_guard.core.types import (
    PackageRisk, Registry, RiskLevel, ValidationResult
)
from phantom_guard.core.scorer import RiskScorer
from phantom_guard.core.patterns import PatternMatcher
from phantom_guard.registry.base import RegistryClient, RegistryError
from phantom_guard.registry.pypi import PyPIClient
from phantom_guard.registry.npm import NpmClient
from phantom_guard.registry.crates import CratesClient

class Detector:
    """Main detection engine for slopsquatting attacks."""

    def __init__(
        self,
        scorer: RiskScorer | None = None,
        pattern_matcher: PatternMatcher | None = None,
    ):
        self.scorer = scorer or RiskScorer()
        self.pattern_matcher = pattern_matcher or PatternMatcher()

    async def check_package(
        self,
        package_name: str,
        registry: Registry = Registry.PYPI,
    ) -> PackageRisk:
        """Check a single package for slopsquatting risk."""
        client = self._get_client(registry)

        async with client:
            metadata = await client.fetch_metadata(package_name)

        result = self.scorer.score(metadata)

        # Add pattern match signal if applicable
        if pattern := self.pattern_matcher.match(package_name):
            # Pattern match adds additional suspicion
            result = self._add_pattern_signal(result, pattern)

        return result

    async def check_packages(
        self,
        packages: Sequence[str],
        registry: Registry = Registry.PYPI,
    ) -> ValidationResult:
        """Check multiple packages concurrently."""
        start_time = time.monotonic()

        safe: list[str] = []
        suspicious: list[PackageRisk] = []
        blocked: list[PackageRisk] = []
        errors: list[str] = []

        client = self._get_client(registry)

        async with client:
            tasks = [
                self._check_one(client, pkg)
                for pkg in packages
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

        for pkg, result in zip(packages, results):
            if isinstance(result, Exception):
                errors.append(f"{pkg}: {result}")
            elif result.risk_level == RiskLevel.SAFE:
                safe.append(pkg)
            elif result.risk_level == RiskLevel.NOT_FOUND:
                blocked.append(result)
            else:
                suspicious.append(result)

        elapsed_ms = int((time.monotonic() - start_time) * 1000)

        return ValidationResult(
            safe=tuple(safe),
            suspicious=tuple(suspicious),
            blocked=tuple(blocked),
            errors=tuple(errors),
            validation_time_ms=elapsed_ms,
        )

    async def _check_one(
        self,
        client: RegistryClient,
        package_name: str,
    ) -> PackageRisk:
        """Check a single package with shared client."""
        try:
            metadata = await client.fetch_metadata(package_name)
            result = self.scorer.score(metadata)

            if pattern := self.pattern_matcher.match(package_name):
                result = self._add_pattern_signal(result, pattern)

            return result
        except RegistryError as e:
            raise RuntimeError(f"Registry error: {e}") from e

    def _get_client(self, registry: Registry) -> RegistryClient:
        clients = {
            Registry.PYPI: PyPIClient,
            Registry.NPM: NpmClient,
            Registry.CRATES: CratesClient,
        }
        return clients[registry]()

    def _add_pattern_signal(
        self,
        result: PackageRisk,
        pattern,
    ) -> PackageRisk:
        """Add hallucination pattern signal to result."""
        from phantom_guard.core.types import RiskSignal, SignalType

        new_signals = result.signals + (RiskSignal(
            SignalType.HALLUCINATION_PATTERN,
            weight=-20,
            details=f"Name matches pattern: {pattern.description}",
        ),)

        # Recalculate risk level with pattern penalty
        new_score = max(0, result.risk_score - 20)

        if new_score >= 60:
            new_level = RiskLevel.SAFE
        elif new_score >= 30:
            new_level = RiskLevel.SUSPICIOUS
        else:
            new_level = RiskLevel.HIGH_RISK

        return PackageRisk(
            package_name=result.package_name,
            registry=result.registry,
            risk_level=new_level,
            risk_score=new_score,
            signals=new_signals,
            recommendation=result.recommendation,
            metadata=result.metadata,
        )
```

---

## File Structure (P1)

```
src/phantom_guard/
├── __init__.py           # Public API exports
├── py.typed              # PEP 561 marker
├── core/
│   ├── __init__.py
│   ├── types.py          # Data models
│   ├── detector.py       # Main orchestrator
│   ├── scorer.py         # Risk scoring
│   └── patterns.py       # Pattern matching
└── registry/
    ├── __init__.py
    ├── base.py           # Abstract base class
    ├── pypi.py           # PyPI client
    ├── npm.py            # npm client
    └── crates.py         # crates.io client
```

---

## Testing Strategy

### Unit Tests

| Component | Test Focus |
|-----------|------------|
| `types.py` | Immutability, enum values, serialization |
| `scorer.py` | Score calculation, threshold boundaries, edge cases |
| `patterns.py` | Pattern matching, false positive prevention |
| `pypi.py` | Response parsing, error handling, 404 handling |
| `npm.py` | Response parsing, error handling |
| `crates.py` | User-Agent header, response parsing |
| `detector.py` | Integration, concurrency, error aggregation |

### Integration Tests

- Real API calls to PyPI/npm/crates.io with known packages
- Verify flask/django/requests score as SAFE
- Verify non-existent packages return NOT_FOUND
- Verify suspicious patterns are flagged

### Performance Tests

- Single package < 200ms
- 50 packages < 5s
- Pattern matching < 1ms

---

## Security Considerations

| Threat | Mitigation |
|--------|------------|
| Package name injection | Validate against `^[a-zA-Z0-9._-]+$` regex |
| Response manipulation | Validate JSON structure, handle unexpected fields |
| DoS via slow responses | 10s timeout per request |
| Information leakage | Don't log API keys or raw responses |

---

## Implementation Order

1. **types.py** - Data models (foundation)
2. **base.py** - Registry interface
3. **pypi.py** - PyPI client (most important registry)
4. **scorer.py** - Risk scoring
5. **patterns.py** - Pattern matching
6. **detector.py** - Integration
7. **npm.py** - npm client
8. **crates.py** - crates.io client
9. **__init__.py** - Public API

---

## Exit Criteria (P1)

- [ ] Can fetch metadata from PyPI, npm, crates.io
- [ ] Can score "flask" as SAFE (score >= 60)
- [ ] Can score non-existent package as NOT_FOUND/BLOCKED
- [ ] Pattern matching identifies "flask-gpt" as suspicious
- [ ] All tests pass
- [ ] mypy passes
- [ ] ruff passes
- [ ] **HOSTILE REVIEW PASSED**
