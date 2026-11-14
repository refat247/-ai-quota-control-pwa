# Changelog

All notable changes follow SemVer and Keep a Changelog.

## [3.0.1] - 2026-11-14

### Fixed
- Block private JSON import at the known shared `refat247.github.io` browser origin; require a dedicated hostname before private onboarding.
- Reject imported Grok 5-hour quotas in the same cross-record validation path used by both import methods.
- Add explicit export-first confirmation before replacing browser records.
- Correct stale HTML submit label; improve contrast and modal background focus isolation.
- Correct release/Pages documentation and add browser regression tests beyond static checks.

### Added
- Paste JSON import for Android download workarounds, through the same validator as file import.
- Firebase Hosting Spark deployment preparation using an explicit five-asset `dist/` allowlist; no Firebase project/account mutation or real deployment was made.

### Not yet verified
- Real Android Chrome import / close-reopen persistence, PWA offline and installation on dedicated Firebase hostname.
- Threat model and privacy acceptance of plaintext browser storage on any hosted origin.

## [3.0.0] - 2026-11-14

### Added
- First public-safe PWA app shell, per-origin localStorage, JSON import/export, service-worker assets.
- GitHub Pages build and deployment workflow successful for commit `084b4abf67fdb4bd5aedd93eb9d7f34ca1f52654`.

### Limitations
- Prior v3.0.0 browser-level Android persistence remains unverified. Original user-private JSON was never committed to GitHub.