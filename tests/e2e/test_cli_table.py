from __future__ import annotations

import os
import shutil
import subprocess
from collections.abc import Callable
from pathlib import Path

from synth_hwp5 import (
    EXPECTED_MARKDOWN_MERGED,
    EXPECTED_MARKDOWN_WITH_TABLE,
    FIXTURE_ITEMS_MERGED,
    FIXTURE_ITEMS_WITH_TABLE,
    build_cfb,
    build_docinfo,
    build_file_header,
    build_section0,
    write_hwp5,
)

RunCli = Callable[[list[str]], subprocess.CompletedProcess[str]]


def _copy_evidence(md: Path) -> None:
    evidence_dir = Path(os.environ.get("ILLY_SHOT_DIR", "tests/e2e/screenshots"))
    evidence_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(md, evidence_dir / md.name)


def test_convert_table_success(tmp_path: Path, run_cli: RunCli) -> None:
    src = write_hwp5(tmp_path / "table.hwp", FIXTURE_ITEMS_WITH_TABLE)
    out_dir = tmp_path / "out"
    result = run_cli([str(src), "-o", str(out_dir)])

    assert result.returncode == 0, result.stderr
    lines = result.stdout.split("\n")
    assert lines[0] == f"✓ table.hwp → {out_dir / 'table.md'}"
    assert lines[1] == "  단락 2개 · 표 1개"
    md = out_dir / "table.md"
    assert md.read_text(encoding="utf-8") == EXPECTED_MARKDOWN_WITH_TABLE
    _copy_evidence(md)


def test_convert_merged_table(tmp_path: Path, run_cli: RunCli) -> None:
    src = write_hwp5(tmp_path / "merged.hwp", FIXTURE_ITEMS_MERGED)
    out_dir = tmp_path / "out"
    result = run_cli([str(src), "-o", str(out_dir)])

    assert result.returncode == 0, result.stderr
    lines = result.stdout.split("\n")
    assert lines[1] == "  단락 1개 · 표 1개"
    md = out_dir / "merged.md"
    assert md.read_text(encoding="utf-8") == EXPECTED_MARKDOWN_MERGED
    _copy_evidence(md)


def test_convert_table_uncompressed_variant(tmp_path: Path, run_cli: RunCli) -> None:
    src = write_hwp5(tmp_path / "table.hwp", FIXTURE_ITEMS_WITH_TABLE, properties=0)
    out_dir = tmp_path / "out"
    result = run_cli([str(src), "-o", str(out_dir)])

    assert result.returncode == 0, result.stderr
    assert (out_dir / "table.md").read_text(encoding="utf-8") == EXPECTED_MARKDOWN_WITH_TABLE


def test_truncated_section_exit_1(tmp_path: Path, run_cli: RunCli) -> None:
    section = build_section0(FIXTURE_ITEMS_WITH_TABLE)
    data = build_cfb(
        {
            "FileHeader": build_file_header(properties=0),
            "DocInfo": build_docinfo(),
            "BodyText/Section0": section[:-10],
        }
    )
    src = tmp_path / "broken.hwp"
    src.write_bytes(data)
    out_dir = tmp_path / "out"
    result = run_cli([str(src), "-o", str(out_dir)])

    assert result.returncode == 1
    assert "truncated record" in result.stderr
    assert not (out_dir / "broken.md").exists()
