"""V3 화면(변환 `/`, 소개 `/about`) E2E. 외부 호스트 요청은 차단하고 합성·저장소 샘플만 쓴다."""

from __future__ import annotations

import os
import subprocess
from collections.abc import Callable, Iterator
from pathlib import Path
from urllib.parse import urlparse

import pytest
from conftest import REAL_SAMPLES, WebServer
from playwright.sync_api import Browser, BrowserContext, Page, Route, sync_playwright

from synth_hwpx import write_hwpx
from synth_items import SynthHeaderFooter

RunCli = Callable[[list[str]], subprocess.CompletedProcess[str]]

IMAGE_HWPX = next(p for p in REAL_SAMPLES if p.suffix == ".hwpx" and p.stem.startswith("브라더"))
TIMEOUT_MS = 60_000
VIEWPORT = {"width": 1440, "height": 900}
NARROW = {"width": 390, "height": 844}
NOT_HWP_TEXT = "HWP 5.0 또는 HWPX 파일이 아닙니다"
NOTICE = "본 제품은 한글과컴퓨터의 한/글 문서 파일(.hwp) 공개 문서를 참고하여 개발하였습니다."


def _screenshot(page: Page, name: str, full_page: bool = True) -> None:
    path = Path(os.environ.get("ILLY_SHOT_DIR", "tests/e2e/screenshots"))
    path.mkdir(parents=True, exist_ok=True)
    page.evaluate("window.scrollTo(0, 0)")
    page.screenshot(path=str(path / name), full_page=full_page)


@pytest.fixture(scope="module")
def browser() -> Iterator[Browser]:
    with sync_playwright() as p:
        br = p.chromium.launch(headless=True)
        try:
            yield br
        finally:
            br.close()


@pytest.fixture
def blocked() -> list[str]:
    return []


@pytest.fixture
def make_context(
    browser: Browser, web_server: WebServer, blocked: list[str]
) -> Iterator[Callable[..., BrowserContext]]:
    contexts: list[BrowserContext] = []
    local = f"localhost:{web_server.port}"

    def _guard(route: Route) -> None:
        url = route.request.url
        if urlparse(url).netloc == local:
            route.continue_()
        else:
            blocked.append(url)
            route.abort()

    def _make(**kwargs: object) -> BrowserContext:
        kwargs.setdefault("viewport", VIEWPORT)
        ctx = browser.new_context(**kwargs)  # type: ignore[arg-type]
        ctx.route("**/*", _guard)
        contexts.append(ctx)
        return ctx

    try:
        yield _make
    finally:
        for ctx in contexts:
            ctx.close()


def _open_app(ctx: BrowserContext, web_server: WebServer) -> Page:
    page = ctx.new_page()
    page.goto(web_server.base_url + "/")
    page.wait_for_selector('body[data-state="idle"]', timeout=TIMEOUT_MS)
    return page


def _convert(page: Page, path: Path) -> None:
    page.set_input_files("#file-input", str(path))
    page.wait_for_function(
        "name => document.querySelector('#file-name').textContent === name"
        " && ['done', 'error'].includes(document.body.dataset.state)",
        arg=path.name,
        timeout=TIMEOUT_MS,
    )


def _convert_ok(page: Page, path: Path) -> None:
    _convert(page, path)
    state = page.locator("body").get_attribute("data-state")
    assert state == "done", page.locator("#error").inner_text()


def test_v3_server_convert_offline(
    make_context: Callable[..., BrowserContext],
    web_server: WebServer,
    blocked: list[str],
    tmp_path: Path,
    run_cli: RunCli,
) -> None:
    page = _open_app(make_context(), web_server)
    page.set_input_files("#file-input", str(IMAGE_HWPX))
    page.wait_for_selector('body[data-state="done"]', timeout=TIMEOUT_MS)
    meta = page.locator("#result-meta").inner_text()

    assert "이미지 1개" in meta
    assert page.evaluate("window.gsap.version") == "3.13.0"
    assert page.evaluate("typeof window.Hwp2mdDemo") == "undefined"
    assert page.locator(".demo-dock").count() == 0
    assert page.locator("#demo-sample").count() == 0

    result = run_cli([str(IMAGE_HWPX), "-o", str(tmp_path)])
    assert result.returncode == 0, result.stderr
    cli_md = (tmp_path / f"{IMAGE_HWPX.stem}.md").read_text(encoding="utf-8")
    assert page.locator("#raw").text_content() == cli_md
    assert page.locator("#preview table").count() == 8

    page.wait_for_load_state("networkidle")
    _screenshot(page, "v3-app-done.png")
    assert blocked == []


def test_v3_not_hwp_error_and_close(
    make_context: Callable[..., BrowserContext],
    web_server: WebServer,
    blocked: list[str],
    tmp_path: Path,
) -> None:
    bad = tmp_path / "not.hwp"
    bad.write_text("plain text, not an ole file\n" * 100, encoding="utf-8")
    page = _open_app(make_context(), web_server)

    _convert(page, bad)

    assert page.locator("body").get_attribute("data-state") == "error"
    assert NOT_HWP_TEXT in page.locator("#error-text").inner_text()
    assert page.locator("#download").is_disabled()
    _screenshot(page, "v3-app-error.png")

    page.click("#error-close")
    assert page.locator("#error").is_hidden()
    assert blocked == []


