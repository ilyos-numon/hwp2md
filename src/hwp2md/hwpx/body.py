"""OWPML section tree -> blocks (paragraphs, tables, notes)."""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from lxml import etree

from ..blocks import (
    Block,
    Image,
    Inline,
    Link,
    Math,
    Note,
    NoteKind,
    NoteRef,
    Paragraph,
    Table,
    make_paragraph,
)
from ..equation import to_latex
from ..skips import SkipCounter, SkipKind
from .header import EMPTY_HEADER, HeaderInfo

if TYPE_CHECKING:
    from .bindata import BinItemStore

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
NS_HC = "http://www.hancom.co.kr/hwpml/2011/core"
HP_PIC = f"{{{NS_HP}}}pic"
HP_CONTAINER = f"{{{NS_HP}}}container"
HC_IMG = f"{{{NS_HC}}}img"
HP_CTRL = f"{{{NS_HP}}}ctrl"
HP_FIELD_BEGIN = f"{{{NS_HP}}}fieldBegin"
HP_FIELD_END = f"{{{NS_HP}}}fieldEnd"
HP_PARAMETERS = f"{{{NS_HP}}}parameters"
HP_STRING_PARAM = f"{{{NS_HP}}}stringParam"
HP_FOOTNOTE = f"{{{NS_HP}}}footNote"
HP_ENDNOTE = f"{{{NS_HP}}}endNote"
HP_EQUATION = f"{{{NS_HP}}}equation"
HP_SCRIPT = f"{{{NS_HP}}}script"
HP_MEMOGROUP = f"{{{NS_HP}}}memogroup"
HP_MEMO = f"{{{NS_HP}}}memo"
NOTE_KINDS: dict[str, NoteKind] = {HP_FOOTNOTE: "footnote", HP_ENDNOTE: "endnote"}
# 하위 트리를 통째로 건너뛰고 세는 요소 (run 직계 또는 hp:ctrl 안)
SKIPPED_ELEMENTS: dict[str, SkipKind] = {
    f"{{{NS_HP}}}header": "header_footer",
    f"{{{NS_HP}}}footer": "header_footer",
    f"{{{NS_HP}}}hiddenComment": "hidden_comment",
}
# hp:ctrl 안에서 다루는 요소 (그 밖 colPr·autoNum·pageNum 등은 무시)
CTRL_CHILDREN = frozenset(
    {HP_FIELD_BEGIN, HP_FIELD_END, HP_FOOTNOTE, HP_ENDNOTE, HP_EQUATION, *SKIPPED_ELEMENTS}
)
_COMMAND_TAIL = re.compile(r";(\d+);\d+;\d+;?$")
_COMMAND_ESCAPE = re.compile(r"\\(.)")
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


@dataclass
class DocContext:
    """문서 하나의 읽기 상태. 섹션을 넘어 각주 번호·건너뜀을 이어 간다."""

    skips: SkipCounter = field(default_factory=SkipCounter)
    notes: dict[NoteKind, list[Note]] = field(
        default_factory=lambda: {"footnote": [], "endnote": []}
    )
    in_note: bool = False

    def note_blocks(self) -> list[Block]:
        """문서 끝에 둘 Note 블록: 각주 번호순, 이어서 미주 번호순."""
        return [*self.notes["footnote"], *self.notes["endnote"]]


def hyperlink_command_target(command: str) -> str | None:
    """하이퍼링크 command → 주소. 꼬리 `;종류;n;n;` 제거 → `|` 앞부분 → `\\(.)` 언이스케이프.
    종류 0(문서 안 이동)이거나 결과가 비면 None."""
    m = _COMMAND_TAIL.search(command)
    if m is not None:
        if m.group(1) == "0":
            return None
        command = command[: m.start()]
    target = _COMMAND_ESCAPE.sub(r"\1", command.split("|", 1)[0]).strip()
    return target or None


def hyperlink_url(field_begin: etree._Element) -> str | None:
    """hp:stringParam[@name="Path"] 우선, 없으면 Command 해석. 링크가 아니면 None."""
    params: dict[str, str] = {}
    for sp in field_begin.iter(HP_STRING_PARAM):
        name = sp.get("name")
        if name and name not in params:
            params[name] = sp.text or ""
    path = params.get("Path", "").strip()
    if path:
        return path
    command = params.get("Command")
    return hyperlink_command_target(command) if command else None


def text_of_t(t: etree._Element) -> str:
    parts = [t.text or ""]
    for child in t:
        if isinstance(child.tag, str):
            parts.append(INLINE_TEXT.get(child.tag, ""))
        parts.append(child.tail or "")
    return "".join(parts)


