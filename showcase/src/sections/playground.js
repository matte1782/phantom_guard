/**
 * Playground Section for Phantom Guard Showcase
 *
 * Interactive package validation demo with real-time feedback.
 * Features debounced input, registry switching, and GSAP animations.
 */

import { gsap } from 'gsap';
import { validatePackage, getExamplePackages } from '../services/validator.js';
import { logger } from '../utils/logger.js';
import '../components/risk-meter.js';
import '../components/signal-card.js';

/**
 * Creates the playground section HTML
 */
export function createPlaygroundSection() {
  const examples = getExamplePackages();

  return `
    <div class="playground-container">
      <!-- Section Header -->
      <div class="playground-header">
        <span class="section-eyebrow">Interactive Demo</span>
        <h2 class="section-title">Try It Now</h2>
        <p class="section-subtitle">
          Enter any package name to see Phantom Guard in action.
          Real-time detection with instant feedback.
        </p>
      </div>

      <!-- Main Playground Card -->
      <div class="playground-card">
        <!-- Input Section -->
        <div class="input-section">
          <div class="input-wrapper">
            <div class="input-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="11" cy="11" r="8"/>
                <path d="m21 21-4.35-4.35"/>
              </svg>
            </div>
            <input
              type="text"
              id="package-input"
              class="package-input"
              placeholder="Enter package name..."
              autocomplete="off"
              spellcheck="false"
            />
            <div class="input-loader" aria-hidden="true">
              <div class="loader-spinner"></div>
            </div>
            <button class="input-clear" type="button" aria-label="Clear input" hidden>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>

          <!-- Registry Tabs -->
          <div class="registry-tabs" role="tablist">
            <button class="registry-tab active" data-registry="pypi" role="tab" aria-selected="true">
              <svg class="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M16.5 9.4l-9-5.19M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
                <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
                <line x1="12" y1="22.08" x2="12" y2="12"/>
              </svg>
              <span>PyPI</span>
            </button>
            <button class="registry-tab" data-registry="npm" role="tab" aria-selected="false">
              <svg class="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M16.5 9.4l-9-5.19M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
                <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
                <line x1="12" y1="22.08" x2="12" y2="12"/>
              </svg>
              <span>npm</span>
            </button>
            <button class="registry-tab" data-registry="crates" role="tab" aria-selected="false">
              <svg class="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M16.5 9.4l-9-5.19M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
                <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
                <line x1="12" y1="22.08" x2="12" y2="12"/>
              </svg>
              <span>Cargo</span>
            </button>
            <div class="tab-indicator"></div>
          </div>
        </div>

        <!-- Results Section -->
        <div class="results-section" id="results-section" aria-live="polite" aria-atomic="false">
          <!-- Empty State -->
          <div class="empty-state" id="empty-state">
            <div class="empty-ghost">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2C7.58 2 4 5.58 4 10v9c0 .55.45 1 1 1h.5c.28 0 .5-.22.5-.5v-1c0-.28.22-.5.5-.5s.5.22.5.5v1c0 .28.22.5.5.5h1c.28 0 .5-.22.5-.5v-1c0-.28.22-.5.5-.5s.5.22.5.5v1c0 .28.22.5.5.5h1c.28 0 .5-.22.5-.5v-1c0-.28.22-.5.5-.5s.5.22.5.5v1c0 .28.22.5.5.5h1c.28 0 .5-.22.5-.5v-1c0-.28.22-.5.5-.5s.5.22.5.5v1c0 .28.22.5.5.5h.5c.55 0 1-.45 1-1v-9c0-4.42-3.58-8-8-8zm-2.5 10c-.83 0-1.5-.67-1.5-1.5S8.67 9 9.5 9s1.5.67 1.5 1.5-.67 1.5-1.5 1.5zm5 0c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5z"/>
              </svg>
            </div>
            <p class="empty-text">Start typing to validate a package</p>
            <p class="empty-hint">Try one of the examples below</p>
          </div>

          <!-- Error State -->
          <div class="error-state" id="error-state" hidden>
            <div class="error-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="8" x2="12" y2="12"/>
                <line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
            </div>
            <p class="error-text">Unable to validate package</p>
            <p class="error-hint" id="error-hint">Please try again</p>
            <button class="error-retry" id="error-retry">Retry</button>
          </div>

          <!-- Results Container (hidden initially) -->
          <div class="results-container" id="results-container" hidden>
            <pg-risk-meter id="risk-meter"></pg-risk-meter>

            <div class="signals-section">
              <h4 class="signals-title">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                </svg>
                Signals Detected
              </h4>
              <div class="signals-list" id="signals-list"></div>
            </div>
          </div>
        </div>

        <!-- Example Packages -->
        <div class="examples-section">
          <span class="examples-label">Try these:</span>
          <div class="examples-list">
            ${examples.map(ex => `
              <button class="example-chip" data-package="${ex.name}" data-expected="${ex.expected}" title="${ex.description}">
                <span class="chip-name">${ex.name}</span>
                <span class="chip-badge chip-badge--${ex.expected.toLowerCase()}">${ex.expected.replace('_', ' ')}</span>
              </button>
            `).join('')}
          </div>
        </div>
      </div>
    </div>
  `;
}

