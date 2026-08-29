# Judge evidence map

Every scored claim below maps to inspectable code, a visible product state, and
the final automated video evidence map. The real Google Cloud E2E backend/agent hard gate passed
on 2026-08-29 in the owner-authenticated deployment, and independent anonymous
public-internet reachability plus full live E2E also passed from a GitHub-hosted
runner on 2026-08-29. The generated 117.33-second MP4 has been inspected and reconciled below; only the final public YouTube/Vimeo URL remains to be inserted.

Current verified hosted application:

`https://places-again-674409858210.europe-west1.run.app`

Independent public proof: GitHub Actions `Live Cloud E2E Proof` run
`33255155489`.

## Final automated video map

The inspected automated MP4 is **117.33 seconds**, 1920×1080, H.264/30 fps,
with English on-screen captions and no audio. Its authoritative evidence map is:

- **0:00–0:53** — one continuous, unedited public-Cloud Proof of Action: Opera
  autonomous recovery, replay exactly-once business effect, adversarial/impossible
  `human_required`, and Commercial Film/Broadcast using the same engine;
- **0:53–1:05** — judge-accessible hosted Cloud Run application + visible `.run.app` URL;
- **1:05–1:16** — `/api/capabilities`: Cloud Run, Pub/Sub, private worker, Google ADK,
  Gemini 3.5 on Vertex AI, Firestore;
- **1:16–1:26** — independent external GitHub-hosted live Cloud E2E evidence;
- **1:26–1:37** — committed architecture;
- **1:37–1:47** — public Quality Gate / reproducible safety evidence;
- **1:47–1:57** — recovered hosted application + closing decision/safety line.

The MP4 is already generated and inspected. The mandatory **public YouTube/Vimeo
URL is not claimed until that upload actually exists**.

## 1. Innovation & Operational Utility — 40%

| Claim | Exact evidence | Visible proof | Video |
|---|---|---|---|
| The failure is understood immediately | README opening; `docs/submission.md` | One absence expands into the cascade | 0:00–0:53 |
| Personal BYOF friction | Firsthand opera origin; all actual identities/data synthetic | Origin line + Opera scenario | 0:00–0:53 |
| Human and operational stakes are measured | `_plan_metrics` in `places_again/engine.py` | 3 activities, 6 people, 3 resources, 12 hours at risk | 0:00–0:53 |
| One event completes without step-by-step guidance | `POST /api/events` → Pub/Sub → private worker | One click, event ID, autonomous timeline | 0:00–0:53 |
| More than one safe recovery genuinely exists | `build_recovery_candidates`; `test_multiple_safe_candidates_expose_a_real_operational_tradeoff` | Multiple safe candidate cards | 0:00–0:53 |
| Gemini makes a consequential bounded choice | Four-tool ADK agent; `candidate_id` + reason-code contract | Actual selected candidate ID + validated reasons from the captured run | 0:00–0:53 |
| The operation actually changes | `commit_event_candidate`; Firestore transaction; cloud E2E assertions | State `v1 → v2` | 0:00–0:53 |
| Opera baseline result | `op_baseline`; report metrics | 3/3, 12 hours restored, 0 unaffected moved | 0:00–0:53 |
| Portability is proved, not promised | `commercial_shoot.json`; same candidate generator and workflow tests | Same UI/mechanism, different domain | 0:00–0:53 |
| Commercial baseline result | `film_baseline` | 4/4 and 26 hours restored | 0:00–0:53 |
| Failure is intentional and safe | `human_required` paths and adversarial cases | No mutation, no outbox, no send | 0:00–0:53 |

## 2. Architectural Discipline & Tech Stack — 30%

| Claim | Exact evidence | Visible/cloud proof | Video |
|---|---|---|---|
| Required Google stack is real | `google-adk`; model config; Cloud Run, Pub/Sub, Firestore code | Passed owner-authenticated + independent public cloud E2E | 1:05–1:47 |
| Event-driven, not a synchronous chatbot | `places_again/pubsub.py`; API returns `202 + event_id`; private push endpoint | Event ID and background timeline | 0:00–0:53 |
| Authenticated private delivery | OIDC push SA and private internal-ingress worker in `deploy.sh` | Passed Pub/Sub OIDC cloud E2E | 1:05–1:47 |
| Hard constraints define the safe space | `build_recovery_candidates`, `validate_schedule` | Every candidate marked hard-safe | 0:00–0:53 |
| Soft priorities belong to Gemini | scenario `soft_priorities`; structured selection tools | Candidate ID and validated operational reasons | 0:00–0:53 |
| Gemini cannot invent or edit a plan | `commit_event_candidate`; invalid-ID evaluation | Invented ID produces `human_required` | 0:00–0:53 |
| Every committed candidate is reverified | `reverify_recovery_plan`; transaction path | “Deterministic re-verification: PASS” | 0:00–0:53 |
| Firestore-cloud exactly-once business effect over at-least-once delivery | event ledger + Firestore transaction; replay assertions | Passed real replay proof: version/outbox unchanged | 0:00–0:53 |
| Crash and concurrency recovery | fault injection and concurrent tests | Evaluation report | 0:00–0:53 |
| Prompt injection cannot change authority | strict schema, opaque ID, tool allowlist, adversarial fixture | `human_required`/normal policy, zero sent | 0:00–0:53 |
| No irreversible send authority | no send tool; deterministic `prepared_not_sent` outbox | prepared count, sent = 0 | 0:00–0:53 |
| Least privilege without keys | separate builder/API/worker/push identities | Deployment report | 1:05–1:47 |
| Threat and failure analysis | `SECURITY.md`; `FAILURE_MODES.md` | Repository | judge review |
| Secret hygiene | `scripts/secret_scan.py --history`; `reports/secret-scan.json`; public Quality Gate | 0 findings on green submitted-commit CI | judge review |

