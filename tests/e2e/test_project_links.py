"""바닥글 프로젝트 링크(GitHub·PyPI) E2E.

서버 화면(`/`, `/about`)과 정적 사이트(build_site) 양쪽을 본다. 링크는 새 창 텍스트 링크뿐이다.
페이지를 불러올 때 localhost 밖으로 나가는 요청은 0건이어야 하고,
정적 사이트 변환 화면(convert.html)만 Pyodide CDN 을 허용한다.
"""

from __future__ import annotations

import importlib.util
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
from playwright.sync_api import Browser, BrowserContext, Page, Route, sync_playwright

from conftest import WebServer

ROOT = Path(__file__).resolve().parents[2]
BUILD_SCRIPT = ROOT / "scripts" / "build_pages.py"
TIMEOUT_MS = 60_000
VIEWPORT = {"width": 1440, "height": 900}
CDN_HOST = "cdn.jsdelivr.net"

GITHUB_URL = "https://github.com/ilyos-numon/hwp2md"
PYPI_URL = "https://pypi.org/project/hwp2markdown/"
LABELS = {
    "ko": {
        "github": ("GitHub", "GitHub 저장소 (새 창)"),
        "pypi": ("PyPI", "PyPI 패키지 (새 창)"),
    },
    "en": {
        "github": ("GitHub", "GitHub repository (opens in a new tab)"),
        "pypi": ("PyPI", "PyPI package (opens in a new tab)"),
    },
}
HREFS = {"github": GITHUB_URL, "pypi": PYPI_URL}


@pytest.fixture(scope="module")
def browser() -> Iterator[Browser]:
    with sync_playwright() as p:
        br = p.chromium.launch(headless=True)
        try:
            yield br
        finally:
            br.close()


def _guarded(
    browser: Browser, locale: str, allow_cdn: bool = False
) -> tuple[BrowserContext, list[str]]:
    """localhost 밖 요청을 막고 기록하는 컨텍스트. allow_cdn 이면 Pyodide CDN 만 통과시킨다."""
    ctx = browser.new_context(viewport=VIEWPORT, locale=locale)
    outside: list[str] = []

    def _route(route: Route) -> None:
        host = urlparse(route.request.url).hostname
        if host == "localhost" or (allow_cdn and host == CDN_HOST):
            route.continue_()
        else:
            outside.append(route.request.url)
            route.abort()

    ctx.route("**/*", _route)
    return ctx, outside


def _load(ctx: BrowserContext, url: str) -> Page:
    page = ctx.new_page()
    page.goto(url, wait_until="load")
    page.wait_for_function("() => !!window.Hwp2mdI18n", timeout=TIMEOUT_MS)
    page.wait_for_selector("footer #link-github", state="attached", timeout=TIMEOUT_MS)
    return page


def _assert_links(page: Page, lang: str) -> None:
    for name in ("github", "pypi"):
        link = page.locator(f"footer #link-{name}")
        assert link.count() == 1, name
        assert link.get_attribute("href") == HREFS[name]
        assert link.get_attribute("target") == "_blank"
        assert "noopener" in (link.get_attribute("rel") or "").split()
        text, label = LABELS[lang][name]
        assert link.inner_text().strip() == text
        assert link.get_attribute("aria-label") == label


def _shot(page: Page, name: str) -> None:
    path = Path(os.environ.get("ILLY_SHOT_DIR", "tests/e2e/screenshots"))
    path.mkdir(parents=True, exist_ok=True)
    footer = page.locator("footer").first
    footer.scroll_into_view_if_needed()
    footer.screenshot(path=str(path / name))


@pytest.mark.parametrize("path", ["/", "/about"])
@pytest.mark.parametrize("lang", ["ko", "en"])
def test_server_footer_links(browser: Browser, web_server: WebServer, path: str, lang: str) -> None:
    ctx, outside = _guarded(browser, "ko-KR" if lang == "ko" else "en-US")
    try:
        page = _load(ctx, f"{web_server.base_url}{path}?lang={lang}")
        assert page.locator("html").get_attribute("lang") == lang
        _assert_links(page, lang)
        if lang == "en":
            assert page.evaluate("window.Hwp2mdI18n.missing()") == []
            if path == "/about":
                _shot(page, "s1-footer-en.png")
            else:
                _shot(page, "s1-convert-footer-en.png")
        page.wait_for_load_state("networkidle")
        assert outside == []
    finally:
        ctx.close()


@pytest.mark.parametrize("path", ["/", "/about"])
def test_invalid_lang_still_has_links(browser: Browser, web_server: WebServer, path: str) -> None:
    ctx, outside = _guarded(browser, "ko-KR")
    try:
        page = _load(ctx, f"{web_server.base_url}{path}?lang=xx")
        assert page.locator("html").get_attribute("lang") == "ko"
        _assert_links(page, "ko")
        page.wait_for_load_state("networkidle")
        assert outside == []
    finally:
        ctx.close()


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("localhost", 0))
        return int(s.getsockname()[1])


@pytest.fixture(scope="module")
def local_pages(tmp_path_factory: pytest.TempPathFactory) -> Iterator[str]:
    spec = importlib.util.spec_from_file_location("build_pages_links", BUILD_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    root = tmp_path_factory.mktemp("pages-links") / "site"
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


@pytest.mark.parametrize("page_name", ["index.html", "convert.html"])
def test_static_site_footer_links(browser: Browser, local_pages: str, page_name: str) -> None:
    ctx, outside = _guarded(browser, "en-US", allow_cdn=page_name == "convert.html")
    try:
        page = _load(ctx, local_pages + page_name)
        assert page.locator("html").get_attribute("lang") == "en"
        _assert_links(page, "en")
        if page_name == "index.html":
            page.wait_for_load_state("networkidle")
        assert outside == []
    finally:
        ctx.close()
