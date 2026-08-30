# Judge testing instructions

These instructions are intentionally short. They do not require credentials for the repository or any proprietary data.

## Preferred path — hosted UI

Verified hosted application:

`https://places-again-674409858210.europe-west1.run.app`

Final post-P0 production validation passed on 2026-08-30. The current live Cloud Run revision is `places-again-00003-jz8`; the exact UI-shaped incident payload returns HTTP 202 and completes through Pub/Sub → private Google ADK/Gemini worker → deterministic re-verification → Firestore.

1. Open the hosted URL in a desktop browser.
2. Select **Opera Production**.
3. Confirm the page is in the clean synthetic baseline state. If the demo reset control is available and no event is running, use **Reset scenario** once.
4. Click **Inject disruption event** once.
5. Do not choose tools or approve intermediate steps. Wait for the workflow to reach a terminal state.
6. Inspect:
   - event ID and timeline;
   - blast radius;
   - multiple hard-safe candidate cards;
   - actual Gemini-selected candidate ID + validated reason codes;
   - deterministic re-verification = PASS;
   - schedule version `v1 → v2`;
   - recovered metrics;
   - outbox prepared / messages sent = 0.
7. Switch to **Commercial Film / Broadcast Production** to inspect the same mechanism on the second synthetic domain.

All people, schedules, resources, incidents, and metrics are synthetic.

## Reproducible local path

Python 3.12 is recommended.

```bash
git clone https://github.com/rarescos-pixel/places-again.git
cd places-again
python -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/pytest -q
.venv/bin/python scripts/run_evaluation.py --summary
.venv/bin/uvicorn places_again.web:app --host 127.0.0.1 --port 8000
```

Open:

`http://127.0.0.1:8000`

The local product uses the persisted deterministic fallback in a background task, while the submitted Google Cloud evidence proves the production Pub/Sub → private ADK/Gemini worker → Firestore path separately.

## Reproducible evidence checks

```bash
.venv/bin/python scripts/verify_core.py
.venv/bin/python scripts/secret_scan.py --history
```

Expected repository baseline after the final Firestore persistence P0 fix:

- 52/52 labeled evaluation cases;
- 67/67 automated tests;
- 0 unsafe commits;
- 0 duplicate business effects;
- 0 Gemini-invented candidate commits;
- 0 hard-constraint overrides;
- 100% of committed candidates deterministically reverified.

## Google Cloud proof

The production path has passed owner-authenticated deployment E2E plus an independent post-deploy public validation:

`Cloud Run API → Pub/Sub/OIDC → private Cloud Run worker → Google ADK + Gemini 3.5 on Vertex AI → deterministic re-verification → Firestore`

The final 2026-08-30 public validation observed:

- exact UI-shaped incident payload accepted with HTTP 202;
- `received → planned → completed`;
- two hard-safe candidates;
- Gemini-selected `candidate-a` with validated reason codes;
- deterministic re-verification PASS;
- Firestore `v1 → v2`;
- 3/3 activities and 12 person-hours recovered;
- zero unaffected activities moved;
- 12 prepared-not-sent outbox items, zero messages sent;
- replay without a duplicate business effect;
- an adversarial/unknown-person event ending in `human_required`, version unchanged, outbox zero.

The post-P0 persistence fix also keeps the observable ADK trace bounded so repeated demo/E2E runs do not recursively inflate the single transactional Firestore document.

See:

- `reports/cloud-e2e-verified-20260830.md`
- `JUDGE_EVIDENCE.md`
- `docs/architecture.svg`

The final submission video also shows the actual Google Cloud deployment and execution evidence, as required by the contest rules.
