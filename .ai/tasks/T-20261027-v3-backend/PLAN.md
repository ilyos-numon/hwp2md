# PLAN — T-20261027-v3-backend V3 프론트엔드를 실제 백엔드에 연결

> 작성: opus · 2026-10-27 · 프로젝트: hwp2md
> 상태: DRAFT → APPROVED → DONE  (현재: APPROVED)
> 이 플랜은 sonnet 등급 모델이 추가 질문 없이 그대로 실행할 수 있을 만큼 구체적이어야 한다.

## 0. 한 줄 목표
사용자는 `hwp2md serve` 로 연 V3 변환 화면(`/`)과 소개 페이지(`/about`)에서, 인터넷 없이(서버 모드) 실제 HWP·HWPX·HWPML 파일을 변환·미리보기·zip 다운로드할 수 있다.

### 0.1 OpenSpec 연동
- change: `openspec/changes/v3-backend/` · 검증: `source ~/.nvm/nvm.sh >/dev/null 2>&1 && openspec validate v3-backend` (작성 시점 결과: `Change 'v3-backend' is valid`)
- tasks.md 체크는 orchestrator 가 단계 DONE 커밋에서 한다. tasks.md 의 모든 `- [ ] N.M` 이 아래 표에 정확히 한 행.

| tasks.md 항목 | 내용(요약) | Stage |
|---------------|-----------|-------|
| 1.1 | GSAP 3.13.0 스크립트 4개 + 라이선스 안내 | S1 |
| 1.2 | 글꼴 woff2 + OFL + fonts.css (실패 시 시스템 글꼴 경로) | S1 |
| 1.3 | marked 라이선스 + vendor/README.md (URL·버전·SHA-256) | S1 |
| 2.1 | base.css·app.css·theme.js 이식 | S2 |
| 2.2 | static/index.html → V3 변환 화면 | S2 |
| 2.3 | static/js/app.js 실제 MODES 연결, 이전 app.js·style.css 삭제 | S2 |
| 3.1 | about.html·landing.css·effects.js·landing.js 이식 | S3 |
| 3.2 | app.py `GET /about` + 단위 테스트 | S3 |
| 4.1 | README·feature-reference §9·decisions·NOTICE·design/v3/README | S4 |
| 5.1 | tests/e2e/test_web_v3.py 작성 | S5 |
| 5.2 | 전체 게이트 실행·로그 | S6 |
| 5.3 | 리뷰·RESULT | S7 |

## 1. 범위
### 포함 (IN)
- `src/hwp2md/web/static/vendor/gsap/` — `gsap.min.js`, `ScrollTrigger.min.js`, `SplitText.min.js`, `ScrambleTextPlugin.min.js`, `LICENSE.md`
- `src/hwp2md/web/static/vendor/fonts/` — `PretendardVariable.woff2`, `JetBrainsMono-Regular.woff2`, `JetBrainsMono-Medium.woff2`, `JetBrainsMono-SemiBold.woff2`, `fonts.css`, `OFL-Pretendard.txt`, `OFL-JetBrainsMono.txt`
- `src/hwp2md/web/static/vendor/marked.LICENSE.md`, `src/hwp2md/web/static/vendor/README.md`
- 변환 화면: `static/index.html`(덮어쓰기), `static/js/app.js`, `static/js/theme.js`, `static/css/base.css`, `static/css/app.css` (새로), `static/app.js`·`static/style.css` 삭제
- 소개 페이지: `static/about.html`, `static/css/landing.css`, `static/js/effects.js`, `static/js/landing.js`
- `src/hwp2md/web/app.py` 에 `GET /about` 라우트 1개, `tests/unit/test_web_app.py` 에 테스트 추가
- 문서: `README.md`(②웹 미리보기 절), `docs/feature-reference.md`(§9 파일 표·DOM 계약 변경분), `docs/decisions.md`, `NOTICE`, `design/v3/README.md`("백엔드에 연결할 때" → 연결 완료 표시)
- 새 E2E `tests/e2e/test_web_v3.py`

### 제외 (OUT) — 절대 건드리지 않는다
- `design/v3/**` 의 HTML·CSS·JS (시안과 데모 엔진은 그대로 둔다. `test_design_v3.py` 가 계속 이를 검사한다). 예외: `design/v3/README.md` 는 S4 에서만 수정
- `src/hwp2md/web/static/pyodide-runner.js` (Pyodide 는 계속 CDN, 브라우저 모드 동작 불변)
- `src/hwp2md/web/static/vendor/marked.min.js` (이미 12.0.2, 교체하지 않음)
- 변환 엔진(`src/hwp2md/` 의 web 외 모듈), `memory.py`, API 응답 형식
- 기존 E2E 파일 `tests/e2e/test_web_ui.py`, `test_web_extract.py`, `test_web_api.py`, `test_design_v3.py`, `conftest.py` — 수정 없이 통과해야 한다
- Docker 관련 일체 (프록시로 pull 불가)
- 글꼴 서브셋 생성, 새 변환 기능, 새 UI 기능(시안에 없는 것)

