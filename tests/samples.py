"""실제 샘플 선정 규칙. 기존 테스트는 LEGACY_* 만 쓰고, 새 샘플은 내용 기준 classify 로 다룬다."""

from __future__ import annotations

import collections
import functools
import struct
import unicodedata
import zipfile
from pathlib import Path
from typing import Literal

import olefile
from lxml import etree

from hwp2md.hwp5.docinfo import parse_docinfo
from hwp2md.hwp5.reader import parse_file_header, read_hwp5_package
from hwp2md.hwp5.records import iter_records

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


# --- S24: 구조 탐색 (내용은 읽지 않고 컨트롤·레코드·XML 요소 개수만 센다) ---

PROBE_KEYS: tuple[str, ...] = (
    "cell_image",
    "body_image",
    "header_footer",
    "header_footer_image",
    "textbox",
    "ole",
    "equation",
    "hyperlink_web",
    "footnote",
    "endnote",
    "numbered",
    "bullet",
    "field_clk",
    "distribution",
    "hwpml_table",
    "hwpml_picture",
    "hwpml_header_footer",
    "bmp",
)

_CTRL_HEADER, _LIST_HEADER, _PARA_HEADER, _PARA_TEXT = 0x47, 0x48, 0x42, 0x43
_REC_PICTURE, _REC_OLE = 0x55, 0x54
_WEB_PREFIXES = ("http://", "https://", "mailto:")
_EXT_UTF16_CODES = frozenset({1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, *range(14, 24)})


def _nfc(path: Path) -> str:
    return unicodedata.normalize("NFC", str(path))


def _unescape_command(command: str) -> str:
    return command.replace("\\:", ":")


def _hwp5_command(payload: bytes) -> str:
    """필드 컨트롤 헤더의 명령 문자열 (ctrl id 4 + 속성 4 + 기타 1 + 길이 2 + UTF-16LE)."""
    if len(payload) < 11:
        return ""
    (length,) = struct.unpack_from("<H", payload, 9)
    return _unescape_command(payload[11 : 11 + 2 * length].decode("utf-16-le", errors="ignore"))


