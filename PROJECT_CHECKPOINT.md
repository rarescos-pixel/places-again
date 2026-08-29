# Project checkpoint

Updated: 2026-08-29 UTC

## Objective

Deliver a memorable, reliable Taskmaster entry: one absence cascades through an operation; Places, Again autonomously evaluates bounded safe recoveries, Gemini chooses what makes operational sense, deterministic code proves what is safe, and Google Cloud commits the verified recovery that best fits ranked operational priorities.

Canonical final checklist: `docs/final-submission-gate.md`. Do not replace it with another planning document; update evidence against that checklist.

## Locked architecture and positioning

Cloud Run event API -> Pub/Sub -> private Cloud Run worker -> Google ADK with Gemini 3.5 -> deterministic candidate engine -> current-state deterministic re-verification -> Firestore atomic commit/event ledger -> prepared-not-sent outbox.

Gemini may select only a supplied safe `candidate_id` and bounded reason codes. It cannot invent plans, relax constraints, mutate state directly, send messages, call arbitrary HTTP/shell, or override hard safety.

Category: Taskmaster. Opera is the firsthand BYOF origin; Commercial Film/Broadcast proves same-engine portability. Safe incidents auto-commit after proof; ambiguity or impossibility becomes `human_required`. External communication remains `prepared_not_sent`; sent count must stay zero.

## What is verified

### Core quality — PASSED

Current `main` is protected by the public Quality Gate: automated tests, 52 labeled evaluation cases, core invariants, full-history secret scan, Python/shell syntax, JSON/SVG parse checks, and generated evidence artifacts.

Acceptance invariants remain:

- 0 unsafe commits;
- 0 unresolved auto-commits;
- 0 duplicate business effects;
- 0 Gemini-invented candidate commits;
- 0 hard-constraint overrides;
- 100% stale-plan rejection;
- 100% of committed candidates independently reverified;
- impossible/ambiguous recovery -> `human_required`;
- messages prepared, never sent.

### Owner-authenticated Google Cloud E2E — PASSED

The authoritative Cloud Shell deployment completed with `FINAL_STATUS=SUCCESS` and proved the real production path:

- Cloud Run API -> Pub/Sub;
- authenticated Pub/Sub OIDC -> private Cloud Run worker;
- Google ADK + Gemini 3.5 on Vertex AI;
- bounded Gemini candidate selection;
- deterministic current-state re-verification;
- Firestore `v1 -> v2` exactly once;
- replay without duplicate state/outbox effects;
- adversarial/impossible event -> `human_required` with no unsafe mutation/send;
- prepared outbox, messages sent = 0.

Verified project: `project-2ee12060-728f-434f-9ad`.
Evidence checkpoint: `reports/cloud-e2e-verified-20260829.md`.

## CURRENT PRIORITY — PUBLIC EXTERNAL REACHABILITY

Anonymous public reachability is **not** an official Stage-One pass/fail requirement. The official FAQ says the application does not have to remain publicly accessible/deployed during judging, and the hosted-project URL is highly encouraged rather than mandatory.

However, public judge access remains a high-value winner-readiness target because it reduces testing friction and strengthens Demo & Production Readiness.

Current state:

- ingress = `all`;
- default `run.app` URL enabled;
- Cloud Run invoker IAM check disabled with `--no-invoker-iam-check`;
- compatibility `allUsers -> roles/run.invoker` attempted where permitted;
- owner Cloud Shell environment returned HTTP 200 from `/api/capabilities` and printed `FINAL_STATUS=PUBLIC_FRONTDOOR_PUBLIC_MODE_SET`;
- independent GitHub runners still received HTTP 404 from both the hash-form and deterministic-form Cloud Run URLs.

Therefore:

- backend/agent/Firestore viability = VERIFIED;
- anonymous public reachability = NOT YET VERIFIED;
- preferred path = diagnose and fix before recording/submission;
- deadline fallback = do not miss submission solely because this anonymous front door remains unavailable. Use the verified video/repo/Cloud evidence and do not advertise a broken hosted URL as judge-accessible.

A read-only diagnostic is committed and Quality-Gate verified:

- `scripts/diagnose_public_404.sh`
- `docs/public-404-diagnostic.md`

It prints `DIAGNOSIS=...` and `FINAL_STATUS=PUBLIC_404_DIAGNOSTIC_COMPLETE` without mutating Cloud Run, IAM, Firestore, Pub/Sub, Vertex AI, or organization policies.

The owner account is temporarily rate-limited from Cloud Shell. Do not purchase Cloud Workstations or improvise around that quota. Resume the one-click diagnostic when Cloud Shell access returns.

## Immediate execution order

1. While Cloud Shell is unavailable: finish submission/video/test materials and low-risk bonuses in repo.
2. Publish the prepared build article + social post when the owner is ready; these bonuses do not require a live-app URL.
3. When owner Cloud Shell access returns, run the one-click read-only public-404 diagnostic.
4. Capture the exact `DIAGNOSIS=...` result and apply only the diagnosis-specific repair.
5. Re-run independent GitHub `Live Cloud E2E Proof`.
6. Preferred: close public reachability, then freeze runtime and record the final video from the externally reachable build.
7. If public reachability remains unresolved near the deadline, follow the official FAQ fallback: record compelling real Cloud execution evidence through the owner-accessible deployed system/Cloud Console, omit a broken hosted-project link, and submit on time.
8. Validate optional Gemma PR #2 only if the core/video/deadline are safe.
9. Reconcile Devpost + Judge Evidence + final video/bonus URLs/timestamps, complete eligibility review, submit, tag/freeze.

## Final assets already prepared

- `docs/final-submission-gate.md` — canonical official + winner-pattern + bonus + freeze checklist.
- `docs/submission.md` — Devpost copy including explicit data sources, pre-existing-work disclosure, findings/learnings.
- `docs/demo-script.md` — target 3:50 English video; no pre-scripted Gemini candidate ID/reasons.
- `docs/recording-runbook.md` — recording flow + direct Cloud Console tabs.
- `docs/judge-testing-instructions.md` — hosted judge flow plus reproducible local fallback.
- `docs/build-article.md` — public bonus article, ready without a live-app dependency.
- `docs/social-post.md` — social bonus copy with required hashtag, ready without a live-app dependency.
- `JUDGE_EVIDENCE.md` — rubric-to-evidence map.
- architecture and workflow diagrams are committed.

## Bonus model branch

Draft PR #2 (`bonus-gemma4-refresh`) is the only current Gemma bonus path. The older PR #1 is closed as superseded.

PR #2 CI is green. It remains intentionally isolated and must not be merged unless:

1. a real managed Gemma 4 call is owner-authenticated and evidenced;
2. README and final demo can show the additional model clearly, as Devpost requires for model-bonus evidence;
3. it does not threaten video/submission timing or the verified Taskmaster core.

Public front-door repair is preferred before Gemma work, but if the core submission is already safely recordable under the official FAQ fallback, deadline protection still takes precedence over optional bonus points.

## Owner-only actions that cannot be delegated

- one-click Cloud Shell diagnostic/repair when Google account authorization is required;
- public YouTube/Vimeo publication;
- public article/social publication;
- entrant eligibility declarations;
- final Devpost Submit.

Everything else should be automated or completed in repo without using the owner as a terminal/browser bridge.
