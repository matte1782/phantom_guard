# Week 5 Day 2: Hero Section & Terminal Component

> **Date**: 2026-01-02
> **Focus**: Hero Section, Terminal Animation, Logo
> **Estimated Hours**: 8

---

## Objectives

1. Create the terminal Web Component
2. Build typing animation with GSAP
3. Design hero section layout
4. Implement animated demo sequence

---

## Tasks

### Task 2.1: Terminal Web Component (2h)

**src/components/terminal.js:**
```javascript
export class PhantomTerminal extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  connectedCallback() {
    this.render();
    this.initAnimation();
  }

  render() {
    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: block;
          background: var(--color-surface, #313244);
          border-radius: var(--radius-lg, 12px);
          overflow: hidden;
          box-shadow: var(--shadow-lg);
        }

        .terminal-header {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 12px 16px;
          background: var(--color-overlay, #45475a);
        }

        .terminal-dot {
          width: 12px;
          height: 12px;
          border-radius: 50%;
        }

        .terminal-dot.red { background: #f38ba8; }
        .terminal-dot.yellow { background: #f9e2af; }
        .terminal-dot.green { background: #a6e3a1; }

        .terminal-title {
          flex: 1;
          text-align: center;
          font-family: var(--font-mono);
          font-size: 12px;
          color: var(--color-subtext, #a6adc8);
        }

        .terminal-body {
          padding: 20px;
          font-family: var(--font-mono);
          font-size: 14px;
          line-height: 1.8;
          min-height: 200px;
        }

        .line {
          opacity: 0;
          transform: translateY(10px);
        }

        .line.visible {
          opacity: 1;
          transform: translateY(0);
          transition: all 0.3s ease-out;
        }

        .prompt { color: var(--color-mauve, #cba6f7); }
        .command { color: var(--color-text, #cdd6f4); }
        .success { color: var(--color-green, #a6e3a1); }
        .warning { color: var(--color-yellow, #f9e2af); }
        .error { color: var(--color-red, #f38ba8); }
        .info { color: var(--color-blue, #89b4fa); }

        .cursor {
          display: inline-block;
          width: 8px;
          height: 16px;
          background: var(--color-mauve);
          animation: blink 1s step-end infinite;
        }

        @keyframes blink {
          0%, 50% { opacity: 1; }
          51%, 100% { opacity: 0; }
        }

        .spinner {
          display: inline-block;
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          to { transform: rotate(360deg); }
        }

        .result-line {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .risk-badge {
          padding: 2px 8px;
          border-radius: 4px;
          font-size: 12px;
          font-weight: 600;
        }

        .risk-badge.high-risk {
          background: rgba(243, 139, 168, 0.2);
          color: var(--color-red);
        }

        .progress-bar {
          height: 4px;
          background: var(--color-overlay);
          border-radius: 2px;
          margin-top: 16px;
          overflow: hidden;
        }

        .progress-fill {
          height: 100%;
          background: var(--color-mauve);
          width: 0;
          transition: width 0.3s ease-out;
        }
      </style>

      <div class="terminal-header">
        <div class="terminal-dot red"></div>
        <div class="terminal-dot yellow"></div>
        <div class="terminal-dot green"></div>
        <span class="terminal-title">phantom-guard</span>
      </div>

      <div class="terminal-body">
        <div class="line" id="line-1">
          <span class="prompt">$</span>
          <span class="command" id="command"></span>
          <span class="cursor" id="cursor"></span>
        </div>
        <div class="line" id="line-2"></div>
        <div class="line" id="line-3"></div>
        <div class="line" id="line-4"></div>
        <div class="line" id="line-5"></div>
        <div class="line result-line" id="line-6"></div>
        <div class="progress-bar" id="progress">
          <div class="progress-fill" id="progress-fill"></div>
        </div>
      </div>
    `;
  }

  async initAnimation() {
    // Animation handled by GSAP in main.js
  }
}

customElements.define('pg-terminal', PhantomTerminal);
```

### Task 2.2: GSAP Terminal Animation (2h) [HOSTILE FIX: Shadow DOM]

**src/animations/terminal-demo.js:**
```javascript
import gsap from 'gsap';

/**
 * [HOSTILE FIX] All GSAP animations must target Shadow DOM elements directly.
 * Standard CSS selectors like '#line-1' won't work inside Shadow DOM.
 * Solution: Cache all element references from shadowRoot before animating.
 */
