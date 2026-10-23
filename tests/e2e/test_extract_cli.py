"""합성 문서 CLI E2E: 추출 요소가 세 포맷에서 같은 결과를 내고, 보호 문서는 정확히 거부된다.

PLAN §2 C5~C12 중 합성 쪽. 실제 샘플은 test_extract_real.py 가 맡는다.
"""

from __future__ import annotations

import os
import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest

from synth_distdoc import build_hwp5_distribution
from synth_hwp5 import EXPECTED_MARKDOWN, FIXTURE_PARAGRAPHS, build_hwp5, write_hwp5
from synth_hwpml import write_hwpml
from synth_hwpx import build_zip, hwpx_entries, write_hwpx
from synth_items import EXT_FIXTURES

RunCli = Callable[[list[str]], subprocess.CompletedProcess[str]]

REPRESENTATIVE = ("link", "footnote", "header", "textbox", "numbers", "chart")
LABELS = {"header_footer": "머리말·꼬리말"}
NS_ODF = "urn:oasis:names:tc:opendocument:xmlns:manifest:1.0"
DRM_ERROR = "unsupported HWP file (DRM protected)"
PASSWORD_ERROR = "unsupported HWP file (password protected)"


def _evidence(name: str, text: str) -> None:
    evidence_dir = Path(os.environ.get("ILLY_SHOT_DIR", "tests/e2e/screenshots"))
    evidence_dir.mkdir(parents=True, exist_ok=True)
    (evidence_dir / name).write_text(text, encoding="utf-8")


def _expected_summary_tail(skipped: tuple[tuple[str, int], ...]) -> list[str]:
    if not skipped:
        return []
    return ["  건너뜀: " + " · ".join(f"{LABELS[kind]} {n}개" for kind, n in skipped)]


def _convert_three(
    tmp_path: Path, run_cli: RunCli, items: list[object]
) -> dict[str, tuple[list[str], str, Path]]:
    writers = {
        "hwp": lambda: write_hwp5(tmp_path / "doc.hwp", items),  # type: ignore[arg-type]
        "hwpx": lambda: write_hwpx(tmp_path / "doc.hwpx", items),  # type: ignore[arg-type]
        "hml": lambda: write_hwpml(tmp_path / "doc.hml", items),  # type: ignore[arg-type]
    }
    results: dict[str, tuple[list[str], str, Path]] = {}
    for fmt, write in writers.items():
        src = write()
        out_dir = tmp_path / f"out_{fmt}"
        result = run_cli([str(src), "-o", str(out_dir)])
        assert result.returncode == 0, f"{fmt}: {result.stderr}"
        assert result.stderr == ""
        lines = [ln.replace(str(out_dir), "<OUT>") for ln in result.stdout.split("\n")]
        results[fmt] = (lines, (out_dir / "doc.md").read_text(encoding="utf-8"), out_dir)
    return results


@pytest.mark.parametrize("fixture_id", REPRESENTATIVE)
def test_extract_same_across_three_formats(
    fixture_id: str, tmp_path: Path, run_cli: RunCli
) -> None:
    items, expected_md, skipped = EXT_FIXTURES[fixture_id]
    results = _convert_three(tmp_path, run_cli, items)

    for fmt, (lines, md, out_dir) in results.items():
        assert md == expected_md, f"{fmt}: Markdown 이 기대와 다름"
        assert lines[0] == f"✓ doc.{fmt} → <OUT>/doc.md"
        assert lines[-1] == ""
        tail = _expected_summary_tail(skipped)
        assert lines[-1 - len(tail) : -1] == tail, f"{fmt}: 건너뜀 줄"
        if "doc_images/" in expected_md:
            assert sorted(os.listdir(out_dir / "doc_images")) == ["img_001.png"]
        else:
            assert not (out_dir / "doc_images").exists()

    first = next(iter(results.values()))
    for fmt, (lines, md, _out) in results.items():
        assert md == first[1]
        assert lines[1:] == first[0][1:], f"{fmt}: 요약 줄이 포맷마다 다르다"
    _evidence(f"extract_cli_{fixture_id}.md", first[1])


