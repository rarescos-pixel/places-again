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

Repository: https://github.com/rarescos-pixel/places-again

Built with Gemini 3.5, Vertex AI, Google ADK, Cloud Run, Pub/Sub, Firestore, FastAPI, Pydantic, Python, JavaScript, and Docker.

#AllThingsAgenticHackathon

### Visibility / compliance

- Public video, not unlisted.
- English narration or English subtitles.
- <= 4:00 final duration.
- Do not replace the final video after submission.
- Do not claim a hosted application URL unless anonymous judge access is actually verified.

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

Preferred: insert the verified anonymous `.run.app` URL only if external judge access is green.

Deadline fallback: if the front door still returns 404 externally, omit the broken hosted URL if the form permits and rely on the public demo, repository, architecture, testing instructions, and real Google Cloud execution evidence.

### Demo video

Insert the final public YouTube/Vimeo URL only after verifying:
- <= 4:00;
- public visibility;
- exact submitted build;
- actual candidate/reason codes match the spoken narration;
- Google Cloud evidence is readable.

## Bonus publication order

1. Publish the build article from `docs/build-article.md` on an accepted public platform.
2. Save its permanent public URL.
3. Publish the social post from `docs/social-post.md` with `#AllThingsAgenticHackathon`.
4. Save its permanent public URL.
5. Insert both URLs into the Devpost submission before final submit.
6. Claim any additional-model bonus only if the model is actually validated, merged, documented in README, and visible in the final demo.

## Final upload stop rule

Before pressing Submit:

- exact submitted commit has a green Quality Gate;
- final public video is <= 4:00;
- all submitted URLs open successfully;
- no placeholders remain in the Devpost form;
- `JUDGE_EVIDENCE.md` contains final video timestamps;
- article/social URLs are included if claiming +0.4;
- entrant eligibility has been reviewed honestly;
- repository, video, and submitted live app are frozen for judging.