### 건드리면 안 되는 파일/디렉토리
- `src/hwp2md/cli.py`, `pyproject.toml`, `uv.lock`, `.gitignore`, `CLAUDE.md`, `.ai/STATE.md`, 이 `PLAN.md` (orchestrator 전용)
- `doc/my_info/**`(워크스페이스 루트, 읽기 전용)
- `openspec/specs/**` (archive 시 orchestrator 가 반영)

## 2. 성공 기준 (전부 만족해야 DONE)
| # | 기준 | 검증 명령 | 기대 결과 |
|---|------|-----------|-----------|
| C1 | `/`·`/about` 응답 | `uv run pytest tests/unit/test_web_app.py -q` | 실패 0 (새 `test_about_html` 포함) |
| C2 | 기존 웹 E2E 무수정 통과 | `uv run pytest tests/e2e/test_web_ui.py tests/e2e/test_web_extract.py tests/e2e/test_web_api.py tests/e2e/test_design_v3.py -q` | 실패 0, 그리고 `git diff --stat main -- tests/e2e/test_web_ui.py tests/e2e/test_web_extract.py tests/e2e/test_web_api.py tests/e2e/test_design_v3.py tests/e2e/conftest.py` 출력 없음 |
| C3 | 새 V3 E2E | `uv run pytest tests/e2e/test_web_v3.py -q` | 실패 0, skip 0 (글꼴 실패 경로일 때 글꼴 단언 1개만 분기, skip 아님) |
| C4 | 전체 E2E | `uv run pytest tests/e2e -q` | 실패 0 |
| C5 | 단위 회귀 | `uv run pytest tests/unit -q` | 실패 0 |
| C6 | 린트·타입 | `uv run ruff check src tests && uv run ruff format --check src tests && uv run mypy src` | 종료 코드 0 |
| C7 | CDN·데모 참조 없음 | `grep -rnE "cdn\.jsdelivr|googleapis|gstatic|Hwp2mdDemo|demo-dock|demo-sample|demo-engine" src/hwp2md/web/static --include=*.html --include=*.css; grep -nE "Hwp2mdDemo|demo-|autoAlpha" src/hwp2md/web/static/js/app.js` | 두 명령 모두 출력 없음 (pyodide-runner.js 는 대상 밖) |
| C8 | 이전 UI 삭제 | `ls src/hwp2md/web/static/app.js src/hwp2md/web/static/style.css` | 두 파일 모두 `No such file` |
| C9 | 라이선스 동봉 | `test -s src/hwp2md/web/static/vendor/gsap/LICENSE.md && test -s src/hwp2md/web/static/vendor/marked.LICENSE.md && test -s src/hwp2md/web/static/vendor/README.md && echo ok` | `ok` (글꼴 동봉 시 `OFL-Pretendard.txt`·`OFL-JetBrainsMono.txt` 도 `test -s` 통과) |
| C10 | GSAP 버전 | `head -c 200 src/hwp2md/web/static/vendor/gsap/gsap.min.js` | `3.13.0` 문자열 포함 |
| C11 | wheel 에 정적 자원 포함 | `uv build --wheel -o .ai/tasks/T-20261027-v3-backend/dist && unzip -l .ai/tasks/T-20261027-v3-backend/dist/*.whl \| grep -cE "web/static/(about.html|js/app.js|vendor/gsap/gsap.min.js)"` | `3` |
| C12 | 익명화 | `cd /Users/illi/illy-projects && scripts/sanitize-check.sh hwp2md` | 종료 코드 0 |
| C13 | 화면 확인 | 스크린샷 `.ai/tasks/T-20261027-v3-backend/screenshots/v3-*.png` (§5 S5 목록 6장) | reviewer 가 직접 보고: 변환 완료 화면에 표·그림 미리보기와 Markdown 원문이 나란히 보임, 오류 화면에 빨간 안내와 닫기 버튼, 소개 페이지 히어로·#limits 가 글꼴 깨짐 없이 보임, 다크 테마 색 반전, 좁은 화면에서 탭 1개만 보임 |
| C14 | OpenSpec | `source ~/.nvm/nvm.sh >/dev/null 2>&1 && openspec validate v3-backend` | `Change 'v3-backend' is valid` |

## 3. 실패 기준 (하나라도 해당하면 즉시 중단 → BLOCKED 기록)
- 같은 단계 재시도 3회 초과
- 같은 오류로 수정 2회 실패
- 단계 하나 도구 호출 40회 초과 → PARTIAL 기록 후 orchestrator 반환 (60회 절대 상한)
- 기존 E2E 파일(§1 OUT) 수정 없이는 C2 를 통과할 수 없음 → BLOCKED (테스트를 고치거나 skip 하지 않는다)
- GSAP 다운로드가 3회(서로 다른 시도) 실패 → BLOCKED (GSAP 없이 소개 페이지는 정적 표시만 되므로 사용자 결정 필요)
- 글꼴 다운로드 2회 실패 → BLOCKED 아님. design.md 결정 6 의 시스템 글꼴 실패 경로로 진행하고 PROGRESS 에 `FONT_FALLBACK` 기록
- 다운로드한 파일 SHA-256 이 같은 URL 재다운로드와 다르거나, `.js` 첫 줄에 기대 버전 문자열이 없음 → 그 파일 폐기 후 재시도 (위 상한 적용)
- 내려받기 전체가 1GB 를 넘거나 계정·키가 필요함 → BLOCKED

