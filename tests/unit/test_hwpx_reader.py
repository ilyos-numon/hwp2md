import io
import zipfile
from pathlib import Path

import pytest
from lxml import etree

from hwp2md.blocks import Paragraph
from hwp2md.errors import Hwp2mdError, NotHwpFileError
from hwp2md.hwpx import reader
from hwp2md.hwpx.reader import (
    HWPX_SECTION0,
    NS_HP,
    NS_HS,
    make_parser,
    read_blocks,
    section_names,
)
from synth_hwp5 import FIXTURE_PARAGRAPHS
from synth_hwpx import XML_DECL, build_zip, hwpx_entries


def _write(tmp_path: Path, section0: bytes | None) -> Path:
    entries = hwpx_entries(FIXTURE_PARAGRAPHS)
    if section0 is None:
        del entries[HWPX_SECTION0]
    else:
        entries[HWPX_SECTION0] = section0
    path = tmp_path / "doc.hwpx"
    path.write_bytes(build_zip(entries))
    return path


def _entity_section(doctype: str, t_inner: str) -> bytes:
    return (
        XML_DECL
        + doctype
        + f'<hs:sec xmlns:hp="{NS_HP}" xmlns:hs="{NS_HS}">'
        + f"<hp:p><hp:run><hp:t>{t_inner}</hp:t></hp:run></hp:p>"
        + "</hs:sec>"
    ).encode("utf-8")


def test_not_a_zip_raises_not_hwp(tmp_path: Path) -> None:
    path = tmp_path / "plain.hwpx"
    path.write_text("not a zip", encoding="utf-8")
    with pytest.raises(NotHwpFileError):
        read_blocks(path)


def test_missing_section0_raises_not_hwp(tmp_path: Path) -> None:
    with pytest.raises(NotHwpFileError):
        read_blocks(_write(tmp_path, None))


def test_section_names_numeric_order() -> None:
    names = [f"Contents/section{n}.xml" for n in (0, 1, 10, 2)]
    zf = zipfile.ZipFile(io.BytesIO(build_zip({n: b"<x/>" for n in names})))
    assert section_names(zf) == [f"Contents/section{n}.xml" for n in (0, 1, 2, 10)]


def test_malformed_xml_raises_hwp2md_error(tmp_path: Path) -> None:
    with pytest.raises(Hwp2mdError, match="malformed section XML"):
        read_blocks(_write(tmp_path, b"<hs:sec>unclosed"))


def test_wrong_root_raises_hwp2md_error(tmp_path: Path) -> None:
    with pytest.raises(Hwp2mdError, match="unexpected root element"):
        read_blocks(_write(tmp_path, b'<?xml version="1.0"?><x/>'))


def test_oversized_section_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(reader, "MAX_SECTION_BYTES", 10)
    with pytest.raises(Hwp2mdError, match="too large"):
        read_blocks(_write(tmp_path, hwpx_entries(FIXTURE_PARAGRAPHS)[HWPX_SECTION0]))


def test_external_entity_not_resolved(tmp_path: Path) -> None:
    doctype = '<!DOCTYPE hs:sec [<!ENTITY xxe SYSTEM "file:///etc/hosts">]>'
    path = _write(tmp_path, _entity_section(doctype, "a&xxe;b"))
    assert read_blocks(path) == [Paragraph("ab")]


def test_internal_entity_not_expanded(tmp_path: Path) -> None:
    doctype = '<!DOCTYPE hs:sec [<!ENTITY lol "lol">]>'
    path = _write(tmp_path, _entity_section(doctype, "a&lol;b"))
    assert read_blocks(path) == [Paragraph("ab")]


def test_make_parser_options() -> None:
    # lxml 6 의 XMLParser 는 resolve_entities 를 속성으로 노출하지 않으므로 동작으로 확인한다:
    # resolve_entities=False 이면 내부 엔티티가 확장되지 않고 _Entity 노드로 남는다.
    p = make_parser()
    root = etree.fromstring(b'<!DOCTYPE r [<!ENTITY lol "lol">]><r>a&lol;b</r>', p)
    assert [type(c) for c in root] == [etree._Entity]
    assert (root.text, root[0].tail) == ("a", "b")
    assert make_parser() is not p
