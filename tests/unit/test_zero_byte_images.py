"""본체를 찾았지만 해석 결과가 0바이트인 그림 → 빈 파일 대신 image_missing 건너뜀."""

import base64
import zlib
from collections.abc import Callable
from pathlib import Path

import pytest
from lxml import etree

from hwp2md import convert
from hwp2md.convert import ConvertResult
from hwp2md.hwpml.reader import BinDataStore as MlBinDataStore
from hwp2md.hwpx.bindata import BinItemStore
from hwp2md.ole import STREAM_OLE10_NATIVE, ole_to_outcome
from hwp2md.skips import SkipCounter
from synth_hwp5 import PNG_1X1, SynthImage, write_hwp5
from synth_hwpml import write_hwpml
from synth_hwpx import write_hwpx
from synth_ole import build_ole_cfb, ole10_native

EMPTY = SynthImage(b"", "bmp")
GOOD = SynthImage(PNG_1X1, "png")
ITEMS: list[object] = ["앞", EMPTY, "가운데", GOOD, "뒤"]

_WRITERS: dict[str, Callable[[Path], Path]] = {
    "hwp_compressed": lambda p: write_hwp5(p / "doc.hwp", ITEMS, properties=0x1),  # type: ignore[arg-type]
    "hwp_plain": lambda p: write_hwp5(p / "doc.hwp", ITEMS, properties=0x0),  # type: ignore[arg-type]
    "hwpx": lambda p: write_hwpx(p / "doc.hwpx", ITEMS),  # type: ignore[arg-type]
    "hml": lambda p: write_hwpml(p / "doc.hml", ITEMS),  # type: ignore[arg-type]
}


def _check(result: ConvertResult) -> None:
    assert result.image_count == 1
    assert [p.name for p in result.image_files] == ["img_001.png"]
    assert [p.read_bytes() for p in result.image_files] == [PNG_1X1]
    assert result.image_dir is not None
    assert [p.name for p in result.image_dir.iterdir()] == ["img_001.png"]
    assert dict(result.skipped).get("image_missing") == 1
    assert "img_001.png" in result.markdown
    assert ".bmp" not in result.markdown


@pytest.mark.parametrize("kind", list(_WRITERS))
def test_zero_byte_picture_is_image_missing(tmp_path: Path, kind: str) -> None:
    src = _WRITERS[kind](tmp_path / "src")
    _check(convert(src, tmp_path / "out"))


def test_hwpx_store_zero_byte_entry_is_none() -> None:
    store = BinItemStore({"image1": "BinData/image1.bmp"}, {"BinData/image1.bmp": b""})
    assert store.resolve("image1") is None


def _ml_root(b64: str) -> etree._Element:
    xml = (
        "<HWPML><HEAD><MAPPINGTABLE><BINDATALIST>"
        '<BINITEM Type="Embedding" BinData="1" Format="bmp"/>'
        "</BINDATALIST></MAPPINGTABLE></HEAD>"
        f'<TAIL><BINDATASTORAGE><BINDATA Id="1" Encoding="Base64">{b64}</BINDATA>'
        "</BINDATASTORAGE></TAIL></HWPML>"
    )
    return etree.fromstring(xml.encode())


def test_hwpml_raw_deflated_empty_bindata_is_none() -> None:
    comp = zlib.compressobj(9, zlib.DEFLATED, -15)
    b64 = base64.b64encode(comp.compress(b"") + comp.flush()).decode()
    skips = SkipCounter()
    assert MlBinDataStore(_ml_root(b64), skips).resolve("1") is None


def test_ole10native_zero_byte_payload_is_ole() -> None:
    cfb = build_ole_cfb({STREAM_OLE10_NATIVE: ole10_native(b"")})
    made: list[str] = []

    def make(key: str, data: bytes) -> object:
        made.append(key)
        raise AssertionError("must not make image")

    outcome = ole_to_outcome(cfb, "1", make)  # type: ignore[arg-type]
    assert outcome.blocks == ()
    assert outcome.skipped == "ole"
    assert made == []
