from pathlib import Path

import pytest
from lxml import etree

import synth_hwpx
from hwp2md.blocks import Block, Paragraph
from hwp2md.errors import Hwp2mdError
from hwp2md.hwpx import body, header
from hwp2md.hwpx.header import NS_HH, NS_HP, _make_parser, parse_header, parse_header_xml
from hwp2md.hwpx.reader import read_blocks
from synth_hwp5 import (
    EXPECTED_BLOCKS_HEADING_EDGE,
    EXPECTED_BLOCKS_HEADING_IN_CELL,
    EXPECTED_BLOCKS_HEADINGS,
    FIXTURE_ITEMS_HEADING_EDGE,
    FIXTURE_ITEMS_HEADING_IN_CELL,
    FIXTURE_ITEMS_HEADINGS,
    Item,
)
from synth_hwpx import build_zip, hwpx_entries, write_hwpx

XML_DECL = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'


def _head(inner: str) -> etree._Element:
    return parse_header_xml(
        (
            XML_DECL
            + f'<hh:head xmlns:hh="{NS_HH}" xmlns:hp="{NS_HP}" version="1.5" secCnt="1">'
            + f"{inner}</hh:head>"
        ).encode()
    )


def _pp(pid: str, inner: str) -> str:
    return (
        "<hh:refList><hh:paraProperties>"
        f'<hh:paraPr id="{pid}">{inner}</hh:paraPr>'
        "</hh:paraProperties></hh:refList>"
    )


def test_ns_constant_matches_generator_and_body() -> None:
    assert header.NS_HH == synth_hwpx.NS_HH
    assert header.NS_HP == body.NS_HP


def test_parse_header_outline_levels() -> None:
    info = parse_header(
        parse_header_xml(hwpx_entries(FIXTURE_ITEMS_HEADINGS)["Contents/header.xml"])
    )
    assert info.para_levels == {1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 6}
    assert info.heading_level(1) == 1
    assert info.heading_level(7) == 6
    assert info.heading_level(0) == 0
    assert info.heading_level(None) == 0
    assert info.heading_level(99) == 0


def test_heading_inside_switch_case_used() -> None:
    inner = (
        '<hp:switch><hp:case hp:required-namespace="x">'
        '<hh:heading type="OUTLINE" idRef="0" level="7"/></hp:case>'
        '<hp:default><hh:heading type="NONE" idRef="0" level="0"/></hp:default></hp:switch>'
    )
    assert parse_header(_head(_pp("5", inner))).heading_level(5) == 6


@pytest.mark.parametrize("kind", ["NUMBER", "BULLET"])
def test_number_and_bullet_not_heading(kind: str) -> None:
    info = parse_header(_head(_pp("2", f'<hh:heading type="{kind}" idRef="0" level="2"/>')))
    assert info.heading_level(2) == 0


def test_missing_level_or_bad_id_ignored() -> None:
    info = parse_header(_head(_pp("3", '<hh:heading type="OUTLINE" idRef="0"/>')))
    assert info.heading_level(3) == 0
    info = parse_header(_head(_pp("x", '<hh:heading type="OUTLINE" idRef="0" level="1"/>')))
    assert info.para_levels == {}


def test_wrong_root_raises() -> None:
    with pytest.raises(Hwp2mdError, match="unexpected header root element"):
        parse_header_xml(b'<?xml version="1.0"?><x/>')


def test_malformed_header_raises() -> None:
    with pytest.raises(Hwp2mdError, match="malformed header XML"):
        parse_header_xml(b"<hh:head")


def test_parser_blocks_entities() -> None:
    # lxml 6 은 resolve_entities 를 속성으로 노출하지 않으므로 동작으로 확인한다.
    p = _make_parser()
    root = etree.fromstring(b'<!DOCTYPE r [<!ENTITY lol "lol">]><r>a&lol;b</r>', p)
    assert [type(c) for c in root] == [etree._Entity]
    assert _make_parser() is not p


def test_missing_header_entry_means_no_headings(tmp_path: Path) -> None:
    entries = hwpx_entries(FIXTURE_ITEMS_HEADINGS)
    del entries["Contents/header.xml"]
    path = tmp_path / "noheader.hwpx"
    path.write_bytes(build_zip(entries))
    expected = [
        Paragraph(b.text) if isinstance(b, Paragraph) else b for b in EXPECTED_BLOCKS_HEADINGS
    ]
    assert read_blocks(path) == expected


@pytest.mark.parametrize(
    ("items", "expected"),
    [
        (FIXTURE_ITEMS_HEADINGS, EXPECTED_BLOCKS_HEADINGS),
        (FIXTURE_ITEMS_HEADING_EDGE, EXPECTED_BLOCKS_HEADING_EDGE),
        (FIXTURE_ITEMS_HEADING_IN_CELL, EXPECTED_BLOCKS_HEADING_IN_CELL),
    ],
    ids=["headings", "edge", "in_cell"],
)
def test_read_blocks_heading_fixtures(
    tmp_path: Path, items: list[Item], expected: list[Block]
) -> None:
    assert read_blocks(write_hwpx(tmp_path / "h.hwpx", items)) == expected
