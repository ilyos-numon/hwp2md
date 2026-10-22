from pathlib import Path

import pytest

import hwp2md
from hwp2md import convert
from synth_hwp5 import (
    FIXTURE_ITEMS_MERGED,
    FIXTURE_ITEMS_WITH_TABLE,
    FIXTURE_PARAGRAPHS,
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
