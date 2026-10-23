"""HWP 5.0 개체: 표 칸 그림, 캡션, 글상자·묶음, OLE·차트, 글맵시, 그림 참조 건너뜀."""

import struct
from pathlib import Path

import pytest

from hwp2md.blocks import Image, Paragraph, Table, make_table
from hwp2md.convert import convert
from hwp2md.hwp5.body import ReadContext, parse_blocks, parse_ole_bindata_id
from hwp2md.hwp5.docinfo import BinDataEntry, DocInfo
from hwp2md.hwp5.reader import BinDataStore, read_blocks
from hwp2md.hwp5.records import (
    CTRL_ID_GSO,
    CTRL_ID_TABLE,
    HWPTAG_CTRL_HEADER,
    HWPTAG_LIST_HEADER,
    HWPTAG_PARA_HEADER,
    HWPTAG_PARA_TEXT,
    HWPTAG_SHAPE_COMPONENT,
    HWPTAG_SHAPE_COMPONENT_OLE,
    HWPTAG_SHAPE_COMPONENT_PICTURE,
    HWPTAG_SHAPE_COMPONENT_TEXTART,
    HWPTAG_TABLE,
    Record,
)
from hwp2md.skips import SkipCounter
from synth_hwp5 import (
    FIXTURE_IMAGE_PNG,
    FIXTURE_ITEMS_IMAGE_IN_CELL,
    FIXTURE_ITEMS_IMAGE_MISSING,
    JPEG_STUB,
    PNG_1X1,
    SynthCell,
    SynthTable,
    build_hwp5,
    build_picture_record,
    write_hwp5,
)
from synth_items import EXT_FIXTURES, EXT_IDS_BY_STAGE, SynthCaptionedTable, SynthTextBox

OBJECT_IDS = [*EXT_IDS_BY_STAGE["objects"], "header_image"]
PNG_FILES = {"textbox": ("img_001.png",)}

CHID_CON = b"$con"[::-1]
CHID_REC = b"$rec"[::-1]
CHID_PIC = b"$pic"[::-1]
HWPTAG_SHAPE_COMPONENT_CONTAINER = 0x56


@pytest.mark.parametrize("fixture_id", OBJECT_IDS)
def test_object_ext_fixtures_markdown_and_skipped(fixture_id: str, tmp_path: Path) -> None:
    items, expected_md, expected_skipped = EXT_FIXTURES[fixture_id]
    src = write_hwp5(tmp_path / "doc.hwp", items)  # type: ignore[arg-type]
    result = convert(src, tmp_path / "out")
    assert result.markdown == expected_md
    assert result.skipped == expected_skipped
    assert tuple(p.name for p in result.image_files) == PNG_FILES.get(fixture_id, ())


def test_object_fixture_ids_are_four() -> None:
    assert EXT_IDS_BY_STAGE["objects"] == ["textbox", "caption", "chart", "chart_legacy"]


def test_cell_image_consumes_number_in_document_order(tmp_path: Path) -> None:
    src = write_hwp5(tmp_path / "doc.hwp", FIXTURE_ITEMS_IMAGE_IN_CELL)
    jpg = Image("img_001.jpg", JPEG_STUB)
    png = Image("img_002.png", PNG_1X1)
    assert read_blocks(src) == [make_table([[[jpg, "\n", "값"], ["나"]]]), png]
    result = convert(src, tmp_path / "out")
    assert result.markdown == (
        "| ![그림 1](doc_images/img_001.jpg)<br>값 | 나 |\n|---|---|\n\n"
        "![그림 2](doc_images/img_002.png)\n"
    )
    assert result.image_count == 2
    assert tuple(p.name for p in result.image_files) == ("img_001.jpg", "img_002.png")


def test_cell_text_and_image_in_one_cell_paragraph_order() -> None:
    table = SynthTable(
        rows=1,
        cols=1,
        cells=(SynthCell(("앞", FIXTURE_IMAGE_PNG, "뒤"), col=0, row=0),),
    )
    blocks = read_blocks(build_hwp5([table]))
    img = Image("img_001.png", PNG_1X1)
    assert blocks == [make_table([[["앞", "\n", img, "\n", "뒤"]]])]


