"""HWP 5.0 OLE container reader: FileHeader, BodyText sections, paragraphs."""

from __future__ import annotations

import struct
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import olefile

from ..blocks import Block, Paragraph
from ..errors import NotHwpFileError, UnsupportedHwpError
from .body import parse_blocks
from .docinfo import parse_docinfo
from .records import iter_records

HWP5_SIGNATURE = b"HWP Document File" + b"\x00" * 15  # 32 bytes
FILE_HEADER_SIZE = 256

_PROP_COMPRESSED = 0x1
_PROP_ENCRYPTED = 0x2
_PROP_DISTRIBUTION = 0x4


@dataclass(frozen=True)
class FileHeader:
    version: tuple[int, int, int, int]  # (MM, nn, PP, rr)
    compressed: bool  # properties bit 0
    encrypted: bool  # properties bit 1
    distribution: bool  # properties bit 2


def parse_file_header(raw: bytes) -> FileHeader:
    """len(raw) != 256 또는 raw[:32] != HWP5_SIGNATURE → NotHwpFileError."""
    if len(raw) != FILE_HEADER_SIZE:
        raise NotHwpFileError(f"FileHeader must be {FILE_HEADER_SIZE} bytes, got {len(raw)}")
    if raw[:32] != HWP5_SIGNATURE:
        raise NotHwpFileError("FileHeader signature mismatch")
    (v,) = struct.unpack("<I", raw[32:36])
    (properties,) = struct.unpack("<I", raw[36:40])
    return FileHeader(
        version=((v >> 24) & 0xFF, (v >> 16) & 0xFF, (v >> 8) & 0xFF, v & 0xFF),
        compressed=bool(properties & _PROP_COMPRESSED),
        encrypted=bool(properties & _PROP_ENCRYPTED),
        distribution=bool(properties & _PROP_DISTRIBUTION),
    )


def _read_stream(ole: Any, name: str) -> bytes:
    return bytes(ole.openstream(name).read())


def _inflate(data: bytes) -> bytes:
    d = zlib.decompressobj(-15)
    return d.decompress(data) + d.flush()


def read_streams(path: Path) -> tuple[bytes, list[bytes]]:
    """(DocInfo 바이트 — 압축이면 해제, 없으면 b"" ; BodyText/Section<N> N 오름차순)."""
    if not olefile.isOleFile(str(path)):
        raise NotHwpFileError(f"not an OLE compound file: {path}")
    ole = olefile.OleFileIO(str(path))
    try:
        if not ole.exists("FileHeader"):
            raise NotHwpFileError(f"FileHeader stream missing: {path}")
        header = parse_file_header(_read_stream(ole, "FileHeader"))
        if header.encrypted:
            raise UnsupportedHwpError(f"encrypted document: {path}")
        if header.distribution:
            raise UnsupportedHwpError(f"distribution document: {path}")
        docinfo = b""
        if ole.exists("DocInfo"):
            raw = _read_stream(ole, "DocInfo")
            docinfo = _inflate(raw) if header.compressed else raw
        sections: list[bytes] = []
        n = 0
        while ole.exists(f"BodyText/Section{n}"):
            data = _read_stream(ole, f"BodyText/Section{n}")
            sections.append(_inflate(data) if header.compressed else data)
            n += 1
    finally:
        ole.close()
    if not sections:
        raise NotHwpFileError(f"BodyText/Section0 stream missing: {path}")
    return docinfo, sections


def read_sections(path: Path) -> list[bytes]:
    """호환 래퍼: BodyText/Section<N> 스트림을 N 오름차순으로 (압축이면 해제해서) 반환."""
    return read_streams(path)[1]


def read_blocks(path: Path) -> list[Block]:
    """각 섹션에 iter_records → parse_blocks 를 적용해 섹션 순서대로 이어 붙인다."""
    docinfo_raw, sections = read_streams(path)
    docinfo = parse_docinfo(docinfo_raw)
    blocks: list[Block] = []
    for section in sections:
        blocks.extend(parse_blocks(iter_records(section), docinfo))
    return blocks


def read_paragraphs(path: Path) -> list[str]:
    """호환 래퍼: 본문 Paragraph 블록의 비어 있지 않은 텍스트만 (표 셀 텍스트 제외)."""
    return [b.text for b in read_blocks(path) if isinstance(b, Paragraph) and b.text]