def parse_paragraph(
    p: etree._Element,
    header: HeaderInfo = EMPTY_HEADER,
    bin_items: BinItemStore | None = None,
    ctx: DocContext | None = None,
) -> list[Block]:
    doc = DocContext() if ctx is None else ctx
    level = header.heading_level(_int_attr(p, "paraPrIDRef"))
    blocks: list[Block] = []
    buf: list[Inline] = []
    # 열린 하이퍼링크: (beginIDRef 로 맞출 id, 주소, 지금까지 글자)
    link: list[tuple[str | None, str, list[str]]] = []

    def close_link_segment() -> None:
        if not link:
            return
        _, url, parts = link[0]
        text = "".join(parts)
        parts.clear()
        if text:
            buf.append(Link(text, url))

    def add_text(text: str) -> None:
        if link:
            link[0][2].append(text)
        else:
            buf.append(text)

    def add_inline(item: Inline) -> None:
        close_link_segment()
        buf.append(item)

    def flush() -> None:
        close_link_segment()
        para = make_paragraph(buf, level)
        buf.clear()
        if para is not None:
            blocks.append(para)

    def append_image(pic: etree._Element) -> None:
        if bin_items is None:
            return
        img = pic.find(HC_IMG)
        if img is None:
            return
        ref = img.get("binaryItemIDRef")
        if not ref:
            return
        image = bin_items.resolve(ref)
        if image is None:
            return
        flush()
        blocks.append(image)

    def field_begin(el: etree._Element) -> None:
        if link or el.get("type") != "HYPERLINK":
            return  # 그 밖 필드(누름틀 등)는 사이 글자를 그대로 둔다
        url = hyperlink_url(el)
        if url is not None:
            link.append((el.get("id"), url, []))

    def field_end(el: etree._Element) -> None:
        if not link:
            return
        ref = el.get("beginIDRef")
        if ref is not None and link[0][0] is not None and ref != link[0][0]:
            return  # 링크 안쪽 다른 필드의 끝
        close_link_segment()
        link.clear()

    def note(el: etree._Element, kind: NoteKind) -> None:
        if doc.in_note:
            return  # 각주 안 각주는 만들지 않는다 (보고하지 않음)
        notes = doc.notes[kind]
        number = len(notes) + 1
        add_inline(NoteRef(kind, number))
        notes.append(Note(kind, number, _note_paragraphs(el, header, bin_items, doc)))

    def equation(el: etree._Element) -> None:
        script_el = el.find(HP_SCRIPT)
        script = "" if script_el is None else (script_el.text or "").strip()
        if script:
            add_inline(Math(script, to_latex(script)))

    def element(child: etree._Element) -> None:
        tag = child.tag
        if tag == HP_T:
            add_text(text_of_t(child))
        elif tag == HP_TBL:
            flush()
            table = parse_table(child, doc)
            if table is not None:
                blocks.append(table)
        elif tag == HP_PIC:
            append_image(child)
        elif tag == HP_CONTAINER:
            for pic in child.iter(HP_PIC):
                append_image(pic)
        elif tag == HP_CTRL:
            for sub in child:
                if sub.tag in CTRL_CHILDREN:
                    element(sub)
        elif tag == HP_FIELD_BEGIN:
            field_begin(child)
        elif tag == HP_FIELD_END:
            field_end(child)
        elif tag in NOTE_KINDS:
            note(child, NOTE_KINDS[tag])
        elif tag == HP_EQUATION:
            equation(child)
        elif tag in SKIPPED_ELEMENTS:
            doc.skips.add(SKIPPED_ELEMENTS[tag])
        # 그 외(secPr, colPr, autoNum, rect, ...)는 무시

    for run in p.iterchildren(HP_RUN):
        for child in run:
            if isinstance(child.tag, str):
                element(child)
    flush()
    return blocks


def _note_paragraphs(
    el: etree._Element,
    header: HeaderInfo,
    bin_items: BinItemStore | None,
    doc: DocContext,
) -> tuple[Paragraph, ...]:
    """각주·미주 subList 단락 → Paragraph. 표는 글자를 이어 붙이고 그림은 인라인으로."""
    sub = el.find(HP_SUBLIST)
    if sub is None:
        return ()
    out: list[Paragraph] = []
    saved = doc.in_note
    doc.in_note = True
    try:
        for p in sub.iterchildren(HP_P):
            for b in parse_paragraph(p, header, bin_items, doc):
                para: Paragraph | None
                if isinstance(b, Paragraph):
                    para = make_paragraph(b.inlines or (b.text,))
                elif isinstance(b, Table):
                    para = make_paragraph([" ".join(c for row in b.rows for c in row if c)])
                elif isinstance(b, Image):
                    para = make_paragraph([b])
                else:
                    para = None
                if para is not None:
                    out.append(para)
    finally:
        doc.in_note = saved
    return tuple(out)


def parse_table(tbl: etree._Element, ctx: DocContext | None = None) -> Table | None:
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
                    text=_cell_text(tc, ctx),
                )
            )
    return Table(rows=_place_cells(rows, cols, cells))


def _cell_text(tc: etree._Element, ctx: DocContext | None = None) -> str:
    sub = tc.find(HP_SUBLIST)
    if sub is None:
        return ""
    parts: list[str] = []
    for p in sub.iterchildren(HP_P):
        for b in parse_paragraph(p, ctx=ctx):
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


def parse_section(
    root: etree._Element,
    header: HeaderInfo = EMPTY_HEADER,
    bin_items: BinItemStore | None = None,
    ctx: DocContext | None = None,
) -> list[Block]:
    """ctx 가 없으면 이 섹션만의 상태를 만들고 Note 블록을 끝에 붙인다.
    ctx 를 받으면 Note 는 ctx 에 쌓이고 호출자(리더)가 문서 끝에 둔다."""
    doc = DocContext() if ctx is None else ctx
    blocks: list[Block] = []
    for p in root.iterchildren(HP_P):
        blocks.extend(parse_paragraph(p, header, bin_items, doc))
    for group in root.iter(HP_MEMOGROUP):
        memos = sum(1 for _ in group.iterchildren(HP_MEMO))
        if memos:
            doc.skips.add("memo", memos)
    if ctx is None:
        blocks.extend(doc.note_blocks())
    return blocks
