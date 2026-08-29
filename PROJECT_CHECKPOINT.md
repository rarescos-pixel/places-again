# Project checkpoint

Updated: 2026-08-29 UTC

## Objective

Deliver a memorable, reliable Taskmaster entry: one absence cascades through an
operation; Places, Again autonomously evaluates bounded safe recoveries, Gemini
chooses what makes operational sense, deterministic code proves what is safe,
and Google Cloud commits the smallest safe change.

## Current architecture

Public Cloud Run API -> Pub/Sub -> private Cloud Run worker -> Google ADK with
Gemini 3.5 -> deterministic candidate engine -> deterministic re-verification ->
Firestore atomic commit/event ledger -> prepared-not-sent outbox and audit trail.

Gemini may select only a `candidate_id` from a deterministic safe set and return
bounded reason codes. It cannot invent plans, mutate state, send messages, call
arbitrary HTTP/shell, or override hard constraints.

## Locked decisions

- Category: Taskmaster; Grand Prize remains possible under the official rules.
- Opera is the firsthand origin scenario; Commercial Film/Broadcast proves the
  same engine works in a second operational domain.
- Safe incidents auto-commit after re-verification; ambiguity/impossibility fails
  closed to `human_required`.
- External communications remain `prepared_not_sent`; sent count must remain zero.
- Cloud Run and Firestore remain in `europe-west1`; Vertex AI Gemini uses `global`.
- No new domain or major architecture work before submission.
- Additional-model bonus work is optional only after final-core freeze and only if
  it cannot destabilize the live build, video, or submission timeline.

## Verified live deployment

Cloud hard gate: **PASSED on 2026-08-29**.

Live application:

https://places-again-inb6leu4ca-ew.a.run.app

Verified project:

`project-2ee12060-728f-434f-9ad`

The authoritative deployment ended with `FINAL_STATUS=SUCCESS` and proved:

- public Cloud Run API;
- Pub/Sub topic `places-again-events`;
- authenticated OIDC delivery to private `places-again-worker`;
- real Google ADK + Gemini 3.5 through Vertex AI;
- multiple deterministic safe candidates and valid bounded Gemini selection;
- deterministic current-state re-verification;
- Firestore `v1 -> v2` exactly once;
- replay without duplicate business effects/outbox;
- impossible/adversarial event -> `human_required` with no unsafe mutation/send;
- messages prepared, messages sent = 0.

Deployment checkpoint is recorded in
`reports/cloud-deployment-success-2026-08-29.md`.

## Completed and published on `main`

- Resilient per-API enablement with bounded 429/transient retry, backoff, jitter,
  and reporting.
- Automatic Cloud Shell deployment helper that discovers an accessible,
  billing-enabled project rather than hardcoding an unavailable project.
- Event ledger, idempotency, retry/crash recovery, stale-plan rejection, atomic
  commit, authenticated worker path, and public-worker-route defense in depth.
- Multiple non-dominated safe candidates in both domains with real trade-offs.
- Bounded Gemini selection, persisted decision evidence, and deterministic
  re-verification from current state before every commit.
- Winner-focused UI cascade, before/after metrics, candidate decision evidence,
  failure state, and same-engine second-domain proof.
- Evaluation harness with 52 labeled cases plus unit/integration, security, replay,
  and adversarial checks.
- Local gate: 59/59 automated tests, 52/52 labeled evaluation cases, core
  verification, secret/history scan, shell/Python syntax checks, SVG/XML/JSON
  parsing, and diff checks pass.
- Public GitHub Actions `Quality Gate` runs tests, labeled evaluation, core
  verification, full-history secret scan, syntax/parse checks, and publishes the
  newly generated JSON evaluation and secret-scan reports as CI artifacts.
- At least one complete public Quality Gate run has passed; the exact final
  submitted commit must also have its own green run and evidence artifact.
- README, Devpost copy, architecture/workflow diagrams, Judge Evidence, demo script,
  build article, social post, and recording runbook are synchronized with the
  verified Cloud deployment.
- Build article and social copy contain the live URL and required hackathon language.

## Current state

The product and real Cloud proof are complete enough for finalist-level judging.
The project is now in **final submission phase**, not development phase.

The main risks are no longer core architecture or Cloud viability. They are:

1. an imperfect or >4-minute video;
2. mismatched spoken numbers/claims;
3. missing public article/social URLs;
4. final Devpost/compliance/eligibility mistakes;
5. unnecessary late feature work destabilizing the verified build.

## Work routing

### SOL leverage points

1. Red-team the final video against the live app and evidence.
2. Perform final 5/5/5 rubric and winner-memorability audit.
3. Decide whether any additional-model bonus is worth the risk after core freeze.
4. Audit final rules, eligibility boundary, Devpost fields, bonus URLs and freeze.

### TERRA implementation queue

- Only scoped fixes revealed by final video/compliance audit.
- Keep all claims synchronized with the live verified build.
- No new domain, major workflow, architecture or speculative feature.

### LUNA mechanical queue

- Verify final `main` Quality Gate and artifact.
- Check exact counts, URLs, timestamps and placeholders.
- Confirm public video duration and visibility.
- Confirm article/social links are public and correct.

## Remaining hard gates

1. Exact final `main` commit has a green public Quality Gate + generated evidence
   artifact.
2. Capture and publish a <=4-minute English video from the verified live build,
   with `.run.app` and Google Cloud proof visible.
3. Add the public video URL everywhere required.
4. Publish the build article and social post for the low-risk +0.4 bonus and add
   their public URLs to the submission.
5. Complete final rule/compliance and owner eligibility review.
6. Submit early, record the submitted commit, then freeze repository/deployment
   through judging.

Optional only:

7. Additional Google AI model bonus(s), only if safely integrated, genuinely useful,
   demonstrated in README/video, and completed without threatening gates 1–6.

## Known constraints

- The verified Cloud deployment is a contest demonstration profile with synthetic
  data and `PLACES_AGAIN_SYNTHETIC_DEMO_MODE=true` on the public API so the scenario
  can be reset between recording attempts. A real operational deployment should
  disable that explicit demo flag.
- If an API request persists an event but exhausts bounded Pub/Sub publish retries,
  the client must retry the returned stable `event_id`; a separate durable
  transport dispatcher is intentionally not added before the deadline.
- Video publication, public article/social publication, eligibility declaration,
  and final Devpost Submit inherently require the owner.
- **OWNER ELIGIBILITY CHECK REQUIRED BEFORE FINAL SUBMIT:** the entrant alone must
  review and attest every Section 3 eligibility condition and any applicable
  third-party policy. Development does not claim personal eligibility on the
  entrant's behalf.

## Next action

1. Let the final public Quality Gate pass on the current `main`.
2. Do not redeploy or add speculative features.
3. Record the video using `docs/recording-runbook.md` and `docs/demo-script.md`.
4. Publish build article + social post and capture public URLs.
5. Reconcile all final links, run final 5/5/5 + winner audit, submit and freeze.

## Acceptance invariants

- 0 unsafe commits; 0 unresolved auto-commits.
- 0 Gemini-invented-plan commits; 0 hard-constraint overrides.
- 100% committed candidates deterministically re-verified from current state.
- 100% stale-plan rejection; replay creates 0 duplicate business effects.
- Impossible or ambiguous recovery becomes `human_required`.
- Outbox is prepared, never sent.
- Both scenarios use the same candidate, selection, verification, and commit path.
