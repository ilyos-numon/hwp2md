# PLAN — T-20261027-pypi-release PyPI 배포(hwp2markdown) + GitHub Actions CI

> 작성: planner(opus) · 2026-10-27 · 프로젝트: hwp2md
> 상태: DRAFT → APPROVED → DONE  (현재: APPROVED)
> 이 플랜은 sonnet 등급 모델이 추가 질문 없이 그대로 실행할 수 있을 만큼 구체적이어야 한다.
> 모든 Bash 는 `cd /Users/illi/illy-projects/hwp2md && ` 로 시작한다. macOS: `timeout` 없음, zsh PIPESTATUS 비어 있음 → 종료 코드는 `; echo exit=$?` 로 받는다.

## 0. 한 줄 목표
사용자는 `pip install 'hwp2markdown[web]'` 한 줄로 hwp2md 를 설치해 `hwp2md` 명령을 쓸 수 있고, 저장소 push·PR 마다 GitHub Actions 가 lint·mypy·unit·E2E·배포물 검사를 돌리며, 태그 `vX.Y.Z` push 하나로 PyPI 에 게시할 수 있다.

### 0.1 OpenSpec 연동
- change: `openspec/changes/pypi-release/` · 검증: `source ~/.nvm/nvm.sh >/dev/null 2>&1 && openspec validate pypi-release` (작성 시점 결과: `Change 'pypi-release' is valid`)
- capability: 새 `distribution`, 수정 `web-preview`(web extra 안내 문자열)
- tasks.md 체크는 orchestrator 가 단계 DONE 커밋에서 한다. tasks.md 의 모든 `- [ ] N.M` 이 아래 표에 정확히 한 행.

| tasks.md 항목 | 내용(요약) | Stage |
|---------------|-----------|-------|
| 1.1 | 클린 체크아웃 기준선·PyPI 이름 가용성 기록 | S1 |
| 2.1 | pyproject 배포 이름·동적 버전·license-files·sdist 허용 목록, uv.lock | S2 |
| 2.2 | cli.py web extra 안내 `hwp2markdown[web]` | S3 |
| 3.1 | `scripts/check_dist.py` | S4 |
| 4.1 | `real_samples` 마커·수집 오류 제거·안내 단언 갱신 | S5 |
| 5.1 | `.github/workflows/ci.yml` | S6 |
| 5.2 | `.github/workflows/release.yml` | S7 |
| 6.1 | README·feature-reference·decisions·web/__init__ 안내 갱신 | S8 |
| 6.2 | `docs/releasing.md` 수동·릴리스 절차 | S8 |
| 7.1 | `tests/e2e/test_dist_package.py` 작성·실행 | S9 |
| 7.2 | 브랜치 push 후 CI 다섯 job success | S10 |
| 7.3 | diff 리뷰·RESULT | S11 |
| 8.1 | 사용자 승인 뒤 main 병합·태그 push·PyPI 설치 확인 | S12 |

## 1. 범위
### 포함 (IN)
- `pyproject.toml`: `name = "hwp2markdown"`, `dynamic = ["version"]`, `[tool.hatch.version]`, `license-files`, `[tool.hatch.build.targets.sdist] only-include`, hatchling 하한 상향. `uv.lock` 재생성.
- `src/hwp2md/cli.py` 49행 안내 문자열 1줄, `src/hwp2md/web/__init__.py` docstring 1줄.
- 새 파일 `scripts/check_dist.py` (표준 라이브러리만).
- `tests/e2e/conftest.py` 마커 등록, 실제 샘플 의존 E2E 파일의 마커·모듈 수준 `next()` 수정, `tests/e2e/test_web_api.py` 179행 단언 갱신.
- 새 파일 `.github/workflows/ci.yml`, `.github/workflows/release.yml`.
- 문서: `README.md`(설치·한계·로드맵), 새 `docs/releasing.md`, `docs/decisions.md`(결정 2건), `docs/feature-reference.md`(안내 문자열).
- 새 E2E `tests/e2e/test_dist_package.py`.
- 사용자 승인 뒤: main 병합, 태그 `v0.1.0` push, PyPI 게시 확인.

### 제외 (OUT) — 절대 건드리지 않는다
- Docker 이미지·컨테이너 실행 (기억: Docker Desktop 프록시가 pull 을 막는다)
- TestPyPI 리허설 업로드 (§7 Q3)
- 저장소 공개 전환, 브랜치 보호 규칙, GitHub 설정을 API 로 바꾸는 일 (사용자 수동 절차 문서로만)
- `[project.urls]`·authors·classifiers 등 추가 메타데이터 (저장소 비공개라 URL 이 404)
- 변환 로직·웹 화면·API 동작 변경, `__version__` 값 변경(0.1.0 유지)
- Windows·macOS CI 러너, 자동 버전 증가·CHANGELOG 생성, pyinstaller 바이너리
- 실제 샘플(`tests/fixtures/**`)을 저장소·CI·배포물에 넣는 일
- README 그림의 PyPI 표시 문제 해결 (§7 Q4)

### 건드리면 안 되는 파일/디렉토리
- `pyproject.toml` 의 `[project.scripts]` 절 (값 `hwp2md = "hwp2md.cli:main"` 유지)
- `src/hwp2md/**` 중 `cli.py` 49행과 `web/__init__.py` 1행 docstring 을 뺀 전부 (`__init__.py` 포함)
- `tests/fixtures/**`, `tests/unit/**`, `tests/samples.py`, `tests/synth_*.py`
- `design/**`, `openspec/specs/**`(archive 가 반영), `.gitignore`, `CLAUDE.md`, `.ai/STATE.md`, `NOTICE`, `LICENSE`
- 워크스페이스 `../doc/my_info/**`, `../scripts/**`

