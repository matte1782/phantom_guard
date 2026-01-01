# Week 5 Day 5: Integration Examples & Polish

> **Date**: 2026-01-05
> **Focus**: Code Examples, Mobile Responsive, Final Polish
> **Estimated Hours**: 8

---

## Objectives

1. Create integration examples section
2. Implement code syntax highlighting
3. Complete mobile responsive design
4. Add final polish and micro-interactions

---

## Tasks

### Task 5.1: Integration Section (2.5h)

**src/sections/integration.js:**
```javascript
export function createIntegrationSection() {
  return `
    <div class="section-header">
      <h2 class="section-title">Easy Integration</h2>
      <p class="section-subtitle">
        Integrate Phantom Guard into your workflow in minutes
      </p>
    </div>

    <div class="integration-tabs">
      <button class="tab-btn active" data-tab="cli">CLI</button>
      <button class="tab-btn" data-tab="python">Python API</button>
      <button class="tab-btn" data-tab="github">GitHub Actions</button>
      <button class="tab-btn" data-tab="precommit">Pre-commit</button>
    </div>

    <div class="integration-content">
      <div class="tab-panel active" id="tab-cli">
        <div class="code-block">
          <div class="code-header">
            <span class="code-lang">bash</span>
            <button class="copy-btn" data-copy="cli">
              <svg class="icon"><use href="#copy"/></svg>
            </button>
          </div>
          <pre><code class="language-bash"># Install
pip install phantom-guard

# Validate a single package
phantom-guard validate flask-gpt-helper

# Validate multiple packages
phantom-guard validate requests numpy flask

# Check your requirements.txt
phantom-guard validate -r requirements.txt

# Use different registry
phantom-guard validate lodash-ai --registry npm</code></pre>
        </div>
      </div>

      <div class="tab-panel" id="tab-python">
        <div class="code-block">
          <div class="code-header">
            <span class="code-lang">python</span>
            <button class="copy-btn" data-copy="python">
              <svg class="icon"><use href="#copy"/></svg>
            </button>
          </div>
          <pre><code class="language-python">from phantom_guard import validate_package, Recommendation

# Synchronous validation
result = validate_package_sync("flask-gpt-helper")

if result.recommendation == Recommendation.BLOCK:
    print(f"Blocked: {result.package_name}")
    print(f"Risk Score: {result.risk_score}")
    for signal in result.signals:
        print(f"  - {signal.description}")

# Async validation
import asyncio

async def check_packages():
    packages = ["requests", "flask-ai-helper", "numpy"]
    results = await validate_batch(packages)

    for result in results:
        if result.is_risky:
            print(f"Warning: {result.package_name}")</code></pre>
        </div>
      </div>

      <div class="tab-panel" id="tab-github">
        <div class="code-block">
          <div class="code-header">
            <span class="code-lang">yaml</span>
            <button class="copy-btn" data-copy="github">
              <svg class="icon"><use href="#copy"/></svg>
            </button>
          </div>
          <pre><code class="language-yaml"># .github/workflows/phantom-guard.yml
name: Security Scan

on:
  pull_request:
    paths:
      - 'requirements*.txt'
      - 'pyproject.toml'

jobs:
  phantom-guard:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Phantom Guard
        run: pip install phantom-guard

      - name: Scan requirements
        run: phantom-guard validate -r requirements.txt

      - name: Scan pyproject.toml
        run: phantom-guard validate -r pyproject.toml</code></pre>
        </div>
      </div>

      <div class="tab-panel" id="tab-precommit">
        <div class="code-block">
          <div class="code-header">
            <span class="code-lang">yaml</span>
            <button class="copy-btn" data-copy="precommit">
              <svg class="icon"><use href="#copy"/></svg>
            </button>
          </div>
          <pre><code class="language-yaml"># .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: phantom-guard
        name: Phantom Guard
        entry: phantom-guard validate -r
        language: system
        files: requirements.*\.txt$
        pass_filenames: true</code></pre>
        </div>
      </div>
    </div>
  `;
}

export function initIntegrationTabs() {
  const tabs = document.querySelectorAll('.tab-btn');
  const panels = document.querySelectorAll('.tab-panel');

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const target = tab.dataset.tab;

      tabs.forEach(t => t.classList.remove('active'));
      panels.forEach(p => p.classList.remove('active'));

      tab.classList.add('active');
      document.getElementById(`tab-${target}`).classList.add('active');
    });
  });
}
```

