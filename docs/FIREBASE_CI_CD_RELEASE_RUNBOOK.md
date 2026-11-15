# Firebase Hosting CI/CD — Owner Release Runbook (Draft)

Date: 2026-11-15 (Asia/Dhaka). Author: ChatGPT (GPT-6). STATUS: NOT ACTIVATED.

## Baseline and scope
- Existing Android PWA v3.0.2 on https://ai-quota-e7258.web.app/ has owner-accepted reopen persistence, offline acceptance, and private backup. Do not rerun the old checks.
- This PR changes CI/CD files only; it does not update Android app, browser storage, index.html, manifest, Service Worker, Firebase project or Firebase live Hosting.
- The separate html-to-pwa-pipeline repository is NOT the app repo.
- Existing .github/workflows/verify.yml already runs static-checks and browser-smoke for PR and main. Do not duplicate those tests.

## Exactly how the release gate works
1. The proposed firebase-hosting-release.yml listens only after a successful verify-public-pwa run on a push to main from THIS repository.
2. Repository Actions variable FIREBASE_DEPLOY_ENABLED must be exactly true. It is NOT set by this PR. By default the deploy job is skipped.
3. Before checkout/auth/deploy it checks that main is protected, the verified SHA is still main HEAD, and GitHub environment production has a required_reviewers rule; any missing or unreadable rule fails closed.
4. The production environment must also require owner approval. GitHub holds the job before it starts if that environment is properly configured. A blank environment is NOT a valid control.
5. With all gates passing, the workflow checks out the exact verified SHA, builds the existing five-file dist whitelist, uses Google Workload Identity Federation, and deploys only Hosting in Firebase project ai-quota-e7258.
6. Each deployment needs an approved main change, passing CI, and environment approval. No new GitHub Pages deployment mechanism is added (existing GitHub Pages is separate).

## Owner setup — in this order, before enabling
1. In repo refat247/-ai-quota-control-pwa, Settings > Branches: protect main; require PR before merge, passing existing jobs static-checks and browser-smoke, and disable force-push/deletion/bypass. This branch is currently UNPROTECTED (independently observed on 15 Nov); protection of html-to-pwa-pipeline does not count.
2. Settings > Environments: create production, configure required reviewer refat247, and limit deployments to main/protected branches. For a solo owner, do not enable Prevent self-review. Verify this in GitHub UI; an unprotected environment cannot satisfy the safety goal.
3. In Google Cloud project ai-quota-e7258, create a dedicated narrowly scoped service account, configure a Workload Identity Pool/provider bound to only this repo + main ref (+ production environment claim when supported), and grant only verified Hosting deploy permissions. No personal Firebase tokens or long-lived JSON keys in code/chat.
4. In production Environment variables set GCP_WIF_PROVIDER and GCP_DEPLOY_SERVICE_ACCOUNT to the non-secret, verified provider resource ID and service-account email. Run a safe isolated auth/permission check first; do not enable deployment if WIF or Spark account capabilities are unverified.
5. Only after separate owner approval for the first production release, set repository variable FIREBASE_DEPLOY_ENABLED to true. Do not set it just to test the Draft PR. No workflow mutation, secret or Firebase deployment is authorized by this runbook.
6. On the first approved production push, inspect the exact verify workflow SHA, review the production deployment request, approve only the intended SHA, and retain Firebase Hosting prior release ID for rollback.

## Acceptance and rollback evidence
- PR number, source SHA, code review, passing existing checks, main protected status, production reviewers and branch restriction, WIF principal/permissions, Hosting target and release ID, prior release ID and owner acceptance.
- No private Plans/Quotas/JSON in GitHub, CI logs, artifacts, Firebase static assets or this chat. Real records stay in Android origin-local storage; backup remains with owner.
- On a bad deploy: disable FIREBASE_DEPLOY_ENABLED immediately; roll back static Hosting release using Firebase Console/CLI authorized owner controls; do NOT reset Chrome site data or reinstall the Android PWA.
- No repeat of v3.0.2 functional tests unless a future changed-risk behavior warrants it. No security certification implied by CI success.
- Two materially distinct attempts per blocker maximum; then HOLD with evidence and a reopening condition.

## Current exact next cursor
Draft PR independent security/logic audit. Manual owner setup of protected main, production reviewer environment and WIF/IAM; then separately approved first real deployment. The app remains unchanged until then.

Related KOS tracker: CROSS-SUBSCRIPTION-AI-ROUTING. Research method: Benchmark Atlas Route A (Evidence-First Bounded Batch).
References: https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments ; https://github.com/google-github-actions/auth ; https://firebase.google.com/docs/cli .
