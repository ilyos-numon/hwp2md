"""실제 샘플에서 '현재 버려지는 요소'가 어디에 얼마나 있는지 센다 (내용은 읽지 않는다)."""
import collections, os, struct, unicodedata, zipfile
from pathlib import Path
from lxml import etree
import olefile
from hwp2md.detect import detect_format
from hwp2md.errors import Hwp2mdError
from hwp2md.hwp5.reader import parse_file_header, read_hwp5_package
from hwp2md.hwp5.records import iter_records
from hwp2md.hwp5.docinfo import parse_docinfo

CTRL_HEADER, LIST_HEADER, PARA_HEADER = 0x47, 0x48, 0x42
REC = {0x55: "picture", 0x54: "ole", 0x58: "eqedit", 0x56: "container", 0x4E: "line", 0x4F: "rect", 0x50: "ellipse",
       0x51: "arc", 0x52: "polygon", 0x53: "curve", 0x5A: "chart_data", 0x5C: "textart", 0x59: "form_object", 0x57: "ctrl_data"}
P = lambda p: unicodedata.normalize("NFC", str(p))

def hwp5(path):
    c = collections.Counter()
    ole = olefile.OleFileIO(str(path)); h = parse_file_header(ole.openstream("FileHeader").read())
    if h.distribution: c["배포용 문서"] += 1
    if h.encrypted: c["암호화 문서"] += 1
    if h.distribution or h.encrypted:
        ole.close(); return c
    ole.close()
    pkg = read_hwp5_package(path); di = parse_docinfo(pkg.docinfo)
    for k in pkg.bin_data: c["BinData ." + Path(k).suffix.lower().lstrip(".")] += 1
    for sec in pkg.sections:
        stack = []  # (level, ctrl_id)
        for r in iter_records(sec):
            while stack and stack[-1][0] >= r.level: stack.pop()
            anc = [cid for _, cid in stack]
            if r.tag_id == CTRL_HEADER:
                cid = r.payload[:4][::-1].decode("latin-1")
                c["ctrl " + cid] += 1
                stack.append((r.level, cid)); continue
            name = REC.get(r.tag_id)
            if name == "picture":
                c["그림: 표 칸 안" if "tbl " in anc else ("그림: 머리말/꼬리말 안" if {"head", "foot"} & set(anc) else ("그림: 각주/미주 안" if {"fn  ", "en  "} & set(anc) else "그림: 본문"))] += 1
            elif name: c["rec " + name] += 1
            if r.tag_id == LIST_HEADER and anc and anc[-1] == "gso ": c["글상자(도형 안 글)"] += 1
            if r.tag_id == PARA_HEADER and len(r.payload) >= 10:
                (sid,) = struct.unpack_from("<H", r.payload, 8)
                if 0 <= sid < len(di.para_shapes):
                    t = di.para_shapes[sid].heading_type
                    if t == 2: c["목록: 번호 문단"] += 1
                    if t == 3: c["목록: 글머리표 문단"] += 1
                    if t == 1: c["개요 문단(제목)"] += 1
    return c

HP_WATCH = {"pic", "container", "rect", "ellipse", "line", "arc", "polygon", "curve", "connectLine", "drawText", "ole", "chart",
            "equation", "footNote", "endNote", "header", "footer", "fieldBegin", "bookmark", "pageNum", "autoNum", "newNum",
            "hiddenComment", "textart", "compose", "dutmal", "btn", "checkBtn", "radioBtn", "comboBox", "edit", "listBox", "video"}

def hwpx(path):
    c = collections.Counter(); z = zipfile.ZipFile(path)
    parser = etree.XMLParser(resolve_entities=False, no_network=True)
    for n in z.namelist():
        if n.startswith("BinData/") and not n.endswith("/"): c["BinData ." + Path(n).suffix.lower().lstrip(".")] += 1
        if n.startswith("Chart"): c["Chart 엔트리"] += 1
    kinds = {}
    if "Contents/header.xml" in z.namelist():
        hr = etree.fromstring(z.read("Contents/header.xml"), parser)
        for pp in hr.iter("{*}paraPr"):
            h = next(pp.iter("{*}heading"), None)
            if h is not None: kinds[pp.get("id")] = h.get("type")
    for n in z.namelist():
        if not (n.startswith("Contents/section") and n.endswith(".xml")): continue
        root = etree.fromstring(z.read(n), parser)
        for el in root.iter():
            if not isinstance(el.tag, str): continue
            ln = etree.QName(el).localname
            anc = {etree.QName(a).localname for a in el.iterancestors() if isinstance(a.tag, str)}
            if ln == "pic":
                c["그림: 표 칸 안" if "tc" in anc else ("그림: 머리말/꼬리말 안" if {"header", "footer"} & anc else ("그림: 글상자/도형 안" if "drawText" in anc else "그림: 본문"))] += 1
            elif ln == "fieldBegin": c["field " + (el.get("type") or "?")] += 1
            elif ln == "drawText": c["글상자(도형 안 글)"] += 1
            elif ln in HP_WATCH: c["el " + ln] += 1
            if ln == "p":
                k = kinds.get(el.get("paraPrIDRef"))
                if k == "NUMBER": c["목록: 번호 문단"] += 1
                if k == "BULLET": c["목록: 글머리표 문단"] += 1
                if k == "OUTLINE": c["개요 문단(제목)"] += 1
    return c

