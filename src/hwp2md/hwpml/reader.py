"""HWPML 2.x (.hml) reader: XML text (UTF-8 / UTF-16 BOM) -> blocks.

DTD 는 파서에 넘기지 않는다. 내부 부분집합의 리터럴 일반 엔티티(예: nbsp)만 직접 치환하고
DOCTYPE 을 지운 뒤, HWPX 와 같은 보안 옵션의 파서로 읽는다."""

from __future__ import annotations

import base64
import binascii
import re
import zlib
from pathlib import Path

from lxml import etree

from ..blocks import Block, Image
from ..errors import Hwp2mdError
from ..hwpx.reader import make_parser
from ..images import ImageNamer, normalize_ext, sniff_ext
from ..ole import OleOutcome, ole_to_outcome, unwrap_hwpx_ole
from ..skips import SkipCounter
from ..source import Source
from .body import DocContext, HeadInfo, parse_body, parse_head

HWPML_ROOT = "HWPML"
MAX_HWPML_BYTES = 50 * 1024 * 1024  # 입력 전체 상한 (메모리 API 상한과 같다)
MAX_BINDATA_BYTES = 50 * 1024 * 1024  # Base64 를 푼(또는 압축을 푼) BINDATA 하나의 상한
HEAD_BYTES = 1024  # 판별에 보는 앞부분 (BOM 제외)
UNSUPPORTED_DTD = "unsupported DTD in HWPML"
CFB_MAGIC = bytes.fromhex("D0CF11E0A1B11AE1")
_PREDEFINED = frozenset({"lt", "gt", "amp", "apos", "quot"})
_BOMS: tuple[tuple[bytes, str], ...] = (
    (b"\xef\xbb\xbf", "utf-8"),
    (b"\xff\xfe", "utf-16-le"),
    (b"\xfe\xff", "utf-16-be"),
)
_NAME = r"[A-Za-z_][\w.\-]*"
_DOCTYPE = re.compile(rf"<!DOCTYPE\s+{_NAME}\s*(?:\[(.*)\])?\s*>\Z", re.S)
_ENTITY_DECL = re.compile(rf"<!ENTITY\s+({_NAME})\s+(?:\"([^\"]*)\"|'([^']*)')\s*>")
_CHAR_REF = re.compile(r"&#(?:x([0-9a-fA-F]{1,6})|([0-9]{1,7}));")
_ENTITY_REF = re.compile(rf"&({_NAME});")
_WS = " \t\r\n"


def _split_bom(data: bytes) -> tuple[bytes, str]:
    for bom, encoding in _BOMS:
        if data.startswith(bom):
            return data[len(bom) :], encoding
    return data, "utf-8"


def _doctype_end(s: str, start: int) -> int | None:
    """s[start:] 가 "<!DOCTYPE" 로 시작할 때 닫는 ">" 다음 위치.
    따옴표·[ ]·주석 안의 ">" 는 건너뛴다."""
    i = start + len("<!DOCTYPE")
    depth = 0
    quote = ""
    while i < len(s):
        ch = s[i]
        if quote:
            if ch == quote:
                quote = ""
        elif s.startswith("<!--", i):
            end = s.find("-->", i + 4)
            if end < 0:
                return None
            i = end + 3
            continue
        elif ch in "\"'":
            quote = ch
        elif ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
        elif ch == ">" and depth <= 0:
            return i + 1
        i += 1
    return None


def _scan_prolog(s: str) -> tuple[int, tuple[int, int] | None] | None:
    """(루트 시작 태그 위치, DOCTYPE 범위 또는 None). 프롤로그가 끝나지 않으면 None."""
    i = 0
    doctype: tuple[int, int] | None = None
    while True:
        while i < len(s) and s[i] in _WS:
            i += 1
        if s.startswith("<?", i):
            end = s.find("?>", i + 2)
            if end < 0:
                return None
            i = end + 2
        elif s.startswith("<!--", i):
            end = s.find("-->", i + 4)
            if end < 0:
                return None
            i = end + 3
        elif s.startswith("<!DOCTYPE", i):
            dt_end = _doctype_end(s, i)
            if dt_end is None:
                return None
            doctype = (i, dt_end)
            i = dt_end
        else:
            return i, doctype


def _is_root_tag(s: str, pos: int) -> bool:
    tag = "<" + HWPML_ROOT
    if not s.startswith(tag, pos):
        return False
    nxt = s[pos + len(tag) : pos + len(tag) + 1]
    return nxt in ("", ">", "/") or nxt in _WS


def looks_like_hwpml(head: bytes) -> bool:
    """BOM 을 건너뛴 앞 HEAD_BYTES 바이트에서 프롤로그(XML 선언·주석·PI·DOCTYPE) 다음 루트가
    <HWPML 이면 True."""
    body, encoding = _split_bom(head)
    text = body[:HEAD_BYTES].decode(encoding, errors="ignore")
    scanned = _scan_prolog(text)
    return scanned is not None and _is_root_tag(text, scanned[0])


