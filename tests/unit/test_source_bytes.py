import builtins
import io
from pathlib import Path
from typing import Any

import pytest

from hwp2md import NotHwpFileError, detect_format
from hwp2md.hwp5 import reader as hwp5_reader
from hwp2md.hwpx import reader as hwpx_reader
from hwp2md.source import MEMORY_LABEL, as_binary_io, source_label
from synth_hwp5 import FIXTURE_PARAGRAPHS, write_hwp5
from synth_hwpx import write_hwpx

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
HWP5_SAMPLES = sorted(FIXTURES.glob("*.hwp"))
HWPX_SAMPLES = sorted((FIXTURES / "hwpx").glob("*.hwpx"))
SAMPLES = [(p, "hwp5") for p in HWP5_SAMPLES] + [(p, "hwpx") for p in HWPX_SAMPLES]
SAMPLE_IDS = [p.name for p, _ in SAMPLES]


def _reader_for(fmt: str) -> Any:
    return hwp5_reader if fmt == "hwp5" else hwpx_reader


def test_sample_counts() -> None:
    assert len(HWP5_SAMPLES) == 2
    assert len(HWPX_SAMPLES) == 3


@pytest.mark.parametrize(("path", "fmt"), SAMPLES, ids=SAMPLE_IDS)
def test_read_blocks_bytes_equals_path(path: Path, fmt: str) -> None:
    reader = _reader_for(fmt)
    from_path = reader.read_blocks(path)
    assert from_path
    assert reader.read_blocks(path.read_bytes()) == from_path


@pytest.mark.parametrize(("path", "fmt"), SAMPLES, ids=SAMPLE_IDS)
def test_detect_format_bytes(path: Path, fmt: str) -> None:
    assert detect_format(path.read_bytes()) == fmt
    assert detect_format(path) == fmt


def test_source_label() -> None:
    assert source_label(b"abc") == MEMORY_LABEL == "<memory>"
    assert source_label(Path("a/b.hwp")) == str(Path("a/b.hwp"))


def test_as_binary_io() -> None:
    wrapped = as_binary_io(b"abc")
    assert isinstance(wrapped, io.BytesIO)
    assert wrapped.read() == b"abc"
    assert as_binary_io(Path("a/b.hwp")) == str(Path("a/b.hwp"))


def test_short_bytes_never_opened_as_path(monkeypatch: pytest.MonkeyPatch) -> None:
    data = b"x" * 100
    calls: list[Any] = []
    real_open = builtins.open

    def spy_open(file: Any, *args: Any, **kwargs: Any) -> Any:
        calls.append(file)
        return real_open(file, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", spy_open)
    with pytest.raises(NotHwpFileError) as exc_info:
        detect_format(data)
    with pytest.raises(NotHwpFileError):
        hwp5_reader.read_blocks(data)
    with pytest.raises(NotHwpFileError):
        hwpx_reader.read_blocks(data)
    monkeypatch.setattr(builtins, "open", real_open)
    assert str(exc_info.value) == f"not an HWP 5.0 or HWPX file: {MEMORY_LABEL}"
    assert calls == []


def test_corrupt_zip_bytes_raises_with_memory_label() -> None:
    data = b"PK\x03\x04" + b"\0" * 200
    with pytest.raises(NotHwpFileError) as exc_info:
        detect_format(data)
    assert MEMORY_LABEL in str(exc_info.value)
    with pytest.raises(NotHwpFileError) as exc_info:
        hwpx_reader.read_blocks(data)
    assert str(exc_info.value) == f"not a zip archive: {MEMORY_LABEL}"


def test_path_error_message_unchanged(tmp_path: Path) -> None:
    src = tmp_path / "plain.hwp"
    src.write_text("hello\n", encoding="utf-8")
    with pytest.raises(NotHwpFileError) as exc_info:
        detect_format(src)
    assert str(exc_info.value) == f"not an HWP 5.0 or HWPX file: {src}"
    with pytest.raises(NotHwpFileError) as exc_info:
        hwp5_reader.read_hwp5_package(src)
    assert str(exc_info.value) == f"not an OLE compound file: {src}"
    with pytest.raises(NotHwpFileError) as exc_info:
        hwpx_reader.read_hwpx_package(src)
    assert str(exc_info.value) == f"not a zip archive: {src}"


def test_hwp5_bytes_error_uses_memory_label() -> None:
    with pytest.raises(NotHwpFileError) as exc_info:
        hwp5_reader.read_hwp5_package(b"not ole at all")
    assert str(exc_info.value) == f"not an OLE compound file: {MEMORY_LABEL}"


def test_synth_hwp5_bytes(tmp_path: Path) -> None:
    src = write_hwp5(tmp_path / "sample.hwp", FIXTURE_PARAGRAPHS)
    data = src.read_bytes()
    assert detect_format(data) == "hwp5"
    assert hwp5_reader.read_paragraphs(data) == hwp5_reader.read_paragraphs(src)
    assert hwp5_reader.read_streams(data) == hwp5_reader.read_streams(src)


def test_synth_hwpx_bytes(tmp_path: Path) -> None:
    src = write_hwpx(tmp_path / "sample.hwpx", FIXTURE_PARAGRAPHS)
    data = src.read_bytes()
    assert detect_format(data) == "hwpx"
    assert hwpx_reader.read_package(data) == hwpx_reader.read_package(src)
    assert hwpx_reader.read_blocks(data) == hwpx_reader.read_blocks(src)
