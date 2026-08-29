# Deploy Places, Again

This path bypasses the fragile guided-deploy preflight and runs the repository's own audited deployment logic.

## Run the full deployment

The helper first discovers Google Cloud projects that the active account can actually access, keeps only projects with verifiably enabled billing, and safely selects the best match. It then runs the authoritative deployment script, which enables only missing APIs with bounded retry/backoff for transient `429` quota errors, creates the two Cloud Run services, Pub/Sub OIDC delivery, Firestore, least-privilege service accounts, and finally runs the real cloud E2E proof.

Click the copy-to-Cloud-Shell button on this single command, then press **Enter** once:

```sh
bash scripts/deploy_auto.sh
```

Do not enter any additional commands while it is running. The intended Cloud Run and Firestore region is `europe-west1`; Vertex AI uses `global` as configured by the script.

If Google asks for an account authorization or permission confirmation, approve only the requested Google Cloud authorization for this deployment.

## Success

A successful run ends with `FINAL_STATUS=SUCCESS` and prints the selected project, public `API_URL`, private `WORKER_URL`, Pub/Sub resources, and the generated cloud E2E evidence path.

The E2E gate must prove all of these before the deployment is submission-ready:

- public Cloud Run API -> Pub/Sub -> authenticated private worker;
- real Google ADK + Gemini 3.5 selection from the deterministic safe candidate set;
- deterministic current-state re-verification;
- Firestore `v1 -> v2` exactly once;
- replay without duplicate business effects;
- impossible/adversarial event -> `human_required` with no state mutation or send;
- messages prepared, messages sent = 0.

## If it stops

Do not improvise or run random fixes. The script writes `runtime/deployment-report-latest.txt` with failure diagnostics. Capture the final screen or report and use that exact evidence for the next repair.
