# STATE — hwp2md

> 모든 세션의 진입점. 이 파일은 항상 "현재"만 담는다 (과거는 PROGRESS.md).
> 갱신 시점: 태스크 시작/종료, 단계 전환, 차단, 세션 종료 직전.
> 20줄을 넘기지 않는다. 태스크가 끝나면 "현재 태스크: 없음", 상태 IDLE.

- 현재 태스크: 없음
- 마지막 완료: T-20261023-web-preview (결과 검토 대기, main 병합 전)
- 플랜: `.ai/tasks/T-20261023-web-preview/PLAN.md` (상태: DONE), 결과: `.ai/tasks/T-20261023-web-preview/RESULT.md`
- 현재 단계: 없음
- 상태: IDLE
- 브랜치: `ai/T-20261023-web-preview` (main 병합 대기)
- 마지막 체크포인트: 2026-10-23 10:54 (S12 DONE)
- 마지막 커밋: 2cc095c [T-20261023-web-preview][s10] e2e: web ui both modes, no-upload, parity, screenshots

## 다음 행동 (이어받는 작업자가 바로 실행)
1. 사용자가 `.ai/tasks/T-20261023-web-preview/RESULT.md`를 검토·승인하면 `cd /Users/illi/illy-projects/hwp2md && git switch main && git merge --ff-only ai/T-20261023-web-preview` 실행.

## 차단 중이면
- 이유: 없음 · 사용자 결정 필요: 없음 (RESULT 검토·병합 승인 대기)