## 2. 성공 기준 (전부 만족해야 DONE — C1~C13. R1~R3 은 S12 승인 시에만)
| # | 기준 | 검증 명령 | 기대 결과 |
|---|------|-----------|-----------|
| C1 | 빌드 산출물 이름 | `rm -rf dist && uv build --out-dir dist && ls dist` | 정확히 `hwp2markdown-0.1.0-py3-none-any.whl`, `hwp2markdown-0.1.0.tar.gz` 2개 |
| C2 | 메타데이터 유효 | `uvx --from 'twine>=6.1' twine check --strict dist/*` | 두 줄 모두 `PASSED`, exit 0 |
| C3 | 배포물 구조 검사 | `uv run python scripts/check_dist.py dist --tag v0.1.0; echo exit=$?` | `check_dist: OK ...` 한 줄, `exit=0` |
| C4 | 배포물 익명화 검사 | `X=$(mktemp -d) && tar -xzf dist/*.tar.gz -C "$X" && mkdir "$X/whl" && unzip -q dist/*.whl -d "$X/whl" && $ILLY_ROOT/scripts/sanitize-check.sh "$X"; echo exit=$?` (반드시 git 저장소 밖 임시 디렉토리) | `exit=0` |
| C5 | 버전 단일 출처 | `grep -cE '^version *=' pyproject.toml; uv lock --check; echo exit=$?` | `0` 출력, `exit=0` |
| C6 | 정적 검사·단위 | LINT_CMD; TYPECHECK_CMD; TEST_CMD | 셋 다 exit 0, 실패 0 |
| C7 | 로컬 E2E 전체(실제 샘플 포함) | `uv run pytest tests/e2e -q` | 실패 0, 오류 0 |
| C8 | CI 동등 E2E (샘플 없는 클린 복사본) | §4.7 클린 복사 후 그 안에서 `uv sync --locked && uv run pytest tests/e2e -q -m "not real_samples"` | 실패 0, 오류 0, collection error 0 |
| C9 | 배포 E2E 성공·실패 경로 | `uv run pytest tests/e2e/test_dist_package.py -q -rA` | 4건 이상 pass (성공 1 + 실패 3), skip 0 |
| C10 | 워크플로우 문법 | `uvx --from actionlint-py actionlint .github/workflows/ci.yml .github/workflows/release.yml; echo exit=$?` | `exit=0` (도구 다운로드 실패 시 PROGRESS 에 `SKIP actionlint: <오류 한 줄>` 기록 후 C11 로 대체) |
| C11 | 실제 CI | §4.8 `gh run watch <id> --exit-status` 후 `gh run view <id> --json jobs --jq '.jobs[]|[.name,.conclusion]|@tsv'` | `lint`·`typecheck`·`unit (3.11)`·`unit (3.13)`·`e2e`·`dist` 전부 `success` |
| C12 | 저장소 익명화 | `$ILLY_ROOT/scripts/sanitize-check.sh /Users/illi/illy-projects/hwp2md; echo exit=$?` | `exit=0` |
| C13 | OpenSpec | `source ~/.nvm/nvm.sh >/dev/null 2>&1 && openspec validate pypi-release` | `Change 'pypi-release' is valid` |
| R1 | Release 실행 (S12) | `gh run watch <release run id> --exit-status` | `build`·`publish` success |
| R2 | PyPI 설치 (S12) | `V=$(mktemp -d) && uv venv "$V/v" -q && uv pip install --python "$V/v/bin/python" 'hwp2markdown[web]==0.1.0' && "$V/v/bin/hwp2md" --version` | `hwp2md 0.1.0` |
| R3 | PyPI 메타데이터 (S12) | `curl -s https://pypi.org/pypi/hwp2markdown/json \| python3 -c 'import json,sys;d=json.load(sys.stdin);print(d["info"]["version"],sorted(u["packagetype"] for u in d["urls"]))'` | `0.1.0 ['bdist_wheel', 'sdist']` |

UI 변경이 없으므로 스크린샷 기준은 없다 (기존 E2E 스크린샷은 C7·C8 이 그대로 만든다).

## 3. 실패 기준 (하나라도 해당하면 즉시 중단 → BLOCKED 기록)
- 같은 단계 재시도 3회 초과
- 같은 오류로 수정 2회 실패
- 단계 하나 도구 호출 40회 초과 → PARTIAL 기록 후 반환 (60회는 maxTurns 강제 상한)
- 단계 하나 40분 초과 (S10 의 CI 대기는 실행당 30분 상한)
- S1 에서 클린 복사본의 LINT·TYPECHECK·TEST 가 실패하거나, 실제 샘플이 아닌 이유로 E2E 가 실패 → BLOCKED (플랜 가정 붕괴, planner 재호출)
- S1 에서 `https://pypi.org/pypi/hwp2markdown/json` 이 404 가 아님 → BLOCKED (사용자 이름 결정 필요)
- `[project.scripts]`·`__init__.py`·`tests/unit/**` 수정 없이는 진행 불가 → BLOCKED
- C4 또는 C12 실패 → 커밋 금지, BLOCKED (금지 문자열을 어디서 지울지 사용자 결정)
- git push 가 `workflow` scope 부족으로 거절 → BLOCKED (사용자 수동 U4)
- PyPI·GitHub 자격증명·결제·계정 설정이 필요 → BLOCKED (사용자 수동 U1~U4)
- S12 에서 사용자 승인 없이 태그 push·main 병합을 해야 하는 상황 → 하지 않고 대기

