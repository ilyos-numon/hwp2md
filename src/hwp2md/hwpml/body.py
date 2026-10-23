"""HWPML BODY tree -> blocks (paragraphs, headings, tables, pictures).

HWPX(OWPML) 요소와 1:1 대응한다 (대문자 요소명·CamelCase 속성). 표 칸 배치는 hwpx.body 의
_place_cells 를 그대로 쓴다."""

from __future__ import annotations

from collections.abc import Callable, Iterable

from lxml import etree

from ..blocks import Block, Image, Paragraph, Table, make_paragraph, make_table
from ..hwpx.body import CellSpec, _place_cells

MAX_HEADING_LEVEL = 6
HEADING_OUTLINE = "Outline"  # PARASHAPE/@HeadingType 값. 그 외: None, Number, Bullet
# CHAR 의 자식 인라인 요소 → 텍스트. 없는 태그는 "" (뒤따르는 tail 텍스트는 유지)
INLINE_TEXT: dict[str, str] = {
    "TAB": " ",
    "LINEBREAK": "\n",
    "NBSPACE": " ",
    "FWSPACE": " ",
    "HYPEN": "-",  # HWPML 요소명 철자가 HYPEN 이다
}

ImageResolver = Callable[[str], Image | None]


def _int_attr(el: etree._Element | None, name: str) -> int | None:
    if el is None:
        return None
    value = el.get(name)
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def parse_para_levels(root: etree._Element) -> dict[int, int]:
    """PARASHAPE Id → 제목 수준 (HeadingType="Outline" 인 것만, min(Level + 1, 6))."""
    levels: dict[int, int] = {}
    for ps in root.iter("PARASHAPE"):
        pid = _int_attr(ps, "Id")
        if pid is None or ps.get("HeadingType") != HEADING_OUTLINE:
            continue
        lvl = _int_attr(ps, "Level")
        if lvl is None:
            continue
        levels[pid] = min(max(lvl, 0) + 1, MAX_HEADING_LEVEL)
    return levels


def text_of_char(ch: etree._Element) -> str:
    parts = [ch.text or ""]
    for child in ch:
        if isinstance(child.tag, str):
            parts.append(INLINE_TEXT.get(child.tag, ""))
        parts.append(child.tail or "")
    return "".join(parts)


def parse_paragraph(
    p: etree._Element,
    para_levels: dict[int, int],
    resolve_image: ImageResolver | None = None,
) -> list[Block]:
    """resolve_image 가 None 이면 그림은 버린다 (표 칸 안, HWPX 리더와 같은 동작)."""
    pid = _int_attr(p, "ParaShape")
    level = 0 if pid is None else para_levels.get(pid, 0)
    blocks: list[Block] = []
    buf: list[str] = []

    def flush() -> None:
        para = make_paragraph(["".join(buf)], level)
        buf.clear()
        if para is not None:
            blocks.append(para)

    def append_image(pic: etree._Element) -> None:
        if resolve_image is None:
            return
        img = pic.find("IMAGE")
        if img is None:
            return
        ref = img.get("BinItem")
        if not ref:
            return
        image = resolve_image(ref)
        if image is None:
            return
        flush()
        blocks.append(image)

    for text in p.iterchildren("TEXT"):
        for child in text:
            if not isinstance(child.tag, str):
                continue
            if child.tag == "CHAR":
                buf.append(text_of_char(child))
            elif child.tag == "TABLE":
                flush()
                table = parse_table(child, para_levels)
                if table is not None:
                    blocks.append(table)
            elif child.tag == "PICTURE":
                append_image(child)
            elif child.tag == "CONTAINER":
                for pic in child.iter("PICTURE"):
                    append_image(pic)
            # 그 외(SECDEF, HEADER, FOOTER, FIELDBEGIN, 각주, 도형, ...)는 무시
    flush()
    return blocks


def parse_table(tbl: etree._Element, para_levels: dict[int, int]) -> Table | None:
    rows_el = list(tbl.iterchildren("ROW"))
    row_cnt = _int_attr(tbl, "RowCount")
    col_cnt = _int_attr(tbl, "ColCount")
    # 속성이 있으면 0 이어도 그 값을 쓴다 (HWPX·HWP 5.0 리더와 동일)
    rows = len(rows_el) if row_cnt is None else row_cnt
    cols = (
        max((len(list(r.iterchildren("CELL"))) for r in rows_el), default=0)
        if col_cnt is None
        else col_cnt
    )
    if rows <= 0 or cols <= 0:
        return None
    cells: list[CellSpec] = []
    for r_idx, row in enumerate(rows_el):
        for cell in row.iterchildren("CELL"):
            r = _int_attr(cell, "RowAddr")
            c = _int_attr(cell, "ColAddr")
            row_span = _int_attr(cell, "RowSpan")
            col_span = _int_attr(cell, "ColSpan")
            cells.append(
                CellSpec(
                    row=r_idx if r is None else r,
                    col=-1 if c is None else c,
                    row_span=1 if row_span is None else row_span,
                    col_span=1 if col_span is None else col_span,
                    text=_cell_text(cell, para_levels),
                )
            )
    grid = _place_cells(rows, cols, cells)
    return make_table([[(text,) for text in row] for row in grid])


def _cell_text(cell: etree._Element, para_levels: dict[int, int]) -> str:
    paralist = cell.find("PARALIST")
    if paralist is None:
        return ""
    parts: list[str] = []
    for p in paralist.iterchildren("P"):
        for b in parse_paragraph(p, para_levels):
            if isinstance(b, Paragraph):
                parts.append(b.text)
            elif isinstance(b, Table):
                flat = " ".join(c for row in b.rows for c in row if c)
                if flat:
                    parts.append(flat)
    return "\n".join(parts)


def parse_body(
    sections: Iterable[etree._Element],
    para_levels: dict[int, int],
    resolve_image: ImageResolver | None = None,
) -> list[Block]:
    blocks: list[Block] = []
    for section in sections:
        for p in section.iterchildren("P"):
            blocks.extend(parse_paragraph(p, para_levels, resolve_image))
    return blocks
