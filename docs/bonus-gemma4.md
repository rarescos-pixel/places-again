# Optional +0.2 model bonus — Gemma 4 recovery briefing

This branch is intentionally isolated from `main` until the core submission is fully frozen.

## Purpose

Gemma 4 is used as a **read-only post-recovery manager briefing model**. It consumes only bounded, observable facts from a terminal Places, Again event and turns the audited record into a concise human handoff.

It is not in the safety or mutation path.

- Gemini 3.5 still performs the bounded operational candidate selection.
- Deterministic code still owns every hard constraint and re-verification.
- Firestore still commits the recovery exactly once.
- Gemma 4 receives the record only after the event is terminal.
- Gemma 4 cannot select/edit a plan, mutate Firestore, send a message, use tools, or alter safety policy.
- Free-form incident `reason`, agent trace, raw plan internals, and hidden reasoning are not sent to Gemma.

This makes the additional model useful without turning bonus scoring into feature bloat.

## Model

Google managed model API on Vertex AI / Gemini Enterprise Agent Platform:

`gemma-4-26b-a4b-it-maas`

Region: `global`.

## Real validation command

After this branch passes CI, validate it against one completed event in the existing Google Cloud project:

```bash
python scripts/gemma4_recovery_briefing.py \
  --api-url https://places-again-inb6leu4ca-ew.a.run.app \
  --event-id YOUR_COMPLETED_EVENT_ID \
  --project-id project-2ee12060-728f-434f-9ad \
  --output runtime/gemma4-briefing-evidence.json
```

A qualifying evidence run must show:

- a real terminal event fetched from the live Places, Again deployment;
- the managed model ID `gemma-4-26b-a4b-it-maas`;
- a non-empty manager briefing;
- authority recorded as `advisory_post_recovery_only`;
- no incident free-text reason in the model input;
- no hidden reasoning persisted;
- no state mutation or message-send authority added.

## Merge gate

Do **not** merge this branch into `main` merely because unit tests pass.

Merge only if:

1. the real managed Gemma 4 call succeeds in the owner-authenticated Google Cloud project;
2. the output is clearly useful and can be shown in a few seconds in the final demo/README;
3. the core live workflow and <=4-minute demo remain unchanged and stable;
4. official Devpost guidance still confirms Gemma counts as an additional Google AI model for +0.2.

If any gate fails, abandon this branch. The verified Taskmaster core remains untouched.