## 4. 인터페이스 계약 (병렬 작업 전 확정)
병렬 단계는 없지만, 단계 사이에 넘겨받는 이름·형식을 여기서 고정한다. 단계가 이 값을 바꾸면 BLOCKED.

### 4.1 이름·버전
| 항목 | 값 |
|------|----|
| 배포 이름 (PyPI) | `hwp2markdown` |
| 콘솔 명령 / import | `hwp2md` / `hwp2md` (`[project.scripts] hwp2md = "hwp2md.cli:main"` 그대로) |
| 버전 출처 | `src/hwp2md/__init__.py` 의 `__version__ = "0.1.0"` (유일) |
| 태그 형식 | `vX.Y.Z` (정규식 `^v\d+\.\d+\.\d+$`), 첫 릴리스 `v0.1.0` |
| 산출물 | `hwp2markdown-<V>.tar.gz`, `hwp2markdown-<V>-py3-none-any.whl` |
| web extra 안내 | `web extra not installed — pip install 'hwp2markdown[web]'` |
| pytest 마커 | `real_samples` (설명: `needs uncommitted real samples in tests/fixtures`) |
| GitHub environment | `pypi` (url `https://pypi.org/project/hwp2markdown/`) |
| 워크플로우 파일 | `.github/workflows/ci.yml` (name `CI`), `.github/workflows/release.yml` (name `Release`) |
| CI job id | `lint`, `typecheck`, `unit`(matrix python `3.11`,`3.13` → 표시 이름 `unit (3.11)`), `e2e`, `dist` |
| Release job id | `build`, `publish` |
| 산출물 artifact 이름 | `dist` |

### 4.2 pyproject.toml 목표 상태 (변경 부분만)
```toml
[project]
name = "hwp2markdown"
dynamic = ["version"]          # 기존 version = "0.1.0" 줄 삭제
license = "MIT"
license-files = ["LICENSE", "NOTICE"]
# description·readme·requires-python·dependencies·optional-dependencies·[project.scripts] 는 그대로

[build-system]
requires = ["hatchling>=1.27"]

[tool.hatch.version]
path = "src/hwp2md/__init__.py"

[tool.hatch.build.targets.sdist]
only-include = ["src/hwp2md", "README.md", "LICENSE", "NOTICE", "pyproject.toml"]
exclude = ["__pycache__", "*.pyc"]

[tool.hatch.build.targets.wheel]
packages = ["src/hwp2md"]      # 그대로
exclude = ["__pycache__", "*.pyc"]
```

### 4.3 `scripts/check_dist.py` CLI
```
uv run python scripts/check_dist.py DIST_DIR [--tag vX.Y.Z] [--patterns FILE]
```
- 표준 라이브러리만(argparse, tarfile, zipfile, re, email.parser, pathlib). Python 3.11. `def main(argv: list[str] | None = None) -> int` + `if __name__ == "__main__": raise SystemExit(main())`.
- DIST_DIR 에 `hwp2markdown-*.tar.gz` 정확히 1개, `hwp2markdown-*-py3-none-any.whl` 정확히 1개가 있어야 한다. 아니면 `missing-artifact`.
- 규칙 (경로는 sdist 최상위 `hwp2markdown-<V>/` 를 뗀 상대 경로 기준, 금지가 허용보다 먼저):
  - 금지 `forbidden-path`: 경로 조각이 `.ai`·`design`·`openspec`·`tests`·`docs`·`.impeccable`·`.github`·`logs`·`out`·`screenshots`·`__pycache__` 중 하나 / 파일 이름이 `CLAUDE.md`·`uv.lock`·`.DS_Store` 또는 `.env` 로 시작 / 확장자 `.hwp`·`.hwpx`·`.hwpml`·`.pyc`
  - sdist 허용: `PKG-INFO`, `pyproject.toml`, `README.md`, `LICENSE`, `NOTICE`, `.gitignore`, `src/hwp2md/**` → 그 밖은 `not-allowed`
  - wheel 허용: `hwp2md/**`, `hwp2markdown-<V>.dist-info/**` → 그 밖은 `not-allowed`. dist-info 에 `licenses/LICENSE`·`licenses/NOTICE` 가 없으면 `missing-license`
  - 크기: 각 파일 5 MiB 초과 → `too-large`
  - `--tag`: 형식 불일치 또는 `tag[1:] != wheel METADATA Version` → `version-mismatch`
  - `--patterns`: 빈 줄·`#` 줄 제외, 각 줄을 `re.compile(p, re.IGNORECASE)`. UTF-8 로 읽히는 멤버의 각 줄에 적용. 적중 → `pattern-hit` (출력은 `<멤버>:<줄번호>` 만, 적중 문자열 금지)
- 출력·종료 코드: 위반마다 `check_dist: FAIL <archive 파일명>: <멤버 또는 ->: <사유>` 한 줄, 하나라도 있으면 exit 1. 위반 0 이면 `check_dist: OK sdist=<n> wheel=<m> version=<V>` 한 줄, exit 0. 인자 오류·DIST_DIR 없음은 exit 2.

