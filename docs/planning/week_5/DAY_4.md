# Week 5 Day 4: Features & Performance Sections

> **Date**: 2026-01-04
> **Focus**: How It Works, Performance Metrics
> **Estimated Hours**: 8

---

## Objectives

1. Build "How It Works" section with 3-step flow
2. Create performance visualization component
3. Implement benchmark demo
4. Add scroll-triggered animations

---

## Tasks

### Task 4.1: How It Works Section (2.5h)

**src/sections/how-it-works.js:**
```javascript
export function createHowItWorksSection() {
  return `
    <div class="section-header">
      <h2 class="section-title">How It Works</h2>
      <p class="section-subtitle">
        Three layers of defense against package supply chain attacks
      </p>
    </div>

    <div class="steps-container">
      <div class="step" data-step="1">
        <div class="step-icon">
          <svg class="icon"><use href="#search"/></svg>
        </div>
        <div class="step-content">
          <h3>1. Pattern Detection</h3>
          <p>
            Analyzes package names against known hallucination patterns.
            Catches AI-generated names like <code>flask-gpt-helper</code>.
          </p>
          <div class="step-demo pattern-demo">
            <code class="pattern">*-gpt-*</code>
            <code class="pattern">*-ai-*</code>
            <code class="pattern">*-llm-*</code>
          </div>
        </div>
      </div>

      <div class="step-connector">
        <div class="connector-line"></div>
        <div class="connector-arrow"></div>
      </div>

      <div class="step" data-step="2">
        <div class="step-icon">
          <svg class="icon"><use href="#shield"/></svg>
        </div>
        <div class="step-content">
          <h3>2. Typosquat Detection</h3>
          <p>
            Computes edit distance to popular packages.
            Flags <code>requets</code> as similar to <code>requests</code>.
          </p>
          <div class="step-demo typo-demo">
            <div class="typo-example">
              <span class="typo-input">requets</span>
              <span class="typo-arrow">→</span>
              <span class="typo-match">requests</span>
              <span class="typo-distance">dist: 1</span>
            </div>
          </div>
        </div>
      </div>

      <div class="step-connector">
        <div class="connector-line"></div>
        <div class="connector-arrow"></div>
      </div>

      <div class="step" data-step="3">
        <div class="step-icon">
          <svg class="icon"><use href="#globe"/></svg>
        </div>
        <div class="step-content">
          <h3>3. Registry Verification</h3>
          <p>
            Checks if package exists on PyPI, npm, or crates.io.
            Non-existent packages with risky names = high threat.
          </p>
          <div class="step-demo registry-demo">
            <div class="registry-check">
              <span class="registry-name">PyPI</span>
              <span class="registry-status not-found">NOT FOUND</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="result-showcase">
      <div class="result-card">
        <div class="result-header">
          <span class="result-package">flask-gpt-helper</span>
          <span class="result-badge high-risk">HIGH_RISK</span>
        </div>
        <div class="result-signals">
          <div class="signal">
            <span class="signal-icon">⚠️</span>
            <span>AI hallucination pattern detected</span>
          </div>
          <div class="signal">
            <span class="signal-icon">❌</span>
            <span>Package not found on PyPI</span>
          </div>
        </div>
        <div class="result-score">
          Risk Score: <strong>0.85</strong>
        </div>
      </div>
    </div>
  `;
}
```

### Task 4.2: How It Works Styles (1.5h)

