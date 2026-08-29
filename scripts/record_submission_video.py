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
QUALITY_RUN_URL = "https://github.com/rarescos-pixel/places-again/actions/runs/33255724383"
ARCH_URL = "https://raw.githubusercontent.com/rarescos-pixel/places-again/main/docs/architecture.svg"
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


def run_visible_live_proof() -> float:
    command = (
        "printf '\\033[1;38;5;208mPLACES, AGAIN — UNEDITED LIVE PROOF OF ACTION\\033[0m\\n'; "
        "printf 'Public Google Cloud endpoint: %s\\n\\n' '" + LIVE_URL + "'; "
        "printf '$ python scripts/live_demo_proof.py\\n\\n'; "
        "python scripts/live_demo_proof.py 2>&1 | tee runtime/live-demo-proof.txt; "
        "rc=${PIPESTATUS[0]}; printf '\\nExit code: %s\\n' \"$rc\"; "
        "if [ \"$rc\" -ne 0 ]; then printf '\\033[1;31mLIVE PROOF FAILED\\033[0m\\n'; sleep 12; exit \"$rc\"; fi; "
        "printf '\\033[1;32mLIVE PROOF PASSED — keeping final evidence on screen\\033[0m\\n'; sleep 10"
    )
    started = time.monotonic()
    proc = subprocess.Popen([
        "xterm", "-T", "Places, Again — Live Google Cloud Proof",
        "-fa", "DejaVu Sans Mono", "-fs", "14",
        "-geometry", "150x43+0+0", "-bg", "#080a0d", "-fg", "#f5f0e7",
        "-e", "bash", "-lc", command,
    ])
    rc = proc.wait(timeout=300)
    elapsed = time.monotonic() - started
    if rc != 0:
        raise RuntimeError(f"live proof terminal exited with {rc}")
    return elapsed


def set_overlay(page, kicker: str, text: str) -> None:
    page.evaluate(
        """
        ({kicker, text}) => {
          let box = document.getElementById('places-again-auto-caption');
          if (!box) {
            box = document.createElement('div');
            box.id = 'places-again-auto-caption';
            box.style.cssText = `position:fixed;left:72px;right:72px;bottom:26px;z-index:2147483647;background:rgba(8,10,13,.94);border:1px solid rgba(255,255,255,.22);border-radius:14px;padding:17px 22px 18px;color:#f7f3ec;font-family:Inter,Arial,sans-serif;box-shadow:0 14px 50px rgba(0,0,0,.5);pointer-events:none;`;
            document.documentElement.appendChild(box);
          }
          box.innerHTML = `<div style="font-size:15px;text-transform:uppercase;letter-spacing:.13em;color:#ff8a5b;font-weight:800;margin-bottom:5px">${kicker}</div><div style="font-size:29px;line-height:1.25;font-weight:650">${text}</div>`;
        }
        """,
        {"kicker": kicker, "text": text},
    )


def show_address_bar(page, seconds: float = 3.0) -> None:
    page.keyboard.press("Control+L")
    time.sleep(seconds)
    page.keyboard.press("Escape")


def browser_evidence() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--window-position=0,0", "--window-size=1920,1080", "--start-maximized"],
        )
        context = browser.new_context(viewport={"width": 1880, "height": 930})

        app = context.new_page()
        app.goto(LIVE_URL, wait_until="networkidle", timeout=60000)
        app.bring_to_front()
        set_overlay(app, "PUBLIC HOSTED BUILD", "This is the judge-accessible Cloud Run application. The live proof just executed against this exact .run.app backend.")
        show_address_bar(app, 4)
        time.sleep(7)

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
        arch.goto(ARCH_URL, wait_until="load", timeout=60000)
        arch.bring_to_front()
        set_overlay(arch, "ARCHITECTURE", "Public Cloud Run API → Pub/Sub/OIDC → private worker → ADK + Gemini → deterministic re-verification → Firestore transaction.")
        time.sleep(10)

        quality = context.new_page()
        quality.goto(QUALITY_RUN_URL, wait_until="domcontentloaded", timeout=60000)
        quality.bring_to_front()
        set_overlay(quality, "REPRODUCIBLE SAFETY EVIDENCE", "59 automated tests and 52 labeled evaluation cases cover replay, stale state, concurrency, model failure, prompt injection and fail-closed behavior.")
        time.sleep(10)

        app.bring_to_front()
        app.evaluate("window.scrollTo(0,0)")
        set_overlay(app, "PLACES, AGAIN", "Gemini decides what makes operational sense. Deterministic code proves what is safe. The plan breaks. The operation recovers.")
        time.sleep(10)
        browser.close()


def main() -> None:
    started = datetime.now(timezone.utc)
    capture = start_capture()
    try:
        time.sleep(2)
        proof_elapsed = run_visible_live_proof()
        log(f"Live proof elapsed: {proof_elapsed:.2f}s")
        browser_evidence()
        time.sleep(2)
    finally:
        stop_capture(capture)

    normalize_video()
    duration = duration_seconds(FINAL_VIDEO)
    if duration > 240:
        raise RuntimeError(f"Generated video is {duration:.2f}s, above contest cap")
    if not PROOF_LOG.exists() or "FINAL_STATUS=SUCCESS" not in PROOF_LOG.read_text(encoding="utf-8"):
        raise RuntimeError("live proof log does not contain FINAL_STATUS=SUCCESS")
    META.write_text(json.dumps({
        "generated_at": started.isoformat(),
        "duration_seconds": round(duration, 3),
        "live_proof_elapsed_seconds": round(proof_elapsed, 3),
        "live_url": LIVE_URL,
        "runtime_source_commit": "5d6b5662cb63f8af1d414f01570c9991278b3e8e",
        "proof_mode": "unedited visible terminal execution against public Cloud Run endpoint",
        "proof_cases": ["opera autonomous safe recovery", "replay exactly-once business effect", "adversarial human_required", "commercial film/broadcast autonomous recovery"],
        "audio": "none; English on-screen text/captions",
    }, indent=2) + "\n", encoding="utf-8")
    log(f"FINAL_STATUS=SUBMISSION_VIDEO_BUILT duration={duration:.2f}s")


if __name__ == "__main__":
    main()
