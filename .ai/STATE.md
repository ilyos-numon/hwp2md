# STATE — hwp2md

> 모든 세션의 진입점. 이 파일은 항상 "현재"만 담는다 (과거는 PROGRESS.md).
> 갱신 시점: 태스크 시작/종료, 단계 전환, 차단, 세션 종료 직전.
> 20줄을 넘기지 않는다. 태스크가 끝나면 "현재 태스크: 없음", 상태 IDLE.

- 현재 태스크: T-20261023-extract-dropped
- 마지막 완료: T-20261023-docs-finalize (main 병합 완료)
- 플랜: `.ai/tasks/T-20261023-extract-dropped/PLAN.md` (상태: APPROVED)
- 현재 단계: S4 / 27 — 결과·페이로드 건너뜀 연결
- 상태: RUNNING
- 브랜치: `ai/T-20261023-extract-dropped`
- 마지막 체크포인트: 2026-10-23 17:47 (S3 DONE)
- 마지막 커밋: ae6ed95 [s0] V3 시안·기능 명세 선행 커밋

## 다음 행동 (이어받는 작업자가 바로 실행)
1. S4(implementer opus): convert/memory/__init__/리더 read_blocks 에 skipped 연결 (PLAN §5 Stage 4, §4-E)

## 차단 중이면
- 이유: 없음 · 사용자 결정 필요: 없음 (Q1~Q10 승인 완료)
