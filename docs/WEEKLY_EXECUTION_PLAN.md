# Weekly Execution Plan: Phantom Guard v0.1.0

**Timeline**: 21 days (3 weeks)
**Start Date**: [Set when starting]
**Ship Date**: [Start + 21 days]

---

## Week 1: Core Detection Works

### Goal
All critical path tests pass with real API calls.

### Daily Breakdown

#### Day 1: Wire the Core
```
Morning:
- [ ] Read existing tests in test_critical_paths.py
- [ ] Understand what each test expects

Afternoon:
- [ ] Update conftest.py fixtures to use real types (not dicts)
- [ ] Wire first test: test_nonexistent_package_is_blocked
- [ ] Create simple integration helper for tests

Exit Criteria:
- [ ] 1 critical test passes (not skipped)
- [ ] Can call: RiskScorer().score(metadata) and get result
```

#### Day 2: Enable All Critical Tests
```
Morning:
- [ ] Wire test_legitimate_package_is_not_blocked
- [ ] Wire test_suspicious_package_is_flagged

Afternoon:
- [ ] Wire pattern matching tests
- [ ] Wire API behavior tests (mock timeouts)

Exit Criteria:
- [ ] 6+ critical tests pass
- [ ] No test is skipped that can be enabled
```

#### Day 3: Real PyPI Integration
```
Morning:
- [ ] Create tests/integration/test_pypi_real.py
- [ ] Test: fetch "flask" metadata, verify SAFE
- [ ] Test: fetch "requests" metadata, verify SAFE
- [ ] Test: fetch "numpy" metadata, verify SAFE

Afternoon:
- [ ] Test: fetch non-existent package, verify NOT_FOUND
- [ ] Test: fetch suspicious package if found, verify flagged
- [ ] Mark integration tests with @pytest.mark.integration

Exit Criteria:
- [ ] 5 real PyPI calls succeed
- [ ] Results match expected risk levels
```

#### Day 4: Pattern Detection Integration
```
Morning:
- [ ] Test pattern matching with real package names
- [ ] Verify: "flask-gpt-helper" triggers pattern
- [ ] Verify: "django-chatgpt" triggers pattern

Afternoon:
- [ ] End-to-end: Detector.check_package() with patterns
- [ ] Verify pattern signal reduces score appropriately

Exit Criteria:
- [ ] Pattern matching works in full detection flow
- [ ] Suspicious names get lower scores
```

#### Day 5: Error Handling
```
Morning:
- [ ] Test: What happens on API timeout?
- [ ] Test: What happens on malformed JSON?
- [ ] Test: What happens on rate limit (429)?

Afternoon:
- [ ] Ensure errors don't approve packages
- [ ] Ensure errors produce clear messages
- [ ] Test concurrent checks don't fail badly

Exit Criteria:
- [ ] All error paths tested
- [ ] No error path allows package approval
```

#### Day 6: Full Test Suite Green
```
Morning:
- [ ] Run full test suite: pytest -v
- [ ] Fix any remaining failures
- [ ] Add missing edge case tests

Afternoon:
- [ ] Run with coverage: pytest --cov
- [ ] Identify untested code paths
- [ ] Add tests for critical untested paths

Exit Criteria:
- [ ] All tests pass
- [ ] Coverage >70% on core/
- [ ] No critical paths untested
```

#### Day 7: HOSTILE REVIEW #1
```
Full Day:
- [ ] Run phantom:hostile-review skill
- [ ] Focus areas:
  - [ ] Input validation (can we inject?)
  - [ ] Error handling (does any error approve?)
  - [ ] API responses (malicious response handling)
  - [ ] Package name validation
- [ ] Document findings
- [ ] Fix any CRITICAL/HIGH issues

Exit Criteria:
- [ ] No CRITICAL security issues
- [ ] All HIGH issues addressed
- [ ] Hostile review document created
```

### Week 1 Deliverables
- [ ] 12/12 critical tests passing
- [ ] Integration tests with real PyPI
- [ ] Hostile review #1 passed
- [ ] Coverage >70%

---

## Week 2: CLI Works

### Goal
`phantom-guard check requirements.txt` works end-to-end.

### Daily Breakdown

