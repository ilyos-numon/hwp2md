# STATE — hwp2md

> 모든 세션의 진입점. 이 파일은 항상 "현재"만 담는다 (과거는 PROGRESS.md).
> 갱신 시점: 태스크 시작/종료, 단계 전환, 차단, 세션 종료 직전.
> 20줄을 넘기지 않는다. 태스크가 끝나면 "현재 태스크: 없음", 상태 IDLE.

- 현재 태스크: T-20261023-extract-dropped
- 마지막 완료: T-20261023-docs-finalize (main 병합 완료)
- 플랜: `.ai/tasks/T-20261023-extract-dropped/PLAN.md` (상태: APPROVED)
- 현재 단계: P1 (S5~S8 병렬, worktree) — 보호 문서·수식·OLE 차트·배포용 복호
- 상태: RUNNING
- 브랜치: `ai/T-20261023-extract-dropped`
- 마지막 체크포인트: 2026-10-23 17:59 (S5 DONE)
- 마지막 커밋: ae6ed95 [s0] V3 시안·기능 명세 선행 커밋

## 다음 행동 (이어받는 작업자가 바로 실행)
1. P1 묶음 S5·S6·S7·S8 를 worktree 로 병렬 실행 → 단계 번호 순서로 diff 적용·검증·단계별 커밋 (PLAN §6)

## 차단 중이면
- 이유: 없음 · 사용자 결정 필요: 없음 (Q1~Q10 승인 완료)
