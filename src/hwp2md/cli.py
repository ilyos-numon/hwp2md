"""Command-line entry point: ``hwp2md INPUT [-o OUT_DIR] [--version]``."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from . import __version__
from .convert import convert
from .errors import Hwp2mdError, NotHwpFileError, UnsupportedHwpError


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="hwp2md")
    parser.add_argument("input", metavar="INPUT", help="변환할 .hwp 파일 경로")
    parser.add_argument(
        "-o",
        "--out-dir",
        default=".",
        help='출력 디렉터리 (기본값 ".", 없으면 생성)',
    )
    parser.add_argument("--version", action="version", version=f"hwp2md {__version__}")
    return parser


def _error(message: str, code: int) -> int:
    print(f"hwp2md: error: {message}", file=sys.stderr)
    return code


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    input_arg: str = args.input
    try:
        result = convert(input_arg, args.out_dir)
    except NotHwpFileError:
        return _error(f"not an HWP 5.0 file: {input_arg}", 3)
    except UnsupportedHwpError:
        return _error(f"unsupported HWP file (encrypted or distribution): {input_arg}", 3)
    except FileNotFoundError:
        return _error(f"file not found: {input_arg}", 2)
    except Hwp2mdError as exc:
        return _error(str(exc), 1)
    except Exception as exc:  # noqa: BLE001 - CLI 경계: traceback 없이 종료 코드 1
        return _error(str(exc), 1)
    print(f"✓ {Path(input_arg).name} → {result.output}")
    print(f"  단락 {result.paragraph_count}개 · 표 {result.table_count}개")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
