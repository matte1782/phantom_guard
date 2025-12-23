---
name: phantom:validate-technical
description: Technical validation of APIs and detection approaches. Use to verify registry APIs work and detection algorithms are viable.
---

# Skill: Technical Validation for Phantom Guard

> **Purpose**: Validate that Phantom Guard can actually be built by testing real APIs and detection approaches
> **Time Budget**: 2-3 hours maximum
> **Output**: `research-output/TECHNICAL_VALIDATION.md`

---

## Objective

Answer the 4 critical unknowns that could block production:

1. **API Availability**: Do PyPI/npm/crates.io APIs expose the data we need?
2. **Rate Limits**: Can we query at scale without being blocked?
3. **Detection Reliability**: Can we distinguish slopsquatting from legitimate new packages?
4. **False Positive Rate**: Will real-world usage trigger too many false alarms?

---

## Execution Steps

### Step 1: API Capability Testing (45 min)

Test each registry API for required signals:

| Signal Needed | PyPI | npm | crates.io |
|---------------|------|-----|-----------|
| Package exists | Test | Test | Test |
| Package age (created date) | Test | Test | Test |
| Download count | Test | Test | Test |
| Maintainer info | Test | Test | Test |
| Repository URL | Test | Test | Test |
| Version history | Test | Test | Test |

**For each registry**:
```bash
# PyPI - Test with a known package
curl -s "https://pypi.org/pypi/requests/json" | jq '.info.author, .info.home_page, .releases | keys | first'

# npm - Test with a known package
curl -s "https://registry.npmjs.org/express" | jq '.time.created, .repository.url'

# crates.io - Test with a known package
curl -s "https://crates.io/api/v1/crates/serde" | jq '.crate.created_at, .crate.downloads, .crate.repository'
```

**Document**: Which signals are available, which are missing, any authentication required.

---

### Step 2: Rate Limit Discovery (30 min)

For each registry, determine:

| Registry | Unauthenticated Limit | Authenticated Limit | Burst Behavior |
|----------|----------------------|---------------------|----------------|
| PyPI | ? | ? | ? |
| npm | ? | ? | ? |
| crates.io | ? | ? | ? |

**Test method**: Make 100 rapid requests, observe:
- Response codes (429 = rate limited)
- Headers (X-RateLimit-Remaining, Retry-After)
- Actual throughput achieved

**Calculate**: For a typical `requirements.txt` with 50 packages, can we validate in <5 seconds?

---

### Step 3: Detection Signal Testing (45 min)

Test detection heuristics against real packages:

**Test Set A - Known Legitimate Packages**:
```
flask, django, requests, numpy, pandas, fastapi, pydantic, httpx
```

**Test Set B - Suspicious Patterns (likely slopsquatting candidates)**:
```
Search PyPI for packages matching:
- flask-*-helper
- django-*-utils
- requests-*-client
- *-gpt-*
- *-openai-*
```

**For each suspicious package found, score**:
- Age < 30 days?
- Downloads < 100?
- No repository URL?
- Maintainer has < 2 packages?
- Name matches hallucination pattern?

**Document**: How many legitimate packages would be flagged? How many suspicious packages would be missed?

---

### Step 4: False Positive Estimation (30 min)

Take 5 real `requirements.txt` files from popular open source projects:

1. https://github.com/tiangolo/fastapi/blob/master/requirements.txt
2. https://github.com/pallets/flask/blob/main/requirements/dev.txt
3. https://github.com/django/django/blob/main/tests/requirements/py3.txt
4. https://github.com/encode/httpx/blob/master/requirements.txt
5. https://github.com/pydantic/pydantic/blob/main/requirements/testing.txt

**For each file**:
- Run detection heuristics on all dependencies
- Count false positives (legitimate packages flagged)
- Calculate false positive rate

**Acceptable threshold**: <5% false positive rate on known-good dependencies.

---

## Output Format

Create `research-output/TECHNICAL_VALIDATION.md`:

```markdown
# Technical Validation Results

**Date**: [date]
**Verdict**: PROCEED / BLOCKED / NEEDS_MITIGATION

---

## 1. API Capability Matrix

| Signal | PyPI | npm | crates.io | Notes |
|--------|------|-----|-----------|-------|
| Package exists | YES/NO | YES/NO | YES/NO | |
| Created date | YES/NO | YES/NO | YES/NO | |
| Downloads | YES/NO | YES/NO | YES/NO | |
| Maintainer | YES/NO | YES/NO | YES/NO | |
| Repository URL | YES/NO | YES/NO | YES/NO | |

**Blockers Found**: [list or "None"]

---

## 2. Rate Limits

| Registry | Limit | Sufficient for MVP? | Mitigation Needed |
|----------|-------|---------------------|-------------------|
| PyPI | X req/min | YES/NO | |
| npm | X req/min | YES/NO | |
| crates.io | X req/min | YES/NO | |

**Blockers Found**: [list or "None"]

---

## 3. Detection Reliability

| Test | Result | Acceptable? |
|------|--------|-------------|
| Legitimate packages correctly passed | X/8 | YES/NO |
| Suspicious packages correctly flagged | X/Y | YES/NO |
| Detection confidence | X% | YES/NO |

**Blockers Found**: [list or "None"]

---

## 4. False Positive Rate

| Project | Dependencies | False Positives | Rate |
|---------|--------------|-----------------|------|
| FastAPI | X | X | X% |
| Flask | X | X | X% |
| Django | X | X | X% |
| httpx | X | X | X% |
| Pydantic | X | X | X% |
| **TOTAL** | X | X | X% |

**Threshold**: <5%
**Result**: PASS / FAIL

---

## Final Verdict

**Overall**: PROCEED / BLOCKED

**Blockers** (if any):
1. [blocker]
2. [blocker]

**Mitigations Required** (if any):
1. [mitigation]
2. [mitigation]

**Recommended Next Step**: [action]
```

---

## Decision Rules

| Condition | Verdict |
|-----------|---------|
| All 4 tests pass | PROCEED to development |
| 1-2 tests fail with known mitigation | PROCEED with mitigation plan |
| Any test reveals fundamental blocker | BLOCKED - document and reassess |
| False positive rate > 10% | BLOCKED - detection approach flawed |

---

## Tools Allowed

- `curl` / `httpx` for API testing
- `jq` for JSON parsing
- Web browser for documentation lookup
- Python REPL for quick calculations
- WebSearch for API documentation

---

## Time Limit

**HARD STOP at 3 hours**. If validation incomplete:
- Document what was tested
- List remaining unknowns
- Make PROCEED/BLOCKED decision on available evidence

Paralysis is worse than imperfect data.
