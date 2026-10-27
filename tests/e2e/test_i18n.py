"""웹 화면 i18n E2E (영어 화면). 입력은 합성 HWPX 와 가짜 .hwp 만 쓴다.

정적 사이트 케이스는 `HWP2MD_PAGES_URL`(끝 슬래시 포함)이 있으면 그 주소로, 없으면 로컬 서버로 돈다.
"""

from __future__ import annotations

import importlib.util
import json
import os
import socket
import subprocess
import sys
import time
import urllib.request
from collections.abc import Iterator
from pathlib import Path
from urllib.parse import urlparse

import pytest
from playwright.sync_api import Browser, Page, Request, Route, sync_playwright

from conftest import WebServer
from synth_hwpx import write_hwpx

ROOT = Path(__file__).resolve().parents[2]
BUILD_SCRIPT = ROOT / "scripts" / "build_pages.py"
TIMEOUT_MS = 60_000
PYODIDE_TIMEOUT_MS = 240_000
VIEWPORT = {"width": 1440, "height": 900}
REMOTE_URL = os.environ.get("HWP2MD_PAGES_URL", "").strip()
CDN_HOST = "cdn.jsdelivr.net"
HANGUL = "[가-힣]"
FRAME_SELECTOR = "header, #drop-zone, .status-bar, .pane-tabs"


def _screenshot(page: Page, name: str) -> None:
    path = Path(os.environ.get("ILLY_SHOT_DIR", "tests/e2e/screenshots"))
    path.mkdir(parents=True, exist_ok=True)
    page.evaluate("window.scrollTo(0, 0)")
    page.screenshot(path=str(path / name), full_page=True)


@pytest.fixture(scope="module")
def browser() -> Iterator[Browser]:
    with sync_playwright() as p:
        br = p.chromium.launch(headless=True)
        try:
            yield br
        finally:
            br.close()


def _open(browser: Browser, url: str, locale: str) -> tuple[object, Page]:
    ctx = browser.new_context(viewport=VIEWPORT, locale=locale)
    page = ctx.new_page()
    page.goto(url)
    page.wait_for_selector('body[data-state="idle"]', timeout=TIMEOUT_MS)
    return ctx, page


def _convert(page: Page, path: Path, timeout: int = TIMEOUT_MS) -> None:
    page.set_input_files("#file-input", str(path))
    page.wait_for_function(
        "name => document.querySelector('#file-name').textContent === name"
        " && ['done', 'error'].includes(document.body.dataset.state)",
        arg=path.name,
        timeout=timeout,
    )


def _frame_text(page: Page) -> str:
    return str(
        page.evaluate(
            "sel => Array.from(document.querySelectorAll(sel)).map(e => e.innerText).join('\\n')",
            FRAME_SELECTOR,
        )
    )


def _hangul_count(text: str) -> int:
    import re

    return len(re.findall(HANGUL, text))


def test_server_en_by_navigator(browser: Browser, web_server: WebServer, tmp_path: Path) -> None:
    ctx, page = _open(browser, web_server.base_url + "/", "en-US")
    try:
        assert page.locator("html").get_attribute("lang") == "en"
        assert page.evaluate("window.Hwp2mdI18n.source") == "navigator"
        assert page.locator("#mode-status").inner_text().strip() == "Server mode"

        sample = write_hwpx(tmp_path / "synth.hwpx", ["Hello", "Second paragraph"])
        _convert(page, sample)
        assert page.locator("body").get_attribute("data-state") == "done", page.locator(
            "#error"
        ).inner_text()
        assert "paragraph" in page.locator("#result-meta").inner_text()
        assert page.evaluate("window.Hwp2mdI18n.missing()") == []
        assert _hangul_count(_frame_text(page)) == 0
        _screenshot(page, "i18n-en-convert-done.png")
    finally:
        ctx.close()  # type: ignore[attr-defined]