### Task 5.2: Integration Styles (1h)

**src/styles/integration.css:**
```css
#integration {
  padding: var(--space-24) var(--space-8);
  background: var(--color-surface);
}

.integration-tabs {
  display: flex;
  justify-content: center;
  gap: var(--space-2);
  margin-bottom: var(--space-8);
  flex-wrap: wrap;
}

.tab-btn {
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-md);
  font-weight: 500;
  color: var(--color-subtext);
  transition: all var(--duration-fast) var(--ease-out);
}

.tab-btn:hover {
  color: var(--color-text);
  background: var(--color-overlay);
}

.tab-btn.active {
  background: var(--color-mauve);
  color: var(--color-base);
}

.integration-content {
  max-width: 800px;
  margin: 0 auto;
}

.tab-panel {
  display: none;
  animation: fadeIn var(--duration-fast) var(--ease-out);
}

.tab-panel.active {
  display: block;
}

.code-block {
  background: var(--color-base);
  border-radius: var(--radius-lg);
  overflow: hidden;
  border: 1px solid var(--color-overlay);
}

.code-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-3) var(--space-4);
  background: var(--color-overlay);
  border-bottom: 1px solid var(--color-surface);
}

.code-lang {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  text-transform: uppercase;
  color: var(--color-subtext);
  letter-spacing: 0.1em;
}

.copy-btn {
  padding: var(--space-1);
  color: var(--color-subtext);
  transition: color var(--duration-fast);
}

.copy-btn:hover {
  color: var(--color-mauve);
}

.copy-btn.copied {
  color: var(--color-green);
}

.code-block pre {
  padding: var(--space-4);
  overflow-x: auto;
  margin: 0;
}

.code-block code {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  line-height: 1.6;
  color: var(--color-text);
}

/* Syntax highlighting */
.token.comment { color: var(--color-subtext); }
.token.keyword { color: var(--color-mauve); }
.token.string { color: var(--color-green); }
.token.function { color: var(--color-blue); }
.token.number { color: var(--color-yellow); }
.token.operator { color: var(--color-red); }
.token.class-name { color: var(--color-yellow); }
```

### Task 5.3: Footer Section (0.5h)

**src/sections/footer.js:**
```javascript
/**
 * [HOSTILE FIX] Dynamic version from package.json via Vite
 *
 * Vite can import JSON files and use define to inject build-time values.
 * Alternative: use import.meta.env.VITE_APP_VERSION from vite.config.js
 */

// Import version from package.json (Vite handles this automatically)
import { version } from '../../package.json';

export function createFooter() {
  return `
    <div class="footer-content">
      <div class="footer-brand">
        <span class="footer-logo">👻</span>
        <span class="footer-name">Phantom Guard</span>
      </div>

      <div class="footer-links">
        <a href="https://github.com/matteocpnz/phantom-guard" target="_blank" rel="noopener noreferrer">
          <svg class="icon"><use href="#github"/></svg>
          GitHub
        </a>
        <a href="https://pypi.org/project/phantom-guard/" target="_blank" rel="noopener noreferrer">
          <svg class="icon"><use href="#package"/></svg>
          PyPI
        </a>
        <a href="#" target="_blank" rel="noopener noreferrer">
          <svg class="icon"><use href="#book"/></svg>
          Docs
        </a>
      </div>

      <div class="footer-meta">
        <p>Created by <strong>Matteo Panzeri</strong></p>
        <p>MIT License</p>
        <p class="version">v${version}</p>
      </div>
    </div>
  `;
}
```

**[HOSTILE FIX] Update vite.config.js to enable JSON imports:**
```javascript
// vite.config.js - add to existing config
export default defineConfig({
  // ... existing config
  json: {
    stringify: false, // Allow importing package.json
  },
});
```

### Task 5.4: Footer Styles (0.5h)

