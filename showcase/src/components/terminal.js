/**
 * Phantom Terminal Web Component
 *
 * A terminal-style display component for showcasing Phantom Guard validation.
 * Uses Shadow DOM for style encapsulation.
 */

export class PhantomTerminal extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  connectedCallback() {
    this.render();
  }

  render() {
    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: block;
          background: var(--color-surface, #313244);
          border-radius: var(--radius-lg, 12px);
          overflow: hidden;
          box-shadow: var(--shadow-lg, 0 10px 15px rgba(0,0,0,0.4));
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
          font-family: var(--font-mono, 'JetBrains Mono', monospace);
          font-size: 12px;
          color: var(--color-subtext, #a6adc8);
        }

        .terminal-body {
          padding: 20px;
          font-family: var(--font-mono, 'JetBrains Mono', monospace);
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
          background: var(--color-mauve, #cba6f7);
          animation: blink 1s step-end infinite;
          vertical-align: middle;
          margin-left: 2px;
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
          flex-wrap: wrap;
        }

        .risk-badge {
          padding: 2px 8px;
          border-radius: 4px;
          font-size: 12px;
          font-weight: 600;
        }

        .risk-badge.high-risk {
          background: rgba(243, 139, 168, 0.2);
          color: var(--color-red, #f38ba8);
        }

        .risk-badge.safe {
          background: rgba(166, 227, 161, 0.2);
          color: var(--color-green, #a6e3a1);
        }

        .progress-bar {
          height: 4px;
          background: var(--color-overlay, #45475a);
          border-radius: 2px;
          margin-top: 16px;
          overflow: hidden;
        }

        .progress-fill {
          height: 100%;
          background: var(--color-mauve, #cba6f7);
          width: 0;
          transition: width 0.3s ease-out;
        }

        .timing-label {
          font-size: 12px;
          color: var(--color-subtext, #a6adc8);
          margin-top: 8px;
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
}

customElements.define('pg-terminal', PhantomTerminal);