def _literal_value(raw: str) -> str:
    """문자 참조만 푼다. 그 밖의 &·%·< 가 있으면 지원하지 않는 DTD."""
    if any(ch in _CHAR_REF.sub("", raw) for ch in "&%<"):
        raise Hwp2mdError(UNSUPPORTED_DTD)

    def char(m: re.Match[str]) -> str:
        code = int(m.group(1), 16) if m.group(1) else int(m.group(2))
        if not 0 < code <= 0x10FFFF:
            raise Hwp2mdError(UNSUPPORTED_DTD)
        return chr(code)

    return _CHAR_REF.sub(char, raw)


def _parse_internal_subset(subset: str) -> dict[str, str]:
    """리터럴 일반 엔티티 선언과 주석만 받는다. 이름 → 값(문자 참조를 푼 글자)."""
    entities: dict[str, str] = {}
    i = 0
    while i < len(subset):
        if subset[i] in _WS:
            i += 1
            continue
        if subset.startswith("<!--", i):
            end = subset.find("-->", i + 4)
            if end < 0:
                raise Hwp2mdError(UNSUPPORTED_DTD)
            i = end + 3
            continue
        m = _ENTITY_DECL.match(subset, i)
        if m is None:
            raise Hwp2mdError(UNSUPPORTED_DTD)
        raw = m.group(2) if m.group(2) is not None else m.group(3)
        value = _literal_value(raw)
        if m.group(1) not in _PREDEFINED:
            entities.setdefault(m.group(1), value)  # XML 규칙: 처음 선언이 이긴다
        i = m.end()
    return entities


def _parse_doctype(doctype: str) -> dict[str, str]:
    m = _DOCTYPE.match(doctype)
    if m is None:  # 외부 식별자(SYSTEM·PUBLIC) 또는 알 수 없는 형식
        raise Hwp2mdError(UNSUPPORTED_DTD)
    return _parse_internal_subset(m.group(1) or "")


def _substitute(text: str, entities: dict[str, str]) -> str:
    if not entities:
        return text
    encoded = {name: "".join(f"&#{ord(ch)};" for ch in v) for name, v in entities.items()}
    growth = sum(
        text.count(f"&{name};") * max(len(rep) - len(name) - 2, 0) for name, rep in encoded.items()
    )
    if len(text) + growth > MAX_HWPML_BYTES * 2:
        raise Hwp2mdError(f"HWPML too large after entity expansion: {len(text) + growth} chars")

    def rep(m: re.Match[str]) -> str:
        return encoded.get(m.group(1), m.group(0))

    return _ENTITY_REF.sub(rep, text)


def prepare_xml(data: bytes) -> bytes:
    """BOM·UTF-16 → UTF-8, XML 선언 제거, 내부 리터럴 엔티티 치환, DOCTYPE 제거.
    외부 엔티티·파라미터 엔티티·그 밖의 선언 → Hwp2mdError("unsupported DTD in HWPML")."""
    body, encoding = _split_bom(data)
    try:
        text = body.decode(encoding)
    except UnicodeDecodeError as exc:
        raise Hwp2mdError(f"malformed HWPML: {exc.reason} ({encoding})") from exc
    if text.startswith("<?xml"):
        end = text.find("?>")
        if end >= 0:
            text = text[end + 2 :]
    scanned = _scan_prolog(text)
    if scanned is None:
        raise Hwp2mdError("malformed HWPML: unterminated prolog")
    _, span = scanned
    if span is not None:
        entities = _parse_doctype(text[span[0] : span[1]])
        text = text[: span[0]] + _substitute(text[span[1] :], entities)
    return text.encode("utf-8")


def parse_hwpml(data: bytes) -> etree._Element:
    try:
        root = etree.fromstring(prepare_xml(data), make_parser())
    except etree.XMLSyntaxError as exc:
        raise Hwp2mdError(f"malformed HWPML: {exc}") from exc
    if root.tag != HWPML_ROOT:
        raise Hwp2mdError(f"unexpected root element: {root.tag}")
    return root


def _inflate_if_needed(data: bytes, label: str) -> bytes:
    """이미지 시그니처가 아니면 raw deflate 를 시도한다. 실패하면 원래 바이트."""
    if sniff_ext(data) is not None:
        return data
    d = zlib.decompressobj(-15)
    try:
        out = d.decompress(data, MAX_BINDATA_BYTES + 1)
    except zlib.error:
        return data
    if len(out) > MAX_BINDATA_BYTES:
        raise Hwp2mdError(f"binary item too large: {label} (> {MAX_BINDATA_BYTES} bytes)")
    if not d.eof:
        return data
    return out


