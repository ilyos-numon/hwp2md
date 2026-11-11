"""HWP 5.0 단락 안 요소: 링크·각주/미주·수식·필드 글자, 머리말·꼬리말·숨은 설명·메모 건너뜀."""

import struct
from pathlib import Path

import pytest

from hwp2md.blocks import Link, Math, Note, NoteRef, Paragraph
from hwp2md.convert import convert
from hwp2md.hwp5.body import (
    ReadContext,
    hyperlink_url,
    parse_blocks,
    parse_eqedit_script,
    parse_field_command,
)
from hwp2md.hwp5.reader import read_blocks
from hwp2md.hwp5.records import (
    CTRL_ID_FOOTNOTE,
    CTRL_ID_HEADER,
    CTRL_ID_HYPERLINK,
    HWPTAG_CTRL_HEADER,
    HWPTAG_LIST_HEADER,
    HWPTAG_MEMO_LIST,
    HWPTAG_PARA_HEADER,
    HWPTAG_PARA_TEXT,
    CtrlMark,
    Record,
    decode_para_runs,
    decode_para_text,
)
from hwp2md.skips import SkipCounter
from synth_hwp5 import (
    CTRL_ID_CLICK_HERE,
    build_ctrl_header_field,
    build_eqedit,
    build_hwp5,
    write_hwp5,
)
from synth_items import (
    EXT_FIXTURES,
    EXT_IDS_BY_STAGE,
    SynthHeaderFooter,
    SynthLink,
    SynthNote,
    SynthRich,
)

INLINE_IDS = EXT_IDS_BY_STAGE["inline"]


def _ctrl(code: int, ctrl_id: bytes) -> bytes:
    return struct.pack("<H", code) + ctrl_id + b"\x00" * 8 + struct.pack("<H", code)


def _text(*parts: str | tuple[int, bytes]) -> bytes:
    out = b""
    for part in parts:
        out += part.encode("utf-16-le") if isinstance(part, str) else _ctrl(*part)
    return out + struct.pack("<H", 13)


def _para(payload: bytes, level: int = 0) -> list[Record]:
    return [
        Record(HWPTAG_PARA_HEADER, level, b"\x00" * 22),
        Record(HWPTAG_PARA_TEXT, level + 1, payload),
    ]


def _note_ctrl(text: str, level: int, ctrl_id: bytes = CTRL_ID_FOOTNOTE) -> list[Record]:
    return [
        Record(HWPTAG_CTRL_HEADER, level, ctrl_id + b"\x00" * 8),
        Record(HWPTAG_LIST_HEADER, level + 1, b"\x00" * 16),
        *_para(_text(text), level + 1),
    ]


@pytest.mark.parametrize("fixture_id", INLINE_IDS)
def test_inline_ext_fixtures_markdown_and_skipped(fixture_id: str, tmp_path: Path) -> None:
    items, expected_md, expected_skipped = EXT_FIXTURES[fixture_id]
    src = write_hwp5(tmp_path / "doc.hwp", items)  # type: ignore[arg-type]
    result = convert(src, tmp_path / "out")
    assert result.markdown == expected_md
    assert result.skipped == expected_skipped
    assert result.image_files == ()


def test_inline_fixture_ids_are_ten() -> None:
    assert len(INLINE_IDS) == 10


def test_footnote_paragraph_count_and_blocks(tmp_path: Path) -> None:
    items, _, _ = EXT_FIXTURES["footnote"]
    src = write_hwp5(tmp_path / "doc.hwp", items)  # type: ignore[arg-type]
    assert convert(src, tmp_path / "out").paragraph_count == 1
    assert read_blocks(src) == [
        Paragraph("가나", 0, ("가", NoteRef("footnote", 1), "나")),
        Note("footnote", 1, (Paragraph("주석"),)),
    ]


def test_link_and_equation_blocks(tmp_path: Path) -> None:
    items, _, _ = EXT_FIXTURES["link"]
    blocks = read_blocks(build_hwp5(items))  # type: ignore[arg-type]
    assert blocks == [
        Paragraph("앞 누리집 뒤", 0, ("앞 ", Link("누리집", "https://example.org/a b"), " 뒤"))
    ]
    items, _, _ = EXT_FIXTURES["equation_inline"]
    blocks = read_blocks(build_hwp5(items))  # type: ignore[arg-type]
    assert blocks == [
        Paragraph("식 a over b 끝", 0, ("식 ", Math("a over b", "\\frac{a}{b}"), " 끝"))
    ]


