# Phantom Guard — Specification

> **Version**: 0.1.0
> **Date**: 2025-12-24
> **Status**: APPROVED
> **Approver**: HOSTILE_VALIDATOR (SPEC_VALIDATOR role)
> **Gate**: 2 of 6 - COMPLETE

---

## 1. Invariant Registry

Complete registry of system invariants with enforcement strategy.

### 1.1 Core Invariants

| INV_ID | Statement | Source | Enforcement | Test Type |
|:-------|:----------|:-------|:------------|:----------|
| INV001 | `risk_score` always in [0.0, 1.0] | S007 | Clamping + assert | proptest |
| INV002 | `signals` tuple never None (empty tuple OK) | S001 | Type system | mypy + unit |
| INV003 | Cached results identical to uncached | S040 | Comparison test | integration |
| INV004 | Batch results contain all input packages | S002 | Set equality | unit |
| INV005 | `fail_fast` stops on first HIGH_RISK | S002 | Order verification | unit |
| INV006 | Detector always returns PackageRisk | S003 | Type annotation | mypy |
| INV007 | `extract_signals` is pure (no side effects) | S004 | No I/O in function | unit + review |
| INV008 | `pattern_match` returns None or valid PatternMatch | S005 | Type check | unit |
| INV009 | Typosquat threshold in (0.0, 1.0) exclusive | S006 | Assert on init | unit |
| INV010 | More risk signals → higher score (monotonicity) | S007 | Property test | proptest |
| INV011 | Thresholds ordered: safe < suspicious < high_risk | S008 | Assert on config | unit |
| INV012 | Aggregate preserves all input packages | S009 | Count equality | unit |

### 1.2 Registry Client Invariants

| INV_ID | Statement | Source | Enforcement | Test Type |
|:-------|:----------|:-------|:------------|:----------|
| INV013 | Registry client returns valid metadata or raises exception | S020+ | Exception handling | unit |
| INV014 | API timeout ≤ configured timeout (default 5s) | S020+ | httpx timeout | integration |
| INV015 | crates.io requests include User-Agent header | S033 | Request inspection | integration |
| INV016 | Cache TTL honored (no stale returns after expiry) | S040 | Time mock | unit |
| INV017 | Cache size limit enforced (eviction works) | S040 | Len check | unit |
| INV018 | Pattern database immutable during match operation | S050 | No writes during read | design review |

### 1.3 Input Validation Invariants

| INV_ID | Statement | Source | Enforcement | Test Type |
|:-------|:----------|:-------|:------------|:----------|
| INV019 | Package name contains only valid chars (a-z, 0-9, -, _, .) | S001 | Regex validation | unit + fuzz |
| INV020 | Package name length 1-214 characters | S001 | Length check | unit |
| INV021 | Registry enum must be known value | S001 | Enum validation | unit |
| INV022 | Config thresholds are floats in [0.0, 1.0] | S003 | Pydantic validation | unit |

### 1.4 Signal Ordering Definition (P1-INV-002 FIX)

**INV010 Clarification**: Monotonicity means adding any risk signal never decreases the score.

```
Signal Risk Weights (from S007):
  TYPOSQUAT:             +50 points (highest risk)
  HALLUCINATION_PATTERN: +40 points
  NEW_PACKAGE:           +30 points
  LOW_DOWNLOADS:         +20 points
  NO_REPOSITORY:         +20 points (implicit from normalization)
  FEW_RELEASES:          +15 points
  NO_AUTHOR:             +10 points
  SHORT_DESCRIPTION:     +10 points

Partial Order: TYPOSQUAT > HALLUCINATION > NEW_PACKAGE > LOW_DOWNLOADS ≥ NO_REPO > FEW_RELEASES > NO_AUTHOR ≥ SHORT_DESC

Property Test:
  For any signal set S1 ⊂ S2:
    calculate_risk_score(S1) ≤ calculate_risk_score(S2)
```

---

## 2. Error Type Definitions (P1-DESIGN-001 FIX)

### 2.1 Exception Hierarchy

