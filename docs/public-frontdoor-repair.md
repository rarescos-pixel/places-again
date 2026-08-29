# Make the public Cloud Run front door externally reachable

This repair changes only the public `places-again` Cloud Run service access settings.
It does **not** rebuild or redeploy application code, change the private worker,
mutate Firestore, or change Gemini/ADK behavior.

## Run the repair

Click the copy-to-Cloud-Shell button on this single command, then press **Enter once**:

```sh
bash scripts/repair_public_frontdoor.sh
```

The script explicitly sets:

- `ingress=all`;
- the default `run.app` URL enabled;
- the Cloud Run Invoker IAM check disabled (`--no-invoker-iam-check`), Google's
  recommended public-service mode;
- `allUsers -> roles/run.invoker` as a compatibility binding when permitted.

A successful run ends with:

`FINAL_STATUS=PUBLIC_FRONTDOOR_PUBLIC_MODE_SET`

After that, do not run anything else. The independent GitHub Actions Live Cloud
E2E proof can be rerun from outside Google Cloud to verify genuine public access.
