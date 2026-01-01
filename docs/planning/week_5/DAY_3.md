# Week 5 Day 3: Live Playground

> **Date**: 2026-01-03
> **Focus**: Interactive Validation Demo
> **Estimated Hours**: 8

---

## Objectives

1. Build live validation playground
2. **[HOSTILE FIX]** Implement CORS proxy for live API access
3. Create risk visualization components
4. Implement real-time feedback

---

## Tasks

### Task 3.1: Validation Service (2.5h) [HOSTILE FIX: CORS Proxy]

**[HOSTILE FIX] CORS Solution Architecture:**

The browser cannot directly call PyPI/npm/crates APIs due to CORS restrictions.
We implement a **hybrid approach**:

1. **Primary**: Use corsproxy.io as a reliable CORS proxy service
2. **Fallback**: If proxy fails, use enhanced mock data with realistic patterns
3. **UI Indicator**: Show whether result is from live API or mock

```
┌─────────────────────────────────────────────────────────────┐
│                    CORS PROXY FLOW                          │
├─────────────────────────────────────────────────────────────┤
│  Browser  →  corsproxy.io  →  PyPI/npm/crates  →  Response  │
│                                                             │
│  If proxy fails:                                            │
│  Browser  →  Enhanced Mock Data  →  (labeled as "Demo")     │
└─────────────────────────────────────────────────────────────┘
```

