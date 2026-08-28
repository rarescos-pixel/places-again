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
