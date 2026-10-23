"""OLE objects and OOXML charts shared by the HWP 5.0 / HWPX / HWPML readers (PLAN §4-H)."""

from __future__ import annotations

import io
import struct
from collections.abc import Callable
from dataclasses import dataclass

import olefile
from lxml import etree

from .blocks import Block, Image, make_paragraph, make_table
from .images import sniff_ext
from .skips import SkipKind

ImageFactory = Callable[[str, bytes], Image]  # (고유 키, 원본 바이트) → 이름 붙은 Image
MAX_OLE_BYTES = 50 * 1024 * 1024

NS_C = "http://schemas.openxmlformats.org/drawingml/2006/chart"
NS_A = "http://schemas.openxmlformats.org/drawingml/2006/main"
_C_CHART_SPACE = f"{{{NS_C}}}chartSpace"
_C_CHART = f"{{{NS_C}}}chart"
_C_TITLE = f"{{{NS_C}}}title"
_C_PLOT_AREA = f"{{{NS_C}}}plotArea"
_C_SER = f"{{{NS_C}}}ser"
_C_TX = f"{{{NS_C}}}tx"
_C_CAT = f"{{{NS_C}}}cat"
_C_VAL = f"{{{NS_C}}}val"
_C_PT = f"{{{NS_C}}}pt"
_C_V = f"{{{NS_C}}}v"
_A_T = f"{{{NS_A}}}t"

STREAM_OOXML_CHART = "OOXMLChartContents"
STREAM_OLE10_NATIVE = "\x01Ole10Native"
STREAM_CONTENTS = "Contents"
_NATIVE_IMAGE_EXTS = frozenset({"png", "jpg", "gif", "bmp"})


@dataclass(frozen=True)
class OleOutcome:
    blocks: tuple[Block, ...]  # 차트 블록 또는 (Image,) 또는 ()
    skipped: SkipKind | None  # "chart_legacy" | "ole" | None


def unwrap_hwpx_ole(data: bytes) -> bytes:
    """앞 UINT32 LE == len(data) - 4 이면 data[4:], 아니면 data."""
    if len(data) >= 4 and struct.unpack_from("<I", data, 0)[0] == len(data) - 4:
        return data[4:]
    return data


def _make_parser() -> etree.XMLParser:
    return etree.XMLParser(resolve_entities=False, no_network=True, huge_tree=False)


def _points(parent: etree._Element | None) -> dict[int, str]:
    """parent 아래 c:pt 의 idx → c:v 문자열 그대로."""
    out: dict[int, str] = {}
    if parent is None:
        return out
    for pt in parent.iter(_C_PT):
        try:
            idx = int(pt.get("idx", ""))
        except ValueError:
            continue
        v = pt.find(_C_V)
        out[idx] = (v.text or "") if v is not None else ""
    return out


def _series_name(ser: etree._Element) -> str:
    tx = ser.find(_C_TX)
    if tx is None:
        return ""
    for v in tx.iter(_C_V):
        return (v.text or "").strip()
    return ""


def _chart_title(chart: etree._Element) -> str:
    title = chart.find(_C_TITLE)
    if title is None:
        return ""
    return "".join(t.text or "" for t in title.iter(_A_T)).strip()


def chart_xml_to_blocks(xml: bytes) -> list[Block]:
    """c:chartSpace 캐시값 → [Paragraph("차트: 제목" | "차트"), Table]. 계열 0·파싱 실패 → []."""
    try:
        root = etree.fromstring(xml, _make_parser())
    except (etree.XMLSyntaxError, ValueError):
        return []
    space = root if root.tag == _C_CHART_SPACE else next(root.iter(_C_CHART_SPACE), None)
    if space is None:
        return []
    chart = space.find(_C_CHART)
    if chart is None:
        return []
    plot = chart.find(_C_PLOT_AREA)
    series = list(plot.iter(_C_SER)) if plot is not None else []
    if not series:
        return []

    categories: dict[int, str] = {}
    for ser in series:
        categories = _points(ser.find(_C_CAT))
        if categories:
            break
    names: list[str] = []
    values: list[dict[int, str]] = []
    for k, ser in enumerate(series, start=1):
        names.append(_series_name(ser) or f"계열 {k}")
        values.append(_points(ser.find(_C_VAL)))
    indices = set(categories)
    for vals in values:
        indices.update(vals)
    row_count = max(indices) + 1 if indices else 0

    grid: list[list[list[str]]] = [[["항목"], *([name] for name in names)]]
    for i in range(row_count):
        grid.append([[categories.get(i, "")], *([vals.get(i, "")] for vals in values)])

    title = _chart_title(chart)
    para = make_paragraph([f"차트: {title}" if title else "차트"])
    blocks: list[Block] = []
    if para is not None:
        blocks.append(para)
    blocks.append(make_table(grid))
    return blocks


def _native_image(data: bytes) -> bytes | None:
    """\\x01Ole10Native = [UINT32 LE 길이][원본]. 원본이 PNG/JPEG/GIF/BMP 면 원본, 아니면 None."""
    if len(data) < 4:
        return None
    (size,) = struct.unpack_from("<I", data, 0)
    if size > len(data) - 4:
        return None
    payload = data[4 : 4 + size]
    if payload and sniff_ext(payload) in _NATIVE_IMAGE_EXTS:
        return payload
    return None


def _read_streams(cfb: bytes) -> dict[str, bytes] | None:
    """필요한 루트 스트림만 읽는다. CFB 가 아니거나 열 수 없으면 None."""
    try:
        if not olefile.isOleFile(io.BytesIO(cfb)):
            return None
        ole = olefile.OleFileIO(io.BytesIO(cfb))
        try:
            out: dict[str, bytes] = {}
            for name in (STREAM_OOXML_CHART, STREAM_OLE10_NATIVE, STREAM_CONTENTS):
                if ole.exists(name) and ole.get_type(name) == olefile.STGTY_STREAM:
                    out[name] = ole.openstream(name).read()
            return out
        finally:
            ole.close()
    except Exception:  # 손상된 CFB 는 olefile 이 여러 종류의 예외를 낸다
        return None


def ole_to_outcome(cfb: bytes, key: str, make_image: ImageFactory) -> OleOutcome:
    """OLE 개체(CFB) 하나 → 차트 블록 / 이미지 / 건너뜀 종류."""
    if len(cfb) > MAX_OLE_BYTES:
        return OleOutcome((), "ole")
    streams = _read_streams(cfb)
    if streams is None:
        return OleOutcome((), "ole")
    chart_xml = streams.get(STREAM_OOXML_CHART)
    if chart_xml is not None:
        blocks = chart_xml_to_blocks(chart_xml)
        if not blocks:
            return OleOutcome((), "chart_legacy")
        return OleOutcome(tuple(blocks), None)
    native = streams.get(STREAM_OLE10_NATIVE)
    if native is not None:
        payload = _native_image(native)
        if payload is not None:
            return OleOutcome((make_image(key, payload),), None)
    if STREAM_CONTENTS in streams:
        return OleOutcome((), "chart_legacy")
    return OleOutcome((), "ole")
