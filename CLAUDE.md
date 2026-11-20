# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A static personal portfolio site served by GitHub Pages (`shakiz.github.io`). Plain HTML/CSS/jQuery. There is no build step, package manager, linter or test suite. To preview, serve the repo root with any static server, e.g. `python3 -m http.server 8000`, and open `http://localhost:8000`. Pushing to `master` deploys.

## Structure

The site has three layers:

1. **`index.html`**: the single-page portfolio (about, resume, portfolio, services, blog, contact). It uses the original template's stack: `css/base.css`, `main.css`, `vendor.css`, `enhanced.css`, plus `js/jquery-2.1.3.min.js`, `plugins.js`, `main.js`.
2. **Hub pages** at the root: `agentic_dev.html` and `mobile_dev.html`. They share the template header/nav and the template CSS, plus `css/agentic_dev.css`, which both hubs use for the `guide-card` grid. Each hub lists its guides as `<a href="guides/..." class="guide-card">` entries.
3. **Guides** in `guides/`: self-contained long-form pages that do **not** use the template's CSS or JS. Each has its own stylesheet in `css/<guide_name>.css` (some, like `claude-code-pro.html`, also pull Tailwind/Chart.js from a CDN). Each starts with a `back-bar` div linking back to its hub (`../mobile_dev.html` or `../agentic_dev.html`). Paths inside `guides/` are relative (`../css/...`, `../favicon.png`).

Adding a new guide usually means touching three files: the guide HTML in `guides/`, its stylesheet in `css/`, and a new `guide-card` entry in the matching hub page. The top nav is duplicated in each root page (`index.html`, `agentic_dev.html`, `mobile_dev.html`). A new top-level page needs a nav link added to each of them.

Interactive guides keep their state in `localStorage` under versioned keys (e.g. `flutter-interview-guide.v2`, with a fallback read from `.v1`). If you change the stored shape, bump the version and keep the migration read.

## Other files

- `extract_css.py`: a one-off helper that moves inline `<style>` blocks out of a guide into `css/<name>.css` and swaps in a `<link>`. Its input and output paths are hardcoded to `learn_flutter_nextjs_way`. Edit them before reusing it.
- `inc/sendEmail.php`: the template's contact-form handler. GitHub Pages can't run PHP, so it doesn't work on the live site.
