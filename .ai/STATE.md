# STATE — hwp2md

> 모든 세션의 진입점. 이 파일은 항상 "현재"만 담는다 (과거는 PROGRESS.md).
> 갱신 시점: 태스크 시작/종료, 단계 전환, 차단, 세션 종료 직전.
> 20줄을 넘기지 않는다. 태스크가 끝나면 "현재 태스크: 없음", 상태 IDLE.

- 현재 태스크: T-20261023-extract-dropped
- 마지막 완료: T-20261023-docs-finalize (main 병합 완료)
- 플랜: `.ai/tasks/T-20261023-extract-dropped/PLAN.md` (상태: APPROVED)
- 현재 단계: R1 (S9~S11 병렬, 수동 worktree .claude/worktrees/s9·s10·s11) — HWP5·HWPX 단락 요소, HWPML
- 상태: RUNNING
- 브랜치: `ai/T-20261023-extract-dropped`
- 마지막 체크포인트: 2026-10-23 18:11 (S10 DONE)
- 마지막 커밋: 1acb24c [s8] 배포용 문서 복호 모듈

## 다음 행동 (이어받는 작업자가 바로 실행)
1. R1: worktree 3개의 변경을 S9→S10→S11 순서로 메인에 복사·검증·단계별 커밋. worktree 는 git worktree remove 로 정리

## 차단 중이면
- 이유: 없음 · 사용자 결정 필요: 없음 (Q1~Q10 승인 완료)
