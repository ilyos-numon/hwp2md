import base64
import builtins
import io
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any

import pytest

import hwp2md
from hwp2md import MemoryResult, convert, convert_bytes, memory
from hwp2md.errors import (
    EmptyInputError,
    Hwp2mdError,
    InputTooLargeError,
    NotHwpFileError,
    UnsupportedHwpError,
)
from hwp2md.memory import (
    MAX_INPUT_BYTES,
    STATUS_BY_CODE,
    MemoryImage,
    build_zip,
    convert_to_response,
    error_code,
    markdown_with_data_uris,
    safe_stem,
    to_payload,
)
from synth_hwp5 import FIXTURE_PARAGRAPHS, write_hwp5

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
SAMPLES = sorted(FIXTURES.glob("*.hwp")) + sorted((FIXTURES / "hwpx").glob("*.hwpx"))
SAMPLE_IDS = [p.name for p in SAMPLES]
BROTHER = next(p for p in SAMPLES if p.name.startswith("브라더"))


def _synth_bytes(tmp_path: Path, **kwargs: Any) -> bytes:
    return write_hwp5(tmp_path / "sample.hwp", FIXTURE_PARAGRAPHS, **kwargs).read_bytes()


def test_sample_count() -> None:
    assert len(SAMPLES) == 5


def test_constants() -> None:
    assert MAX_INPUT_BYTES == 52428800
    assert STATUS_BY_CODE == {
        "empty": 400,
        "too_large": 413,
        "not_hwp": 415,
        "unsupported": 415,
        "convert_failed": 422,
    }


def test_package_exports() -> None:
    assert hwp2md.convert_bytes is convert_bytes
    assert hwp2md.MemoryResult is MemoryResult
    assert "convert_bytes" in hwp2md.__all__
    assert "MemoryResult" in hwp2md.__all__
    assert hwp2md.__all__ == sorted(hwp2md.__all__)


def test_new_errors_are_hwp2md_errors() -> None:
    assert issubclass(EmptyInputError, Hwp2mdError)
    assert issubclass(InputTooLargeError, Hwp2mdError)


@pytest.mark.parametrize("path", SAMPLES, ids=SAMPLE_IDS)
def test_same_as_convert(path: Path, tmp_path: Path) -> None:
    disk = convert(path, tmp_path)
    mem = convert_bytes(path.read_bytes(), path.name)
    assert mem.stem == path.stem
    assert mem.image_dir == f"{path.stem}_images"
    assert mem.markdown.encode("utf-8") == disk.output.read_bytes()
    assert mem.markdown == disk.markdown
    assert (mem.paragraph_count, mem.table_count, mem.heading_count, mem.image_count) == (
        disk.paragraph_count,
        disk.table_count,
        disk.heading_count,
        disk.image_count,
    )
    assert [i.file_name for i in mem.images] == [f.name for f in disk.image_files]
    assert [i.data for i in mem.images] == [f.read_bytes() for f in disk.image_files]


def test_brother_image() -> None:
    result = convert_bytes(BROTHER.read_bytes(), BROTHER.name)
    assert len(result.images) == 1
    img = result.images[0]
    assert len(img.data) == 46249
    assert img.mime == "image/png"


@pytest.mark.parametrize(
    ("name", "mime"),
    [
        ("img_001.png", "image/png"),
        ("img_001.jpg", "image/jpeg"),
        ("img_001.JPEG", "image/jpeg"),
        ("img_001.gif", "image/gif"),
        ("img_001.bmp", "image/bmp"),
        ("img_001.bin", "application/octet-stream"),
        ("img_001.wmf", "application/octet-stream"),
    ],
)
def test_image_mime(name: str, mime: str) -> None:
    assert MemoryImage(file_name=name, data=b"").mime == mime


