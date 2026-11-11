"""Command-line entry point: ``hwp2md INPUT [-o OUT_DIR] [--version]``."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from . import __version__
from .convert import convert
from .errors import (
    DrmProtectedError,
    EncryptedDocumentError,
    Hwp2mdError,
    NotHwpFileError,
    UnsupportedHwpError,
)
from .skips import SKIP_LABELS


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="hwp2md")
    parser.add_argument("input", metavar="INPUT", help="변환할 HWP·HWPX·HWPML 파일 경로")
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


def _serve_main(argv: Sequence[str]) -> int:
    parser = argparse.ArgumentParser(prog="hwp2md serve")
    parser.add_argument("--host", default="localhost", help='바인드 호스트 (기본값 "localhost")')
    parser.add_argument("--port", type=int, default=8770, help="포트 (기본값 8770)")
    parser.add_argument("--no-browser", action="store_true", help="브라우저를 자동으로 열지 않음")
    ns = parser.parse_args(list(argv))
    try:
        from .web.server import serve
    except ImportError:
        return _error("web extra not installed — pip install 'hwp2markdown[web]'", 1)
    host: str = ns.host
    port: int = ns.port
    no_browser: bool = ns.no_browser
    return serve(host, port, open_browser=not no_browser)


def main(argv: Sequence[str] | None = None) -> int:
    argv_list = list(sys.argv[1:] if argv is None else argv)
    if argv_list[:1] == ["serve"]:
        return _serve_main(argv_list[1:])
    args = _build_parser().parse_args(argv_list)
    input_arg: str = args.input
    try:
        result = convert(input_arg, args.out_dir)
    except NotHwpFileError:
        return _error(f"not an HWP 5.0 file: {input_arg}", 3)
    except DrmProtectedError:
        return _error(f"unsupported HWP file (DRM protected): {input_arg}", 3)
    except EncryptedDocumentError:
        return _error(f"unsupported HWP file (password protected): {input_arg}", 3)
    except UnsupportedHwpError:
        return _error(f"unsupported HWP file (encrypted or distribution): {input_arg}", 3)
    except FileNotFoundError:
        return _error(f"file not found: {input_arg}", 2)
    except Hwp2mdError as exc:
        return _error(str(exc), 1)
    except Exception as exc:  # noqa: BLE001 - CLI 경계: traceback 없이 종료 코드 1
        return _error(str(exc), 1)
    print(f"✓ {Path(input_arg).name} → {result.output}")
    summary = f"  단락 {result.paragraph_count}개 · 표 {result.table_count}개"
    if result.heading_count:
        summary += f" · 제목 {result.heading_count}개"
    if result.image_count:
        summary += f" · 이미지 {result.image_count}개"
    print(summary)
    if result.image_files:
        print(f"  이미지: {result.image_dir}/ ({len(result.image_files)} files)")
    if result.skipped:
        skipped = " · ".join(f"{SKIP_LABELS[k]} {n}개" for k, n in result.skipped)
        print(f"  건너뜀: {skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
