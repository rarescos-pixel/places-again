# Places, Again — final recording runbook

## Recording strategy

Record from the exact independently reachable Cloud Run build:

https://places-again-674409858210.europe-west1.run.app

Independent anonymous public reachability and full live Cloud E2E passed on 2026-08-29 in GitHub Actions `Live Cloud E2E Proof` run `33254443473`.

Verified Google Cloud project:

`project-2ee12060-728f-434f-9ad`

The API deployment has `PLACES_AGAIN_SYNTHETIC_DEMO_MODE=true`, so the synthetic scenario can be reset for clean recording attempts without redeploying infrastructure.

Do not rerun `deploy.sh` just to reset the demo. The backend deployment and public production path are already verified.

## Before recording

1. Open the verified hosted URL above in a clean browser tab.
2. Confirm the page loads without authentication or 404 friction.
3. Close personal tabs/notifications and hide any account-sensitive UI.
4. Confirm **Opera Production** is selected.
5. Reset the synthetic scenario from the demo UI if the baseline is not clean.
6. Confirm the page shows the pre-incident state before recording.
7. Open all Google Cloud evidence tabs listed below before starting the take.
8. Keep the deployed Cloud Run URL/service identity visible at least once in the recording.

## Main take — target 3:40–3:55

### 0:00–0:20 — problem, immediately quantified

Show **08:05 — principal unavailable** and let the blast-radius strip make the stakes obvious:

- 3 activities;
- 6 people;
- 3 resources;
- 12 person-hours at risk.

Narration:

> At 08:05, one principal calls in sick. Within seconds, three activities, six people, three resources, and twelve person-hours are at risk. I built this because I know this failure firsthand: in live production, one absence is never one absence, and somebody has to rebuild the day while everyone waits.

### 0:20–0:40 — product promise

Show the hero/autonomy statement.

> Places, Again is autonomous operational disruption recovery. When the plan breaks, it maps the cascade, finds several safe recovery strategies, lets Gemini choose what makes operational sense, proves that exact choice again, and commits the change. If safety cannot be proved, it stops for a human.

### 0:40–1:45 — one real cloud event, one action

**Record this entire segment continuously and without edits.** From the moment
**Inject disruption event** is triggered until the workflow reaches terminal
state, do not pause the recording, splice takes, jump forward, or hide waiting
time. This is the rubric's live Proof of Action.

Trigger **Inject disruption event** once in the exact submitted cloud build.

After that, do not guide the workflow. Let the real Cloud Run → Pub/Sub → private worker → ADK/Gemini → Firestore path finish.

Keep visible where possible:

- event ID;
- blast-radius metrics;
- safe candidate cards;
- actual Gemini selected candidate ID;
- validated reason codes;
- deterministic re-verification PASS;
- timeline reaching terminal state.

Never pre-script a candidate ID or reason code. Narrate only what the captured run actually displays.

### 1:45–2:20 — recovered state

Show:

- 3/3 recovered;
- 12 person-hours restored;
- 0 unaffected activities moved;
- version `1 → 2`;
- outbox prepared;
- messages sent = 0;
- safety proof.

### 2:20–2:45 — replay/failure proof

Use the existing Cloud E2E evidence / UI evidence rather than improvising a new destructive test during the main take.

Show that replay kept the same committed version/outbox and the impossible/adversarial event reached `human_required` without unsafe state mutation or sends.

Independent external evidence is already captured in GitHub Actions run `33254443473`: version remained 2 after replay, outbox count remained 12, and the adversarial unknown-person case ended in `human_required` with messages sent = 0.

### 2:45–3:10 — second domain

Switch to **Commercial Film / Broadcast Production**.

Show the completed recovery proof using the same candidate-selection/re-verification mechanism.

Narration target:

> Different people, resources and priorities—same recovery engine, same Gemini decision contract, same deterministic proof and commit path.

### 3:10–3:30 — undeniable Google Cloud proof

Make one fast cutaway through the following pages. **Open these tabs before recording; do not navigate through menus during the take.**

Cloud Run services:

https://console.cloud.google.com/run?project=project-2ee12060-728f-434f-9ad

Pub/Sub:

https://console.cloud.google.com/cloudpubsub?project=project-2ee12060-728f-434f-9ad

Firestore:

https://console.cloud.google.com/firestore?project=project-2ee12060-728f-434f-9ad

Vertex AI:

https://console.cloud.google.com/vertex-ai?project=project-2ee12060-728f-434f-9ad

Names that must be legible somewhere:

- `places-again`
- `places-again-worker`
- `places-again-events`
- `places-again-worker-push`
- Gemini 3.5 / Vertex AI / Google ADK evidence

Then show the committed architecture diagram briefly.

### 3:30–3:50 — close

Return to the recovered app.

> Gemini decides what makes operational sense. Deterministic code proves what is safe.
>
> Places, Again is the agent where one person disappears—and the broken operation rebuilds itself safely.
>
> The plan breaks. The operation recovers.

## Hard recording gates

Do not publish the take unless all are true:

- duration <= 4:00;
- English audio or English subtitles;
- the exact submitted public Cloud Run build is demonstrated, not a mock;
- the 0:40–1:45 trigger-to-terminal Proof-of-Action segment is continuous and uncut;
- main workflow begins with one action and then proceeds autonomously;
- actual candidate count/ID/reasons match narration;
- deterministic re-verification is visible before commit;
- recovered metrics match the submitted build;
- messages sent = 0;
- replay/fail-closed evidence is visible;
- second-domain proof is visible;
- Google Cloud deployment is visibly demonstrated;
- no credentials, personal data, notifications or unrelated tabs appear.

If any spoken number or model-selection claim differs from the screen, discard the take and record again.

## After recording

1. Upload publicly to YouTube or Vimeo — not unlisted.
2. Confirm the published duration is <= 4:00.
3. Add the public video URL to `docs/submission.md` and `JUDGE_EVIDENCE.md`.
4. Add final video timestamps to `JUDGE_EVIDENCE.md`.
5. Publish the build article and social post; add their public URLs to the submission if claiming the bonuses.
6. Re-open the hosted application anonymously once immediately before Devpost Submit.
7. Finalize Devpost and freeze the exact repository/video/live build.

Do not modify the judged repository/video or any submitted live app after final submission until winners are announced; use a separate fork/branch for later experimentation.