```python
class PhantomGuardError(Exception):
    """Base exception for all Phantom Guard errors."""
    pass

class ValidationError(PhantomGuardError):
    """Input validation failed."""
    pass

class InvalidPackageNameError(ValidationError):
    """Package name contains invalid characters or format."""
    pass

class InvalidRegistryError(ValidationError):
    """Unknown registry specified."""
    pass

class InvalidConfigError(ValidationError):
    """Configuration values out of bounds."""
    pass

class RegistryError(PhantomGuardError):
    """Registry communication failed."""
    pass

class RegistryTimeoutError(RegistryError):
    """Registry request timed out."""
    pass

class RegistryRateLimitError(RegistryError):
    """Registry rate limit exceeded (429)."""
    retry_after: int | None  # Seconds to wait

class RegistryUnavailableError(RegistryError):
    """Registry returned 5xx or is unreachable."""
    pass

class RegistryParseError(RegistryError):
    """Registry response could not be parsed."""
    pass

class CacheError(PhantomGuardError):
    """Cache operation failed."""
    pass

class PatternError(PhantomGuardError):
    """Pattern matching failed."""
    pass
```

### 2.2 Error Handling Rules

| Error | Behavior | User Message |
|:------|:---------|:-------------|
| InvalidPackageNameError | Reject immediately | "Invalid package name: {reason}" |
| RegistryTimeoutError | Retry 3x with backoff | "Registry timeout, retrying..." |
| RegistryRateLimitError | Wait retry_after, then retry | "Rate limited, waiting {n}s..." |
| RegistryUnavailableError | Fall back to cache | "Registry unavailable, using cache" |
| CacheError | Continue without cache | "Cache error, continuing without cache" |

---

## 3. Edge Case Catalog

### 3.1 Package Name Input (EC001-EC015)

| EC_ID | Scenario | Input | Expected | Test Type |
|:------|:---------|:------|:---------|:----------|
| EC001 | Empty name | `""` | InvalidPackageNameError | unit |
| EC002 | Whitespace only | `"   "` | InvalidPackageNameError | unit |
| EC003 | Very long name | `"a" * 300` | InvalidPackageNameError | unit |
| EC004 | Max valid length | `"a" * 214` | Passes | unit |
| EC005 | Unicode characters | `"flask-помощник"` | InvalidPackageNameError | unit |
| EC006 | Special characters | `"flask@redis"` | InvalidPackageNameError | unit |
| EC007 | Valid simple name | `"flask"` | Passes | unit |
| EC008 | Valid with hyphens | `"flask-redis-helper"` | Passes | unit |
| EC009 | Valid with underscores | `"flask_redis"` | Passes | unit |
| EC010 | Valid with numbers | `"py3-redis"` | Passes | unit |
| EC011 | Leading hyphen | `"-flask"` | InvalidPackageNameError | unit |
| EC012 | Trailing hyphen | `"flask-"` | InvalidPackageNameError | unit |
| EC013 | Double hyphen | `"flask--redis"` | InvalidPackageNameError | unit |
| EC014 | Leading number | `"3flask"` | Passes (valid for npm) | unit |
| EC015 | Case normalization | `"Flask"` → `"flask"` | Normalized | unit |

### 3.2 Registry Responses (EC020-EC035)

| EC_ID | Scenario | Condition | Expected | Test Type |
|:------|:---------|:----------|:---------|:----------|
| EC020 | Package exists | 200 response | `exists=True`, metadata populated | unit |
| EC021 | Package not found | 404 response | `exists=False`, NOT_FOUND recommendation | unit |
| EC022 | Registry timeout | No response in 5s | RegistryTimeoutError, retry | integration |
| EC023 | Registry 500 error | 500 response | RegistryUnavailableError, retry | unit |
| EC024 | Registry 502/503/504 | Gateway errors | RegistryUnavailableError, retry | unit |
| EC025 | Rate limited | 429 response | RegistryRateLimitError, backoff | unit |
| EC026 | Invalid JSON | Malformed body | RegistryParseError | unit |
| EC027 | Missing required fields | Partial JSON | Graceful defaults | unit |
| EC028 | Empty response body | `{}` | Graceful defaults | unit |
| EC029 | Huge response | >10MB JSON | Truncate or reject | unit |
| EC030 | Network offline | Connection refused | Use cache or warn | integration |
| EC031 | SSL certificate error | Invalid cert | RegistryError | integration |
| EC032 | DNS resolution failure | Unknown host | RegistryError | integration |
| EC033 | Redirect loop | >10 redirects | RegistryError | unit |
| EC034 | pypistats.org unavailable | 5xx on stats | Continue without downloads (P1-PERF-001) | unit |
| EC035 | Concurrent requests | 50 parallel | All succeed, no corruption | integration |

