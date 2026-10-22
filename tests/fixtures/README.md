# tests/fixtures

실제 샘플 문서 보관 위치. **이 폴더의 문서 파일은 전부 gitignore 대상**이라 커밋되지 않는다 (이 README와 .gitkeep만 추적).

- `*.hwp` (이 폴더 바로 아래) — HWP 5.0 샘플. E2E `test_real_fixture_converts`가 자동으로 찾아 변환을 검증한다.
- `unsupported/hwpx/` — HWPX(zip/XML) 샘플. HWPX 태스크에서 사용 예정.
- `unsupported/hwp3/` — HWP 3.0(구형) 샘플. 지원 계획 없음. 거절 메시지 확인용.

E2E는 하위 폴더를 재귀 탐색하지 않으므로, 아직 지원하지 않는 포맷은 하위 폴더에 두면 테스트가 실패하지 않는다.
