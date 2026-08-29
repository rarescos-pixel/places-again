# Diagnose the external Cloud Run 404

This is a **read-only** diagnostic. It does not change Cloud Run, IAM, Firestore, Pub/Sub, Vertex AI, or organization policies.

## Run the diagnostic

Click the copy-to-Cloud-Shell button on this single command, then press **Enter once**:

```sh
bash scripts/diagnose_public_404.sh
```

The diagnostic checks:

- the effective Cloud Run ingress setting;
- whether the default `run.app` endpoint is enabled;
- whether the Invoker IAM check is disabled;
- effective organization policies relevant to public Cloud Run access;
- Cloud Audit policy logs for `run.googleapis.com/HttpIngress`, including VPC Service Controls / Access Context denials;
- the owner-environment capabilities endpoint.

A successful diagnostic ends with:

`FINAL_STATUS=PUBLIC_404_DIAGNOSTIC_COMPLETE`

and prints a single `DIAGNOSIS=...` line immediately above it.

After it finishes, do not run anything else. Capture the bottom of the terminal containing `DIAGNOSIS=` and `FINAL_STATUS=`.
