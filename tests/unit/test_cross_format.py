from pathlib import Path

import pytest

import hwp2md
from hwp2md import convert
from hwp2md.blocks import Block
from hwp2md.hwp5.reader import read_paragraphs
from synth_hwp5 import (
    EXPECTED_COUNTS_HEADING_EDGE,
    EXPECTED_COUNTS_HEADING_IN_CELL,
    EXPECTED_COUNTS_HEADINGS,
    EXPECTED_MARKDOWN_HEADING_EDGE,
    EXPECTED_MARKDOWN_HEADING_IN_CELL,
    EXPECTED_MARKDOWN_HEADINGS,
    FIXTURE_ITEMS_HEADING_EDGE,
    FIXTURE_ITEMS_HEADING_IN_CELL,
    FIXTURE_ITEMS_HEADINGS,
    FIXTURE_ITEMS_IMAGE_IN_CELL,
    FIXTURE_ITEMS_MERGED,
    FIXTURE_ITEMS_WITH_TABLE,
    FIXTURE_PARAGRAPHS,
    IMAGE_FIXTURES,
    JPEG_STUB,
    PNG_1X1,
    Item,
    write_hwp5,
)
from synth_hwpx import EXPECTED_MARKDOWN_INLINE, FIXTURE_PARAGRAPHS_INLINE, write_hwpx


@pytest.mark.parametrize(
    "items",
    [FIXTURE_PARAGRAPHS, FIXTURE_ITEMS_WITH_TABLE, FIXTURE_ITEMS_MERGED],
    ids=["paragraphs", "with_table", "merged"],
)
def test_hwp5_and_hwpx_same_markdown(tmp_path: Path, items: list[Item]) -> None:
    from_hwp5 = convert(write_hwp5(tmp_path / "a.hwp", items), tmp_path / "out5")
    from_hwpx = convert(write_hwpx(tmp_path / "a.hwpx", items), tmp_path / "outx")
    assert from_hwp5.markdown == from_hwpx.markdown
    assert from_hwp5.paragraph_count == from_hwpx.paragraph_count
    assert from_hwp5.table_count == from_hwpx.table_count


def test_convert_hwpx_inline_fixture(tmp_path: Path) -> None:
    src = write_hwpx(tmp_path / "inline.hwpx", FIXTURE_PARAGRAPHS_INLINE)
    assert convert(src, tmp_path / "out").markdown == EXPECTED_MARKDOWN_INLINE


def test_convert_hwpx_result_fields(tmp_path: Path) -> None:
    src = write_hwpx(tmp_path / "sample.hwpx", FIXTURE_PARAGRAPHS)
    result = convert(src, tmp_path / "out")
    assert result.source == src
    assert result.output == tmp_path / "out" / "sample.md"
    assert result.paragraph_count == 3
    assert result.table_count == 0
    assert result.output.read_bytes() == result.markdown.encode("utf-8")
    assert "DocFormat" in hwp2md.__all__
    assert "detect_format" in hwp2md.__all__


@pytest.mark.parametrize(
    ("items", "expected_markdown", "expected_counts"),
    [
        (FIXTURE_ITEMS_HEADINGS, EXPECTED_MARKDOWN_HEADINGS, EXPECTED_COUNTS_HEADINGS),
        (FIXTURE_ITEMS_HEADING_EDGE, EXPECTED_MARKDOWN_HEADING_EDGE, EXPECTED_COUNTS_HEADING_EDGE),
        (
            FIXTURE_ITEMS_HEADING_IN_CELL,
            EXPECTED_MARKDOWN_HEADING_IN_CELL,
            EXPECTED_COUNTS_HEADING_IN_CELL,
        ),
    ],
    ids=["headings", "edge", "in_cell"],
)
def test_heading_fixtures_same_markdown_both_formats(
    tmp_path: Path,
    items: list[Item],
    expected_markdown: str,
    expected_counts: tuple[int, int, int],
) -> None:
    from_hwp5 = convert(write_hwp5(tmp_path / "h.hwp", items), tmp_path / "out5")
    from_hwpx = convert(write_hwpx(tmp_path / "h.hwpx", items), tmp_path / "outx")
    for result in (from_hwp5, from_hwpx):
        assert result.markdown == expected_markdown
        counts = (result.paragraph_count, result.table_count, result.heading_count)
        assert counts == expected_counts


def test_read_paragraphs_includes_heading_text(tmp_path: Path) -> None:
    path = write_hwp5(tmp_path / "h.hwp", FIXTURE_ITEMS_HEADINGS)
    assert read_paragraphs(path) == [
        "문서 제목",
        "본문 단락",
        "1. 사업 개요",
        "가. 세부 내용",
        "마지막 단락",
    ]


_IMAGE_BYTES = {
    "img_001.png": PNG_1X1,
    "img_002.jpg": JPEG_STUB,
    "img_001.jpg": JPEG_STUB,
    "img_002.png": PNG_1X1,
}


@pytest.mark.parametrize(
    ("items", "expected_blocks", "expected_markdown", "expected_counts", "expected_files"),
    IMAGE_FIXTURES,
    ids=["images", "reuse", "in_cell", "missing"],
)
def test_image_fixtures_same_result_both_formats(
    tmp_path: Path,
    items: list[Item],
    expected_blocks: list[Block],
    expected_markdown: str,
    expected_counts: tuple[int, int, int, int],
    expected_files: tuple[str, ...],
) -> None:
    out5 = tmp_path / "out5"
    outx = tmp_path / "outx"
    from_hwp5 = convert(write_hwp5(tmp_path / "doc.hwp", items), out5)
    from_hwpx = convert(write_hwpx(tmp_path / "doc.hwpx", items), outx)
    for result, out in ((from_hwp5, out5), (from_hwpx, outx)):
        assert result.markdown == expected_markdown
        counts = (
            result.paragraph_count,
            result.table_count,
            result.heading_count,
            result.image_count,
        )
        assert counts == expected_counts
        assert tuple(p.name for p in result.image_files) == expected_files
        for f in result.image_files:
            assert f.read_bytes() == _IMAGE_BYTES[f.name]
        assert result.image_dir == out / "doc_images"
    assert from_hwp5.markdown.encode() == from_hwpx.markdown.encode()


def test_image_fixture_no_jpg_file_when_only_in_cell(tmp_path: Path) -> None:
    out5 = tmp_path / "out5"
    outx = tmp_path / "outx"
    convert(write_hwp5(tmp_path / "doc.hwp", FIXTURE_ITEMS_IMAGE_IN_CELL), out5)
    convert(write_hwpx(tmp_path / "doc.hwpx", FIXTURE_ITEMS_IMAGE_IN_CELL), outx)
    for out in (out5, outx):
        names = sorted(p.name for p in (out / "doc_images").iterdir())
        assert names == ["img_001.jpg", "img_002.png"]
