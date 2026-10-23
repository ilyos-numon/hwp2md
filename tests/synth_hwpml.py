"""Synthetic HWPML 2.x (.hml) generator. Test-only. Mirrors synth_hwpx so formats can be cross-checked."""  # noqa: E501

from __future__ import annotations

import base64
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

from synth_hwp5 import (  # 재정의 금지
    HEADER_IMAGE,
    PNG_1X1,
    Item,
    SynthCell,
    SynthHeading,
    SynthImage,
    SynthTable,
    collect_images,
)
from synth_items import (
    ExtItem,
    Run,
    SynthCaptionedTable,
    SynthChart,
    SynthEquation,
    SynthField,
    SynthHeaderFooter,
    SynthHidden,
    SynthLink,
    SynthListPara,
    SynthNote,
    SynthRich,
    SynthTextBox,
)
from synth_ole import build_ole_cfb, chart_xml

NBSP = " "
DOCTYPE_NBSP = '<!DOCTYPE HWPML [\n\t<!ENTITY nbsp\t"&#160;">\n]>\n'
_ENCODINGS: dict[str, tuple[bytes, str]] = {
    "utf-8": (b"", "UTF-8"),
    "utf-16-le": (b"\xff\xfe", "UTF-16"),
    "utf-16-be": (b"\xfe\xff", "UTF-16"),
}
TEXTBOX_IMAGE = SynthImage(PNG_1X1, "png")  # SynthTextBox(with_image=True) 안의 그림
LIST_SHAPE_BASE = 8  # 목록 PARASHAPE Id 시작 (0 = 본문, 1~7 = 개요)
BULLET_CHAR = "•"
LEGACY_CHART_CONTENTS = b"\x00" * 16  # 구형 차트: Contents 스트림만


@dataclass(frozen=True)
class OleBin:
    """OLE 개체 BINDATA (CFB 그대로)."""

    data: bytes
    ext: str = "ole"
    missing: bool = False


Bin = SynthImage | OleBin
AnyItem = Item | ExtItem


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


def cell_xml(cell: SynthCell, images: Sequence[Bin], *, nbsp_entity: bool) -> str:
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


def _paralist_xml(paragraphs: Sequence[str], *, prefix: str = "", extra: str = "") -> str:
    """PARALIST 안 단락들. prefix 는 첫 단락 TEXT 맨 앞(예: AUTONUM),
    extra 는 끝에 붙일 단락 XML."""
    out = []
    for i, text in enumerate(paragraphs):
        head = prefix if i == 0 else ""
        out.append(
            f'<P ParaShape="0" Style="0"><TEXT CharShape="0">{head}'
            f"<CHAR>{text_xml(text)}</CHAR></TEXT></P>"
        )
    return (
        '<PARALIST LineWrap="Break" TextDirection="0" VertAlign="Top">'
        + "".join(out)
        + extra
        + "</PARALIST>"
    )


def table_xml(
    table: SynthTable, images: Sequence[Bin], *, nbsp_entity: bool, caption: str = ""
) -> str:
    rows = "".join(
        "<ROW>"
        + "".join(cell_xml(c, images, nbsp_entity=nbsp_entity) for c in table.cells if c.row == r)
        + "</ROW>"
        for r in range(table.rows)
    )
    shape_attrs = 'InstId="0" Lock="false" NumberingType="Table" TextWrap="TopAndBottom"'
    shape = (
        f"<SHAPEOBJECT {shape_attrs}>"
        '<CAPTION Side="Bottom" FullSize="false" Width="8504" Gap="850" LastWidth="8504">'
        + _paralist_xml([caption])
        + "</CAPTION></SHAPEOBJECT>"
        if caption
        else f"<SHAPEOBJECT {shape_attrs}/>"
    )
    return (
        '<P ParaShape="0" Style="0"><TEXT CharShape="0">'
        f'<TABLE PageBreak="Cell" RepeatHeader="true" RowCount="{table.rows}" '
        f'ColCount="{table.cols}" CellSpacing="0" BorderFill="1">'
        f"{shape}{rows}</TABLE></TEXT></P>"
    )


# --- 단락 안 요소·개체·목록 (synth_items) ---


def command_escape(url: str) -> str:
    """하이퍼링크 command 의 대상 이스케이프 (`\\` `:` `?` `;` `#` `|` 앞에 `\\`)."""
    return "".join("\\" + ch if ch in "\\:?;#|" else ch for ch in url)


