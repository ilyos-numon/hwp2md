# PLAN — T-20261027-public-launch 공개 출시 (브라우저 체험·공개 저장소·발견성·0.1.1)

> 작성: planner(opus) · 2026-10-27 17:40 · 프로젝트: hwp2md
> 상태: DRAFT → APPROVED → DONE  (현재: DONE)
> 보완: planner(opus) · 2026-10-27 19:10 — 영어 지원 S12~S16 삽입, 옛 S12~S14 → S17~S20. S1~S11(DONE) 내용과 §4.1~§4.7 은 그대로, 새 계약은 §4.8. 이 보완분의 §7(Q9~Q12)도 기본값으로 자동 진행.
> 이 플랜은 sonnet 등급 모델이 추가 질문 없이 그대로 실행할 수 있을 만큼 구체적이어야 한다.
> 사용자 지시 "알아서 해, 질문 많이 하지 마": §7 은 전부 기본값으로 진행한다. 사용자 확인은 S10(이력 재작성 + 공개 전환) 게이트 한 번뿐이다.

## 0. 한 줄 목표
사용자(누구나)는 설치 없이 `https://ilyos-numon.github.io/hwp2md/` 에서 HWP·HWPX 를 브라우저 안에서 Markdown 으로 바꿔 볼 수 있고, 공개 저장소·PyPI(0.1.1) 페이지에서 링크·배지·분류로 hwp2md 를 찾을 수 있다.

### 0.1 OpenSpec 연동
- change: `openspec/changes/public-launch/` · 검증: `source ~/.nvm/nvm.sh >/dev/null 2>&1 && openspec validate public-launch`
- tasks.md 체크는 orchestrator 가 단계 DONE 커밋에서 한다. tasks.md 의 모든 `- [ ] N.M` 이 아래 표에 정확히 한 행.
- capability: `static-site`(신규), `public-repository`(신규), `web-preview`(ADDED — 정적 meta + [보완] 영어 지원), `distribution`(ADDED)
- [보완] tasks.md 의 옛 5.1~5.3(미체크)은 6.2~6.4 로 옮기고, 새 5.1~5.5(영어 지원)·6.1(재배포)을 넣었다. [x] 항목은 그대로.

| tasks.md 항목 | 내용(요약) | Stage |
|---------------|-----------|-------|
| 1.1 | `.gitignore` dist-pages, CLAUDE.md 내부 메모 절 삭제, gh 저장소 설명·홈페이지·토픽 | S1 |
| 2.1 | app.js·pyodide-runner.js 정적 사이트 meta 설정 | S2 |
| 2.2 | scripts/build_pages.py + 단위 테스트 | S3 |
| 2.3 | 정적 사이트 E2E 작성·실행 (로컬 하위 경로) | S4 |
| 3.1 | pyproject urls·keywords·classifiers·description | S5 |
| 3.2 | README·CHANGELOG·버전 0.1.1·releasing·decisions | S6 |
| 3.3 | pages.yml + 이슈 템플릿 | S7 |
| 3.4 | docs/launch 홍보 초안 2개 | S8 |
| 4.1 | 게이트 전 전체 검증 + 브랜치 CI | S9 |
| 4.2 | [게이트] 백업 → 병합 → filter-repo → 검사 → force-push → 공개 | S10 |
| 4.3 | Pages 활성화·배포 확인 | S11 |
| 5.1 | 기존 브라우저 E2E locale ko-KR 고정 | S12 |
| 5.2 | i18n.js 코어 + 변환 화면 영어 | S13 |
| 5.3 | 소개 페이지 영어 | S14 |
| 5.4 | i18n E2E 작성·실행 | S15 |
| 5.5 | README.en·CHANGELOG·feature-reference·decisions | S16 |
| 6.1 | 재검증 + main push + Pages 재배포 확인 | S17 |
| 6.2 | v0.1.1 태그 push(사용자)·PyPI 확인 | S18 |
| 6.3 | 최종 E2E (로컬 전체 + 실제 Pages) | S19 |
| 6.4 | 리뷰·RESULT | S20 |

## 1. 범위
### 포함 (IN)
- 정적 사이트 모드: `src/hwp2md/web/static/js/app.js`, `src/hwp2md/web/static/pyodide-runner.js` 에 meta 기반 설정 (§4.2). meta 가 없으면 기존 동작 그대로.
- 정적 빌드: `scripts/build_pages.py` → `dist-pages/` (§4.1, §4.3), 단위 테스트 `tests/unit/test_build_pages.py`
- E2E: `tests/e2e/test_pages_site.py` (로컬 하위 경로 `/hwp2md/` + 실제 Pages URL 선택 실행)
- Pages 배포: `.github/workflows/pages.yml` (main push·수동, 비공개면 건너뜀)
- 발견성: `pyproject.toml` `[project.urls]`·keywords·classifiers·description, `README.md` 배지·체험 링크·30초 데모·영문 요약·절대 URL, `CHANGELOG.md`, `.github/ISSUE_TEMPLATE/bug_report.yml`·`config.yml`, gh 저장소 description·homepage·topics
- 버전 `0.1.1` (`src/hwp2md/__init__.py`) 과 PyPI 게시 (태그 push)
- 공개 준비: CLAUDE.md 내부 메모 절 삭제, bundle 백업, `git filter-repo` 이력 재작성 (§4.5), force-push, 원격 이전 브랜치 삭제, 공개 전환 — **S10 사용자 승인 게이트 뒤에서만**
- 문서: `docs/releasing.md` (Pages 절), `docs/decisions.md` (정적 사이트·공개 결정), `docs/launch/community-post.md`, `docs/launch/sns-post.md`
- [보완] 영어 지원 (S12~S16, §4.8): 변환 화면(`index.html`·`app.js`·`theme.js`)과 소개 페이지(`about.html`) 의 사용자 노출 문구 ko/en, 새 `static/js/i18n.js`·`i18n-about.js`, 헤더 KO/EN 버튼, `base.css` 의 `.lang-toggle` 규칙, 기존 브라우저 E2E 의 locale 고정, 새 `tests/e2e/test_i18n.py`, `README.en.md`, CHANGELOG·feature-reference §9.9·decisions. serve·정적 사이트 둘 다.

### 제외 (OUT) — 절대 건드리지 않는다
- Docker 이미지·Docker 단계 전부
- 텔레메트리·사용 추적·분석 스크립트(외부 analytics 포함) — "파일이 서버로 전송되지 않습니다" 약속과 원칙(개인정보 최소)에 어긋난다
- 외부 커뮤니티·SNS 실제 게시 (초안 파일만)
- 저장소 이름 변경·저장소 삭제 후 재생성 (Trusted Publisher 가 묶여 있음)
- `hwp2md serve` 동작·서버 API(`src/hwp2md/web/app.py`, `server.py`) 변경, 서버 모드 공개 호스팅
- 변환 엔진(`src/hwp2md/**` 중 `web/static` 2개 JS 와 `__init__.py` 버전 줄 외), `src/hwp2md/cli.py`
- 원본 HTML(`index.html`, `about.html`)·CSS·`fonts.css` 수정 — 경로 치환은 빌드 결과물에서만 ([보완] 예외: S13·S14 의 i18n 표기·스크립트 태그·`.lang-toggle` 버튼, `base.css` 끝 `.lang-toggle` 규칙 추가만. 경로 치환은 여전히 빌드에서만)
- [보완] CLI 출력 번역, HTTP API 응답·엔진의 `skipped[].label` 번역, 한국어·영어 외 언어, PyPI long description 영어화(README.md 그대로), 소개 페이지 문구 내용 개편(번역만), 브라우저 언어 외 지역 감지(IP 등)
- 커스텀 도메인, Pretendard 서브셋, 소개 페이지 문구 개편
- `tests/fixtures/**` 실제 샘플, 테스트 코드 안 샘플 파일명 정리 (§7 Q3)

### 건드리면 안 되는 파일/디렉토리
- `src/hwp2md/web/app.py`, `src/hwp2md/web/server.py`, `src/hwp2md/cli.py`, `src/hwp2md/web/static/*.html`, `src/hwp2md/web/static/css/**`, `src/hwp2md/web/static/vendor/**` ([보완] `*.html`·`css/base.css` 는 S13·S14 쓰기 범위에 적힌 만큼만 예외. `scripts/build_pages.py`·`pyodide-runner.js` 는 S12 이후 변경 금지)
- `.github/workflows/ci.yml`, `.github/workflows/release.yml`, `scripts/check_dist.py`, `uv.lock`(S5 의 `uv lock --check` 가 실패할 때만 orchestrator 가 `uv lock`)
- orchestrator 전용(서브에이전트 쓰기 금지): `pyproject.toml`, `.gitignore`, `CLAUDE.md`, `.ai/STATE.md`, `.ai/tasks/*/PLAN.md`, `.github/**`, `uv.lock` — S5·S7 은 그 파일만 갖는 별도 순차 단계
- `doc/my_info/` (워크스페이스 원본, 읽기 전용)

## 2. 성공 기준 (전부 만족해야 DONE)
모든 명령은 `cd /Users/illi/illy-projects/hwp2md && ` 로 시작, uv 는 `env -u VIRTUAL_ENV uv ...`. gh 는 `GH_TOKEN=$(gh auth token --user ilyos-numon) gh ...`.

