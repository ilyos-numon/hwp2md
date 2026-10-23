"""HWPX 개체: 표 칸 그림·캡션·도형 글상자·묶음·차트·OLE·글맵시·양식 개체."""

from pathlib import Path

import pytest
from lxml import etree

from hwp2md.blocks import Image, NoteRef, Paragraph, Table
from hwp2md.convert import convert
from hwp2md.hwpx import reader
from hwp2md.hwpx.bindata import BinItemStore
from hwp2md.hwpx.body import CellSpec, DocContext, _place_cells, parse_section
from hwp2md.hwpx.header import EMPTY_HEADER
from hwp2md.hwpx.reader import NS_HP, NS_HS, parse_section_xml
from synth_hwp5 import FIXTURE_ITEMS_IMAGE_MISSING, PNG_1X1
from synth_hwpx import XML_DECL, build_hwpx, build_zip, hwpx_entries, write_hwpx
from synth_items import EXT_FIXTURES, EXT_IDS_BY_STAGE, SynthChart
from synth_ole import build_ole_cfb, chart_xml, hwpx_ole_entry, ole10_native

NS_HC = "http://www.hancom.co.kr/hwpml/2011/core"
OBJECT_IDS = EXT_IDS_BY_STAGE["objects"]


def _sec(inner: str) -> etree._Element:
    return parse_section_xml(
        (
            f'<hs:sec xmlns:hp="{NS_HP}" xmlns:hs="{NS_HS}" xmlns:hc="{NS_HC}">{inner}</hs:sec>'
        ).encode()
    )


def _p(*runs: str) -> str:
    return "<hp:p>" + "".join(f"<hp:run>{r}</hp:run>" for r in runs) + "</hp:p>"


def _t(text: str) -> str:
    return f"<hp:t>{text}</hp:t>"


def _pic(ref: str, caption: str = "") -> str:
    cap = f"<hp:caption><hp:subList>{_p(_t(caption))}</hp:subList></hp:caption>" if caption else ""
    return f'<hp:pic>{cap}<hc:img binaryItemIDRef="{ref}"/></hp:pic>'


def _box(tag: str, *paras: str) -> str:
    return (
        f"<hp:{tag}><hp:drawText><hp:subList>{''.join(paras)}</hp:subList></hp:drawText></hp:{tag}>"
    )


def _tbl(*cells: str) -> str:
    tcs = "".join(
        f'<hp:tc><hp:subList>{c}</hp:subList><hp:cellAddr colAddr="{i}" rowAddr="0"/></hp:tc>'
        for i, c in enumerate(cells)
    )
    return f'<hp:tbl rowCnt="1" colCnt="{len(cells)}"><hp:tr>{tcs}</hp:tr></hp:tbl>'


def _store(
    entries: dict[str, bytes] | None = None, charts: dict[str, bytes] | None = None
) -> BinItemStore:
    base = {"BinData/image1.png": PNG_1X1, "BinData/image2.png": PNG_1X1 + b"2"}
    return BinItemStore({}, {**base, **(entries or {})}, charts)


def _parse(inner: str, store: BinItemStore | None = None) -> tuple[list[object], DocContext]:
    ctx = DocContext()
    blocks = parse_section(_sec(inner), EMPTY_HEADER, store or _store(), ctx)
    return [*blocks, *ctx.note_blocks()], ctx


# --- 합성 fixture (세 포맷 공용 기대값) ---


@pytest.mark.parametrize("fixture_id", [*OBJECT_IDS, "header_image"])
def test_object_fixtures_markdown_and_skipped(tmp_path: Path, fixture_id: str) -> None:
    items, expected_md, expected_skipped = EXT_FIXTURES[fixture_id]
    src = write_hwpx(tmp_path / "doc.hwpx", items)  # type: ignore[arg-type]
    result = convert(src, tmp_path / "out")
    assert result.markdown == expected_md
    assert result.skipped == expected_skipped


def test_object_ids_are_four() -> None:
    assert OBJECT_IDS == ["textbox", "caption", "chart", "chart_legacy"]