**src/services/validator.js:**
```javascript
/**
 * [HOSTILE FIX] CORS Proxy Configuration
 *
 * We use corsproxy.io which is a reliable, free CORS proxy.
 * Fallback to mock data if proxy is unavailable.
 */

// CORS proxy configuration
const CORS_PROXY = 'https://corsproxy.io/?';

// Registry API endpoints
const REGISTRY_APIS = {
  pypi: (name) => `${CORS_PROXY}${encodeURIComponent(`https://pypi.org/pypi/${name}/json`)}`,
  npm: (name) => `${CORS_PROXY}${encodeURIComponent(`https://registry.npmjs.org/${name}`)}`,
  crates: (name) => `${CORS_PROXY}${encodeURIComponent(`https://crates.io/api/v1/crates/${name}`)}`,
};

// Configuration
const CONFIG = {
  useLiveAPI: true,       // Try live API first
  timeout: 5000,          // 5 second timeout
  fallbackToMock: true,   // Use mock if live fails
};

// Enhanced mock data for common packages
const MOCK_RESULTS = {
  // Safe packages (exist on PyPI)
  'requests': { exists: true, risk: 0.05, recommendation: 'safe', signals: [], isLive: false },
  'numpy': { exists: true, risk: 0.05, recommendation: 'safe', signals: [], isLive: false },
  'flask': { exists: true, risk: 0.05, recommendation: 'safe', signals: [], isLive: false },
  'django': { exists: true, risk: 0.05, recommendation: 'safe', signals: [], isLive: false },
  'pandas': { exists: true, risk: 0.05, recommendation: 'safe', signals: [], isLive: false },

  // Typosquats (high risk)
  'reqeusts': { exists: false, risk: 0.89, recommendation: 'high_risk', isLive: false, signals: [
    { type: 'typosquat', message: 'Typosquat of "requests" (edit distance: 1)', severity: 'high' },
    { type: 'not_found', message: 'Package does not exist on PyPI', severity: 'medium' },
  ]},
  'numpyy': { exists: false, risk: 0.82, recommendation: 'high_risk', isLive: false, signals: [
    { type: 'typosquat', message: 'Typosquat of "numpy" (edit distance: 1)', severity: 'high' },
    { type: 'not_found', message: 'Package does not exist', severity: 'medium' },
  ]},
  'flaask': { exists: false, risk: 0.85, recommendation: 'high_risk', isLive: false, signals: [
    { type: 'typosquat', message: 'Typosquat of "flask" (edit distance: 1)', severity: 'high' },
    { type: 'not_found', message: 'Package does not exist', severity: 'medium' },
  ]},

  // AI hallucination patterns (high risk)
  'flask-gpt-helper': { exists: false, risk: 0.88, recommendation: 'high_risk', isLive: false, signals: [
    { type: 'pattern', message: 'AI hallucination pattern: "-gpt-" suffix', severity: 'high' },
    { type: 'not_found', message: 'Package not found on PyPI', severity: 'medium' },
  ]},
  'pytorch-llm-utils': { exists: false, risk: 0.85, recommendation: 'high_risk', isLive: false, signals: [
    { type: 'pattern', message: 'AI hallucination pattern: "-llm-" suffix', severity: 'high' },
    { type: 'not_found', message: 'Package not found on PyPI', severity: 'medium' },
  ]},
  'django-ai-assistant': { exists: false, risk: 0.82, recommendation: 'high_risk', isLive: false, signals: [
    { type: 'pattern', message: 'AI hallucination pattern: "-ai-" suffix', severity: 'high' },
    { type: 'not_found', message: 'Package not found on PyPI', severity: 'medium' },
  ]},
};

// Hallucination pattern detection (client-side)
const HALLUCINATION_PATTERNS = [
  { regex: /-gpt-/i, message: 'AI hallucination pattern: "-gpt-" suffix' },
  { regex: /-llm-/i, message: 'AI hallucination pattern: "-llm-" suffix' },
  { regex: /-ai-/i, message: 'AI hallucination pattern: "-ai-" suffix' },
  { regex: /-openai/i, message: 'AI hallucination pattern: "-openai" suffix' },
  { regex: /-chatgpt/i, message: 'AI hallucination pattern: "-chatgpt" suffix' },
  { regex: /-langchain/i, message: 'AI hallucination pattern: "-langchain" suffix' },
];

// Popular packages for typosquat detection
const POPULAR_PACKAGES = ['requests', 'numpy', 'flask', 'django', 'pandas', 'scipy', 'tensorflow', 'pytorch', 'keras'];

/**
 * Calculate Levenshtein distance for typosquat detection
 */
function levenshteinDistance(a, b) {
  const matrix = Array(b.length + 1).fill(null).map(() => Array(a.length + 1).fill(null));
  for (let i = 0; i <= a.length; i++) matrix[0][i] = i;
  for (let j = 0; j <= b.length; j++) matrix[j][0] = j;
  for (let j = 1; j <= b.length; j++) {
    for (let i = 1; i <= a.length; i++) {
      const indicator = a[i - 1] === b[j - 1] ? 0 : 1;
      matrix[j][i] = Math.min(matrix[j][i - 1] + 1, matrix[j - 1][i] + 1, matrix[j - 1][i - 1] + indicator);
    }
  }
  return matrix[b.length][a.length];
}

/**
 * Detect typosquats of popular packages
 */
function detectTyposquat(name) {
  const normalized = name.toLowerCase().replace(/[-_]/g, '');
  for (const popular of POPULAR_PACKAGES) {
    const distance = levenshteinDistance(normalized, popular);
    if (distance > 0 && distance <= 2 && normalized !== popular) {
      return { match: popular, distance };
    }
  }
  return null;
}

/**
 * Detect hallucination patterns
 */
function detectPatterns(name) {
  const signals = [];
  for (const pattern of HALLUCINATION_PATTERNS) {
    if (pattern.regex.test(name)) {
      signals.push({ type: 'pattern', message: pattern.message, severity: 'high' });
    }
  }
  return signals;
}

/**
 * [HOSTILE FIX] Main validation function with CORS proxy
 */
export async function validatePackage(name, registry = 'pypi') {
  const startTime = performance.now();
  const normalizedName = name.toLowerCase().trim();

  // Check mock results first for demo packages
  if (MOCK_RESULTS[normalizedName]) {
    await new Promise(r => setTimeout(r, 80 + Math.random() * 40)); // Simulate latency
    const elapsed = performance.now() - startTime;
    return {
      name: normalizedName,
      registry,
      ...MOCK_RESULTS[normalizedName],
      elapsed: Math.round(elapsed),
      source: 'demo', // [HOSTILE FIX] Indicate data source
    };
  }

  // Try live API with CORS proxy
  if (CONFIG.useLiveAPI) {
    try {
      const apiUrl = REGISTRY_APIS[registry](normalizedName);
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), CONFIG.timeout);

      const response = await fetch(apiUrl, { signal: controller.signal });
      clearTimeout(timeoutId);

      const exists = response.ok;
      const elapsed = performance.now() - startTime;

      // Build signals based on local analysis
      const signals = [];
      const typosquat = detectTyposquat(normalizedName);
      if (typosquat) {
        signals.push({
          type: 'typosquat',
          message: `Typosquat of "${typosquat.match}" (edit distance: ${typosquat.distance})`,
          severity: 'high'
        });
      }
      signals.push(...detectPatterns(normalizedName));

      if (!exists) {
        signals.push({ type: 'not_found', message: `Package not found on ${registry.toUpperCase()}`, severity: 'medium' });
      }

      // Calculate risk score
      let risk = 0.05; // Base safe score
      if (!exists) risk += 0.3;
      if (typosquat) risk += 0.4;
      if (detectPatterns(normalizedName).length > 0) risk += 0.3;
      risk = Math.min(risk, 0.95);

      const recommendation = risk > 0.7 ? 'high_risk' : risk > 0.4 ? 'suspicious' : 'safe';

      return {
        name: normalizedName,
        registry,
        exists,
        risk,
        recommendation,
        signals,
        elapsed: Math.round(elapsed),
        source: 'live', // [HOSTILE FIX] Indicate data source
        isLive: true,
      };
    } catch (error) {
      console.warn('[Phantom Guard] Live API failed, falling back to analysis:', error.message);

      if (!CONFIG.fallbackToMock) {
        throw error;
      }
      // Fall through to local analysis
    }
  }

  // Fallback: Local analysis only (no API call)
  const elapsed = performance.now() - startTime;
  const signals = [];
  const typosquat = detectTyposquat(normalizedName);
  if (typosquat) {
    signals.push({
      type: 'typosquat',
      message: `Possible typosquat of "${typosquat.match}" (edit distance: ${typosquat.distance})`,
      severity: 'high'
    });
  }
  signals.push(...detectPatterns(normalizedName));

  // Calculate risk
  let risk = 0.3; // Unknown package base risk
  if (typosquat) risk += 0.4;
  if (detectPatterns(normalizedName).length > 0) risk += 0.3;
  risk = Math.min(risk, 0.95);

  const recommendation = risk > 0.7 ? 'high_risk' : risk > 0.4 ? 'suspicious' : 'unknown';

  return {
    name: normalizedName,
    registry,
    exists: null, // Unknown - couldn't check
    risk,
    recommendation,
    signals,
    elapsed: Math.round(elapsed),
    source: 'analysis', // [HOSTILE FIX] Indicate data source
    isLive: false,
  };
}
```

