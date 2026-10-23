"""UI smoke for the hwp2md web preview.

Run: uv run python .ai/tasks/T-20261023-web-preview/spike/ui_smoke.py server
Exit 0 on success, 1 on any failed check. Screenshot: $ILLY_SHOT_DIR/smoke_<mode>.png
(default .ai/tasks/T-20261023-web-preview/screenshots/).
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

SPIKE_DIR = Path(__file__).resolve().parent
TASK_DIR = SPIKE_DIR.parent
PROJECT = SPIKE_DIR.parents[3]
FIXTURES = PROJECT / "tests" / "fixtures"
SAMPLE = FIXTURES / "hwpx" / "브라더 공공기관 보고서 양식.hwpx"
PORT = 8766
BASE_URL = f"http://localhost:{PORT}/"
EXPECTED_TABLES = 8
EXPECTED_IMAGES = 1
TIMEOUT_MS = 60_000


def log(msg: str) -> None:
    print(msg, flush=True)


def shot_dir() -> Path:
    env = os.environ.get("ILLY_SHOT_DIR")
    path = Path(env) if env else TASK_DIR / "screenshots"
    path.mkdir(parents=True, exist_ok=True)
    return path


def hwp2md_bin() -> str:
    candidate = Path(sys.executable).parent / "hwp2md"
    return str(candidate) if candidate.exists() else "hwp2md"


def start_server() -> subprocess.Popen[str]:
    proc = subprocess.Popen(
        [hwp2md_bin(), "serve", "--no-browser", "--port", str(PORT)],
        cwd=PROJECT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )
    for _ in range(60):
        if proc.poll() is not None:
            err = proc.stderr.read() if proc.stderr else ""
            raise RuntimeError(f"server exited early ({proc.returncode}): {err.strip()}")
        try:
            with urllib.request.urlopen(BASE_URL + "api/health", timeout=2) as resp:
                if resp.status == 200:
                    return proc
        except Exception:  # noqa: BLE001 - poll until ready
            time.sleep(0.5)
    proc.terminate()
    raise RuntimeError("server did not become healthy")


def stop_server(proc: subprocess.Popen[str]) -> None:
    proc.terminate()
    try:
        proc.wait(10)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(5)


def check(failures: list[str], ok: bool, label: str) -> None:
    log(f"{'OK  ' if ok else 'FAIL'} {label}")
    if not ok:
        failures.append(label)


def run_server_mode(page: Page, failures: list[str]) -> Path:
    page.goto(BASE_URL)
    page.wait_for_selector('body[data-state="idle"]', timeout=TIMEOUT_MS)
    status = page.locator("#mode-status")
    check(failures, status.get_attribute("data-state") == "server", "mode-status data-state=server")
    check(failures, status.inner_text().strip() == "서버 모드", "mode-status text 서버 모드")
    check(failures, page.locator("#download").is_disabled(), "download disabled before result")
    check(failures, page.locator("#error").is_hidden(), "error hidden before result")

    page.set_input_files("#file-input", str(SAMPLE))
    page.wait_for_selector('body[data-state="done"]', timeout=TIMEOUT_MS)
    page.wait_for_function(
        "Array.from(document.querySelectorAll('#preview img')).every(i => i.complete)",
        timeout=TIMEOUT_MS,
    )

    imgs = page.locator("#preview img")
    widths = imgs.evaluate_all("els => els.map(e => e.naturalWidth)")
    check(
        failures,
        len(widths) == EXPECTED_IMAGES and all(w > 0 for w in widths),
        f"#preview img count={len(widths)} naturalWidth={widths}",
    )
    tables = page.locator("#preview table").count()
    check(failures, tables == EXPECTED_TABLES, f"#preview table count={tables}")
    raw = page.locator("#raw").text_content() or ""
    check(failures, len(raw) > 0 and "_images/" in raw, "#raw has relative image link")
    check(failures, page.locator("#download").is_enabled(), "download enabled after result")
    check(failures, SAMPLE.name in page.locator("#file-name").inner_text(), "#file-name shows file")
    log("META " + page.locator("#result-meta").inner_text())

    with page.expect_download(timeout=TIMEOUT_MS) as dl_info:
        page.click("#download")
    dl = dl_info.value
    expected = SAMPLE.stem + ".zip"
    check(failures, dl.suggested_filename == expected, f"download name={dl.suggested_filename!r}")

    page.evaluate("window.scrollTo(0, 0)")
    out = shot_dir() / "smoke_server.png"
    page.screenshot(path=str(out), full_page=True)
    return out


def main(argv: list[str]) -> int:
    mode = argv[0] if argv else "server"
    if mode != "server":
        log(f"SMOKE FAIL unknown mode {mode!r}")
        return 1
    failures: list[str] = []
    proc = start_server()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                ctx = browser.new_context(
                    viewport={"width": 1440, "height": 900}, accept_downloads=True
                )
                page = ctx.new_page()
                page.on(
                    "console",
                    lambda m: log(f"  [console] {m.text}") if m.type == "error" else None,
                )
                page.on("pageerror", lambda e: failures.append(f"pageerror: {e}"))
                out = run_server_mode(page, failures)
                log(f"SCREENSHOT {out}")
                ctx.close()
            finally:
                browser.close()
    except Exception as exc:  # noqa: BLE001 - report as smoke failure
        failures.append(repr(exc))
    finally:
        stop_server(proc)
    if failures:
        log("SMOKE FAIL " + "; ".join(failures))
        return 1
    log(f"SMOKE OK {mode}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
