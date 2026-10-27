"""design/v3 화면 E2E (file:// 직접 열기). 외부 CDN 은 막고 marked 만 로컬 사본으로 대신한다."""

from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from playwright.sync_api import Browser, Page, Route, sync_playwright

ROOT = Path(__file__).resolve().parents[2]
V3 = ROOT / "design" / "v3"
MARKED = ROOT / "src" / "hwp2md" / "web" / "static" / "vendor" / "marked.min.js"
VIEWPORT = {"width": 1440, "height": 900}
DRM_TEXT = "문서보안(DRM)이 적용된 파일이라 변환할 수 없습니다"


def _shot_dir() -> Path:
    path = Path(os.environ.get("ILLY_SHOT_DIR", "tests/e2e/screenshots"))
    path.mkdir(parents=True, exist_ok=True)
    return path


def _screenshot(page: Page, name: str) -> None:
    page.screenshot(path=str(_shot_dir() / name), full_page=True)


def _route_external(route: Route) -> None:
    url = route.request.url
    if url.startswith("file:"):
        route.continue_()
    elif "marked" in url and url.endswith(".js"):
        route.fulfill(status=200, content_type="application/javascript", path=str(MARKED))
    else:
        route.abort()


@pytest.fixture(scope="module")
def browser() -> Iterator[Browser]:
    with sync_playwright() as p:
        br = p.chromium.launch(headless=True)
        try:
            yield br
        finally:
            br.close()


@pytest.fixture
def page(browser: Browser) -> Iterator[Page]:
    ctx = browser.new_context(viewport=VIEWPORT, locale="ko-KR")
    ctx.route("**/*", _route_external)
    pg = ctx.new_page()
    try:
        yield pg
    finally:
        ctx.close()


def _open_app(page: Page) -> None:
    page.goto((V3 / "app.html").as_uri())
    page.wait_for_selector('body[data-state="idle"]')
    page.locator(".demo-dock summary").click()


def _wait_end(page: Page) -> None:
    page.wait_for_function("['done', 'error'].includes(document.body.dataset.state)")


def test_app_sample_shows_skipped_with_doc_link(page: Page) -> None:
    _open_app(page)

    page.click('[data-demo="sample"]')
    _wait_end(page)

    assert page.locator("body").get_attribute("data-state") == "done"
    skipped = page.locator("#skipped")
    assert skipped.is_visible()
    assert "변환하지 못한 요소: 머리말·꼬리말 1개" in skipped.inner_text()
    href = skipped.locator("a").get_attribute("href")
    assert href is not None
    assert href.endswith("extraction-limits.md")
    _screenshot(page, "s26-design-app-skipped.png")


def test_app_reset_hides_skipped(page: Page) -> None:
    _open_app(page)
    page.click('[data-demo="sample"]')
    _wait_end(page)
    assert page.locator("#skipped").is_visible()

    page.click('[data-demo="reset"]')

    page.wait_for_selector('body[data-state="idle"]')
    assert page.locator("#skipped").is_hidden()


def test_app_drm_shows_error_text(page: Page) -> None:
    _open_app(page)

    page.click('[data-demo="drm"]')
    _wait_end(page)

    assert page.locator("body").get_attribute("data-state") == "error"
    assert DRM_TEXT in page.locator("#error-text").inner_text()
    assert page.locator("#skipped").is_hidden()


def test_index_limits_list_and_doc_link(page: Page) -> None:
    page.goto((V3 / "index.html").as_uri() + "#limits")
    section = page.locator("#limits")
    section.scroll_into_view_if_needed()

    assert page.locator("#limits li").count() >= 8
    hrefs = [a.get_attribute("href") or "" for a in page.locator("#limits a").element_handles()]
    assert any(h.endswith("extraction-limits.md") for h in hrefs)
    section.screenshot(path=str(_shot_dir() / "s26-design-limits.png"))
