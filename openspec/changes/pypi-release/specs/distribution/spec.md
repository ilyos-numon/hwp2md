## ADDED Requirements

### Requirement: 배포 이름은 hwp2markdown, 명령과 import 이름은 hwp2md 다
패키지 메타데이터의 배포 이름은 `hwp2markdown` 이어야 한다(SHALL). 설치하면 콘솔 명령 `hwp2md`(`hwp2md.cli:main`)와 import 패키지 `hwp2md` 가 생긴다. 다른 import 패키지나 콘솔 명령은 생기지 않는다.

#### Scenario: 깨끗한 가상환경에 wheel 설치
- **WHEN** 새 가상환경에 빌드한 `hwp2markdown-<버전>-py3-none-any.whl[web]` 을 설치하고 `hwp2md --version` 을 실행한다
- **THEN** 종료 코드 0, 표준 출력이 `hwp2md <버전>` 이고, 같은 환경에서 `hwp2md serve --no-browser --port <빈 포트>` 의 `GET /api/health` 가 30초 안에 200 이다

### Requirement: 버전은 한 곳에서 정한다
배포 버전은 `src/hwp2md/__init__.py` 의 `__version__` 문자열에서만 읽어야 한다(SHALL). `pyproject.toml` 은 `version` 을 `dynamic` 으로 두고 값을 직접 갖지 않는다. wheel METADATA 의 `Version`, `hwp2md --version` 출력, `/api/health` 의 `version` 이 모두 같다.

#### Scenario: 버전 일치
- **WHEN** wheel 을 빌드한다
- **THEN** wheel METADATA `Version` 이 `hwp2md.__version__` 과 같다

### Requirement: 배포물은 허용 목록의 파일만 담는다
sdist 는 `src/hwp2md/**`, `README.md`, `LICENSE`, `NOTICE`, `pyproject.toml`, `PKG-INFO`(빌드 도구가 추가하는 `.gitignore` 는 허용)만 담아야 한다(SHALL). wheel 은 `hwp2md/**` 와 `hwp2markdown-<버전>.dist-info/**` 만 담고, dist-info 의 `licenses/` 에 `LICENSE`·`NOTICE` 가 있다. 어느 배포물에도 `.ai`·`design`·`openspec`·`tests`·`docs`·`.impeccable`·`.github`·`logs`·`out`·`screenshots` 경로 조각, `CLAUDE.md`·`uv.lock`·`.env*` 파일, `.hwp`·`.hwpx`·`.hwpml`·`.pyc` 확장자가 없다.

#### Scenario: 정상 빌드
- **WHEN** `uv build` 결과에 `scripts/check_dist.py` 를 실행한다
- **THEN** 종료 코드 0 과 `check_dist: OK` 줄이 나온다

#### Scenario: 금지 파일이 섞인 sdist
- **WHEN** `hwp2markdown-0.1.0/.ai/STATE.md` 와 `hwp2markdown-0.1.0/CLAUDE.md` 를 담은 sdist 를 검사한다
- **THEN** 종료 코드 1 이고 두 경로가 각각 `forbidden-path` 사유로 출력된다

### Requirement: 배포물 검사는 태그와 버전, 금지 패턴을 확인한다
`scripts/check_dist.py` 는 `--tag vX.Y.Z` 가 주어지면 태그에서 `v` 를 뗀 값이 wheel METADATA `Version` 과 같은지 확인하고, `--patterns FILE` 이 주어지면 배포물 안 텍스트 파일 각 줄에 파일의 정규식(대소문자 무시)을 적용해야 한다(SHALL). 불일치·적중은 종료 코드 1 이다. 적중 보고에는 파일 경로와 줄 번호만 쓰고 적중한 문자열은 쓰지 않는다.

#### Scenario: 태그 불일치
- **WHEN** 버전 0.1.0 배포물을 `--tag v9.9.9` 로 검사한다
- **THEN** 종료 코드 1, 사유 `version-mismatch`

#### Scenario: 금지 패턴 적중
- **WHEN** README 에 패턴 파일의 문자열이 있는 배포물을 `--patterns` 로 검사한다
- **THEN** 종료 코드 1, 사유 `pattern-hit`, 출력에 적중 문자열이 없다

### Requirement: CI 는 push 와 PR 마다 검사를 돌린다
`.github/workflows/ci.yml` 은 모든 브랜치 push 와 pull_request 에서 job `lint`, `typecheck`, `unit`, `e2e`, `dist` 를 돌려야 한다(SHALL). `e2e` 는 Playwright chromium 을 설치하고 `-m "not real_samples"` 로 커밋되지 않은 실제 샘플이 필요한 케이스만 제외한다. `dist` 는 빌드, `twine check --strict`, `scripts/check_dist.py` 를 돌린다.

#### Scenario: 브랜치 push
- **WHEN** 작업 브랜치를 push 한다
- **THEN** CI 실행 하나가 생기고 다섯 job 이 모두 success 로 끝난다

### Requirement: 태그 push 가 Trusted Publishing 으로 PyPI 에 게시한다
`.github/workflows/release.yml` 은 `v*.*.*` 태그 push 에서만 시작해야 한다(SHALL). job `build` 는 단위 테스트, 빌드, `twine check --strict`, `check_dist.py --tag <태그>` 를 통과해야 산출물 `dist` 를 올린다. job `publish` 는 `build` 뒤에 GitHub environment `pypi` 에서 `id-token: write` 권한으로 `pypa/gh-action-pypi-publish` 를 실행하며, 저장소 secret 이나 API 토큰을 쓰지 않는다.

#### Scenario: 버전과 다른 태그
- **WHEN** `__version__` 이 0.1.0 인 커밋에 `v0.1.1` 태그를 push 한다
- **THEN** `build` 가 `version-mismatch` 로 실패하고 `publish` 는 실행되지 않는다