export function animateTerminalDemo(terminal) {
  const shadow = terminal.shadowRoot;
  const command = 'phantom-guard validate flask-gpt-helper';

  // [HOSTILE FIX] Cache all Shadow DOM element references
  const elements = {
    line1: shadow.querySelector('#line-1'),
    line2: shadow.querySelector('#line-2'),
    line3: shadow.querySelector('#line-3'),
    line4: shadow.querySelector('#line-4'),
    line5: shadow.querySelector('#line-5'),
    line6: shadow.querySelector('#line-6'),
    command: shadow.querySelector('#command'),
    cursor: shadow.querySelector('#cursor'),
    progressFill: shadow.querySelector('#progress-fill'),
    progress: shadow.querySelector('#progress'),
  };

  const lines = [
    { el: elements.line2, text: '<span class="spinner">⠋</span> Checking PyPI...', delay: 0.8 },
    { el: elements.line3, text: '<span class="error">✗</span> Package not found on PyPI', delay: 1.3 },
    { el: elements.line4, text: '<span class="warning">⚠</span> Matches hallucination pattern', delay: 1.6 },
    { el: elements.line5, text: '<span class="warning">⚠</span> AI-related suffix detected', delay: 1.9 },
  ];

  const tl = gsap.timeline({ repeat: -1, repeatDelay: 3 });

  // [HOSTILE FIX] Use element reference, not CSS selector
  tl.to(elements.line1, { opacity: 1, y: 0, duration: 0.3 });

  // Type command character by character
  let charIndex = 0;

  tl.to({}, {
    duration: command.length * 0.05,
    onUpdate: function() {
      const progress = this.progress();
      const chars = Math.floor(progress * command.length);
      if (chars > charIndex) {
        charIndex = chars;
        elements.command.textContent = command.slice(0, charIndex);
      }
    }
  });

  // Hide cursor, show lines
  tl.to(elements.cursor, { opacity: 0, duration: 0.1 });

  // [HOSTILE FIX] Use element references for all lines
  lines.forEach(({ el, text, delay }) => {
    tl.to(el, {
      opacity: 1,
      y: 0,
      duration: 0.3,
      onStart: () => {
        el.innerHTML = text;
      }
    }, delay);
  });

  // Show result - [HOSTILE FIX] use element reference
  tl.to(elements.line6, {
    opacity: 1,
    y: 0,
    duration: 0.3,
    onStart: () => {
      elements.line6.innerHTML = `
        <span class="error">flask-gpt-helper</span>
        <span class="risk-badge high-risk">HIGH_RISK</span>
        <span class="info">[0.82]</span>
      `;
    }
  }, 2.2);

  // [HOSTILE FIX] Use element reference for progress bar
  tl.to(elements.progressFill, { width: '100%', duration: 0.3 }, 2.5);

  // Add timing label
  let timingLabel = null;
  tl.to({}, {
    duration: 0.1,
    onComplete: () => {
      timingLabel = document.createElement('div');
      timingLabel.style.cssText = 'font-size: 12px; color: var(--color-subtext); margin-top: 8px;';
      timingLabel.textContent = '━━━━━━━━━━━━━━━━━━━━━━ 147ms';
      elements.progress.after(timingLabel);
    }
  }, 2.8);

  // Reset for loop
  tl.to({}, {
    duration: 0.5,
    onComplete: () => {
      charIndex = 0;
      elements.command.textContent = '';
      elements.cursor.style.opacity = '1';

      // Reset all lines
      [elements.line1, elements.line2, elements.line3, elements.line4, elements.line5, elements.line6].forEach((el, i) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(10px)';
        if (i > 0) el.innerHTML = '';
      });

      elements.progressFill.style.width = '0';

      // Remove timing label
      if (timingLabel) {
        timingLabel.remove();
        timingLabel = null;
      }
    }
  }, 6);

  return tl;
}
```

### Task 2.3: Hero Section Layout (2h)

**src/sections/hero.js:**
```javascript
import { animateTerminalDemo } from '../animations/terminal-demo.js';

export function createHeroSection() {
  return `
    <div class="hero-container">
      <div class="hero-content">
        <div class="hero-badge">
          <span class="ghost">👻</span>
          <span>Supply Chain Security</span>
        </div>

        <h1 class="hero-title">
          Detect AI-Hallucinated<br>
          Package Attacks
        </h1>

        <p class="hero-subtitle">
          Phantom Guard protects your supply chain from slopsquatting—
          when AI hallucinates fake package names that attackers register.
          Validate packages in <strong>&lt;200ms</strong>.
        </p>

        <div class="hero-ctas">
          <a href="#playground" class="btn btn-primary">
            Try it Live
            <svg class="icon"><use href="#arrow-right"/></svg>
          </a>
          <button class="btn btn-secondary" onclick="copyInstall()">
            <code>pip install phantom-guard</code>
            <svg class="icon"><use href="#copy"/></svg>
          </button>
        </div>

        <div class="hero-stats">
          <div class="stat">
            <span class="stat-value">&lt;200ms</span>
            <span class="stat-label">Validation</span>
          </div>
          <div class="stat">
            <span class="stat-value">99%</span>
            <span class="stat-label">Coverage</span>
          </div>
          <div class="stat">
            <span class="stat-value">3</span>
            <span class="stat-label">Registries</span>
          </div>
        </div>
      </div>

      <div class="hero-terminal">
        <pg-terminal id="hero-demo"></pg-terminal>
      </div>
    </div>
  `;
}

