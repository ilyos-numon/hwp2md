# PyPI 배포(hwp2markdown) + GitHub Actions CI

## Why

hwp2md 는 소스를 받아 `uv sync` 해야만 쓸 수 있다. 한 줄 `pip install` 로 설치할 수 없고, push·PR 마다 lint·타입·단위·E2E 를 자동으로 돌리는 CI 도 없다. PyPI 의 `hwp2md` 이름은 타인 소유 프로젝트(2026-04 배포, 활성)가 쓰고 있어 같은 이름으로는 배포할 수 없다. 저장소는 비공개지만 sdist·wheel 은 공개되므로, 작업 기록(`.ai/`)·시안(`design/`)·스펙(`openspec/`)·에이전트 설정·실제 샘플이 배포물에 섞이면 안 된다.

## What Changes

- 배포 이름을 `hwp2markdown` 으로 바꾼다. 실행 명령 `hwp2md` 와 import 이름 `hwp2md` 는 그대로다.
- 버전은 `src/hwp2md/__init__.py` 의 `__version__` 한 곳에서만 정한다(hatch 동적 버전). `pyproject.toml` 의 `version` 줄을 없앤다.
- sdist 포함 파일을 허용 목록(`src/hwp2md`, `README.md`, `LICENSE`, `NOTICE`, `pyproject.toml`)으로 제한하고, `LICENSE`·`NOTICE` 를 license-files 로 wheel 에 싣는다.
- 새 스크립트 `scripts/check_dist.py` 가 sdist·wheel 의 파일 목록을 허용·금지 규칙으로 대조하고, 태그와 버전 일치, 선택적 금지 패턴 검사를 한다. 위반이 있으면 종료 코드 1.
- `hwp2md serve` 의 web extra 미설치 안내를 `pip install 'hwp2markdown[web]'` 로 바꾼다(타인 소유 `hwp2md` 를 설치하게 만들지 않기 위해). **BREAKING**: 안내 문자열이 바뀐다.
- 실제 샘플(커밋하지 않는 `tests/fixtures/**`)이 필요한 E2E 를 마커 `real_samples` 로 표시해 CI 에서 제외할 수 있게 한다. 로컬 `E2E_CMD` 는 전부 그대로 돈다.
- `.github/workflows/ci.yml`: push·PR 에 lint, typecheck, unit, e2e(Playwright chromium), dist(빌드+배포물 검사).
- `.github/workflows/release.yml`: 태그 `vX.Y.Z` push → build → GitHub environment `pypi` 에서 Trusted Publishing 으로 PyPI 게시. 장기 API 토큰은 쓰지 않는다.
- `docs/releasing.md` 에 사용자가 한 번 하는 수동 절차(PyPI pending publisher 등록, GitHub environment 생성)와 릴리스 절차를 적는다. README 설치·한계·로드맵을 갱신한다.

## Capabilities

### New Capabilities
- `distribution`: 배포 이름·버전 출처·배포물 내용 제한·배포물 검사·CI·태그 릴리스

### Modified Capabilities
- `web-preview`: web extra 미설치 안내 문자열이 배포 이름 `hwp2markdown[web]` 을 가리킨다

## Impact

- 파일: `pyproject.toml`, `uv.lock`, `src/hwp2md/cli.py`(안내 1줄), `src/hwp2md/web/__init__.py`(docstring), `scripts/check_dist.py`(새 파일), `tests/e2e/conftest.py` 와 실제 샘플을 쓰는 E2E 파일(마커), `tests/e2e/test_dist_package.py`(새 파일), `.github/workflows/ci.yml`·`release.yml`(새 파일), `README.md`, `docs/releasing.md`(새 파일), `docs/decisions.md`, `docs/feature-reference.md`
- 외부: PyPI 프로젝트 `hwp2markdown`(첫 게시 시 생성), GitHub environment `pypi`, GitHub Actions 사용 시간(비공개 저장소 분 단위 과금 한도)
- 변환 동작·API·화면은 바뀌지 않는다
