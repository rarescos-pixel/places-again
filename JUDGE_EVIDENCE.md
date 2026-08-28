# Judge evidence map

This file maps every scored claim to something a judge can inspect. “Planned
video” timestamps refer to `docs/demo-script.md` and must be updated to the final
public video URL before submission.

## 1. Innovation & Operational Utility — 40%

| Claim | Exact evidence | UI proof | Planned video |
|---|---|---|---|
| Solves the failure moment, not normal planning | README opening and `docs/submission.md` | Hero: “The plan breaks. The operation recovers.” | 0:00–0:25 |
| Personal BYOF friction | Opera scenario derives from entrant's firsthand rehearsal experience; all actual data is synthetic | Origin block | 0:25–0:42 |
| Completes a background workflow without step-by-step guidance | `POST /api/events` → Pub/Sub → private worker; `places_again/workflow.py` | One **Inject disruption event** button + state timeline | 0:42–1:35 |
| Produces a real state change | `apply_plan`; Firestore transaction; version `1 → 2` assertion in `scripts/cloud_e2e_test.py` | Before/after version proof | 1:15–1:35 |
| Measures operational value without invented dollars | `build_recovery_plan` metric calculation; report fixtures | Blast Radius vs Recovery Impact | 0:55–1:35 |
| Opera result | Evaluation `op_baseline`: 3/3 recovered, 12 person-hours restored, 0 unaffected moved | Opera scenario | 0:55–1:35 |
| Portability is demonstrated, not merely claimed | `data/scenarios/commercial_shoot.json`; `test_same_engine_recovers_commercial_shoot` | Scenario selector: same UI and engine | 2:38–2:58 |
| Commercial result | Evaluation `film_baseline`: 4/4 recovered, 26 person-hours restored, 0 unaffected moved | Commercial shoot scenario | 2:38–2:58 |
| Explicit failure boundary | `human_required` branch in `workflow.py`; impossible fixtures | Intentional red failure state | 2:15–2:38 |

## 2. Architectural Discipline & Tech Stack — 30%

| Claim | Exact evidence | UI / cloud proof | Planned video |
|---|---|---|---|
| Mandatory Google stack | `google-adk`, Gemini model config, Cloud Run deploy, Firestore and Pub/Sub clients | Stack badges + `/api/capabilities` | 0:42–0:55 |
| Event-driven, not a synchronous chatbot | `places_again/pubsub.py`; API returns `202 + event_id`; private push endpoint | Timeline and event ID | 0:55–1:15 |
| Authenticated Pub/Sub push | `deploy.sh`: private internal-ingress worker, OIDC push SA, `roles/run.invoker` | Google Cloud console / deployment report | 2:58–3:15 |
| Least privilege without keys | Separate builder/API/worker/push identities in `deploy.sh`; `SECURITY.md` | Deployment report | 2:58–3:15 |
| Probabilistic orchestration separated from safety | Three-tool allowlist in `agent.py`; deterministic `engine.py` | ADK action trace + Safety Gates | 1:35–2:00 |
| Strict input and prompt-injection boundary | `models.py`; agent sees opaque event ID; adversarial fixtures | Adversarial reason produces zero sends | 2:15–2:38 |
| Exactly-once business effects over at-least-once delivery | Event ledger + one Firestore transaction in `repository.py` and `workflow.py` | Replay proof: version/outbox unchanged | 2:00–2:15 |
| Crash and concurrency recovery | Fault injection and concurrent tests in `test_workflow.py` | Evaluation report | 2:00–2:15 |
| No irreversible send authority | No send tool; deterministic outbox IDs; `prepared_not_sent` | Prepared outbox, messages sent = 0 | 1:35–2:00 |
| Threat model and failure modes | `SECURITY.md`; `FAILURE_MODES.md` | Documentation | optional cutaway |
| Secret hygiene | `scripts/secret_scan.py --history`; `reports/secret-scan.json` | Report: 0 findings | optional cutaway |

## 3. Demo & Production Readiness — 30%

| Claim | Exact evidence | UI / deployment proof | Planned video |
|---|---|---|---|
| Finalist-level, responsive control room | `static/index.html`; homepage integration test | Live public Cloud Run URL | entire demo |
| Reproducible local setup | README one-command block | Repository | repository review |
| Cloud deploy is one command | `deploy.sh` | Deployment transcript | 2:58–3:15 |
| Real E2E, replay, and failure validation | `scripts/cloud_e2e_test.py` | JSON cloud evidence report | 1:00–2:38 |
| Strong evaluation corpus | 47 labeled cases, both domains | `reports/evaluation-report.json` | 3:15–3:28 |
| Acceptance targets all met | 0 unsafe/unresolved/duplicate; 100% stale and verification | Evaluation summary | 3:15–3:28 |
| Observable operations | Event/model/tool/plan/version/retry/outbox fields; token/latency if SDK exposes | Action trace and audit | 1:15–2:15 |
| Honest synthetic/real boundary | README and Devpost disclosure | Footnote and Devpost | closing |
| Public video ≤ 4:00 | `docs/demo-script.md` target 3:45 | YouTube/Vimeo URL — pending owner publication | final artifact |

## Cloud hard gate

The following claims remain **unverified until a real deployment report exists**:

- Pub/Sub reaches the private Cloud Run worker with OIDC;
- Vertex AI Gemini 3.5 runs through Google ADK;
- Firestore commits and replay behavior occur in Google Cloud;
- the public Cloud Run URL survives the complete E2E test.

`deploy.sh` is designed to create the infrastructure and run the proof, but code
presence is not cloud evidence. Submission freeze is blocked until
`runtime/cloud-e2e-evidence-*.json` exists and passes.

## Bonus map — after core cloud proof

| Bonus | Asset | Status |
|---|---|---|
| +0.2 public build content | `docs/build-article.md` | Draft; publication pending |
| +0.2 social post | `docs/social-post.md` | Draft; publication pending |
| +0.2 per additional eligible Google AI model, max +0.6 | None added | Deliberately deferred; no decorative model integrations |

## Sceptical judge checks before freeze

- Does the video visibly show the `run.app` URL and Google Cloud evidence?
- Does the user click only once before the autonomous workflow completes?
- Does the trace show real ADK tool calls rather than a precomputed animation?
- Does replay leave version and outbox IDs unchanged?
- Does the impossible/adversarial case visibly stop without commit?
- Does the commercial scenario actually use the same engine?
- Are every metric and claim reproducible from the repository?
- Are no future industries described as implemented?
