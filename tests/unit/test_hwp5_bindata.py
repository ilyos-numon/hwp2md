import struct
from pathlib import Path
from typing import Any

import pytest

from hwp2md.blocks import Block, Image, Paragraph
from hwp2md.errors import Hwp2mdError
from hwp2md.hwp5 import records
from hwp2md.hwp5.body import parse_blocks, parse_picture_bindata_id
from hwp2md.hwp5.docinfo import BinDataEntry, DocInfo, parse_bin_data, parse_docinfo
from hwp2md.hwp5.reader import BinDataStore, read_blocks, read_hwp5_package, read_streams
from hwp2md.hwp5.records import iter_records
from hwp2md.images import normalize_ext
from synth_hwp5 import (
    EXPECTED_BLOCKS_IMAGES,
    FIXTURE_IMAGE_JPG,
    FIXTURE_IMAGE_PNG,
    FIXTURE_ITEMS_IMAGE_MISSING,
    FIXTURE_ITEMS_IMAGES,
    IMAGE_FIXTURES,
    JPEG_STUB,
    PNG_1X1,
    build_bin_data,
    build_docinfo,
    build_picture_record,
    build_section0,
    write_hwp5,
)


def test_tag_constants_match_generator() -> None:
    assert records.HWPTAG_BIN_DATA == 0x12
    assert records.HWPTAG_SHAPE_COMPONENT == 0x4C
    assert records.HWPTAG_SHAPE_COMPONENT_PICTURE == 0x55
    assert records.CTRL_ID_GSO == b" osg"


def test_parse_bin_data_embedding() -> None:
    assert parse_bin_data(build_bin_data(3, "PNG")) == BinDataEntry(1, 0, 3, "png")


def test_parse_bin_data_link_and_storage() -> None:
    link = parse_bin_data(struct.pack("<HH", 0x0000, 1) + "a".encode("utf-16-le"))
    assert (link.storage_type, link.storage_id, link.ext) == (0, 0, "")
    assert parse_bin_data(struct.pack("<HH", 0x0022, 5)) == BinDataEntry(2, 2, 5, "")


def test_parse_bin_data_truncated() -> None:
    for payload in (b"\x01", b"\x01\x00\x01", b"\x01\x00\x01\x00\x03\x00p\x00"):
        with pytest.raises(Hwp2mdError, match="truncated BIN_DATA record"):
            parse_bin_data(payload)


def test_parse_docinfo_collects_bin_data() -> None:
    info = parse_docinfo(build_docinfo(outline=True, images=[FIXTURE_IMAGE_PNG, FIXTURE_IMAGE_JPG]))
    assert len(info.bin_data) == 2
    assert [e.ext for e in info.bin_data] == ["png", "jpg"]
    assert len(info.para_shapes) == 8
    assert info.bin_data_entry(0) is None
    entry = info.bin_data_entry(1)
    assert entry is not None and entry.storage_id == 1
    assert info.bin_data_entry(3) is None


def test_parse_picture_bindata_id() -> None:
    assert parse_picture_bindata_id(build_picture_record(9)) == 9
    with pytest.raises(Hwp2mdError, match="truncated SHAPE_COMPONENT_PICTURE record"):
        parse_picture_bindata_id(b"\x00" * 72)


def test_store_resolve_compressed_and_raw(tmp_path: Path) -> None:
    for properties in (0x1, 0x0):
        _check_store(tmp_path / f"i{properties}.hwp", properties)


def _check_store(path: Path, properties: int) -> None:
    pkg = read_hwp5_package(write_hwp5(path, FIXTURE_ITEMS_IMAGES, properties=properties))
    store = BinDataStore(parse_docinfo(pkg.docinfo), pkg.bin_data, compressed=pkg.header.compressed)
    assert store.resolve(1) == Image("img_001.png", PNG_1X1)
    assert store.resolve(2) == Image("img_002.jpg", JPEG_STUB)


def test_store_resolve_missing_link_and_out_of_range(tmp_path: Path) -> None:
    pkg = read_hwp5_package(write_hwp5(tmp_path / "m.hwp", FIXTURE_ITEMS_IMAGE_MISSING))
    store = BinDataStore(parse_docinfo(pkg.docinfo), pkg.bin_data, compressed=True)
    assert store.resolve(1) is None
    assert store.resolve(2) == Image("img_001.png", PNG_1X1)
    assert store.resolve(99) is None
    link = DocInfo(para_shapes=(), bin_data=(BinDataEntry(0, 0, 0, ""),))
    assert BinDataStore(link, {}, compressed=False).resolve(1) is None


def test_store_case_insensitive_stream_name() -> None:
    info = DocInfo(para_shapes=(), bin_data=(BinDataEntry(1, 0, 1, "png"),))
    store = BinDataStore(info, {"BIN0001.PNG": PNG_1X1}, compressed=False)
    assert store.resolve(1) == Image("img_001.png", PNG_1X1)
    store2 = BinDataStore(info, {"bin0001.jpeg": JPEG_STUB}, compressed=False)
    assert normalize_ext("png", JPEG_STUB) == "png"
    assert store2.resolve(1) == Image("img_001.png", JPEG_STUB)


def test_store_inflate_fallback_to_raw() -> None:
    info = DocInfo(para_shapes=(), bin_data=(BinDataEntry(1, 0, 1, "png"),))
    store = BinDataStore(info, {"BIN0001.png": PNG_1X1}, compressed=True)
    image = store.resolve(1)
    assert image is not None and image.data == PNG_1X1


@pytest.mark.parametrize(
    ("items", "expected"),
    [(f[0], f[1]) for f in IMAGE_FIXTURES],
    ids=["images", "reuse", "in_cell", "missing"],
)
def test_read_blocks_image_fixtures(tmp_path: Path, items: Any, expected: list[Block]) -> None:
    assert read_blocks(write_hwp5(tmp_path / "doc.hwp", items)) == expected


def test_read_blocks_uncompressed_image_fixture(tmp_path: Path) -> None:
    path = write_hwp5(tmp_path / "doc.hwp", FIXTURE_ITEMS_IMAGES, properties=0)
    assert read_blocks(path) == EXPECTED_BLOCKS_IMAGES


def test_gso_without_resolver_yields_no_image() -> None:
    blocks = parse_blocks(iter_records(build_section0(FIXTURE_ITEMS_IMAGES)))
    assert len(blocks) == 3
    assert all(isinstance(b, Paragraph) for b in blocks)


def test_read_streams_wrapper_unchanged(tmp_path: Path) -> None:
    p = write_hwp5(tmp_path / "doc.hwp", FIXTURE_ITEMS_IMAGES)
    pkg = read_hwp5_package(p)
    assert read_streams(p) == (pkg.docinfo, pkg.sections)
