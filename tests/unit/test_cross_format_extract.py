"""세 입력 포맷(HWP 5.0·HWPX·HWPML)이 같은 요소 구성에서 같은 Markdown·skipped 를 내는지.

OpenSpec element-extraction "세 입력 포맷은 같은 내용에 같은 Markdown 을 낸다".
합성기가 직접 만들지 못하는 구성(표 칸 안 목록 단락, 글자-글상자-글자 단락)은
합성기 출력을 이 파일 안에서 고쳐 만든다.
"""

import re
import struct
from collections.abc import Callable, Sequence
from pathlib import Path

import pytest

from hwp2md import convert
from hwp2md.convert import ConvertResult
from hwp2md.hwp5.records import HWPTAG_PARA_HEADER, HWPTAG_PARA_TEXT
from synth_hwp5 import (
    FIXTURE_ITEMS_HEADING_EDGE,
    FIXTURE_ITEMS_HEADING_IN_CELL,
    FIXTURE_ITEMS_HEADINGS,
    FIXTURE_ITEMS_IMAGE_IN_CELL,
    FIXTURE_ITEMS_IMAGE_MISSING,
    FIXTURE_ITEMS_IMAGE_REUSE,
    FIXTURE_ITEMS_IMAGES,
    FIXTURE_ITEMS_MERGED,
    FIXTURE_ITEMS_WITH_TABLE,
    FIXTURE_PARAGRAPHS,
    LIST_PARA_SHAPE_BASE,
    SynthCell,
    SynthTable,
    build_cfb,
    build_docinfo,
    build_file_header,
    build_record,
    build_section0,
    compress_raw,
    list_shape_keys,
    write_hwp5,
)
from synth_hwpml import head_xml, hwpml_text, list_shapes, write_hwpml
from synth_hwpml import text_xml as ml_text_xml
from synth_hwpx import (
    FIXTURE_PARAGRAPHS_INLINE,
    SECPR_RUN,
    build_zip,
    header_xml,
    hwpx_entries,
    list_para_pr_id,
    p_attrs,
    write_hwpx,
)
from synth_hwpx import text_xml as x_text_xml
from synth_items import EXT_FIXTURES, SynthListPara, SynthTextBox

_FORMATS = ("hwp", "hwpx", "hml")
_WRITERS: dict[str, Callable[[Path, list[object]], Path]] = {
    "hwp": write_hwp5,  # type: ignore[dict-item]
    "hwpx": write_hwpx,  # type: ignore[dict-item]
    "hml": write_hwpml,  # type: ignore[dict-item]
}


def _convert_all(tmp_path: Path, items: list[object]) -> dict[str, ConvertResult]:
    """세 포맷 doc.<ext> 를 만들어 변환. 이미지 폴더 이름이 같도록 포맷마다 폴더를 나눈다."""
    out: dict[str, ConvertResult] = {}
    for ext in _FORMATS:
        src = _WRITERS[ext](tmp_path / ext / f"doc.{ext}", items)
        out[ext] = convert(src, tmp_path / f"out_{ext}")
    return out


def _summary(result: ConvertResult) -> tuple[object, ...]:
    return (
        result.markdown,
        result.skipped,
        result.paragraph_count,
        result.table_count,
        result.heading_count,
        result.image_count,
        tuple(p.name for p in result.image_files),
        tuple(p.read_bytes() for p in result.image_files),
    )


# --- EXT_FIXTURES 16개 × 3포맷 ---


@pytest.mark.parametrize("fixture_id", list(EXT_FIXTURES))
def test_ext_fixture_same_in_three_formats(tmp_path: Path, fixture_id: str) -> None:
    items, expected_md, expected_skipped = EXT_FIXTURES[fixture_id]
    results = _convert_all(tmp_path, items)
    for ext, result in results.items():
        assert result.markdown == expected_md, ext
        assert result.skipped == expected_skipped, ext
    assert _summary(results["hwp"]) == _summary(results["hwpx"]) == _summary(results["hml"])


def test_ext_fixture_ids() -> None:
    assert len(EXT_FIXTURES) == 16


# --- 기존 FIXTURE_ITEMS_* 의 HWPML 판 ---

