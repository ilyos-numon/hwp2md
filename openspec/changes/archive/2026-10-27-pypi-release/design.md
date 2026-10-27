# Design — pypi-release

## Context

- 빌드 백엔드 hatchling, `[tool.hatch.build.targets.wheel] packages = ["src/hwp2md"]`, sdist 설정 없음. hatchling sdist 기본값은 `.gitignore` 에 없는 추적 파일을 거의 다 담으므로 `.ai/`·`design/`·`openspec/`·`CLAUDE.md`·`.impeccable`·`tests/` 가 들어간다.
- 버전이 `pyproject.toml` 과 `src/hwp2md/__init__.py` 두 곳에 있다(둘 다 0.1.0).
- PyPI `hwp2md` 는 타인 소유 프로젝트. `hwp2markdown` 은 2026-10-27 기준 미등록(PyPI JSON API 404).
- 실제 샘플 `tests/fixtures/**` 는 라이선스 미확인이라 커밋하지 않는다. `tests/e2e/test_web_api.py`·`test_web_ui.py`·`test_web_v3.py` 는 모듈 수준 `next(p for p in REAL_SAMPLES ...)` 를 써서 샘플이 없으면 수집 단계에서 StopIteration 으로 깨진다. CI 체크아웃에는 샘플이 없다.
- 브라우저 모드 E2E 는 jsDelivr 의 Pyodide 를 받는다. GitHub 호스트 러너는 외부 네트워크가 열려 있다.
- 익명화 금지 패턴(`doc/portfolio/sanitize-rules.md`)은 워크스페이스 루트에만 있고 이 저장소에 넣을 수 없다(패턴 자체가 금지 문자열).

## Goals / Non-Goals

Goals: `pip install 'hwp2markdown[web]'` 로 설치, push·PR CI, 태그 하나로 PyPI 게시, 배포물에 허용 파일만.
Non-Goals: Docker 이미지, TestPyPI 리허설, 문서 사이트, 바이너리(pyinstaller) 배포, Windows·macOS CI 러너, 자동 버전 증가·변경 기록 생성, 저장소 공개 전환.

## Decisions

1. **배포 이름 `hwp2markdown`, 명령·import 는 `hwp2md`**: 사용자 결정. `[project.scripts]` 는 바꾸지 않는다.
2. **버전 단일 출처 = `__init__.py`**: `dynamic = ["version"]` + `[tool.hatch.version] path`. `__init__.py` 를 바꾸지 않고 pyproject 만 고친다. 대안(pyproject 를 출처로 두고 `importlib.metadata` 로 읽기)은 소스 트리에서 설치 없이 import 할 때 버전을 못 읽어 기각.
3. **sdist `only-include`**: 제외 목록(exclude) 방식은 새 디렉토리가 생기면 새어 나간다. 허용 목록으로 고정한다. tests 는 sdist 에 넣지 않는다(합성 생성기만 있어도 실제 샘플 README 가 따라온다).
4. **배포물 검사 = 저장소 안 `scripts/check_dist.py` (표준 라이브러리만)**: 구조 규칙(허용·금지 경로, 크기, 태그·버전)은 저장소에 두고 CI·릴리스 모두에서 돈다. 고유명사 패턴은 저장소 밖에 있으므로 `--patterns FILE` 선택 인자로만 받고, 로컬에서는 워크스페이스 `scripts/sanitize-check.sh` 를 git 저장소 밖에 푼 배포물에 돌린다(저장소 안 무시 경로에 풀면 sanitize-check 가 무시 파일로 보고 건너뛴다).
5. **CI 에서 실제 샘플 케이스 제외 = 마커 deselect**: `pytest.mark.real_samples` 로 표시하고 CI 만 `-m "not real_samples"`. skipif 를 쓰지 않으므로 로컬 `E2E_CMD` 에서 샘플이 없으면 여전히 실패한다(테스트 약화 아님). 모듈 수준 `next()` 는 기본값 `None` 으로 바꿔 수집이 깨지지 않게 한다.
6. **Trusted Publishing + environment `pypi`**: 장기 토큰 없음. PyPI 에서 pending publisher(프로젝트 `hwp2markdown`, owner 저장소 소유 계정, repo `hwp2md`, workflow `release.yml`, environment `pypi`)를 사용자가 한 번 등록한다.
7. **릴리스 build 와 CI dist 가 같은 명령**: release.yml 은 `workflow_dispatch` 를 두지 않는다(기본 브랜치에 없으면 동작하지 않음). 대신 CI `dist` job 이 같은 빌드·검사를 매 push 마다 돌리고, 태그·버전 검사는 로컬 E2E 로 실패 경로까지 확인한다.

## Risks / Trade-offs

- 비공개 저장소 + 무료 플랜에서는 GitHub environment 를 쓸 수 없을 수 있다 → 확인 후 안 되면 `environment:` 줄을 빼고 pending publisher 의 environment 칸을 비운다(PLAN §7).
- 비공개 저장소 Actions 사용 시간 한도 → e2e job 하나에 Playwright 설치 포함 약 10분. `concurrency` 로 같은 브랜치 이전 실행을 취소한다.
- README 의 상대 경로 그림(`docs/images/*`)은 PyPI 페이지에서 깨진다. 저장소가 비공개라 절대 URL 도 열리지 않는다 → 허용(PLAN §7).
- PyPI 게시는 되돌릴 수 없다(같은 버전 재업로드 불가). 사용자 승인 게이트 뒤에서만 태그를 push 한다.
