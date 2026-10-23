"""Block model, render rules, skips and numbering for extracted elements (PLAN §4-A~D)."""

from __future__ import annotations

import pytest

from hwp2md.blocks import (
    Block,
    Image,
    Link,
    ListInfo,
    Math,
    Note,
    NoteRef,
    Paragraph,
    Table,
    iter_images,
    make_paragraph,
    make_table,
    plain_text,
)
from hwp2md.numbering import NumberingCounter, apply_template, format_number
from hwp2md.render import render_blocks, safe_link_url
from hwp2md.skips import SKIP_LABELS, SkipCounter
from synth_items import EXT_FIXTURES, EXT_IDS_BY_STAGE

PNG = b"\x89PNG\r\n\x1a\nfake"
FRAC = "\\frac{a}{b}"


def _p(*inlines: object, level: int = 0, list_info: ListInfo | None = None) -> Paragraph:
    p = make_paragraph(list(inlines), level, list_info)  # type: ignore[arg-type]
    assert p is not None
    return p


def _bullet(text: str, depth: int = 0) -> Paragraph:
    return _p(text, list_info=ListInfo("bullet", depth, ""))


def _number(text: str, label: str, depth: int = 0) -> Paragraph:
    return _p(text, list_info=ListInfo("number", depth, label))


EXPECTED_EXT_BLOCKS: dict[str, list[Block]] = {
    "link": [_p("앞 ", Link("누리집", "https://example.org/a b"), " 뒤")],
    "link_unsafe": [_p(Link("클릭", "javascript:alert(1)"))],
    "footnote": [
        _p("가", NoteRef("footnote", 1), "나"),
        Note("footnote", 1, (Paragraph("주석"),)),
    ],
    "note_mixed": [
        _p("하나", NoteRef("footnote", 1)),
        _p("둘", NoteRef("footnote", 2), " 셋", NoteRef("endnote", 1)),
        Note("footnote", 1, (Paragraph("첫 각주"),)),
        Note("footnote", 2, (Paragraph("둘째 각주"), Paragraph("둘째 단락"))),
        Note("endnote", 1, (Paragraph("미주 내용"),)),
    ],
    "equation_display": [_p(Math("a over b", FRAC))],
    "equation_inline": [_p("식 ", Math("a over b", FRAC), " 끝")],
    "field": [_p("이름: 홍길동")],
    "header": [Paragraph("본문")],
    "header_image": [Paragraph("본문")],
    "hidden_comment": [Paragraph("본문")],
    "textbox": [
        Paragraph("앞"),
        Paragraph("상자1"),
        Paragraph("상자2"),
        Image("img_001.png", PNG),
    ],
    "caption": [make_table([[["값"]]]), Paragraph("표 1 현황")],
    "bullets": [_bullet("하나"), _bullet("둘"), Paragraph("끝")],
    "numbers": [_number("가", "1."), _number("나", "2.")],
    "chart": [
        Paragraph("차트: 실적"),
        make_table([[["항목"], ["매출"]], [["1월"], ["10"]], [["2월"], ["20"]]]),
    ],
    "chart_legacy": [Paragraph("앞")],
}


def test_ext_fixture_ids() -> None:
    assert len(EXT_FIXTURES) == 16
    assert set(EXPECTED_EXT_BLOCKS) == set(EXT_FIXTURES)
    staged = [i for ids in EXT_IDS_BY_STAGE.values() for i in ids]
    assert sorted(staged) == sorted(EXT_FIXTURES)
    assert len(EXT_IDS_BY_STAGE["inline"]) == 10
    assert len(EXT_IDS_BY_STAGE["objects"]) == 4
    assert EXT_IDS_BY_STAGE["lists"] == ["bullets", "numbers"]
    for _items, _md, skipped in EXT_FIXTURES.values():
        assert all(kind in SKIP_LABELS and n > 0 for kind, n in skipped)


@pytest.mark.parametrize("fixture_id", sorted(EXT_FIXTURES))
def test_ext_fixture_markdown(fixture_id: str) -> None:
    _items, expected, _skipped = EXT_FIXTURES[fixture_id]
    blocks = EXPECTED_EXT_BLOCKS[fixture_id]
    assert render_blocks(blocks, image_dir="doc_images") == expected