_LEGACY = {
    "paragraphs": FIXTURE_PARAGRAPHS,
    "with_table": FIXTURE_ITEMS_WITH_TABLE,
    "merged": FIXTURE_ITEMS_MERGED,
    "headings": FIXTURE_ITEMS_HEADINGS,
    "heading_edge": FIXTURE_ITEMS_HEADING_EDGE,
    "heading_in_cell": FIXTURE_ITEMS_HEADING_IN_CELL,
    "images": FIXTURE_ITEMS_IMAGES,
    "image_reuse": FIXTURE_ITEMS_IMAGE_REUSE,
    "image_in_cell": FIXTURE_ITEMS_IMAGE_IN_CELL,
    "image_missing": FIXTURE_ITEMS_IMAGE_MISSING,
}


@pytest.mark.parametrize("fixture_id", list(_LEGACY))
def test_legacy_fixture_hwpml_same_as_hwp5_and_hwpx(tmp_path: Path, fixture_id: str) -> None:
    results = _convert_all(tmp_path, list(_LEGACY[fixture_id]))
    assert _summary(results["hml"]) == _summary(results["hwp"]) == _summary(results["hwpx"])


def test_inline_fixture_hwpml_same_as_hwpx(tmp_path: Path) -> None:
    items: list[object] = list(FIXTURE_PARAGRAPHS_INLINE)
    x = convert(write_hwpx(tmp_path / "x" / "doc.hwpx", items), tmp_path / "outx")  # type: ignore[arg-type]
    ml = convert(write_hwpml(tmp_path / "ml" / "doc.hml", items), tmp_path / "outml")  # type: ignore[arg-type]
    assert _summary(ml) == _summary(x)


# --- 표 칸 안 목록 단락 ---
# 칸 단락은 SynthListPara 로 적고, 합성기에는 글자만 넘긴 뒤
# 그 단락의 문단 모양을 목록 모양으로 고친다.
# 그래서 문서 안 목록 단락 글자는 서로 달라야 한다.

CellPara = str | SynthListPara


def _table(cells: Sequence[Sequence[Sequence[CellPara]]]) -> SynthTable:
    """cells[r][c] = 칸 단락들. SynthCell 에 SynthListPara 를 그대로 둔다(_plain 이 바꾼다)."""
    return SynthTable(
        rows=len(cells),
        cols=len(cells[0]),
        cells=tuple(
            SynthCell(tuple(paras), col=c, row=r)  # type: ignore[arg-type]
            for r, row in enumerate(cells)
            for c, paras in enumerate(row)
        ),
    )


def _lists(items: Sequence[object]) -> list[SynthListPara]:
    """본문·칸의 SynthListPara 를 문서 순서로."""
    out: list[SynthListPara] = []
    for item in items:
        if isinstance(item, SynthListPara):
            out.append(item)
        elif isinstance(item, SynthTable):
            for cell in item.cells:
                out.extend(p for p in cell.paragraphs if isinstance(p, SynthListPara))
    return out


def _plain(items: Sequence[object]) -> list[object]:
    """SynthListPara(본문·칸) → 그 글자. 목록 모양은 포맷별로 나중에 고친다."""
    out: list[object] = []
    for item in items:
        if isinstance(item, SynthListPara):
            out.append(item.text)
        elif isinstance(item, SynthTable):
            cells = tuple(
                SynthCell(
                    tuple(p.text if isinstance(p, SynthListPara) else p for p in c.paragraphs),
                    col=c.col,
                    row=c.row,
                )
                for c in item.cells
            )
            out.append(SynthTable(item.rows, item.cols, cells))
        else:
            out.append(item)
    return out


def _hwp5_records(section: bytes) -> list[tuple[int, int, bytes]]:
    out: list[tuple[int, int, bytes]] = []
    pos = 0
    while pos < len(section):
        (head,) = struct.unpack_from("<I", section, pos)
        pos += 4
        size = head >> 20
        if size == 0xFFF:
            (size,) = struct.unpack_from("<I", section, pos)
            pos += 4
        out.append((head & 0x3FF, (head >> 10) & 0x3FF, section[pos : pos + size]))
        pos += size
    return out


