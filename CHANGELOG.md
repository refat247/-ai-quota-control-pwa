# Changelog

All notable changes are documented here using [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.0] - 2026-11-14

### Added
- First **public-safe GitHub repository** release candidate of the v3 mobile-first PWA shell.
- Same-origin browser storage with explicit write/read-back checks and a visible save status.
- Offline service worker, web app manifest, responsive navigation and touch-friendly quota editing.
- JSON import/export so private user records stay **outside public Git history**.
- Automated version/privacy/PWA smoke checks.

### Changed
- Replaced v2.x local-file per-edit download persistence with an HTTPS single-URL workflow.
- Removed duplicate DOCTYPE from the previous local prototype and rebuilt public icons as minimal two-color raster assets.

### Known limitations
- No live Google/Claude/ChatGPT/Grok quota API and no automatic account sync.
- Browser site-data deletion may remove locally saved private records.
- GitHub Pages deployment, PWA installation and **real Android Chrome close/reopen persistence** are pending external verification.
