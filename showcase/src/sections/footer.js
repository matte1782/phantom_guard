/**
 * Footer Section for Phantom Guard Showcase
 *
 * Includes GitHub, PyPI links and attribution.
 */

export function createFooter() {
  return `
    <div class="footer-container">
      <div class="footer-brand">
        <svg class="footer-logo" aria-hidden="true"><use href="#ghost"/></svg>
        <span class="footer-name">Phantom Guard</span>
        <span class="footer-version">v0.1.2</span>
      </div>

      <div class="footer-links">
        <a href="https://github.com/matte1782/phantom_guard" target="_blank" rel="noopener noreferrer" class="footer-link">
          <svg class="icon" aria-hidden="true"><use href="#github"/></svg>
          <span>GitHub</span>
          <span class="github-stars">
            <svg class="icon icon-sm" aria-hidden="true"><use href="#zap"/></svg>
            <span id="star-count">-</span>
          </span>
        </a>
        <a href="https://pypi.org/project/phantom-guard/" target="_blank" rel="noopener noreferrer" class="footer-link">
          <svg class="icon" aria-hidden="true"><use href="#package"/></svg>
          <span>PyPI</span>
        </a>
        <a href="https://github.com/matte1782/phantom_guard#readme" target="_blank" rel="noopener noreferrer" class="footer-link">
          <svg class="icon" aria-hidden="true"><use href="#book"/></svg>
          <span>Docs</span>
        </a>
      </div>

      <div class="footer-meta">
        <span class="footer-license">MIT License</span>
        <span class="footer-separator">•</span>
        <span class="footer-author">
          Built with <span class="heart" aria-label="love">&#x2764;</span> by
          <a href="https://github.com/matte1782" target="_blank" rel="noopener noreferrer">Matteo Panzeri</a>
        </span>
      </div>
    </div>
  `;
}

/**
 * Initialize footer - fetch GitHub stars
 */
export function initFooter() {
  fetchGitHubStars();
}

/**
 * Fetch GitHub stars count
 */
async function fetchGitHubStars() {
  const starEl = document.querySelector('#star-count');
  if (!starEl) return;

  try {
    // Try to fetch from GitHub API
    const response = await fetch('https://api.github.com/repos/matte1782/phantom_guard');
    if (response.ok) {
      const data = await response.json();
      const stars = data.stargazers_count || 0;
      starEl.textContent = formatStars(stars);
    } else {
      // API error - show dash instead of misleading "0"
      starEl.textContent = '-';
    }
  } catch (err) {
    // Network/CORS error - show dash instead of misleading "0"
    starEl.textContent = '-';
  }
}

/**
 * Format star count (e.g., 1500 -> 1.5k)
 */
function formatStars(count) {
  if (count >= 1000) {
    return (count / 1000).toFixed(1) + 'k';
  }
  return count.toString();
}