### 3.3 Risk Scoring (EC040-EC055)

| EC_ID | Scenario | Input Signals | Expected Score | Test Type |
|:------|:---------|:--------------|:---------------|:----------|
| EC040 | All safe signals | releases=50, has_repo, has_author | ≈0.0 | unit |
| EC041 | All risk signals | new, no_downloads, no_repo, pattern | ≈1.0 | unit |
| EC042 | Mixed signals | has_repo, but new | 0.3 < score < 0.7 | unit |
| EC043 | Popular package | flask, requests | score < 0.1 | unit |
| EC044 | Known phantom | from slopsquat DB | score ≈ 1.0 | unit |
| EC045 | New but legitimate | age=7d, 10k downloads, has_repo | score < 0.5 | unit |
| EC046 | Typosquat of popular | `"reqeusts"` | score > 0.8 | unit |
| EC047 | Hallucination pattern | `"flask-gpt-helper"` | score > 0.6 | unit |
| EC048 | No signals at all | empty list | score = 0.38 (neutral) | unit |
| EC049 | Single weak signal | just NO_AUTHOR | score < 0.5 | unit |
| EC050 | Single strong signal | just TYPOSQUAT | score > 0.5 | unit |
| EC051 | Boundary: exactly 30 days | age = 30d exactly | Not NEW_PACKAGE | unit |
| EC052 | Boundary: exactly 1000 downloads | downloads = 1000 | Not LOW_DOWNLOADS | unit |
| EC053 | Boundary: exactly 3 releases | releases = 3 | Not FEW_RELEASES | unit |
| EC054 | Score clamping low | very safe package | score = 0.0 (not negative) | proptest |
| EC055 | Score clamping high | extreme risk | score = 1.0 (not >1) | proptest |

### 3.4 Cache Behavior (EC060-EC070)

| EC_ID | Scenario | Condition | Expected | Test Type |
|:------|:---------|:----------|:---------|:----------|
| EC060 | Cache hit | Entry exists, not expired | Return cached | unit |
| EC061 | Cache miss | Entry not exists | Fetch from registry | unit |
| EC062 | Cache expired | Entry exists, TTL passed | Fetch fresh | unit |
| EC063 | Cache full | Max entries reached | LRU eviction | unit |
| EC064 | Cache corruption | Invalid data | Rebuild cache | integration |
| EC065 | Concurrent cache access | Multiple readers | No corruption | integration |
| EC066 | Cache key collision | Different registries, same name | Separate entries | unit |
| EC067 | SQLite file locked | Another process | Wait or error | integration |
| EC068 | Disk full | No space for cache | Graceful degradation | integration |
| EC069 | Memory cache only | SQLite disabled | Works with memory only | unit |
| EC070 | Offline mode | No network | Only cache hits work | unit |

### 3.5 CLI Behavior (EC080-EC095) (P1-SPEC-001 FIX)

| EC_ID | Scenario | Command | Expected | Test Type |
|:------|:---------|:--------|:---------|:----------|
| EC080 | Valid single package | `validate flask` | Exit 0, SAFE output | integration |
| EC081 | Suspicious package | `validate gpt4-api` | Exit 1, SUSPICIOUS output | integration |
| EC082 | Blocked package | `validate known-malware` | Exit 2, HIGH_RISK output | integration |
| EC083 | Not found package | `validate nonexistent123xyz` | Exit 3, NOT_FOUND output | integration |
| EC084 | Valid requirements file | `check requirements.txt` | Exit 0 if all safe | integration |
| EC085 | Mixed results file | `check mixed.txt` | Exit 1, list suspicious | integration |
| EC086 | File not found | `check notexist.txt` | Exit 4, error message | unit |
| EC087 | Empty file | `check empty.txt` | Exit 0, "No packages" | unit |
| EC088 | Invalid file format | `check random.bin` | Exit 4, parse error | unit |
| EC089 | JSON output | `check req.txt --output json` | Valid JSON | unit |
| EC090 | Fail on suspicious | `check req.txt --fail-on suspicious` | Exit 1 if any suspicious | integration |
| EC091 | Verbose mode | `validate flask -v` | Show all signals | unit |
| EC092 | Quiet mode | `validate flask -q` | Only result | unit |
| EC093 | Custom threshold | `validate pkg --threshold 0.5` | Use custom threshold | unit |
| EC094 | Offline mode | `validate flask --offline` | Cache only | unit |
| EC095 | Registry selection | `validate express --registry npm` | Use npm registry | integration |