/**
 * Initialize playground interactivity
 */
export function initPlayground() {
  const input = document.querySelector('#package-input');
  const clearBtn = document.querySelector('.input-clear');
  const loader = document.querySelector('.input-loader');
  const tabs = document.querySelectorAll('.registry-tab');
  const tabIndicator = document.querySelector('.tab-indicator');
  const emptyState = document.querySelector('#empty-state');
  const errorState = document.querySelector('#error-state');
  const errorHint = document.querySelector('#error-hint');
  const errorRetry = document.querySelector('#error-retry');
  const resultsContainer = document.querySelector('#results-container');
  const riskMeter = document.querySelector('#risk-meter');
  const signalsList = document.querySelector('#signals-list');
  const exampleChips = document.querySelectorAll('.example-chip');

  let currentRegistry = 'pypi';
  let debounceTimer = null;
  let isValidating = false;
  let lastPackageName = '';

  // Debounce function
  function debounce(fn, delay) {
    return (...args) => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => fn(...args), delay);
    };
  }

  // Show/hide loader
  function setLoading(loading) {
    isValidating = loading;
    loader.classList.toggle('active', loading);
    input.classList.toggle('loading', loading);
  }

  // Show/hide clear button
  function updateClearButton() {
    clearBtn.hidden = !input.value;
  }

  // Switch to results view
  function showResults() {
    if (!resultsContainer.hidden) return;

    // Hide both empty and error states
    const currentVisible = !emptyState.hidden ? emptyState :
                           !errorState.hidden ? errorState : null;

    if (currentVisible) {
      gsap.to(currentVisible, {
        opacity: 0,
        y: -20,
        duration: 0.3,
        ease: 'power2.in',
        onComplete: () => {
          emptyState.hidden = true;
          errorState.hidden = true;
          resultsContainer.hidden = false;
          gsap.fromTo(resultsContainer,
            { opacity: 0, y: 20 },
            { opacity: 1, y: 0, duration: 0.4, ease: 'power2.out' }
          );
        }
      });
    } else {
      resultsContainer.hidden = false;
      gsap.fromTo(resultsContainer,
        { opacity: 0, y: 20 },
        { opacity: 1, y: 0, duration: 0.4, ease: 'power2.out' }
      );
    }
  }

  // Switch to empty state
  function showEmpty() {
    if (!emptyState.hidden) return;

    // Hide both results and error states
    const currentVisible = !resultsContainer.hidden ? resultsContainer :
                           !errorState.hidden ? errorState : null;

    if (currentVisible) {
      gsap.to(currentVisible, {
        opacity: 0,
        y: 20,
        duration: 0.3,
        ease: 'power2.in',
        onComplete: () => {
          resultsContainer.hidden = true;
          errorState.hidden = true;
          emptyState.hidden = false;
          gsap.fromTo(emptyState,
            { opacity: 0, y: -20 },
            { opacity: 1, y: 0, duration: 0.4, ease: 'power2.out' }
          );
        }
      });
    } else {
      emptyState.hidden = false;
      gsap.fromTo(emptyState,
        { opacity: 0, y: -20 },
        { opacity: 1, y: 0, duration: 0.4, ease: 'power2.out' }
      );
    }
  }

  // Switch to error state
  function showError(message = 'Please try again') {
    errorHint.textContent = message;

    // Hide both results and empty states
    const currentVisible = !resultsContainer.hidden ? resultsContainer :
                           !emptyState.hidden ? emptyState : null;

    if (currentVisible) {
      gsap.to(currentVisible, {
        opacity: 0,
        y: 20,
        duration: 0.3,
        ease: 'power2.in',
        onComplete: () => {
          resultsContainer.hidden = true;
          emptyState.hidden = true;
          errorState.hidden = false;
          gsap.fromTo(errorState,
            { opacity: 0, y: -20 },
            { opacity: 1, y: 0, duration: 0.4, ease: 'power2.out' }
          );
        }
      });
    } else {
      errorState.hidden = false;
      gsap.fromTo(errorState,
        { opacity: 0, y: -20 },
        { opacity: 1, y: 0, duration: 0.4, ease: 'power2.out' }
      );
    }
  }

  // Render signals with stagger animation
  function renderSignals(signals) {
    signalsList.innerHTML = '';

    signals.forEach((signal, index) => {
      const card = document.createElement('pg-signal-card');
      card.setAttribute('type', signal.type);
      card.setAttribute('severity', signal.severity);
      card.setAttribute('message', signal.message);
      card.setAttribute('icon', signal.icon || 'info');

      // Set initial state for animation
      card.style.opacity = '0';
      card.style.transform = 'translateX(-20px)';

      signalsList.appendChild(card);

      // Stagger animation
      gsap.to(card, {
        opacity: 1,
        x: 0,
        duration: 0.4,
        delay: index * 0.1,
        ease: 'power2.out'
      });
    });
  }

  // Perform validation
  async function performValidation(packageName) {
    if (!packageName || packageName.length < 2) {
      showEmpty();
      return;
    }

    // Prevent duplicate validations
    if (isValidating) {
      return;
    }

    lastPackageName = packageName;
    setLoading(true);

    try {
      const result = await validatePackage(packageName, currentRegistry);

      // Show results view
      showResults();

      // Update risk meter
      riskMeter.setAttribute('level', result.risk_level);
      riskMeter.setAttribute('score', result.risk_score);
      riskMeter.setValidationTime(result.validation_time_ms);

      // Render signals
      renderSignals(result.signals);

    } catch (error) {
      logger.error('[Playground] Validation error:', error);
      const errorMessage = error.message || 'Network error. Please check your connection.';
      showError(errorMessage);
    } finally {
      setLoading(false);
    }
  }

  // Debounced validation
  const debouncedValidate = debounce(performValidation, 350);

  // Input event handlers
  input.addEventListener('input', (e) => {
    updateClearButton();
    debouncedValidate(e.target.value.trim());
  });

  input.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      input.value = '';
      updateClearButton();
      showEmpty();
    }
  });

  // Clear button
  clearBtn.addEventListener('click', () => {
    input.value = '';
    input.focus();
    updateClearButton();
    showEmpty();
  });

  // Registry tabs
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      // Update active state
      tabs.forEach(t => {
        t.classList.remove('active');
        t.setAttribute('aria-selected', 'false');
      });
      tab.classList.add('active');
      tab.setAttribute('aria-selected', 'true');

      // Move indicator
      const tabRect = tab.getBoundingClientRect();
      const containerRect = tab.parentElement.getBoundingClientRect();
      gsap.to(tabIndicator, {
        x: tabRect.left - containerRect.left,
        width: tabRect.width,
        duration: 0.3,
        ease: 'power2.out'
      });

      // Update registry and revalidate
      currentRegistry = tab.dataset.registry;
      if (input.value.trim()) {
        performValidation(input.value.trim());
      }
    });
  });

  // Initialize tab indicator position
  const activeTab = document.querySelector('.registry-tab.active');
  if (activeTab && tabIndicator) {
    const tabRect = activeTab.getBoundingClientRect();
    const containerRect = activeTab.parentElement.getBoundingClientRect();
    tabIndicator.style.width = `${tabRect.width}px`;
    tabIndicator.style.transform = `translateX(${tabRect.left - containerRect.left}px)`;
  }

  // Example chips
  exampleChips.forEach(chip => {
    chip.addEventListener('click', () => {
      const packageName = chip.dataset.package;
      input.value = packageName;
      updateClearButton();

      // Highlight the chip briefly
      gsap.fromTo(chip,
        { scale: 1 },
        { scale: 0.95, duration: 0.1, yoyo: true, repeat: 1 }
      );

      performValidation(packageName);
    });
  });

  // Animate empty ghost
  const emptyGhost = document.querySelector('.empty-ghost svg');
  if (emptyGhost) {
    gsap.to(emptyGhost, {
      y: -8,
      duration: 2,
      ease: 'power1.inOut',
      yoyo: true,
      repeat: -1
    });
  }

  // Focus input on section visibility (optional intersection observer)
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting && entry.intersectionRatio > 0.5) {
        // Subtle pulse on the input when section comes into view
        gsap.fromTo(input.parentElement,
          { boxShadow: '0 0 0 0 rgba(203, 166, 247, 0)' },
          {
            boxShadow: '0 0 0 4px rgba(203, 166, 247, 0.3)',
            duration: 0.4,
            yoyo: true,
            repeat: 1
          }
        );
      }
    });
  }, { threshold: 0.5 });

  const playgroundSection = document.querySelector('#playground');
  if (playgroundSection) {
    observer.observe(playgroundSection);
  }

  // Error retry button
  if (errorRetry) {
    errorRetry.addEventListener('click', () => {
      if (lastPackageName) {
        performValidation(lastPackageName);
      } else if (input.value.trim()) {
        performValidation(input.value.trim());
      } else {
        showEmpty();
      }
    });
  }

  logger.log('[Playground] Initialized');
}
