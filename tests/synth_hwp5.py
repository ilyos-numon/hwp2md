"""Synthetic HWP 5.0 file generator (pure-Python CFB writer + HWP record builder).

Test-only helper. Layout follows PLAN §4.4-A/B/D/E/F/G/H.
"""

from __future__ import annotations

import math
import struct
import zlib
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from hwp2md.blocks import Image, Paragraph, Table
from hwp2md.hwp5.records import (
    CTRL_ID_ENDNOTE,
    CTRL_ID_EQUATION,
    CTRL_ID_FOOTER,
    CTRL_ID_FOOTNOTE,
    CTRL_ID_HEADER,
    CTRL_ID_HIDDEN_COMMENT,
    CTRL_ID_HYPERLINK,
    CTRL_ID_TABLE,
    HWPTAG_CTRL_HEADER,
    HWPTAG_DOCUMENT_PROPERTIES,
    HWPTAG_EQEDIT,
    HWPTAG_LIST_HEADER,
    HWPTAG_PARA_CHAR_SHAPE,
    HWPTAG_PARA_HEADER,
    HWPTAG_PARA_LINE_SEG,
    HWPTAG_PARA_TEXT,
    HWPTAG_TABLE,
)
from synth_items import (
    SynthCaptionedTable,
    SynthChart,
    SynthEquation,
    SynthField,
    SynthHeaderFooter,
    SynthHidden,
    SynthLink,
    SynthListPara,
    SynthNote,
    SynthRich,
    SynthTextBox,
)

HWPTAG_PARA_SHAPE = 0x19
HWPTAG_STYLE = 0x1A
HWPTAG_BIN_DATA = 0x12
HWPTAG_SHAPE_COMPONENT = 0x4C
HWPTAG_SHAPE_COMPONENT_PICTURE = 0x55
CTRL_ID_GSO = b"gso "[::-1]  # == b" osg"

FIXTURE_PARAGRAPHS: list[str] = ["테스트 문서 제목", "본문 단락 1", "", "본문 단락 2"]
EXPECTED_MARKDOWN = "테스트 문서 제목\n\n본문 단락 1\n\n본문 단락 2\n"

HWP5_SIGNATURE = b"HWP Document File" + b"\x00" * 15  # 32 bytes, §4.3 reader 와 동일
HWP5_VERSION = 0x05000300
FILE_HEADER_SIZE = 256

_EXTENDED_SIZE = 0xFFF
_LAST_PARA_BIT = 0x80000000

# CFB (§4.4-G)
_CFB_MAGIC = bytes.fromhex("D0CF11E0A1B11AE1")
_SECTOR_SIZE = 512
_MINI_SECTOR_SIZE = 64
_MINI_CUTOFF = 0x1000
_DIR_ENTRY_SIZE = 128
_ENTRIES_PER_SECTOR = _SECTOR_SIZE // _DIR_ENTRY_SIZE
_FAT_ENTRIES = _SECTOR_SIZE // 4
FREESECT = 0xFFFFFFFF
ENDOFCHAIN = 0xFFFFFFFE
FATSECT = 0xFFFFFFFD
NOSTREAM = 0xFFFFFFFF

_STREAM_KEYS = ("FileHeader", "DocInfo", "BodyText/Section0")
_BINDATA_PREFIX = "BinData/"
_TYPE_EMPTY = 0
_TYPE_STORAGE = 1
_TYPE_STREAM = 2
_TYPE_ROOT = 5


def compress_raw(data: bytes) -> bytes:
    """zlib raw deflate (헤더 없음), §4.4-B."""
    comp = zlib.compressobj(9, zlib.DEFLATED, -15)
    return comp.compress(data) + comp.flush()


def build_file_header(*, properties: int = 0x1) -> bytes:
    """FileHeader 스트림 256 bytes, §4.4-A."""
    head = HWP5_SIGNATURE + struct.pack("<IIII", HWP5_VERSION, properties, 0, 0) + b"\x00"
    return head + b"\x00" * (FILE_HEADER_SIZE - len(head))


def build_record(tag_id: int, level: int, payload: bytes) -> bytes:
    size = len(payload)
    if size >= _EXTENDED_SIZE:
        header = tag_id | (level << 10) | (_EXTENDED_SIZE << 20)
        return struct.pack("<II", header, size) + payload
    return struct.pack("<I", tag_id | (level << 10) | (size << 20)) + payload


_CTRL_CHAR_EXTENDED = 11
_TABLE_PLACEHOLDER_MASK = 0x00000800
_TABLE_ATTR = 0x04000006
_CELL_ATTR = 0x20
_INNER_MARGIN = 141


@dataclass(frozen=True)
class SynthHeading:
    text: str
    level: int  # 1~7 (개요 1~7). para_shape_id = style_id = level


@dataclass(frozen=True)
class SynthImage:
    data: bytes
    ext: str  # "png" 등 소문자, 점 없음
    missing: bool = False  # True → 참조만 쓰고 바이너리 본체(스트림)는 쓰지 않는다


@dataclass(frozen=True)
class SynthCell:
    paragraphs: tuple[str | SynthHeading | SynthImage, ...]
    col: int
    row: int
    col_span: int = 1
    row_span: int = 1


@dataclass(frozen=True)
class SynthTable:
    rows: int
    cols: int
    cells: tuple[SynthCell, ...]


Item = str | SynthTable | SynthHeading | SynthImage
# build_section0·build_hwp5·write_hwp5 가 받는 항목: 기존 Item + 단락 안 요소 항목(synth_items)
AnyItem = (
    Item
    | SynthRich
    | SynthHeaderFooter
    | SynthHidden
    | SynthTextBox
    | SynthCaptionedTable
    | SynthChart
    | SynthListPara
)


def collect_images(items: Sequence[AnyItem]) -> list[SynthImage]:
    """문서 순서로 처음 보는 SynthImage 만 모은다. 바이너리 항목 k = index + 1 (§4.5)."""
    found: list[SynthImage] = []

    def add(x: object) -> None:
        if isinstance(x, SynthImage) and x not in found:
            found.append(x)

    for item in items:
        if isinstance(item, SynthTable):
            for c in item.cells:
                for p in c.paragraphs:
                    add(p)
        elif isinstance(item, SynthHeaderFooter):
            if item.with_image:
                add(HEADER_IMAGE)
        elif isinstance(item, SynthTextBox):
            if item.with_image:
                add(TEXTBOX_IMAGE)
        else:
            add(item)
    return found


def has_heading(items: Sequence[AnyItem]) -> bool:
    """items 또는 표 셀 단락에 SynthHeading 이 있으면 True."""
    for item in items:
        if isinstance(item, SynthHeading):
            return True
        if isinstance(item, SynthTable) and any(
            isinstance(p, SynthHeading) for c in item.cells for p in c.paragraphs
        ):
            return True
    return False


