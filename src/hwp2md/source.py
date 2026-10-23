"""Input source abstraction: a file path or the document bytes held in memory."""

from __future__ import annotations

import io
from pathlib import Path
from typing import BinaryIO

Source = Path | bytes
MEMORY_LABEL = "<memory>"


def source_label(src: Source) -> str:
    """Path → str(path), bytes → "<memory>" (오류 메시지의 위치 표시용)."""
    if isinstance(src, bytes):
        return MEMORY_LABEL
    return str(src)


def as_binary_io(src: Source) -> BinaryIO | str:
    """bytes → io.BytesIO(src), Path → str(src).
    bytes 를 그대로 olefile 에 넘기면 1536B 미만일 때 경로로 해석되므로 항상 감싼다."""
    if isinstance(src, bytes):
        return io.BytesIO(src)
    return str(src)
