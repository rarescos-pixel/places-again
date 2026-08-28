# Places, Again — operating protocol

## Objective

Maximize the realistic chance of winning Google All Things Agentic Hackathon,
especially Taskmaster, without trading away correctness, reliability, or a stable
four-minute demo.

Priority order: correctness, reliability, chance of winning, experience quality,
then credit efficiency.

## Model routing

Use the least expensive model that can produce the same objectively verifiable
quality:

- **SOL decides:** product strategy, official-rule interpretation, architecture,
  agentic design, security, reliability, cross-system debugging, rubric audits,
  feature freeze, and final submission review.
- **TERRA builds:** approved designs, scoped backend/frontend work, integrations,
  localized debugging, test expansion, technical documentation, and demo assets.
- **LUNA executes mechanically:** repository search, inventories, repetitive edits,
  formatting, lint, existing tests, smoke tests, logs, deterministic comparisons,
  and checklist verification.

Escalate `LUNA -> TERRA` when effects stop being local or judgment is required.
Escalate `TERRA -> SOL` for ambiguity, architectural trade-offs, two failed
attempts, Gemini agenticity, security, reliability, data integrity, or rubric
impact.

SOL hands implementation work down with: decision, reason, invariants,
implementation, acceptance criteria, tests, and escalation conditions. Workers
report only files changed, implementation, tests/results, remaining problems, and
whether SOL review is needed.

## Non-negotiable gates

SOL review is required before a major architecture change, after agentic-core
implementation, before feature freeze, after cloud end-to-end testing, and before
submission. Do not implement a feature unless it improves an official score,
real agenticity, memorability, reliability, or the demo.

Keep `PROJECT_CHECKPOINT.md` current. Read only task-relevant files unless a
global audit is justified. Batch decisions, implementation, mechanical checks,
and critical review. Never claim a model switch or cloud result that did not
actually occur.

Do not use the project owner as a terminal or browser relay. Request owner action
only for authentication, billing approval, publication, personal declarations,
or final submission.