# --- 블록 모델 ---------------------------------------------------------------


def test_existing_constructors_unchanged() -> None:
    assert Paragraph("x") == Paragraph("x", 0)
    assert Paragraph("x", 2).inlines == ()
    assert Paragraph("x").list_info is None
    assert Table([["a"]]).cells == ()
    assert Table([["a", "b"]]).col_count == 2


def test_plain_text() -> None:
    inlines = ["가", Link("링크", "https://x"), NoteRef("footnote", 1), Math("a", None)]
    assert plain_text([*inlines, Image("i.png", PNG)]) == "가링크a"


def test_make_paragraph_str_only_equals_constructor() -> None:
    assert make_paragraph(["  가", "나 "]) == Paragraph("가나")
    assert make_paragraph(["제목"], 2) == Paragraph("제목", 2)
    assert make_paragraph(["a\nb"]) == Paragraph("a\nb")
    assert make_paragraph(["   ", ""]) is None
    assert make_paragraph([]) is None


def test_make_paragraph_merges_and_strips() -> None:
    link = Link("링크", "https://x")
    p = make_paragraph([" 앞", " ", link, "뒤", " 끝 "])
    assert p == Paragraph("앞 링크뒤 끝", 0, ("앞 ", link, "뒤 끝"))


def test_make_paragraph_non_str_only() -> None:
    ref = NoteRef("footnote", 1)
    assert make_paragraph(["  ", ref, " "]) == Paragraph("", 0, (ref,))
    img = Image("i.png", PNG)
    assert make_paragraph([img]) == Paragraph("", 0, (img,))


def test_make_paragraph_list_info() -> None:
    info = ListInfo("bullet", 0, "")
    assert make_paragraph(["항목"], list_info=info) == Paragraph("항목", 0, (), info)


def test_make_table_str_only_equals_constructor() -> None:
    t = make_table([[["가"], [" 나", "\n", "다 "]], [[], ["라"]]])
    assert t == Table([["가", "나\n다"], ["", "라"]])
    assert t.cells == ()


def test_make_table_with_inlines() -> None:
    img = Image("i.png", PNG)
    t = make_table([[[img, "\n", "값"], ["나"]]])
    assert t.rows == [["값", "나"]]
    assert t.cells == (((img, "\n값"), ("나",)),)


def test_iter_images_order() -> None:
    imgs = [Image(f"img_{i}.png", PNG) for i in range(1, 7)]
    blocks: list[Block] = [
        Paragraph("앞"),
        imgs[0],
        _p("x", imgs[1]),
        make_table([[[imgs[2]], ["a", imgs[3]]], [[imgs[4]], ["b"]]]),
        Note("footnote", 1, (_p("주", imgs[5]),)),
    ]
    assert list(iter_images(blocks)) == imgs
    md = render_blocks(blocks, image_dir="d")
    for n, img in enumerate(imgs, start=1):
        assert f"![그림 {n}](d/{img.file_name})" in md


# --- 링크 -------------------------------------------------------------------


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("https://example.org/a b", "https://example.org/a%20b"),
        ("  http://x/(a)<b>  ", "http://x/%28a%29%3Cb%3E"),
        ("HTTPS://X", "HTTPS://X"),
        ("mailto:a@b.c", "mailto:a@b.c"),
        ("javascript:alert(1)", None),
        ("ftp://x", None),
        ("file:///c:/x", None),
        ("?책갈피", None),
        ("example.org", None),
        ("", None),
        ("   ", None),
    ],
)
def test_safe_link_url(url: str, expected: str | None) -> None:
    assert safe_link_url(url) == expected


def test_link_text_brackets_escaped() -> None:
    md = render_blocks([_p(Link("[참고]", "https://x"))])
    assert md == "[\\[참고\\]](https://x)\n"


def test_unsafe_link_text_only() -> None:
    md = render_blocks([_p("가 ", Link("[a]", "javascript:x"))])
    assert md == "가 [a]\n"
    assert "](" not in md


# --- 수식 -------------------------------------------------------------------