| # | 기준 | 검증 명령 | 기대 결과 |
|---|------|-----------|-----------|
| C1 | 정적 빌드 생성 | `rm -rf dist-pages && uv run python scripts/build_pages.py --out dist-pages; echo exit=$?; ls -A dist-pages` | `exit=0`, `.nojekyll convert.html index.html pkg static` |
| C2 | 빌드 결과에 루트 절대 경로 없음 | `grep -rnE '"/static/\|"/api/\|href="/"\|href="/about\|url\("/' dist-pages --include=*.html --include=*.css \| wc -l` | `0` |
| C3 | 단위 테스트(빌드 포함) | `uv run pytest tests/unit -q` | failed 0 |
| C4 | lint (CI 동일, 캐시 없음) | `uv run ruff check --no-cache src tests scripts && uv run ruff format --no-cache --check src tests scripts` | exit 0 |
| C5 | 타입 검사 | `uv run mypy src && uv run mypy --strict scripts/build_pages.py` | `Success` 2회 |
| C6 | 로컬 E2E 전체 (serve 회귀 포함) | `ILLY_SHOT_DIR=.ai/tasks/T-20261027-public-launch/screenshots uv run pytest tests/e2e -q` | failed 0, `test_pages_site.py` 의 로컬 케이스 3개 passed (live 1개 skipped 허용) |
| C7 | 정적 사이트 스크린샷 | `.ai/tasks/T-20261027-public-launch/screenshots/pages-landing.png`, `pages-convert-done.png`, `pages-cdn-blocked.png` | landing: 소개 페이지 hero 와 "변환 도구 열기" 버튼, 깨진 글꼴·빈 화면 아님 / convert-done: 모드 스위치 없음, 상태 "브라우저 모드: 파일이 서버로 전송되지 않습니다", 미리보기에 합성 문서 제목 / cdn-blocked: 상태 "브라우저 모드를 불러오지 못했습니다: …" 와 오류 띠 |
| C8 | 패키지 메타데이터 | `rm -rf dist && uv build --out-dir dist && unzip -p dist/*.whl '*.dist-info/METADATA' \| grep -cE '^(Project-URL\|Classifier: Natural Language :: Korean\|Classifier: Topic :: Text Processing :: Markup :: Markdown\|Version: 0.1.1)'` | `7` (Project-URL 4 + 분류자 2 + Version 1) |
| C9 | 배포물 검사 | `uvx --from 'twine>=6.1' twine check --strict dist/* && uv run python scripts/check_dist.py dist --tag v0.1.1` | `PASSED` 2줄, `check_dist: OK` |
| C10 | README 상대 링크 0 | §4.6 의 README 링크 검사 스크립트 | `relative=0` |
| C11 | 워크플로우 문법 | `uvx --from actionlint-py actionlint .github/workflows/pages.yml .github/workflows/ci.yml .github/workflows/release.yml` | exit 0, 출력 없음 |
| C12 | HEAD 익명화 | `cd /Users/illi/illy-projects && scripts/sanitize-check.sh hwp2md; echo exit=$?` (파이프로 가리지 않는다) | `exit=0` |
| C13 | 전체 이력 익명화·금지 경로 (S10 뒤) | §4.5 "검사 V1~V3" | V1 `0`, V2 `0`, V3 `0` |
| C14 | v0.1.0 내용 동일 (S10 뒤) | §4.5 "검사 V4" | 다섯 줄 모두 `same` |
| C15 | 공개·원격 정리 (S10 뒤) | `gh repo view ilyos-numon/hwp2md --json visibility -q .visibility; git ls-remote --heads origin \| wc -l; git ls-remote origin refs/heads/main \| cut -f1; git rev-parse main` | `PUBLIC`, `1`, 마지막 두 SHA 같음 |
| C16 | Pages 실제 배포 | `curl -s -o /dev/null -w '%{http_code}\n' https://ilyos-numon.github.io/hwp2md/ https://ilyos-numon.github.io/hwp2md/convert.html https://ilyos-numon.github.io/hwp2md/pkg/hwp2md.zip` | `200` 3줄 |
| C17 | 실제 Pages E2E | `HWP2MD_PAGES_URL=https://ilyos-numon.github.io/hwp2md/ ILLY_SHOT_DIR=.ai/tasks/T-20261027-public-launch/screenshots uv run pytest tests/e2e/test_pages_site.py -q -k live` | 1 passed, `pages-live-done.png` 에 변환 결과 |
| C18 | PyPI 0.1.1 | `curl -s https://pypi.org/pypi/hwp2markdown/json \| python3 -c 'import json,sys;d=json.load(sys.stdin)["info"];print(d["version"],len(d["project_urls"] or {}))'` | `0.1.1 4` |
| C19 | 새 환경 설치 | `D=$(mktemp -d) && uv venv -q $D/v && uv pip install -q -p $D/v/bin/python 'hwp2markdown[web]==0.1.1' && $D/v/bin/hwp2md --version` | `hwp2md 0.1.1` |
| C20 | 저장소 메타 | `gh repo view ilyos-numon/hwp2md --json description,homepageUrl,repositoryTopics -q '.homepageUrl, (.repositoryTopics\|length)'` | `https://ilyos-numon.github.io/hwp2md/`, 8 이상 |
| C21 | CI·Pages·Release green | `gh run list -R ilyos-numon/hwp2md --branch main --limit 6 --json workflowName,conclusion` / `gh run list -R ilyos-numon/hwp2md --workflow release.yml --limit 1 --json conclusion,headBranch` | main 최신 `CI`·`Pages` 둘 다 `success`, Release `success` / headBranch `v0.1.1` |
| C22 | OpenSpec | `source ~/.nvm/nvm.sh >/dev/null 2>&1 && openspec validate public-launch` | `Change 'public-launch' is valid` |
| C23 | 홍보 초안 | `ls docs/launch/` 와 `wc -m docs/launch/sns-post.md` | `community-post.md sns-post.md`, sns 본문 500자 이하 |
| C24 | [보완] i18n JS 문법 | `for f in i18n.js i18n-about.js app.js theme.js landing.js; do node --check src/hwp2md/web/static/js/$f \|\| echo FAIL $f; done; echo done` | `done` 한 줄만 (FAIL 없음) |
| C25 | [보완] i18n E2E | `ILLY_SHOT_DIR=.ai/tasks/T-20261027-public-launch/screenshots uv run pytest tests/e2e/test_i18n.py -q` | passed ≥ 8, failed 0, skipped 0 |
| C26 | [보완] 기존 E2E 단언 불변 | `git diff $(cat .ai/tasks/T-20261027-public-launch/.base-s12) -U0 -- tests/e2e/test_web_ui.py tests/e2e/test_web_extract.py tests/e2e/test_web_v3.py tests/e2e/test_design_v3.py tests/e2e/test_pages_site.py \| command grep -cE '^[-+][^-+].*(assert\|_TEXT\|has-text\|timeout\|wait_for)'` | `0` |
| C27 | [보완] 영어 스크린샷 | `.ai/tasks/T-20261027-public-launch/screenshots/i18n-en-convert-done.png`, `i18n-en-error.png`, `i18n-en-about.png`, `i18n-pages-en-done.png` | convert-done: 헤더 `KO` 버튼, 상태 `Server mode`, 영어 안내 문구, 미리보기에 합성 문서 / error: 오류 띠 `Not an HWP 5.0 or HWPX file` / about: 영어 hero·`Open converter` 버튼, 빈 제목·깨진 글자 없음 / pages-en-done: 스위치 없음, `Browser mode: files are not sent to a server`, 변환 결과 |
| C28 | [보완] README 영어판 | C10 스크립트에서 `README.md` → `README.en.md` 로 바꿔 실행; `command grep -c '^## ' README.md README.en.md`; `command grep -c 'README.en.md' README.md` | `relative=0`; 두 수 같음; `1` |
| C29 | [보완] Pages 영어 반영 | `curl -s -o /dev/null -w '%{http_code}\n' https://ilyos-numon.github.io/hwp2md/static/js/i18n.js https://ilyos-numon.github.io/hwp2md/static/js/i18n-about.js; curl -s https://ilyos-numon.github.io/hwp2md/convert.html \| command grep -c 'lang-toggle'` | `200` 2줄, `1` 이상 |
| C30 | [보완] 실제 Pages 영어 E2E | `HWP2MD_PAGES_URL=https://ilyos-numon.github.io/hwp2md/ ILLY_SHOT_DIR=.ai/tasks/T-20261027-public-launch/screenshots uv run pytest tests/e2e/test_i18n.py -q -k static` | 1 passed, `i18n-pages-live-en-done.png` 에 영어 상태·변환 결과 |

## 3. 실패 기준 (하나라도 해당하면 즉시 중단 → BLOCKED 기록)
- 같은 단계 재시도 3회 초과 → BLOCKED
- 같은 오류로 수정 2회 실패 → BLOCKED
- 단계 하나 도구 호출 40회 초과 → PARTIAL 기록 후 orchestrator 반환 (60회 넘기지 않음). 단계 하나 60분 초과 → PARTIAL
- serve 화면 회귀(기존 `test_web_ui.py`·`test_web_v3.py`·`test_web_extract.py` 실패)를 OUT 파일(원본 HTML·app.py) 수정 없이 못 고침 → BLOCKED
- jsDelivr 접근 불가로 Pyodide 케이스가 2회 연속 timeout → BLOCKED (네트워크, 사용자 확인)
- S10: 사용자 승인 없이 force-push·visibility 변경을 해야 하는 상황 → 실행하지 않고 대기
- S10: `gh pr list --state all` 결과 1건 이상 (옛 커밋이 `refs/pull/*` 로 남음) → force-push 전 BLOCKED
- S10: filter-repo 뒤 검사 V1~V4 중 하나라도 기대값과 다름 → push 하지 않고 백업에서 복원(§4.5 복원) 후 BLOCKED. 규칙 보강 재시도는 1회까지
- S10: `git bundle verify` 실패 → filter-repo 실행 금지, BLOCKED
- S12: Release `publish` 실패 → Actions 재실행 1회, 다시 실패하면 BLOCKED (PyPI 는 같은 버전 재업로드 불가)
- 자격증명·결제·외부 계정 생성 필요 (예: gh 토큰 scope 부족으로 workflow 파일 push 거절) → BLOCKED (사용자 `gh auth refresh -h github.com -s workflow`)
- 테스트 약화·삭제·skip 으로만 통과 가능 → BLOCKED (live 케이스의 환경변수 skip 은 §4.4 에 정의된 것만 허용)
- [보완] S12: `locale="ko-KR"` 추가 외에 기존 E2E 의 단언·기대 문구·선택자·타임아웃을 바꿔야 통과 → BLOCKED (C26 ≠ 0 이면 즉시 되돌림)
- [보완] S13·S14: ko 화면의 기존 문구가 한 글자라도 바뀌어 기존 E2E 가 실패 → 그 단계 재시도(최대 2회), 기대 문구를 고치는 방식은 금지
- [보완] S17: `git merge --ff-only` 실패 또는 force push 가 필요해짐 → BLOCKED. S18 태그 push 는 사용자 실행 대기(BLOCKED 로 기록하고 멈춤, 대기 자체는 실패 아님)

## 4. 인터페이스 계약 (병렬 작업 전 확정)

### 4.1 Pages 주소·base path·정적 빌드 출력 구조
- Pages URL: `https://ilyos-numon.github.io/hwp2md/` (프로젝트 사이트, base path `/hwp2md/`). 빌드는 base path 를 몰라도 되도록 **모든 사이트 내부 경로를 상대 경로**로 만든다.
- `scripts/build_pages.py --out <DIR> [--static-dir <DIR>]` 출력:
```
<DIR>/
  .nojekyll                  # 빈 파일
  index.html                 # src/hwp2md/web/static/about.html 변환본 (소개, 첫 화면)
  convert.html               # src/hwp2md/web/static/index.html 변환본 (변환 화면) + meta 2개 주입
  static/                    # static-dir 전체 사본에서 *.html 제외 (css/ js/ vendor/ pyodide-runner.js)
  pkg/hwp2md.zip             # hwp2md.web.app.build_runtime_zip() 바이트 그대로
```
- `.gitignore` 에 `dist-pages/` (S1).

### 4.2 정적 사이트 meta 설정 (S2 구현, S3 주입, S4 검증)
```html
<!-- convert.html <head> 에 build_pages.py 가 </title> 바로 뒤에 주입 -->
<meta name="hwp2md-site" content="static">
<meta name="hwp2md-pkg-url" content="pkg/hwp2md.zip">
<!-- index.html(소개) 에는 hwp2md-site 만 주입 (현재 JS 동작 영향 없음, 표시용) -->
```
- `pyodide-runner.js`: `const PKG_URL = (document.querySelector('meta[name="hwp2md-pkg-url"]') || {}).content || "/pkg/hwp2md.zip";` 를 쓰고 `fetch(PKG_URL, …)`, 오류 문구도 `PKG_URL + " HTTP " + status`. `window.Hwp2mdBrowser` 의 `load/convert/zip` 시그니처 불변.
- `app.js`:
  - `const STATIC_SITE = (meta[name="hwp2md-site"] content) === "static";`
  - `const ABOUT_URL = STATIC_SITE ? "index.html" : "/about";` `LIMITS_DOC = ABOUT_URL + "#limits"` (기존 `"/about#limits"` 대체. 다른 하드코딩된 `/about` 문자열이 있으면 같은 상수로).
  - STATIC_SITE 일 때 시작 시: `label.switch` 에 `hidden` 속성, `#mode-toggle` checked+disabled, `state.mode = "browser"`, `setModeStatus("loading")`, `Hwp2mdBrowser.load()` 호출 → 성공 `setModeStatus("browser")`, 실패 `setModeStatus("error", 메시지)` 이고 **mode 는 browser 유지(서버로 돌아가지 않음)**. 실패 뒤 파일을 넣으면 기존 `handleFile` catch 경로로 `body[data-state="error"]` + `#error` 에 "변환 중 오류가 발생했습니다: …".
  - STATIC_SITE 가 아니면 기존 코드 경로와 DOM 결과가 바이트 단위로 같은 동작 (`handleModeToggle` 변경 없음).
  - `window.Hwp2mdApp` 에 `staticSite: STATIC_SITE` 읽기 전용 필드 추가(테스트용). 기존 필드 불변.

### 4.3 빌드 치환 규칙 (S3, 원본 파일은 수정하지 않음)
| 대상 | 찾기 | 바꾸기 |
|------|------|--------|
| 두 HTML | `"/static/` | `"static/` |
| 두 HTML | `href="/about#` | `href="index.html#` |
| 두 HTML | `href="/about"` | `href="index.html"` |
| 두 HTML | `href="/"` | `href="convert.html"` |
| `static/vendor/fonts/fonts.css` | `url("/static/vendor/fonts/` | `url("` |
- 치환 뒤 HTML·CSS 전체에서 정규식 `(src|href)="/[^/]|url\(["']?/[^/]` 적중이 있으면 `BuildError`, 표준 오류에 `<상대경로>:<줄>: absolute-path`, 종료 코드 1. (JS 파일은 검사하지 않는다 — serve 용 `/api/...` 문자열은 정적 모드에서 쓰이지 않음.)
- `out` 이 존재하고 비어 있지 않은데 `.nojekyll` 이 없으면 지우지 않고 종료 코드 2 (`refuse: <out> is not a previous build`). 그 외에는 지우고 다시 만든다.
```python
# scripts/build_pages.py (표준 라이브러리 + hwp2md.web.app.build_runtime_zip 만)
STATIC_DIR: Path  # = hwp2md.web.app.STATIC_DIR
class BuildError(Exception):
    problems: list[str]          # "<rel>:<line>: absolute-path"
def build_site(out_dir: Path, static_dir: Path = STATIC_DIR) -> None: ...
def main(argv: list[str] | None = None) -> int: ...   # 0 성공, 1 BuildError, 2 refuse
```

