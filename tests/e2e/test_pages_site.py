"""정적 사이트(GitHub Pages 형태) E2E. 하위 경로에서 소개 -> 변환, 실패 경로 2개.

`HWP2MD_PAGES_URL`(끝 슬래시 포함 base)이 있으면 그 주소로, 없으면 로컬 http.server 로 돈다.
입력은 합성 HWPX 만 쓴다.
"""

from __future__ import annotations

import importlib.util
import os
import socket
import subprocess
import sys
import time
import urllib.request
from collections.abc import Callable, Iterator
from pathlib import Path
from urllib.parse import urlparse

import pytest
from playwright.sync_api import Browser, BrowserContext, Page, Request, Route, sync_playwright

from synth_hwpx import write_hwpx

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "build_pages.py"
TIMEOUT_MS = 60_000
PYODIDE_TIMEOUT_MS = 240_000
VIEWPORT = {"width": 1440, "height": 900}
NOT_HWP_TEXT = "HWP 5.0 또는 HWPX 파일이 아닙니다"
CDN_HOST = "cdn.jsdelivr.net"
REMOTE_URL = os.environ.get("HWP2MD_PAGES_URL", "").strip()
SHOT_PREFIX = "pages-live" if REMOTE_URL else "pages"


def _screenshot(page: Page, name: str) -> None:
    path = Path(os.environ.get("ILLY_SHOT_DIR", "tests/e2e/screenshots"))
    path.mkdir(parents=True, exist_ok=True)
    page.evaluate("window.scrollTo(0, 0)")
    page.screenshot(path=str(path / name), full_page=True)


def _load_build_pages() -> object:
    spec = importlib.util.spec_from_file_location("build_pages_e2e", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("localhost", 0))
        return int(s.getsockname()[1])


@pytest.fixture(scope="module")
def pages_base(tmp_path_factory: pytest.TempPathFactory) -> Iterator[str]:
    if REMOTE_URL:
        yield REMOTE_URL if REMOTE_URL.endswith("/") else REMOTE_URL + "/"
        return
    root = tmp_path_factory.mktemp("pages") / "site"
    _load_build_pages().build_site(root / "hwp2md")  # type: ignore[attr-defined]
    port = _free_port()
    env = {k: v for k, v in os.environ.items() if k != "VIRTUAL_ENV"}
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "http.server",
            str(port),
            "--bind",
            "localhost",
            "--directory",
            str(root),
        ],
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


@pytest.fixture(scope="module")
def browser() -> Iterator[Browser]:
    with sync_playwright() as p:
        br = p.chromium.launch(headless=True)
        try:
            yield br
        finally:
            br.close()


class Guard:
    def __init__(self) -> None:
        self.violations: list[str] = []
        self.posts: list[str] = []
        self.cdn_blocked: list[str] = []


@pytest.fixture
def make_context(
    browser: Browser, pages_base: str
) -> Iterator[Callable[..., tuple[BrowserContext, Guard]]]:
    contexts: list[BrowserContext] = []
    base = urlparse(pages_base)

    def _make(*, block_cdn: bool = False) -> tuple[BrowserContext, Guard]:
        guard = Guard()
        ctx = browser.new_context(viewport=VIEWPORT, accept_downloads=True, locale="ko-KR")

        def _on_request(req: Request) -> None:
            if req.method == "POST":
                guard.posts.append(req.url)

        def _route(route: Route) -> None:
            url = urlparse(route.request.url)
            if url.netloc == base.netloc:
                if not url.path.startswith(base.path):
                    guard.violations.append(route.request.url)
                route.continue_()
            elif url.hostname == CDN_HOST and not block_cdn:
                route.continue_()
            elif url.hostname == CDN_HOST:
                guard.cdn_blocked.append(route.request.url)
                route.abort()
            else:
                guard.violations.append(route.request.url)
                route.abort()

        ctx.on("request", _on_request)
        ctx.route("**/*", _route)
        contexts.append(ctx)
        return ctx, guard

    try:
        yield _make
    finally:
        for ctx in contexts:
            ctx.close()


