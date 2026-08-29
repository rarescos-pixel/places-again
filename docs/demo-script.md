# Final public demo script — target 3:30–3:40

English. Public YouTube or Vimeo. Record the exact submitted Google Cloud build.
Use the independently verified public Cloud Run UI:

https://places-again-674409858210.europe-west1.run.app

Independent anonymous hosted-UI reachability and the full live Cloud E2E passed
on 2026-08-29 in GitHub Actions `Live Cloud E2E Proof` run `33255155489` on
commit `374798636b7b907c7fb20ad4ced806b27a07eb55`.

The raw final proof measured the safe Opera recovery at about 12.61 seconds from
`received` to `completed`; the Gemini/ADK portion was about 11.34 seconds. Treat
those numbers as evidence, not as a guaranteed future duration. Give the live
run a ~35-second slot, but if it takes longer, keep recording continuously until
terminal state and shorten later sections instead. Never cut the live execution.

The main recovery must be one real incident trigger; after that, do not guide
the workflow. Do not fake waiting states or replace a failed cloud run with a
claim. If the demonstrated run fails, repair and record again.

## 0:00–0:18 — The human problem, immediately quantified

Visual: Cloud Run UI, Opera Production selected. Show **08:05 — principal
unavailable** and the incident context.

> At 08:05, one principal calls in sick. Three activities, six people, three
> resources, and twelve person-hours are suddenly at risk. I built this because
> I know this failure firsthand: in live production, one absence is never just
> one absence.

## 0:18–0:35 — Product promise and authority boundary

Visual: hero and autonomy/safety statement.

> Places, Again maps the cascade, generates several safe recovery strategies,
> lets Gemini choose what makes operational sense, proves that exact choice
> again, and commits it. If safety cannot be proved, it stops for a human.

## 0:35–1:10 — One live disruption, one action, no guidance

**Proof-of-Action rule: keep this entire trigger-to-terminal sequence as one
continuous, uncut recording.** No pause, splice, jump forward, or replacement
waiting footage.

Trigger **Inject disruption event** once in the exact deployed build. Do not
click anything else until the workflow reaches `completed` or `human_required`.

During the live run, keep the event ID, cascade, candidate area and timeline in
view. Narrate only what the screen supports:

> One action submits the incident. From here, the user does not guide the
> workflow. Cloud Run persists the event, authenticated Pub/Sub invokes the
> private worker, and deterministic code constructs only hard-safe candidates.

When candidates and selection appear:

> Gemini 3.5 through Google ADK chooses only among those already-safe
> strategies. The highlighted candidate and reasons are the actual result of
> this run. Deterministic code then re-verifies that exact candidate against the
> current state before Firestore can commit it.

Do **not** pre-script the candidate ID or reason codes. If the run finishes early,
keep the same continuous shot for a few seconds on the selected candidate,
validated reasons and `Deterministic re-verification: PASS`. If it runs longer
than 35 seconds, stay live and steal time from later sections.

## 1:10–1:38 — Visible recovery and safe authority

Visual: recovered cascade, decision panel, proof cards and outbox.

> Version one becomes version two. All three affected activities are recovered,
> twelve person-hours are restored, zero unaffected activities move, and zero
> unsafe actions occur. Twelve bilingual messages are prepared, but zero are
> sent. The agent has no send tool and no direct database mutation authority.

Show clearly:

- `3/3 recovered`;
- `12 person-hours restored`;
- `0 unaffected activities moved`;
- actual Gemini-selected candidate + reason codes;
- `Deterministic re-verification: PASS`;
- `v1 → v2`;
- `12 prepared · 0 sent`.

## 1:38–2:00 — Replay and fail-closed proof

Visual: concise GitHub/Cloud E2E evidence rather than improvising a destructive
second test during the main take.

> Pub/Sub may deliver twice, but the business effect happens once. The verified
> replay leaves the version at two and the outbox at twelve. And when the
> incident cannot be safely resolved—even with adversarial instruction text—the
> workflow ends in `human_required`: no unsafe mutation, zero messages sent.

The final independent proof recorded:

- replay version = 2;
- replay outbox count = 12;
- impossible/adversarial case = `human_required`;
- messages sent = 0.

## 2:00–2:25 — Same engine, second domain

Visual: switch to **Commercial Film / Broadcast Production** and show its
completed state/candidate proof.

> The same engine also runs a commercial film and broadcast production:
> different people, resources and priorities, but the same candidate generation,
> Gemini decision contract, deterministic proof and commit path. Four activities
> and twenty-six person-hours are recovered.

## 2:25–2:52 — Undeniable Google Cloud proof

Visual: fast cutaway through already-open Cloud Console tabs, then architecture.
Make these legible:

- Cloud Run: `places-again`, `places-again-worker`;
- Pub/Sub: `places-again-events`, `places-again-worker-push`;
- Firestore event/state;
- Gemini 3.5 / Vertex AI / Google ADK evidence;
- committed architecture diagram.

> This is a Cloud Run event API, authenticated Pub/Sub delivery to a private
> Cloud Run worker, Gemini 3.5 with Google ADK on Vertex AI, deterministic
> re-verification, and a Firestore transaction.

## 2:52–3:15 — Reproducible evidence

Visual: repository / Quality Gate / evidence summary.

> Fifty-two labeled evaluation cases and fifty-nine automated tests cover
> replay, crashes, concurrency, stale state, model failure, prompt injection and
> the safety boundary. An independent GitHub runner also opens the public UI and
> executes the real Cloud path end to end.

## 3:15–3:32 — Close

Visual: return to the recovered app and hero.

> Gemini decides what makes operational sense. Deterministic code proves what
> is safe.
>
> One person disappears—and the broken operation rebuilds itself safely.
>
> The plan breaks. The operation recovers.

## Recording gate

Mandatory:

- public YouTube/Vimeo video, not unlisted;
- final duration <= 4:00; aim for 3:30–3:40, not exactly 4:00;
- English audio or English subtitles;
- exact submitted Google Cloud build, not a mock substituted for cloud execution;
- verified public URL above opens without authentication immediately before recording;
- main trigger-to-terminal Proof of Action is continuous and uncut at normal speed;
- if live execution exceeds its planned slot, keep it uncut and shorten later sections;
- one event trigger, then no intermediate user guidance;
- actual candidate count/ID/reasons match narration;
- deterministic re-verification is visible before commit;
- recovered metrics match the captured run;
- messages sent = 0;
- replay and `human_required` proof are visible;
- second domain is visibly the same mechanism;
- Google Cloud deployment evidence is readable;
- no credentials, personal data, notifications or unrelated tabs appear;
- discard the take if any spoken number/model-selection claim contradicts the screen.

Already verified before recording:

- anonymous hosted UI root;
- public `/api/capabilities`;
- full independent live Cloud E2E;
- raw evidence artifact for the exact verified proof run.