def _field_xml(ftype: str, inst_id: int, text: str, command: str = "") -> str:
    cmd = f" Command={quoteattr(command)}" if command else ""
    return (
        f'<FIELDBEGIN Type="{ftype}" Name="" InstId="{inst_id}" Editable="false" '
        f'Dirty="false" Property="0"{cmd}/>'
        f"<CHAR>{text_xml(text)}</CHAR>"
        f'<FIELDEND Type="{ftype}" Editable="false" Property="0"/>'
    )


def run_xml(run: Run, *, inst_id: int) -> str:
    """SynthRich 의 run 하나 → TEXT 안 XML."""
    if isinstance(run, str):
        return f"<CHAR>{text_xml(run)}</CHAR>"
    if isinstance(run, SynthLink):
        return _field_xml("Hyperlink", inst_id, run.text, command_escape(run.url) + ";1;0;0;")
    if isinstance(run, SynthField):
        return _field_xml("ClickHere", inst_id, run.text)
    if isinstance(run, SynthNote):
        tag, num_type = (
            ("FOOTNOTE", "Footnote") if run.kind == "footnote" else ("ENDNOTE", "Endnote")
        )
        auto = (
            f'<AUTONUM Number="1" NumberType="{num_type}">'
            '<AUTONUMFORMAT Type="Digit" SuffixChar=")" Superscript="false"/></AUTONUM>'
        )
        return f"<{tag}>" + _paralist_xml(run.paragraphs, prefix=auto) + f"</{tag}>"
    assert isinstance(run, SynthEquation)
    return (
        '<EQUATION LineMode="false" BaseUnit="1000" TextColor="0" BaseLine="85" '
        'Version="Equation Version 60">'
        '<SHAPEOBJECT InstId="0" Lock="false" NumberingType="Equation" TextWrap="TopAndBottom"/>'
        f"<SCRIPT>{escape(run.script)}</SCRIPT></EQUATION>"
    )


def _text_paragraph(inner: str, *, para_shape: int = 0) -> str:
    return f'<P ParaShape="{para_shape}" Style="0"><TEXT CharShape="0">{inner}</TEXT></P>'


def rich_paragraph_xml(item: SynthRich, *, para_id: int) -> str:
    return _text_paragraph(
        "".join(run_xml(r, inst_id=3000 + para_id * 100 + k) for k, r in enumerate(item.runs))
    )


def header_footer_paragraph_xml(item: SynthHeaderFooter, images: Sequence[Bin]) -> str:
    tag = item.kind.upper()
    pic = picture_paragraph_xml(images.index(HEADER_IMAGE) + 1) if item.with_image else ""
    return _text_paragraph(
        f'<{tag} ApplyPageType="Both" TextWidth="51024" TextHeight="3600" '
        'HasTextRef="false" HasNumRef="false">'
        + _paralist_xml(item.paragraphs, extra=pic)
        + f"</{tag}>"
    )


def hidden_paragraph_xml(item: SynthHidden) -> str:
    return _text_paragraph("<HIDDENCOMMENT>" + _paralist_xml(item.paragraphs) + "</HIDDENCOMMENT>")


def textbox_paragraph_xml(item: SynthTextBox, images: Sequence[Bin]) -> str:
    pic = picture_paragraph_xml(images.index(TEXTBOX_IMAGE) + 1) if item.with_image else ""
    rect = (
        '<RECTANGLE Ratio="0">'
        '<SHAPEOBJECT InstId="0" Lock="false" TextWrap="TopAndBottom">'
        '<SIZE Height="3382" Width="8196"/></SHAPEOBJECT>'
        '<SHAPECOMPONENT GroupLevel="0" InstID="0"/>'
        '<DRAWINGOBJECT><LINESHAPE Color="0" Width="33" Style="Solid"/>'
        '<DRAWTEXT LastWidth="8196" Name="" Editable="false">'
        '<TEXTMARGIN Left="283" Right="283" Top="283" Bottom="283"/>'
        + _paralist_xml(item.paragraphs, extra=pic)
        + "</DRAWTEXT></DRAWINGOBJECT></RECTANGLE>"
    )
    anchor = f"<CHAR>{text_xml(item.anchor_text)}</CHAR>" if item.anchor_text else ""
    return _text_paragraph(anchor + rect)


def captioned_table_xml(item: SynthCaptionedTable, images: Sequence[Bin]) -> str:
    cells = tuple(
        SynthCell((text,), col=c, row=r)
        for r, row in enumerate(item.cells)
        for c, text in enumerate(row)
    )
    table = SynthTable(
        rows=len(item.cells), cols=max((len(r) for r in item.cells), default=0), cells=cells
    )
    return table_xml(table, images, nbsp_entity=False, caption=item.caption)


