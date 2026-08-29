#!/usr/bin/env python3
from __future__ import annotations

import json
import pathlib
import signal
import subprocess
import time
from datetime import datetime, timezone

from playwright.sync_api import sync_playwright

LIVE_URL = "https://places-again-674409858210.europe-west1.run.app"
E2E_RUN_URL = "https://github.com/rarescos-pixel/places-again/actions/runs/33255155489"
QUALITY_RUN_URL = "https://github.com/rarescos-pixel/places-again/actions/runs/33263263630"
ARCH_URL = "https://github.com/rarescos-pixel/places-again/blob/main/docs/architecture.svg"
OUT_DIR = pathlib.Path("runtime")
RAW_VIDEO = OUT_DIR / "places-again-submission-demo-raw.mp4"
FINAL_VIDEO = OUT_DIR / "places-again-submission-demo.mp4"
META = OUT_DIR / "demo-metadata.json"
PROOF_LOG = OUT_DIR / "live-demo-proof.txt"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def log(msg: str) -> None:
    print(f"[demo] {msg}", flush=True)


def start_capture() -> subprocess.Popen:
    cmd = [
        "ffmpeg", "-y", "-f", "x11grab", "-video_size", "1920x1080",
        "-framerate", "30", "-i", ":99.0", "-c:v", "libx264",
        "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart", str(RAW_VIDEO),
    ]
    log("Starting full desktop capture")
    return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)


def stop_capture(proc: subprocess.Popen) -> None:
    log("Stopping full desktop capture")
    proc.send_signal(signal.SIGINT)
    try:
        proc.wait(timeout=20)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=5)
    if proc.returncode not in (0, 255):
        err = proc.stderr.read() if proc.stderr else ""
        raise RuntimeError(f"ffmpeg capture failed with {proc.returncode}: {err[-3000:]}")


def normalize_video() -> None:
    subprocess.run([
        "ffmpeg", "-y", "-i", str(RAW_VIDEO), "-c:v", "libx264",
        "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart", "-an", str(FINAL_VIDEO),
    ], check=True)


def duration_seconds(path: pathlib.Path) -> float:
    result = subprocess.run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path),
    ], check=True, capture_output=True, text=True)
    return float(result.stdout.strip())


def start_visible_live_proof() -> tuple[subprocess.Popen, float]:
    command = (
        "set -o pipefail; "
        "printf '\\033[1;38;5;208mPLACES, AGAIN — UNEDITED LIVE PROOF OF ACTION\\033[0m\\n'; "
        "printf 'Public Google Cloud endpoint: %s\\n\\n' '" + LIVE_URL + "'; "
        "printf '$ python scripts/live_demo_proof.py\\n\\n'; "
        "python scripts/live_demo_proof.py 2>&1 | tee runtime/live-demo-proof.txt; "
        "rc=$?; printf '\\nExit code: %s\\n' \"$rc\"; "
        "if [ \"$rc\" -ne 0 ]; then printf '\\033[1;31mLIVE PROOF FAILED\\033[0m\\n'; sleep 8; exit \"$rc\"; fi; "
        "printf '\\033[1;32mLIVE PROOF PASSED — handing off directly to hosted build\\033[0m\\n'; sleep 3"
    )
    started = time.monotonic()
    proc = subprocess.Popen([
        "xterm", "-T", "Places, Again — Live Google Cloud Proof",
        "-fa", "DejaVu Sans Mono", "-fs", "14",
        "-geometry", "150x43+0+0", "-bg", "#080a0d", "-fg", "#f5f0e7",
        "-e", "bash", "-lc", command,
    ])
    return proc, started


def finish_visible_live_proof(proc: subprocess.Popen, started: float) -> float:
    rc = proc.wait(timeout=300)
    elapsed = time.monotonic() - started
    if rc != 0:
        raise RuntimeError(f"live proof terminal exited with {rc}")
    proof_text = PROOF_LOG.read_text(encoding="utf-8") if PROOF_LOG.exists() else ""
    required = [
        "[1] OPERA",
        "[2] REPLAY",
        "[3] FAIL CLOSED",
        "[4] COMMERCIAL FILM / BROADCAST",
        "FINAL_STATUS=SUCCESS",
    ]
    missing = [marker for marker in required if marker not in proof_text]
    if missing:
        raise RuntimeError(f"live proof log missing required markers: {missing}")
    with PROOF_LOG.open("a", encoding="utf-8") as f:
        f.write("\nPARENT_VERIFIED_LIVE_PROOF_EXIT_CODE=0\n")
    return elapsed


def proof_event_id(section_marker: str) -> str:
    proof_text = PROOF_LOG.read_text(encoding="utf-8")
    in_section = False
    for raw in proof_text.splitlines():
        line = raw.strip()
        if line.startswith(section_marker):
            in_section = True
            continue
        if in_section and line.startswith("["):
            break
        if in_section and line.startswith("event "):
            parts = line.split()
            if len(parts) >= 2:
                return parts[-1]
    raise RuntimeError(f"could not recover event id for {section_marker}")


