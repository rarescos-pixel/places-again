# Google All Things Agentic — internal audit

Checked against the official pages on **2026-08-28**. This is a working audit,
not legal or tax advice.

## Official requirements verified

- Submission deadline: **2026-08-31, 5:00 PM Pacific Time**.
- Winners expected on or around **2026-10-08**.
- Mandatory stack: Gemini 3.5 or newer, a qualifying Google agent framework,
  and Google Cloud infrastructure.
- Taskmaster asks for a multi-step background workflow completed without human
  intervention and a “bring your own friction” origin.
- Required submission assets include a repository with reproducible README,
  architecture diagram, and a public YouTube/Vimeo demo no longer than four
  minutes that visibly proves Google Cloud use.
- Scoring: Innovation & Operational Utility 40%; Architectural Discipline &
  Tech Stack 30%; Demo & Production Readiness 30%.
- Taskmaster prize: USD 20,000 gross. Individual/Hobbyist awards: USD 10,000
  gross. Only one prize may be awarded to a project.
- Prize delivery is stated as within 60 days after completed winner forms are
  received; tax, withholding, transfer cost, and EUR conversion are not the
  headline amount.
- AI coding assistants are allowed under the official FAQ.
- The contest credit pool is exhausted; deployment must use an existing trial,
  free tier, or ordinary billing.

Primary sources:

- https://allthingsagentichackathon.devpost.com/rules
- https://allthingsagentichackathon.devpost.com/details/faqs
- https://allthingsagentichackathon.devpost.com/

## Eligibility

The entrant must independently confirm that the official eligibility terms and
any applicable employer policy are satisfied before the final submission. The
repository makes no eligibility representation; the sponsor retains final
eligibility discretion. This attestation is separate from the technical score.

## Competition calibration

Public entries are technically strong. Two relevant benchmarks:

- **ShiftZero** demonstrates Cloud Run, Pub/Sub, Firestore, a deterministic
  safety kernel, adversarial input, observability, and measured autonomous
  recovery in factory operations:
  https://devpost.com/software/shiftzero-autonomous-factory-operations
- **AgentProof** demonstrates deterministic execution receipts, stale authority,
  duplicate protection, concurrency, and observable evidence around a simulated
  payment workflow:
  https://devpost.com/software/agentproof-26sza5

Implication: an attractive UI plus a plausible agent loop is not competitive.
Places, Again must prove event-driven execution, replay/crash safety, actual
Google Cloud behavior, a personal operational origin, and a credible second
domain. The current rebuild targets precisely those gaps rather than imitating
multi-agent complexity.

## Current evidence

- 35 local tests pass.
- 47/47 labeled two-domain evaluation cases pass.
- Measured acceptance targets: 0 unsafe commits, 0 unresolved auto-commits, 0
  duplicate side effects, 100% stale-plan rejection, 100% accepted-plan
  verification.
- Worktree plus reachable Git history secret scan: 0 findings.
- Main workflow: public API → Pub/Sub → private Cloud Run worker → Gemini/ADK →
  deterministic engine → Firestore transaction → prepared outbox.
- Cloud deployment code and E2E proof script exist, but a real cloud evidence
  report does not yet exist. Therefore cloud execution claims remain pending.

## Fit and honest positioning

- Personal fit: strong. Opera disruption recovery is firsthand friction.
- Taskmaster fit: strong if the cloud E2E proves the one-click background flow.
- Commercial category: Autonomous Operational Disruption Recovery.
- Opera is the proving ground; commercial film/broadcast is the implemented
  portability proof.
- Do not call it “opera scheduling software.”
- Do not claim logistics, manufacturing, healthcare, or global optimization.
- All production data is synthetic and contains no employer-proprietary details.

## Prize and calendar facts

The official rules list USD 10,000 and USD 20,000 gross awards. Currency
conversion, tax, withholding, transfer costs, and administrative timing are not
guaranteed by this repository. The published winner announcement is expected on
or around 2026-10-08.

## Hard gates before submission

1. Real Cloud Run + Pub/Sub OIDC + Vertex AI/ADK + Firestore E2E report passes.
2. Public demo video is ≤ 4 minutes and visibly proves Google Cloud.
3. Repository is accessible to judges under the official rule.
4. Devpost claims are reconciled with the actual submitted commit.
5. Entrant makes the final eligibility and employer-policy attestations.

Working verdict: **continue aggressively, but do not call the entry complete or
5/5-ready until the cloud hard gate and public video pass.**