def _block_disk_writes(monkeypatch: pytest.MonkeyPatch) -> None:
    real_open = builtins.open

    def guarded_open(file: Any, mode: str = "r", *args: Any, **kwargs: Any) -> Any:
        if any(c in mode for c in "wax+"):
            raise AssertionError(f"disk write: {file!r} mode={mode}")
        return real_open(file, mode, *args, **kwargs)

    def forbid(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("disk write attempted")

    monkeypatch.setattr(builtins, "open", guarded_open)
    monkeypatch.setattr(Path, "write_bytes", forbid)
    monkeypatch.setattr(Path, "write_text", forbid)
    for name in ("mkstemp", "mkdtemp", "NamedTemporaryFile", "TemporaryDirectory"):
        monkeypatch.setattr(tempfile, name, forbid)


@pytest.mark.parametrize("path", SAMPLES, ids=SAMPLE_IDS)
def test_no_disk_writes(path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    data = path.read_bytes()
    _block_disk_writes(monkeypatch)
    with pytest.raises(AssertionError):
        Path("x").write_bytes(b"")  # guard is active
    result = convert_bytes(data, path.name)
    assert build_zip(result)
    assert to_payload(result)["name"] == path.stem


def test_zip_matches_disk_output(tmp_path: Path) -> None:
    disk = convert(BROTHER, tmp_path)
    result = convert_bytes(BROTHER.read_bytes(), BROTHER.name)
    with zipfile.ZipFile(io.BytesIO(build_zip(result))) as zf:
        infos = zf.infolist()
        names = [i.filename for i in infos]
        assert names == [f"{BROTHER.stem}.md", f"{BROTHER.stem}_images/img_001.png"]
        assert all(i.date_time == (1980, 1, 1, 0, 0, 0) for i in infos)
        assert all(i.compress_type == zipfile.ZIP_DEFLATED for i in infos)
        assert zf.read(names[0]) == disk.output.read_bytes()
        assert zf.read(names[1]) == disk.image_files[0].read_bytes()


def test_zip_is_deterministic() -> None:
    result = convert_bytes(BROTHER.read_bytes(), BROTHER.name)
    assert build_zip(result) == build_zip(result)


def test_no_image_document(tmp_path: Path) -> None:
    result = convert_bytes(_synth_bytes(tmp_path), "sample.hwp")
    assert result.images == ()
    assert result.image_count == 0
    assert result.image_dir == "sample_images"
    assert markdown_with_data_uris(result) == result.markdown
    with zipfile.ZipFile(io.BytesIO(build_zip(result))) as zf:
        assert zf.namelist() == ["sample.md"]
        assert zf.read("sample.md") == result.markdown.encode("utf-8")


def test_markdown_with_data_uris() -> None:
    result = convert_bytes(BROTHER.read_bytes(), BROTHER.name)
    link = f"]({result.image_dir.replace(' ', '%20')}/img_001.png)"
    assert link in result.markdown
    preview = markdown_with_data_uris(result)
    assert link not in preview
    b64 = base64.b64encode(result.images[0].data).decode("ascii")
    assert f"](data:image/png;base64,{b64})" in preview


def test_markdown_with_data_uris_handles_spaces() -> None:
    img = MemoryImage(file_name="img_001.gif", data=b"GIF89a")
    result = MemoryResult(
        stem="a b",
        markdown="![그림 1](a%20b_images/img_001.gif)\n",
        image_dir="a b_images",
        images=(img,),
        paragraph_count=0,
        table_count=0,
        heading_count=0,
        image_count=1,
    )
    b64 = base64.b64encode(b"GIF89a").decode("ascii")
    assert markdown_with_data_uris(result) == f"![그림 1](data:image/gif;base64,{b64})\n"


def test_to_payload_shape() -> None:
    result = convert_bytes(BROTHER.read_bytes(), BROTHER.name)
    payload = to_payload(result)
    assert set(payload) == {"name", "markdown", "preview_markdown", "image_dir", "images", "counts"}
    assert payload["name"] == BROTHER.stem
    assert payload["markdown"] == result.markdown
    assert payload["preview_markdown"] == markdown_with_data_uris(result)
    assert payload["image_dir"] == result.image_dir
    assert payload["images"] == [{"file_name": "img_001.png", "mime": "image/png", "size": 46249}]
    assert payload["counts"] == {
        "paragraphs": result.paragraph_count,
        "tables": result.table_count,
        "headings": result.heading_count,
        "images": result.image_count,
    }


@pytest.mark.parametrize(
    ("filename", "stem"),
    [
        ("a/b/c.hwp", "c"),
        ("C:\\x\\y.hwpx", "y"),
        ("", "document"),
        (".", "document"),
        ("..", "document"),
        ("a/..", "document"),
        ("a.b.hwp", "a.b"),
        ("  보고서 .hwp", "보고서"),
        ("dir/", "document"),
    ],
)
def test_safe_stem(filename: str, stem: str) -> None:
    assert safe_stem(filename) == stem


def test_default_filename(tmp_path: Path) -> None:
    result = convert_bytes(_synth_bytes(tmp_path))
    assert result.stem == "document"


def test_empty_input_raises() -> None:
    with pytest.raises(EmptyInputError):
        convert_bytes(b"", "x.hwp")


def test_too_large_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(memory, "MAX_INPUT_BYTES", 10)
    with pytest.raises(InputTooLargeError):
        convert_bytes(b"x" * 11, "x.hwp")


def test_reader_errors_propagate(tmp_path: Path) -> None:
    with pytest.raises(NotHwpFileError):
        convert_bytes(b"plain text", "x.hwp")
    with pytest.raises(UnsupportedHwpError):
        convert_bytes(_synth_bytes(tmp_path, properties=0x3), "x.hwp")


@pytest.mark.parametrize(
    ("exc", "code"),
    [
        (EmptyInputError("e"), "empty"),
        (InputTooLargeError("e"), "too_large"),
        (NotHwpFileError("e"), "not_hwp"),
        (UnsupportedHwpError("e"), "unsupported"),
        (Hwp2mdError("e"), "convert_failed"),
        (ValueError("e"), "convert_failed"),
        (KeyError("e"), "convert_failed"),
    ],
)
def test_error_code(exc: BaseException, code: str) -> None:
    assert error_code(exc) == code


def _raise_value_error(_data: bytes) -> Any:
    raise ValueError("broken record")


@pytest.mark.parametrize(
    ("case", "status", "code"),
    [
        ("empty", 400, "empty"),
        ("too_large", 413, "too_large"),
        ("not_hwp", 415, "not_hwp"),
        ("unsupported", 415, "unsupported"),
        ("convert_failed", 422, "convert_failed"),
    ],
)
def test_convert_to_response_errors(
    case: str, status: int, code: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    data = _synth_bytes(tmp_path)
    if case == "empty":
        data = b""
    elif case == "too_large":
        monkeypatch.setattr(memory, "MAX_INPUT_BYTES", 10)
    elif case == "not_hwp":
        data = b"plain text"
    elif case == "unsupported":
        data = _synth_bytes(tmp_path, properties=0x3)
    else:
        monkeypatch.setattr(memory, "read_blocks", _raise_value_error)
    got_status, body = convert_to_response(data, "x.hwp")
    assert got_status == status
    assert body["error"]["code"] == code
    assert isinstance(body["error"]["message"], str)
    assert set(body) == {"error"}


def test_convert_to_response_success() -> None:
    status, body = convert_to_response(BROTHER.read_bytes(), BROTHER.name)
    assert status == 200
    assert body == to_payload(convert_bytes(BROTHER.read_bytes(), BROTHER.name))


def test_import_without_web_extras() -> None:
    code = (
        "import sys\n"
        "sys.modules['starlette'] = None\n"
        "sys.modules['uvicorn'] = None\n"
        "import hwp2md, hwp2md.memory\n"
        "from pathlib import Path\n"
        f"r = hwp2md.convert_bytes(Path({str(BROTHER)!r}).read_bytes(), 'b.hwpx')\n"
        "assert r.images\n"
        "print('hwp2md.web' in sys.modules)\n"
    )
    proc = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, check=False, timeout=120
    )
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.strip() == "False"
