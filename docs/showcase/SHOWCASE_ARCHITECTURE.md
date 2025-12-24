# Phantom Guard — Showcase Architecture

> **Version**: 1.0.0
> **Created**: 2025-12-24
> **Status**: APPROVED
> **Gate**: Extends Gate 1

---

## 1. Overview

### 1.1 Purpose

A high-end, interactive landing page that demonstrates Phantom Guard's speed and simplicity. The showcase serves as:

1. **Marketing asset** — First impression for potential users
2. **Live demo** — Interactive playground proving the tool works
3. **Documentation hub** — Integration examples and quick-start guides

### 1.2 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         SHOWCASE SITE                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    PRESENTATION LAYER                        │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │   │
│  │  │  Hero    │ │Playground│ │ Features │ │  Footer  │       │   │
│  │  │ Section  │ │  Section │ │  Section │ │  Section │       │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                       │
│                              ▼                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    COMPONENT LAYER                           │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │   │
│  │  │<pg-      │ │<pg-      │ │<pg-risk- │ │<pg-code- │       │   │
│  │  │terminal> │ │playground│ │meter>    │ │block>    │       │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                       │
│                              ▼                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    ANIMATION LAYER                           │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐                     │   │
│  │  │ GSAP     │ │ Scroll   │ │ Micro    │                     │   │
│  │  │ Timeline │ │ Triggers │ │ Effects  │                     │   │
│  │  └──────────┘ └──────────┘ └──────────┘                     │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                       │
│                              ▼                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    SERVICE LAYER                             │   │
│  │  ┌──────────┐ ┌──────────┐                                   │   │
│  │  │Validator │ │Analytics │                                   │   │
│  │  │ Mock/API │ │ (Privacy)│                                   │   │
│  │  └──────────┘ └──────────┘                                   │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Specification Registry

| SPEC_ID | Description | Component | Priority |
|:--------|:------------|:----------|:---------|
| SHOW001 | Project scaffold with Vite + ESM | Build system | P0 |
| SHOW002 | Design tokens (colors, spacing, typography) | Styles | P0 |
| SHOW003 | Hero section with animated terminal | Hero | P0 |
| SHOW004 | Live validation playground | Playground | P0 |
| SHOW005 | Feature cards with animations | Features | P1 |
| SHOW006 | Integration code examples | Examples | P1 |
| SHOW007 | Performance visualization | Metrics | P1 |
| SHOW008 | Mobile responsive design | Layout | P0 |

---

## 3. Component Specifications

### 3.1 `<pg-terminal>` — SHOW003

```
SPEC_ID: SHOW003
PURPOSE: Animated terminal demonstrating package validation
```

#### Interface

```javascript
class PgTerminal extends HTMLElement {
  // Properties
  command: string;      // The command to type
  speed: number;        // Typing speed (ms per char)
  autoplay: boolean;    // Start on load

  // Methods
  play(): Promise<void>;    // Start animation
  reset(): void;            // Reset to initial state

  // Events
  'animation-start': CustomEvent;
  'animation-complete': CustomEvent;
}
```

#### Animation Sequence

| Phase | Duration | Description |
|:------|:---------|:------------|
| 1. Fade in | 300ms | Terminal appears with glow |
| 2. Cursor blink | 500ms | Waiting cursor animation |
| 3. Type command | 800ms | Character-by-character typing |
| 4. Spinner | 500ms | Loading animation |
| 5. Results | 600ms | Staggered line reveal |
| 6. Verdict | 300ms | Color flash + slide in |
| 7. Progress bar | 200ms | Fill to show speed |

**Total**: ~3.2 seconds

#### Invariants

| INV_ID | Statement | Enforcement |
|:-------|:----------|:------------|
| SHOW_INV001 | Animation framerate ≥60fps | Performance monitor |
| SHOW_INV002 | Respects prefers-reduced-motion | CSS media query |
| SHOW_INV003 | Keyboard accessible | Focus management |

### 3.2 `<pg-playground>` — SHOW004

```
SPEC_ID: SHOW004
PURPOSE: Interactive package validation demo
```

#### Interface

```javascript
class PgPlayground extends HTMLElement {
  // Properties
  registry: 'pypi' | 'npm' | 'crates';
  debounceMs: number;  // Input debounce (default: 300)

  // State
  packageName: string;
  result: ValidationResult | null;
  loading: boolean;

  // Methods
  validate(name: string): Promise<ValidationResult>;

  // Events
  'validation-start': CustomEvent<{ name: string }>;
  'validation-complete': CustomEvent<{ result: ValidationResult }>;
}

interface ValidationResult {
  name: string;
  exists: boolean;
  riskScore: number;
  signals: Signal[];
  recommendation: 'SAFE' | 'SUSPICIOUS' | 'HIGH_RISK';
  latencyMs: number;
}
```

