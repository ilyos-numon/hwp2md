# Design — V3 프론트엔드 백엔드 연결

## Context

- 시안: `design/v3/{index.html, app.html, css/*, js/*}`. 변환 화면은 `window.Hwp2mdDemo.MODES` 에 변환을 위임한다.
- 현재 UI: `src/hwp2md/web/static/{index.html, app.js, style.css, pyodide-runner.js, vendor/marked.min.js}`. `app.js` 의 `MODES`(서버: fetch `/api/convert`·`/api/zip`, 브라우저: `window.Hwp2mdBrowser`)와 `readErrorBody` 가 실제 연결 코드다.
- `app.py` 는 `/` → `static/index.html`, `/static` → `StaticFiles` 만 둔다. 단위 테스트 `test_index_html` 은 `/` 응답 바이트 == `static/index.html` 을 본다.

## Goals / Non-Goals

- Goals: `hwp2md serve` 화면을 V3 로 교체, 서버 모드 무외부요청, 기존 E2E 무수정 통과, 라이선스 동봉.
- Non-Goals: `design/v3/**` 수정(시안·데모 E2E 유지), `pyodide-runner.js` 변경(Pyodide 는 계속 CDN), 새 변환 기능, Docker.

## Decisions

1. **경로**: 변환 화면은 `GET /`(파일 `static/index.html`), 소개는 `GET /about`(파일 `static/about.html`). `hwp2md serve` 가 여는 `/` 에서 바로 변환할 수 있어야 하고, 기존 E2E·단위 테스트가 `/` 를 변환 화면으로 가정한다.
2. **정적 배치**: 시안의 상대 구조를 `static/` 아래로 그대로 옮긴다 — `static/css/{base,app,landing}.css`, `static/js/{app,theme,effects,landing}.js`. HTML 안 참조는 모두 절대경로 `/static/...` 로 쓴다(`/` 와 `/about` 두 기준 경로에서 같은 자원을 가리키게).
3. **MODES 이식**: 시안 `js/app.js` 를 기준으로, `MODES` 는 현재 `static/app.js` 의 서버·브라우저 객체와 `readErrorBody` 를 그대로 옮긴다. `handleModeToggle` 은 `window.Hwp2mdBrowser` 가 없으면 오류 상태로 돌린다(현재 동작과 같음). 데모 관련 코드(`resetAll` 의 데모 도크 바인딩, `els.sample`, `[data-demo]`)는 지운다. `window.Hwp2mdApp` 노출은 유지한다.
4. **모션 제약**: 변환 화면은 `autoAlpha` 대신 `opacity` 를 쓰고, `renderCounts` 는 `textContent` 에 최종값을 먼저 넣는다(숫자 증가 모션을 쓰려면 별도 장식 요소에만). 이유: Chromium `innerText` 는 `visibility:hidden` 글자를 빼므로 E2E 의 `inner_text()` 단언이 모션 시간에 따라 흔들린다. 소개 페이지는 E2E 가 글자를 읽지 않는 장식 모션이라 `autoAlpha` 를 그대로 둔다.
5. **vendor**: jsDelivr npm 경로에서 받는다 — `gsap@3.13.0/dist/*.min.js`, `pretendard@1.3.9/dist/web/variable/woff2/PretendardVariable.woff2` + `LICENSE`, JetBrains Mono `v2.304` woff2(400·500·600) + `OFL.txt`. 글꼴은 `vendor/fonts/fonts.css` 의 `@font-face` 로 선언하고 두 HTML 이 `/static/vendor/fonts/fonts.css` 를 먼저 불러온다. marked 는 이미 있는 `vendor/marked.min.js` 를 쓴다.
6. **글꼴 실패 경로**: 글꼴 다운로드가 2회 실패하면 woff2 없이 `fonts.css` 를 주석 한 줄만 있는 파일로 두고, `vendor/README.md` 에 "글꼴 미동봉 — 시스템 글꼴 스택 사용"을 적는다. `base.css` 의 글꼴 스택에 시스템 글꼴이 이미 있어 화면은 깨지지 않는다. E2E 는 `fonts.css` 에 `@font-face` 가 있을 때만 글꼴 로드를 단언한다.
7. **추출 한계 링크**: 서버 화면에는 `docs/` 가 없으므로 `LIMITS_DOC = "/about#limits"`. 소개 페이지 `#limits` 의 `../../docs/extraction-limits.md` 링크는 글자로만 남긴다("저장소의 docs/extraction-limits.md").
8. **이전 UI 삭제**: `static/app.js`·`static/style.css` 를 지운다. `static/index.html` 은 V3 마크업으로 덮어쓴다(고지 문구 유지).

## Risks / Trade-offs

- SplitText·ScrambleTextPlugin 은 GSAP 3.13 부터 무료 표준 라이선스다. 재배포 조건은 라이선스 안내에 원문 URL 로 남긴다.
- wheel 크기 증가(글꼴 약 2~3MB). 서브셋을 만들지 않는다.
- 브라우저 모드 E2E 는 여전히 jsDelivr 접근이 필요하다(기존과 같음).