**src/styles/footer.css:**
```css
#footer {
  padding: var(--space-12) var(--space-8);
  background: var(--color-base);
  border-top: 1px solid var(--color-overlay);
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--space-6);
}

.footer-brand {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.footer-logo {
  font-size: var(--text-2xl);
}

.footer-name {
  font-weight: 600;
  font-size: var(--text-lg);
}

.footer-links {
  display: flex;
  gap: var(--space-6);
}

.footer-links a {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  color: var(--color-subtext);
  font-size: var(--text-sm);
}

.footer-links a:hover {
  color: var(--color-mauve);
}

.footer-links .icon {
  width: 16px;
  height: 16px;
}

.footer-meta {
  text-align: right;
  font-size: var(--text-sm);
  color: var(--color-subtext);
}

.footer-meta strong {
  color: var(--color-text);
}

.footer-meta .version {
  font-family: var(--font-mono);
  color: var(--color-mauve);
}

@media (max-width: 768px) {
  .footer-content {
    flex-direction: column;
    text-align: center;
  }

  .footer-meta {
    text-align: center;
  }
}
```

### Task 5.5: Mobile Responsive Polish (2h)

**src/styles/responsive.css:**
```css
/* Global responsive adjustments */
@media (max-width: 1200px) {
  :root {
    --text-5xl: 3rem;
    --text-4xl: 2.25rem;
  }
}

@media (max-width: 900px) {
  :root {
    --text-5xl: 2.5rem;
    --text-4xl: 2rem;
    --space-24: 4rem;
    --space-16: 3rem;
  }

  .hero-container {
    grid-template-columns: 1fr;
    text-align: center;
  }

  .hero-terminal {
    order: -1;
    max-width: 500px;
    margin: 0 auto;
  }

  .hero-ctas {
    justify-content: center;
    flex-direction: column;
    align-items: center;
  }

  .hero-stats {
    justify-content: center;
  }

  .playground-layout {
    grid-template-columns: 1fr;
  }

  .steps-container {
    padding: 0 var(--space-4);
  }

  .step {
    grid-template-columns: 1fr;
  }

  .step-icon {
    margin: 0 auto var(--space-4);
  }

  .step-content {
    text-align: center;
  }

  .perf-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 600px) {
  :root {
    --text-5xl: 2rem;
    --text-4xl: 1.75rem;
    --text-3xl: 1.5rem;
    --space-24: 3rem;
    --space-16: 2rem;
    --space-12: 1.5rem;
  }

  .section {
    padding-left: var(--space-4);
    padding-right: var(--space-4);
  }

  .hero-badge {
    font-size: var(--text-xs);
  }

  .btn {
    width: 100%;
    justify-content: center;
  }

  .integration-tabs {
    overflow-x: auto;
    justify-content: flex-start;
    padding-bottom: var(--space-2);
  }

  .tab-btn {
    flex-shrink: 0;
  }

  .code-block pre {
    font-size: var(--text-xs);
  }

  .comparison-row {
    grid-template-columns: 1fr;
    gap: var(--space-2);
  }

  .result-card {
    padding: var(--space-4);
  }
}

/* Touch-friendly interactions */
@media (hover: none) {
  .btn:hover {
    transform: none;
  }

  .tab-btn:hover {
    background: transparent;
    color: var(--color-subtext);
  }

  .tab-btn.active:hover {
    background: var(--color-mauve);
    color: var(--color-base);
  }
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }

  .hero-terminal::before {
    animation: none;
  }
}

/* High contrast */
@media (prefers-contrast: high) {
  :root {
    --color-overlay: #555555;
    --color-subtext: #cccccc;
  }

  .btn {
    border: 2px solid currentColor;
  }
}
```

### Task 5.6: Micro-interactions & Polish (1.5h)

**src/animations/micro.js:**
```javascript
// Copy to clipboard with feedback
export function initCopyButtons() {
  document.querySelectorAll('.copy-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      const target = btn.dataset.copy;
      const code = document.querySelector(`#tab-${target} code`).textContent;

      await navigator.clipboard.writeText(code);

      btn.classList.add('copied');
      const icon = btn.querySelector('.icon use');
      const originalHref = icon.getAttribute('href');
      icon.setAttribute('href', '#check');

      setTimeout(() => {
        btn.classList.remove('copied');
        icon.setAttribute('href', originalHref);
      }, 2000);
    });
  });
}

// Smooth scroll for anchor links
export function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', (e) => {
      e.preventDefault();
      const target = document.querySelector(anchor.getAttribute('href'));
      if (target) {
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });
}