def test_textbox_fixture_image_file_and_counts(tmp_path: Path) -> None:
    items, _, _ = EXT_FIXTURES["textbox"]
    result = convert(write_hwpx(tmp_path / "doc.hwpx", items), tmp_path / "out")  # type: ignore[arg-type]
    assert [p.name for p in result.image_files] == ["img_001.png"]
    assert (result.paragraph_count, result.image_count) == (3, 1)


def test_chart_fixture_counts_one_table(tmp_path: Path) -> None:
    items, _, _ = EXT_FIXTURES["chart"]
    result = convert(write_hwpx(tmp_path / "doc.hwpx", items), tmp_path / "out")  # type: ignore[arg-type]
    assert result.table_count == 1


def test_header_image_not_output(tmp_path: Path) -> None:
    items, _, _ = EXT_FIXTURES["header_image"]
    result = convert(write_hwpx(tmp_path / "doc.hwpx", items), tmp_path / "out")  # type: ignore[arg-type]
    assert result.image_files == ()


def test_synth_chart_entries() -> None:
    chart = SynthChart("실적", ("1월",), (("매출", ("10",)),))
    legacy = SynthChart("옛", ("1월",), (("매출", ("10",)),), legacy=True)
    entries = hwpx_entries([chart, legacy])  # type: ignore[list-item]
    assert entries["Chart/chart1.xml"] == chart_xml("실적", ("1월",), (("매출", ("10",)),))
    assert "BinData/ole2.ole" in entries
    assert b'id="ole2"' in entries["Contents/content.hpf"]
    assert b'chartIDRef="Chart/chart1.xml"' in entries["Contents/section0.xml"]
    assert b'binaryItemIDRef="ole2"' in entries["Contents/section0.xml"]


# --- 표 칸 ---


def test_cell_image_becomes_cell_inline_and_consumes_number() -> None:
    blocks, _ = _parse(
        _p(_tbl(_p(_pic("image1")) + _p(_t("값")), _p(_t("나")))) + _p(_pic("image2"))
    )
    img1 = Image("img_001.png", PNG_1X1)
    assert blocks == [
        Table([["값", "나"]], ((((img1, "\n값"), ("나",)),))),
        Image("img_002.png", PNG_1X1 + b"2"),
    ]


def test_cell_footnote_ref_visible_in_cell() -> None:
    note = (
        "<hp:ctrl><hp:footNote><hp:subList>"
        + _p(_t("주석"))
        + "</hp:subList></hp:footNote></hp:ctrl>"
    )
    blocks, _ = _parse(_p(_tbl(_p(_t("가") + note))))
    table = blocks[0]
    assert isinstance(table, Table)
    assert table.rows == [["가"]]
    assert table.cells == ((("가", NoteRef("footnote", 1)),),)


def test_cell_footnote_markdown(tmp_path: Path) -> None:
    note = (
        "<hp:ctrl><hp:footNote><hp:subList>"
        + _p(_t("주석"))
        + "</hp:subList></hp:footNote></hp:ctrl>"
    )
    section = (
        XML_DECL
        + f'<hs:sec xmlns:hp="{NS_HP}" xmlns:hs="{NS_HS}" xmlns:hc="{NS_HC}">'
        + _p(_tbl(_p(_t("가") + note)))
        + "</hs:sec>"
    ).encode()
    entries = hwpx_entries(["x"])
    entries["Contents/section0.xml"] = section
    src = tmp_path / "doc.hwpx"
    src.write_bytes(build_zip(entries))
    md = convert(src, tmp_path / "out").markdown
    assert "| 가[^1] |" in md
    assert md.endswith("[^1]: 주석\n")


def test_nested_table_in_cell_flattens_and_images_go_to_end() -> None:
    inner = _tbl(_p(_t("안1")), _p(_t("안2") + _pic("image1")))
    blocks, _ = _parse(_p(_tbl(_p(_t("앞")) + _p(inner) + _p(_t("뒤")))))
    img = Image("img_001.png", PNG_1X1)
    assert blocks == [Table([["앞\n안1 안2\n뒤"]], (((("앞\n안1 안2\n뒤", img),),)))]


