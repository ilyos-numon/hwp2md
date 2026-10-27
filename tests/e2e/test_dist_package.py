"""E2E for the built distribution: install the wheel in a fresh venv and run check_dist."""

from __future__ import annotations

import io
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tarfile
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest

import hwp2md

ROOT = Path(__file__).resolve().parents[2]
CHECK_DIST = ROOT / "scripts" / "check_dist.py"
VERSION = hwp2md.__version__


def _env() -> dict[str, str]:
    env = {k: v for k, v in os.environ.items() if k != "VIRTUAL_ENV"}
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def _run(args: list[str], **kw: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=_env(),
        timeout=300,
        **kw,  # type: ignore[arg-type]
    )


def _check_dist(dist_dir: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return _run([sys.executable, str(CHECK_DIST), str(dist_dir), *extra])


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("localhost", 0))
        port: int = sock.getsockname()[1]
    return port


@pytest.fixture(scope="module")
def dist_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    uv = shutil.which("uv")
    if uv is None:
        pytest.fail("uv not found on PATH")
    out = tmp_path_factory.mktemp("dist")
    res = _run([uv, "build", "--out-dir", str(out)], cwd=ROOT)
    if res.returncode != 0:
        pytest.fail(f"uv build failed:\n{res.stdout}\n{res.stderr}")
    return out


def _wheel(dist_dir: Path) -> Path:
    wheels = list(dist_dir.glob("*.whl"))
    assert len(wheels) == 1, wheels
    return wheels[0]


def test_wheel_installs_and_serves(dist_dir: Path, tmp_path: Path) -> None:
    uv = shutil.which("uv")
    assert uv is not None
    venv = tmp_path / "venv"
    py = f"{sys.version_info.major}.{sys.version_info.minor}"
    res = _run([uv, "venv", "--python", py, str(venv)])
    assert res.returncode == 0, res.stderr
    wheel = _wheel(dist_dir)
    res = _run([uv, "pip", "install", "--python", str(venv / "bin" / "python"), f"{wheel}[web]"])
    assert res.returncode == 0, res.stderr

    exe = str(venv / "bin" / "hwp2md")
    res = _run([exe, "--version"])
    assert res.returncode == 0, res.stderr
    assert res.stdout.strip() == f"hwp2md {VERSION}"

    port = _free_port()
    proc = subprocess.Popen(
        [exe, "serve", "--no-browser", "--port", str(port)],
        cwd=tmp_path,
        env=_env(),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        body: dict[str, object] | None = None
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            if proc.poll() is not None:
                pytest.fail(f"serve exited early: rc={proc.returncode}")
            try:
                url = f"http://localhost:{port}/api/health"
                with urllib.request.urlopen(url, timeout=2) as r:
                    if r.status == 200:
                        body = json.loads(r.read().decode("utf-8"))
                        break
            except (urllib.error.URLError, OSError):
                pass
            time.sleep(0.5)
        assert body is not None, "health not reachable within 30s"
        assert body["version"] == VERSION
    finally:
        proc.terminate()
        try:
            proc.wait(10)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(10)

    res = _check_dist(dist_dir)
    assert res.returncode == 0, res.stdout + res.stderr
    assert res.stdout.startswith("check_dist: OK")


def test_forbidden_files_in_sdist_fail(dist_dir: Path, tmp_path: Path) -> None:
    bad = tmp_path / "bad"
    bad.mkdir()
    shutil.copy(_wheel(dist_dir), bad)
    root = f"hwp2markdown-{VERSION}"
    with tarfile.open(bad / f"{root}.tar.gz", "w:gz") as tar:
        for name, data in {
            f"{root}/.ai/STATE.md": b"state\n",
            f"{root}/CLAUDE.md": b"claude\n",
            f"{root}/PKG-INFO": f"Metadata-Version: 2.1\nVersion: {VERSION}\n".encode(),
        }.items():
            info = tarfile.TarInfo(name)
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))
    res = _check_dist(bad)
    out = res.stdout + res.stderr
    assert res.returncode == 1, out
    assert ".ai/STATE.md" in out
    assert "CLAUDE.md" in out
    assert "forbidden-path" in out


def test_tag_mismatch_fails(dist_dir: Path) -> None:
    res = _check_dist(dist_dir, "--tag", "v9.9.9")
    out = res.stdout + res.stderr
    assert res.returncode == 1, out
    assert "version-mismatch" in out


def test_pattern_hit_fails_without_leaking_text(dist_dir: Path, tmp_path: Path) -> None:
    first_line = (ROOT / "README.md").read_text(encoding="utf-8").splitlines()[0]
    assert first_line.strip()
    patterns = tmp_path / "patterns.txt"
    patterns.write_text(re.escape(first_line) + "\n", encoding="utf-8")
    res = _check_dist(dist_dir, "--patterns", str(patterns))
    out = res.stdout + res.stderr
    assert res.returncode == 1, out
    assert "pattern-hit" in out
    assert first_line not in out
