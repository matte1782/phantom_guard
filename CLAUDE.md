# Phantom Guard - Claude Code Rules

> Project: phantom-guard
> Purpose: Detect AI-hallucinated package attacks (slopsquatting)
> Status: Pre-MVP Development

---

## Project Context

Phantom Guard is a security tool that detects slopsquatting attacks - where AI coding assistants hallucinate package names that attackers then register with malware.

### Key Files
- `PROJECT_FOUNDATION.md` - Original research and business case
- `docs/ROADMAP.md` - Development roadmap to MVP
- `.claude/skills/` - Engineering commands and workflows

### Architecture
```
src/phantom_guard/
├── core/        # Detection logic
├── registry/    # PyPI/npm/crates clients
├── cache/       # Caching layer
├── cli/         # CLI interface
└── hooks/       # pip/npm install hooks
```

---

## Engineering Commands

### Essential Commands (Use These!)

| Command | When to Use |
|---------|-------------|
| `/phantom:roadmap` | Start of each session |
| `/phantom:architect` | Before implementing new features |
| `/phantom:implement` | Guided implementation workflow |
| `/phantom:hostile-review` | **REQUIRED** before commits |
| `/phantom:test` | After implementation |
| `/phantom:release-check` | Before version releases |

---

## Development Rules

### Rule 1: Hostile Review is Mandatory

**NEVER** commit significant changes without hostile review.

The hostile reviewer:
- Actively tries to break the code
- Looks for security vulnerabilities
- Tests edge cases
- Questions design decisions

If hostile review finds CRITICAL issues, STOP and fix immediately.

### Rule 2: MVP Focus

Every feature must answer: "Does this help ship v0.1.0?"

If not clearly needed for MVP, it goes to backlog.

90-day deadline is sacred. Cut scope, not quality.

### Rule 3: Detection Accuracy is Critical

False positives kill adoption.
- Target: <5% false positive rate
- Test against real-world packages
- Every heuristic needs justification

### Rule 4: Security First

This is a security tool. It MUST be secure.

- Validate ALL inputs (package names, file paths)
- No shell command execution
- No path traversal possible
- Errors don't leak sensitive info

### Rule 5: Test First

Write failing tests before implementation.

Coverage requirements:
- Core logic: 90%+
- Overall: 80%+

---

## Code Standards

### Imports Order
```python
# Standard library
import json
from typing import TYPE_CHECKING

# Third party
import httpx
from pydantic import BaseModel

# Local
from phantom_guard.core import types
```

### Type Hints Required
```python
# Good
def check_package(name: str, registry: str = "pypi") -> PackageRisk:
    ...

# Bad
def check_package(name, registry="pypi"):
    ...
```

### Error Handling
```python
# Good - specific exceptions
try:
    response = await client.get(url)
except httpx.TimeoutException:
    logger.warning("Timeout for %s", url)
    return cached_result

# Bad - catch all
try:
    result = do_something()
except Exception:
    return None
```

### Logging
```python
import logging
logger = logging.getLogger(__name__)

# Good - structured, no secrets
logger.info("Validated %d packages in %dms", count, time_ms)

# Bad - print statements, secrets
print(f"Checking {package}")
logger.info(f"API key: {key}")
```

---

## Quality Gates

### Before Every Commit
- [ ] Tests pass: `pytest`
- [ ] Types pass: `mypy src/`
- [ ] Lint passes: `ruff check src/`
- [ ] Hostile review (for significant changes)

### Before Every PR
- [ ] All above
- [ ] Coverage maintained
- [ ] Documentation updated
- [ ] CHANGELOG entry

### Before Every Release
- [ ] Full hostile review
- [ ] Security audit
- [ ] Performance benchmarks
- [ ] Real-world testing

---

## Performance Budgets

| Operation | Max Time |
|-----------|----------|
| Single package (cached) | 10ms |
| Single package (uncached) | 200ms |
| 50 packages (concurrent) | 5s |
| Pattern matching | 1ms |

---

## Current Focus

**Phase**: P0 - Project Setup

**Next Actions**:
1. Initialize git repo
2. Set up pre-commit hooks
3. Configure CI/CD
4. Begin P1 (Core Detection Engine)

---

## Useful Snippets

### Run Tests
```bash
pytest -v
pytest --cov=phantom_guard
```

### Type Check
```bash
mypy src/
```

### Lint
```bash
ruff check src/
ruff format src/
```

### Build Package
```bash
python -m build
```

### Test API Endpoints
```bash
# PyPI
curl -s "https://pypi.org/pypi/flask/json" | python -m json.tool

# npm
curl -s "https://registry.npmjs.org/express"

# crates.io
curl -s "https://crates.io/api/v1/crates/serde" -H "User-Agent: phantom-guard"
```

---

## Don't Forget

1. Window is closing - competitors are emerging
2. Ship fast, iterate based on feedback
3. Every line of code must survive hostile review
4. Security tool must be secure
5. False positives kill adoption