def test_text_only_cells_keep_plain_table() -> None:
    blocks, _ = _parse(_p(_tbl(_p(_t("a")) + _p(_t("b")), _p(_t("c")))))
    assert blocks == [Table([["a\nb", "c"]])]


def test_place_cells_signature_unchanged() -> None:
    cells = [CellSpec(0, 0, 1, 2, "a"), CellSpec(1, 0, 1, 1, "b"), CellSpec(1, 1, 1, 1, "c")]
    assert _place_cells(2, 2, cells) == [["a", ""], ["b", "c"]]


# --- 캡션 ---


def test_table_caption_after_table() -> None:
    cap = "<hp:caption><hp:subList>" + _p(_t("표 캡션")) + "</hp:subList></hp:caption>"
    tbl = _tbl(_p(_t("값"))).replace("<hp:tr>", cap + "<hp:tr>", 1)
    blocks, _ = _parse(_p(_t("앞"), tbl))
    assert blocks == [Paragraph("앞"), Table([["값"]]), Paragraph("표 캡션")]


def test_picture_caption_after_image() -> None:
    blocks, _ = _parse(_p(_pic("image1", caption="그림 캡션")))
    assert blocks == [Image("img_001.png", PNG_1X1), Paragraph("그림 캡션")]


# --- 도형·묶음 ---


@pytest.mark.parametrize("tag", ["rect", "ellipse", "arc", "polygon", "curve", "connectLine"])
def test_shape_draw_text_after_anchor_paragraph(tag: str) -> None:
    blocks, _ = _parse(_p(_box(tag, _p(_t("상자")), _p(_pic("image1"))), _t("앵커")))
    assert blocks == [Paragraph("앵커"), Paragraph("상자"), Image("img_001.png", PNG_1X1)]


def test_shape_without_draw_text_ignored() -> None:
    blocks, _ = _parse(_p("<hp:rect/><hp:line/>", _t("글")))
    assert blocks == [Paragraph("글")]


def test_container_children_in_storage_order() -> None:
    con = (
        "<hp:container>"
        + _box("rect", _p(_t("가")))
        + _pic("image1")
        + "<hp:container>"
        + _box("polygon", _p(_t("나")))
        + _pic("image2")
        + "</hp:container><hp:line/></hp:container>"
    )
    blocks, _ = _parse(_p(con, _t("앵커")))
    assert blocks == [
        Paragraph("앵커"),
        Paragraph("가"),
        Image("img_001.png", PNG_1X1),
        Paragraph("나"),
        Image("img_002.png", PNG_1X1 + b"2"),
    ]


def test_pending_objects_flush_before_split_table() -> None:
    blocks, _ = _parse(_p(_box("rect", _p(_t("상자"))), _t("앞"), _tbl(_p(_t("칸")))))
    assert blocks == [Paragraph("앞"), Paragraph("상자"), Table([["칸"]])]


# --- 차트·OLE ---


def test_chart_entry_to_blocks() -> None:
    xml = chart_xml("제목", ("A",), (("S", ("1",)),))
    store = _store(charts={"Chart/chart1.xml": xml})
    blocks, ctx = _parse(_p('<hp:chart chartIDRef="Chart/chart1.xml"/>'), store)
    assert blocks == [Paragraph("차트: 제목"), Table([["항목", "S"], ["A", "1"]])]
    assert ctx.skips.items() == ()


@pytest.mark.parametrize(
    "charts", [{}, {"Chart/chart1.xml": b"<not-a-chart/>"}], ids=["missing", "bad"]
)
def test_chart_unreadable_is_chart_legacy(charts: dict[str, bytes]) -> None:
    blocks, ctx = _parse(
        _p('<hp:chart chartIDRef="Chart/chart1.xml"/>', _t("글")), _store(charts=charts)
    )
    assert blocks == [Paragraph("글")]
    assert ctx.skips.items() == (("chart_legacy", 1),)