#### Mock API Strategy

For the showcase, we use a mock API that simulates real behavior:

```javascript
const MOCK_RESPONSES = {
  // Known safe packages
  'flask': { exists: true, riskScore: 0.05, signals: [], ... },
  'requests': { exists: true, riskScore: 0.03, signals: [], ... },

  // Known typosquats
  'reqeusts': { exists: false, riskScore: 0.89, signals: ['TYPOSQUAT'], ... },
  'flaask': { exists: false, riskScore: 0.92, signals: ['TYPOSQUAT'], ... },

  // Hallucination patterns
  'flask-ai-helper': { exists: false, riskScore: 0.78, signals: ['HALLUCINATION_PATTERN'], ... },
};

// For unknown packages, generate realistic mock
function generateMockResponse(name) {
  // Apply real detection logic client-side
}
```

#### Invariants

| INV_ID | Statement | Enforcement |
|:-------|:----------|:------------|
| SHOW_INV004 | Debounce prevents API spam | Debounce utility |
| SHOW_INV005 | Loading state always visible | State machine |
| SHOW_INV006 | Error states gracefully handled | Try/catch + UI |

### 3.3 `<pg-risk-meter>` — Internal Component

```
PURPOSE: Animated risk score visualization
```

#### Interface

```javascript
class PgRiskMeter extends HTMLElement {
  // Properties
  score: number;        // 0.0 to 1.0
  animated: boolean;    // Animate on change
  showLabel: boolean;   // Show numeric value

  // Computed
  get level(): 'safe' | 'suspicious' | 'high-risk';
  get color(): string;
}
```

#### Color Mapping

| Score Range | Level | Color |
|:------------|:------|:------|
| 0.00 - 0.30 | SAFE | `#10b981` (emerald-500) |
| 0.31 - 0.60 | SUSPICIOUS | `#f59e0b` (amber-500) |
| 0.61 - 1.00 | HIGH_RISK | `#ef4444` (red-500) |

---

## 4. Design System

### 4.1 Design Tokens — SHOW002

```css
:root {
  /* Colors - Dark Mode Default */
  --color-bg-primary: #0a0a0a;
  --color-bg-secondary: #141414;
  --color-bg-tertiary: #1f1f1f;

  --color-text-primary: #fafafa;
  --color-text-secondary: #a1a1aa;
  --color-text-muted: #71717a;

  --color-accent-primary: #6366f1;    /* Indigo */
  --color-accent-secondary: #8b5cf6;  /* Violet */

  --color-safe: #10b981;
  --color-suspicious: #f59e0b;
  --color-danger: #ef4444;

  /* Terminal Colors */
  --color-terminal-bg: #0d1117;
  --color-terminal-text: #c9d1d9;
  --color-terminal-prompt: #58a6ff;
  --color-terminal-success: #3fb950;
  --color-terminal-error: #f85149;

  /* Spacing */
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 0.75rem;
  --space-4: 1rem;
  --space-6: 1.5rem;
  --space-8: 2rem;
  --space-12: 3rem;
  --space-16: 4rem;
  --space-24: 6rem;

  /* Typography */
  --font-sans: 'Inter', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;

  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.25rem;
  --text-2xl: 1.5rem;
  --text-3xl: 1.875rem;
  --text-4xl: 2.25rem;
  --text-5xl: 3rem;

  /* Animation */
  --ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-in-out-expo: cubic-bezier(0.87, 0, 0.13, 1);
  --duration-fast: 150ms;
  --duration-normal: 300ms;
  --duration-slow: 500ms;

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.5);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.5);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.5);
  --shadow-glow: 0 0 40px rgba(99, 102, 241, 0.15);

  /* Border Radius */
  --radius-sm: 0.25rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
  --radius-xl: 1rem;
}
```

### 4.2 Typography Scale

| Element | Font | Size | Weight | Line Height |
|:--------|:-----|:-----|:-------|:------------|
| H1 (Hero) | Inter | 3rem (48px) | 700 | 1.1 |
| H2 (Section) | Inter | 2.25rem (36px) | 600 | 1.2 |
| H3 (Card) | Inter | 1.5rem (24px) | 600 | 1.3 |
| Body | Inter | 1rem (16px) | 400 | 1.5 |
| Code | JetBrains Mono | 0.875rem (14px) | 400 | 1.6 |
| Terminal | JetBrains Mono | 0.9375rem (15px) | 400 | 1.5 |

