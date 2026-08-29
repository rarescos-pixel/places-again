# Google All Things Agentic — current official audit

Rechecked against the live official pages on **2026-08-28**. This is an
engineering and contest-fit audit, not legal or tax advice.

## Binding facts and latest organizer guidance

- Submission closes **2026-08-31 at 5:00 PM Pacific Time**.
- Judging runs September 1–October 1; winners are expected around
  **2026-10-08**.
- Every project must use Gemini 3.5 or newer, at least one Google agent
  framework, and at least one Google Cloud infrastructure service.
- Taskmaster rewards a complete multi-step background workflow that removes
  personal “bring your own friction” with little or no hand-holding.
- Scoring is Innovation & Operational Utility 40%, Architectural Discipline &
  Tech Stack 30%, and Demo & Production Readiness 30%.
- The video is public YouTube/Vimeo, English or English-subtitled, and only the
  first four minutes are judged. It must visibly prove Google Cloud deployment.
- A repository, reproducible setup, architecture diagram, project text, and
  cloud proof are required.
- The organizer's latest update links the Google Cloud Q&A recording and repeats
  the August 31 deadline. An earlier official self-check warns that judges may
  score entirely from the video, description, and repository rather than run
  the project.
- The public page currently shows roughly 10.7k registered participants. That
  is not the number of final eligible submissions and is not converted into a
  fabricated win probability.

Primary sources:

- https://allthingsagentichackathon.devpost.com/rules
- https://allthingsagentichackathon.devpost.com/details/faqs
- https://allthingsagentichackathon.devpost.com/updates
- https://allthingsagentichackathon.devpost.com/

## Score and prize ceiling

The judged base score is 1–5. Optional contributions can raise the final score
to a maximum of 6:

- public build content with the required contest-purpose disclosure: +0.2;
- eligible social post using `#AllThingsAgenticHackathon` where required: +0.2;
- each genuinely integrated additional eligible Google AI model: +0.2, maximum
  +0.6.

The Grand Prize is USD 50,000 gross; Taskmaster is USD 20,000 gross;
Individual/Hobbyist is USD 10,000 gross; Best Architectural Design is USD 5,000
gross. A project can win at most one prize. Taxes, withholding, currency, bank
fees, and net receipt are separate. Official delivery is within 60 days after
the administrator receives completed winner forms.

## Winner benchmark, not a secret rubric

Google's official 2025 ADK Hackathon results name **SalesShortcut** as Grand
Prize winner and **Energy Agent AI** as the North America regional winner:

- https://cloud.google.com/blog/products/ai-machine-learning/adk-hackathon-results-winners-and-highlights
- https://devpost.com/software/salesshortcut
- https://devpost.com/software/energy-agent-ai

They are not evidence of an unwritten rule that more agents or more services
win. The transferable pattern is clearer:

1. the problem is understandable immediately;
2. personal or commercial stakes are concrete;
3. the AI performs a visible, consequential action;
4. the result is a transformation, not an answer;
5. the architecture and evidence make the claim credible.

Places, Again deliberately follows that pattern without copying their domains
or feature count. Its memory hook is: **one person disappears and the broken
operation rebuilds itself safely**.

## Current product evidence

- One incident expands visibly into the operational blast radius.
- The deterministic engine returns a bounded, heuristically generated
  non-dominated hard-safe recovery candidate set.
- Opera exposes a real trade-off between preserving the highest-priority call
  and reducing total shifted minutes.
- Commercial production exposes a different trade-off between single-cover
  continuity and balanced cover workload.
- Gemini 3.5 through Google ADK selects one supplied candidate ID using domain
  soft priorities.
- Deterministic code independently re-verifies the chosen plan before commit.
- Firestore transaction, event ledger, idempotency, replay, crash, concurrency,
  prepared-not-sent outbox, security boundary, and observability remain intact.
- 52/52 labeled evaluation cases pass locally.
- 65/65 automated tests pass after the candidate-set and worker-route gates.
- Worktree and Git-history secret scan passes with no findings.

## Why Gemini audit

The prior “Gemini calls a recovery function” architecture was not strong enough
for a winner-level demonstration. The current architecture resolves that defect
without moving safety into the model:

- deterministic code defines what is possible and safe;
- multiple feasible strategies expose real operational trade-offs;
- Gemini applies soft context and priorities to select one bounded ID;
- deterministic code proves the current-state result again;
- Firestore, not the model, owns effects.

The model is consequential but not sovereign.

## Eligibility boundary

Personal eligibility under Section 3 is an owner-only attestation and remains
unresolved by the technical project. Development continues without making a
public claim about the entrant's personal circumstances; the sponsor retains
final discretion. **OWNER ELIGIBILITY CHECK REQUIRED BEFORE FINAL SUBMIT.**

AI coding assistants are explicitly welcomed in the current FAQ. AI use is not
a scoring penalty. The submitted entrant remains responsible for originality,
accuracy, rights, and all final representations.

## Current hard gates

1. A real Google Cloud E2E report must prove Cloud Run → authenticated Pub/Sub
   → private worker → Vertex AI Gemini/ADK → deterministic proof → Firestore
   `v1 → v2` → prepared outbox.
2. The same cloud run must prove replay without a second business effect and an
   impossible/adversarial event without an unsafe commit.
3. The final public video must match the submitted commit and show the real
   `.run.app` URL or equivalent Cloud Console evidence.
4. The article and social post must be published if their bonus is claimed.
5. Final Devpost claims, links, selected categories, and owner attestations
   must be reconciled before Submit.

Working verdict: **continue**. The core direction is competitive and the fatal
“Why Gemini?” weakness is now addressed. It is not finalist-ready until the
real cloud hard gate passes.
