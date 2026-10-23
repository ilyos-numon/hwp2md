"""HWPX Contents/header.xml -> paraPr id 별 개요(OUTLINE) 수준, 번호·글머리표 목록 정의."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, cast, get_args

from lxml import etree

from ..errors import Hwp2mdError
from ..numbering import NumFormat

NS_HH = "http://www.hancom.co.kr/hwpml/2011/head"
NS_HP = "http://www.hancom.co.kr/hwpml/2011/paragraph"  # body.py 와 같은 값 (hp:switch)
HH_HEAD = f"{{{NS_HH}}}head"
HH_PARA_PR = f"{{{NS_HH}}}paraPr"
HH_HEADING = f"{{{NS_HH}}}heading"
HH_NUMBERING = f"{{{NS_HH}}}numbering"
HH_PARA_HEAD = f"{{{NS_HH}}}paraHead"
HH_BULLET = f"{{{NS_HH}}}bullet"
HEADING_OUTLINE = "OUTLINE"  # heading/@type 값. 그 외 관찰값: NONE, NUMBER, BULLET
HEADING_LIST: dict[str, Literal["bullet", "number"]] = {"NUMBER": "number", "BULLET": "bullet"}
MAX_HEADING_LEVEL = 6
MAX_LIST_DEPTH = 6
_NUM_FORMATS: frozenset[str] = frozenset(get_args(NumFormat))
# NumFormat 에 같은 이름이 없는 paraHead/@numFormat 값 중 대응이 있는 것. 그 밖은 DIGIT
_NUM_FORMAT_ALIASES: dict[str, NumFormat] = {"IDEOGRAPH": "HANJA_DIGIT"}


@dataclass(frozen=True)
class ListShape:
    kind: Literal["bullet", "number"]
    ref: int  # heading/@idRef — hh:numbering 또는 hh:bullet 의 id
    depth: int  # heading/@level (0부터, 0~6)


@dataclass(frozen=True)
class NumberingDef:
    templates: dict[int, str]  # paraHead/@level(1부터) → 형식 문자열("^1.")
    formats: dict[int, NumFormat]
    starts: dict[int, int]


@dataclass(frozen=True)
class HeaderInfo:
    para_levels: dict[int, int]  # paraPr id → heading/@level (OUTLINE 인 것만)
    lists: dict[int, ListShape] = field(default_factory=dict)  # paraPr id → NUMBER/BULLET
    numberings: dict[int, NumberingDef] = field(default_factory=dict)
    bullets: dict[int, str] = field(default_factory=dict)  # hh:bullet id → @char

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


def to_num_format(value: str | None) -> NumFormat:
    """paraHead/@numFormat("HANGUL_SYLLABLE" 등) → NumFormat. 모르는 값은 "DIGIT"."""
    key = (value or "").strip().upper()
    if key in _NUM_FORMATS:
        return cast(NumFormat, key)
    return _NUM_FORMAT_ALIASES.get(key, "DIGIT")


def parse_numberings(root: etree._Element) -> dict[int, NumberingDef]:
    """hh:numbering id → 수준별 형식 문자열·번호 모양·시작 번호.
    수준 시작 번호는 paraHead/@start, 1 미만이면 numbering/@start(1 이상일 때), 그 밖 1."""
    out: dict[int, NumberingDef] = {}
    for num in root.iter(HH_NUMBERING):
        nid = _int(num.get("id"))
        if nid is None or nid in out:
            continue
        base_start = _int(num.get("start"))
        templates: dict[int, str] = {}
        formats: dict[int, NumFormat] = {}
        starts: dict[int, int] = {}
        for head in num.iter(HH_PARA_HEAD):
            level = _int(head.get("level"))
            if level is None or level in templates:
                continue
            templates[level] = head.text or ""
            formats[level] = to_num_format(head.get("numFormat"))
            start = _int(head.get("start"))
            if start is None or start < 1:
                start = base_start if base_start is not None and base_start >= 1 else 1
            starts[level] = start
        out[nid] = NumberingDef(templates, formats, starts)
    return out


def parse_bullets(root: etree._Element) -> dict[int, str]:
    """hh:bullet id → 글머리표 문자."""
    out: dict[int, str] = {}
    for b in root.iter(HH_BULLET):
        bid = _int(b.get("id"))
        if bid is not None and bid not in out:
            out[bid] = b.get("char") or ""
    return out


def parse_header(root: etree._Element) -> HeaderInfo:
    levels: dict[int, int] = {}
    lists: dict[int, ListShape] = {}
    for pp in root.iter(HH_PARA_PR):
        pid = _int(pp.get("id"))
        if pid is None:
            continue
        # 직계 자식 또는 hp:switch/hp:case 안의 첫 heading (문서 순서)
        h = next(pp.iter(HH_HEADING), None)
        if h is None:
            continue
        htype = h.get("type")
        lvl = _int(h.get("level"))
        if htype == HEADING_OUTLINE:
            if lvl is None:
                continue
            levels[pid] = lvl
            continue
        kind = HEADING_LIST.get(htype or "")
        if kind is None:
            continue
        ref = _int(h.get("idRef"))
        depth = min(max(lvl or 0, 0), MAX_LIST_DEPTH)
        lists[pid] = ListShape(kind, 0 if ref is None else ref, depth)
    return HeaderInfo(
        para_levels=levels,
        lists=lists,
        numberings=parse_numberings(root),
        bullets=parse_bullets(root),
    )