def _hwp5_patch(section: bytes, fix: Callable[[str, bytes, bytes], tuple[bytes, bytes]]) -> bytes:
    """단락마다 fix(글자, PARA_HEADER payload, PARA_TEXT payload) → 새 (header, text) payload."""
    recs = _hwp5_records(section)
    for k in range(len(recs) - 1):
        tag, level, payload = recs[k]
        ntag, nlevel, npayload = recs[k + 1]
        if tag == HWPTAG_PARA_HEADER and ntag == HWPTAG_PARA_TEXT:
            text = npayload.decode("utf-16-le", errors="replace")
            header, body = fix(text, payload, npayload)
            recs[k] = (tag, level, header)
            recs[k + 1] = (ntag, nlevel, body)
    return b"".join(build_record(t, lv, p) for t, lv, p in recs)


def _write_hwp5_raw(
    path: Path, items: Sequence[object], section: bytes, lists: list[SynthListPara]
) -> Path:
    docinfo = build_docinfo(lists=lists)
    streams = {
        "FileHeader": build_file_header(properties=0x1),
        "DocInfo": compress_raw(docinfo),
        "BodyText/Section0": compress_raw(section),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(build_cfb(streams))
    return path


def _write_list_hwp5(path: Path, items: Sequence[object]) -> Path:
    lists = _lists(items)
    keys = list_shape_keys(lists)
    shape_of = {p.text: LIST_PARA_SHAPE_BASE + keys.index((p.kind, p.depth)) for p in lists}

    def fix(text: str, header: bytes, body: bytes) -> tuple[bytes, bytes]:
        key = text.rstrip("\r")
        if key in shape_of:
            header = header[:8] + struct.pack("<H", shape_of[key]) + header[10:]
        return header, body

    section = _hwp5_patch(build_section0(_plain(items)), fix)  # type: ignore[arg-type]
    return _write_hwp5_raw(path, items, section, lists)


def _write_list_hwpx(path: Path, items: Sequence[object]) -> Path:
    lists = _lists(items)
    plain = _plain(items)
    entries = hwpx_entries(plain)  # type: ignore[arg-type]
    entries["Contents/header.xml"] = header_xml(1, outline=False, list_items=lists)
    sec = entries["Contents/section0.xml"].decode("utf-8")
    for p in lists:
        run = f'<hp:run charPrIDRef="0"><hp:t>{x_text_xml(p.text)}</hp:t>'
        # 본문 첫 단락이면 글자 run 앞에 구역 속성 run 이 있다
        pattern = re.escape(p_attrs(0)) + f"(>(?:{re.escape(SECPR_RUN)})?{re.escape(run)})"
        attrs = p_attrs(list_para_pr_id(p.kind, p.depth))
        sec, n = re.subn(pattern, lambda m, a=attrs: a + m.group(1), sec)
        assert n == 1, p.text
    entries["Contents/section0.xml"] = sec.encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(build_zip(entries))
    return path


def _write_list_hwpml(path: Path, items: Sequence[object]) -> Path:
    lists = _lists(items)
    text = hwpml_text(_plain(items))  # type: ignore[arg-type]
    text = re.sub(r"<HEAD .*?</HEAD>", lambda _: head_xml([], lists), text, count=1, flags=re.S)
    shapes = list_shapes(lists)
    for p in lists:
        old = f'<P ParaShape="0" Style="0"><TEXT CharShape="0"><CHAR>{ml_text_xml(p.text)}</CHAR>'
        new = old.replace('ParaShape="0"', f'ParaShape="{shapes[(p.kind, p.depth)]}"')
        assert text.count(old) == 1, p.text
        text = text.replace(old, new)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))
    return path


_LIST_WRITERS = {"hwp": _write_list_hwp5, "hwpx": _write_list_hwpx, "hml": _write_list_hwpml}

_CELL_LISTS: dict[str, tuple[list[object], str | None]] = {
    "cell_bullets": (
        [
            "앞",
            _table(
                [
                    [
                        [SynthListPara("하나", "bullet"), SynthListPara("둘", "bullet")],
                        ["값"],
                    ]
                ]
            ),
        ],
        "앞\n\n| - 하나<br>- 둘 | 값 |\n|---|---|\n",
    ),
    "cell_numbers": (
        [
            "앞",
            _table(
                [
                    [
                        [SynthListPara("가", "number"), SynthListPara("나", "number")],
                        ["값"],
                    ]
                ]
            ),
        ],
        "앞\n\n| 1. 가<br>2. 나 | 값 |\n|---|---|\n",
    ),
    "cell_mixed": (
        [
            "앞",
            _table(
                [
                    [["머리"], ["설명"]],
                    [
                        ["첫 줄", SynthListPara("항목", "bullet")],
                        [SynthListPara("번호 항목", "number", template="(^1)")],
                    ],
                ]
            ),
        ],
        "앞\n\n| 머리 | 설명 |\n|---|---|\n| 첫 줄<br>- 항목 | (1) 번호 항목 |\n",
    ),
    "cell_and_body": (
        [
            "앞",
            SynthListPara("본문 하나", "number"),
            _table([[[SynthListPara("칸 하나", "number")], [SynthListPara("칸 점", "bullet")]]]),
            SynthListPara("본문 둘", "number"),
        ],
        None,  # 칸과 본문의 번호 이어짐은 세 포맷이 같기만 하면 된다
    ),
}


