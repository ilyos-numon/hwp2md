# hwp2md 프론트엔드 V3 (백엔드 미연결 시안)

Stitch V2 시안(`design/stitch/`)의 색·레이아웃·문구를 잇고 GSAP 모션을 더한 정적 프론트엔드. 아직 `hwp2md serve` 에 연결하지 않았다.

| 파일 | 내용 |
|---|---|
| `index.html` + `css/landing.css` + `js/landing.js` | 서비스 소개. 스크롤 핵심 장면(문서 → 블록 → Markdown), 세 가지 입구 터미널, 가로 스크롤 사용 장면, 보안 모드 흐름도 |
| `js/effects.js` | `gsap.registerEffect` 로 등록한 재사용 효과: `riseChars`, `scrambleIn`(Markdown 기호로 해독), `drawIn`, `tagPop`, `typeLines`, `countTo`. 모두 `extendTimeline` 이라 `tl.scrambleIn(...)` 처럼 타임라인에서 바로 쓴다 |
| `app.html` + `css/app.css` + `js/app.js` | 변환 화면. 기존 UI 의 id·`data-state`·오류 문구 계약 유지 |
| `css/base.css`, `js/theme.js` | 공통 토큰(라이트·다크), 헤더, 버튼, 테마 전환 |
| `js/demo-engine.js`, `js/demo-payload.js` | **임시** 변환 엔진. 실제 엔진이 `demo.hwpx` 를 변환한 `/api/convert` 응답을 그대로 담았다 |

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
