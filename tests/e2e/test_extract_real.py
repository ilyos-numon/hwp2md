"""실제 샘플 구조 탐색 E2E (PLAN §2 C5~C12).

샘플 이름·문서 글자는 코드에 쓰지 않는다. 대상은 samples.samples_with(요소) 로 구조 탐색해서 고르고,
기대 개수는 probe 결과(레코드/XML 요소 수)에서 얻는다.
대상은 모듈 수준에서 수집해 parametrize 로 넘긴다(없으면 케이스 미생성).
Markdown 사본은 gitignored 증거 디렉터리(ILLY_SHOT_DIR 또는 tests/e2e/screenshots)에만 쓴다.
"""

from __future__ import annotations

import os
import re
import subprocess
import time
import zipfile
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest
from lxml import etree

from samples import (
    all_samples,
    classify,
    probe,
    probe_texts,
    samples_with,
)

RunCli = Callable[[list[str]], subprocess.CompletedProcess[str]]

_SUMMARY = re.compile(r"^  단락 (\d+)개 · 표 (\d+)개(?: · 제목 (\d+)개)?(?: · 이미지 (\d+)개)?$")
_SKIPPED = re.compile(r"^  건너뜀: (.+)$")
_SKIP_ITEM = re.compile(r"^(.+) (\d+)개$")
_IMAGE_LINK = re.compile(r"!\[그림 \d+\]\(\S+\)")
_WEB_LINK = re.compile(r"\[[^\]]*\]\((?:https?://|mailto:)[^)]*\)")
_FOOTNOTE_DEF = re.compile(r"^\[\^\d+\]:", re.M)
_DISPLAY_MATH = re.compile(r"\$\$[^$]+\$\$")
_INLINE_MATH = re.compile(r"(?<!\$)\$[^$\n]+\$(?!\$)")
_LIST_MARK = {"numbered": r"\d+\.\s", "bullet": r"[-*]\s"}
_HEADER_MIN_CHARS = 4  # 이보다 짧은 머리말 글자는 본문과 우연히 겹친다


@dataclass(frozen=True)
class Converted:
    src: Path
    out_dir: Path
    returncode: int
    stdout: str
    stderr: str
    seconds: float

    @property
    def md_path(self) -> Path:
        return self.out_dir / f"{self.src.stem}.md"

    @property
    def md(self) -> str:
        return self.md_path.read_text(encoding="utf-8")

    @property
    def images_dir(self) -> Path:
        return self.out_dir / f"{self.src.stem}_images"

    @property
    def image_files(self) -> list[Path]:
        return sorted(self.images_dir.iterdir()) if self.images_dir.exists() else []

    @property
    def summary(self) -> tuple[int, int, int]:
        """(단락, 표, 이미지)"""
        m = _SUMMARY.match(self.stdout.split("\n")[1])
        assert m, self.stdout
        return int(m[1]), int(m[2]), int(m[4] or 0)

    @property
    def skipped(self) -> dict[str, int]:
        for line in self.stdout.split("\n"):
            m = _SKIPPED.match(line)
            if m:
                return {
                    item[1]: int(item[2])
                    for part in m[1].split(" · ")
                    if (item := _SKIP_ITEM.match(part))
                }
        return {}


def _convert(run_cli: RunCli, src: Path, tmp_path: Path, tag: str) -> Converted:
    out_dir = tmp_path / f"out_{tag}"
    start = time.monotonic()
    result = run_cli([str(src), "-o", str(out_dir)])
    return Converted(
        src, out_dir, result.returncode, result.stdout, result.stderr, time.monotonic() - start
    )


def _convert_ok(run_cli: RunCli, src: Path, tmp_path: Path, tag: str) -> Converted:
    conv = _convert(run_cli, src, tmp_path, tag)
    assert conv.returncode == 0, conv.stderr
    return conv


def _evidence(name: str, text: str) -> None:
    evidence_dir = Path(os.environ.get("ILLY_SHOT_DIR", "tests/e2e/screenshots"))
    evidence_dir.mkdir(parents=True, exist_ok=True)
    (evidence_dir / name).write_text(text, encoding="utf-8")


def _squash(text: str) -> str:
    return re.sub(r"\s+", "", text)


def _cases(targets: Sequence[Any]) -> pytest.MarkDecorator:
    """대상 목록 하나를 매개변수 `targets` 로 넘긴다. 목록이 비면 케이스가 생성되지 않는다."""
    values = [list(targets)] if targets else []
    return pytest.mark.parametrize("targets", values, ids=["0"][: len(values)])


