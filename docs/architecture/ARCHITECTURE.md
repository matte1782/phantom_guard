# Phantom Guard — System Architecture

> **Version**: 0.1.0
> **Date**: 2025-12-24
> **Status**: APPROVED (CONDITIONAL_GO with P0 fixes applied)
> **Approver**: HOSTILE_VALIDATOR
> **Gate**: 1 of 6 - COMPLETE

---

## 1. Overview

### 1.1 System Purpose

Phantom Guard is a library that detects and prevents AI-hallucinated dependency attacks (slopsquatting) before they compromise your software supply chain.

**Problem**: AI coding assistants hallucinate package names at a 20% rate. Attackers register these phantom names with malware. No tool specifically detects these attacks.

**Solution**: Intercept package installations, validate against registry metadata, and score risk based on signals that differentiate legitimate packages from slopsquatting attacks.

### 1.2 Success Criteria (from Gate 0)

| Criterion | Target | Measurement |
|:----------|:-------|:------------|
| False Positive Rate | <5% | Real-world testing against top 1000 packages |
| True Positive Rate | >95% | Detection of known phantom packages |
| Detection Latency | <200ms | Per-package validation time |
| Batch Performance | <5s | 50 packages concurrent |

### 1.3 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PHANTOM GUARD v0.1.0                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                        CLI LAYER (S010-S019)                         │    │
│  │  ├── phantom-guard check <file>      # Validate dependency file      │    │
│  │  ├── phantom-guard validate <pkg>    # Check single package          │    │
│  │  └── phantom-guard watch             # Monitor installations         │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                       CORE LAYER (S001-S009)                         │    │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐      │    │
│  │  │    Detector     │  │    Analyzer     │  │     Scorer      │      │    │
│  │  │   (S001-S003)   │  │   (S004-S006)   │  │   (S007-S009)   │      │    │
│  │  │                 │  │                 │  │                 │      │    │
│  │  │ - Orchestration │  │ - Pattern match │  │ - Risk scoring  │      │    │
│  │  │ - Batch process │  │ - Signal extract│  │ - Thresholds    │      │    │
│  │  │ - Result merge  │  │ - Heuristics    │  │ - Recommendations│     │    │
│  │  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘      │    │
│  │           │                    │                    │               │    │
│  └───────────┼────────────────────┼────────────────────┼───────────────┘    │
│              │                    │                    │                    │
│              ▼                    ▼                    ▼                    │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                     REGISTRY LAYER (S020-S039)                       │    │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐      │    │
│  │  │   PyPI Client   │  │   npm Client    │  │ crates.io Client│      │    │
│  │  │   (S020-S026)   │  │   (S027-S032)   │  │   (S033-S039)   │      │    │
│  │  │                 │  │                 │  │                 │      │    │
│  │  │ - Exists check  │  │ - Exists check  │  │ - Exists check  │      │    │
│  │  │ - Metadata fetch│  │ - Metadata fetch│  │ - Metadata fetch│      │    │
│  │  │ - Stats fetch   │  │ - Stats fetch   │  │ - Stats fetch   │      │    │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                     CACHE LAYER (S040-S049)                          │    │
│  │  ├── In-memory LRU cache (hot packages)                              │    │
│  │  ├── SQLite persistent cache (cold storage)                          │    │
│  │  └── TTL management (configurable expiry)                            │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                     PATTERNS LAYER (S050-S059)                       │    │
│  │  ├── Hallucination pattern database                                  │    │
│  │  ├── Typosquatting detection                                         │    │
│  │  └── Popular package registry (allowlist)                            │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Requirement Extraction

### 2.1 Functional Requirements

| ID | Requirement | Source | Priority |
|:---|:------------|:-------|:---------|
| FR001 | Validate single package against registry | PROJECT_FOUNDATION | P0 |
| FR002 | Batch validate dependency files (requirements.txt, package.json) | PROJECT_FOUNDATION | P0 |
| FR003 | Return risk score [0.0, 1.0] for each package | PROJECT_FOUNDATION | P0 |
| FR004 | Provide actionable recommendation (SAFE/SUSPICIOUS/BLOCK) | PROJECT_FOUNDATION | P0 |
| FR005 | Support PyPI registry | PROJECT_FOUNDATION | P0 |
| FR006 | Support npm registry | PROJECT_FOUNDATION | P1 |
| FR007 | Support crates.io registry | PROJECT_FOUNDATION | P1 |
| FR008 | Detect typosquatting against popular packages | PROJECT_FOUNDATION | P1 |
| FR009 | Match AI hallucination patterns | PROJECT_FOUNDATION | P0 |
| FR010 | CLI interface for manual validation | PROJECT_FOUNDATION | P0 |
| FR011 | Pre-commit hook integration | PROJECT_FOUNDATION | P1 |
| FR012 | pip install hook | PROJECT_FOUNDATION | P1 |

