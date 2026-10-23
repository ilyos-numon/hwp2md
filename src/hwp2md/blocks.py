"""Document block model: paragraphs and tables."""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from typing import Literal

NoteKind = Literal["footnote", "endnote"]


@dataclass(frozen=True)
class Image:
    file_name: str  # "img_001.png" — 리더가 부여. 같은 원본(바이너리 항목)은 같은 file_name
    data: bytes  # 원본 바이트 (변환 없음)


@dataclass(frozen=True)
class Link:
    text: str
    url: str  # 원문 주소 그대로(언이스케이프만 리더가 함). 허용 판정은 render.safe_link_url


@dataclass(frozen=True)
class NoteRef:
    kind: NoteKind
    number: int  # 종류별 문서 읽기 순서 1부터 (섹션을 넘어 이어짐)


@dataclass(frozen=True)
class Math:
    script: str  # 한글 수식 스크립트 원문 (strip)
    latex: str | None  # equation.to_latex(script) 결과


Inline = str | Link | NoteRef | Math | Image


@dataclass(frozen=True)
class ListInfo:
    kind: Literal["bullet", "number"]
    depth: int  # 0부터 (원문 수준 1 → 0), 0~6
    label: str  # number: numbering.apply_template 결과("1.", "가.", "(1)"), bullet: ""


@dataclass(frozen=True)
class Paragraph:
    text: str
    level: int = 0  # 0 = 본문, 1~6 = Markdown 제목 수준 (리더가 clamp 해서 넣는다)
    inlines: tuple[Inline, ...] = ()  # () 면 text 로 렌더 (기존 동작)
    list_info: ListInfo | None = None


@dataclass(frozen=True)
class Table:
    rows: list[list[str]]  # 칸의 plain_text, 칸 안 단락은 "\n"
    cells: tuple[tuple[tuple[Inline, ...], ...], ...] = ()  # rows 와 같은 모양. () 면 rows 로 렌더

    @property
    def row_count(self) -> int:
        return len(self.rows)

    @property
    def col_count(self) -> int:
        return len(self.rows[0]) if self.rows else 0


@dataclass(frozen=True)
class Note:
    kind: NoteKind
    number: int
    paragraphs: tuple[Paragraph, ...]


Block = Paragraph | Table | Image | Note


def plain_text(inlines: Sequence[Inline]) -> str:
    """str 그대로 + Link.text + Math.script. NoteRef·Image 는 ""."""
    parts: list[str] = []
    for item in inlines:
        if isinstance(item, str):
            parts.append(item)
        elif isinstance(item, Link):
            parts.append(item.text)
        elif isinstance(item, Math):
            parts.append(item.script)
    return "".join(parts)


def _normalize_inlines(inlines: Sequence[Inline]) -> tuple[Inline, ...]:
    """인접 str 병합, 빈 str 제거."""
    out: list[Inline] = []
    for item in inlines:
        if isinstance(item, str):
            if not item:
                continue
            if out and isinstance(out[-1], str):
                out[-1] = out[-1] + item
                continue
        out.append(item)
    return tuple(out)


def _has_non_str(inlines: Sequence[Inline]) -> bool:
    return any(not isinstance(item, str) for item in inlines)


def make_paragraph(
    inlines: Sequence[Inline], level: int = 0, list_info: ListInfo | None = None
) -> Paragraph | None:
    """인접 str 병합, 맨 앞/뒤 str 의 공백 strip. str 이 아닌 인라인이 없으면 inlines=().
    text = plain_text(정규화 inlines).strip(). text=="" 이고 str 이 아닌 인라인도 없으면 None."""
    items = list(_normalize_inlines(inlines))
    if items and isinstance(items[0], str):
        items[0] = items[0].lstrip()
    if items and isinstance(items[-1], str):
        items[-1] = items[-1].rstrip()
    normalized = _normalize_inlines(items)
    text = plain_text(normalized).strip()
    has_non_str = _has_non_str(normalized)
    if not text and not has_non_str:
        return None
    return Paragraph(text, level, normalized if has_non_str else (), list_info)


def make_table(grid: Sequence[Sequence[Sequence[Inline]]]) -> Table:
    """각 칸: 인라인 사이 단락 경계는 "\\n" str 로 리더가 넣는다.
    rows[r][c] = plain_text(칸).strip().
    모든 칸이 str 만이면 cells=() — 기존 Table(rows) 와 같은 값."""
    cells = tuple(tuple(_normalize_inlines(cell) for cell in row) for row in grid)
    rows = [[plain_text(cell).strip() for cell in row] for row in cells]
    if any(_has_non_str(cell) for row in cells for cell in row):
        return Table(rows, cells)
    return Table(rows)


def _paragraph_images(p: Paragraph) -> Iterator[Image]:
    for item in p.inlines:
        if isinstance(item, Image):
            yield item


def iter_images(blocks: Sequence[Block]) -> Iterator[Image]:
    """렌더 순서와 같다: 블록 순서 → Paragraph.inlines 순서 → Table.cells 행 우선·칸 안 순서
    → Note.paragraphs 순서."""
    for block in blocks:
        if isinstance(block, Image):
            yield block
        elif isinstance(block, Paragraph):
            yield from _paragraph_images(block)
        elif isinstance(block, Table):
            for row in block.cells:
                for cell in row:
                    for item in cell:
                        if isinstance(item, Image):
                            yield item
        else:
            for p in block.paragraphs:
                yield from _paragraph_images(p)
