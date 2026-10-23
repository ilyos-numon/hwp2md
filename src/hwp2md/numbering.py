"""Approximate list numbering: number formats, label templates, per-level counters."""

from __future__ import annotations

import re
from collections.abc import Sequence
from typing import Literal

NumFormat = Literal[
    "DIGIT",
    "CIRCLED_DIGIT",
    "ROMAN_CAPITAL",
    "ROMAN_SMALL",
    "LATIN_CAPITAL",
    "LATIN_SMALL",
    "HANGUL_SYLLABLE",
    "CIRCLED_HANGUL_SYLLABLE",
    "HANGUL_JAMO",
    "HANJA_DIGIT",
]

_HANGUL_SYLLABLES = "가나다라마바사아자차카타파하"
_CIRCLED_HANGUL = "㉮㉯㉰㉱㉲㉳㉴㉵㉶㉷㉸㉹㉺㉻"
_HANGUL_JAMO = "ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅊㅋㅌㅍㅎ"
_HANJA_DIGITS = "一二三四五六七八九"
_ROMAN = (
    (1000, "M"),
    (900, "CM"),
    (500, "D"),
    (400, "CD"),
    (100, "C"),
    (90, "XC"),
    (50, "L"),
    (40, "XL"),
    (10, "X"),
    (9, "IX"),
    (5, "V"),
    (4, "IV"),
    (1, "I"),
)
_TEMPLATE_TOKEN = re.compile(r"\^([1-7nN])")


def _circled_digit(n: int) -> str | None:
    if 1 <= n <= 20:
        return chr(0x2460 + n - 1)
    if 21 <= n <= 35:
        return chr(0x3251 + n - 21)
    if 36 <= n <= 50:
        return chr(0x32B1 + n - 36)
    return None


def _roman(n: int) -> str | None:
    if not 1 <= n <= 3999:
        return None
    out: list[str] = []
    for value, symbol in _ROMAN:
        while n >= value:
            out.append(symbol)
            n -= value
    return "".join(out)


def _from_table(n: int, table: str) -> str | None:
    return table[n - 1] if 1 <= n <= len(table) else None


def _hanja(n: int) -> str | None:
    if not 1 <= n <= 99:
        return None
    tens, ones = divmod(n, 10)
    head = "" if tens == 0 else ("十" if tens == 1 else _HANJA_DIGITS[tens - 1] + "十")
    return head + (_HANJA_DIGITS[ones - 1] if ones else "")


def format_number(n: int, fmt: NumFormat) -> str:
    """1→"1","①","I","i","A","a","가","㉮","ㄱ","一". 범위 밖은 DIGIT."""
    out: str | None
    if fmt == "CIRCLED_DIGIT":
        out = _circled_digit(n)
    elif fmt == "ROMAN_CAPITAL":
        out = _roman(n)
    elif fmt == "ROMAN_SMALL":
        roman = _roman(n)
        out = roman.lower() if roman is not None else None
    elif fmt == "LATIN_CAPITAL":
        out = chr(ord("A") + n - 1) if 1 <= n <= 26 else None
    elif fmt == "LATIN_SMALL":
        out = chr(ord("a") + n - 1) if 1 <= n <= 26 else None
    elif fmt == "HANGUL_SYLLABLE":
        out = _from_table(n, _HANGUL_SYLLABLES)
    elif fmt == "CIRCLED_HANGUL_SYLLABLE":
        out = _from_table(n, _CIRCLED_HANGUL)
    elif fmt == "HANGUL_JAMO":
        out = _from_table(n, _HANGUL_JAMO)
    elif fmt == "HANJA_DIGIT":
        out = _hanja(n)
    else:
        out = None
    return out if out is not None else str(n)


def apply_template(template: str, numbers: Sequence[int], formats: Sequence[NumFormat]) -> str:
    """ "^k"(k=1..7)를 수준 k 번호로, "^n"/"^N" 을 현재(마지막) 수준 번호로 바꾼다.
    예: ("^1.", [3], ["DIGIT"]) → "3.". 번호가 없는 수준은 1, 형식이 없는 수준은 DIGIT."""

    def number_at(index: int) -> str:
        n = numbers[index] if 0 <= index < len(numbers) else 1
        fmt: NumFormat = formats[index] if 0 <= index < len(formats) else "DIGIT"
        return format_number(n, fmt)

    def replace(match: re.Match[str]) -> str:
        token = match.group(1)
        if token in ("n", "N"):
            return number_at(len(numbers) - 1)
        return number_at(int(token) - 1)

    return _TEMPLATE_TOKEN.sub(replace, template)


class NumberingCounter:
    """번호 정의(id)별 수준 번호. 문서 하나 단위로 리더가 쓴다."""

    def __init__(self) -> None:
        self._levels: dict[int, list[int | None]] = {}

    def next(self, numbering_id: int, depth: int, start: int = 1) -> list[int]:
        """같은 id 의 depth 번호 +1, 더 깊은 수준은 리셋, 처음이면 start.
        반환: 수준 0..depth 번호 목록 (아직 나오지 않은 상위 수준은 1)."""
        depth = max(depth, 0)
        levels = self._levels.setdefault(numbering_id, [])
        del levels[depth + 1 :]
        while len(levels) <= depth:
            levels.append(None)
        current = levels[depth]
        levels[depth] = start if current is None else current + 1
        return [1 if n is None else n for n in levels]
