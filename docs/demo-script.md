# Four-minute demo script

Target length: 3:25–3:45. Record as one continuous run. Keep the Cloud Run URL
and Google Cloud proof visible.

## 0:00–0:25 — The friction

"At 8:05, the Violetta principal calls in sick. Three rehearsals are now at
risk, but each also depends on a pianist, conductor, director, tenor, stage
manager, a room, and individual availability. In a live production, fixing one
line of a calendar can create five invisible conflicts."

## 0:25–0:45 — The product and Google proof

"Places, Again is not a chatbot and not another calendar. It is a same-day
recovery agent. It analyzes the cascade, proposes a low-change safe plan,
commits a versioned schedule, and prepares every affected call—with a human
approval boundary."

Show the Cloud Run URL, `runtime: Google Cloud Run`, `firestore`, and the
`Gemini 3.5 · Vertex AI` badge.

## 0:45–1:45 — Live action

Click **Simulate 08:05 outage event** once and do not edit the recording.

"The event arrives from the production system; no one guides the recovery step
by step. Gemini inspects the schedule, analyzes the disruption, commits only
after every safety gate passes, and prepares both English and Romanian calls.
The agent identifies three affected sessions. The cover must match every
required skill. It keeps two calls in place and moves one to the nearest slot
allowed by the cover, pianist, room, and the rest of the day's schedule. It
moves zero unaffected sessions."

Point to the live Google ADK tool trace, action list, and five impact metrics.
Do not claim global mathematical optimality; say "nearest conflict-free result
under this policy."

## 1:45–2:20 — Proof and failure boundaries

Point to all four green gates.

"A prose answer is not proof. The deterministic layer checks known people,
participant availability, room conflicts, and person conflicts. An unresolved
plan cannot commit. If the production version changes between analysis and
commit, the plan is rejected as stale."

## 2:20–2:55 — Versioned commit and outbox

"In the same autonomous run, the schedule advances from version one to version
two. Twelve individualized Romanian and English call sheets are prepared. Every
one is marked not sent; the agent has no delivery tool. The audit trail records
the plan, its actions, its verification result, and the outbox preparation."

## 2:55–3:25 — Gemini and architecture

Show the completed Gemini tool trace, then the architecture diagram.

"Gemini 3.5 orchestrates scoped tools through Google ADK. The constraint engine,
state store, and outbox are separate. Cloud Run hosts the control room, Vertex
AI serves Gemini, and Firestore commits state atomically. Gemini decides what to
do next, while deterministic code owns safety and side effects."

## 3:25–3:45 — Why this matters

"This starts with opera because the friction is real and personal, but the same
recovery pattern applies to theatre, film, festivals, broadcast, and any live
operation where one absence can collapse a day. The call changes. The day
survives."
