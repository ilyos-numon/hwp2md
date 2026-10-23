"""Synthetic HWPML 2.x (.hml) generator. Test-only. Mirrors synth_hwpx so formats can be cross-checked."""  # noqa: E501

from __future__ import annotations

import base64
from collections.abc import Sequence
from pathlib import Path
from xml.sax.saxutils import escape

from synth_hwp5 import (  # 재정의 금지
    Item,
    SynthCell,
    SynthHeading,
    SynthImage,
    SynthTable,
    collect_images,
)

NBSP = " "
DOCTYPE_NBSP = '<!DOCTYPE HWPML [\n\t<!ENTITY nbsp\t"&#160;">\n]>\n'
_ENCODINGS: dict[str, tuple[bytes, str]] = {
    "utf-8": (b"", "UTF-8"),
    "utf-16-le": (b"\xff\xfe", "UTF-16"),
    "utf-16-be": (b"\xfe\xff", "UTF-16"),
}


def text_xml(text: str, *, nbsp_entity: bool = False) -> str:
    """escape 후 "\\t" → <TAB/>, "\\n" → <LINEBREAK/>, (nbsp_entity 면) U+00A0 → &nbsp;."""
    out = escape(text).replace("\t", "<TAB/>").replace("\n", "<LINEBREAK/>")
    if nbsp_entity:
        out = out.replace(NBSP, "&nbsp;")
    return out


def paragraph_xml(text: str, *, para_shape: int = 0, nbsp_entity: bool = False) -> str:
    if text == "":
        inner = '<TEXT CharShape="0"/>'
    else:
        inner = f'<TEXT CharShape="0"><CHAR>{text_xml(text, nbsp_entity=nbsp_entity)}</CHAR></TEXT>'
    return f'<P ParaShape="{para_shape}" Style="{para_shape}">{inner}</P>'


def picture_xml(k: int) -> str:
    return (
        "<PICTURE>"
        '<SHAPEOBJECT InstId="0" Lock="false" NumberingType="Figure" TextWrap="TopAndBottom">'
        '<SIZE Height="3382" Width="8196"/></SHAPEOBJECT>'
        '<SHAPECOMPONENT GroupLevel="0" InstID="0"/>'
        '<IMAGERECT X0="0" Y0="0" X1="0" Y1="0"/>'
        f'<IMAGE Bright="0" Contrast="0" Effect="RealPic" BinItem="{k}"/>'
        "</PICTURE>"
    )


def picture_paragraph_xml(k: int) -> str:
    return f'<P ParaShape="0" Style="0"><TEXT CharShape="0">{picture_xml(k)}</TEXT></P>'


def cell_xml(cell: SynthCell, images: Sequence[SynthImage], *, nbsp_entity: bool) -> str:
    paras = "".join(
        paragraph_xml(t.text, para_shape=t.level, nbsp_entity=nbsp_entity)
        if isinstance(t, SynthHeading)
        else picture_paragraph_xml(images.index(t) + 1)
        if isinstance(t, SynthImage)
        else paragraph_xml(t, nbsp_entity=nbsp_entity)
        for t in (cell.paragraphs or ("",))
    )
    return (
        f'<CELL ColAddr="{cell.col}" RowAddr="{cell.row}" ColSpan="{cell.col_span}" '
        f'RowSpan="{cell.row_span}" Width="10000" Height="1000" Header="false" '
        'HasMargin="false" Protect="false" Editable="false" Dirty="false" BorderFill="1">'
        f'<PARALIST LineWrap="Break" TextDirection="0" VertAlign="Center">{paras}</PARALIST>'
        "</CELL>"
    )


def table_xml(table: SynthTable, images: Sequence[SynthImage], *, nbsp_entity: bool) -> str:
    rows = "".join(
        "<ROW>"
        + "".join(cell_xml(c, images, nbsp_entity=nbsp_entity) for c in table.cells if c.row == r)
        + "</ROW>"
        for r in range(table.rows)
    )
    return (
        '<P ParaShape="0" Style="0"><TEXT CharShape="0">'
        f'<TABLE PageBreak="Cell" RepeatHeader="true" RowCount="{table.rows}" '
        f'ColCount="{table.cols}" CellSpacing="0" BorderFill="1">'
        '<SHAPEOBJECT InstId="0" Lock="false" NumberingType="Table" TextWrap="TopAndBottom"/>'
        f"{rows}</TABLE></TEXT></P>"
    )