// Button ripple effect
export function initButtonRipples() {
  document.querySelectorAll('.btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const ripple = document.createElement('span');
      ripple.className = 'ripple';
      ripple.style.left = `${e.offsetX}px`;
      ripple.style.top = `${e.offsetY}px`;
      btn.appendChild(ripple);
      setTimeout(() => ripple.remove(), 600);
    });
  });
}

// Loading states
export function setLoading(element, isLoading) {
  if (isLoading) {
    element.classList.add('loading');
    element.disabled = true;
  } else {
    element.classList.remove('loading');
    element.disabled = false;
  }
}
```

**Add to animations.css:**
```css
/* Ripple effect */
.btn {
  position: relative;
  overflow: hidden;
}

.ripple {
  position: absolute;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  transform: translate(-50%, -50%) scale(0);
  animation: ripple 0.6s ease-out;
  pointer-events: none;
}

@keyframes ripple {
  to {
    transform: translate(-50%, -50%) scale(10);
    opacity: 0;
  }
}

/* Loading state */
.loading {
  position: relative;
  pointer-events: none;
}

.loading::after {
  content: '';
  position: absolute;
  inset: 0;
  background: rgba(30, 30, 46, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 20px;
  height: 20px;
  margin: -10px 0 0 -10px;
  border: 2px solid var(--color-overlay);
  border-top-color: var(--color-mauve);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  z-index: 1;
}

/* Focus states for accessibility */
:focus-visible {
  outline: 2px solid var(--color-mauve);
  outline-offset: 2px;
}

button:focus-visible,
a:focus-visible {
  outline: 2px solid var(--color-mauve);
  outline-offset: 2px;
}

/* Skip link for accessibility */
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  background: var(--color-mauve);
  color: var(--color-base);
  padding: var(--space-2) var(--space-4);
  z-index: 100;
  transition: top var(--duration-fast);
}

.skip-link:focus {
  top: 0;
}
```

### Task 5.7: Benchmark Service (1h) [HOSTILE FIX: Missing Logic]

**[HOSTILE FIX] Day 4 created benchmark UI but benchmark logic was missing.**

**src/services/benchmark.js:**
```javascript
import { validatePackage } from './validator.js';

/**
 * [HOSTILE FIX] Benchmark logic for performance section
 *
 * Generates test packages and runs batch validation to demonstrate
 * Phantom Guard's performance characteristics.
 */

// Test package patterns
const TEST_PACKAGES = {
  safe: ['requests', 'numpy', 'flask', 'django', 'pandas', 'scipy', 'pillow', 'beautifulsoup4'],
  typosquat: ['reqeusts', 'numpyy', 'flaask', 'djnago', 'pandsa', 'sciipy', 'pilloow', 'beautifulsoupp'],
  hallucination: ['flask-gpt-helper', 'django-ai-assistant', 'pytorch-llm-utils', 'numpy-chatgpt', 'pandas-openai'],
};

/**
 * Generate a mix of test packages for benchmarking
 * @param {number} count - Number of packages to generate
 * @returns {string[]} Array of package names
 */
export function generateTestPackages(count) {
  const packages = [];
  const categories = Object.keys(TEST_PACKAGES);

  for (let i = 0; i < count; i++) {
    // Rotate through categories
    const category = categories[i % categories.length];
    const categoryPackages = TEST_PACKAGES[category];
    const pkg = categoryPackages[i % categoryPackages.length];
    packages.push(pkg);
  }

  return packages;
}

/**
 * Run benchmark with specified number of packages
 * @param {number} count - Number of packages to validate
 * @param {Function} onProgress - Progress callback (current, total)
 * @returns {Promise<BenchmarkResult>}
 */
