# STATE — hwp2md

> 모든 세션의 진입점. 이 파일은 항상 "현재"만 담는다 (과거는 PROGRESS.md).
> 갱신 시점: 태스크 시작/종료, 단계 전환, 차단, 세션 종료 직전.
> 20줄을 넘기지 않는다. 태스크가 끝나면 "현재 태스크: 없음", 상태 IDLE.

- 현재 태스크: T-20261023-web-preview
- 마지막 완료: T-20261022-image-extract (main 병합 완료)
- 플랜: `.ai/tasks/T-20261023-web-preview/PLAN.md` (상태: APPROVED)
- 현재 단계: S8 — 브라우저 전용 모드
- 상태: RUNNING
- 브랜치: `ai/T-20261023-web-preview`
- 마지막 체크포인트: 2026-10-23 10:31 (S7 DONE)
- 마지막 커밋: 51416b6 [T-20261022-image-extract][s8] e2e: image extraction both formats, reuse/cell/missing, real samples

## 다음 행동 (이어받는 작업자가 바로 실행)
1. 사용자가 PLAN §7 Q1~Q7에 답하거나 "기본값으로"라고 하면 답을 반영하고 상태를 APPROVED로 바꾼 뒤 `/implement` S1 시작.

## 차단 중이면
- 이유: 없음
- 사용자 결정 필요 사항: 없음