## 4. 인터페이스 계약 (모든 단계 프롬프트에 그대로 넣는다)

```text
# 정적 배치 (HTML 안 참조는 모두 절대경로)
/static/vendor/fonts/fonts.css        @font-face: "Pretendard Variable"(100 900), "JetBrains Mono"(400/500/600). 실패 경로면 주석 1줄만
/static/vendor/marked.min.js          (기존, marked 12.0.2)
/static/vendor/gsap/gsap.min.js | ScrollTrigger.min.js | SplitText.min.js | ScrambleTextPlugin.min.js
/static/css/base.css  /static/css/app.css  /static/css/landing.css
/static/js/theme.js   /static/js/app.js    /static/js/effects.js   /static/js/landing.js
/static/pyodide-runner.js             (기존, 변경 금지)

# 페이지
GET /       -> static/index.html (V3 변환 화면)   text/html; charset=utf-8
GET /about  -> static/about.html (V3 소개 페이지) text/html; charset=utf-8
링크: 변환 화면 brand·"서비스 소개" -> /about ; 소개 페이지 brand -> /about, "변환 도구 열기"·"변환 도구" -> /

# 변환 화면 <head>/<body> 끝 스크립트 순서
<link fonts.css> <link base.css> <link app.css>
<script marked.min.js> <script gsap.min.js> <script pyodide-runner.js> <script theme.js> <script js/app.js>

# 소개 페이지 스크립트 순서
<link fonts.css> <link base.css> <link landing.css>
<script gsap.min.js> <script ScrollTrigger.min.js> <script SplitText.min.js> <script ScrambleTextPlugin.min.js>
<script theme.js> <script effects.js> <script landing.js>
```

```js
// static/js/app.js — MODES 는 현재 static/app.js(삭제 전) 111~146행과 readErrorBody(100~109행)를 그대로 옮긴다
// MODES[name].convert(file: File): Promise<{status: number, body: object}>
// MODES[name].zip(file: File): Promise<Blob>   // 실패 시 {code, message} 를 가진 Error 를 throw
const MODES = { server: {/* fetch POST /api/convert?name=, /api/zip?name= */}, browser: {/* window.Hwp2mdBrowser.convert/zip */} };
// 모드 전환: window.Hwp2mdBrowser 가 없으면 setModeStatus("error", ...) 후 스위치 끔. 있으면 await window.Hwp2mdBrowser.load()
const LIMITS_DOC = "/about#limits";
window.Hwp2mdApp = { MODES, els, setMode(name), get mode(), handleFile }; // 유지
```

DOM·문구 계약 (기존 E2E 가 직접 쓴다. 바꾸지 않는다):
- id: `#drop-zone #file-input #mode-toggle #mode-status #file-name #result-meta #download #error #error-text #error-close #skipped #preview #raw #copy`
- `body[data-state]` ∈ `idle|converting|done|error`, `#mode-status[data-state]` ∈ `server|loading|browser|error`
- 문구: `서버 모드`, `브라우저 모드 준비 중…`, `브라우저 모드: 파일이 서버로 전송되지 않습니다`, `브라우저 모드를 불러오지 못했습니다: `, ERROR_TEXT 6종(시안 `design/v3/js/app.js` 7~14행 그대로), `#skipped` 글자 접두 `변환하지 못한 요소: `, `#result-meta` 형식 `단락 N개 · 표 N개 · 제목 N개 · 이미지 N개`
- `#raw` 의 `textContent` == 응답 `markdown` (줄마다 `span.l`)

모션 계약 (변환 화면 `static/js/app.js` 한정):
- `autoAlpha`·`visibility` 를 쓰지 않는다. 등장 모션은 `opacity`·`x`·`y` 만.
- `renderCounts` 는 `<b>` 의 `textContent` 에 최종 숫자를 먼저 넣는다 (숫자 증가 tween 없음).
- `setState("done")` 과 `renderResult` 는 같은 동기 구간에서 끝난다 (사이에 await 없음).
- `prefers-reduced-motion: reduce` 이면 gsap 호출 생략.

## 5. 단계 (Stage)
모든 Bash 는 `cd /Users/illi/illy-projects/hwp2md && ` 로 시작한다. macOS: `timeout` 명령·zsh `PIPESTATUS` 를 검증에 쓰지 않는다. 단계 시작 시 orchestrator 가 `git rev-parse HEAD > .ai/tasks/T-20261027-v3-backend/.base-s<n>` 를 저장한다.

