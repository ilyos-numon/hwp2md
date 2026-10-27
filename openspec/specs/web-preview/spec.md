# web-preview Specification

## Purpose
`hwp2md serve` 로 띄운 로컬 웹 화면에서 HWP/HWPX 를 드래그앤드롭해 Markdown 미리보기·원문을 보고 zip 으로 내려받는다. "브라우저 안에서만 처리" 를 켜면 파일이 서버로 전송되지 않는다.

## Requirements

### Requirement: serve 하위 명령이 로컬 서버를 띄운다
CLI 는 `hwp2md serve [--host HOST] [--port PORT] [--no-browser]` 를 제공해야 한다(SHALL). 기본값은 host `localhost`, port `8770` 이고, `--no-browser` 가 없으면 기본 브라우저로 화면을 연다. 준비되면 `GET /api/health` 가 `{"ok": true, "version": "<버전>"}` 를 200 으로 준다. 포트가 사용 중이면 표준 오류에 `hwp2md: error: port <PORT> already in use` 를 쓰고 종료 코드 1 로 끝난다. web extra 가 설치되지 않았으면 표준 오류에 배포 이름 기준 설치 안내 `pip install 'hwp2markdown[web]'` 를 쓰고 종료 코드 1 로 끝난다. 첫 인자가 `serve` 가 아니면 기존 변환 CLI 로 동작한다.

#### Scenario: 서버 기동
- **WHEN** `hwp2md serve --no-browser --port <빈 포트>` 를 실행한다
- **THEN** 30초 안에 `GET /api/health` 가 200 이고 `GET /` 가 `text/html` 화면을 준다

#### Scenario: web extra 없음
- **WHEN** starlette·uvicorn import 를 막은 프로세스에서 `main(["serve", "--no-browser"])` 를 호출한다
- **THEN** 반환값 1, 표준 오류에 `hwp2markdown[web]` 이 포함되고 `'hwp2md[web]'` 은 포함되지 않는다

### Requirement: HTTP API 는 업로드를 메모리에서만 처리한다
서버는 `POST /api/convert?name=<파일명>` 과 `POST /api/zip?name=<파일명>` 을 제공해야 한다(SHALL). 요청 본문은 파일 원본 바이트(`application/octet-stream`)이며 multipart 를 쓰지 않는다. `/api/convert` 는 `convert_to_response` 의 status·body 를 그대로 JSON 으로 주고, `/api/zip` 은 성공 시 `application/zip` 과 `Content-Disposition: attachment; filename*=UTF-8''<percent-encoded stem>.zip` 으로 `build_zip` 바이트를, 실패 시 `/api/convert` 와 같은 오류 JSON 을 준다. `Content-Length` 가 52428800 을 넘으면 본문을 읽지 않고 413 을 준다. 서버는 업로드 바이트를 파일·임시 파일로 쓰지 않는다.

#### Scenario: 서버 모드 변환이 CLI 와 같다
- **WHEN** 실제 샘플 5개를 각각 `/api/convert` 로 보낸다
- **THEN** 응답 `markdown` 이 같은 파일의 CLI 출력 `.md` 와 바이트 단위로 같다

#### Scenario: 저장 흔적 없음
- **WHEN** 작업 디렉터리와 `TMPDIR` 을 빈 임시 폴더로 지정해 서버를 띄우고 샘플 5개를 convert·zip 한다
- **THEN** 두 폴더 아래 파일이 0개다

#### Scenario: HWP 아닌 파일
- **WHEN** 텍스트 바이트를 `/api/convert?name=a.hwp` 로 보낸다
- **THEN** 415 와 `error.code == "not_hwp"` 를 받는다

### Requirement: 화면은 미리보기·원문·다운로드를 제공한다
`GET /` 화면은 드롭 영역(`#drop-zone`)과 파일 선택(`#file-input`)으로 파일을 받아 렌더된 미리보기(`#preview`, 이미지는 data URI)와 원문 Markdown(`#raw`, 상대 이미지 링크)을 나란히 보여 주고, `#download` 로 `<stem>.zip` 을 내려받게 해야 한다(SHALL). 오류는 `#error` 에 한국어 문구로 보인다. 미리보기 렌더러는 Markdown 안의 원시 HTML 을 `<br>` 만 남기고 문자로 이스케이프한다.