def test_header_text_not_in_body_and_counted(tmp_path: Path) -> None:
    items = [SynthHeaderFooter(("머리말",)), "본문", SynthHeaderFooter(("꼬리말",), kind="footer")]
    skips = SkipCounter()
    blocks = read_blocks(build_hwp5(items), skips)
    assert blocks == [Paragraph("본문")]
    assert skips.items() == (("header_footer", 2),)


def test_read_blocks_without_counter_still_works() -> None:
    items, _, _ = EXT_FIXTURES["header"]
    assert read_blocks(build_hwp5(items)) == [Paragraph("본문")]  # type: ignore[arg-type]


def test_note_numbers_continue_across_sections() -> None:
    ctx = ReadContext()
    section = _para(_text("가", (17, CTRL_ID_FOOTNOTE))) + _note_ctrl("하나", 1)
    first = parse_blocks(section, ctx=ctx)
    second = parse_blocks(section, ctx=ctx)
    assert first == [Paragraph("가", 0, ("가", NoteRef("footnote", 1)))]
    assert second == [Paragraph("가", 0, ("가", NoteRef("footnote", 2)))]
    assert [n.number for n in ctx.note_blocks() if isinstance(n, Note)] == [1, 2]


def test_parse_blocks_without_ctx_appends_notes_at_end() -> None:
    recs = _para(_text("가", (17, CTRL_ID_FOOTNOTE))) + _note_ctrl("주석", 1) + _para(_text("다음"))
    assert parse_blocks(recs) == [
        Paragraph("가", 0, ("가", NoteRef("footnote", 1))),
        Paragraph("다음"),
        Note("footnote", 1, (Paragraph("주석"),)),
    ]


def test_note_inside_note_is_skipped_silently() -> None:
    inner = _para(_text("안", (17, CTRL_ID_FOOTNOTE)), 2) + _note_ctrl("더 안", 3)
    recs = [
        *_para(_text("가", (17, CTRL_ID_FOOTNOTE))),
        Record(HWPTAG_CTRL_HEADER, 1, CTRL_ID_FOOTNOTE + b"\x00" * 8),
        Record(HWPTAG_LIST_HEADER, 2, b"\x00" * 16),
        *inner,
    ]
    skips = SkipCounter()
    ctx = ReadContext(skips)
    blocks = parse_blocks(recs, ctx=ctx)
    assert blocks == [Paragraph("가", 0, ("가", NoteRef("footnote", 1)))]
    assert ctx.note_blocks() == [Note("footnote", 1, (Paragraph("안"),))]
    assert skips.items() == ()


def test_ctrl_count_mismatch_does_not_fail() -> None:
    # 확장 제어문자 0개, CTRL_HEADER 2개(각주·머리말) → 대응 포기: 글자 뒤에 결과를 둔다
    recs = (
        _para(_text("본문"))
        + _note_ctrl("주석", 1)
        + [
            Record(HWPTAG_CTRL_HEADER, 1, CTRL_ID_HEADER + b"\x00" * 10),
            Record(HWPTAG_LIST_HEADER, 2, b"\x00" * 16),
            *_para(_text("머리말"), 2),
        ]
    )
    skips = SkipCounter()
    blocks = parse_blocks(recs, ctx=ReadContext(skips))
    assert blocks == [Paragraph("본문", 0, ("본문", NoteRef("footnote", 1)))]
    assert skips.items() == (("header_footer", 1),)


def test_ctrl_count_mismatch_extra_marks() -> None:
    # 확장 제어문자 2개, CTRL_HEADER 0개 → 글자만
    recs = _para(_text("앞", (17, CTRL_ID_FOOTNOTE), "뒤", (3, CTRL_ID_HYPERLINK)))
    assert parse_blocks(recs) == [Paragraph("앞뒤")]