### Task 3.2: Playground Component (2.5h)

**src/components/playground.js:**
```javascript
import { validatePackage } from '../services/validator.js';

export class PhantomPlayground extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this.debounceTimer = null;
    this.currentRegistry = 'pypi';
  }

  connectedCallback() {
    this.render();
    this.setupListeners();
  }

  render() {
    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: block;
          max-width: 600px;
          margin: 0 auto;
        }

        .playground-input {
          display: flex;
          gap: 8px;
          margin-bottom: 24px;
        }

        .input-wrapper {
          flex: 1;
          position: relative;
        }

        input {
          width: 100%;
          padding: 16px 20px;
          padding-right: 50px;
          font-family: var(--font-mono);
          font-size: 16px;
          background: var(--color-surface);
          border: 2px solid var(--color-overlay);
          border-radius: var(--radius-lg);
          color: var(--color-text);
          outline: none;
          transition: border-color 0.2s ease;
        }

        input:focus {
          border-color: var(--color-mauve);
        }

        input::placeholder {
          color: var(--color-subtext);
        }

        .search-icon {
          position: absolute;
          right: 16px;
          top: 50%;
          transform: translateY(-50%);
          color: var(--color-subtext);
        }

        .registry-tabs {
          display: flex;
          gap: 4px;
          background: var(--color-surface);
          padding: 4px;
          border-radius: var(--radius-md);
        }

        .registry-tab {
          padding: 8px 16px;
          border-radius: var(--radius-sm);
          font-size: 14px;
          font-weight: 500;
          color: var(--color-subtext);
          background: transparent;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .registry-tab:hover {
          color: var(--color-text);
        }

        .registry-tab.active {
          background: var(--color-mauve);
          color: var(--color-base);
        }

        .result {
          background: var(--color-surface);
          border-radius: var(--radius-lg);
          padding: 24px;
          opacity: 0;
          transform: translateY(10px);
          transition: all 0.3s ease;
        }

        .result.visible {
          opacity: 1;
          transform: translateY(0);
        }

        .result-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 20px;
        }

        .result-status {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .status-icon {
          width: 48px;
          height: 48px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 24px;
        }

        .status-icon.safe { background: rgba(166, 227, 161, 0.2); }
        .status-icon.suspicious { background: rgba(249, 226, 175, 0.2); }
        .status-icon.high_risk { background: rgba(243, 139, 168, 0.2); }

        .status-text h3 {
          font-size: 18px;
          font-weight: 600;
          margin-bottom: 4px;
        }

        .status-text span {
          font-size: 14px;
          color: var(--color-subtext);
        }

        .elapsed {
          font-family: var(--font-mono);
          font-size: 14px;
          color: var(--color-subtext);
          background: var(--color-overlay);
          padding: 4px 12px;
          border-radius: var(--radius-sm);
        }

        .signals {
          display: flex;
          flex-direction: column;
          gap: 8px;
          margin-bottom: 20px;
        }

        .signal {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 12px 16px;
          background: var(--color-overlay);
          border-radius: var(--radius-md);
        }

        .signal-icon {
          color: var(--color-yellow);
        }

        .signal-text {
          font-size: 14px;
          color: var(--color-text);
        }

        .risk-meter {
          margin-top: 16px;
        }

        .risk-label {
          display: flex;
          justify-content: space-between;
          margin-bottom: 8px;
          font-size: 14px;
        }

        .risk-bar {
          height: 8px;
          background: var(--color-overlay);
          border-radius: 4px;
          overflow: hidden;
        }

        .risk-fill {
          height: 100%;
          border-radius: 4px;
          transition: width 0.5s ease;
        }

        .risk-fill.safe { background: var(--color-green); }
        .risk-fill.suspicious { background: var(--color-yellow); }
        .risk-fill.high_risk { background: var(--color-red); }

        /* [HOSTILE FIX] Source badge styles */
        .result-meta {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .source-badge {
          display: inline-flex;
          align-items: center;
          gap: 4px;
          padding: 4px 10px;
          border-radius: var(--radius-sm);
          font-size: 11px;
          font-weight: 600;
          font-family: var(--font-mono);
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }

        .source-live {
          background: rgba(166, 227, 161, 0.15);
          color: var(--color-green);
          border: 1px solid rgba(166, 227, 161, 0.3);
        }

        .source-demo {
          background: rgba(137, 180, 250, 0.15);
          color: var(--color-blue);
          border: 1px solid rgba(137, 180, 250, 0.3);
        }

        .source-analysis {
          background: rgba(249, 226, 175, 0.15);
          color: var(--color-yellow);
          border: 1px solid rgba(249, 226, 175, 0.3);
        }

        .source-unknown {
          background: rgba(166, 173, 200, 0.15);
          color: var(--color-subtext);
          border: 1px solid rgba(166, 173, 200, 0.3);
        }

        .loading {
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 40px;
          color: var(--color-subtext);
        }

        .spinner {
          width: 24px;
          height: 24px;
          border: 2px solid var(--color-overlay);
          border-top-color: var(--color-mauve);
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin-right: 12px;
        }

        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      </style>

      <div class="playground-input">
        <div class="input-wrapper">
          <input type="text"
                 placeholder="Enter package name (e.g., reqeusts)"
                 id="package-input"
                 autocomplete="off"
                 spellcheck="false">
          <span class="search-icon">🔍</span>
        </div>
        <div class="registry-tabs">
          <button class="registry-tab active" data-registry="pypi">PyPI</button>
          <button class="registry-tab" data-registry="npm">npm</button>
          <button class="registry-tab" data-registry="crates">crates</button>
        </div>
      </div>

      <div id="result" class="result"></div>
    `;
  }

  setupListeners() {
    const input = this.shadowRoot.querySelector('#package-input');
    const tabs = this.shadowRoot.querySelectorAll('.registry-tab');

    input.addEventListener('input', (e) => this.handleInput(e.target.value));

    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        tabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        this.currentRegistry = tab.dataset.registry;
        if (input.value) {
          this.validate(input.value);
        }
      });
    });
  }

  handleInput(value) {
    clearTimeout(this.debounceTimer);

    if (!value.trim()) {
      this.hideResult();
      return;
    }

    this.debounceTimer = setTimeout(() => {
      this.validate(value.trim());
    }, 300);
  }

  async validate(name) {
    this.showLoading();

    const result = await validatePackage(name, this.currentRegistry);
    this.showResult(result);
  }

  showLoading() {
    const resultEl = this.shadowRoot.querySelector('#result');
    resultEl.innerHTML = `
      <div class="loading">
        <div class="spinner"></div>
        <span>Validating...</span>
      </div>
    `;
    resultEl.classList.add('visible');
  }

  showResult(result) {
    const resultEl = this.shadowRoot.querySelector('#result');
    const icon = result.recommendation === 'safe' ? '✓' :
                 result.recommendation === 'suspicious' ? '⚠' : '✗';

    const signalsHtml = result.signals.map(s => `
      <div class="signal">
        <span class="signal-icon">⚠</span>
        <span class="signal-text">${s.message}</span>
      </div>
    `).join('');

    // [HOSTILE FIX] Show data source indicator
    const sourceLabel = {
      'live': { text: 'LIVE', class: 'source-live', icon: '🟢' },
      'demo': { text: 'DEMO', class: 'source-demo', icon: '🔵' },
      'analysis': { text: 'LOCAL', class: 'source-analysis', icon: '🟡' },
    }[result.source] || { text: 'UNKNOWN', class: 'source-unknown', icon: '⚪' };

    resultEl.innerHTML = `
      <div class="result-header">
        <div class="result-status">
          <div class="status-icon ${result.recommendation}">${icon}</div>
          <div class="status-text">
            <h3>${result.recommendation.toUpperCase().replace('_', ' ')}</h3>
            <span>${result.name}</span>
          </div>
        </div>
        <div class="result-meta">
          <span class="source-badge ${sourceLabel.class}" title="Data source: ${sourceLabel.text}">
            ${sourceLabel.icon} ${sourceLabel.text}
          </span>
          <span class="elapsed">${result.elapsed}ms</span>
        </div>
      </div>

      ${signalsHtml ? `<div class="signals">${signalsHtml}</div>` : ''}

      <div class="risk-meter">
        <div class="risk-label">
          <span>Risk Score</span>
          <span>${(result.risk * 100).toFixed(0)}%</span>
        </div>
        <div class="risk-bar">
          <div class="risk-fill ${result.recommendation}"
               style="width: ${result.risk * 100}%"></div>
        </div>
      </div>
    `;

    resultEl.classList.add('visible');
  }

  hideResult() {
    const resultEl = this.shadowRoot.querySelector('#result');
    resultEl.classList.remove('visible');
  }
}

