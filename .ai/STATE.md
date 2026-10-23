# STATE — hwp2md

> 모든 세션의 진입점. 이 파일은 항상 "현재"만 담는다 (과거는 PROGRESS.md).
> 갱신 시점: 태스크 시작/종료, 단계 전환, 차단, 세션 종료 직전.
> 20줄을 넘기지 않는다. 태스크가 끝나면 "현재 태스크: 없음", 상태 IDLE.

- 현재 태스크: T-20261023-extract-dropped
- 마지막 완료: T-20261023-docs-finalize (main 병합 완료)
- 플랜: `.ai/tasks/T-20261023-extract-dropped/PLAN.md` (상태: APPROVED)
- 현재 단계: R2 (S12~S14 병렬, 수동 worktree .claude/worktrees/s12·s13·s14) — 개체(칸 그림·캡션·글상자·차트), HWPML 요소
- 상태: RUNNING
- 브랜치: `ai/T-20261023-extract-dropped`
- 마지막 체크포인트: 2026-10-23 18:23 (S14 DONE)
- 마지막 커밋: d59ecd1 [s11] HWPML 2.x 입력

## 다음 행동 (이어받는 작업자가 바로 실행)
1. R2: worktree 3개 변경을 S12→S13→S14 순서로 패치 적용·검증(STD_VERIFY CELL_DESELECT)·단계별 커밋(경로 지정, git add -A 금지). worktree 정리

## 차단 중이면
- 이유: 없음 · 사용자 결정 필요: 없음 (Q1~Q10 승인 완료)