def test_link_without_field_end_and_internal_link() -> None:
    cmd_web = build_ctrl_header_field(CTRL_ID_HYPERLINK, "https\\://a.example/x;1;0;0;")
    cmd_doc = build_ctrl_header_field(CTRL_ID_HYPERLINK, "?책갈피;0;0;0;")
    recs = _para(
        _text(
            (3, CTRL_ID_HYPERLINK),
            "안쪽",
            (4, CTRL_ID_HYPERLINK),
            " ",
            (3, CTRL_ID_HYPERLINK),
            "끝",
        )
    ) + [Record(HWPTAG_CTRL_HEADER, 1, cmd_doc), Record(HWPTAG_CTRL_HEADER, 1, cmd_web)]
    assert parse_blocks(recs) == [
        Paragraph("안쪽 끝", 0, ("안쪽 ", Link("끝", "https://a.example/x")))
    ]


def test_field_text_preserved() -> None:
    recs = _para(_text("이름: ", (3, CTRL_ID_CLICK_HERE), "값", (4, CTRL_ID_CLICK_HERE))) + [
        Record(HWPTAG_CTRL_HEADER, 1, build_ctrl_header_field(CTRL_ID_CLICK_HERE, "x"))
    ]
    assert parse_blocks(recs) == [Paragraph("이름: 값")]


def test_memo_list_counted() -> None:
    recs = _para(_text("본문")) + [
        Record(HWPTAG_MEMO_LIST, 0, struct.pack("<I", 1)),
        Record(HWPTAG_LIST_HEADER, 1, b"\x00" * 16),
        *_para(_text("메모 글"), 1),
        Record(HWPTAG_MEMO_LIST, 0, struct.pack("<I", 2)),
        Record(HWPTAG_LIST_HEADER, 1, b"\x00" * 16),
        *_para(_text("메모 글 2"), 1),
    ]
    skips = SkipCounter()
    assert parse_blocks(recs, ctx=ReadContext(skips)) == [Paragraph("본문")]
    assert skips.items() == (("memo", 2),)


@pytest.mark.parametrize(
    ("command", "expected"),
    [
        ("https\\://example.org/a b;1;0;0;", "https://example.org/a b"),
        ("mailto\\:a@b.example;2;0;0", "mailto:a@b.example"),
        ("https\\://x.example/\\?q=1|툴팁;1;0;0;", "https://x.example/?q=1"),
        ("?책갈피;0;0;0;", None),
        (";1;0;0;", None),
        ("javascript\\:alert(1);1;0;0;", "javascript:alert(1)"),
        ("http\\://no-tail.example", "http://no-tail.example"),
    ],
)
def test_hyperlink_url(command: str, expected: str | None) -> None:
    assert hyperlink_url(command) == expected


def test_field_command_and_eqedit_parsers() -> None:
    assert parse_field_command(build_ctrl_header_field(CTRL_ID_HYPERLINK, "abc;1;0;0;")) == (
        "abc;1;0;0;"
    )
    assert parse_field_command(CTRL_ID_HYPERLINK) == ""
    assert parse_eqedit_script(build_eqedit("a over b")) == "a over b"
    assert parse_eqedit_script(b"\x00" * 5) == ""


def test_decode_para_runs_marks_and_text_unchanged() -> None:
    payload = _text(
        " 앞",
        (9, b"\x00" * 4),
        (3, CTRL_ID_HYPERLINK),
        "링크",
        (4, CTRL_ID_HYPERLINK),
        (17, CTRL_ID_FOOTNOTE),
        "뒤 ",
    )
    runs = decode_para_runs(payload)
    assert runs == [" 앞 ", CtrlMark(3), "링크", CtrlMark(4), CtrlMark(17), "뒤 "]
    assert decode_para_text(payload) == "앞 링크뒤"


def test_equation_display_block(tmp_path: Path) -> None:
    items, _, _ = EXT_FIXTURES["equation_display"]
    assert read_blocks(build_hwp5(items)) == [  # type: ignore[arg-type]
        Paragraph("a over b", 0, (Math("a over b", "\\frac{a}{b}"),))
    ]


def test_link_and_note_in_same_paragraph_keep_order() -> None:
    items = [SynthRich((SynthLink("링크", "https://e.example"), SynthNote(("주",)), "끝"))]
    blocks = read_blocks(build_hwp5(items))
    assert blocks[0] == Paragraph(
        "링크끝", 0, (Link("링크", "https://e.example"), NoteRef("footnote", 1), "끝")
    )