### 2.2 Non-Functional Requirements

| ID | Requirement | Target | Measurement |
|:---|:------------|:-------|:------------|
| NFR001 | Detection latency (uncached) | <200ms | P99 per package |
| NFR002 | Detection latency (cached) | <10ms | P99 per package |
| NFR003 | Batch validation (50 packages) | <5s | P99 total time |
| NFR004 | False positive rate | <5% | Against top 1000 packages |
| NFR005 | True positive rate | >95% | Against known phantoms |
| NFR006 | Memory usage | <50MB | Peak during batch |
| NFR007 | Offline mode support | 100% cached | No network calls |
| NFR008 | Pattern matching | <1ms | P99 per pattern |

### 2.3 Constraints

| ID | Constraint | Rationale |
|:---|:-----------|:----------|
| CON001 | Python 3.11+ | Modern features, type hints |
| CON002 | Minimal dependencies | httpx, typer, pydantic, aiosqlite |
| CON003 | No shell execution | Security: avoid injection |
| CON004 | Async-first | Performance: concurrent registry calls |
| CON005 | Type hints on all public API | Quality: mypy strict |
| CON006 | MIT License | Adoption: enterprise-friendly |

---

## 3. Component Specifications

### 3.1 Core Detection Engine

#### S001: Package Validator

```python
# SPEC_ID: S001
# IMPLEMENTS: FR001, FR003, FR004
# INVARIANTS: INV001, INV002, INV003

async def validate_package(
    name: str,
    registry: Registry = Registry.PYPI,
    *,
    use_cache: bool = True,
    timeout: float = 5.0,
) -> PackageRisk:
    """
    Validate a single package against a registry.

    Args:
        name: Package name to validate
        registry: Target registry (PYPI, NPM, CRATES)
        use_cache: Whether to use cached results
        timeout: Maximum time for network operations

    Returns:
        PackageRisk with risk_score, signals, and recommendation

    Raises:
        ValidationError: If name is invalid
        RegistryError: If registry is unreachable (after retries)

    Performance:
        - Uncached: <200ms P99
        - Cached: <10ms P99
    """
```

#### S002: Batch Validator

```python
# SPEC_ID: S002
# IMPLEMENTS: FR002
# INVARIANTS: INV004, INV005

async def validate_dependencies(
    dependencies: list[str],
    registry: Registry = Registry.PYPI,
    *,
    concurrency: int = 10,
    fail_fast: bool = False,
) -> ValidationResult:
    """
    Validate multiple packages concurrently.

    Args:
        dependencies: List of package names
        registry: Target registry
        concurrency: Max concurrent validations
        fail_fast: Stop on first HIGH_RISK package

    Returns:
        ValidationResult containing safe, suspicious, and blocked lists

    Performance:
        - 50 packages: <5s P99
    """
```

#### S003: Detection Orchestrator

```python
# SPEC_ID: S003
# IMPLEMENTS: FR001, FR002
# INVARIANTS: INV006

class Detector:
    """
    Central orchestration for all detection operations.

    Coordinates:
        - Registry client selection
        - Cache lookup/storage
        - Analyzer invocation
        - Scorer calculation
        - Result aggregation
    """

    def __init__(
        self,
        cache: Cache | None = None,
        pattern_db: PatternDatabase | None = None,
        config: DetectorConfig | None = None,
    ) -> None: ...
```

### 3.2 Analyzer Component

#### S004: Signal Extractor

