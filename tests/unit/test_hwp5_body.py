import struct

import pytest

from hwp2md.blocks import Block, Paragraph, Table
from hwp2md.errors import Hwp2mdError
from hwp2md.hwp5.body import (
    CellHeader,
    TableHeader,
    parse_blocks,
    parse_cell_header,
    parse_table_header,
)
from hwp2md.hwp5.records import (
    CTRL_ID_TABLE,
    HWPTAG_CTRL_HEADER,
    HWPTAG_LIST_HEADER,
    HWPTAG_PARA_CHAR_SHAPE,
    HWPTAG_PARA_HEADER,
    HWPTAG_PARA_LINE_SEG,
    HWPTAG_PARA_TEXT,
    HWPTAG_TABLE,
    Record,
)

Cell = tuple[int, int, int, int, list[str]]  # col, row, col_span, row_span, 단락들


def _wchars(*codes: int) -> bytes:
    return b"".join(struct.pack("<H", c) for c in codes)


def _text_payload(text: str, *, placeholder: bool = False) -> bytes:
    body = text.encode("utf-16-le")
    if placeholder:
        # 확장 컨트롤 11 + ctrl_id 2 WCHAR + 0×4 + 11 = 8 WCHAR
        body += struct.pack("<H", 11) + CTRL_ID_TABLE + b"\x00" * 8 + struct.pack("<H", 11)
    return body + _wchars(13)


def _para(text: str, level: int) -> list[Record]:
    return [
        Record(HWPTAG_PARA_HEADER, level, b"\x00" * 22),
        Record(HWPTAG_PARA_TEXT, level + 1, _text_payload(text)),
        Record(HWPTAG_PARA_CHAR_SHAPE, level + 1, b"\x00" * 8),
        Record(HWPTAG_PARA_LINE_SEG, level + 1, b"\x00" * 36),
    ]


def _table_payload(rows: int, cols: int) -> bytes:
    return struct.pack("<IHHH", 0x04000006, rows, cols, 0) + b"\x8d\x00" * 4 + b"\x00\x00"


def _cell_payload(col: int, row: int, col_span: int, row_span: int, n: int) -> bytes:
    return struct.pack("<HHIHHHH", n, 0, 0x20, col, row, col_span, row_span) + b"\x00" * 22


def _table_ctrl(
    rows: int, cols: int, cells: list[Cell], level: int, *, with_table: bool = True
) -> list[Record]:
    """CTRL_HEADER(tbl) at level, TABLE/LIST_HEADER/셀 단락 at level+1."""
    out = [Record(HWPTAG_CTRL_HEADER, level, CTRL_ID_TABLE + b"\x00" * 40)]
    if with_table:
        out.append(Record(HWPTAG_TABLE, level + 1, _table_payload(rows, cols)))
    for col, row, cs, rs, paras in cells:
        out.append(
            Record(HWPTAG_LIST_HEADER, level + 1, _cell_payload(col, row, cs, rs, len(paras)))
        )
        for p in paras:
            out.extend(_para(p, level + 1))
    return out


def _table_para(
    rows: int,
    cols: int,
    cells: list[Cell],
    *,
    text: str = "",
    level: int = 0,
    with_table: bool = True,
) -> list[Record]:
    head = [
        Record(HWPTAG_PARA_HEADER, level, struct.pack("<II", 9, 0x800) + b"\x00" * 14),
        Record(HWPTAG_PARA_TEXT, level + 1, _text_payload(text, placeholder=True)),
        Record(HWPTAG_PARA_CHAR_SHAPE, level + 1, b"\x00" * 8),
        Record(HWPTAG_PARA_LINE_SEG, level + 1, b"\x00" * 36),
    ]
    return head + _table_ctrl(rows, cols, cells, level + 1, with_table=with_table)


GRID_2X2: list[Cell] = [
    (0, 0, 1, 1, ["a"]),
    (1, 0, 1, 1, ["b"]),
    (0, 1, 1, 1, ["c"]),
    (1, 1, 1, 1, ["d"]),
]


def test_parse_table_header_real_hex() -> None:
    payload = bytes.fromhex("060000040100010000008d008d008d008d0001000100")
    assert parse_table_header(payload) == TableHeader(row_count=1, col_count=1)


def test_parse_table_header_truncated() -> None:
    with pytest.raises(Hwp2mdError, match=r"truncated TABLE record"):
        parse_table_header(b"\x00" * 7)


def test_parse_cell_header_real_hex() -> None:
    first = bytes.fromhex(
        "01000000200000050000000001000100f3580000fe0a00008d008d008d008d000100f3580000"
    )
    assert parse_cell_header(first) == CellHeader(col=0, row=0, col_span=1, row_span=1)
    merged = bytes.fromhex(
        "010000002000000502000100040001004a750000b50b00008d008d008d008d0006004a750000"
    )
    assert parse_cell_header(merged) == CellHeader(col=2, row=1, col_span=4, row_span=1)


