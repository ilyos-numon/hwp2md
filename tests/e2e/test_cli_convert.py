from __future__ import annotations

import os
import re
import shutil
import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest

from synth_hwp5 import EXPECTED_MARKDOWN, FIXTURE_PARAGRAPHS, write_hwp5

RunCli = Callable[[list[str]], subprocess.CompletedProcess[str]]

REAL_FIXTURES = sorted(Path(__file__).resolve().parents[1].joinpath("fixtures").glob("*.hwp"))


def test_convert_synthetic_success(synthetic_hwp: Path, tmp_path: Path, run_cli: RunCli) -> None:
    out_dir = tmp_path / "out"
    result = run_cli([str(synthetic_hwp), "-o", str(out_dir)])

    assert result.returncode == 0, result.stderr
    lines = result.stdout.split("\n")
    assert lines[0] == f"✓ sample.hwp → {out_dir / 'sample.md'}"
    assert lines[1] == "  단락 3개 · 표 0개"
    md = out_dir / "sample.md"
    assert md.read_text(encoding="utf-8") == EXPECTED_MARKDOWN

    evidence_dir = Path(os.environ.get("ILLY_SHOT_DIR", "tests/e2e/screenshots"))
    evidence_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(md, evidence_dir / "sample.md")


def test_convert_uncompressed_variant(tmp_path: Path, run_cli: RunCli) -> None:
    src = write_hwp5(tmp_path / "sample.hwp", FIXTURE_PARAGRAPHS, properties=0)
    out_dir = tmp_path / "out"
    result = run_cli([str(src), "-o", str(out_dir)])

    assert result.returncode == 0, result.stderr
    assert (out_dir / "sample.md").read_text(encoding="utf-8") == EXPECTED_MARKDOWN


def test_missing_input_exit_2(tmp_path: Path, run_cli: RunCli) -> None:
    result = run_cli([str(tmp_path / "nope.hwp")])

    assert result.returncode == 2
    assert "file not found:" in result.stderr


def test_not_hwp_exit_3(tmp_path: Path, run_cli: RunCli) -> None:
    fake = tmp_path / "fake.hwp"
    fake.write_bytes(b"plain text, not an ole file\n" * 100)
    out_dir = tmp_path / "out"
    result = run_cli([str(fake), "-o", str(out_dir)])

    assert result.returncode == 3
    assert "not an HWP 5.0 file:" in result.stderr
    assert not (out_dir / "fake.md").exists()


def test_encrypted_flag_exit_3(tmp_path: Path, run_cli: RunCli) -> None:
    src = write_hwp5(tmp_path / "enc.hwp", FIXTURE_PARAGRAPHS, properties=0x3)
    result = run_cli([str(src), "-o", str(tmp_path / "out")])

    assert result.returncode == 3
    assert "unsupported HWP file" in result.stderr


REAL_FIXTURE_MIN_TABLES = {"form200005063113.hwp": 1}  # 표가 확인된 샘플만


@pytest.mark.real_samples
@pytest.mark.parametrize("real_hwp", REAL_FIXTURES, ids=lambda p: p.name)
def test_real_fixture_converts(real_hwp: Path, tmp_path: Path, run_cli: RunCli) -> None:
    out_dir = tmp_path / "out"
    result = run_cli([str(real_hwp), "-o", str(out_dir)])
    assert result.returncode == 0, result.stderr
    lines = result.stdout.split("\n")
    m = re.match(r"^  단락 (\d+)개 · 표 (\d+)개(?: · 제목 \d+개)?(?: · 이미지 \d+개)?$", lines[1])
    assert m, lines[1]
    table_count = int(m.group(2))
    md = out_dir / f"{real_hwp.stem}.md"
    content = md.read_text(encoding="utf-8")
    assert len(content.strip()) > 0
    separators = [ln for ln in content.split("\n") if re.fullmatch(r"\|(---\|)+", ln)]
    assert len(separators) == table_count  # 출력된 Markdown 표 수 == CLI 가 보고한 표 수
    assert table_count >= REAL_FIXTURE_MIN_TABLES.get(real_hwp.name, 0)
    evidence_dir = Path(os.environ.get("ILLY_SHOT_DIR", "tests/e2e/screenshots"))
    evidence_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(md, evidence_dir / md.name)
