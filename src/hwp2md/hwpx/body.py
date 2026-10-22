"""OWPML section tree -> blocks (paragraphs and tables)."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from lxml import etree

from ..blocks import Block, Paragraph, Table
from .header import EMPTY_HEADER, HeaderInfo

NS_HP = "http://www.hancom.co.kr/hwpml/2011/paragraph"
HP_P = f"{{{NS_HP}}}p"
HP_RUN = f"{{{NS_HP}}}run"
HP_T = f"{{{NS_HP}}}t"
HP_TBL = f"{{{NS_HP}}}tbl"
HP_TR = f"{{{NS_HP}}}tr"
HP_TC = f"{{{NS_HP}}}tc"
HP_SUBLIST = f"{{{NS_HP}}}subList"
HP_CELL_ADDR = f"{{{NS_HP}}}cellAddr"
HP_CELL_SPAN = f"{{{NS_HP}}}cellSpan"
# hp:t 의 자식 인라인 요소 → 텍스트. 없는 태그는 "" (뒤따르는 tail 텍스트는 유지)
INLINE_TEXT: dict[str, str] = {
    f"{{{NS_HP}}}tab": " ",
    f"{{{NS_HP}}}lineBreak": "\n",
    f"{{{NS_HP}}}nbSpace": " ",
    f"{{{NS_HP}}}fwSpace": " ",
    f"{{{NS_HP}}}hypen": "-",  # OWPML 요소명 철자가 hypen 이다
}


@dataclass(frozen=True)
class CellSpec:
    row: int
    col: int
    row_span: int
    col_span: int
    text: str


def text_of_t(t: etree._Element) -> str:
    parts = [t.text or ""]
    for child in t:
        if isinstance(child.tag, str):
            parts.append(INLINE_TEXT.get(child.tag, ""))
        parts.append(child.tail or "")
    return "".join(parts)


def parse_paragraph(p: etree._Element, header: HeaderInfo = EMPTY_HEADER) -> list[Block]:
    level = header.heading_level(_int_attr(p, "paraPrIDRef"))
    blocks: list[Block] = []
    buf: list[str] = []

    def flush() -> None:
        text = "".join(buf).strip()
        buf.clear()
        if text:
            blocks.append(Paragraph(text, level))

    for run in p.iterchildren(HP_RUN):
        for child in run:
            if not isinstance(child.tag, str):
                continue
            if child.tag == HP_T:
                buf.append(text_of_t(child))
            elif child.tag == HP_TBL:
                flush()
                table = parse_table(child)
                if table is not None:
                    blocks.append(table)
            # 그 외(secPr, ctrl, 각주, pic, ...)는 무시
    flush()
    return blocks


def parse_table(tbl: etree._Element) -> Table | None:
    trs = list(tbl.iterchildren(HP_TR))
    row_cnt = _int_attr(tbl, "rowCnt")
    col_cnt = _int_attr(tbl, "colCnt")
    # 속성이 있으면 0 이어도 그 값을 쓴다 (rowCnt="0" → 표 버림, HWP 5.0 리더와 동일)
    rows = len(trs) if row_cnt is None else row_cnt
    cols = (
        max((len(list(tr.iterchildren(HP_TC))) for tr in trs), default=0)
        if col_cnt is None
        else col_cnt
    )
    if rows <= 0 or cols <= 0:
        return None
    cells: list[CellSpec] = []
    for r_idx, tr in enumerate(trs):
        for tc in tr.iterchildren(HP_TC):
            addr = tc.find(HP_CELL_ADDR)
            span = tc.find(HP_CELL_SPAN)
            row = _int_attr(addr, "rowAddr")
            col = _int_attr(addr, "colAddr")
            row_span = _int_attr(span, "rowSpan")
            col_span = _int_attr(span, "colSpan")
            cells.append(
                CellSpec(
                    row=r_idx if row is None else row,
                    col=-1 if col is None else col,
                    row_span=1 if row_span is None else row_span,
                    col_span=1 if col_span is None else col_span,
                    text=_cell_text(tc),
                )
            )
    return Table(rows=_place_cells(rows, cols, cells))


def _cell_text(tc: etree._Element) -> str:
    sub = tc.find(HP_SUBLIST)
    if sub is None:
        return ""
    parts: list[str] = []
    for p in sub.iterchildren(HP_P):
        for b in parse_paragraph(p):
            if isinstance(b, Paragraph):
                parts.append(b.text)
            elif isinstance(b, Table):
                flat = " ".join(c for row in b.rows for c in row if c)
                if flat:
                    parts.append(flat)
    return "\n".join(parts)


def _place_cells(rows: int, cols: int, cells: Sequence[CellSpec]) -> list[list[str]]:
    grid: list[list[str | None]] = [[None] * cols for _ in range(rows)]
    for cell in cells:
        r, c = cell.row, cell.col
        if not (0 <= r < len(grid) and 0 <= c < cols) or grid[r][c] is not None:
            # 좌표가 범위 밖이거나 이미 찬 자리 → 읽기 순서로 첫 빈 칸
            slot = next(
                ((rr, cc) for rr in range(len(grid)) for cc in range(cols) if grid[rr][cc] is None),
                None,
            )
            if slot is None:
                grid.append([None] * cols)
                slot = (len(grid) - 1, 0)
            r, c = slot
        grid[r][c] = cell.text
        for rr in range(r, min(r + max(cell.row_span, 1), len(grid))):
            for cc in range(c, min(c + max(cell.col_span, 1), cols)):
                if (rr, cc) != (r, c) and grid[rr][cc] is None:
                    grid[rr][cc] = ""  # 병합으로 덮인 칸
    return [[x if x is not None else "" for x in row] for row in grid]


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


def parse_section(root: etree._Element, header: HeaderInfo = EMPTY_HEADER) -> list[Block]:
    blocks: list[Block] = []
    for p in root.iterchildren(HP_P):
        blocks.extend(parse_paragraph(p, header))
    return blocks