class BinDataStore:
    """IMAGE@BinItem(BINDATALIST 안 1부터 순서) → BINITEM → TAIL/BINDATASTORAGE/BINDATA@Id."""

    def __init__(self, root: etree._Element, skips: SkipCounter | None = None) -> None:
        self._skips = skips
        self._items: dict[int, etree._Element] = {}
        bin_list = root.find("HEAD/MAPPINGTABLE/BINDATALIST")
        if bin_list is not None:
            for k, item in enumerate(bin_list.iterchildren("BINITEM"), 1):
                self._items[k] = item
        self._data: dict[str, etree._Element] = {}
        storage = root.find("TAIL/BINDATASTORAGE")
        if storage is not None:
            for bd in storage.iterchildren("BINDATA"):
                bid = (bd.get("Id") or "").strip()
                if bid and bid not in self._data:
                    self._data[bid] = bd
        self._namer = ImageNamer()
        self._cache: dict[str, Image | None] = {}

    def _item(self, ref: str) -> etree._Element | None:
        try:
            return self._items.get(int(ref))
        except ValueError:
            return None

    def resolve(self, ref: str) -> Image | None:
        item = self._item(ref)
        if item is None:
            return None
        if (item.get("Type") or "").strip().lower() == "link":
            if self._skips is not None:
                self._skips.add("image_link")
            return None
        bid = (item.get("BinData") or "").strip()
        if bid not in self._cache:
            self._cache[bid] = self._load(bid, item.get("Format"))
        return self._cache[bid]

    def resolve_ole(self, ref: str) -> OleOutcome:
        """OLE@BinItem → BINDATA(CFB. 길이 접두·raw deflate 허용) → 차트·이미지·건너뜀."""
        item = self._item(ref)
        if item is None or (item.get("Type") or "").strip().lower() == "link":
            return OleOutcome((), "ole")
        bid = (item.get("BinData") or "").strip()
        raw = self._raw(bid)
        if raw is None:
            return OleOutcome((), "ole")
        return ole_to_outcome(_ole_bytes(raw, f"BINDATA {bid}"), bid, self._make_image)

    def _make_image(self, key: str, data: bytes) -> Image:
        return Image(file_name=self._namer.name_for(key, normalize_ext(None, data)), data=data)

    def _raw(self, bid: str) -> bytes | None:
        """BINDATA Base64 를 푼 바이트. 없거나 풀 수 없거나 비면 None."""
        bd = self._data.get(bid)
        if bd is None:
            return None
        encoding = (bd.get("Encoding") or "Base64").strip().lower()
        if encoding != "base64":
            return None
        label = f"BINDATA {bid}"
        b64 = "".join((bd.text or "").split())
        estimated = len(b64) * 3 // 4
        if estimated > MAX_BINDATA_BYTES + 2:
            raise Hwp2mdError(f"binary item too large: {label} ({estimated} bytes)")
        try:
            raw = base64.b64decode(b64, validate=True)
        except (binascii.Error, ValueError):
            return None
        if len(raw) > MAX_BINDATA_BYTES:
            raise Hwp2mdError(f"binary item too large: {label} ({len(raw)} bytes)")
        return raw or None

    def _load(self, bid: str, fmt: str | None) -> Image | None:
        raw = self._raw(bid)
        if raw is None:
            return None
        data = _inflate_if_needed(raw, f"BINDATA {bid}")
        if not data:  # 압축 해제 결과 0바이트 → 본체 없는 그림
            return None
        return Image(file_name=self._namer.name_for(bid, normalize_ext(fmt, data)), data=data)


def _ole_bytes(raw: bytes, label: str) -> bytes:
    """CFB 그대로, 길이 접두 CFB, 또는 raw deflate 된 것 → CFB 바이트(아니면 받은 그대로)."""
    for cand in (raw, unwrap_hwpx_ole(raw)):
        if cand.startswith(CFB_MAGIC):
            return cand
    return unwrap_hwpx_ole(_inflate_if_needed(raw, label))


def _read_source(path: Source) -> bytes:
    if isinstance(path, bytes):
        size = len(path)
    else:
        size = Path(path).stat().st_size
    if size > MAX_HWPML_BYTES:
        raise Hwp2mdError(f"HWPML too large: {size} bytes")
    return path if isinstance(path, bytes) else Path(path).read_bytes()


def read_blocks(path: Source, skips: SkipCounter | None = None) -> list[Block]:
    """skips: 건너뛴 요소를 셀 카운터 (외부 연결 그림·머리말·숨은 설명·OLE 등).
    각주·미주 Note 블록은 모든 섹션 뒤에 둔다."""
    root = parse_hwpml(_read_source(path))
    head = root.find("HEAD")
    counter = SkipCounter() if skips is None else skips
    store = BinDataStore(root, counter)
    ctx = DocContext(
        head=parse_head(head) if head is not None else HeadInfo(),
        resolve_image=store.resolve,
        resolve_ole=store.resolve_ole,
        skips=counter,
    )
    return parse_body(root.iterfind("BODY/SECTION"), ctx)
