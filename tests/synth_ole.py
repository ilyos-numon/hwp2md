"""Synthetic OLE objects and OOXML chart XML for tests (PLAN §4-H, Stage 7).

Test-only helper.
"""

from __future__ import annotations

import math
import struct
from collections.abc import Mapping, Sequence
from xml.sax.saxutils import escape

from synth_hwp5 import (
    _CFB_MAGIC,
    _DIR_ENTRY_SIZE,
    _ENTRIES_PER_SECTOR,
    _FAT_ENTRIES,
    _MINI_CUTOFF,
    _MINI_SECTOR_SIZE,
    _SECTOR_SIZE,
    _TYPE_EMPTY,
    _TYPE_ROOT,
    _TYPE_STREAM,
    ENDOFCHAIN,
    FATSECT,
    FREESECT,
    NOSTREAM,
    _dir_entry,
)

NS_C = "http://schemas.openxmlformats.org/drawingml/2006/chart"
NS_A = "http://schemas.openxmlformats.org/drawingml/2006/main"

# synth_hwp5.build_cfb 는 HWP 5.0 스트림 이름(FileHeader·DocInfo·BodyText·BinData)만 받으므로
# OLE 개체의 루트 스트림(OOXMLChartContents 등)은 같은 레이아웃·헬퍼로 여기서 만든다.


def _str_cache(values: Sequence[str]) -> str:
    pts = "".join(f'<c:pt idx="{i}"><c:v>{escape(v)}</c:v></c:pt>' for i, v in enumerate(values))
    return f'<c:strCache><c:ptCount val="{len(values)}"/>{pts}</c:strCache>'


def _num_cache(values: Sequence[str]) -> str:
    pts = "".join(f'<c:pt idx="{i}"><c:v>{escape(v)}</c:v></c:pt>' for i, v in enumerate(values))
    return (
        f'<c:numCache><c:formatCode>General</c:formatCode><c:ptCount val="{len(values)}"/>'
        f"{pts}</c:numCache>"
    )


def chart_xml(
    title: str,
    categories: Sequence[str],
    series: Sequence[tuple[str, Sequence[str]]],
) -> bytes:
    """c:chartSpace + c:barChart. 범주는 strCache, 값은 numCache. title=="" 이면 c:title 없음.
    계열명이 "" 이면 c:tx 를 넣지 않는다."""
    title_xml = ""
    if title:
        title_xml = (
            "<c:title><c:tx><c:rich><a:bodyPr/><a:p><a:r>"
            f"<a:t>{escape(title)}</a:t></a:r></a:p></c:rich></c:tx>"
            '<c:overlay val="0"/></c:title>'
        )
    sers = []
    for k, (name, values) in enumerate(series):
        tx = (
            f"<c:tx><c:strRef><c:f>Sheet1!$B${k + 1}</c:f>{_str_cache([name])}</c:strRef></c:tx>"
            if name
            else ""
        )
        sers.append(
            f'<c:ser><c:idx val="{k}"/><c:order val="{k}"/>{tx}'
            f"<c:cat><c:strRef><c:f>Sheet1!$A$2</c:f>{_str_cache(categories)}</c:strRef></c:cat>"
            f"<c:val><c:numRef><c:f>Sheet1!$B$2</c:f>{_num_cache(values)}</c:numRef></c:val>"
            "</c:ser>"
        )
    xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<c:chartSpace xmlns:c="{NS_C}" xmlns:a="{NS_A}">'
        f"<c:chart>{title_xml}"
        '<c:autoTitleDeleted val="0"/><c:plotArea><c:layout/>'
        '<c:barChart><c:barDir val="col"/><c:grouping val="clustered"/>'
        f'{"".join(sers)}<c:axId val="1"/><c:axId val="2"/></c:barChart>'
        '<c:catAx><c:axId val="1"/><c:title><c:tx><c:rich><a:p><a:r><a:t>축</a:t></a:r></a:p>'
        "</c:rich></c:tx></c:title></c:catAx>"
        '<c:valAx><c:axId val="2"/></c:valAx>'
        "</c:plotArea></c:chart></c:chartSpace>"
    )
    return xml.encode("utf-8")