def test_server_en_error(browser: Browser, web_server: WebServer, tmp_path: Path) -> None:
    ctx, page = _open(browser, web_server.base_url + "/", "en-US")
    try:
        bad = tmp_path / "fake.hwp"
        bad.write_text("plain text, not an ole file\n" * 50, encoding="utf-8")
        _convert(page, bad)
        assert page.locator("body").get_attribute("data-state") == "error"
        assert page.locator("#error-text").inner_text().strip() == "Not an HWP 5.0 or HWPX file"
        _screenshot(page, "i18n-en-error.png")
    finally:
        ctx.close()  # type: ignore[attr-defined]


def test_toggle_to_korean_persists(browser: Browser, web_server: WebServer, tmp_path: Path) -> None:
    ctx, page = _open(browser, web_server.base_url + "/", "en-US")
    try:
        sample = write_hwpx(tmp_path / "synth.hwpx", ["Hello"])
        _convert(page, sample)
        assert page.locator("body").get_attribute("data-state") == "done"

        page.click(".lang-toggle")

        assert page.locator("html").get_attribute("lang") == "ko"
        assert page.locator("#mode-status").inner_text().strip() == "서버 모드"
        assert "단락" in page.locator("#result-meta").inner_text()
        assert page.locator("body").get_attribute("data-state") == "done"
        assert page.locator(".lang-toggle").inner_text().strip() == "EN"

        page.reload()
        page.wait_for_selector('body[data-state="idle"]', timeout=TIMEOUT_MS)
        assert page.locator("html").get_attribute("lang") == "ko"
        assert page.evaluate("window.Hwp2mdI18n.source") == "storage"
    finally:
        ctx.close()  # type: ignore[attr-defined]


def test_query_overrides_navigator(browser: Browser, web_server: WebServer) -> None:
    ctx, page = _open(browser, web_server.base_url + "/?lang=en", "ko-KR")
    try:
        assert page.locator("html").get_attribute("lang") == "en"
        assert page.evaluate("window.Hwp2mdI18n.source") == "query"
    finally:
        ctx.close()  # type: ignore[attr-defined]


def test_unknown_lang_falls_back(browser: Browser, web_server: WebServer) -> None:
    ctx, page = _open(browser, web_server.base_url + "/?lang=fr", "ko-KR")
    try:
        assert page.locator("html").get_attribute("lang") == "ko"
        assert page.evaluate("window.Hwp2mdI18n.source") == "navigator"
        assert page.evaluate("localStorage.getItem('hwp2md-lang')") is None
    finally:
        ctx.close()  # type: ignore[attr-defined]

    ctx2, page2 = _open(browser, web_server.base_url + "/?lang=EN", "en-US")
    try:
        assert page2.locator("html").get_attribute("lang") == "en"
        assert page2.evaluate("window.Hwp2mdI18n.source") == "navigator"
        assert page2.evaluate("localStorage.getItem('hwp2md-lang')") is None
    finally:
        ctx2.close()  # type: ignore[attr-defined]


def test_skipped_prefix_en(browser: Browser, web_server: WebServer, tmp_path: Path) -> None:
    ctx, page = _open(browser, web_server.base_url + "/", "en-US")
    try:

        def _patch(route: Route) -> None:
            resp = route.fetch()
            body = json.loads(resp.text())
            body["skipped"] = [{"label": "머리말·꼬리말", "count": 1}]
            route.fulfill(response=resp, json=body)

        page.route("**/api/convert*", _patch)
        sample = write_hwpx(tmp_path / "synth.hwpx", ["Hello"])
        _convert(page, sample)
        assert page.locator("body").get_attribute("data-state") == "done"
        skipped = page.locator("#skipped")
        assert skipped.is_visible()
        assert skipped.inner_text().startswith("Not converted: 머리말·꼬리말 (1)")
        assert skipped.locator("a").inner_text().strip() == "Why?"
    finally:
        ctx.close()  # type: ignore[attr-defined]


