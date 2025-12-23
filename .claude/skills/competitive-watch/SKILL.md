---
name: phantom:competitive-watch
description: Weekly competition scan. Detects if competitors have emerged that could invalidate the project. Run WEEKLY during development.
---

# Skill: Competitive Watch for Phantom Guard

> **Purpose**: Detect if competition has emerged that invalidates the project
> **Frequency**: Run WEEKLY during development, DAILY before major milestones
> **Time Budget**: 30 minutes maximum
> **Output**: `research-output/COMPETITIVE_SCAN.md`

---

## Objective

Kill the project FAST if any of these occur:

1. **Direct Competitor**: Someone launches slopsquatting-specific detection
2. **Big Tech Move**: GitHub/npm/PyPI announces built-in protection
3. **Funded Startup**: VC money enters slopsquatting defense space
4. **Feature Absorption**: Socket/Snyk/Endor Labs adds hallucination detection

---

## Threat Detection Queries

### Tier 1: Direct Competition (CRITICAL)

Run these searches:

```
Web Search Queries:
- "slopsquatting detection tool"
- "AI hallucination package detection"
- "phantom package detection"
- "hallucinated dependency scanner"
- site:github.com slopsquatting detection
- site:github.com "hallucinated packages"
```

**GitHub Search**:
```
https://github.com/search?q=slopsquatting&type=repositories
https://github.com/search?q=hallucinated+packages&type=repositories
https://github.com/search?q=phantom+package+detection&type=repositories
```

**If found**: Document immediately. Assess: Is it serious? Active? Funded?

---

### Tier 2: Big Tech Announcements (CRITICAL)

Check official channels:

| Source | Check For |
|--------|-----------|
| GitHub Blog | Copilot security features, dependency scanning updates |
| GitHub Changelog | New security features |
| npm Blog | Security announcements |
| PyPI Blog/Twitter | New safety features |
| Socket Blog | New detection capabilities |
| Snyk Blog | AI-related security features |
| Endor Labs Blog | Hallucination detection |

**Search queries**:
```
- site:github.blog AI hallucination OR slopsquatting
- site:socket.dev/blog hallucination OR slopsquatting
- site:snyk.io/blog AI code security 2025
- "GitHub Copilot" security dependencies 2025
```

---

### Tier 3: Funding Events (HIGH)

Check for new funding in adjacent space:

```
Web Search Queries:
- "supply chain security" startup funding 2025
- "AI code security" seed funding 2025
- "dependency security" series A 2025
- site:techcrunch.com supply chain security funding
- site:crunchbase.com AI code security
```

**If new funding found**: Is slopsquatting in their scope? Check their website/pitch.

---

### Tier 4: Community Signals (MEDIUM)

Monitor discussion:

```
- site:news.ycombinator.com slopsquatting
- site:reddit.com/r/programming slopsquatting
- site:reddit.com/r/netsec AI hallucination packages
- site:twitter.com slopsquatting detection
```

**Look for**: Someone announcing they're building this, security researchers claiming the space.

---

## Output Format

Create/Update `research-output/COMPETITIVE_SCAN.md`:

```markdown
# Competitive Scan Results

**Date**: [date]
**Verdict**: CLEAR / THREAT_DETECTED / WINDOW_CLOSING

---

## Tier 1: Direct Competition

| Query | Results Found | Threat Level |
|-------|---------------|--------------|
| slopsquatting detection tool | X results | NONE/LOW/MEDIUM/HIGH |
| GitHub repos | X repos | NONE/LOW/MEDIUM/HIGH |
| ... | ... | ... |

**Threats Identified**:
- [None / List with links]

---

## Tier 2: Big Tech Moves

| Company | Recent Announcements | Threat Level |
|---------|---------------------|--------------|
| GitHub | [summary] | NONE/LOW/MEDIUM/HIGH |
| npm | [summary] | NONE/LOW/MEDIUM/HIGH |
| PyPI | [summary] | NONE/LOW/MEDIUM/HIGH |
| Socket | [summary] | NONE/LOW/MEDIUM/HIGH |
| Snyk | [summary] | NONE/LOW/MEDIUM/HIGH |
| Endor Labs | [summary] | NONE/LOW/MEDIUM/HIGH |

**Threats Identified**:
- [None / List with links]

---

## Tier 3: Funding Events

| Company | Amount | Focus | Overlap Risk |
|---------|--------|-------|--------------|
| [name] | $XM | [focus] | NONE/LOW/MEDIUM/HIGH |

**Threats Identified**:
- [None / List with links]

---

## Tier 4: Community Signals

| Source | Signal | Concern Level |
|--------|--------|---------------|
| HN | [summary] | NONE/LOW/MEDIUM/HIGH |
| Reddit | [summary] | NONE/LOW/MEDIUM/HIGH |
| Twitter | [summary] | NONE/LOW/MEDIUM/HIGH |

**Threats Identified**:
- [None / List with links]

---

## Verdict

**Status**: CLEAR / THREAT_DETECTED / WINDOW_CLOSING

**Rationale**: [1-2 sentences]

**Recommended Action**:
- CLEAR: Continue development
- THREAT_DETECTED: [specific response - accelerate? pivot? differentiate?]
- WINDOW_CLOSING: [evaluate kill vs accelerate]

---

## Historical Log

| Date | Verdict | Key Findings |
|------|---------|--------------|
| [date] | CLEAR | No threats |
| ... | ... | ... |
```

---

## Decision Matrix

| Finding | Verdict | Action |
|---------|---------|--------|
| No results in any tier | CLEAR | Continue |
| Hobby project on GitHub | CLEAR | Monitor, continue |
| Active OSS project with traction | THREAT_DETECTED | Assess differentiation |
| Big Tech blog post hinting at feature | WINDOW_CLOSING | Accelerate MVP |
| Funded startup in space | THREAT_DETECTED | Evaluate pivot or accelerate |
| Direct competitor with funding | KILL | Document and archive project |

---

## Escalation Rules

**Immediate escalation required if**:
- Any result with >100 GitHub stars on similar tool
- Any Big Tech announcement mentioning slopsquatting
- Any funding >$5M in directly adjacent space
- Any YC/a16z/Sequoia investment in supply chain AI security

**Response time**: If threat detected, decide within 24 hours: accelerate, pivot, or kill.

---

## Time Limit

**HARD STOP at 30 minutes**.

- If scans incomplete, note what was checked
- Default to CLEAR if no obvious threats found
- Better to ship fast than scan forever
