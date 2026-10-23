"""Build the synthetic demo document used for README screenshots.

Run: uv run python .ai/tasks/T-20261023-docs-finalize/demo/make_demo.py
Output: .ai/tasks/T-20261023-docs-finalize/demo/demo.hwpx (fictional notice, no real org/logo)
"""

from __future__ import annotations

import struct
import sys
import zlib
from pathlib import Path

DEMO_DIR = Path(__file__).resolve().parent
PROJECT = DEMO_DIR.parents[3]
sys.path.insert(0, str(PROJECT / "tests"))

from synth_hwp5 import SynthCell, SynthHeading, SynthImage, SynthTable  # noqa: E402
from synth_hwpx import write_hwpx  # noqa: E402

W, H = 720, 240
BG = (255, 255, 255)
BOX = (225, 236, 250)
EDGE = (60, 100, 170)


def _png(pixels: list[list[tuple[int, int, int]]]) -> bytes:
    raw = b"".join(b"\x00" + b"".join(bytes(px) for px in row) for row in pixels)

    def chunk(tag: bytes, data: bytes) -> bytes:
        body = tag + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body))

    ihdr = struct.pack(">IIBBBBB", len(pixels[0]), len(pixels), 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )


def diagram_png() -> bytes:
    """세 상자를 화살표로 이은 단순 도식 (신청 → 심사 → 지원)."""
    px = [[BG for _ in range(W)] for _ in range(H)]

    def rect(x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]) -> None:
        for y in range(y0, y1):
            for x in range(x0, x1):
                px[y][x] = color

    boxes = [(40, 70, 200, 170), (280, 70, 440, 170), (520, 70, 680, 170)]
    for x0, y0, x1, y1 in boxes:
        rect(x0, y0, x1, y1, EDGE)
        rect(x0 + 4, y0 + 4, x1 - 4, y1 - 4, BOX)
    for (_, _, ax1, _), (bx0, _, _, _) in zip(boxes, boxes[1:]):
        rect(ax1 + 6, 117, bx0 - 16, 123, EDGE)
        for i in range(14):  # 화살촉
            rect(bx0 - 16 + i, 106 + i, bx0 - 15 + i, 134 - i, EDGE)
    return _png(px)


def main() -> Path:
    img = SynthImage(data=diagram_png(), ext="png")
    table = SynthTable(
        rows=4,
        cols=2,
        cells=(
            SynthCell(("구분",), col=0, row=0),
            SynthCell(("내용",), col=1, row=0),
            SynthCell(("지원 규모",), col=0, row=1),
            SynthCell(("총 10억 원 (기관당 최대 5천만 원)",), col=1, row=1),
            SynthCell(("지원 기간",), col=0, row=2),
            SynthCell(("2026. 3. ~ 2026. 12.",), col=1, row=2),
            SynthCell(("신청 방법",), col=0, row=3),
            SynthCell(("온라인 접수 (붙임 서식 작성 후 제출)",), col=1, row=3),
        ),
    )
    items = [
        SynthHeading("2026년도 가상 문서 디지털 전환 지원사업 공고", 1),
        "이 문서는 hwp2md 시연을 위해 만든 가상의 공고문입니다. 실제 기관·사업과 관계없습니다.",
        SynthHeading("1. 사업 개요", 2),
        "종이와 한글 문서로 관리하던 업무 자료를 검색 가능한 형태로 바꾸는 기관을 지원합니다.",
        table,
        SynthHeading("2. 추진 절차", 2),
        "신청서 접수 후 서면 심사를 거쳐 지원 대상을 선정합니다.",
        img,
        SynthHeading("2.1 심사 기준", 3),
        "사업 필요성, 추진 계획의 구체성, 성과 활용 방안을 평가합니다.",
        SynthHeading("3. 문의", 2),
        "문의는 가상 사업 운영 사무국으로 해 주십시오.",
    ]
    out = write_hwpx(DEMO_DIR / "demo.hwpx", items)
    print(out)
    return out


if __name__ == "__main__":
    main()