def set_overlay(page, kicker: str, text: str) -> None:
    page.evaluate(
        """
        ({kicker, text}) => {
          let box = document.getElementById('places-again-auto-caption');
          if (!box) {
            box = document.createElement('div');
            box.id = 'places-again-auto-caption';
            (document.body || document.documentElement).appendChild(box);
          }
          box.style.cssText = `position:fixed;left:72px;right:72px;bottom:26px;top:auto;z-index:2147483647;background:rgba(8,10,13,.94);border:1px solid rgba(255,255,255,.22);border-radius:14px;padding:17px 22px 18px;color:#f7f3ec;font-family:Inter,Arial,sans-serif;box-shadow:0 14px 50px rgba(0,0,0,.5);pointer-events:none;`;
          box.innerHTML = `<div style="font-size:15px;text-transform:uppercase;letter-spacing:.13em;color:#ff8a5b;font-weight:800;margin-bottom:5px">${kicker}</div><div style="font-size:29px;line-height:1.25;font-weight:650">${text}</div>`;
        }
        """,
        {"kicker": kicker, "text": text},
    )


def set_compact_top_overlay(page, kicker: str, text: str) -> None:
    page.evaluate(
        """
        ({kicker, text}) => {
          let box = document.getElementById('places-again-auto-caption');
          if (!box) {
            box = document.createElement('div');
            box.id = 'places-again-auto-caption';
            (document.body || document.documentElement).appendChild(box);
          }
          box.style.cssText = `position:fixed;left:72px;right:72px;top:14px;bottom:auto;z-index:2147483647;background:rgba(8,10,13,.94);border:1px solid rgba(255,255,255,.22);border-radius:11px;padding:10px 17px 11px;color:#f7f3ec;font-family:Inter,Arial,sans-serif;box-shadow:0 8px 28px rgba(0,0,0,.45);pointer-events:none;`;
          box.innerHTML = `<div style="font-size:12px;text-transform:uppercase;letter-spacing:.12em;color:#ff8a5b;font-weight:800;margin-bottom:3px">${kicker}</div><div style="font-size:21px;line-height:1.18;font-weight:700">${text}</div>`;
        }
        """,
        {"kicker": kicker, "text": text},
    )


def show_address_bar(page, seconds: float = 3.0) -> None:
    page.keyboard.press("Control+L")
    time.sleep(seconds)
    page.keyboard.press("Escape")


def render_captured_opera_event(app) -> str:
    event_id = proof_event_id("[1] OPERA")
    app.evaluate(
        """
        async (eventId) => {
          const response = await fetch(`/api/events/${eventId}`);
          if (!response.ok) throw new Error(`event fetch failed: ${response.status}`);
          const event = await response.json();
          renderEvent(event);
          await loadState();
        }
        """,
        event_id,
    )
    return event_id


def focus_recovered_product(app) -> None:
    app.evaluate(
        """
        () => {
          document.documentElement.style.scrollBehavior = 'auto';
          document.body.style.scrollBehavior = 'auto';
          const cascade = document.getElementById('cascade');
          const y = cascade.getBoundingClientRect().top + window.scrollY - 108;
          window.scrollTo({top: Math.max(0, y), behavior: 'auto'});
        }
        """
    )


def show_problem_cold_open(app) -> None:
    """Lead with the operational problem before asking the judge to read proof."""
    app.bring_to_front()
    app.evaluate("window.scrollTo({top:0,behavior:'auto'})")
    set_overlay(
        app,
        "08:05 — ONE ABSENCE BREAKS THE DAY",
        "3 activities · 6 people · 3 resources · 12 person-hours at risk. One incident starts autonomous recovery — no step-by-step human guidance.",
    )
    time.sleep(9)