def test_parse_cell_header_truncated() -> None:
    with pytest.raises(Hwp2mdError, match=r"truncated LIST_HEADER record"):
        parse_cell_header(b"\x00" * 15)


def test_parse_blocks_table_between_paragraphs() -> None:
    recs = _para("앞", 0) + _table_para(2, 2, GRID_2X2) + _para("뒤", 0)
    expected: list[Block] = [
        Paragraph("앞"),
        Table([["a", "b"], ["c", "d"]]),
        Paragraph("뒤"),
    ]
    assert parse_blocks(recs) == expected
    table = parse_blocks(recs)[1]
    assert isinstance(table, Table)
    assert (table.row_count, table.col_count) == (2, 2)


def test_parse_blocks_empty_placeholder_yields_table_only() -> None:
    blocks = parse_blocks(_table_para(2, 2, GRID_2X2))
    assert blocks == [Table([["a", "b"], ["c", "d"]])]


def test_parse_blocks_placeholder_text_before_table() -> None:
    blocks = parse_blocks(_table_para(2, 2, GRID_2X2, text="표 설명"))
    assert blocks == [Paragraph("표 설명"), Table([["a", "b"], ["c", "d"]])]


def test_parse_blocks_cell_paragraphs_joined_skip_empty() -> None:
    cells: list[Cell] = [(0, 0, 1, 1, ["첫", "", "둘"])]
    assert parse_blocks(_table_para(1, 1, cells)) == [Table([["첫\n둘"]])]


def test_parse_blocks_merged_cells() -> None:
    cells: list[Cell] = [
        (0, 0, 3, 1, ["머리글"]),
        (0, 1, 1, 1, ["가"]),
        (1, 1, 1, 1, ["나"]),
        (2, 1, 1, 1, ["다"]),
    ]
    assert parse_blocks(_table_para(2, 3, cells)) == [
        Table([["머리글", "", ""], ["가", "나", "다"]])
    ]


def test_parse_blocks_out_of_range_cell_goes_to_first_empty_slot() -> None:
    cells: list[Cell] = [(0, 0, 1, 1, ["a"]), (9, 9, 1, 1, ["x"])]
    assert parse_blocks(_table_para(2, 2, cells)) == [Table([["a", "x"], ["", ""]])]


def test_parse_blocks_table_ctrl_without_table_record() -> None:
    assert parse_blocks(_table_para(2, 2, GRID_2X2, with_table=False)) == []


def test_parse_blocks_ignores_non_table_ctrl_children() -> None:
    head = [
        Record(HWPTAG_PARA_HEADER, 0, b"\x00" * 22),
        Record(HWPTAG_PARA_TEXT, 1, _text_payload("본문")),
        Record(HWPTAG_CTRL_HEADER, 1, b"dces" + b"\x00" * 8),
        Record(0x49, 2, b"\x00" * 40),
        Record(0x4A, 2, b"\x00" * 20),
        Record(0x4B, 2, b"\x00" * 10),
    ]
    assert parse_blocks(head + _para("다음", 0)) == [Paragraph("본문"), Paragraph("다음")]


def test_parse_blocks_non_table_ctrl_paragraph_flows_out() -> None:
    recs = (
        [
            Record(HWPTAG_PARA_HEADER, 0, b"\x00" * 22),
            Record(HWPTAG_PARA_TEXT, 1, _text_payload("바깥")),
            Record(HWPTAG_CTRL_HEADER, 1, b"xobt" + b"\x00" * 8),
            Record(HWPTAG_LIST_HEADER, 2, b"\x00" * 16),
        ]
        + _para("안쪽", 2)
        + _para("끝", 0)
    )
    assert parse_blocks(recs) == [Paragraph("바깥"), Paragraph("안쪽"), Paragraph("끝")]


def test_parse_blocks_nested_table_flattened() -> None:
    # 셀 단락(level 2) 안에 표 컨트롤(level 3)
    inner_cell_para = _table_para(1, 2, [(0, 0, 1, 1, ["x"]), (1, 0, 1, 1, ["y"])], level=2)
    recs = [
        Record(HWPTAG_PARA_HEADER, 0, b"\x00" * 22),
        Record(HWPTAG_PARA_TEXT, 1, _text_payload("", placeholder=True)),
        Record(HWPTAG_CTRL_HEADER, 1, CTRL_ID_TABLE + b"\x00" * 40),
        Record(HWPTAG_TABLE, 2, _table_payload(1, 2)),
        Record(HWPTAG_LIST_HEADER, 2, _cell_payload(0, 0, 1, 1, 2)),
        *_para("부모", 2),
        *inner_cell_para,
        Record(HWPTAG_LIST_HEADER, 2, _cell_payload(1, 0, 1, 1, 1)),
        *_para("옆", 2),
    ]
    blocks = parse_blocks(recs)
    assert blocks == [Table([["부모\nx y", "옆"]])]
    assert sum(isinstance(b, Table) for b in blocks) == 1