customElements.define('pg-playground', PhantomPlayground);
```

### Task 3.3: Playground Section (1.5h)

**src/sections/playground.js:**
```javascript
export function createPlaygroundSection() {
  return `
    <div class="section-header">
      <h2 class="section-title">Try It Now</h2>
      <p class="section-subtitle">
        Enter a package name to see Phantom Guard in action.
        Try "reqeusts" or "flask-gpt-helper" for a demo.
      </p>
    </div>

    <pg-playground></pg-playground>

    <div class="example-packages">
      <span class="example-label">Try these:</span>
      <button class="example-btn" data-package="reqeusts">reqeusts</button>
      <button class="example-btn" data-package="flask-gpt-helper">flask-gpt-helper</button>
      <button class="example-btn" data-package="requests">requests</button>
      <button class="example-btn" data-package="numpyy">numpyy</button>
    </div>
  `;
}

export function initPlaygroundSection() {
  const examples = document.querySelectorAll('.example-btn');
  const playground = document.querySelector('pg-playground');

  examples.forEach(btn => {
    btn.addEventListener('click', () => {
      const input = playground.shadowRoot.querySelector('#package-input');
      input.value = btn.dataset.package;
      input.dispatchEvent(new Event('input'));
    });
  });
}
```

### Task 3.4: Playground Styles (1h)

**src/styles/playground.css:**
```css
#playground {
  padding: var(--space-24) var(--space-8);
  background: var(--color-base);
}

