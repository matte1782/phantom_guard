/**
 * RiskMeter Web Component
 *
 * Animated risk score visualization with GSAP.
 * Features smooth transitions, color morphing, and pulsing effects.
 */

import { gsap } from 'gsap';

const RISK_COLORS = {
  SAFE: { primary: '#a6e3a1', secondary: '#40a02b', glow: 'rgba(166, 227, 161, 0.4)' },
  UNKNOWN: { primary: '#f9e2af', secondary: '#df8e1d', glow: 'rgba(249, 226, 175, 0.4)' },
  SUSPICIOUS: { primary: '#fab387', secondary: '#fe640b', glow: 'rgba(250, 179, 135, 0.4)' },
  HIGH_RISK: { primary: '#f38ba8', secondary: '#d20f39', glow: 'rgba(243, 139, 168, 0.5)' }
};

const RISK_ICONS = {
  SAFE: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
    <polyline points="22 4 12 14.01 9 11.01"/>
  </svg>`,
  UNKNOWN: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
    <circle cx="12" cy="12" r="10"/>
    <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/>
    <line x1="12" y1="17" x2="12.01" y2="17"/>
  </svg>`,
  SUSPICIOUS: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
    <line x1="12" y1="9" x2="12" y2="13"/>
    <line x1="12" y1="17" x2="12.01" y2="17"/>
  </svg>`,
  HIGH_RISK: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
    <circle cx="12" cy="12" r="10"/>
    <line x1="15" y1="9" x2="9" y2="15"/>
    <line x1="9" y1="9" x2="15" y2="15"/>
  </svg>`
};

const RISK_LABELS = {
  SAFE: 'Safe to Install',
  UNKNOWN: 'Unknown Package',
  SUSPICIOUS: 'Suspicious',
  HIGH_RISK: 'High Risk'
};

