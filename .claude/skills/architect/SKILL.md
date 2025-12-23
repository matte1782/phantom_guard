---
name: phantom:architect
description: Design system architecture before implementing new features. Use when starting major components or making design decisions with long-term impact.
---

# Skill: Architecture Planning

> **Purpose**: Design and document system architecture before implementation
> **Output**: `docs/ARCHITECTURE.md` updates and component specifications

---

## When to Use

1. Starting a new major component
2. Making design decisions with long-term impact
3. Before implementing any feature that touches multiple modules
4. When refactoring existing architecture

---

## Architecture Decision Process

### Step 1: Problem Statement

Before designing, clearly state:

```markdown
## Problem Statement

**What are we building?**
[Clear, one-sentence description]

**Why is this needed?**
[Business/technical justification]

**What are the constraints?**
- Performance: [requirements]
- Security: [requirements]
- Compatibility: [requirements]
- Dependencies: [limits]

**What are the non-goals?**
[What we're explicitly NOT building]
```

### Step 2: Options Analysis

For any significant decision, document at least 2 options:

```markdown
## Options Considered

### Option A: [Name]
**Description**: [How it works]
**Pros**:
- [Pro 1]
- [Pro 2]
**Cons**:
- [Con 1]
- [Con 2]
**Effort**: [Low/Medium/High]

### Option B: [Name]
**Description**: [How it works]
**Pros**:
- [Pro 1]
**Cons**:
- [Con 1]
**Effort**: [Low/Medium/High]

### Decision: [Option X]
**Rationale**: [Why this option wins]
```

### Step 3: Component Design

For each component, specify:

```markdown
## Component: [Name]

### Responsibility
[Single sentence: what this component does]

### Interface
```python
class ComponentName:
    def method_name(self, arg: Type) -> ReturnType:
        """Brief description."""
        ...
```

### Dependencies
- Internal: [other components it uses]
- External: [third-party libraries]

### Data Flow
[Input] -> [Processing] -> [Output]

### Error Handling
- [Error case 1]: [How handled]
- [Error case 2]: [How handled]

### Testing Strategy
- Unit tests: [what to test]
- Integration tests: [what to test]
```

---

## Phantom Guard Component Architecture

### Core Components

```
phantom-guard/
├── src/phantom_guard/
│   ├── __init__.py           # Public API
│   ├── core/
│   │   ├── detector.py       # Main detection logic
│   │   ├── scorer.py         # Risk scoring engine
│   │   └── patterns.py       # Hallucination pattern matching
│   ├── registry/
│   │   ├── base.py           # Registry interface
│   │   ├── pypi.py           # PyPI client
│   │   ├── npm.py            # npm client
│   │   └── crates.py         # crates.io client
│   ├── cache/
│   │   ├── memory.py         # In-memory cache
│   │   └── persistent.py     # SQLite cache
│   ├── cli/
│   │   └── main.py           # CLI entry point
│   └── hooks/
│       ├── pip_hook.py       # pip install hook
│       └── npm_hook.py       # npm install hook
```

### Component Interaction

```
User Input (requirements.txt / package name)
           │
           ▼
    ┌──────────────┐
    │   CLI/Hook   │  ◄── Entry points
    └──────────────┘
           │
           ▼
    ┌──────────────┐
    │   Detector   │  ◄── Orchestrates validation
    └──────────────┘
           │
     ┌─────┴─────┐
     ▼           ▼
┌─────────┐ ┌─────────┐
│  Cache  │ │ Scorer  │
└─────────┘ └─────────┘
     │           │
     │     ┌─────┴─────┐
     │     ▼           ▼
     │ ┌─────────┐ ┌─────────┐
     │ │ Patterns│ │Registry │
     │ └─────────┘ │ Clients │
     │             └─────────┘
     │                  │
     └────────┬─────────┘
              ▼
    ┌──────────────────┐
    │ ValidationResult │
    └──────────────────┘
```

---

## Data Models

### Core Types

```python
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

class RiskLevel(Enum):
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SignalType(Enum):
    NOT_FOUND = "not_found"
    NEW_PACKAGE = "new_package"
    LOW_DOWNLOADS = "low_downloads"
    NO_REPOSITORY = "no_repository"
    HALLUCINATION_PATTERN = "hallucination_pattern"
    SINGLE_MAINTAINER = "single_maintainer"
    NO_DESCRIPTION = "no_description"

@dataclass
class PackageMetadata:
    name: str
    exists: bool
    created_at: Optional[datetime]
    downloads_last_month: Optional[int]
    repository_url: Optional[str]
    maintainer_count: int
    release_count: int
    has_description: bool

@dataclass
class RiskSignal:
    signal_type: SignalType
    weight: float
    details: str

@dataclass
class PackageRisk:
    package_name: str
    risk_level: RiskLevel
    risk_score: float  # 0.0 - 1.0
    signals: List[RiskSignal]
    recommendation: str
    metadata: Optional[PackageMetadata]

@dataclass
class ValidationResult:
    safe: List[str]
    suspicious: List[PackageRisk]
    blocked: List[PackageRisk]
    errors: List[str]
    validation_time_ms: int
```

---

## API Design

### Public API (src/phantom_guard/__init__.py)

```python
# Simple API - most users need only this
def check(package: str, registry: str = "pypi") -> PackageRisk:
    """Check a single package for slopsquatting risk."""
    ...

def check_many(packages: List[str], registry: str = "pypi") -> ValidationResult:
    """Check multiple packages concurrently."""
    ...

def check_requirements(path: str) -> ValidationResult:
    """Check a requirements.txt or package.json file."""
    ...

# Configuration
def configure(
    cache_enabled: bool = True,
    cache_ttl_hours: int = 24,
    risk_threshold: float = 0.7,
    block_not_found: bool = True,
) -> None:
    """Configure global settings."""
    ...
```

---

## Performance Requirements

| Operation | Target | Measurement |
|-----------|--------|-------------|
| Single package (cached) | <10ms | Time from call to result |
| Single package (uncached) | <200ms | Time including API call |
| 50 packages (concurrent) | <3s | Parallel API calls |
| Pattern matching | <1ms | Per package name |
| Cache lookup | <1ms | SQLite query |

---

## Security Requirements

| Concern | Mitigation |
|---------|------------|
| Package name injection | Validate against regex, no shell usage |
| API response manipulation | Validate JSON schema, handle errors |
| Cache poisoning | Signed cache entries, TTL enforcement |
| Sensitive data in logs | No API keys, sanitize package names |
| Path traversal | Validate paths, use pathlib |

---

## Extensibility Points

### Adding New Registries

1. Implement `RegistryClient` interface
2. Add to registry factory
3. Update CLI options
4. Add tests

### Adding New Signals

1. Add `SignalType` enum value
2. Implement scorer method
3. Configure weight in scoring matrix
4. Add pattern tests

### Adding New Output Formats

1. Implement `Formatter` interface
2. Add CLI flag
3. Add tests
