/**
 * Integration Section
 *
 * Showcases CI/CD integration options with interactive code tabs.
 * Features GSAP animations for tab transitions and code reveals.
 */

import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { logger } from '../utils/logger.js';

gsap.registerPlugin(ScrollTrigger);

// Integration options with code examples
const INTEGRATIONS = [
  {
    id: 'precommit',
    name: 'Pre-commit',
    icon: 'git-commit',
    filename: '.pre-commit-config.yaml',
    language: 'yaml',
    code: `repos:
  - repo: local
    hooks:
      - id: phantom-guard
        name: Validate packages
        entry: phantom-guard validate
        language: system
        files: (requirements.*\\.txt|pyproject\\.toml)$
        pass_filenames: false`,
    description: 'Block phantom packages before they enter your repo'
  },
  {
    id: 'github',
    name: 'GitHub Actions',
    icon: 'github',
    filename: '.github/workflows/security.yml',
    language: 'yaml',
    code: `name: Security Scan
on: [push, pull_request]

jobs:
  phantom-guard:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install phantom-guard
      - run: phantom-guard validate -r requirements.txt`,
    description: 'Automated validation on every push and PR'
  },
  {
    id: 'gitlab',
    name: 'GitLab CI',
    icon: 'gitlab',
    filename: '.gitlab-ci.yml',
    language: 'yaml',
    code: `phantom-guard:
  stage: test
  image: python:3.12-slim
  script:
    - pip install phantom-guard
    - phantom-guard validate -r requirements.txt
  rules:
    - changes:
        - requirements*.txt
        - pyproject.toml`,
    description: 'Integrate with GitLab pipelines seamlessly'
  },
  {
    id: 'python',
    name: 'Python API',
    icon: 'code',
    filename: 'validate.py',
    language: 'python',
    code: `from phantom_guard import validate_package, validate_batch

# Single package
result = validate_package("requests")
print(f"Risk: {result.risk_level}")  # SAFE

# Batch validation
packages = ["flask", "reqeusts", "django"]
results = await validate_batch(packages)

for r in results:
    if r.risk_level == "HIGH_RISK":
        print(f"BLOCKED: {r.package}")`,
    description: 'Programmatic validation with async support'
  }
];

// SVG Icons
const ICONS = {
  'git-commit': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="12" cy="12" r="4"/>
    <line x1="1.05" y1="12" x2="7" y2="12"/>
    <line x1="17.01" y1="12" x2="22.96" y2="12"/>
  </svg>`,
  'github': `<svg viewBox="0 0 24 24" fill="currentColor">
    <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
  </svg>`,
  'gitlab': `<svg viewBox="0 0 24 24" fill="currentColor">
    <path d="m23.546 10.93-2.994-9.21a.604.604 0 0 0-.578-.42.6.6 0 0 0-.578.42l-2.014 6.198H6.618L4.604 1.72a.6.6 0 0 0-.578-.42.604.604 0 0 0-.578.42l-2.994 9.21a.91.91 0 0 0 .33 1.018l10.836 7.875a.41.41 0 0 0 .484 0l10.836-7.875a.91.91 0 0 0 .33-1.018"/>
  </svg>`,
  'code': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <polyline points="16 18 22 12 16 6"/>
    <polyline points="8 6 2 12 8 18"/>
  </svg>`,
  'copy': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
  </svg>`,
  'check': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <polyline points="20 6 9 17 4 12"/>
  </svg>`
};

/**
 * Escape HTML entities
 */
function escapeHtml(text) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

/**
 * Syntax highlighting for code blocks
 * Uses double quotes for HTML attributes to avoid conflicts with string regex
 */
function highlightCode(code, language) {
  // First escape HTML entities to prevent XSS
  let escaped = escapeHtml(code);

  if (language === 'yaml') {
    // IMPORTANT: Use double quotes for HTML attributes
    // The string regex matches single quotes (YAML string literals)
    // so HTML attributes must use double quotes to avoid conflicts
    return escaped
      .replace(/^(\s*)([\w-]+):/gm, '$1<span class="code-key">$2</span>:')
      .replace(/'([^']+)'/g, '<span class="code-string">\'$1\'</span>')
      .replace(/#.*/g, '<span class="code-comment">$&</span>');
  }

  if (language === 'python') {
    // Order matters: strings first, then comments (which may contain keywords)
    return escaped
      .replace(/"([^"]+)"/g, '<span class="code-string">"$1"</span>')
      .replace(/#.*/g, '<span class="code-comment">$&</span>')
      .replace(/\b(from|import|if|for|in|await|print|def|async)\b/g, '<span class="code-keyword">$1</span>')
      .replace(/\b(validate_package|validate_batch|result|results|packages)\b/g, '<span class="code-var">$1</span>');
  }

  return escaped;
}

/**
 * Creates the integration section HTML
 */
