# tests/fixtures

실제 샘플 문서 보관 위치. **이 폴더의 문서 파일은 전부 gitignore 대상**이라 커밋되지 않는다 (이 README와 .gitkeep만 추적).

- `*.hwp` (이 폴더 바로 아래) — HWP 5.0 샘플. E2E `test_real_fixture_converts`가 자동으로 찾아 변환을 검증한다. 파일명이 `tests/e2e/test_cli_heading.py`의 `REAL_EXPECTED`에 있으면 (단락, 표, 제목) 수까지 비교한다.
- `hwpx/*.hwpx` — HWPX(zip/XML) 샘플. E2E `test_real_hwpx_fixture_converts`가 자동으로 찾아 변환을 검증한다. 파일명이 `tests/e2e/test_cli_hwpx.py`의 `REAL_HWPX_EXPECTED`에 있으면 단락·표 수까지 비교한다. 파일명이 `tests/e2e/test_cli_heading.py`의 `REAL_EXPECTED`에 있으면 (단락, 표, 제목) 수까지 비교한다.
- `unsupported/hwp3/` — HWP 3.0(구형) 샘플. 지원 계획 없음. 거절 메시지 확인용.

E2E는 지정한 폴더만 탐색하므로, 아직 지원하지 않는 포맷은 `unsupported/` 아래에 두면 테스트가 실패하지 않는다.

개요(제목) 수준이 있는 샘플을 추가할 때: 한글에서 스타일 "개요 1"~"개요 7"을 적용한 문서를 이 폴더(HWP 5.0) 또는 `hwpx/`(HWPX)에 넣고, `REAL_EXPECTED`에 `(단락, 표, 제목)` 기대값을 추가한다. 기대값이 없으면 변환 성공과 "Markdown 제목 줄 수 == CLI 제목 수"만 검사한다.
