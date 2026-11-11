"""In-memory conversion API: document bytes in, Markdown and image bytes out (no disk access)."""

from __future__ import annotations

import base64
import io
import zipfile
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any, Literal

from .blocks import iter_images
from .convert import _count_blocks, read_blocks
from .errors import (
    DrmProtectedError,
    EmptyInputError,
    EncryptedDocumentError,
    InputTooLargeError,
    NotHwpFileError,
    UnsupportedHwpError,
)
from .images import image_dir_name
from .render import render_blocks
from .skips import SKIP_LABELS, SkipCounter, SkipKind

MAX_INPUT_BYTES = 50 * 1024 * 1024  # 52428800
ErrorCode = Literal[
    "empty", "too_large", "not_hwp", "unsupported", "drm", "encrypted", "convert_failed"
]
STATUS_BY_CODE: dict[ErrorCode, int] = {
    "empty": 400,
    "too_large": 413,
    "not_hwp": 415,
    "unsupported": 415,
    "drm": 415,
    "encrypted": 415,
    "convert_failed": 422,
}
MIME_BY_EXT = {
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "gif": "image/gif",
    "bmp": "image/bmp",
}
_DEFAULT_MIME = "application/octet-stream"
_DEFAULT_STEM = "document"
_ZIP_DATE_TIME = (1980, 1, 1, 0, 0, 0)


@dataclass(frozen=True)
class MemoryImage:
    file_name: str  # "img_001.png"
    data: bytes

    @property
    def mime(self) -> str:
        ext = PurePosixPath(self.file_name).suffix.removeprefix(".").lower()
        return MIME_BY_EXT.get(ext, _DEFAULT_MIME)


@dataclass(frozen=True)
class MemoryResult:
    stem: str  # safe_stem(filename)
    markdown: str  # convert() 가 쓰는 .md 와 바이트 동일 (상대 링크)
    image_dir: str  # f"{stem}_images" (이미지 없어도 값은 채움)
    images: tuple[MemoryImage, ...]  # 고유 file_name 첫 등장 순
    paragraph_count: int
    table_count: int
    heading_count: int
    image_count: int  # Image 블록 수(재참조 포함)
    skipped: tuple[tuple[SkipKind, int], ...] = ()  # SkipCounter.items() — count > 0, 보고 순서


def safe_stem(filename: str) -> str:
    """'/'·'\\' 로 쪼갠 마지막 요소의 stem (strip). "" / "." / ".." → "document"."""
    last = filename.replace("\\", "/").split("/")[-1]
    stem = PurePosixPath(last).stem.strip() if last else ""
    if stem in ("", ".", ".."):
        return _DEFAULT_STEM
    return stem


def convert_bytes(data: bytes, filename: str = "document.hwp") -> MemoryResult:
    """빈 입력 → EmptyInputError, MAX_INPUT_BYTES 초과 → InputTooLargeError.
    그 밖의 리더 예외는 그대로 전파."""
    if len(data) == 0:
        raise EmptyInputError("빈 파일입니다")
    if len(data) > MAX_INPUT_BYTES:
        raise InputTooLargeError(
            f"파일이 너무 큽니다: {len(data)} bytes (최대 {MAX_INPUT_BYTES} bytes)"
        )
    counter = SkipCounter()
    blocks = read_blocks(data, skips=counter)
    stem = safe_stem(filename)
    image_dir = image_dir_name(stem)
    markdown = render_blocks(blocks, image_dir=image_dir)
    paragraph_count, table_count, heading_count, image_count = _count_blocks(blocks)
    unique: dict[str, MemoryImage] = {}
    for img in iter_images(blocks):
        if img.file_name not in unique:
            unique[img.file_name] = MemoryImage(file_name=img.file_name, data=img.data)
    return MemoryResult(
        stem=stem,
        markdown=markdown,
        image_dir=image_dir,
        images=tuple(unique.values()),
        paragraph_count=paragraph_count,
        table_count=table_count,
        heading_count=heading_count,
        image_count=image_count,
        skipped=counter.items(),
    )


def markdown_with_data_uris(result: MemoryResult) -> str:
    """이미지 상대 링크를 data URI 로 바꾼 미리보기용 Markdown."""
    text = result.markdown
    link_dir = result.image_dir.replace(" ", "%20")
    for img in result.images:
        b64 = base64.b64encode(img.data).decode("ascii")
        text = text.replace(f"]({link_dir}/{img.file_name})", f"](data:{img.mime};base64,{b64})")
    return text


def build_zip(result: MemoryResult) -> bytes:
    """<stem>.md 와 <image_dir>/<file_name> 를 담은 zip (고정 타임스탬프)."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        entries: list[tuple[str, bytes]] = [(f"{result.stem}.md", result.markdown.encode("utf-8"))]
        entries += [(f"{result.image_dir}/{img.file_name}", img.data) for img in result.images]
        for name, payload in entries:
            info = zipfile.ZipInfo(name, date_time=_ZIP_DATE_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(info, payload)
    return buf.getvalue()


def to_payload(result: MemoryResult) -> dict[str, Any]:
    return {
        "name": result.stem,
        "markdown": result.markdown,
        "preview_markdown": markdown_with_data_uris(result),
        "image_dir": result.image_dir,
        "images": [
            {"file_name": img.file_name, "mime": img.mime, "size": len(img.data)}
            for img in result.images
        ],
        "counts": {
            "paragraphs": result.paragraph_count,
            "tables": result.table_count,
            "headings": result.heading_count,
            "images": result.image_count,
        },
        "skipped": [
            {"kind": kind, "label": SKIP_LABELS[kind], "count": count}
            for kind, count in result.skipped
        ],
    }


def error_code(exc: BaseException) -> ErrorCode:
    if isinstance(exc, EmptyInputError):
        return "empty"
    if isinstance(exc, InputTooLargeError):
        return "too_large"
    if isinstance(exc, DrmProtectedError):
        return "drm"
    if isinstance(exc, EncryptedDocumentError):
        return "encrypted"
    if isinstance(exc, UnsupportedHwpError):
        return "unsupported"
    if isinstance(exc, NotHwpFileError):
        return "not_hwp"
    return "convert_failed"


def convert_to_response(data: bytes, filename: str) -> tuple[int, dict[str, Any]]:
    """성공 (200, payload), 실패 (status, {"error": {code, message}}). 예외 전파 없음."""
    try:
        result = convert_bytes(data, filename)
    except Exception as exc:
        code = error_code(exc)
        return STATUS_BY_CODE[code], {"error": {"code": code, "message": str(exc)}}
    return 200, to_payload(result)