### 4.4 ci.yml 골격 (값 고정, 세부 문법은 S6)
- `on: push: branches: ["**"]` + `pull_request:` (태그 push 로는 돌지 않음). `permissions: contents: read`. `concurrency: { group: ci-${{ github.ref }}, cancel-in-progress: true }`.
- 공통 준비: `actions/checkout` → `astral-sh/setup-uv`(`enable-cache: true`, `python-version` 입력) → `uv sync --locked`.
- `lint`: `uv run ruff check src tests && uv run ruff format --check src tests` · `typecheck`: `uv run mypy src` · `unit`: matrix `python: ["3.11", "3.13"]`, `uv run pytest tests/unit -q -m "not real_samples"` · `e2e`(python 3.12, timeout-minutes 30): `uv run playwright install --with-deps chromium` → `uv run pytest tests/e2e -q -m "not real_samples"`, 실패 시 `tests/e2e/screenshots/` 를 artifact `e2e-screenshots` 로 업로드 · `dist`: `uv build --out-dir dist` → `uvx --from 'twine>=6.1' twine check --strict dist/*` → `uv run python scripts/check_dist.py dist`.
- 액션 버전: 각 저장소의 최신 major 태그(`git ls-remote --tags https://github.com/<owner>/<repo>` 로 확인, PROGRESS 에 기록). `pypa/gh-action-pypi-publish` 는 `release/v1`.

### 4.5 release.yml 골격
- `on: push: tags: ["v*.*.*"]` 만. 최상위 `permissions: contents: read`.
- `build`: checkout → setup-uv → `uv sync --locked` → `uv run pytest tests/unit -q -m "not real_samples"` → `uv build --out-dir dist` → twine check --strict → `uv run python scripts/check_dist.py dist --tag "${GITHUB_REF_NAME}"` → `actions/upload-artifact` name `dist`, path `dist/`.
- `publish`: `needs: build`, `environment: { name: pypi, url: https://pypi.org/project/hwp2markdown/ }`, `permissions: { id-token: write }`, `actions/download-artifact` name `dist` → `dist/`, `pypa/gh-action-pypi-publish@release/v1` (password·token 입력 없음).

### 4.6 사용자 수동 절차 (docs/releasing.md 에 그대로, 에이전트는 실행하지 않는다)
| # | 작업 | 위치 | 값 |
|---|------|------|----|
| U1 | PyPI 계정 2FA 확인 후 pending publisher 등록 | pypi.org → Account settings → Publishing → Add a new pending publisher (GitHub) | PyPI Project Name `hwp2markdown` · Owner = 저장소 소유 계정(origin URL 의 첫 경로 조각) · Repository name `hwp2md` · Workflow name `release.yml` · Environment name `pypi` |
| U2 | GitHub environment 생성 | 저장소 Settings → Environments → New environment | 이름 `pypi`. (선택) Deployment branches and tags → 태그 규칙 `v*.*.*` |
| U3 | 릴리스 승인 | S12 게이트에서 orchestrator 질문에 답 | "v0.1.0 게시 승인" |
| U4 | (필요 시) gh 토큰에 workflow scope 추가 | 터미널 `gh auth refresh -h github.com -s workflow` (저장소 소유 계정으로) | push 가 workflow scope 로 거절될 때만 |

### 4.7 클린 복사 명령 (CI 체크아웃 흉내, S1·S5·S9 공통)
```bash
cd /Users/illi/illy-projects/hwp2md && CLEAN="$(mktemp -d)/hwp2md" && mkdir -p "$CLEAN" && \
rsync -a --exclude=.git/ --exclude=.venv/ --exclude=__pycache__/ --exclude=.mypy_cache/ \
  --exclude=.pytest_cache/ --exclude=.ruff_cache/ --exclude=dist/ --exclude=out/ \
  --exclude=/tests/fixtures/ --exclude=/tests/e2e/screenshots/ ./ "$CLEAN/" && \
mkdir -p "$CLEAN/tests/fixtures" && cp tests/fixtures/README.md "$CLEAN/tests/fixtures/" && echo "$CLEAN"
# 이후: cd "$CLEAN" && uv sync --locked && ...  (원본 .venv 를 쓰지 않는다)
```

### 4.8 gh 계정 처리 (gh 2개 계정 로그인)
전역 활성 계정을 바꾸지 않는다. 모든 gh 명령 앞에 아래를 붙인다.
```bash
OWNER=$(git -C /Users/illi/illy-projects/hwp2md remote get-url origin | sed -E 's#.*github.com[/:]([^/]+)/.*#\1#')
export GH_TOKEN=$(gh auth token --user "$OWNER") GH_REPO="$OWNER/hwp2md"
```
`gh auth token --user` 가 실패하면 BLOCKED (사용자에게 `gh auth login` 요청).

## 5. 단계 (Stage)
모든 단계 순차. 커밋 형식 `[T-20261027-pypi-release][sN] <요약>`. 커밋 전 C12(sanitize) 실행.

### Stage 1 — 클린 체크아웃 기준선 측정
- 목적: 샘플 없는 CI 환경에서 무엇이 깨지는지 실측하고 PyPI 이름 가용성을 재확인한다.
- 담당: runner(haiku) · 병렬 가능: 아니오 · 선행: 없음
- 입력: §4.7, 명령 블록
- 쓰기 범위: `.ai/tasks/T-20261027-pypi-release/logs/s1-clean-baseline.log` (코드 수정 없음)
- 실행: `curl -s -o /dev/null -w '%{http_code}' https://pypi.org/pypi/hwp2markdown/json` → §4.7 클린 복사 → 그 안에서 `uv sync --locked && uv run playwright install chromium`, LINT_CMD, TYPECHECK_CMD, TEST_CMD, `uv run pytest tests/e2e -q -rfE -p no:cacheprovider` 각각 exit 코드와 실패·오류 테스트 ID(`tail -60`)를 로그에 기록
- 산출물: 로그 끝에 `NAME_STATUS=<code>`, `LINT/TYPE/UNIT/E2E exit`, `E2E_FAILING_FILES=<파일 목록>`, `E2E_FAILING_IDS=<수>` 요약
- 검증: `grep -E '^(NAME_STATUS|E2E_FAILING_FILES)=' <로그>` → 2줄, NAME_STATUS=404
- 완료 조건: 검증 통과 + PROGRESS 기록 + 커밋 `[..][s1] 클린 체크아웃 기준선` (로그는 gitignore 대상이면 PROGRESS 에 요약만)
- 실패 시: §3 의 S1 조항대로 BLOCKED

