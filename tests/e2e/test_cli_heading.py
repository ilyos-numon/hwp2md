from __future__ import annotations

import os
import re
import shutil
import subprocess
from collections import Counter
from collections.abc import Callable
from pathlib import Path

import pytest

from synth_hwp5 import (
    EXPECTED_MARKDOWN,
    EXPECTED_MARKDOWN_HEADING_EDGE,
    EXPECTED_MARKDOWN_HEADING_IN_CELL,
    EXPECTED_MARKDOWN_HEADINGS,
    EXPECTED_MARKDOWN_WITH_TABLE,
    FIXTURE_ITEMS_HEADING_EDGE,
    FIXTURE_ITEMS_HEADING_IN_CELL,
    FIXTURE_ITEMS_HEADINGS,
    FIXTURE_ITEMS_WITH_TABLE,
    FIXTURE_PARAGRAPHS,
    build_cfb,
    build_docinfo,
    build_file_header,
    build_section0,
    write_hwp5,
)
from synth_hwpx import write_hwpx

RunCli = Callable[[list[str]], subprocess.CompletedProcess[str]]

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures"
REAL_HWP5 = sorted(FIXTURES_DIR.glob("*.hwp"))
REAL_HWPX = sorted(FIXTURES_DIR.joinpath("hwpx").glob("*.hwpx"))
REAL_EXPECTED: dict[str, tuple[int, int, int]] = {  # (단락, 표, 제목) §4.11
    "form200005063113.hwp": (118, 8, 0),
    "form210001070268.hwp": (47, 0, 0),
    "(서식1) 비영리법인 현황 제출 양식.hwpx": (1, 1, 0),
    "(서식2) 사업실적 및 사업계획 제출 양식.hwpx": (80, 31, 0),
    "브라더 공공기관 보고서 양식.hwpx": (32, 8, 0),
}
REAL_HEADING_LEVELS: dict[str, dict[int, int]] = {}  # 제목 있는 실제 샘플 추가 시 채운다
STDOUT_LINE2 = re.compile(r"^  단락 (\d+)개 · 표 (\d+)개(?: · 제목 (\d+)개)?$")
HEADING_LINE = re.compile(r"^(#{1,6}) \S")


def _copy_evidence(md: Path, name: str) -> None:
    evidence_dir = Path(os.environ.get("ILLY_SHOT_DIR", "tests/e2e/screenshots"))
    evidence_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(md, evidence_dir / name)


def _convert(run_cli: RunCli, src: Path, out_dir: Path) -> tuple[list[str], Path]:
    result = run_cli([str(src), "-o", str(out_dir)])
    assert result.returncode == 0, result.stderr
    return result.stdout.split("\n"), out_dir / f"{src.stem}.md"


def test_convert_heading_hwp5_success(tmp_path: Path, run_cli: RunCli) -> None:
    src = write_hwp5(tmp_path / "heading.hwp", FIXTURE_ITEMS_HEADINGS)
    out_dir = tmp_path / "out"
    lines, md = _convert(run_cli, src, out_dir)

    assert lines[0] == f"✓ heading.hwp → {out_dir / 'heading.md'}"
    assert lines[1] == "  단락 2개 · 표 1개 · 제목 3개"
    assert md.read_text(encoding="utf-8") == EXPECTED_MARKDOWN_HEADINGS
    _copy_evidence(md, "heading_hwp5.md")


def test_convert_heading_hwpx_success(tmp_path: Path, run_cli: RunCli) -> None:
    src = write_hwpx(tmp_path / "heading.hwpx", FIXTURE_ITEMS_HEADINGS)
    out_dir = tmp_path / "out"
    lines, md = _convert(run_cli, src, out_dir)

    assert lines[0] == f"✓ heading.hwpx → {out_dir / 'heading.md'}"
    assert lines[1] == "  단락 2개 · 표 1개 · 제목 3개"
    assert md.read_text(encoding="utf-8") == EXPECTED_MARKDOWN_HEADINGS
    _copy_evidence(md, "heading_hwpx.md")


def test_heading_edge_cases_same_in_both_formats(tmp_path: Path, run_cli: RunCli) -> None:
    src5 = write_hwp5(tmp_path / "edge.hwp", FIXTURE_ITEMS_HEADING_EDGE)
    srcx = write_hwpx(tmp_path / "edge.hwpx", FIXTURE_ITEMS_HEADING_EDGE)
    lines5, md5 = _convert(run_cli, src5, tmp_path / "out5")
    linesx, mdx = _convert(run_cli, srcx, tmp_path / "outx")

    assert lines5[1] == "  단락 1개 · 표 0개 · 제목 2개"
    assert linesx[1] == "  단락 1개 · 표 0개 · 제목 2개"
    assert md5.read_text(encoding="utf-8") == EXPECTED_MARKDOWN_HEADING_EDGE
    assert mdx.read_text(encoding="utf-8") == EXPECTED_MARKDOWN_HEADING_EDGE
    assert md5.read_bytes() == mdx.read_bytes()
    _copy_evidence(md5, "heading_edge.md")


