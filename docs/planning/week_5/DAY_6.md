# Week 5 Day 6: Hostile Review & Deployment

> **Date**: 2026-01-06
> **Focus**: Testing, Performance Audit, GitHub Pages Deploy
> **Estimated Hours**: 8

---

## Objectives

1. Run hostile review on showcase
2. Complete Lighthouse audit
3. Fix any issues found
4. Deploy to GitHub Pages
5. Verify production deployment

---

## Tasks

### Task 6.1: Functional Testing (2h)

**Manual Test Checklist:**

```markdown
## Cross-Browser Testing

### Chrome (Latest)
- [ ] Hero animation plays correctly
- [ ] Playground validation works
- [ ] All tabs switch properly
- [ ] Copy buttons work
- [ ] Scroll animations trigger
- [ ] No console errors

### Firefox (Latest)
- [ ] Hero animation plays correctly
- [ ] Playground validation works
- [ ] All tabs switch properly
- [ ] Copy buttons work
- [ ] Scroll animations trigger
- [ ] No console errors

### Safari (Latest)
- [ ] Hero animation plays correctly
- [ ] Playground validation works
- [ ] All tabs switch properly
- [ ] Copy buttons work
- [ ] Scroll animations trigger
- [ ] No console errors

### Mobile Safari (iOS)
- [ ] Layout responsive
- [ ] Touch interactions work
- [ ] Keyboard doesn't break layout
- [ ] No horizontal scroll

### Chrome Mobile (Android)
- [ ] Layout responsive
- [ ] Touch interactions work
- [ ] Keyboard doesn't break layout
- [ ] No horizontal scroll
```

**Automated Tests (Playwright):**

```javascript
// tests/e2e/showcase.spec.js
import { test, expect } from '@playwright/test';

test.describe('Showcase Landing Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('hero section renders', async ({ page }) => {
    await expect(page.locator('.hero-title')).toBeVisible();
    await expect(page.locator('pg-terminal')).toBeVisible();
  });

  test('playground validates package', async ({ page }) => {
    await page.fill('#package-input', 'requests');
    await page.click('#validate-btn');
    await expect(page.locator('.result-card')).toBeVisible({ timeout: 10000 });
  });

  test('tabs switch correctly', async ({ page }) => {
    await page.click('[data-tab="python"]');
    await expect(page.locator('#tab-python')).toHaveClass(/active/);
  });

  test('copy button works', async ({ page }) => {
    await page.click('[data-copy="cli"]');
    // Check clipboard or visual feedback
  });

  test('mobile layout', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await expect(page.locator('.hero-container')).toBeVisible();
    // No horizontal scroll
    const body = page.locator('body');
    const scrollWidth = await body.evaluate(el => el.scrollWidth);
    const clientWidth = await body.evaluate(el => el.clientWidth);
    expect(scrollWidth).toBeLessThanOrEqual(clientWidth + 1);
  });
});
```

### Task 6.2: Performance Audit (1.5h)

**Lighthouse CI Configuration:**

```javascript
// lighthouserc.js
module.exports = {
  ci: {
    collect: {
      url: ['http://localhost:4173/'],
      numberOfRuns: 3,
    },
    assert: {
      assertions: {
        'categories:performance': ['error', { minScore: 0.9 }],
        'categories:accessibility': ['error', { minScore: 0.9 }],
        'categories:best-practices': ['error', { minScore: 0.9 }],
        'categories:seo': ['error', { minScore: 0.9 }],
        'first-contentful-paint': ['error', { maxNumericValue: 1500 }],
        'largest-contentful-paint': ['error', { maxNumericValue: 2500 }],
        'cumulative-layout-shift': ['error', { maxNumericValue: 0.1 }],
        'total-blocking-time': ['error', { maxNumericValue: 300 }],
      },
    },
    upload: {
      target: 'temporary-public-storage',
    },
  },
};
```

**Bundle Analysis:**

```bash
# Analyze bundle size
npm run build -- --report

# Check gzip size
gzip -c dist/assets/*.js | wc -c
# Target: < 50KB gzipped

# Check CSS size
gzip -c dist/assets/*.css | wc -c
# Target: < 10KB gzipped
```

**Performance Checklist:**

```markdown
## Performance Verification

### Core Web Vitals
- [ ] LCP < 2.5s
- [ ] FID < 100ms
- [ ] CLS < 0.1

### Bundle Size
- [ ] JS bundle < 50KB gzipped
- [ ] CSS bundle < 10KB gzipped
- [ ] Total < 100KB gzipped

### Loading
- [ ] Fonts preloaded
- [ ] Critical CSS inlined
- [ ] Images lazy loaded
- [ ] No render-blocking resources

### Runtime
- [ ] Animations at 60fps
- [ ] No memory leaks
- [ ] Smooth scrolling
- [ ] No layout thrashing
```

### Task 6.3: Hostile Review (2h)

**Run hostile review command:**

```bash
/hostile-review showcase
```

**Review Checklist:**

```markdown
## HOSTILE_VALIDATOR Report - Showcase

### Security Scan
- [ ] No inline scripts with untrusted data
- [ ] CSP headers configured
- [ ] HTTPS enforced
- [ ] No exposed API keys
- [ ] External links have rel="noopener"

### Accessibility Scan
- [ ] All images have alt text
- [ ] Color contrast ratio > 4.5:1
- [ ] Keyboard navigation works
- [ ] Focus indicators visible
- [ ] Screen reader tested

### Code Quality
- [ ] No console.log statements
- [ ] No debugger statements
- [ ] Error boundaries in place
- [ ] Graceful degradation

### Cross-Origin
- [ ] CORS configured for API calls
- [ ] Fonts loaded with crossorigin
- [ ] Images optimized

### Edge Cases
- [ ] Empty state for playground
- [ ] Error state for failed validation
- [ ] Loading state visible
- [ ] Timeout handling
```