```python
# SPEC_ID: S004
# IMPLEMENTS: FR009
# INVARIANTS: INV007

def extract_signals(metadata: PackageMetadata) -> list[Signal]:
    """
    Extract risk signals from package metadata.

    Signals extracted:
        - SIGNAL_NEW_PACKAGE: Created < 30 days ago
        - SIGNAL_LOW_DOWNLOADS: < 1000 monthly downloads
        - SIGNAL_NO_REPO: Missing repository URL
        - SIGNAL_FEW_RELEASES: < 3 versions
        - SIGNAL_NO_AUTHOR: Missing maintainer info
        - SIGNAL_SHORT_DESCRIPTION: Description < 20 chars
        - SIGNAL_HALLUCINATION_PATTERN: Matches known patterns
        - SIGNAL_TYPOSQUAT: Similar to popular package

    Performance:
        - <1ms per package
    """
```

#### S005: Pattern Matcher

```python
# SPEC_ID: S005
# IMPLEMENTS: FR008, FR009
# INVARIANTS: INV008

def match_hallucination_pattern(name: str) -> PatternMatch | None:
    """
    Check if package name matches known AI hallucination patterns.

    Patterns:
        - {popular}-gpt, {popular}-ai, {popular}-chatgpt
        - {popular}-helper, {popular}-utils, {popular}-wrapper
        - {popular}-client, {popular}-sdk, {popular}-api
        - common-*, easy-*, simple-*, auto-*

    Performance:
        - <1ms per check
    """
```

#### S006: Typosquat Detector

```python
# SPEC_ID: S006
# IMPLEMENTS: FR008
# INVARIANTS: INV009

def detect_typosquat(
    name: str,
    popular_packages: set[str],
    threshold: float = 0.85,
) -> TyposquatMatch | None:
    """
    Check if name is a typosquat of a popular package.

    Methods:
        - Levenshtein distance (edit distance <= 2)
        - Keyboard adjacency (qwerty mistakes)
        - Common substitutions (0/o, 1/l, -/_)

    Performance:
        - <1ms per check against 1000 popular packages
    """
```

### 3.3 Scorer Component

#### S007: Risk Calculator

```python
# SPEC_ID: S007
# IMPLEMENTS: FR003
# INVARIANTS: INV001, INV010

def calculate_risk_score(signals: list[Signal]) -> float:
    """
    Calculate risk score from signals.

    Scoring weights (from TECHNICAL_VALIDATION.md):
        - Releases >= 10:        -30 points (safer)
        - Releases 3-9:          -15 points
        - Has repository:        -30 points
        - Has author:            -20 points
        - Has description (>20): -20 points
        - Hallucination pattern: +40 points (riskier)
        - New package (<30d):    +30 points
        - Low downloads:         +20 points
        - Typosquat match:       +50 points

    Normalization (P0-INV-001 FIX):
        Raw score range: [-100, +160] (all negative vs all positive)
        Formula: normalized = (raw_score + 100) / 260
        Clamping: result = max(0.0, min(1.0, normalized))

        Examples:
        - All safe signals (-100): (−100 + 100) / 260 = 0.0
        - No signals (0): (0 + 100) / 260 = 0.38
        - All risk signals (+160): (160 + 100) / 260 = 1.0

    Returns:
        Score in [0.0, 1.0] where:
        - 0.0 = completely safe
        - 1.0 = definitely malicious

    Invariant:
        INV001: Result always in [0.0, 1.0] (enforced by clamping)
    """
```

#### S008: Threshold Evaluator

```python
# SPEC_ID: S008
# IMPLEMENTS: FR004
# INVARIANTS: INV011

def evaluate_recommendation(
    risk_score: float,
    config: ThresholdConfig | None = None,
) -> Recommendation:
    """
    Convert risk score to actionable recommendation.

    Default thresholds:
        - SAFE: risk_score < 0.3
        - SUSPICIOUS: 0.3 <= risk_score < 0.7
        - HIGH_RISK: risk_score >= 0.7

    Returns:
        Recommendation enum value
    """
```

#### S009: Result Aggregator

```python
# SPEC_ID: S009
# IMPLEMENTS: FR002
# INVARIANTS: INV012

def aggregate_results(
    results: list[PackageRisk],
) -> ValidationResult:
    """
    Aggregate individual package results into summary.

    Returns:
        ValidationResult with:
        - safe: list of SAFE packages
        - suspicious: list of SUSPICIOUS packages
        - blocked: list of HIGH_RISK packages
        - summary: overall verdict
    """
```

### 3.4 Registry Clients