#### Day 8: CLI Skeleton
```
Morning:
- [ ] Create src/phantom_guard/cli/__init__.py
- [ ] Create src/phantom_guard/cli/main.py
- [ ] Set up Typer app with --version

Afternoon:
- [ ] Add `check` command stub
- [ ] Test: phantom-guard --help works
- [ ] Test: phantom-guard check --help works

Exit Criteria:
- [ ] CLI installs and runs
- [ ] --help shows commands
- [ ] --version shows version
```

#### Day 9: Check Command Core
```
Morning:
- [ ] Accept file path argument
- [ ] Validate file exists
- [ ] Read file contents

Afternoon:
- [ ] Call Detector.check_packages()
- [ ] Print raw results (ugly is fine)
- [ ] Handle basic errors

Exit Criteria:
- [ ] phantom-guard check requirements.txt runs
- [ ] Shows some output (even ugly)
```

#### Day 10: requirements.txt Parser
```
Morning:
- [ ] Create src/phantom_guard/parsers/requirements.py
- [ ] Parse: package==version
- [ ] Parse: package>=version
- [ ] Parse: package (no version)

Afternoon:
- [ ] Handle comments (#)
- [ ] Handle blank lines
- [ ] Handle -r includes (basic)
- [ ] Handle extras [dev]
- [ ] Ignore URLs, local paths

Exit Criteria:
- [ ] Parses real-world requirements.txt files
- [ ] Returns list of package names
```

#### Day 11: Pretty Output
```
Morning:
- [ ] Add Rich dependency
- [ ] Create output formatter
- [ ] Color: green for safe, yellow for suspicious, red for blocked

Afternoon:
- [ ] Table format for results
- [ ] Summary line at end
- [ ] Progress indicator for checks

Exit Criteria:
- [ ] Output looks professional
- [ ] Clear at a glance what's safe/blocked
```

#### Day 12: JSON Output
```
Morning:
- [ ] Add --json flag
- [ ] Define JSON schema
- [ ] Output valid JSON

Afternoon:
- [ ] Test JSON parseable
- [ ] Include all relevant fields
- [ ] Test piping to jq

Exit Criteria:
- [ ] --json produces valid JSON
- [ ] JSON has: packages, results, summary
```

#### Day 13: Error Messages & Polish
```
Morning:
- [ ] File not found error
- [ ] Network error handling
- [ ] Empty file handling

Afternoon:
- [ ] Exit codes (0=safe, 1=blocked, 2=error)
- [ ] --quiet flag for CI
- [ ] --verbose flag for debugging

Exit Criteria:
- [ ] All error cases show clear messages
- [ ] Exit codes documented
```

#### Day 14: HOSTILE REVIEW #2
```
Full Day:
- [ ] Run phantom:hostile-review on CLI
- [ ] Focus areas:
  - [ ] File path validation
  - [ ] Output injection
  - [ ] Error message leaks
  - [ ] Exit code consistency
- [ ] UX review: is it clear?
- [ ] Fix issues found

Exit Criteria:
- [ ] CLI security verified
- [ ] UX is intuitive
- [ ] Hostile review #2 passed
```

### Week 2 Deliverables
- [ ] Working CLI command
- [ ] requirements.txt parser
- [ ] Pretty + JSON output
- [ ] Hostile review #2 passed

---

## Week 3: Ship

### Goal
Available on PyPI, documented, announced.

### Daily Breakdown

#### Day 15: README Polish
```
Morning:
- [ ] Rewrite README.md
- [ ] Clear installation: pip install phantom-guard
- [ ] Quick start example
- [ ] Screenshot of output

Afternoon:
- [ ] Feature list
- [ ] How it works section
- [ ] Comparison to alternatives
- [ ] Badges (PyPI version, Python versions)

Exit Criteria:
- [ ] README is compelling
- [ ] Someone could use tool from README alone
```

#### Day 16: Release Prep
```
Morning:
- [ ] Update CHANGELOG.md
- [ ] Version bump to 0.1.0
- [ ] Update pyproject.toml metadata

Afternoon:
- [ ] Final test suite run
- [ ] Build package: python -m build
- [ ] Inspect wheel contents

Exit Criteria:
- [ ] Version is 0.1.0
- [ ] Package builds cleanly
- [ ] CHANGELOG complete
```