def build_ole_cfb(streams: Mapping[str, bytes]) -> bytes:
    """루트 바로 아래 스트림만 있는 CFB (v3, 512B 섹터, 스트림은 모두 미니스트림 < 4096B).

    synth_hwp5 의 상수·디렉터리 엔트리 헬퍼(build_cfb 와 같은 레이아웃)를 쓴다."""
    names = sorted(streams, key=lambda n: (len(n), n.upper()))
    if not names or any(not n or "/" in n for n in names):
        raise ValueError("streams must be non-empty root-level names")
    for name in names:
        if len(streams[name]) >= _MINI_CUTOFF:
            raise ValueError(f"stream {name!r} is {len(streams[name])} bytes; supports < 4096")

    ministream = bytearray()
    minifat: list[int] = []
    mini_start: dict[str, int] = {}
    for name in names:
        data = streams[name]
        count = math.ceil(len(data) / _MINI_SECTOR_SIZE)
        if count == 0:
            mini_start[name] = ENDOFCHAIN
            continue
        first = len(minifat)
        mini_start[name] = first
        minifat.extend(range(first + 1, first + count))
        minifat.append(ENDOFCHAIN)
        ministream += data + b"\x00" * (count * _MINI_SECTOR_SIZE - len(data))
    if len(minifat) > _FAT_ENTRIES:
        raise ValueError("too many mini sectors for a single MiniFAT sector")

    entries_count = 1 + len(names)
    dir_sectors = math.ceil(entries_count * _DIR_ENTRY_SIZE / _SECTOR_SIZE)
    minifat_sector = 1 + dir_sectors
    ministream_first = minifat_sector + 1
    ministream_sectors = math.ceil(len(ministream) / _SECTOR_SIZE)
    total_sectors = ministream_first + ministream_sectors
    if total_sectors > _FAT_ENTRIES:
        raise ValueError("too many sectors for a single FAT sector")

    fat = [FREESECT] * _FAT_ENTRIES
    fat[0] = FATSECT
    for s in range(1, 1 + dir_sectors):
        fat[s] = s + 1 if s < dir_sectors else ENDOFCHAIN
    fat[minifat_sector] = ENDOFCHAIN
    for i in range(ministream_sectors):
        s = ministream_first + i
        fat[s] = s + 1 if i < ministream_sectors - 1 else ENDOFCHAIN
    fat_bytes = struct.pack(f"<{_FAT_ENTRIES}I", *fat)
    minifat_full = minifat + [FREESECT] * (_FAT_ENTRIES - len(minifat))
    minifat_bytes = struct.pack(f"<{_FAT_ENTRIES}I", *minifat_full)

    # 디렉터리: 루트의 자식은 1번, 형제는 이름 순으로 오른쪽 사슬
    root_start = ministream_first if ministream_sectors else ENDOFCHAIN
    entries = [
        _dir_entry("Root Entry", _TYPE_ROOT, child=1, start=root_start, size=len(ministream))
    ]
    for j, name in enumerate(names):
        entries.append(
            _dir_entry(
                name,
                _TYPE_STREAM,
                right=2 + j if j < len(names) - 1 else NOSTREAM,
                start=mini_start[name],
                size=len(streams[name]),
            )
        )
    slots = dir_sectors * _ENTRIES_PER_SECTOR
    entries.extend(_dir_entry("", _TYPE_EMPTY) for _ in range(slots - len(entries)))
    dir_bytes = b"".join(entries)

    header = bytearray(_SECTOR_SIZE)
    header[0:8] = _CFB_MAGIC
    struct.pack_into("<HHHHH", header, 24, 0x003E, 0x0003, 0xFFFE, 0x0009, 0x0006)
    struct.pack_into(
        "<IIIIIIIII",
        header,
        40,
        0,
        1,
        1,
        0,
        _MINI_CUTOFF,
        minifat_sector,
        1,
        ENDOFCHAIN,
        0,
    )
    struct.pack_into("<109I", header, 76, *([0] + [FREESECT] * 108))

    ministream_padded = bytes(ministream) + b"\x00" * (
        ministream_sectors * _SECTOR_SIZE - len(ministream)
    )
    return bytes(header) + fat_bytes + dir_bytes + minifat_bytes + ministream_padded


def ole10_native(payload: bytes) -> bytes:
    """\\x01Ole10Native 스트림 = [UINT32 LE 길이][원본]."""
    return struct.pack("<I", len(payload)) + payload


def hwpx_ole_entry(cfb: bytes) -> bytes:
    """HWPX BinData/*.ole 엔트리 = [UINT32 LE len(cfb)][cfb]."""
    return struct.pack("<I", len(cfb)) + cfb
