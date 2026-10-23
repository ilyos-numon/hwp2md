from __future__ import annotations

import os
import shutil
import socket
import subprocess
import time
import urllib.error
import urllib.request
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from pathlib import Path

import pytest

from samples import LEGACY_SAMPLES
from synth_hwp5 import FIXTURE_PARAGRAPHS, write_hwp5


@pytest.fixture
def hwp2md_bin() -> str:
    found = shutil.which("hwp2md")
    if found is None:
        pytest.fail("hwp2md console script not on PATH — run `uv sync`")
    return found


@pytest.fixture
def synthetic_hwp(tmp_path: Path) -> Path:
    return write_hwp5(tmp_path / "sample.hwp", FIXTURE_PARAGRAPHS)


@pytest.fixture
def run_cli(hwp2md_bin: str) -> Callable[[list[str]], subprocess.CompletedProcess[str]]:
    def _run(args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [hwp2md_bin, *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            timeout=60,
        )

    return _run


_FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures"
REAL_SAMPLES: list[Path] = LEGACY_SAMPLES


@dataclass(frozen=True)
class WebServer:
    base_url: str
    port: int
    cwd: Path
    tmpdir: Path
    proc: subprocess.Popen[str]


def _free_port() -> int:
    with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as sock:
        sock.bind(("localhost", 0))
        port: int = sock.getsockname()[1]
    return port


@pytest.fixture(scope="session")
def web_server(tmp_path_factory: pytest.TempPathFactory) -> Iterator[WebServer]:
    found = shutil.which("hwp2md")
    if found is None:
        pytest.fail("hwp2md console script not on PATH — run `uv sync`")
    port = _free_port()
    cwd = tmp_path_factory.mktemp("srv_cwd")
    tmpdir = tmp_path_factory.mktemp("srv_tmp")
    proc = subprocess.Popen(
        [found, "serve", "--no-browser", "--port", str(port)],
        cwd=cwd,
        env={**os.environ, "TMPDIR": str(tmpdir), "PYTHONIOENCODING": "utf-8"},
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    base_url = f"http://localhost:{port}"
    try:
        for _ in range(60):
            if proc.poll() is not None:
                break
            try:
                with urllib.request.urlopen(f"{base_url}/api/health", timeout=2) as resp:
                    if resp.status == 200:
                        break
            except (urllib.error.URLError, OSError):
                pass
            time.sleep(0.5)
        else:
            pytest.fail("hwp2md serve did not become healthy within 30s")
        if proc.poll() is not None:
            pytest.fail(f"hwp2md serve exited early: rc={proc.returncode}")
        yield WebServer(base_url=base_url, port=port, cwd=cwd, tmpdir=tmpdir, proc=proc)
    finally:
        proc.terminate()
        try:
            proc.wait(10)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(10)
        for stream in (proc.stdout, proc.stderr):
            if stream is not None:
                stream.close()
