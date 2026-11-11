"""HWP 5.0 record stream parsing and PARA_TEXT decoding."""

from __future__ import annotations

import struct
from collections.abc import Iterator
from dataclasses import dataclass

from ..errors import Hwp2mdError

HWPTAG_BEGIN = 0x10
HWPTAG_DOCUMENT_PROPERTIES = 0x10  # DocInfo 첫 레코드 (파서는 읽지 않음, fixture가 씀)
HWPTAG_PARA_SHAPE = 0x19  # 25. DocInfo 문단 모양 (ID = 등장 순서)
HWPTAG_STYLE = 0x1A  # 26. DocInfo 스타일 (파서는 읽지 않음, fixture가 씀)
HWPTAG_PARA_HEADER = 0x42  # 66
HWPTAG_PARA_TEXT = 0x43  # 67
HWPTAG_PARA_CHAR_SHAPE = 0x44  # 68
HWPTAG_PARA_LINE_SEG = 0x45  # 69
HWPTAG_CTRL_HEADER = 0x47  # 71
HWPTAG_LIST_HEADER = 0x48  # 72
HWPTAG_TABLE = 0x4D  # 77
CTRL_ID_TABLE = b"tbl "[::-1]  # == b" lbt". 파일에는 ctrl_id 4바이트가 역순으로 저장된다
HWPTAG_BIN_DATA = 0x12  # 18. DocInfo 바이너리 데이터 (ID = 등장 순서, 1부터)
HWPTAG_SHAPE_COMPONENT = 0x4C  # 76. 개체 요소 (파서는 읽지 않음, fixture가 씀)
HWPTAG_SHAPE_COMPONENT_PICTURE = 0x55  # 85. 그림 개체 (UINT16 bindata_id @71)
CTRL_ID_GSO = b"gso "[::-1]  # == b" osg". 그리기 개체 컨트롤
CTRL_ID_HEADER = b"head"[::-1]  # 머리말
CTRL_ID_FOOTER = b"foot"[::-1]  # 꼬리말
CTRL_ID_FOOTNOTE = b"fn  "[::-1]  # 각주
CTRL_ID_ENDNOTE = b"en  "[::-1]  # 미주
CTRL_ID_HYPERLINK = b"%hlk"[::-1]  # 하이퍼링크 필드
CTRL_ID_EQUATION = b"eqed"[::-1]  # 수식
CTRL_ID_HIDDEN_COMMENT = b"tcmt"[::-1]  # 숨은 설명
CTRL_ID_MEMO = b"%%me"[::-1]  # 메모 필드
HWPTAG_NUMBERING = 0x17  # 23. DocInfo 문단 번호
HWPTAG_BULLET = 0x18  # 24. DocInfo 글머리표
HWPTAG_SHAPE_COMPONENT_OLE = 0x54  # 84
HWPTAG_CTRL_DATA = 0x57  # 87
HWPTAG_EQEDIT = 0x58  # 88. 수식 (UINT32 속성, WORD len, WCHAR[len] 스크립트)
HWPTAG_SHAPE_COMPONENT_TEXTART = 0x5A  # 90
HWPTAG_MEMO_LIST = 0x5D  # 93. 마지막 섹션 끝의 메모 목록

_EXTENDED_SIZE = 0xFFF

# 8 WCHAR(16 bytes)를 차지하는 확장·인라인 컨트롤 코드
_WIDE_CONTROLS = frozenset(
    {1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23}
)
# 같은 단락의 CTRL_HEADER 하나와 등장 순서로 1:1 대응하는 확장 제어문자
EXTENDED_CONTROLS = frozenset({1, 2, 3, 11, 12, 14, 15, 16, 17, 18, 21, 22, 23})
FIELD_START = 3
FIELD_END = 4
_TAB = 9
_LINE_BREAK = 10
_PARA_END = 13
_HYPHEN = 24
_SPACES = frozenset({30, 31})


@dataclass(frozen=True)
class CtrlMark:
    """PARA_TEXT 안 확장 제어문자(EXTENDED_CONTROLS) 또는 필드 끝(4)의 위치."""

    code: int


@dataclass(frozen=True)
class Record:
    tag_id: int
    level: int
    payload: bytes


def iter_records(data: bytes) -> Iterator[Record]:
    """레코드 헤더 UINT32 LE:
    tag_id = v & 0x3FF, level = (v >> 10) & 0x3FF, size = (v >> 20) & 0xFFF.
    size == 0xFFF 이면 바로 다음 UINT32 LE 가 실제 size. 헤더 또는 payload가 잘리면
    Hwp2mdError("truncated record at offset N")."""
    pos = 0
    end = len(data)
    while pos < end:
        start = pos
        if pos + 4 > end:
            raise Hwp2mdError(f"truncated record at offset {start}")
        (header,) = struct.unpack_from("<I", data, pos)
        pos += 4
        tag_id = header & 0x3FF
        level = (header >> 10) & 0x3FF
        size = (header >> 20) & 0xFFF
        if size == _EXTENDED_SIZE:
            if pos + 4 > end:
                raise Hwp2mdError(f"truncated record at offset {start}")
            (size,) = struct.unpack_from("<I", data, pos)
            pos += 4
        if pos + size > end:
            raise Hwp2mdError(f"truncated record at offset {start}")
        yield Record(tag_id=tag_id, level=level, payload=bytes(data[pos : pos + size]))
        pos += size


def decode_para_text(payload: bytes) -> str:
    """UTF-16LE WCHAR 배열을 단락 문자열로. 규칙은 §4.4-C. 결과는 .strip() 적용."""
    count = len(payload) // 2  # 홀수 길이면 마지막 1바이트 무시
    out = bytearray()
    i = 0
    while i < count:
        code = payload[2 * i] | (payload[2 * i + 1] << 8)
        if code >= 32:
            out += payload[2 * i : 2 * i + 2]
            i += 1
        elif code in _WIDE_CONTROLS:
            if code == _TAB:
                out += b" \x00"
            i += 8
        elif code == _PARA_END:
            break
        else:
            if code == _LINE_BREAK:
                out += b"\n\x00"
            elif code == _HYPHEN:
                out += b"-\x00"
            elif code in _SPACES:
                out += b" \x00"
            # 0, 25~29: 출력 없음
            i += 1
    return out.decode("utf-16-le", errors="replace").strip()


def decode_para_runs(payload: bytes) -> list[str | CtrlMark]:
    """decode_para_text 와 같은 글자 규칙으로 읽되, 확장 제어문자와 필드 끝(4) 자리에
    CtrlMark 를 남긴다. 인접 글자는 한 str 로 합친다. strip 하지 않는다."""
    count = len(payload) // 2  # 홀수 길이면 마지막 1바이트 무시
    runs: list[str | CtrlMark] = []
    out = bytearray()

    def flush() -> None:
        if out:
            runs.append(out.decode("utf-16-le", errors="replace"))
            out.clear()

    i = 0
    while i < count:
        code = payload[2 * i] | (payload[2 * i + 1] << 8)
        if code >= 32:
            out += payload[2 * i : 2 * i + 2]
            i += 1
        elif code in _WIDE_CONTROLS:
            if code == _TAB:
                out += b" \x00"
            elif code in EXTENDED_CONTROLS or code == FIELD_END:
                flush()
                runs.append(CtrlMark(code))
            i += 8
        elif code == _PARA_END:
            break
        else:
            if code == _LINE_BREAK:
                out += b"\n\x00"
            elif code == _HYPHEN:
                out += b"-\x00"
            elif code in _SPACES:
                out += b" \x00"
            i += 1
    flush()
    return runs