## 3. Demo & Production Readiness — 30%

| Claim | Exact evidence | Visible/deployment proof | Video |
|---|---|---|---|
| Memorable visible transformation | cascade UI in `static/index.html` | AT RISK → RECOVERED | 0:00–2:00 |
| Decision evidence is inspectable | `candidate_summaries`, selected ID, reasons, proof in event ledger | candidate strip + decision panel | 0:00–0:53 |
| Responsive finalist control room | `static/index.html`; integration test | Independently reachable hosted Cloud Run UI | 0:00–1:57 |
| Public reproducible quality gate | `.github/workflows/quality-gate.yml` | GitHub Actions: tests, evaluation, core verification, secret/history scan, syntax/parse checks; JSON evidence artifact | repository review |
| Robust guided deploy | `enable_google_apis.sh`; `scripts/deploy_auto.sh`; retry tests | Owner-authenticated deployment succeeded after bypassing fragile hosted preflight | deployment evidence |
| Real cloud E2E, replay, and failure | `scripts/cloud_e2e_test.py`; `reports/cloud-e2e-verified-20260829.md` | Owner-authenticated `FINAL_STATUS=SUCCESS` + independent public E2E `passed: true` | 0:00–1:47 |
| Independent external reachability | `.github/workflows/live-cloud-e2e-proof.yml` | PASSED: public `/api/capabilities` + full live E2E from GitHub-hosted runner | production-readiness gate |
| Reproducible local evaluation | 52 labeled deterministic/fake-selection cases across both domains; not a Gemini invocation | `reports/evaluation-report.json` | 1:05–1:47 |
| Acceptance invariants pass | 0 unsafe/unresolved/duplicate/invented/override; 100% reverified | evaluation summary | 1:05–1:47 |
| Judge testing path | `docs/judge-testing-instructions.md` | Hosted Cloud Run path + local reproducible fallback | judge review |
| Observable without hidden reasoning | event/model/tool/candidate/proof/version/retry/outbox fields | action trace and audit | 0:00–0:53 |
| Honest evidence boundary | README and submission disclosure | synthetic-data label + exact cloud evidence | judge review |
| Public video ≤ 4:00 | automated submission-video artifact, 117.33 s | MP4 verified locally; public YouTube/Vimeo URL still required | final artifact |

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

The current public service URL is:

`https://places-again-674409858210.europe-west1.run.app`

The deployment proved:

- Cloud Run API → Pub/Sub.
- Authenticated Pub/Sub OIDC → private Cloud Run worker.
- Vertex AI Gemini 3.5 running through Google ADK.
- Bounded Gemini candidate selection followed by deterministic re-verification.
- Firestore state commit `v1 → v2` exactly once as a business effect.
- Replay without duplicate business effects.
- Impossible/adversarial incident → `human_required` with no unsafe mutation/send.
- Prepared outbox with messages sent = 0.

A concise committed checkpoint is available at
`reports/cloud-e2e-verified-20260829.md`.

## Anonymous public-internet reachability + live E2E — PASSED 2026-08-29

GitHub Actions `Live Cloud E2E Proof` run `33255155489` independently reached the
current public service from a GitHub-hosted runner.

The external `/api/capabilities` response identified:

- `Google Cloud Run` runtime;
- `Google Agent Development Kit`;
- `gemini-3.5-flash`;
- `Vertex AI`;
- `firestore` repository;
- `Google Pub/Sub` event transport;
- private worker configured;
- outbound delivery disabled / `prepared_not_sent` only.

The runner then executed the production E2E and finished with `passed: true`.
The captured run showed two hard-safe candidates, selected `candidate-a` with
validated reason codes `preserve_highest_priority_activity` and
`minimize_people_schedule_changes`, passed deterministic re-verification, moved
Firestore state from v1 to v2, recovered 3/3 activities and 12 person-hours,
moved zero unaffected activities, prepared 12 outbox items and sent zero
messages. Replay preserved v2 and the 12-item outbox. The adversarial unknown
person case ended in `human_required`.

Raw evidence artifact:
`live-cloud-e2e-374798636b7b907c7fb20ad4ced806b27a07eb55`, artifact ID `9715582052`.

## Bonus map

| Bonus | Evidence asset | Status |
|---|---|---|
| +0.2 public build content | https://github.com/rarescos-pixel/places-again/issues/3 | **Published** with required hackathon disclosure, live app, repository, and current 65/65 + 52/52 evidence |
| +0.2 social post | `docs/social-post.md` | Publish-ready with required hashtag; owner publication pending |
| +0.2 Gemma 4 additional-model bonus | draft PR #2 `bonus-gemma4-refresh` | CI green; real owner-authenticated Gemma call + README/demo evidence still required; do not merge yet |
| Further additional models, max +0.6 total | none | Intentionally deferred; no decorative model stuffing |

## Final sceptical-judge gate

- Is the submitted commit's public Quality Gate green and are its generated reports downloadable?
- Can the problem be repeated after ten seconds?
- Is the cascade visible before architecture is discussed?
- Does the live trace show more than one real safe candidate?
- Does Gemini choose a supplied ID for a validated operational reason?
- Does deterministic re-verification visibly precede commit?
- Does replay preserve the same version and outbox IDs?
- Does the impossible/adversarial case stop without side effects?
- Does the film scenario use the same code path rather than renamed slides?
- Are the Google Cloud deployment, Pub/Sub delivery, ADK/Gemini trace, and Firestore state impossible to mistake for a mock?
- Does every spoken number/model-selection claim match the submitted commit's generated evidence?
- Can a judge open the hosted UI anonymously without auth/404 friction?
