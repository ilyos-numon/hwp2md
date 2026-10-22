# RESULT — T-20261022-heading-levels 제목 계층(heading) 지원

> 작성: scribe · 2026-10-22 23:11 · 최종 상태: DONE
> 사용자는 이 파일만 읽고 받아들일지 판단한다. 3분 안에 읽히게 쓴다.

## 결론 (3줄)
- HWP 5.0(DocInfo 문단 모양 개요 비트)과 HWPX(header.xml OUTLINE paraPr)의 개요 1~7 단락을 `#`~`######` 제목으로 렌더한다. 두 포맷 합성 fixture 출력은 바이트 동일하다.
- 실제 샘플 5개에는 제목이 0개라 실문서 양성 검증은 없다. 합성 fixture로만 검증했다.
- 지금 바로 쓸 수 있다. main 병합은 사용자 RESULT 검토 후 진행한다 (브랜치 `ai/T-20261022-heading-levels`).

## 성공 기준 대비 (PLAN §2)
| # | 기준 | 결과 | 근거 |
|---|------|------|------|
| S1 | 합성 제목 fixture 두 포맷 동일 MD | ✅ | `uv run pytest tests/e2e/test_cli_heading.py -q` → 12 passed (합성 7 + 실제 샘플 5) |
| S2 | E2E 전체 | ✅ | `uv run pytest tests/e2e -q` → 33 passed, failed 0, skipped 0 |
| S3 | 단위 회귀 없음 | ✅ | `uv run pytest tests/unit -q` → 171 passed, failed 0 (기준 143 이상) |
| S4 | 린트·포맷·타입 | ✅ | All checks passed! / already formatted / Success: no issues found in 16 source files |
| S5 | 실제 HWP 5.0 샘플 제목 판정 | ✅ | form200005063113.hwp: `단락 118개 · 표 8개`, `^#{1,6} ` grep → 0 |
| S6 | 실제 샘플 5개 출력 불변 | ✅ | 2행 불변, 제목 없음, exit=0 |
| S7 | 제목 없는 입력 합성 바이트 불변 | ✅ | sha256 기준 단위 테스트 통과 |
| S8 | 기존 E2E 수정 범위 | ✅ | test_cli_convert.py·test_cli_hwpx.py 정규식 1줄씩 (reviewer 확인) |
| S9 | 익명화 | ✅ | `sanitize-check: OK` |
| S10 | 증거 파일 | ✅ | screenshots에 heading_hwp5.md·heading_hwpx.md·heading_edge.md·heading_cell.md 및 실제 샘플 .md 5개 (reviewer: §2 S1~S10 전부 PASS) |

## 변경 요약
- 커밋 범위: `main..HEAD` 12 commits (93f7cea … ad99b4d)
- 추가/수정 파일: 45개 (+3423 / -68) — 핵심: `src/hwp2md/hwp5/docinfo.py`, `src/hwp2md/hwpx/header.py`, `src/hwp2md/render.py`, `src/hwp2md/convert.py`, `src/hwp2md/cli.py`
- 새 의존성: 없음 (플랜상 pyproject·uv.lock 변경 금지, diff 재확인 안 함)
- 새 환경변수: 없음

## 테스트
- 단위: `uv run pytest tests/unit -q` → 171 passed
- E2E: `uv run pytest tests/e2e -q` → 33 passed, 케이스 목록:
  - test_cli_heading.py 8케이스(12건) — 합성 HWP5·HWPX 제목, 깊은 수준·빈 제목·두 줄 제목 엣지, 셀 안 제목, 실제 샘플 5개 2행 불변

## 실행 방법
```bash
cd /Users/illi/illy-projects/hwp2md && uv run hwp2md <file.hwp|.hwpx> -o <outdir>
```

## 못 한 것 / 알려진 문제
- 실제 문서로 제목 양성 검증 없음 — 현재 샘플 5개 모두 제목 0 — 제목 있는 실제 샘플이 없음 — 합성 fixture로만 검증. 제안: 제목 있는 실제 HWP·HWPX를 추가하고 REAL_EXPECTED 갱신.

## 결정 사항 (플랜에 없었는데 실행 중 정한 것)
- PARA_HEADER para_shape_id 오프셋 @12 → @8 정정 (HWP 5.0 스펙 기준). 샘플1 기대값 (100,8,18) → (118,8,0). 근거: `.ai/decisions/2026-10-22-para-header-offset.md`. 18개 @12 매치는 본문 단락이었음.
- lxml 6이 resolve_entities 속성을 노출하지 않아 E-8 테스트를 동작 기반으로 대체. reviewer: 약화 아님.
- 플랜 §7 기본값 7개 승인 적용. 주요 내용: Paragraph에 level 필드 추가, 판정은 para_shape_id만 사용(STYLE 파서 미구현), 개요 7 이상은 `######`, 표 셀 안 제목은 텍스트만 쓰고 수준은 버림, 긴 제목도 제목으로 둠, CLI 2행 ` · 제목 K개`는 제목 1개 이상일 때만. 나머지는 PLAN §7 참조.

## 후속 제안 (별도 태스크로)
- 제목 있는 실제 HWP·HWPX 샘플 추가 후 REAL_EXPECTED 갱신 (실문서 양성 검증)
- 번호·글머리 리스트 렌더 (문단 머리 모양 2·3)
- 이미지·각주

## 비용
- 서브에이전트 호출: 15회 (PROGRESS 기준 집계. planner fable 1 / opus 7 / sonnet 7 / haiku 0, 본 기록 단계 제외)
- 재시도: 1회 (S3 RETRY, PARA_HEADER 오프셋 정정) · 차단: 0회
