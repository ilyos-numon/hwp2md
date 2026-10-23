## MODIFIED Requirements

### Requirement: 기존 경로 API 와 CLI 는 바뀌지 않는다
`convert(path, out_dir)` 의 시그니처와 기존 반환 필드, CLI `hwp2md INPUT [-o OUT_DIR]` 의 표준 출력 1·2·3행 형식, 기존 오류 메시지 문자열(`not an HWP 5.0 file:`, `unsupported HWP file`, `file not found:`)과 종료 코드 규칙(0 성공, 1 변환 오류, 2 파일 없음, 3 HWP 아님·지원 안 함)은 바뀌지 않아야 한다(SHALL). 허용되는 변경은 추가뿐이다: `ConvertResult.skipped` 필드(기본값 `()`), 건너뛴 요소가 있을 때 표준 출력 마지막 `  건너뜀: …` 행, `unsupported HWP file` 뒤 괄호 안 사유(`(DRM protected)`, `(password protected)`).

#### Scenario: 기존 테스트 무수정 통과
- **WHEN** 이 변경 전부터 있던 `tests/unit`·`tests/e2e` 를 실행한다
- **THEN** 플랜 `.ai/tasks/T-20261023-extract-dropped/PLAN.md` §1 "의도적으로 바뀌는 기존 테스트" 목록에 없는 테스트는 수정 없이 통과한다

#### Scenario: 보호 문서 메시지 호환
- **WHEN** FileHeader 속성 `0x3` 인 합성 문서를 CLI 로 변환한다
- **THEN** 종료 코드 3 이고 표준 오류에 `unsupported HWP file` 이 그대로 들어 있다

### Requirement: 응답 페이로드와 오류 코드는 한 함수가 정한다
라이브러리는 `convert_to_response(data, filename) -> (status, body)` 를 제공해야 하고(SHALL), 서버 모드 HTTP 응답과 브라우저 모드 결과는 모두 이 함수의 `body` 를 JSON 으로 쓴다. 성공 시 status 200, body 는 `name`·`markdown`·`preview_markdown`·`image_dir`·`images[{file_name,mime,size}]`·`counts{paragraphs,tables,headings,images}`·`skipped[{kind,label,count}]` 키를 갖는다(`skipped` 는 건너뛴 것이 없으면 `[]`). 실패 시 body 는 `{"error": {"code", "message"}}` 이고 code·status 는 빈 입력 `empty`/400, 50MB(52428800바이트) 초과 `too_large`/413, `NotHwpFileError` `not_hwp`/415, `DrmProtectedError` `drm`/415, `EncryptedDocumentError` `encrypted`/415, 그 밖의 `UnsupportedHwpError` `unsupported`/415, 그 밖의 모든 예외 `convert_failed`/422 다.

#### Scenario: HWP 가 아닌 입력
- **WHEN** `b"hello"` 를 `convert_to_response(b"hello", "a.hwp")` 로 넘긴다
- **THEN** `(415, {"error": {"code": "not_hwp", "message": ...}})` 이 나오고 예외는 전파되지 않는다

#### Scenario: 빈 입력
- **WHEN** `b""` 를 넘긴다
- **THEN** status 400, code `empty` 다

#### Scenario: 건너뜀 보고
- **WHEN** 머리말 컨트롤 1개가 있는 합성 HWPX 를 넘긴다
- **THEN** status 200 이고 `body["skipped"] == [{"kind": "header_footer", "label": "머리말·꼬리말", "count": 1}]` 이다