export function initHeroSection() {
  const terminal = document.querySelector('#hero-demo');
  if (terminal) {
    animateTerminalDemo(terminal);
  }
}
```

### Task 2.4: Hero Styles (1.5h)

**src/styles/hero.css:**
```css
.hero {
  min-height: 100vh;
  display: flex;
  align-items: center;
  padding: var(--space-16) var(--space-8);
  background: radial-gradient(
    ellipse at top,
    rgba(203, 166, 247, 0.1) 0%,
    transparent 50%
  );
}

.hero-container {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-16);
  align-items: center;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  background: var(--color-surface);
  border-radius: var(--radius-xl);
  font-size: var(--text-sm);
  color: var(--color-subtext);
  margin-bottom: var(--space-6);
}

.hero-badge .ghost {
  font-size: var(--text-lg);
}

.hero-title {
  font-size: clamp(2.5rem, 6vw, 4rem);
  font-weight: 700;
  line-height: 1.1;
  margin-bottom: var(--space-6);
  background: linear-gradient(
    135deg,
    var(--color-text) 0%,
    var(--color-mauve) 100%
  );
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-subtitle {
  font-size: var(--text-lg);
  color: var(--color-subtext);
  line-height: 1.7;
  margin-bottom: var(--space-8);
  max-width: 50ch;
}

.hero-subtitle strong {
  color: var(--color-mauve);
  font-weight: 600;
}

.hero-ctas {
  display: flex;
  gap: var(--space-4);
  margin-bottom: var(--space-12);
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-6);
  border-radius: var(--radius-md);
  font-weight: 500;
  transition: all var(--duration-fast) var(--ease-out);
}

.btn-primary {
  background: var(--color-mauve);
  color: var(--color-base);
}

.btn-primary:hover {
  background: var(--color-text);
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.btn-secondary {
  background: var(--color-surface);
  color: var(--color-text);
  border: 1px solid var(--color-overlay);
}

.btn-secondary:hover {
  border-color: var(--color-mauve);
}

.btn-secondary code {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
}

.hero-stats {
  display: flex;
  gap: var(--space-8);
}

.stat {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: var(--text-2xl);
  font-weight: 700;
  font-family: var(--font-mono);
  color: var(--color-mauve);
}

.stat-label {
  font-size: var(--text-sm);
  color: var(--color-subtext);
}

.hero-terminal {
  position: relative;
}

.hero-terminal::before {
  content: '';
  position: absolute;
  inset: -20px;
  background: radial-gradient(
    circle at center,
    rgba(203, 166, 247, 0.15) 0%,
    transparent 70%
  );
  z-index: -1;
}

/* Responsive */
@media (max-width: 900px) {
  .hero-container {
    grid-template-columns: 1fr;
    text-align: center;
  }

  .hero-subtitle {
    margin-left: auto;
    margin-right: auto;
  }

  .hero-ctas {
    justify-content: center;
    flex-wrap: wrap;
  }

  .hero-stats {
    justify-content: center;
  }
}
```

### Task 2.5: Logo & Favicon (0.5h)

**public/favicon.svg:**
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <defs>
    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#cba6f7"/>
      <stop offset="100%" style="stop-color:#89b4fa"/>
    </linearGradient>
  </defs>
  <text x="50%" y="50%" text-anchor="middle" dy=".35em"
        font-size="24" fill="url(#grad)">👻</text>
</svg>
```

---

## Deliverables

- [ ] `<pg-terminal>` Web Component working
- [ ] GSAP typing animation playing
- [ ] Hero section fully styled
- [ ] Responsive layout (mobile + desktop)
- [ ] Copy-to-clipboard for install command
- [ ] Favicon visible in browser tab

---

## Exit Criteria

- [ ] Terminal animation loops smoothly
- [ ] No layout shift during animation
- [ ] Hero looks great at 320px and 1920px
- [ ] All text readable with good contrast
