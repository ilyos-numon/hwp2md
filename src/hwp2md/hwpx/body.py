"""OWPML section tree -> blocks (paragraphs, tables, notes)."""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, TypeVar

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
    iter_images,
    make_paragraph,
    make_table,
    plain_text,
)
from ..equation import to_latex
from ..ole import chart_xml_to_blocks, ole_to_outcome, unwrap_hwpx_ole
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
HP_CAPTION = f"{{{NS_HP}}}caption"
HP_DRAW_TEXT = f"{{{NS_HP}}}drawText"
HP_CHART = f"{{{NS_HP}}}chart"
HP_OLE = f"{{{NS_HP}}}ole"
HP_TEXTART = f"{{{NS_HP}}}textart"
# 글상자를 가질 수 있는 도형 (hp:drawText/hp:subList/hp:p)
SHAPE_ELEMENTS = frozenset(
    f"{{{NS_HP}}}{name}" for name in ("rect", "ellipse", "arc", "polygon", "curve", "connectLine")
)
FORM_ELEMENTS = frozenset(
    f"{{{NS_HP}}}{name}"
    for name in ("btn", "checkBtn", "radioBtn", "comboBox", "listBox", "edit", "scrollBar")
)
# 단락 run 직계에서 앵커 단락 뒤로 미루는 개체 (hp:pic·hp:tbl 은 등장 위치에서 나눈다)
DRAWING_ELEMENTS = frozenset(
    {HP_CONTAINER, HP_CHART, HP_OLE, HP_TEXTART, *SHAPE_ELEMENTS, *FORM_ELEMENTS}
)
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

    # 도형·묶음·차트·OLE 블록: 앵커 단락(다음 flush 의 단락) 뒤에 둔다
    pending: list[Block] = []

    def flush() -> None:
        close_link_segment()
        para = make_paragraph(buf, level)
        buf.clear()
        if para is not None:
            blocks.append(para)
        blocks.extend(pending)
        pending.clear()

    def sub_blocks(owner: etree._Element | None) -> list[Block]:
        """owner/hp:subList/hp:p 단락들 → 블록 (캡션·글상자)."""
        sub = None if owner is None else owner.find(HP_SUBLIST)
        if sub is None:
            return []
        out: list[Block] = []
        for sub_p in sub.iterchildren(HP_P):
            out.extend(parse_paragraph(sub_p, header, bin_items, doc))
        return out

    def picture(pic: etree._Element) -> list[Block]:
        """그림 + 캡션 단락. 해석 불가 그림은 image_missing 으로 센다."""
        out: list[Block] = []
        if bin_items is not None:
            img = pic.find(HC_IMG)
            ref = None if img is None else img.get("binaryItemIDRef")
            image = bin_items.resolve(ref) if ref else None
            if image is None:
                doc.skips.add("image_missing")
            else:
                out.append(image)
        out.extend(sub_blocks(pic.find(HP_CAPTION)))
        return out

    def chart(el: etree._Element) -> list[Block]:
        if bin_items is None:
            return []
        ref = el.get("chartIDRef")
        data = bin_items.chart(ref) if ref else None
        out = chart_xml_to_blocks(data) if data is not None else []
        if not out:
            doc.skips.add("chart_legacy")
        return out

    def ole(el: etree._Element) -> list[Block]:
        if bin_items is None:
            return []
        ref = el.get("binaryItemIDRef")
        data = bin_items.raw(ref) if ref else None
        if data is None:
            doc.skips.add("ole")
            return []
        outcome = ole_to_outcome(unwrap_hwpx_ole(data), f"ole:{ref}", bin_items.make_image)
        if outcome.skipped is not None:
            doc.skips.add(outcome.skipped)
        return list(outcome.blocks)

    def drawing(el: etree._Element) -> list[Block]:
        """그리기 개체 하나 → 블록 (묶음은 자식 저장 순서대로 재귀)."""
        tag = el.tag
        if tag == HP_PIC:
            return picture(el)
        if tag in SHAPE_ELEMENTS:
            return sub_blocks(el.find(HP_DRAW_TEXT))
        if tag == HP_CONTAINER:
            out: list[Block] = []
            for sub in el:
                if isinstance(sub.tag, str):
                    out.extend(drawing(sub))
            return out
        if tag == HP_CHART:
            return chart(el)
        if tag == HP_OLE:
            return ole(el)
        if tag == HP_TEXTART:
            doc.skips.add("textart")
        elif tag in FORM_ELEMENTS:
            doc.skips.add("form_control")
        return []

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
            table = parse_table(child, doc, header, bin_items)
            if table is not None:
                blocks.append(table)
            blocks.extend(sub_blocks(child.find(HP_CAPTION)))
        elif tag == HP_PIC:
            items = picture(child)
            if items:
                flush()
                blocks.extend(items)
        elif tag in DRAWING_ELEMENTS:
            pending.extend(drawing(child))
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
        # 그 외(secPr, colPr, autoNum, line, ...)는 무시

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


