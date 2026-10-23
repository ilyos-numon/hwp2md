"""HWP 5.0 OLE container reader: FileHeader, BodyText sections, paragraphs."""

from __future__ import annotations

import struct
import zlib
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import olefile

from ..blocks import Block, Image, Paragraph
from ..errors import (
    DrmProtectedError,
    EncryptedDocumentError,
    NotHwpFileError,
    UnsupportedHwpError,
)
from ..images import ImageNamer, normalize_ext
from ..skips import SkipCounter
from ..source import Source, as_binary_io, source_label
from .body import parse_blocks
from .docinfo import BIN_DATA_EMBEDDING, DocInfo, parse_docinfo
from .records import iter_records

HWP5_SIGNATURE = b"HWP Document File" + b"\x00" * 15  # 32 bytes
FILE_HEADER_SIZE = 256

_PROP_COMPRESSED = 0x1
_PROP_ENCRYPTED = 0x2
_PROP_DISTRIBUTION = 0x4
_PROP_DRM = 0x10  # bit 4: DRM 보안 문서
_PROP_CERT_DRM = 0x400  # bit 10: 공인인증서 DRM 보안 문서


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


@dataclass(frozen=True)
class Hwp5Package:
    header: FileHeader
    docinfo: bytes  # 압축이면 해제됨, 없으면 b""
    sections: list[bytes]  # 압축이면 해제됨, Section<N> 오름차순
    bin_data: dict[str, bytes]  # "BinData/<NAME>" 스트림 원본 바이트(해제 안 함). 키 = <NAME>


def read_hwp5_package(path: Source) -> Hwp5Package:
    """FileHeader·DocInfo·BodyText 섹션·BinData 스트림을 읽는다."""
    label = source_label(path)
    if not olefile.isOleFile(as_binary_io(path)):
        raise NotHwpFileError(f"not an OLE compound file: {label}")
    ole = olefile.OleFileIO(as_binary_io(path))
    try:
        if not ole.exists("FileHeader"):
            raise NotHwpFileError(f"FileHeader stream missing: {label}")
        raw_header = _read_stream(ole, "FileHeader")
        header = parse_file_header(raw_header)
        (properties,) = struct.unpack("<I", raw_header[36:40])
        if header.encrypted:
            raise EncryptedDocumentError(f"encrypted document: {label}")
        if properties & (_PROP_DRM | _PROP_CERT_DRM):
            raise DrmProtectedError(f"DRM-protected document: {label}")
        if header.distribution:
            raise UnsupportedHwpError(f"distribution document: {label}")
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
        bin_data: dict[str, bytes] = {}
        for entry in ole.listdir():
            if len(entry) == 2 and entry[0] == "BinData":
                bin_data[entry[1]] = _read_stream(ole, "/".join(entry))
    finally:
        ole.close()
    if not sections:
        raise NotHwpFileError(f"BodyText/Section0 stream missing: {label}")
    return Hwp5Package(header=header, docinfo=docinfo, sections=sections, bin_data=bin_data)


def read_streams(path: Source) -> tuple[bytes, list[bytes]]:
    """호환 래퍼: (DocInfo 바이트, BodyText/Section<N> 목록)."""
    pkg = read_hwp5_package(path)
    return pkg.docinfo, pkg.sections


class BinDataStore:
    """ImageResolver 구현. 문서 하나당 인스턴스 하나(ImageNamer 포함)."""

    def __init__(self, docinfo: DocInfo, streams: Mapping[str, bytes], *, compressed: bool) -> None:
        self._docinfo = docinfo
        self._streams = streams
        self._compressed = compressed
        self._namer = ImageNamer()
        self._cache: dict[int, Image | None] = {}

    def resolve(self, bindata_id: int) -> Image | None:
        if bindata_id not in self._cache:
            self._cache[bindata_id] = self._resolve(bindata_id)
        return self._cache[bindata_id]

    def _resolve(self, bindata_id: int) -> Image | None:
        entry = self._docinfo.bin_data_entry(bindata_id)
        if entry is None or entry.storage_type != BIN_DATA_EMBEDDING:
            return None
        exact = f"BIN{entry.storage_id:04X}.{entry.ext}".upper()
        prefix = f"BIN{entry.storage_id:04X}.".upper()
        name = next((k for k in self._streams if k.upper() == exact), None)
        if name is None:
            name = next((k for k in sorted(self._streams) if k.upper().startswith(prefix)), None)
        if name is None:
            return None
        raw = self._streams[name]
        if entry.compression == 2:
            inflate = False
        elif entry.compression == 1:
            inflate = True
        else:
            inflate = self._compressed
        data = raw
        if inflate:
            try:
                data = _inflate(raw)
            except zlib.error:
                data = raw
        ext = normalize_ext(entry.ext, data)
        return Image(file_name=self._namer.name_for(str(bindata_id), ext), data=data)


def read_sections(path: Source) -> list[bytes]:
    """호환 래퍼: BodyText/Section<N> 스트림을 N 오름차순으로 (압축이면 해제해서) 반환."""
    return read_streams(path)[1]


def read_blocks(path: Source, skips: SkipCounter | None = None) -> list[Block]:
    """각 섹션에 iter_records → parse_blocks 를 적용해 섹션 순서대로 이어 붙인다.
    skips: 건너뛴 요소를 셀 카운터 (아직 세지 않는다)."""
    pkg = read_hwp5_package(path)
    docinfo = parse_docinfo(pkg.docinfo)
    store = BinDataStore(docinfo, pkg.bin_data, compressed=pkg.header.compressed)
    blocks: list[Block] = []
    for section in pkg.sections:
        blocks.extend(parse_blocks(iter_records(section), docinfo, store))
    return blocks


def read_paragraphs(path: Source) -> list[str]:
    """호환 래퍼: 본문 Paragraph 블록의 비어 있지 않은 텍스트만 (표 셀 텍스트 제외)."""
    return [b.text for b in read_blocks(path) if isinstance(b, Paragraph) and b.text]