.section-header {
  text-align: center;
  margin-bottom: var(--space-12);
}

.section-title {
  font-size: var(--text-4xl);
  margin-bottom: var(--space-4);
}

.section-subtitle {
  color: var(--color-subtext);
  font-size: var(--text-lg);
  max-width: 50ch;
  margin: 0 auto;
}

.example-packages {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-3);
  margin-top: var(--space-8);
}

.example-label {
  color: var(--color-subtext);
  font-size: var(--text-sm);
}

.example-btn {
  padding: var(--space-2) var(--space-4);
  background: var(--color-surface);
  border: 1px solid var(--color-overlay);
  border-radius: var(--radius-md);
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  color: var(--color-text);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
}

.example-btn:hover {
  border-color: var(--color-mauve);
  background: var(--color-overlay);
}
```

### Task 3.5: Risk Meter Component (1h)

**src/components/risk-meter.js:**
```javascript
import gsap from 'gsap';

export class RiskMeter extends HTMLElement {
  static get observedAttributes() {
    return ['value', 'recommendation'];
  }

  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  connectedCallback() {
    this.render();
  }

  attributeChangedCallback(name, oldValue, newValue) {
    if (oldValue !== newValue) {
      this.updateMeter();
    }
  }

  render() {
    const value = parseFloat(this.getAttribute('value') || '0');
    const recommendation = this.getAttribute('recommendation') || 'safe';

    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: block;
        }