#### Scenario: 이미지 있는 HWPX 드롭
- **WHEN** 서버 모드에서 `브라더 공공기관 보고서 양식.hwpx` 를 드롭한다
- **THEN** `#preview` 에 `src` 가 `data:image/png;base64,` 로 시작하고 `naturalWidth > 0` 인 `img` 가 1개, `table` 이 8개 있고, `#raw` 텍스트에 `![그림 1](브라더%20공공기관%20보고서%20양식_images/img_001.png)` 이 있다

### Requirement: 브라우저 전용 모드는 파일을 전송하지 않는다
화면은 "브라우저 안에서만 처리" 토글(`#mode-toggle`)을 제공해야 한다(SHALL). 켜면 Pyodide 와 lxml 을 CDN 에서, hwp2md·olefile 소스를 서버 `GET /pkg/hwp2md.zip` 에서 받아 브라우저 안에서 `convert_to_response`·`build_zip` 을 실행한다. 이 모드에서 파일을 넣고 미리보기·다운로드를 하는 동안 브라우저가 보내는 요청 중 GET 이 아닌 요청과 `/api/` 경로 요청은 0개여야 한다. 같은 파일에 대해 브라우저 모드의 `#raw` 텍스트는 서버 모드의 `#raw` 텍스트와 같아야 한다.

#### Scenario: 무전송 확인
- **WHEN** 토글을 켜고 준비 완료(`#mode-status[data-state=browser]`) 후 요청 기록을 비우고 샘플 5개를 차례로 넣고 하나를 zip 으로 내려받는다
- **THEN** 기록된 요청 중 method 가 GET 이 아닌 것 0개, URL 경로가 `/api/` 로 시작하는 것 0개다. 같은 기록기는 서버 모드에서 `POST /api/convert` 1개(본문 길이 = 파일 크기)를 잡는다

#### Scenario: 두 모드 출력 동일
- **WHEN** 샘플 5개를 서버 모드와 브라우저 모드에서 각각 변환한다
- **THEN** 파일마다 두 `#raw` 텍스트가 같고 CLI `.md` 와도 같으며, 두 모드의 zip 엔트리 이름·내용 바이트가 같다

### Requirement: 화면은 건너뛴 요소를 경고로 보여 준다
`GET /` 화면과 `design/v3/app.html` 변환 화면은 변환 성공 응답의 `skipped` 가 비어 있지 않으면 `#skipped`(role=status) 영역에 `변환하지 못한 요소: <라벨> <n>개[ · …]` 를 보여 주고, 비어 있으면 `#skipped` 를 숨겨야 한다(SHALL). 문구는 `skipped[].label` 을 그대로 쓰고 화면이 따로 라벨 표를 갖지 않는다. `GET /` 화면의 `#skipped` 에는 `/about#limits` 로 가는 링크가, `design/v3/app.html` 의 `#skipped` 에는 `docs/extraction-limits.md` 로 가는 링크가 있다. 라벨은 `textContent` 로 넣는다.

#### Scenario: 머리말 있는 문서
- **WHEN** 서버 모드에서 머리말 컨트롤 1개가 있는 합성 HWPX 를 넣는다
- **THEN** `#skipped` 가 보이고 글자에 `머리말·꼬리말 1개` 가 있으며, 그 안 링크의 `href` 는 `/about#limits` 다

#### Scenario: 건너뜀 없는 문서
- **WHEN** 단락만 있는 합성 문서를 넣는다
- **THEN** `#skipped` 는 숨겨져 있다

### Requirement: 화면은 보호 문서 오류를 구분해 안내한다
화면 오류 문구 표는 `drm` → `문서보안(DRM)이 적용된 파일이라 변환할 수 없습니다. 보안 프로그램에서 해제한 뒤 다시 시도하세요`, `encrypted` → `암호가 설정된 문서라 변환할 수 없습니다. 한글에서 암호를 해제한 뒤 다시 시도하세요`, `unsupported` → `지원하지 않는 HWP 문서라 변환할 수 없습니다` 를 가져야 하고(SHALL), 서버 모드와 브라우저 모드가 같은 문구를 보여 준다.

#### Scenario: DRM 파일
- **WHEN** 서버 모드에서 `9B 20` + `DRMONE` 서명으로 시작하는 합성 파일을 넣는다
- **THEN** `body[data-state="error"]` 이고 `#error` 글자에 `문서보안(DRM)` 이 있다

