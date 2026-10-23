# PROGRESS — T-20261023-extract-dropped (버려지던 HWP 요소 추출과 추출 한계 명시)

> append-only.

---

## [2026-10-23 17:32] S0 | planner(opus) | DONE
- 한 일: PLAN.md·OpenSpec extract-dropped 작성, 사용자 승인(Q7 MIT, Q8 기본 변환+고지)
- 변경 파일(미커밋, .ai 제외): ".ai/tasks/T-20261023-extract-dropped openspec/changes/extract-dropped/ 
- 커밋: ae6ed95 [T-20261023-extract-dropped][s0] V3 프론트엔드 시안·Stitch 원본·기능 명세 (선행 작업 커밋)
- 다음: S1 기준선 기록

## [2026-10-23 17:33] S1 | orchestrator | START
- 한 일: 기준선 기록
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 0d1546a [T-20261023-extract-dropped][record] PROGRESS 위치 정정 (STATE 태스크 줄 형식)

## [2026-10-23 17:35] S1 | runner(haiku) | DONE
- 한 일: 기준선: unit 6F/360P, e2e 6F/92P(샘플 집합 변화 4 + 브라우저 모드 2), CLI 69파일(종료0 61, 종료3 8)
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 0d1546a [T-20261023-extract-dropped][record] PROGRESS 위치 정정 (STATE 태스크 줄 형식)
- 다음: S2 샘플 선정 규칙

## [2026-10-23 17:35] S2 | orchestrator | START
- 한 일: 실제 샘플 선정 규칙 고정
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 7a6518d [T-20261023-extract-dropped][s1] 기준선 기록

## [2026-10-23 17:36] S2 | hook | AUTO
- 한 일: 도구 호출 15회 경과
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 7a6518d [T-20261023-extract-dropped][s1] 기준선 기록

## [2026-10-23 17:38] S2 | test-writer(sonnet) | DONE
- 한 일: tests/samples.py(LEGACY 5개·classify·all_samples) + 기존 테스트 7개 샘플 정의만 교체. 1회 수정(HWPML DOCTYPE 분류). unit 338P, e2e cli/api 51P, web_ui 8P(브라우저 모드 포함)
- 변경 파일(미커밋, .ai 제외): tests/e2e/conftest.py tests/e2e/test_cli_heading.py tests/e2e/test_cli_hwpx.py tests/e2e/test_cli_image.py tests/fixtures/README.md tests/unit/test_memory.py tests/unit/test_source_bytes.py tests/unit/test_web_app.py tests/samples.py 
- 커밋: 7a6518d [T-20261023-extract-dropped][s1] 기준선 기록
- 다음: S3 블록 모델·렌더 계약
- 메모: S1 브라우저 모드 실패 2건도 샘플 집합 원인이었음. test_cli_convert.py:16 *.hwp glob 잔존(현재 통과, 범위 밖)