        .meter-container {
          display: flex;
          align-items: center;
          gap: 16px;
        }

        .meter-bar {
          flex: 1;
          height: 12px;
          background: var(--color-overlay);
          border-radius: 6px;
          overflow: hidden;
        }

        .meter-fill {
          height: 100%;
          border-radius: 6px;
          transition: width 0.5s cubic-bezier(0.16, 1, 0.3, 1);
        }

        .meter-fill.safe { background: var(--color-green); }
        .meter-fill.suspicious { background: var(--color-yellow); }
        .meter-fill.high_risk { background: var(--color-red); }

        .meter-value {
          font-family: var(--font-mono);
          font-size: 14px;
          font-weight: 600;
          min-width: 50px;
          text-align: right;
        }

        .meter-value.safe { color: var(--color-green); }
        .meter-value.suspicious { color: var(--color-yellow); }
        .meter-value.high_risk { color: var(--color-red); }
      </style>

      <div class="meter-container">
        <div class="meter-bar">
          <div class="meter-fill ${recommendation}" style="width: ${value * 100}%"></div>
        </div>
        <span class="meter-value ${recommendation}">${(value * 100).toFixed(0)}%</span>
      </div>
    `;
  }

  updateMeter() {
    const value = parseFloat(this.getAttribute('value') || '0');
    const recommendation = this.getAttribute('recommendation') || 'safe';

    const fill = this.shadowRoot.querySelector('.meter-fill');
    const valueEl = this.shadowRoot.querySelector('.meter-value');

    if (fill && valueEl) {
      fill.className = `meter-fill ${recommendation}`;
      fill.style.width = `${value * 100}%`;
      valueEl.className = `meter-value ${recommendation}`;
      valueEl.textContent = `${(value * 100).toFixed(0)}%`;
    }
  }
}

customElements.define('pg-risk-meter', RiskMeter);
```

---

## Deliverables

- [ ] `<pg-playground>` component working
- [ ] Real-time validation with debounce
- [ ] Registry switcher (PyPI/npm/crates)
- [ ] Risk meter animation
- [ ] Example buttons working
- [ ] Loading state displayed

---

## Exit Criteria

- [ ] Type "reqeusts" → shows HIGH_RISK
- [ ] Type "requests" → shows SAFE
- [ ] Registry switch re-validates
- [ ] Response time shown in ms
- [ ] No flickering during validation
