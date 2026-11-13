AI Quota Control PWA v3.0 — public-safe deploy package

DO NOT upload your private JSON or old personal HTML to any public repository!
This zip intentionally contains NO email addresses, private quota percentages, or personal renewal dates.

Deployment (one time):
1. Upload contents of this folder (index.html, sw.js, manifest.webmanifest, icons) to a NEW dedicated PUBLIC GitHub Pages repository, or another HTTPS static host. Keep personal JSON outside repository.
2. Enable GitHub Pages from repo root/main branch, or follow hosting provider instructions.
3. Open the exact published HTTPS site in Chrome Android.
4. In Backup > Import my data (once), choose the separate PRIVATE JSON backup delivered in this conversation.
5. Edit a quota > Save changes. Close Chrome and re-open THE SAME HTTPS ADDRESS; your change should remain.
6. Optionally use Chrome menu > Add to Home screen / Install app.

Data / privacy:
- Personal JSON is imported locally in the browser only. It never uploads to GitHub Pages.
- The public shell is accessible to all; it starts EMPTY for everyone else.
- Local browser storage is not account-wide cloud sync and can be cleared by user/browser. Do occasional optional JSON backup, particularly before phone replacement or browser reset.
- Never store secrets/passwords/API keys or patient data in the dashboard.
- No automatic sync with ChatGPT/Claude/Gemini/Grok providers; all quotas owner-entered.

Version 3.0.0. Test locally on HTTP before deployment using e.g. python -m http.server 8787 inside this folder. For PWA installation and service-worker functionality use HTTPS public hosting or localhost.