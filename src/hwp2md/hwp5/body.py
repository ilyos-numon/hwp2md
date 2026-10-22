"""BodyText record sequence -> blocks (paragraphs and tables)."""

from __future__ import annotations

import struct
from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from ..blocks import Block, Paragraph, Table
from ..errors import Hwp2mdError
from .docinfo import EMPTY_DOCINFO, DocInfo
from .records import (
    CTRL_ID_TABLE,
    HWPTAG_CTRL_HEADER,
    HWPTAG_LIST_HEADER,
    HWPTAG_PARA_HEADER,
    HWPTAG_PARA_TEXT,
    HWPTAG_TABLE,
    Record,
    decode_para_text,
)


@dataclass(frozen=True)
class TableHeader:
    row_count: int
    col_count: int


@dataclass(frozen=True)
class CellHeader:
    col: int
    row: int
    col_span: int
    row_span: int


def parse_table_header(payload: bytes) -> TableHeader:
    """len(payload) < 8 → Hwp2mdError("truncated TABLE record")."""
    if len(payload) < 8:
        raise Hwp2mdError("truncated TABLE record")
    row_count, col_count = struct.unpack_from("<HH", payload, 4)
    return TableHeader(row_count=row_count, col_count=col_count)


def parse_cell_header(payload: bytes) -> CellHeader:
    """len(payload) < 16 → Hwp2mdError("truncated LIST_HEADER record")."""
    if len(payload) < 16:
        raise Hwp2mdError("truncated LIST_HEADER record")
    col, row, col_span, row_span = struct.unpack_from("<HHHH", payload, 8)
    return CellHeader(col=col, row=row, col_span=col_span, row_span=row_span)


def parse_blocks(records: Iterable[Record], docinfo: DocInfo = EMPTY_DOCINFO) -> list[Block]:
    """§4.3 알고리즘. 섹션 하나의 레코드 시퀀스 → 블록 목록."""
    recs = list(records)
    blocks: list[Block] = []
    i = 0
    while i < len(recs):
        r = recs[i]
        if r.tag_id == HWPTAG_PARA_HEADER and r.level == 0:
            text, heading, trailing, i = _parse_paragraph(recs, i, 0, docinfo)
            if text:
                blocks.append(Paragraph(text, heading))
            blocks.extend(trailing)
        else:
            i += 1
    return blocks


def _heading_level(para_header_payload: bytes, docinfo: DocInfo) -> int:
    """len(payload) < 10 → 0. para_shape_id = UINT16 @8."""
    if len(para_header_payload) < 10:
        return 0
    (para_shape_id,) = struct.unpack_from("<H", para_header_payload, 8)
    return docinfo.heading_level(para_shape_id)


def _parse_paragraph(
    recs: Sequence[Record], i: int, level: int, docinfo: DocInfo
) -> tuple[str, int, list[Block], int]:
    heading = _heading_level(recs[i].payload, docinfo)
    i += 1
    text = ""
    trailing: list[Block] = []
    while i < len(recs) and recs[i].level > level:
        r = recs[i]
        if r.tag_id == HWPTAG_PARA_TEXT and r.level == level + 1:
            text = decode_para_text(r.payload)
            i += 1
        elif (
            r.tag_id == HWPTAG_CTRL_HEADER
            and r.level == level + 1
            and r.payload[:4] == CTRL_ID_TABLE
        ):
            table, i = _parse_table(recs, i, level + 1, docinfo)
            if table is not None:
                trailing.append(table)
        elif r.tag_id == HWPTAG_CTRL_HEADER and r.level == level + 1:
            # 표가 아닌 컨트롤: 안쪽 단락을 그대로 흘려보낸다
            ctrl_level = r.level
            i += 1
            while i < len(recs) and recs[i].level > ctrl_level:
                if recs[i].tag_id == HWPTAG_PARA_HEADER and recs[i].level == ctrl_level + 1:
                    t2, h2, tr2, i = _parse_paragraph(recs, i, ctrl_level + 1, docinfo)
                    if t2:
                        trailing.append(Paragraph(t2, h2))
                    trailing.extend(tr2)
                else:
                    i += 1
        else:
            i += 1
    return text, heading, trailing, i


def _parse_table(
    recs: Sequence[Record], i: int, ctrl_level: int, docinfo: DocInfo
) -> tuple[Table | None, int]:
    i += 1
    header: TableHeader | None = None
    cells: list[tuple[CellHeader, list[str]]] = []
    current: tuple[CellHeader, list[str]] | None = None
    while i < len(recs) and recs[i].level > ctrl_level:
        r = recs[i]
        if r.tag_id == HWPTAG_TABLE and r.level == ctrl_level + 1:
            header = parse_table_header(r.payload)
            i += 1
        elif r.tag_id == HWPTAG_LIST_HEADER and r.level == ctrl_level + 1:
            current = (parse_cell_header(r.payload), [])
            cells.append(current)
            i += 1
        elif r.tag_id == HWPTAG_PARA_HEADER and r.level == ctrl_level + 1 and current is not None:
            # 셀 단락은 텍스트만 쓴다 (수준은 버린다)
            text, _, trailing, i = _parse_paragraph(recs, i, ctrl_level + 1, docinfo)
            if text:
                current[1].append(text)
            for b in trailing:
                # 셀 안의 중첩 표·컨트롤 단락 → 부모 셀 텍스트로 평탄화
                if isinstance(b, Paragraph):
                    current[1].append(b.text)
                else:
                    flat = " ".join(c for row in b.rows for c in row if c)
                    if flat:
                        current[1].append(flat)
        else:
            i += 1
    if header is None or header.row_count == 0 or header.col_count == 0:
        return None, i
    return Table(rows=_place_cells(header, cells)), i


def _place_cells(
    header: TableHeader, cells: Sequence[tuple[CellHeader, list[str]]]
) -> list[list[str]]:
    rows, cols = header.row_count, header.col_count
    grid: list[list[str | None]] = [[None] * cols for _ in range(rows)]
    for cell, paras in cells:
        text = "\n".join(paras)
        r, c = cell.row, cell.col
        if not (0 <= r < len(grid) and 0 <= c < cols) or grid[r][c] is not None:
            # 좌표가 범위 밖이거나 이미 찬 자리 → 읽기 순서로 첫 빈 칸
            slot = next(
                ((rr, cc) for rr in range(len(grid)) for cc in range(cols) if grid[rr][cc] is None),
                None,
            )
            if slot is None:
                grid.append([None] * cols)
                slot = (len(grid) - 1, 0)
            r, c = slot
        grid[r][c] = text
        for rr in range(r, min(r + max(cell.row_span, 1), len(grid))):
            for cc in range(c, min(c + max(cell.col_span, 1), cols)):
                if (rr, cc) != (r, c) and grid[rr][cc] is None:
                    grid[rr][cc] = ""  # 병합으로 덮인 칸
    return [[x if x is not None else "" for x in row] for row in grid]