**src/styles/how-it-works.css:**
```css
#how-it-works {
  padding: var(--space-24) var(--space-8);
  background: linear-gradient(
    180deg,
    var(--color-base) 0%,
    var(--color-surface) 100%
  );
}

.section-header {
  text-align: center;
  margin-bottom: var(--space-16);
}

.section-title {
  font-size: var(--text-4xl);
  margin-bottom: var(--space-4);
}

.section-subtitle {
  font-size: var(--text-lg);
  color: var(--color-subtext);
  max-width: 50ch;
  margin: 0 auto;
}

.steps-container {
  max-width: 800px;
  margin: 0 auto;
}

.step {
  display: grid;
  grid-template-columns: 60px 1fr;
  gap: var(--space-6);
  padding: var(--space-8);
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-overlay);
  opacity: 0;
  transform: translateX(-20px);
  transition: all var(--duration-slow) var(--ease-out);
}

.step.visible {
  opacity: 1;
  transform: translateX(0);
}

.step-icon {
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-overlay);
  border-radius: var(--radius-md);
  color: var(--color-mauve);
}

.step-icon .icon {
  width: 28px;
  height: 28px;
}

.step-content h3 {
  font-size: var(--text-xl);
  margin-bottom: var(--space-2);
}

.step-content p {
  color: var(--color-subtext);
  margin-bottom: var(--space-4);
}

.step-content code {
  background: var(--color-overlay);
  padding: 2px 6px;
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);
  color: var(--color-mauve);
}

.step-demo {
  margin-top: var(--space-4);
  padding: var(--space-4);
  background: var(--color-base);
  border-radius: var(--radius-md);
  font-family: var(--font-mono);
  font-size: var(--text-sm);
}

.pattern-demo {
  display: flex;
  gap: var(--space-3);
  flex-wrap: wrap;
}

.pattern {
  background: rgba(203, 166, 247, 0.1);
  color: var(--color-mauve);
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-sm);
}

.step-connector {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-4) 0;
}

.connector-line {
  width: 2px;
  height: 30px;
  background: var(--color-overlay);
}

.connector-arrow {
  width: 0;
  height: 0;
  border-left: 6px solid transparent;
  border-right: 6px solid transparent;
  border-top: 8px solid var(--color-overlay);
}

.typo-example {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.typo-input {
  color: var(--color-red);
  text-decoration: line-through;
}

.typo-arrow {
  color: var(--color-subtext);
}

.typo-match {
  color: var(--color-green);
}

.typo-distance {
  background: var(--color-overlay);
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  color: var(--color-yellow);
  font-size: var(--text-xs);
}

.registry-check {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.registry-status {
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  font-size: var(--text-xs);
  font-weight: 600;
}

.registry-status.not-found {
  background: rgba(243, 139, 168, 0.2);
  color: var(--color-red);
}

.result-showcase {
  max-width: 500px;
  margin: var(--space-12) auto 0;
}

.result-card {
  background: var(--color-surface);
  border: 2px solid var(--color-red);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  box-shadow: 0 0 30px rgba(243, 139, 168, 0.2);
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
}

.result-package {
  font-family: var(--font-mono);
  font-size: var(--text-lg);
  font-weight: 600;
}

.result-badge {
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);
  font-weight: 600;
}

.result-badge.high-risk {
  background: rgba(243, 139, 168, 0.2);
  color: var(--color-red);
}

.result-signals {
  margin-bottom: var(--space-4);
}

.result-signals .signal {
  display: flex;
  gap: var(--space-2);
  padding: var(--space-2) 0;
  color: var(--color-subtext);
  font-size: var(--text-sm);
}

.result-score {
  text-align: right;
  color: var(--color-subtext);
  font-family: var(--font-mono);
}

.result-score strong {
  color: var(--color-red);
  font-size: var(--text-xl);
}
```

### Task 4.3: Performance Metrics Section (2h)

