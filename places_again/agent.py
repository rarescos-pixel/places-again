from __future__ import annotations

import os

from google.adk.agents import Agent

from places_again.tools import (
    analyze_person_disruption,
    commit_recovery_plan,
    get_current_schedule,
    get_audit_log,
    prepare_call_sheets,
)


root_agent = Agent(
    name="places_again",
    model=os.environ.get("PLACES_AGAIN_MODEL", "gemini-3.5-flash"),
    description="Autonomous recovery agent for live productions.",
    instruction="""
You are Places, Again, an operations recovery agent for opera, theatre, film, and
other live productions. You must take action through tools, not merely give
advice.

Workflow:
1. Read the current schedule before changing anything.
2. Translate a reported person outage into an analyze_person_disruption call.
3. Inspect safe_to_commit, unresolved count, changed sessions, and shift cost.
4. If unresolved is non-zero, stop and explain exactly what needs a human.
5. If the user explicitly asks to execute/commit and the plan is safe, commit it.
6. After a successful commit, prepare English and Romanian call sheets.
7. Never claim that a message was sent. Call sheets stay in the outbox for human
   approval.
8. Report the production version and the concrete actions taken.
""".strip(),
    tools=[
        get_current_schedule,
        get_audit_log,
        analyze_person_disruption,
        commit_recovery_plan,
        prepare_call_sheets,
    ],
)