def build_paragraph(
    text: str, *, last: bool, level: int = 0, para_shape_id: int = 0, style_id: int = 0
) -> bytes:
    """§4.4-D/E: PARA_HEADER(level), PARA_TEXT·PARA_CHAR_SHAPE·PARA_LINE_SEG(level+1)."""
    text_bytes = text.encode("utf-16-le")
    nchars = len(text_bytes) // 2 + 1
    if last:
        nchars |= _LAST_PARA_BIT
    para_header = struct.pack("<IIHBBHHHI", nchars, 0, para_shape_id, style_id, 0, 1, 0, 1, 0)
    return (
        build_record(HWPTAG_PARA_HEADER, level, para_header)
        + build_record(HWPTAG_PARA_TEXT, level + 1, text_bytes + b"\r\x00")
        + build_record(HWPTAG_PARA_CHAR_SHAPE, level + 1, struct.pack("<II", 0, 0))
        + build_record(HWPTAG_PARA_LINE_SEG, level + 1, b"\x00" * 36)
    )


def build_ctrl_header_table(table: SynthTable) -> bytes:
    """§4.4-B: 표 컨트롤 CTRL_HEADER payload 44 bytes."""
    return CTRL_ID_TABLE + struct.pack("<IiiIIiHHHHII", 0, 0, 0, 10000, 2000, 0, 0, 0, 0, 0, 0, 0)


def build_table_record(table: SynthTable) -> bytes:
    """§4.4-C: TABLE payload, 18 + 2×rows + 4 bytes."""
    per_row = [sum(1 for c in table.cells if c.row == r) for r in range(table.rows)]
    return (
        struct.pack("<IHHH4H", _TABLE_ATTR, table.rows, table.cols, 0, *[_INNER_MARGIN] * 4)
        + struct.pack(f"<{table.rows}H", *per_row)
        + struct.pack("<HH", 1, 0)
    )


def build_cell_header(cell: SynthCell) -> bytes:
    """§4.4-D: 셀 LIST_HEADER payload 38 bytes."""
    return struct.pack(
        "<HHIHHHHII4HHI",
        len(cell.paragraphs),
        0,
        _CELL_ATTR,
        cell.col,
        cell.row,
        cell.col_span,
        cell.row_span,
        5000,
        1000,
        *[_INNER_MARGIN] * 4,
        1,
        5000,
    )


_PIC_W, _PIC_H = 8196, 3382
CHID_PIC = b"$pic"[::-1]  # == b"cip$"
_SHAPE_COMPONENT_LEN = 196  # chid0(4)+chid(4)+188 zero bytes. 파서는 읽지 않는다
_PIC_BINDATA_ID_OFFSET = 71


def build_bin_data(storage_id: int, ext: str) -> bytes:
    """§4.3-B: EMBEDDING, 압축 비트 0(문서 기본). "png" → 12 bytes."""
    return struct.pack("<HHH", 0x0001, storage_id, len(ext)) + ext.encode("utf-16-le")


def build_ctrl_header_gso() -> bytes:
    """§4.5: 그리기 개체 CTRL_HEADER payload 44 bytes."""
    return CTRL_ID_GSO + struct.pack("<IiiIIiHHHHII", 0, 0, 0, _PIC_W, _PIC_H, 0, 0, 0, 0, 0, 0, 0)


def build_shape_component_pic() -> bytes:
    """§4.5: SHAPE_COMPONENT payload 196 bytes."""
    return CHID_PIC + CHID_PIC + b"\x00" * (_SHAPE_COMPONENT_LEN - 8)


def build_picture_record(bindata_id: int) -> bytes:
    """§4.4/§4.5: SHAPE_COMPONENT_PICTURE payload 78 bytes, bindata_id @71."""
    return (
        struct.pack("<IiI", 0, 0, 0)
        + struct.pack("<8i", 0, 0, _PIC_W, 0, _PIC_W, _PIC_H, 0, _PIC_H)
        + struct.pack("<4i", 0, 0, 0, 0)
        + struct.pack("<4H", 0, 0, 0, 0)
        + struct.pack("<bbBH", 0, 0, 0, bindata_id)
        + struct.pack("<BI", 0, 0)
    )


def build_picture_control(bindata_id: int, *, level: int, last: bool) -> bytes:
    """§4.4-A: 자리표시자 단락 + CTRL_HEADER(gso) + SHAPE_COMPONENT + SHAPE_COMPONENT_PICTURE."""
    placeholder = (
        struct.pack("<H", _CTRL_CHAR_EXTENDED)
        + CTRL_ID_GSO
        + b"\x00" * 8
        + struct.pack("<H", _CTRL_CHAR_EXTENDED)
        + b"\r\x00"
    )
    nchars = len(placeholder) // 2
    if last:
        nchars |= _LAST_PARA_BIT
    para_header = struct.pack("<IIHBBHHHI", nchars, _TABLE_PLACEHOLDER_MASK, 0, 0, 0, 1, 0, 1, 0)
    return (
        build_record(HWPTAG_PARA_HEADER, level, para_header)
        + build_record(HWPTAG_PARA_TEXT, level + 1, placeholder)
        + build_record(HWPTAG_PARA_CHAR_SHAPE, level + 1, struct.pack("<II", 0, 0))
        + build_record(HWPTAG_PARA_LINE_SEG, level + 1, b"\x00" * 36)
        + build_record(HWPTAG_CTRL_HEADER, level + 1, build_ctrl_header_gso())
        + build_record(HWPTAG_SHAPE_COMPONENT, level + 2, build_shape_component_pic())
        + build_record(HWPTAG_SHAPE_COMPONENT_PICTURE, level + 3, build_picture_record(bindata_id))
    )


def build_table_control(
    table: SynthTable, *, level: int, last: bool, images: Sequence[SynthImage] = ()
) -> bytes:
    """§4.4-F: 자리표시자 단락 + CTRL_HEADER + TABLE + [LIST_HEADER + 셀 단락]×k."""
    placeholder = (
        struct.pack("<H", _CTRL_CHAR_EXTENDED)
        + CTRL_ID_TABLE
        + b"\x00" * 8
        + struct.pack("<H", _CTRL_CHAR_EXTENDED)
        + b"\r\x00"
    )
    nchars = len(placeholder) // 2
    if last:
        nchars |= _LAST_PARA_BIT
    para_header = struct.pack("<IIHBBHHHI", nchars, _TABLE_PLACEHOLDER_MASK, 0, 0, 0, 1, 0, 1, 0)
    out = (
        build_record(HWPTAG_PARA_HEADER, level, para_header)
        + build_record(HWPTAG_PARA_TEXT, level + 1, placeholder)
        + build_record(HWPTAG_PARA_CHAR_SHAPE, level + 1, struct.pack("<II", 0, 0))
        + build_record(HWPTAG_PARA_LINE_SEG, level + 1, b"\x00" * 36)
        + build_record(HWPTAG_CTRL_HEADER, level + 1, build_ctrl_header_table(table))
        + build_record(HWPTAG_TABLE, level + 2, build_table_record(table))
    )
    for cell in table.cells:
        out += build_record(HWPTAG_LIST_HEADER, level + 2, build_cell_header(cell))
        last_index = len(cell.paragraphs) - 1
        for i, p in enumerate(cell.paragraphs):
            if isinstance(p, SynthHeading):
                out += build_paragraph(
                    p.text,
                    last=(i == last_index),
                    level=level + 2,
                    para_shape_id=p.level,
                    style_id=p.level,
                )
            elif isinstance(p, SynthImage):
                out += build_picture_control(
                    images.index(p) + 1, level=level + 2, last=(i == last_index)
                )
            else:
                out += build_paragraph(p, last=(i == last_index), level=level + 2)
    return out


