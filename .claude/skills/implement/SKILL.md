---
name: phantom:implement
description: Guided workflow for implementing features with quality gates. Use when building new features - includes spec, test-first, implementation, and verification steps.
---

# Skill: Implementation Workflow

> **Purpose**: Guided workflow for implementing features with quality gates
> **Mindset**: Write code that your hostile reviewer cannot break

---

## Implementation Checklist

Before writing ANY code, verify:

- [ ] Feature is on the roadmap
- [ ] Architecture is documented
- [ ] Edge cases identified
- [ ] Test plan exists
- [ ] No blockers from previous hostile reviews

---

## Implementation Steps

### Step 1: Specification (10 min)

Write a mini-spec before coding:

```markdown
## Feature: [Name]

### What
[One sentence: what does this do?]

### Why
[Why is this needed for MVP?]

### Inputs
- [Input 1]: [Type, validation rules]
- [Input 2]: [Type, validation rules]

### Outputs
- Success: [What returns on success]
- Failure: [What returns on failure]

### Edge Cases
1. [Edge case 1]: [How to handle]
2. [Edge case 2]: [How to handle]
3. [Edge case 3]: [How to handle]

### Security Considerations
- [Consideration 1]
- [Consideration 2]

### Dependencies
- Internal: [modules used]
- External: [packages used]
```

### Step 2: Test First (15 min)

Write failing tests before implementation:

```python
# tests/test_feature.py

def test_feature_happy_path():
    """Feature works with valid input."""
    result = feature(valid_input)
    assert result == expected_output

def test_feature_edge_case_1():
    """Feature handles [edge case 1]."""
    result = feature(edge_case_input)
    assert result == expected_edge_output

def test_feature_invalid_input():
    """Feature rejects invalid input gracefully."""
    with pytest.raises(ValidationError):
        feature(invalid_input)

def test_feature_empty_input():
    """Feature handles empty input."""
    result = feature([])
    assert result == empty_result
```

### Step 3: Implementation (varies)

Write the code:

```python
# src/phantom_guard/feature.py

def feature(input: InputType) -> OutputType:
    """
    Brief description.

    Args:
        input: Description of input

    Returns:
        Description of output

    Raises:
        ValidationError: When input is invalid
    """
    # Validate input FIRST
    if not input:
        return empty_result

    _validate_input(input)

    # Main logic
    result = _process(input)

    return result
```

### Step 4: Verify (5 min)

Run the verification suite:

```bash
# Run tests
pytest tests/test_feature.py -v

# Check types
mypy src/phantom_guard/feature.py

# Check style
ruff check src/phantom_guard/feature.py

# Run all tests
pytest
```

### Step 5: Document (5 min)

Update documentation if needed:

- [ ] Docstrings complete
- [ ] README updated (if public API changed)
- [ ] CHANGELOG.md entry added
- [ ] Architecture doc updated (if design changed)

### Step 6: Hostile Self-Review (5 min)

Before committing, ask yourself:

1. "What would break this?"
2. "What did I assume that might be wrong?"
3. "What happens at 10x scale?"
4. "Did I handle all error cases?"
5. "Is there a simpler way?"

---

## Code Standards

### File Structure

```python
"""
Module description.

This module provides [functionality].
"""

from __future__ import annotations

# Standard library
import logging
from typing import TYPE_CHECKING

# Third party
import httpx

# Local
from phantom_guard.core import types

if TYPE_CHECKING:
    from phantom_guard.registry import RegistryClient

logger = logging.getLogger(__name__)


# Constants
DEFAULT_TIMEOUT = 10.0
MAX_RETRIES = 3


# Public API
__all__ = ["PublicClass", "public_function"]


class PublicClass:
    """Class description."""

    def __init__(self, config: Config) -> None:
        """Initialize with config."""
        self._config = config

    def public_method(self, arg: str) -> Result:
        """
        Method description.

        Args:
            arg: Argument description

        Returns:
            Result description

        Raises:
            ValueError: When arg is invalid
        """
        ...


def public_function(arg: str) -> Result:
    """Function description."""
    ...


# Private helpers
def _private_helper() -> None:
    """Internal helper."""
    ...
```

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Module | snake_case | `registry_client.py` |
| Class | PascalCase | `RegistryClient` |
| Function | snake_case | `check_package` |
| Constant | UPPER_SNAKE | `MAX_RETRIES` |
| Private | _prefix | `_validate_input` |
| Type alias | PascalCase | `PackageList = List[str]` |

