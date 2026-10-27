from __future__ import annotations

import io
import os
import subprocess
import urllib.parse
import zipfile
from collections.abc import Callable, Iterator
from pathlib import Path

import pytest
from playwright.sync_api import Browser, BrowserContext, Page, Request, sync_playwright

from conftest import REAL_SAMPLES, WebServer

RunCli = Callable[[list[str]], subprocess.CompletedProcess[str]]

IMAGE_HWPX = next(
    (p for p in REAL_SAMPLES if p.suffix == ".hwpx" and p.stem.startswith("브라더")), None
)
# 이미지 샘플을 마지막에 두어 스크린샷에 그림·표가 보이게 한다.
ORDERED_SAMPLES = [p for p in REAL_SAMPLES if p != IMAGE_HWPX] + [IMAGE_HWPX]

TIMEOUT_MS = 60_000
PYODIDE_TIMEOUT_MS = 240_000
BROWSER_STATUS = "브라우저 모드: 파일이 서버로 전송되지 않습니다"
NOT_HWP_TEXT = "HWP 5.0 또는 HWPX 파일이 아닙니다"
VIEWPORT = {"width": 1440, "height": 900}


def _shot_dir() -> Path:
    path = Path(os.environ.get("ILLY_SHOT_DIR", "tests/e2e/screenshots"))
    path.mkdir(parents=True, exist_ok=True)
    return path


def _screenshot(page: Page, name: str) -> None:
    page.evaluate("window.scrollTo(0, 0)")
    page.screenshot(path=str(_shot_dir() / name), full_page=True)


@pytest.fixture(scope="module")
def browser() -> Iterator[Browser]:
    with sync_playwright() as p:
        br = p.chromium.launch(headless=True)
        try:
            yield br
        finally:
            br.close()


@pytest.fixture
def server_page(browser: Browser, web_server: WebServer) -> Iterator[Page]:
    ctx = browser.new_context(viewport=VIEWPORT, accept_downloads=True)
    page = ctx.new_page()
    page.goto(web_server.base_url + "/")
    page.wait_for_selector('body[data-state="idle"]', timeout=TIMEOUT_MS)
    try:
        yield page
    finally:
        ctx.close()


@pytest.fixture(scope="module")
def browser_context(browser: Browser) -> Iterator[BrowserContext]:
    ctx = browser.new_context(viewport=VIEWPORT, accept_downloads=True)
    try:
        yield ctx
    finally:
        ctx.close()


@pytest.fixture(scope="module")
def browser_page(browser_context: BrowserContext, web_server: WebServer) -> Page:
    """Pyodide 를 1회만 로드한 브라우저 모드 페이지 (module scope). jsDelivr CDN 접근 필요."""
    page = browser_context.new_page()
    page.goto(web_server.base_url + "/", wait_until="commit")
    page.wait_for_selector('body[data-state="idle"]', timeout=TIMEOUT_MS)
    page.click("label.switch")
    page.wait_for_selector(
        '#mode-status[data-state="browser"], #mode-status[data-state="error"]',
        timeout=PYODIDE_TIMEOUT_MS,
    )
    state = page.locator("#mode-status").get_attribute("data-state")
    assert state == "browser", page.locator("#mode-status").inner_text()
    return page


def _convert(page: Page, path: Path) -> None:
    """파일을 넣고 그 파일의 변환이 끝날 때(done/error)까지 기다린다. 이전 상태는 비워 둔다."""
    page.evaluate("document.body.dataset.state = 'idle'")
    page.set_input_files("#file-input", str(path))
    page.wait_for_function(
        "name => document.querySelector('#file-name').textContent === name"
        " && ['done', 'error'].includes(document.body.dataset.state)",
        arg=path.name,
        timeout=PYODIDE_TIMEOUT_MS,
    )


def _convert_ok(page: Page, path: Path) -> str:
    _convert(page, path)
    state = page.locator("body").get_attribute("data-state")
    assert state == "done", page.locator("#error").inner_text()
    return page.locator("#raw").text_content() or ""


def _wait_images(page: Page) -> None:
    page.wait_for_function(
        "Array.from(document.querySelectorAll('#preview img')).every(i => i.complete)",
        timeout=TIMEOUT_MS,
    )


