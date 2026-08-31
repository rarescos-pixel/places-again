# Places, Again — final judge evidence map

This file is the canonical judge-facing evidence map for the final submission package. Older recording plans and automated-video artifacts are historical working material and are not the submitted master.

## Current verified state

- Hosted application: `https://places-again-674409858210.europe-west1.run.app`
- Final validated Cloud Run revision: `places-again-00003-jz8`
- Google Agent Framework: Google Agent Development Kit (ADK)
- Model: `gemini-3.5-flash`
- Model backend: Vertex AI
- Event transport: Google Pub/Sub
- Durable repository: Firestore
- Final repository baseline: **67/67 automated tests**, **52/52 labeled evaluation cases**
- Current `main` Quality Gate: green
- Final post-P0 live verification: `reports/cloud-e2e-verified-20260830.md`

## Final submission video

Approved master: **v8**

- duration: **159.680 seconds (2:39.680)**;
- resolution: **1920×1080**;
- H.264 video + AAC stereo audio;
- English narration / English on-screen text;
- public YouTube/Vimeo URL: **pending publication**;
- the live agent-run interval was mechanically checked for hard visual cuts at multiple scene-change thresholds and none were detected;
- direct audio audit with two speech-recognition models found the last narration ending at approximately **2:08.84**; the remaining close is instrumental/operatic audio only.

A historical evidence frame in the video shows an earlier **65-test** checkpoint. That was a real passing checkpoint. After the final Firestore persistence P0 fix, the submitted repository baseline is **67/67 automated tests** and **52/52 labeled evaluation cases**.

### Final video map

- **0:00–0:24 — problem / stakes:** one principal becomes unavailable; 3 activities, 6 people, 3 resources and 12 person-hours become at risk; the manual alternative is calls, spreadsheets and guesswork.
- **0:24–0:29 — product handoff:** the real hosted Places, Again UI appears and the narration states that the execution from there is live and continuous.
- **0:29–1:30 — continuous live Proof of Action:** incident accepted; deterministic hard-safe candidates are built; Gemini chooses among safe alternatives; deterministic current-state re-verification precedes commit. This interval was mechanically checked for hard cuts and none were detected.
- **1:30–1:45 — visible recovered state:** atomic recovery / replay semantics / prepared-not-sent boundary; product view shows recovered metrics.
- **1:45–2:02 — measurable result and stack evidence:** 3/3 activities recovered, 12 person-hours restored, zero unaffected movement and zero unsafe actions; capability evidence identifies Google Cloud Run, Pub/Sub, Google ADK, Gemini 3.5 / Vertex AI and Firestore.
- **2:02–2:24 — independent proof + architecture:** GitHub-hosted live-cloud evidence and the Google-native execution path / Quality Gate are shown.
- **2:24–2:33 — product close:** closing product message remains on screen over non-narrated music.
- **2:33–2:39 — human payoff:** the operation is visibly functioning again in the rehearsal/performance environment.

## 1. Innovation & Operational Utility — 40%

| Claim | Inspectable evidence | Visible proof |
|---|---|---|
| One real operational failure expands into a cascade | README baseline; synthetic `opera` fixture | opening 0:00–0:24 |
| One event completes a multi-step workflow without step-by-step guidance | `POST /api/events` → Pub/Sub → private worker | 0:24–1:30 |
| More than one hard-safe recovery genuinely exists | candidate generator + regression tests | live proof shows multiple safe candidates |
| Gemini is consequential but bounded | ADK four-tool allowlist; candidate-ID selection contract | Gemini selection in live proof |
| The choice has a real soft trade-off | README: Candidate A = 0 critical moved / 3 people / 270 min; Candidate B = 1 critical moved / 7 people / 240 min | selection result + README explanation |
| The operation actually changes | Firestore transaction + version ledger | `v1 → v2`, recovered state |
| Result is measurable | baseline metrics | 3/3, 12 person-hours restored, zero unsafe |
| Portability is executed, not merely claimed | `commercial_shoot` fixture uses same engine | second domain referenced in demo / repo |
| Impossible or invalid recovery fails closed | `human_required` paths | adversarial evidence + live report |

## 2. Architectural Discipline & Tech Stack — 30%

| Claim | Evidence |
|---|---|
| Required Google stack is real | Cloud Run + Pub/Sub/OIDC + private worker + Google ADK + Gemini 3.5 on Vertex AI + Firestore |
| Public API and private worker are separated | `deploy.sh`, service identities and ingress assertions |
| LLM does not own hard safety | deterministic candidate engine and hard-constraint validator |
| Gemini cannot invent/edit a plan | supplied candidate-ID contract; unknown ID fails closed |
| Selected state is independently reverified | deterministic re-verification before Firestore commit |
| At-least-once transport does not create duplicate business effects | stable event ledger + Firestore transaction + replay proof |
| Stale / malformed / prompt-injection / impossible cases are covered | tests, evaluation, `FAILURE_MODES.md`, `SECURITY.md` |
| Outbound authority is intentionally absent | no send tool; `prepared_not_sent`; messages sent = 0 |
| Firestore persistence remains bounded after repeated demos | final P0 compact-trace fix + regression coverage |

Final post-P0 production evidence is recorded in `reports/cloud-e2e-verified-20260830.md`: the exact UI-shaped payload returned HTTP 202, reached `completed`, used two hard-safe candidates, selected `candidate-a`, passed deterministic re-verification, moved Firestore `v1 → v2`, recovered 3/3 activities and 12 person-hours, replayed without a second business effect, and sent zero messages. The adversarial unknown-person incident ended at `human_required` with no mutation/send.

## 3. Demo & Production Readiness — 30%

- Public Cloud Run URL opens anonymously.
- Judge testing path is documented in `docs/judge-testing-instructions.md`.
- One-click synthetic demo is reset to clean baseline state after verification.
- Live public event path has been retested after the Firestore P0 fix.
- Final master is <4 minutes and includes problem, value proposition, live execution, architecture, Cloud proof, failure handling and measurable result.
- Repository Quality Gate covers tests, 52-case evaluation, core invariants, full-history secret scan, Python/shell syntax and JSON/SVG parse checks.
- All people, schedules, incidents and scenario metrics are explicitly synthetic.

## Fatal question: Why Gemini?

The deterministic engine defines what is allowed; Gemini chooses which already-safe strategy best fits ranked soft operational priorities. In the opera baseline, Candidate B shifts 30 fewer minutes but moves the highest-priority call and changes more people's schedules. Gemini returns only a supplied candidate ID and bounded reason codes. Deterministic code then rebuilds and re-verifies that exact candidate before Firestore can commit.

> **Gemini decides what makes operational sense. Deterministic code proves what is safe.**

## Bonus evidence

- Public build content: `https://github.com/rarescos-pixel/places-again/issues/3` — published with the required hackathon disclosure. Final numeric update to 67/67 is part of the submission-reconciliation step.
- Social bonus: `docs/social-post.md` — publication URL pending.
- Additional-model bonus: **not claimed**. The final base submission intentionally avoids decorative model stuffing.

## Final stop rule

Before pressing Submit:

1. public YouTube/Vimeo URL must point to exactly the approved v8 master;
2. social URL must exist before claiming the social bonus;
3. all Devpost fields and URLs must be checked for placeholders and public accessibility;
4. the final repository Quality Gate must be green;
5. the hosted application must remain anonymously reachable and at clean synthetic baseline;
6. after submission, freeze repository, video and live app through judging.
