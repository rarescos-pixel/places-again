# Cloud E2E verified — 2026-08-29

The production path is now verified from both the owner-authenticated Google Cloud environment and an independent anonymous GitHub-hosted runner.

## Current judge-accessible endpoint

- Public application: `https://places-again-674409858210.europe-west1.run.app`
- Cloud revision observed by the external probe: `places-again-00001-m8f`

## Owner-authenticated production proof

The Google Cloud deployment completed with:

- `FINAL_STATUS=SUCCESS`
- Cloud Run API → Pub/Sub
- authenticated Pub/Sub OIDC → private Cloud Run worker
- real Google ADK + Gemini 3.5 on Vertex AI
- deterministic current-state re-verification before commit
- Firestore state `v1 -> v2` exactly once as a business effect
- replay without duplicate business effects
- impossible/adversarial incident -> `human_required` with no unsafe state mutation or send
- prepared outbox with `messages_sent = 0`

## Independent anonymous public-internet proof

GitHub Actions `Live Cloud E2E Proof` run `33254443473` completed successfully on 2026-08-29 against the current Cloud Run URL.

The external runner first verified `/api/capabilities` and observed:

- runtime: `Google Cloud Run`
- agent framework: `Google Agent Development Kit`
- model: `gemini-3.5-flash`
- model backend: `Vertex AI`
- repository: `firestore`
- event transport: `Google Pub/Sub`
- private worker configured: `true`
- outbound delivery: `disabled; prepared_not_sent only`

It then ran `scripts/cloud_e2e_test.py` against the public endpoint and completed with `passed: true`.

The successful live run proved:

1. two deterministic hard-safe candidates were produced;
2. Gemini selected an existing candidate ID (`candidate-a` in this captured run);
3. validated selection reason codes were `preserve_highest_priority_activity` and `minimize_people_schedule_changes`;
4. deterministic re-verification passed with no violations;
5. Firestore state changed from version 1 to version 2;
6. 3/3 affected opera activities were recovered and 12.0 person-hours restored;
7. 0 unaffected activities were moved;
8. 12 outbox items were prepared and 0 messages were sent;
9. replay preserved version 2 and outbox count 12, demonstrating no duplicate business effect;
10. the adversarial/unknown-person incident ended in `human_required` with no unsafe send.

The workflow uploaded the raw evidence artifact:

- artifact name: `live-cloud-e2e-7e5cb3d29a11ef9affa3d3c44fe73d94df84cbfd`
- artifact ID: `9715370372`

This closes the previously open anonymous front-door gate. The live application may now be presented as independently judge-accessible, subject to the normal final pre-submit link check.

Source implementation: `.github/workflows/live-cloud-e2e-proof.yml`, `scripts/cloud_e2e_test.py`, and `deploy.sh`.