def test_heading_in_table_cell_stays_cell_text(tmp_path: Path, run_cli: RunCli) -> None:
    src5 = write_hwp5(tmp_path / "cell.hwp", FIXTURE_ITEMS_HEADING_IN_CELL)
    srcx = write_hwpx(tmp_path / "cell.hwpx", FIXTURE_ITEMS_HEADING_IN_CELL)
    lines5, md5 = _convert(run_cli, src5, tmp_path / "out5")
    linesx, mdx = _convert(run_cli, srcx, tmp_path / "outx")

    assert lines5[1] == "  단락 0개 · 표 1개 · 제목 1개"
    assert linesx[1] == "  단락 0개 · 표 1개 · 제목 1개"
    assert md5.read_text(encoding="utf-8") == EXPECTED_MARKDOWN_HEADING_IN_CELL
    assert mdx.read_text(encoding="utf-8") == EXPECTED_MARKDOWN_HEADING_IN_CELL
    _copy_evidence(md5, "heading_cell.md")


def test_no_heading_keeps_two_field_summary(tmp_path: Path, run_cli: RunCli) -> None:
    src5 = write_hwp5(tmp_path / "plain.hwp", FIXTURE_PARAGRAPHS)
    result5 = run_cli([str(src5), "-o", str(tmp_path / "out5")])
    assert result5.returncode == 0, result5.stderr
    assert result5.stdout.split("\n")[1] == "  단락 3개 · 표 0개"
    assert (tmp_path / "out5" / "plain.md").read_text(encoding="utf-8") == EXPECTED_MARKDOWN
    assert "제목" not in result5.stdout

    srcx = write_hwpx(tmp_path / "table.hwpx", FIXTURE_ITEMS_WITH_TABLE)
    resultx = run_cli([str(srcx), "-o", str(tmp_path / "outx")])
    assert resultx.returncode == 0, resultx.stderr
    assert resultx.stdout.split("\n")[1] == "  단락 2개 · 표 1개"
    assert (tmp_path / "outx" / "table.md").read_text(
        encoding="utf-8"
    ) == EXPECTED_MARKDOWN_WITH_TABLE


def test_heading_uncompressed_variant(tmp_path: Path, run_cli: RunCli) -> None:
    src = write_hwp5(tmp_path / "raw.hwp", FIXTURE_ITEMS_HEADINGS, properties=0)
    _, md = _convert(run_cli, src, tmp_path / "out")

    assert md.read_text(encoding="utf-8") == EXPECTED_MARKDOWN_HEADINGS


def test_truncated_docinfo_exit_1(tmp_path: Path, run_cli: RunCli) -> None:
    src = tmp_path / "broken.hwp"
    src.write_bytes(
        build_cfb(
            {
                "FileHeader": build_file_header(properties=0),
                "DocInfo": build_docinfo(outline=True)[:-3],
                "BodyText/Section0": build_section0(FIXTURE_ITEMS_HEADINGS),
            }
        )
    )
    out_dir = tmp_path / "out"
    result = run_cli([str(src), "-o", str(out_dir)])

    assert result.returncode == 1
    assert "truncated record" in result.stderr
    assert not (out_dir / "broken.md").exists()


@pytest.mark.parametrize("real", REAL_HWP5 + REAL_HWPX, ids=lambda p: p.name)
def test_real_fixture_headings(real: Path, tmp_path: Path, run_cli: RunCli) -> None:
    lines, md = _convert(run_cli, real, tmp_path / "out")
    m = STDOUT_LINE2.match(lines[1])
    assert m, lines[1]
    p, t, h = int(m[1]), int(m[2]), int(m[3] or 0)
    if real.name in REAL_EXPECTED:
        assert (p, t, h) == REAL_EXPECTED[real.name]
    content = md.read_text(encoding="utf-8")
    levels = [len(mm.group(1)) for ln in content.split("\n") if (mm := HEADING_LINE.match(ln))]
    assert len(levels) == h
    if real.name in REAL_HEADING_LEVELS:
        assert dict(Counter(levels)) == REAL_HEADING_LEVELS[real.name]
    assert len(content.strip()) > 0
    _copy_evidence(md, md.name)
