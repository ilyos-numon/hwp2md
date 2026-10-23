from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest

from samples import LEGACY_HWP5, LEGACY_HWPX
from synth_hwp5 import (
    EXPECTED_MARKDOWN_IMAGE_IN_CELL,
    EXPECTED_MARKDOWN_IMAGE_MISSING,
    EXPECTED_MARKDOWN_IMAGE_REUSE,
    EXPECTED_MARKDOWN_IMAGES,
    FIXTURE_IMAGE_PNG,
    FIXTURE_ITEMS_HEADINGS,
    FIXTURE_ITEMS_IMAGE_IN_CELL,
    FIXTURE_ITEMS_IMAGE_MISSING,
    FIXTURE_ITEMS_IMAGE_REUSE,
    FIXTURE_ITEMS_IMAGES,
    FIXTURE_ITEMS_WITH_TABLE,
    HWPTAG_SHAPE_COMPONENT_PICTURE,
    JPEG_STUB,
    PNG_1X1,
    build_cfb,
    build_docinfo,
    build_file_header,
    build_picture_control,
    build_picture_record,
    build_record,
    write_hwp5,
)
from synth_hwpx import write_hwpx

RunCli = Callable[[list[str]], subprocess.CompletedProcess[str]]

REAL_HWP5 = LEGACY_HWP5
REAL_HWPX = LEGACY_HWPX
REAL_IMAGE_EXPECTED: dict[str, tuple[int, int, dict[str, str]]] = {  # §4.10
    "form200005063113.hwp": (0, 0, {}),
    "form210001070268.hwp": (0, 0, {}),
    "(서식1) 비영리법인 현황 제출 양식.hwpx": (0, 0, {}),
    "(서식2) 사업실적 및 사업계획 제출 양식.hwpx": (0, 0, {}),
    "브라더 공공기관 보고서 양식.hwpx": (
        1,
        1,
        {"img_001.png": "f9be5b73bc6b32a79f15e52fd850b24c95203459756867104a6c297dbfc58632"},
    ),
}
STDOUT_LINE2 = re.compile(
    r"^  단락 (\d+)개 · 표 (\d+)개(?: · 제목 (\d+)개)?(?: · 이미지 (\d+)개)?$"
)
STDOUT_LINE3 = re.compile(r"^  이미지: (.+)/ \((\d+) files\)$")
IMAGE_LINE = re.compile(r"^!\[그림 (\d+)\]\((\S+)\)$")


def _copy_evidence(src: Path, name: str) -> None:
    evidence_dir = Path(os.environ.get("ILLY_SHOT_DIR", "tests/e2e/screenshots"))
    evidence_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, evidence_dir / name)


def _convert(run_cli: RunCli, src: Path, out_dir: Path) -> tuple[list[str], Path]:
    result = run_cli([str(src), "-o", str(out_dir)])
    assert result.returncode == 0, result.stderr
    return result.stdout.split("\n"), out_dir / f"{src.stem}.md"


def _check_images_success(tmp_path: Path, run_cli: RunCli, src: Path) -> tuple[Path, Path]:
    out_dir = tmp_path / "out"
    lines, md = _convert(run_cli, src, out_dir)
    images = out_dir / "doc_images"

    assert lines[0] == f"✓ {src.name} → {out_dir / 'doc.md'}"
    assert lines[1] == "  단락 2개 · 표 0개 · 제목 1개 · 이미지 2개"
    assert lines[2] == f"  이미지: {images}/ (2 files)"
    assert lines[3] == ""
    assert md.read_text(encoding="utf-8") == EXPECTED_MARKDOWN_IMAGES
    assert (images / "img_001.png").read_bytes() == PNG_1X1
    assert (images / "img_002.jpg").read_bytes() == JPEG_STUB
    assert sorted(os.listdir(images)) == ["img_001.png", "img_002.jpg"]
    return md, images


def test_convert_images_hwp5_success(tmp_path: Path, run_cli: RunCli) -> None:
    src = write_hwp5(tmp_path / "doc.hwp", FIXTURE_ITEMS_IMAGES)
    md, images = _check_images_success(tmp_path, run_cli, src)

    _copy_evidence(md, "image_hwp5.md")
    _copy_evidence(images / "img_001.png", "image_hwp5_img_001.png")


