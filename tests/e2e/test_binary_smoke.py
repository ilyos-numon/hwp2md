"""Smoke E2E for the frozen single-file executable (PyInstaller build).

Uses ``HWP2MD_BINARY`` when set, otherwise builds one for the current OS.
"""

from __future__ import annotations

import io
import os
import re
import socket
import subprocess
import time
import urllib.error
import urllib.request
import zipfile
from collections.abc import Iterator
from pathlib import Path

import pytest

import hwp2md
from synth_hwp5 import FIXTURE_PARAGRAPHS, write_hwp5
from synth_hwpx import write_hwpx

ROOT = Path(__file__).resolve().parents[2]
FONT_REL = "web/static/vendor/fonts/PretendardVariable.woff2"
BUILD_TIMEOUT = 900


def _clean_env() -> dict[str, str]:
    env = dict(os.environ)
    env.pop("PYTHONIOENCODING", None)
    env.pop("PYTHONUTF8", None)
    return env


def _free_port() -> int:
    with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as sock:
        sock.bind(("localhost", 0))
        port: int = sock.getsockname()[1]
    return port


@pytest.fixture(scope="session")
def binary(tmp_path_factory: pytest.TempPathFactory) -> Path:
    given = os.environ.get("HWP2MD_BINARY")
    if given:
        path = Path(given)
        if not path.is_absolute():
            path = ROOT / path
        if not path.is_file():
            pytest.fail(f"HWP2MD_BINARY does not exist: {path}")
        return path
    out = tmp_path_factory.mktemp("binout")
    cmd = [
        "uv",
        "run",
        "--with",
        "pyinstaller==6.22.3",
        "python",
        "scripts/build_binary.py",
        "--out",
        str(out),
    ]
    try:
        proc = subprocess.run(
            cmd,
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=BUILD_TIMEOUT,
            env={k: v for k, v in os.environ.items() if k != "VIRTUAL_ENV"},
        )
    except subprocess.TimeoutExpired:
        pytest.fail(f"build_binary timed out after {BUILD_TIMEOUT}s")
    if proc.returncode != 0:
        pytest.fail(
            f"build_binary failed rc={proc.returncode}\n{proc.stdout[-800:]}\n{proc.stderr[-800:]}"
        )
    ok = [ln for ln in proc.stdout.splitlines() if ln.startswith("build_binary: OK ")]
    if not ok:
        pytest.fail(f"no 'build_binary: OK' line in output:\n{proc.stdout[-800:]}")
    m = re.match(r"build_binary: OK (.+) (\d+)$", ok[-1])
    if m is None:
        pytest.fail(f"unparsable build_binary line: {ok[-1]}")
    path = Path(m.group(1))
    if not path.is_absolute():
        path = out / path.name if not (ROOT / path).is_file() else ROOT / path
    if not path.is_file():
        pytest.fail(f"built binary missing: {path}")
    return path


def _run(binary: Path, args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(binary), *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=_clean_env(),
        timeout=120,
    )


def test_version(binary: Path, tmp_path: Path) -> None:
    res = _run(binary, ["--version"], tmp_path)
    assert res.returncode == 0, res.stderr
    assert res.stdout.strip() == f"hwp2md {hwp2md.__version__}"


def test_convert_hwpx(binary: Path, tmp_path: Path) -> None:
    src = write_hwpx(tmp_path / "doc.hwpx", FIXTURE_PARAGRAPHS)
    out = tmp_path / "out"
    res = _run(binary, [str(src), "-o", str(out)], tmp_path)
    assert res.returncode == 0, res.stderr
    assert "✓" in res.stdout
    md = out / "doc.md"
    assert md.is_file()
    text = md.read_text(encoding="utf-8")
    assert "테스트 문서 제목" in text
    assert "본문 단락 2" in text


