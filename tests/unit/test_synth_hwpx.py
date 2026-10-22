import hashlib
import io
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import pytest

from hwp2md.blocks import Paragraph, Table
from hwp2md.hwpx.reader import HWPX_MIMETYPE, NS_HP, NS_HS, read_blocks
from synth_hwp5 import (
    EXPECTED_BLOCKS_MERGED,
    EXPECTED_BLOCKS_WITH_TABLE,
    FIXTURE_ITEMS_HEADING_IN_CELL,
    FIXTURE_ITEMS_HEADINGS,
    FIXTURE_ITEMS_IMAGE_IN_CELL,
    FIXTURE_ITEMS_IMAGE_MISSING,
    FIXTURE_ITEMS_IMAGES,
    FIXTURE_ITEMS_MERGED,
    FIXTURE_ITEMS_WITH_TABLE,
    FIXTURE_PARAGRAPHS,
    JPEG_STUB,
    PNG_1X1,
    Item,
    SynthTable,
)
from synth_hwpx import (
    EXPECTED_BLOCKS_INLINE,
    FIXTURE_PARAGRAPHS_INLINE,
    NS_HC,
    NS_HH,
    NS_OPF,
    P_ATTRS,
    XML_DECL,
    build_hwpx,
    hwpx_entries,
    p_attrs,
    section_xml,
    write_hwpx,
)

ENTRY_NAMES = [
    "mimetype",
    "version.xml",
    "META-INF/container.xml",
    "Contents/content.hpf",
    "Contents/header.xml",
    "Contents/section0.xml",
]


def _zip(data: bytes) -> zipfile.ZipFile:
    return zipfile.ZipFile(io.BytesIO(data))


def test_mimetype_first_and_stored() -> None:
    zf = _zip(build_hwpx(FIXTURE_ITEMS_WITH_TABLE))
    assert zf.namelist()[0] == "mimetype"
    assert zf.infolist()[0].compress_type == zipfile.ZIP_STORED
    assert zf.read("mimetype") == HWPX_MIMETYPE


def test_entries_exact() -> None:
    assert _zip(build_hwpx(FIXTURE_ITEMS_WITH_TABLE)).namelist() == ENTRY_NAMES


def test_section_parses_with_stdlib() -> None:
    for items in (FIXTURE_PARAGRAPHS, FIXTURE_ITEMS_WITH_TABLE, FIXTURE_ITEMS_MERGED):
        root = ET.fromstring(section_xml(items))
        assert root.tag == f"{{{NS_HS}}}sec"
        assert len(root.findall(f"{{{NS_HP}}}p")) == len(items)
        n_tables = sum(1 for item in items if isinstance(item, SynthTable))
        assert len(list(root.iter(f"{{{NS_HP}}}tbl"))) == n_tables


def test_round_trip_paragraphs(tmp_path: Path) -> None:
    path = write_hwpx(tmp_path / "p.hwpx", FIXTURE_PARAGRAPHS)
    assert read_blocks(path) == [Paragraph(p) for p in FIXTURE_PARAGRAPHS if p]


def test_round_trip_table(tmp_path: Path) -> None:
    path = write_hwpx(tmp_path / "t.hwpx", FIXTURE_ITEMS_WITH_TABLE)
    assert read_blocks(path) == EXPECTED_BLOCKS_WITH_TABLE


def test_round_trip_merged(tmp_path: Path) -> None:
    path = write_hwpx(tmp_path / "m.hwpx", FIXTURE_ITEMS_MERGED)
    assert read_blocks(path) == EXPECTED_BLOCKS_MERGED


def test_round_trip_inline(tmp_path: Path) -> None:
    path = write_hwpx(tmp_path / "i.hwpx", FIXTURE_PARAGRAPHS_INLINE)
    assert read_blocks(path) == EXPECTED_BLOCKS_INLINE


def test_deterministic_bytes() -> None:
    assert build_hwpx(FIXTURE_ITEMS_MERGED) == build_hwpx(FIXTURE_ITEMS_MERGED)