### 3.6 Pattern Matching (EC100-EC110)

| EC_ID | Scenario | Package Name | Expected Pattern | Test Type |
|:------|:---------|:-------------|:-----------------|:----------|
| EC100 | Suffix: -gpt | `flask-gpt` | HALLUCINATION_PATTERN | unit |
| EC101 | Suffix: -ai | `django-ai` | HALLUCINATION_PATTERN | unit |
| EC102 | Suffix: -chatgpt | `react-chatgpt` | HALLUCINATION_PATTERN | unit |
| EC103 | Suffix: -helper | `requests-helper` | HALLUCINATION_PATTERN | unit |
| EC104 | Suffix: -wrapper | `numpy-wrapper` | HALLUCINATION_PATTERN | unit |
| EC105 | Prefix: easy- | `easy-requests` | HALLUCINATION_PATTERN | unit |
| EC106 | Prefix: simple- | `simple-flask` | HALLUCINATION_PATTERN | unit |
| EC107 | Prefix: auto- | `auto-django` | HALLUCINATION_PATTERN | unit |
| EC108 | Legitimate suffix | `requests-oauthlib` | No pattern match | unit |
| EC109 | Legitimate prefix | `easydict` | No pattern match (known pkg) | unit |
| EC110 | Compound pattern | `flask-gpt-helper` | HALLUCINATION_PATTERN | unit |

---

## 4. Popular Packages Source (P1-DESIGN-002 FIX)

### 4.1 Popular Packages Registry

**Source**: Top 1000 packages from each registry by download count.

```python
class PopularPackages:
    """
    SPEC: S006
    Storage: Built-in data file, updated monthly
    """

    # Data sources:
    # - PyPI: https://hugovk.github.io/top-pypi-packages/
    # - npm: https://www.npmjs.com/browse/depended
    # - crates.io: https://crates.io/crates?sort=downloads

    PYPI_TOP_1000: frozenset[str]   # ~50KB
    NPM_TOP_1000: frozenset[str]    # ~50KB
    CRATES_TOP_1000: frozenset[str] # ~50KB

    def is_popular(self, name: str, registry: Registry) -> bool: ...
    def get_similar(self, name: str, registry: Registry, threshold: float = 0.85) -> str | None: ...
```

### 4.2 Update Strategy

| Aspect | Strategy |
|:-------|:---------|
| Initial data | Bundled with package |
| Update frequency | Monthly release |
| Update mechanism | New package version |
| Fallback | Use bundled data if network unavailable |
| Custom additions | Config file for user additions |

---

## 5. pypistats.org Handling (P1-PERF-001 FIX)

### 5.1 Download Stats as Optional Signal

```python
async def get_downloads(self, name: str) -> int | None:
    """
    SPEC: S023
    OPTIONAL: Failure does not block validation

    Returns:
        Download count, or None if unavailable
    """
    try:
        response = await self._client.get(
            f"https://pypistats.org/api/packages/{name}/recent",
            timeout=2.0  # Shorter timeout than main API
        )
        if response.status_code == 200:
            return response.json().get("data", {}).get("last_month", None)
        return None
    except Exception:
        return None  # Graceful degradation
```

### 5.2 Scoring Without Downloads

| Downloads Available | Behavior |
|:--------------------|:---------|
| Yes, count > 0 | Use in scoring (LOW_DOWNLOADS if < 1000) |
| Yes, count = 0 | Flag as LOW_DOWNLOADS |
| No (None) | Skip download signal, use other signals |

---

## 6. CLI Specification (P1-SPEC-001 FIX)

### 6.1 Command Structure

```
phantom-guard [OPTIONS] COMMAND [ARGS]

Commands:
  validate    Validate a single package
  check       Check a dependency file
  cache       Manage the local cache
  version     Show version information
```

