from lxml import etree

from hwp2md.blocks import Paragraph, Table
from hwp2md.hwpx import body, reader
from hwp2md.hwpx.body import parse_section
from hwp2md.hwpx.reader import NS_HP, NS_HS, parse_section_xml

XML_DECL = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'


def _sec(inner: str) -> etree._Element:
    return parse_section_xml(
        (XML_DECL + f'<hs:sec xmlns:hp="{NS_HP}" xmlns:hs="{NS_HS}">{inner}</hs:sec>').encode()
    )


def _p(*runs: str) -> str:
    return "<hp:p>" + "".join(f"<hp:run>{r}</hp:run>" for r in runs) + "</hp:p>"


def _t(text: str) -> str:
    return f"<hp:t>{text}</hp:t>"


def _tc(
    text: str | list[str] | None,
    row: int | None = None,
    col: int | None = None,
    row_span: int = 1,
    col_span: int = 1,
    *,
    raw: str | None = None,
) -> str:
    if raw is not None:
        sub = f"<hp:subList>{raw}</hp:subList>"
    elif text is None:
        sub = "<hp:subList/>"
    else:
        paras = [text] if isinstance(text, str) else text
        sub = "<hp:subList>" + "".join(_p(_t(x)) for x in paras) + "</hp:subList>"
    addr = "" if row is None else f'<hp:cellAddr colAddr="{col}" rowAddr="{row}"/>'
    span = f'<hp:cellSpan colSpan="{col_span}" rowSpan="{row_span}"/>'
    return f"<hp:tc>{sub}{addr}{span}</hp:tc>"


def _tbl(rows: int | None, cols: int | None, trs: list[list[str]]) -> str:
    attrs = ""
    if rows is not None:
        attrs += f' rowCnt="{rows}"'
    if cols is not None:
        attrs += f' colCnt="{cols}"'
    body_xml = "".join("<hp:tr>" + "".join(tr) + "</hp:tr>" for tr in trs)
    return f"<hp:tbl{attrs}>{body_xml}</hp:tbl>"


def test_ns_constant_matches_reader() -> None:
    assert body.NS_HP == reader.NS_HP


def test_text_runs_concatenated() -> None:
    assert parse_section(_sec(_p(_t("가"), _t("나")))) == [Paragraph("가나")]


def test_empty_and_whitespace_paragraph_skipped() -> None:
    xml = '<hp:p><hp:run charPrIDRef="0"/></hp:p>' + _p(_t("  "))
    assert parse_section(_sec(xml)) == []


def test_inline_tab_linebreak_unknown_keep_tail() -> None:
    xml = _p(_t("a<hp:tab/>b<hp:lineBreak/>c<hp:markpenBegin/>d"))
    assert parse_section(_sec(xml)) == [Paragraph("a b\ncd")]


def test_comment_inside_t_ignored() -> None:
    assert parse_section(_sec(_p(_t("a<!-- x -->b")))) == [Paragraph("ab")]


def test_table_between_text_in_same_paragraph() -> None:
    xml = _p(_t("앞"), _tbl(1, 1, [[_tc("x", 0, 0)]]), _t("뒤"))
    assert parse_section(_sec(xml)) == [Paragraph("앞"), Table([["x"]]), Paragraph("뒤")]


def test_table_only_paragraph() -> None:
    xml = _p(_tbl(1, 2, [[_tc("a", 0, 0), _tc("b", 0, 1)]]))
    assert parse_section(_sec(xml)) == [Table([["a", "b"]])]


def test_grid_from_cell_addr() -> None:
    trs = [
        [_tc("d", 1, 1), _tc("c", 1, 0)],
        [_tc("b", 0, 1), _tc("a", 0, 0)],
    ]
    assert parse_section(_sec(_p(_tbl(2, 2, trs)))) == [Table([["a", "b"], ["c", "d"]])]


def test_merged_cell_blank() -> None:
    trs = [
        [_tc("머리글", 0, 0, col_span=3)],
        [_tc("1", 1, 0), _tc("2", 1, 1), _tc("3", 1, 2)],
    ]
    assert parse_section(_sec(_p(_tbl(2, 3, trs)))) == [
        Table([["머리글", "", ""], ["1", "2", "3"]])
    ]


def test_cell_paragraphs_joined_with_newline() -> None:
    xml = _p(_tbl(1, 1, [[_tc(["라", "마"], 0, 0)]]))
    assert parse_section(_sec(xml)) == [Table([["라\n마"]])]


def test_nested_table_flattened() -> None:
    inner = _tbl(1, 2, [[_tc("x", 0, 0), _tc("y", 0, 1)]])
    xml = _p(_tbl(1, 1, [[_tc(None, 0, 0, raw=_p(inner))]]))
    assert parse_section(_sec(xml)) == [Table([["x y"]])]


def test_missing_row_col_cnt_falls_back_to_tr_tc() -> None:
    trs = [[_tc("a", 0, 0), _tc("b", 0, 1)], [_tc("c", 1, 0), _tc("d", 1, 1)]]
    assert parse_section(_sec(_p(_tbl(None, None, trs)))) == [Table([["a", "b"], ["c", "d"]])]


def test_zero_rows_table_dropped() -> None:
    xml = _p(_tbl(0, 2, [[_tc("a", 0, 0), _tc("b", 0, 1)]]))
    assert parse_section(_sec(xml)) == []


def test_out_of_range_cell_goes_to_first_empty_slot() -> None:
    trs = [[_tc("x", 9, 0)], [_tc("y", 1, 0)]]
    assert parse_section(_sec(_p(_tbl(2, 1, trs)))) == [Table([["x"], ["y"]])]


def test_missing_cell_addr_uses_first_empty_slot() -> None:
    trs = [[_tc("a"), _tc("b")], [_tc("c"), _tc("d")]]
    assert parse_section(_sec(_p(_tbl(2, 2, trs)))) == [Table([["a", "b"], ["c", "d"]])]


def test_ctrl_header_and_footnote_ignored() -> None:
    ctrl = (
        "<hp:ctrl><hp:header><hp:subList>"
        + _p(_t("머리말"))
        + "</hp:subList></hp:header></hp:ctrl>"
    )
    foot = "<hp:footNote><hp:subList>" + _p(_t("각주")) + "</hp:subList></hp:footNote>"
    xml = "<hp:p><hp:run>" + ctrl + _t("본문") + foot + "</hp:run></hp:p>"
    assert parse_section(_sec(xml)) == [Paragraph("본문")]


def test_secpr_and_pic_ignored() -> None:
    assert parse_section(_sec(_p("<hp:secPr/>", "<hp:pic/>"))) == []


def test_section_only_direct_p_children() -> None:
    xml = _p(_t("하나")) + "<hp:other>" + _p(_t("무시")) + "</hp:other>" + _p(_t("둘"))
    assert parse_section(_sec(xml)) == [Paragraph("하나"), Paragraph("둘")]
