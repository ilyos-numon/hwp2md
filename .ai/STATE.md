# STATE — hwp2md

> 모든 세션의 진입점. 이 파일은 항상 "현재"만 담는다 (과거는 PROGRESS.md).
> 갱신 시점: 태스크 시작/종료, 단계 전환, 차단, 세션 종료 직전.
> 20줄을 넘기지 않는다. 태스크가 끝나면 "현재 태스크: 없음", 상태 IDLE.

- 현재 태스크: T-20261027-pypi-release
- 마지막 완료: T-20261027-v3-backend (main 병합·푸시 6b75180)
- 플랜: `.ai/tasks/T-20261027-pypi-release/PLAN.md` (상태: APPROVED, §7 기본값)
- OpenSpec: `openspec/changes/pypi-release/`
- 현재 단계: S4 배포물 검사 스크립트
- 상태: RUNNING
- 브랜치: `ai/T-20261027-pypi-release`

## 다음 행동 (이어받는 작업자가 바로 실행)
1. `/implement` S4부터. 사용자 수동 U1·U2 는 S12 전까지

## 차단 중이면
- 이유: 없음 · 사용자 결정 필요: 없음
