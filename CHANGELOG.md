# Changelog

All notable changes follow SemVer and Keep a Changelog.

## [3.3.0] - 2026-11-18 (DRAFT, not merged/deployed)

### Changed
- Home visual cockpit with compact date metrics, 2×3 provider tiles, separate circular model used-percent indicators and provider detail dialog.
- Quotas: provider shortcuts at entry, optional full original model list; retain one-tap quota update, validation and Grok 5h N/A.
- Plans: compact status tiles with existing detail/edit/delete on tap. Dates: Today / Next 3 / 7 days / All; full event and past timestamp lists on demand.
- Color+text semantics and compact saved status; never merge percentages across distinct models/accounts.

### Evidence and limits
- Original quota localStorage key, JSON schema, import/export, F1 recovery and origin rules unchanged. No new network calls.
- Synthetic-browser regression checks mobile overflow, source data byte identity, new navigation and editing. Actual Android acceptance, independent source review, canonical Version Manager CLI and owner exact-SHA release approval remain pending.

## [3.2.0] - 2026-11-18 (Firebase deployed; owner UX acceptance subsequently rejected)

### Changed
- Compact Quick Home now displays each model's separate manually-entered used percentage in labeled color chips: green <75%, amber 75–89%, red >=90%, grey Unknown; no cross-model/account aggregation.
- Visible legend, 2-row filter grid, shorter success notice and KPIs, and expandable upcoming decisions reduce scrolling. Comfortable retains detailed 5h/weekly cards and model actions.
- Passed reset timestamps are labeled as verification reminders, not proof of quota refill. Subscription decisions are not quota health.

### Safety and evidence
- Original quota JSON schema and storage key, backup/import, error/recovery behavior and separate optional UI preferences are unchanged.
- Synthetic Playwright regression targets 320/390px, color thresholds, per-model cards and byte-identical local quota JSON.
- Owner merge and Firebase deployment verified on 2026-11-18 (Firebase workflow #44265590988); independent PR review, canonical version-manager CLI, private backup integrity and Android persistence acceptance were not verified. Owner later rejected the scroll-heavy UX.

## [3.1.0] - 2026-11-18 (Firebase deployed; earlier draft notes preserved below)

### Added
- Batch A mobile Home provider/plan/model search + clear; All/Pinned/Reset ≤24h/Overdue/Weekly/5-hour filters.
- Per-account pinning and Quick/Comfortable display density; these preferences use a separate non-sensitive UI key and never rewrite the existing quota dataset.
- Provider-level quick actions: single model edit, multiple model details, or Add quota for an empty plan.
- Focus-visible UI and 44px touch targets with small-screen layouts. Synthetic Playwright regression verifies no quota localStorage mutation.

### Safety / pending acceptance
- No quota schema migration, provider API, AI usage history, remote sync or background alerts.
- Owner private JSON export and Android actual-data acceptance remain unverified. Draft branch must not deploy automatically.


## [3.0.3] - 2026-11-18 (draft, not deployed)

### Fixed (review candidate)
- Home render exceptions no longer leave the entire Home blank; a non-destructive diagnostic panel links to Quotas and Backup.
- Browser regression injects a synthetic Home TypeError and verifies records remain unchanged and backup navigation stays accessible.
- Bump the PWA service-worker cache identifier so a future owner-approved release updates the app shell without deleting browser localStorage.

### Root-cause repair (2026-11-18, review candidate)
- Fixed the Home “Expected renewal” sort comparator: `o.date.localeCompare(b.date)` referenced undefined variable `o` when comparing two or more monthly renewal dates. Changed to comparator argument `a`.
- Added deterministic two-renewal Chromium regression verifying nonblank Home, earliest expected renewal and unchanged browser records. This reproduces the original JavaScript ReferenceError using synthetic data only.
- No schema change. Version stays 3.0.3 because the previous merged v3.0.3 Firebase release is awaiting Production approval.

### Still open
- Exact owner-device console stack was not collected, but the source's ReferenceError and blank Home condition are independently reproduced. Android acceptance remains pending.
- Actual Android/iPhone recovery and persistence unverified. No deployment from this draft.


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