files = sorted((p for p in Path("tests/fixtures").rglob("*") if p.is_file() and p.suffix.lower() in (".hwp", ".hwpx")), key=P)
rows = {}
for f in files:
    try:
        fmt = detect_format(f)
        c = hwp5(f) if fmt == "hwp5" else hwpx(f)
        rows[P(f)] = (fmt, c, "")
    except Hwp2mdError as e:
        rows[P(f)] = ("판독 불가", collections.Counter(), str(e).split(":")[0])
    except Exception as e:  # noqa: BLE001
        rows[P(f)] = ("판독 불가", collections.Counter(), type(e).__name__)

FOCUS = [
    ("표 칸 안 그림", ["그림: 표 칸 안"]),
    ("머리말·꼬리말 안 그림", ["그림: 머리말/꼬리말 안"]),
    ("글상자·도형 안 글/그림", ["글상자(도형 안 글)", "그림: 글상자/도형 안"]),
    ("그래프·차트 / OLE 개체", ["rec ole", "rec chart_data", "el ole", "el chart", "Chart 엔트리", "BinData .ole"]),
    ("수식", ["ctrl eqed", "rec eqedit", "el equation"]),
    ("하이퍼링크", ["ctrl %hlk", "field HYPERLINK"]),
    ("각주·미주", ["ctrl fn  ", "ctrl en  ", "el footNote", "el endNote"]),
    ("머리말·꼬리말", ["ctrl head", "ctrl foot", "el header", "el footer"]),
    ("번호·글머리표 목록", ["목록: 번호 문단", "목록: 글머리표 문단"]),
    ("개요(제목)", ["개요 문단(제목)"]),
    ("쪽 번호·자동 번호", ["ctrl pgnp", "ctrl atno", "ctrl nwno", "el pageNum", "el autoNum", "el newNum"]),
    ("날짜·기타 필드", ["ctrl %dte", "ctrl $dte", "ctrl %clk", "ctrl %pat", "field DATE", "field CLICK_HERE", "field PATH"]),
    ("책갈피·메모·숨은 설명", ["ctrl bokm", "ctrl tcmt", "el bookmark", "el hiddenComment"]),
    ("도형(선·사각형·타원 등)", ["rec line", "rec rect", "rec ellipse", "rec arc", "rec polygon", "rec curve", "el rect", "el ellipse", "el line", "el arc", "el polygon", "el curve", "el connectLine"]),
    ("묶음 개체", ["rec container", "el container"]),
    ("글맵시·양식 개체", ["rec textart", "rec form_object", "el textart", "el btn", "el checkBtn", "el radioBtn", "el comboBox", "el edit", "el listBox"]),
    ("WMF·EMF 등 비웹 이미지", ["BinData .wmf", "BinData .emf", "BinData .bmp", "BinData .tif", "BinData .tiff"]),
    ("배포용 문서", ["배포용 문서"]),
    ("암호화 문서", ["암호화 문서"]),
]

out = ["# 실제 샘플 구조 조사 (T-20261023-extract-dropped)", "",
       "문서 내용은 읽지 않고 구조(컨트롤·레코드·XML 요소) 개수만 셌다. 형식은 확장자가 아니라 내용으로 판별했다.",
       "갱신: `uv run python <스크래치>/inventory.py` (스크립트 원본은 이 태스크 PROGRESS 에 경로 기록).", "",
       "## 1. 요소별 집중 파일 (개발 완료 뒤 이 파일들로 검증한다)", "",
       "| 요소 | 개수 합 | 파일 (개수) |", "|---|---|---|"]
for label, keys in FOCUS:
    hits = []
    for path, (fmt, c, _) in rows.items():
        n = sum(c[k] for k in keys)
        if n: hits.append((path, n))
    total = sum(n for _, n in hits)
    cell = "<br>".join(f"`{p}` ({n})" for p, n in sorted(hits, key=lambda x: -x[1])) if hits else "**샘플 없음** → 합성 문서로만 검증"
    out.append(f"| {label} | {total} | {cell} |")
out += ["", "## 2. 파일별 형식과 원시 개수", "", "| 파일 | 형식(내용 기준) | 개수 |", "|---|---|---|"]
for path, (fmt, c, err) in rows.items():
    body = err or ", ".join(f"{k}={v}" for k, v in sorted(c.items()) if not k.startswith(("ctrl secd", "ctrl cold", "ctrl tbl ", "rec ctrl_data"))) or "—"
    out.append(f"| `{path}` | {fmt} | {body} |")
out += ["", "참고: `ctrl` 은 HWP 5.0 컨트롤 ID(`gso ` 그리기 개체, `%hlk` 하이퍼링크, `fn  `/`en  ` 각주/미주, `head`/`foot` 머리말/꼬리말, `pgnp` 쪽번호 위치, `atno` 자동번호, `nwno` 새 번호, `pghd` 감추기, `%pat` 경로 필드, `eqed` 수식, `bokm` 책갈피), `rec` 은 HWP 5.0 레코드, `el`·`field` 는 HWPX 요소·필드 종류."]
print("\n".join(out))
