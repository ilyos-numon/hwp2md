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
from ..skips import SkipCounter, SkipKind
from ..source import Source, as_binary_io, source_label
from .body import ReadContext, parse_blocks
from .distdoc import decrypt_view_text
from .docinfo import (
    BIN_DATA_EMBEDDING,
    BIN_DATA_LINK,
    BIN_DATA_STORAGE,
    BinDataEntry,
    DocInfo,
    parse_docinfo,
)
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


def _strip_aes_padding(data: bytes) -> bytes:
    """비압축 배포용 섹션 끝의 AES 블록 0 채움(16B 미만)을 레코드 경계에서 잘라 낸다."""
    pos = 0
    end = len(data)
    while pos < end:
        if end - pos < 16 and not any(data[pos:]):
            return data[:pos]
        if pos + 4 > end:
            break
        (header,) = struct.unpack_from("<I", data, pos)
        pos += 4
        size = (header >> 20) & 0xFFF
        if size == 0xFFF:
            if pos + 4 > end:
                break
            (size,) = struct.unpack_from("<I", data, pos)
            pos += 4
        pos += size
    return data


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
        if header.distribution and not ole.exists("ViewText/Section0"):
            raise UnsupportedHwpError(f"distribution document: ViewText missing: {label}")
        docinfo = b""
        if ole.exists("DocInfo"):
            raw = _read_stream(ole, "DocInfo")
            docinfo = _inflate(raw) if header.compressed else raw
        # 배포용(bit2): BodyText 대신 ViewText/Section<N> 을 복호화해 읽는다.
        # DocInfo·BinData 는 평문
        storage = "ViewText" if header.distribution else "BodyText"
        sections: list[bytes] = []
        n = 0
        while ole.exists(f"{storage}/Section{n}"):
            data = _read_stream(ole, f"{storage}/Section{n}")
            if header.distribution:
                data = decrypt_view_text(data)
            if header.compressed:
                try:
                    data = _inflate(data)
                except zlib.error as exc:
                    if not header.distribution:
                        raise
                    raise UnsupportedHwpError(
                        f"distribution document: cannot inflate ViewText: {label}"
                    ) from exc
            elif header.distribution:
                data = _strip_aes_padding(data)
            sections.append(data)
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
    """ImageResolver·ObjectResolver 구현. 문서 하나당 인스턴스 하나(ImageNamer 포함).
    skips 가 있으면 해석하지 못한 그림 참조를 참조 1개당 1 센다
    (LINK → image_link, 항목·본체 없음 → image_missing)."""

    def __init__(
        self,
        docinfo: DocInfo,
        streams: Mapping[str, bytes],
        *,
        compressed: bool,
        skips: SkipCounter | None = None,
    ) -> None:
        self._docinfo = docinfo
        self._streams = streams
        self._compressed = compressed
        self._skips = skips
        self._namer = ImageNamer()
        self._cache: dict[int, tuple[Image | None, SkipKind | None]] = {}

    def resolve(self, bindata_id: int) -> Image | None:
        if bindata_id not in self._cache:
            self._cache[bindata_id] = self._resolve(bindata_id)
        image, reason = self._cache[bindata_id]
        if reason is not None and self._skips is not None:
            self._skips.add(reason)
        return image

    def ole_data(self, bindata_id: int) -> bytes | None:
        """OLE 개체 BinData 스트림(압축이면 해제). 항목·스트림이 없으면 None."""
        entry = self._docinfo.bin_data_entry(bindata_id)
        if entry is None or entry.storage_type not in (BIN_DATA_EMBEDDING, BIN_DATA_STORAGE):
            return None
        return self._stream_data(entry)

    def make_image(self, key: str, data: bytes) -> Image:
        """OLE 안 원본 그림 → 이름 붙은 Image (그림과 같은 번호 체계)."""
        return Image(file_name=self._namer.name_for(key, normalize_ext(None, data)), data=data)

    def _stream_data(self, entry: BinDataEntry) -> bytes | None:
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
        if not inflate:
            return raw
        try:
            return _inflate(raw)
        except zlib.error:
            return raw

    def _resolve(self, bindata_id: int) -> tuple[Image | None, SkipKind | None]:
        entry = self._docinfo.bin_data_entry(bindata_id)
        if entry is not None and entry.storage_type == BIN_DATA_LINK:
            return None, "image_link"
        if entry is None or entry.storage_type != BIN_DATA_EMBEDDING:
            return None, "image_missing"
        data = self._stream_data(entry)
        if data is None:
            return None, "image_missing"
        ext = normalize_ext(entry.ext, data)
        return Image(file_name=self._namer.name_for(str(bindata_id), ext), data=data), None


def read_sections(path: Source) -> list[bytes]:
    """호환 래퍼: BodyText/Section<N> 스트림을 N 오름차순으로 (압축이면 해제해서) 반환."""
    return read_streams(path)[1]


def read_blocks(path: Source, skips: SkipCounter | None = None) -> list[Block]:
    """각 섹션에 iter_records → parse_blocks 를 적용해 섹션 순서대로 이어 붙이고,
    문서 끝에 각주(번호순)·미주(번호순) Note 블록을 둔다.
    skips: 건너뛴 요소(머리말·꼬리말·숨은 설명·메모·차트·OLE·글맵시·그림 참조)를 셀 카운터."""
    pkg = read_hwp5_package(path)
    docinfo = parse_docinfo(pkg.docinfo)
    ctx = ReadContext(skips)  # 각주 번호·건너뜀을 섹션을 넘어 유지
    store = BinDataStore(docinfo, pkg.bin_data, compressed=pkg.header.compressed, skips=ctx.skips)
    blocks: list[Block] = []
    for section in pkg.sections:
        blocks.extend(parse_blocks(iter_records(section), docinfo, store, ctx))
    blocks.extend(ctx.note_blocks())
    return blocks


def read_paragraphs(path: Source) -> list[str]:
    """호환 래퍼: 본문 Paragraph 블록의 비어 있지 않은 텍스트만 (표 셀 텍스트 제외)."""
    return [b.text for b in read_blocks(path) if isinstance(b, Paragraph) and b.text]
