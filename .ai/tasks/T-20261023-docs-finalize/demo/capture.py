"""Capture README screenshots of the web preview with the synthetic demo document.

Run: uv run python .ai/tasks/T-20261023-docs-finalize/demo/capture.py [server|browser|all]
Output: docs/images/web-server-mode.png, docs/images/web-browser-mode.png
"""

from __future__ import annotations

import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

DEMO_DIR = Path(__file__).resolve().parent
PROJECT = DEMO_DIR.parents[3]
DEMO = DEMO_DIR / "demo.hwpx"
IMAGES = PROJECT / "docs" / "images"
PORT = 8791
BASE_URL = f"http://localhost:{PORT}/"
TIMEOUT_MS = 60_000
PYODIDE_TIMEOUT_MS = 240_000


def hwp2md_bin() -> str:
    candidate = Path(sys.executable).parent / "hwp2md"
    return str(candidate) if candidate.exists() else "hwp2md"


def start_server() -> subprocess.Popen[bytes]:
    proc = subprocess.Popen(
        [hwp2md_bin(), "serve", "--no-browser", "--port", str(PORT)],
        cwd=PROJECT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for _ in range(60):
        if proc.poll() is not None:
            raise RuntimeError(f"server exited early ({proc.returncode})")
        try:
            with urllib.request.urlopen(BASE_URL + "api/health", timeout=2) as resp:
                if resp.status == 200:
                    return proc
        except Exception:  # noqa: BLE001 - poll until ready
            time.sleep(0.5)
    proc.terminate()
    raise RuntimeError("server did not become healthy")


def stop_server(proc: subprocess.Popen[bytes]) -> None:
    proc.terminate()
    try:
        proc.wait(10)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(5)


def load_demo(page: Page) -> None:
    page.set_input_files("#file-input", str(DEMO))
    page.wait_for_function(
        "name => document.querySelector('#file-name').textContent === name"
        " && ['done', 'error'].includes(document.body.dataset.state)",
        arg=DEMO.name,
        timeout=TIMEOUT_MS,
    )
    if page.locator("body").get_attribute("data-state") != "done":
        raise RuntimeError(page.locator("#error").inner_text())
    page.wait_for_function(
        "Array.from(document.querySelectorAll('#preview img')).every(i => i.complete)",
        timeout=TIMEOUT_MS,
    )
    print("META", page.locator("#result-meta").inner_text(), flush=True)
    page.evaluate("window.scrollTo(0, 0)")


def server_mode(page: Page) -> Path:
    page.goto(BASE_URL)
    page.wait_for_selector('body[data-state="idle"]', timeout=TIMEOUT_MS)
    load_demo(page)
    out = IMAGES / "web-server-mode.png"
    page.screenshot(path=str(out), full_page=True)
    return out


def browser_mode(page: Page) -> Path:
    page.goto(BASE_URL, wait_until="commit")
    page.wait_for_selector('body[data-state="idle"]', timeout=TIMEOUT_MS)
    page.click("label.switch")
    t0 = time.monotonic()
    page.wait_for_selector(
        '#mode-status[data-state="browser"], #mode-status[data-state="error"]',
        timeout=PYODIDE_TIMEOUT_MS,
    )
    print(f"PYODIDE_LOAD_SECONDS={time.monotonic() - t0:.1f}", flush=True)
    state = page.locator("#mode-status").get_attribute("data-state")
    if state != "browser":
        raise RuntimeError("pyodide load failed: " + page.locator("#mode-status").inner_text())
    load_demo(page)
    out = IMAGES / "web-browser-mode.png"
    page.screenshot(path=str(out), full_page=True)
    return out


def main(argv: list[str]) -> int:
    mode = argv[0] if argv else "all"
    runs = {"server": [server_mode], "browser": [browser_mode], "all": [server_mode, browser_mode]}
    IMAGES.mkdir(parents=True, exist_ok=True)
    proc = start_server()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                for run in runs[mode]:
                    ctx = browser.new_context(viewport={"width": 1440, "height": 900})
                    page = ctx.new_page()
                    print("SCREENSHOT", run(page), flush=True)
                    ctx.close()
            finally:
                browser.close()
    finally:
        stop_server(proc)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
