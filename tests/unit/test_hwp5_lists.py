"""HWP 5.0 목록: 번호·글머리표 문단 모양, NUMBERING·BULLET 레코드, 단락 ListInfo."""

from collections.abc import Sequence
from pathlib import Path

import pytest

from hwp2md.blocks import Block, ListInfo, Paragraph
from hwp2md.convert import convert
from hwp2md.hwp5.body import ReadContext, parse_blocks
from hwp2md.hwp5.docinfo import (
    BulletDef,
    NumberingDef,
    ParaShape,
    num_format,
    parse_bullet,
    parse_docinfo,
    parse_numbering,
    parse_para_shape,
)
from hwp2md.hwp5.records import HWPTAG_BULLET, HWPTAG_NUMBERING, iter_records
from synth_hwp5 import (
    BULLET_CHAR,
    NUM_FORMAT_CIRCLED_DIGIT,
    NUM_FORMAT_DIGIT,
    NUM_FORMAT_HANGUL,
    build_bullet,
    build_docinfo,
    build_list_para_shape,
    build_numbering,
    build_section0,
    write_hwp5,
)
from synth_items import EXT_FIXTURES, EXT_IDS_BY_STAGE, SynthListPara


def _read(items: Sequence[object], formats: Sequence[int] = ()) -> list[Block]:
    lists = [x for x in items if isinstance(x, SynthListPara)]
    docinfo = parse_docinfo(build_docinfo(lists=lists, list_formats=formats))
    section = build_section0(items)  # type: ignore[arg-type]
    return parse_blocks(iter_records(section), docinfo, None, ReadContext())


def _infos(blocks: Sequence[Block]) -> list[ListInfo | None]:
    return [b.list_info for b in blocks if isinstance(b, Paragraph)]


def test_tag_constants() -> None:
    assert HWPTAG_NUMBERING == 0x17
    assert HWPTAG_BULLET == 0x18


@pytest.mark.parametrize("fixture_id", EXT_IDS_BY_STAGE["lists"])
def test_list_ext_fixtures_markdown(fixture_id: str, tmp_path: Path) -> None:
    items, expected_md, expected_skipped = EXT_FIXTURES[fixture_id]
    src = write_hwp5(tmp_path / "doc.hwp", items)  # type: ignore[arg-type]
    result = convert(src, tmp_path / "out")
    assert result.markdown == expected_md
    assert result.skipped == expected_skipped


def test_parse_para_shape_head_id_and_kind() -> None:
    assert parse_para_shape(build_list_para_shape("number", 2, head_id=3)) == ParaShape(2, 2, 3)
    assert parse_para_shape(build_list_para_shape("bullet", 0, head_id=1)) == ParaShape(3, 0, 1)
    # 오프셋 30 이 없는 짧은 레코드 → ID 0
    assert parse_para_shape((2 << 23).to_bytes(4, "little")).head_id == 0


def test_parse_numbering_levels_formats_and_starts() -> None:
    payload = build_numbering(
        ["^1.", "^2)"],
        formats=[NUM_FORMAT_DIGIT, NUM_FORMAT_HANGUL],
        start=0,
        level_starts=(5, 1, 1, 1, 1, 1, 1),
    )
    numbering = parse_numbering(payload)
    assert len(numbering.levels) == 7
    assert [lv.template for lv in numbering.levels[:3]] == ["^1.", "^2)", "^3."]
    assert [lv.num_format for lv in numbering.levels[:2]] == ["DIGIT", "HANGUL_SYLLABLE"]
    assert numbering.start == 0
    assert numbering.level_start(0) == 5
    assert numbering.level_start(1) == 1


def test_parse_numbering_without_level_starts_uses_start() -> None:
    numbering = parse_numbering(build_numbering(["^1."], start=3, level_starts=None))
    assert numbering.levels[0].start is None
    assert numbering.level_start(0) == 3
    assert parse_numbering(build_numbering(["^1."], start=0, level_starts=None)).level_start(0) == 1


def test_parse_numbering_truncated_does_not_fail() -> None:
    numbering = parse_numbering(build_numbering(["^1."])[:20])
    assert len(numbering.levels) == 1
    assert numbering.levels[0].template == "^1."
    assert parse_numbering(b"") == NumberingDef(levels=(), start=0)


