# Places, Again — final upload / copy-paste packet

This is the canonical upload packet for the final submission. It supersedes earlier video-generation notes and working recording plans.

## YouTube / Vimeo

### Title

**Places, Again — Autonomous Operational Disruption Recovery | All Things Agentic Hackathon**

### Description

At 08:05, one principal becomes unavailable. Within seconds, 3 activities, 6 people, 3 resources, and 12 person-hours are at risk.

Places, Again takes that single incident and recovers the operation without waiting for step-by-step human guidance. It maps the cascade, constructs several deterministically hard-safe recovery strategies, lets Gemini choose the strategy that best fits ranked operational priorities, proves that choice again against current state, and commits the bounded recovery.

The production path is:

`Cloud Run API → authenticated Pub/Sub/OIDC → private Cloud Run worker → Google ADK + Gemini 3.5 on Vertex AI → deterministic re-verification → Firestore atomic commit`

Gemini does not own hard safety. It receives only already-safe candidate summaries and ranked soft priorities. In the opera baseline:

- Candidate A: 0 highest-priority calls moved, 3 people changed, 270 shifted minutes;
- Candidate B: 1 highest-priority call moved, 7 people changed, 240 shifted minutes.

Both satisfy hard constraints. Gemini selects Candidate A because preserving the highest-priority call outweighs the 30-minute reduction in shifted time; deterministic code then rebuilds and re-verifies that exact candidate before Firestore can commit.

The demo shows one continuous live Proof of Action with no hard cuts detected inside the agent-run interval, autonomous recovery of 3/3 activities and 12 person-hours, multiple safe candidates, the real Gemini-selected candidate, deterministic re-verification before commit, replay without a duplicate business effect, an adversarial/impossible case failing closed, a second commercial film/broadcast domain, and real Google Cloud architecture/execution evidence.

Final post-P0 repository baseline: 67/67 automated tests and 52/52 labeled evaluation cases.

A historical evidence frame in the video shows an earlier 65-test checkpoint; that checkpoint was genuine. The final submitted repository passes 67/67 after the bounded Firestore persistence fix.

Hosted application: https://places-again-674409858210.europe-west1.run.app
Repository: https://github.com/rarescos-pixel/places-again

Built with Gemini 3.5, Vertex AI, Google ADK, Cloud Run, Pub/Sub, Firestore, FastAPI, Pydantic, Python, JavaScript and Docker.

#AllThingsAgenticHackathon

## Final master — VERIFIED FOR UPLOAD

Final master **v8**:

- duration: **159.680 seconds (2:39.680)**;
- resolution: **1920×1080**;
- H.264 video + AAC stereo audio;
- English narration / English on-screen text;
- cinematic problem cold open before technical proof;
- real hosted UI and public-cloud execution proof;
- live agent-run interval mechanically checked for hard visual cuts at multiple thresholds: none detected;
- multiple safe candidates and actual Gemini selection visible;
- deterministic re-verification, recovered result, replay/failure evidence and Google Cloud architecture shown;
- no added top-of-screen overlay captions from the discarded v3/v5 experiments;
- direct audio audit confirms no narration after approximately 2:08.84; the close is instrumental/operatic audio.

The mandatory Devpost video field must contain the **public YouTube or Vimeo URL**, not a temporary media-storage URL.

## Devpost anchors

### Project name

**Places, Again**

### Tagline

**The plan breaks. The operation recovers.**

### One-line summary

At 08:05, one critical principal becomes unavailable and 3 activities, 6 people, 3 resources, and 12 person-hours become at risk. Places, Again autonomously maps the cascade, lets Gemini choose among deterministically safe recovery strategies, re-verifies that choice against current state, and commits the bounded recovery without step-by-step human guidance.

### Primary category

**Taskmaster**

### Built with

Gemini 3.5, Vertex AI, Google ADK, Google Cloud Run, Google Pub/Sub, Firestore, Python, FastAPI, Pydantic, JavaScript, HTML/CSS, Pytest, Docker

### Repository

https://github.com/rarescos-pixel/places-again

### Hosted application

https://places-again-674409858210.europe-west1.run.app

Final live post-P0 validation passed on 2026-08-30 on revision `places-again-00003-jz8`: exact UI-shaped incident → HTTP 202 → Pub/Sub → private ADK/Gemini worker → deterministic PASS → Firestore `v1 → v2` → 3/3 recovered; replay produced no second business effect; adversarial case ended in `human_required` without send.

### Demo video

Insert the public YouTube/Vimeo URL only after verifying that the upload is exactly the approved **v8 / 2:39.680** master and is publicly accessible.

## Final repository/evidence baseline

- 67/67 automated tests;
- 52/52 labeled evaluation cases;
- current `main` Quality Gate green;
- bounded Firestore persistence P0 fixed and regression-tested;
- public UI path: HTTP 202 → `completed`;
- Gemini-selected Candidate A;
- deterministic re-verification PASS;
- Firestore v1 → v2;
- 3/3 activities / 12 person-hours recovered;
- replay: no duplicate business effect;
- adversarial case: `human_required`, no unsafe mutation/send;
- both synthetic scenarios reset to clean version-1 state after final validation.

Detailed checkpoint: `reports/cloud-e2e-verified-20260830.md`.

## Bonus status

- Public build article: https://github.com/rarescos-pixel/places-again/issues/3 — published; final numeric evidence must read 67/67 + 52/52 before claiming the bonus.
- Social bonus: use `docs/social-post.md`; claim only after the post is public and its permanent URL is inserted into Devpost.
- Additional-model bonus: **not claimed**. Do not add model integrations to the final base submission.

## Final upload stop rule

Before pressing Submit:

1. final repository Quality Gate is green;
2. hosted application opens anonymously and both scenarios are at clean synthetic baseline;
3. final public YouTube/Vimeo video is exactly approved v8 and <=4 minutes;
4. all submitted URLs open successfully;
5. no placeholders remain in Devpost;
6. `JUDGE_EVIDENCE.md` matches the final v8 master;
7. public article URL is included if claiming +0.2;
8. social URL is included only after publication if claiming +0.2;
9. entrant eligibility is reviewed honestly;
10. after submission, freeze repository, video and live app through judging.