### Stage 1 — vendor 자원 내려받기와 라이선스 동봉
- 목적: GSAP·글꼴을 `static/vendor/` 에 두고 모든 동봉 자원의 라이선스·출처를 남긴다.
- 담당: implementer(opus)
- 병렬 가능: 아니오 · 선행: 없음
- 입력: design.md 결정 5·6, §4 정적 배치. 다운로드 URL:
  - `https://cdn.jsdelivr.net/npm/gsap@3.13.0/dist/{gsap,ScrollTrigger,SplitText,ScrambleTextPlugin}.min.js`
  - GSAP 라이선스 원문 URL `https://gsap.com/standard-license` (LICENSE.md 에 이름·버전·URL·"무료 표준 라이선스, 재배포 시 이 안내 유지" 요약을 적는다. npm 패키지 `gsap@3.13.0/package.json` 의 `license` 필드 값을 그대로 인용)
  - `https://cdn.jsdelivr.net/npm/pretendard@1.3.9/dist/web/variable/woff2/PretendardVariable.woff2`, 라이선스 `https://cdn.jsdelivr.net/npm/pretendard@1.3.9/LICENSE`
  - `https://cdn.jsdelivr.net/gh/JetBrains/JetBrainsMono@v2.304/fonts/webfonts/JetBrainsMono-{Regular,Medium,SemiBold}.woff2`, 라이선스 `https://cdn.jsdelivr.net/gh/JetBrains/JetBrainsMono@v2.304/OFL.txt`
  - marked MIT: `https://cdn.jsdelivr.net/npm/marked@12.0.2/LICENSE.md`
- 절차: 먼저 빈 스크래치 디렉토리 `.ai/tasks/T-20261027-v3-backend/dl/` 에 `curl -fsSL --retry 2 -o` 로 받고, 크기>0·`.js` 첫 200바이트에 `3.13.0`·woff2 첫 4바이트 `wOF2` 를 확인한 뒤 vendor 로 복사. 받은 파일을 실행하지 않는다.
- 쓰기 범위 (이 파일들만 수정/생성):
  - `src/hwp2md/web/static/vendor/gsap/gsap.min.js`, `ScrollTrigger.min.js`, `SplitText.min.js`, `ScrambleTextPlugin.min.js`, `LICENSE.md`
  - `src/hwp2md/web/static/vendor/fonts/PretendardVariable.woff2`, `JetBrainsMono-Regular.woff2`, `JetBrainsMono-Medium.woff2`, `JetBrainsMono-SemiBold.woff2`, `fonts.css`, `OFL-Pretendard.txt`, `OFL-JetBrainsMono.txt`
  - `src/hwp2md/web/static/vendor/marked.LICENSE.md`, `src/hwp2md/web/static/vendor/README.md`
  - `.ai/tasks/T-20261027-v3-backend/dl/**` (임시, 커밋 안 함)
- 산출물: `fonts.css` 는 `@font-face { font-family: "Pretendard Variable"; src: url("/static/vendor/fonts/PretendardVariable.woff2") format("woff2-variations"), url(...) format("woff2"); font-weight: 100 900; font-display: swap; }` 와 JetBrains Mono 400/500/600 3개. README.md 는 파일·원본 URL·버전·SHA-256(`shasum -a 256`)·라이선스 표.
- 글꼴 실패 경로: 글꼴 URL 이 2회 실패하면 woff2·OFL 파일을 만들지 않고 `fonts.css` 를 `/* 글꼴 미동봉: 시스템 글꼴 스택 사용 (vendor/README.md 참고) */` 한 줄로 쓰고, README.md 에 "글꼴 미동봉" 행을 적고, 보고서 NOTES 에 `FONT_FALLBACK` 을 쓴다.
- 검증: `head -c 200 src/hwp2md/web/static/vendor/gsap/gsap.min.js | grep -c 3.13.0` → `1`; `for f in src/hwp2md/web/static/vendor/gsap/*.min.js; do test -s $f || echo MISSING $f; done` → 출력 없음; C9 명령 → `ok`; `grep -c "@font-face" src/hwp2md/web/static/vendor/fonts/fonts.css` → `4` (실패 경로면 `0`); `du -sh src/hwp2md/web/static/vendor` → 10M 미만
- 완료 조건: 검증 통과 + PROGRESS 기록 + 커밋 `[T-20261027-v3-backend][s1] vendor GSAP·글꼴·라이선스 동봉` (`dl/` 는 커밋 제외)
- 실패 시: GSAP 3회 실패 → BLOCKED. vendor 아래 부분 파일은 `git clean -n` 확인 후 orchestrator 가 삭제.

