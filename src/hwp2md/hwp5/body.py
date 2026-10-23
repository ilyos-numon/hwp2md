"""BodyText record sequence -> blocks (paragraphs, tables, inline elements)."""

from __future__ import annotations

import re
import struct
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, replace
from typing import Protocol, runtime_checkable

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
    iter_images,
    make_paragraph,
    make_table,
)
from ..equation import to_latex
from ..errors import Hwp2mdError
from ..numbering import NumberingCounter, apply_template
from ..ole import ole_to_outcome, unwrap_hwpx_ole
from ..skips import SkipCounter
from .docinfo import EMPTY_DOCINFO, HEADING_BULLET, HEADING_NUMBER, DocInfo
from .records import (
    CTRL_ID_ENDNOTE,
    CTRL_ID_EQUATION,
    CTRL_ID_FOOTER,
    CTRL_ID_FOOTNOTE,
    CTRL_ID_GSO,
    CTRL_ID_HEADER,
    CTRL_ID_HIDDEN_COMMENT,
    CTRL_ID_HYPERLINK,
    CTRL_ID_TABLE,
    FIELD_END,
    FIELD_START,
    HWPTAG_CTRL_HEADER,
    HWPTAG_EQEDIT,
    HWPTAG_LIST_HEADER,
    HWPTAG_MEMO_LIST,
    HWPTAG_PARA_HEADER,
    HWPTAG_PARA_TEXT,
    HWPTAG_SHAPE_COMPONENT,
    HWPTAG_SHAPE_COMPONENT_OLE,
    HWPTAG_SHAPE_COMPONENT_PICTURE,
    HWPTAG_SHAPE_COMPONENT_TEXTART,
    HWPTAG_TABLE,
    CtrlMark,
    Record,
    decode_para_runs,
)


class ImageResolver(Protocol):
    def resolve(self, bindata_id: int) -> Image | None: ...


@runtime_checkable
class ObjectResolver(Protocol):
    """ImageResolver 가 OLE 개체도 다룰 수 있으면 이 메서드도 갖는다."""

    def resolve(self, bindata_id: int) -> Image | None: ...

    def ole_data(self, bindata_id: int) -> bytes | None: ...

    def make_image(self, key: str, data: bytes) -> Image: ...


@dataclass(frozen=True)
class TableHeader:
    row_count: int
    col_count: int


@dataclass(frozen=True)
class CellHeader:
    col: int
    row: int
    col_span: int
    row_span: int


def parse_table_header(payload: bytes) -> TableHeader:
    """len(payload) < 8 → Hwp2mdError("truncated TABLE record")."""
    if len(payload) < 8:
        raise Hwp2mdError("truncated TABLE record")
    row_count, col_count = struct.unpack_from("<HH", payload, 4)
    return TableHeader(row_count=row_count, col_count=col_count)


def parse_cell_header(payload: bytes) -> CellHeader:
    """len(payload) < 16 → Hwp2mdError("truncated LIST_HEADER record")."""
    if len(payload) < 16:
        raise Hwp2mdError("truncated LIST_HEADER record")
    col, row, col_span, row_span = struct.unpack_from("<HHHH", payload, 8)
    return CellHeader(col=col, row=row, col_span=col_span, row_span=row_span)


OLE_BINDATA_ID_OFFSET = 12  # 속성 UINT32, extent x·y INT32 다음 UINT16 (실제 샘플로 확인)


def parse_ole_bindata_id(payload: bytes) -> int | None:
    """SHAPE_COMPONENT_OLE 의 BinData ID. 잘렸으면 None."""
    if len(payload) < OLE_BINDATA_ID_OFFSET + 2:
        return None
    (bindata_id,) = struct.unpack_from("<H", payload, OLE_BINDATA_ID_OFFSET)
    return int(bindata_id)


def parse_picture_bindata_id(payload: bytes) -> int:
    """len(payload) < 73 → Hwp2mdError("truncated SHAPE_COMPONENT_PICTURE record")."""
    if len(payload) < 73:
        raise Hwp2mdError("truncated SHAPE_COMPONENT_PICTURE record")
    (bindata_id,) = struct.unpack_from("<H", payload, 71)
    return int(bindata_id)


_LINK_TAIL = re.compile(r";(\d+);\d+;\d+;?$")
_LINK_ESCAPE = re.compile(r"\\(.)", re.DOTALL)