export function createIntegrationSection() {
  return `
    <div class="integration-container">
      <!-- Section Header -->
      <div class="integration-header">
        <span class="section-eyebrow">Integration</span>
        <h2 class="section-title">Works Everywhere</h2>
        <p class="section-subtitle">
          Drop-in integration with your existing workflow.
          From local hooks to cloud pipelines.
        </p>
      </div>

      <!-- Integration Tabs -->
      <div class="integration-panel">
        <div class="integration-tabs" role="tablist">
          ${INTEGRATIONS.map((int, idx) => `
            <button class="integration-tab ${idx === 0 ? 'active' : ''}"
                    data-tab="${int.id}"
                    role="tab"
                    aria-selected="${idx === 0}">
              <span class="tab-icon">${ICONS[int.icon]}</span>
              <span class="tab-name">${int.name}</span>
            </button>
          `).join('')}
        </div>

        <div class="integration-content">
          ${INTEGRATIONS.map((int, idx) => `
            <div class="integration-pane ${idx === 0 ? 'active' : ''}"
                 data-pane="${int.id}"
                 role="tabpanel">
              <div class="pane-header">
                <div class="pane-info">
                  <span class="pane-filename">${int.filename}</span>
                  <span class="pane-description">${int.description}</span>
                </div>
                <button class="copy-btn" data-code="${int.id}" aria-label="Copy code">
                  <span class="copy-icon">${ICONS.copy}</span>
                  <span class="copy-check">${ICONS.check}</span>
                </button>
              </div>
              <pre class="pane-code"><code data-lang="${int.language}"></code></pre>
            </div>
          `).join('')}
        </div>
      </div>

      <!-- CTA Section -->
      <div class="integration-cta">
        <p class="cta-text">Ready to protect your supply chain?</p>
        <div class="cta-actions">
          <a href="https://pypi.org/project/phantom-guard/" class="cta-btn cta-btn--primary" target="_blank" rel="noopener">
            Install from PyPI
          </a>
          <a href="https://github.com/matte1782/phantom_guard" class="cta-btn cta-btn--secondary" target="_blank" rel="noopener">
            View on GitHub
          </a>
        </div>
      </div>
    </div>
  `;
}

/**
 * Initialize integration section interactivity
 */
export function initIntegrationSection() {
  const section = document.querySelector('#integration');
  if (!section) return;

  // Apply syntax highlighting to code blocks AFTER DOM is created
  // This avoids template literal double-escaping issues
  const panes = section.querySelectorAll('.integration-pane');
  panes.forEach((pane, idx) => {
    const codeEl = pane.querySelector('code');
    const integration = INTEGRATIONS[idx];
    if (codeEl && integration) {
      codeEl.innerHTML = highlightCode(integration.code, integration.language);
    }
  });

  const tabs = section.querySelectorAll('.integration-tab');
  const copyBtns = section.querySelectorAll('.copy-btn');

  // Tab switching
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const targetId = tab.dataset.tab;

      // Update tabs
      tabs.forEach(t => {
        t.classList.remove('active');
        t.setAttribute('aria-selected', 'false');
      });
      tab.classList.add('active');
      tab.setAttribute('aria-selected', 'true');

      // Update panes with animation
      const currentPane = section.querySelector('.integration-pane.active');
      const targetPane = section.querySelector(`[data-pane="${targetId}"]`);

      if (currentPane && targetPane && currentPane !== targetPane) {
        gsap.to(currentPane, {
          opacity: 0,
          y: -10,
          duration: 0.2,
          ease: 'power2.in',
          onComplete: () => {
            currentPane.classList.remove('active');
            targetPane.classList.add('active');
            gsap.fromTo(targetPane,
              { opacity: 0, y: 10 },
              { opacity: 1, y: 0, duration: 0.3, ease: 'power2.out' }
            );
          }
        });
      }
    });
  });

  // Copy functionality
  copyBtns.forEach(btn => {
    btn.addEventListener('click', async () => {
      const codeId = btn.dataset.code;
      const integration = INTEGRATIONS.find(i => i.id === codeId);
      if (!integration) return;

      try {
        await navigator.clipboard.writeText(integration.code);

        // Show success state
        btn.classList.add('copied');
        setTimeout(() => {
          btn.classList.remove('copied');
        }, 2000);
      } catch (err) {
        logger.error('[Integration] Copy failed:', err);
      }
    });
  });

  // Scroll animations
  const header = section.querySelector('.integration-header');
  const panel = section.querySelector('.integration-panel');
  const cta = section.querySelector('.integration-cta');

  // Header animation
  if (header) {
    gsap.fromTo(header.children,
      { opacity: 0, y: 30 },
      {
        opacity: 1,
        y: 0,
        duration: 0.7,
        stagger: 0.12,
        ease: 'power3.out',
        scrollTrigger: {
          trigger: header,
          start: 'top 80%'
        }
      }
    );
  }

  // Panel animation
  if (panel) {
    gsap.fromTo(panel,
      { opacity: 0, y: 40 },
      {
        opacity: 1,
        y: 0,
        duration: 0.8,
        ease: 'power3.out',
        scrollTrigger: {
          trigger: panel,
          start: 'top 80%'
        }
      }
    );
  }

  // CTA animation
  if (cta) {
    gsap.fromTo(cta,
      { opacity: 0, y: 30 },
      {
        opacity: 1,
        y: 0,
        duration: 0.7,
        ease: 'power3.out',
        scrollTrigger: {
          trigger: cta,
          start: 'top 90%'
        }
      }
    );
  }

  logger.log('[Integration] Section initialized');
}
