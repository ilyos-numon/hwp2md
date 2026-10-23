import builtins
import io
import socket
import tempfile
import urllib.parse
import zipfile
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from starlette.testclient import TestClient

import hwp2md
from hwp2md import convert_bytes, memory
from hwp2md.web import app as web_app
from hwp2md.web import server
from hwp2md.web.app import STATIC_DIR, build_runtime_zip, create_app

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
HWP5 = FIXTURES / "form200005063113.hwp"
BROTHER = next((FIXTURES / "hwpx").glob("브라더*.hwpx"))
OCTET = {"Content-Type": "application/octet-stream"}


@pytest.fixture(scope="module")
def client() -> Iterator[TestClient]:
    with TestClient(create_app()) as c:
        yield c


def _post(client: TestClient, path: str, data: bytes, name: str | None) -> Any:
    params = {"name": name} if name is not None else None
    return client.post(path, content=data, params=params, headers=OCTET)


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


def test_health(client: TestClient) -> None:
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json() == {"ok": True, "version": hwp2md.__version__}


def test_index_html(client: TestClient) -> None:
    res = client.get("/")
    assert res.status_code == 200
    assert res.headers["content-type"].startswith("text/html")
    assert res.content == (STATIC_DIR / "index.html").read_bytes()


def test_static_files(client: TestClient) -> None:
    res = client.get("/static/index.html")
    assert res.status_code == 200
    assert client.get("/static/does-not-exist.js").status_code == 404


def test_convert_hwp5(client: TestClient) -> None:
    data = HWP5.read_bytes()
    res = _post(client, "/api/convert", data, HWP5.name)
    assert res.status_code == 200
    assert res.headers["content-type"].startswith("application/json")
    body = res.json()
    expected = convert_bytes(data, HWP5.name)
    assert body["name"] == HWP5.stem
    assert body["markdown"] == expected.markdown
    assert body["counts"]["paragraphs"] == expected.paragraph_count


def test_convert_hwpx_with_image(client: TestClient) -> None:
    data = BROTHER.read_bytes()
    res = _post(client, "/api/convert", data, BROTHER.name)
    assert res.status_code == 200
    body = res.json()
    assert body["markdown"] == convert_bytes(data, BROTHER.name).markdown
    assert "data:image/png;base64," in body["preview_markdown"]
    assert body["images"] and body["images"][0]["mime"] == "image/png"


def test_convert_korean_name_and_raw_utf8(client: TestClient) -> None:
    name = "보고서 양식.hwpx"
    url = "/api/convert?name=" + urllib.parse.quote(name)
    res = client.post(url, content=BROTHER.read_bytes(), headers=OCTET)
    assert res.status_code == 200
    assert res.json()["name"] == "보고서 양식"
    assert res.json()["image_dir"] == "보고서 양식_images"
    assert "보고서 양식".encode() in res.content  # ensure_ascii=False


def test_convert_default_name(client: TestClient) -> None:
    res = _post(client, "/api/convert", HWP5.read_bytes(), None)
    assert res.status_code == 200
    assert res.json()["name"] == "document"


def test_convert_not_hwp(client: TestClient) -> None:
    res = _post(client, "/api/convert", b"plain text, not a document", "a.hwp")
    assert res.status_code == 415
    assert res.json()["error"]["code"] == "not_hwp"
    assert res.json()["error"]["message"]


def test_convert_empty(client: TestClient) -> None:
    res = _post(client, "/api/convert", b"", "a.hwp")
    assert res.status_code == 400
    assert res.json()["error"]["code"] == "empty"


