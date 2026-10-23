"""건너뜀 경고·보호 문서 오류 화면 E2E (서버 모드·브라우저 모드·API). 합성 문서만 쓴다."""

from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path

import httpx
import pytest
from conftest import WebServer
from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright

from synth_hwp5 import write_hwp5
from synth_hwpml import write_hwpml
from synth_hwpx import write_hwpx
from synth_items import SynthHeaderFooter

TIMEOUT_MS = 60_000
PYODIDE_TIMEOUT_MS = 240_000
VIEWPORT = {"width": 1440, "height": 900}
SKIPPED_TEXT = "변환하지 못한 요소: 머리말·꼬리말 1개"
DRM_TEXT = "문서보안(DRM)이 적용된 파일이라 변환할 수 없습니다"
ENCRYPTED_TEXT = "암호가 설정된 문서라 변환할 수 없습니다"
BODY = ["합성 본문 첫째 줄", "합성 본문 둘째 줄"]


def _shot_dir() -> Path:
    path = Path(os.environ.get("ILLY_SHOT_DIR", "tests/e2e/screenshots"))
    path.mkdir(parents=True, exist_ok=True)
    return path


def _screenshot(page: Page, name: str) -> None:
    page.evaluate("window.scrollTo(0, 0)")
    page.screenshot(path=str(_shot_dir() / name), full_page=True)


def _header_hwpx(tmp_path: Path) -> Path:
    return write_hwpx(tmp_path / "header.hwpx", [SynthHeaderFooter(("쪽 머리말",)), *BODY])


def _plain_hwpx(tmp_path: Path) -> Path:
    return write_hwpx(tmp_path / "plain.hwpx", list(BODY))


def _drm_file(tmp_path: Path) -> Path:
    path = tmp_path / "drm.hwp"
    path.write_bytes(b"\x9b\x20" + b"DRMONE" + bytes(600))
    return path


def _encrypted_file(tmp_path: Path) -> Path:
    return write_hwp5(tmp_path / "locked.hwp", BODY, properties=0x3)


def _convert(page: Page, path: Path, timeout: int = TIMEOUT_MS) -> None:
    page.evaluate("document.body.dataset.state = 'idle'")
    page.set_input_files("#file-input", str(path))
    page.wait_for_function(
        "name => document.querySelector('#file-name').textContent === name"
        " && ['done', 'error'].includes(document.body.dataset.state)",
        arg=path.name,
        timeout=timeout,
    )


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
    ctx = browser.new_context(viewport=VIEWPORT)
    page = ctx.new_page()
    page.goto(web_server.base_url + "/")
    page.wait_for_selector('body[data-state="idle"]', timeout=TIMEOUT_MS)
    try:
        yield page
    finally:
        ctx.close()


@pytest.fixture(scope="module")
def browser_context(browser: Browser) -> Iterator[BrowserContext]:
    ctx = browser.new_context(viewport=VIEWPORT)
    try:
        yield ctx
    finally:
        ctx.close()


@pytest.fixture(scope="module")
def browser_page(browser_context: BrowserContext, web_server: WebServer) -> Page:
    """Pyodide 를 1회만 로드한 브라우저 모드 페이지. CDN 을 못 받으면 그대로 실패한다."""
    page = browser_context.new_page()
    page.goto(web_server.base_url + "/", wait_until="commit")
    page.wait_for_selector('body[data-state="idle"]', timeout=TIMEOUT_MS)
    page.click("label.switch")
    page.wait_for_selector(
        '#mode-status[data-state="browser"], #mode-status[data-state="error"]',
        timeout=PYODIDE_TIMEOUT_MS,
    )
    assert page.locator("#mode-status").get_attribute("data-state") == "browser", page.locator(
        "#mode-status"
    ).inner_text()
    return page


# ---------- 서버 모드 화면 ----------


def test_server_header_shows_skipped(server_page: Page, tmp_path: Path) -> None:
    _convert(server_page, _header_hwpx(tmp_path))

    assert server_page.locator("body").get_attribute("data-state") == "done"
    skipped = server_page.locator("#skipped")
    assert skipped.is_visible()
    assert SKIPPED_TEXT in skipped.inner_text()
    _screenshot(server_page, "s26-web-skipped.png")