def test_ole_native_png_becomes_image_numbered_in_order() -> None:
    cfb = build_ole_cfb({"\x01Ole10Native": ole10_native(PNG_1X1 + b"o")})
    store = _store({"BinData/ole1.ole": hwpx_ole_entry(cfb)})
    blocks, ctx = _parse(_p('<hp:ole binaryItemIDRef="ole1"/>') + _p(_pic("image1")), store)
    assert blocks == [Image("img_001.png", PNG_1X1 + b"o"), Image("img_002.png", PNG_1X1)]
    assert ctx.skips.items() == ()


def test_ole_chart_stream_to_blocks() -> None:
    xml = chart_xml("", ("A",), (("S", ("1",)),))
    cfb = build_ole_cfb({"OOXMLChartContents": xml})
    store = _store({"BinData/ole1.ole": hwpx_ole_entry(cfb)})
    blocks, _ = _parse(_p('<hp:ole binaryItemIDRef="ole1"/>'), store)
    assert blocks == [Paragraph("차트"), Table([["항목", "S"], ["A", "1"]])]


@pytest.mark.parametrize(
    ("entries", "kind"),
    [
        ({}, "ole"),
        ({"BinData/ole1.ole": b"not cfb"}, "ole"),
        ({"BinData/ole1.ole": hwpx_ole_entry(build_ole_cfb({"Other": b"x"}))}, "ole"),
        ({"BinData/ole1.ole": hwpx_ole_entry(build_ole_cfb({"Contents": b"x"}))}, "chart_legacy"),
    ],
    ids=["missing", "not_cfb", "other", "legacy"],
)
def test_ole_skipped_kinds(entries: dict[str, bytes], kind: str) -> None:
    blocks, ctx = _parse(_p('<hp:ole binaryItemIDRef="ole1"/>', _t("글")), _store(entries))
    assert blocks == [Paragraph("글")]
    assert ctx.skips.items() == ((kind, 1),)


def test_reader_loads_chart_entries_with_size_limit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    items, _, _ = EXT_FIXTURES["chart"]
    src = tmp_path / "doc.hwpx"
    src.write_bytes(build_hwpx(items))  # type: ignore[arg-type]
    assert list(reader.read_hwpx_package(src).charts) == ["Chart/chart1.xml"]
    monkeypatch.setattr(reader, "MAX_OLE_BYTES", 10)
    counter = reader.SkipCounter()
    assert reader.read_blocks(src, skips=counter) == []
    assert counter.items() == (("chart_legacy", 1),)


# --- 글맵시·양식 개체·본체 없는 그림 ---


def test_textart_and_form_controls_counted() -> None:
    forms = "".join(
        f"<hp:{t}/>"
        for t in ("btn", "checkBtn", "radioBtn", "comboBox", "listBox", "edit", "scrollBar")
    )
    blocks, ctx = _parse(
        _p(
            '<hp:textart text="글맵시"/>',
            forms,
            "<hp:container><hp:textart/></hp:container>",
            _t("글"),
        )
    )
    assert blocks == [Paragraph("글")]
    assert ctx.skips.items() == (("textart", 2), ("form_control", 7))


def test_unresolvable_picture_counted_image_missing() -> None:
    blocks, ctx = _parse(_p(_pic("nope"), "<hp:pic/>", _t("글")))
    assert blocks == [Paragraph("글")]
    assert ctx.skips.items() == (("image_missing", 2),)


def test_missing_image_fixture_reports_image_missing(tmp_path: Path) -> None:
    result = convert(
        write_hwpx(tmp_path / "doc.hwpx", FIXTURE_ITEMS_IMAGE_MISSING), tmp_path / "out"
    )
    assert result.skipped == (("image_missing", 1),)


def test_header_picture_not_counted_missing() -> None:
    hdr = (
        "<hp:ctrl><hp:header><hp:subList>"
        + _p(_pic("nope"))
        + "</hp:subList></hp:header></hp:ctrl>"
    )
    _, ctx = _parse(_p(hdr, _t("본문")))
    assert ctx.skips.items() == (("header_footer", 1),)
