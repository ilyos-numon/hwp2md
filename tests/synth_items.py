"""Synthetic element items shared by the HWP 5.0 / HWPX / HWPML generators.

Test-only. Layout follows PLAN §4-M. Does not import synth_hwp5 (generators use
synth_hwp5.PNG_1X1 when an item needs a picture).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class SynthLink:
    text: str
    url: str


@dataclass(frozen=True)
class SynthNote:
    paragraphs: tuple[str, ...]
    kind: Literal["footnote", "endnote"] = "footnote"


@dataclass(frozen=True)
class SynthEquation:
    script: str


@dataclass(frozen=True)
class SynthField:
    text: str  # 누름틀 표시 글자


Run = str | SynthLink | SynthNote | SynthEquation | SynthField


@dataclass(frozen=True)
class SynthRich:
    runs: tuple[Run, ...]  # 단락 하나


@dataclass(frozen=True)
class SynthHeaderFooter:
    paragraphs: tuple[str, ...]
    kind: Literal["header", "footer"] = "header"
    with_image: bool = False


@dataclass(frozen=True)
class SynthHidden:
    paragraphs: tuple[str, ...]  # 숨은 설명


@dataclass(frozen=True)
class SynthTextBox:
    anchor_text: str
    paragraphs: tuple[str, ...]
    with_image: bool = False


@dataclass(frozen=True)
class SynthCaptionedTable:
    cells: tuple[tuple[str, ...], ...]
    caption: str


@dataclass(frozen=True)
class SynthListPara:
    text: str
    kind: Literal["bullet", "number"]
    depth: int = 0
    template: str = "^1."


@dataclass(frozen=True)
class SynthChart:
    title: str
    categories: tuple[str, ...]
    series: tuple[tuple[str, tuple[str, ...]], ...]
    legacy: bool = False


ExtItem = (
    SynthRich
    | SynthHeaderFooter
    | SynthHidden
    | SynthTextBox
    | SynthCaptionedTable
    | SynthListPara
    | SynthChart
)

# id → (items, 기대 Markdown(입력 stem "doc"), 기대 skipped). items 안 str 은 일반 단락.
# 수식 기대값은 equation.to_latex("a over b") == "\\frac{a}{b}" 를 전제로 한다.
EXT_FIXTURES: dict[str, tuple[list[object], str, tuple[tuple[str, int], ...]]] = {
    "link": (
        [SynthRich(("앞 ", SynthLink("누리집", "https://example.org/a b"), " 뒤"))],
        "앞 [누리집](https://example.org/a%20b) 뒤\n",
        (),
    ),
    "link_unsafe": (
        [SynthRich((SynthLink("클릭", "javascript:alert(1)"),))],
        "클릭\n",
        (),
    ),
    "footnote": (
        [SynthRich(("가", SynthNote(("주석",)), "나"))],
        "가[^1]나\n\n[^1]: 주석\n",
        (),
    ),
    "note_mixed": (
        [
            SynthRich(("하나", SynthNote(("첫 각주",)))),
            SynthRich(
                (
                    "둘",
                    SynthNote(("둘째 각주", "둘째 단락")),
                    " 셋",
                    SynthNote(("미주 내용",), kind="endnote"),
                )
            ),
        ],
        "하나[^1]\n\n둘[^2] 셋[^e1]\n\n[^1]: 첫 각주\n\n[^2]: 둘째 각주\n\n    둘째 단락\n\n"
        "[^e1]: 미주 내용\n",
        (),
    ),
    "equation_display": (
        [SynthRich((SynthEquation("a over b"),))],
        "$$\\frac{a}{b}$$\n",
        (),
    ),
    "equation_inline": (
        [SynthRich(("식 ", SynthEquation("a over b"), " 끝"))],
        "식 $\\frac{a}{b}$ 끝\n",
        (),
    ),
    "field": (
        [SynthRich(("이름: ", SynthField("홍길동")))],
        "이름: 홍길동\n",
        (),
    ),
    "header": (
        [
            SynthHeaderFooter(("머리말",)),
            SynthHeaderFooter(("꼬리말",), kind="footer"),
            "본문",
        ],
        "본문\n",
        (("header_footer", 2),),
    ),
    "header_image": (
        ["본문", SynthHeaderFooter(("머리말",), with_image=True)],
        "본문\n",
        (("header_footer", 1),),
    ),
    "hidden_comment": (
        ["본문", SynthHidden(("숨은 설명 글",))],
        "본문\n",
        (("hidden_comment", 1),),
    ),
    "textbox": (
        [SynthTextBox("앞", ("상자1", "상자2"), with_image=True)],
        "앞\n\n상자1\n\n상자2\n\n![그림 1](doc_images/img_001.png)\n",
        (),
    ),
    "caption": (
        [SynthCaptionedTable((("값",),), "표 1 현황")],
        "| 값 |\n|---|\n\n표 1 현황\n",
        (),
    ),
    "bullets": (
        [SynthListPara("하나", "bullet"), SynthListPara("둘", "bullet"), "끝"],
        "- 하나\n- 둘\n\n끝\n",
        (),
    ),
    "numbers": (
        [SynthListPara("가", "number"), SynthListPara("나", "number")],
        "1. 가\n2. 나\n",
        (),
    ),
    "chart": (
        [SynthChart("실적", ("1월", "2월"), (("매출", ("10", "20")),))],
        "차트: 실적\n\n| 항목 | 매출 |\n|---|---|\n| 1월 | 10 |\n| 2월 | 20 |\n",
        (),
    ),
    "chart_legacy": (
        ["앞", SynthChart("실적", ("1월",), (("매출", ("10",)),), legacy=True)],
        "앞\n",
        (("chart_legacy", 1),),
    ),
}

EXT_IDS_BY_STAGE: dict[str, list[str]] = {
    "inline": [
        "link",
        "link_unsafe",
        "footnote",
        "note_mixed",
        "equation_display",
        "equation_inline",
        "field",
        "header",
        "header_image",
        "hidden_comment",
    ],
    "objects": ["textbox", "caption", "chart", "chart_legacy"],
    "lists": ["bullets", "numbers"],
}
