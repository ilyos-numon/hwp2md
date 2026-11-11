"""HWPX 번호·글머리표 목록: hh:heading NUMBER/BULLET → ListInfo."""

from pathlib import Path

import pytest
from lxml import etree

from hwp2md.blocks import Block, ListInfo, Paragraph
from hwp2md.convert import convert
from hwp2md.hwpx.body import DocContext, parse_section
from hwp2md.hwpx.header import (
    NS_HH,
    NS_HP,
    HeaderInfo,
    ListShape,
    parse_header,
    parse_header_xml,
    to_num_format,
)
from hwp2md.hwpx.reader import NS_HS, parse_section_xml, read_blocks
from synth_hwp5 import SynthHeading
from synth_hwpx import (
    XML_DECL,
    build_zip,
    hwpx_entries,
    list_para_pr_id,
    numbering_xml,
    paragraph_xml,
    write_hwpx,
)
from synth_items import EXT_FIXTURES, EXT_IDS_BY_STAGE, SynthListPara

LIST_IDS = EXT_IDS_BY_STAGE["lists"]


def _header(numberings: str = "", bullets: str = "", para_props: str = "") -> HeaderInfo:
    return parse_header(
        parse_header_xml(
            (
                XML_DECL
                + f'<hh:head xmlns:hh="{NS_HH}" xmlns:hp="{NS_HP}" version="1.5" secCnt="1">'
                + "<hh:refList>"
                + (f"<hh:numberings>{numberings}</hh:numberings>" if numberings else "")
                + (f"<hh:bullets>{bullets}</hh:bullets>" if bullets else "")
                + f"<hh:paraProperties>{para_props}</hh:paraProperties>"
                + "</hh:refList></hh:head>"
            ).encode()
        )
    )


def _pp(pid: int, htype: str, id_ref: int, level: int) -> str:
    return (
        f'<hh:paraPr id="{pid}"><hh:heading type="{htype}" idRef="{id_ref}" level="{level}"/>'
        "</hh:paraPr>"
    )


def _section(paras: list[tuple[str, int]]) -> etree._Element:
    body = "".join(
        paragraph_xml(text, para_id=i, para_pr_id=pid) for i, (text, pid) in enumerate(paras)
    )
    return parse_section_xml(
        (XML_DECL + f'<hs:sec xmlns:hp="{NS_HP}" xmlns:hs="{NS_HS}">{body}</hs:sec>').encode()
    )


def _infos(blocks: list[Block]) -> list[ListInfo | None]:
    return [b.list_info for b in blocks if isinstance(b, Paragraph)]


def test_list_ids_are_two() -> None:
    assert LIST_IDS == ["bullets", "numbers"]


@pytest.mark.parametrize("in_switch", [False, True], ids=["direct", "switch_case"])
@pytest.mark.parametrize("fixture_id", LIST_IDS)
def test_ext_fixture_markdown(tmp_path: Path, fixture_id: str, in_switch: bool) -> None:
    items, expected_md, expected_skipped = EXT_FIXTURES[fixture_id]
    src = tmp_path / "doc.hwpx"
    src.write_bytes(build_zip(hwpx_entries(items, list_in_switch=in_switch)))  # type: ignore[arg-type]
    result = convert(src, tmp_path / "out")
    assert result.markdown == expected_md
    assert result.skipped == expected_skipped


def test_bullets_counts_paragraphs(tmp_path: Path) -> None:
    items, _, _ = EXT_FIXTURES["bullets"]
    result = convert(write_hwpx(tmp_path / "doc.hwpx", items), tmp_path / "out")  # type: ignore[arg-type]
    assert result.paragraph_count == 3
    assert result.heading_count == 0


def test_numbers_blocks(tmp_path: Path) -> None:
    items, _, _ = EXT_FIXTURES["numbers"]
    blocks = read_blocks(write_hwpx(tmp_path / "doc.hwpx", items))  # type: ignore[arg-type]
    assert blocks == [
        Paragraph("가", list_info=ListInfo("number", 0, "1.")),
        Paragraph("나", list_info=ListInfo("number", 0, "2.")),
    ]


def test_switch_case_heading_parsed() -> None:
    entries = hwpx_entries([SynthListPara("a", "number", depth=2)], list_in_switch=True)
    assert b"<hp:switch>" in entries["Contents/header.xml"]
    info = parse_header(parse_header_xml(entries["Contents/header.xml"]))
    pid = list_para_pr_id("number", 2)
    assert info.lists[pid] == ListShape("number", 1, 2)
    assert info.para_levels == {}
    assert info.heading_level(pid) == 0


def test_level_reset_and_nested_template(tmp_path: Path) -> None:
    items = [
        SynthListPara("a", "number", 0, "^1."),
        SynthListPara("b", "number", 1, "^1.^2."),
        SynthListPara("c", "number", 1, "^1.^2."),
        SynthListPara("d", "number", 0, "^1."),
        SynthListPara("e", "number", 1, "^1.^2."),
    ]
    blocks = read_blocks(write_hwpx(tmp_path / "doc.hwpx", items))
    assert _infos(blocks) == [
        ListInfo("number", 0, "1."),
        ListInfo("number", 1, "1.1."),
        ListInfo("number", 1, "1.2."),
        ListInfo("number", 0, "2."),
        ListInfo("number", 1, "2.1."),
    ]


