# Week 5 Day 1: Project Setup & Design System

> **Date**: 2026-01-01
> **Focus**: Scaffold, Design Tokens, Base Styles
> **Estimated Hours**: 7

---

## Objectives

1. Set up Vite project with proper structure
2. Define design tokens (colors, typography, spacing)
3. Create base CSS (reset, utilities, animations)
4. Establish component architecture
5. **[HOSTILE FIX]** Create icon system with SVG sprite
6. **[HOSTILE FIX]** Create main.js assembly file

---

## Tasks

### Task 1.1: Vite Project Scaffold (1h)

**Windows-Compatible Commands:**
```powershell
# Create showcase directory
mkdir showcase
cd showcase

# Initialize with Vite
npm create vite@latest . -- --template vanilla

# Install production dependencies
npm install gsap prismjs

# Install dev dependencies (Playwright for e2e tests)
npm install -D @playwright/test

# Create directory structure (Windows PowerShell)
mkdir src\components, src\styles, src\animations, src\services, src\assets, src\sections
mkdir src\assets\fonts, src\assets\images
mkdir public
```

**Cross-Platform Alternative (package.json script):**
```json
{
  "scripts": {
    "setup": "node -e \"const fs=require('fs'); ['src/components','src/styles','src/animations','src/services','src/sections','src/assets/fonts','src/assets/images','public'].forEach(d=>fs.mkdirSync(d,{recursive:true}))\""
  }
}
```

**Directory Structure:**
```
showcase/
├── index.html
├── vite.config.js
├── package.json
├── src/
│   ├── main.js              # [HOSTILE FIX] Assembly file
│   ├── styles/
│   │   ├── tokens.css
│   │   ├── reset.css
│   │   ├── typography.css
│   │   ├── utilities.css
│   │   └── animations.css
│   ├── components/
│   │   └── icons.js          # [HOSTILE FIX] Icon system
│   ├── sections/             # Section modules
│   ├── animations/
│   ├── services/
│   └── assets/
│       ├── fonts/
│       └── images/
└── public/
    ├── favicon.svg
    └── icons.svg             # [HOSTILE FIX] SVG sprite
```

### Task 1.2: Design Tokens (1.5h)

**tokens.css:**
```css
:root {
  /* Phantom Mocha Color Palette */
  --color-base: #1e1e2e;
  --color-surface: #313244;
  --color-overlay: #45475a;
  --color-text: #cdd6f4;
  --color-subtext: #a6adc8;
  --color-mauve: #cba6f7;
  --color-green: #a6e3a1;
  --color-yellow: #f9e2af;
  --color-red: #f38ba8;
  --color-blue: #89b4fa;

  /* Status Colors */
  --color-safe: var(--color-green);
  --color-suspicious: var(--color-yellow);
  --color-high-risk: var(--color-red);
  --color-not-found: var(--color-blue);

  /* Typography */
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
  --font-sans: 'Inter', -apple-system, sans-serif;

  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.25rem;
  --text-2xl: 1.5rem;
  --text-3xl: 2rem;
  --text-4xl: 2.5rem;
  --text-5xl: 3.5rem;

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

  /* Borders */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.2);
  --shadow-md: 0 4px 6px rgba(0,0,0,0.3);
  --shadow-lg: 0 10px 15px rgba(0,0,0,0.4);
  --shadow-glow: 0 0 20px rgba(203,166,247,0.3);

  /* Transitions */
  --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-in-out: cubic-bezier(0.65, 0, 0.35, 1);
  --duration-fast: 150ms;
  --duration-normal: 300ms;
  --duration-slow: 500ms;
}
```

### Task 1.3: CSS Reset & Base (1h)

**reset.css:**
```css
*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html {
  font-size: 16px;
  scroll-behavior: smooth;
  -webkit-font-smoothing: antialiased;
}

body {
  font-family: var(--font-sans);
  background: var(--color-base);
  color: var(--color-text);
  line-height: 1.6;
  min-height: 100vh;
}

a {
  color: var(--color-mauve);
  text-decoration: none;
  transition: color var(--duration-fast) var(--ease-out);
}

a:hover {
  color: var(--color-text);
}

button {
  font-family: inherit;
  cursor: pointer;
  border: none;
  background: none;
}

code, pre {
  font-family: var(--font-mono);
}

img, svg {
  display: block;
  max-width: 100%;
}
```

### Task 1.4: Typography System (1h)

**typography.css:**
```css
/* Headings */
h1, h2, h3, h4, h5, h6 {
  font-weight: 600;
  line-height: 1.2;
  color: var(--color-text);
}

h1 { font-size: var(--text-5xl); }
h2 { font-size: var(--text-4xl); }
h3 { font-size: var(--text-3xl); }
h4 { font-size: var(--text-2xl); }

/* Hero Typography */
.hero-title {
  font-size: clamp(2.5rem, 8vw, 4.5rem);
  font-weight: 700;
  letter-spacing: -0.02em;
  background: linear-gradient(135deg, var(--color-text), var(--color-mauve));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-subtitle {
  font-size: clamp(1rem, 2.5vw, 1.25rem);
  color: var(--color-subtext);
  max-width: 50ch;
}

/* Monospace Text */
.mono {
  font-family: var(--font-mono);
}

/* Terminal Text */
.terminal-text {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  color: var(--color-green);
}
```

### Task 1.5: Animation Keyframes (1h)

