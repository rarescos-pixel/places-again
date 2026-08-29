# Places, Again — canonical final submission / winner gate

This file is the single final checklist. Do not replace it with a new planning document.
A box becomes green only with inspectable evidence.

Final upload/copy-paste packet: `docs/final-upload-copy.md`.

## 1. Stage One — mandatory eligibility / submission viability

- [x] Project created during the official submission period.
- [x] Primary track: **Taskmaster**.
- [x] Gemini 3.5+ used through Vertex AI.
- [x] Google ADK used as the agent framework.
- [x] Google Cloud infrastructure used: Cloud Run + Pub/Sub + Firestore.
- [x] Public GitHub repository with reproducible setup instructions.
- [x] Clean architecture diagram.
- [x] English product / submission materials.
- [x] Real owner-authenticated Google Cloud backend/agent E2E passed.
- [x] Independent anonymous GitHub-hosted E2E reached the current public Cloud Run URL and completed the live workflow.
- [ ] Public YouTube/Vimeo demo is <= 4:00 and English / English-subtitled.
- [ ] Final entrant eligibility attestation completed honestly.

Current verified hosted application:

`https://places-again-674409858210.europe-west1.run.app`

Independent public proof: GitHub Actions `Live Cloud E2E Proof` run `33254443473`, completed successfully on 2026-08-29.

## 2. Innovation & Operational Utility — 40%

Internal target: 5/5.

- [x] Real specific friction learned firsthand.
- [x] Problem understandable in <10 seconds.
- [x] One incident expands into a measurable cascade.
- [x] Agent executes a multi-step background workflow, not a chat loop.
- [x] User submits one incident and does not choose tools / approve intermediate steps.
- [x] System mutates real application state when safe.
- [x] Gemini makes a meaningful bounded operational decision among multiple hard-safe strategies.
- [x] Hard safety remains deterministic.
- [x] Impossible/ambiguous recovery escalates to `human_required` with no unsafe commit.
- [x] Second implemented domain proves the mechanism is not an opera-specific conditional.
- [x] No invented financial ROI or unsupported industry claims.

Winner memorability test:

> A judge should be able to retell the project as: “one person disappears and the agent safely rebuilds the broken operation.”

## 3. Architectural Discipline & Proof of Action — 30%

Internal target: 5/5.

- [x] Cloud Run API and private worker are decoupled.
- [x] Pub/Sub delivers only opaque event IDs using authenticated OIDC.
- [x] Firestore transaction owns event ledger + version + selected candidate + audit + outbox.
- [x] At-least-once delivery is handled as exactly-once **business effect**, not falsely described as exactly-once delivery.
- [x] Stable event IDs prevent duplicate state/outbox effects.
- [x] Current-state / stale-version protection exists.
- [x] Gemini has no direct DB mutation, shell, arbitrary HTTP, credentials, or send tool.
- [x] Deterministic re-verification occurs after Gemini selection and before commit.
- [x] Replay, concurrency, crashes, malformed input, prompt injection, model failure, and impossible recovery are tested.
- [x] Secret + git-history scanning is public in CI.
- [x] Public GitHub Quality Gate is green on the commit that established the verified public endpoint.
- [x] Owner-authenticated real Google Cloud E2E passed with ADK/Gemini/PubSub/Firestore.
- [x] Independent anonymous external E2E reached the public front door and completed the workflow.

External proof captured on 2026-08-29:

- `/api/capabilities` returned Cloud Run + Google ADK + Gemini 3.5 + Vertex AI + Firestore + Pub/Sub;
- two hard-safe candidates were observed;
- Gemini selected an existing candidate ID with validated reason codes;
- deterministic re-verification passed;
- version changed `v1 → v2`;
- replay preserved version/outbox;
- adversarial unknown-person input ended at `human_required`;
- raw JSON evidence was uploaded as a GitHub Actions artifact.

## 4. Demo & Production Readiness — 30%

Internal target: 5/5.

Preferred path is now available: record from the exact independently reachable Cloud Run build.

The final <=4 minute video must visibly prove:

