/**
 * Phantom Guard Showcase - Main Entry Point
 *
 * This file imports all styles, components, and initializes the application.
 */

// Styles
import './styles/tokens.css';
import './styles/reset.css';
import './styles/typography.css';
import './styles/animations.css';
import './styles/hero.css';
import './styles/playground.css';
import './styles/features.css';
import './styles/performance.css';
import './styles/integration.css';
import './styles/footer.css';
import './styles/premium.css'; // 2025 glassmorphism + glow effects

// Icon system
import { loadIcons } from './components/icons.js';

// Components
import './components/terminal.js';

// Sections
import { createHeroSection, initHeroSection } from './sections/hero.js';
import { createPlaygroundSection, initPlayground } from './sections/playground.js';
import { createFeaturesSection, initFeaturesSection } from './sections/features.js';
import { createPerformanceSection, initPerformanceSection } from './sections/performance.js';
import { createIntegrationSection, initIntegrationSection } from './sections/integration.js';
import { createFooter, initFooter } from './sections/footer.js';

// Utils
import { logger } from './utils/logger.js';

// Initialize application
async function init() {
  logger.log('[Phantom Guard] Initializing showcase...');

  // Load SVG icons first
  await loadIcons();

  // Render hero section
  const hero = document.querySelector('#hero');
  if (hero) {
    hero.innerHTML = createHeroSection();
    initHeroSection();
    logger.log('[Phantom Guard] Hero section initialized');
  }

  // Render playground section
  const playground = document.querySelector('#playground');
  if (playground) {
    playground.innerHTML = createPlaygroundSection();
    initPlayground();
    logger.log('[Phantom Guard] Playground initialized');
  }

  // Render features/how-it-works section
  const features = document.querySelector('#how-it-works');
  if (features) {
    features.innerHTML = createFeaturesSection();
    initFeaturesSection();
    logger.log('[Phantom Guard] Features section initialized');
  }

  // Render performance section
  const performance = document.querySelector('#performance');
  if (performance) {
    performance.innerHTML = createPerformanceSection();
    initPerformanceSection();
    logger.log('[Phantom Guard] Performance section initialized');
  }

  // Render integration section
  const integration = document.querySelector('#integration');
  if (integration) {
    integration.innerHTML = createIntegrationSection();
    initIntegrationSection();
    logger.log('[Phantom Guard] Integration section initialized');
  }

  // Render footer section
  const footer = document.querySelector('#footer');
  if (footer) {
    footer.innerHTML = createFooter();
    initFooter();
    logger.log('[Phantom Guard] Footer initialized');
  }

  logger.log('[Phantom Guard] Showcase initialized successfully');
}

// Start when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