def test_captioned_table_cell_count_and_caption_after() -> None:
    item = SynthCaptionedTable((("가", "나"), ("다", "라")), "표 2 캡션")
    blocks = read_blocks(build_hwp5([item]))
    assert blocks == [Table([["가", "나"], ["다", "라"]]), Paragraph("표 2 캡션")]
    table = blocks[0]
    assert isinstance(table, Table)
    assert (table.row_count, table.col_count) == (2, 2)


def test_caption_fixture_table_has_one_cell() -> None:
    items, _, _ = EXT_FIXTURES["caption"]
    blocks = read_blocks(build_hwp5(items))  # type: ignore[arg-type]
    table = blocks[0]
    assert isinstance(table, Table)
    assert table.rows == [["값"]]
    assert blocks[1:] == [Paragraph("표 1 현황")]


def test_textbox_blocks_and_counts(tmp_path: Path) -> None:
    item = SynthTextBox("앵커", ("첫째", "둘째"), with_image=True)
    blocks = read_blocks(build_hwp5([item, "끝"]))
    assert blocks == [
        Paragraph("앵커"),
        Paragraph("첫째"),
        Paragraph("둘째"),
        Image("img_001.png", PNG_1X1),
        Paragraph("끝"),
    ]
    result = convert(write_hwp5(tmp_path / "doc.hwp", [item]), tmp_path / "out")
    assert (result.paragraph_count, result.image_count) == (3, 1)


def test_missing_image_body_is_reported(tmp_path: Path) -> None:
    result = convert(write_hwp5(tmp_path / "doc.hwp", FIXTURE_ITEMS_IMAGE_MISSING), tmp_path / "o")
    assert result.skipped == (("image_missing", 1),)
    assert tuple(p.name for p in result.image_files) == ("img_001.png",)


def test_link_image_is_reported_per_reference() -> None:
    docinfo = DocInfo(para_shapes=(), bin_data=(BinDataEntry(0, 0, 0, ""),))
    skips = SkipCounter()
    store = BinDataStore(docinfo, {}, compressed=True, skips=skips)
    assert store.resolve(1) is None
    assert store.resolve(1) is None
    assert store.resolve(7) is None
    assert skips.items() == (("image_link", 2), ("image_missing", 1))


def test_store_without_counter_still_resolves() -> None:
    docinfo = DocInfo(para_shapes=(), bin_data=(BinDataEntry(1, 2, 1, "png"),))
    store = BinDataStore(docinfo, {"BIN0001.png": PNG_1X1}, compressed=True)
    assert store.resolve(1) == Image("img_001.png", PNG_1X1)
    assert store.resolve(2) is None


def test_ole_bindata_id_offset_twelve() -> None:
    payload = struct.pack("<IiiHIiI", 0x00010001, 100, 200, 5, 0, 0, 0)
    assert parse_ole_bindata_id(payload) == 5
    assert parse_ole_bindata_id(payload[:13]) is None


# ── 레코드 단위: 묶음·글맵시·그림 캡션·칸 안 표 그림 ──────────────────────────────


class _Resolver:
    def resolve(self, bindata_id: int) -> Image | None:
        return Image(f"img_{bindata_id:03d}.png", PNG_1X1)


def _text(s: str) -> bytes:
    return s.encode("utf-16-le") + struct.pack("<H", 13)


def _ctrl(code: int, ctrl_id: bytes) -> bytes:
    return struct.pack("<H", code) + ctrl_id + b"\x00" * 8 + struct.pack("<H", code)


def _para(level: int, payload: bytes) -> list[Record]:
    return [
        Record(HWPTAG_PARA_HEADER, level, b"\x00" * 22),
        Record(HWPTAG_PARA_TEXT, level + 1, payload),
    ]


def _anchor(level: int, ctrl_id: bytes, text: str = "") -> list[Record]:
    return _para(level, text.encode("utf-16-le") + _ctrl(11, ctrl_id) + struct.pack("<H", 13))


def _sc(level: int, chid: bytes) -> Record:
    return Record(HWPTAG_SHAPE_COMPONENT, level, chid + chid + b"\x00" * 40)


def _pic(level: int, bindata_id: int) -> Record:
    return Record(HWPTAG_SHAPE_COMPONENT_PICTURE, level, build_picture_record(bindata_id))


