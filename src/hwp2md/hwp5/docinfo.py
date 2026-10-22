"""DocInfo stream: paragraph shapes (outline level) and binary data entries."""

from __future__ import annotations

import struct
from dataclasses import dataclass

from ..errors import Hwp2mdError
from .records import HWPTAG_BIN_DATA, HWPTAG_PARA_SHAPE, iter_records

HEADING_OUTLINE = 1  # 속성1 비트 23~24 값
MAX_HEADING_LEVEL = 6  # Markdown 상한
BIN_DATA_LINK, BIN_DATA_EMBEDDING, BIN_DATA_STORAGE = 0, 1, 2


@dataclass(frozen=True)
class ParaShape:
    heading_type: int  # 0~3
    heading_level: int  # 0~7 (비트 값 그대로)


@dataclass(frozen=True)
class BinDataEntry:
    storage_type: int  # attr & 0xF
    compression: int  # (attr >> 4) & 0x3
    storage_id: int  # EMBEDDING/STORAGE: UINT16 @2 ; LINK: 0
    ext: str  # EMBEDDING: BSTR @4 를 strip·소문자·앞 '.' 제거 ; 그 외 ""


@dataclass(frozen=True)
class DocInfo:
    para_shapes: tuple[ParaShape, ...]
    bin_data: tuple[BinDataEntry, ...] = ()  # 등장 순서. bindata_id = index + 1

    def heading_level(self, para_shape_id: int) -> int:
        """개요 문단 모양이면 min(heading_level + 1, MAX_HEADING_LEVEL), 아니면 0."""
        if not 0 <= para_shape_id < len(self.para_shapes):
            return 0
        shape = self.para_shapes[para_shape_id]
        if shape.heading_type != HEADING_OUTLINE:
            return 0
        return min(shape.heading_level + 1, MAX_HEADING_LEVEL)

    def bin_data_entry(self, bindata_id: int) -> BinDataEntry | None:
        """1 <= bindata_id <= len(bin_data) 면 bin_data[bindata_id - 1], 아니면 None."""
        if not 1 <= bindata_id <= len(self.bin_data):
            return None
        return self.bin_data[bindata_id - 1]


EMPTY_DOCINFO = DocInfo(para_shapes=())


def parse_para_shape(payload: bytes) -> ParaShape:
    """len < 4 → Hwp2mdError("truncated PARA_SHAPE record")."""
    if len(payload) < 4:
        raise Hwp2mdError("truncated PARA_SHAPE record")
    (attr1,) = struct.unpack_from("<I", payload, 0)
    return ParaShape(heading_type=(attr1 >> 23) & 0x3, heading_level=(attr1 >> 25) & 0x7)


def parse_bin_data(payload: bytes) -> BinDataEntry:
    """len < 2 → Hwp2mdError("truncated BIN_DATA record"). EMBEDDING/STORAGE 인데 len < 4,
    EMBEDDING 인데 len < 6 또는 6 + 2n → 같은 메시지."""
    if len(payload) < 2:
        raise Hwp2mdError("truncated BIN_DATA record")
    (attr,) = struct.unpack_from("<H", payload, 0)
    storage_type = attr & 0xF
    compression = (attr >> 4) & 0x3
    storage_id = 0
    ext = ""
    if storage_type in (BIN_DATA_EMBEDDING, BIN_DATA_STORAGE):
        if len(payload) < 4:
            raise Hwp2mdError("truncated BIN_DATA record")
        (storage_id,) = struct.unpack_from("<H", payload, 2)
    if storage_type == BIN_DATA_EMBEDDING:
        if len(payload) < 6:
            raise Hwp2mdError("truncated BIN_DATA record")
        (n,) = struct.unpack_from("<H", payload, 4)
        if len(payload) < 6 + 2 * n:
            raise Hwp2mdError("truncated BIN_DATA record")
        raw = payload[6 : 6 + 2 * n].decode("utf-16-le", errors="replace")
        ext = raw.strip().lower().lstrip(".")
    return BinDataEntry(storage_type, compression, storage_id, ext)


def parse_docinfo(data: bytes) -> DocInfo:
    """PARA_SHAPE 와 BIN_DATA 를 각각 등장 순서대로 수집. data == b"" → EMPTY_DOCINFO."""
    if not data:
        return EMPTY_DOCINFO
    shapes: list[ParaShape] = []
    bins: list[BinDataEntry] = []
    for r in iter_records(data):
        if r.tag_id == HWPTAG_PARA_SHAPE:
            shapes.append(parse_para_shape(r.payload))
        elif r.tag_id == HWPTAG_BIN_DATA:
            bins.append(parse_bin_data(r.payload))
    return DocInfo(para_shapes=tuple(shapes), bin_data=tuple(bins))