def test_server_plain_hides_skipped(server_page: Page, tmp_path: Path) -> None:
    _convert(server_page, _plain_hwpx(tmp_path))

    assert server_page.locator("body").get_attribute("data-state") == "done"
    assert server_page.locator("#skipped").is_hidden()


def test_server_skipped_cleared_by_next_file(server_page: Page, tmp_path: Path) -> None:
    _convert(server_page, _header_hwpx(tmp_path))
    assert server_page.locator("#skipped").is_visible()

    _convert(server_page, _plain_hwpx(tmp_path))

    assert server_page.locator("#skipped").is_hidden()


def test_server_drm_shows_error(server_page: Page, tmp_path: Path) -> None:
    _convert(server_page, _drm_file(tmp_path))

    assert server_page.locator("body").get_attribute("data-state") == "error"
    assert DRM_TEXT in server_page.locator("#error").inner_text()
    _screenshot(server_page, "s26-web-drm.png")


def test_server_encrypted_shows_error(server_page: Page, tmp_path: Path) -> None:
    _convert(server_page, _encrypted_file(tmp_path))

    assert server_page.locator("body").get_attribute("data-state") == "error"
    assert ENCRYPTED_TEXT in server_page.locator("#error").inner_text()


def test_server_hwpml_converts(server_page: Page, tmp_path: Path) -> None:
    _convert(server_page, write_hwpml(tmp_path / "doc.hml", list(BODY)))

    assert server_page.locator("body").get_attribute("data-state") == "done"
    assert BODY[0] in (server_page.locator("#raw").text_content() or "")


# ---------- 브라우저 모드 화면 ----------


def test_browser_header_shows_skipped(browser_page: Page, tmp_path: Path) -> None:
    _convert(browser_page, _header_hwpx(tmp_path), PYODIDE_TIMEOUT_MS)

    assert browser_page.locator("body").get_attribute("data-state") == "done"
    assert browser_page.locator("#skipped").is_visible()
    assert SKIPPED_TEXT in browser_page.locator("#skipped").inner_text()


def test_browser_plain_hides_skipped(browser_page: Page, tmp_path: Path) -> None:
    _convert(browser_page, _plain_hwpx(tmp_path), PYODIDE_TIMEOUT_MS)

    assert browser_page.locator("body").get_attribute("data-state") == "done"
    assert browser_page.locator("#skipped").is_hidden()


def test_browser_drm_shows_error(browser_page: Page, tmp_path: Path) -> None:
    _convert(browser_page, _drm_file(tmp_path), PYODIDE_TIMEOUT_MS)

    assert browser_page.locator("body").get_attribute("data-state") == "error"
    assert DRM_TEXT in browser_page.locator("#error").inner_text()


# ---------- API ----------


def _post(server: WebServer, path: Path) -> httpx.Response:
    return httpx.post(
        f"{server.base_url}/api/convert",
        params={"name": path.name},
        content=path.read_bytes(),
        headers={"Content-Type": "application/octet-stream"},
        timeout=60,
    )


def test_api_convert_skipped_array(web_server: WebServer, tmp_path: Path) -> None:
    resp = _post(web_server, _header_hwpx(tmp_path))

    assert resp.status_code == 200
    skipped = resp.json()["skipped"]
    assert [(s["label"], s["count"]) for s in skipped] == [("머리말·꼬리말", 1)]


def test_api_convert_skipped_empty(web_server: WebServer, tmp_path: Path) -> None:
    resp = _post(web_server, _plain_hwpx(tmp_path))

    assert resp.status_code == 200
    assert resp.json()["skipped"] == []


def test_api_convert_drm_415(web_server: WebServer, tmp_path: Path) -> None:
    resp = _post(web_server, _drm_file(tmp_path))

    assert resp.status_code == 415
    assert resp.json()["error"]["code"] == "drm"


def test_api_convert_encrypted_415(web_server: WebServer, tmp_path: Path) -> None:
    resp = _post(web_server, _encrypted_file(tmp_path))

    assert resp.status_code == 415
    assert resp.json()["error"]["code"] == "encrypted"


def test_api_convert_hwpml_200(web_server: WebServer, tmp_path: Path) -> None:
    resp = _post(web_server, write_hwpml(tmp_path / "doc.hml", list(BODY)))

    assert resp.status_code == 200
    assert BODY[0] in resp.json()["markdown"]
