from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class Disruption(BaseModel):
    kind: Literal["person_unavailable"] = "person_unavailable"
    person_id: str
    start: str
    end: str
    reason: str = "unavailable"


class RecoveryRequest(BaseModel):
    disruption: Disruption
    commit: bool = False


class RecoveryEventRequest(BaseModel):
    disruption: Disruption
    reset_demo: bool = False


class PlanCommitRequest(BaseModel):
    plan_id: str = Field(pattern=r"^plan-[a-f0-9]{8}$")


class AgentRequest(BaseModel):
    message: str = Field(min_length=3, max_length=4_000)