def test_two_sections_concatenated(tmp_path: Path) -> None:
    path = write_hwpx(tmp_path / "s.hwpx", FIXTURE_PARAGRAPHS, more_sections=[["둘째 섹션"]])
    blocks = read_blocks(path)
    assert blocks[-1] == Paragraph("둘째 섹션")
    assert blocks[:-1] == [Paragraph(p) for p in FIXTURE_PARAGRAPHS if p]
    header = zipfile.ZipFile(path).read("Contents/header.xml").decode("utf-8")
    assert 'secCnt="2"' in header


HEADING_TEXTS = ["문서 제목", "본문 단락", "1. 사업 개요", "가. 세부 내용", "마지막 단락"]


def test_header_default_bytes_unchanged() -> None:
    expected = (
        XML_DECL
        + f'<hh:head xmlns:hh="{NS_HH}" version="1.5" secCnt="1">'
        + '<hh:beginNum page="1" footnote="1" endnote="1" pic="1" tbl="1" equation="1"/>'
        + "<hh:refList/></hh:head>"
    ).encode("utf-8")
    assert hwpx_entries(FIXTURE_PARAGRAPHS)["Contents/header.xml"] == expected


@pytest.mark.parametrize(
    ("items", "digest"),
    [
        (FIXTURE_PARAGRAPHS, "b83d0aa5762aeb738f5a78819c0f050098d5eb23d2f960d4e8c0d32ac9530deb"),
        (
            FIXTURE_ITEMS_WITH_TABLE,
            "185204bc869255ddfc9cc1d26ea85a34c6a89cea674f5a99ad5627934f4c0db8",
        ),
        (FIXTURE_ITEMS_MERGED, "65b87fb60e131bf30b40dc4a03f9beaf82e3b7d11936a134075bcb3118bdc84e"),
    ],
)
def test_fixture_bytes_unchanged_sha256(items: list[Item], digest: str) -> None:
    assert hashlib.sha256(build_hwpx(items)).hexdigest() == digest


def test_header_outline_structure() -> None:
    root = ET.fromstring(hwpx_entries(FIXTURE_ITEMS_HEADINGS)["Contents/header.xml"])
    para_prs = list(root.iter(f"{{{NS_HH}}}paraPr"))
    assert [pp.get("id") for pp in para_prs] == [str(i) for i in range(8)]
    pairs = []
    for pp in para_prs:
        h = pp.find(f"{{{NS_HH}}}heading")
        assert h is not None
        pairs.append((h.get("type"), h.get("level")))
    assert pairs == [("NONE", "0")] + [("OUTLINE", str(i)) for i in range(7)]
    styles = list(root.iter(f"{{{NS_HH}}}style"))
    assert len(styles) == 8
    assert styles[3].get("name") == "개요 3"
    assert styles[3].get("paraPrIDRef") == "3"


def test_heading_paragraph_attrs() -> None:
    root = ET.fromstring(section_xml(FIXTURE_ITEMS_HEADINGS))
    ps = root.findall(f"{{{NS_HP}}}p")
    assert [p.get("paraPrIDRef") for p in ps] == ["1", "0", "2", "0", "3", "0"]
    assert [p.get("styleIDRef") for p in ps] == ["1", "0", "2", "0", "3", "0"]


def test_cell_heading_paragraph_attrs() -> None:
    root = ET.fromstring(section_xml(FIXTURE_ITEMS_HEADING_IN_CELL))
    tc = next(root.iter(f"{{{NS_HP}}}tc"))
    p = next(tc.iter(f"{{{NS_HP}}}p"))
    assert p.get("paraPrIDRef") == "2"


def test_p_attrs_zero_equals_constant() -> None:
    assert p_attrs(0) == P_ATTRS


def test_heading_fixture_round_trips_text(tmp_path: Path) -> None:
    blocks = read_blocks(write_hwpx(tmp_path / "h.hwpx", FIXTURE_ITEMS_HEADINGS))
    assert [b.text for b in blocks if isinstance(b, Paragraph)] == HEADING_TEXTS
    tables = [b for b in blocks if isinstance(b, Table)]
    assert tables == [Table([["구분", "내용"], ["지원 규모", "총 30억 원"]])]


