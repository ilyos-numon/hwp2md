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

from hwp2md.blocks import Paragraph, Table
from hwp2md.hwp5.records import (
    CTRL_ID_TABLE,
    HWPTAG_CTRL_HEADER,
    HWPTAG_DOCUMENT_PROPERTIES,
    HWPTAG_LIST_HEADER,
    HWPTAG_PARA_CHAR_SHAPE,
    HWPTAG_PARA_HEADER,
    HWPTAG_PARA_LINE_SEG,
    HWPTAG_PARA_TEXT,
    HWPTAG_TABLE,
)

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
class SynthCell:
    paragraphs: tuple[str, ...]
    col: int
    row: int
    col_span: int = 1
    row_span: int = 1


@dataclass(frozen=True)
class SynthTable:
    rows: int
    cols: int
    cells: tuple[SynthCell, ...]


Item = str | SynthTable


def build_paragraph(text: str, *, last: bool, level: int = 0) -> bytes:
    """§4.4-D/E: PARA_HEADER(level), PARA_TEXT·PARA_CHAR_SHAPE·PARA_LINE_SEG(level+1)."""
    text_bytes = text.encode("utf-16-le")
    nchars = len(text_bytes) // 2 + 1
    if last:
        nchars |= _LAST_PARA_BIT
    para_header = struct.pack("<IIHBBHHHI", nchars, 0, 0, 0, 0, 1, 0, 1, 0)
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


def build_table_control(table: SynthTable, *, level: int, last: bool) -> bytes:
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
        for i, text in enumerate(cell.paragraphs):
            out += build_paragraph(text, last=(i == last_index), level=level + 2)
    return out


def build_section0(items: Sequence[Item]) -> bytes:
    """미압축 섹션. str → 본문 단락, SynthTable → 표 컨트롤. 마지막 원소만 last=True."""
    last_index = len(items) - 1
    return b"".join(
        build_table_control(item, level=0, last=(i == last_index))
        if isinstance(item, SynthTable)
        else build_paragraph(item, last=(i == last_index))
        for i, item in enumerate(items)
    )


def build_docinfo() -> bytes:
    """미압축 DocInfo, §4.4-F."""
    payload = struct.pack("<7HIII", 1, 1, 1, 1, 1, 1, 1, 0, 0, 0)
    return build_record(HWPTAG_DOCUMENT_PROPERTIES, 0, payload)


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
    """키: "FileHeader", "DocInfo", "BodyText/Section0" 정확히 3개. §4.4-G (v3, 512-byte 섹터)."""
    if set(streams) != set(_STREAM_KEYS):
        raise ValueError(f"streams must have exactly the keys {sorted(_STREAM_KEYS)}")
    for key, data in streams.items():
        if len(data) >= _MINI_CUTOFF:
            raise ValueError(f"stream {key!r} is {len(data)} bytes; fixture supports < 4096")

    # 미니스트림 배치 + MiniFAT
    ministream = bytearray()
    minifat: list[int] = []
    mini_start: dict[str, int] = {}
    for key in _STREAM_KEYS:
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

    entries_count = 5
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


def build_hwp5(paragraphs: Sequence[Item], *, properties: int = 0x1) -> bytes:
    """bit0 set → DocInfo/Section0 압축. 다른 비트는 FileHeader 에만 반영."""
    docinfo = build_docinfo()
    section0 = build_section0(paragraphs)
    if properties & 0x1:
        docinfo = compress_raw(docinfo)
        section0 = compress_raw(section0)
    return build_cfb(
        {
            "FileHeader": build_file_header(properties=properties),
            "DocInfo": docinfo,
            "BodyText/Section0": section0,
        }
    )


def write_hwp5(path: Path, paragraphs: Sequence[Item], *, properties: int = 0x1) -> Path:
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
