import base64
import re
import zlib
from pathlib import Path

import pytest

from hwp2md import Hwp2mdError, NotHwpFileError, convert, detect_format
from hwp2md.blocks import Image, Paragraph, Table
from hwp2md.cli import main
from hwp2md.convert import read_blocks
from hwp2md.hwpml.reader import (
    MAX_BINDATA_BYTES,
    looks_like_hwpml,
    prepare_xml,
)
from hwp2md.hwpml.reader import read_blocks as read_hwpml_blocks
from hwp2md.memory import convert_bytes
from hwp2md.skips import SkipCounter
from synth_hwp5 import (
    FIXTURE_IMAGE_PNG,
    FIXTURE_ITEMS_HEADING_EDGE,
    FIXTURE_ITEMS_HEADING_IN_CELL,
    FIXTURE_ITEMS_HEADINGS,
    FIXTURE_ITEMS_MERGED,
    FIXTURE_ITEMS_WITH_TABLE,
    FIXTURE_PARAGRAPHS,
    IMAGE_FIXTURES,
    PNG_1X1,
    Item,
    SynthCell,
    SynthHeading,
    SynthTable,
)
from synth_hwpml import build_hwpml, hwpml_text, write_hwpml
from synth_hwpx import FIXTURE_PARAGRAPHS_INLINE, write_hwpx

BASIC_ITEMS: list[Item] = [
    SynthHeading("제목", 1),
    "본문",
    SynthTable(rows=1, cols=2, cells=(SynthCell(("가",), 0, 0), SynthCell(("나",), 1, 0))),
    FIXTURE_IMAGE_PNG,
]
BASIC_MARKDOWN = "# 제목\n\n본문\n\n| 가 | 나 |\n|---|---|\n\n![그림 1](doc_images/img_001.png)\n"


# --- 판별 ---


def test_hwpml_with_hwp_extension_is_hwpml(tmp_path: Path) -> None:
    src = tmp_path / "a.hwp"
    src.write_bytes(b'<?xml version="1.0" encoding="UTF-8"?><HWPML Version="2.1"><HEAD/></HWPML>')
    assert detect_format(src) == "hwpml"


def test_other_xml_is_not_hwp() -> None:
    with pytest.raises(NotHwpFileError):
        detect_format(b'<?xml version="1.0"?><root/>')


@pytest.mark.parametrize("encoding", ["utf-8", "utf-16-le", "utf-16-be"])
def test_detect_hwpml_encodings_and_doctype(encoding: str) -> None:
    data = build_hwpml(BASIC_ITEMS, encoding=encoding, doctype_nbsp=True)
    assert detect_format(data) == "hwpml"


def test_looks_like_hwpml_edges() -> None:
    assert looks_like_hwpml(b"\xef\xbb\xbf<!-- c --><?pi x?>\n<HWPML>")
    assert not looks_like_hwpml(b"<HWPMLX/>")
    assert not looks_like_hwpml(b"<root><HWPML/></root>")
    assert not looks_like_hwpml(b"\x00\x01\x02")
    assert not looks_like_hwpml(b"")


# --- 본문·제목·표·그림 ---


def test_basic_document_markdown(tmp_path: Path) -> None:
    src = write_hwpml(tmp_path / "doc.hml", BASIC_ITEMS)
    result = convert(src, tmp_path / "out")
    assert result.markdown == BASIC_MARKDOWN
    assert (tmp_path / "out" / "doc_images" / "img_001.png").read_bytes() == PNG_1X1
    hwpx = convert(write_hwpx(tmp_path / "x" / "doc.hwpx", BASIC_ITEMS), tmp_path / "outx")
    assert result.markdown == hwpx.markdown


def test_read_blocks_values() -> None:
    blocks = read_blocks(build_hwpml(BASIC_ITEMS))
    assert blocks == [
        Paragraph("제목", 1),
        Paragraph("본문"),
        Table([["가", "나"]]),
        Image("img_001.png", PNG_1X1),
    ]


def test_inline_elements() -> None:
    xml = hwpml_text(["x"]).replace(
        "<CHAR>x</CHAR>",
        "<CHAR>a<TAB/>b<NBSPACE/>c<FWSPACE/>d<HYPEN/>e<LINEBREAK/>f<MARKPENBEGIN/>g</CHAR>",
    )
    assert read_blocks(xml.encode()) == [Paragraph("a b c d-e\nfg")]


def test_multiple_text_runs_and_sections() -> None:
    xml = hwpml_text(["x"]).replace(
        '<TEXT CharShape="0"><CHAR>x</CHAR></TEXT>',
        '<TEXT CharShape="0"><CHAR>가</CHAR></TEXT><TEXT CharShape="1"><CHAR>나</CHAR></TEXT>',
    )
    xml = xml.replace(
        "</SECTION>",
        '</SECTION><SECTION Id="1"><P ParaShape="0"><TEXT><CHAR>다</CHAR></TEXT></P></SECTION>',
    )
    assert read_blocks(xml.encode()) == [Paragraph("가나"), Paragraph("다")]