def test_convert_images_hwpx_success(tmp_path: Path, run_cli: RunCli) -> None:
    src = write_hwpx(tmp_path / "doc.hwpx", FIXTURE_ITEMS_IMAGES)
    md, _ = _check_images_success(tmp_path, run_cli, src)

    _copy_evidence(md, "image_hwpx.md")


def _both_formats(
    tmp_path: Path, run_cli: RunCli, items: list, name: str
) -> tuple[list[str], list[str], Path, Path, Path, Path]:
    src5 = write_hwp5(tmp_path / "doc.hwp", items)
    srcx = write_hwpx(tmp_path / "doc.hwpx", items)
    out5, outx = tmp_path / "out5", tmp_path / "outx"
    lines5, md5 = _convert(run_cli, src5, out5)
    linesx, mdx = _convert(run_cli, srcx, outx)
    return lines5, linesx, md5, mdx, out5 / "doc_images", outx / "doc_images"


def test_image_reuse_single_file_both_formats(tmp_path: Path, run_cli: RunCli) -> None:
    lines5, linesx, md5, mdx, dir5, dirx = _both_formats(
        tmp_path, run_cli, FIXTURE_ITEMS_IMAGE_REUSE, "reuse"
    )
    for lines, md, d in ((lines5, md5, dir5), (linesx, mdx, dirx)):
        assert lines[1] == "  단락 1개 · 표 0개 · 이미지 2개"
        assert lines[2] == f"  이미지: {d}/ (1 files)"
        assert md.read_text(encoding="utf-8") == EXPECTED_MARKDOWN_IMAGE_REUSE
        assert sorted(os.listdir(d)) == ["img_001.png"]
    assert md5.read_bytes() == mdx.read_bytes()
    _copy_evidence(md5, "image_reuse.md")


def test_image_in_table_cell_extracted_both_formats(tmp_path: Path, run_cli: RunCli) -> None:
    lines5, linesx, md5, mdx, dir5, dirx = _both_formats(
        tmp_path, run_cli, FIXTURE_ITEMS_IMAGE_IN_CELL, "cell"
    )
    for lines, md, d in ((lines5, md5, dir5), (linesx, mdx, dirx)):
        assert lines[1] == "  단락 0개 · 표 1개 · 이미지 2개"
        assert lines[2] == f"  이미지: {d}/ (2 files)"
        assert md.read_text(encoding="utf-8") == EXPECTED_MARKDOWN_IMAGE_IN_CELL
        assert sorted(os.listdir(d)) == ["img_001.jpg", "img_002.png"]
    assert md5.read_bytes() == mdx.read_bytes()
    _copy_evidence(md5, "image_cell.md")


def test_missing_binary_skipped_both_formats(tmp_path: Path, run_cli: RunCli) -> None:
    src5 = write_hwp5(tmp_path / "doc.hwp", FIXTURE_ITEMS_IMAGE_MISSING)
    srcx = write_hwpx(tmp_path / "doc.hwpx", FIXTURE_ITEMS_IMAGE_MISSING)
    for src, out_name in ((src5, "out5"), (srcx, "outx")):
        out_dir = tmp_path / out_name
        result = run_cli([str(src), "-o", str(out_dir)])
        assert result.returncode == 0, result.stderr
        lines = result.stdout.split("\n")
        assert lines[1] == "  단락 2개 · 표 0개 · 이미지 1개"
        assert lines[2] == f"  이미지: {out_dir / 'doc_images'}/ (1 files)"
        md = out_dir / "doc.md"
        assert md.read_text(encoding="utf-8") == EXPECTED_MARKDOWN_IMAGE_MISSING
        assert result.stderr == ""
    _copy_evidence(tmp_path / "out5" / "doc.md", "image_missing.md")


