"""Synthetic HWPX (OWPML zip) generator. Test-only. Mirrors synth_hwp5 fixtures so both formats can be cross-checked."""  # noqa: E501

from __future__ import annotations

import io
import zipfile
from collections.abc import Mapping, Sequence
from pathlib import Path
from xml.sax.saxutils import escape

from hwp2md.blocks import Paragraph
from hwp2md.hwpx.reader import HWPX_MIMETYPE, NS_HP, NS_HS
from synth_hwp5 import (  # 재정의 금지
    PNG_1X1,
    Item,
    SynthCell,
    SynthHeading,
    SynthImage,
    SynthTable,
    collect_images,
    has_heading,
)
from synth_items import (
    ExtItem,
    Run,
    SynthField,
    SynthHeaderFooter,
    SynthHidden,
    SynthLink,
    SynthNote,
    SynthRich,
)

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


def pic_xml(k: int, *, pic_id: int) -> str:
    return (
        f'<hp:pic id="{pic_id}" zOrder="0" numberingType="PICTURE" textWrap="TOP_AND_BOTTOM" '
        'textFlow="BOTH_SIDES" lock="0" dropcapstyle="None" href="" groupLevel="0" '
        f'instid="{pic_id + 1000}" reverse="0">'
        '<hp:offset x="0" y="0"/><hp:orgSz width="8196" height="3382"/>'
        '<hp:curSz width="0" height="0"/><hp:flip horizontal="0" vertical="0"/>'
        '<hp:rotationInfo angle="0" centerX="4098" centerY="1691" rotateimage="1"/>'
        "<hp:renderingInfo/>"
        f'<hc:img binaryItemIDRef="image{k}" bright="0" contrast="0" effect="REAL_PIC" alpha="0"/>'
        '<hp:imgRect/><hp:imgClip left="0" right="0" top="0" bottom="0"/>'
        '<hp:inMargin left="0" right="0" top="0" bottom="0"/>'
        '<hp:imgDim dimwidth="0" dimheight="0"/><hp:effects/>'
        '<hp:sz width="8196" widthRelTo="ABSOLUTE" height="3382" heightRelTo="ABSOLUTE" '
        'protect="0"/>'
        '<hp:pos treatAsChar="1" affectLSpacing="0" flowWithText="1" allowOverlap="0" '
        'holdAnchorAndSO="0" vertRelTo="PARA" horzRelTo="PARA" vertAlign="TOP" horzAlign="LEFT" '
        'vertOffset="0" horzOffset="0"/>'
        '<hp:outMargin left="0" right="0" top="0" bottom="0"/><hp:shapeComment/></hp:pic>'
    )


def pic_paragraph_xml(k: int, *, para_id: int, first: bool = False) -> str:
    return (
        f'<hp:p id="{para_id}" {P_ATTRS}>'
        + (SECPR_RUN if first else "")
        + f'<hp:run charPrIDRef="0">{pic_xml(k, pic_id=2000 + para_id)}</hp:run></hp:p>'
    )


def cell_xml(cell: SynthCell, images: Sequence[SynthImage] = ()) -> str:
    return (
        f"<hp:tc {TC_ATTRS}><hp:subList {SUBLIST_ATTRS}>"
        + "".join(
            paragraph_xml(t.text, para_id=0, para_pr_id=t.level)
            if isinstance(t, SynthHeading)
            else pic_paragraph_xml(images.index(t) + 1, para_id=0)
            if isinstance(t, SynthImage)
            else paragraph_xml(t, para_id=0)
            for t in (cell.paragraphs or ("",))
        )
        + "</hp:subList>"
        + f'<hp:cellAddr colAddr="{cell.col}" rowAddr="{cell.row}"/>'
        + f'<hp:cellSpan colSpan="{cell.col_span}" rowSpan="{cell.row_span}"/>'
        + '<hp:cellSz width="10000" height="1000"/>'
        + '<hp:cellMargin left="141" right="141" top="141" bottom="141"/></hp:tc>'
    )


