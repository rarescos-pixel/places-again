from pathlib import Path


def test_demo_ui_does_not_send_presentation_copy_in_disruption_payload():
    html = Path("static/index.html").read_text(encoding="utf-8")
    assert "disruption:configs[scenario]" not in html
    assert "const {copy,...disruption}=configs[scenario]" in html
    assert "disruption};" in html