#### S020-S026: PyPI Client

```python
# SPEC_ID: S020
# IMPLEMENTS: FR005
# INVARIANTS: INV013, INV014

class PyPIClient(RegistryClient):
    """
    PyPI registry client.

    Endpoints:
        - https://pypi.org/pypi/{package}/json (metadata)
        - https://pypistats.org/api/packages/{package}/recent (downloads)

    Rate limits:
        - No explicit limit (tested 50 concurrent OK)
        - Implement exponential backoff anyway

    Timeout:
        - 5s per request (configurable)
        - 3 retries with backoff
    """

    async def exists(self, name: str) -> bool: ...  # S021
    async def get_metadata(self, name: str) -> PackageMetadata: ...  # S022
    async def get_downloads(self, name: str) -> int: ...  # S023
```

#### S027-S032: npm Client

```python
# SPEC_ID: S027
# IMPLEMENTS: FR006
# INVARIANTS: INV013, INV014

class NpmClient(RegistryClient):
    """
    npm registry client.

    Endpoints:
        - https://registry.npmjs.org/{package} (metadata)
        - https://api.npmjs.org/downloads/point/last-week/{package} (downloads)
    """
```

#### S033-S039: crates.io Client

```python
# SPEC_ID: S033
# IMPLEMENTS: FR007
# INVARIANTS: INV013, INV014, INV015

class CratesClient(RegistryClient):
    """
    crates.io registry client.

    Endpoints:
        - https://crates.io/api/v1/crates/{package} (metadata)
        - https://crates.io/api/v1/crates/{package}/owners (maintainers)

    Required headers:
        - User-Agent: PhantomGuard/0.1.0 (REQUIRED by crates.io)
    """
```

### 3.5 Cache Layer

#### S040-S049: Cache System

```python
# SPEC_ID: S040
# IMPLEMENTS: NFR002, NFR007
# INVARIANTS: INV016, INV017

class Cache:
    """
    Two-tier caching system.

    Tier 1: In-memory LRU (hot packages)
        - Max 1000 entries
        - TTL: 1 hour
        - Size: ~200KB

    Tier 2: SQLite persistent (cold storage)
        - Max 100,000 entries
        - TTL: 24 hours
        - Size: ~10MB

    Cache key format:
        {registry}:{package_name}:{version_hash}
    """

    async def get(self, key: str) -> CacheEntry | None: ...  # S041
    async def set(self, key: str, entry: CacheEntry) -> None: ...  # S042
    async def invalidate(self, pattern: str) -> int: ...  # S043
```

### 3.6 Patterns Database

#### S050-S059: Pattern System

```python
# SPEC_ID: S050
# IMPLEMENTS: FR009
# INVARIANTS: INV018

class PatternDatabase:
    """
    Hallucination pattern storage and matching.

    Pattern types:
        - SUFFIX: {popular}-gpt, {popular}-ai
        - PREFIX: easy-, simple-, auto-
        - COMPOUND: {framework}-{ai_term}-{suffix}

    Storage:
        - Built-in patterns (compiled)
        - User patterns (config file)
        - Community patterns (optional download)
    """

    def match(self, name: str) -> list[PatternMatch]: ...  # S051
    def add_pattern(self, pattern: Pattern) -> None: ...  # S052
```

---

## 4. Data Structures

### 4.1 Core Types

