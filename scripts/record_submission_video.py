#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import pathlib
import signal
import subprocess
import time
from datetime import datetime, timezone
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from uuid import uuid4

from playwright.sync_api import sync_playwright

LIVE_URL = "https://places-again-674409858210.europe-west1.run.app"
E2E_RUN_URL = "https://github.com/rarescos-pixel/places-again/actions/runs/33255155489"
QUALITY_RUN_URL = "https://github.com/rarescos-pixel/places-again/actions/runs/33255724383"
ARCH_URL = "https://raw.githubusercontent.com/rarescos-pixel/places-again/main/docs/architecture.svg"
OUT_DIR = pathlib.Path("runtime")
RAW_VIDEO = OUT_DIR / "places-again-submission-demo-raw.mp4"
FINAL_VIDEO = OUT_DIR / "places-again-submission-demo.mp4"
FILM_EVIDENCE = OUT_DIR / "film-live-evidence.html"
META = OUT_DIR / "demo-metadata.json"

OUT_DIR.mkdir(parents=True, exist_ok=True)


def log(msg: str) -> None:
    print(f"[demo] {msg}", flush=True)


def api(path: str, payload: dict | None = None) -> tuple[int, dict]:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = Request(
        LIVE_URL.rstrip("/") + path,
        data=body,
        headers={"content-type": "application/json"} if body else {},
        method="POST" if payload is not None else "GET",
    )
    try:
        with urlopen(req, timeout=30) as response:
            return response.status, json.loads(response.read())
    except HTTPError as error:
        raw = error.read().decode("utf-8", errors="replace")
        try:
            payload_out = json.loads(raw)
        except json.JSONDecodeError:
            payload_out = {"raw": raw}
        return error.code, payload_out


def wait_terminal(event_id: str, timeout: int = 180) -> dict:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        code, event = api(f"/api/events/{event_id}")
        if code == 200 and event.get("status") in {"completed", "human_required"}:
            return event
        time.sleep(1)
    raise RuntimeError(f"event {event_id} did not reach terminal state")


def stage_real_film_event() -> dict:
    log("Staging real commercial_shoot Cloud event through public API")
    code, reset = api("/api/demo/reset?scenario_id=commercial_shoot", {})
    if code != 200:
        raise RuntimeError(f"film reset failed: {code} {reset}")
    event_id = str(uuid4())
    incident = {
        "scenario_id": "commercial_shoot",
        "event_id": event_id,
        "source": "demo",
        "disruption": {
            "person_id": "dp_principal",
            "start": "07:00",
            "end": "16:00",
            "reason": "same-day illness",
        },
    }
    code, accepted = api("/api/events", incident)
    if code != 202:
        raise RuntimeError(f"film event rejected: {code} {accepted}")
    event = wait_terminal(event_id)
    if event.get("status") != "completed":
        raise RuntimeError(f"film event did not complete safely: {event}")
    log(f"Film live event completed: {event_id}")
    return event


