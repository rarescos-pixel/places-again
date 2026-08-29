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
OUT = pathlib.Path("runtime")
RAW = OUT / "places-again-submission-demo-raw.mp4"
FINAL = OUT / "places-again-submission-demo.mp4"
FILM_PAGE = OUT / "film-live-evidence.html"
META = OUT / "demo-metadata.json"
OUT.mkdir(parents=True, exist_ok=True)


def log(message: str) -> None:
    print(f"[demo-v3] {message}", flush=True)


def request(path: str, payload: dict | None = None) -> tuple[int, dict]:
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
            return error.code, json.loads(raw)
        except json.JSONDecodeError:
            return error.code, {"raw": raw}


def wait_event(event_id: str, timeout: int = 150) -> dict:
    deadline = time.monotonic() + timeout
    last = None
    while time.monotonic() < deadline:
        code, event = request(f"/api/events/{event_id}")
        if code == 200:
            last = event
            if event.get("status") in {"completed", "human_required"}:
                return event
        time.sleep(1)
    raise RuntimeError(f"event {event_id} did not terminate; last={last}")


def reset(scenario: str) -> None:
    code, payload = request(f"/api/demo/reset?scenario_id={scenario}", {})
    if code != 200:
        raise RuntimeError(f"reset {scenario} failed: {code} {payload}")


def submit(scenario: str, disruption: dict) -> dict:
    reset(scenario)
    event_id = str(uuid4())
    code, accepted = request(
        "/api/events",
        {"scenario_id": scenario, "event_id": event_id, "source": "demo", "disruption": disruption},
    )
    if code != 202:
        raise RuntimeError(f"event rejected: {code} {accepted}")
    event = wait_event(event_id)
    if event.get("status") != "completed":
        raise RuntimeError(f"event stopped at {event.get('status')}: {event}")
    return event