def test_parse_bullet_char() -> None:
    assert parse_bullet(build_bullet()) == BulletDef(BULLET_CHAR)
    assert parse_bullet(b"\x00" * 5) == BulletDef("")


def test_num_format_codes() -> None:
    assert num_format(0) == "DIGIT"
    assert num_format(1) == "CIRCLED_DIGIT"
    assert num_format(8) == "HANGUL_SYLLABLE"
    assert num_format(13) == "HANJA_DIGIT"
    assert num_format(12) == "DIGIT"  # 모르는 모양
    assert num_format(31) == "DIGIT"


def test_docinfo_collects_numberings_and_bullets_one_based() -> None:
    info = parse_docinfo(build_docinfo(lists=[SynthListPara("가", "number")]))
    assert len(info.numberings) == 1
    assert len(info.bullets) == 1
    assert info.numbering(1) is info.numberings[0]
    assert info.numbering(0) is None
    assert info.bullet(1) == BulletDef(BULLET_CHAR)
    assert info.bullet(2) is None


def test_bullet_paragraphs_get_list_info() -> None:
    blocks = _read([SynthListPara("하나", "bullet"), SynthListPara("둘", "bullet", depth=1), "끝"])
    assert _infos(blocks) == [ListInfo("bullet", 0, ""), ListInfo("bullet", 1, ""), None]


def test_number_counter_resets_deeper_levels() -> None:
    items = [
        SynthListPara("a", "number"),
        SynthListPara("b", "number", depth=1, template="^1.^2."),
        SynthListPara("c", "number", depth=1, template="^1.^2."),
        SynthListPara("d", "number"),
        SynthListPara("e", "number", depth=1, template="^1.^2."),
    ]
    labels = [i.label for i in _infos(_read(items)) if i is not None]
    assert labels == ["1.", "1.1.", "1.2.", "2.", "2.1."]
    assert [i.depth for i in _infos(_read(items)) if i is not None] == [0, 1, 1, 0, 1]


def test_number_counter_continues_across_sections() -> None:
    items = [SynthListPara("a", "number"), SynthListPara("b", "number")]
    docinfo = parse_docinfo(build_docinfo(lists=items))
    ctx = ReadContext()
    blocks = [
        *parse_blocks(iter_records(build_section0(items)), docinfo, None, ctx),  # type: ignore[arg-type]
        *parse_blocks(iter_records(build_section0(items)), docinfo, None, ctx),  # type: ignore[arg-type]
    ]
    assert [i.label for i in _infos(blocks) if i is not None] == ["1.", "2.", "3.", "4."]


@pytest.mark.parametrize(
    ("fmt", "template", "expected"),
    [
        (NUM_FORMAT_DIGIT, "^1.", ["1.", "2.", "3."]),
        (NUM_FORMAT_CIRCLED_DIGIT, "^1", ["①", "②", "③"]),
        (NUM_FORMAT_HANGUL, "^1.", ["가.", "나.", "다."]),
        (12, "(^1)", ["(1)", "(2)", "(3)"]),  # 모르는 번호 모양 → 숫자
    ],
)
def test_number_formats(fmt: int, template: str, expected: list[str]) -> None:
    items = [SynthListPara(t, "number", template=template) for t in ("x", "y", "z")]
    labels = [i.label for i in _infos(_read(items, [fmt])) if i is not None]
    assert labels == expected


def test_number_without_numbering_definition_falls_back_to_digit() -> None:
    items = [SynthListPara("a", "number"), SynthListPara("b", "number")]
    info = parse_docinfo(build_docinfo(lists=items))
    bare = type(info)(para_shapes=info.para_shapes)  # NUMBERING 레코드 없음
    blocks = parse_blocks(iter_records(build_section0(items)), bare, None, ReadContext())  # type: ignore[arg-type]
    assert [i.label for i in _infos(blocks) if i is not None] == ["1.", "2."]


def test_heading_paragraphs_unchanged() -> None:
    info = parse_docinfo(build_docinfo(outline=True, lists=[SynthListPara("a", "bullet")]))
    assert info.heading_level(1) == 1
    assert info.heading_level(8) == 0  # 목록 문단 모양은 제목이 아니다