**src/sections/performance.js:**
```javascript
export function createPerformanceSection() {
  return `
    <div class="section-header">
      <h2 class="section-title">Built for Speed</h2>
      <p class="section-subtitle">
        Real-time validation that doesn't slow down your workflow
      </p>
    </div>

    <div class="perf-grid">
      <div class="perf-card">
        <div class="perf-metric">
          <span class="perf-value" data-value="200">&lt;200</span>
          <span class="perf-unit">ms</span>
        </div>
        <div class="perf-label">Uncached Validation</div>
        <div class="perf-bar">
          <div class="perf-fill" style="--width: 20%"></div>
        </div>
        <div class="perf-context">Full registry lookup + analysis</div>
      </div>

      <div class="perf-card">
        <div class="perf-metric">
          <span class="perf-value" data-value="10">&lt;10</span>
          <span class="perf-unit">ms</span>
        </div>
        <div class="perf-label">Cached Validation</div>
        <div class="perf-bar">
          <div class="perf-fill cached" style="--width: 1%"></div>
        </div>
        <div class="perf-context">In-memory cache hit</div>
      </div>

      <div class="perf-card">
        <div class="perf-metric">
          <span class="perf-value" data-value="50">50</span>
          <span class="perf-unit">pkgs/5s</span>
        </div>
        <div class="perf-label">Batch Processing</div>
        <div class="perf-bar">
          <div class="perf-fill batch" style="--width: 100%"></div>
        </div>
        <div class="perf-context">Concurrent validation</div>
      </div>
    </div>

    <div class="benchmark-demo">
      <h3>Live Benchmark</h3>
      <div class="benchmark-controls">
        <button class="btn btn-secondary" id="run-benchmark">
          <svg class="icon"><use href="#play"/></svg>
          Run Benchmark
        </button>
        <select id="benchmark-size">
          <option value="10">10 packages</option>
          <option value="25">25 packages</option>
          <option value="50">50 packages</option>
        </select>
      </div>
      <div class="benchmark-results" id="benchmark-results">
        <div class="benchmark-placeholder">
          Click "Run Benchmark" to test validation speed
        </div>
      </div>
    </div>

    <div class="cache-comparison">
      <h3>Cache Impact</h3>
      <div class="comparison-chart">
        <div class="comparison-row">
          <span class="comparison-label">First Request</span>
          <div class="comparison-bar uncached">
            <div class="bar-fill" style="width: 100%"></div>
            <span class="bar-time">~150ms</span>
          </div>
        </div>
        <div class="comparison-row">
          <span class="comparison-label">Cached Request</span>
          <div class="comparison-bar cached">
            <div class="bar-fill" style="width: 5%"></div>
            <span class="bar-time">~8ms</span>
          </div>
        </div>
      </div>
      <p class="comparison-note">
        Cache TTL: 1 hour • Memory efficient LRU eviction
      </p>
    </div>
  `;
}
```

### Task 4.4: Performance Styles (1h)

**src/styles/performance.css:**
```css
#performance {
  padding: var(--space-24) var(--space-8);
}

.perf-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--space-6);
  max-width: 1000px;
  margin: 0 auto var(--space-12);
}

.perf-card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  border: 1px solid var(--color-overlay);
}

.perf-metric {
  display: flex;
  align-items: baseline;
  gap: var(--space-1);
  margin-bottom: var(--space-2);
}

.perf-value {
  font-size: var(--text-4xl);
  font-weight: 700;
  font-family: var(--font-mono);
  color: var(--color-mauve);
}

.perf-unit {
  font-size: var(--text-lg);
  color: var(--color-subtext);
}

.perf-label {
  font-size: var(--text-lg);
  font-weight: 500;
  margin-bottom: var(--space-4);
}

.perf-bar {
  height: 8px;
  background: var(--color-overlay);
  border-radius: 4px;
  margin-bottom: var(--space-2);
  overflow: hidden;
}

.perf-fill {
  height: 100%;
  width: var(--width);
  background: var(--color-mauve);
  border-radius: 4px;
  transition: width 1s var(--ease-out);
}

.perf-fill.cached {
  background: var(--color-green);
}

.perf-fill.batch {
  background: linear-gradient(90deg, var(--color-mauve), var(--color-blue));
}

.perf-context {
  font-size: var(--text-sm);
  color: var(--color-subtext);
}

.benchmark-demo {
  max-width: 700px;
  margin: 0 auto var(--space-12);
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
}

.benchmark-demo h3 {
  margin-bottom: var(--space-4);
}

.benchmark-controls {
  display: flex;
  gap: var(--space-4);
  margin-bottom: var(--space-4);
}

.benchmark-controls select {
  padding: var(--space-2) var(--space-4);
  background: var(--color-overlay);
  border: 1px solid var(--color-overlay);
  border-radius: var(--radius-md);
  color: var(--color-text);
  font-family: inherit;
}

.benchmark-results {
  min-height: 100px;
  background: var(--color-base);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  font-family: var(--font-mono);
  font-size: var(--text-sm);
}

.benchmark-placeholder {
  text-align: center;
  color: var(--color-subtext);
  padding: var(--space-8);
}

.cache-comparison {
  max-width: 600px;
  margin: 0 auto;
}

.cache-comparison h3 {
  text-align: center;
  margin-bottom: var(--space-6);
}

.comparison-chart {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.comparison-row {
  display: grid;
  grid-template-columns: 120px 1fr;
  gap: var(--space-4);
  align-items: center;
}

.comparison-label {
  font-size: var(--text-sm);
  color: var(--color-subtext);
}

.comparison-bar {
  height: 32px;
  background: var(--color-overlay);
  border-radius: var(--radius-sm);
  position: relative;
  overflow: hidden;
}

.comparison-bar .bar-fill {
  height: 100%;
  background: var(--color-red);
  transition: width 1s var(--ease-out);
}

.comparison-bar.cached .bar-fill {
  background: var(--color-green);
}

.comparison-bar .bar-time {
  position: absolute;
  right: var(--space-3);
  top: 50%;
  transform: translateY(-50%);
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  color: var(--color-text);
}

.comparison-note {
  text-align: center;
  font-size: var(--text-sm);
  color: var(--color-subtext);
  margin-top: var(--space-4);
}
```

