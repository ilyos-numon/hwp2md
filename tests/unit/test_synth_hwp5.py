import struct
import zlib
from pathlib import Path

import olefile
import pytest

from hwp2md.hwp5.records import (
    HWPTAG_PARA_HEADER,
    HWPTAG_PARA_TEXT,
    decode_para_text,
    iter_records,
)
from synth_hwp5 import (
    FIXTURE_PARAGRAPHS,
    HWP5_SIGNATURE,
    build_cfb,
    build_file_header,
    build_hwp5,
    write_hwp5,
)


def _read_stream(path: Path, name: str) -> bytes:
    ole = olefile.OleFileIO(str(path))
    try:
        return bytes(ole.openstream(name).read())
    finally:
        ole.close()


def _inflate(data: bytes) -> bytes:
    d = zlib.decompressobj(-15)
    return d.decompress(data) + d.flush()


def test_build_file_header_layout() -> None:
    header = build_file_header()
    assert len(header) == 256
    assert header[:32] == HWP5_SIGNATURE
    assert header[32:36] == struct.pack("<I", 0x05000300)
    assert header[36:40] == b"\x01\x00\x00\x00"
    assert header[40:] == b"\x00" * 216


def test_write_hwp5_is_ole_with_expected_streams(tmp_path: Path) -> None:
    path = write_hwp5(tmp_path / "sub" / "sample.hwp", FIXTURE_PARAGRAPHS)
    assert path == tmp_path / "sub" / "sample.hwp"
    assert olefile.isOleFile(str(path))
    ole = olefile.OleFileIO(str(path))
    try:
        assert sorted(ole.listdir()) == [["BodyText", "Section0"], ["DocInfo"], ["FileHeader"]]
    finally:
        ole.close()


def test_file_header_stream_is_256_bytes(tmp_path: Path) -> None:
    path = write_hwp5(tmp_path / "sample.hwp", FIXTURE_PARAGRAPHS)
    raw = _read_stream(path, "FileHeader")
    assert len(raw) == 256
    assert raw == build_file_header()


def test_section0_round_trips_paragraphs(tmp_path: Path) -> None:
    path = write_hwp5(tmp_path / "sample.hwp", FIXTURE_PARAGRAPHS)
    section = _inflate(_read_stream(path, "BodyText/Section0"))
    texts = [r for r in iter_records(section) if r.tag_id == HWPTAG_PARA_TEXT]
    assert len(texts) == 4
    assert [decode_para_text(r.payload) for r in texts] == [p.strip() for p in FIXTURE_PARAGRAPHS]


def test_only_last_para_header_has_last_bit(tmp_path: Path) -> None:
    path = write_hwp5(tmp_path / "sample.hwp", FIXTURE_PARAGRAPHS)
    section = _inflate(_read_stream(path, "BodyText/Section0"))
    headers = [r for r in iter_records(section) if r.tag_id == HWPTAG_PARA_HEADER]
    assert len(headers) == 4
    nchars = [struct.unpack_from("<I", r.payload)[0] for r in headers]
    assert all(len(r.payload) == 22 for r in headers)
    assert [bool(n & 0x80000000) for n in nchars] == [False, False, False, True]
    expected = [len(p.encode("utf-16-le")) // 2 + 1 for p in FIXTURE_PARAGRAPHS]
    assert [n & 0x7FFFFFFF for n in nchars] == expected


def test_uncompressed_section_when_properties_zero(tmp_path: Path) -> None:
    path = write_hwp5(tmp_path / "plain.hwp", FIXTURE_PARAGRAPHS, properties=0)
    assert _read_stream(path, "FileHeader")[36:40] == b"\x00\x00\x00\x00"
    section = _read_stream(path, "BodyText/Section0")
    texts = [
        decode_para_text(r.payload) for r in iter_records(section) if r.tag_id == HWPTAG_PARA_TEXT
    ]
    assert texts == [p.strip() for p in FIXTURE_PARAGRAPHS]


def test_build_cfb_rejects_stream_of_4096_bytes_or_more() -> None:
    streams = {
        "FileHeader": build_file_header(),
        "DocInfo": b"",
        "BodyText/Section0": b"\x00" * 4096,
    }
    with pytest.raises(ValueError):
        build_cfb(streams)


def test_build_hwp5_rejects_oversized_uncompressed_section() -> None:
    long_paragraphs = ["가" * 3000]
    with pytest.raises(ValueError):
        build_hwp5(long_paragraphs, properties=0)
