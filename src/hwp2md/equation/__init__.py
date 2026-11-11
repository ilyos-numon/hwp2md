"""한글 수식 스크립트 → LaTeX 변환.

변환기 본체(eqedit.py, tokens.py)는 python-hwpx(Apache-2.0)에서 벤더링했다. 출처는 루트 NOTICE.
"""

from __future__ import annotations

from .eqedit import eqedit_to_latex

__all__ = ["to_latex"]


def to_latex(script: str) -> str | None:
    """수식 스크립트를 LaTeX 조각으로 바꾼다. 빈 스크립트·변환 실패는 None. 예외를 내지 않는다."""
    try:
        if not script or not script.strip():
            return None
        latex = eqedit_to_latex(script)
        result = latex.strip() if isinstance(latex, str) else ""
    except Exception:  # 변환기 내부 오류(재귀 한도·메모리 포함)를 모두 삼킨다
        return None
    return result or None
