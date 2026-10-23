from __future__ import annotations

import io
import socket
import subprocess
import sys
import zipfile
from collections.abc import Callable
from pathlib import Path

import httpx
import pytest
from conftest import REAL_SAMPLES, WebServer

RunCli = Callable[[list[str]], subprocess.CompletedProcess[str]]

IMAGE_HWPX = next(p for p in REAL_SAMPLES if p.suffix == ".hwpx" and p.stem.startswith("브라더"))


def _post(server: WebServer, route: str, body: bytes, name: str) -> httpx.Response:
    return httpx.post(
        f"{server.base_url}{route}",
        params={"name": name},
        content=body,
        headers={"Content-Type": "application/octet-stream"},
        timeout=60,
    )


def _cli_convert(path: Path, out_dir: Path, run_cli: RunCli) -> Path:
    result = run_cli([str(path), "-o", str(out_dir)])
    assert result.returncode == 0, result.stderr
    return out_dir / f"{path.stem}.md"


def test_health(web_server: WebServer) -> None:
    resp = httpx.get(f"{web_server.base_url}/api/health", timeout=10)

    assert resp.status_code == 200
    body = resp.json()
    assert body["ok"] is True
    assert body["version"]


def test_index_has_drop_zone(web_server: WebServer) -> None:
    resp = httpx.get(f"{web_server.base_url}/", timeout=10)

    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/html")
    assert 'id="drop-zone"' in resp.text


@pytest.mark.parametrize("sample", REAL_SAMPLES, ids=lambda p: p.name)
def test_convert_matches_cli(
    web_server: WebServer, sample: Path, tmp_path: Path, run_cli: RunCli
) -> None:
    md_path = _cli_convert(sample, tmp_path / "out", run_cli)

    resp = _post(web_server, "/api/convert", sample.read_bytes(), sample.name)

    assert resp.status_code == 200
    assert resp.json()["markdown"].encode("utf-8") == md_path.read_bytes()


def test_zip_matches_cli_with_image(web_server: WebServer, tmp_path: Path, run_cli: RunCli) -> None:
    out_dir = tmp_path / "out"
    md_path = _cli_convert(IMAGE_HWPX, out_dir, run_cli)
    image_dir = out_dir / f"{IMAGE_HWPX.stem}_images"

    resp = _post(web_server, "/api/zip", IMAGE_HWPX.read_bytes(), IMAGE_HWPX.name)

    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/zip"
    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        names = zf.namelist()
        assert names == [md_path.name, f"{image_dir.name}/img_001.png"]
        assert zf.read(names[0]) == md_path.read_bytes()
        assert zf.read(names[1]) == (image_dir / "img_001.png").read_bytes()


def test_not_hwp_415(web_server: WebServer) -> None:
    resp = _post(web_server, "/api/convert", b"plain text, not an ole file\n" * 100, "fake.hwp")

    assert resp.status_code == 415
    assert resp.json()["error"]["code"] == "not_hwp"


def test_empty_400(web_server: WebServer) -> None:
    resp = _post(web_server, "/api/convert", b"", "empty.hwp")

    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "empty"


def test_content_length_over_limit_413(web_server: WebServer) -> None:
    declared = 50 * 1024 * 1024 + 1
    request = (
        f"POST /api/convert?name=big.hwp HTTP/1.1\r\n"
        f"Host: localhost:{web_server.port}\r\n"
        f"Content-Type: application/octet-stream\r\n"
        f"Content-Length: {declared}\r\n"
        f"Connection: close\r\n\r\n"
    ).encode("ascii")
    with socket.create_connection(("localhost", web_server.port), timeout=10) as sock:
        sock.sendall(request)
        chunks: list[bytes] = []
        while b'"too_large"' not in b"".join(chunks):
            data = sock.recv(4096)
            if not data:
                break
            chunks.append(data)
    raw = b"".join(chunks)

    assert raw.startswith(b"HTTP/1.1 413")
    assert b'"too_large"' in raw


def test_runtime_zip_listing(web_server: WebServer) -> None:
    resp = httpx.get(f"{web_server.base_url}/pkg/hwp2md.zip", timeout=30)

    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/zip"
    assert resp.headers["cache-control"] == "no-store"
    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        names = set(zf.namelist())
    assert "hwp2md/memory.py" in names
    assert "hwp2md/__init__.py" in names
    assert any(n.startswith("olefile/") and n.endswith(".py") for n in names)
    assert not any(n.startswith("hwp2md/web/") or "__pycache__" in n for n in names)


def test_no_files_written(web_server: WebServer) -> None:
    sample = IMAGE_HWPX
    assert _post(web_server, "/api/convert", sample.read_bytes(), sample.name).status_code == 200
    assert _post(web_server, "/api/zip", sample.read_bytes(), sample.name).status_code == 200
    assert _post(web_server, "/api/convert", b"junk" * 100, "x.hwp").status_code == 415

    leftovers = [p for root in (web_server.cwd, web_server.tmpdir) for p in root.rglob("*")]
    assert leftovers == []


def test_serve_port_in_use_exit_1(hwp2md_bin: str, tmp_path: Path) -> None:
    with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as holder:
        holder.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        holder.bind(("localhost", 0))
        holder.listen()
        port = holder.getsockname()[1]
        result = subprocess.run(
            [hwp2md_bin, "serve", "--no-browser", "--port", str(port)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=tmp_path,
            timeout=30,
        )

    assert result.returncode == 1
    assert "already in use" in result.stderr


def test_serve_without_web_extra_exit_1(tmp_path: Path) -> None:
    code = (
        "import sys\n"
        "for m in ('starlette', 'uvicorn'):\n"
        "    sys.modules[m] = None\n"
        "from hwp2md.cli import main\n"
        "sys.exit(main(['serve', '--no-browser']))\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=tmp_path,
        timeout=30,
    )

    assert result.returncode == 1
    assert "hwp2md[web]" in result.stderr


def test_existing_convert_still_works(synthetic_hwp: Path, tmp_path: Path, run_cli: RunCli) -> None:
    out_dir = tmp_path / "out"
    result = run_cli([str(synthetic_hwp), "-o", str(out_dir)])

    assert result.returncode == 0, result.stderr
    assert (out_dir / "sample.md").is_file()
