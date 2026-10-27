"""Build a single-file ``hwp2md`` executable for the current OS with PyInstaller.

Usage: python scripts/build_binary.py [--out DIR] [--platform PLATFORM]

PLATFORM is one of windows-x64, macos-arm64, macos-x64, linux-x64 and defaults
to the current machine. Asking for another OS exits 2 (no cross builds).
PyInstaller is not a project dependency; run this script with
``uv run --with pyinstaller==6.22.3 python scripts/build_binary.py``.

The web UI static files and the ``.py`` sources that ``/pkg/hwp2md.zip`` packs
(``hwp2md`` and ``olefile``) are copied into ``build/pyinstaller/stage`` and
bundled with ``--add-data`` so the frozen app finds them next to its modules.

Exit codes: 0 success (last stdout line ``build_binary: OK <out>/<asset> <bytes>``),
1 PyInstaller failed or produced no file, 2 usage error, unsupported or
mismatching platform, or PyInstaller not installed.
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import platform
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_PACKAGE = ROOT / "src" / "hwp2md"
ENTRY_SCRIPT = ROOT / "packaging" / "pyinstaller" / "hwp2md_entry.py"
PYINSTALLER_DIR = ROOT / "build" / "pyinstaller"
WORK_DIR = PYINSTALLER_DIR / "work"
STAGE_DIR = PYINSTALLER_DIR / "stage"
DEFAULT_OUT = "build/bin"
PYINSTALLER_PIN = "pyinstaller==6.22.3"

ASSETS: dict[str, str] = {
    "windows-x64": "hwp2md-windows-x64.exe",
    "macos-arm64": "hwp2md-macos-arm64",
    "macos-x64": "hwp2md-macos-x64",
    "linux-x64": "hwp2md-linux-x64",
}
_X64 = frozenset({"x86_64", "amd64"})


def detect_platform() -> str | None:
    """Return the §4.1 platform name of this machine, or None if unsupported."""
    machine = platform.machine().lower()
    if sys.platform == "win32" and machine in _X64:
        return "windows-x64"
    if sys.platform == "darwin" and machine == "arm64":
        return "macos-arm64"
    if sys.platform == "darwin" and machine == "x86_64":
        return "macos-x64"
    if sys.platform.startswith("linux") and machine in _X64:
        return "linux-x64"
    return None


def _stage_sources() -> Path:
    """Copy ``src/hwp2md`` and installed ``olefile`` ``*.py`` into a fresh stage dir."""
    import olefile

    if STAGE_DIR.exists():
        shutil.rmtree(STAGE_DIR)
    STAGE_DIR.mkdir(parents=True)
    shutil.copytree(
        SRC_PACKAGE,
        STAGE_DIR / "hwp2md",
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )
    olefile_stage = STAGE_DIR / "olefile"
    olefile_stage.mkdir()
    for path in sorted(Path(olefile.__file__).parent.glob("*.py")):
        shutil.copy2(path, olefile_stage / path.name)
    return STAGE_DIR


def _pyinstaller_args(name: str, dist: Path, stage: Path) -> list[str]:
    sep = os.pathsep
    return [
        "--onefile",
        "--noconfirm",
        "--clean",
        "--console",
        "--name",
        name,
        "--distpath",
        str(dist),
        "--workpath",
        str(WORK_DIR),
        "--specpath",
        str(PYINSTALLER_DIR),
        "--collect-submodules",
        "uvicorn",
        "--hidden-import",
        "hwp2md.web.server",
        "--hidden-import",
        "hwp2md.web.app",
        "--add-data",
        f"{stage / 'hwp2md'}{sep}hwp2md",
        "--add-data",
        f"{stage / 'olefile'}{sep}olefile",
        "--exclude-module",
        "tkinter",
        "--exclude-module",
        "pytest",
        "--exclude-module",
        "playwright",
        "--exclude-module",
        "mypy",
        str(ENTRY_SCRIPT),
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="build_binary")
    parser.add_argument("--out", default=DEFAULT_OUT, help="output directory (default build/bin)")
    parser.add_argument("--platform", choices=sorted(ASSETS), help="target (default: this OS)")
    args = parser.parse_args(argv)

    current = detect_platform()
    if current is None:
        print(
            f"build_binary: unsupported platform {sys.platform}/{platform.machine().lower()}",
            file=sys.stderr,
        )
        return 2
    target: str = args.platform or current
    if target != current:
        print(
            f"build_binary: cannot build {target} on {current} (no cross builds)",
            file=sys.stderr,
        )
        return 2
    if importlib.util.find_spec("PyInstaller") is None:
        print(
            "build_binary: PyInstaller not installed — "
            f"uv run --with {PYINSTALLER_PIN} python scripts/build_binary.py",
            file=sys.stderr,
        )
        return 2

    asset = ASSETS[target]
    out_arg: str = args.out
    out = Path(out_arg)
    dist = out if out.is_absolute() else ROOT / out
    dist.mkdir(parents=True, exist_ok=True)
    stage = _stage_sources()

    import PyInstaller.__main__

    try:
        PyInstaller.__main__.run(_pyinstaller_args(asset.removesuffix(".exe"), dist, stage))
    except SystemExit as exc:
        if exc.code not in (None, 0):
            print(f"build_binary: PyInstaller failed (exit {exc.code})", file=sys.stderr)
            return 1
    except Exception as exc:  # PyInstaller reports build errors as plain exceptions
        print(f"build_binary: PyInstaller failed: {exc}", file=sys.stderr)
        return 1

    result = dist / asset
    if not result.is_file():
        print(f"build_binary: no output at {result}", file=sys.stderr)
        return 1
    shown = f"{out_arg.rstrip('/').rstrip(os.sep)}/{asset}"
    print(f"build_binary: OK {shown} {result.stat().st_size}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
