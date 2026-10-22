"""Synthetic HWPX (OWPML zip) generator. Test-only. Mirrors synth_hwp5 fixtures so both formats can be cross-checked."""  # noqa: E501

from __future__ import annotations

import io
import zipfile
from collections.abc import Mapping, Sequence
from pathlib import Path
from xml.sax.saxutils import escape

from hwp2md.blocks import Paragraph
from hwp2md.hwpx.reader import HWPX_MIMETYPE, NS_HP, NS_HS
from synth_hwp5 import Item, SynthCell, SynthHeading, SynthTable, has_heading  # 재정의 금지

NS_HC = "http://www.hancom.co.kr/hwpml/2011/core"
NS_HH = "http://www.hancom.co.kr/hwpml/2011/head"
NS_HV = "http://www.hancom.co.kr/hwpml/2011/version"
NS_OCF = "urn:oasis:names:tc:opendocument:xmlns:container"
NS_OPF = "http://www.idpf.org/2007/opf/"
XML_DECL = '<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>'
P_ATTRS = 'paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0"'
SECPR_RUN = (
    '<hp:run charPrIDRef="0">'
    '<hp:secPr id="" textDirection="HORIZONTAL" spaceColumns="1134" tabStop="8000" '
    'tabStopVal="4000" '
    'tabStopUnit="HWPUNIT" outlineShapeIDRef="1" memoShapeIDRef="0" textVerticalWidthHead="0" '
    'masterPageCnt="0"/>'
    '<hp:ctrl><hp:colPr id="" type="NEWSPAPER" layout="LEFT" colCount="1" sameSz="1" sameGap="0"/>'
    "</hp:ctrl>"
    "</hp:run>"
)  # 섹션 첫 단락의 첫 run. 리더가 무시해야 하는 요소를 실제 파일처럼 넣는다
TBL_ATTRS = (
    'zOrder="0" numberingType="TABLE" textWrap="TOP_AND_BOTTOM" textFlow="BOTH_SIDES" lock="0" '
    'dropcapstyle="None" pageBreak="CELL" repeatHeader="1" cellSpacing="0" borderFillIDRef="1" '
    'noAdjust="0"'
)
TC_ATTRS = 'name="" header="0" hasMargin="0" protect="0" editable="0" dirty="0" borderFillIDRef="1"'
SUBLIST_ATTRS = (
    'id="" textDirection="HORIZONTAL" lineWrap="BREAK" vertAlign="CENTER" linkListIDRef="0" '
    'linkListNextIDRef="0" textWidth="0" textHeight="0" hasTextRef="0" hasNumRef="0"'
)


def text_xml(text: str) -> str:
    """escape 후 "\\t" → <hp:tab/>, "\\n" → <hp:lineBreak/>."""
    return escape(text).replace("\t", "<hp:tab/>").replace("\n", "<hp:lineBreak/>")


def p_attrs(para_pr_id: int) -> str:
    return (
        f'paraPrIDRef="{para_pr_id}" styleIDRef="{para_pr_id}" pageBreak="0" columnBreak="0" '
        'merged="0"'
    )


def paragraph_xml(text: str, *, para_id: int, first: bool = False, para_pr_id: int = 0) -> str:
    if text == "":
        run = '<hp:run charPrIDRef="0"/>'
    else:
        run = f'<hp:run charPrIDRef="0"><hp:t>{text_xml(text)}</hp:t></hp:run>'
    return (
        f'<hp:p id="{para_id}" {p_attrs(para_pr_id)}>'
        + (SECPR_RUN if first else "")
        + run
        + "</hp:p>"
    )


def cell_xml(cell: SynthCell) -> str:
    return (
        f"<hp:tc {TC_ATTRS}><hp:subList {SUBLIST_ATTRS}>"
        + "".join(
            paragraph_xml(t.text, para_id=0, para_pr_id=t.level)
            if isinstance(t, SynthHeading)
            else paragraph_xml(t, para_id=0)
            for t in (cell.paragraphs or ("",))
        )
        + "</hp:subList>"
        + f'<hp:cellAddr colAddr="{cell.col}" rowAddr="{cell.row}"/>'
        + f'<hp:cellSpan colSpan="{cell.col_span}" rowSpan="{cell.row_span}"/>'
        + '<hp:cellSz width="10000" height="1000"/>'
        + '<hp:cellMargin left="141" right="141" top="141" bottom="141"/></hp:tc>'
    )


def table_xml(table: SynthTable, *, para_id: int, first: bool = False) -> str:
    return (
        f'<hp:p id="{para_id}" {P_ATTRS}>'
        + (SECPR_RUN if first else "")
        + f'<hp:run charPrIDRef="0"><hp:tbl id="{1000 + para_id}" rowCnt="{table.rows}" '
        + f'colCnt="{table.cols}" {TBL_ATTRS}>'
        + "".join(
            "<hp:tr>" + "".join(cell_xml(c) for c in table.cells if c.row == r) + "</hp:tr>"
            for r in range(table.rows)
        )
        + "</hp:tbl></hp:run></hp:p>"
    )


def section_xml(items: Sequence[Item]) -> bytes:
    body = "".join(
        paragraph_xml(item, para_id=i, first=(i == 0))
        if isinstance(item, str)
        else paragraph_xml(item.text, para_id=i, first=(i == 0), para_pr_id=item.level)
        if isinstance(item, SynthHeading)
        else table_xml(item, para_id=i, first=(i == 0))
        for i, item in enumerate(items)
    )
    return (
        XML_DECL
        + f'<hs:sec xmlns:hp="{NS_HP}" xmlns:hs="{NS_HS}" xmlns:hc="{NS_HC}">'
        + body
        + "</hs:sec>"
    ).encode("utf-8")