### Error Handling

```python
# Good: Specific exceptions with context
class PackageNotFoundError(Exception):
    """Raised when package doesn't exist in registry."""

    def __init__(self, package: str, registry: str):
        self.package = package
        self.registry = registry
        super().__init__(f"Package '{package}' not found in {registry}")

# Good: Handle expected errors, let unexpected propagate
try:
    response = await client.get(url)
except httpx.TimeoutException:
    logger.warning(f"Timeout fetching {url}")
    return cached_result or default_result
except httpx.HTTPStatusError as e:
    if e.response.status_code == 404:
        return PackageNotFoundResult(package)
    raise  # Unexpected status, propagate

# Bad: Catching everything
try:
    result = do_something()
except Exception:
    return None  # Lost error context!
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

# Good: Structured, appropriate levels
logger.debug("Checking package %s", package_name)
logger.info("Validated %d packages in %dms", count, time_ms)
logger.warning("Rate limited by %s, retrying in %ds", registry, delay)
logger.error("Failed to fetch %s: %s", url, error)

# Bad: Print statements, sensitive data
print(f"Checking {package}")  # Don't use print
logger.info(f"API key: {api_key}")  # Don't log secrets
```

---

## Common Patterns

### Async HTTP Client

```python
async def fetch_package_info(
    client: httpx.AsyncClient,
    package: str,
    timeout: float = 10.0,
) -> PackageInfo:
    """Fetch package info with retry and timeout."""
    url = f"https://pypi.org/pypi/{package}/json"

    for attempt in range(MAX_RETRIES):
        try:
            response = await client.get(url, timeout=timeout)
            response.raise_for_status()
            return PackageInfo.from_dict(response.json())
        except httpx.TimeoutException:
            if attempt == MAX_RETRIES - 1:
                raise
            await asyncio.sleep(2 ** attempt)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return PackageInfo.not_found(package)
            raise
```

### Caching

```python
from functools import lru_cache
from datetime import datetime, timedelta

class TTLCache:
    """Simple TTL cache."""

    def __init__(self, ttl_seconds: int = 3600):
        self._cache: dict[str, tuple[Any, datetime]] = {}
        self._ttl = timedelta(seconds=ttl_seconds)

    def get(self, key: str) -> Optional[Any]:
        if key not in self._cache:
            return None
        value, timestamp = self._cache[key]
        if datetime.now() - timestamp > self._ttl:
            del self._cache[key]
            return None
        return value

    def set(self, key: str, value: Any) -> None:
        self._cache[key] = (value, datetime.now())
```

### Validation

```python
import re
from pydantic import BaseModel, validator

PACKAGE_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9]([a-zA-Z0-9._-]*[a-zA-Z0-9])?$')

class PackageRequest(BaseModel):
    name: str
    registry: str = "pypi"

    @validator('name')
    def validate_name(cls, v):
        if not PACKAGE_NAME_PATTERN.match(v):
            raise ValueError(f"Invalid package name: {v}")
        if len(v) > 100:
            raise ValueError("Package name too long")
        return v.lower()

    @validator('registry')
    def validate_registry(cls, v):
        allowed = {'pypi', 'npm', 'crates'}
        if v not in allowed:
            raise ValueError(f"Registry must be one of: {allowed}")
        return v
```

---

## Checkpoint Command

After completing a unit of work, run checkpoint:

```markdown
## Checkpoint: [Feature Name]

**Date**: [date]
**Status**: COMPLETE / IN_PROGRESS / BLOCKED

### Completed
- [x] [Task 1]
- [x] [Task 2]

### Tests
- [x] Unit tests passing
- [x] Integration tests passing
- [ ] Edge case tests (need more)

### Quality
- [x] Type checked
- [x] Linted
- [ ] Hostile reviewed

### Remaining
- [ ] [Remaining task 1]

### Blockers
- [None / blocker description]

### Next Session
- [What to do next]
```