```python
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

# === Enums (1 byte each) ===

class Registry(Enum):
    """SPEC: S020, S027, S033"""
    PYPI = "pypi"
    NPM = "npm"
    CRATES = "crates"

class Recommendation(Enum):
    """SPEC: S008"""
    SAFE = "safe"           # Proceed with installation
    SUSPICIOUS = "suspicious"  # Warn user, ask confirmation
    HIGH_RISK = "high_risk"    # Block installation
    NOT_FOUND = "not_found"    # Package doesn't exist

class Signal(Enum):
    """SPEC: S004"""
    NEW_PACKAGE = "new_package"          # Created < 30 days
    LOW_DOWNLOADS = "low_downloads"      # < 1000/month
    NO_REPOSITORY = "no_repository"      # Missing repo URL
    FEW_RELEASES = "few_releases"        # < 3 versions
    NO_AUTHOR = "no_author"              # Missing maintainer
    SHORT_DESCRIPTION = "short_description"  # < 20 chars
    HALLUCINATION_PATTERN = "hallucination_pattern"
    TYPOSQUAT = "typosquat"


# === Core Data Structures ===

@dataclass(frozen=True, slots=True)
class PackageMetadata:
    """
    SPEC: S022
    Size: ~500 bytes typical
    """
    name: str                    # 8 bytes (pointer) + string
    version: str                 # 8 bytes (pointer) + string
    description: str             # 8 bytes (pointer) + string
    author: str | None           # 8 bytes
    repository_url: str | None   # 8 bytes
    created_at: datetime | None  # 8 bytes
    release_count: int           # 8 bytes
    download_count: int          # 8 bytes
    registry: Registry           # 1 byte


@dataclass(frozen=True, slots=True)
class PackageRisk:
    """
    SPEC: S001, S007
    Size: ~200 bytes typical
    INVARIANT: INV001 - risk_score in [0.0, 1.0]
    INVARIANT: INV002 - signals is never None
    """
    name: str                    # 8 bytes (pointer)
    risk_score: float            # 8 bytes
    signals: tuple[Signal, ...]  # 8 bytes (pointer)
    recommendation: Recommendation  # 1 byte
    registry: Registry           # 1 byte
    metadata: PackageMetadata | None  # 8 bytes (optional)

    def __post_init__(self):
        # INV001 enforcement
        assert 0.0 <= self.risk_score <= 1.0, f"risk_score {self.risk_score} out of range"


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """
    SPEC: S002, S009
    Size: depends on package count
    """
    safe: tuple[PackageRisk, ...]
    suspicious: tuple[PackageRisk, ...]
    blocked: tuple[PackageRisk, ...]
    not_found: tuple[str, ...]
    total_packages: int
    scan_duration_ms: float


@dataclass(frozen=True, slots=True)
class PatternMatch:
    """
    SPEC: S005
    Size: ~100 bytes
    """
    pattern_id: str
    pattern_type: str  # "suffix", "prefix", "compound"
    matched_against: str  # The popular package matched
    confidence: float  # 0.0 - 1.0


@dataclass(frozen=True, slots=True)
class CacheEntry:
    """
    SPEC: S040
    Size: ~700 bytes (metadata + overhead)
    """
    key: str
    package_risk: PackageRisk
    created_at: datetime
    expires_at: datetime
```

### 4.2 Configuration Types

```python
@dataclass
class DetectorConfig:
    """
    SPEC: S003
    Size: ~200 bytes
    """
    # Thresholds
    suspicious_threshold: float = 0.3
    high_risk_threshold: float = 0.7

    # Performance
    request_timeout: float = 5.0
    max_concurrency: int = 10
    retry_count: int = 3

    # Cache
    cache_ttl_seconds: int = 3600
    max_cache_entries: int = 10000

    # Offline mode
    offline_mode: bool = False
    require_cache_hit: bool = False


@dataclass
class ThresholdConfig:
    """
    SPEC: S008
    Size: ~50 bytes
    """
    safe_max: float = 0.3
    suspicious_max: float = 0.7
    # Anything >= suspicious_max is HIGH_RISK
```

### 4.3 Size Summary

| Structure | Typical Size | Max Instances | Max Total |
|:----------|:-------------|:--------------|:----------|
| PackageMetadata | 500B | 1,000 | 500KB |
| PackageRisk | 200B | 1,000 | 200KB |
| ValidationResult | 1KB | 10 | 10KB |
| CacheEntry | 700B | 100,000 | 70MB |
| PatternMatch | 100B | 100 | 10KB |
| DetectorConfig | 200B | 1 | 200B |

**Peak memory estimate**: <100MB for largest batch (1000 packages)

---

## 5. Performance Budget

### 5.1 Operation Budgets

| Operation | Budget | Constraint | SPEC_ID | Benchmark |
|:----------|:-------|:-----------|:--------|:----------|
| validate_package (uncached) | <200ms | P99 | S001 | bench_validate_uncached |
| validate_package (cached) | <10ms | P99 | S001 | bench_validate_cached |
| validate_dependencies (50) | <5s | P99 | S002 | bench_batch_50 |
| pattern_match | <1ms | P99 | S005 | bench_pattern |
| typosquat_check | <1ms | P99 | S006 | bench_typosquat |
| calculate_risk_score | <0.1ms | P99 | S007 | bench_scorer |
| cache_get | <0.5ms | P99 | S041 | bench_cache_get |
| cache_set | <1ms | P99 | S042 | bench_cache_set |
| registry_api_call | <500ms | P99 | S020+ | network_dependent |

