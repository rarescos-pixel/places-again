# Places, Again — final recording runbook

Use this only after the Google Cloud deployment is green. The verified live app is:

https://places-again-inb6leu4ca-ew.a.run.app

Verified Google Cloud project:

`project-2ee12060-728f-434f-9ad`

The API deployment has `PLACES_AGAIN_SYNTHETIC_DEMO_MODE=true`, so the synthetic scenario can be reset for clean recording attempts without redeploying the infrastructure.

## Before recording

1. Open the live app in a clean browser tab.
2. Close personal tabs/notifications and hide any account-sensitive UI.
3. Confirm **Opera Production** is selected.
4. Reset the synthetic scenario from the demo UI if the baseline is not clean.
5. Confirm the page shows the pre-incident state before recording.
6. Keep the `.run.app` URL visible at least once in the recording.

Do not rerun `deploy.sh` just to reset the demo. The deployment is already verified.

## Main take — target 3:40–3:55

### 0:00–0:20 — problem

Show the clean Opera baseline and the disruption control.

Narration:

> I built this because I know this failure firsthand. In live production, one absence is never one absence. It instantly becomes a problem of people, skills, rooms, resources, and time—and somebody has to rebuild the day while everyone waits.

### 0:20–0:40 — product promise

Show the hero/autonomy statement.

> Places, Again is autonomous operational disruption recovery. When the plan breaks, it maps the cascade, finds several safe recovery strategies, Gemini chooses what makes operational sense, deterministic code proves what is safe, and the system commits the recovery.

### 0:40–1:45 — one live event, one click

Click **Inject disruption event** once.

After that, do not guide the workflow. Let the real Cloud Run → Pub/Sub → private worker → ADK/Gemini → Firestore path finish.

Keep visible where possible:

- event ID;
- blast-radius metrics;
- candidate cards;
- Gemini selected candidate ID;
- validated reason codes;
- deterministic re-verification PASS;
- timeline reaching terminal state.

Never narrate a candidate ID or reason code before it is visible in the actual run.

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

Use the existing cloud E2E evidence / UI evidence rather than improvising a new destructive test during the main take.

Show that replay kept the same committed version/outbox and the impossible/adversarial event reached `human_required` without unsafe state mutation or sends.

### 2:45–3:10 — second domain

Switch to **Commercial Film / Broadcast Production**.

Show the already completed recovery proof using the same candidate-selection/re-verification mechanism.

Narration target:

> Different people, resources and priorities—same recovery engine, same Gemini decision contract, same deterministic proof and commit path.

### 3:10–3:30 — Google Cloud proof

Make one fast cutaway through the following pages. Do not spend time navigating during the take; open these tabs before recording if possible.

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
- live `.run.app` build visible;
- main workflow begins with one click and then proceeds autonomously;
- actual candidate count/ID/reasons match narration;
- deterministic re-verification is visible before commit;
- recovered metrics match the submitted build;
- messages sent = 0;
- replay/fail-closed evidence is visible;
- second-domain proof is visible;
- Google Cloud deployment is visible;
- no credentials, personal data, notifications or unrelated tabs appear.

If any spoken number differs from the screen, discard the take and record again.

## After recording

1. Upload publicly to YouTube or Vimeo — not unlisted.
2. Confirm the published duration is <= 4:00.
3. Add the public video URL to `docs/submission.md` and `JUDGE_EVIDENCE.md`.
4. Only then finalize Devpost.

Do not modify the judged live app/repository after final submission until winners are announced; use a separate fork/branch for later experimentation.