def chart_cfb(item: SynthChart) -> bytes:
    if item.legacy:
        return build_ole_cfb({"Contents": LEGACY_CHART_CONTENTS})
    return build_ole_cfb(
        {"OOXMLChartContents": chart_xml(item.title, item.categories, item.series)}
    )


def chart_paragraph_xml(item: SynthChart, images: Sequence[Bin]) -> str:
    k = images.index(OleBin(chart_cfb(item))) + 1
    return _text_paragraph(
        f'<OLE ObjetType="Embedded" ExtentX="8196" ExtentY="3382" BinItem="{k}" '
        'DrawAspect="Content" HasMoniker="false" EqBaseLine="0">'
        '<SHAPEOBJECT InstId="0" Lock="false" TextWrap="TopAndBottom">'
        '<SIZE Height="3382" Width="8196"/></SHAPEOBJECT>'
        '<SHAPECOMPONENT GroupLevel="0" InstID="0"/></OLE>'
    )


def _list_key(item: SynthListPara) -> tuple[str, int]:
    return (item.kind, item.depth)


def list_shapes(items: Sequence[object]) -> dict[tuple[str, int], int]:
    """(종류, 수준) → PARASHAPE Id (LIST_SHAPE_BASE 부터 등장 순)."""
    out: dict[tuple[str, int], int] = {}
    for item in items:
        if isinstance(item, SynthListPara):
            out.setdefault(_list_key(item), LIST_SHAPE_BASE + len(out))
    return out


def parahead_templates(items: Sequence[object]) -> dict[int, str]:
    """번호 정의 하나(Id 1)의 수준(1~7) → 형식. 그 수준 첫 번호 항목의 template, 없으면 "^L."."""
    out = {level: f"^{level}." for level in range(1, 8)}
    seen: set[int] = set()
    for item in items:
        if isinstance(item, SynthListPara) and item.kind == "number":
            level = item.depth + 1
            if level in out and level not in seen:
                out[level] = item.template
                seen.add(level)
    return out


def list_paragraph_xml(item: SynthListPara, shapes: dict[tuple[str, int], int]) -> str:
    return _text_paragraph(
        f"<CHAR>{text_xml(item.text)}</CHAR>", para_shape=shapes[_list_key(item)]
    )


def all_bins(items: Sequence[object]) -> list[Bin]:
    """collect_images(머리말 그림 포함) + 글상자 그림 + 차트 OLE (문서 순서, 중복 제외).
    바이너리 항목 k = index + 1."""
    found: list[Bin] = list(collect_images(items))  # type: ignore[arg-type]
    for item in items:
        extra: Bin | None = None
        if isinstance(item, SynthTextBox) and item.with_image:
            extra = TEXTBOX_IMAGE
        elif isinstance(item, SynthChart):
            extra = OleBin(chart_cfb(item))
        if extra is not None and extra not in found:
            found.append(extra)
    return found


def item_xml(
    item: object,
    *,
    para_id: int,
    images: Sequence[Bin],
    shapes: dict[tuple[str, int], int],
    nbsp_entity: bool,
) -> str:
    if isinstance(item, str):
        return paragraph_xml(item, nbsp_entity=nbsp_entity)
    if isinstance(item, SynthHeading):
        return paragraph_xml(item.text, para_shape=item.level, nbsp_entity=nbsp_entity)
    if isinstance(item, SynthImage):
        return picture_paragraph_xml(images.index(item) + 1)
    if isinstance(item, SynthTable):
        return table_xml(item, images, nbsp_entity=nbsp_entity)
    if isinstance(item, SynthRich):
        return rich_paragraph_xml(item, para_id=para_id)
    if isinstance(item, SynthHeaderFooter):
        return header_footer_paragraph_xml(item, images)
    if isinstance(item, SynthHidden):
        return hidden_paragraph_xml(item)
    if isinstance(item, SynthTextBox):
        return textbox_paragraph_xml(item, images)
    if isinstance(item, SynthCaptionedTable):
        return captioned_table_xml(item, images)
    if isinstance(item, SynthListPara):
        return list_paragraph_xml(item, shapes)
    if isinstance(item, SynthChart):
        return chart_paragraph_xml(item, images)
    raise TypeError(f"unsupported item: {item!r}")


def para_shape_xml(i: int) -> str:
    heading = "None" if i == 0 else "Outline"
    return (
        f'<PARASHAPE Id="{i}" Align="Justify" Heading="0" HeadingType="{heading}" '
        f'Level="{max(i - 1, 0)}" TabDef="0"><PARAMARGIN Left="0" Right="0"/></PARASHAPE>'
    )


