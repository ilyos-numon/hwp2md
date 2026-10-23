# STATE — hwp2md

> 모든 세션의 진입점. 이 파일은 항상 "현재"만 담는다 (과거는 PROGRESS.md).
> 갱신 시점: 태스크 시작/종료, 단계 전환, 차단, 세션 종료 직전.
> 20줄을 넘기지 않는다. 태스크가 끝나면 "현재 태스크: 없음", 상태 IDLE.

- 현재 태스크: T-20261023-extract-dropped
- 마지막 완료: T-20261023-docs-finalize (main 병합 완료)
- 플랜: `.ai/tasks/T-20261023-extract-dropped/PLAN.md` (상태: APPROVED)
- 현재 단계: R3 (S15~S17 병렬, 수동 worktree .claude/worktrees/s15·s16·s17) — HWP5·HWPX 목록, 배포용 문서 읽기
- 상태: RUNNING
- 브랜치: `ai/T-20261023-extract-dropped`
- 마지막 체크포인트: 2026-10-23 18:32 (S16 DONE)
- 마지막 커밋: 81169a0 [s14] HWPML 요소

## 다음 행동 (이어받는 작업자가 바로 실행)
1. R3: worktree 3개 변경을 S15→S16→S17 순서로 패치 적용·검증(CELL_DESELECT 4개)·단계별 커밋(경로 지정). worktree 정리. 다음 S18 교차 포맷(혼합 단락 fixture 추가)

## 차단 중이면
- 이유: 없음 · 사용자 결정 필요: 없음 (Q1~Q10 승인 완료)
