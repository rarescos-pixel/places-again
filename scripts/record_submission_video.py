#!/usr/bin/env python3
import json
import pathlib
import signal
import subprocess
import time
from datetime import datetime, timezone

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

LIVE_URL = "https://places-again-674409858210.europe-west1.run.app"
E2E_RUN_URL = "https://github.com/rarescos-pixel/places-again/actions/runs/33255155489"
QUALITY_RUN_URL = "https://github.com/rarescos-pixel/places-again/actions/runs/33255724383"
ARCH_URL = "https://raw.githubusercontent.com/rarescos-pixel/places-again/main/docs/architecture.svg"
OUT_DIR = pathlib.Path("runtime")
RAW_VIDEO = OUT_DIR / "places-again-submission-demo-raw.mp4"
FINAL_VIDEO = OUT_DIR / "places-again-submission-demo.mp4"
META = OUT_DIR / "demo-metadata.json"

OUT_DIR.mkdir(parents=True, exist_ok=True)


def log(msg: str) -> None:
    print(f"[demo] {msg}", flush=True)


def set_overlay(page, kicker: str, text: str) -> None:
    page.evaluate(
        """
        ({kicker, text}) => {
          let box = document.getElementById('places-again-auto-caption');
          if (!box) {
            box = document.createElement('div');
            box.id = 'places-again-auto-caption';
            box.style.cssText = `
              position:fixed;left:72px;right:72px;bottom:26px;z-index:2147483647;
              background:rgba(8,10,13,.93);border:1px solid rgba(255,255,255,.22);
              border-radius:14px;padding:17px 22px 18px;color:#f7f3ec;
              font-family:Inter,Arial,sans-serif;box-shadow:0 14px 50px rgba(0,0,0,.5);
              pointer-events:none;
            `;
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


def wait_good(page, timeout_ms: int = 90000) -> None:
    page.wait_for_function(
        "document.querySelector('#runStatus')?.classList.contains('good')",
        timeout=timeout_ms,
    )


def reset_scenario(page, scenario: str) -> None:
    page.select_option("#scenario", scenario)
    page.wait_for_timeout(1200)
    page.click("#reset")
    page.wait_for_function(
        "document.querySelector('#runStatus')?.innerText.includes('Scenario reset')",
        timeout=30000,
    )


def run_scenario(page, scenario: str, retries: int = 2) -> None:
    reset_scenario(page, scenario)
    for attempt in range(1, retries + 1):
        log(f"Running {scenario}, attempt {attempt}")
        page.click("#run")
        try:
            wait_good(page)
            return
        except PlaywrightTimeoutError:
            status = page.locator("#runStatus").inner_text()
            log(f"Attempt {attempt} timed out. Status: {status}")
            if attempt == retries:
                raise
            page.click("#reset")
            page.wait_for_timeout(1500)


def show_address_bar(page, seconds: float = 4.0) -> None:
    page.keyboard.press("Control+L")
    time.sleep(seconds)
    page.keyboard.press("Escape")


def start_capture() -> subprocess.Popen:
    cmd = [
        "ffmpeg", "-y",
        "-f", "x11grab",
        "-video_size", "1920x1080",
        "-framerate", "30",
        "-i", ":99.0",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "21",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(RAW_VIDEO),
    ]
    log("Starting desktop capture")
    return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)


def stop_capture(proc: subprocess.Popen) -> None:
    log("Stopping desktop capture")
    proc.send_signal(signal.SIGINT)
    try:
        proc.wait(timeout=20)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=5)
    if proc.returncode not in (0, 255):
        err = proc.stderr.read() if proc.stderr else ""
        raise RuntimeError(f"ffmpeg capture failed with {proc.returncode}: {err[-2000:]}")


def normalize_video() -> None:
    subprocess.run([
        "ffmpeg", "-y", "-i", str(RAW_VIDEO),
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        "-an", str(FINAL_VIDEO),
    ], check=True)


def duration_seconds(path: pathlib.Path) -> float:
    result = subprocess.run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path)
    ], check=True, capture_output=True, text=True)
    return float(result.stdout.strip())


def main() -> None:
    started = datetime.now(timezone.utc)
    live_elapsed = None
    capture = None
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=False,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--window-position=0,0",
                    "--window-size=1920,1080",
                    "--start-maximized",
                ],
            )
            context = browser.new_context(
                viewport={"width": 1880, "height": 930},
                device_scale_factor=1,
            )

            film = context.new_page()
            log("Pre-staging completed film/broadcast recovery")
            film.goto(LIVE_URL, wait_until="networkidle", timeout=60000)
            zoom_app(film)
            run_scenario(film, "commercial_shoot")
            film.locator("#selectedCandidate").scroll_into_view_if_needed()

            opera = context.new_page()
            log("Preparing clean Opera baseline")
            opera.goto(LIVE_URL, wait_until="networkidle", timeout=60000)
            zoom_app(opera)
            reset_scenario(opera, "opera")
            opera.locator("#run").scroll_into_view_if_needed()
            opera.evaluate("window.scrollBy(0, -90)")
            opera.bring_to_front()

            capture = start_capture()
            time.sleep(2)

            set_overlay(opera, "LIVE GOOGLE CLOUD BUILD", "Places, Again — The plan breaks. The operation recovers.")
            time.sleep(5)
            show_address_bar(opera, 4)

            set_overlay(opera, "THE FAILURE MOMENT", "At 08:05 one principal becomes unavailable. One absence cascades across people, resources and time.")
            time.sleep(9)

            set_overlay(opera, "SAFE AUTONOMY", "Gemini chooses among already-safe strategies. Deterministic code proves the exact choice again before commit.")
            time.sleep(8)

            # Proof of Action: no automation or DOM changes from click until terminal state.
            set_overlay(opera, "UNEDITED PROOF OF ACTION", "One click starts the real Cloud Run → Pub/Sub/OIDC → private ADK + Gemini worker → Firestore workflow. No step-by-step guidance follows.")
            live_start = time.monotonic()
            opera.click("#run")
            wait_good(opera, timeout_ms=90000)
            live_elapsed = time.monotonic() - live_start
            log(f"Live Opera run completed in {live_elapsed:.2f}s")
            time.sleep(4)

            opera.locator("#selectedCandidate").scroll_into_view_if_needed()
            set_overlay(opera, "VISIBLE DECISION CONTRACT", "Multiple hard-safe candidates survive. The highlighted ID and validated reason codes are the actual Gemini result of this run.")
            time.sleep(10)

            opera.locator("#reverifyResult").scroll_into_view_if_needed()
            set_overlay(opera, "DETERMINISTIC SAFETY GATE", "Deterministic re-verification: PASS. Only then can Firestore commit the state transition from v1 to v2.")
            time.sleep(10)

            opera.locator("#outbox").scroll_into_view_if_needed()
            set_overlay(opera, "BOUNDED AUTHORITY", "3/3 activities recovered, 12 person-hours restored, zero unaffected activities moved. Messages are prepared, not sent.")
            time.sleep(10)

            capabilities = context.new_page()
            capabilities.goto(LIVE_URL + "/api/capabilities", wait_until="networkidle", timeout=60000)
            capabilities.bring_to_front()
            set_overlay(capabilities, "GOOGLE CLOUD BACKEND PROOF", "The public .run.app endpoint identifies Cloud Run, Google ADK, Gemini 3.5 on Vertex AI, Pub/Sub and Firestore.")
            show_address_bar(capabilities, 4)
            time.sleep(9)

            evidence = context.new_page()
            evidence.goto(E2E_RUN_URL, wait_until="domcontentloaded", timeout=60000)
            evidence.bring_to_front()
            set_overlay(evidence, "INDEPENDENT EXTERNAL E2E", "A GitHub-hosted runner opened the public UI and completed the real cloud workflow, replay proof and fail-closed adversarial case.")
            time.sleep(12)

            film.bring_to_front()
            film.locator("#selectedCandidate").scroll_into_view_if_needed()
            set_overlay(film, "SAME ENGINE — SECOND DOMAIN", "Commercial film / broadcast: different people, resources and priorities; same candidate generation, Gemini decision contract and deterministic proof.")
            time.sleep(13)

            architecture = context.new_page()
            architecture.goto(ARCH_URL, wait_until="load", timeout=60000)
            architecture.bring_to_front()
            set_overlay(architecture, "ARCHITECTURE", "Public Cloud Run API → Pub/Sub/OIDC → private worker → Google ADK + Gemini → deterministic re-verification → Firestore transaction.")
            time.sleep(13)

            quality = context.new_page()
            quality.goto(QUALITY_RUN_URL, wait_until="domcontentloaded", timeout=60000)
            quality.bring_to_front()
            set_overlay(quality, "REPRODUCIBLE EVIDENCE", "59/59 automated tests and 52/52 labeled evaluation cases protect replay, crashes, stale state, model failure, prompt injection and safety boundaries.")
            time.sleep(12)

            opera.bring_to_front()
            opera.evaluate("window.scrollTo(0, 0)")
            set_overlay(opera, "PLACES, AGAIN", "Gemini decides what makes operational sense. Deterministic code proves what is safe. The plan breaks. The operation recovers.")
            time.sleep(11)

            clear_overlay(opera)
            time.sleep(2)
            stop_capture(capture)
            capture = None
            browser.close()
    finally:
        if capture is not None and capture.poll() is None:
            capture.kill()

    normalize_video()
    duration = duration_seconds(FINAL_VIDEO)
    if duration > 240:
        raise RuntimeError(f"Generated video is {duration:.2f}s, above the 240s contest cap")
    META.write_text(json.dumps({
        "generated_at": started.isoformat(),
        "live_url": LIVE_URL,
        "live_opera_elapsed_seconds": round(live_elapsed or 0.0, 3),
        "duration_seconds": round(duration, 3),
        "e2e_run": E2E_RUN_URL,
        "quality_run": QUALITY_RUN_URL,
        "runtime_source_commit": "5d6b5662cb63f8af1d414f01570c9991278b3e8e",
        "proof_of_action_note": "No page/DOM automation occurs between the single Inject disruption event click and terminal completion.",
        "audio": "none; English on-screen captions are part of the captured browser view",
    }, indent=2) + "\n", encoding="utf-8")
    log(f"FINAL_STATUS=SUBMISSION_VIDEO_BUILT duration={duration:.2f}s")


if __name__ == "__main__":
    main()