---

## 5. Animation Specifications

### 5.1 GSAP Configuration

```javascript
// Global defaults
gsap.defaults({
  ease: 'expo.out',
  duration: 0.8,
});

// Register plugins
gsap.registerPlugin(ScrollTrigger);

// Respect user preferences
if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
  gsap.globalTimeline.timeScale(0);
}
```

### 5.2 Scroll Trigger Defaults

```javascript
ScrollTrigger.defaults({
  start: 'top 80%',
  end: 'bottom 20%',
  toggleActions: 'play none none reverse',
});
```

### 5.3 Animation Patterns

| Pattern | Use Case | Duration | Easing |
|:--------|:---------|:---------|:-------|
| Fade Up | Card entry | 0.6s | expo.out |
| Stagger | List items | 0.1s delay | expo.out |
| Typewriter | Terminal text | 50ms/char | linear |
| Counter | Numbers | 1.5s | power2.out |
| Progress | Meters | 0.8s | expo.out |
| Glow Pulse | Accents | 2s | sine.inOut |

---

## 6. Performance Budget

| Metric | Budget | Measurement |
|:-------|:-------|:------------|
| First Contentful Paint | <1.0s | Lighthouse |
| Largest Contentful Paint | <1.5s | Lighthouse |
| Time to Interactive | <2.0s | Lighthouse |
| Total Blocking Time | <100ms | Lighthouse |
| Cumulative Layout Shift | <0.1 | Lighthouse |
| Bundle Size (gzipped) | <50KB | Build output |
| Animation framerate | ≥60fps | Performance monitor |

### 6.1 Optimization Strategies

1. **Code Splitting**: Load animations only when in viewport
2. **Font Subsetting**: Only load used characters
3. **Image Optimization**: WebP with fallbacks
4. **Preload Critical**: Fonts, above-fold CSS
5. **Lazy Load**: Below-fold sections
6. **Service Worker**: Offline support

---

## 7. Accessibility Requirements

### 7.1 WCAG 2.1 AA Compliance

| Requirement | Implementation |
|:------------|:---------------|
| Color Contrast | ≥4.5:1 for text, ≥3:1 for UI |
| Keyboard Navigation | All interactive elements focusable |
| Screen Reader | Semantic HTML + ARIA labels |
| Reduced Motion | Disable animations when preferred |
| Focus Indicators | Visible focus rings |

### 7.2 ARIA Patterns

```html
<!-- Terminal -->
<div role="region" aria-label="Package validation demo">
  <pre role="log" aria-live="polite" aria-atomic="false">
    <!-- Terminal output -->
  </pre>
</div>

<!-- Risk Meter -->
<div role="meter"
     aria-valuenow="0.89"
     aria-valuemin="0"
     aria-valuemax="1"
     aria-label="Risk score: 89%">
</div>
```

---

## 8. Browser Support

| Browser | Version | Notes |
|:--------|:--------|:------|
| Chrome | Last 2 | Full support |
| Firefox | Last 2 | Full support |
| Safari | Last 2 | Full support |
| Edge | Last 2 | Full support |
| Mobile Safari | iOS 14+ | Touch optimized |
| Chrome Android | Last 2 | Touch optimized |

### 8.1 Progressive Enhancement

```javascript
// Feature detection
const supportsWebComponents = 'customElements' in window;
const supportsGSAP = typeof gsap !== 'undefined';

// Fallback for no-JS
<noscript>
  <style>.js-only { display: none; }</style>
  <div class="static-demo">Static fallback content</div>
</noscript>
```

---

## 9. Security Considerations

| Concern | Mitigation |
|:--------|:-----------|
| XSS in input | Sanitize package names |
| CSP | Strict Content-Security-Policy |
| External scripts | Subresource Integrity (SRI) |
| Analytics | Privacy-first (no cookies) |

### 9.1 Content Security Policy

```html
<meta http-equiv="Content-Security-Policy"
      content="default-src 'self';
               script-src 'self' https://cdnjs.cloudflare.com;
               style-src 'self' 'unsafe-inline';
               font-src 'self' https://fonts.gstatic.com;">
```

---

## 10. File Structure