_FIELD_START = 3
_FIELD_END = 4
_CTRL_CHAR_HIDDEN = 15
_CTRL_CHAR_HEADER_FOOTER = 16
_CTRL_CHAR_NOTE = 17
CTRL_ID_CLICK_HERE = b"%clk"[::-1]  # 누름틀 필드


def _ctrl_chars(code: int, ctrl_id: bytes) -> bytes:
    """확장·필드 끝 제어문자 8 WCHAR: 코드 + ctrl_id(4) + 0×8 + 코드."""
    return struct.pack("<H", code) + ctrl_id + b"\x00" * 8 + struct.pack("<H", code)


def _para_records(wchars: bytes, *, level: int, last: bool, ctrl_mask: int = 0) -> bytes:
    """PARA_HEADER(level) + PARA_TEXT·CHAR_SHAPE·LINE_SEG(level+1). wchars 는 끝 13 제외."""
    body = wchars + b"\r\x00"
    nchars = len(body) // 2
    if last:
        nchars |= _LAST_PARA_BIT
    para_header = struct.pack("<IIHBBHHHI", nchars, ctrl_mask, 0, 0, 0, 1, 0, 1, 0)
    return (
        build_record(HWPTAG_PARA_HEADER, level, para_header)
        + build_record(HWPTAG_PARA_TEXT, level + 1, body)
        + build_record(HWPTAG_PARA_CHAR_SHAPE, level + 1, struct.pack("<II", 0, 0))
        + build_record(HWPTAG_PARA_LINE_SEG, level + 1, b"\x00" * 36)
    )


def escape_link_target(url: str) -> str:
    """하이퍼링크 command 의 대상 이스케이프: `\\` `:` `?` `;` `#` `|` 앞에 `\\`."""
    return "".join("\\" + ch if ch in "\\:?;#|" else ch for ch in url)


