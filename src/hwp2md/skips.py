"""Elements the converter could not output, counted by kind."""

from __future__ import annotations

from typing import Literal

SkipKind = Literal[
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

SKIP_LABELS: dict[SkipKind, str] = {  # 이 순서가 보고 순서
    "header_footer": "머리말·꼬리말",
    "memo": "메모",
    "hidden_comment": "숨은 설명",
    "chart_legacy": "데이터를 꺼낼 수 없는 차트",
    "ole": "OLE 개체",
    "textart": "글맵시",
    "form_control": "양식 개체",
    "image_link": "외부 연결 그림",
    "image_missing": "본체 없는 그림",
}


class SkipCounter:
    """종류별 건너뜀 개수. 문서 하나 단위로 리더가 쓴다."""

    def __init__(self) -> None:
        self._counts: dict[SkipKind, int] = {}

    def add(self, kind: SkipKind, n: int = 1) -> None:
        self._counts[kind] = self._counts.get(kind, 0) + n

    def items(self) -> tuple[tuple[SkipKind, int], ...]:
        """count > 0 만, SKIP_LABELS 순서."""
        return tuple(
            (kind, self._counts[kind]) for kind in SKIP_LABELS if self._counts.get(kind, 0) > 0
        )
