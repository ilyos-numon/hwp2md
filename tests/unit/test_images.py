from pathlib import Path

import hwp2md
from hwp2md.blocks import Image, Paragraph, Table
from hwp2md.convert import _write_images
from hwp2md.images import ImageNamer, image_dir_name, normalize_ext, sniff_ext
from hwp2md.render import render_blocks
from synth_hwp5 import EXPECTED_MARKDOWN, FIXTURE_PARAGRAPHS, write_hwp5

PNG_1X1: bytes = bytes.fromhex(
    "89504e470d0a1a0a0000000d4948445200000001000000010802000000907753de"
    "0000000c4944415478da63f8cfc0000003010100f70341430000000049454e44ae426082"
)
JPEG_STUB: bytes = b"\xff\xd8\xff\xe0" + bytes(range(16)) + b"\xff\xd9"


def test_image_block_equality_and_block_union() -> None:
    assert Image("a.png", b"x") == Image("a.png", b"x")
    assert Image("a.png", b"x") != Image("a.png", b"y")
    assert "Image" in hwp2md.__all__


def test_image_dir_name() -> None:
    assert image_dir_name("doc") == "doc_images"
    assert image_dir_name("브라더 공공기관 보고서 양식") == "브라더 공공기관 보고서 양식_images"


def test_sniff_ext() -> None:
    assert sniff_ext(PNG_1X1) == "png"
    assert sniff_ext(JPEG_STUB) == "jpg"
    assert sniff_ext(b"GIF89a\x01\x00") == "gif"
    assert sniff_ext(b"BM\x00\x00") == "bmp"
    assert sniff_ext(b"zzz") is None


def test_normalize_ext() -> None:
    assert normalize_ext("PNG", b"") == "png"
    assert normalize_ext(".Jpg", b"") == "jpg"
    assert normalize_ext("", PNG_1X1) == "png"
    assert normalize_ext(None, b"zzz") == "bin"
    assert normalize_ext("  ", JPEG_STUB) == "jpg"


def test_image_namer_sequence_and_reuse() -> None:
    namer = ImageNamer()
    assert namer.name_for("a", "png") == "img_001.png"
    assert namer.name_for("b", "jpg") == "img_002.jpg"
    assert namer.name_for("a", "jpg") == "img_001.png"
    assert namer.name_for("c", "bin") == "img_003.bin"


def test_render_image_with_dir() -> None:
    out = render_blocks([Image("img_001.png", b"")], image_dir="doc_images")
    assert out == "![그림 1](doc_images/img_001.png)\n"


def test_render_image_without_dir() -> None:
    assert render_blocks([Image("img_001.png", b"")]) == "![그림 1](img_001.png)\n"


def test_render_image_numbering_counts_occurrences() -> None:
    blocks = [
        Paragraph("a"),
        Image("img_001.png", b""),
        Image("img_001.png", b""),
        Image("img_002.jpg", b""),
    ]
    assert render_blocks(blocks, image_dir="doc_images") == (
        "a\n\n![그림 1](doc_images/img_001.png)\n\n"
        "![그림 2](doc_images/img_001.png)\n\n![그림 3](doc_images/img_002.jpg)\n"
    )


def test_render_image_dir_space_percent_encoded() -> None:
    out = render_blocks([Image("img_001.png", b"")], image_dir="두 단어_images")
    assert out == "![그림 1](두%20단어_images/img_001.png)\n"


def test_render_existing_blocks_unchanged() -> None:
    blocks = [Paragraph("a"), Paragraph("h", 1), Table([["x", "y"]])]
    expected = "a\n\n# h\n\n| x | y |\n|---|---|\n"
    assert render_blocks(blocks) == expected
    assert render_blocks(blocks, image_dir="doc_images") == expected


def test_write_images_dedupes_and_creates_dir(tmp_path: Path) -> None:
    d = tmp_path / "d"
    blocks = [Image("img_001.png", b"A"), Image("img_001.png", b"B"), Image("img_002.jpg", b"C")]
    files = _write_images(blocks, d)
    assert files == (d / "img_001.png", d / "img_002.jpg")
    assert (d / "img_001.png").read_bytes() == b"A"
    assert (d / "img_002.jpg").read_bytes() == b"C"


def test_write_images_no_images_no_dir(tmp_path: Path) -> None:
    assert _write_images([Paragraph("a")], tmp_path / "d") == ()
    assert not (tmp_path / "d").exists()


def test_convert_without_images_has_defaults(tmp_path: Path) -> None:
    result = hwp2md.convert(write_hwp5(tmp_path / "s.hwp", FIXTURE_PARAGRAPHS), tmp_path / "out")
    assert result.image_count == 0
    assert result.image_dir is None
    assert result.image_files == ()
    assert not (tmp_path / "out" / "s_images").exists()
    assert result.markdown == EXPECTED_MARKDOWN