### 6.2 Command: validate

```
phantom-guard validate [OPTIONS] PACKAGE

Arguments:
  PACKAGE               Package name to validate

Options:
  -r, --registry TEXT   Registry: pypi (default), npm, crates
  -t, --threshold FLOAT Risk threshold for SUSPICIOUS (default: 0.3)
  -o, --output FORMAT   Output format: text (default), json
  -v, --verbose         Show detailed signals
  -q, --quiet           Only show result
  --offline             Use cache only, no network
  --no-cache            Skip cache, always fetch fresh
  --timeout FLOAT       Request timeout in seconds (default: 5.0)
```

### 6.3 Command: check

```
phantom-guard check [OPTIONS] FILE

Arguments:
  FILE                  Dependency file (requirements.txt, package.json, Cargo.toml)

Options:
  -r, --registry TEXT   Registry: pypi (default), npm, crates, auto
  -o, --output FORMAT   Output format: text (default), json
  --fail-on LEVEL       Exit non-zero if any package is: suspicious, high_risk
  --ignore PACKAGES     Comma-separated packages to skip
  --allowlist FILE      File with packages to always allow
  --parallel INT        Concurrent validations (default: 10)
```

### 6.4 Exit Codes

| Code | Meaning |
|:-----|:--------|
| 0 | All packages SAFE |
| 1 | At least one SUSPICIOUS |
| 2 | At least one HIGH_RISK |
| 3 | At least one NOT_FOUND |
| 4 | Input error (file not found, invalid format) |
| 5 | Runtime error (network, cache) |

### 6.5 Output Formats

**Text (default):**
```
flask                 SAFE        score=0.02
flask-gpt-helper      SUSPICIOUS  score=0.65  [HALLUCINATION_PATTERN, NEW_PACKAGE]
malware-pkg           HIGH_RISK   score=0.92  [TYPOSQUAT, NO_REPO, LOW_DOWNLOADS]
```

**JSON:**
```json
{
  "results": [
    {
      "name": "flask",
      "recommendation": "safe",
      "risk_score": 0.02,
      "signals": []
    }
  ],
  "summary": {
    "total": 3,
    "safe": 1,
    "suspicious": 1,
    "high_risk": 1,
    "not_found": 0
  }
}
```

---

## 7. Acceptance Matrix

### 7.1 SPEC_ID to Test Count

| SPEC_ID | Description | Unit | Property | Fuzz | Integration | Bench | Total |
|:--------|:------------|:-----|:---------|:-----|:------------|:------|:------|
| S001 | Package validation | 8 | 2 | 1 | 2 | 1 | 14 |
| S002 | Batch validation | 6 | 1 | 0 | 2 | 1 | 10 |
| S003 | Detection orchestrator | 4 | 0 | 0 | 1 | 0 | 5 |
| S004 | Signal extraction | 12 | 2 | 0 | 0 | 0 | 14 |
| S005 | Pattern matching | 15 | 1 | 1 | 0 | 1 | 18 |
| S006 | Typosquat detection | 10 | 2 | 1 | 0 | 1 | 14 |
| S007 | Risk calculation | 15 | 3 | 0 | 0 | 1 | 19 |
| S008 | Threshold evaluation | 6 | 1 | 0 | 0 | 0 | 7 |
| S009 | Result aggregation | 5 | 1 | 0 | 0 | 0 | 6 |
| S010-S019 | CLI commands | 16 | 0 | 0 | 8 | 0 | 24 |
| S020-S026 | PyPI client | 10 | 0 | 0 | 5 | 1 | 16 |
| S027-S032 | npm client | 8 | 0 | 0 | 4 | 1 | 13 |
| S033-S039 | crates.io client | 8 | 0 | 0 | 4 | 1 | 13 |
| S040-S049 | Cache system | 12 | 1 | 0 | 3 | 1 | 17 |
| S050-S059 | Pattern database | 10 | 1 | 1 | 0 | 1 | 13 |
| **TOTAL** | | **145** | **15** | **5** | **29** | **10** | **204** |

### 7.2 Test ID Registry

