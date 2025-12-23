---
name: phantom:roadmap
description: View and update the development roadmap. Use at the start of each session to understand current progress and next priorities.
---

# Skill: Development Roadmap

> **Purpose**: Track progress toward MVP release
> **Usage**: Run at the start of each development session

---

## Quick Status

Read and display the current roadmap status from `docs/ROADMAP.md`.

When invoked:
1. Read `docs/ROADMAP.md`
2. Summarize current phase and progress
3. List immediate next tasks
4. Identify any blockers

---

## Session Start Protocol

Every development session should:

1. **Check Roadmap**: What phase are we in?
2. **Review Blockers**: Any issues from last session?
3. **Set Focus**: What's the ONE thing to accomplish today?
4. **Time Check**: How many days until deadline?

---

## Progress Update Protocol

After completing work:

1. Update the progress table in `docs/ROADMAP.md`
2. Mark completed items with `[x]`
3. Note any new blockers discovered
4. Update "Next Session" notes

---

## Deadline Tracking

**MVP Target**: 90 days from project start

| Phase | Days | Deadline Status |
|-------|------|-----------------|
| P0: Setup | 1-3 | |
| P1: Core | 4-21 | |
| P2: CLI | 22-35 | |
| P3: Cache | 36-49 | |
| P4: Action | 50-63 | |
| P5: Hooks | 64-77 | |
| P6: Harden | 78-84 | |
| P7: Release | 85-90 | |

---

## If Behind Schedule

| Days Behind | Action |
|-------------|--------|
| 1-7 | Increase focus, no scope cut |
| 8-14 | Cut P5 (hooks) to post-MVP |
| 15-21 | Cut P4 (GitHub Action) to v0.1.1 |
| 22+ | Emergency scope reassessment |
