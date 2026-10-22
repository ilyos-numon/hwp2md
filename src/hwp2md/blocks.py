"""Document block model: paragraphs and tables."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Paragraph:
    text: str
    level: int = 0  # 0 = 본문, 1~6 = Markdown 제목 수준 (리더가 clamp 해서 넣는다)


@dataclass(frozen=True)
class Table:
    rows: list[list[str]]

    @property
    def row_count(self) -> int:
        return len(self.rows)

    @property
    def col_count(self) -> int:
        return len(self.rows[0]) if self.rows else 0


@dataclass(frozen=True)
class Image:
    file_name: str  # "img_001.png" — 리더가 부여. 같은 원본(바이너리 항목)은 같은 file_name
    data: bytes  # 원본 바이트 (변환 없음)


Block = Paragraph | Table | Image