def _para_text(payload: bytes) -> str:
    """PARA_TEXT 레코드의 글자만 (확장·인라인 제어 문자는 8글자 분량을 건너뛴다)."""
    units = struct.unpack(f"<{len(payload) // 2}H", payload[: len(payload) // 2 * 2])
    out: list[str] = []
    i = 0
    while i < len(units):
        u = units[i]
        if u in _EXT_UTF16_CODES:
            i += 8
            continue
        if u >= 32:
            out.append(chr(u))
        i += 1
    return "".join(out)


def _walk_hwp5(path: Path) -> tuple[collections.Counter[str], dict[str, list[str]]]:
    counts: collections.Counter[str] = collections.Counter()
    texts: dict[str, list[str]] = collections.defaultdict(list)
    ole = olefile.OleFileIO(str(path))
    try:
        header = parse_file_header(ole.openstream("FileHeader").read())
    finally:
        ole.close()
    if header.distribution:
        counts["distribution"] += 1
    if header.distribution or header.encrypted:
        return counts, texts
    pkg = read_hwp5_package(path)
    docinfo = parse_docinfo(pkg.docinfo)
    for name in pkg.bin_data:
        if Path(name).suffix.lower() == ".bmp":
            counts["bmp"] += 1
    for section in pkg.sections:
        stack: list[list] = []  # [level, ctrl_id, 목록 머리 본 적 있음]
        last_text = ""
        list_kind = ""
        for rec in iter_records(section):
            while stack and stack[-1][0] >= rec.level:
                stack.pop()
            anc = [entry[1] for entry in stack]
            if rec.tag_id == _CTRL_HEADER:
                cid = rec.payload[:4][::-1].decode("latin-1")
                stack.append([rec.level, cid, False])
                if cid in ("head", "foot"):
                    counts["header_footer"] += 1
                elif cid == "eqed":
                    counts["equation"] += 1
                elif cid == "fn  ":
                    counts["footnote"] += 1
                elif cid == "en  ":
                    counts["endnote"] += 1
                elif cid == "%hlk":
                    if _hwp5_command(rec.payload).lower().startswith(_WEB_PREFIXES):
                        counts["hyperlink_web"] += 1
                elif cid == "%clk":
                    counts["field_clk"] += 1
                    if last_text.strip():
                        texts["field_clk"].append(last_text)
                continue
            if rec.tag_id == _REC_PICTURE:
                if "tbl " in anc:
                    counts["cell_image"] += 1
                elif {"head", "foot"} & set(anc):
                    counts["header_footer_image"] += 1
                elif not {"fn  ", "en  "} & set(anc):
                    counts["body_image"] += 1
            elif rec.tag_id == _REC_OLE:
                counts["ole"] += 1
            elif rec.tag_id == _LIST_HEADER and anc and anc[-1] == "gso ":
                stack[-1][2] = True
                counts["textbox"] += 1
            elif rec.tag_id == _PARA_HEADER:
                last_text = ""
                list_kind = ""
                if len(rec.payload) >= 10:
                    (sid,) = struct.unpack_from("<H", rec.payload, 8)
                    if 0 <= sid < len(docinfo.para_shapes):
                        kind = docinfo.para_shapes[sid].heading_type
                        if kind == 2:
                            counts["numbered"] += 1
                            list_kind = "numbered"
                        elif kind == 3:
                            counts["bullet"] += 1
                            list_kind = "bullet"
            elif rec.tag_id == _PARA_TEXT:
                last_text = _para_text(rec.payload)
                if list_kind:
                    texts[list_kind].append(last_text)
                if not {"head", "foot"} & set(anc):
                    texts["body"].append(last_text)
                if {"head", "foot"} & set(anc):
                    texts["header_footer"].append(last_text)
                if any(e[1] == "gso " and e[2] for e in stack):
                    texts["textbox"].append(last_text)
    return counts, texts


def _own_run(t: etree._Element, p: etree._Element) -> bool:
    """t 의 가장 가까운 p 조상이 p 자신인지 (표·글상자 안 단락의 글자를 섞지 않기)."""
    return next(a for a in t.iterancestors() if etree.QName(a).localname == "p") is p


def _walk_hwpx(path: Path) -> tuple[collections.Counter[str], dict[str, list[str]]]:
    counts: collections.Counter[str] = collections.Counter()
    texts: dict[str, list[str]] = collections.defaultdict(list)
    parser = etree.XMLParser(resolve_entities=False, no_network=True)
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        counts["bmp"] += sum(
            1 for n in names if n.startswith("BinData/") and n.lower().endswith(".bmp")
        )
        kinds: dict[str, str] = {}
        if "Contents/header.xml" in names:
            head = etree.fromstring(z.read("Contents/header.xml"), parser)
            for pp in head.iter("{*}paraPr"):
                h = next(pp.iter("{*}heading"), None)
                if h is not None:
                    kinds[pp.get("id") or ""] = h.get("type") or ""
        for name in names:
            if not (name.startswith("Contents/section") and name.endswith(".xml")):
                continue
            root = etree.fromstring(z.read(name), parser)
            for el in root.iter():
                if not isinstance(el.tag, str):
                    continue
                ln = etree.QName(el).localname
                anc = {
                    etree.QName(a).localname for a in el.iterancestors() if isinstance(a.tag, str)
                }
                if ln == "pic":
                    if "tc" in anc:
                        counts["cell_image"] += 1
                    elif {"header", "footer"} & anc:
                        counts["header_footer_image"] += 1
                    elif "drawText" not in anc:
                        counts["body_image"] += 1
                elif ln in ("header", "footer"):
                    counts["header_footer"] += 1
                elif ln == "drawText":
                    counts["textbox"] += 1
                    texts["textbox"].extend("".join(p.itertext()) for p in el.iter("{*}p"))
                elif ln == "ole":
                    counts["ole"] += 1
                elif ln == "equation":
                    counts["equation"] += 1
                elif ln == "footNote":
                    counts["footnote"] += 1
                elif ln == "endNote":
                    counts["endnote"] += 1
                elif ln == "fieldBegin":
                    ftype = el.get("type")
                    if ftype == "CLICK_HERE":
                        counts["field_clk"] += 1
                    elif ftype == "HYPERLINK":
                        command = next(
                            (
                                _unescape_command(sp.text or "")
                                for sp in el.iter("{*}stringParam")
                                if sp.get("name") == "Command"
                            ),
                            "",
                        )
                        if command.lower().startswith(_WEB_PREFIXES):
                            counts["hyperlink_web"] += 1
                if ln in ("header", "footer"):
                    texts["header_footer"].extend("".join(p.itertext()) for p in el.iter("{*}p"))
                if ln == "p":
                    kind = kinds.get(el.get("paraPrIDRef") or "")
                    own = "".join(t.text or "" for t in el.iter("{*}t") if _own_run(t, el))
                    if kind == "NUMBER":
                        counts["numbered"] += 1
                        texts["numbered"].append(own)
                    elif kind == "BULLET":
                        counts["bullet"] += 1
                        texts["bullet"].append(own)
                    if not {"header", "footer"} & anc:
                        texts["body"].append("".join(el.itertext()))
    return counts, texts


def _walk_hwpml(path: Path) -> collections.Counter[str]:
    counts: collections.Counter[str] = collections.Counter()
    parser = etree.XMLParser(resolve_entities=False, no_network=True, huge_tree=True)
    root = etree.fromstring(path.read_bytes(), parser)
    for el in root.iter():
        if not isinstance(el.tag, str):
            continue
        ln = etree.QName(el).localname
        anc = {etree.QName(a).localname for a in el.iterancestors() if isinstance(a.tag, str)}
        if ln in ("HEADER", "FOOTER"):
            counts["hwpml_header_footer"] += 1
        elif ln == "TABLE" and not {"HEADER", "FOOTER"} & anc:
            counts["hwpml_table"] += 1
        elif ln == "PICTURE" and not {"HEADER", "FOOTER"} & anc:
            counts["hwpml_picture"] += 1
    return counts


@functools.cache
def _probe_all(path: Path) -> tuple[dict[str, int], dict[str, tuple[str, ...]]]:
    kind = classify(path)
    counts: collections.Counter[str] = collections.Counter()
    texts: dict[str, list[str]] = {}
    if kind == "hwp5":
        counts, texts = _walk_hwp5(path)
    elif kind == "hwpx":
        counts, texts = _walk_hwpx(path)
    elif kind == "hwpml":
        counts = _walk_hwpml(path)
    return (
        {key: counts[key] for key in PROBE_KEYS},
        {key: tuple(value) for key, value in texts.items()},
    )


def probe(path: Path) -> dict[str, int]:
    """요소별 개수. 형식은 확장자가 아니라 내용(classify)으로 판별하고, 못 읽는 종류는 모두 0."""
    return dict(_probe_all(path)[0])


def samples_with(feature: str) -> list[tuple[Path, int]]:
    """probe[feature] > 0 인 실제 샘플을 개수 내림차순(같으면 경로 순)으로."""
    if feature not in PROBE_KEYS:
        raise KeyError(feature)
    hits = [(p, probe(p)[feature]) for p in sorted(all_samples(), key=_nfc)]
    return sorted((hit for hit in hits if hit[1] > 0), key=lambda hit: -hit[1])


def probe_texts(path: Path, feature: str) -> list[str]:
    """글상자(textbox)·누름틀(field_clk)·머리말·꼬리말(header_footer) 안 단락 글자."""
    return list(_probe_all(path)[1].get(feature, ()))
