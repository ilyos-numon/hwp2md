"""Check that the preview renderer drops unsafe link/image URLs.

Run: uv run python .ai/tasks/T-20261023-web-preview/spike/xss_check.py
Exit 0 when every case passes.
"""

from __future__ import annotations

import sys

from playwright.sync_api import sync_playwright
from ui_smoke import BASE_URL, log, start_server, stop_server

# (markdown, selector, attribute, expect_attr_present)
CASES = [
    ("[x](javascript:alert(1))", "a", "href", False),
    ("[y](java\tscript:alert(1))", "a", "href", False),
    ("[y2](<java\tscript:alert(1)>)", "a", "href", False),
    ("[y3]( JavaScript:alert(1))", "a", "href", False),
    ("[y4](&#106;avascript:alert(1))", "a", "href", False),
    ("[y5](java%09script:alert(1))", "a", "href", False),
    ("[v](vbscript:msgbox(1))", "a", "href", False),
    ("<javascript:alert(1)>", "a", "href", False),
    ("![z](data:text/html,<script>)", "img", "src", False),
    ("![z2](data:text/html;base64,PHNjcmlwdD4=)", "img", "src", False),
    ("[d](data:image/png;base64,AAAA)", "a", "href", False),
    ("[ok](https://example.com)", "a", "href", True),
    ("[ok2](mailto:a@example.com)", "a", "href", True),
    ("[rel](sub/page.md)", "a", "href", True),
    ("![img](data:image/png;base64,iVBORw0KGgo=)", "img", "src", True),
    ("![rel](doc_images/img_001.png)", "img", "src", True),
]


def main() -> int:
    failures: list[str] = []
    proc = start_server()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                page = browser.new_page()
                page.goto(BASE_URL)
                for md, sel, attr, present in CASES:
                    res = page.evaluate(
                        """([md, sel, attr]) => {
                            const div = document.createElement("div");
                            div.innerHTML = window.marked.parse(md);
                            const el = div.querySelector(sel);
                            return {html: div.innerHTML.trim(),
                                    has: !!(el && el.hasAttribute(attr))};
                        }""",
                        [md, sel, attr],
                    )
                    ok = res["has"] == present
                    log(f"{'OK  ' if ok else 'FAIL'} {md!r} -> {res['html']}")
                    if not ok:
                        failures.append(md)
            finally:
                browser.close()
    finally:
        stop_server(proc)
    if failures:
        log(f"XSS FAIL {len(failures)}/{len(CASES)}")
        return 1
    log(f"XSS OK {len(CASES)}/{len(CASES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main() if len(sys.argv) == 1 else 1)