def _hwpx_container_count(path: Path) -> int:
    parser = etree.XMLParser(resolve_entities=False, no_network=True)
    total = 0
    with zipfile.ZipFile(path) as z:
        for name in z.namelist():
            if name.startswith("Contents/section") and name.endswith(".xml"):
                root = etree.fromstring(z.read(name), parser)
                total += sum(1 for _ in root.iter("{*}container"))
    return total


_HITS = {
    feature: samples_with(feature)
    for feature in (
        "cell_image",
        "header_footer_image",
        "textbox",
        "ole",
        "equation",
        "hyperlink_web",
        "footnote",
        "header_footer",
        "numbered",
        "bullet",
        "field_clk",
        "bmp",
        "distribution",
        "hwpml_header_footer",
    )
}
_SAMPLES = all_samples()
_SHAPED = [p for p in _SAMPLES if classify(p) == "hwpx" and _hwpx_container_count(p) > 0]
_DRM = [p for p in _SAMPLES if classify(p) == "drm"]
_NOT_HWP = [p for p in _SAMPLES if classify(p) in ("text", "unknown")]


@_cases(_HITS["cell_image"])
def test_cell_image(targets: list[Any], tmp_path: Path, run_cli: RunCli) -> None:
    """C6: 표 칸 안 그림이 링크와 이미지 파일로 나온다."""
    hits = targets
    for idx, (src, expected) in enumerate(hits):
        conv = _convert_ok(run_cli, src, tmp_path, str(idx))
        links = len(_IMAGE_LINK.findall(conv.md))
        assert links >= expected, f"#{idx}: 링크 {links} < 탐색 {expected}"
        assert len(conv.image_files) >= expected
        assert conv.summary[2] >= expected
    top_src, top_n = hits[0]
    top = _convert_ok(run_cli, top_src, tmp_path, "top")
    row_links = sum(line.count("![") for line in top.md.split("\n") if line.startswith("|"))
    assert row_links >= top_n
    assert len(top.image_files) >= top_n
    _evidence("extract_real_cell_image.md", top.md)


@_cases(_HITS["header_footer_image"])
def test_header_footer_image(targets: list[Any], tmp_path: Path, run_cli: RunCli) -> None:
    """머리말·꼬리말 안 그림은 내보내지 않고 본문 그림만 나온다 (C8 의 그림 쪽)."""
    for idx, (src, _n) in enumerate(targets):
        counts = probe(src)
        body = counts["body_image"] + counts["cell_image"]
        conv = _convert_ok(run_cli, src, tmp_path, str(idx))
        assert conv.summary[2] == body
        assert len(conv.image_files) == body
        assert len(_IMAGE_LINK.findall(conv.md)) == body
        assert conv.skipped.get("머리말·꼬리말") == counts["header_footer"]


@_cases(_HITS["textbox"])
def test_textbox(targets: list[Any], tmp_path: Path, run_cli: RunCli) -> None:
    """글상자 안 글: 비어 있지 않은 단락이 모두 Markdown 에 있다."""
    total = 0
    for idx, (src, boxes) in enumerate(targets):
        conv = _convert_ok(run_cli, src, tmp_path, str(idx))
        flat = _squash(conv.md)
        paragraphs = [t for t in probe_texts(src, "textbox") if t.strip()]
        assert paragraphs, f"#{idx}: 글상자 {boxes}개인데 글 단락이 없다"
        missing = [i for i, t in enumerate(paragraphs) if _squash(t) not in flat]
        assert not missing, f"#{idx}: 빠진 글상자 단락 {len(missing)}/{len(paragraphs)}"
        total += len(paragraphs)
        _evidence(f"extract_real_textbox_{idx}.md", conv.md)
    assert total >= 1


@_cases(_HITS["ole"])
def test_chart_ole(targets: list[Any], tmp_path: Path, run_cli: RunCli) -> None:
    """실제 OLE 샘플은 스트림이 빈 CFB 라 차트 표가 아니라 `OLE 개체 1개` 건너뜀이 정답.
    OOXML 차트 표 추출은 test_extract_cli.py 의 합성 chart 가 검증한다."""
    for idx, (src, n) in enumerate(targets):
        conv = _convert_ok(run_cli, src, tmp_path, str(idx))
        assert conv.skipped.get("OLE 개체") == n
        assert "  건너뜀: " in conv.stdout
        assert "차트:" not in conv.md
        assert "chart_legacy" not in conv.stdout


@_cases(_HITS["equation"])
def test_equation(targets: list[Any], tmp_path: Path, run_cli: RunCli) -> None:
    """C7: 수식 렌더(`$$…$$`, `$…$`) 수 = 탐색 수식 수."""
    for idx, (src, n) in enumerate(targets):
        conv = _convert_ok(run_cli, src, tmp_path, str(idx))
        display = _DISPLAY_MATH.findall(conv.md)
        inline = _INLINE_MATH.findall(_DISPLAY_MATH.sub("", conv.md))
        assert len(display) + len(inline) == n
        _evidence(f"extract_real_equation_{idx}.md", conv.md)


