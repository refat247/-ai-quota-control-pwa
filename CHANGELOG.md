# Changelog

All notable changes follow SemVer and Keep a Changelog.

## [3.0.2] - 2026-11-14

### Fixed
- First-time Quotas → Add guides through Add Plan if no subscription exists; then opens the quota form with the saved Plan selected.
- An empty Plan list no longer silently produces a blank selector and failed quota submission.
- Cancelling the guided Plan setup clears onboarding state; the JSON schema is unchanged.
- Added synthetic browser regression test for Plan → quota onboarding.

### Unverified
- Physical Android Chrome Custom Tab/browser restart persistence and offline/PWA install remain unverified.
- Private JSON onboarding still requires privacy and device acceptance; no personal data is included.

## [3.0.1] - 2026-11-14

### Fixed
- Block manual editing and local persistence on the shared GitHub Pages host; existing browser data is not deleted.
- Detect `xAI` as a Grok provider alias for unsupported five-hour quotas.
- Revalidate `/` responses with Firebase Hosting `Cache-Control: no-cache`.
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