from __future__ import annotations

import os
import re
import shutil
import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest

from samples import LEGACY_HWPX
from synth_hwp5 import (
    EXPECTED_MARKDOWN,
    EXPECTED_MARKDOWN_MERGED,
    EXPECTED_MARKDOWN_WITH_TABLE,
    FIXTURE_ITEMS_MERGED,
    FIXTURE_ITEMS_WITH_TABLE,
    FIXTURE_PARAGRAPHS,
    write_hwp5,
)
from synth_hwpx import build_zip, hwpx_entries, write_hwpx

RunCli = Callable[[list[str]], subprocess.CompletedProcess[str]]

REAL_HWPX_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "hwpx"
REAL_HWPX_FIXTURES = LEGACY_HWPX
REAL_HWPX_EXPECTED: dict[str, tuple[int, int]] = {
    "(서식1) 비영리법인 현황 제출 양식.hwpx": (1, 1),
    "(서식2) 사업실적 및 사업계획 제출 양식.hwpx": (80, 31),
    "브라더 공공기관 보고서 양식.hwpx": (32, 8),
}
STDOUT_LINE2 = re.compile(r"^  단락 (\d+)개 · 표 (\d+)개(?: · 제목 \d+개)?(?: · 이미지 \d+개)?$")


def _copy_evidence(md: Path, name: str) -> None:
    evidence_dir = Path(os.environ.get("ILLY_SHOT_DIR", "tests/e2e/screenshots"))
    evidence_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(md, evidence_dir / name)


def test_convert_hwpx_synthetic_success(tmp_path: Path, run_cli: RunCli) -> None:
    src = write_hwpx(tmp_path / "sample.hwpx", FIXTURE_PARAGRAPHS)
    out_dir = tmp_path / "out"
    result = run_cli([str(src), "-o", str(out_dir)])

    assert result.returncode == 0, result.stderr
    lines = result.stdout.split("\n")
    assert lines[0] == f"✓ sample.hwpx → {out_dir / 'sample.md'}"
    assert lines[1] == "  단락 3개 · 표 0개"
    md = out_dir / "sample.md"
    assert md.read_text(encoding="utf-8") == EXPECTED_MARKDOWN
    _copy_evidence(md, "sample_hwpx.md")


def test_convert_hwpx_table_success(tmp_path: Path, run_cli: RunCli) -> None:
    src = write_hwpx(tmp_path / "table.hwpx", FIXTURE_ITEMS_WITH_TABLE)
    out_dir = tmp_path / "out"
    result = run_cli([str(src), "-o", str(out_dir)])

    assert result.returncode == 0, result.stderr
    lines = result.stdout.split("\n")
    assert lines[1] == "  단락 2개 · 표 1개"
    md = out_dir / "table.md"
    assert md.read_text(encoding="utf-8") == EXPECTED_MARKDOWN_WITH_TABLE
    _copy_evidence(md, "table_hwpx.md")


def test_convert_hwpx_merged_table(tmp_path: Path, run_cli: RunCli) -> None:
    src = write_hwpx(tmp_path / "merged.hwpx", FIXTURE_ITEMS_MERGED)
    out_dir = tmp_path / "out"
    result = run_cli([str(src), "-o", str(out_dir)])

    assert result.returncode == 0, result.stderr
    lines = result.stdout.split("\n")
    assert lines[1] == "  단락 1개 · 표 1개"
    md = out_dir / "merged.md"
    assert md.read_text(encoding="utf-8") == EXPECTED_MARKDOWN_MERGED
    _copy_evidence(md, "merged_hwpx.md")


def test_hwpx_content_with_hwp_extension_converts(tmp_path: Path, run_cli: RunCli) -> None:
    src = write_hwpx(tmp_path / "disguised.hwp", FIXTURE_PARAGRAPHS)
    out_dir = tmp_path / "out"
    result = run_cli([str(src), "-o", str(out_dir)])

    assert result.returncode == 0, result.stderr
    md = out_dir / "disguised.md"
    assert md.read_text(encoding="utf-8") == EXPECTED_MARKDOWN


def test_hwp5_and_hwpx_same_markdown(tmp_path: Path, run_cli: RunCli) -> None:
    src_a = write_hwp5(tmp_path / "a.hwp", FIXTURE_ITEMS_WITH_TABLE)
    src_b = write_hwpx(tmp_path / "b.hwpx", FIXTURE_ITEMS_WITH_TABLE)
    out_dir = tmp_path / "out"
    result_a = run_cli([str(src_a), "-o", str(out_dir)])
    result_b = run_cli([str(src_b), "-o", str(out_dir)])

    assert result_a.returncode == 0, result_a.stderr
    assert result_b.returncode == 0, result_b.stderr
    assert (out_dir / "a.md").read_bytes() == (out_dir / "b.md").read_bytes()
    assert result_a.stdout.split("\n")[1] == result_b.stdout.split("\n")[1]


def test_zip_not_hwpx_exit_3(tmp_path: Path, run_cli: RunCli) -> None:
    src = tmp_path / "notes.hwpx"
    src.write_bytes(build_zip({"mimetype": b"application/epub+zip", "hello.txt": b"hi"}))
    out_dir = tmp_path / "out"
    result = run_cli([str(src), "-o", str(out_dir)])

    assert result.returncode == 3
    assert "not an HWP 5.0 file:" in result.stderr
    assert not (out_dir / "notes.md").exists()


def test_hwpx_malformed_section_exit_1(tmp_path: Path, run_cli: RunCli) -> None:
    entries = hwpx_entries(FIXTURE_PARAGRAPHS)
    entries["Contents/section0.xml"] = b"<hs:sec>unclosed"
    src = tmp_path / "broken.hwpx"
    src.write_bytes(build_zip(entries))
    out_dir = tmp_path / "out"
    result = run_cli([str(src), "-o", str(out_dir)])

    assert result.returncode == 1
    assert "malformed section XML" in result.stderr
    assert not (out_dir / "broken.md").exists()


@pytest.mark.real_samples
@pytest.mark.parametrize("real_hwpx", REAL_HWPX_FIXTURES, ids=lambda p: p.name)
def test_real_hwpx_fixture_converts(real_hwpx: Path, tmp_path: Path, run_cli: RunCli) -> None:
    out_dir = tmp_path / "out"
    result = run_cli([str(real_hwpx), "-o", str(out_dir)])

    assert result.returncode == 0, result.stderr
    lines = result.stdout.split("\n")
    m = STDOUT_LINE2.match(lines[1])
    assert m, lines[1]
    paragraphs, tables = int(m.group(1)), int(m.group(2))
    if real_hwpx.name in REAL_HWPX_EXPECTED:
        assert (paragraphs, tables) == REAL_HWPX_EXPECTED[real_hwpx.name]
    md = out_dir / f"{real_hwpx.stem}.md"
    content = md.read_text(encoding="utf-8")
    assert len(content.strip()) > 0
    separators = [ln for ln in content.split("\n") if re.fullmatch(r"\|(---\|)+", ln)]
    assert len(separators) == tables
    _copy_evidence(md, md.name)
