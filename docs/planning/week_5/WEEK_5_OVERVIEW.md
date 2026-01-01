# Week 5: Showcase Landing Page

> **Phase**: 5 of 5
> **Duration**: 6 days
> **Goal**: Build an impressive, high-end landing page with interactive demo
> **Prerequisites**: Week 4 complete, v0.1.2 released on PyPI

---

## Objectives

1. **Impress First-Time Visitors** - Make security sexy
2. **Interactive Demo** - Real-time package validation in browser
3. **Developer-First UX** - Terminal aesthetic, dark mode, monospace
4. **Performance Showcase** - Prove the <200ms claim visually
5. **Easy Adoption** - Copy-paste install commands

---

## Design Philosophy

```
┌─────────────────────────────────────────────────────────────────┐
│                    SHOWCASE PRINCIPLES                          │
├─────────────────────────────────────────────────────────────────┤
│  1. SPEED IS THE FEATURE                                        │
│     - Show <200ms validation in real-time                       │
│     - Animated progress that feels instant                      │
│                                                                 │
│  2. LESS IS MORE                                                │
│     - Minimal UI, maximum impact                                │
│     - Every element serves a purpose                            │
│                                                                 │
│  3. MOTION WITH MEANING                                         │
│     - Animations guide attention                                │
│     - No gratuitous effects                                     │
│                                                                 │
│  4. DEVELOPER-FIRST AESTHETIC                                   │
│     - Dark mode default                                         │
│     - Monospace where it matters                                │
│     - Terminal-inspired interactions                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## Technical Stack

| Component | Technology | Rationale |
|:----------|:-----------|:----------|
| Framework | Vanilla JS + Web Components | Zero dependencies, fast load |
| Bundler | Vite | Lightning-fast HMR, ESM native |
| Animations | GSAP + CSS | Industry standard, 60fps |
| Styling | CSS Custom Properties | Themeable, no runtime cost |
| Icons | Lucide (tree-shaken) | Lightweight, consistent |
| Hosting | GitHub Pages | Free, fast CDN |

---

## Page Sections

### 1. Hero Section
- Phantom Guard logo + tagline
- Animated terminal demo showing real validation
- Two CTAs: "Try it Live" + "pip install"

### 2. Live Playground
- Real-time package validation
- Registry switcher (PyPI, npm, crates)
- Risk score visualization
- Signal cards with details

### 3. How It Works
- 3-step visual explanation
- Pattern matching illustration
- Typosquat detection demo

### 4. Performance Metrics
- Live benchmark visualization
- Cached vs uncached comparison
- Batch validation demo

### 5. Integration Examples
- pip/requirements.txt
- GitHub Actions workflow
- Pre-commit hook
- Python API usage

### 6. Footer
- GitHub link
- PyPI badge
- MIT License
- Created by Matteo Panzeri

---

## Day-by-Day Schedule

| Day | Focus | Deliverables |
|:----|:------|:-------------|
| Day 1 | Project Setup | Vite scaffold, design tokens, base styles |
| Day 2 | Hero Section | Terminal component, typing animation, logo |
| Day 3 | Live Playground | Validation API, input component, results display |
| Day 4 | Features & Performance | How it works, metrics visualization |
| Day 5 | Integration & Polish | Code examples, mobile responsive, animations |
| Day 6 | Hostile Review & Deploy | Testing, performance audit, GitHub Pages deploy |

---

## Success Metrics

| Metric | Target |
|:-------|:-------|
| Lighthouse Performance | >90 |
| First Contentful Paint | <1.5s |
| Time to Interactive | <3s |
| Bundle Size | <100KB gzipped |
| Mobile Usability | 100 |

---

## Exit Criteria

- [ ] Landing page deployed to GitHub Pages
- [ ] Interactive demo working with real PyPI API
- [ ] Mobile responsive (320px - 1920px)
- [ ] Lighthouse score >90
- [ ] All animations at 60fps
- [ ] Hostile review GO verdict
