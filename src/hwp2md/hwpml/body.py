"""HWPML BODY tree -> blocks (paragraphs, headings, lists, tables, pictures, notes, objects).

HWPX(OWPML) 요소와 1:1 대응한다 (대문자 요소명·CamelCase 속성). 표 칸 배치는 hwpx.body 의
_place_cells 를 그대로 쓰고, 하이퍼링크 command 해석도 hwpx.body 의 것을 쓴다."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from typing import Literal

from lxml import etree

from ..blocks import (
    Block,
    Image,
    Inline,
    Link,
    ListInfo,
    Math,
    Note,
    NoteKind,
    NoteRef,
    Paragraph,
    Table,
    make_paragraph,
    make_table,
)
from ..equation import to_latex
from ..hwpx.body import CellSpec, _place_cells, hyperlink_command_target
from ..numbering import NumberingCounter, NumFormat, apply_template
from ..ole import OleOutcome
from ..skips import SkipCounter, SkipKind

MAX_HEADING_LEVEL = 6
MAX_LIST_DEPTH = 6
HEADING_OUTLINE = "Outline"  # PARASHAPE/@HeadingType 값. 그 외: None, Number, Bullet
HEADING_LIST: dict[str, Literal["bullet", "number"]] = {"Number": "number", "Bullet": "bullet"}
# CHAR 의 자식 인라인 요소 → 텍스트. 없는 태그는 "" (뒤따르는 tail 텍스트는 유지)
INLINE_TEXT: dict[str, str] = {
    "TAB": " ",
    "LINEBREAK": "\n",
    "NBSPACE": " ",
    "FWSPACE": " ",
    "HYPEN": "-",  # HWPML 요소명 철자가 HYPEN 이다
}
NOTE_KINDS: dict[str, NoteKind] = {"FOOTNOTE": "footnote", "ENDNOTE": "endnote"}
# 하위 트리를 통째로 건너뛰고 세는 요소
SKIPPED_ELEMENTS: dict[str, SkipKind] = {
    "HEADER": "header_footer",
    "FOOTER": "header_footer",
    "HIDDENCOMMENT": "hidden_comment",
    "TEXTART": "textart",
    "BUTTON": "form_control",
    "RADIOBUTTON": "form_control",
    "CHECKBUTTON": "form_control",
    "COMBOBOX": "form_control",
    "EDIT": "form_control",
    "LISTBOX": "form_control",
    "SCROLLBAR": "form_control",
}
# 글상자(DRAWTEXT)를 가질 수 있는 도형
SHAPES = frozenset({"LINE", "RECTANGLE", "ELLIPSE", "ARC", "POLYGON", "CURVE", "CONNECTLINE"})
FIELD_HYPERLINK = "hyperlink"  # FIELDBEGIN/@Type 소문자 비교
# PARAHEAD/@NumFormat → NumFormat. 그 밖 값은 DIGIT
NUM_FORMATS: dict[str, NumFormat] = {
    "digit": "DIGIT",
    "circleddigit": "CIRCLED_DIGIT",
    "romancapital": "ROMAN_CAPITAL",
    "romansmall": "ROMAN_SMALL",
    "latincapital": "LATIN_CAPITAL",
    "latinsmall": "LATIN_SMALL",
    "hangulsyllable": "HANGUL_SYLLABLE",
    "circledhangulsyllable": "CIRCLED_HANGUL_SYLLABLE",
    "hanguljamo": "HANGUL_JAMO",
    "hanjadigit": "HANJA_DIGIT",
    "ideograph": "HANJA_DIGIT",
}

ImageResolver = Callable[[str], Image | None]
OleResolver = Callable[[str], OleOutcome]


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


def to_num_format(value: str | None) -> NumFormat:
    """PARAHEAD/@NumFormat("HangulSyllable" 등) → NumFormat. 모르는 값은 "DIGIT"."""
    key = (value or "").replace("_", "").strip().lower()
    return NUM_FORMATS.get(key, "DIGIT")


@dataclass(frozen=True)
class ListShape:
    kind: Literal["bullet", "number"]
    ref: int  # PARASHAPE/@Heading — NUMBERING 또는 BULLET Id
    depth: int  # PARASHAPE/@Level (0부터)


@dataclass(frozen=True)
class NumberingDef:
    templates: dict[int, str]  # PARAHEAD/@Level(1부터) → 형식 문자열("^1.")
    formats: dict[int, NumFormat]
    starts: dict[int, int]


@dataclass(frozen=True)
class HeadInfo:
    para_levels: dict[int, int] = field(default_factory=dict)
    lists: dict[int, ListShape] = field(default_factory=dict)
    numberings: dict[int, NumberingDef] = field(default_factory=dict)


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


def parse_list_shapes(root: etree._Element) -> dict[int, ListShape]:
    """PARASHAPE Id → 목록 모양 (HeadingType="Number"|"Bullet")."""
    shapes: dict[int, ListShape] = {}
    for ps in root.iter("PARASHAPE"):
        pid = _int_attr(ps, "Id")
        kind = HEADING_LIST.get(ps.get("HeadingType") or "")
        if pid is None or kind is None:
            continue
        ref = _int_attr(ps, "Heading")
        depth = min(max(_int_attr(ps, "Level") or 0, 0), MAX_LIST_DEPTH)
        shapes[pid] = ListShape(kind, 0 if ref is None else ref, depth)
    return shapes


def parse_numberings(root: etree._Element) -> dict[int, NumberingDef]:
    """NUMBERINGLIST/NUMBERING Id → 수준별 형식·번호 모양·시작 번호."""
    out: dict[int, NumberingDef] = {}
    for num in root.iter("NUMBERING"):
        nid = _int_attr(num, "Id")
        if nid is None or nid in out:
            continue
        base_start = _int_attr(num, "Start")
        templates: dict[int, str] = {}
        formats: dict[int, NumFormat] = {}
        starts: dict[int, int] = {}
        for head in num.iterchildren("PARAHEAD"):
            level = _int_attr(head, "Level")
            if level is None or level in templates:
                continue
            templates[level] = head.text or ""
            formats[level] = to_num_format(head.get("NumFormat"))
            start = _int_attr(head, "Start")
            if start is None or start < 1:
                start = base_start if base_start is not None and base_start >= 1 else 1
            starts[level] = start
        out[nid] = NumberingDef(templates, formats, starts)
    return out


def parse_head(head: etree._Element) -> HeadInfo:
    return HeadInfo(parse_para_levels(head), parse_list_shapes(head), parse_numberings(head))


@dataclass
class DocContext:
    """문서 하나의 읽기 상태. 섹션을 넘어 각주 번호·건너뜀·목록 번호를 이어 간다."""

    head: HeadInfo = field(default_factory=HeadInfo)
    resolve_image: ImageResolver | None = None
    resolve_ole: OleResolver | None = None
    skips: SkipCounter = field(default_factory=SkipCounter)
    notes: dict[NoteKind, list[Note]] = field(
        default_factory=lambda: {"footnote": [], "endnote": []}
    )
    numbering: NumberingCounter = field(default_factory=NumberingCounter)
    in_note: bool = False

    def note_blocks(self) -> list[Block]:
        """문서 끝에 둘 Note 블록: 각주 번호순, 이어서 미주 번호순."""
        return [*self.notes["footnote"], *self.notes["endnote"]]

    def list_info(self, para_shape: int | None) -> ListInfo | None:
        shape = None if para_shape is None else self.head.lists.get(para_shape)
        if shape is None:
            return None
        if shape.kind == "bullet":
            return ListInfo("bullet", shape.depth, "")
        level = shape.depth + 1
        nd = self.head.numberings.get(shape.ref)
        template = nd.templates.get(level) if nd is not None else None
        if template is None:
            template = f"^{level}."
        start = nd.starts.get(level, 1) if nd is not None else 1
        numbers = self.numbering.next(shape.ref, shape.depth, start)
        formats: list[NumFormat] = [
            nd.formats.get(k, "DIGIT") if nd is not None else "DIGIT" for k in range(1, level + 1)
        ]
        return ListInfo("number", shape.depth, apply_template(template, numbers, formats))


def text_of_char(ch: etree._Element) -> str:
    parts = [ch.text or ""]
    for child in ch:
        if isinstance(child.tag, str):
            parts.append(INLINE_TEXT.get(child.tag, ""))
        parts.append(child.tail or "")
    return "".join(parts)


def _paralist_blocks(owner: etree._Element | None, ctx: DocContext) -> list[Block]:
    """owner/PARALIST 의 단락들 → 블록 (본문 단락과 같은 규칙)."""
    if owner is None:
        return []
    paralist = owner.find("PARALIST")
    if paralist is None:
        return []
    blocks: list[Block] = []
    for p in paralist.iterchildren("P"):
        blocks.extend(parse_paragraph(p, ctx))
    return blocks


def _caption_blocks(obj: etree._Element, ctx: DocContext) -> list[Block]:
    """표·그림 캡션: obj/CAPTION 또는 obj/SHAPEOBJECT/CAPTION 의 단락."""
    cap = obj.find("CAPTION")
    if cap is None:
        cap = obj.find("SHAPEOBJECT/CAPTION")
    return _paralist_blocks(cap, ctx)


def _drawtext_blocks(shape: etree._Element, ctx: DocContext) -> list[Block]:
    """도형 글상자: shape/DRAWTEXT 또는 shape/DRAWINGOBJECT/DRAWTEXT 의 단락."""
    dt = shape.find("DRAWTEXT")
    if dt is None:
        dt = shape.find("DRAWINGOBJECT/DRAWTEXT")
    return _paralist_blocks(dt, ctx)


def _picture_blocks(pic: etree._Element, ctx: DocContext) -> list[Block]:
    blocks: list[Block] = []
    img = pic.find("IMAGE")
    ref = img.get("BinItem") if img is not None else None
    if ctx.resolve_image is not None:
        # 해석기가 세지 않은(외부 연결이 아닌) 해석 불가 참조는 image_missing (HWP 5.0·HWPX 와 같음)
        before = ctx.skips.items()
        image = ctx.resolve_image(ref) if ref else None
        if image is not None:
            blocks.append(image)
        elif ctx.skips.items() == before:
            ctx.skips.add("image_missing")
    blocks.extend(_caption_blocks(pic, ctx))
    return blocks


def _ole_blocks(ole: etree._Element, ctx: DocContext) -> list[Block]:
    ref = (ole.get("BinItem") or "").strip()
    outcome = ctx.resolve_ole(ref) if ref and ctx.resolve_ole is not None else OleOutcome((), "ole")
    if outcome.skipped is not None:
        ctx.skips.add(outcome.skipped)
    return [*outcome.blocks, *_caption_blocks(ole, ctx)]


def object_blocks(el: etree._Element, ctx: DocContext) -> list[Block] | None:
    """그리기 개체(그림·도형·묶음·OLE) → 블록. 그리기 개체가 아니면 None."""
    tag = el.tag
    if tag == "PICTURE":
        return _picture_blocks(el, ctx)
    if tag in SHAPES:
        return _drawtext_blocks(el, ctx)
    if tag == "OLE":
        return _ole_blocks(el, ctx)
    if tag == "CONTAINER":
        blocks: list[Block] = []
        for child in el:
            if not isinstance(child.tag, str):
                continue
            if child.tag in SKIPPED_ELEMENTS:
                ctx.skips.add(SKIPPED_ELEMENTS[child.tag])
                continue
            sub = object_blocks(child, ctx)
            if sub is not None:
                blocks.extend(sub)
        return blocks
    return None


def parse_paragraph(p: etree._Element, ctx: DocContext) -> list[Block]:
    pid = _int_attr(p, "ParaShape")
    level = 0 if pid is None else ctx.head.para_levels.get(pid, 0)
    is_list = level == 0 and pid is not None and pid in ctx.head.lists
    blocks: list[Block] = []
    buf: list[Inline] = []
    # 열린 하이퍼링크: (주소, 지금까지 글자)
    link: list[tuple[str, list[str]]] = []
    list_done = False

    def close_link_segment() -> None:
        if not link:
            return
        url, parts = link[0]
        text = "".join(parts)
        parts.clear()
        if text:
            buf.append(Link(text, url))

    def add_text(text: str) -> None:
        if link:
            link[0][1].append(text)
        else:
            buf.append(text)

    def add_inline(item: Inline) -> None:
        close_link_segment()
        buf.append(item)

    # 도형·묶음·OLE 블록: 앵커 단락(다음 flush 의 단락) 뒤에 둔다 (HWP 5.0·HWPX 와 같음)
    pending: list[Block] = []

    def flush() -> None:
        nonlocal list_done
        close_link_segment()
        info: ListInfo | None = None
        if is_list and not list_done and make_paragraph(buf) is not None:
            info = ctx.list_info(pid)
            list_done = True
        para = make_paragraph(buf, level, info)
        buf.clear()
        if para is not None:
            blocks.append(para)
        blocks.extend(pending)
        pending.clear()

    def field_begin(el: etree._Element) -> None:
        if link or (el.get("Type") or "").lower() != FIELD_HYPERLINK:
            return  # 그 밖 필드(누름틀 등)는 사이 글자를 그대로 둔다
        command = el.get("Command")
        url = hyperlink_command_target(command) if command else None
        if url is not None:
            link.append((url, []))

    def field_end(el: etree._Element) -> None:
        if not link:
            return
        ftype = el.get("Type")
        if ftype is not None and ftype.lower() != FIELD_HYPERLINK:
            return  # 링크 안쪽 다른 필드의 끝
        close_link_segment()
        link.clear()

    def note(el: etree._Element, kind: NoteKind) -> None:
        if ctx.in_note:
            return  # 각주 안 각주는 만들지 않는다 (보고하지 않음)
        notes = ctx.notes[kind]
        number = len(notes) + 1
        add_inline(NoteRef(kind, number))
        notes.append(Note(kind, number, _note_paragraphs(el, ctx)))

    def equation(el: etree._Element) -> None:
        script_el = el.find("SCRIPT")
        script = "" if script_el is None else (script_el.text or "").strip()
        if script:
            add_inline(Math(script, to_latex(script)))

    for text in p.iterchildren("TEXT"):
        for child in text:
            if not isinstance(child.tag, str):
                continue
            tag = child.tag
            if tag == "CHAR":
                add_text(text_of_char(child))
            elif tag == "TABLE":
                flush()
                table = parse_table(child, ctx)
                if table is not None:
                    blocks.append(table)
                blocks.extend(_caption_blocks(child, ctx))
            elif tag == "FIELDBEGIN":
                field_begin(child)
            elif tag == "FIELDEND":
                field_end(child)
            elif tag in NOTE_KINDS:
                note(child, NOTE_KINDS[tag])
            elif tag == "EQUATION":
                equation(child)
            elif tag in SKIPPED_ELEMENTS:
                ctx.skips.add(SKIPPED_ELEMENTS[tag])
            elif tag == "PICTURE":
                sub = object_blocks(child, ctx)
                if sub:
                    flush()
                    blocks.extend(sub)
            else:
                sub = object_blocks(child, ctx)
                if sub:
                    pending.extend(sub)
            # 그 외(SECDEF, COLDEF, AUTONUM, BOOKMARK, ...)는 무시
    flush()
    return blocks


def _note_paragraphs(el: etree._Element, ctx: DocContext) -> tuple[Paragraph, ...]:
    """각주·미주 PARALIST 단락 → Paragraph. 표는 글자를 이어 붙이고 그림은 인라인으로."""
    out: list[Paragraph] = []
    saved = ctx.in_note
    ctx.in_note = True
    try:
        for b in _paralist_blocks(el, ctx):
            para: Paragraph | None
            if isinstance(b, Paragraph):
                para = make_paragraph(b.inlines or (b.text,))
            elif isinstance(b, Table):
                para = make_paragraph([_flat_table_text(b)])
            elif isinstance(b, Image):
                para = make_paragraph([b])
            else:
                para = None
            if para is not None:
                out.append(para)
    finally:
        ctx.in_note = saved
    return tuple(out)


def _flat_table_text(table: Table) -> str:
    return " ".join(c for row in table.rows for c in row if c)


def _table_images(table: Table) -> list[Image]:
    return [item for row in table.cells for cell in row for item in cell if isinstance(item, Image)]


def parse_table(tbl: etree._Element, ctx: DocContext) -> Table | None:
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
    contents: dict[str, list[Inline]] = {}
    for r_idx, row in enumerate(rows_el):
        for cell in row.iterchildren("CELL"):
            r = _int_attr(cell, "RowAddr")
            c = _int_attr(cell, "ColAddr")
            row_span = _int_attr(cell, "RowSpan")
            col_span = _int_attr(cell, "ColSpan")
            key = f"\x00{len(contents)}"  # 배치용 표식. _place_cells 는 글자만 옮긴다
            contents[key] = _cell_inlines(cell, ctx)
            cells.append(
                CellSpec(
                    row=r_idx if r is None else r,
                    col=-1 if c is None else c,
                    row_span=1 if row_span is None else row_span,
                    col_span=1 if col_span is None else col_span,
                    text=key,
                )
            )
    grid = _place_cells(rows, cols, cells)
    return make_table([[contents.get(key, []) for key in row] for row in grid])


def _list_head(para: Paragraph) -> list[Inline]:
    """칸 안 목록 단락의 머리 글자 (§4-D): 글머리표 "- ", 그 밖 "<머리> ". 목록이 아니면 []."""
    info = para.list_info
    if info is None:
        return []
    return ["- " if info.kind == "bullet" else f"{info.label} "]


def _cell_inlines(cell: etree._Element, ctx: DocContext) -> list[Inline]:
    """칸 단락 → 인라인. 단락 경계는 "\\n".
    칸 안 표는 글자를 공백으로 잇고, 그 안 그림은 칸 끝에 붙인다."""
    parts: list[list[Inline]] = []
    tail: list[Image] = []
    for b in _paralist_blocks(cell, ctx):
        if isinstance(b, Paragraph):
            parts.append([*_list_head(b), *(b.inlines or (b.text,))])
        elif isinstance(b, Table):
            flat = _flat_table_text(b)
            if flat:
                parts.append([flat])
            tail.extend(_table_images(b))
        elif isinstance(b, Image):
            parts.append([b])
    parts.extend([img] for img in tail)
    out: list[Inline] = []
    for i, part in enumerate(parts):
        if i:
            out.append("\n")
        out.extend(part)
    return out


def parse_body(sections: Iterable[etree._Element], ctx: DocContext) -> list[Block]:
    """모든 섹션의 블록 뒤에 각주·미주 Note 블록을 둔다."""
    blocks: list[Block] = []
    for section in sections:
        for p in section.iterchildren("P"):
            blocks.extend(parse_paragraph(p, ctx))
    blocks.extend(ctx.note_blocks())
    return blocks