def parse_table(
    tbl: etree._Element,
    ctx: DocContext | None = None,
    header: HeaderInfo = EMPTY_HEADER,
    bin_items: BinItemStore | None = None,
) -> Table | None:
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
    contents: list[tuple[Inline, ...]] = []
    for r_idx, tr in enumerate(trs):
        for tc in tr.iterchildren(HP_TC):
            addr = tc.find(HP_CELL_ADDR)
            span = tc.find(HP_CELL_SPAN)
            row = _int_attr(addr, "rowAddr")
            col = _int_attr(addr, "colAddr")
            row_span = _int_attr(span, "rowSpan")
            col_span = _int_attr(span, "colSpan")
            inlines = _cell_inlines(tc, ctx, header, bin_items)
            cells.append(
                CellSpec(
                    row=r_idx if row is None else row,
                    col=-1 if col is None else col,
                    row_span=1 if row_span is None else row_span,
                    col_span=1 if col_span is None else col_span,
                    text=plain_text(inlines).strip(),
                )
            )
            contents.append(inlines)
    return make_table(_place_grid(rows, cols, cells, contents, ()))


def _cell_inlines(
    tc: etree._Element,
    ctx: DocContext | None = None,
    header: HeaderInfo = EMPTY_HEADER,
    bin_items: BinItemStore | None = None,
) -> tuple[Inline, ...]:
    """칸 subList 의 블록들 → 칸 인라인. 블록 사이에 "\n". 칸 안 표는 글자를 공백으로 이어 붙이고
    그 안의 그림은 칸 인라인 끝에 붙인다."""
    sub = tc.find(HP_SUBLIST)
    if sub is None:
        return ()
    doc = DocContext() if ctx is None else ctx
    parts: list[tuple[Inline, ...]] = []
    tail: list[Inline] = []
    for p in sub.iterchildren(HP_P):
        for b in parse_paragraph(p, header, bin_items, doc):
            if isinstance(b, Paragraph):
                parts.append(b.inlines or (b.text,))
            elif isinstance(b, Table):
                flat = " ".join(c for row in b.rows for c in row if c)
                if flat:
                    parts.append((flat,))
                tail.extend(iter_images([b]))
            elif isinstance(b, Image):
                parts.append((b,))
    out: list[Inline] = []
    for k, part in enumerate(parts):
        if k:
            out.append("\n")
        out.extend(part)
    out.extend(tail)
    return tuple(out)


_T = TypeVar("_T")


def _place_grid(
    rows: int, cols: int, cells: Sequence[CellSpec], values: Sequence[_T], fill: _T
) -> list[list[_T]]:
    """cells[i] 자리에 values[i] 를 둔다. 병합으로 덮인 칸·빈 칸은 fill."""
    grid: list[list[_T | None]] = [[None] * cols for _ in range(rows)]
    for cell, value in zip(cells, values, strict=True):
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
        grid[r][c] = value
        for rr in range(r, min(r + max(cell.row_span, 1), len(grid))):
            for cc in range(c, min(c + max(cell.col_span, 1), cols)):
                if (rr, cc) != (r, c) and grid[rr][cc] is None:
                    grid[rr][cc] = fill  # 병합으로 덮인 칸
    return [[x if x is not None else fill for x in row] for row in grid]


def _place_cells(rows: int, cols: int, cells: Sequence[CellSpec]) -> list[list[str]]:
    return _place_grid(rows, cols, cells, [cell.text for cell in cells], "")


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
