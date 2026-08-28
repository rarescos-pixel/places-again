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
- Region remains `europe-west1`; Vertex AI Gemini uses its supported global
  endpoint.
- No additional-model bonus work until the core cloud E2E gate is green.
- If core Cloud is not completely green by 2026-08-30 12:00 Europe/Bucharest,
  cancel all additional-model bonus work and protect the core plus the low-risk
  article/social bonus path.

## Completed and published on `main`

- Resilient per-API enablement with bounded 429/transient retry, backoff, jitter,
  and reporting.
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
- At least one complete public Quality Gate run has passed. The exact final
  submitted commit must also have its own green run and evidence artifact.
- Product-first README, Devpost copy, architecture/workflow diagrams, judge evidence,
  final demo script, build article, and social draft are published in the repo.
- Demo script consistency audit completed: duplicate narration removed and test
  count synchronized to 59 automated tests / 52 labeled evaluation cases.

## Current state

The winner-level code and evidence tree are already public on `main`. We are no
longer waiting for repository synchronization or a core product redesign.

The remaining decisive work is **proof and submission**, not feature expansion.
The next repository change should be driven only by a concrete failed gate or by
verified cloud evidence; otherwise preserve stability.

## Work routing

### SOL leverage points

1. Red-team real cloud evidence and every 5/5 rubric claim after deployment.
2. Resolve only concrete cross-system reliability/security defects exposed by the
   real API -> Pub/Sub -> worker -> Gemini/ADK -> Firestore run.
3. Apply the feature-freeze test: reject anything that does not improve the rubric,
   winner memorability, reliability, or the four-minute proof.
4. Audit the final video against the actual cloud evidence and submitted commit.
5. Perform final rules, eligibility-boundary, bonus, demo, and submission review.

### TERRA implementation queue

- Implement only scoped fixes revealed by cloud E2E or final compliance audit.
- Keep product copy and evidence synchronized with the verified deployed build.
- Do not introduce a new domain, major workflow, or architecture without a
  demonstrated scoring need.

### LUNA mechanical queue

- Verify the final `main` Quality Gate and downloadable generated evidence.
- Regenerate deterministic reports after any final code change.
- Check exact counts, URLs, timestamps, placeholders, and cross-document consistency.

Repository inventory, repeated test execution, report regeneration, simple text
consistency, and mechanical checks must not consume SOL work unless a failure
reveals ambiguity, regression risk, or a cross-system decision.

## Remaining hard gates

1. The exact final `main` commit has a green public GitHub Actions Quality Gate and
   generated evaluation/secret-scan evidence artifact.
2. One owner-authenticated guided deployment creates the real Google Cloud stack.
3. Cloud E2E proves real public Cloud Run -> Pub/Sub -> authenticated private
   worker -> Google ADK/Gemini selection -> deterministic re-verification ->
   Firestore commit, including `v1 -> v2`, replay without duplicate effects,
   impossible/adversarial fail-closed behavior, and zero sent messages.
4. Reconcile README, Judge Evidence, Devpost copy, and video numbers/links against
   the generated cloud evidence. Remove all remaining final-link placeholders.
5. Capture and publish a <=4-minute English video from the exact verified cloud
   build, with `.run.app` and Google Cloud proof visible.
6. Publish the prepared build article and social post for the low-risk +0.4 bonus.
7. Consider additional-model bonus work only after the core cloud gate is green and
   only if it cannot destabilize the submitted workflow or video.
8. Complete final rule/compliance and owner eligibility review, submit early, then
   tag and freeze the exact judged commit/deployment.

## Known constraints

- This execution environment has no authenticated Google Cloud control plane, so
  it cannot truthfully complete the cloud hard gate without one account-owner
  authentication/billing approval action.
- Real Gemini candidate behavior remains unproven until cloud E2E; deterministic,
  stubbed, and local fallback paths are not substitutes for that evidence.
- If an API request persists an event but exhausts bounded Pub/Sub publish retries,
  the client must retry the returned stable `event_id`; a separate durable
  transport dispatcher is intentionally not added before the deadline.
- The public contest profile exposes reset only for synthetic demo data. Reset is
  transactional, refuses active events, and preserves terminal evidence; a real
  operational deployment must leave this explicit demo flag disabled outside the
  contest demonstration profile.
- The video, public article/social action, eligibility declaration, and final
  Devpost Submit inherently require the owner.
- **OWNER ELIGIBILITY CHECK REQUIRED BEFORE FINAL SUBMIT:** the entrant alone must
  review and attest every Section 3 eligibility condition and any applicable
  third-party policy. Development does not claim personal eligibility on the
  entrant's behalf.

## Next action

1. Let the public Quality Gate finish on this exact `main` commit and verify its
   generated evidence artifact.
2. Make no speculative feature changes while that gate is green.
3. Then use the single guided Google Cloud deployment flow; do not give the owner
   terminal commands unless the hosted flow itself proves impossible.
4. Treat the first real cloud run as evidence collection: repair only concrete
   failures, rerun until the full Cloud E2E report is green, then feature-freeze.

## Acceptance invariants

- 0 unsafe commits; 0 unresolved auto-commits.
- 0 Gemini-invented-plan commits; 0 hard-constraint overrides.
- 100% committed candidates deterministically re-verified from current state.
- 100% stale-plan rejection; replay creates 0 duplicate business effects.
- Impossible or ambiguous recovery becomes `human_required`.
- Outbox is prepared, never sent.
- Both scenarios use the same candidate, selection, verification, and commit path.