def test_convert_hwp5(binary: Path, tmp_path: Path) -> None:
    src = write_hwp5(tmp_path / "doc.hwp", FIXTURE_PARAGRAPHS)
    out = tmp_path / "out"
    res = _run(binary, [str(src), "-o", str(out)], tmp_path)
    assert res.returncode == 0, res.stderr
    md = out / "doc.md"
    assert md.is_file()
    assert "테스트 문서 제목" in md.read_text(encoding="utf-8")


def test_not_hwp_exit3(binary: Path, tmp_path: Path) -> None:
    note = tmp_path / "note.txt"
    note.write_text("not a hwp document", encoding="utf-8")
    res = _run(binary, [str(note), "-o", str(tmp_path / "out")], tmp_path)
    assert res.returncode == 3
    assert "hwp2md: error: not an HWP 5.0 file" in res.stderr
    assert "Traceback" not in res.stderr


def test_corrupt_hwpx(binary: Path, tmp_path: Path) -> None:
    good = write_hwpx(tmp_path / "good.hwpx", FIXTURE_PARAGRAPHS)
    bad = tmp_path / "bad.hwpx"
    bad.write_bytes(good.read_bytes()[:100])
    res = _run(binary, [str(bad), "-o", str(tmp_path / "out")], tmp_path)
    assert res.returncode != 0
    assert "hwp2md: error:" in res.stderr
    assert "Traceback" not in res.stderr


def test_missing_file_exit2(binary: Path, tmp_path: Path) -> None:
    res = _run(binary, [str(tmp_path / "nope.hwp"), "-o", str(tmp_path / "out")], tmp_path)
    assert res.returncode == 2
    assert "hwp2md: error: file not found" in res.stderr


def _get(url: str) -> tuple[int, str, bytes]:
    with urllib.request.urlopen(url, timeout=10) as resp:
        return resp.status, resp.headers.get("Content-Type", ""), resp.read()


@pytest.fixture
def served(binary: Path, tmp_path: Path) -> Iterator[str]:
    port = _free_port()
    log = (tmp_path / "serve.log").open("wb")
    proc = subprocess.Popen(
        [str(binary), "serve", "--no-browser", "--port", str(port)],
        cwd=tmp_path,
        env={**_clean_env(), "TMPDIR": str(tmp_path)},
        stdout=log,
        stderr=subprocess.STDOUT,
    )
    base = f"http://localhost:{port}"
    try:
        deadline = time.monotonic() + 60
        while True:
            if proc.poll() is not None:
                pytest.fail(f"serve exited early rc={proc.returncode}")
            try:
                if _get(f"{base}/api/health")[0] == 200:
                    break
            except (urllib.error.URLError, OSError):
                pass
            if time.monotonic() > deadline:
                pytest.fail("serve not healthy within 60s")
            time.sleep(0.5)
        yield base
    finally:
        proc.terminate()
        try:
            proc.wait(5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(10)
        log.close()


def test_serve(served: str, tmp_path: Path) -> None:
    import json

    status, _, body = _get(f"{served}/api/health")
    assert status == 200
    assert json.loads(body)["version"] == hwp2md.__version__

    status, _, font = _get(f"{served}/static/vendor/fonts/PretendardVariable.woff2")
    assert status == 200
    assert font == (ROOT / "src" / "hwp2md" / FONT_REL).read_bytes()

    status, ctype, _ = _get(f"{served}/")
    assert status == 200
    assert ctype.startswith("text/html")

    status, _, zbody = _get(f"{served}/pkg/hwp2md.zip")
    assert status == 200
    names = zipfile.ZipFile(io.BytesIO(zbody)).namelist()
    for needed in ("hwp2md/__init__.py", "hwp2md/convert.py", "olefile/olefile.py"):
        assert needed in names
    assert not [n for n in names if n.startswith("hwp2md/web/")]

    src = write_hwpx(tmp_path / "a.hwpx", FIXTURE_PARAGRAPHS)
    req = urllib.request.Request(
        f"{served}/api/convert?name=a.hwpx",
        data=src.read_bytes(),
        headers={"Content-Type": "application/octet-stream"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        assert resp.status == 200
        assert "테스트 문서 제목" in json.loads(resp.read())["markdown"]