### 4.4 E2E 계약 (`tests/e2e/test_pages_site.py`)
- fixture `pages_site` (module): `tmp/site/hwp2md/` 에 `build_site` 결과, `python -m http.server <빈 포트> --bind localhost --directory tmp/site` 백그라운드, base URL `http://localhost:<port>/hwp2md/`. 종료 시 프로세스 kill.
- 요청 감시: 같은 호스트 요청은 경로가 `/hwp2md/` 로 시작해야 함(아니면 기록 → assert 빈 목록). 그 밖 호스트는 `cdn.jsdelivr.net` 만 허용, 나머지는 abort + 기록 → assert 빈 목록. POST 요청 0건.
- 입력은 합성만: `tests/synth_hwpx.py` 의 `write_hwpx` 로 만든 HWPX. 실제 샘플·`REAL_SAMPLES` 사용 금지 (CI 에서도 돈다, `real_samples` 마커 없음).
- 케이스: (1) `test_pages_landing_to_convert` 성공 — 소개→"변환 도구 열기"(`a[href="convert.html"]`)→스위치 숨김 확인→`#mode-status[data-state="browser"]` (최대 240 s)→변환 `done`→스크린샷 `pages-landing.png`, `pages-convert-done.png`. (2) `test_pages_not_hwp` 실패 — `.hwp` 이름의 텍스트 파일 → `#error` 에 "HWP 5.0 또는 HWPX 파일이 아닙니다". (3) `test_pages_cdn_blocked` 실패 — `cdn.jsdelivr.net` abort → status `error`, 파일 넣으면 `body[data-state="error"]` → `pages-cdn-blocked.png`. (4) `test_pages_live` — `HWP2MD_PAGES_URL` 이 없으면 `pytest.mark.skipif` 로 건너뜀, 있으면 그 URL 의 `convert.html` 에서 (1) 과 같은 변환 → `pages-live-done.png`.
- 스크린샷 경로: `os.environ.get("ILLY_SHOT_DIR", "tests/e2e/screenshots")`. 타임아웃: 페이지 60 s, Pyodide 240 s.

### 4.5 이력 재작성 계약 (S10)
- 백업 위치(저장소 밖): `/Users/illi/hwp2md-backups/` — `hwp2md-pre-filter-20261027.bundle` (`git bundle create … --all`), `pre-filter-refs.txt` (`git show-ref` 출력), 복원 시험용 클론 `pre-filter-clone/`.
- 이력에서 지울 경로 (`/Users/illi/hwp2md-backups/filter/paths.txt`, `--paths-from-file … --invert-paths`):
```
glob:.ai/tasks/*/screenshots/*.md
.ai/tasks/T-20261023-extract-dropped/inventory.md
```
  - 근거(조사 결과): 첫 줄은 실제 샘플 5종과 합성 문서의 변환 Markdown(5개 태스크, 72개 경로, 커밋 `cd2ba3c` 에서 추적 해제됨). 둘째 줄은 실제 샘플 약 50개의 파일명 목록으로 기관 식별 정보를 담고 HEAD 에서도 추적 중. 그 밖에 실제 샘플 파일명·내용이 든 추적 파일은 이력 전체 검색(기관명·규정명 키워드)에서 이 둘뿐이었다.
- 문자열 치환 (`/Users/illi/hwp2md-backups/filter/replace.txt`, `--replace-text`). 금지 문자열을 이 플랜에 쓰지 않도록 printf 로 만든다:
```bash
mkdir -p /Users/illi/hwp2md-backups/filter && {
  printf '%s\n' 'regex:## 내부 메모 \(사용자에게 노출 금지\)\n[^\n]*\n[^\n]*\n\n==>'
  printf '%s.%s.%s.%s==>localhost\n' 127 0 0 1
  printf 'LXML=%s.%s.%s.%s==>LXML=%s.%s.%s\n' 5 2 1 0 5 2 1
} > /Users/illi/hwp2md-backups/filter/replace.txt
```
- 실행: `git filter-repo --force --paths-from-file /Users/illi/hwp2md-backups/filter/paths.txt --invert-paths --replace-text /Users/illi/hwp2md-backups/filter/replace.txt` (작업 트리 깨끗한 상태, main 체크아웃). 뒤에 `git remote -v` 가 비면 `git remote add origin https://github.com/ilyos-numon/hwp2md.git`.
- 태그 v0.1.0: filter-repo 가 annotated 태그를 새 커밋으로 다시 쓴다. 지운 경로·치환 대상이 배포물 경로(src, README.md, LICENSE, NOTICE, pyproject.toml)에 없으므로 같은 객체를 가리켜야 한다 → V4 로 확인. 다르면 push 금지.
- 검사 (모두 저장소에서):
  - V1 금지 경로: `git log --all --name-only --format= | LC_ALL=C command grep -cE '^"?\.ai/tasks/[^/]+/screenshots/.*\.md"?$|inventory\.md$'` → `0` (재작성 전 같은 명령 = `145` (커밋별 중복 포함, 고유 경로 73). 한글 경로는 따옴표로 감싸여 나오므로 `"?` 필수. 이 환경의 `grep` 은 셸 함수라 `command grep` 을 쓴다)
  - V2 금지 패턴: `P=$(awk '/^```sanitize-patterns/{f=1;next}/^```/{f=0}f' /Users/illi/illy-projects/doc/portfolio/sanitize-rules.md | paste -sd'|' -); for r in $(git rev-list --all); do git grep -IlEi "$P" $r; done | wc -l` → `0`
  - V3 내부 메모: `for r in $(git rev-list --all -- CLAUDE.md); do git show $r:CLAUDE.md; done | grep -cE '내부 메모|엔진 공유 프로젝트'` → `0`
  - V4 태그 내용: `O=$(git -C /Users/illi/hwp2md-backups/pre-filter-clone rev-parse 'v0.1.0^{commit}'); N=$(git rev-parse 'v0.1.0^{commit}'); for p in src README.md LICENSE NOTICE pyproject.toml; do [ "$(git -C /Users/illi/hwp2md-backups/pre-filter-clone rev-parse $O:$p)" = "$(git rev-parse $N:$p)" ] && echo "same $p" || echo "DIFF $p"; done` → `same` 5줄
- push: `git push --force origin main` → `git push --force origin --tags` → 원격의 main 외 브랜치 삭제 (`git ls-remote --heads origin` 에서 main 이외 각각 `git push origin --delete <branch>`; 현재 알려진 것 `ai/T-20261027-pypi-release`, 게이트 전 S9 에서 push 한 `ai/T-20261027-public-launch`).
- 복원 (V1~V4 실패 또는 push 전 중단 시): `git fetch /Users/illi/hwp2md-backups/hwp2md-pre-filter-20261027.bundle '+refs/heads/*:refs/heads/*' '+refs/tags/*:refs/tags/*' --update-head-ok` 후 `git reset --hard main` (main 체크아웃 상태에서 `--update-head-ok`).

### 4.6 발견성 값 (S5·S6·S1)
```toml
# pyproject.toml [project] — license 분류자 금지 (PEP 639 license 표현식과 충돌)
description = "Convert Korean HWP, HWPX and HWPML documents to Markdown without Hancom Office"
keywords = ["hwp", "hwpx", "hwpml", "markdown", "converter", "korean", "hangul", "hancom", "document-conversion", "pyodide"]
classifiers = [
  "Development Status :: 4 - Beta",
  "Environment :: Console",
  "Environment :: Web Environment",
  "Intended Audience :: Developers",
  "Intended Audience :: End Users/Desktop",
  "Natural Language :: Korean",
  "Operating System :: OS Independent",
  "Programming Language :: Python :: 3",
  "Programming Language :: Python :: 3 :: Only",
  "Programming Language :: Python :: 3.11",
  "Programming Language :: Python :: 3.12",
  "Programming Language :: Python :: 3.13",
  "Topic :: Office/Business :: Office Suites",
  "Topic :: Text Processing :: Markup :: Markdown",
  "Topic :: Utilities",
  "Typing :: Typed",
]
[project.urls]
Homepage = "https://ilyos-numon.github.io/hwp2md/"
Repository = "https://github.com/ilyos-numon/hwp2md"
Issues = "https://github.com/ilyos-numon/hwp2md/issues"
Changelog = "https://github.com/ilyos-numon/hwp2md/blob/main/CHANGELOG.md"
```
- README 배지 (맨 위 `# hwp2md` 바로 다음 줄, 이 순서). **배지 서비스는 badgen.net·pepy·GitHub 만 쓴다 — 흔히 쓰는 배지 서비스 도메인은 익명화 금지 패턴(대소문자 무시)에 걸려 sanitize-check 가 실패한다:**
```markdown
[![PyPI](https://badgen.net/pypi/v/hwp2markdown)](https://pypi.org/project/hwp2markdown/)
[![Python](https://badgen.net/pypi/python/hwp2markdown)](https://pypi.org/project/hwp2markdown/)
[![CI](https://github.com/ilyos-numon/hwp2md/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/ilyos-numon/hwp2md/actions/workflows/ci.yml)
[![Downloads](https://static.pepy.tech/badge/hwp2markdown/month)](https://pepy.tech/projects/hwp2markdown)
[![License: MIT](https://badgen.net/badge/license/MIT/blue)](https://github.com/ilyos-numon/hwp2md/blob/main/LICENSE)
```
- README 절대 URL 규칙: 그림 → `https://raw.githubusercontent.com/ilyos-numon/hwp2md/main/<경로>`, 저장소 파일 링크 → `https://github.com/ilyos-numon/hwp2md/blob/main/<경로>`. 코드 블록 안(예: CLI 출력 예시의 `demo_images/...`)은 바꾸지 않는다.
- README 추가 절: 배지 아래 "**브라우저에서 바로 써 보기 → https://ilyos-numon.github.io/hwp2md/** (설치 없음, 파일은 브라우저 밖으로 나가지 않음, 첫 준비 약 1분)" 한 줄 / "30초 데모" 절(체험 링크 + `pip install hwp2markdown` + `hwp2md 문서.hwp -o out/` 3줄) / `## English` 절(5~8줄: what, install, browser demo, privacy, license).
- README 링크 검사 (C10):
```bash
uv run python - <<'EOF'
import re, pathlib
t = re.sub(r"```.*?```", "", pathlib.Path("README.md").read_text(), flags=re.S)
bad = [u for u in re.findall(r"\]\(([^)\s]+)", t) if not u.startswith(("https://", "#"))]
print("relative=%d" % len(bad), bad)
EOF
```
- gh 저장소 (S1): `gh repo edit ilyos-numon/hwp2md --description "Convert Korean HWP/HWPX documents to Markdown — CLI, Python library, and in-browser converter (no Hancom Office)" --homepage https://ilyos-numon.github.io/hwp2md/ --add-topic hwp --add-topic hwpx --add-topic markdown --add-topic converter --add-topic korean --add-topic hangul --add-topic pyodide --add-topic python --add-topic cli`
- `CHANGELOG.md`: Keep a Changelog 형식, `## [0.1.1] - <S6 작업일>` (Added: 브라우저 체험 사이트, 프로젝트 URL·분류자, README 배지·영문 요약 / Changed: README 절대 URL, 패키지 description) 와 `## [0.1.0] - 2026-10-27` (첫 PyPI 릴리스 요약 3~5줄).
- 이슈 템플릿 `.github/ISSUE_TEMPLATE/bug_report.yml` (name "변환 오류 신고", 필드: hwp2md 버전·입력 형식(HWP 5.0/HWPX/HWPML 드롭다운)·실행 방법(CLI/라이브러리/웹 serve/브라우저 체험)·오류 메시지·기대 결과. 상단 markdown 안내: "실제 문서를 첨부하기 전에 개인정보·내부 정보가 없는지 확인하세요. 가능하면 문제를 재현하는 짧은 문서를 새로 만들어 첨부하세요.") + `config.yml` (`blank_issues_enabled: true`).

