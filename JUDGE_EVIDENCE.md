# Judge evidence map

Every scored claim below maps to inspectable code, a visible product state, and
a planned video moment. The real Google Cloud E2E backend/agent hard gate passed
on 2026-08-29 in the owner-authenticated deployment. Independent public-internet
reachability is a separate final gate and is not claimed as passed until the
GitHub-hosted live proof reaches the service successfully. Final video URLs and
exact video timestamps still need reconciliation with the submitted build.

## 1. Innovation & Operational Utility — 40%

| Claim | Exact evidence | Visible proof | Video |
|---|---|---|---|
| The failure is understood immediately | README opening; `docs/submission.md` | One absence expands into the cascade | 0:00–0:20 |
| Personal BYOF friction | Firsthand opera origin; all actual identities/data synthetic | Origin line + Opera scenario | 0:00–0:20 |
| Human and operational stakes are measured | `_plan_metrics` in `places_again/engine.py` | 3 activities, 6 people, 3 resources, 12 hours at risk | 0:00–1:05 |
| One event completes without step-by-step guidance | `POST /api/events` → Pub/Sub → private worker | One click, event ID, autonomous timeline | 0:40–1:45 |
| More than one safe recovery genuinely exists | `build_recovery_candidates`; `test_multiple_safe_candidates_expose_a_real_operational_tradeoff` | Multiple safe candidate cards | 1:00–1:20 |
| Gemini makes a consequential bounded choice | Four-tool ADK agent; `candidate_id` + reason-code contract | Actual selected candidate ID + validated reasons from the captured run | 1:15–1:30 |
| The operation actually changes | `commit_event_candidate`; Firestore transaction; cloud E2E assertions | State `v1 → v2` | 1:30–2:00 |
| Opera baseline result | `op_baseline`; report metrics | 3/3, 12 hours restored, 0 unaffected moved | 1:45–2:20 |
| Portability is proved, not promised | `commercial_shoot.json`; same candidate generator and workflow tests | Same UI/mechanism, different domain | 2:45–3:10 |
| Commercial baseline result | `film_baseline` | 4/4 and 26 hours restored | 2:45–3:10 |
| Failure is intentional and safe | `human_required` paths and adversarial cases | No mutation, no outbox, no send | 2:20–2:45 |

## 2. Architectural Discipline & Tech Stack — 30%

| Claim | Exact evidence | Visible/cloud proof | Video |
|---|---|---|---|
| Required Google stack is real | `google-adk`; model config; Cloud Run, Pub/Sub, Firestore code | Passed real owner-authenticated cloud E2E + Cloud services + trace | 3:10–3:30 |
| Event-driven, not a synchronous chatbot | `places_again/pubsub.py`; API returns `202 + event_id`; private push endpoint | Event ID and background timeline | 0:40–1:45 |
| Authenticated private delivery | OIDC push SA and private internal-ingress worker in `deploy.sh` | Passed Pub/Sub OIDC cloud E2E | 3:10–3:30 |
| Hard constraints define the safe space | `build_recovery_candidates`, `validate_schedule` | Every candidate marked hard-safe | 1:00–1:20 |
| Soft priorities belong to Gemini | scenario `soft_priorities`; structured selection tools | Candidate ID and validated operational reasons | 1:15–1:30 |
| Gemini cannot invent or edit a plan | `commit_event_candidate`; invalid-ID evaluation | Invented ID produces `human_required` | 2:20–2:45 |
| Every committed candidate is reverified | `reverify_recovery_plan`; transaction path | “Deterministic re-verification: PASS” | 1:25–1:40 |
| Firestore-cloud exactly-once business effect over at-least-once delivery | event ledger + Firestore transaction; replay assertions | Passed real replay proof: version/outbox unchanged | 2:20–2:35 |
| Crash and concurrency recovery | fault injection and concurrent tests | Evaluation report | 2:20–2:45 |
| Prompt injection cannot change authority | strict schema, opaque ID, tool allowlist, adversarial fixture | `human_required`/normal policy, zero sent | 2:35–2:45 |
| No irreversible send authority | no send tool; deterministic `prepared_not_sent` outbox | prepared count, sent = 0 | 1:45–2:20 |
| Least privilege without keys | separate builder/API/worker/push identities | Deployment report | 3:10–3:30 |
| Threat and failure analysis | `SECURITY.md`; `FAILURE_MODES.md` | Repository | judge review |
| Secret hygiene | `scripts/secret_scan.py --history`; `reports/secret-scan.json`; public Quality Gate | 0 findings on green submitted-commit CI | judge review |

## 3. Demo & Production Readiness — 30%