### 5.2 Memory Budgets

| Component | Budget | Measurement |
|:----------|:-------|:------------|
| In-memory cache | <10MB | len(cache) * sizeof(CacheEntry) |
| SQLite cache | <50MB | database file size |
| Pattern database | <5MB | loaded patterns |
| Peak batch operation | <100MB | during 1000-package scan |
| Idle memory | <20MB | after initialization |

### 5.3 Concurrency Budgets

| Resource | Limit | Rationale |
|:---------|:------|:----------|
| Concurrent registry requests | 10 | Avoid rate limiting |
| Connection pool size | 20 | httpx default |
| Cache write concurrency | 1 | SQLite limitation |
| Pattern matching threads | 1 | CPU-bound, fast enough |

---

## 6. Invariant Registry

| INV_ID | Statement | Component | Enforcement | Test Type |
|:-------|:----------|:----------|:------------|:----------|
| INV001 | risk_score always in [0.0, 1.0] | Scorer | assert + property | proptest |
| INV002 | signals tuple never None (empty tuple OK) | PackageRisk | type system | unit |
| INV003 | cached results match uncached | Detector | comparison test | integration |
| INV004 | batch results contain all inputs | Detector | set equality | unit |
| INV005 | fail_fast stops on first HIGH_RISK | Detector | order check | unit |
| INV006 | Detector always returns PackageRisk | Detector | type check | mypy |
| INV007 | extract_signals is pure (no side effects) | Analyzer | no I/O calls | unit |
| INV008 | pattern_match returns None or valid match | Analyzer | type check | unit |
| INV009 | typosquat threshold in (0, 1) | Analyzer | assert | unit |
| INV010 | higher risk = higher score | Scorer | monotonicity | proptest |
| INV011 | recommendation thresholds are ordered | Scorer | safe < suspicious < high | unit |
| INV012 | aggregate preserves all inputs | Aggregator | count check | unit |
| INV013 | registry client returns valid metadata or raises | Client | exception handling | unit |
| INV014 | API timeout honored | Client | timeout mock | integration |
| INV015 | User-Agent header sent to crates.io | CratesClient | request inspection | integration |
| INV016 | cache TTL honored (no stale returns) | Cache | time mock | unit |
| INV017 | cache size limit enforced | Cache | len check after eviction | unit |
| INV018 | pattern database is immutable during match | PatternDB | no concurrent writes | design |

---

## 7. Architectural Decisions

### ADR-001: Python Over Rust

**SPEC_ID**: ADR001

#### Context
Need to choose implementation language. Rust would give best performance, Python gives best adoption.

#### Options Considered
1. **Rust** - Maximum performance, harder to install/contribute
2. **Python** - Good enough performance, easy pip install, large community
3. **Go** - Good performance, single binary, smaller ecosystem

#### Decision
**Python 3.11+** with async/await.

#### Consequences
- Positive: Easy adoption (pip install), familiar to target users
- Positive: Rich ecosystem (httpx, typer, pydantic)
- Positive: Easy contribution from community
- Negative: Slower than Rust (~10x for CPU-bound work)
- Neutral: Performance is acceptable (validated in TECHNICAL_VALIDATION.md)

#### Verification
- Benchmark: <200ms per package is achievable
- If performance becomes issue: rewrite hot paths in Rust (PyO3)

---

### ADR-002: Async-First Architecture

**SPEC_ID**: ADR002

#### Context
Registry API calls are I/O bound. Need concurrent execution.

#### Options Considered
1. **Threading** - GIL issues, complex error handling
2. **asyncio** - Native Python async, good httpx support
3. **multiprocessing** - Overkill for I/O bound work

#### Decision
**asyncio** with httpx async client.

#### Consequences
- Positive: Excellent I/O concurrency
- Positive: Single-threaded (no race conditions)
- Positive: httpx native async support
- Negative: Sync callers need asyncio.run()
- Neutral: Provide sync wrappers for convenience

---

### ADR-003: Two-Tier Cache Architecture