@pytest.mark.parametrize("fixture_id", list(_CELL_LISTS))
def test_cell_list_same_in_three_formats(tmp_path: Path, fixture_id: str) -> None:
    items, expected = _CELL_LISTS[fixture_id]
    results = {
        ext: convert(_LIST_WRITERS[ext](tmp_path / ext / f"doc.{ext}", items), tmp_path / ext)
        for ext in _FORMATS
    }
    if expected is not None:
        for ext, result in results.items():
            assert result.markdown == expected, ext
    assert _summary(results["hwp"]) == _summary(results["hwpx"]) == _summary(results["hml"])


def test_cell_list_writers_match_synth_for_body_lists(tmp_path: Path) -> None:
    """고친 합성 결과가 합성기의 본문 목록과 같은 문서를 만든다 (패치 방식 자체 확인)."""
    items, expected_md, _ = EXT_FIXTURES["bullets"]
    for ext in _FORMATS:
        src = _LIST_WRITERS[ext](tmp_path / ext / f"doc.{ext}", items)
        assert convert(src, tmp_path / f"o_{ext}").markdown == expected_md, ext


# --- 글자-글상자-글자 혼합 단락 ---
# 세 포맷 모두 글상자 안 단락을 앵커 단락 글자 뒤에 둔다 (HWP 5.0·HWPX 방식).

_BOX = ("상자1", "상자2")
_MIXED_MD = "앞뒤\n\n상자1\n\n상자2\n\n끝\n"


def _write_mixed_hwp5(path: Path) -> Path:
    items: list[object] = [SynthTextBox("앞", _BOX), "끝"]

    def fix(text: str, header: bytes, body: bytes) -> tuple[bytes, bytes]:
        if text.startswith("앞"):
            body = body[:-2] + "뒤".encode("utf-16-le") + body[-2:]
            (nchars,) = struct.unpack_from("<I", header, 0)
            header = struct.pack("<I", nchars + 1) + header[4:]
        return header, body

    section = _hwp5_patch(build_section0(items), fix)  # type: ignore[arg-type]
    return _write_hwp5_raw(path, items, section, [])


def _write_mixed_hwpx(path: Path) -> Path:
    entries = hwpx_entries([SynthTextBox("뒤", _BOX), "끝"])
    sec = entries["Contents/section0.xml"].decode("utf-8")
    old = '<hp:run charPrIDRef="0"><hp:rect '
    assert sec.count(old) == 1
    sec = sec.replace(old, '<hp:run charPrIDRef="0"><hp:t>앞</hp:t></hp:run>' + old)
    entries["Contents/section0.xml"] = sec.encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(build_zip(entries))
    return path


def _write_mixed_hwpml(path: Path) -> Path:
    text = hwpml_text([SynthTextBox("앞", _BOX), "끝"])
    old = "</RECTANGLE></TEXT>"
    assert text.count(old) == 1
    text = text.replace(old, "</RECTANGLE><CHAR>뒤</CHAR></TEXT>")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))
    return path


def test_text_box_text_mixed_paragraph_same_in_three_formats(tmp_path: Path) -> None:
    results = {
        "hwp": convert(_write_mixed_hwp5(tmp_path / "a" / "doc.hwp"), tmp_path / "o5"),
        "hwpx": convert(_write_mixed_hwpx(tmp_path / "b" / "doc.hwpx"), tmp_path / "ox"),
        "hml": convert(_write_mixed_hwpml(tmp_path / "c" / "doc.hml"), tmp_path / "oml"),
    }
    for ext, result in results.items():
        assert result.markdown == _MIXED_MD, ext
    assert _summary(results["hwp"]) == _summary(results["hwpx"]) == _summary(results["hml"])