**animations.css:**
```css
/* Fade In */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Slide Up */
@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Glow Pulse */
@keyframes glowPulse {
  0%, 100% { box-shadow: var(--shadow-glow); }
  50% { box-shadow: 0 0 30px rgba(203,166,247,0.5); }
}

/* Typing Cursor */
@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

/* Spinner */
@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Progress Bar Fill */
@keyframes fillProgress {
  from { width: 0; }
  to { width: var(--progress, 100%); }
}

/* Utility Classes */
.animate-fadeIn {
  animation: fadeIn var(--duration-normal) var(--ease-out);
}

.animate-slideUp {
  animation: slideUp var(--duration-slow) var(--ease-out);
}

.animate-glow {
  animation: glowPulse 2s ease-in-out infinite;
}
```

### Task 1.6: Base HTML Structure (0.5h)

**index.html:**
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Phantom Guard - Detect AI-Hallucinated Package Attacks</title>
  <meta name="description" content="Protect your supply chain from slopsquatting attacks. Validate packages in &lt;200ms.">

  <!-- Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">

  <!-- Favicon -->
  <link rel="icon" type="image/svg+xml" href="/favicon.svg">

  <!-- Open Graph -->
  <meta property="og:title" content="Phantom Guard">
  <meta property="og:description" content="Detect AI-Hallucinated Package Attacks">
  <meta property="og:type" content="website">
</head>
<body>
  <div id="app">
    <!-- Hero Section -->
    <section id="hero" class="section hero">
      <!-- Populated by JS -->
    </section>

    <!-- Playground Section -->
    <section id="playground" class="section">
      <!-- Populated by JS -->
    </section>

    <!-- How It Works -->
    <section id="how-it-works" class="section">
      <!-- Populated by JS -->
    </section>

    <!-- Performance -->
    <section id="performance" class="section">
      <!-- Populated by JS -->
    </section>

    <!-- Integration -->
    <section id="integration" class="section">
      <!-- Populated by JS -->
    </section>

    <!-- Footer -->
    <footer id="footer">
      <!-- Populated by JS -->
    </footer>
  </div>

  <script type="module" src="/src/main.js"></script>
</body>
</html>
```

### Task 1.7: Icon System [HOSTILE FIX] (0.5h)

**public/icons.svg** - SVG Sprite Sheet:
```svg
<svg xmlns="http://www.w3.org/2000/svg" style="display: none;">
  <!-- Arrow Right -->
  <symbol id="arrow-right" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
    <path d="M5 12h14M12 5l7 7-7 7"/>
  </symbol>

  <!-- Copy -->
  <symbol id="copy" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
  </symbol>

  <!-- Check -->
  <symbol id="check" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
    <polyline points="20 6 9 17 4 12"/>
  </symbol>

  <!-- GitHub -->
  <symbol id="github" viewBox="0 0 24 24" fill="currentColor">
    <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
  </symbol>

  <!-- Package -->
  <symbol id="package" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
    <path d="M16.5 9.4l-9-5.19M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
    <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
    <line x1="12" y1="22.08" x2="12" y2="12"/>
  </symbol>

  <!-- Book -->
  <symbol id="book" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
    <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
    <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
  </symbol>

  <!-- Search -->
  <symbol id="search" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
    <circle cx="11" cy="11" r="8"/>
    <path d="m21 21-4.35-4.35"/>
  </symbol>

  <!-- Shield -->
  <symbol id="shield" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
  </symbol>

  <!-- Globe -->
  <symbol id="globe" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
    <circle cx="12" cy="12" r="10"/>
    <line x1="2" y1="12" x2="22" y2="12"/>
    <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
  </symbol>

  <!-- Play -->
  <symbol id="play" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
    <polygon points="5 3 19 12 5 21 5 3"/>
  </symbol>
</svg>
```

**src/components/icons.js** - Icon Helper:
```javascript
// Load SVG sprite into document
export async function loadIcons() {
  const response = await fetch('/icons.svg');
  const svgText = await response.text();
  const container = document.createElement('div');
  container.innerHTML = svgText;
  container.style.display = 'none';
  document.body.insertBefore(container, document.body.firstChild);
}

// Create icon element
export function icon(name, className = '') {
  return `<svg class="icon ${className}"><use href="#${name}"/></svg>`;
}
```

---

### Task 1.8: Main.js Assembly [HOSTILE FIX] (0.5h)

**src/main.js** - Application Entry Point:
```javascript
// Styles
import './styles/tokens.css';
import './styles/reset.css';
import './styles/typography.css';
import './styles/animations.css';

// Icon system
import { loadIcons } from './components/icons.js';

// Initialize application
async function init() {
  // Load SVG icons first
  await loadIcons();

  console.log('Phantom Guard Showcase initialized');

  // Sections will be imported and initialized in Day 2+
  // import { createHeroSection, initHeroSection } from './sections/hero.js';
  // document.querySelector('#hero').innerHTML = createHeroSection();
  // initHeroSection();
}

// Start when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
```

**vite.config.js** - Vite Configuration:
```javascript
import { defineConfig } from 'vite';

export default defineConfig({
  base: '/phantom-guard/',  // For GitHub Pages
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
      },
    },
  },
  server: {
    port: 5173,
    open: true,
  },
});
```

---

## Deliverables

- [ ] Vite project initialized and running
- [ ] Design tokens defined in CSS variables
- [ ] Reset and base styles applied
- [ ] Typography system established
- [ ] Animation keyframes ready
- [ ] HTML skeleton in place
- [ ] Fonts loading correctly
- [ ] Dev server running at localhost:5173
- [ ] **[HOSTILE FIX]** SVG sprite with all icons
- [ ] **[HOSTILE FIX]** main.js assembly file working

---

## Exit Criteria

```powershell
# Verify setup (Windows)
npm run dev   # Should start without errors
npm run build # Should build successfully
```

- [ ] `npm run dev` starts successfully
- [ ] Page loads with dark background
- [ ] Fonts render correctly
- [ ] No console errors
- [ ] **[HOSTILE FIX]** Icons load correctly (check Network tab)
