/**
 * Hero Section for Phantom Guard Showcase
 *
 * Premium centered layout based on Linear/Vercel design patterns.
 * Research: https://evilmartians.com/chronicles/we-studied-100-devtool-landing-pages-here-is-what-actually-works-in-2025
 */

import { animateTerminalDemo } from '../animations/terminal-demo.js';

/**
 * Creates the hero section HTML - Centered Layout
 * @returns {string} Hero section HTML
 */
export function createHeroSection() {
  return `
    <div class="hero-container">
      <!-- Floating Ghost Icon - Premium Animation -->
      <div class="hero-ghost-wrapper">
        <div class="hero-ghost-glow" aria-hidden="true"></div>
        <svg class="hero-ghost" aria-hidden="true"><use href="#ghost"/></svg>
      </div>

      <!-- Pain-Point Headline -->
      <h1 class="hero-title">
        Stop Phantom Packages<br>
        <span class="title-gradient">Before They Haunt Your Code</span>
      </h1>

      <!-- Value Proposition -->
      <p class="hero-subtitle">
        Validate npm, PyPI, and Cargo packages in <strong>&lt;200ms</strong>.<br>
        Detect AI-hallucinated package names before attackers exploit them.
      </p>

      <!-- CTAs - Specific Action Language -->
      <div class="hero-ctas">
        <a href="#playground" class="btn btn-primary">
          <span>Validate a Package</span>
          <svg class="icon" aria-hidden="true"><use href="#arrow-right"/></svg>
        </a>
        <button class="btn btn-secondary" id="copy-install-btn" type="button" aria-label="Copy install command">
          <svg class="icon" aria-hidden="true"><use href="#terminal"/></svg>
          <code>pip install phantom-guard</code>
          <svg class="icon icon-copy" aria-hidden="true"><use href="#copy"/></svg>
        </button>
      </div>

      <!-- Terminal Demo - Centered -->
      <div class="hero-terminal-wrapper">
        <pg-terminal id="hero-demo"></pg-terminal>
      </div>

      <!-- Stats with Icons -->
      <div class="hero-stats">
        <div class="stat">
          <div class="stat-icon">&#x26A1;</div>
          <span class="stat-value">&lt;200ms</span>
          <span class="stat-label">Validation Speed</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat">
          <div class="stat-icon">&#x1F3AF;</div>
          <span class="stat-value">99%</span>
          <span class="stat-label">Detection Rate</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat">
          <div class="stat-icon">&#x1F4E6;</div>
          <span class="stat-value">3</span>
          <span class="stat-label">Registries</span>
        </div>
      </div>

      <!-- Trust Signals - Works With -->
      <div class="hero-trust">
        <span class="trust-label">Works with</span>
        <div class="trust-logos">
          <div class="trust-logo" title="Python / PyPI">
            <svg class="icon" aria-hidden="true"><use href="#package"/></svg>
            <span>PyPI</span>
          </div>
          <div class="trust-logo" title="npm">
            <svg class="icon" aria-hidden="true"><use href="#package"/></svg>
            <span>npm</span>
          </div>
          <div class="trust-logo" title="Cargo / crates.io">
            <svg class="icon" aria-hidden="true"><use href="#package"/></svg>
            <span>Cargo</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Cursor Glow Effect -->
    <div class="cursor-glow" aria-hidden="true"></div>
  `;
}

/**
 * Initializes the hero section
 */
export function initHeroSection() {
  // Initialize terminal animation
  const terminal = document.querySelector('#hero-demo');
  if (terminal) {
    if (terminal.shadowRoot) {
      animateTerminalDemo(terminal);
    } else {
      requestAnimationFrame(() => {
        if (terminal.shadowRoot) {
          animateTerminalDemo(terminal);
        }
      });
    }
  }

  // Set up copy-to-clipboard
  const copyBtn = document.querySelector('#copy-install-btn');
  if (copyBtn) {
    copyBtn.addEventListener('click', handleCopyInstall);
  }

  // Initialize cursor glow effect
  initCursorGlow();

  // Initialize magnetic buttons
  initMagneticButtons();
}

/**
 * Handles copy-to-clipboard for the install command
 */
async function handleCopyInstall() {
  const command = 'pip install phantom-guard';
  const btn = document.querySelector('#copy-install-btn');

  try {
    await navigator.clipboard.writeText(command);

    const icon = btn.querySelector('.icon-copy use');
    if (icon) {
      icon.setAttribute('href', '#check');
    }

    btn.classList.add('copied');

    setTimeout(() => {
      if (icon) {
        icon.setAttribute('href', '#copy');
      }
      btn.classList.remove('copied');
    }, 2000);

  } catch (err) {
    console.error('[Hero] Failed to copy:', err);
    const code = btn.querySelector('code');
    if (code) {
      const range = document.createRange();
      range.selectNode(code);
      window.getSelection()?.removeAllRanges();
      window.getSelection()?.addRange(range);
    }
  }
}

/**
 * Cursor glow effect that follows mouse
 */
function initCursorGlow() {
  const glow = document.querySelector('.cursor-glow');
  const hero = document.querySelector('#hero');

  if (!glow || !hero) return;

  // Only on desktop
  if (window.matchMedia('(hover: hover)').matches) {
    hero.addEventListener('mousemove', (e) => {
      const rect = hero.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      glow.style.opacity = '1';
      glow.style.left = `${x}px`;
      glow.style.top = `${y}px`;
    });

    hero.addEventListener('mouseleave', () => {
      glow.style.opacity = '0';
    });
  }
}

/**
 * Magnetic button effect
 */
function initMagneticButtons() {
  const buttons = document.querySelectorAll('.btn-primary');

  if (window.matchMedia('(hover: hover)').matches) {
    buttons.forEach(btn => {
      btn.addEventListener('mousemove', (e) => {
        const rect = btn.getBoundingClientRect();
        const x = e.clientX - rect.left - rect.width / 2;
        const y = e.clientY - rect.top - rect.height / 2;

        btn.style.transform = `translate(${x * 0.15}px, ${y * 0.15}px)`;
      });

      btn.addEventListener('mouseleave', () => {
        btn.style.transform = 'translate(0, 0)';
      });
    });
  }
}