- [ ] 08:05 incident + immediate 3 activities / 6 people / 3 resources / 12 person-hours at risk.
- [ ] One action starts the main workflow; no step-by-step guidance until terminal state.
- [ ] The main proof-of-action segment is one continuous unedited take from trigger to terminal state.
- [ ] Multiple safe candidates are visible.
- [ ] Actual Gemini-selected candidate ID and validated reason codes are visible.
- [ ] Deterministic re-verification = PASS is visible.
- [ ] `v1 → v2` exactly once is visible.
- [ ] 3/3 recovered, 12 person-hours restored, 0 unaffected moved, 0 unsafe actions.
- [ ] Outbox prepared and messages sent = 0.
- [ ] Replay leaves version/outbox unchanged.
- [ ] Impossible/adversarial event becomes `human_required` with no unsafe effect.
- [ ] Commercial film/broadcast fixture visibly uses the same mechanism.
- [ ] Google Cloud execution evidence is visible: `.run.app` deployment/Cloud Run, worker, Pub/Sub, Firestore, Vertex AI/ADK/Gemini.
- [ ] Architecture diagram appears briefly.
- [ ] Spoken claims match the captured run exactly; candidate ID/reasons are not pre-scripted.
- [x] Anonymous judge access to the hosted UI works with no 404/auth friction in independent verification.

## 5. Winner-pattern benchmark from prior Google/Devpost winners

This is an empirical benchmark, not a secret judging rule.

- [x] Instantly understandable real problem.
- [x] Human/economic stakes visible before architecture.
- [x] Authentic personal origin rather than invented enterprise theater.
- [x] AI performs something operationally useful rather than generating text only.
- [x] Clear “newly practical with AI” capability: contextual choice within a safe action space.
- [x] Visible before → after transformation.
- [x] Technical depth exists underneath the product story.
- [x] Human gate is presented as responsible authority, not failure of autonomy.
- [x] Same core behavior shown in a second domain.
- [ ] Final video polish proves the above in under four minutes.

## 6. Bonus score — Stage Three

Low-risk bonuses do **not** require a live-app URL.

- [x] Build article draft exists and contains the required hackathon-purpose disclosure.
- [ ] Publish build article publicly on an accepted public platform. **+0.2**
- [x] Social post draft exists with `#AllThingsAgenticHackathon`.
- [ ] Publish social post publicly. **+0.2**

Additional-model bonus:

- [x] Gemma 4 experiment is isolated from `main` and outside the safety/mutation path.
- [x] Refreshed Gemma bonus branch / PR #2 exists and CI is green.
- [ ] Real owner-authenticated Gemma call succeeds with evidence.
- [ ] Gemma integration is useful, documented clearly in README, and visible in the final demo.
- [ ] Only then merge and claim **+0.2**.

Do not pursue extra models if they threaten the verified Taskmaster core or the <=4 minute demo.
Official maximum for additional-model bonus: +0.6 total.

## 7. Honest evidence boundary

- [x] All people, schedules, resources, incidents, and scenario metrics are labeled synthetic.
- [x] Cloud E2E claims are based on actual execution evidence.
- [x] Anonymous public-internet access is independently verified.
- [x] Local evaluation is not described as a real Gemini invocation.
- [x] No hidden chain-of-thought is requested or stored.
- [x] No unimplemented industry support is claimed.
- [x] No real outbound communication is claimed.
- [x] Data sources + pre-existing-work disclosure + findings/learnings are explicit in the Devpost draft.

## 8. Entrant eligibility — separate blocking gate

The official rules explicitly say individuals or organizations employed by a government agency are ineligible, and also reserve discretion over real/apparent conflicts of interest. This is separate from project quality.

- [ ] Entrant reviews the exact official eligibility language before final Submit.
- [ ] No employment/status information is hidden or misrepresented.
- [ ] Final eligibility declaration is made by the entrant, not inferred by the software project.

## 9. Submission and judging freeze

Before pressing Submit — mandatory / evidence critical:

- [ ] Final Quality Gate green on exact submitted commit.
- [ ] Public video URL inserted and video <=4:00.
- [ ] Hosted application URL still opens successfully from a logged-out/anonymous browser.
- [ ] Devpost text contains no unresolved placeholders for claims actually submitted.
- [ ] `JUDGE_EVIDENCE.md` has final video timestamps.
- [ ] Entrant eligibility review completed.
- [ ] Exact submitted commit tagged/frozen.

Already closed winner-readiness gates:

- [x] Anonymous public front door green.
- [x] Independent external E2E green.

Bonus items if claimed:

- [ ] Public article URL inserted.
- [ ] Social URL inserted.
- [ ] Additional-model evidence inserted only if actually validated/merged and shown in README/demo.

After Submit until winners are announced:

- [ ] Do not change submitted repository, demo video, live app, or submission assets.
- [ ] Any continued development happens only on a separate fork/branch.

## Definition of done

The project is ready only when it is:

**hard to score below 5, hard to doubt technically, easy to understand, and hard to forget.**
