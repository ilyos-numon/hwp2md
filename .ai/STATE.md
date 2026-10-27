# STATE — hwp2md

> 모든 세션의 진입점. 이 파일은 항상 "현재"만 담는다 (과거는 PROGRESS.md).
> 갱신 시점: 태스크 시작/종료, 단계 전환, 차단, 세션 종료 직전.
> 20줄을 넘기지 않는다. 태스크가 끝나면 "현재 태스크: 없음", 상태 IDLE.

- 현재 태스크: T-20261027-public-launch
- 마지막 완료: T-20261027-pypi-release (v0.1.0 PyPI 게시)
- 플랜: `.ai/tasks/T-20261027-public-launch/PLAN.md` (상태: APPROVED, §7 기본값 — 사용자 "알아서 해")
- OpenSpec: `openspec/changes/public-launch/`
- 현재 단계: S5 패키지 메타데이터
- 상태: RUNNING
- 브랜치: `ai/T-20261027-public-launch`

## 다음 행동 (이어받는 작업자가 바로 실행)
1. `/implement` S5(패키지 메타데이터)부터. S10 은 사용자 승인 게이트

## 차단 중이면
- 이유: 없음 · 사용자 결정 필요: 없음 (S10 에서 게이트)
