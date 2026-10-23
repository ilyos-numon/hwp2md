"""HWPML 요소: 링크·각주·수식·필드, 머리말·숨은 설명, 글상자·묶음·캡션·OLE, 칸 그림, 목록."""

from pathlib import Path

import pytest

from hwp2md.blocks import Image, ListInfo, Paragraph, Table
from hwp2md.convert import convert
from hwp2md.hwpml.body import to_num_format
from hwp2md.hwpml.reader import read_blocks
from hwp2md.skips import SkipCounter
from synth_hwp5 import (
    FIXTURE_IMAGE_JPG,
    FIXTURE_IMAGE_PNG,
    JPEG_STUB,
    PNG_1X1,
    SynthCell,
    SynthTable,
)
from synth_hwpml import build_hwpml, hwpml_text, write_hwpml
from synth_items import EXT_FIXTURES, SynthChart, SynthListPara, SynthNote, SynthRich
from synth_ole import build_ole_cfb, hwpx_ole_entry, ole10_native


def test_ext_fixture_ids_are_sixteen() -> None:
    assert len(EXT_FIXTURES) == 16


@pytest.mark.parametrize("fixture_id", list(EXT_FIXTURES))
def test_ext_fixtures_markdown_and_skipped(tmp_path: Path, fixture_id: str) -> None:
    items, expected_md, expected_skipped = EXT_FIXTURES[fixture_id]
    src = write_hwpml(tmp_path / "doc.hml", items)  # type: ignore[arg-type]
    result = convert(src, tmp_path / "out")
    assert result.markdown == expected_md
    assert result.skipped == expected_skipped
    expected_files = ("img_001.png",) if fixture_id == "textbox" else ()
    assert tuple(p.name for p in result.image_files) == expected_files


def test_header_counted_into_given_counter() -> None:
    items, _, expected = EXT_FIXTURES["header"]
    counter = SkipCounter()
    read_blocks(build_hwpml(items), skips=counter)  # type: ignore[arg-type]
    assert counter.items() == expected


# --- 칸 그림 ---


def test_cell_image_is_inline_and_consumes_number(tmp_path: Path) -> None:
    items = [
        SynthTable(
            rows=1,
            cols=2,
            cells=(
                SynthCell((FIXTURE_IMAGE_JPG, "값"), col=0, row=0),
                SynthCell(("나",), col=1, row=0),
            ),
        ),
        FIXTURE_IMAGE_PNG,
    ]
    result = convert(write_hwpml(tmp_path / "doc.hml", items), tmp_path / "out")
    assert result.markdown == (
        "| ![그림 1](doc_images/img_001.jpg)<br>값 | 나 |\n|---|---|\n\n"
        "![그림 2](doc_images/img_002.png)\n"
    )
    assert result.image_count == 2
    assert [p.name for p in result.image_files] == ["img_001.jpg", "img_002.png"]
    blocks = read_blocks(build_hwpml(items))
    assert blocks[0] == Table(
        [["값", "나"]],
        ((((Image("img_001.jpg", JPEG_STUB), "\n값")), ("나",)),),
    )


def test_text_only_table_has_no_cells() -> None:
    items = [SynthTable(rows=1, cols=1, cells=(SynthCell(("가",), 0, 0),))]
    assert read_blocks(build_hwpml(items)) == [Table([["가"]])]


# --- 목록 ---


def test_nested_numbers_reset_lower_level(tmp_path: Path) -> None:
    items = [
        SynthListPara("가", "number"),
        SynthListPara("가1", "number", depth=1, template="^2."),
        SynthListPara("가2", "number", depth=1, template="^2."),
        SynthListPara("나", "number"),
        SynthListPara("나1", "number", depth=1, template="^2."),
    ]
    blocks = read_blocks(build_hwpml(items))
    assert [b.list_info for b in blocks if isinstance(b, Paragraph)] == [
        ListInfo("number", 0, "1."),
        ListInfo("number", 1, "1."),
        ListInfo("number", 1, "2."),
        ListInfo("number", 0, "2."),
        ListInfo("number", 1, "1."),
    ]