def test_convert_too_large_by_header(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(memory, "MAX_INPUT_BYTES", 10)

    def must_not_run(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("body should not be converted")

    monkeypatch.setattr(memory, "convert_to_response", must_not_run)
    monkeypatch.setattr(memory, "convert_bytes", must_not_run)
    for path in ("/api/convert", "/api/zip"):
        res = _post(client, path, b"x" * 11, "a.hwp")
        assert res.status_code == 413
        assert res.json() == {"error": {"code": "too_large", "message": "input exceeds 10 bytes"}}


def test_convert_too_large_without_header(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(memory, "MAX_INPUT_BYTES", 10)

    def chunks() -> Iterator[bytes]:
        yield b"x" * 6
        yield b"x" * 6

    res = client.post("/api/convert", content=chunks(), headers=OCTET)
    assert res.status_code == 413
    assert res.json()["error"]["code"] == "too_large"


def test_zip_ok(client: TestClient) -> None:
    data = BROTHER.read_bytes()
    res = _post(client, "/api/zip", data, BROTHER.name)
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/zip"
    expected_name = urllib.parse.quote(BROTHER.stem + ".zip")
    assert res.headers["content-disposition"] == (f"attachment; filename*=UTF-8''{expected_name}")
    result = convert_bytes(data, BROTHER.name)
    names = zipfile.ZipFile(io.BytesIO(res.content)).namelist()
    assert names[0] == f"{BROTHER.stem}.md"
    assert f"{result.image_dir}/{result.images[0].file_name}" in names
    assert res.content == memory.build_zip(result)


def test_zip_not_hwp(client: TestClient) -> None:
    res = _post(client, "/api/zip", b"plain text, not a document", "a.hwp")
    assert res.status_code == 415
    assert res.headers["content-type"].startswith("application/json")
    assert res.json()["error"]["code"] == "not_hwp"


def test_zip_empty(client: TestClient) -> None:
    res = _post(client, "/api/zip", b"", "a.hwp")
    assert res.status_code == 400
    assert res.json()["error"]["code"] == "empty"


def test_runtime_package_zip(client: TestClient) -> None:
    res = client.get("/pkg/hwp2md.zip")
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/zip"
    assert res.headers["cache-control"] == "no-store"
    zf = zipfile.ZipFile(io.BytesIO(res.content))
    names = zf.namelist()
    for required in (
        "hwp2md/__init__.py",
        "hwp2md/memory.py",
        "hwp2md/hwpx/reader.py",
        "hwp2md/py.typed",
        "olefile/__init__.py",
    ):
        assert required in names
    assert not [n for n in names if n.startswith("hwp2md/web/")]
    assert not [n for n in names if "__pycache__" in n]
    assert all(info.date_time == (1980, 1, 1, 0, 0, 0) for info in zf.infolist())


def test_runtime_zip_deterministic() -> None:
    assert build_runtime_zip() == build_runtime_zip()


def test_no_disk_writes(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    data = BROTHER.read_bytes()
    _block_disk_writes(monkeypatch)
    with pytest.raises(AssertionError):
        Path("x").write_bytes(b"")  # guard is active
    assert _post(client, "/api/convert", data, BROTHER.name).status_code == 200
    assert _post(client, "/api/zip", data, BROTHER.name).status_code == 200


def test_app_source_has_no_write_calls() -> None:
    source = Path(web_app.__file__).read_text(encoding="utf-8")
    for needle in ("tempfile", "write_bytes", "write_text", "open("):
        assert needle not in source


def _localhost_socket() -> socket.socket:
    """serve() 와 같은 주소 해석(getaddrinfo 첫 결과)으로 소켓을 만든다."""
    family, socktype, proto, _canon, _addr = socket.getaddrinfo(
        "localhost", 0, type=socket.SOCK_STREAM
    )[0]
    return socket.socket(family, socktype, proto)


def test_serve_port_in_use(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    def must_not_run(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("uvicorn must not start")

    monkeypatch.setattr(server.uvicorn, "run", must_not_run)
    with _localhost_socket() as sock:
        sock.bind(("localhost", 0))
        sock.listen(1)
        port = sock.getsockname()[1]
        assert server.serve("localhost", port, open_browser=False) == 1
    err = capsys.readouterr().err
    assert f"hwp2md: error: port {port} already in use" in err


def test_serve_runs_uvicorn(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[dict[str, Any]] = []

    def fake_run(app: Any, **kwargs: Any) -> None:
        calls.append(kwargs)

    monkeypatch.setattr(server.uvicorn, "run", fake_run)
    with _localhost_socket() as sock:
        sock.bind(("localhost", 0))
        port = sock.getsockname()[1]
    assert server.serve("localhost", port, open_browser=False) == 0
    assert calls == [{"host": "localhost", "port": port, "log_level": "warning"}]
    out = capsys.readouterr().out
    assert out == f"hwp2md serve: http://localhost:{port}/ (Ctrl+C 로 종료)\n"


def test_serve_keyboard_interrupt(monkeypatch: pytest.MonkeyPatch) -> None:
    def interrupted(*args: Any, **kwargs: Any) -> None:
        raise KeyboardInterrupt

    monkeypatch.setattr(server.uvicorn, "run", interrupted)
    with _localhost_socket() as sock:
        sock.bind(("localhost", 0))
        port = sock.getsockname()[1]
    assert server.serve("localhost", port, open_browser=False) == 0


def test_server_defaults() -> None:
    assert server.DEFAULT_HOST == "localhost"
    assert server.DEFAULT_PORT == 8765


def test_port_available_after_time_wait() -> None:
    """방금 끈 서버 포트(TIME_WAIT 잔여 연결)는 사용 가능으로 판정한다."""
    with _localhost_socket() as listener:
        listener.bind(("localhost", 0))
        listener.listen(1)
        host, port = listener.getsockname()[:2]
        with socket.create_connection((host, port)) as client:
            conn, _addr = listener.accept()
            conn.close()  # 서버 쪽이 먼저 닫아 서버 포트에 TIME_WAIT 를 남긴다
            client.recv(1)
    assert server._port_available("localhost", port) is True


def test_port_available_sets_reuseaddr(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[int, int, int]] = []
    real_socket = socket.socket

    class SpySocket(real_socket):  # type: ignore[misc, valid-type]
        def setsockopt(self, level: int, optname: int, value: Any) -> None:  # type: ignore[override]
            calls.append((level, optname, value))
            super().setsockopt(level, optname, value)

    monkeypatch.setattr(server.socket, "socket", SpySocket)
    with _localhost_socket() as sock:
        sock.bind(("localhost", 0))
        port = sock.getsockname()[1]
    assert server._port_available("localhost", port) is True
    assert (socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) in calls