HP = f"{{{NS_HP}}}"
HC_IMG = f"{{{NS_HC}}}img"
OPF_ITEM = f"{{{NS_OPF}}}item"


def _manifest_items(content: bytes) -> list[ET.Element]:
    return list(ET.fromstring(content).iter(OPF_ITEM))


def test_ns_hc_constant_present() -> None:
    assert NS_HC == "http://www.hancom.co.kr/hwpml/2011/core"


def test_entries_with_images_order_and_bytes() -> None:
    entries = hwpx_entries(FIXTURE_ITEMS_IMAGES)
    assert list(entries) == ENTRY_NAMES[:5] + [
        "BinData/image1.png",
        "BinData/image2.jpg",
        "Contents/section0.xml",
    ]
    assert entries["BinData/image1.png"] == PNG_1X1
    assert entries["BinData/image2.jpg"] == JPEG_STUB


def test_manifest_items_inserted_after_header() -> None:
    items = _manifest_items(hwpx_entries(FIXTURE_ITEMS_IMAGES)["Contents/content.hpf"])
    assert [i.get("id") for i in items] == ["header", "image1", "image2", "section0"]
    image1 = items[1]
    assert image1.get("href") == "BinData/image1.png"
    assert image1.get("media-type") == "image/png"
    assert image1.get("isEmbeded") == "1"


def test_content_hpf_unchanged_without_images() -> None:
    content = hwpx_entries(FIXTURE_ITEMS_HEADINGS)["Contents/content.hpf"]
    assert [i.get("id") for i in _manifest_items(content)] == ["header", "section0"]
    assert b"BinData" not in content


def test_pic_paragraph_structure() -> None:
    root = ET.fromstring(section_xml(FIXTURE_ITEMS_IMAGES))
    paras = root.findall(f"{HP}p")
    runs = paras[1].findall(f"{HP}run")
    assert [c.tag for r in runs for c in r] == [f"{HP}pic"]
    img1 = paras[1].find(f"{HP}run/{HP}pic/{HC_IMG}")
    assert img1 is not None and img1.get("binaryItemIDRef") == "image1"
    img2 = paras[3].find(f"{HP}run/{HP}pic/{HC_IMG}")
    assert img2 is not None and img2.get("binaryItemIDRef") == "image2"


def test_cell_image_paragraph() -> None:
    root = ET.fromstring(section_xml(FIXTURE_ITEMS_IMAGE_IN_CELL))
    tc = next(root.iter(f"{HP}tc"))
    cell_paras = tc.findall(f"{HP}subList/{HP}p")
    assert len(cell_paras) == 2
    img = cell_paras[0].find(f".//{HC_IMG}")
    assert img is not None and img.get("binaryItemIDRef") == "image1"
    assert "".join(t.text or "" for t in cell_paras[1].iter(f"{HP}t")) == "값"
    top = root.findall(f"{HP}p")[1].find(f"{HP}run/{HP}pic/{HC_IMG}")
    assert top is not None and top.get("binaryItemIDRef") == "image2"


def test_missing_image_has_manifest_but_no_entry() -> None:
    entries = hwpx_entries(FIXTURE_ITEMS_IMAGE_MISSING)
    ids = [i.get("id") for i in _manifest_items(entries["Contents/content.hpf"])]
    assert "image1" in ids and "image2" in ids
    assert [n for n in entries if n.startswith("BinData/")] == ["BinData/image2.png"]


def test_image_fixture_round_trips_text(tmp_path: Path) -> None:
    blocks = read_blocks(write_hwpx(tmp_path / "doc.hwpx", FIXTURE_ITEMS_IMAGES))
    assert [b.text for b in blocks if isinstance(b, Paragraph)] == [
        "그림 앞 단락",
        "1. 결과",
        "그림 뒤 단락",
    ]