| Claim | Exact evidence | Visible/deployment proof | Video |
|---|---|---|---|
| Memorable visible transformation | cascade UI in `static/index.html` | AT RISK → RECOVERED | 0:00–2:00 |
| Decision evidence is inspectable | `candidate_summaries`, selected ID, reasons, proof in event ledger | candidate strip + decision panel | 1:00–1:40 |
| Responsive finalist control room | `static/index.html`; integration test | Cloud Run UI — final anonymous external reachability gate must pass before video/submission | entire demo |
| Public reproducible quality gate | `.github/workflows/quality-gate.yml` | GitHub Actions: tests, evaluation, core verification, secret/history scan, syntax/parse checks; JSON evidence artifact | repository review |
| Robust guided deploy | `enable_google_apis.sh`; `scripts/deploy_auto.sh`; retry tests | Owner-authenticated deployment succeeded after bypassing fragile hosted preflight | deployment evidence |
| Real cloud E2E, replay, and failure | `scripts/cloud_e2e_test.py`; `reports/cloud-e2e-verified-20260829.md` | `FINAL_STATUS=SUCCESS`; generated cloud evidence JSON | 0:40–3:30 |
| Independent external reachability | `.github/workflows/live-cloud-e2e-proof.yml`; `scripts/diagnose_public_404.sh` | PENDING: external runner currently receives 404; must be green before final submission | final gate |
| Reproducible local evaluation | 52 labeled deterministic/fake-selection cases across both domains; not a Gemini invocation | `reports/evaluation-report.json` | 3:10–3:30 |
| Acceptance invariants pass | 0 unsafe/unresolved/duplicate/invented/override; 100% reverified | evaluation summary | 3:10–3:30 |
| Observable without hidden reasoning | event/model/tool/candidate/proof/version/retry/outbox fields | action trace and audit | 1:00–2:20 |
| Honest evidence boundary | README and submission disclosure | synthetic-data label + explicit reachability gate | judge review |
| Public video ≤ 4:00 | `docs/demo-script.md`, target 3:50 | public YouTube/Vimeo | final artifact |

## Fatal question: Why Gemini?

| Sceptical question | Demonstrable answer |
|---|---|
| If Gemini is removed, is this the same product? | No. Deterministic code still defines safety, but it no longer makes a context-sensitive choice between safe operational strategies. |
| Is Gemini only calling an algorithm? | No. The engine returns a bounded, heuristically generated non-dominated candidate set. Gemini selects one actual candidate using domain soft priorities and returns auditable reason codes. |
| Can Gemini bypass safety? | No. It cannot edit plans, and its ID is checked for set membership before current-state deterministic re-verification. |
| Is the choice fake? | No. Opera trades critical-call preservation against total shifted minutes; film trades single-cover continuity against balanced cover workload. Tests assert both. |

## Public quality gate

The repository has a GitHub Actions `Quality Gate` on every push to `main` and on
pull requests. The submitted commit must show this workflow green. It independently
runs the automated tests, the labeled evaluation, `verify_core.py`, full-history
secret scanning, Python and shell syntax checks, and JSON/SVG parse checks. A
successful run publishes the generated JSON reports as a downloadable Actions
artifact.

## Google Cloud backend/agent hard gate — PASSED 2026-08-29

The owner-authenticated Google Cloud deployment completed with
`FINAL_STATUS=SUCCESS`.

Deployed service URL reported by Cloud Run:

`https://places-again-inb6leu4ca-ew.a.run.app`

The deployment reported successful proof for:

- Cloud Run API → Pub/Sub.
- Authenticated Pub/Sub OIDC → private Cloud Run worker.
- Vertex AI Gemini 3.5 running through Google ADK.
- Bounded Gemini candidate selection followed by deterministic re-verification.
- Firestore state commit `v1 → v2` exactly once.
- Replay without duplicate business effects.
- Impossible/adversarial incident → `human_required` with no unsafe mutation/send.
- Prepared outbox with messages sent = 0.

The deployment generated a raw `runtime/cloud-e2e-evidence-*.json` report in the
owner's Cloud Shell environment. A concise committed checkpoint is available at
`reports/cloud-e2e-verified-20260829.md`. The raw JSON should be preserved as the
authoritative detailed artifact during final evidence reconciliation.

### Separate public-internet reachability gate — OPEN

Cloud Shell later confirmed `/api/capabilities` with HTTP 200 after setting the
Cloud Run event API to ingress `all`, enabling the default `run.app` URL, and
disabling the Cloud Run Invoker IAM check. However, independent GitHub-hosted
runners still received HTTP 404 from both the hash-form and deterministic-form
Cloud Run URLs.

This means the backend/agent proof above remains valid, but the project is **not
submission-ready as a public live application yet**. Do not record the final
video or claim public internet accessibility until `.github/workflows/live-cloud-e2e-proof.yml`
can reach `/api/capabilities` and complete the real workflow externally.

A Quality-Gate-verified read-only diagnostic is committed at
`scripts/diagnose_public_404.sh` with a one-click tutorial in
`docs/public-404-diagnostic.md`. It reads effective Cloud Run configuration and
recent `run.googleapis.com/HttpIngress` audit evidence without mutating the
service.

## Bonus map — only after the public gate closes

| Bonus | Evidence asset | Status |
|---|---|---|
| +0.2 public build content | `docs/build-article.md` | Draft gated on externally verified live URL; owner publication pending |
| +0.2 social post | `docs/social-post.md` | Draft gated on externally verified live URL; owner publication pending |
| +0.2 Gemma 4 additional-model bonus | draft PR #2 `bonus-gemma4-refresh` | CI green; real owner-authenticated Gemma call + README/demo evidence still required; do not merge yet |
| Further additional models, max +0.6 total | none | Intentionally deferred; no decorative model stuffing |

## Final sceptical-judge gate

- Is the submitted commit's public Quality Gate green and are its generated reports downloadable?
- Does an independent external runner reach the live Cloud Run UI/API without authentication or 404?
- Can the problem be repeated after ten seconds?
- Is the cascade visible before architecture is discussed?
- Does the live trace show more than one real safe candidate?
- Does Gemini choose a supplied ID for a validated operational reason?
- Does deterministic re-verification visibly precede commit?
- Does replay preserve the same version and outbox IDs?
- Does the impossible/adversarial case stop without side effects?
- Does the film scenario use the same code path rather than renamed slides?
- Are the Cloud Run URL, Pub/Sub delivery, ADK/Gemini trace, and Firestore state impossible to mistake for a mock?
- Does every spoken number/model-selection claim match the submitted commit's generated evidence?