class RiskMeter extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._score = 0;
    this._level = 'SAFE';
    this._timeline = null;
  }

  static get observedAttributes() {
    return ['score', 'level'];
  }

  connectedCallback() {
    this.render();
  }

  attributeChangedCallback(name, oldValue, newValue) {
    if (oldValue === newValue) return;

    if (name === 'score') {
      this._score = parseFloat(newValue) || 0;
    } else if (name === 'level') {
      this._level = newValue || 'SAFE';
    }

    if (this.shadowRoot.querySelector('.risk-meter')) {
      this.animateUpdate();
    }
  }

  get score() {
    return this._score;
  }

  set score(value) {
    this._score = value;
    this.setAttribute('score', value);
  }

  get level() {
    return this._level;
  }

  set level(value) {
    this._level = value;
    this.setAttribute('level', value);
  }

  render() {
    const colors = RISK_COLORS[this._level] || RISK_COLORS.SAFE;

    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: block;
          font-family: var(--font-sans, 'Inter', system-ui, sans-serif);
        }

        .risk-meter {
          background: rgba(30, 30, 46, 0.8);
          backdrop-filter: blur(20px);
          -webkit-backdrop-filter: blur(20px);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 16px;
          padding: 24px;
          position: relative;
          overflow: hidden;
        }

        .risk-meter::before {
          content: '';
          position: absolute;
          inset: 0;
          background: radial-gradient(
            ellipse at top center,
            var(--glow-color, rgba(203, 166, 247, 0.1)) 0%,
            transparent 60%
          );
          opacity: 0;
          transition: opacity 0.3s;
        }

        .risk-meter.active::before {
          opacity: 1;
        }

        .header {
          display: flex;
          align-items: center;
          gap: 16px;
          margin-bottom: 20px;
        }

        .icon-wrapper {
          width: 56px;
          height: 56px;
          border-radius: 14px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: var(--icon-bg, rgba(166, 227, 161, 0.15));
          color: var(--icon-color, #a6e3a1);
          position: relative;
          overflow: hidden;
        }

        .icon-wrapper::after {
          content: '';
          position: absolute;
          inset: 0;
          background: inherit;
          filter: blur(20px);
          opacity: 0.5;
        }

        .icon-wrapper svg {
          width: 28px;
          height: 28px;
          position: relative;
          z-index: 1;
        }

        .title-section {
          flex: 1;
        }

        .risk-label {
          font-size: 20px;
          font-weight: 600;
          color: var(--label-color, #a6e3a1);
          margin: 0 0 4px 0;
          letter-spacing: -0.02em;
        }

        .risk-description {
          font-size: 13px;
          color: rgba(205, 214, 244, 0.6);
          margin: 0;
        }

        .score-section {
          margin-top: 20px;
        }

        .score-header {
          display: flex;
          justify-content: space-between;
          align-items: baseline;
          margin-bottom: 10px;
        }

        .score-label {
          font-size: 12px;
          color: rgba(205, 214, 244, 0.5);
          text-transform: uppercase;
          letter-spacing: 0.08em;
        }

        .score-value {
          font-size: 24px;
          font-weight: 700;
          font-family: var(--font-mono, 'JetBrains Mono', monospace);
          color: var(--score-color, #a6e3a1);
          letter-spacing: -0.02em;
        }

        .progress-track {
          height: 8px;
          background: rgba(49, 50, 68, 0.8);
          border-radius: 4px;
          overflow: hidden;
          position: relative;
        }

        .progress-fill {
          height: 100%;
          width: 0%;
          background: linear-gradient(90deg, var(--bar-start, #a6e3a1), var(--bar-end, #40a02b));
          border-radius: 4px;
          position: relative;
          transition: width 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
        }

        .progress-fill::after {
          content: '';
          position: absolute;
          right: 0;
          top: 50%;
          transform: translateY(-50%);
          width: 12px;
          height: 12px;
          background: var(--bar-end, #40a02b);
          border-radius: 50%;
          box-shadow: 0 0 20px var(--glow-color, rgba(166, 227, 161, 0.6));
          opacity: 0;
          transition: opacity 0.3s;
        }

        .progress-fill.animate::after {
          opacity: 1;
          animation: pulseGlow 1.5s ease-in-out infinite;
        }

        @keyframes pulseGlow {
          0%, 100% { transform: translateY(-50%) scale(1); opacity: 0.8; }
          50% { transform: translateY(-50%) scale(1.3); opacity: 1; }
        }

        .time-badge {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          margin-top: 16px;
          padding: 6px 12px;
          background: rgba(49, 50, 68, 0.6);
          border-radius: 20px;
          font-size: 12px;
          color: rgba(205, 214, 244, 0.7);
          font-family: var(--font-mono, 'JetBrains Mono', monospace);
        }

        .time-badge svg {
          width: 14px;
          height: 14px;
          color: var(--color-mauve, #cba6f7);
        }

        /* Shake animation for high risk */
        @keyframes shake {
          0%, 100% { transform: translateX(0); }
          10%, 30%, 50%, 70%, 90% { transform: translateX(-2px); }
          20%, 40%, 60%, 80% { transform: translateX(2px); }
        }

        .risk-meter.shake {
          animation: shake 0.5s ease-in-out;
        }
      </style>

      <div class="risk-meter" style="
        --glow-color: ${colors.glow};
        --icon-bg: ${colors.primary}22;
        --icon-color: ${colors.primary};
        --label-color: ${colors.primary};
        --score-color: ${colors.primary};
        --bar-start: ${colors.primary};
        --bar-end: ${colors.secondary};
      ">
        <div class="header">
          <div class="icon-wrapper">
            ${RISK_ICONS[this._level] || RISK_ICONS.SAFE}
          </div>
          <div class="title-section">
            <h3 class="risk-label">${RISK_LABELS[this._level] || 'Unknown'}</h3>
            <p class="risk-description">Risk assessment complete</p>
          </div>
        </div>

        <div class="score-section">
          <div class="score-header">
            <span class="score-label">Risk Score</span>
            <span class="score-value">${this._score.toFixed(2)}</span>
          </div>
          <div class="progress-track">
            <div class="progress-fill" style="width: ${this._score * 100}%"></div>
          </div>
        </div>

        <div class="time-badge">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
          </svg>
          <span class="validation-time">--ms</span>
        </div>
      </div>
    `;
  }

  animateUpdate() {
    const colors = RISK_COLORS[this._level] || RISK_COLORS.SAFE;
    const meter = this.shadowRoot.querySelector('.risk-meter');
    const iconWrapper = this.shadowRoot.querySelector('.icon-wrapper');
    const label = this.shadowRoot.querySelector('.risk-label');
    const scoreValue = this.shadowRoot.querySelector('.score-value');
    const progressFill = this.shadowRoot.querySelector('.progress-fill');

    // Kill any existing timeline
    if (this._timeline) {
      this._timeline.kill();
    }

    // Create new timeline
    this._timeline = gsap.timeline();

    // Update CSS variables with transition
    meter.style.setProperty('--glow-color', colors.glow);
    meter.style.setProperty('--icon-bg', colors.primary + '22');
    meter.style.setProperty('--icon-color', colors.primary);
    meter.style.setProperty('--label-color', colors.primary);
    meter.style.setProperty('--score-color', colors.primary);
    meter.style.setProperty('--bar-start', colors.primary);
    meter.style.setProperty('--bar-end', colors.secondary);

    // Update icon
    iconWrapper.innerHTML = RISK_ICONS[this._level] || RISK_ICONS.SAFE;

    // Update label
    label.textContent = RISK_LABELS[this._level] || 'Unknown';

    // Animate score counter
    const currentScore = parseFloat(scoreValue.textContent) || 0;
    this._timeline.to({ val: currentScore }, {
      val: this._score,
      duration: 0.8,
      ease: 'power2.out',
      onUpdate: function() {
        scoreValue.textContent = this.targets()[0].val.toFixed(2);
      }
    }, 0);

    // Animate progress bar
    this._timeline.to(progressFill, {
      width: `${this._score * 100}%`,
      duration: 0.8,
      ease: 'power2.out'
    }, 0);

    // Add glow pulse
    progressFill.classList.add('animate');

    // Activate glow
    meter.classList.add('active');

    // Shake for high risk
    if (this._level === 'HIGH_RISK') {
      meter.classList.add('shake');
      setTimeout(() => meter.classList.remove('shake'), 500);
    }

    // Icon bounce
    this._timeline.fromTo(iconWrapper,
      { scale: 0.8, opacity: 0 },
      { scale: 1, opacity: 1, duration: 0.4, ease: 'back.out(1.7)' },
      0
    );
  }

  setValidationTime(ms) {
    const timeEl = this.shadowRoot.querySelector('.validation-time');
    if (timeEl) {
      gsap.fromTo(timeEl,
        { opacity: 0 },
        {
          opacity: 1,
          duration: 0.3,
          onStart: () => { timeEl.textContent = `${ms}ms`; }
        }
      );
    }
  }

  reset() {
    const meter = this.shadowRoot.querySelector('.risk-meter');
    const progressFill = this.shadowRoot.querySelector('.progress-fill');

    meter.classList.remove('active');
    progressFill.classList.remove('animate');
    progressFill.style.width = '0%';

    this._score = 0;
    this._level = 'SAFE';
  }
}

customElements.define('pg-risk-meter', RiskMeter);

export { RiskMeter };
