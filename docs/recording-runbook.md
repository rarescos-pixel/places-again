# Places, Again — final recording runbook

## Recording strategy

Record from the exact independently reachable Cloud Run build:

https://places-again-674409858210.europe-west1.run.app

Independent anonymous hosted-UI reachability and the full live Cloud E2E passed
on 2026-08-29 in GitHub Actions `Live Cloud E2E Proof` run `33255155489` on
commit `374798636b7b907c7fb20ad4ced806b27a07eb55`.

Verified Google Cloud project:

`project-2ee12060-728f-434f-9ad`

The API deployment has `PLACES_AGAIN_SYNTHETIC_DEMO_MODE=true`, so the synthetic
scenario can be reset for clean recording attempts without redeploying
infrastructure. Do not rerun `deploy.sh` just to reset the demo.

The final proof measured the safe Opera run at about 12.61 seconds from
`received` to `completed`, with about 11.34 seconds of Gemini/ADK latency. This
is not a guaranteed future duration. Plan ~35 seconds for the live segment; if
the run takes longer, keep it continuous and shorten later sections.

## Before recording

1. Open the hosted URL in a clean desktop browser tab. This is the **Opera live
   tab** used for the unedited Proof of Action.
2. Confirm it loads without auth/404 and the badges identify Google ADK, Gemini
   3.5, Cloud Run, Pub/Sub and Firestore.
3. Confirm **Opera Production** is selected. Press **Reset scenario** once if the
   page is not in the clean baseline. Confirm the status says the scenario is
   ready and the event ID is blank.
4. Open the same hosted URL in a **second browser tab**. In that second tab,
   select **Commercial Film / Broadcast Production**, press **Inject disruption
   event** once, wait until it completes, and leave that completed film result
   open. Do this **before** recording. Changing the scenario dropdown resets that
   scenario, so the completed film proof must be pre-staged in its own tab.
5. Return to the Opera live tab and do not touch **Inject disruption event**
   until recording is underway.
6. Close personal tabs, notifications and any account-sensitive UI.
7. Open all Google Cloud evidence tabs listed below before recording.
8. Open the architecture diagram and repository/Quality Gate in separate tabs.
9. Keep the browser address bar with the public `.run.app` URL visible at least
   once in the final video.

## Main take — target 3:30–3:40

### 0:00–0:18 — problem and stakes

Show the Opera incident context and say the quantified stakes: 3 activities, 6
people, 3 resources, 12 person-hours at risk.

### 0:18–0:35 — product promise

Explain the authority split: Gemini chooses among already-safe strategies;
deterministic code proves the exact selected candidate again before commit.

### 0:35–1:10 — one real Cloud event

**From the click on `Inject disruption event` until terminal state, keep the
recording continuous and uncut.** No pause, splice, speed-up, jump-forward or
second take inserted inside this live sequence.

Click **Inject disruption event** exactly once in the Opera live tab.

Then do not interact until the workflow reaches `completed` or
`human_required`.

Keep visible where possible:

- event ID;
- blast-radius metrics;
- timeline;
- safe candidate cards;
- actual Gemini-selected candidate ID;
- actual validated reason codes;
- `Deterministic re-verification: PASS`;
- terminal status.

If the run completes before the planned 35 seconds, stay in the same continuous
shot and hold on the decision/re-verification proof. If it runs longer, keep
recording and shorten the later evidence/closing sections. Never cut the live
run to hit a timestamp.

### 1:10–1:38 — recovered state

Show clearly:

- 3/3 recovered;
- 12 person-hours restored;
- 0 unaffected activities moved;
- version `1 → 2`;
- 12 messages prepared;
- messages sent = 0;
- safety proof / re-verification PASS.

### 1:38–2:00 — replay and fail-closed evidence

Use the already-verified Cloud/GitHub E2E evidence rather than improvising a
second destructive test during the main take.

Final independent proof run `33255155489` recorded:

- replay version remained 2;
- outbox count remained 12;
- the impossible/adversarial unknown-person case ended in `human_required`;
- messages sent remained 0.

### 2:00–2:25 — second domain

Switch browser tabs to the **pre-staged completed Commercial Film / Broadcast
Production tab**. Do not change the scenario dropdown in the Opera tab during
the recording, because doing so resets the selected scenario.

Show the film candidate/decision proof and recovered metrics. This keeps the
second-domain proof instant while preserving the Opera run as the single live
Proof-of-Action trigger.

### 2:25–2:52 — Google Cloud proof

These tabs must already be open before recording:

Cloud Run services:
https://console.cloud.google.com/run?project=project-2ee12060-728f-434f-9ad

Pub/Sub:
https://console.cloud.google.com/cloudpubsub?project=project-2ee12060-728f-434f-9ad

Firestore:
https://console.cloud.google.com/firestore?project=project-2ee12060-728f-434f-9ad

Vertex AI:
https://console.cloud.google.com/vertex-ai?project=project-2ee12060-728f-434f-9ad

Make these names legible somewhere:

- `places-again`;
- `places-again-worker`;
- `places-again-events`;
- `places-again-worker-push`;
- Gemini 3.5 / Vertex AI / Google ADK evidence.

Then show the committed architecture diagram briefly.

### 2:52–3:15 — reproducible evidence

Show the public repo / Quality Gate and state:

- 52/52 labeled evaluation cases;
- 65/65 automated tests;
- independent public hosted-UI + live Cloud E2E proof.

### 3:15–3:32 — close

Return to the recovered Opera tab.

> Gemini decides what makes operational sense. Deterministic code proves what is safe.
>
> One person disappears—and the broken operation rebuilds itself safely.
>
> The plan breaks. The operation recovers.

## Hard recording gates

Do not publish the take unless all are true:

- duration <= 4:00; target 3:30–3:40;
- English audio or English subtitles;
- exact public Cloud Run build is demonstrated;
- browser shows the judge-accessible `.run.app` URL at least once;
- trigger-to-terminal Proof of Action is one continuous uncut normal-speed shot;
- main workflow begins with one action and receives no intermediate user guidance;
- actual candidate count/ID/reasons match narration;
- deterministic re-verification is visible before commit;
- recovered metrics match the captured run;
- messages sent = 0;
- replay/fail-closed evidence is visible;
- second-domain proof is visible from the pre-staged completed film tab;
- Google Cloud deployment proof is readable;
- no credentials, personal data, notifications or unrelated tabs appear.

If any spoken number or model-selection claim differs from the screen, discard
the take and record again.

## After recording

1. Upload publicly to YouTube or Vimeo — not unlisted.
2. Confirm published duration <= 4:00.
3. Send the public video URL back into this workflow.
4. Add the URL and exact timestamps to `docs/submission.md` and
   `JUDGE_EVIDENCE.md`.
5. Publish the prepared build article and social post if claiming +0.4 and save
   their permanent public URLs.
6. Re-open the hosted app anonymously immediately before Devpost Submit.
7. Complete the eligibility declaration honestly.
8. Submit, then tag/freeze the exact repository/video/live build.

Do not modify the judged repository/video or submitted live app after final
submission until winners are announced; use a separate branch/fork for later
experimentation.
