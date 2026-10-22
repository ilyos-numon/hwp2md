"""DocInfo stream: paragraph shapes (outline level) only."""

from __future__ import annotations

import struct
from dataclasses import dataclass

from ..errors import Hwp2mdError
from .records import HWPTAG_PARA_SHAPE, iter_records

HEADING_OUTLINE = 1  # 속성1 비트 23~24 값
MAX_HEADING_LEVEL = 6  # Markdown 상한


@dataclass(frozen=True)
class ParaShape:
    heading_type: int  # 0~3
    heading_level: int  # 0~7 (비트 값 그대로)


@dataclass(frozen=True)
class DocInfo:
    para_shapes: tuple[ParaShape, ...]

    def heading_level(self, para_shape_id: int) -> int:
        """개요 문단 모양이면 min(heading_level + 1, MAX_HEADING_LEVEL), 아니면 0."""
        if not 0 <= para_shape_id < len(self.para_shapes):
            return 0
        shape = self.para_shapes[para_shape_id]
        if shape.heading_type != HEADING_OUTLINE:
            return 0
        return min(shape.heading_level + 1, MAX_HEADING_LEVEL)


EMPTY_DOCINFO = DocInfo(para_shapes=())


def parse_para_shape(payload: bytes) -> ParaShape:
    """len < 4 → Hwp2mdError("truncated PARA_SHAPE record")."""
    if len(payload) < 4:
        raise Hwp2mdError("truncated PARA_SHAPE record")
    (attr1,) = struct.unpack_from("<I", payload, 0)
    return ParaShape(heading_type=(attr1 >> 23) & 0x3, heading_level=(attr1 >> 25) & 0x7)


def parse_docinfo(data: bytes) -> DocInfo:
    """PARA_SHAPE 레코드만 등장 순서대로 읽는다. data == b"" → EMPTY_DOCINFO."""
    if not data:
        return EMPTY_DOCINFO
    shapes = tuple(
        parse_para_shape(r.payload) for r in iter_records(data) if r.tag_id == HWPTAG_PARA_SHAPE
    )
    return DocInfo(para_shapes=shapes)
