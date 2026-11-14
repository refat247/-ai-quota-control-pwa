# AI Quota Control PWA

**Version:** 3.0.2 · **Status:** First-run UX patch candidate. Dedicated Firebase Hosting v3.0.1 deploy succeeded per owner terminal; real Android persistence remains unverified. GitHub Pages private import/edit HOLD.

A mobile-first manual AI quota tracker. Not a provider API, automatic quota update, paid subscription sync, or alert service.

**First-use order:** create a Plan (subscription) before adding a quota. When none exist, Quotas → Add guides the user to create a Plan and resumes the quota form after the Plan is saved. This does not change the JSON data schema.

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