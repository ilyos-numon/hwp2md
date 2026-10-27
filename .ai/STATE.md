# STATE — hwp2md

> 모든 세션의 진입점. 이 파일은 항상 "현재"만 담는다 (과거는 PROGRESS.md).
> 갱신 시점: 태스크 시작/종료, 단계 전환, 차단, 세션 종료 직전.
> 20줄을 넘기지 않는다. 태스크가 끝나면 "현재 태스크: 없음", 상태 IDLE.

- 현재 태스크: T-20261027-binaries-brew
- 마지막 완료: T-20261027-adoption-links (PyPI 0.1.3)
- 플랜: `.ai/tasks/T-20261027-binaries-brew/PLAN.md` (APPROVED, §7 기본값 + Q1 PyInstaller 사용자 확인)
- OpenSpec: `openspec/changes/binaries-brew/`
- 현재 단계: S6 실행 파일 E2E
- 상태: RUNNING
- 브랜치: `ai/T-20261027-binaries-brew`

## 다음 행동 (이어받는 작업자가 바로 실행)
1. `/implement` S6부터. S8 탭 저장소 생성이 막히면 사용자 U1(웹에서 생성)

## 차단 중이면
- 이유: 없음