### Requirement: 화면과 문서는 한컴 공개 문서 참고 사실과 추출 한계를 밝힌다
README, `src/hwp2md/__init__.py` 모듈 docstring, `src/hwp2md/web/static/index.html`, `src/hwp2md/web/static/about.html`, `design/v3/index.html`, `design/v3/app.html` 은 문구 `본 제품은 한글과컴퓨터의 한/글 문서 파일(.hwp) 공개 문서를 참고하여 개발하였습니다.` 를 그대로 담아야 한다(SHALL). `design/v3/index.html` 과 `src/hwp2md/web/static/about.html` 의 `#limits` 목록은 `docs/extraction-limits.md` 의 "불가"·"부분" 행을 한 줄씩 보여 준다. `design/v3/index.html` 의 `#limits` 는 문서 링크를 갖는다.

#### Scenario: 문구 존재
- **WHEN** 여섯 파일에서 위 문구를 고정 문자열로 찾는다
- **THEN** 여섯 파일 모두 1회 이상 나온다

### Requirement: 서버 화면은 V3 변환 화면과 소개 페이지를 제공한다
`GET /` 는 `src/hwp2md/web/static/index.html`(V3 변환 화면), `GET /about` 은 `src/hwp2md/web/static/about.html`(V3 소개 페이지)을 `text/html; charset=utf-8` 로 돌려줘야 한다(SHALL). 변환 화면은 서버 모드에서 `POST /api/convert`·`POST /api/zip` 을, 브라우저 모드에서 `window.Hwp2mdBrowser.load/convert/zip` 을 쓴다. 변환 화면에는 데모 엔진(`window.Hwp2mdDemo`), 데모 도크(`.demo-dock`), 예시 버튼(`#demo-sample`)이 없다. 변환 화면의 상호 링크는 `/about`, 소개 페이지의 "변환 도구 열기" 링크는 `/` 이다.

#### Scenario: 두 페이지 응답
- **WHEN** `GET /` 와 `GET /about` 을 요청한다
- **THEN** 둘 다 200 과 `text/html` 이고, `/` 본문에는 `id="drop-zone"` 이 있고 `demo-engine.js`·`demo-dock` 은 없으며, `/about` 본문에는 `id="limits"` 와 `href="/"` 가 있다

#### Scenario: 데모 없이 실제 변환
- **WHEN** 서버 모드 변환 화면에 이미지 있는 HWPX 를 넣는다
- **THEN** `body[data-state="done"]` 이 되고 `#raw` 텍스트가 같은 파일의 CLI `.md` 와 같으며, `window.Hwp2mdDemo` 는 `undefined` 다

### Requirement: 서버 모드 화면은 외부 호스트 없이 동작한다
`GET /` 와 `GET /about` 이 불러오는 스크립트·스타일·글꼴은 모두 같은 서버의 `/static/` 아래에 있어야 한다(SHALL). GSAP 3.13.0(`gsap.min.js`, `ScrollTrigger.min.js`, `SplitText.min.js`, `ScrambleTextPlugin.min.js`)은 `static/vendor/gsap/`, marked 12.0.2 는 `static/vendor/marked.min.js`, 글꼴은 `static/vendor/fonts/` 에 둔다. 서버 모드에서 두 페이지를 열고 파일 하나를 변환하는 동안 페이지 서버가 아닌 호스트로 가는 요청은 0개다. 글꼴 파일이 없으면 화면은 `@font-face` 없이 시스템 글꼴 스택으로 그린다.

#### Scenario: 외부 요청 차단 상태에서 변환
- **WHEN** 페이지 서버가 아닌 호스트로 가는 요청을 모두 막은 브라우저로 `/` 를 열고 HWPX 를 넣는다
- **THEN** 막힌 요청 수는 0 이고, `window.gsap.version` 은 `3.13.0` 이며, `body[data-state="done"]` 이 된다

#### Scenario: 소개 페이지 모션 자원
- **WHEN** 같은 조건으로 `/about` 을 연다
- **THEN** 막힌 요청 수는 0 이고 `window.ScrollTrigger`·`window.SplitText`·`window.ScrambleTextPlugin` 이 정의돼 있다

### Requirement: 동봉한 외부 자원은 라이선스를 함께 둔다
`static/vendor/` 의 각 외부 자원은 같은 디렉토리 안에 라이선스 파일을 가져야 한다(SHALL): GSAP 표준 라이선스 안내(`vendor/gsap/LICENSE.md`, 원문 URL 포함), marked MIT 전문(`vendor/marked.LICENSE.md`), 글꼴별 SIL OFL 1.1 전문(`vendor/fonts/OFL-*.txt`). `vendor/README.md` 는 파일마다 원본 URL·버전·SHA-256 을 적는다.