def _cli_md(path: Path, out_dir: Path, run_cli: RunCli) -> Path:
    result = run_cli([str(path), "-o", str(out_dir)])
    assert result.returncode == 0, result.stderr
    return out_dir / f"{path.stem}.md"


def _zip_entries(data: bytes) -> dict[str, bytes]:
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        return {n: zf.read(n) for n in zf.namelist()}


def _download_zip(page: Page) -> tuple[str, dict[str, bytes]]:
    with page.expect_download(timeout=TIMEOUT_MS) as info:
        page.click("#download")
    dl = info.value
    path = dl.path()
    assert path is not None
    return dl.suggested_filename, _zip_entries(Path(path).read_bytes())


def _write_not_hwp(tmp_path: Path) -> Path:
    bad = tmp_path / "not.hwp"
    bad.write_text("plain text, not an ole file\n" * 100, encoding="utf-8")
    return bad


@pytest.mark.real_samples
def test_server_mode_preview(server_page: Page) -> None:
    page = server_page
    status = page.locator("#mode-status")
    assert status.get_attribute("data-state") == "server"
    assert status.inner_text().strip() == "서버 모드"
    assert page.locator("#download").is_disabled()
    assert page.locator("#error").is_hidden()

    page.set_input_files("#file-input", str(IMAGE_HWPX))
    page.wait_for_selector('body[data-state="done"]', timeout=TIMEOUT_MS)
    _wait_images(page)

    imgs = page.locator("#preview img")
    assert imgs.count() == 1
    assert imgs.first.get_attribute("src", timeout=TIMEOUT_MS).startswith("data:")
    assert all(w > 0 for w in imgs.evaluate_all("els => els.map(e => e.naturalWidth)"))
    assert page.locator("#preview table").count() == 8
    raw = page.locator("#raw").text_content() or ""
    assert f"![그림 1]({IMAGE_HWPX.stem.replace(' ', '%20')}_images/img_001.png)" in raw
    assert "이미지 1개" in page.locator("#result-meta").inner_text()
    assert IMAGE_HWPX.name in page.locator("#file-name").inner_text()
    assert page.locator("#download").is_enabled()

    _screenshot(page, "web_server_preview.png")


@pytest.mark.real_samples
def test_drop_event(server_page: Page) -> None:
    data = list(IMAGE_HWPX.read_bytes())
    server_page.evaluate(
        """({name, data}) => {
            const dt = new DataTransfer();
            dt.items.add(new File([new Uint8Array(data)], name));
            const zone = document.querySelector('#drop-zone');
            const init = {dataTransfer: dt, bubbles: true, cancelable: true};
            zone.dispatchEvent(new DragEvent('dragover', init));
            zone.dispatchEvent(new DragEvent('drop', init));
        }""",
        {"name": IMAGE_HWPX.name, "data": data},
    )

    server_page.wait_for_selector('body[data-state="done"]', timeout=TIMEOUT_MS)
    assert server_page.locator("#file-name").inner_text().strip() == IMAGE_HWPX.name
    assert server_page.locator("#preview table").count() == 8


@pytest.mark.real_samples
def test_server_mode_zip_download(server_page: Page, tmp_path: Path, run_cli: RunCli) -> None:
    out_dir = tmp_path / "out"
    md_path = _cli_md(IMAGE_HWPX, out_dir, run_cli)
    image = out_dir / f"{IMAGE_HWPX.stem}_images" / "img_001.png"

    server_page.set_input_files("#file-input", str(IMAGE_HWPX))
    server_page.wait_for_selector('body[data-state="done"]', timeout=TIMEOUT_MS)
    filename, entries = _download_zip(server_page)

    assert filename == f"{IMAGE_HWPX.stem}.zip"
    assert list(entries) == [md_path.name, f"{image.parent.name}/img_001.png"]
    assert entries[md_path.name] == md_path.read_bytes()
    assert entries[f"{image.parent.name}/img_001.png"] == image.read_bytes()


def test_error_display(server_page: Page, tmp_path: Path) -> None:
    server_page.set_input_files("#file-input", str(_write_not_hwp(tmp_path)))
    server_page.wait_for_selector('body[data-state="error"]', timeout=TIMEOUT_MS)

    error = server_page.locator("#error")
    assert error.is_visible()
    assert NOT_HWP_TEXT in error.inner_text()
    assert server_page.locator("#download").is_disabled()

    _screenshot(server_page, "web_error.png")


