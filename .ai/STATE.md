# STATE — hwp2md

> 모든 세션의 진입점. 이 파일은 항상 "현재"만 담는다 (과거는 PROGRESS.md).
> 갱신 시점: 태스크 시작/종료, 단계 전환, 차단, 세션 종료 직전.
> 20줄을 넘기지 않는다. 태스크가 끝나면 "현재 태스크: 없음", 상태 IDLE.

- 현재 태스크: T-20261022-hwpx-reader
- 마지막 완료: T-20261022-table-markdown
- 플랜: `.ai/tasks/T-20261022-hwpx-reader/PLAN.md` (상태: APPROVED)
- 현재 단계: S4 / 7  — 포맷 감지와 convert 디스패치 (detect.py, convert.py, __init__.py)
- 상태: RUNNING
- 브랜치: `ai/T-20261022-hwpx-reader`
- 마지막 체크포인트: 2026-10-22 18:04 (S3 DONE)
- 마지막 커밋: [s3] synth hwpx

## 다음 행동 (이어받는 작업자가 바로 실행)
1. S4 implementer(opus) 보고 대기 → runner(실제 샘플 CLI 3개) → reviewer → 커밋 [s4] → S5(docs). Stage 4b는 기본값이라 건너뜀

## 차단 중이면
- 이유: 없음
- 사용자 결정 필요 사항: 없음
