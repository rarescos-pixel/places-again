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

The public Quality Gate passes automated tests, 52 labeled evaluation cases, core invariants, full-history secret scan, Python/shell syntax, JSON/SVG parse checks, and generated evidence artifacts.

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

The authoritative Google Cloud deployment completed with `FINAL_STATUS=SUCCESS` and proved the real production path:

- Cloud Run API -> Pub/Sub;
- authenticated Pub/Sub OIDC -> private Cloud Run worker;
- Google ADK + Gemini 3.5 on Vertex AI;
- bounded Gemini candidate selection;
- deterministic current-state re-verification;
- Firestore `v1 -> v2` exactly once as a business effect;
- replay without duplicate state/outbox effects;
- adversarial/impossible event -> `human_required` with no unsafe mutation/send;
- prepared outbox, messages sent = 0.

Verified project: `project-2ee12060-728f-434f-9ad`.
Evidence checkpoint: `reports/cloud-e2e-verified-20260829.md`.

### Anonymous public reachability + independent live Cloud E2E — PASSED

Current judge-accessible hosted application:

`https://places-again-674409858210.europe-west1.run.app`

The prior 404 diagnosis was a false lead caused by two stale Cloud Run URLs hardcoded in the GitHub workflow. After the workflow was pointed at the current Cloud Run service URL, GitHub Actions `Live Cloud E2E Proof` run `33254443473` completed successfully from an anonymous GitHub-hosted runner.

The external proof verified `/api/capabilities` and observed:

- Google Cloud Run;
- Google Agent Development Kit;
- `gemini-3.5-flash`;
- Vertex AI;
- Firestore;
- Google Pub/Sub;
- private worker configured;
- outbound delivery disabled / `prepared_not_sent` only.

It then executed the full production E2E and ended with `passed: true`.

The captured live run showed:

- two hard-safe candidates;
- Gemini selected an existing candidate ID (`candidate-a` in that run);
- validated reasons: `preserve_highest_priority_activity` and `minimize_people_schedule_changes`;
- deterministic re-verification PASS;
- Firestore `v1 -> v2`;
- 3/3 opera activities recovered;
- 12.0 person-hours restored;
- 0 unaffected activities moved;
- 12 outbox items prepared;
- 0 messages sent;
- replay preserved version 2 and outbox count 12;
- adversarial unknown-person incident -> `human_required`.

Raw evidence artifact:
`live-cloud-e2e-7e5cb3d29a11ef9affa3d3c44fe73d94df84cbfd`, artifact ID `9715370372`.

**The public-front-door blocker is closed. Do not spend more time on Cloud Shell diagnostics or front-door repair unless the verified URL later stops responding.**

## Immediate execution order

1. Synchronize README, Devpost, Judge Evidence, checkpoint, and final checklist with the verified public URL/evidence.
2. Keep the runtime frozen unless a concrete defect appears.
3. Record the final <=4 minute video from the exact externally reachable build, with the main trigger-to-terminal proof segment continuous and unedited.
4. Publish the prepared build article + social post for the low-risk +0.4 bonus when the owner approves publication.
5. Validate optional Gemma PR #2 only if a real managed call can be evidenced without threatening video/submission timing.
6. Reconcile final video URL/timestamps and any bonus URLs into Devpost + Judge Evidence.
7. Complete the entrant eligibility review honestly.
8. Submit early, tag/freeze the exact judged commit/build/video.

## Final assets already prepared

- `docs/final-submission-gate.md` — canonical official + winner-pattern + bonus + freeze checklist.
- `docs/final-upload-copy.md` — YouTube/Vimeo + Devpost copy-paste packet with verified hosted URL.
- `docs/submission.md` — Devpost copy including explicit data sources, pre-existing-work disclosure, findings/learnings.
- `docs/demo-script.md` — target 3:50 English video; no pre-scripted Gemini candidate ID/reasons.
- `docs/recording-runbook.md` — recording flow + direct Cloud Console tabs.
- `docs/judge-testing-instructions.md` — hosted judge flow plus reproducible local fallback.
- `docs/build-article.md` — public bonus article.
- `docs/social-post.md` — social bonus copy with required hashtag.
- `JUDGE_EVIDENCE.md` — rubric-to-evidence map.
- architecture and workflow diagrams are committed.

## Bonus model branch

Draft PR #2 (`bonus-gemma4-refresh`) is the only current Gemma bonus path. The older PR #1 is closed as superseded.

PR #2 CI is green. It remains intentionally isolated and must not be merged unless:

1. a real managed Gemma 4 call is owner-authenticated and evidenced;
2. README and final demo can show the additional model clearly, as Devpost requires for model-bonus evidence;
3. it does not threaten video/submission timing or the verified Taskmaster core.

Do not pursue extra models merely for score stuffing.

## Owner-only actions that cannot be delegated

- public YouTube/Vimeo publication;
- public article/social publication;
- entrant eligibility declarations;
- final Devpost Submit.

Everything else should be automated or completed in repo without using the owner as a terminal/browser bridge.