def para_shape_xml(i: int) -> str:
    heading = "None" if i == 0 else "Outline"
    return (
        f'<PARASHAPE Id="{i}" Align="Justify" Heading="0" HeadingType="{heading}" '
        f'Level="{max(i - 1, 0)}" TabDef="0"><PARAMARGIN Left="0" Right="0"/></PARASHAPE>'
    )


def head_xml(images: Sequence[SynthImage]) -> str:
    bin_items = "".join(
        f'<BINITEM Type="Embedding" BinData="{k}" Format="{img.ext}"/>'
        for k, img in enumerate(images, 1)
    )
    bin_list = f'<BINDATALIST Count="{len(images)}">{bin_items}</BINDATALIST>' if images else ""
    return (
        '<HEAD SecCnt="1"><DOCSUMMARY><TITLE>synth</TITLE></DOCSUMMARY>'
        '<DOCSETTING><BEGINNUMBER Page="1" Footnote="1" Endnote="1"/></DOCSETTING>'
        "<MAPPINGTABLE>"
        + bin_list
        + '<PARASHAPELIST Count="8">'
        + "".join(para_shape_xml(i) for i in range(8))
        + "</PARASHAPELIST></MAPPINGTABLE></HEAD>"
    )


def tail_xml(images: Sequence[SynthImage]) -> str:
    if not images:
        return ""
    datas = "".join(
        f'<BINDATA Id="{k}" Encoding="Base64" Size="{len(img.data)}">'
        + _wrapped_base64(img.data)
        + "</BINDATA>"
        for k, img in enumerate(images, 1)
        if not img.missing
    )
    return f"<TAIL><BINDATASTORAGE>{datas}</BINDATASTORAGE></TAIL>"


def _wrapped_base64(data: bytes) -> str:
    """실제 파일처럼 76자마다 줄바꿈."""
    b64 = base64.b64encode(data).decode("ascii")
    return "\n".join(b64[i : i + 76] for i in range(0, len(b64), 76))


def hwpml_text(
    items: Sequence[Item], *, doctype_nbsp: bool = False, decl_encoding: str = "UTF-8"
) -> str:  # noqa: E501
    images = collect_images(items)
    body = "".join(
        paragraph_xml(item, nbsp_entity=doctype_nbsp)
        if isinstance(item, str)
        else paragraph_xml(item.text, para_shape=item.level, nbsp_entity=doctype_nbsp)
        if isinstance(item, SynthHeading)
        else picture_paragraph_xml(images.index(item) + 1)
        if isinstance(item, SynthImage)
        else table_xml(item, images, nbsp_entity=doctype_nbsp)
        for item in items
    )
    return (
        f'<?xml version="1.0" encoding="{decl_encoding}"?>\n'
        + (DOCTYPE_NBSP if doctype_nbsp else "")
        + '<HWPML Version="2.1" Style2="embed">'
        + head_xml(images)
        + f'<BODY><SECTION Id="0">{body}</SECTION></BODY>'
        + tail_xml(images)
        + "</HWPML>"
    )


def build_hwpml(
    items: Sequence[Item], *, encoding: str = "utf-8", doctype_nbsp: bool = False
) -> bytes:
    """encoding: "utf-8" | "utf-16-le" | "utf-16-be" (UTF-16 은 BOM 을 붙인다).
    doctype_nbsp: nbsp 내부 엔티티를 선언하고 글자 안 U+00A0 을 &nbsp; 로 쓴다."""
    bom, decl = _ENCODINGS[encoding]
    return bom + hwpml_text(items, doctype_nbsp=doctype_nbsp, decl_encoding=decl).encode(encoding)


def write_hwpml(path: Path, items: Sequence[Item], **kw: object) -> Path:
    """부모 디렉터리 생성 후 저장, path 반환. kw 는 build_hwpml 에 그대로."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(build_hwpml(items, **kw))  # type: ignore[arg-type]
    return path
