# STATE — hwp2md

> 모든 세션의 진입점. 이 파일은 항상 "현재"만 담는다 (과거는 PROGRESS.md).
> 갱신 시점: 태스크 시작/종료, 단계 전환, 차단, 세션 종료 직전.
> 20줄을 넘기지 않는다. 태스크가 끝나면 "현재 태스크: 없음", 상태 IDLE.

- 현재 태스크: T-20261022-stack-cli-smoke
- 마지막 완료: 없음
- 플랜: `.ai/tasks/T-20261022-stack-cli-smoke/PLAN.md` (상태: APPROVED)
- 현재 단계: S2 / 9  — CLAUDE.md 명령 블록·전용 파일 추가분·.gitignore (orchestrator 직접)
- 상태: RUNNING
- 브랜치: `ai/T-20261022-stack-cli-smoke`
- 마지막 체크포인트: 2026-10-22 12:00 (S1 DONE)
- 마지막 커밋: [s1] pyproject.toml

## 다음 행동 (이어받는 작업자가 바로 실행)
1. S2: CLAUDE.md 명령 블록을 PLAN §4.7로, 추가분 §4.8, .gitignore 2줄 → 커밋 [s2] → S3 implementer(opus)

## 차단 중이면
- 이유: 
- 사용자 결정 필요 사항: 
