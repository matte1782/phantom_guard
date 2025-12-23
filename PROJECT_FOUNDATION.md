# Phantom-Guard: Project Foundation

> **Status**: Research Complete, Awaiting Specification Phase
> **Decision Date**: December 22, 2025
> **Research Source**: Research Fortress v7 (7 iterations, 40+ domains analyzed, 40+ web searches)

---

## Executive Summary

**One-liner**: A library that detects and prevents AI-hallucinated dependency attacks (slopsquatting) before they compromise your software supply chain.

**Goal**: Moderate success path - 5K+ GitHub stars, $500K-2M ARR, acquisition by Snyk/Socket/JFrog ($15-50M)

**Why This Project**: After analyzing 40+ domains across 7 research iterations, this is the ONLY opportunity that combines:
- Brand new attack vector (named 2024-2025)
- Quantified pain (20% hallucination rate)
- Zero funded competition
- Zero Big Tech attention
- Simple technical build
- Clear monetization path

---

## The Problem

### What is Slopsquatting?

When AI coding assistants (Copilot, Claude Code, Cursor) generate code, they sometimes "hallucinate" package names that don't exist. Attackers can:

1. Study which names AI commonly hallucinates
2. Register those phantom package names on PyPI/npm with malware
3. Wait for developers to install the AI-suggested packages
4. Malware executes on developer machines

### The Numbers

| Statistic | Source |
|-----------|--------|
| **20%** of AI-generated code references non-existent packages | Arxiv March 2025 |
| **43%** of hallucinated packages appear consistently | Same study |
| **1.8M+** GitHub Copilot users | GitHub 2024 |
| **40%** higher secret leak rate with AI tools | GitGuardian 2025 |

### Why Current Tools Don't Help

| Tool | What It Does | Why It Misses Slopsquatting |
|------|--------------|----------------------------|
| Snyk | Scans for known vulnerabilities | Only checks REAL packages with CVEs |
| Socket | Detects malicious packages | Not focused on hallucination patterns |
| Endor Labs | SBOM reachability analysis | Analyzes existing dependencies, not phantom ones |
| PyPI/npm | Package registries | Passive, reactive takedowns only |

**Gap**: No tool specifically detects AI-hallucinated dependencies before installation.

---

## The Solution

### What Phantom-Guard Does

```
Developer's AI suggests: pip install flask-redis-helper

Phantom-Guard intercepts and checks:
- Does this package exist? YES (attacker registered it 3 days ago)
- Package age: 3 days (SUSPICIOUS)
- Downloads: 23 (SUSPICIOUS)
- Has repository link: NO (SUSPICIOUS)
- Matches hallucination pattern: YES (flask_*_helper)
- Maintainer other packages: 0 (SUSPICIOUS)

WARNING: This package shows signs of slopsquatting attack.
Proceed? [y/N]
```

### Detection Signals

| Signal | Why It Matters |
|--------|----------------|
| Package age < 30 days | Attackers register just-in-time |
| Zero/low downloads | Legitimate packages have history |
| No source repository | Malware often has no GitHub link |
| Name matches hallucination patterns | `flask_*_helper`, `django_*_utils`, `common_*` |
| Maintainer has no other packages | New throwaway accounts |
| Package appeared after AI boom (2023+) | Timing correlates with attack window |

### Core API Concept

```python
from phantom_guard import validate_dependencies

result = validate_dependencies(
    dependencies=["flask", "flask-redis-helper", "requests"],
    language="python",
    confidence_threshold=0.7
)

# Returns:
# ValidationResult(
#     safe=["flask", "requests"],
#     suspicious=[
#         SuspiciousPackage(
#             name="flask-redis-helper",
#             risk_score=0.85,
#             signals=["new_package", "no_repo", "hallucination_pattern"],
#             recommendation="BLOCK"
#         )
#     ]
# )
```

---

## Competition Analysis

### Direct Competition: $0

