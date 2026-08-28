# Sceptical 5/5/5 audit — pre-cloud checkpoint

This audit does not award aspirational points. A criterion is defensible only
when the submitted artifact and public video prove it.

## Innovation & Operational Utility

Evidence already strong:

- firsthand BYOF origin rather than an invented generic workflow;
- background workflow that mutates operational state;
- narrow, defensible category: disruption recovery after the plan breaks;
- measured opera result and same-engine commercial-production proof;
- a visible incident cascade and a memorable before/after transformation;
- two non-dominated choices in each domain rather than artificial decoys;
- Gemini makes a bounded, consequential selection using domain soft priorities;
- explicit distinction between demonstrated functionality and future scope.

Current reasons a sceptical judge could score below 5:

- no public live run yet;
- the commercial value is demonstrated by operational metrics, not customer
  adoption or real cost data;
- person unavailability is the only implemented disruption type.

Action: do not broaden claims. Make the live one-click recovery and the second
domain undeniable in the video.

## Architectural Discipline & Tech Stack

Evidence already strong:

- Pub/Sub event-driven path and stable event ledger;
- Firestore-cloud exactly-once business effects over at-least-once delivery;
- transactional Firestore state/version/plan/audit/outbox;
- deterministic feasible-space generation and re-verification separated from
  Gemini/ADK soft-policy selection;
- strict schemas, inert reason text, four-tool allowlist, no send/shell/HTTP;
- separate least-privilege service identities and no keys;
- crash, retry, replay, concurrency, stale-state, and adversarial tests;
- persistent observable trace without hidden chain-of-thought.

Current reasons a sceptical judge could score below 5:

- deployment code is not proof that Pub/Sub OIDC and IAM work;
- actual Gemini/ADK token/latency fields may vary by SDK event support;
- Firestore single-document transaction is appropriate for this bounded demo,
  but is not a claim of unlimited multi-tenant scale.

Action: pass the cloud E2E, show IAM/private-worker evidence, and describe the
single-document choice as a deliberate atomic demo boundary.

## Demo & Production Readiness

Evidence already strong:

- finalist control room with event ID, cascade, non-dominated candidates,
  Gemini decision evidence, timeline, recovery impact, state version, gates,
  trace, outbox, and intentional failure state;
- one-command local reproduction and one-command cloud deployment;
- 52-case reproducible evaluator plus deployment evidence script;
- README, architecture, workflow, threat model, failure modes, judge map, video
  script, and Devpost draft.

Current reasons a sceptical judge could score below 5:

- no successful cloud evidence report yet;
- no public video URL;
- repository visibility/access is not yet proven for judges;
- Devpost still contains placeholders;
- no exact submitted commit tag exists.

Action: these are hard gates, not polish. Do not freeze or submit until each is
closed.

## Current verdict

The local core is finalist-grade by its own reproducible evidence, but the
submission is **not yet defensible as 5/5/5** because the highest-risk criterion
— undeniable real Google Cloud execution — is still unproven. The next allowed
strategic move is cloud deployment and evidence capture; bonus models remain
deferred.
