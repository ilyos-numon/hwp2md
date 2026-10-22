import struct

import pytest

from hwp2md.errors import Hwp2mdError
from hwp2md.hwp5.records import (
    HWPTAG_PARA_HEADER,
    HWPTAG_PARA_TEXT,
    Record,
    decode_para_text,
    iter_records,
)


def _header(tag_id: int, level: int, size: int) -> bytes:
    return struct.pack("<I", tag_id | (level << 10) | (size << 20))


def _wchars(*codes: int) -> bytes:
    return b"".join(struct.pack("<H", c) for c in codes)


def test_iter_records_plain_header() -> None:
    data = struct.pack("<I", 0x00400443) + b"\x01\x02\x03\x04"
    records = list(iter_records(data))
    assert records == [Record(tag_id=0x43, level=1, payload=b"\x01\x02\x03\x04")]
    assert records[0].tag_id == HWPTAG_PARA_TEXT


def test_iter_records_multiple_records() -> None:
    data = _header(HWPTAG_PARA_HEADER, 0, 2) + b"ab" + _header(HWPTAG_PARA_TEXT, 1, 0)
    records = list(iter_records(data))
    assert records == [
        Record(tag_id=HWPTAG_PARA_HEADER, level=0, payload=b"ab"),
        Record(tag_id=HWPTAG_PARA_TEXT, level=1, payload=b""),
    ]


def test_iter_records_extended_size() -> None:
    payload = bytes(range(256)) * 20  # 5120 bytes > 0xFFF
    data = _header(HWPTAG_PARA_TEXT, 2, 0xFFF) + struct.pack("<I", len(payload)) + payload
    records = list(iter_records(data))
    assert len(records) == 1
    assert records[0].tag_id == HWPTAG_PARA_TEXT
    assert records[0].level == 2
    assert records[0].payload == payload


def test_iter_records_truncated_payload() -> None:
    data = _header(HWPTAG_PARA_TEXT, 0, 2) + b"ok" + _header(HWPTAG_PARA_TEXT, 1, 10) + b"short"
    with pytest.raises(Hwp2mdError, match=r"truncated record at offset 6"):
        list(iter_records(data))


def test_iter_records_truncated_header() -> None:
    with pytest.raises(Hwp2mdError, match=r"truncated record at offset 0"):
        list(iter_records(b"\x43\x04"))


def test_iter_records_truncated_extended_size() -> None:
    data = _header(HWPTAG_PARA_TEXT, 0, 0xFFF) + b"\x00\x01"
    with pytest.raises(Hwp2mdError, match=r"truncated record at offset 0"):
        list(iter_records(data))


def test_decode_skips_extended_control() -> None:
    # 코드 2(구역/단 정의) + 7 WCHAR 부가 정보 = 8 WCHAR 를 건너뛴다
    ctrl = _wchars(2, ord("d"), ord("c"), ord("e"), ord("s"), 0, 0, 2)
    payload = "앞".encode("utf-16-le") + ctrl + "뒤".encode("utf-16-le") + _wchars(13)
    assert decode_para_text(payload) == "앞뒤"


def test_decode_inline_char_controls() -> None:
    payload = (
        _wchars(ord("a"), 9, 0, 0, 0, 0, 0, 0, 9)
        + _wchars(ord("b"), 24, ord("c"), 30, ord("d"), 31, ord("e"), 10, ord("f"))
        + _wchars(0, 25, 29, ord("g"), 13)
    )
    assert decode_para_text(payload) == "a b-c d e\nfg"


def test_decode_stops_at_para_end() -> None:
    payload = "본문".encode("utf-16-le") + _wchars(13) + "무시".encode("utf-16-le")
    assert decode_para_text(payload) == "본문"


def test_decode_preserves_surrogate_pair() -> None:
    payload = "웃음 \U0001f600!".encode("utf-16-le") + _wchars(13)
    assert decode_para_text(payload) == "웃음 \U0001f600!"


def test_decode_odd_length_payload() -> None:
    payload = "가나".encode("utf-16-le") + b"\x41"
    assert decode_para_text(payload) == "가나"


def test_decode_strips_whitespace_and_empty() -> None:
    assert decode_para_text(_wchars(13)) == ""
    assert decode_para_text(b"") == ""
    assert decode_para_text(_wchars(30, ord("x"), 31, 13)) == "x"
