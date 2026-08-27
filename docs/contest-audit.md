# Google All Things Agentic — internal audit

Checked: 2026-08-27. This is a working audit, not legal advice.

## Verified facts

- Deadline: 2026-08-31 at 17:00 Pacific Time.
- Winners announced on or around 2026-10-08.
- Required stack: Gemini 3.5+, a listed Google agent framework, and a Google
  Cloud infrastructure service.
- Required assets include a code repository, reproducible README, architecture
  diagram, and public demo video no longer than four minutes showing Google
  Cloud execution.
- Grand Prize: USD 50,000 gross. Taskmaster: USD 20,000 gross.
  Individual/Hobbyist: two prizes of USD 10,000 gross. Best Architectural
  Design and Best Multimodal UX: two prizes each of USD 5,000 gross. Honorable
  Mentions are USD 2,000 and therefore below the user's target. One project can
  receive at most one prize.
- Prize delivery: within 60 days after completed winner forms are received.
- Fees, exchange costs, withholding, and Romanian tax treatment are not included
  in the headline prize.
- AI coding assistants are permitted by the new-project rule; the entrant owns
  and takes responsibility for the submission.
- The official USD 150 credit form is already closed because the available
  credits were exhausted. The official resources page still permits use of the
  Google Cloud free tier or a no-cost trial. Deployment is therefore capped at
  zero minimum and one maximum Cloud Run instance.

Primary source: https://allthingsagentichackathon.devpost.com/rules

## Eligibility uncertainty

The rule excludes individuals or organizations "employed by a government
agency." The user's employer is a Romanian public cultural institution
subordinate to the Ministry of Culture. Those descriptions are not identical,
and the rule does not define "government agency." Therefore:

- It is not defensible to state that the user is certainly excluded.
- It is also not defensible to promise eligibility.
- The sponsor keeps sole discretion to verify eligibility and conflicts.
- No organizer has been contacted, per the user's explicit instruction.

Working classification: **plausible but unconfirmed eligibility**. This is the
only current stop-risk that could invalidate a technically complete entry.

## Fit and feasibility

- Personal fit: strong. The problem comes from extensive direct opera-rehearsal
  experience rather than a generic invented use case.
- Category fit: strong for Taskmaster because the system mutates state and
  completes a multi-step workflow instead of returning advice.
- Technical status: the deterministic verification and the full dependency
  suite both pass locally. On 2026-08-27, all 14 pytest tests passed, covering
  the HTTP API, preview/commit boundary, stale-plan rejection, the unsent
  outbox, both repository adapters, and the public Gemini usage limit. The
  mandatory Gemini/Google ADK integration and transactional Firestore
  repository are in code. Cloud Run deployment and a real Gemini 3.5 run still
  require the owner's Google Cloud project.
- Competitive volume: the public page showed 9,533 registered participants on
  2026-08-27. That is not the number of valid final submissions and cannot be
  converted into a success probability.
- Financial fit: the USD 10,000 and USD 20,000 cash prizes exceed the requested
  EUR 5,000 floor at ordinary recent exchange-rate ranges, but this audit does
  not guarantee a future exchange rate or net amount after tax.
- Calendar fit: announcement is before 2026-12-31. A prompt winner response and
  completed forms would ordinarily put the stated 60-day delivery window before
  2027-02-28, but administrative delay is possible.

## Competitive and claim risks

- Production scheduling, conflict detection, and call sheets already exist in
  commercial products. Do not claim invention of that category.
- The defensible difference is narrow: same-day autonomous recovery,
  policy-bounded minimum change, versioned commit, explicit safety proof, and an
  audited outbox.
- "Places, Again" passed only a preliminary exact-name web search. It is not a
  trademark clearance.
- The prototype currently handles person unavailability, not every disruption
  type mentioned in the product roadmap.

## Decision gate

Continue: local work is reversible and currently costs EUR 0. Before external
submission, verify the real Gemini path, deploy to Cloud Run, record the demo,
and have the entrant make the final eligibility and employer-policy
attestations.
