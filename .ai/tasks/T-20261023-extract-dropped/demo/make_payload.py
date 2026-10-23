"""design/v3 데모 응답(js/demo-payload.js)을 실제 엔진 출력으로 다시 만든다.

합성 HWPX(제목·링크·각주·글머리표·칸 그림 표·수식·머리말)를 tests/synth_hwpx.py 로 만들고
hwp2md.memory.convert_to_response 결과를 그대로 JS 파일에 쓴다. 문서 내용은 모두 가상이다.

실행: uv run python .ai/tasks/T-20261023-extract-dropped/demo/make_payload.py
"""

from __future__ import annotations

import base64
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "tests"))

from synth_hwp5 import SynthCell, SynthHeading, SynthImage, SynthTable  # noqa: E402
from synth_hwpx import build_hwpx  # noqa: E402
from synth_items import (  # noqa: E402
    SynthEquation,
    SynthHeaderFooter,
    SynthLink,
    SynthListPara,
    SynthNote,
    SynthRich,
)

from hwp2md.memory import convert_to_response  # noqa: E402

OUT = ROOT / "design" / "v3" / "js" / "demo-payload.js"
FILENAME = "2026_가상_공고문.hwpx"
HEAD = (
    "/* 실제 hwp2md 엔진이 합성 데모 문서(demo.hwpx)를 변환한 /api/convert 응답 그대로. "
    "백엔드 연결 시 이 파일은 지운다.\n"
    "   다시 만들기: uv run python .ai/tasks/T-20261023-extract-dropped/demo/make_payload.py */\n"
)

# 절차 흐름도(상자 세 개와 화살표) 그림. 이전 데모 응답에 있던 것과 같은 PNG.
FLOW_PNG = base64.b64decode(
    "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"
)


def demo_items() -> list[object]:
    flow = SynthImage(FLOW_PNG, "png")
    return [
        SynthHeaderFooter(("2026 가상 공고문",)),
        SynthHeading("2026년도 가상 문서 디지털 전환 지원사업 공고", 1),
        "이 문서는 hwp2md 시연을 위해 만든 가상의 공고문입니다. 실제 기관·사업과 관계없습니다.",
        SynthHeading("1. 사업 개요", 2),
        SynthRich(
            (
                "종이와 한글 문서로 관리하던 업무 자료를 검색 가능한 형태로 바꾸는 기관을 지원합니다",
                SynthNote(("지원 대상은 가상의 기관입니다.",)),
                ". 자세한 내용은 ",
                SynthLink("사업 안내 페이지", "https://example.org/notice"),
                "를 참고하십시오.",
            )
        ),
        SynthTable(
            rows=4,
            cols=2,
            cells=(
                SynthCell(("구분",), 0, 0),
                SynthCell(("내용",), 1, 0),
                SynthCell(("지원 규모",), 0, 1),
                SynthCell(("총 10억 원 (기관당 최대 5천만 원)",), 1, 1),
                SynthCell(("지원 기간",), 0, 2),
                SynthCell(("2026. 3. ~ 2026. 12.",), 1, 2),
                SynthCell(("추진 절차",), 0, 3),
                SynthCell((flow,), 1, 3),
            ),
        ),
        SynthHeading("2. 신청 자격", 2),
        SynthListPara("공공기관 또는 비영리법인", "bullet"),
        SynthListPara("문서 전환 계획을 제출한 기관", "bullet"),
        SynthHeading("2.1 지원금 산정", 3),
        SynthRich(("지원금은 ", SynthEquation("a times b over c"), " 로 계산합니다.")),
        SynthHeading("3. 문의", 2),
        "문의는 가상 사업 운영 사무국으로 해 주십시오.",
    ]


def main() -> int:
    data = build_hwpx(demo_items())
    status, payload = convert_to_response(data, FILENAME)
    if status != 200:
        print(f"convert failed: {status} {payload}", file=sys.stderr)
        return 1
    body = json.dumps(payload, ensure_ascii=False, indent=2)
    OUT.write_text(HEAD + "window.HWP2MD_DEMO_PAYLOAD = " + body + ";\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} skipped={payload['skipped']} counts={payload['counts']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
