"""Markdown rendering of document blocks (paragraphs and tables)."""

from __future__ import annotations

from collections.abc import Sequence

from .blocks import Block, Paragraph, Table


def _render_cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", "<br>").strip()


def _render_row(cells: Sequence[str]) -> str:
    return "| " + " | ".join(_render_cell(c) for c in cells) + " |"


def _render_table(table: Table) -> str:
    if table.row_count == 0 or table.col_count == 0:
        return ""
    lines = [_render_row(table.rows[0]), "|" + "---|" * table.col_count]
    lines.extend(_render_row(row) for row in table.rows[1:])
    return "\n".join(lines)


def render_blocks(blocks: Sequence[Block]) -> str:
    """블록 문자열 중 비어 있지 않은 것을 '\\n\\n' 으로 join 하고 끝에 '\\n' 1개. 전부 비면 ''."""
    parts: list[str] = []
    for block in blocks:
        text = block.text if isinstance(block, Paragraph) else _render_table(block)
        if text:
            parts.append(text)
    if not parts:
        return ""
    return "\n\n".join(parts) + "\n"


def render_markdown(paragraphs: Sequence[str]) -> str:
    """빈 문자열을 제외한 단락을 '\\n\\n' 으로 join 하고 끝에 '\\n' 1개. 단락이 0개면 ''."""
    return render_blocks([Paragraph(p) for p in paragraphs if p])
