"""Markdown rendering of document blocks (paragraphs and tables)."""

from __future__ import annotations

import re
from collections.abc import Sequence

from .blocks import Block, Image, Inline, Link, Math, Note, NoteRef, Paragraph, Table

_SAFE_SCHEMES = ("http", "https", "mailto")
_SCHEME = re.compile(r"^([A-Za-z][A-Za-z0-9+.\-]*):")
_URL_ESCAPES = ((" ", "%20"), ("(", "%28"), (")", "%29"), ("<", "%3C"), (">", "%3E"))
_NUMERIC_LABEL = re.compile(r"^\d{1,9}[.)]$")
_BACKTICK_RUN = re.compile(r"`+")
_LIST_INDENT = "    "


def safe_link_url(url: str) -> str | None:
    """strip 후 스킴(소문자)이 http·https·mailto 면 퍼센트 인코딩(공백 %20, ( %28, ) %29, < %3C,
    > %3E)한 값, 아니면 None."""
    value = url.strip()
    match = _SCHEME.match(value)
    if match is None or match.group(1).lower() not in _SAFE_SCHEMES:
        return None
    for raw, encoded in _URL_ESCAPES:
        value = value.replace(raw, encoded)
    return value


class _Context:
    def __init__(self, image_dir: str) -> None:
        self.image_dir = image_dir
        self.image_n = 0

    def image(self, img: Image) -> str:
        self.image_n += 1
        return _render_image(img, self.image_n, self.image_dir)


def _render_cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", "<br>").strip()


def _render_row(cells: Sequence[str]) -> str:
    return "| " + " | ".join(cells) + " |"


def _render_table(table: Table, ctx: _Context) -> str:
    if table.row_count == 0 or table.col_count == 0:
        return ""
    if table.cells:
        grid = [[_render_inline_cell(cell, ctx) for cell in row] for row in table.cells]
    else:
        grid = [[_render_cell(c) for c in row] for row in table.rows]
    lines = [_render_row(grid[0]), "|" + "---|" * table.col_count]
    lines.extend(_render_row(row) for row in grid[1:])
    return "\n".join(lines)


def _render_inline_cell(cell: Sequence[Inline], ctx: _Context) -> str:
    return _render_inlines(cell, ctx, cell_mode=True).replace("\n", "<br>").strip()


def _code_span(script: str) -> str:
    longest = max((len(run) for run in _BACKTICK_RUN.findall(script)), default=0)
    fence = "`" * (longest + 1)
    pad = " " if script.startswith("`") or script.endswith("`") else ""
    return f"{fence}{pad}{script}{pad}{fence}"


def _render_math(math: Math, display: bool) -> str:
    if math.latex is None:
        return _code_span(math.script)
    if display:
        return f"$${math.latex}$$"
    return f"${math.latex}$"


def _is_display_math(inlines: Sequence[Inline]) -> bool:
    rest = [item for item in inlines if not (isinstance(item, str) and not item.strip())]
    return len(rest) == 1 and isinstance(rest[0], Math)


def _render_inline(item: Inline, ctx: _Context, *, cell_mode: bool, display: bool) -> str:
    if isinstance(item, str):
        return item.replace("|", "\\|") if cell_mode else item
    if isinstance(item, Link):
        text = item.text.replace("|", "\\|") if cell_mode else item.text
        url = safe_link_url(item.url)
        if url is None:
            return text
        return "[" + text.replace("[", "\\[").replace("]", "\\]") + "](" + url + ")"
    if isinstance(item, NoteRef):
        return f"[^{item.number}]" if item.kind == "footnote" else f"[^e{item.number}]"
    if isinstance(item, Math):
        return _render_math(item, display)
    return ctx.image(item)


def _render_inlines(inlines: Sequence[Inline], ctx: _Context, *, cell_mode: bool = False) -> str:
    display = not cell_mode and _is_display_math(inlines)
    return "".join(
        _render_inline(item, ctx, cell_mode=cell_mode, display=display) for item in inlines
    ).strip()


def _render_paragraph(p: Paragraph, ctx: _Context) -> str:
    """level <= 0 → p.text 그대로(현재 동작). inlines 가 있으면 인라인 렌더 결과(strip).
    level >= 1 → text 의 "\\n" 을 공백으로 바꾸고 strip; text 가 "" 이면 "" (블록 생략);
                 아니면 "#" * min(p.level, 6) + " " + text."""
    text = _render_inlines(p.inlines, ctx) if p.inlines else p.text
    if p.level <= 0:
        return text
    text = text.replace("\n", " ").strip()
    if not text:
        return ""
    return "#" * min(p.level, 6) + " " + text


def _render_list_item(
    p: Paragraph, ctx: _Context, prev_level: int | None
) -> tuple[str, int | None]:
    """(문자열, 목록 문법 항목이면 유효 수준 아니면 None)."""
    info = p.list_info
    assert info is not None
    body = (_render_inlines(p.inlines, ctx) if p.inlines else p.text).strip()
    if not body:
        return "", None
    if info.kind == "bullet":
        head = "-"
    elif _NUMERIC_LABEL.match(info.label):
        head = info.label
    else:
        return (f"{info.label} {body}" if info.label else body), None
    level = 0 if prev_level is None else min(max(info.depth, 0), prev_level + 1)
    return f"{_LIST_INDENT * level}{head} {body}", level


def _render_note(note: Note, ctx: _Context) -> str:
    label = f"[^{note.number}]" if note.kind == "footnote" else f"[^e{note.number}]"
    texts = [t for t in (_render_paragraph(p, ctx) for p in note.paragraphs) if t]
    if not texts:
        return f"{label}:"
    out = f"{label}: {texts[0]}"
    for text in texts[1:]:
        out += "\n\n" + _LIST_INDENT + text.replace("\n", "\n" + _LIST_INDENT)
    return out


def _render_image(img: Image, n: int, image_dir: str) -> str:
    path = f"{image_dir}/{img.file_name}" if image_dir else img.file_name
    return f"![그림 {n}]({path.replace(' ', '%20')})"


def render_blocks(blocks: Sequence[Block], *, image_dir: str = "") -> str:
    """블록 문자열 중 비어 있지 않은 것을 '\\n\\n' 으로 join 하고 끝에 '\\n' 1개. 전부 비면 ''.
    이미지 번호 n 은 블록 이미지와 인라인 이미지가 공유하며 렌더 순으로 1부터 증가.
    목록 문법 항목(글머리표·숫자 머리)끼리는 '\\n' 하나로 잇는다."""
    ctx = _Context(image_dir)
    out: list[str] = []
    prev_level: int | None = None  # 직전 렌더 블록이 목록 문법 항목이면 그 유효 수준
    for block in blocks:
        level: int | None = None
        if isinstance(block, Image):
            text = ctx.image(block)
        elif isinstance(block, Paragraph):
            if block.list_info is not None and block.level <= 0:
                text, level = _render_list_item(block, ctx, prev_level)
            else:
                text = _render_paragraph(block, ctx)
        elif isinstance(block, Table):
            text = _render_table(block, ctx)
        else:
            text = _render_note(block, ctx)
        if not text:
            continue
        if out:
            out.append("\n" if level is not None and prev_level is not None else "\n\n")
        out.append(text)
        prev_level = level
    if not out:
        return ""
    return "".join(out) + "\n"


def render_markdown(paragraphs: Sequence[str]) -> str:
    """빈 문자열을 제외한 단락을 '\\n\\n' 으로 join 하고 끝에 '\\n' 1개. 단락이 0개면 ''."""
    return render_blocks([Paragraph(p) for p in paragraphs if p])