### 4.7 Pages 워크플로우 (S7)
```yaml
# .github/workflows/pages.yml — 액션 major 버전은 S7 에서 `gh api repos/<owner>/<action>/releases/latest` 로 확인한 최신 major
name: Pages
on:
  push: { branches: [main] }
  workflow_dispatch:
permissions: { contents: read, pages: write, id-token: write }
concurrency: { group: pages, cancel-in-progress: false }
jobs:
  build:
    if: ${{ !github.event.repository.private }}
    runs-on: ubuntu-latest
    steps: checkout(ci.yml 과 같은 버전) → astral-sh/setup-uv(ci.yml 과 같은 버전, python 3.12) → uv sync --locked
           → uv run python scripts/build_pages.py --out dist-pages → actions/configure-pages → actions/upload-pages-artifact (path: dist-pages)
  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment: { name: github-pages, url: "${{ steps.deployment.outputs.page_url }}" }
    steps: actions/deploy-pages (id: deployment)
```

### 4.8 영어 지원 (i18n) 계약 (S12~S16) — [보완 2026-10-27]
- 언어는 `ko`·`en` 두 개뿐. 새 의존성 없음 (순수 JS 사전 객체). CLI 출력·Python 엔진·HTTP API 응답 형식은 바꾸지 않는다.
- 파일:
  - `src/hwp2md/web/static/js/i18n.js` (새 파일, S13) — 결정 로직·DOM 적용·토글·JS 문구 사전(`KO`·`EN` 객체 둘 다)과 변환 화면 HTML 문구의 영어값.
  - `src/hwp2md/web/static/js/i18n-about.js` (새 파일, S14) — 소개 페이지 HTML 문구의 영어값만: `window.HWP2MD_I18N_EXTRA = { en: { "<key>": "<문구>", … } };` (다른 코드 없음).
  - `effects.js`·`landing.js` 에는 사용자 노출 한국어 문자열이 없다(조사 결과: 한글은 주석뿐). 소개 페이지 문구는 전부 `about.html` 안(텍스트·`data-t`·`data-type`·`data-tag`·`aria-label`·`<title>`·`<meta name="description">`)에 있다.
- 스크립트 위치 (원본 HTML, `/static/...` 절대 경로 — `build_pages.py` 가 기존 규칙 `"/static/`→`"static/` 로 치환하므로 빌드 스크립트 변경 없음):
  - `index.html`: `</body>` 앞 스크립트 묶음의 **맨 앞**에 `<script src="/static/js/i18n.js"></script>` (marked·gsap·pyodide-runner·theme·app 보다 먼저).
  - `about.html`: 스크립트 묶음 맨 앞에 `<script src="/static/js/i18n-about.js"></script><script src="/static/js/i18n.js"></script>` (gsap 보다 먼저 → SplitText 가 번역된 글자를 나눈다). `<body>` 에 `data-i18n-reload` 속성 추가.
- 언어 결정 (i18n.js 로드 즉시, 동기):
```js
// 1) ?lang= 쿼리가 "ko" 또는 "en" (소문자 정확히 일치) → 그 값, localStorage 에 저장, source="query"
// 2) localStorage["hwp2md-lang"] 이 "ko"|"en" → 그 값, source="storage"
// 3) (navigator.languages && navigator.languages[0]) || navigator.language || "" 를 소문자로 → "ko" 로 시작하면 "ko", 아니면 "en", source="navigator"
// 그 밖의 ?lang= 값(예 "fr", "EN", "")은 무시하고 2) → 3) 으로 폴백 (저장하지 않음). localStorage 접근 예외는 무시.
// 결정 직후 document.documentElement.lang = lang
```
- 공개 API (i18n.js):
```ts
interface Hwp2mdI18n {
  readonly lang: "ko" | "en";
  readonly source: "query" | "storage" | "navigator";
  t(key: string, vars?: Record<string, string | number>): string; // "{name}" 치환. en: EN[key] ?? KO[key] ?? key / ko: KO[key] ?? key
  set(lang: "ko" | "en"): void;  // 저장 → URL 의 lang 쿼리 제거(history.replaceState) → body[data-i18n-reload] 면 location.reload(), 아니면 html lang 갱신 + apply(document) + 토글 갱신 + 이벤트
  apply(root?: ParentNode): void;
  missing(): string[];           // KO 에 있는데 EN 에 없는 키 + DOM 의 data-i18n* 키 중 EN 에 없는 키 (정렬, 중복 제거)
}
declare global { interface Window { Hwp2mdI18n: Hwp2mdI18n; HWP2MD_I18N_EXTRA?: { en: Record<string, string> } } }
// 언어가 바뀌면 document.dispatchEvent(new CustomEvent("hwp2md:langchange", { detail: lang }))
```
- DOM 표기 (HTML 원문 한국어가 곧 ko 값이다 — ko 사전에 HTML 문구를 중복으로 두지 않는다):
  - `data-i18n="<key>"` → `textContent`. 자식 요소(svg 등)가 있는 요소에는 달지 않는다 — 글자를 `<span data-i18n>` 으로 감싼다.
  - `data-i18n-html="<key>"` → `innerHTML` (사전 값은 저장소의 정적 문자열만. 사용자·서버 입력을 넣지 않는다).
  - `data-i18n-attr="<attr>:<key>;<attr>:<key>"` → 속성 (`aria-label`, `title`, `content`, `data-t`, `data-type`, `data-tag`, `data-from`).
  - `apply()` 는 처음 볼 때 원문(텍스트/HTML/속성값)을 `WeakMap` 에 저장하고, ko 로 돌아갈 때 그 원문을 쓴다. en 값이 없는 키는 원문 유지 + 요소에 `data-i18n-missing="<key>"` + `console.warn`.
  - **`app.js` 가 글자를 바꾸는 요소에는 `data-i18n` 을 달지 않는다**: `#mode-status`, `#error-text`, `#skipped`, `#result-meta`, `#raw-meta`, `#toast`, `#copy span`, `#file-name`(파일 선택 뒤). 이들의 초기 글자도 app.js 가 `t()` 로 쓴다. 예외: `#file-name` 의 초기 "선택한 파일 없음" 은 `data-i18n` 으로 두고 app.js 가 파일 이름으로 덮는다(파일 선택 후 apply 가 다시 덮지 않도록 app.js 가 `removeAttribute("data-i18n")`).
  - 키 이름: `<영역>.<이름>` 소문자·점·밑줄 (`convert.*`, `about.*`, `common.*`, 그리고 JS 키 `mode.*`, `error.*`, `skipped.*`, `count.*`, `raw.*`, `toast.*`, `copy.*`, `theme.*`, `lang.*`).
- 전환 버튼 (두 화면 모두 `.header-actions` 안, `.theme-toggle` 바로 앞):
```html
<button type="button" class="icon-btn lang-toggle" data-i18n-attr="aria-label:lang.toggle_label" aria-label="Switch to English"><span data-i18n="lang.toggle_text">EN</span></button>
```
  - en 사전: `lang.toggle_text` = `KO`, `lang.toggle_label` = `한국어로 보기`. 즉 ko 화면에는 `EN`, en 화면에는 `KO` 가 보이고, 누르면 반대 언어로 `set()`.
  - 변환 화면(`index.html`)은 새로고침 없이 바로 바꾼다(변환 결과 유지). 소개 화면(`about.html`, `body[data-i18n-reload]`)은 저장 후 새로고침한다(SplitText·ScrambleText 가 이미 나눈 글자를 다시 쓰지 않기 위해).
  - CSS: `src/hwp2md/web/static/css/base.css` 끝에 `.lang-toggle` 규칙만 10줄 이하 추가 (글자 크기·굵기·자간). 다른 CSS 규칙 변경 금지.
- `app.js` (S13):
  - `ERROR_TEXT`·`MODE_STATUS_TEXT`·고정 한국어 문자열을 `Hwp2mdI18n.t()` 호출로 바꾼다. 한국어 결과는 지금 문자열과 **바이트 단위로 같다** (기존 E2E 가 단언).
  - `hwp2md:langchange` 에서 다시 그린다: 모드 상태(마지막 name·detail), 표시 중인 오류(마지막 code·message 를 state 에 보관), `state.result` 가 있으면 `#result-meta`·`#raw-meta`·`#skipped`, 복사 버튼 글자. 토스트는 다시 그리지 않는다.
  - `window.Hwp2mdApp` 기존 필드 불변. 숫자 서식은 `toLocaleString(lang === "en" ? "en-US" : "ko-KR")`.
  - `theme.js` (S13): 두 aria-label 을 `t("theme.to_dark")`·`t("theme.to_light")` 로, `hwp2md:langchange` 에서 갱신. `Hwp2mdI18n` 이 없으면 지금 한국어 문자열을 쓴다.
- 고정 문구 (E2E 가 그대로 단언. ko 열은 현재 문자열 그대로):

| 키 | ko | en |
|----|----|----|
| `mode.server` | 서버 모드 | Server mode |
| `mode.loading` | 브라우저 모드 준비 중… | Preparing browser mode… |
| `mode.browser` | 브라우저 모드: 파일이 서버로 전송되지 않습니다 | Browser mode: files are not sent to a server |
| `mode.error` (뒤에 detail) | 브라우저 모드를 불러오지 못했습니다:␠ | Could not load browser mode:␠ |
| `error.empty` | 빈 파일입니다 | The file is empty |
| `error.too_large` | 파일이 너무 큽니다 (최대 50MB) | The file is too large (max 50MB) |
| `error.not_hwp` | HWP 5.0 또는 HWPX 파일이 아닙니다 | Not an HWP 5.0 or HWPX file |
| `error.unsupported` | 지원하지 않는 HWP 문서라 변환할 수 없습니다 | This HWP document is not supported and cannot be converted |
| `error.drm` | (현재 문자열) | This file is protected by document security (DRM) and cannot be converted. Remove the protection in your security software and try again |
| `error.encrypted` | (현재 문자열) | This document is password-protected and cannot be converted. Remove the password in Hangul and try again |
| `error.generic` (뒤에 message) | 변환 중 오류가 발생했습니다:␠ | An error occurred during conversion:␠ |
| `skipped.prefix` | 변환하지 못한 요소:␠ | Not converted:␠ |
| `skipped.item` | {label} {n}개 | {label} ({n}) |
| `skipped.why` | 왜 빠졌나요? | Why? |
| `raw.meta` | {lines}줄 · {chars}자 | {lines} lines · {chars} chars |
| `toast.zip` | {name}.zip 을 내려받았습니다 | Downloaded {name}.zip |
| `toast.copied` | Markdown 원문을 복사했습니다 | Copied the Markdown source |
| `copy.idle` / `copy.done` | 복사 / 복사됨 | Copy / Copied |
| `theme.to_dark` / `theme.to_light` | 다크 모드로 전환 / 라이트 모드로 전환 | Switch to dark mode / Switch to light mode |
| `convert.title` (`<title>`) | hwp2md 변환 도구 | hwp2md converter |
| `convert.heading` (`h1`) | 한글 문서를 Markdown으로 | HWP documents to Markdown |
| `about.open_converter` (헤더 버튼 글자) | 변환 도구 열기 | Open converter |

  - `#skipped` 의 라벨(`skipped[].label`)은 서버·엔진이 주는 한국어 그대로 표시하고 접두·개수 서식만 번역한다 (§7 Q9). 예 en: `Not converted: 머리말·꼬리말 (1)`.
  - `#result-meta` en 형식: `<b data-k="paragraphs">N</b> paragraph(s) · <b data-k="tables">N</b> table(s) · …` — N 이 1 이면 단수(`paragraph`, `table`, `heading`, `image`), 아니면 복수(`paragraphs`, `tables`, `headings`, `images`). 항목 순서·`b[data-k]`·구분자 ` · ` 는 ko 와 같다. ko 형식은 현재 그대로(`단락 <b data-k="paragraphs">N</b>개 · …`).
  - 한컴 공개 문서 참고 고지(바닥글)의 en 값: 영어 번역 뒤에 한국어 원문 문장을 괄호로 그대로 붙인다 (§7 Q11). 그 밖 문구의 영어는 S13·S14 implementer 가 정하고 E2E 는 키 누락(`missing()` = `[]`)과 화면 틀의 한글 0 으로 검사한다.
  - 소개 페이지에서 **번역하지 않는 것**: 한국어 예시 문서 내용(히어로 `.hv-line` 의 Markdown 예시, 파이프라인 `.blk` 안의 원고 문장)과 CLI 출력 줄(`.tl` 중 `tl--note` 가 아닌 출력 줄 — CLI 는 한국어 출력 그대로). `.blk` 의 `data-tag`(블록 꼬리표)와 `tl--note` 주석 줄은 번역한다.
