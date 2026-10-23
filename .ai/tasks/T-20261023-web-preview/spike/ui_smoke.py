"""UI smoke for the hwp2md web preview.

Run: uv run python .ai/tasks/T-20261023-web-preview/spike/ui_smoke.py server|browser
Exit 0 on success, 1 on any failed check. Screenshot: $ILLY_SHOT_DIR/smoke_<mode>.png
(default .ai/tasks/T-20261023-web-preview/screenshots/).
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
import urllib.parse
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
PYODIDE_TIMEOUT_MS = 240_000  # 콜드 로드 약 65초 (CDN)
BROWSER_STATUS = "브라우저 모드: 파일이 서버로 전송되지 않습니다"
# 이미지 샘플을 마지막에 두어 스크린샷에 미리보기(그림·표)가 보이게 한다.
SAMPLES = [
    FIXTURES / "form200005063113.hwp",
    FIXTURES / "form210001070268.hwp",
    FIXTURES / "hwpx" / "(서식1) 비영리법인 현황 제출 양식.hwpx",
    FIXTURES / "hwpx" / "(서식2) 사업실적 및 사업계획 제출 양식.hwpx",
    SAMPLE,
]


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


def convert_sample(page: Page, path: Path, timeout_ms: int = TIMEOUT_MS) -> str:
    """파일을 넣고 그 파일의 변환이 끝날 때까지 기다린 뒤 #raw 를 돌려준다."""
    page.set_input_files("#file-input", str(path))
    page.wait_for_function(
        "name => document.querySelector('#file-name').textContent === name"
        " && ['done', 'error'].includes(document.body.dataset.state)",
        arg=path.name,
        timeout=timeout_ms,
    )
    if page.locator("body").get_attribute("data-state") != "done":
        raise RuntimeError(f"{path.name}: {page.locator('#error').inner_text()}")
    return page.locator("#raw").text_content() or ""


def run_browser_mode(page: Page, failures: list[str]) -> Path:
    requests: list[tuple[str, str]] = []
    page.on("request", lambda r: requests.append((r.method, r.url)))
    page.goto(BASE_URL, wait_until="commit")
    page.wait_for_selector('body[data-state="idle"]', timeout=TIMEOUT_MS)
    toggle = page.locator("#mode-toggle")
    check(failures, toggle.is_enabled(), "mode-toggle enabled")
    page.click("label.switch")
    check(failures, toggle.is_checked(), "mode-toggle checked")
    status = page.locator("#mode-status")
    t0 = time.monotonic()
    page.wait_for_selector(
        '#mode-status[data-state="browser"], #mode-status[data-state="error"]',
        timeout=PYODIDE_TIMEOUT_MS,
    )
    log(f"PYODIDE_LOAD_SECONDS={time.monotonic() - t0:.1f}")
    state = status.get_attribute("data-state")
    check(failures, state == "browser", f"mode-status data-state={state}")
    text = status.inner_text().strip()
    check(failures, text == BROWSER_STATUS, f"mode-status text {text!r}")
    loaded_pkg = any(u.endswith("/pkg/hwp2md.zip") and m == "GET" for m, u in requests)
    check(failures, loaded_pkg, "GET /pkg/hwp2md.zip during load")

    requests.clear()
    browser_raw: dict[str, str] = {}
    for path in SAMPLES:
        browser_raw[path.name] = convert_sample(page, path)
        log(f"  browser {path.name}: {len(browser_raw[path.name])} chars")
    page.wait_for_function(
        "Array.from(document.querySelectorAll('#preview img')).every(i => i.complete)",
        timeout=TIMEOUT_MS,
    )
    widths = page.locator("#preview img").evaluate_all("els => els.map(e => e.naturalWidth)")
    check(
        failures,
        len(widths) == EXPECTED_IMAGES and all(w > 0 for w in widths),
        f"browser #preview img count={len(widths)} naturalWidth={widths}",
    )
    tables = page.locator("#preview table").count()
    check(failures, tables == EXPECTED_TABLES, f"browser #preview table count={tables}")

    with page.expect_download(timeout=TIMEOUT_MS) as dl_info:
        page.click("#download")
    dl = dl_info.value
    expected = SAMPLE.stem + ".zip"
    name = dl.suggested_filename
    check(failures, name == expected, f"browser download name={name!r}")

    non_get = [(m, u) for m, u in requests if m != "GET"]
    api = [(m, u) for m, u in requests if urllib.parse.urlsplit(u).path.startswith("/api/")]
    check(failures, not non_get, f"browser mode non-GET requests={non_get}")
    check(failures, not api, f"browser mode /api/ requests={api}")
    log(f"  browser mode requests recorded={len(requests)}")

    page.evaluate("window.scrollTo(0, 0)")
    out = shot_dir() / "smoke_browser.png"
    page.screenshot(path=str(out), full_page=True)

    page.click("label.switch")
    check(failures, not toggle.is_checked(), "mode-toggle unchecked")
    check(failures, status.get_attribute("data-state") == "server", "back to server mode")
    requests.clear()
    same = 0
    for path in SAMPLES:
        raw = convert_sample(page, path)
        if raw == browser_raw[path.name]:
            same += 1
        else:
            log(f"  DIFF {path.name}")
    check(failures, same == len(SAMPLES), f"server #raw == browser #raw {same}/{len(SAMPLES)}")
    posts = [u for m, u in requests if m == "POST" and "/api/convert" in u]
    check(failures, len(posts) == len(SAMPLES), f"server mode POST /api/convert={len(posts)}")
    return out


def main(argv: list[str]) -> int:
    mode = argv[0] if argv else "server"
    if mode not in ("server", "browser"):
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
                run = run_browser_mode if mode == "browser" else run_server_mode
                out = run(page, failures)
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
