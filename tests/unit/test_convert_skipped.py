"""건너뜀 보고 경로: 리더 → ConvertResult/MemoryResult → 페이로드, iter_images 기반 이미지 수집."""

import sys
from pathlib import Path

import pytest

from hwp2md import memory
from hwp2md.blocks import (
    Block,
    Image,
    ListInfo,
    Note,
    Paragraph,
    Table,
    make_paragraph,
    make_table,
)
from hwp2md.convert import _count_blocks, _write_images, convert
from hwp2md.memory import convert_bytes, to_payload
from hwp2md.skips import SKIP_LABELS, SkipCounter

convert_module = sys.modules["hwp2md.convert"]  # hwp2md.convert 속성은 함수

BLOCKS: list[Block] = [Paragraph("본문")]


def _fake_reader(path: object, skips: SkipCounter | None = None) -> list[Block]:
    assert skips is not None
    skips.add("image_missing")
    skips.add("header_footer", 2)
    skips.add("ole")
    skips.add("ole")
    return list(BLOCKS)


def _plain_reader(path: object, skips: SkipCounter | None = None) -> list[Block]:
    return list(BLOCKS)


EXPECTED = (("header_footer", 2), ("ole", 2), ("image_missing", 1))


def test_convert_result_skipped(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    src = tmp_path / "a.hwp"
    src.write_bytes(b"x")
    monkeypatch.setattr(convert_module, "read_blocks", _fake_reader)
    result = convert(src, tmp_path / "out")
    assert result.skipped == EXPECTED


def test_memory_result_and_payload_skipped(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(memory, "read_blocks", _fake_reader)
    result = convert_bytes(b"x", "a.hwp")
    assert result.skipped == EXPECTED
    assert to_payload(result)["skipped"] == [
        {"kind": "header_footer", "label": "머리말·꼬리말", "count": 2},
        {"kind": "ole", "label": "OLE 개체", "count": 2},
        {"kind": "image_missing", "label": "본체 없는 그림", "count": 1},
    ]
    kinds = [item["kind"] for item in to_payload(result)["skipped"]]
    assert kinds == [k for k in SKIP_LABELS if k in kinds]


def test_no_skips(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    src = tmp_path / "a.hwp"
    src.write_bytes(b"x")
    monkeypatch.setattr(convert_module, "read_blocks", _plain_reader)
    monkeypatch.setattr(memory, "read_blocks", _plain_reader)
    assert convert(src, tmp_path / "out").skipped == ()
    result = convert_bytes(b"x", "a.hwp")
    assert result.skipped == ()
    assert to_payload(result)["skipped"] == []


def test_default_skipped_field() -> None:
    assert convert_module.ConvertResult(Path("a"), Path("b"), 0, 0, 0, "").skipped == ()


IMG_A = Image("img_001.png", b"A")
IMG_B = Image("img_002.png", b"B")
IMG_C = Image("img_003.png", b"C")
IMG_D = Image("img_004.png", b"D")


def _image_blocks() -> list[Block]:
    note_para = make_paragraph(["각주 글", IMG_D])
    assert note_para is not None
    return [
        Paragraph("첫 단락"),
        make_table([[["칸 ", IMG_B], ["글"]], [[IMG_C], [IMG_B]]]),
        IMG_A,
        Paragraph("제목", level=1),
        Note("footnote", 1, (note_para, Paragraph("둘째"))),
    ]


def test_count_blocks_iter_images() -> None:
    blocks = _image_blocks()
    # 단락 1 (Note 안 단락 제외), 표 1, 제목 1, 이미지 = iter_images 개수 (재참조 포함) 5
    assert _count_blocks(blocks) == (1, 1, 1, 5)


def test_count_blocks_list_paragraph() -> None:
    blocks: list[Block] = [Paragraph("항목", list_info=ListInfo("bullet", 0, "")), Paragraph("")]
    assert _count_blocks(blocks) == (1, 0, 0, 0)


def test_write_images_order(tmp_path: Path) -> None:
    files = _write_images(_image_blocks(), tmp_path / "imgs")
    assert [f.name for f in files] == ["img_002.png", "img_003.png", "img_001.png", "img_004.png"]
    assert (tmp_path / "imgs" / "img_004.png").read_bytes() == b"D"


def test_convert_bytes_images_order(monkeypatch: pytest.MonkeyPatch) -> None:
    def reader(path: object, skips: SkipCounter | None = None) -> list[Block]:
        return _image_blocks()

    monkeypatch.setattr(memory, "read_blocks", reader)
    result = convert_bytes(b"x", "a.hwp")
    assert [img.file_name for img in result.images] == [
        "img_002.png",
        "img_003.png",
        "img_001.png",
        "img_004.png",
    ]
    assert result.image_count == 5
    assert to_payload(result)["counts"]["images"] == 5


def test_table_is_inline_table() -> None:
    table = _image_blocks()[1]
    assert isinstance(table, Table)
    assert table.cells != ()
