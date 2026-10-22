import hashlib
import struct
import zlib
from pathlib import Path

import olefile
import pytest

from hwp2md.blocks import Paragraph, Table
from hwp2md.hwp5.body import parse_blocks
from hwp2md.hwp5.reader import read_blocks, read_sections
from hwp2md.hwp5.records import (
    HWPTAG_CTRL_HEADER,
    HWPTAG_LIST_HEADER,
    HWPTAG_PARA_HEADER,
    HWPTAG_PARA_TEXT,
    HWPTAG_TABLE,
    Record,
    decode_para_text,
    iter_records,
)
from synth_hwp5 import (
    EXPECTED_BLOCKS_MERGED,
    EXPECTED_BLOCKS_WITH_TABLE,
    FIXTURE_ITEMS_HEADING_IN_CELL,
    FIXTURE_ITEMS_HEADINGS,
    FIXTURE_ITEMS_MERGED,
    FIXTURE_ITEMS_WITH_TABLE,
    FIXTURE_PARAGRAPHS,
    HWP5_SIGNATURE,
    build_cfb,
    build_docinfo,
    build_file_header,
    build_hwp5,
    build_section0,
    has_heading,
    write_hwp5,
)


def _read_stream(path: Path, name: str) -> bytes:
    ole = olefile.OleFileIO(str(path))
    try:
        return bytes(ole.openstream(name).read())
    finally:
        ole.close()


def _inflate(data: bytes) -> bytes:
    d = zlib.decompressobj(-15)
    return d.decompress(data) + d.flush()


def test_build_file_header_layout() -> None:
    header = build_file_header()
    assert len(header) == 256
    assert header[:32] == HWP5_SIGNATURE
    assert header[32:36] == struct.pack("<I", 0x05000300)
    assert header[36:40] == b"\x01\x00\x00\x00"
    assert header[40:] == b"\x00" * 216


def test_write_hwp5_is_ole_with_expected_streams(tmp_path: Path) -> None:
    path = write_hwp5(tmp_path / "sub" / "sample.hwp", FIXTURE_PARAGRAPHS)
    assert path == tmp_path / "sub" / "sample.hwp"
    assert olefile.isOleFile(str(path))
    ole = olefile.OleFileIO(str(path))
    try:
        assert sorted(ole.listdir()) == [["BodyText", "Section0"], ["DocInfo"], ["FileHeader"]]
    finally:
        ole.close()


def test_file_header_stream_is_256_bytes(tmp_path: Path) -> None:
    path = write_hwp5(tmp_path / "sample.hwp", FIXTURE_PARAGRAPHS)
    raw = _read_stream(path, "FileHeader")
    assert len(raw) == 256
    assert raw == build_file_header()


def test_section0_round_trips_paragraphs(tmp_path: Path) -> None:
    path = write_hwp5(tmp_path / "sample.hwp", FIXTURE_PARAGRAPHS)
    section = _inflate(_read_stream(path, "BodyText/Section0"))
    texts = [r for r in iter_records(section) if r.tag_id == HWPTAG_PARA_TEXT]
    assert len(texts) == 4
    assert [decode_para_text(r.payload) for r in texts] == [p.strip() for p in FIXTURE_PARAGRAPHS]