**SPEC_ID**: ADR003

#### Context
Need fast lookups for repeated packages, but also persistence across sessions.

#### Options Considered
1. **Memory only** - Fast, lost on restart
2. **SQLite only** - Persistent, slower reads
3. **Redis** - External dependency, overkill
4. **Two-tier** - Best of both worlds

#### Decision
**Two-tier cache**: In-memory LRU (hot) + SQLite (cold).

#### Consequences
- Positive: Fast reads for hot packages (<1ms)
- Positive: Persistence across sessions
- Positive: No external dependencies
- Negative: More complex cache invalidation
- Negative: Potential consistency issues (mitigated by TTL)

#### Implementation Note (P0-INV-003 FIX)
Standard `sqlite3` is blocking and incompatible with async-first architecture.

**Solution**: Use `aiosqlite` package for async SQLite access.
- Add to dependencies: `aiosqlite>=0.19.0`
- All cache operations use `async with aiosqlite.connect()`
- Alternative fallback: `asyncio.to_thread()` for stdlib sqlite3

**Performance verification**:
- aiosqlite read: <1ms typical (meets <10ms budget)
- aiosqlite write: <5ms typical (meets <1ms budget with batching)

---

### ADR-004: Frozen Dataclasses for Core Types

**SPEC_ID**: ADR004

#### Context
Core types (PackageRisk, etc.) should be immutable for safety.

#### Options Considered
1. **Regular classes** - Mutable, error-prone
2. **NamedTuple** - Immutable, limited features
3. **Pydantic models** - Validation, some overhead
4. **Frozen dataclasses** - Immutable, slots, fast

#### Decision
**Frozen dataclasses with slots** for core types.

#### Consequences
- Positive: Immutability prevents bugs
- Positive: Slots reduce memory usage
- Positive: Type hints work well
- Negative: Cannot modify after creation
- Neutral: Use builders or replace() for modifications

---

### ADR-005: Scoring Algorithm

**SPEC_ID**: ADR005

#### Context
Need to convert signals to risk score. Algorithm from TECHNICAL_VALIDATION.md.

#### Options Considered
1. **Additive scoring** - Simple, interpretable
2. **ML model** - Complex, requires training data
3. **Rule-based** - Boolean, no nuance
4. **Weighted additive** - Configurable, interpretable

#### Decision
**Weighted additive scoring** (validated in TECHNICAL_VALIDATION.md).

#### Consequences
- Positive: Interpretable (user can understand why)
- Positive: Configurable weights
- Positive: 0% false positive in testing
- Negative: May need tuning as patterns evolve
- Neutral: Can add ML layer later if needed

---

## 8. Security Considerations

### 8.1 Input Validation

| Input | Validation | SPEC_ID |
|:------|:-----------|:--------|
| Package name | Alphanumeric, hyphens, underscores only | S001 |
| Registry enum | Must be known value | S001 |
| Config values | Bounds checking | S003 |
| API responses | JSON schema validation | S020+ |

### 8.2 Security Invariants

| Invariant | Enforcement |
|:----------|:------------|
| No shell execution | No subprocess, os.system, eval |
| No arbitrary file access | Only cache directory |
| API keys not logged | Redact in error messages |
| HTTPS only | httpx default, no http:// |
| Timeout on all requests | Prevent hanging |

### 8.3 Dependency Security

| Dependency | Purpose | Security Review |
|:-----------|:--------|:----------------|
| httpx | HTTP client | Well-maintained, no known vulns |
| typer | CLI framework | Well-maintained |
| pydantic | Validation | Well-maintained |
| sqlite3 | Cache | Python stdlib, safe |

---

## 9. Trace Matrix

