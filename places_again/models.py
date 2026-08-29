from __future__ import annotations

import re
from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


ID_PATTERN = r"^[a-z][a-z0-9_-]{1,63}$"
TIME_PATTERN = r"^(?:[01]\d|2[0-3]):[0-5]\d$"
CONTROL_CHARACTERS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Disruption(StrictModel):
    kind: Literal["person_unavailable"] = "person_unavailable"
    person_id: str = Field(pattern=ID_PATTERN)
    start: str = Field(pattern=TIME_PATTERN)
    end: str = Field(pattern=TIME_PATTERN)
    reason: str = Field(default="unavailable", min_length=1, max_length=280)

    @field_validator("reason")
    @classmethod
    def reason_is_data_safe(cls, value: str) -> str:
        """Reject controls while preserving the report as inert operational data."""
        if CONTROL_CHARACTERS.search(value):
            raise ValueError("reason contains unsupported control characters")
        return value

    @model_validator(mode="after")
    def interval_is_forward(self) -> Disruption:
        start = datetime.strptime(self.start, "%H:%M")
        end = datetime.strptime(self.end, "%H:%M")
        if start >= end:
            raise ValueError("start must be before end")
        return self


class RecoveryRequest(StrictModel):
    scenario_id: str = Field(default="opera", pattern=ID_PATTERN)
    disruption: Disruption
    commit: bool = False


class IncidentRequest(StrictModel):
    scenario_id: Literal["opera", "commercial_shoot"] = "opera"
    disruption: Disruption
    event_id: UUID | None = None
    source: Literal["ui", "api", "demo", "evaluation"] = "api"

    @model_validator(mode="before")
    @classmethod
    def strip_demo_presentation_metadata(cls, value):
        """Keep the public demo compatible without relaxing normal API strictness.

        The browser demo config carries a human-readable ``copy`` string beside
        the actual disruption fields. Treat that one presentation-only key as
        client metadata when the request explicitly comes from the demo UI.
        All other sources keep StrictModel's extra-field rejection unchanged.
        """
        if not isinstance(value, dict) or value.get("source") != "demo":
            return value
        disruption = value.get("disruption")
        if not isinstance(disruption, dict) or "copy" not in disruption:
            return value
        cleaned = dict(value)
        cleaned_disruption = dict(disruption)
        cleaned_disruption.pop("copy", None)
        cleaned["disruption"] = cleaned_disruption
        return cleaned


class RecoveryEventRequest(StrictModel):
    scenario_id: Literal["opera", "commercial_shoot"] = "opera"
    disruption: Disruption
    reset_demo: bool = False


class PlanCommitRequest(StrictModel):
    scenario_id: Literal["opera", "commercial_shoot"] = "opera"
    plan_id: str = Field(pattern=r"^plan-[a-f0-9]{8,32}$")


class AgentRequest(StrictModel):
    message: str = Field(min_length=3, max_length=4_000)


class PubSubMessage(StrictModel):
    data: str
    message_id: str | None = Field(default=None, alias="messageId")
    publish_time: str | None = Field(default=None, alias="publishTime")

    model_config = ConfigDict(
        extra="allow", str_strip_whitespace=True, populate_by_name=True
    )


class PubSubEnvelope(StrictModel):
    message: PubSubMessage
    subscription: str | None = None
