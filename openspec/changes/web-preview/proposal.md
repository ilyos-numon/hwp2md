# Proposal

## Why

hwp2md 는 지금 CLI(`hwp2md input.hwp -o out/`)로만 쓸 수 있고, 라이브러리 `convert()` 도 항상 디스크에 `.md` 와 이미지를 쓴다. 개발자가 아닌 사람은 결과를 보려면 터미널과 Markdown 뷰어가 필요하고, 민감한 공문서를 다루는 사람은 "파일이 어디로 가는가"를 확인할 방법이 없다. 로컬 웹 미리보기로 드래그앤드롭 한 번에 변환 결과를 보여 주고, 원하면 변환 자체를 브라우저 안(Pyodide)에서만 돌려 파일이 서버로 전송되지 않게 한다.

## What Changes

- 디스크에 쓰지 않는 메모리 변환 API `hwp2md.memory.convert_bytes(data, filename)` 를 추가한다. 결과는 Markdown(상대 이미지 링크)·이미지 바이트·카운트를 담고, data URI 미리보기 Markdown·`.md`+이미지 zip 바이트·JSON 페이로드로 바꾸는 함수를 함께 제공한다.
- 두 리더(HWP 5.0·HWPX)와 포맷 감지가 경로뿐 아니라 `bytes` 입력도 받는다. 경로 입력의 동작·오류 메시지는 바뀌지 않는다.
- `convert(path, out_dir)` 와 CLI `hwp2md INPUT [-o OUT_DIR]` 의 출력·종료 코드는 바이트 단위로 유지된다.
- 새 하위 명령 `hwp2md serve [--host] [--port] [--no-browser]` 가 로컬 웹 서버(Starlette + uvicorn)를 띄운다. 화면에서 HWP/HWPX 를 드래그앤드롭하면 렌더된 Markdown 미리보기(이미지는 data URI)와 원문 Markdown 을 나란히 보여 주고, `.md`+이미지 zip 을 내려받을 수 있다. 서버는 업로드 바이트를 메모리에서만 처리하고 저장하지 않는다.
- 화면의 "브라우저 안에서만 처리" 토글을 켜면 Pyodide(CDN)로 hwp2md 패키지를 브라우저에서 실행한다. 이 모드에서는 파일 바이트를 담은 요청이 하나도 나가지 않는다. 서버 모드와 브라우저 모드는 같은 입력에서 같은 Markdown 을 낸다.
- 웹 의존성(starlette, uvicorn)은 optional extra `hwp2md[web]` 이다. 기본 설치는 지금처럼 lxml·olefile 만 쓰고, extra 없이 `hwp2md serve` 를 실행하면 설치 안내 오류로 종료한다.

## Capabilities

### New Capabilities
- `memory-conversion`: 파일 시스템을 쓰지 않고 바이트 입력을 Markdown·이미지·zip·JSON 으로 바꾸는 라이브러리 API 와 오류 코드 규칙.
- `web-preview`: `hwp2md serve` 로컬 웹 서버, HTTP API, 미리보기 화면, 브라우저 전용(Pyodide) 모드와 그 무전송 보장.

### Modified Capabilities
(없음 — `image-extraction` 의 파일 추출·링크 규칙은 그대로이고, 메모리 API 가 같은 규칙을 재사용한다)

## Impact

- 코드: 신규 `src/hwp2md/source.py`, `src/hwp2md/memory.py`, `src/hwp2md/web/{__init__,app,server}.py`, `src/hwp2md/web/static/{index.html,app.js,style.css,pyodide-runner.js,vendor/marked.min.js}`; 수정 `detect.py`, `hwp5/reader.py`, `hwpx/reader.py`, `convert.py`, `errors.py`, `__init__.py`, `cli.py`(serve 분기).
- 의존성: `[project.optional-dependencies] web = [starlette, uvicorn]`, dev 그룹에 starlette·uvicorn·httpx·playwright 추가, Playwright chromium 브라우저 다운로드. 브라우저 모드는 런타임에 jsDelivr CDN 의 Pyodide 와 lxml 패키지를 내려받는다.
- 공개 API: `hwp2md.convert_bytes`, `hwp2md.MemoryResult` export 추가. 기존 export·시그니처 불변.
- 테스트: 단위 3파일 신규, E2E 2파일 신규(+ conftest 픽스처 추가). 기존 단위 240 · E2E 46 은 수정 없이 통과해야 한다.
