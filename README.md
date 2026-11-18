# AI Quota Control PWA

**Version:** 3.3.0 · **Status:** compact glance/legend UI review candidate on a separate branch; v3.1.0 merged and Firebase workflow succeeded at 7351cb1. This change is NOT merged/deployed. Real Android data/persistence acceptance remains unverified. GitHub Pages private import/edit HOLD.

A mobile-first manual AI quota tracker. Not a provider API, automatic quota update, paid subscription sync, or alert service.

**First-use order:** create a Plan (subscription) before adding a quota. When none exist, Quotas → Add guides the user to create a Plan and resumes the quota form after the Plan is saved. This does not change the JSON data schema.

## Batch A mobile Home UX (v3.1.0 review candidate)

Home search/clear and filters (All, Pinned, Reset ≤24h, Overdue, Weekly, 5-hour); independent provider pinning and Quick/Comfortable display density; safe provider quick actions (single pool edit, multiple pool details, zero-pool Add). UI preferences use a separate optional local key `ai-quota-ui-preferences-v1`, and are **not included in private JSON backup**; no provider quota schema or main key `ai-quota-control-center-v1` changes. Browser storage can fail; preferences then apply for this session only, and the interface discloses this. No background notifications or provider API sync.

Real Android/iPhone owner acceptance and verified independent JSON backup are prerequisites before any production release.

## Privacy rule

The original GitHub Pages project URL `https://refat247.github.io/-ai-quota-control-pwa/` shares its browser **origin** with any sibling Pages project on `https://refat247.github.io`. Browser `localStorage` is not isolated by path. v3.0.1 **blocks file and paste JSON import on that known shared origin**. Do not enter private account details manually on the old host either. There is no evidence of past compromise.

The application shell contains no private subscription JSON, owner emails, usage values or billing records. **Never publish private export data** to GitHub, Firebase Hosting, CI logs, screenshots, issues, or public bug reports. Encrypted storage is *not* implemented. Browser data can be erased by clearing site data or switching devices.

## Secure hosting preparation: Firebase Hosting (Spark)

Firebase **Hosting** (not **App Hosting**) can serve the static app on a unique `<SITE_ID>.web.app` origin under Spark. Create a dedicated Firebase project and site reserved for this dashboard, with Spark/no billing, then verify the final hostname before importing personal data. Do **not** confuse `*.firebaseapp.com` default auth domain with server-side secure private storage: data remains in browser `localStorage` on the hostname you actually open.

**Owner steps after release approval, before real data:**

1. Create a **separate Firebase project** at https://console.firebase.google.com/, choose **Spark** (no card). Use a globally unique project/site ID. As of 15 Oct 2026, a default Hosting site may need to be created when initializing Hosting.
2. From the approved checkout, run `npm run build:hosting`. It copies ONLY these five files into `dist/`: `index.html`, `sw.js`, `manifest.webmanifest`, `icon-192.png`, `icon-512.png`. This avoids accidentally serving repository tests, logs and private JSON.
3. Authenticate Firebase CLI **locally/Cloud Shell as the owner**: `firebase login`; then `firebase init hosting` or `firebase use --add`, select the specific existing project and confirm `dist` as public directory. **Do not override** the included `firebase.json` or `dist/` whitelist. If `firebase init` prompts to overwrite files, decline and inspect settings.
4. Deploy with `firebase deploy --only hosting --project YOUR_PROJECT_ID`. **Replace the placeholder**; project/site availability must be checked in your own console. No automatic GitHub-to-Firebase deploy or paid plan is configured by this PR.
5. Confirm the published URL is the dedicated `https://SITE_ID.web.app/`, not any `github.io` path. Open it in Chrome and test with **synthetic** data first.
6. Only after an independent privacy review and Android acceptance, optionally import the private JSON using **Backup → file import or Paste JSON**. If replacing records, export existing backup first. Pasted text is cleared after import attempt; Android clipboard history might retain it.

For day-to-day use: use the same HTTPS hostname in non-incognito Chrome. Quota edits save locally with read-back verification and no new HTML download. This does **not** synchronize across devices. Export private JSON backup periodically and store it privately.

## Browser acceptance gates

On synthetic fixtures: (a) 6 plans / 17 quota pools / 6 milestones import, (b) editor uses Save changes, (c) invalid Grok 5-hour import rejected, (d) 42% edit remains after reopening *the same origin*, (e) failed localStorage writes do not claim Saved automatically, (f) offline install/update on actual Android Chrome and 320px/390px layout (separate checks).

## Tests / Release

```bash
npm test
npm run build:hosting
python tests/browser_smoke.py
```

`tests/browser_smoke.py` requires Python Playwright and Chromium. It exercises local HTTP browser functionality; **passing it is not a physical Android Chrome test**. The GitHub Actions workflow runs smoke checks on a PR. Existing GitHub Pages main is not changed until owner-controlled merge.

SemVer: v3.0.1 is a compatible bugfix/UX repair to v3.0.0; original JSON schema and localStorage key retained. **Independent review and owner merge remain separate.**

KOS canonical ID: `CROSS-SUBSCRIPTION-AI-ROUTING`.

## v3.3.0 compact glance and color legend (DRAFT)

Quick Home shows a separate textual used-percentage chip for **each** tracked model; never average different models or accounts. Color threshold (manual used %, not API status): green less than 75%; amber 75–89%; red 90–100%; grey for Unknown. A passed reset timestamp is a reminder to verify provider UI, NOT proof of automatic refill. Subscription decision labels (Keep/Trial/Cancel) are separate. Filters use a 2-row layout, success-only storage status is compact and upcoming decision details are collapsed. Comfortable view retains the original detailed window cells, per-model details, Grok 5h N/A and quick editing. Main quota JSON key/schema, backup/import and optional separate UI preferences are unchanged.


## v3.3.0 visual cockpit (Draft PR — not deployed)

Mobile Home now shows three compact date metrics and a two-column provider grid with individual circular model-used meters, rather than six tall provider forms. Tap a provider for **every** model and quick update. Quotas starts with provider shortcuts; the original 17-card detailed list remains available only when explicitly chosen. Plans uses compact status tiles and opens original detail/edit/delete controls in a second-level dialog. Dates prioritizes the next three events, Today/Next 3/7 days/All, with all and past events accessible on demand. Backup/recovery and original quota JSON are unchanged. Colors pair with actual text: below 75% used green, 75–89% amber, 90%+ red, Unknown grey; 0 remains 0. All model percentages are independent and manual, never API-synced or averaged. Synthetic CI and Android acceptance are separate gates. No production merge or Firebase deployment is authorized by this draft.
