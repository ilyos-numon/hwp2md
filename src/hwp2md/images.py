"""Image helpers: output folder name, extension detection, sequential naming."""

from __future__ import annotations

IMAGE_DIR_SUFFIX = "_images"
_MAGIC: tuple[tuple[bytes, str], ...] = (
    (b"\x89PNG\r\n\x1a\n", "png"),
    (b"\xff\xd8\xff", "jpg"),
    (b"GIF87a", "gif"),
    (b"GIF89a", "gif"),
    (b"BM", "bmp"),
)


def image_dir_name(stem: str) -> str:
    return f"{stem}{IMAGE_DIR_SUFFIX}"


def sniff_ext(data: bytes) -> str | None:
    for magic, ext in _MAGIC:
        if data.startswith(magic):
            return ext
    return None


def normalize_ext(ext: str | None, data: bytes) -> str:
    """ext 를 strip() 후 앞의 '.' 제거·소문자. "" 이면 sniff_ext(data), 그것도 None 이면 "bin"."""
    norm = (ext or "").strip().removeprefix(".").lower()
    if norm:
        return norm
    return sniff_ext(data) or "bin"


class ImageNamer:
    """같은 key 는 같은 이름. 첫 등장 순서대로 img_001, img_002, …"""

    def __init__(self) -> None:
        self._names: dict[str, str] = {}

    def name_for(self, key: str, ext: str) -> str:
        name = self._names.get(key)
        if name is None:
            name = f"img_{len(self._names) + 1:03d}.{ext}"
            self._names[key] = name
        return name
