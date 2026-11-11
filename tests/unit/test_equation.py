"""수식 스크립트 → LaTeX 변환 래퍼 테스트."""

from __future__ import annotations

import pytest

from hwp2md import equation
from hwp2md.equation import to_latex


def test_over_is_fraction() -> None:
    result = to_latex("a over b")
    assert result is not None
    assert "\\frac" in result


def test_sqrt() -> None:
    result = to_latex("sqrt x")
    assert result is not None
    assert "\\sqrt" in result
    assert "x" in result


def test_sum_with_bounds() -> None:
    result = to_latex("sum _{i=1} ^{n}")
    assert result is not None
    assert result == "\\sum_{i = 1}^{n}"


def test_greek_letters() -> None:
    result = to_latex("alpha + beta")
    assert result is not None
    assert "\\alpha" in result
    assert "\\beta" in result


@pytest.mark.parametrize("script", ["", "   ", "\n\t"])
def test_empty_script_is_none(script: str) -> None:
    assert to_latex(script) is None


def test_deep_nesting_does_not_raise() -> None:
    script = "{" * 500 + "x" + "}" * 500
    result = to_latex(script)
    assert result is None or isinstance(result, str)


def test_long_input_does_not_raise() -> None:
    script = "a over b " * 600  # 5400자
    assert len(script) > 5000
    result = to_latex(script)
    assert result is None or isinstance(result, str)


def test_oversized_input_is_none() -> None:
    assert to_latex("x " * 20_000) is None


def test_unbalanced_braces_do_not_raise() -> None:
    for script in ["{", "}", "a over", "^", "_{", "sqrt", "{{{a"]:
        result = to_latex(script)
        assert result is None or isinstance(result, str)


def test_internal_exception_is_swallowed(monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(script: str) -> str:
        raise RuntimeError("converter bug")

    monkeypatch.setattr(equation, "eqedit_to_latex", boom)
    assert to_latex("a over b") is None


def test_recursion_error_is_swallowed(monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(script: str) -> str:
        raise RecursionError

    monkeypatch.setattr(equation, "eqedit_to_latex", boom)
    assert to_latex("a over b") is None


def test_blank_converter_output_is_none(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(equation, "eqedit_to_latex", lambda script: "   ")
    assert to_latex("a") is None


def test_result_is_stripped(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(equation, "eqedit_to_latex", lambda script: "  x  \n")
    assert to_latex("x") == "x"
    real = to_latex("  a over b  ")
    assert real is not None
    assert real == real.strip()