#### Scenario: 라이선스 파일 존재
- **WHEN** `static/vendor/` 아래 `.js`·`.woff2` 파일 목록과 라이선스 파일을 대조한다
- **THEN** 모든 자원 파일 이름이 `vendor/README.md` 에 나오고, GSAP·marked·각 글꼴의 라이선스 파일이 비어 있지 않다

### Requirement: 변환 화면 모션은 상태 판정을 늦추지 않는다
변환 화면의 GSAP 모션은 `opacity`·`transform` 만 바꾸고 `visibility`(GSAP `autoAlpha`)를 바꾸지 않아야 하며(SHALL), `#result-meta` 의 개수·`#file-name`·`#raw` 글자는 `body[data-state]` 가 `done` 으로 바뀌는 같은 동기 구간에 최종값이 들어 있어야 한다. `prefers-reduced-motion: reduce` 이면 모션을 생략한다.

#### Scenario: 완료 직후 개수
- **WHEN** 이미지 1개 있는 HWPX 를 넣고 `body[data-state="done"]` 을 기다린 직후 `#result-meta` 의 `innerText` 를 읽는다
- **THEN** 글자에 `이미지 1개` 가 있다

### Requirement: 정적 사이트 설정은 브라우저 모드를 고정한다
변환 화면은 `<meta name="hwp2md-site" content="static">` 이 있으면 시작할 때 브라우저 모드로 들어가 Pyodide 를 불러오고, 모드 스위치(`label.switch`)를 숨기며, 불러오기에 실패해도 서버 모드로 돌아가지 않아야 한다(SHALL). `<meta name="hwp2md-pkg-url">` 이 있으면 런타임 zip 을 그 주소에서 받고, 없으면 `/pkg/hwp2md.zip` 에서 받는다. 두 meta 가 없으면 화면 동작은 이 변경 전과 같다.

#### Scenario: serve 화면은 그대로
- **WHEN** `hwp2md serve` 의 `/` 를 연다
- **THEN** `#mode-status[data-state="server"]` 이고 `label.switch` 가 보인다

#### Scenario: 정적 설정이 있는 화면
- **WHEN** 두 meta 가 있는 `convert.html` 을 연다
- **THEN** `label.switch` 가 보이지 않고 `#mode-status` 가 `loading` 을 거쳐 `browser` 가 된다

### Requirement: 웹 화면은 한국어와 영어로 보인다
변환 화면과 소개 페이지는 사용자 노출 문구를 한국어(`ko`)와 영어(`en`)로 보여야 한다(SHALL). 언어는 `?lang=ko|en` 쿼리, 저장된 선택(`localStorage` `hwp2md-lang`), 브라우저 언어(`ko` 로 시작하면 한국어, 아니면 영어) 순으로 정하고 `<html lang>` 에 반영한다. 알 수 없는 `lang` 값은 무시한다. 헤더의 KO/EN 버튼은 언어를 바꾸고 선택을 저장한다. 한국어 문구는 이 변경 전과 같고, CLI 출력과 HTTP API 응답(건너뜀 라벨 포함)은 바뀌지 않는다. `hwp2md serve` 화면과 정적 사이트 모두에 적용된다.

#### Scenario: 영어 브라우저의 첫 방문
- **WHEN** 브라우저 언어가 `en-US` 이고 저장된 선택이 없는 상태로 변환 화면을 연다
- **THEN** `<html lang="en">` 이고 모드 상태가 `Server mode` 이며, 비 HWP 파일을 넣으면 오류가 `Not an HWP 5.0 or HWPX file` 이다

#### Scenario: 전환과 유지
- **WHEN** 영어 화면에서 KO/EN 버튼을 누르고 새로고침한다
- **THEN** 화면이 한국어(`서버 모드`)로 바뀌고 새로고침 뒤에도 한국어다

#### Scenario: 알 수 없는 언어 값
- **WHEN** 브라우저 언어가 `ko-KR` 인 상태로 `?lang=fr` 을 연다
- **THEN** 쿼리를 무시하고 한국어로 보이며 선택을 저장하지 않는다

#### Scenario: 정적 사이트 영어 변환
- **WHEN** 브라우저 언어가 `en-US` 인 상태로 정적 사이트 `convert.html` 에서 합성 HWPX 를 넣는다
- **THEN** 상태가 `Browser mode: files are not sent to a server` 이고 변환이 끝난다
