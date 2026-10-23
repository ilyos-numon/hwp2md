"""HWPX 단락 안 요소: 링크·각주/미주·수식·필드 글자, 머리말·꼬리말·숨은 설명·메모 건너뜀."""

from pathlib import Path

import pytest
from lxml import etree

from hwp2md.blocks import Link, Math, Note, NoteRef, Paragraph
from hwp2md.convert import convert
from hwp2md.hwpx import reader
from hwp2md.hwpx.body import (
    DocContext,
    hyperlink_command_target,
    parse_section,
)
from hwp2md.hwpx.reader import NS_HP, NS_HS, parse_section_xml
from hwp2md.skips import SkipCounter
from synth_hwpx import write_hwpx
from synth_items import EXT_FIXTURES, EXT_IDS_BY_STAGE, SynthNote, SynthRich

INLINE_IDS = EXT_IDS_BY_STAGE["inline"]


def _sec(inner: str) -> etree._Element:
    return parse_section_xml(
        (f'<hs:sec xmlns:hp="{NS_HP}" xmlns:hs="{NS_HS}">{inner}</hs:sec>').encode()
    )


def _p(*runs: str) -> str:
    return "<hp:p>" + "".join(f"<hp:run>{r}</hp:run>" for r in runs) + "</hp:p>"


def _t(text: str) -> str:
    return f"<hp:t>{text}</hp:t>"


def _link_begin(params: str, fid: str = "1", ftype: str = "HYPERLINK") -> str:
    return (
        f'<hp:ctrl><hp:fieldBegin id="{fid}" type="{ftype}">'
        f"<hp:parameters>{params}</hp:parameters></hp:fieldBegin></hp:ctrl>"
    )


def _end(fid: str = "1") -> str:
    return f'<hp:ctrl><hp:fieldEnd beginIDRef="{fid}"/></hp:ctrl>'


def _param(name: str, value: str) -> str:
    return f'<hp:stringParam name="{name}">{value}</hp:stringParam>'


@pytest.mark.parametrize("fixture_id", INLINE_IDS)
def test_inline_fixtures_markdown_and_skipped(tmp_path: Path, fixture_id: str) -> None:
    items, expected_md, expected_skipped = EXT_FIXTURES[fixture_id]
    src = write_hwpx(tmp_path / "doc.hwpx", items)  # type: ignore[arg-type]
    result = convert(src, tmp_path / "out")
    assert result.markdown == expected_md
    assert result.skipped == expected_skipped
    assert result.image_files == ()


def test_inline_ids_are_ten() -> None:
    assert len(INLINE_IDS) == 10


def test_read_blocks_counts_into_given_counter(tmp_path: Path) -> None:
    items, _, expected = EXT_FIXTURES["header"]
    counter = SkipCounter()
    reader.read_blocks(write_hwpx(tmp_path / "doc.hwpx", items), skips=counter)  # type: ignore[arg-type]
    assert counter.items() == expected


def test_note_numbers_continue_across_sections(tmp_path: Path) -> None:
    first = [SynthRich(("가", SynthNote(("하나",))))]
    second = [SynthRich(("나", SynthNote(("둘",)), SynthNote(("미",), kind="endnote")))]
    src = write_hwpx(tmp_path / "doc.hwpx", first, more_sections=[second])  # type: ignore[arg-type]
    blocks = reader.read_blocks(src)
    assert blocks == [
        Paragraph("가", inlines=("가", NoteRef("footnote", 1))),
        Paragraph("나", inlines=("나", NoteRef("footnote", 2), NoteRef("endnote", 1))),
        Note("footnote", 1, (Paragraph("하나"),)),
        Note("footnote", 2, (Paragraph("둘"),)),
        Note("endnote", 1, (Paragraph("미"),)),
    ]


def test_link_path_preferred_over_command() -> None:
    params = _param("Command", "https\\://b.example;1;0;0;") + _param("Path", "https://a.example")
    xml = _p(_t("앞 "), _link_begin(params), _t("글"), _end(), _t(" 뒤"))
    assert parse_section(_sec(xml)) == [
        Paragraph("앞 글 뒤", inlines=("앞 ", Link("글", "https://a.example"), " 뒤"))
    ]


def test_link_command_used_without_path() -> None:
    xml = _p(_link_begin(_param("Command", "mailto\\:a@b.example;2;0;0;")), _t("메일"), _end())
    assert parse_section(_sec(xml)) == [
        Paragraph("메일", inlines=(Link("메일", "mailto:a@b.example"),))
    ]