export async function runBenchmark(count, onProgress = null) {
  const packages = generateTestPackages(count);
  const startTime = performance.now();
  const results = [];

  // Run validations with progress tracking
  for (let i = 0; i < packages.length; i++) {
    const result = await validatePackage(packages[i], 'pypi');
    results.push(result);

    if (onProgress) {
      onProgress(i + 1, packages.length);
    }
  }

  const elapsed = performance.now() - startTime;

  // Calculate statistics
  const times = results.map(r => r.elapsed);
  const avgTime = times.reduce((a, b) => a + b, 0) / times.length;
  const minTime = Math.min(...times);
  const maxTime = Math.max(...times);
  const p99Time = times.sort((a, b) => a - b)[Math.floor(times.length * 0.99)] || maxTime;

  // Count results by recommendation
  const breakdown = results.reduce((acc, r) => {
    acc[r.recommendation] = (acc[r.recommendation] || 0) + 1;
    return acc;
  }, {});

  return {
    count,
    elapsed: Math.round(elapsed),
    avgTime: Math.round(avgTime),
    minTime: Math.round(minTime),
    maxTime: Math.round(maxTime),
    p99Time: Math.round(p99Time),
    throughput: Math.round(count / (elapsed / 1000)), // packages per second
    breakdown,
    results,
  };
}

/**
 * Run concurrent benchmark (validates packages in parallel)
 * @param {number} count - Number of packages to validate
 * @param {number} concurrency - Number of concurrent validations
 * @returns {Promise<BenchmarkResult>}
 */
export async function runConcurrentBenchmark(count, concurrency = 5) {
  const packages = generateTestPackages(count);
  const startTime = performance.now();
  const results = [];

  // Process in batches
  for (let i = 0; i < packages.length; i += concurrency) {
    const batch = packages.slice(i, i + concurrency);
    const batchResults = await Promise.all(
      batch.map(pkg => validatePackage(pkg, 'pypi'))
    );
    results.push(...batchResults);
  }

  const elapsed = performance.now() - startTime;

  const times = results.map(r => r.elapsed);
  const avgTime = times.reduce((a, b) => a + b, 0) / times.length;

  return {
    count,
    concurrency,
    elapsed: Math.round(elapsed),
    avgTime: Math.round(avgTime),
    throughput: Math.round(count / (elapsed / 1000)),
    breakdown: results.reduce((acc, r) => {
      acc[r.recommendation] = (acc[r.recommendation] || 0) + 1;
      return acc;
    }, {}),
  };
}
```

**Update Day 4 performance section to use benchmark:**
```javascript
// In src/sections/performance.js, update initPerformanceSection:
import { runBenchmark } from '../services/benchmark.js';

export function initPerformanceSection() {
  const runBtn = document.querySelector('#run-benchmark');
  const resultEl = document.querySelector('#benchmark-result');

  if (!runBtn) return;

  runBtn.addEventListener('click', async () => {
    runBtn.disabled = true;
    runBtn.textContent = 'Running...';
    resultEl.innerHTML = '<div class="loading">Benchmarking...</div>';

    try {
      const result = await runBenchmark(50, (current, total) => {
        resultEl.innerHTML = `<div class="progress">Validating ${current}/${total}...</div>`;
      });

      resultEl.innerHTML = `
        <div class="benchmark-result">
          <div class="stat">
            <span class="stat-value">${result.count}</span>
            <span class="stat-label">Packages</span>
          </div>
          <div class="stat">
            <span class="stat-value">${result.elapsed}ms</span>
            <span class="stat-label">Total Time</span>
          </div>
          <div class="stat">
            <span class="stat-value">${result.avgTime}ms</span>
            <span class="stat-label">Avg/Package</span>
          </div>
          <div class="stat">
            <span class="stat-value">${result.throughput}/s</span>
            <span class="stat-label">Throughput</span>
          </div>
        </div>
      `;
    } catch (error) {
      resultEl.innerHTML = `<div class="error">Benchmark failed: ${error.message}</div>`;
    } finally {
      runBtn.disabled = false;
      runBtn.textContent = 'Run Benchmark';
    }
  });
}
```

---

## Deliverables

- [ ] Integration section with 4 tabs
- [ ] Code blocks with syntax highlighting
- [ ] Copy-to-clipboard functionality
- [ ] Footer with links and credits
- [ ] Full mobile responsive design
- [ ] Touch-friendly interactions
- [ ] Reduced motion support
- [ ] Accessibility features (focus, skip link)
- [ ] Button ripple effects
- [ ] Loading states

---

## Exit Criteria

- [ ] All tabs switch smoothly
- [ ] Copy button shows feedback
- [ ] Layout works at 320px width
- [ ] All touch interactions work
- [ ] Keyboard navigation works
- [ ] No horizontal scroll on mobile
- [ ] Lighthouse Accessibility score > 90
