# Places, Again — final upload / copy-paste packet

Use this only after the exact submitted build and video have been captured. Do not rewrite the project story during upload.

## YouTube / Vimeo

### Recommended title

**Places, Again — Autonomous Operational Disruption Recovery | All Things Agentic Hackathon**

### Description

At 08:05, one principal becomes unavailable. Within seconds, 3 activities, 6 people, 3 resources, and 12 person-hours are at risk.

Places, Again takes that single incident and recovers the operation without waiting for step-by-step human guidance. It maps the cascade, constructs several deterministically safe recovery strategies, lets Gemini choose the strategy that best fits the operation's ranked priorities, proves that choice again against current state, and commits the bounded recovery.

The production path is: Cloud Run API → authenticated Pub/Sub → private Cloud Run worker → Google ADK + Gemini 3.5 on Vertex AI → deterministic re-verification → Firestore atomic commit.

Gemini chooses among several already-safe recovery strategies using ranked operational priorities. Deterministic code owns every hard constraint and proves the selected plan again before any state change. When safety cannot be proved, the workflow ends in `human_required` with no unsafe commit and no outbound send.

The Opera proof includes a real safe trade-off rather than a single preordained answer:
- Candidate A: 0 highest-priority calls moved, 3 people changed, 270 shifted minutes;
- Candidate B: 1 highest-priority call moved, 7 people changed, 240 shifted minutes.

Both pass hard constraints. Gemini selects Candidate A because preserving the highest-priority call outweighs the 30-minute reduction in shifted time; deterministic code then re-verifies that exact candidate before Firestore can commit.

The demo shows:
- the operational problem first: one absence expanding into 3 activities, 6 people, 3 resources, and 12 person-hours at risk;
- one continuous live Proof of Action with no cuts inside the agent run;
- autonomous recovery of 3/3 activities and 12 person-hours;
- multiple safe candidates and the real Gemini-selected candidate/reason codes;
- deterministic re-verification before Firestore commit;
- replay without a duplicate business effect;
- adversarial/impossible recovery failing closed;
- the same recovery engine in a commercial film/broadcast scenario;
- real Google Cloud execution and architecture evidence.

Hosted application: https://places-again-674409858210.europe-west1.run.app
Repository: https://github.com/rarescos-pixel/places-again

Built with Gemini 3.5, Vertex AI, Google ADK, Cloud Run, Pub/Sub, Firestore, FastAPI, Pydantic, Python, JavaScript, and Docker.

#AllThingsAgenticHackathon

### Final master — VERIFIED FOR UPLOAD

Final master v3:

- duration: **159.701 seconds (2:39.701)**;
- resolution: **1920×1080**;
- H.264 video + AAC audio;
- English narration / on-screen text;
- cinematic problem cold open before technical proof;
- visible live public-Cloud Proof of Action;
- explicit `CONTINUOUS LIVE PROOF — NO CUTS IN AGENT RUN` label over the continuous execution segment;
- visible Candidate A vs Candidate B safe trade-off and Gemini selection rationale;
- deterministic re-verification proof;
- recovery result and safe-failure path;
- Cloud Run → Pub/Sub → private Google ADK worker → Gemini 3.5 on Vertex AI → deterministic re-verification → Firestore architecture explanation;
- final human payoff.

The mandatory Devpost video field must contain the **public YouTube or Vimeo URL**, not a GitHub artifact or temporary media-storage URL.

### Visibility / compliance

- Public YouTube/Vimeo video, not private.
- English narration or English subtitles/on-screen captions.
- <= 4:00 final duration.
- Do not replace the final video after submission unless the Devpost rules explicitly permit it before deadline.
- Hosted application final post-P0 production validation passed on 2026-08-30.

## Devpost — fixed copy anchors

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

Final live validation on 2026-08-30 reached the exact UI-shaped public event path and completed the full Cloud workflow successfully on revision `places-again-00003-jz8`.

### Demo video

Insert the final public YouTube/Vimeo URL only after verifying:
- duration = 2:39.701 and therefore <= 4:00;
- public visibility;
- the uploaded file is the final v3 master;
- actual candidate/reason codes match what is shown;
- Google Cloud evidence and architecture labels are readable.

## Final repository/evidence baseline

- 67/67 automated tests;
- 52/52 labeled evaluation cases;
- Quality Gate #91 green on the post-P0 runtime commit;
- final Firestore persistence P0 fixed with bounded observable trace persistence and regression coverage;
- public UI-shaped incident path: HTTP 202 → completed;
- Gemini-selected Candidate A;
- deterministic re-verification PASS;
- Firestore v1 → v2;
- 3/3 activities / 12 person-hours recovered;
- replay: no duplicate business effect;
- adversarial case: `human_required`, version unchanged, outbox zero;
- both synthetic scenarios reset to clean version-1 state for judge use.

Detailed checkpoint: `reports/cloud-e2e-verified-20260830.md`.

## Bonus publication status

### Build article — PUBLISHED

Permanent public URL:

https://github.com/rarescos-pixel/places-again/issues/3

The article explicitly states that it was created for entering the Google All Things Agentic Hackathon and links the live app and repository. Before submission, ensure its numeric evidence is synchronized to the final **67/67 automated tests** and **52/52 labeled evaluation cases**.

### Social bonus — NOT YET CLAIMED

The canonical copy remains `docs/social-post.md`. Claim +0.2 only after it is actually public on an eligible social platform with `#AllThingsAgenticHackathon` and its permanent URL is inserted into the submission.

### Additional-model bonus — NOT CLAIMED

Do not claim the optional Gemma/additional-model bonus unless a real managed-model call is validated, the integration is merged and documented, and the final demo visibly includes it. The final base submission intentionally avoids decorative model stuffing.

## Final upload stop rule

Before pressing Submit:

- final repository Quality Gate is green;
- hosted application opens anonymously and the clean one-click demo works;
- final public YouTube/Vimeo video is exactly the approved <=4:00 master;
- all submitted URLs open successfully;
- no placeholders remain in the Devpost form;
- `JUDGE_EVIDENCE.md` contains final video timestamps;
- published article URL is included if claiming its +0.2;
- social URL is included only if actually published and claiming its +0.2;
- entrant eligibility has been reviewed honestly;
- repository, video, and submitted live app are frozen for judging.
