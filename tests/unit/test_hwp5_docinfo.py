from pathlib import Path

import pytest

import synth_hwp5
from hwp2md.blocks import Block, Paragraph
from hwp2md.errors import Hwp2mdError
from hwp2md.hwp5 import records
from hwp2md.hwp5.docinfo import EMPTY_DOCINFO, DocInfo, ParaShape, parse_docinfo, parse_para_shape
from hwp2md.hwp5.reader import read_blocks, read_sections, read_streams
from synth_hwp5 import (
    EXPECTED_BLOCKS_HEADING_EDGE,
    EXPECTED_BLOCKS_HEADING_IN_CELL,
    EXPECTED_BLOCKS_HEADINGS,
    FIXTURE_ITEMS_HEADING_EDGE,
    FIXTURE_ITEMS_HEADING_IN_CELL,
    FIXTURE_ITEMS_HEADINGS,
    build_cfb,
    build_docinfo,
    build_file_header,
    build_section0,
    write_hwp5,
)


def test_tag_constants_match_generator() -> None:
    assert records.HWPTAG_PARA_SHAPE == synth_hwp5.HWPTAG_PARA_SHAPE == 0x19
    assert records.HWPTAG_STYLE == synth_hwp5.HWPTAG_STYLE == 0x1A


def test_parse_para_shape_bits() -> None:
    assert parse_para_shape(((1 << 23) | (2 << 25)).to_bytes(4, "little")) == ParaShape(1, 2)
    assert parse_para_shape((2 << 23).to_bytes(4, "little")).heading_type == 2
    with pytest.raises(Hwp2mdError, match="truncated PARA_SHAPE record"):
        parse_para_shape(b"\x00\x00\x00")


def test_parse_docinfo_collects_shapes_in_order() -> None:
    info = parse_docinfo(build_docinfo(outline=True))
    assert len(info.para_shapes) == 8
    assert [s.heading_type for s in info.para_shapes] == [0, 1, 1, 1, 1, 1, 1, 1]
    assert [s.heading_level for s in info.para_shapes] == [0, 0, 1, 2, 3, 4, 5, 6]


def test_parse_docinfo_empty_and_default() -> None:
    assert parse_docinfo(b"") == EMPTY_DOCINFO
    assert parse_docinfo(build_docinfo()).para_shapes == ()


def test_heading_level_rule() -> None:
    info = parse_docinfo(build_docinfo(outline=True))
    assert info.heading_level(0) == 0
    assert info.heading_level(1) == 1
    assert info.heading_level(6) == 6
    assert info.heading_level(7) == 6
    assert info.heading_level(99) == 0
    assert info.heading_level(-1) == 0
    other = DocInfo((ParaShape(2, 3), ParaShape(3, 1)))
    assert other.heading_level(0) == 0
    assert other.heading_level(1) == 0


@pytest.mark.parametrize(
    ("items", "expected"),
    [
        (FIXTURE_ITEMS_HEADINGS, EXPECTED_BLOCKS_HEADINGS),
        (FIXTURE_ITEMS_HEADING_EDGE, EXPECTED_BLOCKS_HEADING_EDGE),
        (FIXTURE_ITEMS_HEADING_IN_CELL, EXPECTED_BLOCKS_HEADING_IN_CELL),
    ],
)
def test_read_blocks_heading_fixtures(
    tmp_path: Path, items: list[synth_hwp5.Item], expected: list[Block]
) -> None:
    assert read_blocks(write_hwp5(tmp_path / "h.hwp", items)) == expected


def test_read_blocks_uncompressed_heading_fixture(tmp_path: Path) -> None:
    path = write_hwp5(tmp_path / "h.hwp", FIXTURE_ITEMS_HEADINGS, properties=0)
    assert read_blocks(path) == EXPECTED_BLOCKS_HEADINGS


def test_empty_docinfo_stream_means_no_headings(tmp_path: Path) -> None:
    path = tmp_path / "e.hwp"
    path.write_bytes(
        build_cfb(
            {
                "FileHeader": build_file_header(properties=0),
                "DocInfo": b"",
                "BodyText/Section0": build_section0(FIXTURE_ITEMS_HEADINGS),
            }
        )
    )
    expected = [
        Paragraph(b.text) if isinstance(b, Paragraph) else b for b in EXPECTED_BLOCKS_HEADINGS
    ]
    assert read_blocks(path) == expected


def test_truncated_docinfo_raises(tmp_path: Path) -> None:
    path = tmp_path / "t.hwp"
    path.write_bytes(
        build_cfb(
            {
                "FileHeader": build_file_header(properties=0),
                "DocInfo": build_docinfo(outline=True)[:-3],
                "BodyText/Section0": build_section0(FIXTURE_ITEMS_HEADINGS),
            }
        )
    )
    with pytest.raises(Hwp2mdError, match="truncated record"):
        read_blocks(path)


def test_read_sections_wrapper_matches_read_streams(tmp_path: Path) -> None:
    path = write_hwp5(tmp_path / "h.hwp", FIXTURE_ITEMS_HEADINGS)
    assert read_sections(path) == read_streams(path)[1]
    assert len(read_streams(path)[0]) > 0
