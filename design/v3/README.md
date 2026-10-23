# hwp2md 프론트엔드 V3 (백엔드 미연결 시안)

Stitch V2 시안(`design/stitch/`)의 색·레이아웃·문구를 잇고 GSAP 모션을 더한 정적 프론트엔드. 아직 `hwp2md serve` 에 연결하지 않았다.

| 파일 | 내용 |
|---|---|
| `index.html` + `css/landing.css` + `js/landing.js` | 서비스 소개. 스크롤 핵심 장면(문서 → 블록 → Markdown), 세 가지 입구 터미널, 가로 스크롤 사용 장면, 보안 모드 흐름도 |
| `js/effects.js` | `gsap.registerEffect` 로 등록한 재사용 효과: `riseChars`, `scrambleIn`(Markdown 기호로 해독), `drawIn`, `tagPop`, `typeLines`, `countTo`. 모두 `extendTimeline` 이라 `tl.scrambleIn(...)` 처럼 타임라인에서 바로 쓴다 |
| `app.html` + `css/app.css` + `js/app.js` | 변환 화면. 기존 UI 의 id·`data-state`·오류 문구 계약 유지 |
| `css/base.css`, `js/theme.js` | 공통 토큰(라이트·다크), 헤더, 버튼, 테마 전환 |
| `js/demo-engine.js`, `js/demo-payload.js` | **임시** 변환 엔진. 실제 엔진이 합성 데모 HWPX 를 변환한 `/api/convert` 응답을 그대로 담았다 |

## 보는 법

`index.html` 또는 `app.html` 을 브라우저로 연다. GSAP 3.13.0·marked 12.0.2·글꼴은 CDN 에서 받으므로 인터넷이 필요하다.
변환 화면 왼쪽 아래 "데모"를 펼치면 예시 변환·오류 상태·처음으로를 바로 볼 수 있다.

## 백엔드에 연결할 때

1. `app.html` 에서 `demo-payload.js`, `demo-engine.js` 를 빼고 `src/hwp2md/web/static/pyodide-runner.js` 를 넣는다.
2. `js/app.js` 의 `const MODES = window.Hwp2mdDemo.MODES;` 를 현재 UI 의 서버·브라우저 `MODES`(fetch `/api/convert`, `/api/zip`, `window.Hwp2mdBrowser`)로 바꾼다.
3. `handleModeToggle` 의 `window.Hwp2mdDemo.loadBrowser()` 를 `window.Hwp2mdBrowser.load()` 로 바꾸고, 데모 도크와 "예시 문서로 해 보기" 버튼을 지운다.
4. 서버 모드는 CDN 없이 동작해야 하므로 GSAP·marked·글꼴을 `static/vendor/` 에 동봉한다.
5. 기존 E2E(`tests/e2e/test_web_ui.py`)가 쓰는 선택자는 모두 유지돼 있다. 바뀐 점: `#error` 안에 `#error-text`·닫기 버튼이 생겼고, `#raw` 는 줄마다 `span.l` 로 그리지만 `textContent` 는 Markdown 원문과 같다.

## 바뀐 문구 (V2 대비)

V2 시안 중 실제 동작과 다른 문구를 [기능 명세](../../docs/feature-reference.md)에 맞춰 고쳤다: 브라우저 모드 준비(서버의 20MB 번들 → CDN 의 Python 실행 환경 + 서버의 변환 코드, 첫 준비 약 1분), 각주·목록·서식 변환 주장 삭제, 지원 한계에 병합 칸·표 칸 안 그림·WMF/EMF 추가.

## 추출 한계 표기 (2026-10-23)

- 변환 화면: 응답의 `skipped` 가 비어 있지 않으면 `#skipped`(role=status)에 `변환하지 못한 요소: 머리말·꼬리말 1개 · …` 와 [추출 한계 문서](../../docs/extraction-limits.md) 링크("왜 빠졌나요?")를 보인다. 라벨은 `skipped[].label` 그대로, `textContent` 로만 넣는다.
- 오류 문구: `drm`·`encrypted` 를 추가하고 `unsupported` 문구를 바꿨다(`js/app.js` 의 `ERROR_TEXT`). 데모 엔진도 두 코드를 415 로 돌려주고, 데모 도크에 "DRM 오류" 버튼이 있다.
- 서비스 소개 `#limits`: 불가·부분·제외·예정·범위 밖 칩으로 다시 썼고, 이번에 된 것(각주·미주, 하이퍼링크, 수식, 번호·글머리표 목록, 표 칸·글상자 안 그림, 배포용 문서, HWPML)은 기능 쪽 문구로 옮겼다.
- 바닥글(`index.html`)과 변환 화면 아래(`app.html`)에 한컴 공개 문서 참고 고지가 있다.
- 데모 응답 다시 만들기: `uv run python .ai/tasks/T-20261023-extract-dropped/demo/make_payload.py` (합성 HWPX: 제목·링크·각주·글머리표·칸 그림 표·수식·머리말 → `js/demo-payload.js`).