def test_about_en_and_toggle(browser: Browser, web_server: WebServer) -> None:
    ctx = browser.new_context(viewport=VIEWPORT, locale="en-US")
    page = ctx.new_page()
    try:
        page.goto(web_server.base_url + "/about")
        page.wait_for_selector('a:has-text("Open converter")', timeout=TIMEOUT_MS)
        assert page.locator("html").get_attribute("lang") == "en"
        link = page.locator('a:has-text("Open converter")').first
        assert link.get_attribute("href") == "/"
        assert page.evaluate("window.Hwp2mdI18n.missing()") == []
        page.wait_for_timeout(1500)  # 히어로 애니메이션 정착 (스크린샷용)
        _screenshot(page, "i18n-en-about.png")

        with page.expect_navigation():
            page.click(".lang-toggle")
        page.wait_for_selector('a:has-text("변환 도구 열기")', timeout=TIMEOUT_MS)
        assert page.locator("html").get_attribute("lang") == "ko"
        assert page.locator('a:has-text("변환 도구 열기")').first.is_visible()
    finally:
        ctx.close()


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("localhost", 0))
        return int(s.getsockname()[1])


@pytest.fixture(scope="module")
def pages_base(tmp_path_factory: pytest.TempPathFactory) -> Iterator[str]:
    if REMOTE_URL:
        yield REMOTE_URL if REMOTE_URL.endswith("/") else REMOTE_URL + "/"
        return
    spec = importlib.util.spec_from_file_location("build_pages_i18n", BUILD_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    root = tmp_path_factory.mktemp("pages") / "site"
    module.build_site(root / "hwp2md")
    port = _free_port()
    env = {k: v for k, v in os.environ.items() if k != "VIRTUAL_ENV"}
    proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port), "--bind", "localhost"]
        + ["--directory", str(root)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=env,
    )
    base = f"http://localhost:{port}/hwp2md/"
    try:
        for _ in range(50):
            try:
                urllib.request.urlopen(base + "convert.html", timeout=2).close()
                break
            except OSError:
                time.sleep(0.2)
        else:
            raise RuntimeError("http.server did not start")
        yield base
    finally:
        proc.terminate()
        proc.wait(timeout=10)


def test_static_site_en(browser: Browser, pages_base: str, tmp_path: Path) -> None:
    base = urlparse(pages_base)
    violations: list[str] = []
    posts: list[str] = []

    ctx = browser.new_context(viewport=VIEWPORT, locale="en-US", accept_downloads=True)

    def _on_request(req: Request) -> None:
        if req.method == "POST":
            posts.append(req.url)

    def _route(route: Route) -> None:
        url = urlparse(route.request.url)
        if url.netloc == base.netloc:
            if not url.path.startswith(base.path):
                violations.append(route.request.url)
            route.continue_()
        elif url.hostname == CDN_HOST:
            route.continue_()
        else:
            violations.append(route.request.url)
            route.abort()

    ctx.on("request", _on_request)
    ctx.route("**/*", _route)
    page = ctx.new_page()
    try:
        page.goto(pages_base + "convert.html", wait_until="load")
        page.wait_for_selector('body[data-state="idle"]', timeout=TIMEOUT_MS)
        page.wait_for_selector(
            '#mode-status[data-state="browser"], #mode-status[data-state="error"]',
            timeout=PYODIDE_TIMEOUT_MS,
        )
        status = page.locator("#mode-status")
        assert status.get_attribute("data-state") == "browser", status.inner_text()
        assert status.inner_text().strip() == "Browser mode: files are not sent to a server"

        sample = write_hwpx(tmp_path / "synth.hwpx", ["Hello", "Static site"])
        _convert(page, sample, PYODIDE_TIMEOUT_MS)
        assert page.locator("body").get_attribute("data-state") == "done", page.locator(
            "#error"
        ).inner_text()
        name = "i18n-pages-live-en-done.png" if REMOTE_URL else "i18n-pages-en-done.png"
        _screenshot(page, name)
        assert violations == []
        assert posts == []
    finally:
        ctx.close()
