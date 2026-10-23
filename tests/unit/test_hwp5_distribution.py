import io
import struct
from pathlib import Path

import olefile
import pytest

from hwp2md import UnsupportedHwpError, convert
from hwp2md.errors import DrmProtectedError, EncryptedDocumentError
from hwp2md.hwp5.reader import read_hwp5_package
from synth_distdoc import build_hwp5_distribution
from synth_hwp5 import (
    EXPECTED_MARKDOWN,
    EXPECTED_MARKDOWN_WITH_TABLE,
    FIXTURE_ITEMS_WITH_TABLE,
    FIXTURE_PARAGRAPHS,
    build_file_header,
    build_hwp5,
    write_hwp5,
)


def _write(path: Path, data: bytes) -> Path:
    path.write_bytes(data)
    return path


def _with_properties(data: bytes, properties: int) -> bytes:
    """FileHeader 속성만 바꾼 같은 길이 CFB (FileHeader 스트림 바이트를 제자리 교체)."""
    old = olefile.OleFileIO(io.BytesIO(data)).openstream("FileHeader").read()
    assert data.count(old) == 1
    return data.replace(old, build_file_header(properties=properties))


def test_synth_distribution_has_viewtext_only() -> None:
    data = build_hwp5_distribution(FIXTURE_PARAGRAPHS)
    ole = olefile.OleFileIO(io.BytesIO(data))
    names = {"/".join(e) for e in ole.listdir()}
    header = ole.openstream("FileHeader").read()
    ole.close()
    assert "ViewText/Section0" in names
    assert not any(n.startswith("BodyText/") for n in names)
    assert struct.unpack("<I", header[36:40])[0] == 0x5


@pytest.mark.parametrize("compressed", [True, False])
@pytest.mark.parametrize(
    ("items", "expected"),
    [
        (FIXTURE_PARAGRAPHS, EXPECTED_MARKDOWN),
        (FIXTURE_ITEMS_WITH_TABLE, EXPECTED_MARKDOWN_WITH_TABLE),
    ],
    ids=["paragraphs", "table"],
)
def test_distribution_same_markdown_as_plain(
    tmp_path: Path, compressed: bool, items: list, expected: str
) -> None:
    plain_src = _write(
        tmp_path / "plain.hwp",
        build_hwp5(items, properties=0x1 if compressed else 0x0),
    )
    dist_src = _write(tmp_path / "dist.hwp", build_hwp5_distribution(items, compressed=compressed))
    plain = convert(plain_src, tmp_path / "out_plain")
    dist = convert(dist_src, tmp_path / "out_dist")
    assert plain.markdown == expected
    assert dist.markdown.encode("utf-8") == plain.markdown.encode("utf-8")
    assert dist.paragraph_count == plain.paragraph_count


def test_distribution_package_sections_decrypted(tmp_path: Path) -> None:
    src = _write(tmp_path / "dist.hwp", build_hwp5_distribution(FIXTURE_PARAGRAPHS))
    pkg = read_hwp5_package(src)
    assert pkg.header.distribution
    assert len(pkg.sections) == 1
    assert pkg.docinfo  # DocInfo 는 배포용에서도 평문(압축만)


def test_distribution_without_viewtext_rejected(tmp_path: Path) -> None:
    src = write_hwp5(tmp_path / "dist.hwp", FIXTURE_PARAGRAPHS, properties=0x5)
    with pytest.raises(UnsupportedHwpError, match="distribution document: ViewText missing"):
        convert(src, tmp_path / "out")
    assert not (tmp_path / "out" / "dist.md").exists()


@pytest.mark.parametrize(
    ("properties", "error"),
    [
        (0x7, EncryptedDocumentError),  # 암호 + 배포용 → 암호가 먼저
        (0x15, DrmProtectedError),  # DRM(bit4) + 배포용 → DRM 이 먼저
        (0x405, DrmProtectedError),  # 인증서 DRM(bit10) + 배포용
        (0x17, EncryptedDocumentError),  # 암호 + DRM + 배포용 → 암호가 먼저
    ],
)
def test_protection_bits_take_precedence(
    tmp_path: Path, properties: int, error: type[UnsupportedHwpError]
) -> None:
    data = _with_properties(build_hwp5_distribution(FIXTURE_PARAGRAPHS), properties)
    src = _write(tmp_path / "dist.hwp", data)
    with pytest.raises(error):
        convert(src, tmp_path / "out")


def test_distribution_bad_viewtext_header_rejected(tmp_path: Path) -> None:
    data = build_hwp5_distribution(FIXTURE_PARAGRAPHS)
    ole = olefile.OleFileIO(io.BytesIO(data))
    stream = ole.openstream("ViewText/Section0").read()
    ole.close()
    broken = struct.pack("<I", 0x1D | (256 << 20)) + stream[4:]
    assert data.count(stream) == 1
    src = _write(tmp_path / "dist.hwp", data.replace(stream, broken))
    with pytest.raises(UnsupportedHwpError, match="distribution document"):
        convert(src, tmp_path / "out")