def para_pr_xml(i: int) -> str:
    return (
        f'<hh:paraPr id="{i}" tabPrIDRef="0" condense="0" fontLineHeight="0" snapToGrid="1" '
        'suppressLineNumbers="0" checked="0">'
        '<hh:align horizontal="JUSTIFY" vertical="BASELINE"/>'
        f'<hh:heading type="{"NONE" if i == 0 else "OUTLINE"}" idRef="0" '
        f'level="{max(i - 1, 0)}"/></hh:paraPr>'
    )


def style_xml(i: int) -> str:
    name, eng = ("바탕글", "Normal") if i == 0 else (f"개요 {i}", f"Outline {i}")
    return (
        f'<hh:style id="{i}" type="PARA" name="{name}" engName="{eng}" paraPrIDRef="{i}" '
        f'charPrIDRef="0" nextStyleIDRef="{i}" langID="1042" lockForm="0"/>'
    )


def header_xml(section_count: int, *, outline: bool) -> bytes:
    n = section_count
    begin = '<hh:beginNum page="1" footnote="1" endnote="1" pic="1" tbl="1" equation="1"/>'
    if not outline:
        return (
            XML_DECL
            + f'<hh:head xmlns:hh="{NS_HH}" version="1.5" secCnt="{n}">'
            + begin
            + "<hh:refList/></hh:head>"
        ).encode("utf-8")
    return (
        XML_DECL
        + f'<hh:head xmlns:hh="{NS_HH}" xmlns:hp="{NS_HP}" version="1.5" secCnt="{n}">'
        + begin
        + '<hh:refList><hh:paraProperties itemCnt="8">'
        + "".join(para_pr_xml(i) for i in range(8))
        + "</hh:paraProperties>"
        + '<hh:styles itemCnt="8">'
        + "".join(style_xml(i) for i in range(8))
        + "</hh:styles></hh:refList></hh:head>"
    ).encode("utf-8")


def hwpx_entries(
    items: Sequence[Item], *, more_sections: Sequence[Sequence[Item]] = ()
) -> dict[str, bytes]:
    """삽입 순서: mimetype, version.xml, META-INF/container.xml, Contents/content.hpf,
    Contents/header.xml, Contents/section0.xml, (Contents/section1.xml, …)."""
    sections: list[Sequence[Item]] = [items, *more_sections]
    n = len(sections)
    version = (
        XML_DECL
        + f'<hv:HCFVersion xmlns:hv="{NS_HV}" tagetApplication="WORDPROCESSOR" major="5" '
        + 'minor="1" micro="1" buildNumber="0" os="1" xmlVersion="1.5" '
        + 'application="hwp2md-synth" appVersion="0"/>'
    )
    container = (
        XML_DECL
        + f'<ocf:container xmlns:ocf="{NS_OCF}"><ocf:rootfiles>'
        + '<ocf:rootfile full-path="Contents/content.hpf" '
        + 'media-type="application/hwpml-package+xml"/>'
        + "</ocf:rootfiles></ocf:container>"
    )
    content = (
        XML_DECL
        + f'<opf:package xmlns:opf="{NS_OPF}" version="" unique-identifier="" id="">'
        + "<opf:metadata><opf:title/><opf:language/></opf:metadata><opf:manifest>"
        + '<opf:item id="header" href="Contents/header.xml" media-type="application/xml"/>'
        + "".join(
            f'<opf:item id="section{i}" href="Contents/section{i}.xml" '
            'media-type="application/xml"/>'
            for i in range(n)
        )
        + '</opf:manifest><opf:spine><opf:itemref idref="header" linear="yes"/>'
        + "".join(f'<opf:itemref idref="section{i}" linear="yes"/>' for i in range(n))
        + "</opf:spine></opf:package>"
    )
    header = header_xml(n, outline=any(has_heading(s) for s in sections))
    entries: dict[str, bytes] = {
        "mimetype": HWPX_MIMETYPE,
        "version.xml": version.encode("utf-8"),
        "META-INF/container.xml": container.encode("utf-8"),
        "Contents/content.hpf": content.encode("utf-8"),
        "Contents/header.xml": header,
    }
    for i, sec_items in enumerate(sections):
        entries[f"Contents/section{i}.xml"] = section_xml(sec_items)
    return entries


def build_zip(entries: Mapping[str, bytes]) -> bytes:
    """Mapping 순서대로 기록. mimetype 만 STORED. 결정적 바이트."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, data in entries.items():
            zf.writestr(
                zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0)),
                data,
                compress_type=(zipfile.ZIP_STORED if name == "mimetype" else zipfile.ZIP_DEFLATED),
            )
    return buf.getvalue()


def build_hwpx(items: Sequence[Item], *, more_sections: Sequence[Sequence[Item]] = ()) -> bytes:
    return build_zip(hwpx_entries(items, more_sections=more_sections))


def write_hwpx(
    path: Path, items: Sequence[Item], *, more_sections: Sequence[Sequence[Item]] = ()
) -> Path:
    """부모 디렉터리 생성 후 저장, path 반환."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(build_hwpx(items, more_sections=more_sections))
    return path


# 공용 fixture 추가 (synth_hwp5 의 FIXTURE_* 는 그대로 import 해서 쓴다)
FIXTURE_PARAGRAPHS_INLINE: list[str] = ["앞\t뒤", "첫 줄\n둘째 줄"]
EXPECTED_BLOCKS_INLINE = [Paragraph("앞 뒤"), Paragraph("첫 줄\n둘째 줄")]
EXPECTED_MARKDOWN_INLINE = "앞 뒤\n\n첫 줄\n둘째 줄\n"