### Stage 2 — 변환 화면 이식과 실제 MODES 연결
- 목적: `GET /` 가 V3 변환 화면을 실제 API·브라우저 모드로 동작시키고 이전 UI 파일을 지운다.
- 담당: implementer(opus)
- 병렬 가능: 아니오 · 선행: Stage 1
- 입력: `design/v3/app.html`, `design/v3/js/app.js`, `design/v3/js/theme.js`, `design/v3/css/base.css`, `design/v3/css/app.css`, 현재 `src/hwp2md/web/static/index.html`·`app.js`(MODES 100~146행, handleModeToggle 299~325행), §4 전체, design.md 결정 2·3·4·7·8, `tests/e2e/test_web_ui.py`(선택자 확인용, 수정 금지)
- 작업:
  - `base.css`·`app.css`·`theme.js` 를 그대로 복사 (CSS 안 `url(...)` 상대경로가 있으면 `/static/...` 로).
  - `index.html`: 시안 `app.html` 기준. CDN `<link>`·`preconnect` 제거 → `/static/vendor/fonts/fonts.css`; 스크립트는 §4 순서; `demo-payload.js`·`demo-engine.js`·`.demo-dock`·`#demo-sample`·`i-flask` 심볼 제거; `href="index.html"` → `/about`; 바닥글 `../../docs/extraction-limits.md` 링크 → `/about#limits`; 고지 문구 문단 유지.
  - `js/app.js`: 시안 기준. `MODES` 를 §4 대로 교체, `handleModeToggle` 의 데모 로더 → `window.Hwp2mdBrowser.load()` (없으면 오류 상태), 데모 도크·`els.sample`·`resetAll` 데모 바인딩 제거, `LIMITS_DOC = "/about#limits"`, 모션 계약 적용(`autoAlpha` → `opacity`, `renderCounts` 숫자 tween 제거), 헤더 주석에서 "데모 엔진" 문구 수정.
  - `static/app.js`, `static/style.css` 를 `git rm`.
- 쓰기 범위:
  - `src/hwp2md/web/static/index.html`
  - `src/hwp2md/web/static/js/app.js`, `src/hwp2md/web/static/js/theme.js`
  - `src/hwp2md/web/static/css/base.css`, `src/hwp2md/web/static/css/app.css`
  - 삭제: `src/hwp2md/web/static/app.js`, `src/hwp2md/web/static/style.css`
  - 로그: `logs/s2-app.log`
  (파일 5개 + 삭제 2개. CSS·theme.js 는 복사라 단계 크기 기준 안에 든다)
- 검증: `uv run pytest tests/unit/test_web_app.py tests/e2e/test_web_ui.py tests/e2e/test_web_extract.py tests/e2e/test_web_api.py -q > logs/s2-app.log 2>&1; echo rc=$?; tail -3 logs/s2-app.log` → `rc=0`, 실패 0 (브라우저 모드 케이스 포함 — jsDelivr Pyodide 접근 필요); C7 명령 → 출력 없음; C8 → 두 파일 없음
- 완료 조건: 검증 통과 + PROGRESS 기록 + 커밋 `[T-20261027-v3-backend][s2] V3 변환 화면을 /api·브라우저 모드에 연결`
- 실패 시: 기존 E2E 가 선택자·문구 차이로 실패하면 app.js/index.html 쪽을 고친다(테스트 수정 금지). 2회 같은 오류 → BLOCKED. 브라우저 모드 케이스만 네트워크 오류(Pyodide CDN)로 실패하면 `logs/s2-app.log` 에 남기고 orchestrator 가 S6 에서 재실행으로 판정.

### Stage 3 — 소개 페이지 `/about` 연결
- 목적: V3 소개 페이지를 `GET /about` 으로 vendor 자원만으로 띄운다.
- 담당: implementer(opus)
- 병렬 가능: 아니오 · 선행: Stage 2 (base.css·theme.js 를 공유)
- 입력: `design/v3/index.html`, `design/v3/css/landing.css`, `design/v3/js/effects.js`, `design/v3/js/landing.js`, `src/hwp2md/web/app.py`, `tests/unit/test_web_app.py`, §4, design.md 결정 1·7
- 작업:
  - `about.html`: 시안 `index.html` 기준. CDN 제거 → §4 소개 페이지 순서, 상대 링크 `app.html` → `/`, `index.html` → `/about`, `#limits` 의 `../../docs/extraction-limits.md` 링크 → 링크 없는 글자 `저장소의 docs/extraction-limits.md`. 고지 문구 유지.
  - `landing.css`·`effects.js`·`landing.js` 는 복사 (상대경로가 있으면 `/static/...`).
  - `app.py`: `_about` 핸들러(`FileResponse(STATIC_DIR / "about.html", media_type="text/html; charset=utf-8")`)와 `Route("/about", _about, methods=["GET"])` 추가. 다른 라우트 불변.
  - `test_web_app.py`: `test_about_html` — 200, `text/html`, 본문 == `about.html` 바이트, `id="limits"` 와 `href="/"` 포함. 그리고 `test_index_has_no_demo` — `/` 본문에 `demo-engine`·`demo-dock` 없음.