def test_only_last_para_header_has_last_bit(tmp_path: Path) -> None:
    path = write_hwp5(tmp_path / "sample.hwp", FIXTURE_PARAGRAPHS)
    section = _inflate(_read_stream(path, "BodyText/Section0"))
    headers = [r for r in iter_records(section) if r.tag_id == HWPTAG_PARA_HEADER]
    assert len(headers) == 4
    nchars = [struct.unpack_from("<I", r.payload)[0] for r in headers]
    assert all(len(r.payload) == 22 for r in headers)
    assert [bool(n & 0x80000000) for n in nchars] == [False, False, False, True]
    expected = [len(p.encode("utf-16-le")) // 2 + 1 for p in FIXTURE_PARAGRAPHS]
    assert [n & 0x7FFFFFFF for n in nchars] == expected


def test_uncompressed_section_when_properties_zero(tmp_path: Path) -> None:
    path = write_hwp5(tmp_path / "plain.hwp", FIXTURE_PARAGRAPHS, properties=0)
    assert _read_stream(path, "FileHeader")[36:40] == b"\x00\x00\x00\x00"
    section = _read_stream(path, "BodyText/Section0")
    texts = [
        decode_para_text(r.payload) for r in iter_records(section) if r.tag_id == HWPTAG_PARA_TEXT
    ]
    assert texts == [p.strip() for p in FIXTURE_PARAGRAPHS]


def test_build_cfb_rejects_stream_of_4096_bytes_or_more() -> None:
    streams = {
        "FileHeader": build_file_header(),
        "DocInfo": b"",
        "BodyText/Section0": b"\x00" * 4096,
    }
    with pytest.raises(ValueError):
        build_cfb(streams)


def test_build_hwp5_rejects_oversized_uncompressed_section() -> None:
    long_paragraphs = ["가" * 3000]
    with pytest.raises(ValueError):
        build_hwp5(long_paragraphs, properties=0)


# BASE(4f1b92f) 버전 build_section0(FIXTURE_PARAGRAPHS) 의 sha256
_BASE_PLAIN_SECTION_SHA256 = "5ff234b19bad734ca9812e68b8c44d55a83faeec9dd3eb19ba4d191115b49fb6"


def _round_trip(path: Path) -> list[object]:
    blocks: list[object] = []
    for section in read_sections(path):
        blocks.extend(parse_blocks(iter_records(section)))
    return blocks


def _table_records() -> list[Record]:
    return list(iter_records(build_section0(FIXTURE_ITEMS_WITH_TABLE)))


def test_table_fixture_round_trips_to_blocks(tmp_path: Path) -> None:
    path = write_hwp5(tmp_path / "table.hwp", FIXTURE_ITEMS_WITH_TABLE)
    assert _round_trip(path) == EXPECTED_BLOCKS_WITH_TABLE


def test_merged_table_fixture_round_trips_to_blocks(tmp_path: Path) -> None:
    path = write_hwp5(tmp_path / "merged.hwp", FIXTURE_ITEMS_MERGED)
    assert _round_trip(path) == EXPECTED_BLOCKS_MERGED


def test_table_control_record_layout() -> None:
    recs = _table_records()
    ctrl = [r for r in recs if r.tag_id == HWPTAG_CTRL_HEADER]
    assert len(ctrl) == 1
    assert ctrl[0].payload[:4] == b" lbt"
    assert len(ctrl[0].payload) == 44
    assert ctrl[0].level == 1
    tables = [r for r in recs if r.tag_id == HWPTAG_TABLE]
    assert len(tables) == 1
    assert tables[0].level == 2
    assert len(tables[0].payload) == 18 + 2 * 2 + 4
    assert struct.unpack_from("<HH", tables[0].payload, 4) == (2, 2)
    cells = [r for r in recs if r.tag_id == HWPTAG_LIST_HEADER]
    assert len(cells) == 4
    assert all(r.level == 2 and len(r.payload) == 38 for r in cells)
    coords = [struct.unpack_from("<HHHH", r.payload, 8) for r in cells]
    assert coords == [(0, 0, 1, 1), (1, 0, 1, 1), (0, 1, 1, 1), (1, 1, 1, 1)]


def test_table_placeholder_paragraph() -> None:
    recs = _table_records()
    ctrl_index = next(i for i, r in enumerate(recs) if r.tag_id == HWPTAG_CTRL_HEADER)
    header_index = max(
        i
        for i, r in enumerate(recs[:ctrl_index])
        if r.tag_id == HWPTAG_PARA_HEADER and r.level == 0
    )
    header = recs[header_index]
    text = recs[header_index + 1]
    assert text.tag_id == HWPTAG_PARA_TEXT
    assert text.level == 1
    assert struct.unpack_from("<H", text.payload)[0] == 11
    assert decode_para_text(text.payload) == ""
    nchars, control_mask = struct.unpack_from("<II", header.payload)
    assert nchars & 0x7FFFFFFF == 9
    assert len(text.payload) // 2 == 9
    assert control_mask == 0x800


def test_cell_paragraph_levels_and_last_bit() -> None:
    recs = list(iter_records(build_section0(FIXTURE_ITEMS_MERGED)))
    ctrl_index = next(i for i, r in enumerate(recs) if r.tag_id == HWPTAG_CTRL_HEADER)
    cell_recs = recs[ctrl_index + 1 :]
    cell_headers = [r for r in cell_recs if r.tag_id == HWPTAG_PARA_HEADER]
    cell_texts = [r for r in cell_recs if r.tag_id == HWPTAG_PARA_TEXT]
    assert len(cell_headers) == 5
    assert all(r.level == 2 for r in cell_headers)
    assert all(r.level == 3 for r in cell_texts)
    texts = [decode_para_text(r.payload) for r in cell_texts]
    assert texts == ["머리글", "가", "나|다", "라", "마"]
    last_bits = [bool(struct.unpack_from("<I", r.payload)[0] & 0x80000000) for r in cell_headers]
    assert last_bits == [True, True, True, False, True]


def test_table_fixture_uncompressed_variant(tmp_path: Path) -> None:
    path = write_hwp5(tmp_path / "plain.hwp", FIXTURE_ITEMS_WITH_TABLE, properties=0)
    assert _read_stream(path, "FileHeader")[36:40] == b"\x00\x00\x00\x00"
    assert _round_trip(path) == EXPECTED_BLOCKS_WITH_TABLE


def test_plain_fixture_has_no_table_records() -> None:
    section = build_section0(FIXTURE_PARAGRAPHS)
    assert hashlib.sha256(section).hexdigest() == _BASE_PLAIN_SECTION_SHA256
    recs = list(iter_records(section))
    table_tags = {HWPTAG_CTRL_HEADER, HWPTAG_TABLE, HWPTAG_LIST_HEADER}
    assert [r for r in recs if r.tag_id in table_tags] == []
    assert all(r.level == (0 if r.tag_id == HWPTAG_PARA_HEADER else 1) for r in recs)


_BASE_DOCINFO_SHA256 = "39f61ef96a725101222bf887e50fcaac3c9b9c80c3610caa593c582870d031d4"


def test_docinfo_default_unchanged() -> None:
    docinfo = build_docinfo()
    assert docinfo == build_docinfo(outline=False)
    assert len(docinfo) == 30
    assert hashlib.sha256(docinfo).hexdigest() == _BASE_DOCINFO_SHA256
    assert [r.tag_id for r in iter_records(docinfo)] == [0x10]


def test_docinfo_outline_records() -> None:
    recs = list(iter_records(build_docinfo(outline=True)))
    assert [r.tag_id for r in recs] == [0x10] + [0x19] * 8 + [0x1A] * 8
    shapes = [r for r in recs if r.tag_id == 0x19]
    assert all(len(r.payload) == 54 for r in shapes)
    attrs = [struct.unpack_from("<I", r.payload, 0)[0] for r in shapes]
    assert attrs[0] == 0
    for lv in range(1, 8):
        assert attrs[lv] == (1 << 23) | ((lv - 1) << 25)


def test_style_record_layout() -> None:
    styles = [r for r in iter_records(build_docinfo(outline=True)) if r.tag_id == 0x1A]
    payload = styles[2].payload
    assert len(payload) == 40
    off = 0
    (n1,) = struct.unpack_from("<H", payload, off)
    off += 2
    ko = payload[off : off + 2 * n1].decode("utf-16-le")
    off += 2 * n1
    (n2,) = struct.unpack_from("<H", payload, off)
    off += 2
    en = payload[off : off + 2 * n2].decode("utf-16-le")
    off += 2 * n2
    attr, next_id, lang, para_shape_id, char_shape_id, zero = struct.unpack_from(
        "<BBhHHH", payload, off
    )
    assert ko == "개요 2"
    assert en == "Outline 2"
    assert (attr, next_id, lang) == (0, 2, 1042)
    assert para_shape_id == 2
    assert (char_shape_id, zero) == (0, 0)


def _header_ids(section: bytes, level: int) -> list[tuple[int, int]]:
    heads = [
        r for r in iter_records(section) if r.tag_id == HWPTAG_PARA_HEADER and r.level == level
    ]
    assert all(len(r.payload) == 22 for r in heads)
    return [(struct.unpack_from("<H", r.payload, 8)[0], r.payload[10]) for r in heads]


def test_heading_paragraph_header_ids() -> None:
    section = build_section0(FIXTURE_ITEMS_HEADINGS)
    assert _header_ids(section, 0) == [(1, 1), (0, 0), (2, 2), (0, 0), (3, 3), (0, 0)]


def test_cell_heading_paragraph_header_ids() -> None:
    section = build_section0(FIXTURE_ITEMS_HEADING_IN_CELL)
    assert _header_ids(section, 2) == [(2, 2), (0, 0)]


@pytest.mark.parametrize(
    ("items", "properties", "expected"),
    [
        (
            FIXTURE_PARAGRAPHS,
            0x1,
            "8e17f5de3eabea84e476d13d0e5dc993e629de8597d850b75921ad37c05b8b4b",
        ),
        (
            FIXTURE_PARAGRAPHS,
            0,
            "50f3b370aa8f41c2ccc8ca961500567a956de10baebe4bb957b8848a1980b030",
        ),
        (
            FIXTURE_ITEMS_WITH_TABLE,
            0x1,
            "b3635fb47a3412ca763b8491d9b61e8e8eb400d7950292a0dc500df201ffd7ee",
        ),
        (
            FIXTURE_ITEMS_WITH_TABLE,
            0,
            "93121aecd08248f24ac247473cd0ec96348eb28b832d2dc2a670d7ec3da4a689",
        ),
        (
            FIXTURE_ITEMS_MERGED,
            0x1,
            "223eb106e7f43245822cc178f919abba72d2a45e42fa386d4cf6e38b4796d33e",
        ),
        (
            FIXTURE_ITEMS_MERGED,
            0,
            "bb8c92ff627fbca29984d7371c9db1c0cb98bfbe08cfec250a03d69ec03ad097",
        ),
    ],
)
def test_fixture_bytes_unchanged_sha256(items: list, properties: int, expected: str) -> None:
    assert hashlib.sha256(build_hwp5(items, properties=properties)).hexdigest() == expected


def test_has_heading() -> None:
    assert has_heading(FIXTURE_ITEMS_HEADING_IN_CELL) is True
    assert has_heading(FIXTURE_ITEMS_HEADINGS) is True
    assert has_heading(FIXTURE_ITEMS_WITH_TABLE) is False
    assert has_heading(FIXTURE_PARAGRAPHS) is False


def test_heading_fixture_round_trips_text(tmp_path: Path) -> None:
    blocks = read_blocks(write_hwp5(tmp_path / "h.hwp", FIXTURE_ITEMS_HEADINGS))
    texts = [b.text for b in blocks if isinstance(b, Paragraph)]
    assert texts == ["문서 제목", "본문 단락", "1. 사업 개요", "가. 세부 내용", "마지막 단락"]
    tables = [b for b in blocks if isinstance(b, Table)]
    assert tables == [Table([["구분", "내용"], ["지원 규모", "총 30억 원"]])]
