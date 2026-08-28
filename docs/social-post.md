Every organization has software for when the plan works. I built Places, Again for the moment when the plan breaks.

It is an autonomous operational disruption recovery agent built with Gemini 3.5, Google ADK, Cloud Run, Pub/Sub, and Firestore. One incident starts a background workflow that measures the blast radius, finds the smallest qualified recovery, proves the new state against deterministic safety gates, commits atomically, and prepares an outbox it cannot send.

I started with opera because I know this failure mode firsthand. Opera is the proving ground, not the market: the same engine also recovers a synthetic commercial film/broadcast shoot.

Current reproducible evaluation: 47/47 cases, 0 unsafe commits, 0 unresolved auto-commits, 0 duplicate side effects, 100% stale-plan rejection, and zero messages sent.

Built for the Google All Things Agentic Hackathon. #AllThingsAgenticHackathon