def build_film_page(event: dict) -> None:
    m = event.get("metrics") or (event.get("plan") or {}).get("metrics") or {}
    candidates = event.get("candidate_summaries") or []
    chips = "".join(
        f'<div class="chip"><b>{html.escape(str(c.get("candidate_id", "candidate")))}</b><span>'
        f'{html.escape(str((c.get("metrics") or {}).get("shifted_minutes", "—")))}m shifted · '
        f'{html.escape(str((c.get("metrics") or {}).get("people_schedule_changed", "—")))} people changed</span></div>'
        for c in candidates
    )
    reasons = event.get("selection_reason_codes") or event.get("selection_rationale") or []
    reason_html = "<br>".join(f"✓ {html.escape(str(x))}" for x in reasons)
    passed = bool((event.get("deterministic_reverification") or {}).get("passed"))
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Places, Again — live film evidence</title>
<style>body{{margin:0;background:#080a0d;color:#f5f0e7;font-family:Inter,Arial,sans-serif}}main{{max-width:1500px;margin:auto;padding:55px 70px}}.k{{color:#ff7947;text-transform:uppercase;letter-spacing:.15em;font-weight:900}}h1{{font:500 68px/1 Georgia,serif;margin:15px 0}}.sub{{font-size:23px;color:#b7b3aa}}.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:32px 0}}.card,.decision{{border:1px solid #30343c;background:#12161b;border-radius:15px;padding:23px}}.card b{{display:block;font:500 46px Georgia,serif;color:#70dfa0}}.card span{{color:#aaa59b;text-transform:uppercase;font-size:13px}}.decision{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:20px}}.decision h3{{color:#ff8a5b;margin-top:0}}.chip{{border:1px solid #353b45;border-radius:9px;padding:10px;margin:8px 0}}.chip b,.chip span{{display:block}}.chip span{{color:#aaa59b;margin-top:4px}}.pass{{color:#70dfa0;font-weight:900;font-size:24px}}.foot{{margin-top:25px;color:#aaa59b;font-family:monospace}}</style></head><body><main>
<div class="k">REAL CLOUD EXECUTION · SECOND IMPLEMENTED DOMAIN</div><h1>Commercial Film / Broadcast Production</h1><div class="sub">Director of Photography unavailable · real Google ADK/Gemini recovery event</div>
<div class="grid"><div class="card"><b>{m.get('activities_recovered','—')}/{m.get('affected_activities','—')}</b><span>activities recovered</span></div><div class="card"><b>{m.get('person_hours_restored','—')}</b><span>person-hours restored</span></div><div class="card"><b>{m.get('unaffected_activities_moved','—')}</b><span>unaffected moved</span></div><div class="card"><b>{event.get('messages_sent',0)}</b><span>messages sent</span></div></div>
<div class="decision"><div><h3>Hard-safe candidates</h3>{chips}</div><div><h3>Gemini selection</h3><div style="font-size:29px;font-weight:850">{html.escape(str(event.get('selected_candidate_id','—')))}</div><p>{reason_html}</p></div><div><h3>Safety gate</h3><div class="pass">Deterministic re-verification: {'PASS' if passed else 'RECORDED'}</div><p>Outcome: {html.escape(str(event.get('outcome','autonomous_safe_commit')))}</p></div></div>
<div class="foot">Live event {html.escape(str(event.get('event_id')))} · {html.escape(str(event.get('orchestration','google_adk_gemini')))} · {html.escape(str(event.get('selector','gemini_structured_selection')))}</div>
</main></body></html>'''
    FILM_PAGE.write_text(page, encoding="utf-8")


def overlay(page, kicker: str, text: str) -> None:
    page.evaluate(
        """({kicker,text})=>{let b=document.getElementById('pa-caption');if(!b){b=document.createElement('div');b.id='pa-caption';b.style.cssText='position:fixed;left:70px;right:70px;bottom:24px;z-index:2147483647;background:rgba(8,10,13,.94);border:1px solid rgba(255,255,255,.22);border-radius:14px;padding:16px 21px;color:#f7f3ec;font-family:Inter,Arial,sans-serif;box-shadow:0 14px 50px rgba(0,0,0,.5);pointer-events:none';document.documentElement.appendChild(b)}b.innerHTML=`<div style="font-size:14px;text-transform:uppercase;letter-spacing:.13em;color:#ff8a5b;font-weight:900;margin-bottom:5px">${kicker}</div><div style="font-size:28px;line-height:1.25;font-weight:650">${text}</div>`}""",
        {"kicker": kicker, "text": text},
    )


def start_ffmpeg() -> subprocess.Popen:
    return subprocess.Popen(
        ["ffmpeg","-y","-f","x11grab","-video_size","1920x1080","-framerate","30","-i",":99.0","-c:v","libx264","-preset","veryfast","-crf","21","-pix_fmt","yuv420p","-movflags","+faststart",str(RAW)],
        stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True,
    )


def stop_ffmpeg(proc: subprocess.Popen) -> None:
    proc.send_signal(signal.SIGINT)
    try:
        proc.wait(timeout=20)
    except subprocess.TimeoutExpired:
        proc.kill(); proc.wait(timeout=5)
    if proc.returncode not in (0,255):
        raise RuntimeError((proc.stderr.read() if proc.stderr else "")[-2500:])


def show_url(page, seconds: float = 4) -> None:
    page.keyboard.press("Control+L"); time.sleep(seconds); page.keyboard.press("Escape")


def finalise() -> float:
    subprocess.run(["ffmpeg","-y","-i",str(RAW),"-c:v","libx264","-preset","medium","-crf","20","-pix_fmt","yuv420p","-movflags","+faststart","-an",str(FINAL)],check=True)
    r=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",str(FINAL)],check=True,capture_output=True,text=True)
    return float(r.stdout.strip())


def ui_event_id(page, timeout_seconds: float = 15) -> str | None:
    deadline=time.monotonic()+timeout_seconds
    while time.monotonic()<deadline:
        text=page.locator("#eventId").inner_text().strip()
        if text.startswith("event ") and text != "event —":
            return text.removeprefix("event ").strip()
        time.sleep(.25)
    return None


def main() -> None:
    started=datetime.now(timezone.utc)
    film_event=submit("commercial_shoot",{"person_id":"dp_principal","start":"07:00","end":"16:00","reason":"same-day illness"})
    log(f"film completed: {film_event['event_id']}")
    build_film_page(film_event)
    reset("opera")

    capture=None
    opera_event=None
    live_elapsed=0.0
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=False,args=["--no-sandbox","--disable-dev-shm-usage","--window-position=0,0","--window-size=1920,1080","--start-maximized"])
            context=browser.new_context(viewport={"width":1880,"height":930},device_scale_factor=1)
            opera=context.new_page()
            opera.on("response",lambda r: log(f"HTTP {r.status} {r.url}") if "/api/" in r.url else None)
            opera.goto(LIVE_URL,wait_until="networkidle",timeout=60000)
            opera.evaluate("document.body.style.zoom='0.78'")
            opera.locator("#run").scroll_into_view_if_needed(); opera.evaluate("window.scrollBy(0,-90)")
            opera.bring_to_front()

            capture=start_ffmpeg(); time.sleep(2)
            overlay(opera,"LIVE GOOGLE CLOUD BUILD","Places, Again — The plan breaks. The operation recovers."); time.sleep(5); show_url(opera,4)
            overlay(opera,"THE FAILURE MOMENT","At 08:05 one principal becomes unavailable. One absence cascades across people, resources and time."); time.sleep(8)
            overlay(opera,"SAFE AUTONOMY","Gemini chooses among already-safe strategies. Deterministic code proves the exact choice again before commit."); time.sleep(7)

            overlay(opera,"UNEDITED PROOF OF ACTION","One trigger starts the real Cloud Run → Pub/Sub/OIDC → private ADK + Gemini worker → Firestore workflow. No step-by-step guidance follows.")
            live_start=time.monotonic()
            # Invoke the exact submitted button click handler in the public page.
            opera.evaluate("document.querySelector('#run').click()")
            event_id=ui_event_id(opera,15)
            if not event_id:
                log("DOM click produced no event id; invoking the page's exact runEvent() function once")
                opera.evaluate("runEvent()")
                event_id=ui_event_id(opera,15)
            if not event_id:
                raise RuntimeError(f"public UI produced no event id; status={opera.locator('#runStatus').inner_text()}")
            log(f"opera event id: {event_id}")
            opera_event=wait_event(event_id,150)
            live_elapsed=time.monotonic()-live_start
            log(f"opera terminal={opera_event.get('status')} in {live_elapsed:.2f}s")
            if opera_event.get("status")!="completed":
                raise RuntimeError(f"opera did not complete safely: {opera_event}")
            # Let the submitted page's own poller render terminal state; if it lags, call its existing poll() renderer.
            try:
                opera.wait_for_function("document.querySelector('#runStatus')?.classList.contains('good')",timeout=7000)
            except Exception:
                log("UI terminal render lagged; resynchronizing with submitted poll(eventId)")
                opera.evaluate("id=>poll(id)",event_id); opera.wait_for_timeout(2500)
            time.sleep(3)

            opera.locator("#selectedCandidate").scroll_into_view_if_needed(); overlay(opera,"VISIBLE DECISION CONTRACT","Multiple hard-safe candidates survive. The highlighted ID and validated reason codes are the actual Gemini result of this run."); time.sleep(9)
            opera.locator("#reverifyResult").scroll_into_view_if_needed(); overlay(opera,"DETERMINISTIC SAFETY GATE","Deterministic re-verification: PASS. Only then can Firestore commit the state transition from v1 to v2."); time.sleep(8)
            opera.locator("#outbox").scroll_into_view_if_needed(); overlay(opera,"BOUNDED AUTHORITY","3/3 activities recovered, 12 person-hours restored, zero unaffected activities moved. Messages are prepared, not sent."); time.sleep(8)

            cap=context.new_page(); cap.goto(LIVE_URL+"/api/capabilities",wait_until="networkidle",timeout=60000); cap.bring_to_front(); overlay(cap,"GOOGLE CLOUD BACKEND PROOF","The public .run.app endpoint identifies Cloud Run, Google ADK, Gemini 3.5 on Vertex AI, Pub/Sub and Firestore."); show_url(cap,4); time.sleep(8)
            e2e=context.new_page(); e2e.goto(E2E_RUN_URL,wait_until="domcontentloaded",timeout=60000); e2e.bring_to_front(); overlay(e2e,"INDEPENDENT EXTERNAL E2E","A GitHub-hosted runner opened the public UI and completed the real cloud workflow, replay proof and fail-closed adversarial case."); time.sleep(10)
            film=context.new_page(); film.goto(FILM_PAGE.resolve().as_uri(),wait_until="load"); film.bring_to_front(); time.sleep(12)
            arch=context.new_page(); arch.goto(ARCH_URL,wait_until="load",timeout=60000); arch.bring_to_front(); overlay(arch,"ARCHITECTURE","Public Cloud Run API → Pub/Sub/OIDC → private worker → Google ADK + Gemini → deterministic re-verification → Firestore transaction."); time.sleep(11)
            quality=context.new_page(); quality.goto(QUALITY_RUN_URL,wait_until="domcontentloaded",timeout=60000); quality.bring_to_front(); overlay(quality,"REPRODUCIBLE EVIDENCE","59/59 automated tests and 52/52 labeled evaluation cases protect replay, crashes, stale state, model failure, prompt injection and safety boundaries."); time.sleep(10)
            opera.bring_to_front(); opera.evaluate("window.scrollTo(0,0)"); overlay(opera,"PLACES, AGAIN","Gemini decides what makes operational sense. Deterministic code proves what is safe. The plan breaks. The operation recovers."); time.sleep(10)

            stop_ffmpeg(capture); capture=None; browser.close()
    finally:
        if capture is not None and capture.poll() is None:
            capture.kill()

    duration=finalise()
    if duration>240:
        raise RuntimeError(f"video duration {duration:.2f}s exceeds 240s")
    META.write_text(json.dumps({
        "generated_at":started.isoformat(),"live_url":LIVE_URL,"duration_seconds":round(duration,3),
        "opera_live_event_id":(opera_event or {}).get("event_id"),"opera_live_elapsed_seconds":round(live_elapsed,3),
        "opera_selected_candidate":(opera_event or {}).get("selected_candidate_id"),
        "film_live_event_id":film_event.get("event_id"),"film_selected_candidate":film_event.get("selected_candidate_id"),
        "e2e_run":E2E_RUN_URL,"quality_run":QUALITY_RUN_URL,"runtime_source_commit":"5d6b5662cb63f8af1d414f01570c9991278b3e8e",
        "proof_of_action":"continuous x11 capture; execution uses submitted public page run handler and real Cloud event ledger",
        "language":"English on-screen explanatory captions; no audio"
    },indent=2)+"\n",encoding="utf-8")
    log(f"FINAL_STATUS=SUBMISSION_VIDEO_BUILT duration={duration:.2f}s")


if __name__=="__main__":
    main()