@pytest.mark.parametrize(
    ("script", "span"),
    [
        ("a over b", "`a over b`"),
        ("a`b", "``a`b``"),
        ("a``b`c", "```a``b`c```"),
        ("`a", "`` `a ``"),
        ("a`", "`` a` ``"),
    ],
)
def test_math_code_span(script: str, span: str) -> None:
    assert render_blocks([_p("식 ", Math(script, None))]) == f"식 {span}\n"


def test_math_display_only_when_single() -> None:
    m = Math("a over b", FRAC)
    assert render_blocks([Paragraph("", 0, ("  ", m, " "))]) == f"$${FRAC}$$\n"
    assert render_blocks([_p(m, m)]) == f"${FRAC}$${FRAC}$\n"
    assert render_blocks([_p(m, NoteRef("footnote", 1))]) == f"${FRAC}$[^1]\n"
    assert render_blocks([_p(Math("a over b", None))]) == "`a over b`\n"


def test_math_heading() -> None:
    assert render_blocks([_p("식 ", Math("x", "x"), level=2)]) == "## 식 $x$\n"


# --- 목록 -------------------------------------------------------------------


def test_list_indent_and_join() -> None:
    blocks: list[Block] = [
        _bullet("a", 0),
        _bullet("b", 1),
        _bullet("c", 3),
        _bullet("d", 0),
        Paragraph("끝"),
        _bullet("e", 2),
    ]
    assert render_blocks(blocks) == "- a\n    - b\n        - c\n- d\n\n끝\n\n- e\n"


def test_list_numeric_and_other_labels() -> None:
    blocks: list[Block] = [
        _number("가", "1."),
        _number("나", "2)", 1),
        _number("다", "가."),
        _number("라", "(1)", 1),
        _number("마", "1."),
    ]
    assert render_blocks(blocks) == "1. 가\n    2) 나\n\n가. 다\n\n(1) 라\n\n1. 마\n"


def test_list_after_heading_and_table() -> None:
    blocks: list[Block] = [Paragraph("제목", 1), _bullet("a", 1), Table([["x"]]), _bullet("b", 2)]
    assert render_blocks(blocks) == "# 제목\n\n- a\n\n| x |\n|---|\n\n- b\n"


def test_list_with_inlines_and_empty_label() -> None:
    p = _p("보기 ", Link("링크", "https://x"), list_info=ListInfo("bullet", 0, ""))
    q = _p("빈 머리", list_info=ListInfo("number", 0, ""))
    assert render_blocks([p, q]) == "- 보기 [링크](https://x)\n\n빈 머리\n"


# --- 표 칸 인라인 ------------------------------------------------------------


def test_cell_inlines() -> None:
    img = Image("img_001.jpg", PNG)
    t = make_table(
        [
            [[img, "\n", "값"], ["나|다"]],
            [[Link("a|b", "https://x/y z")], ["줄1", "\n", "줄2", NoteRef("footnote", 1)]],
        ]
    )
    md = render_blocks([t, Image("img_002.png", PNG)], image_dir="doc_images")
    assert md == (
        "| ![그림 1](doc_images/img_001.jpg)<br>값 | 나\\|다 |\n|---|---|\n"
        "| [a\\|b](https://x/y%20z) | 줄1<br>줄2[^1] |\n\n![그림 2](doc_images/img_002.png)\n"
    )


def test_cell_math_inline_not_display() -> None:
    t = make_table([[[Math("a over b", FRAC)]]])
    assert render_blocks([t]) == f"| ${FRAC}$ |\n|---|\n"


# --- 각주 -------------------------------------------------------------------


def test_note_multi_paragraph() -> None:
    note = Note("endnote", 3, (Paragraph("첫"), Paragraph("둘\n줄"), Paragraph("셋")))
    assert render_blocks([note]) == "[^e3]: 첫\n\n    둘\n    줄\n\n    셋\n"


def test_note_inlines() -> None:
    note = Note("footnote", 1, (_p("참고 ", Link("누리집", "https://x")),))
    assert render_blocks([Paragraph("본문"), note]) == "본문\n\n[^1]: 참고 [누리집](https://x)\n"


