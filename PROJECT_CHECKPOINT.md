# Project checkpoint

Updated: 2026-08-29 UTC

## Objective

Deliver a memorable, reliable Taskmaster entry: one absence cascades through an operation; Places, Again autonomously evaluates bounded safe recoveries, Gemini chooses what makes operational sense, deterministic code proves what is safe, and Google Cloud commits the smallest safe change.

## Locked architecture and positioning

Public Cloud Run API -> Pub/Sub -> private Cloud Run worker -> Google ADK with Gemini 3.5 -> deterministic candidate engine -> current-state deterministic re-verification -> Firestore atomic commit/event ledger -> prepared-not-sent outbox.

Gemini may select only a supplied safe `candidate_id` and bounded reason codes. It cannot invent plans, relax constraints, mutate state directly, send messages, call arbitrary HTTP/shell, or override hard safety.

Category: Taskmaster. Opera is the firsthand BYOF origin; Commercial Film/Broadcast proves same-engine portability. Safe incidents auto-commit after proof; ambiguity or impossibility becomes `human_required`. External communication remains `prepared_not_sent`; sent count must stay zero.

## What is verified

### Core quality — PASSED

Current `main` has a green public Quality Gate. The latest gate passes automated tests, 52 labeled evaluation cases, core invariants, full-history secret scan, Python/shell syntax, and JSON/SVG parse checks.

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

## CURRENT HARD BLOCKER — PUBLIC EXTERNAL REACHABILITY

Do not treat the public application as submission-ready yet.

After the Cloud E2E passed, the public service was repaired to:

- ingress = `all`;
- default `run.app` URL enabled;
- Cloud Run invoker IAM check disabled with `--no-invoker-iam-check`;
- compatibility `allUsers -> roles/run.invoker` binding attempted where permitted.

The owner Cloud Shell environment then returned HTTP 200 from `/api/capabilities` and printed:

`FINAL_STATUS=PUBLIC_FRONTDOOR_PUBLIC_MODE_SET`

However, independent GitHub-hosted runners still received HTTP 404 from BOTH:

- `https://places-again-inb6leu4ca-ew.a.run.app/api/capabilities`
- `https://places-again-618104708054.europe-west1.run.app/api/capabilities`

Therefore:

- backend/agent/Firestore viability = VERIFIED;
- public internet reachability = NOT YET VERIFIED;
- final video must NOT be recorded and final Devpost must NOT be submitted until an external runner reaches the service and the independent live E2E passes.

Google Cloud documentation identifies this 404 pattern as consistent with effective ingress/default-URL restrictions or VPC Service Controls / policy-level `run.googleapis.com/HttpIngress` blocking. A read-only diagnostic is already committed and Quality-Gate verified:

- `scripts/diagnose_public_404.sh`
- `docs/public-404-diagnostic.md`

It prints `DIAGNOSIS=...` and `FINAL_STATUS=PUBLIC_404_DIAGNOSTIC_COMPLETE` without mutating Cloud Run, IAM, Firestore, Pub/Sub, Vertex AI, or organization policies.

## Immediate execution order

1. Run the one-click read-only public-404 diagnostic in the owner Google Cloud environment.
2. Capture the exact `DIAGNOSIS=...` result.
3. Apply only the diagnosis-specific repair; do not guess or redeploy the working backend.
4. Re-run the independent GitHub `Live Cloud E2E Proof`.
5. Gate is closed only when an external runner reaches `/api/capabilities` and completes the real Gemini/ADK/Firestore E2E.
6. Then freeze runtime and move immediately to final video, article/social +0.4, Devpost reconciliation, compliance/eligibility review, submit, and freeze.

## Final assets already prepared

- `docs/submission.md` — final-form Devpost copy; final public URLs still need reconciliation.
- `docs/demo-script.md` — target 3:50 public English video.
- `docs/recording-runbook.md` — recording flow.
- `docs/build-article.md` — publication-ready build article draft.
- `docs/social-post.md` — publication-ready social post draft.
- `JUDGE_EVIDENCE.md` — rubric-to-evidence map.
- architecture and workflow diagrams are committed.

Do not publish article/social copy with the current live-app URL until external public reachability is verified.

## Bonus model branch

Draft PR #1 (`bonus-gemma4`) remains isolated. It is optional and must not be merged unless:

1. the public-reachability hard gate is already closed;
2. its CI is green;
3. a real managed Gemma call is owner-authenticated and evidenced;
4. it does not threaten video/submission timing or the verified core.

Core submission wins over bonus points.

## Owner-only actions that cannot be delegated

- one-click Cloud Shell diagnostic/repair when Google account authorization is required;
- public YouTube/Vimeo publication;
- public article/social publication;
- entrant eligibility declarations;
- final Devpost Submit.

Everything else should be automated or completed in repo without using the owner as a terminal/browser bridge.
