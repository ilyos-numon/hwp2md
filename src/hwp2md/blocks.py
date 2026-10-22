"""Document block model: paragraphs and tables."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Paragraph:
    text: str


@dataclass(frozen=True)
class Table:
    rows: list[list[str]]

    @property
    def row_count(self) -> int:
        return len(self.rows)

    @property
    def col_count(self) -> int:
        return len(self.rows[0]) if self.rows else 0


Block = Paragraph | Table