| TEST_ID | SPEC_ID | INV_ID | EC_ID | Type | Description |
|:--------|:--------|:-------|:------|:-----|:------------|
| T001.01 | S001 | INV019 | EC001 | unit | Empty package name rejected |
| T001.02 | S001 | INV019 | EC005 | unit | Unicode package name rejected |
| T001.03 | S001 | INV019 | EC007 | unit | Valid simple name accepted |
| T001.04 | S001 | INV020 | EC003 | unit | Oversized name rejected |
| T001.05 | S001 | INV002 | - | unit | Signals never None |
| T001.06 | S001 | INV001 | EC054 | proptest | Risk score in bounds |
| T001.07 | S001 | - | EC015 | unit | Case normalization works |
| T001.08 | S001 | - | - | fuzz | Random package names |
| T001.09 | S001 | - | EC020 | integration | Real PyPI query |
| T001.10 | S001 | - | - | bench | Latency < 200ms |
| T002.01 | S002 | INV004 | - | unit | Batch contains all inputs |
| T002.02 | S002 | INV005 | - | unit | Fail-fast stops correctly |
| T002.03 | S002 | - | EC035 | integration | 50 concurrent requests |
| T002.04 | S002 | - | - | bench | Batch < 5s |
| T004.01 | S004 | INV007 | - | unit | extract_signals is pure |
| T004.02 | S004 | - | EC043 | unit | Popular package signals |
| T004.03 | S004 | - | EC045 | unit | New but legitimate |
| T005.01 | S005 | INV008 | EC100 | unit | Pattern: -gpt suffix |
| T005.02 | S005 | INV008 | EC103 | unit | Pattern: -helper suffix |
| T005.03 | S005 | INV008 | EC108 | unit | Legitimate suffix ignored |
| T006.01 | S006 | INV009 | EC046 | unit | Typosquat detected |
| T006.02 | S006 | - | - | proptest | Threshold bounds |
| T007.01 | S007 | INV001 | EC040 | unit | All safe = score 0 |
| T007.02 | S007 | INV001 | EC041 | unit | All risk = score 1 |
| T007.03 | S007 | INV010 | - | proptest | Monotonicity holds |
| T007.04 | S007 | - | EC051 | unit | Boundary: 30 days |
| T007.05 | S007 | - | EC052 | unit | Boundary: 1000 downloads |
| T020.01 | S020 | INV013 | EC020 | unit | Package exists |
| T020.02 | S020 | INV013 | EC021 | unit | Package not found |
| T020.03 | S020 | INV014 | EC022 | integration | Timeout handling |
| T020.04 | S020 | - | EC034 | unit | pypistats optional |
| T040.01 | S040 | INV016 | EC060 | unit | Cache hit |
| T040.02 | S040 | INV016 | EC062 | unit | Cache expired |
| T040.03 | S040 | INV017 | EC063 | unit | LRU eviction |
| T050.01 | S050 | INV018 | EC100-110 | unit | Pattern matching |
| T010.01 | S010 | - | EC080 | integration | CLI validate safe |
| T010.02 | S010 | - | EC081 | integration | CLI validate suspicious |
| T010.03 | S010 | - | EC089 | unit | CLI JSON output |

*(Full registry: 204 tests defined)*

---

## 8. Failure Mode Analysis

### 8.1 Critical Failures (Must Not Happen)

| FM_ID | Failure | Impact | Prevention | Detection | Recovery |
|:------|:--------|:-------|:-----------|:----------|:---------|
| FM001 | False positive on popular package | User loses trust, abandons tool | Allowlist top 1000 | Test against top 1000 | Add to allowlist |
| FM002 | Miss known malware | Security breach | Pattern database, telemetry | Cross-reference CVE database | Update patterns |
| FM003 | Crash on malformed input | Denial of service | Input validation, fuzz testing | Exception monitoring | Fix and release |
| FM004 | Expose secrets in logs | Security breach | No credential logging | Log audit | Redact and rotate |
| FM005 | Score outside [0,1] | Incorrect recommendations | Clamping + property tests | Assertion in tests | Bug is blocked by tests |

### 8.2 Recoverable Failures