| Potential Competitor | Status | Gap |
|---------------------|--------|-----|
| Socket | Supply chain focus | Not hallucination-aware |
| Snyk | SCA, real vulnerabilities | Doesn't detect phantoms |
| Endor Labs ($188M) | Reachability for real vulns | Not hallucination-focused |
| GitHub | Secret scanning | Not package validation |
| PyPI/npm | Package registries | Passive, not proactive |

**No funded startup is building slopsquatting-specific detection.**

### Why This Window Exists

```
2023: Copilot reaches 1M users. Hallucinations happen but not weaponized.
2024: Slopsquatting attack vector identified and named.
2025: AI coding tools mainstream. First documented attacks.
      Research quantifies the 20% hallucination rate.
      --> WE ARE HERE - PERFECT WINDOW <--
2026: VCs will discover this. Competition will arrive.
```

**Window duration**: 12-18 months before VC-funded competition.

---

## Scoring (Research Fortress v7)

### Final Score: 51/55 (WINNER)

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Timing | 15 | 15 | Attack vector just named, no incumbents |
| Pain | 14 | 15 | 20% hallucination rate, quantified |
| Build | 14 | 15 | Pattern matching + API calls, 90-day MVP |
| Moat | 8 | 10 | First-mover, pattern database as asset |

### 25-Vector Hostile Review

| Category | Score | Max |
|----------|-------|-----|
| Technical | 7.5 | 8 |
| Market | 8 | 8 |
| Execution | 8.5 | 9 |
| **TOTAL** | **24/25** | **SURVIVOR** |

### Why Previous Winners Were Killed

| Iteration | Winner | Why Killed |
|-----------|--------|------------|
| 5 | AI Code Verification | $100M+ entered space (Endor Labs, Graphite) |
| 6 | SBOM Reachability | $188M Endor Labs doing exact same thing |
| **7** | **Slopsquatting** | **Zero competition - SURVIVOR** |

---

## Target Customer

### Profile

- 500+ developers
- Using GitHub Copilot or Claude Code
- Has AppSec team
- Under compliance requirements (SOC2, HIPAA, PCI)
- Previously concerned about supply chain attacks

### Day 1 Customers

1. Fintech companies (compliance + security focus)
2. Healthcare tech (HIPAA requirements)
3. AI-native startups (heavy AI tool usage)
4. Security-conscious enterprises (post-SolarWinds trauma)

### Pricing Expectation

| Tier | Price | Features |
|------|-------|----------|
| OSS | Free | Core detection, CLI, basic patterns |
| Team | $10/dev/month | Dashboard, policy config, SSO |
| Enterprise | $25/dev/month | Audit logging, SLA, private patterns |

---

## MVP Scope (90 Days)

### Month 1: Detection Engine

- [ ] Package registry API clients (PyPI, npm, crates.io)
- [ ] Package existence + metadata verification
- [ ] Name similarity scoring (detect typosquatting/slopsquatting)
- [ ] Hallucination pattern database (initial 100 patterns)
- [ ] CLI tool: `phantom-guard check requirements.txt`

### Month 2: Integration Layer

- [ ] pip install hook (pre-install validation)
- [ ] npm install hook
- [ ] requirements.txt / package.json scanner
- [ ] GitHub Action for CI/CD
- [ ] Pre-commit hook

### Month 3: Intelligence Layer

- [ ] Community-contributed hallucination patterns
- [ ] Telemetry (opt-in) for new phantom discoveries
- [ ] Confidence scoring refinement
- [ ] v1.0.0 release
- [ ] Launch (HN, Reddit, Twitter)

### Technical Stack

```
Language: Python 3.11+
Dependencies:
  - httpx (async API calls)
  - typer (CLI)
  - pydantic (validation)
  - sqlite (local cache)
Distribution:
  - PyPI package
  - npm wrapper
  - GitHub Action
  - Pre-commit hook
```

---

## Monetization Path

### Year 1: OSS Foundation ($0 revenue)

```
phantom-guard (MIT License)
├── Core detection engine
├── CLI tool
├── pip/npm hooks
├── Basic GitHub Action
└── Community pattern database
```

Focus: Adoption, stars, contributors

### Year 2: Enterprise Features ($500K ARR target)