- 기존 E2E 와 locale (S12): 기존 브라우저 E2E 5개 파일은 `sync_playwright()` 로 각자 `browser.new_context(...)` 를 만들고 `locale` 을 주지 않는다 (공용 pytest-playwright 픽스처 없음, conftest 에 브라우저 픽스처 없음). Playwright Chromium 의 기본 언어는 호스트 설정을 따르므로(CI ubuntu 는 `en-US`) i18n 뒤에는 기본 언어가 영어가 되어 한국어 단언이 깨진다. 해결: **모든 기존 `browser.new_context(` 호출에 `locale="ko-KR"` 인자만 추가**한다 (test_web_v3 의 `_make` 는 `kwargs.setdefault("locale", "ko-KR")`). 이는 테스트 대상 환경(브라우저 언어)을 고정하는 것이지 단언을 약화하는 것이 아니다 — 단언·기대 문구·선택자·타임아웃은 한 글자도 바꾸지 않는다. 대상 호출 수: `test_web_ui.py` 3, `test_web_extract.py` 2, `test_web_v3.py` 1, `test_design_v3.py` 1, `test_pages_site.py` 1.
- 새 E2E `tests/e2e/test_i18n.py` (S15) — 기존 파일 패턴(`sync_playwright`, module `browser` 픽스처, `web_server`, 합성 입력 `tests/synth_hwpx.py`·`synth_hwp5.py`)을 따른다. 컨텍스트마다 `locale` 을 명시한다. 실제 샘플 사용 금지. 케이스(최소 8, skip 0):
  1. `test_server_en_by_navigator` 성공 — locale `en-US`, `/` → `html[lang="en"]`, `Hwp2mdI18n.source == "navigator"`, `#mode-status` = `Server mode`, 합성 HWPX 변환 → `body[data-state="done"]`, `#result-meta` 에 `paragraph`, `Hwp2mdI18n.missing()` = `[]`, `header, #drop-zone, .status-bar, .pane-tabs` 의 innerText 에 한글(`[가-힣]`) 0 → 스크린샷 `i18n-en-convert-done.png`.
  2. `test_server_en_error` 실패 경로 — locale `en-US`, `.hwp` 이름 텍스트 파일 → `#error-text` = `Not an HWP 5.0 or HWPX file` → `i18n-en-error.png`.
  3. `test_toggle_to_korean_persists` — locale `en-US`, 변환 후 `.lang-toggle` 클릭 → `html[lang="ko"]`, `#mode-status` = `서버 모드`, `#result-meta` 에 `단락`, `body[data-state="done"]` 유지, `.lang-toggle` 글자 `EN` → 새로고침 → 여전히 ko, `source == "storage"`.
  4. `test_query_overrides_navigator` — locale `ko-KR`, `/?lang=en` → `html[lang="en"]`, `source == "query"`.
  5. `test_unknown_lang_falls_back` 실패 경로 — locale `ko-KR` `/?lang=fr` → `ko`; 새 컨텍스트 locale `en-US` `/?lang=EN` → `en`, 둘 다 `source == "navigator"`, localStorage `hwp2md-lang` 없음.
  6. `test_skipped_prefix_en` — locale `en-US`, `/api/convert` 응답을 `page.route` 로 대체(기존 `test_design_v3.py` 패턴)해 `skipped=[{"label":"머리말·꼬리말","count":1}]` → `#skipped` 가 `Not converted: 머리말·꼬리말 (1)` 로 시작, 링크 글자 `Why?`.
  7. `test_about_en_and_toggle` — locale `en-US`, `/about` → `html[lang="en"]`, `a:has-text("Open converter")` 첫 요소 href `/`, `missing()` = `[]` → `i18n-en-about.png`; `.lang-toggle` 클릭 → 새로고침 뒤 `html[lang="ko"]`, `a:has-text("변환 도구 열기")` 보임.
  8. `test_static_site_en` — `build_site` 결과를 하위 경로 `/hwp2md/` 로 `http.server` 서비스(test_pages_site 의 픽스처 패턴 복제), locale `en-US`, `convert.html` → `#mode-status[data-state="browser"]`(최대 240 s) 글자 `Browser mode: files are not sent to a server`, 합성 HWPX 변환 `done` → `i18n-pages-en-done.png`. 요청 감시: 같은 호스트는 `/hwp2md/` 아래만, 외부는 `cdn.jsdelivr.net` 만, POST 0. `HWP2MD_PAGES_URL` 이 있으면 그 base 로 같은 케이스를 돌리고 스크린샷 이름은 `i18n-pages-live-en-done.png` (skipif 쓰지 않음).
- 스크린샷 경로 `os.environ.get("ILLY_SHOT_DIR", "tests/e2e/screenshots")`. 타임아웃 페이지 60 s, Pyodide 240 s.
- 문서 (S16): `README.en.md` = README.md 전체 영어판(배지 5개 동일, 체험 링크, 30초 데모, 같은 `## ` 절 수, §4.6 절대 URL 규칙, 코드 블록 안 CLI 출력은 원문 그대로). README.md 의 배지 블록 바로 다음 줄에 `**English:** [README.en.md](https://github.com/ilyos-numon/hwp2md/blob/main/README.en.md)` 한 줄. `pyproject` readme 는 README.md 그대로 (§7 Q10). CHANGELOG `[0.1.1]` Added 에 `- 웹 화면(변환·소개) 영어 지원: 브라우저 언어로 자동 선택, 헤더 KO/EN 전환, \`?lang=ko|en\`. README 영어판(README.en.md).` 한 줄. `docs/feature-reference.md` §9 끝에 `### 9.9 언어 (i18n)` 절(이 계약 요약: 결정 순서, API, DOM 표기, 고정 문구 표 링크, 서버 라벨 비번역). `docs/decisions.md` 끝에 `## 2026-10-27 웹 화면 영어 지원: 의존성 없는 사전 + data-i18n` 항목(결정·이유, E2E locale 고정 근거 포함).

## 5. 단계 (Stage)
공통: 서브에이전트 프롬프트 [경로]에 `PROJECT_ROOT=/Users/illi/illy-projects/hwp2md`, "모든 Bash 는 `cd /Users/illi/illy-projects/hwp2md && ` 로 시작, uv 는 `env -u VIRTUAL_ENV uv`". 단계 시작 시 orchestrator 가 `git rev-parse HEAD > .ai/tasks/T-20261027-public-launch/.base-s<n>`. 단계 완료 = 검증 통과 + PROGRESS 체크포인트 + sanitize(C12) exit 0 + 커밋 `[T-20261027-public-launch][sN] …` + tasks.md 해당 항목 체크.

### Stage 1 — 공개 전 설정 정리 (orchestrator 전용 파일)
- 목적: 정적 빌드 출력 무시, 공개 전 내부 메모 절 삭제, 저장소 메타 설정
- 담당: orchestrator 직접 (전용 파일, 각 10줄 이하)
- 병렬 가능: 아니오 · 선행: 없음
- 입력: §4.1, §4.6 gh 명령
- 쓰기 범위:
  - `.gitignore` (끝에 `dist-pages/` 1줄)
  - `CLAUDE.md` (`## 내부 메모 (사용자에게 노출 금지)` 절 heading+2줄+빈 줄 삭제)
- 산출물: 위 2파일 변경, GitHub 저장소 description·homepage·topics
- 검증: `grep -c '내부 메모' CLAUDE.md` → `0`; `git check-ignore dist-pages/x` → `dist-pages/x`; C20 의 topics 수 ≥ 8
- 완료 조건: 검증 + 커밋 `[…][s1] 공개 전 설정 정리`
- 실패 시: gh 오류(권한) → BLOCKED. 파일 변경은 `git restore`

### Stage 2 — 정적 사이트 모드 훅 (app.js·pyodide-runner.js)
- 목적: meta 가 있으면 브라우저 모드 고정, 없으면 serve 그대로
- 담당: implementer(opus)
- 병렬 가능: 아니오 · 선행: S1
- 입력: §4.2, `src/hwp2md/web/static/js/app.js`, `src/hwp2md/web/static/pyodide-runner.js`, `src/hwp2md/web/static/index.html`(읽기만), `docs/feature-reference.md` §9·§10(읽기만)
- 쓰기 범위:
  - `src/hwp2md/web/static/js/app.js`
  - `src/hwp2md/web/static/pyodide-runner.js`
- 산출물: §4.2 동작
- 검증: `node --check src/hwp2md/web/static/js/app.js && node --check src/hwp2md/web/static/pyodide-runner.js` → exit 0; `uv run pytest tests/e2e/test_web_ui.py tests/e2e/test_web_v3.py tests/e2e/test_web_extract.py tests/e2e/test_web_api.py -q` → failed 0 (serve 회귀 없음); `uv run pytest tests/unit/test_web_app.py -q` → failed 0
- 완료 조건: 검증 + 커밋 `[…][s2] 정적 사이트 meta 설정`
- 실패 시: 2파일 `git restore` 후 재시도(최대 2회), 넘으면 BLOCKED

### Stage 3 — 정적 빌드 스크립트
- 목적: `dist-pages/` 를 만드는 `build_pages.py` 와 단위 테스트
- 담당: implementer(opus)
- 병렬 가능: 아니오 · 선행: S2 (meta 이름 사용)
- 입력: §4.1, §4.2, §4.3, `src/hwp2md/web/app.py`(읽기만, `build_runtime_zip`·`STATIC_DIR`), `scripts/check_dist.py`(스타일 참고)
- 쓰기 범위:
  - `scripts/build_pages.py`
  - `tests/unit/test_build_pages.py`
- 산출물: §4.3 시그니처. 단위 테스트 최소 4개: 정상 빌드 구조·zip 바이트 동일·convert.html 에 meta 2개, 절대 경로 0, 잘못된 원본(임시 static-dir 에 `src="/x.js"`)→ exit 1 + `absolute-path`, 비어 있지 않은 남의 폴더 → exit 2 이고 파일 보존
- 검증: C1, C2, `uv run pytest tests/unit/test_build_pages.py -q` → passed ≥ 4 failed 0, C4, C5
- 완료 조건: 검증 + 커밋 `[…][s3] 정적 빌드 스크립트`
- 실패 시: 재시도 최대 2회 → BLOCKED

### Stage 4 — 정적 사이트 E2E 작성·실행 (로컬 하위 경로)
- 목적: 하위 경로에서 합성 HWPX 브라우저 변환 성공 + 실패 경로 2개를 자동 검증
- 담당: test-writer(sonnet) 작성 → runner(haiku) 실행 (test-writer 2회 실패 시 opus)
- 병렬 가능: 아니오 · 선행: S3
- 입력: §4.4, `tests/e2e/test_web_ui.py`(Pyodide 대기 패턴), `tests/e2e/test_web_v3.py`(요청 가드 패턴), `tests/e2e/conftest.py`, `tests/synth_hwpx.py`, `scripts/build_pages.py`
- 쓰기 범위:
  - `tests/e2e/test_pages_site.py`
- 산출물: §4.4 케이스 3개. [orchestrator 보완 2026-10-27] skipif 는 gate 가 약화로 판정하므로 test_pages_live 를 만들지 않고, `HWP2MD_PAGES_URL` 이 있으면 같은 3케이스가 그 base 로 돈다(S13 실제 Pages 확인은 이 환경변수로 실행). 기대값 `3 passed`, skip 0
- 검증: `ILLY_SHOT_DIR=.ai/tasks/T-20261027-public-launch/screenshots uv run pytest tests/e2e/test_pages_site.py -q > .ai/tasks/T-20261027-public-launch/logs/s4-e2e.log 2>&1; echo exit=$?` → `3 passed, 1 skipped`, exit=0; 스크린샷 3장 존재. reviewer 는 S14 에서 C7 대조
- 완료 조건: 검증 + 커밋 `[…][s4] 정적 사이트 E2E`
- 실패 시: §e2e-standard 실패 분류 — 테스트 오류는 test-writer, 구현 오류(S2·S3 파일)는 implementer 에 그 파일 쓰기 범위로 재호출. 합계 재시도 3회 초과 → BLOCKED