### Stage 2 — pyproject 배포 메타데이터
- 목적: 배포 이름·동적 버전·sdist 허용 목록을 §4.2 대로 만든다.
- 담당: implementer(opus). 근거: `pyproject.toml`·`uv.lock` 은 orchestrator 전용이지만 10줄을 넘고 빌드 반복 검증이 필요해 이 두 파일만 쓰기 범위로 갖는 단독 단계로 위임한다(subagent-boundaries "별도 단계"). `[project.scripts]` 절은 수정 금지.
- 병렬 가능: 아니오 · 선행: S1
- 입력: §4.1, §4.2, `pyproject.toml`
- 쓰기 범위: `pyproject.toml`, `uv.lock`
- 산출물: §4.2 상태의 pyproject, `uv lock` 결과
- 검증: C1, C2, C5, C6, `uv run hwp2md --version` → `hwp2md 0.1.0`, `tar -tzf dist/*.tar.gz | sed 's#^[^/]*/##' | sort -u` 가 §4.3 sdist 허용 목록 안 (로그 `logs/s2-build.log`)
- 완료 조건: 검증 통과 + `git diff --stat` 이 두 파일뿐 + 커밋 `[..][s2] 배포 이름 hwp2markdown·동적 버전·sdist 허용 목록`
- 실패 시: hatchling 이 sdist 에 허용 목록 밖 파일을 강제로 넣으면 그 목록을 NEEDS 로 보고하고 BLOCKED (계약 §4.3 변경은 planner)

### Stage 3 — CLI web extra 안내를 배포 이름으로
- 목적: web extra 미설치 안내가 타인 소유 `hwp2md` 대신 `hwp2markdown[web]` 을 가리키게 한다.
- 담당: orchestrator(직접, 1줄 문자열 변경 — 10줄 이하 예외. `cli.py` 는 이 프로젝트의 orchestrator 전용 파일이므로 이 파일만 갖는 단독 단계)
- 병렬 가능: 아니오 · 선행: S2
- 쓰기 범위: `src/hwp2md/cli.py` (49행 문자열만)
- 검증: `uv run python -c "import sys; sys.modules['starlette']=None; sys.modules['uvicorn']=None; from hwp2md.cli import main; raise SystemExit(main(['serve','--no-browser']))"; echo exit=$?` → stderr 에 `pip install 'hwp2markdown[web]'`, `exit=1`. LINT_CMD·TYPECHECK_CMD·TEST_CMD exit 0
- 완료 조건: 검증 통과 + 커밋 `[..][s3] web extra 안내 hwp2markdown[web]`. PROGRESS 에 "test_web_api.py 의 web extra 단언은 S5 에서 갱신, 그 사이 1건 실패 예상" 기록
- 실패 시: `git restore --source=HEAD -- src/hwp2md/cli.py` 후 BLOCKED

### Stage 4 — 배포물 검사 스크립트
- 목적: §4.3 계약대로 sdist·wheel 을 검사하는 스크립트를 만든다.
- 담당: implementer(opus) · 병렬 가능: 아니오 · 선행: S2
- 입력: §4.1, §4.3, S2 의 `dist/`
- 쓰기 범위: `scripts/check_dist.py` (새 파일)
- 검증: `uv build --out-dir dist` 후 C3 → exit 0 · `--tag v9.9.9` → exit 1 + `version-mismatch` · `uv run ruff check scripts && uv run ruff format --check scripts` exit 0 · `uv run mypy --strict scripts/check_dist.py` exit 0 · C4 exit 0
- 완료 조건: 검증 통과 + 커밋 `[..][s4] 배포물 검사 scripts/check_dist.py`
- 실패 시: 새 파일이므로 삭제 후 재시도, 3회 초과 BLOCKED

### Stage 5 — CI 용 실제 샘플 테스트 표시
- 목적: 커밋되지 않은 실제 샘플이 필요한 E2E 를 `real_samples` 로 표시해 CI 에서 deselect 할 수 있게 하고, 샘플 없는 환경의 수집 오류를 없앤다.
- 담당: implementer(opus) · 병렬 가능: 아니오 · 선행: S1, S3
- 입력: S1 로그의 `E2E_FAILING_FILES`, §4.1 마커, `tests/e2e/conftest.py`
- 쓰기 범위 (S1 목록에 있는 것만 실제 수정; 목록 밖 파일이 필요하면 NEEDS 후 BLOCKED): `tests/e2e/conftest.py`, `tests/e2e/test_web_api.py`, `tests/e2e/test_web_ui.py`, `tests/e2e/test_web_v3.py`, `tests/e2e/test_extract_real.py`, `tests/e2e/test_cli_convert.py`, `tests/e2e/test_cli_hwpx.py`, `tests/e2e/test_cli_heading.py`, `tests/e2e/test_cli_image.py`. 파일 수가 5개를 넘는 이유: 각 파일 변경이 마커 줄·`next(..., None)` 같은 기계적 수정이라 한 번에 해야 C8 하나로 검증된다.
- [S1 결과로 보완 2026-10-27, orchestrator] 클린 복사본에서 단위 테스트도 수집 오류(StopIteration): `tests/unit/test_memory.py`, `tests/unit/test_web_app.py`. 이 두 파일과 새 `tests/conftest.py`(마커 등록 위치)를 쓰기 범위에 추가한다. 마커 등록은 e2e conftest 대신 `tests/conftest.py` 한 곳에서 한다. 검증에 C8 단위판 추가: 클린 복사본에서 `uv run pytest tests/unit -q -m "not real_samples"` 실패 0·오류 0, 로컬 `uv run pytest tests/unit -q` 실패 0. §4.4·§4.5 의 unit 명령에 `-m "not real_samples"` 추가.
- 규칙: 마커 등록은 (위 보완대로 `tests/conftest.py`) `pytest_configure` 에서 `config.addinivalue_line("markers", "real_samples: needs uncommitted real samples in tests/fixtures")` (pyproject 수정 금지). 실제 샘플을 쓰는 테스트에만 마커(모듈 전체가 쓰면 `pytestmark`). `skipif`·`pytest.skip` 추가 금지. 기존 단언 약화 금지. `test_web_api.py` 179행은 `"hwp2markdown[web]" in result.stderr` 로 바꾼다.
- 검증: C7 (로컬, 샘플 있음) 실패 0 · C8 (클린 복사본) 실패 0·오류 0 · `uv run pytest tests/e2e -q -m real_samples --collect-only -q | tail -1` 의 수가 S1 `E2E_FAILING_IDS` 이상 · LINT_CMD exit 0 (로그 `logs/s5-markers.log`)
- 완료 조건: 검증 통과 + 커밋 `[..][s5] real_samples 마커와 CI 수집 오류 제거`
- 실패 시: `git restore` 로 범위 파일 되돌림 후 재시도, 같은 오류 2회 BLOCKED

