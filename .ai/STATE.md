# STATE — hwp2md

> 모든 세션의 진입점. 이 파일은 항상 "현재"만 담는다 (과거는 PROGRESS.md).
> 갱신 시점: 태스크 시작/종료, 단계 전환, 차단, 세션 종료 직전.
> 20줄을 넘기지 않는다. 태스크가 끝나면 "현재 태스크: 없음", 상태 IDLE.

- 현재 태스크: T-20261022-hwpx-reader
- 마지막 완료: T-20261022-table-markdown
- 플랜: `.ai/tasks/T-20261022-hwpx-reader/PLAN.md` (상태: APPROVED)
- 현재 단계: S0 / 7  — 플랜 작성 완료, 사용자 승인 대기
- 상태: RUNNING
- 브랜치: `ai/T-20261022-hwpx-reader`
- 마지막 체크포인트: 2026-10-22 17:51 (S0 DONE)
- 마지막 커밋: 0a346b8 [T-20261022-table-markdown][done] (main에 ff 병합 완료)

## 다음 행동 (이어받는 작업자가 바로 실행)
1. 사용자 §7 답변 반영 → PLAN.md APPROVED → 커밋 → /implement (Stage 1은 orchestrator 직접: uv add lxml / lxml-stubs, fixtures/hwpx 이동)

## 차단 중이면
- 이유: 없음
- 사용자 결정 필요 사항: 없음
