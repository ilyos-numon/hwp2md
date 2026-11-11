import io
import zipfile
from pathlib import Path

import pytest

from hwp2md import NotHwpFileError, detect_format
from synth_hwp5 import FIXTURE_PARAGRAPHS, write_hwp5
from synth_hwpx import build_zip, hwpx_entries, write_hwpx


def test_hwp5_fixture_is_hwp5(tmp_path: Path) -> None:
    src = write_hwp5(tmp_path / "sample.hwp", FIXTURE_PARAGRAPHS)
    assert detect_format(src) == "hwp5"


def test_hwpx_fixture_is_hwpx(tmp_path: Path) -> None:
    src = write_hwpx(tmp_path / "sample.hwpx", FIXTURE_PARAGRAPHS)
    assert detect_format(src) == "hwpx"


def test_hwpx_with_hwp_extension_is_hwpx(tmp_path: Path) -> None:
    src = write_hwpx(tmp_path / "disguised.hwp", FIXTURE_PARAGRAPHS)
    assert detect_format(src) == "hwpx"


def test_zip_without_mimetype_but_section0_is_hwpx(tmp_path: Path) -> None:
    entries = hwpx_entries(FIXTURE_PARAGRAPHS)
    del entries["mimetype"]
    src = tmp_path / "no_mimetype.zip"
    src.write_bytes(build_zip(entries))
    assert detect_format(src) == "hwpx"


def test_zip_other_mimetype_no_section_raises(tmp_path: Path) -> None:
    src = tmp_path / "other.zip"
    src.write_bytes(build_zip({"mimetype": b"application/zip", "a.txt": b"x"}))
    with pytest.raises(NotHwpFileError) as exc_info:
        detect_format(src)
    assert str(exc_info.value) == f"zip archive is not an HWPX package: {src}"


def test_text_file_raises(tmp_path: Path) -> None:
    src = tmp_path / "plain.hwpx"
    src.write_text("hello\n", encoding="utf-8")
    with pytest.raises(NotHwpFileError) as exc_info:
        detect_format(src)
    assert str(exc_info.value) == f"not an HWP 5.0 or HWPX file: {src}"


def test_empty_file_raises(tmp_path: Path) -> None:
    src = tmp_path / "empty.hwp"
    src.write_bytes(b"")
    with pytest.raises(NotHwpFileError) as exc_info:
        detect_format(src)
    assert str(exc_info.value) == f"not an HWP 5.0 or HWPX file: {src}"


def test_corrupt_zip_raises(tmp_path: Path) -> None:
    empty_zip = tmp_path / "empty.zip"
    empty_zip.write_bytes(b"PK\x05\x06" + b"\x00" * 18)
    with pytest.raises(NotHwpFileError) as exc_info:
        detect_format(empty_zip)
    assert str(exc_info.value) == f"zip archive is not an HWPX package: {empty_zip}"

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("a.txt", b"x")
    data = buf.getvalue()
    broken = tmp_path / "broken.zip"
    broken.write_bytes(data.replace(b"PK\x01\x02", b"XX\x01\x02"))
    with pytest.raises(NotHwpFileError) as exc_info:
        detect_format(broken)
    assert str(exc_info.value) == f"corrupt zip archive: {broken}"
