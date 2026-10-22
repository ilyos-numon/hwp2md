"""HWPX Contents/header.xml -> paraPr id 별 개요(OUTLINE) 수준."""

from __future__ import annotations

from dataclasses import dataclass

from lxml import etree

from ..errors import Hwp2mdError

NS_HH = "http://www.hancom.co.kr/hwpml/2011/head"
NS_HP = "http://www.hancom.co.kr/hwpml/2011/paragraph"  # body.py 와 같은 값 (hp:switch)
HH_HEAD = f"{{{NS_HH}}}head"
HH_PARA_PR = f"{{{NS_HH}}}paraPr"
HH_HEADING = f"{{{NS_HH}}}heading"
HEADING_OUTLINE = "OUTLINE"  # heading/@type 값. 그 외 관찰값: NONE, NUMBER, BULLET
MAX_HEADING_LEVEL = 6


@dataclass(frozen=True)
class HeaderInfo:
    para_levels: dict[int, int]  # paraPr id → heading/@level (OUTLINE 인 것만)

    def heading_level(self, para_pr_id: int | None) -> int:
        """None 이거나 para_levels 에 없으면 0, 있으면 min(level + 1, MAX_HEADING_LEVEL)."""
        if para_pr_id is None:
            return 0
        lvl = self.para_levels.get(para_pr_id)
        if lvl is None:
            return 0
        return min(lvl + 1, MAX_HEADING_LEVEL)


EMPTY_HEADER = HeaderInfo(para_levels={})


def _make_parser() -> etree.XMLParser:
    """reader.make_parser 와 같은 옵션. 호출마다 새 인스턴스."""
    return etree.XMLParser(resolve_entities=False, no_network=True, huge_tree=False)


def _int(value: str | None) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def parse_header_xml(data: bytes) -> etree._Element:
    try:
        root = etree.fromstring(data, _make_parser())
    except etree.XMLSyntaxError as exc:
        raise Hwp2mdError(f"malformed header XML: {exc}") from exc
    if root.tag != HH_HEAD:
        raise Hwp2mdError(f"unexpected header root element: {root.tag}")
    return root


def parse_header(root: etree._Element) -> HeaderInfo:
    levels: dict[int, int] = {}
    for pp in root.iter(HH_PARA_PR):
        pid = _int(pp.get("id"))
        if pid is None:
            continue
        # 직계 자식 또는 hp:switch/hp:case 안의 첫 heading (문서 순서)
        h = next(pp.iter(HH_HEADING), None)
        if h is None:
            continue
        if h.get("type") != HEADING_OUTLINE:
            continue
        lvl = _int(h.get("level"))
        if lvl is None:
            continue
        levels[pid] = lvl
    return HeaderInfo(para_levels=levels)