def test_v3_skipped_links_about(
    make_context: Callable[..., BrowserContext],
    web_server: WebServer,
    blocked: list[str],
    tmp_path: Path,
) -> None:
    doc = write_hwpx(tmp_path / "header.hwpx", [SynthHeaderFooter(("쪽 머리말",)), "합성 본문"])
    page = _open_app(make_context(), web_server)
    _convert_ok(page, doc)

    link = page.locator("#skipped a")
    assert link.get_attribute("href") == "/about#limits"
    link.click()
    page.wait_for_url("**/about#limits")
    page.locator("#limits").scroll_into_view_if_needed()
    page.wait_for_function(
        "() => { const e = document.querySelector('#limits');"
        " return e.getBoundingClientRect().height > 0 && getComputedStyle(e).opacity !== '0'; }",
        timeout=TIMEOUT_MS,
    )
    assert page.locator("#limits").is_visible()
    assert blocked == []


def test_v3_about_offline(
    make_context: Callable[..., BrowserContext],
    web_server: WebServer,
    blocked: list[str],
) -> None:
    page = make_context().new_page()
    page.goto(web_server.base_url + "/about")
    page.wait_for_load_state("networkidle")

    for name in ("ScrollTrigger", "SplitText", "ScrambleTextPlugin"):
        assert page.evaluate(f"typeof window.{name}") != "undefined", name
    assert page.locator("#limits li").count() >= 8
    assert page.locator('a:has-text("변환 도구 열기")').first.get_attribute("href") == "/"
    assert NOTICE in page.locator("body").inner_text()

    fonts_css = page.request.get(web_server.base_url + "/static/vendor/fonts/fonts.css").text()
    if "@font-face" in fonts_css:
        assert page.evaluate(
            "document.fonts.ready.then(() => document.fonts.check('16px \"Pretendard Variable\"'))"
        )
    else:
        assert "-apple-system" in page.evaluate("getComputedStyle(document.body).fontFamily")

    _screenshot(page, "v3-about.png")

    page.evaluate("window.scrollTo(0, 0)")
    page.evaluate("document.fonts.ready.then(() => true)")
    page.wait_for_function(
        "() => window.__h2mReady === true"
        " && document.querySelector('#hero-title .hero__md').textContent === 'Markdown'",
        timeout=TIMEOUT_MS,
    )
    _screenshot(page, "v3-about-hero.png", full_page=False)

    page.locator("#limits").scroll_into_view_if_needed()
    page.wait_for_function(
        "() => [...document.querySelectorAll('#limits li')]"
        ".every(e => getComputedStyle(e).opacity === '1')",
        timeout=TIMEOUT_MS,
    )
    page.screenshot(
        path=str(
            Path(os.environ.get("ILLY_SHOT_DIR", "tests/e2e/screenshots")) / "v3-about-limits.png"
        )
    )
    assert blocked == []


def test_v3_dark_theme(
    make_context: Callable[..., BrowserContext],
    web_server: WebServer,
    blocked: list[str],
) -> None:
    page = _open_app(make_context(), web_server)
    page.click(".theme-toggle")
    page.wait_for_selector('html[data-theme="dark"]')

    page.reload()
    page.wait_for_selector('body[data-state="idle"]', timeout=TIMEOUT_MS)
    assert page.locator("html").get_attribute("data-theme") == "dark"

    _convert_ok(page, IMAGE_HWPX)
    page.wait_for_load_state("networkidle")
    _screenshot(page, "v3-app-dark.png")
    assert blocked == []


def test_v3_narrow_tabs(
    make_context: Callable[..., BrowserContext],
    web_server: WebServer,
    blocked: list[str],
) -> None:
    page = _open_app(make_context(viewport=NARROW), web_server)
    _convert_ok(page, IMAGE_HWPX)

    assert page.locator("#pane-raw").is_hidden()
    page.click("#tab-raw")
    assert page.locator("#pane-raw").is_visible()
    assert page.locator("#pane-preview").is_hidden()

    page.wait_for_load_state("networkidle")
    _screenshot(page, "v3-app-narrow.png")
    assert blocked == []


def test_v3_copy_button(
    make_context: Callable[..., BrowserContext],
    web_server: WebServer,
    blocked: list[str],
) -> None:
    ctx = make_context(permissions=["clipboard-read", "clipboard-write"])
    page = _open_app(ctx, web_server)
    _convert_ok(page, IMAGE_HWPX)

    page.click("#copy")

    page.wait_for_function(
        "() => document.querySelector('#toast').textContent === 'Markdown 원문을 복사했습니다'",
        timeout=TIMEOUT_MS,
    )
    copied = page.evaluate("navigator.clipboard.readText()")
    assert copied == page.locator("#raw").text_content()
    assert blocked == []