### Task 4.5: Scroll Animations (1h)

**src/animations/scroll.js:**
```javascript
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

export function initScrollAnimations() {
  // How It Works steps
  gsap.utils.toArray('.step').forEach((step, i) => {
    gsap.from(step, {
      scrollTrigger: {
        trigger: step,
        start: 'top 80%',
        toggleActions: 'play none none reverse'
      },
      opacity: 0,
      x: -30,
      duration: 0.6,
      delay: i * 0.2,
      ease: 'power2.out'
    });
  });

  // Performance cards
  gsap.utils.toArray('.perf-card').forEach((card, i) => {
    gsap.from(card, {
      scrollTrigger: {
        trigger: card,
        start: 'top 85%'
      },
      opacity: 0,
      y: 30,
      duration: 0.5,
      delay: i * 0.1
    });
  });

  // Perf bars animate when in view
  gsap.utils.toArray('.perf-fill').forEach(bar => {
    const width = bar.style.getPropertyValue('--width');
    bar.style.width = '0';

    ScrollTrigger.create({
      trigger: bar,
      start: 'top 90%',
      onEnter: () => {
        gsap.to(bar, { width: width, duration: 1, ease: 'power2.out' });
      }
    });
  });

  // Cache comparison bars
  gsap.utils.toArray('.comparison-bar .bar-fill').forEach(bar => {
    const width = bar.style.width;
    bar.style.width = '0';

    ScrollTrigger.create({
      trigger: bar,
      start: 'top 90%',
      onEnter: () => {
        gsap.to(bar, { width: width, duration: 1, ease: 'power2.out' });
      }
    });
  });

  // Result card pulse
  gsap.to('.result-card', {
    scrollTrigger: {
      trigger: '.result-card',
      start: 'top 80%'
    },
    boxShadow: '0 0 40px rgba(243, 139, 168, 0.4)',
    duration: 0.5,
    yoyo: true,
    repeat: 1
  });
}
```

---

## Deliverables

- [ ] How It Works section with 3-step flow
- [ ] Visual step connectors with arrows
- [ ] Performance metrics cards
- [ ] Animated progress bars
- [ ] Live benchmark demo UI
- [ ] Cache comparison chart
- [ ] Scroll-triggered animations

---

## Exit Criteria

- [ ] Steps animate in sequence on scroll
- [ ] Performance bars animate from 0
- [ ] All animations run at 60fps
- [ ] Responsive layout works at all sizes
- [ ] Benchmark button wired (logic in Day 5)
