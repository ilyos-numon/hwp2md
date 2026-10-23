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
INSTALL_CMD: uv sync && uv run playwright install chromium
DEV_CMD: uv run hwp2md serve --no-browser --port 8765
DEV_URL: http://localhost:8765
DEV_READY: curl -sf http://localhost:8765/api/health >/dev/null
BUILD_CMD: (none)
LINT_CMD: uv run ruff check src tests && uv run ruff format --check src tests
TYPECHECK_CMD: uv run mypy src
TEST_CMD: uv run pytest tests/unit -q
E2E_CMD: uv run pytest tests/e2e -q
E2E_ONE: uv run pytest {file} -q
E2E_DIR: tests/e2e
```

## 이 프로젝트의 orchestrator 전용 파일 (추가분)
- `src/hwp2md/cli.py` (CLI 진입점. 변경은 그 파일만 갖는 별도 단계로)
- `pyproject.toml` 의 `[project.scripts]` (상위 목록에 이미 포함, 재확인용)
