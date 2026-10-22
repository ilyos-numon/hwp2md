# STATE — hwp2md

> 모든 세션의 진입점. 이 파일은 항상 "현재"만 담는다 (과거는 PROGRESS.md).
> 갱신 시점: 태스크 시작/종료, 단계 전환, 차단, 세션 종료 직전.
> 20줄을 넘기지 않는다. 태스크가 끝나면 "현재 태스크: 없음", 상태 IDLE.

- 현재 태스크: T-20261022-table-markdown
- 마지막 완료: T-20261022-stack-cli-smoke
- 플랜: `.ai/tasks/T-20261022-table-markdown/PLAN.md` (상태: APPROVED)
- 현재 단계: S4 / 7  — CLI 2행에 표 개수 (cli.py 전용)
- 상태: RUNNING
- 브랜치: `ai/T-20261022-table-markdown`
- 마지막 체크포인트: 2026-10-22 14:14 (S3 DONE)
- 마지막 커밋: [s3] read_blocks/render_blocks

## 다음 행동 (이어받는 작업자가 바로 실행)
1. S4 implementer(opus) 보고 대기 → 검증(E2E는 의도된 3 failed) → reviewer → 커밋 [s4] → S5(docs)

## 차단 중이면
- 이유: 
- 사용자 결정 필요 사항: 
