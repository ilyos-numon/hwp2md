# STATE — hwp2md

> 모든 세션의 진입점. 이 파일은 항상 "현재"만 담는다 (과거는 PROGRESS.md).
> 갱신 시점: 태스크 시작/종료, 단계 전환, 차단, 세션 종료 직전.
> 20줄을 넘기지 않는다. 태스크가 끝나면 "현재 태스크: 없음", 상태 IDLE.

- 현재 태스크: T-20261022-image-extract
- 마지막 완료: T-20261022-heading-levels
- 플랜: `.ai/tasks/T-20261022-image-extract/PLAN.md` (상태: APPROVED)
- 현재 단계: S5 / 9  — HWPX 리더 hp:pic → Image·교차 포맷
- 상태: RUNNING
- 브랜치: `ai/T-20261022-image-extract`
- 마지막 체크포인트: 2026-10-23 00:07 (S4 DONE)
- 마지막 커밋: ad99b4d [T-20261022-heading-levels][s8] e2e: heading levels both formats, edge cases, real samples

## 다음 행동 (이어받는 작업자가 바로 실행)
1. 사용자가 `.ai/tasks/T-20261022-heading-levels/RESULT.md`를 검토하고 승인하면 `cd /Users/illi/illy-projects/hwp2md && git switch main && git merge --ff-only ai/T-20261022-heading-levels` 실행

## 차단 중이면
- 이유:
- 사용자 결정 필요 사항:
