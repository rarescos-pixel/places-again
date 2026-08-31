# Devpost submission — canonical final copy

This file supersedes the earlier working draft in `docs/submission.md`.

## Project name

**Places, Again**

## Tagline

**The plan breaks. The operation recovers.**

## Primary category

**Taskmaster**

## One-line summary

At 08:05, one critical principal becomes unavailable and 3 activities, 6 people, 3 resources, and 12 person-hours become at risk. Places, Again autonomously maps the cascade, lets Gemini choose among deterministically safe recovery strategies, re-verifies that choice against current state, and commits the bounded recovery without step-by-step human guidance.

## Inspiration

I built Places, Again because I know this failure firsthand from live production. One absence is not one empty calendar cell: qualified cover, other people, rooms, scarce resources, availability windows, priorities and downstream calls all become coupled. Existing planning software describes yesterday's plan; the difficult work begins when reality makes that plan false.

Opera is the proving ground, not a claim that every industry is already implemented. A second synthetic commercial film/broadcast scenario runs through the same engine to prove portability across a different operational domain.

## What it does

The user reports one incident once. The public Cloud Run API validates and persists it, returns an `event_id`, and publishes only that opaque ID through Pub/Sub. Authenticated OIDC delivery invokes a private Cloud Run worker running Google ADK and Gemini 3.5 on Vertex AI.

The workflow then:

1. measures the operational blast radius;
2. deterministically enumerates a bounded non-dominated set of hard-safe recovery candidates;
3. lets Gemini select one supplied candidate ID using ranked soft operational priorities;
4. rebuilds and independently re-verifies that candidate against current state;
5. commits schedule + event ledger + audit + deterministic outbox atomically in Firestore;
6. ends at `human_required` when safety cannot be proved.

Messages can be prepared, but the agent has no send tool and messages sent remain zero.

## Why Gemini is necessary

Removing Gemini changes the operational choice, not the safety boundary.

In the opera baseline there are two genuine hard-safe strategies:

- Candidate A: 0 highest-priority calls moved, 3 people changed, 270 shifted minutes;
- Candidate B: 1 highest-priority call moved, 7 people changed, 240 shifted minutes.

Candidate B moves fewer minutes, but it disrupts the highest-priority call and changes more people's schedules. A fixed deterministic weight would encode one permanent soft-preference policy. Places, Again instead keeps hard safety deterministic and lets Gemini apply ranked contextual priorities only inside the already-safe set.

Gemini cannot invent or edit plans, waive a hard constraint, mutate Firestore, use shell/arbitrary HTTP/secrets, or send messages. An unknown candidate ID fails closed. Deterministic code re-verifies the selected state before Firestore can commit.

> **Gemini decides what makes operational sense. Deterministic code proves what is safe.**

## Visible result

All scenario data is synthetic.

Opera baseline:

- 3 affected activities, 6 people, 3 resources;
- 12.0 person-hours at risk;
- 3/3 activities recovered;
- 12.0 person-hours restored;
- zero unaffected activities moved;
- zero unresolved activities;
- Firestore state `v1 → v2` exactly once as a business effect;
- 12 prepared-not-sent outbox items;
- zero messages sent;
- zero unsafe actions.

Commercial film/broadcast baseline: 4/4 activities recovered and 26.0 person-hours restored with zero unaffected activities moved, through the same candidate generator, Gemini selection contract, deterministic re-verification, transaction and UI.

## Architecture

`Cloud Run API → Pub/Sub/OIDC → private Cloud Run worker → Google ADK + Gemini 3.5 on Vertex AI → deterministic re-verification → Firestore`

Pub/Sub is at-least-once. Places, Again therefore claims exactly-once **business effect** in the Firestore deployment, not exactly-once delivery. A stable event ledger plus one Firestore transaction prevents replay from applying the recovery twice or duplicating outbox items.

The final Firestore persistence P0 discovered during judge-path testing was fixed structurally: persisted ADK tool-result evidence is bounded and terminal events no longer retain the full transient candidate payload. The recovery engine, safety authority, transaction boundary and replay semantics were unchanged. Regression coverage now includes repeated demo evidence and explicit Firestore-size headroom.

## Production evidence

Final post-P0 live validation on 2026-08-30, revision `places-again-00003-jz8`:

- exact UI-shaped public incident payload accepted with HTTP 202;
- `received → planned → completed`;
- two hard-safe candidates;
- Gemini-selected `candidate-a` with validated reason codes;
- deterministic re-verification PASS;
- Firestore `v1 → v2`;
- 3/3 activities and 12 person-hours recovered;
- zero unaffected movement;
- 12 prepared-not-sent outbox items, zero messages sent;
- replay without a duplicate business effect;
- adversarial unknown-person incident → `human_required`, no mutation/send.

Final reproducible repository baseline:

- **67/67 automated tests**;
- **52/52 labeled evaluation cases**;
- zero unsafe commits;
- zero duplicate business effects;
- zero Gemini-invented candidate commits;
- zero hard-constraint overrides;
- 100% of committed candidates independently reverified.

Detailed evidence: `JUDGE_EVIDENCE.md` and `reports/cloud-e2e-verified-20260830.md`.

## Built with

Gemini 3.5, Vertex AI, Google ADK, Google Cloud Run, Google Pub/Sub, Firestore, Python, FastAPI, Pydantic, JavaScript, HTML/CSS, Pytest, Docker.

## Links

- Hosted application: https://places-again-674409858210.europe-west1.run.app
- Repository: https://github.com/rarescos-pixel/places-again
- Judge testing instructions: `docs/judge-testing-instructions.md`
- Public video: **insert final public YouTube/Vimeo URL after upload**
- Public build article: https://github.com/rarescos-pixel/places-again/issues/3
- Social bonus URL: **insert only after publication**

## Prize/category selections

- Taskmaster — primary.
- Best Architectural Design — strong fit.
- Individual/Hobbyist — select only if the final entrant form confirms eligibility.
- Do not select Startup Excellence without an incorporated entrant organization.
- Do not select Best Multimodal UX.
- Do not claim an additional-model bonus; the final base submission intentionally avoids decorative model stuffing.