def table_xml(
    table: SynthTable,
    *,
    para_id: int,
    first: bool = False,
    images: Sequence[SynthImage] = (),
) -> str:
    return (
        f'<hp:p id="{para_id}" {P_ATTRS}>'
        + (SECPR_RUN if first else "")
        + f'<hp:run charPrIDRef="0"><hp:tbl id="{1000 + para_id}" rowCnt="{table.rows}" '
        + f'colCnt="{table.cols}" {TBL_ATTRS}>'
        + "".join(
            "<hp:tr>" + "".join(cell_xml(c, images) for c in table.cells if c.row == r) + "</hp:tr>"
            for r in range(table.rows)
        )
        + "</hp:tbl></hp:run></hp:p>"
    )


HEADER_IMAGE = SynthImage(PNG_1X1, "png")  # SynthHeaderFooter(with_image=True) 의 그림


def all_images(items: Sequence[Item | ExtItem]) -> list[SynthImage]:
    """collect_images + 머리말·꼬리말 안 그림 (문서 순서, 중복 제외)."""
    found = collect_images([x for x in items if not isinstance(x, SynthHeaderFooter)])  # type: ignore[arg-type]
    for item in items:
        if isinstance(item, SynthHeaderFooter) and item.with_image and HEADER_IMAGE not in found:
            found.append(HEADER_IMAGE)
    return found


def _command_escape(url: str) -> str:
    """하이퍼링크 command 의 대상 이스케이프 (`\\` `:` `?` `;` `#` `|` 앞에 `\\`)."""
    return "".join("\\" + ch if ch in "\\:?;#|" else ch for ch in url)


def _t_run(text: str) -> str:
    return f'<hp:run charPrIDRef="0"><hp:t>{text_xml(text)}</hp:t></hp:run>'


def _field_runs(field_id: int, ftype: str, params: str, text: str) -> str:
    return (
        f'<hp:run charPrIDRef="0"><hp:ctrl><hp:fieldBegin id="{field_id}" type="{ftype}" '
        f'name="" editable="1" dirty="0" zorder="-1" fieldid="{field_id}">'
        f"<hp:parameters>{params}</hp:parameters></hp:fieldBegin></hp:ctrl></hp:run>"
        + _t_run(text)
        + f'<hp:run charPrIDRef="0"><hp:ctrl><hp:fieldEnd beginIDRef="{field_id}" '
        f'fieldid="{field_id}"/></hp:ctrl></hp:run>'
    )


def _sub_paragraphs_xml(paragraphs: Sequence[str], *, prefix: str = "") -> str:
    """subList 안 단락들. prefix 는 첫 단락 첫 run 안(예: autoNum ctrl)."""
    out = []
    for i, text in enumerate(paragraphs):
        head = prefix if i == 0 else ""
        out.append(
            f'<hp:p id="0" {P_ATTRS}><hp:run charPrIDRef="0">{head}'
            f"<hp:t>{text_xml(text)}</hp:t></hp:run></hp:p>"
        )
    return "".join(out)