def test_link_fieldbegin_directly_in_run() -> None:
    begin = '<hp:fieldBegin id="7" type="HYPERLINK"><hp:parameters>'
    begin += _param("Path", "https://a.example") + "</hp:parameters></hp:fieldBegin>"
    xml = _p(begin, _t("글"), '<hp:fieldEnd beginIDRef="7"/>')
    assert parse_section(_sec(xml)) == [Paragraph("글", inlines=(Link("글", "https://a.example"),))]


def test_bookmark_link_is_plain_text() -> None:
    xml = _p(_link_begin(_param("Command", "?책갈피;0;0;0;")), _t("이동"), _end())
    assert parse_section(_sec(xml)) == [Paragraph("이동")]


def test_inner_field_end_does_not_close_link() -> None:
    params = _param("Path", "https://a.example")
    inner = _link_begin("", fid="9", ftype="CLICK_HERE")
    xml = _p(_link_begin(params), _t("가"), inner, _t("나"), _end("9"), _t("다"), _end(), _t("끝"))
    assert parse_section(_sec(xml)) == [
        Paragraph("가나다끝", inlines=(Link("가나다", "https://a.example"), "끝"))
    ]


@pytest.mark.parametrize(
    ("command", "expected"),
    [
        ("https\\://a.example/x\\?q=1;1;0;0;", "https://a.example/x?q=1"),
        ("mailto\\:a@b.example;2;0;0", "mailto:a@b.example"),
        ("https\\://a.example|설명;1;0;0;", "https://a.example"),
        ("?이름;0;0;0;", None),
        (";1;0;0;", None),
        ("", None),
    ],
)
def test_hyperlink_command_target(command: str, expected: str | None) -> None:
    assert hyperlink_command_target(command) == expected


def test_equation_inline_and_empty_script() -> None:
    eq = "<hp:equation><hp:shapeComment>설명</hp:shapeComment><hp:script>a over b</hp:script>"
    eq += "</hp:equation>"
    empty = "<hp:equation><hp:script>  </hp:script></hp:equation>"
    xml = _p(_t("식 "), eq, empty, _t(" 끝"))
    [para] = parse_section(_sec(xml))
    assert isinstance(para, Paragraph)
    assert para.inlines[1] == Math("a over b", "\\frac{a}{b}")
    assert len(para.inlines) == 3


def test_autonum_and_nested_note_ignored() -> None:
    nested = "<hp:footNote><hp:subList>" + _p(_t("안쪽")) + "</hp:subList></hp:footNote>"
    auto = '<hp:ctrl><hp:autoNum num="1" numType="FOOTNOTE"/></hp:ctrl>'
    body = "<hp:subList>" + _p(auto, _t(" 바깥"), f"<hp:ctrl>{nested}</hp:ctrl>") + "</hp:subList>"
    xml = _p(_t("본문"), f"<hp:ctrl><hp:footNote>{body}</hp:footNote></hp:ctrl>")
    assert parse_section(_sec(xml)) == [
        Paragraph("본문", inlines=("본문", NoteRef("footnote", 1))),
        Note("footnote", 1, (Paragraph("바깥"),)),
    ]


def test_header_footer_hidden_and_memo_counted() -> None:
    hdr = (
        "<hp:ctrl><hp:header><hp:subList>" + _p(_t("머리")) + "</hp:subList></hp:header></hp:ctrl>"
    )
    ftr = (
        "<hp:ctrl><hp:footer><hp:subList>" + _p(_t("꼬리")) + "</hp:subList></hp:footer></hp:ctrl>"
    )
    hid = "<hp:ctrl><hp:hiddenComment><hp:subList>" + _p(_t("숨은")) + "</hp:subList>"
    hid += "</hp:hiddenComment></hp:ctrl>"
    memo = "<hp:memogroup><hp:memo/><hp:memo/></hp:memogroup>"
    ctx = DocContext()
    blocks = parse_section(_sec(_p(hdr, ftr, _t("본문"), hid) + memo), ctx=ctx)
    assert blocks == [Paragraph("본문")]
    assert ctx.skips.items() == (("header_footer", 2), ("memo", 2), ("hidden_comment", 1))


def test_plain_document_unchanged_and_no_skips(tmp_path: Path) -> None:
    counter = SkipCounter()
    blocks = reader.read_blocks(write_hwpx(tmp_path / "doc.hwpx", ["가", "나"]), skips=counter)
    assert blocks == [Paragraph("가"), Paragraph("나")]
    assert counter.items() == ()