def test_nested_digit_list_markdown_indent(tmp_path: Path) -> None:
    items = [
        SynthListPara("a", "number", 0, "^1."),
        SynthListPara("b", "number", 1, "^2."),
        SynthListPara("c", "number", 1, "^2."),
        SynthListPara("d", "number", 0, "^1."),
        SynthListPara("e", "number", 1, "^2."),
    ]
    md = convert(write_hwpx(tmp_path / "doc.hwpx", items), tmp_path / "out").markdown
    assert md == "1. a\n    1. b\n    2. c\n2. d\n    1. e\n"


def test_counter_continues_across_sections(tmp_path: Path) -> None:
    src = write_hwpx(
        tmp_path / "doc.hwpx",
        [SynthListPara("a", "number")],
        more_sections=[[SynthListPara("b", "number")]],
    )
    assert _infos(read_blocks(src)) == [
        ListInfo("number", 0, "1."),
        ListInfo("number", 0, "2."),
    ]


def test_headings_unchanged_with_lists(tmp_path: Path) -> None:
    items = [SynthHeading("제목", 1), SynthListPara("a", "bullet", 1), "끝"]
    blocks = read_blocks(write_hwpx(tmp_path / "doc.hwpx", items))
    assert blocks == [
        Paragraph("제목", level=1),
        Paragraph("a", list_info=ListInfo("bullet", 1, "")),
        Paragraph("끝"),
    ]


def test_parse_header_numbering_formats_starts_bullets() -> None:
    num = numbering_xml(
        {1: "^1.", 2: "^2)", 3: "(^3)", 4: "^4"},
        numbering_id=3,
        formats={1: "HANGUL_SYLLABLE", 2: "IDEOGRAPH", 3: "NOT_A_FORMAT", 4: "CIRCLED_DIGIT"},
        starts={1: 3, 2: 0},
        start=5,
    )
    bullet = '<hh:bullet id="2" char="-" useImage="0"/>'
    info = _header(
        num,
        bullet,
        _pp(10, "NUMBER", 3, 0) + _pp(11, "BULLET", 2, 9) + _pp(12, "OUTLINE", 0, 1),
    )
    nd = info.numberings[3]
    assert nd.templates == {1: "^1.", 2: "^2)", 3: "(^3)", 4: "^4"}
    assert nd.formats == {
        1: "HANGUL_SYLLABLE",
        2: "HANJA_DIGIT",
        3: "DIGIT",
        4: "CIRCLED_DIGIT",
    }
    assert nd.starts == {1: 3, 2: 5, 3: 1, 4: 1}
    assert info.bullets == {2: "-"}
    assert info.lists == {10: ListShape("number", 3, 0), 11: ListShape("bullet", 2, 6)}
    assert info.para_levels == {12: 1}
    assert info.heading_level(12) == 2


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("DIGIT", "DIGIT"),
        ("HANGUL_SYLLABLE", "HANGUL_SYLLABLE"),
        ("CIRCLED_HANGUL_SYLLABLE", "CIRCLED_HANGUL_SYLLABLE"),
        ("ROMAN_SMALL", "ROMAN_SMALL"),
        ("IDEOGRAPH", "HANJA_DIGIT"),
        ("HANGUL_PHONETIC", "DIGIT"),
        (None, "DIGIT"),
    ],
)
def test_to_num_format(value: str | None, expected: str) -> None:
    assert to_num_format(value) == expected


def test_num_format_and_start_used_in_label() -> None:
    num = numbering_xml({1: "^1.", 2: "(^2)"}, formats={1: "HANGUL_SYLLABLE"}, starts={2: 3})
    info = _header(num, para_props=_pp(20, "NUMBER", 1, 0) + _pp(21, "NUMBER", 1, 1))
    blocks = parse_section(_section([("a", 20), ("b", 21), ("c", 21), ("d", 20)]), info)
    assert [i.label if i else None for i in _infos(blocks)] == ["가.", "(3)", "(4)", "나."]


def test_unknown_numbering_id_uses_default_template() -> None:
    info = _header(para_props=_pp(20, "NUMBER", 9, 1))
    blocks = parse_section(_section([("a", 20), ("b", 20)]), info)
    # 형식이 없으면 "^L." (수준 2 → "^2.")
    assert _infos(blocks) == [ListInfo("number", 1, "1."), ListInfo("number", 1, "2.")]


def test_empty_list_paragraph_does_not_consume_number() -> None:
    info = _header(numbering_xml({1: "^1."}), para_props=_pp(20, "NUMBER", 1, 0))
    blocks = parse_section(_section([("", 20), ("a", 20)]), info)
    assert _infos(blocks) == [ListInfo("number", 0, "1.")]


def test_counter_shared_through_context() -> None:
    info = _header(numbering_xml({1: "^1."}), para_props=_pp(20, "NUMBER", 1, 0))
    ctx = DocContext()
    first = parse_section(_section([("a", 20)]), info, None, ctx)
    second = parse_section(_section([("b", 20)]), info, None, ctx)
    assert _infos(first + second) == [ListInfo("number", 0, "1."), ListInfo("number", 0, "2.")]
