# hwp2md

상위 원칙: ../PRINCIPLES.md 참조

## 한 줄 설명
한국의 공공·기업 문서는 HWP 안에 갇혀 있다.

## 현재 단계
MVP 착수 전. README.md의 MVP 범위만 구현한다.

## 작업 규칙
- README.md "하지 않는 것"에 있는 기능은 제안하지 않는다
- 기술 선택·범위 변경은 docs/decisions.md에 날짜와 이유를 남긴다
- 외부 API 키는 .env로, 커밋 금지
- 완료 기준: README MVP 항목이 실제로 동작하고 실행 방법이 README에 있다

## 에이전트 작업
- 상위 `../CLAUDE.md` 규칙이 먼저 적용된다. 상태는 `.ai/STATE.md`에만 적는다 (이 파일에 적지 않는다).
- 명령 블록이 비어 있으면 `/plan`의 S1은 "스택 확정 + 스캐폴드 + 명령 블록 채우기 + 스모크 E2E"다.

## 명령 (에이전트가 그대로 실행한다 — 스택 확정 후 채운다. (none)은 그 검증 생략)
```
INSTALL_CMD: (채워 넣을 것)
DEV_CMD: (채워 넣을 것)
DEV_URL: http://localhost:PORT
DEV_READY: (채워 넣을 것)
BUILD_CMD: (none)
LINT_CMD: (채워 넣을 것)
TYPECHECK_CMD: (채워 넣을 것)
TEST_CMD: (채워 넣을 것)
E2E_CMD: (채워 넣을 것)
E2E_ONE: (채워 넣을 것)
E2E_DIR: tests/e2e
```

## 이 프로젝트의 orchestrator 전용 파일 (추가분)
- (스택 확정 후 진입점·라우터·마이그레이션 인덱스 경로를 적는다)