@pytest.mark.real_samples
def test_browser_mode_sends_no_file(
    browser: Browser, web_server: WebServer, browser_page: Page
) -> None:
    """C11. jsDelivr CDN 접근 필요 (Pyodide 로드)."""
    # 대조군: 서버 모드는 파일 본문을 POST 로 보낸다.
    ctx = browser.new_context(viewport=VIEWPORT, accept_downloads=True)
    try:
        control = ctx.new_page()
        control_reqs: list[Request] = []
        control.on("request", lambda r: control_reqs.append(r))
        control.goto(web_server.base_url + "/")
        control.wait_for_selector('body[data-state="idle"]', timeout=TIMEOUT_MS)
        control.set_input_files("#file-input", str(IMAGE_HWPX))
        control.wait_for_selector('body[data-state="done"]', timeout=TIMEOUT_MS)
        # Chromium 은 File 본문의 post_data_buffer 를 노출하지 않아 헤더 길이로 확인한다.
        sent_length = int(
            [r for r in control_reqs if r.method == "POST"][0].all_headers()["content-length"]
        )
    finally:
        ctx.close()
    posts = [r for r in control_reqs if r.method == "POST"]
    assert len(posts) == 1
    assert urllib.parse.urlsplit(posts[0].url).path == "/api/convert"
    assert sent_length == IMAGE_HWPX.stat().st_size

    # 브라우저 모드: 5개 변환 + zip 1회 후에도 non-GET, /api/ 요청 없음.
    page = browser_page
    requests: list[tuple[str, str]] = []

    def record(r: Request) -> None:
        requests.append((r.method, r.url))

    page.on("request", record)
    try:
        for path in ORDERED_SAMPLES:
            _convert_ok(page, path)
        _wait_images(page)
        filename, _ = _download_zip(page)
        _screenshot(page, "web_browser_preview.png")
    finally:
        page.remove_listener("request", record)

    assert filename == f"{IMAGE_HWPX.stem}.zip"
    assert page.locator("#mode-status").inner_text().strip() == BROWSER_STATUS
    assert page.locator("#mode-toggle").is_checked()
    assert page.locator("#preview table").count() == 8
    non_get = [(m, u) for m, u in requests if m != "GET"]
    api = [(m, u) for m, u in requests if urllib.parse.urlsplit(u).path.startswith("/api/")]
    assert non_get == []
    assert api == []


@pytest.mark.real_samples
def test_modes_produce_identical_markdown(
    server_page: Page, browser_page: Page, tmp_path: Path, run_cli: RunCli
) -> None:
    """C12. jsDelivr CDN 접근 필요 (Pyodide 로드)."""
    assert len(REAL_SAMPLES) == 5
    for sample in REAL_SAMPLES:
        cli_md = _cli_md(sample, tmp_path / sample.stem, run_cli).read_text(encoding="utf-8")
        server_raw = _convert_ok(server_page, sample)
        browser_raw = _convert_ok(browser_page, sample)

        assert server_raw == browser_raw, sample.name
        assert server_raw == cli_md, sample.name


@pytest.mark.real_samples
def test_browser_mode_zip_matches_server(server_page: Page, browser_page: Page) -> None:
    """jsDelivr CDN 접근 필요 (Pyodide 로드)."""
    _convert_ok(server_page, IMAGE_HWPX)
    server_name, server_entries = _download_zip(server_page)
    _convert_ok(browser_page, IMAGE_HWPX)
    browser_name, browser_entries = _download_zip(browser_page)

    assert browser_name == server_name == f"{IMAGE_HWPX.stem}.zip"
    assert list(browser_entries) == list(server_entries)
    assert len(browser_entries) == 2
    for name, data in server_entries.items():
        assert browser_entries[name] == data, name


def test_browser_mode_error_same_code(
    server_page: Page, browser_page: Page, tmp_path: Path
) -> None:
    """jsDelivr CDN 접근 필요 (Pyodide 로드)."""
    bad = _write_not_hwp(tmp_path)
    _convert(server_page, bad)
    _convert(browser_page, bad)

    assert server_page.locator("body").get_attribute("data-state") == "error"
    assert browser_page.locator("body").get_attribute("data-state") == "error"
    server_text = server_page.locator("#error").inner_text()
    browser_text = browser_page.locator("#error").inner_text()
    assert NOT_HWP_TEXT in browser_text
    assert browser_text == server_text