- 쓰기 범위:
  - `src/hwp2md/web/static/about.html`, `src/hwp2md/web/static/css/landing.css`, `src/hwp2md/web/static/js/effects.js`, `src/hwp2md/web/static/js/landing.js`
  - `src/hwp2md/web/app.py`, `tests/unit/test_web_app.py`
- 검증: `uv run pytest tests/unit/test_web_app.py -q` → 실패 0; `uv run ruff check src tests && uv run ruff format --check src tests && uv run mypy src` → rc 0; `grep -nE "cdn\.jsdelivr|googleapis|gstatic|href=\"app\.html\"|href=\"index\.html\"" src/hwp2md/web/static/about.html` → 출력 없음
- 완료 조건: 검증 통과 + PROGRESS 기록 + 커밋 `[T-20261027-v3-backend][s3] 소개 페이지 /about 연결`
- 실패 시: 2회 같은 오류 → BLOCKED.

### Stage 4 — 문서 갱신 (README·기능 명세·결정·NOTICE·시안 README)
- 목적: 새 화면 구조·vendor 출처·라이선스를 문서에 반영한다.
- 담당: implementer(opus)
- 병렬 가능: 아니오 · 선행: Stage 3
- 입력: S1~S3 커밋 diff(`git diff .ai/tasks/T-20261027-v3-backend/.base-s1 HEAD --stat`), `src/hwp2md/web/static/vendor/README.md`, `docs/feature-reference.md` §9(691~895행), README `### ② 웹 미리보기`(110~135행), `NOTICE`, `design/v3/README.md`
- 작업:
  - README ②: `/` 변환 화면·`/about` 소개, 서버 모드는 인터넷 없이 동작, 브라우저 모드는 Pyodide CDN 필요.
  - feature-reference §9: 파일 표를 새 정적 배치로, 스크립트 순서, §9.1 에 `#error-text`·`#error-close`·`#copy`·`span.l` 추가, §9.8 시각 디자인을 V3 토큰(base.css) 기준으로 한두 줄. 표 1(57~68행) 의 `static/app.js` 경로를 `static/js/app.js` 로.
  - decisions.md: `## 2026-10-27 V3 화면 연결: / 변환, /about 소개, 자원 동봉` (결정·이유 2줄, 글꼴 실패 경로였다면 그 사실).
  - NOTICE: GSAP(표준 라이선스, URL), marked(MIT), Pretendard·JetBrains Mono(OFL 1.1) 항목 추가 — 글꼴 실패 경로면 글꼴 항목 생략.
  - design/v3/README.md: 첫 줄 "백엔드 미연결 시안" → "시안 (서버 연결본: `src/hwp2md/web/static/`)", "백엔드에 연결할 때" 절 끝에 "2026-10-27 연결 완료" 한 줄.
- 쓰기 범위: `README.md`, `docs/feature-reference.md`, `docs/decisions.md`, `NOTICE`, `design/v3/README.md`
- 검증: `grep -c "/about" README.md docs/feature-reference.md` → 각 1 이상; `grep -c "static/app.js\|style.css" docs/feature-reference.md` → `0`; `grep -c "GSAP" NOTICE` → 1 이상; `cd /Users/illi/illy-projects && scripts/sanitize-check.sh hwp2md` → rc 0
- 완료 조건: 검증 통과 + PROGRESS 기록 + 커밋 `[T-20261027-v3-backend][s4] 문서에 V3 화면 구조와 동봉 자원 반영`
- 실패 시: sanitize 실패 → 해당 문구 수정 후 재검증, 2회 실패 → BLOCKED.

