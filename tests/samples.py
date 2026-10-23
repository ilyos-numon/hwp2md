"""실제 샘플 선정 규칙. 기존 테스트는 LEGACY_* 만 쓰고, 새 샘플은 내용 기준 classify 로 다룬다."""

from __future__ import annotations

import unicodedata
from pathlib import Path
from typing import Literal

FIXTURES = Path(__file__).resolve().parent / "fixtures"

LEGACY_NAMES: tuple[str, ...] = (
    "form200005063113.hwp",
    "form210001070268.hwp",
    "(서식1) 비영리법인 현황 제출 양식.hwpx",
    "(서식2) 사업실적 및 사업계획 제출 양식.hwpx",
    "브라더 공공기관 보고서 양식.hwpx",
)
_LEGACY_NFC = frozenset(unicodedata.normalize("NFC", n) for n in LEGACY_NAMES)


def _legacy(paths: list[Path]) -> list[Path]:
    return [p for p in sorted(paths) if unicodedata.normalize("NFC", p.name) in _LEGACY_NFC]


LEGACY_HWP5: list[Path] = _legacy(list(FIXTURES.glob("*.hwp")))
LEGACY_HWPX: list[Path] = _legacy(list(FIXTURES.joinpath("hwpx").glob("*.hwpx")))
LEGACY_SAMPLES: list[Path] = LEGACY_HWP5 + LEGACY_HWPX

SampleClass = Literal["hwp5", "hwpx", "hwpml", "drm", "text", "unknown"]

_OLE_MAGIC = bytes.fromhex("d0cf11e0a1b11ae1")
_ZIP_MAGIC = b"PK\x03\x04"
_SKIP_NAMES = {"README.md", ".gitkeep"}


def _decode_head(head: bytes) -> str | None:
    if head.startswith((b"\xff\xfe", b"\xfe\xff")):
        return head.decode("utf-16", errors="ignore")
    try:
        return head.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        if exc.start >= len(head) - 3:  # 잘린 끝 바이트만 무시
            return head[: exc.start].decode("utf-8-sig", errors="ignore")
        return None


def _skip_doctype(s: str) -> str | None:
    depth = 0
    for i, ch in enumerate(s):
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
        elif ch == ">" and depth <= 0:
            return s[i + 1 :]
    return None


def _is_hwpml(text: str) -> bool:
    s = text.lstrip("\ufeff \t\r\n")
    while True:
        if s.startswith("<?"):
            end = s.find("?>")
            rest = s[end + 2 :] if end >= 0 else None
        elif s.startswith("<!--"):
            end = s.find("-->")
            rest = s[end + 3 :] if end >= 0 else None
        elif s.startswith("<!DOCTYPE"):
            rest = _skip_doctype(s)
        else:
            return s.startswith("<HWPML")
        if rest is None:
            return False
        s = rest.lstrip()


def classify(path: Path) -> SampleClass:
    with path.open("rb") as fh:
        head = fh.read(1024)
    if head[:2] == b"\x9b\x20" or b"DRMONE" in head:
        return "drm"
    if head.startswith(_OLE_MAGIC):
        return "hwp5"
    if head.startswith(_ZIP_MAGIC):
        return "hwpx"
    text = _decode_head(head)
    if text is None:
        return "unknown"
    if _is_hwpml(text):
        return "hwpml"
    if head and all(ch.isprintable() or ch in "\t\r\n" for ch in text):
        return "text"
    return "unknown"


def all_samples() -> list[Path]:
    return sorted(p for p in FIXTURES.rglob("*") if p.is_file() and p.name not in _SKIP_NAMES)