def browser_evidence(context, app, browser) -> None:
    # The app is deliberately preloaded before capture. After the continuous
    # live proof closes, the same browser is ready for an immediate product
    # handoff with no blank desktop or startup frames.
    app.bring_to_front()
    opera_event_id = render_captured_opera_event(app)
    show_address_bar(app, 2.5)
    focus_recovered_product(app)
    time.sleep(0.6)
    set_compact_top_overlay(
        app,
        "LIVE PRODUCT RECOVERY · SAME CAPTURED EVENT",
        "AT RISK → RECOVERED · 3/3 activities · 12 person-hours · Gemini selected · deterministic PASS",
    )
    time.sleep(8.5)
    log(f"Rendered captured Opera event in public UI: {opera_event_id}")

    cap = context.new_page()
    cap.goto(LIVE_URL + "/api/capabilities", wait_until="networkidle", timeout=60000)
    cap.bring_to_front()
    set_overlay(cap, "GOOGLE CLOUD BACKEND", "Cloud Run · Google Pub/Sub · private worker · Google ADK · Gemini 3.5 on Vertex AI · Firestore.")
    show_address_bar(cap, 3)
    time.sleep(8)

    e2e = context.new_page()
    e2e.goto(E2E_RUN_URL, wait_until="domcontentloaded", timeout=60000)
    e2e.bring_to_front()
    set_overlay(e2e, "INDEPENDENT EXTERNAL EVIDENCE", "A GitHub-hosted runner independently opened the public UI and executed the real cloud path end to end.")
    time.sleep(9)

    arch = context.new_page()
    arch.goto(ARCH_URL, wait_until="domcontentloaded", timeout=60000)
    arch.bring_to_front()
    set_overlay(arch, "ARCHITECTURE", "Public Cloud Run API → Pub/Sub/OIDC → private worker → ADK + Gemini → deterministic re-verification → Firestore transaction.")
    time.sleep(10)

    quality = context.new_page()
    quality.goto(QUALITY_RUN_URL, wait_until="domcontentloaded", timeout=60000)
    quality.bring_to_front()
    set_overlay(quality, "REPRODUCIBLE SAFETY EVIDENCE", "65 automated tests and 52 labeled evaluation cases cover replay, stale state, concurrency, model failure, prompt injection and fail-closed behavior.")
    time.sleep(10)

    app.bring_to_front()
    app.evaluate("window.scrollTo({top:0,behavior:'auto'})")
    set_overlay(app, "PLACES, AGAIN", "Gemini decides what makes operational sense. Deterministic code proves what is safe. The plan breaks. The operation recovers.")
    time.sleep(10)
    browser.close()


def main() -> None:
    started = datetime.now(timezone.utc)
    capture = None
    proof_elapsed = 0.0
    with sync_playwright() as p:
        # Preload the exact public build before recording. The judge sees the
        # product/problem first; the proof terminal then opens above it and is
        # captured continuously from trigger through terminal state.
        browser = p.chromium.launch(
            headless=False,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--window-position=0,0", "--window-size=1920,1080", "--start-maximized"],
        )
        context = browser.new_context(viewport={"width": 1880, "height": 930})
        app = context.new_page()
        app.goto(LIVE_URL, wait_until="networkidle", timeout=60000)

        capture = start_capture()
        try:
            time.sleep(1)
            show_problem_cold_open(app)

            proof_proc, proof_started = start_visible_live_proof()
            # Give the window manager time to put xterm above the browser. Once
            # it appears, the actual Proof of Action runs without cuts until its
            # terminal state.
            time.sleep(1.2)
            proof_elapsed = finish_visible_live_proof(proof_proc, proof_started)
            log(f"Live proof elapsed: {proof_elapsed:.2f}s")

            # xterm has closed. Render the exact captured Opera event into the
            # already-open public app before the rest of the evidence tour.
            browser_evidence(context, app, browser)
            time.sleep(1)
        finally:
            if capture is not None:
                stop_capture(capture)

    normalize_video()
    duration = duration_seconds(FINAL_VIDEO)
    if duration > 240:
        raise RuntimeError(f"Generated video is {duration:.2f}s, above contest cap")
    proof_text = PROOF_LOG.read_text(encoding="utf-8") if PROOF_LOG.exists() else ""
    if "PARENT_VERIFIED_LIVE_PROOF_EXIT_CODE=0" not in proof_text:
        raise RuntimeError("live proof process did not persist verified zero exit code")
    META.write_text(json.dumps({
        "generated_at": started.isoformat(),
        "duration_seconds": round(duration, 3),
        "live_proof_elapsed_seconds": round(proof_elapsed, 3),
        "live_url": LIVE_URL,
        "runtime_source_commit": "5d6b5662cb63f8af1d414f01570c9991278b3e8e",
        "repository_evidence_head": "d8074322fa39cd6eb6a7fa7eb038e39d4fffd4d3",
        "quality_gate_run": "33263263630",
        "proof_mode": "product-first cold open followed by unedited visible terminal execution against public Cloud Run endpoint",
        "proof_cases": [
            "opera autonomous safe recovery",
            "replay exactly-once business effect",
            "adversarial human_required",
            "commercial film/broadcast autonomous recovery",
        ],
        "product_ui_proof": "problem-first hosted-product cold open, then same captured Opera event re-rendered by the public app after live proof with recovered cascade and decision proof framed on screen",
        "proof_process_exit_code": 0,
        "transition": "9-second product/problem cold open; continuous xterm proof; direct handoff back to preloaded hosted build",
        "audio": "none; English on-screen text/captions",
    }, indent=2) + "\n", encoding="utf-8")
    log(f"FINAL_STATUS=SUBMISSION_VIDEO_BUILT duration={duration:.2f}s")


if __name__ == "__main__":
    main()