### Stage 5 — V3 화면 E2E 작성·실행 (필수)
- 목적: 서버가 띄운 V3 두 페이지를 외부 요청 차단 상태에서 성공·실패 경로로 검증하고 스크린샷을 남긴다.
- 담당: test-writer(sonnet) 작성 → runner(haiku) 실행
- 병렬 가능: 아니오 · 선행: Stage 4
- 입력: `tests/e2e/conftest.py`(`web_server` 픽스처, 수정 금지), `tests/e2e/test_web_ui.py`·`test_web_extract.py`(헬퍼 패턴·합성 파일 작성법 참고, 수정 금지), §4, openspec `specs/web-preview/spec.md` 델타
- 공통: 브라우저 컨텍스트에 `ctx.route("**/*", ...)` — URL 호스트가 `localhost:<web_server.port>` 가 아니면 `route.abort()` 하고 그 URL 을 `blocked` 리스트에 넣는다. viewport 1440×900. 스크린샷 경로 `Path(os.environ.get("ILLY_SHOT_DIR", "tests/e2e/screenshots"))`.
- 케이스 (최소):
  1. `test_v3_server_convert_offline` (성공): `/` 열기 → `IMAGE_HWPX`(test_web_ui 와 같은 선택 규칙) 입력 → `done`; `blocked == []`; `page.evaluate("window.gsap.version") == "3.13.0"`; `window.Hwp2mdDemo` undefined; `.demo-dock`·`#demo-sample` 개수 0; `done` 직후 `#result-meta` innerText 에 `이미지 1개`; `#raw` 텍스트 == CLI 변환 `.md`(run_cli 픽스처); `#preview table` 8개. 스크린샷 `v3-app-done.png`.
  2. `test_v3_not_hwp_error_and_close` (실패): 텍스트 바이트 `.hwp` 입력 → `error`; `#error-text` 에 `HWP 5.0 또는 HWPX 파일이 아닙니다`; `#download` disabled; 스크린샷 `v3-app-error.png`; `#error-close` 클릭 → `#error` hidden.
  3. `test_v3_skipped_links_about`: 머리말 합성 HWPX(test_web_extract 의 생성 방식 재사용·복제) → `#skipped a` 의 `href` 가 `/about#limits`; 그 링크 클릭 후 `#limits` 보임, `blocked == []`.
  4. `test_v3_about_offline`: `/about` → `blocked == []`; `window.ScrollTrigger`·`window.SplitText`·`window.ScrambleTextPlugin` 정의; `#limits li` ≥ 8; "변환 도구 열기" 링크 href `/`; 고지 문구 포함; 글꼴: `fonts.css` 에 `@font-face` 가 있으면 `document.fonts.check('16px "Pretendard Variable"')` true 를 `document.fonts.ready` 뒤 단언, 없으면 `getComputedStyle(body).fontFamily` 에 `-apple-system` 포함 단언. 스크린샷 `v3-about.png`(full_page).
  5. `test_v3_dark_theme`: `.theme-toggle` 클릭 → `html[data-theme="dark"]`, 새로고침 후 유지(localStorage); 변환 1회 후 스크린샷 `v3-app-dark.png`.
  6. `test_v3_narrow_tabs`: viewport 390×844, 변환 후 `#pane-raw` hidden, `#tab-raw` 클릭 → `#pane-raw` 보이고 `#pane-preview` hidden; 스크린샷 `v3-app-narrow.png`.
  7. `test_v3_copy_button`: 컨텍스트에 `clipboard-read`,`clipboard-write` 권한, 변환 후 `#copy` 클릭 → `navigator.clipboard.readText()` == `#raw` textContent, `#toast` 글자 `Markdown 원문을 복사했습니다`.
- 쓰기 범위: `tests/e2e/test_web_v3.py`
- 검증 (runner): `ILLY_SHOT_DIR=.ai/tasks/T-20261027-v3-backend/screenshots uv run pytest tests/e2e/test_web_v3.py -q > logs/s5-e2e-v3.log 2>&1; echo rc=$?; tail -5 logs/s5-e2e-v3.log` → `rc=0`, `7 passed` 이상, skip 0; `ls .ai/tasks/T-20261027-v3-backend/screenshots/v3-*.png | wc -l` → `5` 이상 (`v3-app-done`, `v3-app-error`, `v3-about`, `v3-app-dark`, `v3-app-narrow`)
- 완료 조건: 검증 통과 + PROGRESS 기록 + 커밋 `[T-20261027-v3-backend][s5] V3 화면 E2E 7케이스`
- 실패 시: 테스트가 제품 결함을 드러내면 테스트를 약화하지 않는다 — runner 가 실패 로그를 orchestrator 에 반환 → orchestrator 가 해당 Stage(2 또는 3) 쓰기 범위로 implementer 재호출(RETRY 기록, 상한 2회). test-writer 2회 실패 → opus 로 1회.

### Stage 6 — 전체 게이트 실행
- 목적: 회귀·린트·타입·wheel·익명화를 한 번에 확인하고 로그를 남긴다.
- 담당: runner(haiku)
- 병렬 가능: 아니오 · 선행: Stage 5
- 쓰기 범위: `logs/s6-gate.log`, `logs/e2e.log`, `.ai/tasks/T-20261027-v3-backend/dist/**` (커밋 안 함)
- 검증: 차례로 실행하고 각 rc 를 기록 — C5 `uv run pytest tests/unit -q`; C6; C4 `ILLY_SHOT_DIR=.ai/tasks/T-20261027-v3-backend/screenshots uv run pytest tests/e2e -q > logs/e2e.log 2>&1; echo rc=$?`; C2 의 `git diff --stat main -- ...` 출력 없음; C7; C11 → `3`; C12 rc 0; C14 valid. 전부 기대값이면 PASS.
- 완료 조건: 모든 rc 0 + PROGRESS 기록 + 커밋 `[T-20261027-v3-backend][s6] 전체 게이트 통과` (로그만)
- 실패 시: 실패 항목 tail 20줄을 orchestrator 에 반환 → 원인 Stage 재호출(상한 2회). 브라우저 모드 케이스가 jsDelivr 네트워크 오류로만 실패하면 1회 재실행, 다시 실패하면 BLOCKED(네트워크) 로 기록.

