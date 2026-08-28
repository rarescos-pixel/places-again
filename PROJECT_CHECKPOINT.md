# Project checkpoint

Updated: 2026-08-28 UTC

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

## Completed locally

- Resilient per-API enablement with bounded 429/transient retry, backoff, jitter,
  and reporting.
- Event ledger, idempotency, retry/crash recovery, stale-plan rejection, atomic
  commit, authenticated worker path, and public-worker-route defense in depth.
- Multiple non-dominated safe candidates in both domains with real trade-offs.
- Bounded Gemini selection, persisted decision evidence, and deterministic
  re-verification before every commit.
- Winner-focused UI cascade, before/after metrics, candidate decision evidence,
  failure state, and same-engine second-domain proof.
- Evaluation harness with 52 labeled cases plus unit/integration, security, replay,
  and adversarial checks.
- Final local gate: 59/59 automated tests, 52/52 labeled evaluation cases,
  core verification, secret/history scan, shell/Python/JavaScript syntax checks,
  SVG/XML/JSON parsing, and diff checks all pass.
- Product-first README, Devpost copy, architecture/workflow diagrams, judge evidence,
  video script, build article, and social draft.

## In progress

- Synchronization of the SOL-reviewed, independently audited, locally verified
  tree to public GitHub `main`.

## Work routing

### SOL leverage points

1. Decide whether bounded Gemini selection is materially agentic and judge-visible,
   without weakening deterministic safety.
2. Resolve cross-system reliability/security findings across API, Pub/Sub, worker,
   Firestore, and the public contest demo.
3. Apply the feature-freeze test: reject anything that does not improve the rubric,
   winner memorability, reliability, or the four-minute proof.
4. Red-team the final cloud evidence and every 5/5 rubric claim.
5. Perform final rules, eligibility-boundary, demo, and submission compliance audit.

### TERRA implementation queue

- Implement approved, scoped cloud reliability fixes from the critical audit.
- Correct bounded-selection or persistence defects found by the agentic audit.
- Keep product copy and evidence synchronized after implementation is stable.

### LUNA mechanical queue

- Run tests, evaluation, secret scan, diff/XML checks, and stale-claim searches.
- Regenerate deterministic reports after the final code tree stabilizes.
- Verify exact counts, links, placeholders, and cross-document consistency.

Repository inventory, repeated test execution, report regeneration, simple text
consistency, and mechanical deployment checks must not consume SOL work unless a
failure reveals ambiguity, regression risk, or a cross-system decision.

## Remaining hard gates

1. All local tests, evaluation invariants, secret scan, document consistency, and
   submission audit are green on the final tree.
2. The final tree is published to `rarescos-pixel/places-again`.
3. One owner-authenticated guided deployment creates the real Google Cloud stack.
4. Cloud E2E proves real Pub/Sub delivery, Gemini/ADK selection, Firestore version
   increment, replay without duplicate effects, impossible/adversarial fail-closed,
   authenticated push, and zero sent messages.
5. Capture a public <=4-minute English video from the verified cloud build.
6. Complete final rule/compliance audit, submit, then tag and freeze the exact
   judged commit.

## Known constraints

- This execution environment has no authenticated Google Cloud control plane, so
  it cannot truthfully complete the cloud hard gate without one account-owner
  authentication/billing approval action.
- Real Gemini candidate behavior remains unproven until cloud E2E; deterministic
  and stubbed paths are not substitutes for that evidence.
- If an API request persists an event but exhausts bounded Pub/Sub publish retries,
  the client must retry the returned stable `event_id`; a separate durable
  transport dispatcher is intentionally not added before the deadline.
- The public contest profile exposes reset only for synthetic demo data. Reset is
  transactional, refuses active events, and preserves terminal evidence; a real
  operational deployment must leave this explicit demo flag disabled.
- The video, public article/social action, eligibility declaration, and final
  Devpost Submit inherently require the owner.
- **OWNER ELIGIBILITY CHECK REQUIRED BEFORE FINAL SUBMIT:** the entrant alone must
  review and attest every Section 3 eligibility condition and any applicable
  third-party policy. Development does not claim personal eligibility on the
  entrant's behalf.

## Next action

Apply only concrete audit fixes, run the full local gate, publish the verified
tree, then give the owner one guided-deploy link rather than terminal commands.

## Acceptance invariants

- 0 unsafe commits; 0 unresolved auto-commits.
- 0 Gemini-invented-plan commits; 0 hard-constraint overrides.
- 100% committed candidates deterministically re-verified.
- 100% stale-plan rejection; replay creates 0 duplicate business effects.
- Impossible or ambiguous recovery becomes `human_required`.
- Outbox is prepared, never sent.
- Both scenarios use the same candidate, selection, verification, and commit path.