@_cases(_HITS["hyperlink_web"])
def test_hyperlink(targets: list[Any], tmp_path: Path, run_cli: RunCli) -> None:
    """C7: http/https/mailto 링크 수 ≥ 탐색 웹 링크 수."""
    for idx, (src, n) in enumerate(targets):
        conv = _convert_ok(run_cli, src, tmp_path, str(idx))
        assert len(_WEB_LINK.findall(conv.md)) >= n


@_cases(_HITS["footnote"])
def test_footnote(targets: list[Any], tmp_path: Path, run_cli: RunCli) -> None:
    """C7: 각주 정의 `[^n]:` 수 = 탐색 각주 수, 참조도 같은 수."""
    for idx, (src, n) in enumerate(targets):
        conv = _convert_ok(run_cli, src, tmp_path, str(idx))
        assert len(_FOOTNOTE_DEF.findall(conv.md)) == n
        refs = re.findall(r"\[\^\d+\](?!:)", conv.md)
        assert len(refs) == n
        _evidence(f"extract_real_footnote_{idx}.md", conv.md)


@_cases(_HITS["header_footer"])
def test_header_footer(targets: list[Any], tmp_path: Path, run_cli: RunCli) -> None:
    """C8: 건너뜀 N = 탐색 머리말+꼬리말 수, 머리말 글자가 본문에 새로 섞이지 않는다."""
    for idx, (src, n) in enumerate(targets):
        conv = _convert_ok(run_cli, src, tmp_path, str(idx))
        assert conv.skipped.get("머리말·꼬리말") == n
        assert re.search(rf"^  건너뜀: .*머리말·꼬리말 {n}개", conv.stdout, re.M)
        flat = _squash(conv.md)
        body = _squash("".join(probe_texts(src, "body")))
        for text in probe_texts(src, "header_footer"):
            key = _squash(text)
            if len(key) >= _HEADER_MIN_CHARS:
                # 본문에 같은 글이 이미 있으면 그만큼은 허용, 그 이상 나오면 머리말이 섞인 것
                assert flat.count(key) <= body.count(key), f"#{idx}: 머리말 글자가 본문에 섞임"


def _check_list_marks(kind: str, targets: list[Any], tmp_path: Path, run_cli: RunCli) -> None:
    """목록 단락(본문·표 칸 안)의 글 앞에 번호·글머리표 머리 글자가 붙는다."""
    checked = 0
    for idx, (src, _n) in enumerate(targets):
        conv = _convert_ok(run_cli, src, tmp_path, str(idx))
        for text in (t for t in probe_texts(src, kind) if t.strip()):
            head = [c for c in text if not c.isspace()][:8]
            pattern = _LIST_MARK[kind] + r"\s*".join(re.escape(c) for c in head)
            assert re.search(pattern, conv.md), f"#{idx}: 목록 머리 글자 없음"
            checked += 1
        if idx == 0:
            _evidence(f"extract_real_{kind}.md", conv.md)
    assert checked >= 1


@_cases(_HITS["numbered"])
def test_numbered_list(targets: list[Any], tmp_path: Path, run_cli: RunCli) -> None:
    _check_list_marks("numbered", targets, tmp_path, run_cli)


@_cases(_HITS["bullet"])
def test_bullet_list(targets: list[Any], tmp_path: Path, run_cli: RunCli) -> None:
    _check_list_marks("bullet", targets, tmp_path, run_cli)


@_cases(_HITS["field_clk"])
def test_field_text(targets: list[Any], tmp_path: Path, run_cli: RunCli) -> None:
    """누름틀 필드의 표시 글자는 본문에 남는다."""
    for idx, (src, _n) in enumerate(targets):
        conv = _convert_ok(run_cli, src, tmp_path, str(idx))
        flat = _squash(conv.md)
        texts = [t for t in probe_texts(src, "field_clk") if t.strip()]
        assert texts
        for text in texts:
            assert _squash(text) in flat


@_cases(_SHAPED)
def test_shapes_hwpx(targets: list[Any], tmp_path: Path, run_cli: RunCli) -> None:
    """도형·묶음 개체가 많은 HWPX: 오류 없이 변환되고 그 안의 그림이 빠지지 않는다."""
    for idx, src in enumerate(targets):
        counts = probe(src)
        pictures = counts["body_image"] + counts["cell_image"]
        conv = _convert_ok(run_cli, src, tmp_path, str(idx))
        assert conv.summary[0] >= 1
        assert conv.summary[2] == pictures
        assert len(conv.image_files) == pictures
        assert "본체 없는 그림" not in conv.stdout
        assert conv.stderr == ""