### Task 6.4: Issue Remediation (1h)

**Common Issues & Fixes:**

```markdown
## Issue: Lighthouse Performance < 90

### Potential Fixes
1. Defer non-critical JS
   ```html
   <script type="module" src="/src/main.js" defer></script>
   ```

2. Inline critical CSS
   ```html
   <style>/* Critical above-fold CSS */</style>
   ```

3. Optimize images
   ```bash
   npx sharp-cli --input public/images/* --output public/images/optimized/
   ```

4. Add resource hints
   ```html
   <link rel="preconnect" href="https://fonts.googleapis.com">
   <link rel="dns-prefetch" href="https://pypi.org">
   ```

## Issue: Accessibility < 90

### Potential Fixes
1. Add aria-labels
   ```html
   <button aria-label="Copy code">...</button>
   ```

2. Fix color contrast
   ```css
   --color-subtext: #b4bdd0; /* Increased contrast */
   ```

3. Add skip link
   ```html
   <a href="#main" class="skip-link">Skip to content</a>
   ```

## Issue: Animation Jank

### Potential Fixes
1. Use will-change sparingly
   ```css
   .animating { will-change: transform; }
   ```

2. Avoid animating expensive properties
   ```css
   /* Bad */
   .step { animation: fadeIn 0.3s; width: 100%; }

   /* Good */
   .step { animation: fadeIn 0.3s; transform: translateX(0); }
   ```

3. Use GPU-accelerated properties
   ```css
   .animated { transform: translateZ(0); }
   ```
```

### Task 6.5: GitHub Pages Deployment (1h)

**Vite Configuration:**

```javascript
// vite.config.js
import { defineConfig } from 'vite';

export default defineConfig({
  base: '/phantom-guard/',  // Repository name
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
    rollupOptions: {
      output: {
        manualChunks: {
          gsap: ['gsap'],
        },
      },
    },
  },
});
```

**GitHub Actions Workflow:**

```yaml
# .github/workflows/deploy-showcase.yml
name: Deploy Showcase

on:
  push:
    branches: [main]
    paths:
      - 'showcase/**'
  workflow_dispatch:

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pages: write
      id-token: write

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: showcase/package-lock.json

      - name: Install dependencies
        working-directory: showcase
        run: npm ci

      - name: Build
        working-directory: showcase
        run: npm run build

      - name: Setup Pages
        uses: actions/configure-pages@v4

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: showcase/dist

      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

**Manual Deployment:**

```bash
# Build for production
cd showcase
npm run build

# Preview locally
npm run preview

# Deploy (if not using GitHub Actions)
npm run deploy  # Requires gh-pages package
```

### Task 6.6: Production Verification (0.5h)

**Post-Deploy Checklist:**

```markdown
## Production Verification

### URL Check
- [ ] https://matteocpnz.github.io/phantom-guard/ loads
- [ ] No 404 errors
- [ ] Assets load correctly
- [ ] Favicon visible

### Functionality Check
- [ ] Hero animation plays
- [ ] Playground works with live API
- [ ] All links work
- [ ] Copy buttons work

### Performance Check
- [ ] Load time < 3s on 3G
- [ ] All resources cached
- [ ] Service worker registered (if applicable)

### SEO Check
- [ ] Title correct
- [ ] Meta description present
- [ ] Open Graph tags work
- [ ] robots.txt accessible

### Analytics (if added)
- [ ] Page views tracking
- [ ] Event tracking working
```

---

## Deliverables

- [ ] All functional tests passing
- [ ] Lighthouse score > 90 (all categories)
- [ ] Hostile review verdict: GO
- [ ] GitHub Pages deployed
- [ ] Production URL working
- [ ] Final documentation updated

---

## Exit Criteria

```markdown
## Week 5 Complete Criteria

### Quality Gates
- [ ] Lighthouse Performance > 90
- [ ] Lighthouse Accessibility > 90
- [ ] Lighthouse Best Practices > 90
- [ ] Lighthouse SEO > 90
- [ ] FCP < 1.5s
- [ ] TTI < 3s
- [ ] Bundle < 100KB gzipped

### Hostile Review
- [ ] Security: PASS
- [ ] Accessibility: PASS
- [ ] Performance: PASS
- [ ] Code Quality: PASS
- [ ] Verdict: GO

### Deployment
- [ ] GitHub Pages live
- [ ] No console errors in production
- [ ] Mobile layout verified
- [ ] All browsers tested

### Documentation
- [ ] README updated with showcase link
- [ ] ROADMAP.md marked Week 5 complete
```

---

## Week 5 Summary

| Day | Focus | Hours | Deliverables |
|:----|:------|:------|:-------------|
| Day 1 | Setup | 6 | Vite project, design tokens, base styles |
| Day 2 | Hero | 8 | Terminal component, GSAP animations |
| Day 3 | Playground | 8 | Live validation, risk meter |
| Day 4 | Features | 8 | How It Works, Performance section |
| Day 5 | Polish | 8 | Integration examples, responsive, micro-interactions |
| Day 6 | Deploy | 8 | Testing, Lighthouse, GitHub Pages |
| **Total** | - | **46** | - |
