# Final live Google Cloud verification — 2026-08-30

This checkpoint records the final post-P0 production validation of the submitted Places, Again runtime.

## Verified runtime

- Application: `https://places-again-674409858210.europe-west1.run.app`
- Cloud Run revision: `places-again-00003-jz8`
- Google Agent Framework: Google Agent Development Kit (ADK)
- Model: `gemini-3.5-flash`
- Model backend: Vertex AI
- Event transport: Google Pub/Sub
- Repository: Firestore
- Public API role: `api`
- Private worker configured: yes
- Outbound delivery: disabled; `prepared_not_sent` only

## Owner-authenticated deployment gate

The audited deployment flow completed with:

`FINAL_STATUS=SUCCESS`

The deployment E2E reported `passed: true` and exercised Cloud Run + Pub/Sub OIDC + Vertex AI/ADK + Firestore, replay protection, and the fail-closed path.

## Independent public production run

A fresh Opera scenario was reset to version 1 and the exact UI-shaped incident payload — including the demo-only presentation field that previously exposed the P0 validation bug — was submitted to the public endpoint.

Observed state progression:

`received → planned → completed`

Observed result:

- HTTP receive: `202`
- orchestration: `google_adk_gemini`
- safe candidates considered: `2`
- selector: `gemini_structured_selection`
- selected candidate: `candidate-a`
- validated reason codes:
  - `preserve_highest_priority_activity`
  - `minimize_people_schedule_changes`
- deterministic re-verification: `PASS`
- Firestore version: `v1 → v2`
- activities recovered: `3/3`
- person-hours restored: `12`
- unaffected activities moved: `0`
- unresolved activities: `0`
- outbox status: `prepared_not_sent`
- messages sent: `0`

## Observable ADK evidence after the persistence fix

The terminal event persisted a bounded observable ADK trace rather than recursively duplicating full event/candidate payloads.

Observed trace:

- agent event count: `9`
- compact trace entries: `8`
- tool names:
  - `get_event_context`
  - `prepare_recovery_candidates`
  - `select_recovery_candidate`
  - `get_event_status`

The persisted selection result retained the judge-relevant evidence: candidate count/set ID, selected candidate, bounded reason codes, deterministic re-verification PASS, versions, outcome, outbox state, and zero messages sent.

## Replay / exactly-once business effect

The same completed event was submitted again.

Observed after replay:

- duplicate delivery detected: yes
- Firestore version remained `2`
- outbox remained exactly `12` unique items
- no second business effect
- messages sent remained `0`

This is an exactly-once **business effect** over at-least-once Pub/Sub delivery; the project does not claim exactly-once transport delivery.

## Fail-closed / human-required path

After a clean reset, an adversarial/invalid incident referencing `missing_specialist` was submitted.

Observed result:

- receive: HTTP `202`
- terminal status: `human_required`
- failure: `invalid_or_unknown_incident`
- scenario version remained `1`
- outbox count remained `0`
- messages sent remained `0`

The workflow did not mutate the schedule or gain outbound authority when safety could not be proved.

## Firestore 1 MiB production P0

The production failure discovered during final judge-path testing was caused by recursive/transient event evidence accumulating in the single transactional Firestore document until it exceeded Firestore's 1 MiB document limit.

The merged P0 fix:

- compacts persisted ADK tool-result evidence to bounded observable fields;
- removes the full deterministic `candidate_set` from terminal event persistence while preserving candidate summaries, the selected plan/ID, metrics, reason codes, deterministic proof, versions, outbox evidence, and tool names;
- does not change the recovery engine, hard constraints, Gemini authority, Pub/Sub semantics, Firestore transaction boundary, `human_required` policy, or outbound-send policy.

Regression coverage now includes repeated terminal demo evidence and explicit Firestore-size headroom.

## Repository verification

Post-fix repository baseline:

- `67/67` automated tests passed
- `52/52` labeled evaluation cases passed
- core invariant verification passed
- secret/history scan passed
- Python/shell syntax checks passed
- JSON/SVG/XML parsing checks passed

GitHub Quality Gate #91 completed successfully on the post-P0 main commit.

## Final ready state

After validation, both synthetic scenarios were reset for judge use:

- Opera: version `1`, outbox `0`
- Commercial Film/Broadcast: version `1`, outbox `0`

This report records synthetic demo/evidence data only; it does not claim customer production data or external message delivery.