def test_number_format_and_template() -> None:
    xml = hwpml_text([SynthListPara("가", "number", template="(^1)")])
    xml = xml.replace('NumFormat="Digit">(^1)', 'NumFormat="HangulSyllable">(^1)', 1)
    blocks = read_blocks(xml.encode())
    assert blocks == [Paragraph("가", list_info=ListInfo("number", 0, "(가)"))]


def test_to_num_format() -> None:
    assert to_num_format("Digit") == "DIGIT"
    assert to_num_format("HangulSyllable") == "HANGUL_SYLLABLE"
    assert to_num_format("CircledDigit") == "CIRCLED_DIGIT"
    assert to_num_format("RomanSmall") == "ROMAN_SMALL"
    assert to_num_format("Ideograph") == "HANJA_DIGIT"
    assert to_num_format("Unknown") == "DIGIT"
    assert to_num_format(None) == "DIGIT"


def test_bullet_list_info() -> None:
    blocks = read_blocks(build_hwpml([SynthListPara("하나", "bullet", depth=2)]))
    assert blocks == [Paragraph("하나", list_info=ListInfo("bullet", 2, ""))]


# --- 각주 ---


def test_note_inside_note_is_dropped() -> None:
    xml = hwpml_text([SynthRich(("가", SynthNote(("바깥",))))])
    inner = "<FOOTNOTE><PARALIST><P><TEXT><CHAR>안</CHAR></TEXT></P></PARALIST></FOOTNOTE>"
    xml = xml.replace("<CHAR>바깥</CHAR>", "<CHAR>바깥</CHAR>" + inner, 1)
    result = read_blocks(xml.encode())
    assert len(result) == 2
    note = result[1]
    assert note.kind == "footnote"  # type: ignore[union-attr]
    assert [p.text for p in note.paragraphs] == ["바깥"]  # type: ignore[union-attr]


def test_link_closed_only_by_hyperlink_fieldend(tmp_path: Path) -> None:
    body = (
        '<P><TEXT><FIELDBEGIN Type="Hyperlink" Command="https\\://a.example/;1;0;0;"/>'
        '<CHAR>가</CHAR><FIELDBEGIN Type="ClickHere"/><CHAR>나</CHAR><FIELDEND Type="ClickHere"/>'
        '<CHAR>다</CHAR><FIELDEND Type="Hyperlink"/><CHAR> 끝</CHAR></TEXT></P>'
    )
    data = f'<HWPML Version="2.1"><BODY><SECTION>{body}</SECTION></BODY></HWPML>'.encode()
    src = tmp_path / "doc.hml"
    src.write_bytes(data)
    assert convert(src, tmp_path / "out").markdown == "[가나다](https://a.example/) 끝\n"


def test_bookmark_link_is_text() -> None:
    body = (
        '<P><TEXT><FIELDBEGIN Type="Hyperlink" Command="?책갈피;0;0;0;"/>'
        '<CHAR>안쪽</CHAR><FIELDEND Type="Hyperlink"/></TEXT></P>'
    )
    data = f'<HWPML Version="2.1"><BODY><SECTION>{body}</SECTION></BODY></HWPML>'.encode()
    assert read_blocks(data) == [Paragraph("안쪽")]


# --- 개체 ---


def _doc(body: str, bins: list[bytes] = ()) -> bytes:  # type: ignore[assignment]
    import base64

    items = "".join(
        f'<BINITEM Type="Embedding" BinData="{k}" Format="ole"/>' for k in range(1, len(bins) + 1)
    )
    datas = "".join(
        f'<BINDATA Id="{k}" Encoding="Base64">{base64.b64encode(b).decode()}</BINDATA>'
        for k, b in enumerate(bins, 1)
    )
    return (
        f'<HWPML Version="2.1"><HEAD><MAPPINGTABLE><BINDATALIST>{items}</BINDATALIST>'
        f"</MAPPINGTABLE></HEAD><BODY><SECTION>{body}</SECTION></BODY>"
        f"<TAIL><BINDATASTORAGE>{datas}</BINDATASTORAGE></TAIL></HWPML>"
    ).encode()