def _drm_wrapped() -> bytes:
    return b"\x9b\x20" + b"DRMONE  " + bytes(range(256)) * 8


def _manifest(encrypted: bool) -> bytes:
    inner = (
        '<odf:encryption-data odf:checksum-type="SHA1" odf:checksum="AAAA">'
        '<odf:algorithm odf:algorithm-name="AES"/></odf:encryption-data>'
        if encrypted
        else ""
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f'<odf:manifest xmlns:odf="{NS_ODF}">'
        '<odf:file-entry odf:full-path="Contents/section0.xml" odf:media-type="text/xml">'
        f"{inner}</odf:file-entry></odf:manifest>"
    ).encode()


def _hwpx_with_manifest(path: Path, manifest: bytes) -> Path:
    entries = hwpx_entries(FIXTURE_PARAGRAPHS)
    entries["META-INF/manifest.xml"] = manifest
    path.write_bytes(build_zip(entries))
    return path


def _assert_rejected(
    run_cli: RunCli, src: Path, out_dir: Path, message: str
) -> subprocess.CompletedProcess[str]:
    result = run_cli([str(src), "-o", str(out_dir)])
    assert result.returncode == 3, result.stderr
    assert message in result.stderr
    assert result.stdout == ""
    assert not (out_dir / f"{src.stem}.md").exists()
    return result


def test_drm_wrapped_file_exit_3(tmp_path: Path, run_cli: RunCli) -> None:
    src = tmp_path / "drm.hwp"
    src.write_bytes(_drm_wrapped())
    _assert_rejected(run_cli, src, tmp_path / "out", DRM_ERROR)


def test_drm_bit_in_file_header_exit_3(tmp_path: Path, run_cli: RunCli) -> None:
    src = tmp_path / "drmbit.hwp"
    src.write_bytes(build_hwp5(FIXTURE_PARAGRAPHS, properties=0x11))
    _assert_rejected(run_cli, src, tmp_path / "out", DRM_ERROR)


def test_password_hwp5_exit_3(tmp_path: Path, run_cli: RunCli) -> None:
    src = write_hwp5(tmp_path / "locked.hwp", FIXTURE_PARAGRAPHS, properties=0x3)
    _assert_rejected(run_cli, src, tmp_path / "out", PASSWORD_ERROR)


def test_password_hwpx_manifest_exit_3(tmp_path: Path, run_cli: RunCli) -> None:
    src = _hwpx_with_manifest(tmp_path / "locked.hwpx", _manifest(encrypted=True))
    _assert_rejected(run_cli, src, tmp_path / "out", PASSWORD_ERROR)


def test_plain_hwpx_manifest_still_converts(tmp_path: Path, run_cli: RunCli) -> None:
    """실패 경로의 짝: 암호화 항목이 없는 매니페스트는 거부하지 않는다."""
    src = _hwpx_with_manifest(tmp_path / "plain.hwpx", _manifest(encrypted=False))
    result = run_cli([str(src), "-o", str(tmp_path / "out")])
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "out" / "plain.md").read_text(encoding="utf-8") == EXPECTED_MARKDOWN


def test_missing_file_is_not_a_protection_error(tmp_path: Path, run_cli: RunCli) -> None:
    result = run_cli([str(tmp_path / "nope.hwp"), "-o", str(tmp_path / "out")])
    assert result.returncode != 0
    assert "DRM" not in result.stderr
    assert "password" not in result.stderr


@pytest.mark.parametrize("compressed", [True, False])
def test_distribution_document_converts(compressed: bool, tmp_path: Path, run_cli: RunCli) -> None:
    src = tmp_path / "dist.hwp"
    src.write_bytes(build_hwp5_distribution(FIXTURE_PARAGRAPHS, compressed=compressed))
    out_dir = tmp_path / "out"
    result = run_cli([str(src), "-o", str(out_dir)])

    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    assert (out_dir / "dist.md").read_text(encoding="utf-8") == EXPECTED_MARKDOWN
    assert result.stdout.split("\n")[1] == "  단락 3개 · 표 0개"
    _evidence(f"extract_cli_distribution_{'z' if compressed else 'raw'}.md", EXPECTED_MARKDOWN)
