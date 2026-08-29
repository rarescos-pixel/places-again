# Cloud E2E verified — 2026-08-29

Owner-authenticated deployment completed successfully in Google Cloud Shell.

Terminal result:

- `FINAL_STATUS=SUCCESS`
- Public API: `https://places-again-inb6leu4ca-ew.a.run.app`
- Private worker service URL: `https://places-again-worker-inb6leu4ca-ew.a.run.app`
- Pub/Sub topic: `places-again-events`
- Pub/Sub push subscription: `places-again-worker-push`
- The deployment script reported: `Cloud Run + Pub/Sub OIDC + Vertex AI/ADK + Firestore + replay/failure proved.`
- The deployment generated a raw cloud E2E JSON report under the Cloud Shell `runtime/` directory.

This checkpoint proves the previously open production hard gate passed in the owner-authenticated Google Cloud environment. The raw generated JSON remains the authoritative detailed execution artifact and should be preserved/attached during final submission evidence reconciliation.

The successful E2E verifier is designed to assert:

1. public Cloud Run API -> Pub/Sub -> authenticated private worker;
2. real Google ADK + Gemini 3.5 bounded candidate selection;
3. deterministic current-state re-verification before commit;
4. Firestore state `v1 -> v2` exactly once;
5. replay with no duplicate business effects;
6. impossible/adversarial incident -> `human_required` with no unsafe state mutation or send;
7. prepared outbox with `messages_sent = 0`.

Source implementation: `scripts/cloud_e2e_test.py` and `deploy.sh`.