### Stage 6 — CI 워크플로우
- 목적: push·PR 에서 다섯 검사를 도는 `ci.yml` 을 만든다.
- 담당: implementer(opus). `.github/**` 는 orchestrator 전용이므로 이 파일만 쓰기 범위로 갖는 단독 단계
- 병렬 가능: 아니오 · 선행: S4, S5
- 입력: §4.1, §4.4, 명령 블록
- 쓰기 범위: `.github/workflows/ci.yml` (새 파일)
- 검증: C10 (ci.yml) exit 0 · `grep -c -- '-m "not real_samples"' .github/workflows/ci.yml` → 1 · 각 job id 가 §4.1 과 같음 (`grep -E '^  (lint|typecheck|unit|e2e|dist):' | wc -l` → 5)
- 완료 조건: 검증 통과 + 사용한 액션 태그를 PROGRESS 에 기록 + 커밋 `[..][s6] CI 워크플로우`
- 실패 시: actionlint 지적을 고쳐 재시도 3회, 초과 BLOCKED

### Stage 7 — 릴리스 워크플로우
- 목적: 태그 push 로 build → Trusted Publishing 게시하는 `release.yml` 을 만든다.
- 담당: implementer(opus). `.github/**` 단독 단계
- 병렬 가능: 아니오 · 선행: S6
- 입력: §4.1, §4.5, S6 의 액션 태그
- 쓰기 범위: `.github/workflows/release.yml` (새 파일)
- 검증: C10 (release.yml) exit 0 · `grep -cE 'id-token: write|name: pypi|gh-action-pypi-publish@release/v1|check_dist.py dist --tag' .github/workflows/release.yml` → 4 · `grep -ciE 'password|api[-_]token|secrets\.' .github/workflows/release.yml` → 0 · 로컬 재현: `uv run python scripts/check_dist.py dist --tag v0.1.0` exit 0
- 완료 조건: 검증 통과 + 커밋 `[..][s7] 릴리스 워크플로우 (Trusted Publishing)`
- 실패 시: 재시도 3회, 초과 BLOCKED

### Stage 8 — 설치·릴리스 문서
- 목적: README 와 문서를 배포 후 상태로 고치고, 사용자 수동 절차를 문서화한다.
- 담당: implementer(opus) · 병렬 가능: 아니오 · 선행: S7
- 입력: §4.1, §4.6, README 28~46행·277행·294행, `docs/feature-reference.md` 539행, `docs/decisions.md` 끝
- 쓰기 범위: `README.md`, `docs/releasing.md`(새 파일), `docs/decisions.md`, `docs/feature-reference.md`, `src/hwp2md/web/__init__.py`(docstring 1줄)
- 내용: README 설치 = `pip install 'hwp2markdown[web]'`(또는 `uv tool install 'hwp2markdown[web]'`), 명령은 `hwp2md`, "PyPI 의 `hwp2md` 는 다른 프로젝트" 한 줄, 소스 설치는 개발용으로 유지. 한계의 "PyPI 에 배포하지 않았다. CI 도 아직 없다" 줄 삭제. 로드맵 `[x] PyPI 배포(hwp2markdown) + GitHub Actions CI`. 문서 목록에 `docs/releasing.md`. `docs/releasing.md` = §4.6 U1~U4 표 + 릴리스 절차(`__version__` 올림 → main CI green → `git tag -a vX.Y.Z` → `git push origin vX.Y.Z` → Release 실행 확인) + 실패 대응(version-mismatch 면 태그 삭제 후 재태그, PyPI 는 같은 버전 재업로드 불가 → 버전 올림). decisions 에 2026-10-27 항목 2개(배포 이름 hwp2markdown, CI 실제 샘플 deselect). 타인 계정명·회사명 금지.
- 검증: `grep -rn "hwp2md\[web\]" README.md docs src | grep -v hwp2markdown` → 0줄 · `grep -c "hwp2markdown" README.md` ≥ 2 · `grep -c "PyPI 에 배포하지 않았다" README.md` → 0 · C2(README 렌더) PASSED · C12 exit 0 · TEST_CMD exit 0
- 완료 조건: 검증 통과 + 커밋 `[..][s8] 설치·릴리스 문서`
- 실패 시: 재시도 3회, 초과 BLOCKED