### Stage 5 — 패키지 메타데이터 (pyproject.toml 전용 단계)
- 목적: PyPI 에 urls·keywords·classifiers·description 표시
- 담당: implementer(opus) — 쓰기 범위가 orchestrator 전용 파일 하나뿐인 별도 순차 단계
- 병렬 가능: 아니오 · 선행: S4
- 입력: §4.6 toml 블록
- 쓰기 범위:
  - `pyproject.toml` (`[project]` 의 description·keywords·classifiers, 새 `[project.urls]` 만. `[project.scripts]`·빌드 설정 불변)
- 산출물: §4.6 값 그대로
- 검증: `uv lock --check` → exit 0 (실패하면 orchestrator 가 `uv lock` 후 `uv.lock` 같이 커밋); `uv build --out-dir dist` 후 `unzip -p dist/*.whl '*.dist-info/METADATA' | grep -cE '^(Project-URL|Classifier: Natural Language :: Korean|Classifier: Topic :: Text Processing :: Markup :: Markdown)'` → `6`; C9 (`--tag` 없이) → OK
- 완료 조건: 검증 + 커밋 `[…][s5] 패키지 메타데이터`
- 실패 시: hatchling 이 분류자 거절 → 해당 분류자 제거 1회, 그래도 실패면 BLOCKED

### Stage 6 — README·CHANGELOG·버전 0.1.1·문서
- 목적: PyPI·GitHub 첫 화면에서 체험 링크·배지·영문 요약이 보이고 그림이 열린다
- 담당: implementer(opus)
- 병렬 가능: 아니오 · 선행: S5
- 입력: §4.1 URL, §4.6 README·CHANGELOG 규칙, 현재 `README.md`, `docs/releasing.md`, `docs/decisions.md`
- 쓰기 범위:
  - `README.md`
  - `CHANGELOG.md` (새 파일)
  - `src/hwp2md/__init__.py` (`__version__ = "0.1.1"` 한 줄만)
  - `docs/releasing.md` (끝에 "## GitHub Pages" 절: pages.yml, 비공개면 건너뜀, 로컬 빌드 `uv run python scripts/build_pages.py --out dist-pages`, 로컬 미리보기 `python -m http.server 8771 --directory dist-pages`)
  - `docs/decisions.md` (2026-10-27 항목 2개: 정적 사이트는 원본 HTML 을 두고 빌드에서 상대 경로로 치환·meta 로 모드 고정 / 공개 전 filter-repo 로 샘플 산출물 이력 삭제)
- 산출물: §4.6 배지 5개·체험 줄·30초 데모·English 절, 절대 URL
- 검증: C10 → `relative=0`; `grep -c 'static.pepy.tech/badge/hwp2markdown' README.md` → `1`; `grep -cE '^## \[0\.1\.(0|1)\]' CHANGELOG.md` → `2`; C8, C9; `uv run pytest tests/unit -q` failed 0; C12
- 완료 조건: 검증 + 커밋 `[…][s6] README·CHANGELOG·0.1.1`
- 실패 시: 재시도 최대 2회 → BLOCKED

### Stage 7 — Pages 워크플로우·이슈 템플릿 (.github 전용 단계)
- 목적: main push 시 Pages 배포, 버그 신고 양식
- 담당: implementer(opus) — 쓰기 범위가 `.github/**` 의 새 파일 3개뿐인 별도 순차 단계
- 병렬 가능: 아니오 · 선행: S6
- 입력: §4.6 이슈 템플릿, §4.7, `.github/workflows/ci.yml`(읽기만, 액션 버전 맞춤)
- 쓰기 범위:
  - `.github/workflows/pages.yml`
  - `.github/ISSUE_TEMPLATE/bug_report.yml`
  - `.github/ISSUE_TEMPLATE/config.yml`
- 산출물: §4.7 워크플로우, 템플릿 2개
- 검증: C11 → exit 0; `uvx --from pyyaml python -c "import yaml,sys;[yaml.safe_load(open(f)) for f in sys.argv[1:]];print('yaml ok')" .github/ISSUE_TEMPLATE/bug_report.yml .github/ISSUE_TEMPLATE/config.yml` → `yaml ok`
- 완료 조건: 검증 + 커밋 `[…][s7] Pages 워크플로우·이슈 템플릿`
- 실패 시: actionlint 오류 2회 수정 실패 → BLOCKED

### Stage 8 — 홍보 초안 (docs/launch)
- 목적: 사용자가 바로 붙여 넣을 수 있는 한국어 게시글 초안 2개 (게시는 사용자)
- 담당: implementer(opus)
- 병렬 가능: 아니오 · 선행: S7
- 입력: README.md(S6 판), §4.1·§4.6 URL
- 쓰기 범위:
  - `docs/launch/community-post.md` (개발자 커뮤니티용: 제목 후보 3개, 본문 — 문제·해결·30초 데모·브라우저 체험·개인정보(파일이 기기 밖으로 나가지 않음)·한계·피드백 요청, 1,500~3,000자)
  - `docs/launch/sns-post.md` (500자 이하 1개 + 해시태그 5개 이하)
- 산출물: 위 2파일. 회사·고객·사람 이름, 실제 샘플 파일명, 근거 없는 수치(사용자 수·정확도 %) 금지
- 검증: C23; C12 exit 0; `grep -c 'ilyos-numon.github.io/hwp2md' docs/launch/*.md` → 각 1 이상
- 완료 조건: 검증 + 커밋 `[…][s8] 홍보 초안`
- 실패 시: 재시도 최대 2회 → BLOCKED

### Stage 9 — 게이트 전 전체 검증 + 브랜치 CI
- 목적: 공개 전에 로컬·CI 모두 green 임을 확인 (공개 뒤에 깨진 상태가 보이지 않게)
- 담당: runner(haiku) — 파일 쓰기 없음(로그만). push 는 orchestrator
- 병렬 가능: 아니오 · 선행: S8
- 입력: §2 명령
- 쓰기 범위:
  - 없음 (`.ai/tasks/T-20261027-public-launch/logs/s9-*.log` 기록만)
- 산출물: `logs/s9-local.log`, `logs/e2e.log`
- 검증: C1~C12, C22 전부 기대값 (C6 은 `logs/e2e.log`). 그 뒤 orchestrator 가 `git push -u origin ai/T-20261027-public-launch` → `gh run watch` 로 그 브랜치 CI 6 job success 확인 (Pages 워크플로우는 main 이 아니라 돌지 않음)
- 완료 조건: 로컬 전부 기대값 + 브랜치 CI success + PROGRESS 기록 + 커밋 `[…][s9] 게이트 전 검증 기록`
- 실패 시: 실패 항목을 해당 단계 implementer/test-writer 로 되돌림 (그 단계 쓰기 범위로). 합계 3회 초과 → BLOCKED

### Stage 10 — [사용자 승인 게이트] 이력 재작성 + 공개 전환
- 목적: 실제 샘플 산출물·내부 메모가 없는 이력으로 원격을 바꾸고 저장소를 공개한다
- 담당: orchestrator 직접 (되돌리기 어려운 원격 작업, 서브에이전트에 위임하지 않음)
- 병렬 가능: 아니오 · 선행: S9
- 입력: §4.5 전부
- 쓰기 범위:
  - 저장소 이력 전체 (모든 ref), 원격 `origin` 의 브랜치·태그, 저장소 visibility
  - 저장소 밖 `/Users/illi/hwp2md-backups/**`
- 절차:
  1. 승인 요청 전 준비(되돌릴 수 있음): `gh pr list -R ilyos-numon/hwp2md --state all --json number -q length` → `0` 이어야 함. `mkdir -p /Users/illi/hwp2md-backups && git bundle create /Users/illi/hwp2md-backups/hwp2md-pre-filter-20261027.bundle --all && git bundle verify …` → `is okay`; `git show-ref > /Users/illi/hwp2md-backups/pre-filter-refs.txt`; `git clone -q /Users/illi/hwp2md-backups/hwp2md-pre-filter-20261027.bundle /Users/illi/hwp2md-backups/pre-filter-clone` 후 그 안에서 `git tag` 에 `v0.1.0` 확인.
  2. **사용자에게 한 번 묻는다**: 지울 경로 2규칙(72+1 경로), 치환 3규칙, 백업 경로, 원격에서 지울 브랜치 목록, "force-push 와 공개 전환 승인?" — 승인 문구를 PROGRESS 에 기록. 승인 없으면 여기서 멈추고 STATE "다음 행동"에 이 절차 2번부터라고 적는다.
  3. 작업 트리 clean 확인 → `git checkout main && git merge --no-ff ai/T-20261027-public-launch -m "Merge ai/T-20261027-public-launch: 공개 출시 준비"`
  4. §4.5 filter 파일 생성 → filter-repo 실행 → origin 재등록
  5. 검사 V1~V4 + `uv run pytest tests/unit -q` failed 0 + C12. 하나라도 실패 → §4.5 복원, 규칙 보강 1회 재시도, 다시 실패면 BLOCKED (push 전)
  6. `git push --force origin main` → `git push --force origin --tags` → 원격 main 외 브랜치 삭제 → `git checkout -B ai/T-20261027-public-launch main` (이후 단계는 이 브랜치에서, push 는 main 으로 fast-forward)
  7. `gh repo edit ilyos-numon/hwp2md --visibility public --accept-visibility-change-consequences`
- 검증: C13, C14, C15
- 완료 조건: 검증 + PROGRESS(옛→새 main SHA, 새 v0.1.0 SHA) + 커밋 `[…][s10] 이력 정리·공개 전환 기록` (이 커밋은 새 이력 위)
- 실패 시: push 전이면 복원 후 BLOCKED. push 후 문제 발견(예: 금지 문자열 추가 발견) → 즉시 `gh repo edit --visibility private --accept-visibility-change-consequences` 후 BLOCKED

### Stage 11 — Pages 활성화·배포 확인
- 목적: 체험 URL 을 실제로 연다
- 담당: orchestrator(gh 명령) → runner(haiku, curl 확인)
- 병렬 가능: 아니오 · 선행: S10
- 입력: §4.1, §4.7
- 쓰기 범위:
  - 없음 (GitHub Pages 설정, `logs/s11-pages.log`)
- 절차: `gh api -X POST repos/ilyos-numon/hwp2md/pages -f build_type=workflow` (409 면 `-X PUT … -f build_type=workflow`) → `gh workflow run pages.yml -R ilyos-numon/hwp2md --ref main` → `gh run watch` (최대 15분)
- 검증: C16 → `200` 3줄
- 완료 조건: 검증 + 커밋 `[…][s11] Pages 배포 기록`
- 실패 시: 워크플로우 실패 → 로그 tail 40 을 보고 S7(워크플로우) 또는 S3(빌드) implementer 재호출, 합계 2회 → BLOCKED. 배포 직후 404 는 5분 간격 3회 재확인 후 실패 판정

> [보완 2026-10-27] 사용자 요청 "영어도 추가해서 코드 올리고 배포해줘" 로 S12~S16(영어 지원)을 넣고, 옛 S12(v0.1.1 릴리스)·S13(최종 E2E)·S14(리뷰)는 S18·S19·S20 으로 옮겼다. 옛 S12 에서 이미 한 일(main CI 40485010179 success, check_dist·twine 통과, 실제 Pages E2E 3 passed)은 S17 에서 새 커밋 기준으로 다시 한다. S12~S20 공통: 브랜치 `ai/T-20261027-public-launch`, 로컬 검증 시 ruff 는 `--no-cache`, grep 은 `command grep`, uv 는 `env -u VIRTUAL_ENV uv`.