def test_no_image_keeps_two_line_output(tmp_path: Path, run_cli: RunCli) -> None:
    src5 = write_hwp5(tmp_path / "plain.hwp", FIXTURE_ITEMS_HEADINGS)
    out5 = tmp_path / "out5"
    result5 = run_cli([str(src5), "-o", str(out5)])
    assert result5.returncode == 0, result5.stderr
    assert result5.stdout.split("\n") == [
        f"✓ plain.hwp → {out5 / 'plain.md'}",
        "  단락 2개 · 표 1개 · 제목 3개",
        "",
    ]
    assert not (out5 / "plain_images").exists()

    srcx = write_hwpx(tmp_path / "plain.hwpx", FIXTURE_ITEMS_WITH_TABLE)
    outx = tmp_path / "outx"
    resultx = run_cli([str(srcx), "-o", str(outx)])
    assert resultx.returncode == 0, resultx.stderr
    assert resultx.stdout.split("\n") == [
        f"✓ plain.hwpx → {outx / 'plain.md'}",
        "  단락 2개 · 표 1개",
        "",
    ]
    assert "이미지" not in resultx.stdout


def test_images_uncompressed_variant(tmp_path: Path, run_cli: RunCli) -> None:
    src = write_hwp5(tmp_path / "doc.hwp", FIXTURE_ITEMS_IMAGES, properties=0)
    _, md = _convert(run_cli, src, tmp_path / "out")

    assert md.read_text(encoding="utf-8") == EXPECTED_MARKDOWN_IMAGES
    assert (tmp_path / "out" / "doc_images" / "img_001.png").read_bytes() == PNG_1X1


def test_truncated_picture_record_exit_1(tmp_path: Path, run_cli: RunCli) -> None:
    full = build_picture_control(1, level=0, last=True)
    last_record = build_record(HWPTAG_SHAPE_COMPONENT_PICTURE, 3, build_picture_record(1))
    assert full.endswith(last_record)
    section = full[: -len(last_record)] + build_record(
        HWPTAG_SHAPE_COMPONENT_PICTURE, 3, build_picture_record(1)[:72]
    )
    src = tmp_path / "broken.hwp"
    src.write_bytes(
        build_cfb(
            {
                "FileHeader": build_file_header(properties=0),
                "DocInfo": build_docinfo(images=[FIXTURE_IMAGE_PNG]),
                "BodyText/Section0": section,
            }
        )
    )
    out_dir = tmp_path / "out"
    result = run_cli([str(src), "-o", str(out_dir)])

    assert result.returncode == 1
    assert "truncated SHAPE_COMPONENT_PICTURE record" in result.stderr
    assert not (out_dir / "broken.md").exists()
    assert not (out_dir / "broken_images").exists()


@pytest.mark.parametrize("real", REAL_HWP5 + REAL_HWPX, ids=lambda p: p.name)
def test_real_fixture_images(real: Path, tmp_path: Path, run_cli: RunCli) -> None:
    out_dir = tmp_path / "out"
    lines, md = _convert(run_cli, real, out_dir)
    m = STDOUT_LINE2.match(lines[1])
    assert m, lines[1]
    images = int(m[4] or 0)
    images_dir = out_dir / f"{real.stem}_images"
    content = md.read_text(encoding="utf-8")
    link_lines = [mm for ln in content.split("\n") if (mm := IMAGE_LINE.match(ln))]

    if real.name in REAL_IMAGE_EXPECTED:
        exp_images, exp_files, exp_shas = REAL_IMAGE_EXPECTED[real.name]
        assert images == exp_images
    else:
        exp_files, exp_shas = images, {}

    assert len(link_lines) == images
    prefix = f"{real.stem.replace(' ', '%20')}_images/"
    assert all(mm[2].startswith(prefix) for mm in link_lines)

    if images == 0:
        # 건너뜀 줄(`  건너뜀: …`)이 붙으면 줄 수가 4
        has_skipped = any(ln.startswith("  건너뜀: ") for ln in lines)
        assert len(lines) == (4 if has_skipped else 3)
        assert not images_dir.exists()
    else:
        m3 = STDOUT_LINE3.match(lines[2])
        assert m3, lines[2]
        assert int(m3[2]) == exp_files
        files = sorted(images_dir.iterdir())
        assert len(files) == exp_files
        for name, sha in exp_shas.items():
            assert hashlib.sha256((images_dir / name).read_bytes()).hexdigest() == sha

    _copy_evidence(md, md.name)
    if images and (images_dir / "img_001.png").exists():
        _copy_evidence(images_dir / "img_001.png", "real_hwpx_img_001.png")
