# memory-conversion Specification (delta)

## Purpose
파일 시스템에 아무것도 쓰지 않고 HWP 5.0·HWPX 바이트를 Markdown·이미지·zip·JSON 으로 바꾸는 라이브러리 API. 웹 서버와 브라우저(Pyodide)가 같은 함수를 호출해 같은 결과를 낸다.

## ADDED Requirements

### Requirement: 바이트 입력을 디스크 쓰기 없이 변환한다
라이브러리는 `hwp2md.memory.convert_bytes(data: bytes, filename: str)` 를 제공해야 하고(SHALL), 이 함수는 파일·임시 파일·디렉터리를 하나도 만들지 않고 `MemoryResult` 를 돌려줘야 한다. `MemoryResult.markdown` 은 같은 바이트를 디스크 경로로 `convert()` 했을 때 쓰이는 `.md` 내용과 바이트 단위로 같아야 하고, `images` 는 `convert()` 가 `<stem>_images/` 에 쓰는 파일과 이름·바이트·순서가 같아야 한다. `stem` 은 `filename` 의 마지막 경로 구성 요소(`/`·`\` 기준)의 stem 이며, 비어 있거나 `.`·`..` 이면 `document` 다.

#### Scenario: 실제 샘플 5개의 경로 변환과 동일
- **WHEN** `tests/fixtures/*.hwp` 2개와 `tests/fixtures/hwpx/*.hwpx` 3개의 바이트를 각각 `convert_bytes(data, 파일명)` 으로 변환한다
- **THEN** 각 `markdown` 이 `convert(경로, tmp)` 가 쓴 `.md` 바이트와 같고, 카운트(단락·표·제목·이미지)가 `ConvertResult` 와 같으며, `브라더 공공기관 보고서 양식.hwpx` 는 `images` 가 `img_001.png` 1개(46249바이트)다

#### Scenario: 변환 중 파일 쓰기 시도 없음
- **WHEN** `open()` 의 쓰기 모드, `Path.write_bytes/write_text`, `tempfile` 생성 함수를 호출 즉시 예외가 나도록 바꾼 상태에서 이미지가 있는 문서를 `convert_bytes` 로 변환하고 `build_zip` 까지 호출한다
- **THEN** 예외 없이 결과가 나온다

#### Scenario: 1536바이트 미만 입력도 경로로 오인하지 않는다
- **WHEN** 길이 100바이트의 임의 바이트를 `convert_bytes` 로 변환한다
- **THEN** 해당 바이트를 파일 경로로 열려는 시도 없이 `NotHwpFileError` 가 난다

### Requirement: 기존 경로 API 와 CLI 는 바뀌지 않는다
`convert(path, out_dir)` 의 시그니처·반환 필드·파일 출력과 CLI `hwp2md INPUT [-o OUT_DIR]` 의 표준 출력·표준 오류·종료 코드는 이 변경 이전과 같아야 한다(SHALL). 경로 입력에서 나는 오류 메시지 문자열도 바뀌지 않는다.

#### Scenario: 기존 테스트 무수정 통과
- **WHEN** 이 변경 전부터 있던 `tests/unit` 240개와 `tests/e2e` 46개를 수정 없이 실행한다
- **THEN** 전부 통과한다

### Requirement: 미리보기용 data URI Markdown 과 zip 을 만든다
라이브러리는 `markdown_with_data_uris(result)` 와 `build_zip(result)` 를 제공해야 한다(SHALL). `markdown_with_data_uris` 는 `markdown` 안의 각 이미지 링크 목적지 `<image_dir 의 공백을 %20 으로 바꾼 것>/<file_name>` 을 `data:<mime>;base64,<바이트>` 로 바꾼 문자열이다(mime: png→image/png, jpg·jpeg→image/jpeg, gif→image/gif, bmp→image/bmp, 그 밖→application/octet-stream). `build_zip` 은 `<stem>.md`(= `markdown` UTF-8)와 `<stem>_images/<file_name>`(이미지가 있을 때만) 엔트리를 갖는 zip 바이트이고, 모든 엔트리의 날짜는 1980-01-01 00:00:00 이다.

#### Scenario: 이미지 있는 HWPX 의 zip
- **WHEN** `브라더 공공기관 보고서 양식.hwpx` 를 변환해 `build_zip` 한다
- **THEN** zip 엔트리 이름은 정확히 `브라더 공공기관 보고서 양식.md` 와 `브라더 공공기관 보고서 양식_images/img_001.png` 2개이고, 압축을 풀면 `convert()` 디스크 출력과 바이트가 같다

#### Scenario: 이미지 없는 문서의 미리보기
- **WHEN** `form210001070268.hwp` 를 변환해 `markdown_with_data_uris` 한다
- **THEN** 결과가 `markdown` 과 같고, zip 엔트리는 `form210001070268.md` 1개뿐이다

### Requirement: 응답 페이로드와 오류 코드는 한 함수가 정한다
라이브러리는 `convert_to_response(data, filename) -> (status, body)` 를 제공해야 하고(SHALL), 서버 모드 HTTP 응답과 브라우저 모드 결과는 모두 이 함수의 `body` 를 JSON 으로 쓴다. 성공 시 status 200, body 는 `name`·`markdown`·`preview_markdown`·`image_dir`·`images[{file_name,mime,size}]`·`counts{paragraphs,tables,headings,images}` 키를 갖는다. 실패 시 body 는 `{"error": {"code", "message"}}` 이고 code·status 는 빈 입력 `empty`/400, 50MB(52428800바이트) 초과 `too_large`/413, `NotHwpFileError` `not_hwp`/415, `UnsupportedHwpError` `unsupported`/415, 그 밖의 모든 예외 `convert_failed`/422 다.

#### Scenario: HWP 가 아닌 입력
- **WHEN** `b"hello"` 를 `convert_to_response(b"hello", "a.hwp")` 로 넘긴다
- **THEN** `(415, {"error": {"code": "not_hwp", "message": ...}})` 이 나오고 예외는 전파되지 않는다

#### Scenario: 빈 입력
- **WHEN** `b""` 를 넘긴다
- **THEN** status 400, code `empty` 다

### Requirement: 기본 설치는 웹 의존성 없이 동작한다
`import hwp2md` 와 `hwp2md.memory` 는 starlette·uvicorn 을 import 하지 않아야 한다(SHALL). 두 모듈이 import 불가능한 환경에서도 `convert`·`convert_bytes`·CLI 변환은 동작한다.

#### Scenario: 웹 모듈 차단 상태에서 변환
- **WHEN** `sys.modules["starlette"] = None`, `sys.modules["uvicorn"] = None` 을 먼저 실행한 파이썬 프로세스에서 `import hwp2md` 후 `convert_bytes` 를 호출한다
- **THEN** 변환이 성공하고, import 후 `sys.modules` 에 `hwp2md.web` 이 없다
