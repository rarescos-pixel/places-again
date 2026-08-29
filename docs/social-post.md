One person disappears. The schedule is not the problem anymore—the operation is.

I built Places, Again because I know that failure firsthand from live production. It maps the cascade, generates only hard-safe recovery candidates, then uses Gemini 3.5 + Google ADK to choose the strategy that makes the most operational sense.

Gemini selects. Deterministic code re-verifies. Firestore commits once. If safety cannot be proved, the agent stops for a human. Messages are prepared; it has no ability to send them.

The same engine recovers both an opera production and a synthetic commercial film/broadcast day. Current reproducible evaluation: 52/52 cases, 0 unsafe commits, 0 duplicate business effects, 0 model-invented plan commits, and 100% of committed candidates reverified.

The full Google Cloud E2E is now green: public Cloud Run → Pub/Sub/OIDC → private worker → Vertex AI / Google ADK / Gemini 3.5 → Firestore, including replay and fail-closed proof.

Live app: https://places-again-inb6leu4ca-ew.a.run.app
Repo: https://github.com/rarescos-pixel/places-again

The plan breaks. The operation recovers.

Built for the Google All Things Agentic Hackathon. #AllThingsAgenticHackathon
