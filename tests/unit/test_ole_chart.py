import struct
from pathlib import Path

import pytest

from hwp2md import ole
from hwp2md.blocks import Image, Paragraph, Table
from hwp2md.ole import OleOutcome, chart_xml_to_blocks, ole_to_outcome, unwrap_hwpx_ole
from hwp2md.render import render_blocks
from synth_hwp5 import JPEG_STUB, PNG_1X1
from synth_ole import NS_A, NS_C, build_ole_cfb, chart_xml, hwpx_ole_entry, ole10_native

BAR = chart_xml("실적", ["1월", "2월"], [("매출", ["10", "20"])])


class _Factory:
    def __init__(self) -> None:
        self.calls: list[tuple[str, bytes]] = []

    def __call__(self, key: str, data: bytes) -> Image:
        self.calls.append((key, data))
        return Image(f"img_{len(self.calls):03d}.png", data)


def _no_image(key: str, data: bytes) -> Image:
    raise AssertionError("make_image must not be called")


# --- chart_xml_to_blocks ---


def test_bar_chart_blocks_and_markdown() -> None:
    blocks = chart_xml_to_blocks(BAR)
    assert blocks == [
        Paragraph("차트: 실적"),
        Table([["항목", "매출"], ["1월", "10"], ["2월", "20"]]),
    ]
    assert render_blocks(blocks) == (
        "차트: 실적\n\n| 항목 | 매출 |\n|---|---|\n| 1월 | 10 |\n| 2월 | 20 |\n"
    )


def test_chart_without_title() -> None:
    blocks = chart_xml_to_blocks(chart_xml("", ["가"], [("값", ["1"])]))
    assert blocks == [Paragraph("차트"), Table([["항목", "값"], ["가", "1"]])]


def test_chart_two_series_and_unnamed_series() -> None:
    xml = chart_xml(
        "분기",
        ["1분기", "2분기", "3분기"],
        [("매출", ["10", "20.5", "30"]), ("", ["1", "2", "3"])],
    )
    assert chart_xml_to_blocks(xml) == [
        Paragraph("차트: 분기"),
        Table(
            [
                ["항목", "매출", "계열 2"],
                ["1분기", "10", "1"],
                ["2분기", "20.5", "2"],
                ["3분기", "30", "3"],
            ]
        ),
    ]


def test_chart_no_series_or_broken_xml_is_empty() -> None:
    assert chart_xml_to_blocks(chart_xml("빈", ["1월"], [])) == []
    assert chart_xml_to_blocks(b"<c:chartSpace") == []
    assert chart_xml_to_blocks(b"") == []
    assert chart_xml_to_blocks(b"<root/>") == []


def test_chart_xxe_entity_not_resolved(tmp_path: Path) -> None:
    secret = tmp_path / "secret.txt"
    secret.write_text("SECRET-VALUE", encoding="utf-8")
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f'<!DOCTYPE c:chartSpace [<!ENTITY xxe SYSTEM "{secret.as_uri()}">]>'
        f'<c:chartSpace xmlns:c="{NS_C}" xmlns:a="{NS_A}"><c:chart>'
        "<c:title><c:tx><c:rich><a:p><a:r><a:t>제목&xxe;</a:t></a:r></a:p></c:rich></c:tx>"
        "</c:title><c:plotArea><c:barChart><c:ser>"
        '<c:tx><c:strRef><c:strCache><c:pt idx="0"><c:v>&xxe;</c:v></c:pt></c:strCache>'
        "</c:strRef></c:tx>"
        '<c:cat><c:strRef><c:strCache><c:pt idx="0"><c:v>가</c:v></c:pt></c:strCache>'
        "</c:strRef></c:cat>"
        '<c:val><c:numRef><c:numCache><c:pt idx="0"><c:v>1&xxe;</c:v></c:pt></c:numCache>'
        "</c:numRef></c:val>"
        "</c:ser></c:barChart></c:plotArea></c:chart></c:chartSpace>"
    ).encode()
    blocks = chart_xml_to_blocks(xml)
    assert blocks, "chart with unresolved entity still parses"
    assert "SECRET-VALUE" not in render_blocks(blocks)
    assert blocks[0] == Paragraph("차트: 제목")


# --- unwrap_hwpx_ole ---


def test_unwrap_strips_matching_length_prefix() -> None:
    cfb = build_ole_cfb({"Contents": b"x"})
    assert unwrap_hwpx_ole(hwpx_ole_entry(cfb)) == cfb