@pytest.mark.parametrize(
    "items",
    [
        FIXTURE_PARAGRAPHS,
        FIXTURE_PARAGRAPHS_INLINE,
        FIXTURE_ITEMS_WITH_TABLE,
        FIXTURE_ITEMS_MERGED,
        FIXTURE_ITEMS_HEADINGS,
        FIXTURE_ITEMS_HEADING_EDGE,
        FIXTURE_ITEMS_HEADING_IN_CELL,
    ],
    ids=[
        "paragraphs",
        "inline",
        "with_table",
        "merged",
        "headings",
        "heading_edge",
        "heading_cell",
    ],
)
def test_same_markdown_as_hwpx(tmp_path: Path, items: list[Item]) -> None:
    ml = convert(write_hwpml(tmp_path / "doc.hml", items), tmp_path / "outml")
    x = convert(write_hwpx(tmp_path / "x" / "doc.hwpx", items), tmp_path / "outx")
    assert ml.markdown == x.markdown
    assert (ml.paragraph_count, ml.table_count, ml.heading_count) == (
        x.paragraph_count,
        x.table_count,
        x.heading_count,
    )


@pytest.mark.parametrize(
    ("items", "blocks", "markdown", "counts", "files"),
    IMAGE_FIXTURES,
    ids=["images", "reuse", "in_cell", "missing"],
)
def test_image_fixtures_same_as_hwpx(
    tmp_path: Path,
    items: list[Item],
    blocks: list[object],
    markdown: str,
    counts: tuple[int, int, int, int],
    files: tuple[str, ...],
) -> None:
    ml = convert(write_hwpml(tmp_path / "doc.hml", items), tmp_path / "outml")
    x = convert(write_hwpx(tmp_path / "x" / "doc.hwpx", items), tmp_path / "outx")
    assert ml.markdown == x.markdown
    assert ml.image_count == x.image_count
    assert [p.name for p in ml.image_files] == [p.name for p in x.image_files]


# --- BINDATA ---


def _b64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def _with_bindata(payload: bytes) -> bytes:
    xml = hwpml_text([FIXTURE_IMAGE_PNG])
    out, n = re.subn(r"(<BINDATA [^>]*>)[^<]*(</BINDATA>)", rf"\g<1>{_b64(payload)}\g<2>", xml)
    assert n == 1
    return out.encode()


def test_bindata_raw_deflate_is_decompressed() -> None:
    co = zlib.compressobj(9, zlib.DEFLATED, -15)
    packed = co.compress(PNG_1X1) + co.flush()
    assert read_blocks(_with_bindata(packed)) == [Image("img_001.png", PNG_1X1)]


def test_bindata_not_image_not_deflate_kept_as_is() -> None:
    raw = b"\x00\x01not-an-image\xff" * 3
    assert read_blocks(_with_bindata(raw)) == [Image("img_001.png", raw)]


def test_bindata_too_large(monkeypatch: pytest.MonkeyPatch) -> None:
    import hwp2md.hwpml.reader as reader

    monkeypatch.setattr(reader, "MAX_BINDATA_BYTES", 10)
    with pytest.raises(Hwp2mdError, match="binary item too large"):
        read_blocks(build_hwpml([FIXTURE_IMAGE_PNG]))
    assert MAX_BINDATA_BYTES == 52428800


def test_bindata_deflate_bomb_too_large(monkeypatch: pytest.MonkeyPatch) -> None:
    import hwp2md.hwpml.reader as reader

    co = zlib.compressobj(9, zlib.DEFLATED, -15)
    packed = co.compress(b"\x00" * 5000) + co.flush()
    monkeypatch.setattr(reader, "MAX_BINDATA_BYTES", 1000)
    with pytest.raises(Hwp2mdError, match="binary item too large"):
        read_blocks(_with_bindata(packed))


def test_link_picture_is_skipped_and_counted() -> None:
    data = build_hwpml(["앞", FIXTURE_IMAGE_PNG, "뒤"]).replace(
        b'Type="Embedding"', b'Type="Link" APath="C:\\\\a.png"'
    )
    skips = SkipCounter()
    assert read_hwpml_blocks(data, skips) == [Paragraph("앞"), Paragraph("뒤")]
    assert skips.items() == (("image_link", 1),)


def test_link_picture_counted_in_convert_result(tmp_path: Path) -> None:
    src = tmp_path / "doc.hml"
    src.write_bytes(build_hwpml([FIXTURE_IMAGE_PNG]).replace(b'"Embedding"', b'"Link"'))
    result = convert(src, tmp_path / "out")
    assert result.skipped == (("image_link", 1),)
    assert result.image_count == 0