def run_xml(run: Run, *, field_id: int) -> str:
    """SynthRich 의 run 하나 → hp:run XML (필드는 run 3개)."""
    if isinstance(run, str):
        return _t_run(run)
    if isinstance(run, SynthLink):
        params = (
            '<hp:integerParam name="Prop">0</hp:integerParam>'
            f'<hp:stringParam name="Command">{escape(_command_escape(run.url))};1;0;0;'
            "</hp:stringParam>"
            f'<hp:stringParam name="Path">{escape(run.url)}</hp:stringParam>'
            '<hp:stringParam name="Category">HWPHYPERLINK_TYPE_URL</hp:stringParam>'
        )
        return _field_runs(field_id, "HYPERLINK", params, run.text)
    if isinstance(run, SynthField):
        params = '<hp:stringParam name="Direction"></hp:stringParam>'
        return _field_runs(field_id, "CLICK_HERE", params, run.text)
    if isinstance(run, SynthNote):
        tag, num_type = (
            ("footNote", "FOOTNOTE") if run.kind == "footnote" else ("endNote", "ENDNOTE")
        )
        auto = f'<hp:ctrl><hp:autoNum num="1" numType="{num_type}"/></hp:ctrl>'
        return (
            f'<hp:run charPrIDRef="0"><hp:ctrl><hp:{tag} number="0" suffixChar="41" '
            f'instId="{field_id}"><hp:subList {SUBLIST_ATTRS}>'
            + _sub_paragraphs_xml(run.paragraphs, prefix=auto)
            + f"</hp:subList></hp:{tag}></hp:ctrl></hp:run>"
        )
    return (
        f'<hp:run charPrIDRef="0"><hp:equation id="{field_id}" zOrder="0" '
        'numberingType="EQUATION" version="Equation Version 60" baseLine="85" '
        'textColor="#000000" baseUnit="1000" lineMode="CHAR" font="HYhwpEQ">'
        "<hp:shapeComment>수식입니다.</hp:shapeComment>"
        f"<hp:script>{escape(run.script)}</hp:script></hp:equation></hp:run>"
    )


def rich_paragraph_xml(item: SynthRich, *, para_id: int, first: bool = False) -> str:
    return (
        f'<hp:p id="{para_id}" {P_ATTRS}>'
        + (SECPR_RUN if first else "")
        + "".join(run_xml(r, field_id=3000 + para_id * 100 + k) for k, r in enumerate(item.runs))
        + "</hp:p>"
    )


def header_footer_paragraph_xml(
    item: SynthHeaderFooter,
    *,
    para_id: int,
    first: bool = False,
    images: Sequence[SynthImage] = (),
) -> str:
    pic = (
        f'<hp:p id="0" {P_ATTRS}><hp:run charPrIDRef="0">'
        + pic_xml(images.index(HEADER_IMAGE) + 1, pic_id=4000 + para_id)
        + "</hp:run></hp:p>"
        if item.with_image
        else ""
    )
    return (
        f'<hp:p id="{para_id}" {P_ATTRS}>'
        + (SECPR_RUN if first else "")
        + f'<hp:run charPrIDRef="0"><hp:ctrl><hp:{item.kind} id="{para_id}" '
        f'applyPageType="BOTH"><hp:subList {SUBLIST_ATTRS}>'
        + _sub_paragraphs_xml(item.paragraphs)
        + pic
        + f"</hp:subList></hp:{item.kind}></hp:ctrl></hp:run></hp:p>"
    )


def hidden_paragraph_xml(item: SynthHidden, *, para_id: int, first: bool = False) -> str:
    return (
        f'<hp:p id="{para_id}" {P_ATTRS}>'
        + (SECPR_RUN if first else "")
        + f'<hp:run charPrIDRef="0"><hp:ctrl><hp:hiddenComment><hp:subList {SUBLIST_ATTRS}>'
        + _sub_paragraphs_xml(item.paragraphs)
        + "</hp:subList></hp:hiddenComment></hp:ctrl></hp:run></hp:p>"
    )


def ext_item_xml(
    item: object, *, para_id: int, first: bool, images: Sequence[SynthImage]
) -> str | None:
    """단락 안 요소 항목(SynthRich·SynthHeaderFooter·SynthHidden) → 단락 XML. 그 밖 None."""
    if isinstance(item, SynthRich):
        return rich_paragraph_xml(item, para_id=para_id, first=first)
    if isinstance(item, SynthHeaderFooter):
        return header_footer_paragraph_xml(item, para_id=para_id, first=first, images=images)
    if isinstance(item, SynthHidden):
        return hidden_paragraph_xml(item, para_id=para_id, first=first)
    return None


