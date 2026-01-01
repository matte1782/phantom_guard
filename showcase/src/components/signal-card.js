/**
 * SignalCard Web Component
 *
 * Displays individual detection signals with severity-based styling.
 * Features entrance animations and hover effects.
 */

const SEVERITY_CONFIG = {
  high: {
    color: '#f38ba8',
    bg: 'rgba(243, 139, 168, 0.1)',
    border: 'rgba(243, 139, 168, 0.3)',
    icon: 'alert-triangle'
  },
  medium: {
    color: '#fab387',
    bg: 'rgba(250, 179, 135, 0.1)',
    border: 'rgba(250, 179, 135, 0.3)',
    icon: 'alert-triangle'
  },
  low: {
    color: '#f9e2af',
    bg: 'rgba(249, 226, 175, 0.1)',
    border: 'rgba(249, 226, 175, 0.3)',
    icon: 'info'
  },
  info: {
    color: '#a6e3a1',
    bg: 'rgba(166, 227, 161, 0.1)',
    border: 'rgba(166, 227, 161, 0.3)',
    icon: 'check-circle'
  }
};

const ICONS = {
  'alert-triangle': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
    <line x1="12" y1="9" x2="12" y2="13"/>
    <line x1="12" y1="17" x2="12.01" y2="17"/>
  </svg>`,
  'check-circle': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
    <polyline points="22 4 12 14.01 9 11.01"/>
  </svg>`,
  'x-circle': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="12" cy="12" r="10"/>
    <line x1="15" y1="9" x2="9" y2="15"/>
    <line x1="9" y1="9" x2="15" y2="15"/>
  </svg>`,
  'info': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="12" cy="12" r="10"/>
    <line x1="12" y1="16" x2="12" y2="12"/>
    <line x1="12" y1="8" x2="12.01" y2="8"/>
  </svg>`,
  'zap': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
  </svg>`,
  'search': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="11" cy="11" r="8"/>
    <path d="m21 21-4.35-4.35"/>
  </svg>`
};

class SignalCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  static get observedAttributes() {
    return ['type', 'severity', 'message', 'icon'];
  }

  connectedCallback() {
    this.render();
  }

  attributeChangedCallback(name, oldValue, newValue) {
    if (oldValue !== newValue && this.shadowRoot.querySelector('.signal-card')) {
      this.render();
    }
  }

  get type() {
    return this.getAttribute('type') || 'UNKNOWN';
  }

  get severity() {
    return this.getAttribute('severity') || 'info';
  }

  get message() {
    return this.getAttribute('message') || '';
  }

  get icon() {
    return this.getAttribute('icon') || 'info';
  }

  render() {
    const config = SEVERITY_CONFIG[this.severity] || SEVERITY_CONFIG.info;
    const iconSvg = ICONS[this.icon] || ICONS[config.icon] || ICONS.info;

    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: block;
        }

        .signal-card {
          display: flex;
          align-items: flex-start;
          gap: 12px;
          padding: 14px 16px;
          background: var(--bg-color);
          border: 1px solid var(--border-color);
          border-radius: 12px;
          transition: all 0.2s ease;
          cursor: default;
          position: relative;
          overflow: hidden;
        }

        .signal-card::before {
          content: '';
          position: absolute;
          left: 0;
          top: 0;
          bottom: 0;
          width: 3px;
          background: var(--accent-color);
          transform: scaleY(0);
          transform-origin: bottom;
          transition: transform 0.3s ease;
        }

        .signal-card:hover {
          background: var(--bg-hover);
          border-color: var(--accent-color);
          transform: translateX(4px);
        }

        .signal-card:hover::before {
          transform: scaleY(1);
        }

        .icon-wrapper {
          flex-shrink: 0;
          width: 32px;
          height: 32px;
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: var(--icon-bg);
          color: var(--accent-color);
        }

        .icon-wrapper svg {
          width: 18px;
          height: 18px;
        }

        .content {
          flex: 1;
          min-width: 0;
        }

        .signal-type {
          display: inline-block;
          font-size: 10px;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.08em;
          color: var(--accent-color);
          background: var(--icon-bg);
          padding: 3px 8px;
          border-radius: 4px;
          margin-bottom: 6px;
        }

        .signal-message {
          font-size: 14px;
          color: rgba(205, 214, 244, 0.9);
          line-height: 1.5;
          margin: 0;
        }

        /* Severity indicator dot */
        .severity-dot {
          position: absolute;
          top: 14px;
          right: 14px;
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: var(--accent-color);
          box-shadow: 0 0 8px var(--accent-color);
          animation: pulse 2s ease-in-out infinite;
        }

        @keyframes pulse {
          0%, 100% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.6; transform: scale(0.9); }
        }

        /* High severity gets faster pulse */
        :host([severity="high"]) .severity-dot {
          animation-duration: 1s;
        }
      </style>

      <div class="signal-card" style="
        --accent-color: ${config.color};
        --bg-color: ${config.bg};
        --bg-hover: ${config.bg.replace('0.1', '0.15')};
        --border-color: ${config.border};
        --icon-bg: ${config.bg};
      ">
        <div class="icon-wrapper">
          ${iconSvg}
        </div>
        <div class="content">
          <span class="signal-type">${this.type.replace(/_/g, ' ')}</span>
          <p class="signal-message">${this.message}</p>
        </div>
        <div class="severity-dot"></div>
      </div>
    `;
  }
}

customElements.define('pg-signal-card', SignalCard);

export { SignalCard };