### Stage 12 — 기존 브라우저 E2E 의 locale 을 ko-KR 로 고정
- 목적: i18n 기본 언어가 브라우저 언어를 따르게 되어도 기존 한국어 단언이 같은 조건에서 돌게 한다 (환경 고정, 단언 불변)
- 담당: test-writer(sonnet) (2회 실패 시 opus)
- 병렬 가능: 아니오 · 선행: S11
- 입력: §4.8 "기존 E2E 와 locale"
- 쓰기 범위:
  - `tests/e2e/test_web_ui.py`
  - `tests/e2e/test_web_extract.py`
  - `tests/e2e/test_web_v3.py`
  - `tests/e2e/test_design_v3.py`
  - `tests/e2e/test_pages_site.py`
- 산출물: 모든 `browser.new_context(` 호출에 `locale="ko-KR"` 추가 (v3 는 `kwargs.setdefault("locale", "ko-KR")`). 그 밖의 줄 변경 0
- 검증:
  - `for f in test_web_ui test_web_extract test_web_v3 test_design_v3 test_pages_site; do echo "$f $(command grep -c 'new_context(' tests/e2e/$f.py) $(command grep -c '"ko-KR"' tests/e2e/$f.py)"; done` → `3 3`, `2 2`, `1 1`, `1 1`, `1 1`
  - C26: `git diff $(cat .ai/tasks/T-20261027-public-launch/.base-s12) -U0 -- tests/e2e | command grep -cE '^[-+][^-+].*(assert|_TEXT|has-text|timeout|wait_for)'` → `0`; `git diff --stat $(cat .ai/tasks/T-20261027-public-launch/.base-s12) -- tests/e2e` → 위 5파일만
  - `uv run ruff check --no-cache tests && uv run ruff format --no-cache --check tests` → exit 0
  - `ILLY_SHOT_DIR=.ai/tasks/T-20261027-public-launch/screenshots uv run pytest tests/e2e/test_web_ui.py tests/e2e/test_web_extract.py tests/e2e/test_web_v3.py tests/e2e/test_design_v3.py tests/e2e/test_pages_site.py -q > .ai/tasks/T-20261027-public-launch/logs/s12-e2e.log 2>&1; echo exit=$?` → `exit=0`, failed 0 (i18n 전이므로 결과는 이전과 같아야 함)
- 완료 조건: 검증 + 커밋 `[…][s12] 기존 E2E 브라우저 locale ko-KR 고정` + tasks 5.1
- 실패 시: 5파일 `git restore` 후 재시도 최대 2회 → BLOCKED

### Stage 13 — i18n 코어 + 변환 화면 영어
- 목적: 변환 화면(`hwp2md serve` 의 `/`, 정적 `convert.html`)이 ko/en 으로 보이고 KO/EN 버튼으로 즉시 바뀐다
- 담당: implementer(opus)
- 병렬 가능: 아니오 · 선행: S12
- 입력: §4.2(정적 meta, 불변), §4.8 전부, `docs/feature-reference.md` §9.1·§9.7(읽기만), `src/hwp2md/web/static/pyodide-runner.js`(읽기만)
- 쓰기 범위:
  - `src/hwp2md/web/static/js/i18n.js` (새 파일)
  - `src/hwp2md/web/static/index.html`
  - `src/hwp2md/web/static/js/app.js`
  - `src/hwp2md/web/static/js/theme.js`
  - `src/hwp2md/web/static/css/base.css` (끝에 `.lang-toggle` 규칙 10줄 이하만)
- 산출물: §4.8 API·결정 로직·DOM 표기·고정 문구 표(변환 화면·JS 키 전부). index.html 의 사용자 노출 한국어(텍스트·aria-label·`<title>`) 전부에 `data-i18n*` 또는 app.js 관리. `about.html` 은 이 단계에서 건드리지 않는다 (소개 화면 theme.js aria-label 은 `t()` 의 KO 값으로 동작)
- 검증:
  - `node --check` 4파일(i18n.js, app.js, theme.js, pyodide-runner.js) → exit 0
  - `git diff $(cat .ai/tasks/T-20261027-public-launch/.base-s13) -- src/hwp2md/web/static/css/base.css | command grep -cE '^-[^-]'` → `0` (추가만)
  - serve 회귀(ko-KR 고정): `uv run pytest tests/e2e/test_web_ui.py tests/e2e/test_web_v3.py tests/e2e/test_web_extract.py tests/e2e/test_web_api.py tests/e2e/test_design_v3.py -q` → failed 0
  - `uv run pytest tests/unit -q` → failed 0; C1, C2 (빌드 결과에 `static/js/i18n.js` 존재: `ls dist-pages/static/js/i18n.js`)
  - 영어 스모크(임시, 파일 남기지 않음): runner 가 `uv run python - <<'EOF'` 로 Playwright locale `en-US` 에서 `http://localhost:<serve 포트>/` 를 열어 `document.documentElement.lang`, `#mode-status` 글자, `Hwp2mdI18n.missing()` 출력 → `en`, `Server mode`, `[]`
- 완료 조건: 검증 + C12 + 커밋 `[…][s13] i18n 코어·변환 화면 영어` + tasks 5.2
- 실패 시: 한국어 회귀(기존 E2E 실패)를 단언 변경 없이 못 고침 → 5파일 `git restore` 후 재시도 최대 2회 → BLOCKED

### Stage 14 — 소개 페이지 영어
- 목적: 소개 페이지(`/about`, 정적 `index.html`)가 ko/en 으로 보이고 KO/EN 버튼(새로고침 방식)이 동작한다
- 담당: implementer(opus)
- 병렬 가능: 아니오 · 선행: S13 (i18n.js API 사용)
- 입력: §4.8, `src/hwp2md/web/static/js/i18n.js`(읽기만), `src/hwp2md/web/static/js/landing.js`·`effects.js`(읽기만 — 사용자 문자열 없음 확인됨)
- 쓰기 범위:
  - `src/hwp2md/web/static/about.html`
  - `src/hwp2md/web/static/js/i18n-about.js` (새 파일)
  - `src/hwp2md/web/static/js/landing.js` (번역된 글자를 나누는 순서 문제가 실제로 생길 때만. 변경하면 PROGRESS 에 이유 1줄)
- 산출물: about.html 의 사용자 노출 한국어(§4.8 "번역하지 않는 것" 제외) 전부에 `data-i18n*`, `i18n-about.js` 영어 사전, 헤더 `.lang-toggle`, `body[data-i18n-reload]`, 스크립트 순서
- 검증:
  - `node --check src/hwp2md/web/static/js/i18n-about.js src/hwp2md/web/static/js/landing.js` → exit 0 (파일마다 실행)
  - `uv run pytest tests/e2e/test_design_v3.py tests/e2e/test_web_v3.py -q` → failed 0 (ko 회귀)
  - C1, C2; `uv run pytest tests/unit -q` failed 0
  - 영어 스모크(임시): locale `en-US` 로 `/about` → `html.lang == "en"`, `Hwp2mdI18n.missing()` = `[]`, `a:has-text("Open converter")` 1개 이상
- 완료 조건: 검증 + C12 + 커밋 `[…][s14] 소개 페이지 영어` + tasks 5.3
- 실패 시: 재시도 최대 2회 → BLOCKED. 애니메이션이 en 에서 깨지면(빈 제목 등) landing.js 를 쓰기 범위 안에서 1회 수정, 그래도 안 되면 BLOCKED

### Stage 15 — i18n E2E 작성·실행
- 목적: 영어 화면의 성공·실패 경로·전환·저장·정적 사이트를 자동 검증하고 영어 스크린샷을 남긴다
- 담당: test-writer(sonnet) 작성 → runner(haiku) 실행 (test-writer 2회 실패 시 opus)
- 병렬 가능: 아니오 · 선행: S14
- 입력: §4.8 "새 E2E", `tests/e2e/test_web_ui.py`·`test_design_v3.py`(route 대체 패턴)·`test_pages_site.py`(정적 서버 픽스처), `tests/e2e/conftest.py`, `tests/synth_hwpx.py`
- 쓰기 범위:
  - `tests/e2e/test_i18n.py` (새 파일)
- 산출물: 케이스 8개 이상, 스크린샷 4장(`i18n-en-convert-done.png`, `i18n-en-error.png`, `i18n-en-about.png`, `i18n-pages-en-done.png`)
- 검증: C25 `ILLY_SHOT_DIR=.ai/tasks/T-20261027-public-launch/screenshots uv run pytest tests/e2e/test_i18n.py -q > .ai/tasks/T-20261027-public-launch/logs/s15-e2e.log 2>&1; echo exit=$?` → `exit=0`, passed ≥ 8, failed 0, skipped 0; 스크린샷 4장 존재; C4
- 완료 조건: 검증 + 커밋 `[…][s15] i18n E2E` + tasks 5.4
- 실패 시: §e2e-standard 실패 분류 — 테스트 오류는 test-writer, 구현 오류는 S13/S14 implementer 에 그 단계 쓰기 범위로 재호출. 합계 재시도 3회 초과 → BLOCKED

### Stage 16 — 영어 문서·변경 기록
- 목적: GitHub 방문자가 영어 README 를 읽을 수 있고, 변경·계약·결정이 기록된다
- 담당: implementer(opus)
- 병렬 가능: 아니오 · 선행: S15
- 입력: §4.6(README 절대 URL·배지), §4.8 "문서", 현재 `README.md`, `CHANGELOG.md`, `docs/feature-reference.md` §9, `docs/decisions.md`
- 쓰기 범위:
  - `README.en.md` (새 파일)
  - `README.md` (배지 블록 다음 English 링크 1줄만)
  - `CHANGELOG.md` (`[0.1.1]` Added 1줄만)
  - `docs/feature-reference.md` (§9 끝 `### 9.9 언어 (i18n)` 절 추가만)
  - `docs/decisions.md` (끝에 항목 1개)
- 산출물: §4.8 "문서"
- 검증:
  - C10 (README.md) → `relative=0`; C28 (README.en.md) → `relative=0`, 두 파일 `^## ` 개수 같음, `static.pepy.tech/badge/hwp2markdown` 1
  - `command grep -c 'README.en.md' README.md` → `1`; `git diff $(cat .ai/tasks/T-20261027-public-launch/.base-s16) --numstat -- README.md CHANGELOG.md` → README `1 0`, CHANGELOG `1 0`
  - C8, C9 (README.md 변경이 long description 에 반영돼도 twine PASSED); C12
- 완료 조건: 검증 + 커밋 `[…][s16] README 영어판·CHANGELOG·i18n 문서` + tasks 5.5
- 실패 시: 재시도 최대 2회 → BLOCKED

### Stage 17 — 재검증 + main push + Pages 재배포 확인
- 목적: 영어 지원을 공개 main·Pages 에 올리고 실제 사이트에서 확인한다
- 담당: runner(haiku) 로컬 검증 → orchestrator push·gh 확인 → runner(haiku) 실제 사이트 확인
- 병렬 가능: 아니오 · 선행: S16
- 입력: §2 명령
- 쓰기 범위:
  - 없음 (`logs/s17-local.log`, `logs/e2e.log`, `logs/s17-live.log`, `screenshots/`)
- 절차: (1) runner: C1~C12, C22, C24, C25 → `logs/s17-local.log`, C6 → `logs/e2e.log`. (2) orchestrator: 작업 트리 clean 확인 → `git checkout main && git merge --ff-only ai/T-20261027-public-launch && git push origin main && git checkout ai/T-20261027-public-launch` (force 아님) → `gh run watch` 로 그 커밋의 `CI`·`Pages` 둘 다 success (최대 20분). (3) runner: C29, C30, 그리고 `HWP2MD_PAGES_URL=https://ilyos-numon.github.io/hwp2md/ ILLY_SHOT_DIR=… uv run pytest tests/e2e/test_pages_site.py -q` → 3 passed
- 검증: 로컬 전부 기대값, 원격 `git ls-remote origin refs/heads/main | cut -f1` = `git rev-parse main`, C29, C30
- 완료 조건: 검증 + PROGRESS(새 main SHA, run id) + 커밋 `[…][s17] 영어 지원 배포 기록` (이 커밋도 S18 전에 main 으로 ff push) + tasks 6.1
- 실패 시: 로컬 실패 → 해당 단계(S12~S16) 담당에게 그 쓰기 범위로 되돌림, 합계 3회 → BLOCKED. `--ff-only` 실패(main 이 앞섬) → BLOCKED (force 금지). Pages 배포 직후 옛 파일 → 5분 간격 3회 재확인 후 실패 판정