def section_xml(
    items: Sequence[Item | ExtItem], images: Sequence[SynthImage] | None = None
) -> bytes:
    imgs = all_images(items) if images is None else images
    body = "".join(
        ext
        if (ext := ext_item_xml(item, para_id=i, first=(i == 0), images=imgs)) is not None
        else paragraph_xml(item, para_id=i, first=(i == 0))
        if isinstance(item, str)
        else paragraph_xml(item.text, para_id=i, first=(i == 0), para_pr_id=item.level)
        if isinstance(item, SynthHeading)
        else pic_paragraph_xml(imgs.index(item) + 1, para_id=i, first=(i == 0))
        if isinstance(item, SynthImage)
        else table_xml(item, para_id=i, first=(i == 0), images=imgs)
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


def manifest_items(images: Sequence[SynthImage]) -> str:
    return "".join(
        f'<opf:item id="image{k}" href="BinData/image{k}.{img.ext}" '
        f'media-type="image/{img.ext}" isEmbeded="1"/>'
        for k, img in enumerate(images, 1)
    )


def hwpx_entries(
    items: Sequence[Item | ExtItem], *, more_sections: Sequence[Sequence[Item | ExtItem]] = ()
) -> dict[str, bytes]:
    """삽입 순서: mimetype, version.xml, META-INF/container.xml, Contents/content.hpf,
    Contents/header.xml, BinData/image{k}.{ext} (missing 제외),
    Contents/section0.xml, (Contents/section1.xml, …)."""
    sections: list[Sequence[Item | ExtItem]] = [items, *more_sections]
    n = len(sections)
    images: list[SynthImage] = []
    for sec in sections:
        for img in all_images(sec):
            if img not in images:
                images.append(img)
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
        + manifest_items(images)
        + "".join(
            f'<opf:item id="section{i}" href="Contents/section{i}.xml" '
            'media-type="application/xml"/>'
            for i in range(n)
        )
        + '</opf:manifest><opf:spine><opf:itemref idref="header" linear="yes"/>'
        + "".join(f'<opf:itemref idref="section{i}" linear="yes"/>' for i in range(n))
        + "</opf:spine></opf:package>"
    )
    header = header_xml(n, outline=any(has_heading(s) for s in sections))  # type: ignore[arg-type]
    entries: dict[str, bytes] = {
        "mimetype": HWPX_MIMETYPE,
        "version.xml": version.encode("utf-8"),
        "META-INF/container.xml": container.encode("utf-8"),
        "Contents/content.hpf": content.encode("utf-8"),
        "Contents/header.xml": header,
    }
    for k, img in enumerate(images, 1):
        if not img.missing:
            entries[f"BinData/image{k}.{img.ext}"] = img.data
    for i, sec_items in enumerate(sections):
        entries[f"Contents/section{i}.xml"] = section_xml(sec_items, images)
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


def build_hwpx(
    items: Sequence[Item | ExtItem], *, more_sections: Sequence[Sequence[Item | ExtItem]] = ()
) -> bytes:
    return build_zip(hwpx_entries(items, more_sections=more_sections))


def write_hwpx(
    path: Path,
    items: Sequence[Item | ExtItem],
    *,
    more_sections: Sequence[Sequence[Item | ExtItem]] = (),
) -> Path:
    """부모 디렉터리 생성 후 저장, path 반환."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(build_hwpx(items, more_sections=more_sections))
    return path


# 공용 fixture 추가 (synth_hwp5 의 FIXTURE_* 는 그대로 import 해서 쓴다)
FIXTURE_PARAGRAPHS_INLINE: list[str] = ["앞\t뒤", "첫 줄\n둘째 줄"]
EXPECTED_BLOCKS_INLINE = [Paragraph("앞 뒤"), Paragraph("첫 줄\n둘째 줄")]
EXPECTED_MARKDOWN_INLINE = "앞 뒤\n\n첫 줄\n둘째 줄\n"