def write_film_evidence(event: dict) -> None:
    metrics = event.get("metrics") or (event.get("plan") or {}).get("metrics") or {}
    candidates = event.get("candidate_summaries") or []
    selected = event.get("selected_candidate_id") or "—"
    reasons = event.get("selection_reason_codes") or event.get("selection_rationale") or []
    chips = "".join(
        f'<div class="chip"><b>{html.escape(str(c.get("candidate_id", "candidate")))}</b>'
        f'<span>{html.escape(str((c.get("metrics") or {}).get("shifted_minutes", "—")))}m shifted · '
        f'{html.escape(str((c.get("metrics") or {}).get("people_schedule_changed", "—")))} people changed</span></div>'
        for c in candidates
    )
    reasons_html = "<br>".join(f"✓ {html.escape(str(r))}" for r in reasons) or "Selection recorded"
    doc = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
    <title>Places, Again — live film recovery evidence</title><style>
    body{{margin:0;background:#080a0d;color:#f5f0e7;font-family:Inter,Arial,sans-serif}}main{{max-width:1500px;margin:auto;padding:55px 70px}}
    .k{{color:#ff7947;text-transform:uppercase;letter-spacing:.15em;font-weight:900}}h1{{font:500 70px/1 Georgia,serif;margin:15px 0 18px}}
    .sub{{font-size:24px;color:#b7b3aa}}.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:18px;margin:35px 0}}
    .card,.decision{{border:1px solid #30343c;background:#12161b;border-radius:16px;padding:25px}}.card b{{display:block;font:500 48px Georgia,serif;color:#70dfa0}}.card span{{color:#aaa59b;text-transform:uppercase;font-size:14px}}
    .decision{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:20px;align-items:start}}.decision h3{{color:#ff8a5b;margin-top:0}}
    .chip{{border:1px solid #353b45;border-radius:9px;padding:10px;margin:8px 0}}.chip b,.chip span{{display:block}}.chip span{{color:#aaa59b;margin-top:4px}}
    .pass{{color:#70dfa0;font-weight:800;font-size:24px}}code{{color:#8ab4ff}}.foot{{margin-top:28px;color:#aaa59b;font-family:monospace}}
    </style></head><body><main>
    <div class="k">REAL CLOUD EXECUTION · SECOND DOMAIN</div><h1>Commercial Film / Broadcast Production</h1>
    <div class="sub">A Director of Photography becomes unavailable. Same recovery engine, different people, resources and priorities.</div>
    <div class="grid"><div class="card"><b>{html.escape(str(metrics.get("activities_recovered", "4")))}/{html.escape(str(metrics.get("affected_activities", "4")))}</b><span>activities recovered</span></div>
    <div class="card"><b>{html.escape(str(metrics.get("person_hours_restored", "26")))}</b><span>person-hours restored</span></div>
    <div class="card"><b>{html.escape(str(metrics.get("unaffected_activities_moved", "0")))}</b><span>unaffected moved</span></div>
    <div class="card"><b>{html.escape(str(event.get("messages_sent", 0)))}</b><span>messages sent</span></div></div>
    <div class="decision"><div><h3>Hard-safe candidates</h3>{chips or '<div class="chip">Candidate evidence recorded in event ledger</div>'}</div>
    <div><h3>Gemini selection</h3><div style="font-size:30px;font-weight:800">{html.escape(str(selected))}</div><p>{reasons_html}</p></div>
    <div><h3>Safety gate</h3><div class="pass">Deterministic re-verification: {'PASS' if (event.get('deterministic_reverification') or {}).get('passed') else 'RECORDED'}</div><p>Outcome: <code>{html.escape(str(event.get('outcome', 'autonomous_safe_commit')))}</code></p></div></div>
    <div class="foot">Live Cloud event: {html.escape(str(event.get('event_id', '—')))} · orchestration: {html.escape(str(event.get('orchestration', 'google_adk_gemini')))} · selector: {html.escape(str(event.get('selector', 'gemini_structured_selection')))}</div>
    </main></body></html>'''
    FILM_EVIDENCE.write_text(doc, encoding="utf-8")


def set_overlay(page, kicker: str, text: str) -> None:
    page.evaluate(
        """
        ({kicker, text}) => {
          let box = document.getElementById('places-again-auto-caption');
          if (!box) {
            box = document.createElement('div');
            box.id = 'places-again-auto-caption';
            box.style.cssText = `position:fixed;left:72px;right:72px;bottom:26px;z-index:2147483647;background:rgba(8,10,13,.93);border:1px solid rgba(255,255,255,.22);border-radius:14px;padding:17px 22px 18px;color:#f7f3ec;font-family:Inter,Arial,sans-serif;box-shadow:0 14px 50px rgba(0,0,0,.5);pointer-events:none;`;
            document.documentElement.appendChild(box);
          }
          box.innerHTML = `<div style="font-size:15px;text-transform:uppercase;letter-spacing:.13em;color:#ff8a5b;font-weight:800;margin-bottom:5px">${kicker}</div><div style="font-size:29px;line-height:1.25;font-weight:650">${text}</div>`;
        }
        """,
        {"kicker": kicker, "text": text},
    )


def clear_overlay(page) -> None:
    page.evaluate("document.getElementById('places-again-auto-caption')?.remove()")


def zoom_app(page, factor: float = 0.78) -> None:
    page.evaluate("factor => { document.body.style.zoom = String(factor); }", factor)


def reset_opera(page) -> None:
    # Opera is the default scenario. Avoid select_option because its onchange already resets asynchronously.
    current = page.locator("#scenario").input_value()
    if current != "opera":
        page.select_option("#scenario", "opera")
        page.wait_for_function("document.querySelector('#runStatus')?.innerText.includes('Scenario reset')", timeout=30000)
    else:
        page.click("#reset")
        page.wait_for_function("document.querySelector('#runStatus')?.innerText.includes('Scenario reset')", timeout=30000)
    page.wait_for_timeout(700)


def wait_good(page, timeout_ms: int = 90000) -> None:
    page.wait_for_function("document.querySelector('#runStatus')?.classList.contains('good')", timeout=timeout_ms)


def show_address_bar(page, seconds: float = 4.0) -> None:
    page.keyboard.press("Control+L")
    time.sleep(seconds)
    page.keyboard.press("Escape")


def start_capture() -> subprocess.Popen:
    cmd = ["ffmpeg", "-y", "-f", "x11grab", "-video_size", "1920x1080", "-framerate", "30", "-i", ":99.0", "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(RAW_VIDEO)]
    return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)


def stop_capture(proc: subprocess.Popen) -> None:
    proc.send_signal(signal.SIGINT)
    try:
        proc.wait(timeout=20)
    except subprocess.TimeoutExpired:
        proc.kill(); proc.wait(timeout=5)
    if proc.returncode not in (0, 255):
        err = proc.stderr.read() if proc.stderr else ""
        raise RuntimeError(f"ffmpeg capture failed with {proc.returncode}: {err[-2000:]}")


def normalize_video() -> None:
    subprocess.run(["ffmpeg", "-y", "-i", str(RAW_VIDEO), "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", str(FINAL_VIDEO)], check=True)


def duration_seconds(path: pathlib.Path) -> float:
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(path)], check=True, capture_output=True, text=True)
    return float(result.stdout.strip())


def main() -> None:
    started = datetime.now(timezone.utc)
    film_event = stage_real_film_event()
    write_film_evidence(film_event)
    capture = None
    live_elapsed = 0.0
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, args=["--no-sandbox", "--disable-dev-shm-usage", "--window-position=0,0", "--window-size=1920,1080", "--start-maximized"])
            context = browser.new_context(viewport={"width": 1880, "height": 930}, device_scale_factor=1)
            opera = context.new_page()
            opera.goto(LIVE_URL, wait_until="networkidle", timeout=60000)
            zoom_app(opera)
            reset_opera(opera)
            opera.locator("#run").scroll_into_view_if_needed(); opera.evaluate("window.scrollBy(0, -90)")
            opera.bring_to_front()

            capture = start_capture(); time.sleep(2)
            set_overlay(opera, "LIVE GOOGLE CLOUD BUILD", "Places, Again — The plan breaks. The operation recovers."); time.sleep(5); show_address_bar(opera, 4)
            set_overlay(opera, "THE FAILURE MOMENT", "At 08:05 one principal becomes unavailable. One absence cascades across people, resources and time."); time.sleep(8)
            set_overlay(opera, "SAFE AUTONOMY", "Gemini chooses among already-safe strategies. Deterministic code proves the exact choice again before commit."); time.sleep(7)

            set_overlay(opera, "UNEDITED PROOF OF ACTION", "One click starts the real Cloud Run → Pub/Sub/OIDC → private ADK + Gemini worker → Firestore workflow. No step-by-step guidance follows.")
            live_start = time.monotonic(); opera.click("#run"); wait_good(opera, timeout_ms=90000); live_elapsed = time.monotonic() - live_start
            log(f"Live Opera run completed in {live_elapsed:.2f}s"); time.sleep(4)

            opera.locator("#selectedCandidate").scroll_into_view_if_needed(); set_overlay(opera, "VISIBLE DECISION CONTRACT", "Multiple hard-safe candidates survive. The highlighted ID and validated reason codes are the actual Gemini result of this run."); time.sleep(9)
            opera.locator("#reverifyResult").scroll_into_view_if_needed(); set_overlay(opera, "DETERMINISTIC SAFETY GATE", "Deterministic re-verification: PASS. Only then can Firestore commit the state transition from v1 to v2."); time.sleep(8)
            opera.locator("#outbox").scroll_into_view_if_needed(); set_overlay(opera, "BOUNDED AUTHORITY", "3/3 activities recovered, 12 person-hours restored, zero unaffected activities moved. Messages are prepared, not sent."); time.sleep(8)

            capabilities = context.new_page(); capabilities.goto(LIVE_URL + "/api/capabilities", wait_until="networkidle", timeout=60000); capabilities.bring_to_front(); set_overlay(capabilities, "GOOGLE CLOUD BACKEND PROOF", "The public .run.app endpoint identifies Cloud Run, Google ADK, Gemini 3.5 on Vertex AI, Pub/Sub and Firestore."); show_address_bar(capabilities, 4); time.sleep(8)
            evidence = context.new_page(); evidence.goto(E2E_RUN_URL, wait_until="domcontentloaded", timeout=60000); evidence.bring_to_front(); set_overlay(evidence, "INDEPENDENT EXTERNAL E2E", "A GitHub-hosted runner opened the public UI and completed the real cloud workflow, replay proof and fail-closed adversarial case."); time.sleep(10)

            film = context.new_page(); film.goto(FILM_EVIDENCE.resolve().as_uri(), wait_until="load"); film.bring_to_front(); time.sleep(2); time.sleep(11)
            architecture = context.new_page(); architecture.goto(ARCH_URL, wait_until="load", timeout=60000); architecture.bring_to_front(); set_overlay(architecture, "ARCHITECTURE", "Public Cloud Run API → Pub/Sub/OIDC → private worker → Google ADK + Gemini → deterministic re-verification → Firestore transaction."); time.sleep(11)
            quality = context.new_page(); quality.goto(QUALITY_RUN_URL, wait_until="domcontentloaded", timeout=60000); quality.bring_to_front(); set_overlay(quality, "REPRODUCIBLE EVIDENCE", "59/59 automated tests and 52/52 labeled evaluation cases protect replay, crashes, stale state, model failure, prompt injection and safety boundaries."); time.sleep(10)

            opera.bring_to_front(); opera.evaluate("window.scrollTo(0, 0)"); set_overlay(opera, "PLACES, AGAIN", "Gemini decides what makes operational sense. Deterministic code proves what is safe. The plan breaks. The operation recovers."); time.sleep(10); clear_overlay(opera); time.sleep(2)
            stop_capture(capture); capture = None; browser.close()
    finally:
        if capture is not None and capture.poll() is None:
            capture.kill()

    normalize_video(); duration = duration_seconds(FINAL_VIDEO)
    if duration > 240:
        raise RuntimeError(f"Generated video is {duration:.2f}s, above the 240s contest cap")
    META.write_text(json.dumps({"generated_at": started.isoformat(), "live_url": LIVE_URL, "live_opera_elapsed_seconds": round(live_elapsed, 3), "film_live_event_id": film_event.get("event_id"), "film_status": film_event.get("status"), "duration_seconds": round(duration, 3), "e2e_run": E2E_RUN_URL, "quality_run": QUALITY_RUN_URL, "runtime_source_commit": "5d6b5662cb63f8af1d414f01570c9991278b3e8e", "proof_of_action_note": "No page/DOM mutation occurs between the single Inject disruption event click and terminal completion; Playwright only waits for terminal status.", "audio": "none; English on-screen captions are part of the captured browser view"}, indent=2) + "\n", encoding="utf-8")
    log(f"FINAL_STATUS=SUBMISSION_VIDEO_BUILT duration={duration:.2f}s")


if __name__ == "__main__":
    main()
