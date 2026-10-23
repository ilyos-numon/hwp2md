"""HWPX binary items: Contents/content.hpf manifest + BinData/* zip entries -> Image."""

from __future__ import annotations

from collections.abc import Mapping

from lxml import etree

from ..blocks import Image
from ..images import ImageNamer, normalize_ext

HWPX_CONTENT_HPF = "Contents/content.hpf"
NS_OPF = "http://www.idpf.org/2007/opf/"
OPF_ITEM = f"{{{NS_OPF}}}item"
BIN_DATA_PREFIX = "BinData/"
CHART_PREFIX = "Chart/"
MAX_IMAGE_BYTES = 50 * 1024 * 1024


def parse_manifest(data: bytes) -> dict[str, str]:
    """opf:item 의 id → href (둘 다 있는 것만). 깨진 XML → {}."""
    # reader.make_parser() 와 같은 옵션 (reader 가 이 모듈을 import 하므로 순환을 피해 직접 만든다)
    parser = etree.XMLParser(resolve_entities=False, no_network=True, huge_tree=False)
    try:
        root = etree.fromstring(data, parser)
    except etree.XMLSyntaxError:
        return {}
    out: dict[str, str] = {}
    for item in root.iter(OPF_ITEM):
        item_id = item.get("id")
        href = item.get("href")
        if item_id and href:
            out[item_id] = href
    return out


class BinItemStore:
    """문서 하나당 인스턴스 하나. item_id → Image (같은 id 는 같은 file_name).
    charts: 차트 XML zip 엔트리 (키 = 엔트리 전체 이름, hp:chart/@chartIDRef 로 찾는다)."""

    def __init__(
        self,
        manifest: Mapping[str, str],
        entries: Mapping[str, bytes],
        charts: Mapping[str, bytes] | None = None,
    ) -> None:
        self._manifest = manifest
        self._entries = entries
        self._charts: Mapping[str, bytes] = {} if charts is None else charts
        self._namer = ImageNamer()
        self._cache: dict[str, Image | None] = {}

    def resolve(self, item_id: str) -> Image | None:
        if item_id in self._cache:
            return self._cache[item_id]
        image = self._resolve(item_id)
        self._cache[item_id] = image
        return image

    def raw(self, item_id: str) -> bytes | None:
        """바이너리 항목 원본 바이트 (OLE 등). 없으면 None."""
        name = self._entry_name(item_id)
        return None if name is None else self._entries[name]

    def chart(self, ref: str) -> bytes | None:
        """chartIDRef(zip 엔트리 경로) → 차트 XML 바이트. 없으면 None."""
        return self._charts.get(ref.lstrip("/"))

    def make_image(self, key: str, data: bytes) -> Image:
        """ole.ImageFactory: 그림 번호를 문서의 다른 그림과 같은 순서로 이어 붙인다."""
        return Image(file_name=self._namer.name_for(key, normalize_ext(None, data)), data=data)

    def _entry_name(self, item_id: str) -> str | None:
        href = self._manifest.get(item_id)
        if href is not None and href in self._entries:
            return href
        prefix = f"{BIN_DATA_PREFIX}{item_id}."
        return next((n for n in sorted(self._entries) if n.startswith(prefix)), None)

    def _resolve(self, item_id: str) -> Image | None:
        name = self._entry_name(item_id)
        if name is None:
            return None
        data = self._entries[name]
        if not data:  # 0바이트 본체 → 본체 없는 그림 (호출 쪽이 image_missing 으로 센다)
            return None
        base = name.rsplit("/", 1)[-1]
        ext = base.rsplit(".", 1)[1] if "." in base else None
        return Image(file_name=self._namer.name_for(item_id, normalize_ext(ext, data)), data=data)
