import io
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

from hwp2md.blocks import Paragraph
from hwp2md.hwpx.reader import HWPX_MIMETYPE, NS_HP, NS_HS, read_blocks
from synth_hwp5 import (
    EXPECTED_BLOCKS_MERGED,
    EXPECTED_BLOCKS_WITH_TABLE,
    FIXTURE_ITEMS_MERGED,
    FIXTURE_ITEMS_WITH_TABLE,
    FIXTURE_PARAGRAPHS,
    SynthTable,
)
from synth_hwpx import (
    EXPECTED_BLOCKS_INLINE,
    FIXTURE_PARAGRAPHS_INLINE,
    build_hwpx,
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
