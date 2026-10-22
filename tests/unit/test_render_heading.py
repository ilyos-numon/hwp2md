from pathlib import Path

from hwp2md import convert
from hwp2md.blocks import Paragraph
from hwp2md.render import render_blocks
from synth_hwp5 import FIXTURE_PARAGRAPHS, write_hwp5


def test_paragraph_default_level_zero_equality() -> None:
    assert Paragraph("a") == Paragraph("a", 0)
    assert Paragraph("a").level == 0
    assert Paragraph("a", 1) != Paragraph("a")


def test_render_heading_levels() -> None:
    for level in range(1, 7):
        assert render_blocks([Paragraph("t", level)]) == "#" * level + " t\n"


def test_render_heading_clamps_above_six() -> None:
    assert render_blocks([Paragraph("t", 9)]) == "###### t\n"


def test_render_heading_newline_to_space_and_strip() -> None:
    assert render_blocks([Paragraph(" a\nb ", 2)]) == "## a b\n"


def test_render_heading_empty_text_skipped() -> None:
    blocks = [Paragraph("", 2), Paragraph(" \n ", 3), Paragraph("x")]
    assert render_blocks(blocks) == "x\n"


def test_render_heading_between_paragraphs() -> None:
    blocks = [Paragraph("a"), Paragraph("h", 1), Paragraph("b")]
    assert render_blocks(blocks) == "a\n\n# h\n\nb\n"


def test_convert_result_has_heading_count(tmp_path: Path) -> None:
    result = convert(write_hwp5(tmp_path / "s.hwp", FIXTURE_PARAGRAPHS), tmp_path / "out")
    assert result.heading_count == 0
    assert result.paragraph_count == 3