@_cases(_HITS["bmp"])
def test_bmp(targets: list[Any], tmp_path: Path, run_cli: RunCli) -> None:
    """BMP 는 원본 그대로 저장된다. 내용 있는 BMP 수 = .bmp 파일 수, 각 파일은 `BM` 머리.
    0바이트 BMP 는 파일을 만들지 않고 `본체 없는 그림` 으로 센다."""
    with_content = 0
    for idx, (src, total) in enumerate(targets):
        empty = probe(src)["bmp_empty"]
        good = total - empty
        conv = _convert_ok(run_cli, src, tmp_path, str(idx))
        bmps = [f for f in conv.image_files if f.suffix == ".bmp"]
        assert all(f.stat().st_size > 0 for f in conv.image_files), f"#{idx}: 0바이트 파일"
        for f in bmps:
            assert f.read_bytes().startswith(b"BM"), f"#{idx}: BMP 머리가 아님"
        assert len(bmps) >= good, f"#{idx}: .bmp {len(bmps)} < 내용 있는 BMP {good}"
        if good == 0:
            assert not bmps
        if empty:
            assert "본체 없는 그림" in conv.skipped, f"#{idx}: 건너뜀 줄에 본체 없는 그림 없음"
        with_content += good
    assert with_content >= 1


@_cases(_HITS["distribution"])
def test_distribution(targets: list[Any], tmp_path: Path, run_cli: RunCli) -> None:
    """C9: 배포용 문서는 종료 코드 0, 단락 ≥ 1, 변환 30초 이하."""
    hits = targets
    assert len(hits) >= 1
    for idx, (src, _n) in enumerate(hits):
        conv = _convert_ok(run_cli, src, tmp_path, str(idx))
        assert conv.summary[0] >= 1
        assert conv.seconds <= 30
        assert conv.md_path.exists()


@_cases(_HITS["hwpml_header_footer"])
def test_hwpml(targets: list[Any], tmp_path: Path, run_cli: RunCli) -> None:
    """C10: HWPML 은 표 0, 본문 그림 수 = 탐색 수, 머리말·꼬리말 안은 건너뜀."""
    hits = targets
    for idx, (src, in_header) in enumerate(hits):
        counts = probe(src)
        conv = _convert_ok(run_cli, src, tmp_path, str(idx))
        paragraphs, tables, images = conv.summary
        assert paragraphs >= 200
        assert tables == counts["hwpml_table"] == 0
        assert images == counts["hwpml_picture"]
        assert len(conv.image_files) == images
        assert conv.skipped == {"머리말·꼬리말": in_header}
        assert in_header == 2


@_cases(_DRM)
def test_drm(targets: list[Any], tmp_path: Path, run_cli: RunCli) -> None:
    """C11: DRM 파일은 종료 코드 3 과 `DRM protected` 오류."""
    for idx, src in enumerate(targets):
        conv = _convert(run_cli, src, tmp_path, str(idx))
        assert conv.returncode == 3, conv.stderr
        assert "DRM protected" in conv.stderr
        assert not conv.md_path.exists()


@_cases(_NOT_HWP)
def test_not_hwp(targets: list[Any], tmp_path: Path, run_cli: RunCli) -> None:
    """C11: HWP 가 아닌 텍스트 파일과 HWP 3.x 는 종료 코드 3 과 `not an HWP 5.0 file:`."""
    for idx, src in enumerate(targets):
        conv = _convert(run_cli, src, tmp_path, str(idx))
        assert conv.returncode == 3, conv.stderr
        assert "not an HWP 5.0 file:" in conv.stderr
        assert not conv.md_path.exists()


@_cases(_SAMPLES)
def test_all_samples_convert(targets: list[Any], tmp_path: Path, run_cli: RunCli) -> None:
    """C12: 모든 실제 샘플이 종료 코드 0, 거부 대상(drm/text/HWP3)이면 3. 종료 코드 1 은 0개."""
    rejected = {"drm", "text", "unknown"}
    crashed: list[int] = []
    wrong: list[tuple[int, int, str]] = []
    for idx, src in enumerate(targets):
        kind = classify(src)
        want = 3 if kind in rejected else 0
        conv = _convert(run_cli, src, tmp_path, str(idx))
        if conv.returncode == 1:
            crashed.append(idx)
        if conv.returncode != want:
            wrong.append((idx, conv.returncode, kind))
    assert not crashed, f"종료 코드 1: {len(crashed)}개"
    assert not wrong, f"기대와 다른 종료 코드: {wrong}"