def _para(text: str) -> str:
    return f"<P><TEXT><CHAR>{text}</CHAR></TEXT></P>"


def test_container_children_in_order() -> None:
    rect = (
        "<RECTANGLE><DRAWINGOBJECT><DRAWTEXT><PARALIST>"
        + _para("상자")
        + "</PARALIST></DRAWTEXT></DRAWINGOBJECT></RECTANGLE>"
    )
    ellipse = "<ELLIPSE><DRAWTEXT><PARALIST>" + _para("타원") + "</PARALIST></DRAWTEXT></ELLIPSE>"
    inner = f"<CONTAINER>{ellipse}</CONTAINER>"
    body = f"<P><TEXT><CHAR>앞</CHAR><CONTAINER>{rect}{inner}</CONTAINER><CHAR>뒤</CHAR></TEXT></P>"
    assert read_blocks(_doc(body)) == [
        Paragraph("앞"),
        Paragraph("상자"),
        Paragraph("타원"),
        Paragraph("뒤"),
    ]


def test_ole_native_image_and_prefixed_cfb() -> None:
    cfb = build_ole_cfb({"\x01Ole10Native": ole10_native(PNG_1X1)})
    body = '<P><TEXT><OLE BinItem="1"/></TEXT></P>'
    assert read_blocks(_doc(body, [hwpx_ole_entry(cfb)])) == [Image("img_001.png", PNG_1X1)]


def test_ole_unknown_and_missing_are_skipped() -> None:
    cfb = build_ole_cfb({"Other": b"x" * 8})
    body = '<P><TEXT><OLE BinItem="1"/><OLE BinItem="9"/><OLE/></TEXT></P>'
    counter = SkipCounter()
    assert read_blocks(_doc(body, [cfb]), skips=counter) == []
    assert counter.items() == (("ole", 3),)


def test_chart_in_cell_flattens_to_text() -> None:
    xml = hwpml_text([SynthChart("실적", ("1월",), (("매출", ("10",)),))])
    ole = xml[xml.index("<OLE ") : xml.index("</OLE>") + len("</OLE>")]
    table = SynthTable(rows=1, cols=1, cells=(SynthCell(("자리",), 0, 0),))
    doc = hwpml_text([table, SynthChart("실적", ("1월",), (("매출", ("10",)),))])
    doc = doc.replace("<CHAR>자리</CHAR>", ole, 1)
    blocks = read_blocks(doc.encode())
    assert blocks[0] == Table([["차트: 실적\n항목 매출 1월 10"]])


def test_textart_and_form_controls_are_skipped() -> None:
    body = '<P><TEXT><CHAR>가</CHAR><TEXTART Text="글"/><CHECKBUTTON/><EDIT/></TEXT></P>'
    counter = SkipCounter()
    assert read_blocks(_doc(body), skips=counter) == [Paragraph("가")]
    assert counter.items() == (("textart", 1), ("form_control", 2))


def test_picture_caption_after_image() -> None:
    xml = hwpml_text([FIXTURE_IMAGE_PNG])
    cap = '<CAPTION Side="Bottom"><PARALIST>' + _para("그림 설명") + "</PARALIST></CAPTION>"
    xml = xml.replace(
        '<SIZE Height="3382" Width="8196"/></SHAPEOBJECT>', "<SIZE/>" + cap + "</SHAPEOBJECT>", 1
    )
    assert read_blocks(xml.encode()) == [Image("img_001.png", PNG_1X1), Paragraph("그림 설명")]