def test_container_children_in_stored_order() -> None:
    recs = [
        *_anchor(0, CTRL_ID_GSO, "앞"),
        Record(HWPTAG_CTRL_HEADER, 1, CTRL_ID_GSO + b"\x00" * 40),
        _sc(2, CHID_CON),
        Record(HWPTAG_SHAPE_COMPONENT_CONTAINER, 3, struct.pack("<H", 3)),
        _sc(3, CHID_REC),
        Record(HWPTAG_LIST_HEADER, 4, b"\x00" * 16),
        *_para(4, _text("상자 글")),
        _sc(3, CHID_PIC),
        _pic(4, 2),
        _sc(3, CHID_CON),
        _sc(4, CHID_PIC),
        _pic(5, 3),
        *_para(0, _text("뒤")),
    ]
    assert parse_blocks(recs, bin_data=_Resolver()) == [
        Paragraph("앞"),
        Paragraph("상자 글"),
        Image("img_002.png", PNG_1X1),
        Image("img_003.png", PNG_1X1),
        Paragraph("뒤"),
    ]


def test_textart_is_skipped_and_counted() -> None:
    recs = [
        *_anchor(0, CTRL_ID_GSO),
        Record(HWPTAG_CTRL_HEADER, 1, CTRL_ID_GSO + b"\x00" * 40),
        _sc(2, b"$tat"[::-1]),
        Record(HWPTAG_SHAPE_COMPONENT_TEXTART, 3, b"\x00" * 20),
    ]
    ctx = ReadContext()
    assert parse_blocks(recs, ctx=ctx) == []
    assert ctx.skips.items() == (("textart", 1),)


def test_ole_without_object_resolver_counts_ole() -> None:
    recs = [
        *_anchor(0, CTRL_ID_GSO),
        Record(HWPTAG_CTRL_HEADER, 1, CTRL_ID_GSO + b"\x00" * 40),
        _sc(2, b"$ole"[::-1]),
        Record(HWPTAG_SHAPE_COMPONENT_OLE, 3, struct.pack("<IiiH", 0, 0, 0, 1)),
    ]
    ctx = ReadContext()
    assert parse_blocks(recs, bin_data=_Resolver(), ctx=ctx) == []
    assert ctx.skips.items() == (("ole", 1),)


def test_picture_caption_follows_image() -> None:
    recs = [
        *_anchor(0, CTRL_ID_GSO),
        Record(HWPTAG_CTRL_HEADER, 1, CTRL_ID_GSO + b"\x00" * 40),
        Record(HWPTAG_LIST_HEADER, 2, b"\x00" * 30),
        *_para(2, _text("그림 1 설명")),
        _sc(2, CHID_PIC),
        _pic(3, 1),
    ]
    assert parse_blocks(recs, bin_data=_Resolver()) == [
        Image("img_001.png", PNG_1X1),
        Paragraph("그림 1 설명"),
    ]


def test_nested_table_image_goes_to_parent_cell_end() -> None:
    cell = struct.pack("<HHIHHHH", 1, 0, 0, 0, 0, 1, 1) + b"\x00" * 22
    inner = [
        *_anchor(2, CTRL_ID_TABLE),
        Record(HWPTAG_CTRL_HEADER, 3, CTRL_ID_TABLE + b"\x00" * 40),
        Record(HWPTAG_TABLE, 4, struct.pack("<IHH", 0, 1, 1)),
        Record(HWPTAG_LIST_HEADER, 4, cell),
        *_anchor(4, CTRL_ID_GSO, "안"),
        Record(HWPTAG_CTRL_HEADER, 5, CTRL_ID_GSO + b"\x00" * 40),
        _sc(6, CHID_PIC),
        _pic(7, 4),
    ]
    recs = [
        *_anchor(0, CTRL_ID_TABLE),
        Record(HWPTAG_CTRL_HEADER, 1, CTRL_ID_TABLE + b"\x00" * 40),
        Record(HWPTAG_TABLE, 2, struct.pack("<IHH", 0, 1, 1)),
        Record(HWPTAG_LIST_HEADER, 2, cell),
        *inner,
    ]
    img = Image("img_004.png", PNG_1X1)
    assert parse_blocks(recs, bin_data=_Resolver()) == [make_table([[["안", img]]])]
