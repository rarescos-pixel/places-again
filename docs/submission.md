# Devpost submission draft

## Project name

Places, Again

## Tagline

The call changes. The day survives.

## Category

Taskmaster

## Inspiration

A live production can lose hours of work when one performer becomes unavailable.
The damage is not the absence alone: every rehearsal that depends on that person,
every other participant's availability, every room, and every notification now
has to be reconciled under time pressure. This project comes from direct,
long-term experience inside opera rehearsal workflows.

## What it does

Places, Again converts a same-day absence event into action. When the event
arrives, Gemini reads the current production state, identifies affected calls,
finds a fully qualified cover, searches for the nearest conflict-free slots,
and produces a low-change recovery plan under the fixed policy—without someone
guiding each step. It verifies participant availability, room conflicts, people
conflicts, and the rule that unaffected sessions stay untouched.

The agent does not silently mutate the schedule. It first presents a plan. A
safe plan can be explicitly committed against the exact state version it was
calculated from; a stale or unresolved plan is rejected. After commit, the
agent prepares individualized Romanian and English call sheets in an audited
outbox. It has no tool for sending them.

## How we built it

- Gemini 3.5 for agent reasoning and tool orchestration
- Google Agent Development Kit for the agent and scoped tool interface
- Google Cloud Run for the deployed backend
- Firestore transactions for plans, schedule versions, audit events, and the
  unsent outbox across concurrent Cloud Run instances
- FastAPI for the control-room API and interface
- A deterministic Python constraint engine for safety-critical decisions
- Versioned JSON state for free local reproduction, with the same repository
  interface used by Firestore in Cloud Run
- Pytest integration tests for preview, commit, stale-plan rejection, conflict
  detection, and the unsent-message boundary

The architecture deliberately separates probabilistic orchestration from
deterministic constraints. Gemini chooses the workflow. The engine decides
whether a schedule is safe. Firestore commits the versioned transition
atomically. This keeps the agent useful without allowing a confident model
answer—or a concurrent service instance—to bypass operational rules.

## Challenges

The hardest part was not generating a plausible schedule; it was proving that
the schedule is safe. A replacement must be qualified, available, and free of
overlaps, while every other participant and room must also remain conflict-free.
The second challenge was containing side effects. Preview and commit are
separate, stale plans fail closed, and outbound messages remain unsent.

## Accomplishments

In the synthetic opera scenario, one same-day illness event affects three
calls. From that event, the system recovers all three, moves zero unaffected
sessions, reports zero unresolved calls, passes four safety gates, commits a new
state version, and prepares twelve bilingual call sheets without sending one.

## What we learned

Operational agents need a smaller authority surface than chat assistants. A
good agent should be able to do meaningful work, but every side effect should
be explicit, versioned, auditable, and reversible where possible. Pairing an
LLM orchestrator with a deterministic constraint layer is substantially more
reliable than asking the model to invent a timetable in prose.

## What's next

The next production steps are Firestore persistence, authentication and roles,
acknowledgment tracking, room/equipment disruption types, and connectors for
existing production-management systems. The same recovery pattern can then be
used by theatre, film, festivals, broadcast, and conferences.

## Built with

Gemini 3.5, Google ADK, Google Cloud Run, Python, FastAPI, Pydantic, JavaScript,
HTML/CSS, Pytest, Docker
