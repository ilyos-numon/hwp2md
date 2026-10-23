"""Detect the container format of an input file by content (never by extension)."""

from __future__ import annotations

import zipfile
from typing import Literal

import olefile

from .errors import DrmProtectedError, NotHwpFileError
from .hwpx.reader import HWPX_MIMETYPE, HWPX_SECTION0
from .source import Source, as_binary_io, source_label

DocFormat = Literal["hwp5", "hwpx"]

_MAX_MIMETYPE_BYTES = 256
_DRM_HEAD_BYTES = 64
_DRM_PREFIX = b"\x9b\x20"
_DRM_MARKER = b"DRMONE"


def _read_head(path: Source) -> bytes:
    if isinstance(path, bytes):
        return path[:_DRM_HEAD_BYTES]
    with path.open("rb") as fh:
        return fh.read(_DRM_HEAD_BYTES)


def is_drm_wrapped(head: bytes) -> bool:
    """앞 2바이트가 9B 20 이거나 앞 64바이트 안에 ASCII "DRMONE" 이 있으면 True."""
    head = head[:_DRM_HEAD_BYTES]
    return head[:2] == _DRM_PREFIX or _DRM_MARKER in head


def detect_format(path: Source) -> DocFormat:
    """판정 순서 (첫 번째로 맞는 것):
    0. DRM 서명 (앞 2바이트 9B 20 또는 앞 64바이트 안 "DRMONE") → DrmProtectedError
    1. OLE 복합 문서 → "hwp5" (FileHeader 검사는 hwp5 리더가 한다)
    2. zip → mimetype == HWPX_MIMETYPE 이면 "hwpx", 아니면 HWPX_SECTION0 있으면 "hwpx",
       아니면 NotHwpFileError. 깨진 zip 도 NotHwpFileError.
    3. 그 외 → NotHwpFileError
    확장자(.hwp/.hwpx)는 어떤 경우에도 보지 않는다."""
    label = source_label(path)
    if is_drm_wrapped(_read_head(path)):
        raise DrmProtectedError(f"DRM-protected document: {label}")
    if olefile.isOleFile(as_binary_io(path)):
        return "hwp5"
    if zipfile.is_zipfile(as_binary_io(path)):
        try:
            with zipfile.ZipFile(as_binary_io(path)) as zf:
                names = zf.namelist()
                if (
                    "mimetype" in names
                    and zf.getinfo("mimetype").file_size <= _MAX_MIMETYPE_BYTES
                    and zf.read("mimetype").strip() == HWPX_MIMETYPE
                ):
                    return "hwpx"
                if HWPX_SECTION0 in names:
                    return "hwpx"
        except zipfile.BadZipFile as exc:
            raise NotHwpFileError(f"corrupt zip archive: {label}") from exc
        raise NotHwpFileError(f"zip archive is not an HWPX package: {label}")
    raise NotHwpFileError(f"not an HWP 5.0 or HWPX file: {label}")
