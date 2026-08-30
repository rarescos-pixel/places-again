# Places, Again — Building an autonomous recovery agent for when the plan breaks

> I created this piece of content for the purposes of entering the Google All Things Agentic Hackathon.

Most operational software is designed for the moment when the plan still holds. Places, Again starts at the opposite moment: a critical person suddenly becomes unavailable and the schedule, people, rooms, resources, and downstream communications all have to be reconsidered at once.

I built Places, Again from a problem I know personally from live performance operations. In opera, one same-day absence can invalidate multiple rehearsals and calls at once. The goal was not to build another scheduling chatbot. The goal was to build a background agent that can take a real disruption, calculate its blast radius, recover the operation when a safe recovery exists, and stop safely when it does not.

## The core design decision: AI does not own safety

The most important architectural choice was to separate operational judgment from hard feasibility.

A deterministic recovery engine owns the hard constraints: participant availability, qualification, resource conflicts, schedule conflicts, duration preservation, completeness of the affected set, and current-state freshness. It produces a bounded set of recovery candidates that have already passed those constraints.

Gemini 3.5 then receives only those safe candidate IDs, observable trade-offs, and explicit soft operational priorities. It can choose which already-safe option makes the most operational sense, but it cannot invent a new plan, edit an action, write directly to the database, send a message, or bypass a safety gate.

After Gemini chooses, deterministic code verifies the selected plan again against the current state. Only then can the result be committed.

The design rule is simple:

**Gemini decides what makes operational sense. Deterministic code proves what is safe.**

## Google-native execution path

The deployed architecture uses Google Agent Development Kit with Gemini 3.5 on Vertex AI. A public Cloud Run API persists the incident and publishes only an opaque event ID through Google Pub/Sub. A private Cloud Run worker receives the authenticated push, runs the ADK workflow, and accesses the state in Firestore.

The Firestore transition is transactional so the selected plan, schedule version, event status, audit trail, and prepared outbox move together. Pub/Sub may redeliver an event, but the business effect is protected from duplication.

The agent has no external-send tool. Recovery communications are prepared in an outbox with `prepared_not_sent` status and `messages_sent = 0`.

## What one event looks like

In the opera scenario, one principal performer becomes unavailable. The system identifies three affected activities, six affected people, three affected resources, and 12 person-hours at risk.

The deterministic engine produces multiple safe recovery strategies. Gemini chooses between those bounded strategies using the operational priorities visible to it. The chosen candidate is re-verified, committed transactionally, and the UI shows the resulting before/after state.

In the labeled live evidence case, all three affected activities are recovered, 12 person-hours are restored, no unaffected activity is moved, and no unsafe action is allowed.

## Failure is part of the product

A recovery agent is not trustworthy if it only demonstrates the happy path.

Places, Again has an explicit `human_required` terminal state. If no safe recovery exists, if Gemini selects outside the deterministic set, if the state has become stale, or if validation fails, the workflow fails closed instead of forcing an answer.

An adversarial evaluation case also puts instruction-like text inside the incident reason. The reason is treated as untrusted data. The agent has no shell, arbitrary HTTP, secret-access, database-mutation, or external-delivery tool that such text could unlock.

## Proving that it is not just an opera scheduler

Opera is the proving ground. Disruption recovery is the product.

A second synthetic scenario models a commercial film/broadcast shoot. The names, resources, priorities, and activities change, but the recovery mechanism stays the same: detect what has become invalid, construct hard-constraint-safe alternatives, make a bounded contextual decision, re-verify, commit atomically, and escalate when safety cannot be proven.

## Verification

The repository's automated quality gate currently runs 65 tests plus 52 labeled evaluation cases across the opera and commercial-shoot domains. The evaluation targets include zero unsafe commits, zero unresolved auto-commits, zero duplicate side effects, 100% stale-plan rejection, 100% re-verification of committed candidates, zero Gemini-invented plan commits, and zero hard-constraint override commits.

An independent GitHub Actions Cloud E2E workflow also exercises the public Cloud Run service, real Pub/Sub path, private ADK/Gemini worker, Firestore state transition, replay behavior, and a `human_required` adversarial case.

## What I learned

The hardest part of an autonomous agent is not making it capable of taking action. It is defining exactly where that authority ends.

The useful pattern I arrived at is a narrow agent surrounded by deterministic contracts: give the model the contextual choice that benefits from language-model judgment, but keep feasibility, state integrity, and irreversible effects under deterministic control.

That is the idea behind Places, Again:

**The plan breaks. The operation recovers.**

Project repository: https://github.com/rarescos-pixel/places-again

Live application: https://places-again-674409858210.europe-west1.run.app
