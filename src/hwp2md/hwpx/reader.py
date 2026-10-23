"""HWPX (OWPML zip package) reader: section XML files -> blocks."""

from __future__ import annotations

import re
import zipfile
from dataclasses import dataclass

from lxml import etree

from ..blocks import Block
from ..errors import EncryptedDocumentError, Hwp2mdError, NotHwpFileError
from ..skips import SkipCounter
from ..source import Source, as_binary_io, source_label
from .bindata import (
    BIN_DATA_PREFIX,
    HWPX_CONTENT_HPF,
    MAX_IMAGE_BYTES,
    BinItemStore,
    parse_manifest,
)
from .body import DocContext, parse_section
from .header import EMPTY_HEADER, parse_header, parse_header_xml

HWPX_MIMETYPE = b"application/hwp+zip"
HWPX_SECTION0 = "Contents/section0.xml"
HWPX_HEADER = "Contents/header.xml"
HWPX_ODF_MANIFEST = "META-INF/manifest.xml"
NS_HP = "http://www.hancom.co.kr/hwpml/2011/paragraph"
NS_HS = "http://www.hancom.co.kr/hwpml/2011/section"
HS_SEC = f"{{{NS_HS}}}sec"
MAX_SECTION_BYTES = 50 * 1024 * 1024
_SECTION_NAME = re.compile(r"^Contents/section(\d+)\.xml$")


def make_parser() -> etree.XMLParser:
    """XXE·엔티티 폭발 방어 옵션으로만 만든다. 호출마다 새 인스턴스."""
    return etree.XMLParser(resolve_entities=False, no_network=True, huge_tree=False)


def section_names(zf: zipfile.ZipFile) -> list[str]:
    found: list[tuple[int, str]] = []
    for name in zf.namelist():
        m = _SECTION_NAME.match(name)
        if m:
            found.append((int(m.group(1)), name))
    if not any(name == HWPX_SECTION0 for _, name in found):
        raise NotHwpFileError(f"{HWPX_SECTION0} missing")
    return [name for _, name in sorted(found)]


@dataclass(frozen=True)
class HwpxPackage:
    header: bytes | None  # Contents/header.xml
    sections: list[bytes]
    manifest: bytes | None  # Contents/content.hpf
    bin_data: dict[str, bytes]  # "BinData/" 로 시작하는 파일 엔트리 전부 (키 = 엔트리 전체 이름)


def is_encrypted_manifest(data: bytes) -> bool:
    """META-INF/manifest.xml 안에 local-name 이 "encryption-data" 인 요소가 있으면 True.
    파싱할 수 없는 매니페스트는 False (본문 판정에 맡긴다)."""
    try:
        root = etree.fromstring(data, make_parser())
    except etree.XMLSyntaxError:
        return False
    return any(
        isinstance(el.tag, str) and etree.QName(el).localname == "encryption-data"
        for el in root.iter()
    )


def _check_encryption(zf: zipfile.ZipFile, label: str) -> None:
    if HWPX_ODF_MANIFEST not in zf.namelist():
        return
    if zf.getinfo(HWPX_ODF_MANIFEST).file_size > MAX_SECTION_BYTES:
        return
    if is_encrypted_manifest(zf.read(HWPX_ODF_MANIFEST)):
        raise EncryptedDocumentError(f"encrypted document: {label}")


def read_hwpx_package(path: Source) -> HwpxPackage:
    try:
        zf = zipfile.ZipFile(as_binary_io(path))
    except zipfile.BadZipFile as exc:
        raise NotHwpFileError(f"not a zip archive: {source_label(path)}") from exc
    with zf:
        _check_encryption(zf, source_label(path))
        out: list[bytes] = []
        for name in section_names(zf):
            size = zf.getinfo(name).file_size
            if size > MAX_SECTION_BYTES:
                raise Hwp2mdError(f"section XML too large: {name} ({size} bytes)")
            out.append(zf.read(name))
        names = zf.namelist()
        header: bytes | None = None
        if HWPX_HEADER in names:
            size = zf.getinfo(HWPX_HEADER).file_size
            if size > MAX_SECTION_BYTES:
                raise Hwp2mdError(f"header XML too large: {size} bytes")
            header = zf.read(HWPX_HEADER)
        manifest: bytes | None = None
        if HWPX_CONTENT_HPF in names:
            size = zf.getinfo(HWPX_CONTENT_HPF).file_size
            if size > MAX_SECTION_BYTES:
                raise Hwp2mdError(f"manifest XML too large: {size} bytes")
            manifest = zf.read(HWPX_CONTENT_HPF)
        bin_data: dict[str, bytes] = {}
        for name in names:
            if not name.startswith(BIN_DATA_PREFIX) or name.endswith("/"):
                continue
            size = zf.getinfo(name).file_size
            if size > MAX_IMAGE_BYTES:
                raise Hwp2mdError(f"binary item too large: {name} ({size} bytes)")
            bin_data[name] = zf.read(name)
        return HwpxPackage(header=header, sections=out, manifest=manifest, bin_data=bin_data)


def read_package(path: Source) -> tuple[bytes | None, list[bytes]]:
    """(header.xml 바이트 — 엔트리 없으면 None ; 섹션 바이트 목록)."""
    pkg = read_hwpx_package(path)
    return pkg.header, pkg.sections


def read_sections(path: Source) -> list[bytes]:
    return read_package(path)[1]


def parse_section_xml(data: bytes) -> etree._Element:
    try:
        root = etree.fromstring(data, make_parser())
    except etree.XMLSyntaxError as exc:
        raise Hwp2mdError(f"malformed section XML: {exc}") from exc
    if root.tag != HS_SEC:
        raise Hwp2mdError(f"unexpected root element: {root.tag}")
    return root


def read_blocks(path: Source, skips: SkipCounter | None = None) -> list[Block]:
    """skips: 건너뛴 요소(머리말·꼬리말·숨은 설명·메모)를 셀 카운터.
    각주·미주 Note 블록은 모든 섹션 뒤에 둔다."""
    pkg = read_hwpx_package(path)
    info = EMPTY_HEADER if pkg.header is None else parse_header(parse_header_xml(pkg.header))
    manifest = parse_manifest(pkg.manifest) if pkg.manifest is not None else {}
    store = BinItemStore(manifest, pkg.bin_data)
    ctx = DocContext(skips=SkipCounter() if skips is None else skips)
    blocks: list[Block] = []
    for data in pkg.sections:
        blocks.extend(parse_section(parse_section_xml(data), info, store, ctx))
    blocks.extend(ctx.note_blocks())
    return blocks