### Stage 7 — 리뷰·결과 기록
- 목적: diff 와 스크린샷을 직접 보고 C13 을 판정하고 RESULT 를 쓴다.
- 담당: reviewer(sonnet) → scribe(haiku)
- 병렬 가능: 아니오 · 선행: Stage 6
- 입력: `git diff main...HEAD --stat`, `.ai/tasks/T-20261027-v3-backend/screenshots/v3-*.png`, `logs/s6-gate.log`, `logs/e2e.log` tail
- 리뷰 항목: C13 의 화면 조건 5개, §4 모션 계약(app.js 에 `autoAlpha` 없음), OUT 파일 미변경(`git diff --stat main -- design/v3 ':!design/v3/README.md' src/hwp2md/web/static/pyodide-runner.js` 출력 없음), vendor 라이선스 표가 실제 파일과 일치.
- 쓰기 범위: `.ai/tasks/T-20261027-v3-backend/RESULT.md` (scribe)
- 검증: RESULT.md 에 C1~C14 각각 PASS/FAIL 과 근거 한 줄, 스크린샷 경로 5개 이상
- 완료 조건: reviewer 판정 APPROVE + RESULT.md 커밋 `[T-20261027-v3-backend][s7] 리뷰·RESULT`. 이후 orchestrator 가 `openspec validate v3-backend` → archive.
- 실패 시: reviewer CHANGES_REQUESTED → 지적 Stage 재호출(상한 2회) 후 S6 재실행.

## 6. 병렬 실행 맵
```
S1(vendor) ──> S2(변환 화면) ──> S3(/about) ──> S4(문서) ──> S5(E2E) ──> S6(게이트) ──> S7(리뷰·RESULT)
```
전부 순차. S2·S3 는 `base.css`·`theme.js` 를 공유하고, S4·S5 는 쓰기 범위가 겹치지 않지만(문서 5개 vs `tests/e2e/test_web_v3.py`) 쓰는 단계 2개를 병렬로 두려면 worktree 격리가 필요하고 Agent worktree 는 main 에서 갈라지므로 순차가 싸다. 병렬 묶음 없음.

## 7. 사용자에게 확인받을 것 (플랜 승인 시 한 번에)
- [ ] Q1. 경로: `/` 를 변환 화면, `/about` 을 소개 페이지로 둔다. (반대로 `/` 소개·`/app` 변환으로 하면 기존 E2E·단위 테스트의 URL 을 고쳐야 한다)
  - 기본값: `/` 변환 화면, `/about` 소개.
- [ ] Q2. 화면의 "왜 빠졌나요?"·추출 한계 링크 대상: 서버에는 `docs/` 가 없다.
  - 기본값: `/about#limits` 로 연결하고, 소개 페이지의 문서 링크는 링크 없는 글자로 남긴다.
- [ ] Q3. 글꼴: Pretendard Variable 전체(약 2MB)와 JetBrains Mono 3굵기를 그대로 동봉한다(서브셋 안 만듦).
  - 기본값: 전체 동봉. 다운로드 2회 실패 시 시스템 글꼴 폴백.
- [ ] Q4. `design/v3/` 시안(데모 엔진 포함)과 `test_design_v3.py` 는 유지한다.
  - 기본값: 유지 (README 만 "서버 연결본 위치" 표시).
- [ ] Q5. 헤더의 `v3.0` 배지는 시안 그대로 둔다(패키지 버전과 무관한 화면 버전 표기).
  - 기본값: 그대로.

## 8. 리스크
| 리스크 | 가능성 | 대응 |
|--------|--------|------|
| 시안 GSAP `autoAlpha` 로 `inner_text()` 단언이 모션 중 빈 글자 | 높음 | §4 모션 계약으로 변환 화면에서 `autoAlpha` 금지, `renderCounts` 즉시 최종값 |
| jsDelivr 접근 실패(다운로드·브라우저 모드 E2E) | 중 | S1 재시도 상한·글꼴 폴백, S6 네트워크 실패 1회 재실행 후 BLOCKED |
| CSS 안 상대 `url()` 이 `/about` 기준에서 깨짐 | 중 | S2·S3 에서 `/static/` 절대경로로 바꾸고 S5 `blocked`·스크린샷으로 확인 |
| `#error[hidden]` 이 `display:flex; visibility:hidden` 이라 레이아웃 높이 차이 | 낮음 | 시안 그대로 유지, `is_hidden()` 는 visibility 로도 true |
| wheel 에 woff2 가 빠짐(hatch 기본 포함 규칙) | 낮음 | C11 로 확인, 빠지면 BLOCKED(pyproject 는 orchestrator 전용) |
| GSAP 표준 라이선스 재배포 조건 해석 | 낮음 | LICENSE.md 에 원문 URL·package.json license 필드 인용, NOTICE 에 기재 |

## 9. 예상 비용
- 예상 단계 수: 7 · 서브에이전트 호출: 9회 (implementer 4, test-writer 1, runner 2, reviewer 1, scribe 1) + 재시도 예비 2회 · 주 모델: opus 4 / sonnet 2 / haiku 3