# --- 엔티티·DTD ---


def test_nbsp_entity(tmp_path: Path) -> None:
    src = write_hwpml(tmp_path / "doc.hml", ["가\u00a0나"], doctype_nbsp=True)
    assert b"&nbsp;" in src.read_bytes()
    assert convert(src, tmp_path / "out").markdown == "가\u00a0나\n"


def test_nbsp_entity_in_attribute_and_table() -> None:
    items: list[Item] = [
        SynthTable(rows=1, cols=1, cells=(SynthCell(("a\u00a0b",), 0, 0),)),
    ]
    assert read_blocks(build_hwpml(items, doctype_nbsp=True)) == [Table([["a\u00a0b"]])]


@pytest.mark.parametrize(
    "doctype",
    [
        '<!DOCTYPE HWPML [<!ENTITY x SYSTEM "file:///etc/passwd">]>',
        '<!DOCTYPE HWPML [<!ENTITY x PUBLIC "-//x//EN" "http://example.invalid/x">]>',
        '<!DOCTYPE HWPML SYSTEM "http://example.invalid/hwpml.dtd">',
        '<!DOCTYPE HWPML PUBLIC "-//x//EN" "hwpml.dtd" [<!ENTITY nbsp "&#160;">]>',
        '<!DOCTYPE HWPML [<!ENTITY % p "x">]>',
        '<!DOCTYPE HWPML [<!ENTITY a "&b;">]>',
        '<!DOCTYPE HWPML [<!ENTITY a "<x/>">]>',
        "<!DOCTYPE HWPML [<!ELEMENT HWPML ANY>]>",
        '<!DOCTYPE HWPML [<!ENTITY nbsp "&#160;"> %p;]>',
    ],
    ids=["system", "public", "ext_subset", "ext_and_int", "param", "ref", "lt", "element", "peref"],
)
def test_unsupported_dtd_rejected(doctype: str) -> None:
    xml = hwpml_text(["가"]).replace("?>\n", "?>\n" + doctype, 1)
    with pytest.raises(Hwp2mdError, match="unsupported DTD in HWPML"):
        prepare_xml(xml.encode())
    with pytest.raises(Hwp2mdError, match="unsupported DTD in HWPML"):
        read_blocks(xml.encode())


def test_external_entity_cli_exit_1(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    xml = hwpml_text(["가&x;"]).replace(
        "?>\n", '?>\n<!DOCTYPE HWPML [<!ENTITY x SYSTEM "file:///etc/passwd">]>', 1
    )
    src = tmp_path / "x.hml"
    src.write_bytes(xml.replace("가&amp;x;", "가&x;").encode())
    assert main([str(src), "-o", str(tmp_path / "out")]) == 1
    err = capsys.readouterr().err
    assert "unsupported DTD in HWPML" in err
    assert "root:" not in err


def test_undeclared_entity_is_malformed() -> None:
    xml = hwpml_text(["가"]).replace("<CHAR>가</CHAR>", "<CHAR>가&nbsp;</CHAR>")
    with pytest.raises(Hwp2mdError):
        read_blocks(xml.encode())


def test_prepare_xml_outputs_utf8_without_doctype() -> None:
    out = prepare_xml(build_hwpml(["가\u00a0나"], encoding="utf-16-le", doctype_nbsp=True))
    text = out.decode("utf-8")
    assert "<!DOCTYPE" not in text
    assert "&nbsp;" not in text
    assert "UTF-16" not in text
    assert text.lstrip().startswith(("<?xml", "<HWPML"))


# --- 인코딩·크기 ---


@pytest.mark.parametrize("encoding", ["utf-16-le", "utf-16-be"])
def test_utf16_same_markdown(tmp_path: Path, encoding: str) -> None:
    utf8 = convert(write_hwpml(tmp_path / "a" / "doc.hml", BASIC_ITEMS), tmp_path / "o8")
    u16 = convert(
        write_hwpml(tmp_path / "b" / "doc.hml", BASIC_ITEMS, encoding=encoding),
        tmp_path / "o16",
    )
    assert u16.markdown == utf8.markdown == BASIC_MARKDOWN


def test_input_too_large(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import hwp2md.hwpml.reader as reader

    src = write_hwpml(tmp_path / "doc.hml", BASIC_ITEMS)
    monkeypatch.setattr(reader, "MAX_HWPML_BYTES", 100)
    with pytest.raises(Hwp2mdError, match="too large"):
        read_blocks(src)


def test_memory_api_reads_hwpml() -> None:
    result = convert_bytes(build_hwpml(BASIC_ITEMS), "doc.hml")
    assert result.markdown == BASIC_MARKDOWN
