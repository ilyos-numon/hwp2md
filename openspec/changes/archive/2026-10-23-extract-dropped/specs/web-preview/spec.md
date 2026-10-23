## ADDED Requirements

### Requirement: 화면은 건너뛴 요소를 경고로 보여 준다
`GET /` 화면과 `design/v3/app.html` 변환 화면은 변환 성공 응답의 `skipped` 가 비어 있지 않으면 `#skipped`(role=status) 영역에 `변환하지 못한 요소: <라벨> <n>개[ · …]` 를 보여 주고, 비어 있으면 `#skipped` 를 숨겨야 한다(SHALL). 문구는 `skipped[].label` 을 그대로 쓰고 화면이 따로 라벨 표를 갖지 않는다. `design/v3/app.html` 의 `#skipped` 에는 `docs/extraction-limits.md` 로 가는 링크가 있다. 라벨은 `textContent` 로 넣는다.

#### Scenario: 머리말 있는 문서
- **WHEN** 서버 모드에서 머리말 컨트롤 1개가 있는 합성 HWPX 를 넣는다
- **THEN** `#skipped` 가 보이고 글자에 `머리말·꼬리말 1개` 가 있다

#### Scenario: 건너뜀 없는 문서
- **WHEN** 단락만 있는 합성 문서를 넣는다
- **THEN** `#skipped` 는 숨겨져 있다

### Requirement: 화면은 보호 문서 오류를 구분해 안내한다
화면 오류 문구 표는 `drm` → `문서보안(DRM)이 적용된 파일이라 변환할 수 없습니다. 보안 프로그램에서 해제한 뒤 다시 시도하세요`, `encrypted` → `암호가 설정된 문서라 변환할 수 없습니다. 한글에서 암호를 해제한 뒤 다시 시도하세요`, `unsupported` → `지원하지 않는 HWP 문서라 변환할 수 없습니다` 를 가져야 하고(SHALL), 서버 모드와 브라우저 모드가 같은 문구를 보여 준다.

#### Scenario: DRM 파일
- **WHEN** 서버 모드에서 `9B 20` + `DRMONE` 서명으로 시작하는 합성 파일을 넣는다
- **THEN** `body[data-state="error"]` 이고 `#error` 글자에 `문서보안(DRM)` 이 있다

### Requirement: 화면과 문서는 한컴 공개 문서 참고 사실과 추출 한계를 밝힌다
README, `src/hwp2md/__init__.py` 모듈 docstring, `src/hwp2md/web/static/index.html`, `design/v3/index.html`, `design/v3/app.html` 은 문구 `본 제품은 한글과컴퓨터의 한/글 문서 파일(.hwp) 공개 문서를 참고하여 개발하였습니다.` 를 그대로 담아야 한다(SHALL). `design/v3/index.html` 의 `#limits` 목록은 `docs/extraction-limits.md` 의 "불가"·"부분" 행을 한 줄씩 보여 주고 문서 링크를 갖는다.

#### Scenario: 문구 존재
- **WHEN** 다섯 파일에서 위 문구를 고정 문자열로 찾는다
- **THEN** 다섯 파일 모두 1회 이상 나온다
