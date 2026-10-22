from __future__ import annotations

import os
import shutil
import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest

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