def build_ctrl_header_field(ctrl_id: bytes, command: str) -> bytes:
    """필드 CTRL_HEADER: ctrl_id + UINT32 속성 + BYTE 기타 + WORD len + WCHAR command
    + UINT32 인스턴스 ID."""
    cmd = command.encode("utf-16-le")
    return ctrl_id + struct.pack("<IBH", 0, 0, len(cmd) // 2) + cmd + struct.pack("<I", 1)


def build_list_header(n_paragraphs: int) -> bytes:
    """문단 리스트 LIST_HEADER: UINT32 문단 수 + UINT32 속성 + 0×8."""
    return struct.pack("<II", n_paragraphs, 0) + b"\x00" * 8


def build_subtree_paragraphs(paragraphs: Sequence[str], *, level: int) -> bytes:
    """LIST_HEADER(level) + 단락들(level)."""
    out = build_record(HWPTAG_LIST_HEADER, level, build_list_header(len(paragraphs)))
    for i, text in enumerate(paragraphs):
        out += build_paragraph(text, last=(i == len(paragraphs) - 1), level=level)
    return out


def build_eqedit(script: str) -> bytes:
    """EQEDIT payload: UINT32 속성, WORD len + WCHAR 스크립트, UINT32 글자 크기, COLORREF,
    INT16 baseline, UINT16, WORD len + 버전 문자열, WORD len + 글꼴 이름."""
    sc = script.encode("utf-16-le")
    ver = "Equation Version 60".encode("utf-16-le")
    font = "HancomEQN".encode("utf-16-le")
    return (
        struct.pack("<IH", 0, len(sc) // 2)
        + sc
        + struct.pack("<IIhH", 1000, 0, 85, 0)
        + struct.pack("<H", len(ver) // 2)
        + ver
        + struct.pack("<H", len(font) // 2)
        + font
    )


def build_rich_paragraph(rich: SynthRich, *, level: int, last: bool) -> bytes:
    """링크·누름틀(필드 시작 3 … 끝 4), 각주·미주(17), 수식(11) 을 위치대로 쓴 단락.
    확장 제어문자 순서와 같은 순서로 CTRL_HEADER(level+1) 를 단락 뒤에 둔다."""
    wchars = b""
    ctrls = b""
    for run in rich.runs:
        if isinstance(run, str):
            wchars += run.encode("utf-16-le")
        elif isinstance(run, SynthLink):
            wchars += (
                _ctrl_chars(_FIELD_START, CTRL_ID_HYPERLINK)
                + run.text.encode("utf-16-le")
                + _ctrl_chars(_FIELD_END, CTRL_ID_HYPERLINK)
            )
            command = escape_link_target(run.url) + ";1;0;0;"
            ctrls += build_record(
                HWPTAG_CTRL_HEADER, level + 1, build_ctrl_header_field(CTRL_ID_HYPERLINK, command)
            )
        elif isinstance(run, SynthField):
            wchars += (
                _ctrl_chars(_FIELD_START, CTRL_ID_CLICK_HERE)
                + run.text.encode("utf-16-le")
                + _ctrl_chars(_FIELD_END, CTRL_ID_CLICK_HERE)
            )
            ctrls += build_record(
                HWPTAG_CTRL_HEADER,
                level + 1,
                build_ctrl_header_field(CTRL_ID_CLICK_HERE, "Clickhere:set:0:"),
            )
        elif isinstance(run, SynthNote):
            ctrl_id = CTRL_ID_FOOTNOTE if run.kind == "footnote" else CTRL_ID_ENDNOTE
            wchars += _ctrl_chars(_CTRL_CHAR_NOTE, ctrl_id)
            ctrls += build_record(HWPTAG_CTRL_HEADER, level + 1, ctrl_id + b"\x00" * 8)
            ctrls += build_subtree_paragraphs(run.paragraphs, level=level + 2)
        else:
            assert isinstance(run, SynthEquation)
            wchars += _ctrl_chars(_CTRL_CHAR_EXTENDED, CTRL_ID_EQUATION)
            ctrls += build_record(
                HWPTAG_CTRL_HEADER,
                level + 1,
                CTRL_ID_EQUATION
                + struct.pack("<IiiIIiHHHHII", 0, 0, 0, 2000, 1000, 0, 0, 0, 0, 0, 0, 0),
            )
            ctrls += build_record(HWPTAG_EQEDIT, level + 2, build_eqedit(run.script))
    return _para_records(wchars, level=level, last=last) + ctrls


def build_header_footer_paragraph(
    item: SynthHeaderFooter, *, level: int, last: bool, images: Sequence[SynthImage] = ()
) -> bytes:
    """제어문자 16 하나뿐인 단락 + CTRL_HEADER(head|foot) + LIST_HEADER + 안쪽 단락(+그림)."""
    ctrl_id = CTRL_ID_HEADER if item.kind == "header" else CTRL_ID_FOOTER
    out = _para_records(_ctrl_chars(_CTRL_CHAR_HEADER_FOOTER, ctrl_id), level=level, last=last)
    out += build_record(
        HWPTAG_CTRL_HEADER, level + 1, ctrl_id + struct.pack("<IiiBB", 0, 42520, 4252, 0, 0)
    )
    n = len(item.paragraphs) + (1 if item.with_image else 0)
    out += build_record(HWPTAG_LIST_HEADER, level + 2, build_list_header(n))
    for i, text in enumerate(item.paragraphs):
        out += build_paragraph(text, last=(i == n - 1), level=level + 2)
    if item.with_image:
        out += build_picture_control(images.index(HEADER_IMAGE) + 1, level=level + 2, last=True)
    return out


def build_hidden_paragraph(item: SynthHidden, *, level: int, last: bool) -> bytes:
    """제어문자 15 하나뿐인 단락 + CTRL_HEADER(tcmt) + LIST_HEADER + 안쪽 단락."""
    out = _para_records(
        _ctrl_chars(_CTRL_CHAR_HIDDEN, CTRL_ID_HIDDEN_COMMENT), level=level, last=last
    )
    out += build_record(HWPTAG_CTRL_HEADER, level + 1, CTRL_ID_HIDDEN_COMMENT)
    out += build_subtree_paragraphs(item.paragraphs, level=level + 2)
    return out


# 개체(S12): 글상자 · 캡션 있는 표 · 차트(OLE)
CHID_RECT = b"$rec"[::-1]
CHID_OLE = b"$ole"[::-1]
HWPTAG_SHAPE_COMPONENT_RECTANGLE = 0x4F
HWPTAG_SHAPE_COMPONENT_OLE = 0x54
_BIN_DATA_STORAGE_ATTR = 0x0002


def collect_charts(items: Sequence[AnyItem]) -> list[SynthChart]:
    """문서 순서의 SynthChart. BinData ID = len(collect_images(items)) + index + 1."""
    return [x for x in items if isinstance(x, SynthChart)]


def build_bin_data_storage(storage_id: int) -> bytes:
    """OLE 개체용 BIN_DATA: STORAGE, 압축 비트 0(문서 기본). 스트림 BIN<id>.ole."""
    return struct.pack("<HH", _BIN_DATA_STORAGE_ATTR, storage_id)


def build_chart_ole(chart: SynthChart) -> bytes:
    """OLE BinData 스트림 본문(압축 전) = [UINT32 LE len(cfb)][cfb] (실제 샘플과 같은 모양).
    legacy → 구형 차트 `Contents` 스트림만, 아니면 `OOXMLChartContents`."""
    from synth_ole import build_ole_cfb, chart_xml  # synth_ole 이 synth_hwp5 를 import 한다

    if chart.legacy:
        cfb = build_ole_cfb({"Contents": b"\x00" * 64})
    else:
        cfb = build_ole_cfb(
            {"OOXMLChartContents": chart_xml(chart.title, chart.categories, chart.series)}
        )
    return struct.pack("<I", len(cfb)) + cfb


def _gso_anchor(text: str, *, level: int, last: bool) -> bytes:
    """글자 + 확장 제어문자 11(gso) 단락."""
    return _para_records(
        text.encode("utf-16-le") + _ctrl_chars(_CTRL_CHAR_EXTENDED, CTRL_ID_GSO),
        level=level,
        last=last,
        ctrl_mask=_TABLE_PLACEHOLDER_MASK,
    )


def build_textbox_list_header(n_paragraphs: int) -> bytes:
    """글상자 LIST_HEADER: UINT32 문단 수 + UINT32 속성 + 여백 4×INT16 + 최대 폭 UINT32."""
    return struct.pack("<II4hI", n_paragraphs, 0x20, 283, 283, 283, 283, 8000) + b"\x00" * 13


def build_textbox_paragraph(
    item: SynthTextBox, *, level: int, last: bool, images: Sequence[SynthImage] = ()
) -> bytes:
    """앵커 단락(글자 + gso) + CTRL_HEADER(gso) + SHAPE_COMPONENT($rec) + 글상자 LIST_HEADER
    + 단락들(+그림 단락) + SHAPE_COMPONENT_RECTANGLE. 실제 샘플과 같은 수준 관계."""
    out = _gso_anchor(item.anchor_text, level=level, last=last)
    out += build_record(HWPTAG_CTRL_HEADER, level + 1, build_ctrl_header_gso())
    out += build_record(HWPTAG_SHAPE_COMPONENT, level + 2, CHID_RECT + CHID_RECT + b"\x00" * 244)
    n = len(item.paragraphs) + (1 if item.with_image else 0)
    out += build_record(HWPTAG_LIST_HEADER, level + 3, build_textbox_list_header(n))
    for i, text in enumerate(item.paragraphs):
        out += build_paragraph(text, last=(i == n - 1), level=level + 3)
    if item.with_image:
        out += build_picture_control(images.index(TEXTBOX_IMAGE) + 1, level=level + 3, last=True)
    out += build_record(HWPTAG_SHAPE_COMPONENT_RECTANGLE, level + 3, b"\x00" * 33)
    return out


def build_caption_list_header(n_paragraphs: int) -> bytes:
    """캡션 LIST_HEADER 30 bytes: UINT32 문단 수 + UINT32 속성 + 캡션 속성(방향 아래=3)
    + 폭 + 간격 + 텍스트 최대 길이. 오프셋 8 이 칸 열 번호로 읽히면 3 이 된다."""
    return struct.pack("<IIIIhI", n_paragraphs, 0, 3, 8504, 850, 42520) + b"\x00" * 4


def build_captioned_table_paragraph(item: SynthCaptionedTable, *, level: int, last: bool) -> bytes:
    """자리표시자 단락 + CTRL_HEADER(tbl) + 캡션 LIST_HEADER + 캡션 단락 + TABLE + 칸들.
    캡션은 TABLE 레코드보다 앞에 온다(실제 샘플과 같은 순서)."""
    rows = len(item.cells)
    cols = max((len(r) for r in item.cells), default=0)
    table = SynthTable(
        rows=rows,
        cols=cols,
        cells=tuple(
            SynthCell((text,), col=c, row=r)
            for r, row in enumerate(item.cells)
            for c, text in enumerate(row)
        ),
    )
    plain = build_table_control(table, level=level, last=last)
    split = plain.index(build_record(HWPTAG_TABLE, level + 2, build_table_record(table)))
    caption = build_record(HWPTAG_LIST_HEADER, level + 2, build_caption_list_header(1))
    caption += build_paragraph(item.caption, last=True, level=level + 2)
    return plain[:split] + caption + plain[split:]


def build_chart_paragraph(bindata_id: int, *, level: int, last: bool) -> bytes:
    """gso 하나뿐인 단락 + CTRL_HEADER(gso) + SHAPE_COMPONENT($ole) + SHAPE_COMPONENT_OLE.
    OLE 레코드: UINT32 속성, INT32 extent x·y, UINT16 BinData ID(오프셋 12), 테두리."""
    out = _gso_anchor("", level=level, last=last)
    out += build_record(HWPTAG_CTRL_HEADER, level + 1, build_ctrl_header_gso())
    out += build_record(HWPTAG_SHAPE_COMPONENT, level + 2, CHID_OLE + CHID_OLE + b"\x00" * 188)
    ole = struct.pack("<IiiHIiI", 0x00010001, 7926, 3728, bindata_id, 0, 0, 0)
    out += build_record(HWPTAG_SHAPE_COMPONENT_OLE, level + 3, ole)
    return out


def build_section0(items: Sequence[AnyItem], images: Sequence[SynthImage] | None = None) -> bytes:
    """미압축 섹션. str → 본문 단락, SynthHeading → 개요 단락, SynthTable → 표 컨트롤.

    마지막 원소만 last=True.
    """
    if images is None:
        images = collect_images(items)
    last_index = len(items) - 1
    out = b""
    for i, item in enumerate(items):
        last = i == last_index
        if isinstance(item, SynthTable):
            out += build_table_control(item, level=0, last=last, images=images)
        elif isinstance(item, SynthImage):
            out += build_picture_control(images.index(item) + 1, level=0, last=last)
        elif isinstance(item, SynthRich):
            out += build_rich_paragraph(item, level=0, last=last)
        elif isinstance(item, SynthHeaderFooter):
            out += build_header_footer_paragraph(item, level=0, last=last, images=images)
        elif isinstance(item, SynthHidden):
            out += build_hidden_paragraph(item, level=0, last=last)
        elif isinstance(item, SynthTextBox):
            out += build_textbox_paragraph(item, level=0, last=last, images=images)
        elif isinstance(item, SynthCaptionedTable):
            out += build_captioned_table_paragraph(item, level=0, last=last)
        elif isinstance(item, SynthChart):
            bindata_id = len(images) + collect_charts(items).index(item) + 1
            out += build_chart_paragraph(bindata_id, level=0, last=last)
        elif isinstance(item, SynthHeading):
            out += build_paragraph(
                item.text, last=last, para_shape_id=item.level, style_id=item.level
            )
        elif isinstance(item, SynthListPara):
            shape_id = LIST_PARA_SHAPE_BASE + list_shape_keys(items).index((item.kind, item.depth))
            out += build_paragraph(item.text, last=last, para_shape_id=shape_id)
        else:
            out += build_paragraph(item, last=last)
    return out


def build_para_shape(*, outline_level: int) -> bytes:
    """§4.3-D: PARA_SHAPE payload 54 bytes. 0 → 본문, 1~7 → 개요 L."""
    attr1 = 0 if outline_level == 0 else (1 << 23) | ((outline_level - 1) << 25)
    return (
        struct.pack("<I", attr1)
        + struct.pack("<6i", 0, 0, 0, 0, 0, 0)
        + struct.pack("<3H", 0, 0, 0)
        + struct.pack("<4h", 0, 0, 0, 0)
        + struct.pack("<III", 0, 0, 0)
    )


HWPTAG_NUMBERING = 0x17
HWPTAG_BULLET = 0x18
LIST_PARA_SHAPE_BASE = 8  # 목록 문단 모양 ID 는 본문·개요 8개 다음부터
BULLET_CHAR = "\u25cf"
NUM_FORMAT_DIGIT, NUM_FORMAT_CIRCLED_DIGIT, NUM_FORMAT_HANGUL = 0, 1, 8  # 번호 모양 코드


def list_shape_keys(items: Sequence[object]) -> list[tuple[str, int]]:
    """SynthListPara 의 (kind, depth) 를 처음 나온 순서로. 문단 모양 ID = BASE + index."""
    keys: list[tuple[str, int]] = []
    for item in items:
        if isinstance(item, SynthListPara) and (item.kind, item.depth) not in keys:
            keys.append((item.kind, item.depth))
    return keys


def build_list_para_shape(kind: str, depth: int, head_id: int = 1) -> bytes:
    """번호(2)·글머리표(3) 문단 모양. 속성1 비트 23~24 머리 종류, 25~27 수준, @30 ID."""
    head_type = 2 if kind == "number" else 3
    attr1 = (head_type << 23) | (depth << 25)
    return (
        struct.pack("<I", attr1)
        + struct.pack("<6i", 0, 0, 0, 0, 0, 0)
        + struct.pack("<3H", 0, head_id, 0)
        + struct.pack("<4h", 0, 0, 0, 0)
        + struct.pack("<III", 0, 0, 0)
    )


def build_para_head_info(num_format: int = NUM_FORMAT_DIGIT) -> bytes:
    """문단 머리 정보 12B: UINT32 속성(비트 5~9 번호 모양), HWPUNIT16 ×2, UINT32 글자 모양."""
    return struct.pack("<IHHI", num_format << 5, 0, 0, 0)


def build_numbering(
    templates: Sequence[str],
    *,
    formats: Sequence[int] = (),
    start: int = 1,
    level_starts: Sequence[int] | None = (1, 1, 1, 1, 1, 1, 1),
) -> bytes:
    """NUMBERING payload. 수준 1~7 [머리 정보 + WORD len + WCHAR 형식], UINT16 시작 번호,
    level_starts 가 있으면 UINT32 ×7. 빠진 수준 형식은 "^k.", 빠진 모양은 숫자."""
    out = b""
    for k in range(7):
        template = templates[k] if k < len(templates) else f"^{k + 1}."
        fmt = formats[k] if k < len(formats) else NUM_FORMAT_DIGIT
        raw = template.encode("utf-16-le")
        out += build_para_head_info(fmt) + struct.pack("<H", len(raw) // 2) + raw
    out += struct.pack("<H", start)
    if level_starts is not None:
        out += struct.pack("<7I", *level_starts)
    return out


def build_bullet(char: str = BULLET_CHAR) -> bytes:
    """BULLET payload: 머리 정보 + WCHAR 글머리표 문자 + INT32 이미지 여부 + 그림 정보 4B
    + WCHAR 체크 글머리표 문자."""
    return build_para_head_info() + char.encode("utf-16-le") + struct.pack("<iI", 0, 0) + b"\0\0"


def list_templates(items: Sequence[object]) -> list[str]:
    """수준별 형식 문자열: 그 수준 SynthListPara 의 첫 template, 없으면 "^k."."""
    out = [f"^{k + 1}." for k in range(7)]
    seen: set[int] = set()
    for item in items:
        if isinstance(item, SynthListPara) and item.kind == "number" and item.depth not in seen:
            seen.add(item.depth)
            if 0 <= item.depth < 7:
                out[item.depth] = item.template
    return out


def build_style(index: int) -> bytes:
    """§4.3-E: STYLE payload. 0 → 바탕글/Normal, 1~7 → 개요 L/Outline L."""
    if index == 0:
        ko, en = "바탕글", "Normal"
    else:
        ko, en = f"개요 {index}", f"Outline {index}"
    ko_b = ko.encode("utf-16-le")
    en_b = en.encode("utf-16-le")
    return (
        struct.pack("<H", len(ko_b) // 2)
        + ko_b
        + struct.pack("<H", len(en_b) // 2)
        + en_b
        + struct.pack("<BBhHHH", 0, index, 1042, index, 0, 0)
    )


def build_docinfo(
    *,
    outline: bool = False,
    images: Sequence[SynthImage] = (),
    ole_count: int = 0,
    lists: Sequence[SynthListPara] = (),
    list_formats: Sequence[int] = (),
) -> bytes:
    """미압축 DocInfo, §4.4-F·§4.5.

    images 마다 BIN_DATA(level 1), 이어서 OLE 개체 ole_count 개의 STORAGE BIN_DATA,
    outline=True 면 PARA_SHAPE·STYLE 각 8개.
    lists 가 있으면 NUMBERING 1개(ID 1, 번호 모양 list_formats)·BULLET 1개(ID 1),
    PARA_SHAPE·STYLE 각 8개, 이어서 list_shape_keys 순서의 목록 PARA_SHAPE.
    """
    payload = struct.pack("<7HIII", 1, 1, 1, 1, 1, 1, 1, 0, 0, 0)
    out = build_record(HWPTAG_DOCUMENT_PROPERTIES, 0, payload)
    for k, img in enumerate(images, start=1):
        out += build_record(HWPTAG_BIN_DATA, 1, build_bin_data(k, img.ext))
    for k in range(len(images) + 1, len(images) + ole_count + 1):
        out += build_record(HWPTAG_BIN_DATA, 1, build_bin_data_storage(k))
    if lists:
        out += build_record(
            HWPTAG_NUMBERING, 1, build_numbering(list_templates(lists), formats=list_formats)
        )
        out += build_record(HWPTAG_BULLET, 1, build_bullet())
    if outline or lists:
        for i in range(8):
            out += build_record(HWPTAG_PARA_SHAPE, 1, build_para_shape(outline_level=i))
        for kind, depth in list_shape_keys(lists):
            out += build_record(HWPTAG_PARA_SHAPE, 1, build_list_para_shape(kind, depth))
        for i in range(8):
            out += build_record(HWPTAG_STYLE, 1, build_style(i))
    return out


def _dir_entry(
    name: str,
    entry_type: int,
    *,
    left: int = NOSTREAM,
    right: int = NOSTREAM,
    child: int = NOSTREAM,
    start: int = 0,
    size: int = 0,
) -> bytes:
    if entry_type == _TYPE_EMPTY:
        name_field = b"\x00" * 64
        name_len = 0
        color = 0
    else:
        encoded = name.encode("utf-16-le") + b"\x00\x00"
        name_field = encoded + b"\x00" * (64 - len(encoded))
        name_len = len(encoded)
        color = 1
    entry = (
        name_field
        + struct.pack("<HBB", name_len, entry_type, color)
        + struct.pack("<III", left, right, child)
        + b"\x00" * 16  # CLSID
        + b"\x00" * 4  # state bits
        + b"\x00" * 16  # times
        + struct.pack("<II", start, size)
        + b"\x00" * 4
    )
    assert len(entry) == _DIR_ENTRY_SIZE
    return entry


def build_cfb(streams: Mapping[str, bytes]) -> bytes:
    """§4.4-G, §4.5 (v3, 512-byte 섹터).

    키: "FileHeader", "DocInfo", "BodyText/Section0" 필수 + 선택 "BinData/<NAME>".
    """
    bin_keys = [k for k in streams if k.startswith(_BINDATA_PREFIX)]
    if set(streams) - set(bin_keys) != set(_STREAM_KEYS) or any(
        not k[len(_BINDATA_PREFIX) :] or "/" in k[len(_BINDATA_PREFIX) :] for k in bin_keys
    ):
        raise ValueError(
            f"streams must have exactly the keys {sorted(_STREAM_KEYS)}"
            " plus optional BinData/<NAME>"
        )
    bin_keys.sort(key=lambda k: (len(k), k[len(_BINDATA_PREFIX) :].upper()))
    for key, data in streams.items():
        if len(data) >= _MINI_CUTOFF:
            raise ValueError(f"stream {key!r} is {len(data)} bytes; fixture supports < 4096")

    # 미니스트림 배치 + MiniFAT
    ministream = bytearray()
    minifat: list[int] = []
    mini_start: dict[str, int] = {}
    for key in (*_STREAM_KEYS, *bin_keys):
        data = streams[key]
        count = math.ceil(len(data) / _MINI_SECTOR_SIZE)
        if count == 0:
            mini_start[key] = ENDOFCHAIN
            continue
        first = len(minifat)
        mini_start[key] = first
        minifat.extend(range(first + 1, first + count))
        minifat.append(ENDOFCHAIN)
        ministream += data + b"\x00" * (count * _MINI_SECTOR_SIZE - len(data))
    if len(minifat) > _FAT_ENTRIES:
        raise ValueError("too many mini sectors for a single MiniFAT sector")

    entries_count = 5 + (1 + len(bin_keys) if bin_keys else 0)
    dir_sectors = math.ceil(entries_count * _DIR_ENTRY_SIZE / _SECTOR_SIZE)
    minifat_sector = 1 + dir_sectors
    ministream_first = minifat_sector + 1
    ministream_sectors = math.ceil(len(ministream) / _SECTOR_SIZE)
    total_sectors = ministream_first + ministream_sectors
    if total_sectors > _FAT_ENTRIES:
        raise ValueError("too many sectors for a single FAT sector")

    # FAT
    fat = [FREESECT] * _FAT_ENTRIES
    fat[0] = FATSECT
    for s in range(1, 1 + dir_sectors):
        fat[s] = s + 1 if s < dir_sectors else ENDOFCHAIN
    fat[minifat_sector] = ENDOFCHAIN
    for i in range(ministream_sectors):
        s = ministream_first + i
        fat[s] = s + 1 if i < ministream_sectors - 1 else ENDOFCHAIN
    fat_bytes = struct.pack(f"<{_FAT_ENTRIES}I", *fat)

    minifat_full = minifat + [FREESECT] * (_FAT_ENTRIES - len(minifat))
    minifat_bytes = struct.pack(f"<{_FAT_ENTRIES}I", *minifat_full)

    # 디렉터리 (엔트리 번호·트리 고정)
    root_start = ministream_first if ministream_sectors else ENDOFCHAIN
    entries = [
        _dir_entry("Root Entry", _TYPE_ROOT, child=1, start=root_start, size=len(ministream)),
        _dir_entry("BodyText", _TYPE_STORAGE, left=2, right=3, child=4),
        _dir_entry(
            "DocInfo",
            _TYPE_STREAM,
            left=5 if bin_keys else NOSTREAM,
            start=mini_start["DocInfo"],
            size=len(streams["DocInfo"]),
        ),
        _dir_entry(
            "FileHeader",
            _TYPE_STREAM,
            start=mini_start["FileHeader"],
            size=len(streams["FileHeader"]),
        ),
        _dir_entry(
            "Section0",
            _TYPE_STREAM,
            start=mini_start["BodyText/Section0"],
            size=len(streams["BodyText/Section0"]),
        ),
    ]
    if bin_keys:
        entries.append(_dir_entry("BinData", _TYPE_STORAGE, child=6))
        for j, key in enumerate(bin_keys):
            entries.append(
                _dir_entry(
                    key[len(_BINDATA_PREFIX) :],
                    _TYPE_STREAM,
                    right=7 + j if j < len(bin_keys) - 1 else NOSTREAM,
                    start=mini_start[key],
                    size=len(streams[key]),
                )
            )
    slots = dir_sectors * _ENTRIES_PER_SECTOR
    entries.extend(_dir_entry("", _TYPE_EMPTY) for _ in range(slots - len(entries)))
    dir_bytes = b"".join(entries)

    # 헤더
    header = bytearray(_SECTOR_SIZE)
    header[0:8] = _CFB_MAGIC
    struct.pack_into("<HHHHH", header, 24, 0x003E, 0x0003, 0xFFFE, 0x0009, 0x0006)
    struct.pack_into(
        "<IIIIIIIII",
        header,
        40,
        0,  # v3 디렉터리 섹터 수
        1,  # FAT 섹터 수
        1,  # 첫 디렉터리 섹터
        0,  # transaction signature
        _MINI_CUTOFF,
        minifat_sector,
        1,  # MiniFAT 섹터 수
        ENDOFCHAIN,  # 첫 DIFAT 섹터
        0,  # DIFAT 섹터 수
    )
    difat = [0] + [FREESECT] * 108
    struct.pack_into("<109I", header, 76, *difat)

    ministream_padded = bytes(ministream) + b"\x00" * (
        ministream_sectors * _SECTOR_SIZE - len(ministream)
    )
    return bytes(header) + fat_bytes + dir_bytes + minifat_bytes + ministream_padded


def build_hwp5(paragraphs: Sequence[AnyItem], *, properties: int = 0x1) -> bytes:
    """bit0 set → DocInfo/Section0 압축. 다른 비트는 FileHeader 에만 반영."""
    images = collect_images(paragraphs)
    charts = collect_charts(paragraphs)
    lists = [p for p in paragraphs if isinstance(p, SynthListPara)]
    docinfo = build_docinfo(
        outline=has_heading(paragraphs), images=images, ole_count=len(charts), lists=lists
    )
    section0 = build_section0(paragraphs, images)
    if properties & 0x1:
        docinfo = compress_raw(docinfo)
        section0 = compress_raw(section0)
    streams = {
        "FileHeader": build_file_header(properties=properties),
        "DocInfo": docinfo,
        "BodyText/Section0": section0,
    }
    for k, img in enumerate(images, start=1):
        if img.missing:
            continue
        data = compress_raw(img.data) if properties & 0x1 else img.data
        streams[f"{_BINDATA_PREFIX}BIN{k:04X}.{img.ext}"] = data
    for k, chart in enumerate(charts, start=len(images) + 1):
        data = build_chart_ole(chart)
        streams[f"{_BINDATA_PREFIX}BIN{k:04X}.ole"] = (
            compress_raw(data) if properties & 0x1 else data
        )
    return build_cfb(streams)


def write_hwp5(path: Path, paragraphs: Sequence[AnyItem], *, properties: int = 0x1) -> Path:
    """부모 디렉터리 생성 후 바이트 저장, path 반환."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(build_hwp5(paragraphs, properties=properties))
    return path


# 공용 fixture (E2E·단위 테스트가 이 이름을 그대로 import)
FIXTURE_TABLE = SynthTable(
    rows=2,
    cols=2,
    cells=(
        SynthCell(("구분",), col=0, row=0),
        SynthCell(("내용",), col=1, row=0),
        SynthCell(("지원 규모",), col=0, row=1),
        SynthCell(("총 30억 원",), col=1, row=1),
    ),
)
FIXTURE_ITEMS_WITH_TABLE: list[Item] = ["표 앞 단락", FIXTURE_TABLE, "표 뒤 단락"]
EXPECTED_MARKDOWN_WITH_TABLE = (
    "표 앞 단락\n\n| 구분 | 내용 |\n|---|---|\n| 지원 규모 | 총 30억 원 |\n\n표 뒤 단락\n"
)
EXPECTED_BLOCKS_WITH_TABLE = [
    Paragraph("표 앞 단락"),
    Table([["구분", "내용"], ["지원 규모", "총 30억 원"]]),
    Paragraph("표 뒤 단락"),
]

FIXTURE_TABLE_MERGED = SynthTable(
    rows=2,
    cols=3,
    cells=(
        SynthCell(("머리글",), col=0, row=0, col_span=3),
        SynthCell(("가",), col=0, row=1),
        SynthCell(("나|다",), col=1, row=1),
        SynthCell(("라", "마"), col=2, row=1),
    ),
)
FIXTURE_ITEMS_MERGED: list[Item] = ["제목", FIXTURE_TABLE_MERGED]
EXPECTED_MARKDOWN_MERGED = "제목\n\n| 머리글 |  |  |\n|---|---|---|\n| 가 | 나\\|다 | 라<br>마 |\n"
EXPECTED_BLOCKS_MERGED = [Paragraph("제목"), Table([["머리글", "", ""], ["가", "나|다", "라\n마"]])]

FIXTURE_ITEMS_HEADINGS: list[Item] = [
    SynthHeading("문서 제목", 1),
    "본문 단락",
    SynthHeading("1. 사업 개요", 2),
    FIXTURE_TABLE,
    SynthHeading("가. 세부 내용", 3),
    "마지막 단락",
]
EXPECTED_MARKDOWN_HEADINGS = (
    "# 문서 제목\n\n본문 단락\n\n## 1. 사업 개요\n\n"
    "| 구분 | 내용 |\n|---|---|\n| 지원 규모 | 총 30억 원 |\n\n"
    "### 가. 세부 내용\n\n마지막 단락\n"
)
EXPECTED_BLOCKS_HEADINGS = [
    Paragraph("문서 제목", 1),
    Paragraph("본문 단락"),
    Paragraph("1. 사업 개요", 2),
    Table([["구분", "내용"], ["지원 규모", "총 30억 원"]]),
    Paragraph("가. 세부 내용", 3),
    Paragraph("마지막 단락"),
]
EXPECTED_COUNTS_HEADINGS = (2, 1, 3)  # (paragraph_count, table_count, heading_count)

FIXTURE_ITEMS_HEADING_EDGE: list[Item] = [
    SynthHeading("깊은 수준", 7),
    SynthHeading("", 1),
    SynthHeading("두 줄\n제목", 2),
    "본문",
]
EXPECTED_MARKDOWN_HEADING_EDGE = "###### 깊은 수준\n\n## 두 줄 제목\n\n본문\n"
EXPECTED_BLOCKS_HEADING_EDGE = [
    Paragraph("깊은 수준", 6),
    Paragraph("두 줄\n제목", 2),
    Paragraph("본문"),
]
EXPECTED_COUNTS_HEADING_EDGE = (1, 0, 2)

FIXTURE_ITEMS_HEADING_IN_CELL: list[Item] = [
    SynthHeading("표 제목", 1),
    SynthTable(
        rows=1,
        cols=2,
        cells=(
            SynthCell((SynthHeading("셀 제목", 2),), col=0, row=0),
            SynthCell(("값",), col=1, row=0),
        ),
    ),
]
EXPECTED_MARKDOWN_HEADING_IN_CELL = "# 표 제목\n\n| 셀 제목 | 값 |\n|---|---|\n"
EXPECTED_BLOCKS_HEADING_IN_CELL = [Paragraph("표 제목", 1), Table([["셀 제목", "값"]])]
EXPECTED_COUNTS_HEADING_IN_CELL = (0, 1, 1)

PNG_1X1: bytes = bytes.fromhex(
    "89504e470d0a1a0a0000000d4948445200000001000000010802000000907753de"
    "0000000c4944415478da63f8cfc0000003010100f70341430000000049454e44ae426082"
)  # 69 bytes, 1×1 RGB PNG
JPEG_STUB: bytes = b"\xff\xd8\xff\xe0" + bytes(range(16)) + b"\xff\xd9"  # 22 bytes, 유효 JPEG 아님
FIXTURE_IMAGE_PNG = SynthImage(PNG_1X1, "png")
HEADER_IMAGE = SynthImage(PNG_1X1, "png")  # SynthHeaderFooter(with_image=True) 안의 그림
TEXTBOX_IMAGE = SynthImage(PNG_1X1, "png")  # SynthTextBox(with_image=True) 안의 그림
FIXTURE_IMAGE_JPG = SynthImage(JPEG_STUB, "jpg")

# 모든 EXPECTED_MARKDOWN_IMAGE* 는 입력 파일 stem 이 "doc" 일 때(doc.hwp / doc.hwpx → doc_images/)
FIXTURE_ITEMS_IMAGES: list[Item] = [
    "그림 앞 단락",
    FIXTURE_IMAGE_PNG,
    SynthHeading("1. 결과", 2),
    FIXTURE_IMAGE_JPG,
    "그림 뒤 단락",
]
EXPECTED_BLOCKS_IMAGES = [
    Paragraph("그림 앞 단락"),
    Image("img_001.png", PNG_1X1),
    Paragraph("1. 결과", 2),
    Image("img_002.jpg", JPEG_STUB),
    Paragraph("그림 뒤 단락"),
]
EXPECTED_MARKDOWN_IMAGES = (
    "그림 앞 단락\n\n![그림 1](doc_images/img_001.png)\n\n## 1. 결과\n\n"
    "![그림 2](doc_images/img_002.jpg)\n\n그림 뒤 단락\n"
)
EXPECTED_COUNTS_IMAGES = (2, 0, 1, 2)  # (paragraph, table, heading, image)
EXPECTED_IMAGE_FILES_IMAGES = ("img_001.png", "img_002.jpg")

FIXTURE_ITEMS_IMAGE_REUSE: list[Item] = [FIXTURE_IMAGE_PNG, "중간 단락", FIXTURE_IMAGE_PNG]
EXPECTED_BLOCKS_IMAGE_REUSE = [
    Image("img_001.png", PNG_1X1),
    Paragraph("중간 단락"),
    Image("img_001.png", PNG_1X1),
]
EXPECTED_MARKDOWN_IMAGE_REUSE = (
    "![그림 1](doc_images/img_001.png)\n\n중간 단락\n\n![그림 2](doc_images/img_001.png)\n"
)
EXPECTED_COUNTS_IMAGE_REUSE = (1, 0, 0, 2)
EXPECTED_IMAGE_FILES_IMAGE_REUSE = ("img_001.png",)

FIXTURE_ITEMS_IMAGE_IN_CELL: list[Item] = [
    SynthTable(
        rows=1,
        cols=2,
        cells=(
            SynthCell((FIXTURE_IMAGE_JPG, "값"), col=0, row=0),
            SynthCell(("나",), col=1, row=0),
        ),
    ),
    FIXTURE_IMAGE_PNG,
]  # 바이너리 항목: 1 = JPG(셀), 2 = PNG. 셀 이미지는 해석되지 않으므로 PNG 가 img_001
EXPECTED_BLOCKS_IMAGE_IN_CELL = [Table([["값", "나"]]), Image("img_001.png", PNG_1X1)]
EXPECTED_MARKDOWN_IMAGE_IN_CELL = "| 값 | 나 |\n|---|---|\n\n![그림 1](doc_images/img_001.png)\n"
EXPECTED_COUNTS_IMAGE_IN_CELL = (0, 1, 0, 1)
EXPECTED_IMAGE_FILES_IMAGE_IN_CELL = ("img_001.png",)

FIXTURE_ITEMS_IMAGE_MISSING: list[Item] = [
    "앞",
    SynthImage(b"", "png", missing=True),
    FIXTURE_IMAGE_PNG,
    "뒤",
]
EXPECTED_BLOCKS_IMAGE_MISSING = [Paragraph("앞"), Image("img_001.png", PNG_1X1), Paragraph("뒤")]
EXPECTED_MARKDOWN_IMAGE_MISSING = "앞\n\n![그림 1](doc_images/img_001.png)\n\n뒤\n"
EXPECTED_COUNTS_IMAGE_MISSING = (2, 0, 0, 1)
EXPECTED_IMAGE_FILES_IMAGE_MISSING = ("img_001.png",)

# (items, blocks, markdown, counts, files). ids ["images", "reuse", "in_cell", "missing"]
IMAGE_FIXTURES = [
    (
        FIXTURE_ITEMS_IMAGES,
        EXPECTED_BLOCKS_IMAGES,
        EXPECTED_MARKDOWN_IMAGES,
        EXPECTED_COUNTS_IMAGES,
        EXPECTED_IMAGE_FILES_IMAGES,
    ),
    (
        FIXTURE_ITEMS_IMAGE_REUSE,
        EXPECTED_BLOCKS_IMAGE_REUSE,
        EXPECTED_MARKDOWN_IMAGE_REUSE,
        EXPECTED_COUNTS_IMAGE_REUSE,
        EXPECTED_IMAGE_FILES_IMAGE_REUSE,
    ),
    (
        FIXTURE_ITEMS_IMAGE_IN_CELL,
        EXPECTED_BLOCKS_IMAGE_IN_CELL,
        EXPECTED_MARKDOWN_IMAGE_IN_CELL,
        EXPECTED_COUNTS_IMAGE_IN_CELL,
        EXPECTED_IMAGE_FILES_IMAGE_IN_CELL,
    ),
    (
        FIXTURE_ITEMS_IMAGE_MISSING,
        EXPECTED_BLOCKS_IMAGE_MISSING,
        EXPECTED_MARKDOWN_IMAGE_MISSING,
        EXPECTED_COUNTS_IMAGE_MISSING,
        EXPECTED_IMAGE_FILES_IMAGE_MISSING,
    ),
]