### Stage 9 — E2E 테스트 작성·실행 (필수)
- 목적: 배포물 스모크(성공)와 배포물 검사 실패 경로를 E2E 로 고정한다.
- 담당: test-writer(sonnet) → runner(haiku) · 병렬 가능: 아니오 · 선행: S8
- 쓰기 범위: `tests/e2e/test_dist_package.py` (새 파일)
- 케이스 (모듈 scope fixture 로 `uv build --out-dir <tmp>` 1회, `uv` 없으면 `pytest.fail`):
  1. 성공 — 새 venv(`uv venv`, 현재 인터프리터 버전)에 `<wheel>[web]` 설치 → `<venv>/bin/hwp2md --version` 이 `hwp2md 0.1.0` (`hwp2md.__version__` 과 비교) → `<venv>/bin/hwp2md serve --no-browser --port <빈 포트>` 30초 안 `/api/health` 200 이고 JSON `version` 일치 → 종료. 같은 빌드에 `check_dist.py` exit 0.
  2. 실패 — 금지 파일: 실제 wheel 복사 + `hwp2markdown-0.1.0/.ai/STATE.md`·`hwp2markdown-0.1.0/CLAUDE.md` 를 넣은 가짜 sdist → exit 1, 출력에 두 경로와 `forbidden-path`.
  3. 실패 — 태그 불일치: 실제 빌드에 `--tag v9.9.9` → exit 1, `version-mismatch`.
  4. 실패 — 패턴 적중: README.md 첫 줄을 `re.escape` 한 패턴 파일 → exit 1, `pattern-hit`, 출력에 그 문자열 없음.
- 검증: C9 · C7 · C8 (새 파일 포함) · LINT_CMD exit 0 (로그 `logs/e2e.log`)
- 완료 조건: 검증 통과 + 커밋 `[..][s9] 배포물 E2E`
- 실패 시: test-writer 2회 실패 → opus 재호출, 제품 결함이면 해당 단계 범위로 implementer 재호출(RETRY 기록)

### Stage 10 — GitHub 실제 CI 확인
- 목적: 브랜치 push 로 실제 CI 다섯 job 이 통과하는지 본다.
- 담당: orchestrator(`git push -u origin ai/T-20261027-pypi-release` — 브랜치 push 만, 태그 없음) → runner(haiku, 대기·로그)
- 병렬 가능: 아니오 · 선행: S9
- 쓰기 범위: `.ai/tasks/T-20261027-pypi-release/logs/s10-ci.log`
- 실행: §4.8 → `gh run list --branch ai/T-20261027-pypi-release --workflow ci.yml -L 1 --json databaseId,headSha` (headSha 가 로컬 HEAD 와 같은지) → `gh run watch <id> --exit-status` → C11 명령. 실패 job 은 `gh run view <id> --log-failed | tail -80`. 추가로 읽기 전용 확인 `gh api user --jq .plan.name` 와 `gh api repos/$GH_REPO/environments --jq '.total_count'` 결과를 로그에 남긴다(§7 Q2 판단용, 설정 변경 없음)
- 검증: C11
- 완료 조건: C11 통과 + PROGRESS 기록 + 커밋 `[..][s10] CI 실행 확인`
- 실패 시: 실패 job 이 속한 단계(S4~S9)를 RETRY, CI 재실행 3회 초과 BLOCKED. push 가 workflow scope 로 거절되면 BLOCKED(U4)

### Stage 11 — 리뷰·결과 기록
- 담당: reviewer(sonnet) → scribe(haiku) · 선행: S10
- 입력: `git diff main...HEAD`, §1 건드리면 안 되는 파일, C1~C13 로그
- 리뷰 항목: `[project.scripts]`·`__init__.py`·`tests/unit/**` 무변경, 마커가 실제 샘플 테스트에만 붙음, release.yml 에 토큰·secret 없음, 배포물 목록이 §4.3 허용 목록 안, 문서에 타인 계정명·회사명 없음
- 산출물: `.ai/tasks/T-20261027-pypi-release/RESULT.md` (C1~C13 PASS/FAIL, R1~R3 "S12 대기")
- 검증: RESULT.md 에 C1~C13 13행 · reviewer `VERDICT: PASS`
- 완료 조건: 커밋 `[..][s11] 리뷰·RESULT`

### Stage 12 — 릴리스 게이트 (사용자 승인 필수)
- 목적: 사용자가 승인하면 v0.1.0 을 PyPI 에 게시하고 설치를 확인한다.
- 담당: orchestrator(병합·태그·push) → runner(haiku, 대기·확인) → scribe(haiku, RESULT 갱신)
- 선행: S11 + 사용자 확인 3가지: U1 등록 완료, U2 생성 완료(또는 §7 Q2 대체안), "v0.1.0 게시 승인". 하나라도 없으면 실행하지 않고 STATE 다음 행동을 "릴리스 게이트 대기"로 두고 멈춘다(브랜치는 main 에 병합하지 않는다 — README 가 배포 후 상태라서).
- 쓰기 범위: `.ai/tasks/T-20261027-pypi-release/RESULT.md`, `.ai/tasks/T-20261027-pypi-release/logs/s12-release.log`
- 실행: `git checkout main && git merge --no-ff ai/T-20261027-pypi-release && git push origin main` → main CI success 확인(§4.8) → `git tag -a v0.1.0 -m "v0.1.0" && git push origin v0.1.0` → Release run watch(R1) → 2분 대기 후 R2(실패 시 60초 간격 3회) → R3
- 검증: R1, R2, R3
- 완료 조건: R1~R3 PASS + RESULT 갱신 + 커밋 `[..][s12] v0.1.0 PyPI 게시 확인`
- 실패 시: `build` 실패 → 태그 삭제(`git push origin :refs/tags/v0.1.0`, 사용자에게 알림) 후 원인 단계 RETRY. `publish` 가 OIDC/publisher 오류 → BLOCKED(U1·U2 재확인 요청). 게시 후 결함 → 같은 버전 재게시 불가, 0.1.1 은 새 태스크.

