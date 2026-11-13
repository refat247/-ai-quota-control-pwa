# AI Quota Control PWA

**Version:** 3.0.0 · **Status:** Public-safe app source; production deployment requires GitHub Pages after the release PR is reviewed and merged.

Mobile-first, offline-ready quota tracking for ChatGPT, Claude, Gemini/Antigravity, Grok and other subscriptions. This is a **manual tracker**, not a live quota API.

## Privacy boundary

This repository contains **only the public application shell**. It deliberately contains **no** account emails, quota percentages, renewal/cancellation history or private JSON backups. Personal data can be imported locally into the browser and is stored under that website's browser origin; it is **not sent to this repository or synced between devices**.

Never commit private exports, medical records, passwords, API tokens or billing credentials. Do not treat browser storage as an encrypted vault. Clearing site data, resetting Chrome or changing origin can erase saved data; export a private JSON backup periodically.

## After the owner merges the release PR

1. In this repository select **Settings → Pages → Build and deployment → Deploy from a branch**.
2. Select **main**, **/(root)**, and **Save**.
3. Open the published HTTPS URL on Android Chrome; do not open `index.html` as a downloaded local file.
4. On the **Backup** tab, choose **Import my data (once)** and select the separate private JSON from your ChatGPT download. **Never upload that JSON to GitHub.**
5. Edit a quota and choose Save. Close and reopen **the same HTTPS URL**: the edited value should persist in that browser. Test this on your actual device before relying on it.
6. Optionally use Chrome **Add to Home screen**. Backup private data before browser/site-data deletion.

No file is downloaded on each edit. Offline mode depends on service-worker activation and browser cache.

## Development and verification

```sh
npm test
```

No npm install is required for the static smoke suite (only Node.js). The tests check version consistency, basic PWA structure, safe public source and JavaScript syntax. They are not proof of Android persistence or account-specific provider quotas.

Local preview: `python -m http.server 8787` then open `http://localhost:8787`. GitHub Pages HTTPS is needed for end-user deployment.

## Canonical governance

Workstream: `CROSS-SUBSCRIPTION-AI-ROUTING`. Initial public release follows SemVer 2.0.0. Current declarations: `package.json`, `README.md`, `CHANGELOG.md` and the app's `VERSION` constant. Owner-controlled merge is required. The GitHub source, Pages activation, real Android smoke test and private-data import are independent completion gates.
