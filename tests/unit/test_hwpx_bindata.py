from pathlib import Path

import pytest
from lxml import etree

import synth_hwpx
from hwp2md.blocks import Block, Image, Paragraph
from hwp2md.errors import Hwp2mdError
from hwp2md.hwpx import bindata, body, reader
from hwp2md.hwpx.bindata import BinItemStore, parse_manifest
from hwp2md.hwpx.body import NS_HC, parse_paragraph, parse_section
from hwp2md.hwpx.header import EMPTY_HEADER
from hwp2md.hwpx.reader import NS_HP, NS_HS, parse_section_xml, read_hwpx_package
from synth_hwp5 import FIXTURE_ITEMS_IMAGES, IMAGE_FIXTURES, JPEG_STUB, PNG_1X1, Item
from synth_hwpx import hwpx_entries, write_hwpx

XML_DECL = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'


def _sec(inner: str) -> etree._Element:
    return parse_section_xml(
        (
            XML_DECL + f'<hs:sec xmlns:hp="{NS_HP}" xmlns:hs="{NS_HS}" xmlns:hc="{NS_HC}">'
            f"{inner}</hs:sec>"
        ).encode()
    )


def _pic(ref: str | None) -> str:
    if ref is None:
        return "<hp:pic><hc:img/></hp:pic>"
    return f'<hp:pic><hc:img binaryItemIDRef="{ref}"/></hp:pic>'


def _store() -> BinItemStore:
    return BinItemStore(
        {"image1": "BinData/image1.png", "image2": "BinData/image2.jpg"},
        {"BinData/image1.png": PNG_1X1, "BinData/image2.jpg": JPEG_STUB},
    )


def _images(blocks: list[Block]) -> list[Image]:
    return [b for b in blocks if isinstance(b, Image)]


def test_ns_constants_match_generator() -> None:
    assert body.NS_HC == synth_hwpx.NS_HC
    assert bindata.NS_OPF == synth_hwpx.NS_OPF
    assert bindata.HWPX_CONTENT_HPF == "Contents/content.hpf"


def test_parse_manifest_ids_to_href() -> None:
    data = hwpx_entries(FIXTURE_ITEMS_IMAGES)["Contents/content.hpf"]
    assert parse_manifest(data) == {
        "header": "Contents/header.xml",
        "image1": "BinData/image1.png",
        "image2": "BinData/image2.jpg",
        "section0": "Contents/section0.xml",
    }


def test_parse_manifest_malformed_returns_empty() -> None:
    assert parse_manifest(b"<opf:package") == {}
    assert parse_manifest(b'<?xml version="1.0"?><x/>') == {}


def test_store_resolve_via_manifest() -> None:
    store = BinItemStore({"image1": "BinData/image1.png"}, {"BinData/image1.png": PNG_1X1})
    first = store.resolve("image1")
    assert first == Image("img_001.png", PNG_1X1)
    assert store.resolve("image1") == first


def test_store_fallback_by_name() -> None:
    store = BinItemStore({}, {"BinData/image1.PNG": PNG_1X1})
    assert store.resolve("image1") == Image("img_001.png", PNG_1X1)
    assert store.resolve("nope") is None


def test_store_sniffs_ext_when_unknown() -> None:
    store = BinItemStore({"image1": "BinData/image1"}, {"BinData/image1": PNG_1X1})
    image = store.resolve("image1")
    assert image is not None and image.file_name == "img_001.png"
    store2 = BinItemStore({}, {"BinData/image1.dat": b"zzz"})
    image2 = store2.resolve("image1")
    assert image2 is not None and image2.file_name == "img_001.dat"


def test_read_hwpx_package_collects_bin_data(tmp_path: Path) -> None:
    p = write_hwpx(tmp_path / "doc.hwpx", FIXTURE_ITEMS_IMAGES)
    pkg = read_hwpx_package(p)
    assert set(pkg.bin_data) == {"BinData/image1.png", "BinData/image2.jpg"}
    assert pkg.manifest is not None
    assert pkg.header is not None
    assert len(pkg.sections) == 1
    assert reader.read_package(p) == (pkg.header, pkg.sections)


def test_read_hwpx_package_rejects_large_bin_data(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    p = write_hwpx(tmp_path / "doc.hwpx", FIXTURE_ITEMS_IMAGES)
    monkeypatch.setattr(reader, "MAX_IMAGE_BYTES", 10)
    with pytest.raises(Hwp2mdError, match="binary item too large"):
        read_hwpx_package(p)


@pytest.mark.parametrize(
    ("items", "expected_blocks", "expected_markdown", "expected_counts", "expected_files"),
    IMAGE_FIXTURES,
    ids=["images", "reuse", "in_cell", "missing"],
)
def test_read_blocks_image_fixtures(
    tmp_path: Path,
    items: list[Item],
    expected_blocks: list[Block],
    expected_markdown: str,
    expected_counts: tuple[int, int, int, int],
    expected_files: tuple[str, ...],
) -> None:
    assert reader.read_blocks(write_hwpx(tmp_path / "doc.hwpx", items)) == expected_blocks


def test_pic_inside_ctrl_header_ignored() -> None:
    root = _sec(
        "<hp:p><hp:run><hp:ctrl><hp:header><hp:subList><hp:p><hp:run>"
        + _pic("image1")
        + "</hp:run></hp:p></hp:subList></hp:header></hp:ctrl></hp:run></hp:p>"
        + "<hp:p><hp:run>"
        + _pic("image1")
        + "</hp:run></hp:p>"
    )
    images = _images(parse_section(root, EMPTY_HEADER, _store()))
    assert [i.file_name for i in images] == ["img_001.png"]


def test_pic_inside_container_extracted() -> None:
    root = _sec(
        "<hp:p><hp:run><hp:container>"
        + _pic("image1")
        + _pic("image2")
        + "</hp:container></hp:run></hp:p>"
    )
    images = _images(parse_section(root, EMPTY_HEADER, _store()))
    assert [i.file_name for i in images] == ["img_001.png", "img_002.jpg"]


def test_pic_without_img_or_ref_skipped() -> None:
    root = _sec(
        "<hp:p><hp:run><hp:pic/>" + _pic(None) + _pic("") + "<hp:t>글</hp:t></hp:run></hp:p>"
    )
    assert parse_section(root, EMPTY_HEADER, _store()) == [Paragraph("글")]


def test_parse_paragraph_without_store_yields_no_image() -> None:
    root = _sec("<hp:p><hp:run><hp:t>앞</hp:t>" + _pic("image1") + "</hp:run></hp:p>")
    p = root[0]
    assert parse_paragraph(p) == [Paragraph("앞")]
