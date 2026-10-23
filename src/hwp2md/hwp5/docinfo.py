"""DocInfo stream: paragraph shapes (outline level, list head), numbering/bullet definitions
and binary data entries."""

from __future__ import annotations

import struct
from dataclasses import dataclass

from ..errors import Hwp2mdError
from ..numbering import NumFormat
from .records import (
    HWPTAG_BIN_DATA,
    HWPTAG_BULLET,
    HWPTAG_NUMBERING,
    HWPTAG_PARA_SHAPE,
    iter_records,
)

HEADING_OUTLINE, HEADING_NUMBER, HEADING_BULLET = 1, 2, 3  # 속성1 비트 23~24 값
PARA_HEAD_ID_OFFSET = 30  # PARA_SHAPE 의 번호/글머리표 ID (UINT16, 1부터. 0 = 없음)
NUMBERING_LEVELS = 7  # NUMBERING 레코드 앞부분의 수준 1~7
_PARA_HEAD_INFO_SIZE = 12  # 문단 머리 정보: UINT32 속성, HWPUNIT16 ×2, UINT32 글자 모양
# 문단 머리 정보 속성 비트 5~9 의 번호 모양 코드 → NumFormat. 그 밖의 코드는 DIGIT.
_NUM_FORMAT_CODES: dict[int, NumFormat] = {
    0: "DIGIT",
    1: "CIRCLED_DIGIT",
    2: "ROMAN_CAPITAL",
    3: "ROMAN_SMALL",
    4: "LATIN_CAPITAL",
    5: "LATIN_SMALL",
    8: "HANGUL_SYLLABLE",
    9: "CIRCLED_HANGUL_SYLLABLE",
    10: "HANGUL_JAMO",
    13: "HANJA_DIGIT",
}
MAX_HEADING_LEVEL = 6  # Markdown 상한
BIN_DATA_LINK, BIN_DATA_EMBEDDING, BIN_DATA_STORAGE = 0, 1, 2


@dataclass(frozen=True)
class ParaShape:
    heading_type: int  # 0~3
    heading_level: int  # 0~7 (비트 값 그대로)
    head_id: int = 0  # UINT16 @30: 번호(NUMBERING)·글머리표(BULLET) ID, 1부터. 잘렸으면 0


@dataclass(frozen=True)
class NumberingLevel:
    template: str  # 형식 문자열 ("^1.", "(^2)")
    num_format: NumFormat
    start: int | None = None  # 수준별 시작 번호 (없는 문서 버전이면 None)


@dataclass(frozen=True)
class NumberingDef:
    levels: tuple[NumberingLevel, ...]  # 수준 1~7 (잘렸으면 있는 만큼)
    start: int  # UINT16 시작 번호

    def level_start(self, depth: int) -> int:
        """수준별 시작 번호가 있으면 그 값, 없으면 문서 시작 번호(0 이하면 1)."""
        if 0 <= depth < len(self.levels):
            start = self.levels[depth].start
            if start is not None:
                return start
        return self.start if self.start > 0 else 1


@dataclass(frozen=True)
class BulletDef:
    char: str  # 글머리표 문자


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
    numberings: tuple[NumberingDef, ...] = ()  # 등장 순서. 번호 ID = index + 1
    bullets: tuple[BulletDef, ...] = ()  # 등장 순서. 글머리표 ID = index + 1

    def para_shape(self, para_shape_id: int) -> ParaShape | None:
        if not 0 <= para_shape_id < len(self.para_shapes):
            return None
        return self.para_shapes[para_shape_id]

    def numbering(self, head_id: int) -> NumberingDef | None:
        """1 <= head_id <= len(numberings) 면 numberings[head_id - 1], 아니면 None."""
        if not 1 <= head_id <= len(self.numberings):
            return None
        return self.numberings[head_id - 1]

    def bullet(self, head_id: int) -> BulletDef | None:
        """1 <= head_id <= len(bullets) 면 bullets[head_id - 1], 아니면 None."""
        if not 1 <= head_id <= len(self.bullets):
            return None
        return self.bullets[head_id - 1]

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
    head_id = 0
    if len(payload) >= PARA_HEAD_ID_OFFSET + 2:
        (head_id,) = struct.unpack_from("<H", payload, PARA_HEAD_ID_OFFSET)
    return ParaShape(
        heading_type=(attr1 >> 23) & 0x3, heading_level=(attr1 >> 25) & 0x7, head_id=head_id
    )


def num_format(code: int) -> NumFormat:
    """번호 모양 코드 → NumFormat. 모르는 값은 "DIGIT"."""
    return _NUM_FORMAT_CODES.get(code, "DIGIT")


def parse_numbering(payload: bytes) -> NumberingDef:
    """수준 1~7 [문단 머리 정보 12B + WORD len + WCHAR[len] 형식 문자열], UINT16 시작 번호,
    (있으면) 수준별 시작 번호 UINT32 ×7. 잘렸으면 있는 만큼만 읽는다."""
    templates: list[tuple[str, NumFormat]] = []
    off = 0
    for _ in range(NUMBERING_LEVELS):
        if len(payload) < off + _PARA_HEAD_INFO_SIZE + 2:
            break
        (prop,) = struct.unpack_from("<I", payload, off)
        off += _PARA_HEAD_INFO_SIZE
        (n,) = struct.unpack_from("<H", payload, off)
        off += 2
        raw = payload[off : off + 2 * n]
        off += 2 * n
        template = raw[: len(raw) // 2 * 2].decode("utf-16-le", errors="replace")
        templates.append((template, num_format((prop >> 5) & 0x1F)))
    start = 0
    if len(templates) == NUMBERING_LEVELS and len(payload) >= off + 2:
        (start,) = struct.unpack_from("<H", payload, off)
        off += 2
    level_starts: tuple[int, ...] = ()
    if len(payload) >= off + 4 * NUMBERING_LEVELS:
        level_starts = struct.unpack_from(f"<{NUMBERING_LEVELS}I", payload, off)
    levels = tuple(
        NumberingLevel(t, f, level_starts[k] if k < len(level_starts) else None)
        for k, (t, f) in enumerate(templates)
    )
    return NumberingDef(levels=levels, start=start)


def parse_bullet(payload: bytes) -> BulletDef:
    """문단 머리 정보 12B 다음 WCHAR 글머리표 문자. 잘렸으면 ""."""
    raw = payload[_PARA_HEAD_INFO_SIZE : _PARA_HEAD_INFO_SIZE + 2]
    char = raw.decode("utf-16-le", errors="replace") if len(raw) == 2 else ""
    return BulletDef(char=char)


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
    """PARA_SHAPE·BIN_DATA·NUMBERING·BULLET 을 각각 등장 순서대로 수집.
    data == b"" → EMPTY_DOCINFO."""
    if not data:
        return EMPTY_DOCINFO
    shapes: list[ParaShape] = []
    bins: list[BinDataEntry] = []
    numberings: list[NumberingDef] = []
    bullets: list[BulletDef] = []
    for r in iter_records(data):
        if r.tag_id == HWPTAG_PARA_SHAPE:
            shapes.append(parse_para_shape(r.payload))
        elif r.tag_id == HWPTAG_BIN_DATA:
            bins.append(parse_bin_data(r.payload))
        elif r.tag_id == HWPTAG_NUMBERING:
            numberings.append(parse_numbering(r.payload))
        elif r.tag_id == HWPTAG_BULLET:
            bullets.append(parse_bullet(r.payload))
    return DocInfo(
        para_shapes=tuple(shapes),
        bin_data=tuple(bins),
        numberings=tuple(numberings),
        bullets=tuple(bullets),
    )
