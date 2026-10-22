"""HWPX (OWPML zip package) reader: section XML files -> blocks."""

from __future__ import annotations

import re
import zipfile
from pathlib import Path

from lxml import etree

from ..blocks import Block
from ..errors import Hwp2mdError, NotHwpFileError
from .body import parse_section

HWPX_MIMETYPE = b"application/hwp+zip"
HWPX_SECTION0 = "Contents/section0.xml"
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


def read_sections(path: Path) -> list[bytes]:
    try:
        zf = zipfile.ZipFile(path)
    except zipfile.BadZipFile as exc:
        raise NotHwpFileError(f"not a zip archive: {path}") from exc
    with zf:
        out: list[bytes] = []
        for name in section_names(zf):
            size = zf.getinfo(name).file_size
            if size > MAX_SECTION_BYTES:
                raise Hwp2mdError(f"section XML too large: {name} ({size} bytes)")
            out.append(zf.read(name))
        return out


def parse_section_xml(data: bytes) -> etree._Element:
    try:
        root = etree.fromstring(data, make_parser())
    except etree.XMLSyntaxError as exc:
        raise Hwp2mdError(f"malformed section XML: {exc}") from exc
    if root.tag != HS_SEC:
        raise Hwp2mdError(f"unexpected root element: {root.tag}")
    return root


def read_blocks(path: Path) -> list[Block]:
    blocks: list[Block] = []
    for data in read_sections(path):
        blocks.extend(parse_section(parse_section_xml(data)))
    return blocks
