# V3 프론트엔드를 실제 백엔드에 연결

## Why

`design/v3` 에 새 소개 페이지(`index.html`)와 변환 화면(`app.html`)이 있지만, 데모 엔진(`demo-engine.js`·`demo-payload.js`)이 고정 응답을 돌려줄 뿐 `hwp2md serve` 에 연결돼 있지 않다. GSAP·marked·글꼴은 CDN 에서 받아 인터넷 없이는 화면이 깨진다. 사용자가 `hwp2md serve` 로 여는 화면은 여전히 이전 UI(`static/style.css`·`static/app.js`)다. 새 화면을 실제 변환 API·브라우저 모드에 붙이고, 서버 모드가 외부 네트워크 없이 동작하게 해 기존 UI 를 대체한다.

## What Changes

- `GET /` 는 V3 변환 화면을 돌려준다(`static/index.html` 을 V3 마크업으로 교체). 변환은 `POST /api/convert`·`POST /api/zip`(서버 모드)과 `window.Hwp2mdBrowser`(브라우저 모드)를 쓴다. 데모 엔진·데모 도크·"예시 문서로 해 보기" 버튼은 없다.
- 새 경로 `GET /about` 이 V3 소개 페이지(`static/about.html`)를 돌려준다. 두 페이지는 서로 링크한다.
- GSAP 3.13.0(`gsap`, `ScrollTrigger`, `SplitText`, `ScrambleTextPlugin`), marked 12.0.2, Pretendard Variable·JetBrains Mono 글꼴을 `static/vendor/` 에 동봉하고 각 라이선스 파일을 함께 둔다. 서버 모드 두 페이지는 외부 호스트에 요청을 보내지 않는다(브라우저 모드의 Pyodide CDN 은 그대로).
- 글꼴을 받지 못하면 `@font-face` 없이 시스템 글꼴 스택(`base.css` 의 `--font-base`·`--font-mono`)으로 동작한다.
- 이전 UI 파일 `static/app.js`·`static/style.css` 를 지운다. 기존 E2E 선택자(id·`data-state`·오류 문구)는 그대로 유지한다.
- 화면의 "왜 빠졌나요?" 링크는 서버가 제공하는 `/about#limits` 로 간다.
- `design/v3/**` 시안(데모 엔진 포함)은 그대로 둔다.

## Capabilities

### New Capabilities
- 없음

### Modified Capabilities
- `web-preview`: `GET /` 화면이 V3 변환 화면이 되고, `GET /about` 소개 페이지·정적 자원 동봉(외부 요청 없음)·라이선스 동봉 요구를 더한다. 건너뜀 경고 링크와 고지 문구 대상 파일 목록을 바꾼다.

## Impact

- 코드: `src/hwp2md/web/app.py`(라우트 1개), `src/hwp2md/web/static/**`(HTML·CSS·JS·vendor).
- 테스트: `tests/unit/test_web_app.py`(라우트), 새 `tests/e2e/test_web_v3.py`. 기존 `tests/e2e/test_web_ui.py`·`test_web_extract.py`·`test_web_api.py`·`test_design_v3.py` 는 수정 없이 통과해야 한다.
- 문서: README 웹 절, `docs/feature-reference.md` §9, `docs/decisions.md`, `NOTICE`, `design/v3/README.md`.
- 패키지 크기: 글꼴 woff2 로 wheel 이 약 2~3MB 커진다.