#### Day 17: TestPyPI
```
Morning:
- [ ] Upload to TestPyPI
- [ ] Install in fresh venv from TestPyPI
- [ ] Run: phantom-guard --version

Afternoon:
- [ ] Run: phantom-guard check test-requirements.txt
- [ ] Verify all functionality works
- [ ] Fix any issues found

Exit Criteria:
- [ ] Installs from TestPyPI
- [ ] All commands work
```

#### Day 18: Production PyPI
```
Morning:
- [ ] Final check of package metadata
- [ ] Upload to production PyPI
- [ ] Verify on pypi.org/project/phantom-guard

Afternoon:
- [ ] Install in fresh venv: pip install phantom-guard
- [ ] Run test commands
- [ ] Verify no issues

Exit Criteria:
- [ ] pip install phantom-guard works globally
- [ ] Package page looks correct
```

#### Day 19: GitHub Release
```
Morning:
- [ ] Create git tag v0.1.0
- [ ] Push tag to origin
- [ ] Create GitHub release

Afternoon:
- [ ] Write release notes
- [ ] Attach wheel files
- [ ] Add badges to README

Exit Criteria:
- [ ] GitHub release published
- [ ] Release notes complete
```

#### Day 20: Launch Prep
```
Morning:
- [ ] Write Hacker News post
- [ ] Write Reddit r/Python post
- [ ] Write Twitter thread

Afternoon:
- [ ] Review all posts
- [ ] Schedule or prepare to post
- [ ] Set up monitoring (GitHub issues, PyPI stats)

Exit Criteria:
- [ ] All launch posts ready
- [ ] Monitoring in place
```

#### Day 21: LAUNCH
```
Morning:
- [ ] Post on Hacker News (Show HN)
- [ ] Post on r/Python
- [ ] Post Twitter thread

Afternoon:
- [ ] Monitor for feedback
- [ ] Respond to comments
- [ ] Fix any reported issues quickly

Exit Criteria:
- [ ] Posts published
- [ ] Active monitoring
- [ ] v0.1.0 SHIPPED
```

### Week 3 Deliverables
- [ ] README polished
- [ ] PyPI package live
- [ ] GitHub release created
- [ ] Launch posts published
- [ ] v0.1.0 SHIPPED

---

## Daily Standup Template

```markdown
## Day [X] Standup

### Yesterday
- Completed: [list]
- Blocked by: [issues]

### Today
- Will do: [list]
- Need help with: [issues]

### Metrics
- Tests passing: X/12
- Coverage: X%
- Blockers: X
```

---

## Red Flags / Stop Signals

### Stop and Reassess If:

1. **Day 7**: Less than 8 critical tests passing
   - Action: Focus only on tests, skip hostile review

2. **Day 14**: CLI doesn't work end-to-end
   - Action: Reduce scope, skip JSON output

3. **Day 17**: TestPyPI install fails
   - Action: Fix packaging before proceeding

4. **Any day**: Critical security issue found
   - Action: Fix immediately, extend timeline

### Scope Reduction Ladder

If behind schedule:

| Days Behind | Cut |
|-------------|-----|
| 1-2 days | Skip verbose logging |
| 3-4 days | Skip --verbose flag |
| 5-6 days | Skip progress indicator |
| 7+ days | Ship with minimal CLI, polish in v0.1.1 |

---

## Success Criteria for v0.1.0

### Must Ship With:
- [ ] `phantom-guard check requirements.txt` works
- [ ] Detects non-existent packages as BLOCKED
- [ ] Detects suspicious packages as SUSPICIOUS
- [ ] Legitimate packages pass as SAFE
- [ ] Clear terminal output
- [ ] Available on PyPI

### Can Ship Without:
- JSON output (add in v0.1.1)
- Progress indicator
- --verbose flag
- --quiet flag
- Colored output (if Rich causes issues)

---

## Post-Launch (v0.1.1+)

After successful launch, prioritize based on feedback:

| Feature | Add If... |
|---------|-----------|
| JSON output | Users need CI integration |
| npm support | JavaScript users request |
| pyproject.toml parser | Users request |
| Caching | Performance complaints |
| GitHub Action | 100+ weekly downloads |
