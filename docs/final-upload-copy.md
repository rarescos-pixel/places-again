# Places, Again — final upload / copy-paste packet

Use this only after the exact submitted build and video have been captured. Do not rewrite the project story during upload.

## YouTube / Vimeo

### Recommended title

**Places, Again — Autonomous Operational Disruption Recovery | All Things Agentic Hackathon**

### Description

Places, Again is an autonomous operational disruption-recovery agent for complex, time-critical operations.

One incident starts a Google Cloud workflow: Cloud Run API → authenticated Pub/Sub → private Cloud Run worker → Google ADK + Gemini 3.5 on Vertex AI → deterministic re-verification → Firestore atomic commit.

Gemini chooses among several already-safe recovery strategies using ranked operational priorities. Deterministic code owns every hard constraint and proves the selected plan again before any state change. When safety cannot be proved, the workflow ends in `human_required` with no unsafe commit and no outbound send.

The demo shows:
- one absence expanding into 3 activities, 6 people, 3 resources, and 12 person-hours at risk;
- autonomous recovery of 3/3 activities and 12 person-hours;
- multiple safe candidates and the real Gemini-selected candidate/reason codes;
- deterministic re-verification before Firestore commit;
- replay without a duplicate business effect;
- adversarial/impossible recovery failing closed;
- the same recovery engine in a commercial film/broadcast scenario;
- real Google Cloud execution evidence.

Hosted application: https://places-again-674409858210.europe-west1.run.app
Repository: https://github.com/rarescos-pixel/places-again

Built with Gemini 3.5, Vertex AI, Google ADK, Cloud Run, Pub/Sub, Firestore, FastAPI, Pydantic, Python, JavaScript, and Docker.

#AllThingsAgenticHackathon

### Generated demo candidate — VERIFIED LOCALLY

The automated submission-video workflow has already produced and inspected a 1920×1080 H.264 MP4:

- duration: **117.33 seconds**;
- English on-screen captions;
- visible unedited terminal proof against the public `.run.app` endpoint;
- Opera safe recovery;
- replay exactly-once business-effect proof;
- adversarial/impossible `human_required` proof;
- commercial film/broadcast second-domain proof;
- public app, capabilities, independent E2E, architecture, and Quality Gate evidence.

This MP4 is a generated artifact, **not yet the mandatory public-video URL**. Do not put a GitHub artifact/release URL in the Devpost video field: the official submission requires public YouTube or Vimeo.

### Visibility / compliance

- Public YouTube/Vimeo video, not unlisted.
- English narration or English subtitles/on-screen captions.
- <= 4:00 final duration.
- Do not replace the final video after submission.
- Hosted application is independently verified from GitHub Actions on 2026-08-29.

## Devpost — fixed copy anchors

### Project name

**Places, Again**

### Tagline

**The plan breaks. The operation recovers.**

### One-line summary

When one person disappears from a live operation, Places, Again maps the cascade, compares several deterministically safe recovery strategies with Gemini, proves the selected plan again, and commits the bounded safe recovery that best fits the operation's ranked priorities—without waiting for step-by-step human guidance.

### Primary category

**Taskmaster**

### Built with

Gemini 3.5, Vertex AI, Google ADK, Google Cloud Run, Google Pub/Sub, Firestore, Python, FastAPI, Pydantic, JavaScript, HTML/CSS, Pytest, Docker

### Repository

https://github.com/rarescos-pixel/places-again

### Hosted application

https://places-again-674409858210.europe-west1.run.app

Independent GitHub-hosted verification on 2026-08-29 reached `/api/capabilities` and completed the full live Cloud E2E path successfully.

### Demo video

Insert the final public YouTube/Vimeo URL only after verifying:
- <= 4:00;
- public visibility;
- exact submitted build/evidence path;
- actual candidate/reason codes match what is shown;
- Google Cloud evidence is readable.

## Bonus publication status

### Build article — PUBLISHED

Permanent public URL:

https://github.com/rarescos-pixel/places-again/issues/3

The article explicitly states that it was created for entering the Google All Things Agentic Hackathon and links the live app and repository. Current evidence text has been synchronized to **65/65 automated tests** and **52/52 labeled evaluation cases**.

### Social bonus — NOT YET CLAIMED

The canonical copy remains `docs/social-post.md`. Claim +0.2 only after it is actually public on an eligible social platform with `#AllThingsAgenticHackathon` and its permanent URL is inserted into the submission.

### Additional-model bonus — NOT YET CLAIMED

Do not claim the optional Gemma/additional-model bonus unless the real managed-model call is validated, the integration is merged and documented, and the final demo visibly includes it.

## Final upload stop rule

Before pressing Submit:

- exact submitted commit has a green Quality Gate;
- final public YouTube/Vimeo video is <= 4:00;
- all submitted URLs open successfully;
- no placeholders remain in the Devpost form;
- `JUDGE_EVIDENCE.md` contains final video timestamps;
- published article URL is included if claiming its +0.2;
- social URL is included only if actually published and claiming its +0.2;
- entrant eligibility has been reviewed honestly;
- repository, video, and submitted live app are frozen for judging.