def parse_field_command(payload: bytes) -> str:
    """필드 CTRL_HEADER: ctrl_id(4) UINT32 속성 BYTE 기타 WORD len WCHAR[len] command.
    잘렸으면 있는 만큼만 읽는다."""
    if len(payload) < 11:
        return ""
    (n,) = struct.unpack_from("<H", payload, 9)
    raw = payload[11 : 11 + 2 * n]
    return raw[: len(raw) // 2 * 2].decode("utf-16-le", errors="replace")


def hyperlink_url(command: str) -> str | None:
    """꼬리 `;\\d+;\\d+;\\d+;?$` 제거 → `|` 앞부분 → `\\(.)` 언이스케이프.
    종류(꼬리 첫 수)가 0(문서 안 이동)이거나 결과가 비거나 `?` 로 시작하면 None."""
    target = command
    m = _LINK_TAIL.search(command)
    if m is not None:
        if int(m.group(1)) == 0:
            return None
        target = command[: m.start()]
    target = target.split("|", 1)[0]
    url = _LINK_ESCAPE.sub(lambda x: x.group(1), target)
    if not url or url.startswith("?"):
        return None
    return url


def parse_eqedit_script(payload: bytes) -> str:
    """EQEDIT: UINT32 속성, WORD len, WCHAR[len] 스크립트. 잘렸으면 있는 만큼만 읽는다."""
    if len(payload) < 6:
        return ""
    (n,) = struct.unpack_from("<H", payload, 4)
    raw = payload[6 : 6 + 2 * n]
    return raw[: len(raw) // 2 * 2].decode("utf-16-le", errors="replace")


class ReadContext:
    """문서 하나를 읽는 동안 섹션을 넘어 유지하는 상태(각주·미주 번호와 내용, 건너뜀,
    목록 번호)."""

    def __init__(self, skips: SkipCounter | None = None) -> None:
        self.skips = skips if skips is not None else SkipCounter()
        self.notes: dict[NoteKind, list[Note]] = {"footnote": [], "endnote": []}
        self._numbers: dict[NoteKind, int] = {"footnote": 0, "endnote": 0}
        self.in_note = False
        self.numbers = NumberingCounter()

    def next_note_number(self, kind: NoteKind) -> int:
        self._numbers[kind] += 1
        return self._numbers[kind]

    def note_blocks(self) -> list[Block]:
        """각주 번호순, 이어서 미주 번호순."""
        return [*self.notes["footnote"], *self.notes["endnote"]]  # 번호를 매긴 순서로 쌓인다


def parse_blocks(
    records: Iterable[Record],
    docinfo: DocInfo = EMPTY_DOCINFO,
    bin_data: ImageResolver | None = None,
    ctx: ReadContext | None = None,
) -> list[Block]:
    """§4.3 알고리즘. 섹션 하나의 레코드 시퀀스 → 블록 목록.
    ctx 가 없으면 이 섹션만의 컨텍스트를 만들고 Note 블록을 끝에 붙인다.
    ctx 가 있으면 Note 블록은 호출자가 ctx.note_blocks() 로 문서 끝에 붙인다."""
    own = ctx is None
    if ctx is None:
        ctx = ReadContext()
    recs = list(records)
    blocks: list[Block] = []
    i = 0
    while i < len(recs):
        r = recs[i]
        if r.tag_id == HWPTAG_PARA_HEADER and r.level == 0:
            inlines, heading, list_info, trailing, i = _parse_paragraph(
                recs, i, 0, docinfo, bin_data, ctx
            )
            para = make_paragraph(inlines, heading, list_info)
            if para is not None:
                blocks.append(para)
            blocks.extend(trailing)
        else:
            if r.tag_id == HWPTAG_MEMO_LIST:
                ctx.skips.add("memo")
            i += 1
    if own:
        blocks.extend(ctx.note_blocks())
    return blocks


def _heading_level(para_header_payload: bytes, docinfo: DocInfo) -> int:
    """len(payload) < 10 → 0. para_shape_id = UINT16 @8."""
    if len(para_header_payload) < 10:
        return 0
    (para_shape_id,) = struct.unpack_from("<H", para_header_payload, 8)
    return docinfo.heading_level(para_shape_id)


MAX_LIST_DEPTH = 6


def _list_info(para_header_payload: bytes, docinfo: DocInfo, ctx: ReadContext) -> ListInfo | None:
    """번호·글머리표 문단 모양이면 ListInfo. 번호는 문서 단위 카운터를 1 올린다.
    번호 정의가 없으면 형식 "^n." 숫자로 근사한다."""
    if len(para_header_payload) < 10:
        return None
    (para_shape_id,) = struct.unpack_from("<H", para_header_payload, 8)
    shape = docinfo.para_shape(para_shape_id)
    if shape is None or shape.heading_type not in (HEADING_NUMBER, HEADING_BULLET):
        return None
    depth = min(shape.heading_level, MAX_LIST_DEPTH)
    if shape.heading_type == HEADING_BULLET:
        return ListInfo("bullet", depth, "")
    numbering = docinfo.numbering(shape.head_id)
    if numbering is None:
        numbers = ctx.numbers.next(shape.head_id, depth)
        return ListInfo("number", depth, apply_template("^n.", numbers, ["DIGIT"] * len(numbers)))
    numbers = ctx.numbers.next(shape.head_id, depth, numbering.level_start(depth))
    template = numbering.levels[depth].template if depth < len(numbering.levels) else "^n."
    formats = [lv.num_format for lv in numbering.levels]
    return ListInfo("number", depth, apply_template(template, numbers, formats))


def _subtree_end(recs: Sequence[Record], i: int) -> int:
    """recs[i] 의 하위 레코드(level 이 더 큰 연속 레코드) 바로 다음 인덱스."""
    ctrl_level = recs[i].level
    j = i + 1
    while j < len(recs) and recs[j].level > ctrl_level:
        j += 1
    return j


class _InlineBuilder:
    """단락 인라인을 위치대로 모은다. 하이퍼링크 필드 안 글자는 Link 로 묶는다."""

    def __init__(self) -> None:
        self.items: list[Inline] = []
        self._depth = 0  # 열린 필드 수
        self._link_depth = 0  # 열린 링크 필드의 깊이 (0 = 없음)
        self._link_url: str | None = None
        self._link_text: list[str] = []

    def text(self, s: str) -> None:
        if self._link_depth:
            self._link_text.append(s)
        else:
            self.items.append(s)

    def inline(self, item: Inline) -> None:
        if self._link_depth:
            self._flush_link()
        self.items.append(item)

    def field_start(self, url: str | None, *, link: bool) -> None:
        self._depth += 1
        if link and not self._link_depth:
            self._link_depth = self._depth
            self._link_url = url
            self._link_text = []

    def field_end(self) -> None:
        if not self._depth:
            return
        if self._link_depth == self._depth:
            self._flush_link()
            self._link_depth = 0
            self._link_url = None
        self._depth -= 1

    def _flush_link(self) -> None:
        text = "".join(self._link_text)
        self._link_text = []
        if not text:
            return
        if self._link_url is None:
            self.items.append(text)
        else:
            self.items.append(Link(text, self._link_url))

    def finish(self) -> list[Inline]:
        if self._link_depth:
            self._flush_link()
            self._link_depth = 0
        return self.items


def _parse_paragraph(
    recs: Sequence[Record],
    i: int,
    level: int,
    docinfo: DocInfo,
    bin_data: ImageResolver | None,
    ctx: ReadContext,
) -> tuple[list[Inline], int, ListInfo | None, list[Block], int]:
    """(인라인, 제목 수준, 목록 정보, 단락 뒤에 둘 블록, 다음 인덱스).
    확장 제어문자와 같은 단락의 CTRL_HEADER 를 등장 순서로 1:1 대응한다. 개수가 다르면
    대응을 포기하고 글자 뒤에 컨트롤 결과를 차례로 둔다."""
    heading = _heading_level(recs[i].payload, docinfo)
    list_info = _list_info(recs[i].payload, docinfo, ctx)
    i += 1
    payload: bytes | None = None
    ctrls: list[tuple[int, int]] = []  # level+1 CTRL_HEADER 하위 트리 [start, stop)
    while i < len(recs) and recs[i].level > level:
        r = recs[i]
        if r.tag_id == HWPTAG_PARA_TEXT and r.level == level + 1:
            payload = r.payload
            i += 1
        elif r.tag_id == HWPTAG_CTRL_HEADER and r.level == level + 1:
            stop = _subtree_end(recs, i)
            ctrls.append((i, stop))
            i = stop
        else:
            i += 1
    end = i
    runs = decode_para_runs(payload) if payload is not None else []
    marks = sum(1 for x in runs if isinstance(x, CtrlMark) and x.code != FIELD_END)
    mapped = marks == len(ctrls)
    seq: list[str | CtrlMark] = runs
    if not mapped:
        seq = [x for x in runs if isinstance(x, str)] + [CtrlMark(0)] * len(ctrls)
    builder = _InlineBuilder()
    trailing: list[Block] = []
    k = 0
    for item in seq:
        if isinstance(item, str):
            builder.text(item)
        elif item.code == FIELD_END:
            builder.field_end()
        else:
            start, stop = ctrls[k]
            k += 1
            _handle_control(
                recs,
                start,
                stop,
                item.code if mapped else 0,
                docinfo,
                bin_data,
                ctx,
                builder,
                trailing,
            )
    return builder.finish(), heading, list_info, trailing, end


def _handle_control(
    recs: Sequence[Record],
    start: int,
    stop: int,
    code: int,
    docinfo: DocInfo,
    bin_data: ImageResolver | None,
    ctx: ReadContext,
    builder: _InlineBuilder,
    trailing: list[Block],
) -> None:
    """code: 대응한 확장 제어문자 코드(대응 포기면 0)."""
    r = recs[start]
    ctrl_id = r.payload[:4]
    if ctrl_id == CTRL_ID_TABLE:
        table, captions, _ = _parse_table(recs, start, r.level, docinfo, bin_data, ctx)
        if table is not None:
            trailing.append(table)
        trailing.extend(captions)
    elif ctrl_id == CTRL_ID_GSO:
        trailing.extend(_parse_gso(recs, start, stop, docinfo, bin_data, ctx))
    elif code == FIELD_START:
        if ctrl_id == CTRL_ID_HYPERLINK:
            builder.field_start(hyperlink_url(parse_field_command(r.payload)), link=True)
        else:
            builder.field_start(None, link=False)  # 누름틀 등: 글자는 그대로 둔다
    elif ctrl_id in (CTRL_ID_FOOTNOTE, CTRL_ID_ENDNOTE):
        kind: NoteKind = "footnote" if ctrl_id == CTRL_ID_FOOTNOTE else "endnote"
        ref = _parse_note(recs, start, stop, kind, docinfo, bin_data, ctx)
        if ref is not None:
            builder.inline(ref)
    elif ctrl_id == CTRL_ID_EQUATION:
        math = _parse_equation(recs, start, stop)
        if math is not None:
            builder.inline(math)
    elif ctrl_id in (CTRL_ID_HEADER, CTRL_ID_FOOTER):
        ctx.skips.add("header_footer")  # 하위 트리 통째로 건너뜀
    elif ctrl_id == CTRL_ID_HIDDEN_COMMENT:
        ctx.skips.add("hidden_comment")
    else:
        # 그 밖의 컨트롤: 안쪽 단락을 그대로 흘려보낸다
        trailing.extend(_subtree_blocks(recs, start, stop, docinfo, bin_data, ctx))


def _subtree_blocks(
    recs: Sequence[Record],
    start: int,
    stop: int,
    docinfo: DocInfo,
    bin_data: ImageResolver | None,
    ctx: ReadContext,
) -> list[Block]:
    """컨트롤 하위 트리 안 단락(level = 컨트롤+1)을 블록으로."""
    ctrl_level = recs[start].level
    out: list[Block] = []
    j = start + 1
    while j < stop:
        if recs[j].tag_id == HWPTAG_PARA_HEADER and recs[j].level == ctrl_level + 1:
            inlines, heading, list_info, trailing, j = _parse_paragraph(
                recs, j, ctrl_level + 1, docinfo, bin_data, ctx
            )
            para = make_paragraph(inlines, heading, list_info)
            if para is not None:
                out.append(para)
            out.extend(trailing)
        else:
            j += 1
    return out


def _parse_note(
    recs: Sequence[Record],
    start: int,
    stop: int,
    kind: NoteKind,
    docinfo: DocInfo,
    bin_data: ImageResolver | None,
    ctx: ReadContext,
) -> NoteRef | None:
    """각주 안 각주는 만들지 않는다(건너뛰고 보고하지 않는다)."""
    if ctx.in_note:
        return None
    number = ctx.next_note_number(kind)
    ctx.in_note = True
    try:
        blocks = _subtree_blocks(recs, start, stop, docinfo, bin_data, ctx)
    finally:
        ctx.in_note = False
    paragraphs: list[Paragraph] = []
    for b in blocks:
        para: Paragraph | None
        if isinstance(b, Paragraph):
            para = replace(b, level=0)
        elif isinstance(b, Table):
            para = make_paragraph([_flatten_table(b)])
        elif isinstance(b, Image):
            para = make_paragraph([b])
        else:
            para = None
        if para is not None:
            paragraphs.append(para)
    ctx.notes[kind].append(Note(kind, number, tuple(paragraphs)))
    return NoteRef(kind, number)


def _parse_equation(recs: Sequence[Record], start: int, stop: int) -> Math | None:
    for j in range(start + 1, stop):
        if recs[j].tag_id == HWPTAG_EQEDIT:
            script = parse_eqedit_script(recs[j].payload).strip()
            if not script:
                return None
            return Math(script, to_latex(script))
    return None


def _flatten_table(table: Table) -> str:
    return " ".join(c for row in table.rows for c in row if c)


def _paragraph_blocks(
    recs: Sequence[Record],
    j: int,
    docinfo: DocInfo,
    bin_data: ImageResolver | None,
    ctx: ReadContext,
) -> tuple[list[Block], int]:
    """recs[j] (PARA_HEADER) 단락 하나 → [단락, 뒤 블록...] 과 다음 인덱스."""
    inlines, heading, list_info, trailing, j = _parse_paragraph(
        recs, j, recs[j].level, docinfo, bin_data, ctx
    )
    para = make_paragraph(inlines, heading, list_info)
    out: list[Block] = [para] if para is not None else []
    out.extend(trailing)
    return out, j


def _parse_gso(
    recs: Sequence[Record],
    start: int,
    stop: int,
    docinfo: DocInfo,
    bin_data: ImageResolver | None,
    ctx: ReadContext,
) -> list[Block]:
    """그리기 개체 하나 → 블록. 개체 앞 캡션(LIST_HEADER + 단락)은 개체 블록 뒤에 둔다."""
    ctrl_level = recs[start].level
    blocks: list[Block] = []
    captions: list[Block] = []
    in_caption = False
    j = start + 1
    while j < stop:
        r = recs[j]
        if r.level != ctrl_level + 1:
            j += 1
        elif r.tag_id == HWPTAG_SHAPE_COMPONENT:
            in_caption = False
            end = _subtree_end(recs, j)
            blocks.extend(_parse_shape(recs, j, end, docinfo, bin_data, ctx))
            j = end
        elif r.tag_id == HWPTAG_LIST_HEADER:
            in_caption = True
            j += 1
        elif r.tag_id == HWPTAG_PARA_HEADER and in_caption:
            out, j = _paragraph_blocks(recs, j, docinfo, bin_data, ctx)
            captions.extend(out)
        else:
            j += 1
    return blocks + captions


def _parse_shape(
    recs: Sequence[Record],
    start: int,
    stop: int,
    docinfo: DocInfo,
    bin_data: ImageResolver | None,
    ctx: ReadContext,
) -> list[Block]:
    """SHAPE_COMPONENT 하나(recs[start]) 의 하위 트리를 저장 순서대로 순회한다.
    글상자 단락 · 그림 · OLE · 글맵시 · 묶음 자식 개체(재귀)."""
    blocks: list[Block] = []
    j = start + 1
    while j < stop:
        r = recs[j]
        if r.tag_id == HWPTAG_SHAPE_COMPONENT:
            end = _subtree_end(recs, j)
            blocks.extend(_parse_shape(recs, j, end, docinfo, bin_data, ctx))
            j = end
        elif r.tag_id == HWPTAG_PARA_HEADER:
            out, j = _paragraph_blocks(recs, j, docinfo, bin_data, ctx)
            blocks.extend(out)
        elif r.tag_id == HWPTAG_SHAPE_COMPONENT_PICTURE:
            if bin_data is not None:
                image = bin_data.resolve(parse_picture_bindata_id(r.payload))
                if image is not None:
                    blocks.append(image)
            j += 1
        elif r.tag_id == HWPTAG_SHAPE_COMPONENT_OLE:
            blocks.extend(_parse_ole(r.payload, bin_data, ctx))
            j += 1
        elif r.tag_id == HWPTAG_SHAPE_COMPONENT_TEXTART:
            ctx.skips.add("textart")
            j += 1
        else:
            j += 1
    return blocks


def _parse_ole(payload: bytes, bin_data: ImageResolver | None, ctx: ReadContext) -> list[Block]:
    """OLE 개체 → 차트 블록 / 이미지. 꺼낼 수 없으면 chart_legacy·ole 로 센다."""
    bindata_id = parse_ole_bindata_id(payload)
    data: bytes | None = None
    if bindata_id is not None and isinstance(bin_data, ObjectResolver):
        data = bin_data.ole_data(bindata_id)
    if data is None or not isinstance(bin_data, ObjectResolver):
        ctx.skips.add("ole")
        return []
    outcome = ole_to_outcome(unwrap_hwpx_ole(data), str(bindata_id), bin_data.make_image)
    if outcome.skipped is not None:
        ctx.skips.add(outcome.skipped)
    return list(outcome.blocks)


def _list_head(para: Paragraph) -> list[Inline]:
    """칸 안 목록 단락의 머리 글자 (§4-D): 글머리표 "- ", 그 밖 "<머리> ". 목록이 아니면 []."""
    info = para.list_info
    if info is None:
        return []
    return ["- " if info.kind == "bullet" else f"{info.label} "]


CellParas = list[list[Inline]]


def _cell_paragraphs(blocks: Sequence[Block]) -> CellParas:
    """칸 단락 하나의 블록(단락 + 뒤 블록) → 칸 단락 인라인 목록.
    그림은 바로 앞 칸 단락 끝에 붙이고, 중첩 표는 글자를 공백으로 이어 붙인 뒤
    그 안의 그림을 같은 칸 단락 끝에 붙인다."""
    paras: CellParas = []

    def tail() -> list[Inline]:
        if not paras:
            paras.append([])
        return paras[-1]

    for b in blocks:
        if isinstance(b, Paragraph):
            paras.append([*_list_head(b), *(b.inlines or (b.text,))])
        elif isinstance(b, Image):
            tail().append(b)
        elif isinstance(b, Table):
            flat = _flatten_table(b)
            if flat:
                paras.append([flat])
            for image in iter_images([b]):
                tail().append(image)
    return [p for p in paras if p]


def _parse_table(
    recs: Sequence[Record],
    i: int,
    ctrl_level: int,
    docinfo: DocInfo,
    bin_data: ImageResolver | None,
    ctx: ReadContext,
) -> tuple[Table | None, list[Block], int]:
    """(표, 캡션 블록, 다음 인덱스). TABLE 레코드 앞의 LIST_HEADER 는 캡션이다.
    TABLE 레코드가 없으면 표도 캡션도 없다."""
    stop = _subtree_end(recs, i)
    table_at = next(
        (
            k
            for k in range(i + 1, stop)
            if recs[k].tag_id == HWPTAG_TABLE and recs[k].level == ctrl_level + 1
        ),
        None,
    )
    if table_at is None:
        return None, [], stop
    i += 1
    header: TableHeader | None = None
    cells: list[tuple[CellHeader, CellParas]] = []
    captions: list[Block] = []
    current: tuple[CellHeader, CellParas] | None = None
    in_caption = False
    while i < len(recs) and recs[i].level > ctrl_level:
        r = recs[i]
        if r.tag_id == HWPTAG_TABLE and r.level == ctrl_level + 1:
            header = parse_table_header(r.payload)
            in_caption = False
            i += 1
        elif r.tag_id == HWPTAG_LIST_HEADER and r.level == ctrl_level + 1:
            if header is None:
                in_caption = True
            else:
                current = (parse_cell_header(r.payload), [])
                cells.append(current)
            i += 1
        elif r.tag_id == HWPTAG_PARA_HEADER and r.level == ctrl_level + 1 and in_caption:
            out, i = _paragraph_blocks(recs, i, docinfo, bin_data, ctx)
            captions.extend(out)
        elif r.tag_id == HWPTAG_PARA_HEADER and r.level == ctrl_level + 1 and current is not None:
            # 셀 단락은 인라인만 쓴다 (수준은 버린다)
            out, i = _paragraph_blocks(recs, i, docinfo, bin_data, ctx)
            current[1].extend(_cell_paragraphs(out))
        else:
            i += 1
    if header is None or header.row_count == 0 or header.col_count == 0:
        return None, captions, i
    return make_table(_place_cells(header, cells)), captions, i


def _place_cells(
    header: TableHeader, cells: Sequence[tuple[CellHeader, CellParas]]
) -> list[list[list[Inline]]]:
    rows, cols = header.row_count, header.col_count
    grid: list[list[list[Inline] | None]] = [[None] * cols for _ in range(rows)]
    for cell, paras in cells:
        text: list[Inline] = []
        for n, para in enumerate(paras):
            if n:
                text.append("\n")
            text.extend(para)
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
        grid[r][c] = text
        for rr in range(r, min(r + max(cell.row_span, 1), len(grid))):
            for cc in range(c, min(c + max(cell.col_span, 1), cols)):
                if (rr, cc) != (r, c) and grid[rr][cc] is None:
                    grid[rr][cc] = []  # 병합으로 덮인 칸
    return [[x if x is not None else [] for x in row] for row in grid]