```
showcase/
├── index.html                      # Single page entry
├── vite.config.js                  # Build configuration
├── package.json                    # Dependencies
├── .gitignore
│
├── src/
│   ├── main.js                     # Application bootstrap
│   │
│   ├── styles/
│   │   ├── tokens.css              # Design tokens
│   │   ├── reset.css               # Modern CSS reset
│   │   ├── typography.css          # Font definitions
│   │   ├── layout.css              # Grid/container
│   │   ├── animations.css          # Keyframe definitions
│   │   └── utilities.css           # Utility classes
│   │
│   ├── components/
│   │   ├── base.js                 # Base component class
│   │   ├── terminal.js             # <pg-terminal>
│   │   ├── playground.js           # <pg-playground>
│   │   ├── risk-meter.js           # <pg-risk-meter>
│   │   ├── signal-card.js          # <pg-signal-card>
│   │   ├── code-block.js           # <pg-code-block>
│   │   └── perf-chart.js           # <pg-perf-chart>
│   │
│   ├── sections/
│   │   ├── hero.js                 # Hero section logic
│   │   ├── features.js             # Features section
│   │   ├── integrations.js         # Code examples
│   │   └── performance.js          # Metrics section
│   │
│   ├── animations/
│   │   ├── gsap-config.js          # GSAP setup
│   │   ├── timelines.js            # Complex sequences
│   │   ├── scroll-triggers.js      # Scroll animations
│   │   └── micro.js                # Hover/click effects
│   │
│   ├── services/
│   │   ├── validator.js            # Mock/real API client
│   │   └── analytics.js            # Privacy-first tracking
│   │
│   └── utils/
│       ├── debounce.js
│       ├── typewriter.js
│       ├── accessibility.js
│       └── sanitize.js
│
├── public/
│   ├── fonts/
│   │   ├── inter-var.woff2
│   │   └── jetbrains-mono.woff2
│   ├── og-image.png
│   ├── favicon.ico
│   └── manifest.json               # PWA manifest
│
└── tests/
    ├── e2e/
    │   ├── hero.spec.js
    │   ├── playground.spec.js
    │   └── accessibility.spec.js
    └── unit/
        ├── validator.test.js
        └── components.test.js
```

---

## 11. Testing Strategy

| Type | Tool | Coverage Target |
|:-----|:-----|:----------------|
| Unit | Vitest | Components, utilities |
| E2E | Playwright | Critical user flows |
| Visual | Percy | Screenshot regression |
| Accessibility | axe-core | WCAG compliance |
| Performance | Lighthouse CI | Score ≥95 |

### 11.1 Critical Test Cases

| Test ID | Description | Type |
|:--------|:------------|:-----|
| TW5.01 | Vite builds without errors | Unit |
| TW5.05 | Terminal animation completes | E2E |
| TW5.11 | Playground validates input | E2E |
| TW5.15 | Risk meter updates on result | Unit |
| TW5.20 | Scroll animations trigger | E2E |
| TW5.30 | Mobile touch interactions work | E2E |
| TW5.35 | Screen reader announces results | A11y |

---

## 12. Deployment

### 12.1 Build Process

```bash
# Development
npm run dev          # Vite dev server

# Production
npm run build        # Vite production build
npm run preview      # Preview production build

# Deploy
npm run deploy       # Deploy to GitHub Pages/Vercel
```

### 12.2 CI/CD Pipeline

```yaml
# .github/workflows/showcase.yml
name: Deploy Showcase

on:
  push:
    branches: [main]
    paths: ['showcase/**']

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: cd showcase && npm ci
      - run: cd showcase && npm run build
      - run: cd showcase && npm run test
      - run: npx lighthouse-ci --upload.target=temporary-public-storage
      - uses: peaceiris/actions-gh-pages@v3
        with:
          publish_dir: ./showcase/dist
```

---

## Appendix A: Mock Data Examples

```javascript
export const MOCK_PACKAGES = {
  // Safe packages
  flask: {
    exists: true,
    riskScore: 0.05,
    signals: [],
    recommendation: 'SAFE',
    metadata: {
      downloads: 15_000_000,
      age: 4380, // days
      hasRepo: true,
      maintainerCount: 12,
    },
  },

  // Typosquats
  reqeusts: {
    exists: false,
    riskScore: 0.89,
    signals: [
      { type: 'TYPOSQUAT', target: 'requests', distance: 1 },
      { type: 'NOT_FOUND', registry: 'pypi' },
    ],
    recommendation: 'HIGH_RISK',
  },

  // Hallucination patterns
  'flask-gpt-helper': {
    exists: false,
    riskScore: 0.78,
    signals: [
      { type: 'HALLUCINATION_PATTERN', pattern: '*-gpt-*' },
      { type: 'NOT_FOUND', registry: 'pypi' },
    ],
    recommendation: 'HIGH_RISK',
  },
};
```

---

**Architecture Status**: APPROVED

**Next Step**: Create Week 1 Day-by-Day implementation guide