def test_unwrap_keeps_data_without_matching_prefix() -> None:
    cfb = build_ole_cfb({"Contents": b"x"})
    assert unwrap_hwpx_ole(cfb) == cfb
    wrong = struct.pack("<I", len(cfb) + 1) + cfb
    assert unwrap_hwpx_ole(wrong) == wrong
    assert unwrap_hwpx_ole(b"\x00\x00") == b"\x00\x00"


# --- ole_to_outcome ---


def test_ooxml_chart_stream() -> None:
    cfb = build_ole_cfb({"OOXMLChartContents": BAR, "Contents": b"legacy"})
    outcome = ole_to_outcome(cfb, "BIN0001", _no_image)
    assert outcome == OleOutcome(tuple(chart_xml_to_blocks(BAR)), None)


def test_ooxml_chart_without_series_is_chart_legacy() -> None:
    cfb = build_ole_cfb({"OOXMLChartContents": chart_xml("t", ["a"], [])})
    assert ole_to_outcome(cfb, "k", _no_image) == OleOutcome((), "chart_legacy")


def test_contents_only_is_chart_legacy() -> None:
    cfb = build_ole_cfb({"Contents": b"\x00" * 100})
    assert ole_to_outcome(cfb, "k", _no_image) == OleOutcome((), "chart_legacy")


def test_ole10native_png_becomes_image() -> None:
    factory = _Factory()
    cfb = build_ole_cfb({"\x01Ole10Native": ole10_native(PNG_1X1), "Contents": b"c"})
    outcome = ole_to_outcome(cfb, "BIN0003", factory)
    assert factory.calls == [("BIN0003", PNG_1X1)]
    assert outcome == OleOutcome((Image("img_001.png", PNG_1X1),), None)


def test_ole10native_jpeg_becomes_image() -> None:
    factory = _Factory()
    cfb = build_ole_cfb({"\x01Ole10Native": ole10_native(JPEG_STUB)})
    outcome = ole_to_outcome(cfb, "k", factory)
    assert factory.calls == [("k", JPEG_STUB)]
    assert outcome.skipped is None and len(outcome.blocks) == 1


def test_ole10native_non_image_is_ole() -> None:
    cfb = build_ole_cfb({"\x01Ole10Native": ole10_native(b"PK\x03\x04 not an image")})
    assert ole_to_outcome(cfb, "k", _no_image) == OleOutcome((), "ole")


def test_ole10native_bad_length_is_ole() -> None:
    bad = struct.pack("<I", len(PNG_1X1) + 10) + PNG_1X1
    cfb = build_ole_cfb({"\x01Ole10Native": bad})
    assert ole_to_outcome(cfb, "k", _no_image) == OleOutcome((), "ole")


def test_other_streams_is_ole() -> None:
    cfb = build_ole_cfb({"\x01CompObj": b"comp", "Package": b"data"})
    assert ole_to_outcome(cfb, "k", _no_image) == OleOutcome((), "ole")


@pytest.mark.parametrize(
    "data",
    [b"", b"not a cfb at all", b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" + b"\x00" * 600],
)
def test_not_cfb_or_broken_is_ole(data: bytes) -> None:
    assert ole_to_outcome(data, "k", _no_image) == OleOutcome((), "ole")


def test_hwpx_prefixed_entry_is_not_cfb_until_unwrapped() -> None:
    cfb = build_ole_cfb({"OOXMLChartContents": BAR})
    entry = hwpx_ole_entry(cfb)
    assert ole_to_outcome(entry, "k", _no_image) == OleOutcome((), "ole")
    assert ole_to_outcome(unwrap_hwpx_ole(entry), "k", _no_image).skipped is None


def test_over_max_ole_bytes_is_ole(monkeypatch: pytest.MonkeyPatch) -> None:
    cfb = build_ole_cfb({"OOXMLChartContents": BAR})
    monkeypatch.setattr(ole, "MAX_OLE_BYTES", len(cfb) - 1)
    assert ole_to_outcome(cfb, "k", _no_image) == OleOutcome((), "ole")
    monkeypatch.setattr(ole, "MAX_OLE_BYTES", len(cfb))
    assert ole_to_outcome(cfb, "k", _no_image).skipped is None


def test_max_ole_bytes_constant() -> None:
    assert ole.MAX_OLE_BYTES == 50 * 1024 * 1024
