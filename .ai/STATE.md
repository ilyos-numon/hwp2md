# STATE — hwp2md

> 모든 세션의 진입점. 이 파일은 항상 "현재"만 담는다 (과거는 PROGRESS.md).
> 갱신 시점: 태스크 시작/종료, 단계 전환, 차단, 세션 종료 직전.
> 20줄을 넘기지 않는다. 태스크가 끝나면 "현재 태스크: 없음", 상태 IDLE.

- 현재 태스크: T-20261022-hwpx-reader
- 마지막 완료: T-20261022-table-markdown
- 플랜: `.ai/tasks/T-20261022-hwpx-reader/PLAN.md` (상태: APPROVED)
- 현재 단계: S2 / 7  — HWPX 섹션 파서와 리더 (hwpx/body.py, hwpx/reader.py)
- 상태: RUNNING
- 브랜치: `ai/T-20261022-hwpx-reader`
- 마지막 체크포인트: 2026-10-22 17:54 (S1 DONE)
- 마지막 커밋: [s1] deps lxml

## 다음 행동 (이어받는 작업자가 바로 실행)
1. S2 implementer(opus) 보고 대기 → runner 검증(실제 샘플 3개 기대값 (1,1)(80,31)(32,8)) → reviewer → 커밋 [s2] → S3

## 차단 중이면
- 이유: 없음
- 사용자 결정 필요 사항: 없음
