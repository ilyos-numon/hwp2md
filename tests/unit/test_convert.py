from pathlib import Path

import pytest

import synth_hwp5
from hwp2md import ConvertResult, NotHwpFileError, UnsupportedHwpError, convert
from hwp2md import render as render_mod
from hwp2md.blocks import Paragraph, Table
from hwp2md.hwp5 import reader
from hwp2md.hwp5.reader import parse_file_header, read_paragraphs
from hwp2md.render import render_markdown
from synth_hwp5 import EXPECTED_MARKDOWN, FIXTURE_PARAGRAPHS, build_file_header, write_hwp5


def test_signature_matches_fixture_generator() -> None:
    assert reader.HWP5_SIGNATURE == synth_hwp5.HWP5_SIGNATURE


def test_convert_compressed_fixture(tmp_path: Path) -> None:
    src = write_hwp5(tmp_path / "sample.hwp", FIXTURE_PARAGRAPHS)
    result = convert(src, tmp_path / "out")
    assert isinstance(result, ConvertResult)
    assert result.paragraph_count == 3
    assert result.output == tmp_path / "out" / "sample.md"
    assert result.source == src
    assert result.markdown == EXPECTED_MARKDOWN
    assert result.output.read_bytes() == EXPECTED_MARKDOWN.encode("utf-8")


def test_convert_uncompressed_fixture(tmp_path: Path) -> None:
    src = write_hwp5(tmp_path / "sample.hwp", FIXTURE_PARAGRAPHS, properties=0)
    result = convert(src, tmp_path / "out")
    assert result.paragraph_count == 3
    assert result.output == tmp_path / "out" / "sample.md"
    assert result.output.read_text(encoding="utf-8") == EXPECTED_MARKDOWN


def test_read_paragraphs_skips_empty(tmp_path: Path) -> None:
    src = write_hwp5(tmp_path / "sample.hwp", FIXTURE_PARAGRAPHS)
    assert read_paragraphs(src) == [p for p in FIXTURE_PARAGRAPHS if p]


@pytest.mark.parametrize("properties", [0x3, 0x5])
def test_encrypted_or_distribution_rejected(tmp_path: Path, properties: int) -> None:
    src = write_hwp5(tmp_path / "sample.hwp", FIXTURE_PARAGRAPHS, properties=properties)
    with pytest.raises(UnsupportedHwpError):
        convert(src, tmp_path / "out")


def test_text_file_is_not_hwp(tmp_path: Path) -> None:
    src = tmp_path / "fake.hwp"
    src.write_text("plain text", encoding="utf-8")
    with pytest.raises(NotHwpFileError):
        convert(src, tmp_path / "out")


def test_missing_path_raises_file_not_found(tmp_path: Path) -> None:
    missing = tmp_path / "nope.hwp"
    with pytest.raises(FileNotFoundError):
        convert(missing, tmp_path / "out")


def test_parse_file_header_rejects_bad_signature() -> None:
    with pytest.raises(NotHwpFileError):
        parse_file_header(b"x" * 256)


@pytest.mark.parametrize("size", [0, 255, 257])
def test_parse_file_header_rejects_wrong_length(size: int) -> None:
    raw = (build_file_header() + b"\x00")[:size]
    with pytest.raises(NotHwpFileError):
        parse_file_header(raw)


def test_parse_file_header_fields() -> None:
    header = parse_file_header(build_file_header(properties=0x1))
    assert header.version == (5, 0, 3, 0)
    assert header.compressed is True
    assert header.encrypted is False
    assert header.distribution is False


def test_render_markdown_empty() -> None:
    assert render_markdown([]) == ""


def test_render_markdown_skips_empty_paragraphs() -> None:
    assert render_markdown(["a", "", "b"]) == "a\n\nb\n"


def test_convert_fixture_with_table(tmp_path: Path) -> None:
    src = write_hwp5(tmp_path / "table.hwp", synth_hwp5.FIXTURE_ITEMS_WITH_TABLE)
    result = convert(src, tmp_path / "out")
    assert result.markdown == synth_hwp5.EXPECTED_MARKDOWN_WITH_TABLE
    assert result.paragraph_count == 2
    assert result.table_count == 1
    assert result.output.read_bytes() == synth_hwp5.EXPECTED_MARKDOWN_WITH_TABLE.encode("utf-8")


def test_convert_fixture_with_merged_table(tmp_path: Path) -> None:
    src = write_hwp5(tmp_path / "merged.hwp", synth_hwp5.FIXTURE_ITEMS_MERGED)
    result = convert(src, tmp_path / "out")
    assert result.markdown == synth_hwp5.EXPECTED_MARKDOWN_MERGED
    assert result.paragraph_count == 1
    assert result.table_count == 1


def test_convert_paragraph_fixture_has_no_tables(tmp_path: Path) -> None:
    src = write_hwp5(tmp_path / "sample.hwp", FIXTURE_PARAGRAPHS)
    result = convert(src, tmp_path / "out")
    assert result.table_count == 0
    assert result.markdown == EXPECTED_MARKDOWN


def test_render_blocks_empty_and_skips_empty_paragraph() -> None:
    assert render_mod.render_blocks([]) == ""
    assert render_mod.render_blocks([Paragraph(""), Paragraph("a")]) == "a\n"


def test_render_blocks_table_escapes_pipe_and_newline() -> None:
    assert (
        render_mod.render_blocks([Table([["x|y", "l1\nl2"]])])
        == "| x\\|y | l1<br>l2 |\n|---|---|\n"
    )


def test_render_markdown_wrapper_unchanged() -> None:
    assert render_markdown(["a", "", "b"]) == "a\n\nb\n"


def test_read_blocks_fixture_with_table(tmp_path: Path) -> None:
    src = write_hwp5(tmp_path / "table.hwp", synth_hwp5.FIXTURE_ITEMS_WITH_TABLE)
    assert reader.read_blocks(src) == synth_hwp5.EXPECTED_BLOCKS_WITH_TABLE
    assert read_paragraphs(src) == ["표 앞 단락", "표 뒤 단락"]


def test_public_exports_include_blocks() -> None:
    import hwp2md

    for name in ("Block", "Paragraph", "Table"):
        assert name in hwp2md.__all__
