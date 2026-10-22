# STATE — hwp2md

> 모든 세션의 진입점. 이 파일은 항상 "현재"만 담는다 (과거는 PROGRESS.md).
> 갱신 시점: 태스크 시작/종료, 단계 전환, 차단, 세션 종료 직전.
> 20줄을 넘기지 않는다. 태스크가 끝나면 "현재 태스크: 없음", 상태 IDLE.

- 현재 태스크: T-20261022-table-markdown
- 마지막 완료: T-20261022-stack-cli-smoke
- 플랜: `.ai/tasks/T-20261022-table-markdown/PLAN.md` (상태: APPROVED)
- 현재 단계: S5 / 7  — 결정 기록·README 현재 지원 갱신
- 상태: RUNNING
- 브랜치: `ai/T-20261022-table-markdown`
- 마지막 체크포인트: 2026-10-22 14:16 (S4 DONE)
- 마지막 커밋: [s4] cli table count

## 다음 행동 (이어받는 작업자가 바로 실행)
1. S5 implementer(opus) 보고 대기 → grep 검증 → 커밋 [s5] → S6 test-writer(sonnet) E2E

## 차단 중이면
- 이유: 
- 사용자 결정 필요 사항: 