def _convert(page: Page, path: Path) -> None:
    page.set_input_files("#file-input", str(path))
    page.wait_for_function(
        "name => document.querySelector('#file-name').textContent === name"
        " && ['done', 'error'].includes(document.body.dataset.state)",
        arg=path.name,
        timeout=TIMEOUT_MS,
    )


def test_pages_landing_to_convert(
    make_context: Callable[..., tuple[BrowserContext, Guard]],
    pages_base: str,
    tmp_path: Path,
) -> None:
    ctx, guard = make_context()
    page = ctx.new_page()
    page.goto(pages_base, wait_until="load")
    page.wait_for_selector('a[href="convert.html"]', timeout=TIMEOUT_MS)
    _screenshot(page, f"{SHOT_PREFIX}-landing.png")

    page.locator('a[href="convert.html"]').first.click()
    page.wait_for_url("**/convert.html", timeout=TIMEOUT_MS)
    page.wait_for_selector('body[data-state="idle"]', timeout=TIMEOUT_MS)
    assert page.locator("label.switch").is_hidden()
    page.wait_for_selector(
        '#mode-status[data-state="browser"], #mode-status[data-state="error"]',
        timeout=PYODIDE_TIMEOUT_MS,
    )
    status = page.locator("#mode-status")
    assert status.get_attribute("data-state") == "browser", status.inner_text()
    assert page.evaluate("window.Hwp2mdApp.staticSite") is True

    sample = write_hwpx(tmp_path / "합성.hwpx", ["안녕하세요", "정적 사이트 변환 확인"])
    _convert(page, sample)
    assert page.locator("body").get_attribute("data-state") == "done", page.locator(
        "#error"
    ).inner_text()
    _screenshot(page, f"{SHOT_PREFIX}-convert-done.png")

    assert guard.violations == []
    assert guard.posts == []


def test_pages_not_hwp(
    make_context: Callable[..., tuple[BrowserContext, Guard]],
    pages_base: str,
    tmp_path: Path,
) -> None:
    ctx, guard = make_context()
    page = ctx.new_page()
    page.goto(pages_base + "convert.html", wait_until="load")
    page.wait_for_selector(
        '#mode-status[data-state="browser"], #mode-status[data-state="error"]',
        timeout=PYODIDE_TIMEOUT_MS,
    )
    assert page.locator("#mode-status").get_attribute("data-state") == "browser"

    bad = tmp_path / "가짜.hwp"
    bad.write_text("이것은 한글 문서가 아닙니다", encoding="utf-8")
    _convert(page, bad)
    assert page.locator("body").get_attribute("data-state") == "error"
    assert NOT_HWP_TEXT in page.locator("#error").inner_text()
    assert guard.violations == []
    assert guard.posts == []


def test_pages_cdn_blocked(
    make_context: Callable[..., tuple[BrowserContext, Guard]],
    pages_base: str,
    tmp_path: Path,
) -> None:
    ctx, guard = make_context(block_cdn=True)
    page = ctx.new_page()
    page.goto(pages_base + "convert.html", wait_until="load")
    page.wait_for_selector(
        '#mode-status[data-state="browser"], #mode-status[data-state="error"]',
        timeout=PYODIDE_TIMEOUT_MS,
    )
    assert page.locator("#mode-status").get_attribute("data-state") == "error"
    assert guard.cdn_blocked

    sample = write_hwpx(tmp_path / "합성.hwpx", ["안녕하세요"])
    _convert(page, sample)
    assert page.locator("body").get_attribute("data-state") == "error"
    assert page.locator("#error-text").inner_text().strip() != ""
    _screenshot(page, f"{SHOT_PREFIX}-cdn-blocked.png")
    assert guard.violations == []
    assert guard.posts == []