def list_para_shape_xml(key: tuple[str, int], shape_id: int) -> str:
    kind, depth = key
    heading_type = "Bullet" if kind == "bullet" else "Number"
    return (
        f'<PARASHAPE Id="{shape_id}" Align="Justify" Heading="1" '
        f'HeadingType="{heading_type}" Level="{depth}" TabDef="0">'
        '<PARAMARGIN Left="0" Right="0"/></PARASHAPE>'
    )


def _parahead_xml(level: int, text: str) -> str:
    return (
        f'<PARAHEAD Level="{level}" Alignment="Left" UseInstWidth="true" AutoIndent="true" '
        'WidthAdjust="0" TextOffsetType="percent" TextOffset="50" CharShape="0" '
        f'NumFormat="Digit">{escape(text)}</PARAHEAD>'
    )


def lists_head_xml(items: Sequence[object]) -> str:
    """NUMBERINGLIST(번호 항목이 있을 때 Id 1 하나) + BULLETLIST(글머리표가 있을 때 Id 1 하나)."""
    out = ""
    if any(isinstance(x, SynthListPara) and x.kind == "number" for x in items):
        out += (
            '<NUMBERINGLIST Count="1"><NUMBERING Id="1" Start="0">'
            + "".join(_parahead_xml(lv, t) for lv, t in parahead_templates(items).items())
            + "</NUMBERING></NUMBERINGLIST>"
        )
    if any(isinstance(x, SynthListPara) and x.kind == "bullet" for x in items):
        out += (
            f'<BULLETLIST Count="1"><BULLET Id="1" Char="{BULLET_CHAR}">'
            + _parahead_xml(0, "")
            + "</BULLET></BULLETLIST>"
        )
    return out


def head_xml(images: Sequence[Bin], items: Sequence[object] = ()) -> str:
    bin_items = "".join(
        f'<BINITEM Type="Embedding" BinData="{k}" Format="{img.ext}"/>'
        for k, img in enumerate(images, 1)
    )
    bin_list = f'<BINDATALIST Count="{len(images)}">{bin_items}</BINDATALIST>' if images else ""
    shapes = list_shapes(items)
    return (
        '<HEAD SecCnt="1"><DOCSUMMARY><TITLE>synth</TITLE></DOCSUMMARY>'
        '<DOCSETTING><BEGINNUMBER Page="1" Footnote="1" Endnote="1"/></DOCSETTING>'
        "<MAPPINGTABLE>"
        + bin_list
        + lists_head_xml(items)
        + f'<PARASHAPELIST Count="{8 + len(shapes)}">'
        + "".join(para_shape_xml(i) for i in range(8))
        + "".join(list_para_shape_xml(k, sid) for k, sid in shapes.items())
        + "</PARASHAPELIST></MAPPINGTABLE></HEAD>"
    )


def tail_xml(images: Sequence[Bin]) -> str:
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
    items: Sequence[AnyItem], *, doctype_nbsp: bool = False, decl_encoding: str = "UTF-8"
) -> str:
    images = all_bins(items)
    shapes = list_shapes(items)
    body = "".join(
        item_xml(item, para_id=i, images=images, shapes=shapes, nbsp_entity=doctype_nbsp)
        for i, item in enumerate(items)
    )
    return (
        f'<?xml version="1.0" encoding="{decl_encoding}"?>\n'
        + (DOCTYPE_NBSP if doctype_nbsp else "")
        + '<HWPML Version="2.1" Style2="embed">'
        + head_xml(images, items)
        + f'<BODY><SECTION Id="0">{body}</SECTION></BODY>'
        + tail_xml(images)
        + "</HWPML>"
    )


def build_hwpml(
    items: Sequence[AnyItem], *, encoding: str = "utf-8", doctype_nbsp: bool = False
) -> bytes:
    """encoding: "utf-8" | "utf-16-le" | "utf-16-be" (UTF-16 은 BOM 을 붙인다).
    doctype_nbsp: nbsp 내부 엔티티를 선언하고 글자 안 U+00A0 을 &nbsp; 로 쓴다.
    items 는 기존 Item 과 synth_items 의 ExtItem 을 섞어 받는다."""
    bom, decl = _ENCODINGS[encoding]
    return bom + hwpml_text(items, doctype_nbsp=doctype_nbsp, decl_encoding=decl).encode(encoding)


def write_hwpml(path: Path, items: Sequence[AnyItem], **kw: object) -> Path:
    """부모 디렉터리 생성 후 저장, path 반환. kw 는 build_hwpml 에 그대로."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(build_hwpml(items, **kw))  # type: ignore[arg-type]
    return path
