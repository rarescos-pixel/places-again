import pytest
from pydantic import ValidationError

from places_again.models import Disruption, IncidentRequest


def test_incident_models_forbid_unknown_fields():
    with pytest.raises(ValidationError):
        IncidentRequest.model_validate(
            {
                "scenario_id": "opera",
                "disruption": {
                    "person_id": "soprano_principal",
                    "start": "08:00",
                    "end": "14:00",
                    "reason": "illness",
                    "send_now": True,
                },
            }
        )


def test_demo_incident_strips_only_presentation_copy_field():
    request = IncidentRequest.model_validate(
        {
            "scenario_id": "opera",
            "source": "demo",
            "disruption": {
                "person_id": "soprano_principal",
                "start": "08:00",
                "end": "14:00",
                "reason": "illness",
                "copy": "08:05 · principal unavailable · 3 calls at risk",
            },
        }
    )

    assert request.source == "demo"
    assert request.disruption.person_id == "soprano_principal"
    assert "copy" not in request.disruption.model_dump()


def test_non_demo_incident_still_rejects_presentation_copy_field():
    with pytest.raises(ValidationError):
        IncidentRequest.model_validate(
            {
                "scenario_id": "opera",
                "source": "api",
                "disruption": {
                    "person_id": "soprano_principal",
                    "start": "08:00",
                    "end": "14:00",
                    "reason": "illness",
                    "copy": "presentation-only text",
                },
            }
        )


@pytest.mark.parametrize(
    "start,end", [("14:00", "08:00"), ("08:00", "08:00"), ("25:00", "26:00")]
)
def test_disruption_rejects_malformed_intervals(start, end):
    with pytest.raises(ValidationError):
        Disruption(
            person_id="soprano_principal",
            start=start,
            end=end,
            reason="illness",
        )


def test_disruption_rejects_control_characters():
    with pytest.raises(ValidationError):
        Disruption(
            person_id="soprano_principal",
            start="08:00",
            end="14:00",
            reason="illness\u0000send",
        )