### Stage 18 — v0.1.1 태그 (사용자 실행)
- 목적: 영어 지원·메타데이터 반영본을 PyPI 에 게시
- 담당: 사용자(태그 push — 세션 권한이 태그 push 를 막음) → orchestrator 안내·확인 → runner(haiku) 확인
- 병렬 가능: 아니오 · 선행: S17
- 입력: `docs/releasing.md` 릴리스 순서
- 쓰기 범위:
  - 없음 (태그 `v0.1.1`, `logs/s18-release.log`)
- 절차: orchestrator 가 main CI 최신 success 와 `uv build --out-dir dist && uvx --from 'twine>=6.1' twine check --strict dist/* && uv run python scripts/check_dist.py dist --tag v0.1.1` 통과를 확인한 뒤, 사용자에게 실행할 명령 2줄을 보여 주고 BLOCKED(사용자 실행 대기)로 기록: `cd /Users/illi/illy-projects/hwp2md && git tag -a v0.1.1 -m "v0.1.1" main && git push origin v0.1.1`. 사용자 실행 뒤 `gh run watch` Release
- 검증: C18, C19, C21(Release headBranch `v0.1.1`), `git rev-parse 'v0.1.1^{commit}'` = S17 의 main SHA
- 완료 조건: 검증 + 커밋 `[…][s18] v0.1.1 릴리스 기록` + tasks 6.2
- 실패 시: §3 S12 규칙(Release publish 실패 → 재실행 1회 → BLOCKED), `docs/releasing.md` "실패 대응". 태그가 다른 커밋에 찍힘 → 사용자에게 알리고 BLOCKED (태그 삭제·재생성은 사용자 결정)

### Stage 19 — 최종 E2E (로컬 전체 + 실제 Pages)
- 목적: 공개·릴리스 상태에서 사용자 관점 검증. E2E 는 마지막에 다시 돈다
- 담당: runner(haiku) (2회 실패 시 sonnet)
- 병렬 가능: 아니오 · 선행: S18
- 입력: C6, C17, C25, C30
- 쓰기 범위:
  - 없음 (`logs/e2e.log`, `logs/s19-live.log`, `screenshots/`)
- 검증: C6 (failed 0, `test_i18n.py` 포함), C17 — 실제 명령은 `HWP2MD_PAGES_URL=https://ilyos-numon.github.io/hwp2md/ ILLY_SHOT_DIR=… uv run pytest tests/e2e/test_pages_site.py -q` → 3 passed (S4 보완에 따라 `-k live` 케이스는 없음), C30, C20, C21
- 완료 조건: 검증 + 커밋 `[…][s19] 최종 E2E 기록` + tasks 6.3
- 실패 시: §e2e-standard 실패 분류로 S2·S3·S4·S12~S15 담당에게 되돌림, 합계 3회 → BLOCKED

### Stage 20 — 리뷰·결과 기록
- 담당: reviewer(sonnet) → scribe(haiku)
- 병렬 가능: 아니오 · 선행: S19
- 입력: `.base-s2` 이후 diff(새 이력 기준 `git diff <S10 직후 main>~1..HEAD` 와 S10 PROGRESS), 스크린샷 C7·C17 4장 + C27 영어 4장(+ `i18n-pages-live-en-done.png`)을 reviewer 가 직접 Read, §2 표
- 쓰기 범위:
  - `.ai/tasks/T-20261027-public-launch/RESULT.md`
- 산출물: RESULT.md (C1~C30 대조표, 스크린샷 판정, 남은 위험: GitHub 의 옛 SHA 캐시, 서버 라벨 한국어 표시)
- 검증: RESULT 에 C1~C30 행 30개, 각 행 근거(명령 출력·로그 경로)
- 완료 조건: 커밋 `[…][done] 공개 출시` + tasks 6.4 + openspec validate → archive (orchestrator)

## 6. 병렬 실행 맵
```
S1 → S2 → S3 → S4 → S5 → S6 → S7 → S8 → S9 ══[사용자 승인]══> S10 → S11
  → [보완] S12 → S13 → S14 → S15 → S16 → S17 ══[사용자 태그 push]══> S18 → S19 → S20
```
- [보완] S12~S20 도 전부 순차, worktree 격리 불필요. 이유: S13·S14 가 같은 `i18n.js` API 를 쓰고(S14 는 읽기만), S12·S15 는 S13·S14 결과를 검증하며, S13·S14 의 `index.html`/`about.html` 은 서로 다른 파일이지만 둘 다 `base.css` 의 `.lang-toggle` 규칙에 기대므로 순차가 안전하다.
- 전부 순차. 병렬 묶음 없음 (worktree 격리 불필요). 이유: 단계마다 10~20분 규모라 순차가 충돌 비용보다 싸고, S5·S7 은 orchestrator 전용 파일 단계라 병렬 금지, S2→S3→S4 는 meta 계약으로 이어진다.
- 게이트 전(S1~S9)은 모두 로컬·비공개 브랜치에서 되돌릴 수 있는 일. 게이트 뒤(S10~S13)는 원격·공개·PyPI.

## 7. 사용자에게 확인받을 것 (플랜 승인 시 한 번에 — 모두 기본값으로 자동 진행)
- [ ] Q1. 공개 이력에 `.ai/`(작업 기록)·`openspec/`·`design/` 을 남길까?
  - 기본값: 남긴다 (AI 워크플로우 포트폴리오 가치). 실제 샘플 산출물 2규칙과 내부 메모만 지운다.
- [ ] Q2. 이력 속 루프백 IP 리터럴과 이를 닮은 버전 문자열(lxml 4단 버전 1건)을 치환할까?
  - 기본값: 치환한다 (`localhost`, 3단 버전). 익명화 금지 패턴 0건을 만든다.
- [ ] Q3. 테스트 코드·과거 기록에 남은 실제 샘플 파일명(공개 양식 이름 5개, 내용 없음)을 지울까?
  - 기본값: 남긴다 (파일 내용이 아니고 기관명이 없음). 기관 식별 정보가 든 `inventory.md` 는 지운다.
- [ ] Q4. 원격의 이전 작업 브랜치(`ai/T-20261027-pypi-release` 등)는?
  - 기본값: 삭제한다 (옛 이력을 붙잡으므로). 원격에는 main 과 태그만 남긴다.
- [ ] Q5. v0.1.1 PyPI 게시를 게이트 없이 S12 에서 진행할까?
  - 기본값: 진행 (릴리스 방식 승인됨, 버전 bump 만).
- [ ] Q6. 과거 기록 속 로컬 절대경로(`/Users/<계정>/…`)를 치환할까?
  - 기본값: 치환하지 않는다 (본인 계정명, 금지 패턴 아님).
- [ ] Q7. 체험 사이트 첫 화면은?
  - 기본값: 소개 페이지(`index.html`), 변환 화면은 `convert.html`.
- [ ] Q8. 홍보 초안을 공개 저장소 `docs/launch/` 에 둘까?
  - 기본값: 둔다 (요청된 위치).
- [ ] Q9. [보완] 영어 화면에서 서버가 주는 건너뜀 라벨(`skipped[].label`, 예 머리말·꼬리말)은?
  - 기본값: 라벨은 한국어 그대로, 접두(`Not converted: `)·개수 서식(`(n)`)만 번역한다. API·엔진 불변(OUT).
- [ ] Q10. [보완] PyPI 페이지(pyproject readme)도 영어로 바꿀까?
  - 기본값: 바꾸지 않는다. README.md(한국어 + 기존 `## English` 절) 그대로, GitHub 에 README.en.md 를 두고 README.md 상단에서 링크한다.
- [ ] Q11. [보완] 바닥글의 한컴 공개 문서 참고 고지를 영어 화면에서 어떻게 보일까?
  - 기본값: 영어 번역 뒤에 한국어 원문 문장을 괄호로 그대로 붙인다(원문 고지 문장 유지).
- [ ] Q12. [보완] 처음 방문자의 기본 언어는?
  - 기본값: `?lang=` → 저장값 → 브라우저 언어가 `ko*` 면 한국어, 그 밖은 영어. 기존 E2E 는 브라우저 언어를 `ko-KR` 로 고정해 한국어 단언을 유지한다(§4.8).
- 게이트(S10 절차 2)는 질문이 아니라 필수 승인 지점이다: "force-push 와 공개 전환 승인?"

## 8. 리스크
| 리스크 | 가능성 | 대응 |
|--------|--------|------|
| GitHub 이 force-push 뒤에도 옛 커밋을 SHA 직접 주소로 한동안 보여 줌 | 중 | 비공개 기간 SHA 비노출, PR 0건 확인. 필요 시 사용자가 GitHub 지원에 캐시 삭제 요청(§RESULT 에 안내) |
| filter-repo 가 v0.1.0 태그 객체를 바꿔 PyPI 와 내용 불일치 | 낮 | V4 로 배포물 경로 객체 해시 대조, 다르면 push 금지·복원 |
| Pyodide CDN(jsDelivr) 장애·지연으로 E2E·체험 실패 | 중 | 240 s 대기, 실패 경로 E2E 로 오류 표시 보장. 2회 연속 timeout 은 BLOCKED |
| 정적 모드 수정이 serve 화면을 깨뜨림 | 낮 | meta 없을 때 기존 경로 그대로(§4.2), S2 에서 serve E2E 4파일 회귀 실행 |
| pepy 배지가 첫날 0 또는 미표시 | 중 | 허용 (외부 서비스 집계 지연) |
| PyPI 그림이 공개 전환 전 깨짐 | 낮 | 릴리스는 공개 뒤(S12) |
| filter-repo 가 origin remote 를 지움 | 높 | §4.5 에 재등록 명령 |
| gh 토큰 workflow scope 부족으로 `.github/workflows/pages.yml` push 거절 | 낮 | BLOCKED → 사용자 `gh auth refresh -s workflow` (releasing.md U4) |
| 이력 재작성 뒤 로컬 다른 클론·작업 브랜치와 어긋남 | 중 | 로컬 ai/* 브랜치도 함께 재작성됨. 백업 bundle 로 언제든 이전 상태 확인 |
| [보완] CI(ubuntu, en-US)에서 기존 E2E 가 영어로 떠 한국어 단언 실패 | 높(고정 안 하면) | S12 에서 모든 `new_context` 에 `locale="ko-KR"`, S12 를 i18n 구현(S13) 앞에 둠 |
| [보완] 소개 페이지 SplitText·ScrambleText 가 번역 전 글자를 나눔 | 중 | i18n 스크립트를 gsap 앞에 두고 로드 즉시 동기 적용, 소개 페이지 전환은 새로고침 |
| [보완] 영어 사용자가 첫 화면에서 한국어가 잠깐 보임(i18n.js 가 body 끝에서 적용) | 낮 | 허용. 소개 페이지는 `.js` 클래스로 모션 전 내용이 숨겨져 있어 거의 보이지 않음 |
| [보완] 사전 키 누락으로 영어 화면에 한국어가 섞임 | 중 | `Hwp2mdI18n.missing()` = `[]` 와 화면 틀 한글 0 을 E2E 로 검사 |
| [보완] 세션 권한이 태그 push 를 막음 | 확정 | S18 은 사용자 실행 단계 |

## 9. 예상 비용
- 예상 단계 수: 14 · 서브에이전트 호출: 약 14회 (implementer opus 6, test-writer sonnet 1, runner haiku 5, reviewer sonnet 1, scribe haiku 1) + 재시도 여유 3회
- [보완] 단계 수 20 (새 S12~S16 5개 + 옮긴 S17~S20). 남은 호출 약 12회: test-writer sonnet 2(S12, S15), implementer opus 3(S13, S14, S16), runner haiku 5(S13·S14 스모크 포함, S15, S17, S18, S19), reviewer sonnet 1, scribe haiku 1 + 재시도 여유 3회. 추가 대기: Pyodide E2E 2회(약 6분), CI·Pages 1회(약 10분), 사용자 태그 push 1회
- 주 모델 비율: opus 약 45% / sonnet 15% / haiku 40% (호출 수 기준)
- 대기 시간: Pyodide E2E 로컬 2~3회 × 약 3분, CI·Pages·Release Actions 대기 합계 약 30~40분, 사용자 게이트 1회
