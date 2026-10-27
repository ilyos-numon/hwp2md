"""Starlette app: HTTP conversion API, static UI files, runtime package zip."""

from __future__ import annotations

import io
import urllib.parse
import zipfile
from pathlib import Path

import olefile
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse, Response
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

import hwp2md
from hwp2md import memory

STATIC_DIR: Path = Path(__file__).parent / "static"
_PACKAGE_DIR = Path(hwp2md.__file__).parent
_ZIP_DATE_TIME = (1980, 1, 1, 0, 0, 0)
_DEFAULT_NAME = "document.hwp"
_EXCLUDED_PARTS = frozenset({"web", "__pycache__"})


def build_runtime_zip() -> bytes:
    """hwp2md(web 제외) 와 olefile 순수 파이썬 소스를 담은 zip (Pyodide 용)."""
    entries: list[tuple[str, Path]] = []
    for path in sorted(_PACKAGE_DIR.rglob("*")):
        if not path.is_file() or not (path.suffix == ".py" or path.name == "py.typed"):
            continue
        rel = path.relative_to(_PACKAGE_DIR)
        if _EXCLUDED_PARTS.intersection(rel.parts):
            continue
        entries.append((f"hwp2md/{rel.as_posix()}", path))
    olefile_dir = Path(olefile.__file__).parent
    for path in sorted(olefile_dir.glob("*.py")):
        entries.append((f"olefile/{path.name}", path))

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, path in entries:
            info = zipfile.ZipInfo(name, date_time=_ZIP_DATE_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(info, path.read_bytes())
    return buf.getvalue()


def _too_large_response(request: Request) -> JSONResponse | None:
    """Content-Length 가 한도를 넘으면 body 를 읽지 않고 413."""
    limit = memory.MAX_INPUT_BYTES
    header = request.headers.get("content-length")
    if header is None:
        return None
    try:
        length = int(header)
    except ValueError:
        return None
    if length <= limit:
        return None
    return JSONResponse(
        {"error": {"code": "too_large", "message": f"input exceeds {limit} bytes"}},
        status_code=memory.STATUS_BY_CODE["too_large"],
    )


def _name(request: Request) -> str:
    return request.query_params.get("name") or _DEFAULT_NAME


async def _index(request: Request) -> Response:
    return FileResponse(STATIC_DIR / "index.html", media_type="text/html; charset=utf-8")


async def _about(request: Request) -> Response:
    return FileResponse(STATIC_DIR / "about.html", media_type="text/html; charset=utf-8")


async def _health(request: Request) -> Response:
    return JSONResponse({"ok": True, "version": hwp2md.__version__})


async def _convert(request: Request) -> Response:
    rejected = _too_large_response(request)
    if rejected is not None:
        return rejected
    body = await request.body()
    status, payload = memory.convert_to_response(body, _name(request))
    return JSONResponse(payload, status_code=status)


async def _zip(request: Request) -> Response:
    rejected = _too_large_response(request)
    if rejected is not None:
        return rejected
    body = await request.body()
    name = _name(request)
    try:
        result = memory.convert_bytes(body, name)
    except Exception as exc:
        code = memory.error_code(exc)
        return JSONResponse(
            {"error": {"code": code, "message": str(exc)}},
            status_code=memory.STATUS_BY_CODE[code],
        )
    filename = urllib.parse.quote(result.stem + ".zip")
    return Response(
        memory.build_zip(result),
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"},
    )


def create_app() -> Starlette:
    runtime_zip = build_runtime_zip()

    async def _pkg(request: Request) -> Response:
        return Response(
            runtime_zip,
            media_type="application/zip",
            headers={"Cache-Control": "no-store"},
        )

    routes = [
        Route("/", _index, methods=["GET"]),
        Route("/about", _about, methods=["GET"]),
        Route("/api/health", _health, methods=["GET"]),
        Route("/api/convert", _convert, methods=["POST"]),
        Route("/api/zip", _zip, methods=["POST"]),
        Route("/pkg/hwp2md.zip", _pkg, methods=["GET"]),
        Mount("/static", app=StaticFiles(directory=STATIC_DIR), name="static"),
    ]
    return Starlette(routes=routes)