| SPEC_ID | Description | Component | Module | Tests |
|:--------|:------------|:----------|:-------|:------|
| S001 | Package validation | Detector | core/detector.py | T001.* |
| S002 | Batch validation | Detector | core/detector.py | T002.* |
| S003 | Detection orchestrator | Detector | core/detector.py | T003.* |
| S004 | Signal extraction | Analyzer | core/analyzer.py | T004.* |
| S005 | Pattern matching | Analyzer | core/patterns.py | T005.* |
| S006 | Typosquat detection | Analyzer | core/typosquat.py | T006.* |
| S007 | Risk calculation | Scorer | core/scorer.py | T007.* |
| S008 | Threshold evaluation | Scorer | core/scorer.py | T008.* |
| S009 | Result aggregation | Scorer | core/scorer.py | T009.* |
| S010-S019 | CLI commands | CLI | cli/main.py | T010.* |
| S020-S026 | PyPI client | Registry | registry/pypi.py | T020.* |
| S027-S032 | npm client | Registry | registry/npm.py | T027.* |
| S033-S039 | crates.io client | Registry | registry/crates.py | T033.* |
| S040-S049 | Cache system | Cache | cache/cache.py | T040.* |
| S050-S059 | Pattern database | Patterns | patterns/database.py | T050.* |

---

## 10. API Surface

### 10.1 Public API (Stable)

```python
# phantom_guard/__init__.py

# Core functions
async def validate_package(name: str, registry: str = "pypi") -> PackageRisk: ...
async def validate_dependencies(dependencies: list[str], registry: str = "pypi") -> ValidationResult: ...

# Sync wrappers
def validate_package_sync(name: str, registry: str = "pypi") -> PackageRisk: ...
def validate_dependencies_sync(dependencies: list[str], registry: str = "pypi") -> ValidationResult: ...

# Types (re-exported)
from phantom_guard.types import (
    PackageRisk,
    ValidationResult,
    Recommendation,
    Signal,
    Registry,
)

# Configuration
from phantom_guard.config import DetectorConfig, ThresholdConfig
```

### 10.2 CLI Interface

```bash
# Single package
phantom-guard validate requests
phantom-guard validate flask-gpt --registry pypi

# Dependency file
phantom-guard check requirements.txt
phantom-guard check package.json --registry npm

# Batch with output
phantom-guard check requirements.txt --output json
phantom-guard check requirements.txt --fail-on suspicious

# Watch mode (future)
phantom-guard watch --pre-install
```

---

## Appendix A: Open Questions

| Question | Impact | Resolution Target |
|:---------|:-------|:------------------|
| Should we support private registries? | Feature scope | Gate 2 |
| How to handle package name normalization? | Accuracy | Gate 2 |
| Should allowlist be built-in or configurable? | UX | Gate 2 |
| Rate limiting strategy for heavy users? | Performance | Gate 2 |

---

## Appendix B: Future Considerations (Out of Scope for v0.1.0)

- IDE plugins (VS Code, PyCharm)
- GitHub App for PR scanning
- SaaS dashboard for teams
- ML-based pattern discovery
- Private registry support
- Package version-specific analysis
- Transitive dependency analysis

---

## Appendix C: File Structure

```
phantom-guard/
├── src/
│   └── phantom_guard/
│       ├── __init__.py          # Public API
│       ├── py.typed             # PEP 561 marker
│       ├── types.py             # Core types (S001-S009)
│       ├── config.py            # Configuration
│       ├── core/
│       │   ├── __init__.py
│       │   ├── detector.py      # S001-S003
│       │   ├── analyzer.py      # S004
│       │   ├── patterns.py      # S005
│       │   ├── typosquat.py     # S006
│       │   └── scorer.py        # S007-S009
│       ├── registry/
│       │   ├── __init__.py
│       │   ├── base.py          # Abstract client
│       │   ├── pypi.py          # S020-S026
│       │   ├── npm.py           # S027-S032
│       │   └── crates.py        # S033-S039
│       ├── cache/
│       │   ├── __init__.py
│       │   └── cache.py         # S040-S049
│       └── patterns/
│           ├── __init__.py
│           ├── database.py      # S050-S059
│           └── builtin.py       # Built-in patterns
├── tests/
│   ├── unit/
│   ├── integration/
│   └── property/
├── docs/
│   └── architecture/
│       └── ARCHITECTURE.md      # This file
└── pyproject.toml
```

---

**Gate 1 Status**: COMPLETE - HOSTILE_VALIDATOR approved with CONDITIONAL_GO

**P0 Fixes Applied**:
- P0-INV-001: Score normalization formula added to S007
- P0-INV-003: Async SQLite strategy (aiosqlite) added to ADR-003

**P1 Issues Deferred to Gate 2**: See `.fortress/reports/validation/HOSTILE_REVIEW_GATE1_2025-12-24.md`

**Next Step**: Run `/spec` to begin Gate 2 (Specification)