# --- 기존 출력 유지 -----------------------------------------------------------


def test_legacy_blocks_unchanged() -> None:
    blocks: list[Block] = [
        Paragraph(" 앞 공백\n줄 "),
        Paragraph("제목\n둘", 7),
        Paragraph("  ", 1),
        Table([["a|b", "c\nd"], [" e ", ""]]),
        Image("x y.png", PNG),
        Paragraph(""),
    ]
    assert render_blocks(blocks, image_dir="d") == (
        " 앞 공백\n줄 \n\n###### 제목 둘\n\n| a\\|b | c<br>d |\n|---|---|\n| e |  |\n\n"
        "![그림 1](d/x%20y.png)\n"
    )
    assert render_blocks([]) == ""


# --- 건너뜀 -----------------------------------------------------------------


def test_skip_labels_order() -> None:
    assert list(SKIP_LABELS) == [
        "header_footer",
        "memo",
        "hidden_comment",
        "chart_legacy",
        "ole",
        "textart",
        "form_control",
        "image_link",
        "image_missing",
    ]
    assert SKIP_LABELS["header_footer"] == "머리말·꼬리말"
    assert SKIP_LABELS["image_missing"] == "본체 없는 그림"


def test_skip_counter() -> None:
    c = SkipCounter()
    assert c.items() == ()
    c.add("image_missing")
    c.add("header_footer", 2)
    c.add("ole", 0)
    c.add("image_missing")
    assert c.items() == (("header_footer", 2), ("image_missing", 2))


# --- 번호 -------------------------------------------------------------------


@pytest.mark.parametrize(
    ("fmt", "one", "three"),
    [
        ("DIGIT", "1", "3"),
        ("CIRCLED_DIGIT", "①", "③"),
        ("ROMAN_CAPITAL", "I", "III"),
        ("ROMAN_SMALL", "i", "iii"),
        ("LATIN_CAPITAL", "A", "C"),
        ("LATIN_SMALL", "a", "c"),
        ("HANGUL_SYLLABLE", "가", "다"),
        ("CIRCLED_HANGUL_SYLLABLE", "㉮", "㉰"),
        ("HANGUL_JAMO", "ㄱ", "ㄷ"),
        ("HANJA_DIGIT", "一", "三"),
    ],
)
def test_format_number(fmt: str, one: str, three: str) -> None:
    assert format_number(1, fmt) == one  # type: ignore[arg-type]
    assert format_number(3, fmt) == three  # type: ignore[arg-type]


def test_format_number_out_of_range() -> None:
    assert format_number(15, "HANGUL_SYLLABLE") == "15"
    assert format_number(27, "LATIN_SMALL") == "27"
    assert format_number(0, "ROMAN_CAPITAL") == "0"
    assert format_number(14, "ROMAN_CAPITAL") == "XIV"
    assert format_number(12, "HANJA_DIGIT") == "十二"


def test_apply_template() -> None:
    assert apply_template("^1.", [3], ["DIGIT"]) == "3."
    assert apply_template("^2)", [1, 2], ["DIGIT", "HANGUL_SYLLABLE"]) == "나)"
    assert apply_template("(^n)", [1, 4], ["DIGIT", "DIGIT"]) == "(4)"
    assert apply_template("^N.", [2], ["ROMAN_CAPITAL"]) == "II."
    assert apply_template("^1.^2.", [2, 5], ["DIGIT", "DIGIT"]) == "2.5."
    assert apply_template("•", [1], ["DIGIT"]) == "•"


def test_numbering_counter() -> None:
    c = NumberingCounter()
    assert c.next(1, 0) == [1]
    assert c.next(1, 0) == [2]
    assert c.next(1, 1) == [2, 1]
    assert c.next(1, 1) == [2, 2]
    assert c.next(1, 0) == [3]
    assert c.next(1, 1) == [3, 1]  # 상위 수준이 나오면 하위는 처음으로
    assert c.next(2, 0, start=5) == [5]  # id 별로 따로
    assert c.next(2, 0, start=5) == [6]
    assert c.next(3, 2) == [1, 1, 1]
    assert c.next(3, 0) == [1]  # 처음 나온 수준은 start
