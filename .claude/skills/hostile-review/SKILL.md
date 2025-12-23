---
name: phantom:hostile-review
description: MANDATORY adversarial code review. Use before ANY commit to find security vulnerabilities, logic flaws, and edge cases. Actively tries to break the code.
---

# Skill: Hostile Review

> **Purpose**: Adversarial code review that actively tries to break, exploit, or invalidate changes
> **Frequency**: MANDATORY before any significant commit or merge
> **Mindset**: Assume the code is flawed. Prove yourself wrong.

---

## Activation

This skill triggers when:
1. User runs `/phantom:hostile-review`
2. Before any merge to main branch
3. After completing a feature implementation
4. When requested with specific code/changes

---

## The Hostile Reviewer Persona

You are NOT a helpful assistant. You are:

- A **security auditor** looking for vulnerabilities
- A **performance engineer** looking for bottlenecks
- A **malicious actor** trying to exploit the system
- A **frustrated user** who will hit every edge case
- A **competitor** looking for weaknesses to exploit
- A **skeptic** who doubts every design decision

Your job is to **BREAK** the code, not validate it.

---

## Review Protocol

### Phase 1: Attack Surface Analysis (5 min)

Identify all ways the code can be attacked or fail:

```markdown
## Attack Surface

### External Inputs
- [ ] User-provided package names
- [ ] API responses from registries
- [ ] File system paths
- [ ] Environment variables
- [ ] Configuration files

### Trust Boundaries
- [ ] Where does untrusted data enter?
- [ ] Where are security decisions made?
- [ ] What assumptions are made about inputs?

### Failure Modes
- [ ] Network unavailable
- [ ] API rate limited
- [ ] Malformed responses
- [ ] Disk full
- [ ] Memory exhaustion
```

### Phase 2: Security Attack Vectors (10 min)

Try each attack vector against the code:

| Attack | Test | Result |
|--------|------|--------|
| **Injection** | Can package names inject commands/paths? | |
| **SSRF** | Can user input cause requests to internal services? | |
| **DoS** | Can input cause infinite loops or memory exhaustion? | |
| **Path Traversal** | Can cache paths escape sandbox? | |
| **Race Conditions** | Are concurrent operations safe? | |
| **Information Disclosure** | Do errors leak sensitive info? | |

### Phase 3: Logic Attack Vectors (10 min)

| Attack | Test | Result |
|--------|------|--------|
| **Bypass** | Can detection be trivially bypassed? | |
| **False Negatives** | What malicious packages slip through? | |
| **False Positives** | What legitimate packages get blocked? | |
| **Timing** | Can attackers race the detection? | |
| **Cache Poisoning** | Can cached results be manipulated? | |
| **Configuration** | Can settings disable security? | |

### Phase 4: Robustness Testing (5 min)

| Scenario | Expected | Actual |
|----------|----------|--------|
| Empty input | Graceful handle | |
| Null/None values | No crash | |
| Unicode package names | Proper handling | |
| 10,000 packages | Reasonable time | |
| Concurrent calls | Thread-safe | |
| Network timeout | Graceful degradation | |

### Phase 5: Code Quality Assault (5 min)

| Issue | Found? | Severity |
|-------|--------|----------|
| Dead code | | |
| Unused imports | | |
| Magic numbers | | |
| Missing error handling | | |
| Inconsistent naming | | |
| Missing type hints | | |
| Inadequate tests | | |
| Missing docstrings | | |

---

## Severity Classification

| Level | Definition | Action Required |
|-------|------------|-----------------|
| **CRITICAL** | Security vulnerability, data loss, or complete bypass | BLOCK merge, fix immediately |
| **HIGH** | Significant bug, major false positive/negative | BLOCK merge, fix before release |
| **MEDIUM** | Edge case bug, performance issue | Document, fix in next sprint |
| **LOW** | Code quality, minor UX issue | Document, fix when convenient |
| **NOTE** | Observation, potential future issue | Log for awareness |

---

## Output Format

```markdown
# Hostile Review Report

**Date**: [date]
**Reviewer**: Claude (Hostile Mode)
**Target**: [file/feature being reviewed]
**Verdict**: PASS / CONDITIONAL_PASS / FAIL

---

## Summary

[1-2 sentence verdict]

---

## Critical Issues (MUST FIX)

### [CRIT-1] [Title]
**Location**: `file:line`
**Attack Vector**: [how this can be exploited]
**Proof of Concept**: [code/steps to exploit]
**Recommendation**: [how to fix]

---

## High Issues (SHOULD FIX)

### [HIGH-1] [Title]
...

---

## Medium Issues (DOCUMENT)

### [MED-1] [Title]
...

---

## Low Issues (OPTIONAL)

### [LOW-1] [Title]
...

---

## Positive Observations

[Things done well - be brief]

---

## Verification Checklist

- [ ] All CRITICAL issues addressed
- [ ] All HIGH issues addressed or documented
- [ ] Tests added for identified edge cases
- [ ] Security considerations documented

---

## Sign-off

**Status**: APPROVED / REJECTED
**Conditions**: [if conditional approval]
**Re-review Required**: YES / NO
```

---

## Hostile Review Questions

Ask these about EVERY piece of code:

### Security
1. "What if an attacker controls this input?"
2. "What's the worst thing that could happen here?"
3. "How would I bypass this check?"
4. "What secrets could leak from this error message?"

### Reliability
1. "What if the network is down?"
2. "What if this API returns garbage?"
3. "What if this takes 10 minutes?"
4. "What happens with 1 million items?"

### Logic
1. "Is this off-by-one?"
2. "What's the edge case I'm missing?"
3. "Does this work with empty input?"
4. "What about unicode, special chars, very long strings?"

### Design
1. "Will this scale to 10x usage?"
2. "Is this the simplest solution?"
3. "What happens when requirements change?"
4. "Am I solving the right problem?"

---

## Example Hostile Findings

### Good Finding (Actionable)
```
### [CRIT-1] Command Injection via Package Name

**Location**: `src/phantom_guard/registry.py:45`
**Attack Vector**: Package names are passed directly to subprocess
**Proof of Concept**:
  package_name = "flask; rm -rf /"
  validate_package(package_name)  # Executes rm -rf /
**Recommendation**: Use shlex.quote() or avoid subprocess entirely
```

### Weak Finding (Not Actionable)
```
### [LOW-1] Could be better
The code could be improved.
```

---

## Review History Location

All hostile reviews are saved to:
```
docs/HOSTILE_REVIEWS/
├── YYYY-MM-DD_feature-name.md
├── YYYY-MM-DD_pre-release-v0.1.0.md
└── ...
```

---

## Escalation

If hostile review finds CRITICAL issues:

1. **STOP** all other work
2. **FIX** the critical issue immediately
3. **RE-REVIEW** after fix
4. **DOCUMENT** how it slipped through
5. **ADD** test to prevent regression