| FM_ID | Failure | Impact | Recovery | User Experience |
|:------|:--------|:-------|:---------|:----------------|
| FM010 | Registry timeout | Slower check | Retry 3x with backoff | "Retrying..." message |
| FM011 | Registry rate limit | Slower check | Respect retry-after | "Rate limited, waiting..." |
| FM012 | Registry 500 error | Slower check | Retry, then cache | "Using cached data" |
| FM013 | Network offline | No fresh data | Use cache only | "Offline mode" warning |
| FM014 | pypistats unavailable | Missing download signal | Continue without | No user impact |
| FM015 | Cache corruption | Slower first run | Rebuild cache | One-time delay |

### 8.3 Degraded Operation Modes

| Condition | Behavior | User Impact | How to Exit |
|:----------|:---------|:------------|:------------|
| Offline | Cache-only mode | Stale data possible | Network restored |
| Rate limited | Slower validation | Delays between checks | Wait for reset |
| Cache disabled | No caching | Slower, more API calls | Re-enable cache |
| Partial cache | Some hits, some misses | Variable latency | Cache warms up |

---

## 9. Coverage Targets

| Metric | Target | Minimum | Tool |
|:-------|:-------|:--------|:-----|
| Line coverage | 90% | 85% | pytest-cov |
| Branch coverage | 85% | 80% | pytest-cov |
| Property test cases | 10,000 | 1,000 | hypothesis |
| Fuzz duration | 1 hour | 10 min | hypothesis |
| Mutation score | 80% | 70% | mutmut |

### 9.1 Coverage Exclusions

Files excluded from coverage requirements:
- `__main__.py` (CLI entry)
- `py.typed` (marker file)
- Type stubs

---

## 10. Trace Links

| SPEC_ID | INV_IDs | EC_IDs | TEST_IDs | Module |
|:--------|:--------|:-------|:---------|:-------|
| S001 | INV001, INV002, INV019, INV020 | EC001-EC015 | T001.* | core/detector.py |
| S002 | INV004, INV005 | EC035 | T002.* | core/detector.py |
| S003 | INV006 | - | T003.* | core/detector.py |
| S004 | INV007 | EC040-EC055 | T004.* | core/analyzer.py |
| S005 | INV008 | EC100-EC110 | T005.* | core/patterns.py |
| S006 | INV009 | EC046 | T006.* | core/typosquat.py |
| S007 | INV001, INV010 | EC040-EC055 | T007.* | core/scorer.py |
| S008 | INV011 | - | T008.* | core/scorer.py |
| S009 | INV012 | - | T009.* | core/scorer.py |
| S010-S019 | - | EC080-EC095 | T010.* | cli/main.py |
| S020-S026 | INV013, INV014 | EC020-EC034 | T020.* | registry/pypi.py |
| S027-S032 | INV013, INV014 | EC020-EC034 | T027.* | registry/npm.py |
| S033-S039 | INV013, INV014, INV015 | EC020-EC034 | T033.* | registry/crates.py |
| S040-S049 | INV016, INV017 | EC060-EC070 | T040.* | cache/cache.py |
| S050-S059 | INV018 | EC100-EC110 | T050.* | patterns/database.py |

---

## Appendix A: P1 Issues Addressed

| Issue ID | Description | Resolution |
|:---------|:------------|:-----------|
| P1-SPEC-001 | CLI layer not fully specified | Section 6: CLI Specification |
| P1-INV-002 | Signal ordering ambiguous | Section 1.4: Signal Ordering Definition |
| P1-PERF-001 | pypistats.org should be optional | Section 5: pypistats.org Handling |
| P1-DESIGN-001 | Error types not defined | Section 2: Error Type Definitions |
| P1-DESIGN-002 | Popular packages source undefined | Section 4: Popular Packages Source |

---

## Appendix B: Open Questions for Gate 3

| Question | Impact | Owner |
|:---------|:-------|:------|
| Property test framework: hypothesis vs pytest-quickcheck? | Test design | TEST_ARCHITECT |
| Fuzz testing scope: all inputs or just package names? | Test coverage | TEST_ARCHITECT |
| Mock strategy for registry tests: VCR or manual? | Test reliability | TEST_ARCHITECT |

---

**Gate 2 Status**: COMPLETE - HOSTILE_VALIDATOR approved with GO

**P2 Issues for Gate 3**: See `.fortress/reports/validation/HOSTILE_REVIEW_GATE2_2025-12-24.md`

**Next Step**: Run `/test` to begin Gate 3 (Test Design)
