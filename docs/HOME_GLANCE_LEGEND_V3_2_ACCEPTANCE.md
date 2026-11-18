# Home compact-glance / legend — A96 acceptance specification

Baseline: main 7351cb10577677146c2c13d31962da371c512fe3; owner Android screenshot 2026-11-18.

Goal: reduce vertical scrolling and add semantic color-coded quota use in the existing PWA, inspired by the *information hierarchy*, not branding, of owner reference apps.

Frozen scope:
1. Keep Home to a short header, short save-success notice, 3 concise KPIs and compact filters (2x3 grid at 390px).
2. Quick view: show all six providers as small rows; each model must display its own used percentage as a text-labelled chip (never aggregate model/account percentages). Comfortable restores full window cards and all per-model actions.
3. Used-percentage legend: green less than 75%; amber 75–89%; red 90–100%; grey unknown. These colors describe **manual used %**, not provider/API health. Also label reset timestamps that have passed; never auto-assume quota refill.
4. Keep subscription decision (Keep/Trial/Cancel) separate from quota use. Keep direct Quotas, Plans, Dates, Backup tabs.
5. No changes to the existing main localStorage key, schema, private import/export, F1 recovery, payment logic or Firebase secrets. Preserve independent UI preference key.
6. Playwright synthetic regression across 320px, 390px, privacy, Grok 5h N/A, pin/search/filter/density, manual color thresholds, storage byte identity and no JS errors.
7. One Draft PR, exact HEAD CI, independent review/Version Manager CLI evidence, owner-scoped merge decision, separate Firebase production decision, one Android real-data acceptance batch.

Status: SPEC ONLY. Not an implemented feature. Not authorized for main merge/deploy.
