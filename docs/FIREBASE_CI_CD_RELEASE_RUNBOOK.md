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
3. The deploy job checks that main is protected, both static-checks and browser-smoke are required status contexts, and the verified SHA is still main HEAD. It also checks that production has an actual required-reviewer rule, can_admins_bypass is false, and deployment_branch_policy.protected_branches is true. Any missing or unreadable rule fails closed.
4. The production environment must also require owner approval. GitHub holds the job before it starts if that environment is properly configured. A blank environment is NOT a valid control.
5. A separate build job (NO id-token permission) checks out the exact verified SHA, runs tests/build, validates the five-file dist allowlist and safe firebase.json, and uploads those public assets only. After owner environment approval, the separate deploy job downloads and independently validates those assets, authenticates via Google WIF, rechecks main SHA immediately before deployment, and targets only Firebase Hosting project ai-quota-e7258.
6. Each deployment needs an approved main change, passing CI, and environment approval. No new GitHub Pages deployment mechanism is added (existing GitHub Pages is separate).

## Owner setup — in this order, before enabling
1. In repo refat247/-ai-quota-control-pwa, Settings > Branches: confirm main requires PR before merge, required jobs static-checks and browser-smoke, no force-push/deletion and no unapproved bypass. As of 16 Nov, GitHub public branch response shows protected: true and lists both required status contexts. Full PR/force-push/deletion/admin-bypass rules were not independently readable via the available connector; owner must verify those exact settings in the GitHub UI. Protection of html-to-pwa-pipeline does not count.
2. Settings > Environments: create/configure production, add required reviewer refat247, DESELECT Allow administrators to bypass configured protection rules, and set deployment branches to Protected branches. The code deliberately requires protected_branches: true (Selected branches only is not accepted by the current fail-closed gate). For a solo owner, do not enable Prevent self-review if the owner must approve their own deploy. Verify all protection rules in GitHub UI; an absent or blank environment is not an approval gate.
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
Grok Build's first independent audit on SHA e681e44eb84dd682f3b438989ce6f423f12f0dbd returned REQUEST_CHANGES (F1/F2 P1, F3/F4/F5 P2, F6/F7 P3). This draft repair adds required check-context and environment checks, fresh SHA validation, fixed five-file allowlist, and separates build from OIDC-enabled deploy. Obtain an independent review on the NEW exact SHA and complete owner production environment + Firebase WIF/IAM setup; only then discuss a separately approved first release. This is NOT a security certification or actual deployment. The app remains unchanged until then.

Related KOS tracker: CROSS-SUBSCRIPTION-AI-ROUTING. Research method: Benchmark Atlas Route A (Evidence-First Bounded Batch).
References: https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments ; https://github.com/google-github-actions/auth ; https://firebase.google.com/docs/cli .

## Audit status and residual caveats (16 Nov 2026)
- Grok independent verdict on prior SHA: REQUEST_CHANGES; new SHA is NOT independently approved until reviewed again.
- GitHub API main protected:true with both required checks is verified; full branch policy settings and production environment / repo variables / GCP IAM remain owner-side verification gates.
- Build job does not receive id-token:write; deploy job receives it only after production environment approval, then uses pinned google-github-actions/auth. The Firebase CLI version is pinned to 15.36.0, but an npm package-integrity lock is not separately implemented. Review this residual supply-chain exposure before real release.
- Never turn on FIREBASE_DEPLOY_ENABLED or merge the Draft PR merely because the PR CI passes. Deploy only after separate owner authorization, WIF proof and rollback receipt.