## 6. 병렬 실행 맵
```
S1 → S2 → S3 → S4 → S5 → S6 → S7 → S8 → S9(E2E) → S10(실제 CI) → S11(리뷰) → [사용자 승인] → S12(릴리스)
```
병렬 없음(전부 순차). 이유: S2·S3·S6·S7 이 orchestrator 전용 파일 단독 단계라 병렬 금지, S4·S5 는 각각 S2·S3 결과에 의존, 단계마다 10분 안쪽이라 worktree 격리 비용이 더 크다. S10~S12 가 E2E 뒤에 오는 이유: 실제 CI 는 S9 의 새 E2E 까지 돌려야 의미가 있고, 되돌릴 수 없는 PyPI 게시는 리뷰 PASS 뒤에만 한다.

## 7. 사용자에게 확인받을 것 (플랜 승인 시 한 번에)
- [ ] Q1. 첫 릴리스 버전을 `0.1.0` 으로 할까?
  - 기본값: `0.1.0` (현재 `__version__` 그대로, 파일 변경 없음)
- [ ] Q2. 비공개 저장소에서 GitHub environment `pypi` 를 못 쓰는 플랜이면(S10 에서 확인) 어떻게 할까?
  - 기본값: release.yml 에서 `environment:` 블록을 빼고(orchestrator, 3줄 이하), U1 pending publisher 의 Environment 칸을 비워 등록하도록 안내한다. 쓸 수 있으면 `pypi` 그대로.
- [ ] Q3. TestPyPI 에 먼저 리허설 게시할까?
  - 기본값: 하지 않는다 (pending publisher 를 한 번 더 등록해야 함). 대신 CI `dist` job 과 S9 E2E 로 빌드·검사 경로를 확인한다.
- [ ] Q4. README 그림(`docs/images/*`, 상대 경로)이 PyPI 페이지에서 깨진다. 처리할까?
  - 기본값: 그대로 둔다 (저장소가 비공개라 절대 URL 도 열리지 않음). 리스크에 기록.
- [ ] Q5. 고유명사 금지 패턴을 CI 에서도 검사할까? (패턴을 GitHub secret 으로 넣고 `--patterns` 로 전달)
  - 기본값: 하지 않는다. CI·Release 는 구조 검사만, 고유명사 검사는 로컬 C4(커밋·S12 전 필수)로 한다.
- 사용자 수동 작업(승인과 별개, S12 전까지): U1 PyPI pending publisher 등록, U2 GitHub environment `pypi` 생성, U3 릴리스 승인, U4(필요 시) gh workflow scope 추가 — 절차는 S8 이 쓰는 `docs/releasing.md`.

## 8. 리스크
| 리스크 | 가능성 | 대응 |
|--------|--------|------|
| 실제 샘플 없는 CI 에서 E2E 수집 오류(`next()` StopIteration) | 높음(코드로 확인) | S1 실측 → S5 마커·`next(..., None)` |
| hatchling sdist 가 허용 목록 밖 파일(.gitignore 등)을 넣음 | 중간 | `.gitignore` 는 허용, 그 밖은 S2 BLOCKED |
| 저장소 안 무시 경로(`dist/`)에 풀어 sanitize-check 를 돌리면 무시 파일이라 건너뜀 → 거짓 통과 | 높음 | C4 는 `mktemp -d`(저장소 밖)에서만 |
| twine 구버전이 Metadata 2.4(license-files) 를 거부 | 중간 | `twine>=6.1` 고정 |
| push 시 OAuth 토큰에 workflow scope 없음 | 중간 | BLOCKED → U4 |
| gh 활성 계정이 저장소 소유자가 아님 | 높음 | §4.8 `gh auth token --user`, 전역 전환 안 함 |
| 비공개 저장소 무료 플랜에서 environment 불가·Actions 분 한도 | 중간 | Q2 기본값, `concurrency` 취소, e2e timeout 30분 |
| 브라우저 모드 E2E 가 jsDelivr 지연으로 CI 에서 시간 초과 | 중간 | 실패 로그 확인 후 S10 재실행 1회, 반복되면 BLOCKED(테스트 약화 금지) |
| PyPI 게시는 되돌릴 수 없음 | 확정 | S12 사용자 게이트, 리뷰 PASS 후에만 |
| 동봉 GSAP 은 OSI 라이선스가 아님(기존 `vendor/gsap/LICENSE.md` 안내) | 낮음 | 이번 범위 밖, RESULT 에 공개 배포 사실 기록 |

## 9. 예상 비용
- 예상 단계 수: 12 · 서브에이전트 호출: 약 14회 (implementer opus 6 — S2·S4·S5·S6·S7·S8 / test-writer sonnet 1 · reviewer sonnet 1 / runner haiku 4 — S1·S9·S10·S12 / scribe haiku 2) + orchestrator 직접 S3·S10 push·S12 병합·태그
- 모델 비율: opus 약 45%, sonnet 15%, haiku 40% (호출 기준)
- 외부 비용: GitHub Actions 비공개 저장소 분 — push 1회당 약 15~20 job-분(e2e 가 대부분), 이번 태스크 예상 3~5회 실행
