# Tasks

## 1. 의존성

- [x] 1.1 `pyproject.toml` 에 `[project.optional-dependencies] web = ["starlette>=0.37", "uvicorn>=0.30"]` 과 dev 그룹 `starlette`·`uvicorn`·`httpx>=0.27`·`playwright>=1.45` 를 추가하고 `uv sync` + `uv run playwright install chromium` 후 네 모듈 import 와 wheel METADATA 의 `Provides-Extra: web` 을 확인한다

## 2. Pyodide 스파이크

- [x] 2.1 headless chromium 에서 CDN Pyodide + lxml 로 `src/hwp2md` + olefile 소스를 import 해 실제 샘플 5개를 변환하고, Markdown 이 네이티브 `convert()` 와 5/5 같음을 `logs/s2-spike.log` 의 `SPIKE OK 5/5` 로 확인한다

## 3. 바이트 입력 리더

- [x] 3.1 `src/hwp2md/source.py`(`Source`, `source_label`, `as_binary_io`)를 추가하고 `detect_format`·`read_hwp5_package`·`read_hwpx_package`·두 `read_blocks` 가 `Path | bytes` 를 받도록 바꾼다(bytes 는 `io.BytesIO` 로 감싼다, 경로 메시지 불변)
- [x] 3.2 `tests/unit/test_source_bytes.py` 로 샘플 5개의 bytes/경로 블록 동일성, 100바이트 입력이 경로로 열리지 않음, bytes 오류 메시지의 `<memory>` 라벨을 확인한다

## 4. 메모리 변환 API

- [ ] 4.1 `src/hwp2md/memory.py`(`MemoryImage`, `MemoryResult`, `safe_stem`, `convert_bytes`, `markdown_with_data_uris`, `build_zip`, `to_payload`, `error_code`, `convert_to_response`)와 `errors.py` 의 `EmptyInputError`·`InputTooLargeError` 를 추가한다
- [ ] 4.2 `convert()` 가 `memory` 와 같은 블록→결과 계산을 공유하도록 바꾸되 출력 바이트·`ConvertResult` 필드를 유지하고 `__init__.py` 에 `convert_bytes`·`MemoryResult` export 를 더한다
- [ ] 4.3 `tests/unit/test_memory.py` 로 샘플 5개 경로 변환 동일성, 쓰기 차단 가드 하 변환·zip, zip 엔트리·날짜, data URI, 오류 코드 5종, 웹 모듈 차단 subprocess 를 확인한다

## 5. 웹 서버 앱

- [ ] 5.1 `src/hwp2md/web/app.py` 의 `create_app()` 에 `GET /`·`/static/*`·`/api/health`·`POST /api/convert`·`POST /api/zip` 을 구현한다(Content-Length 상한 선검사, 디스크 쓰기 없음)
- [ ] 5.2 `build_runtime_zip()` 과 `GET /pkg/hwp2md.zip`(hwp2md 소스 중 `web/` 제외 + olefile `*.py`)을 구현하고 `src/hwp2md/web/server.py` 의 `serve()`(포트 사용 중 검사, 브라우저 열기, uvicorn 실행)를 구현한다
- [ ] 5.3 `tests/unit/test_web_app.py`(Starlette TestClient)로 엔드포인트 상태 코드·본문, 413 선검사, 런타임 zip 목록, 쓰기 차단 가드를 확인한다

## 6. CLI

- [ ] 6.1 `src/hwp2md/cli.py` 에 첫 인자 `serve` 분기(`--host`, `--port`, `--no-browser`, web extra 미설치 안내 종료 코드 1)를 추가하고 기존 변환 경로·`--help` 출력이 바뀌지 않았음을 확인한다

## 7. 화면

- [ ] 7.1 `src/hwp2md/web/static/index.html`·`app.js`·`style.css`·`vendor/marked.min.js` 로 서버 모드 화면(드롭·파일 선택·미리보기·원문·zip 다운로드·오류 표시)을 만들고 UI 스모크 스크립트 스크린샷으로 확인한다
- [ ] 7.2 `src/hwp2md/web/static/pyodide-runner.js` 와 `app.js`·`index.html` 의 토글로 브라우저 전용 모드(Pyodide 로딩 상태, 브라우저 안 변환·zip)를 만들고 UI 스모크 스크립트로 무전송·출력 동일을 확인한다

## 8. E2E

- [ ] 8.1 `tests/e2e/test_web_api.py`(+ `conftest.py` 서버 픽스처)로 실제 `hwp2md serve` 프로세스의 health·convert·zip·오류·저장 흔적 없음·포트 사용 중·extra 미설치를 검증한다
- [ ] 8.2 `tests/e2e/test_web_ui.py` 로 서버·브라우저 모드 화면, 무전송 요청 기록, 5개 샘플 두 모드·CLI 출력 동일, zip 다운로드, 오류 표시, 스크린샷을 검증하고 E2E 전체 통과를 확인한다

## 9. 문서

- [ ] 9.1 `README.md` 에 `hwp2md[web]` 설치·`hwp2md serve`·브라우저 전용 모드(CDN 필요)·`./serve` 주의를, `docs/decisions.md` 에 결정 4건을 적고 `sanitize-check.sh` OK 를 확인한다

## 10. 리뷰·기록

- [ ] 10.1 reviewer 가 diff·스크린샷·로그를 성공 기준 표와 대조하고 scribe 가 RESULT.md·STATE.md 를 쓴다
