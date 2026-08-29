# Repair the public Places, Again endpoint

The application code and real Google Cloud E2E already passed. An independent
internet probe later found that the default `run.app` front door returns a
Google-hosted 404 before the request reaches the container.

Google documents this behavior when the default Cloud Run URL is disabled or
network ingress blocks the caller. The deployment already proved API ingress was
`all`, so this repair explicitly restores the default HTTPS endpoint and
re-asserts unauthenticated invocation for **only the public API service**.

It does **not** rebuild or redeploy application code, change Firestore state,
change Gemini/ADK, or make the private worker public.

## Run the repair

Click the copy-to-Cloud-Shell button on this single command, then press **Enter** once:

```sh
bash scripts/repair_public_frontdoor.sh
```

A successful repair ends with:

`FINAL_STATUS=PUBLIC_FRONTDOOR_REPAIRED`

and prints the API URL.

After that, do not run anything else. The repository's independent GitHub
Actions `Live Cloud E2E Proof` will be rerun from outside Google Cloud to verify
that the public endpoint, real Pub/Sub/ADK/Gemini/Firestore workflow, replay and
fail-closed behavior are all externally reachable.