```
phantom-guard-enterprise
├── Team dashboards
├── Policy configuration (block/warn/allow)
├── SSO/SAML integration
├── Audit logging
├── Private pattern database
└── Priority support
```

### Year 3: Platform ($2M ARR target)

```
phantom-guard-platform
├── API access
├── Custom pattern marketplace
├── Compliance packs (SOC2, HIPAA)
├── Multi-registry support
└── Integration marketplace
```

---

## Exit Path

### Potential Acquirers

| Company | Rationale | Likelihood |
|---------|-----------|------------|
| Snyk | Add AI-aware supply chain to SCA | HIGH |
| Socket | Expand supply chain protection | HIGH |
| GitHub | Add to Advanced Security | MEDIUM |
| Endor Labs | Complement reachability | MEDIUM |
| JFrog | Add to Xray | MEDIUM |

### Acquisition Multiple

- Typical DevSecOps: 8-12x ARR
- Strategic premium: 15-20x ARR (if category leader)

### Exit Timeline

- Year 2-3: Acquisition interest if traction
- Year 4-5: Potential acquisition at $20-50M

---

## Risk Assessment

### Technical Risks

| Risk | Probability | Mitigation |
|------|-------------|------------|
| False positives annoy users | HIGH | Configurable thresholds, easy ignore |
| AI hallucination patterns evolve | MEDIUM | Community contributions, telemetry |
| Package registries rate-limit | LOW | Caching, batch validation |

### Market Risks

| Risk | Probability | Mitigation |
|------|-------------|------------|
| Big Tech builds it | MEDIUM | First mover, community moat |
| VC-funded startup appears | MEDIUM | Speed, category definition |
| AI stops hallucinating | LOW | Attack vector persists at any rate |

### Execution Risks

| Risk | Probability | Mitigation |
|------|-------------|------------|
| Solo developer burnout | HIGH | MVP focus, community building |
| Feature creep | MEDIUM | Ruthless prioritization |
| Premature monetization | LOW | OSS-first, prove value first |

---

## Success Metrics

### 6-Month Targets

| Metric | Target | Stretch |
|--------|--------|---------|
| GitHub Stars | 2,000 | 5,000 |
| Weekly Downloads | 1,000 | 5,000 |
| Patterns in Database | 500 | 1,000 |
| Contributors | 15 | 30 |
| Enterprise Inquiries | 10 | 25 |

### 12-Month Targets

| Metric | Target | Stretch |
|--------|--------|---------|
| GitHub Stars | 8,000 | 15,000 |
| Weekly Downloads | 10,000 | 50,000 |
| Paying Customers | 20 | 50 |
| ARR | $200K | $500K |

---

## Research Sources

- [GitGuardian State of Secrets 2025](https://www.gitguardian.com/state-of-secrets-sprawl-report-2025)
- [Endor Labs TechCrunch $93M](https://techcrunch.com/2025/04/23/endor-labs-which-builds-tools-to-scan-ai-generated-code-for-vulnerabilities-lands-93m/)
- [Trend Micro Slopsquatting](https://www.trendmicro.com/vinfo/us/security/news/cybercrime-and-digital-threats/slopsquatting-when-ai-agents-hallucinate-malicious-packages)
- [BleepingComputer AI Hallucinated Dependencies](https://www.bleepingcomputer.com/news/security/ai-hallucinated-code-dependencies-become-new-supply-chain-risk/)
- [Socket Slopsquatting](https://socket.dev/blog/slopsquatting-how-ai-hallucinations-are-fueling-a-new-class-of-supply-chain-attacks)
- [Graphite TechCrunch $52M](https://techcrunch.com/2025/03/18/anthropic-backed-ai-powered-code-review-platform-graphite-raises-cash/)

---

## Next Steps

1. **Tomorrow**: Create detailed technical specification
2. **This Week**: Project structure, tooling decisions
3. **Week 1-2**: Core detection engine
4. **Week 3-4**: CLI + hooks
5. **Month 2**: GitHub Action + integrations
6. **Month 3**: v1.0.0 launch

---

**Research Fortress v7 Complete. Build begins tomorrow.**
