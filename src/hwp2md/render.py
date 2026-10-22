"""Markdown rendering of paragraph lists."""

from __future__ import annotations

from collections.abc import Sequence


def render_markdown(paragraphs: Sequence[str]) -> str:
    """빈 문자열을 제외한 단락을 '\\n\\n' 으로 join 하고 끝에 '\\n' 1개. 단락이 0개면 ''."""
    kept = [p for p in paragraphs if p]
    if not kept:
        return ""
    return "\n\n".join(kept) + "\n"
