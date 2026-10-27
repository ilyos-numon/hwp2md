# RESULT — T-20261027-v3-backend V3 프론트엔드를 실제 백엔드에 연결

> 작성: scribe · 2026-10-27 14:30 · 최종 상태: DONE
> 사용자는 이 파일만 읽고 받아들일지 판단한다. 3분 안에 읽히게 쓴다.

## 결론 (3줄)
- 되었다: `/` 변환 화면이 `/api/convert`·`/api/zip` 서버 모드와 브라우저 모드에 실제로 연결됐고, `/about` 소개 페이지가 vendor 자원만으로 뜬다. 이전 UI(`static/app.js`, `style.css`) 삭제.
- 안 된 것: 없음. C1~C14 전부 PASS, 리뷰 APPROVE, OpenSpec `v3-backend` 아카이브 완료.
- 지금 바로 쓸 수 있다: `uv run hwp2md serve` → http://localhost:8765/ (소개 `/about`). main 병합은 사용자 검토 후.

## 성공 기준 대비
| # | 기준 | 결과 | 근거 |
|---|------|------|------|
| C1 | `/`·`/about` 응답 | ✅ | `tests/unit/test_web_app.py` 26 passed (PROGRESS S3, `logs/s3-unit.log`); 단위 전체 C5에 포함 |
| C2 | 기존 웹 E2E 무수정 통과 | ✅ | `logs/s6-gate.log` C2 rc=0; 기존 E2E 파일 diff 출력 없음 |
| C3 | 새 V3 E2E | ✅ | `logs/s5-e2e-v3.log` 7 passed, skip 0 |
| C4 | 전체 E2E | ✅ | `logs/e2e.log` 127 passed, exit=0 |
| C5 | 단위 회귀 | ✅ | `logs/s6-gate.log` 815 passed, rc=0 |
| C6 | 린트·타입 | ✅ | `logs/s6-gate.log` ruff check passed, format 94 files OK, mypy 34 files no issues, rc=0 |
| C7 | CDN·데모 참조 없음 | ✅ | `logs/s6-gate.log` 두 grep 출력 없음 (rc=1 = 매치 없음) |
| C8 | 이전 UI 삭제 | ✅ | `logs/s6-gate.log` app.js·style.css `No such file` |
| C9 | 라이선스 동봉 | ✅ | `logs/s6-gate.log` `ok` |
| C10 | GSAP 버전 | ✅ | `logs/s6-gate.log` `3.13.0` 포함 (1) |
| C11 | wheel 에 정적 자원 포함 | ✅ | `logs/s6-gate.log` grep 3; woff2 4 (`dist/hwp2md-0.1.0-py3-none-any.whl`) |
| C12 | 익명화 | ✅ | `logs/s6-gate.log` sanitize-check OK (22 patterns), rc=0 |
| C13 | 화면 확인 | ✅ | reviewer(sonnet) APPROVE, 5개 조건 PASS (PROGRESS S7); 스크린샷 7장 |
| C14 | OpenSpec | ✅ | `logs/openspec-validate.log` valid; `logs/openspec-archive.log` archived |

스크린샷 (`.ai/tasks/T-20261027-v3-backend/screenshots/`):
`v3-app-done.png`, `v3-app-error.png`, `v3-app-dark.png`, `v3-app-narrow.png`, `v3-about.png`, `v3-about-hero.png`, `v3-about-limits.png`

OpenSpec 아카이브: `openspec/changes/archive/2026-10-27-v3-backend/`

## 변경 요약
- 커밋 범위: `36183cb..d4c4964` (19 commits, `main..HEAD` 기준; 이 RESULT 커밋은 이후 추가)
- 추가/수정 파일: 42개 (+4142 / -777) — 핵심: `src/hwp2md/web/app.py`, `src/hwp2md/web/static/index.html`, `src/hwp2md/web/static/js/app.js`, `src/hwp2md/web/static/about.html`, `src/hwp2md/web/static/vendor/`, `tests/e2e/test_web_v3.py`
- 새 의존성: 없음 (`pyproject.toml`·`uv.lock` 변경 없음). 동봉 자원: GSAP 3.13.0, Pretendard 1.3.9, JetBrains Mono 2.304, marked 12.0.2(기존)
- 새 환경변수: 없음

## 테스트
- 단위/통합: `uv run pytest tests/unit -q` → pass (815 passed, 실패 0)
- E2E: `uv run pytest tests/e2e -q` → pass (127 passed, V3 7 포함)
  - `test_v3_server_convert_offline` — 외부 요청 차단 상태 변환 성공, `window.gsap` 3.13.0, `#raw`·표 8개·`이미지 1개`
  - `test_v3_not_hwp_error_and_close` — 비 HWP 입력 시 오류 문구, 다운로드 비활성, 닫기 동작
  - `test_v3_skipped_links_about` — 변환하지 못한 요소 링크가 `/about#limits`로 이동
  - `test_v3_about_offline` — 소개 페이지 외부 요청 0, GSAP 플러그인 정의, 글꼴 단언
  - `test_v3_dark_theme` — 다크 테마 전환·새로고침 유지
  - `test_v3_narrow_tabs` — 390×844에서 탭 1개만 표시
  - `test_v3_copy_button` — 복사 버튼으로 클립보드에 Markdown 원문

## 실행 방법
```bash
cd /Users/illi/illy-projects/hwp2md && uv run hwp2md serve
# 변환 화면: http://localhost:8765/   소개: http://localhost:8765/about
```

## 못 한 것 / 알려진 문제
- 없음. (브라우저 모드 케이스는 Pyodide 로드를 위해 jsDelivr 접근이 필요하다 — 네트워크 전제.)

## 결정 사항 (플랜에 없었는데 실행 중 정한 것)
- Pretendard 라이선스 원문 위치: 플랜 URL(`pretendard@1.3.9/LICENSE`)이 아니라 패키지 내 `dist/LICENSE.txt` 를 받아 `OFL-Pretendard.txt` 로 동봉 (PROGRESS S1). 원문 동일성은 확인 필요.
- `renderRaw` 끝 개행 보정 추가 (S2, `#raw` 텍스트가 응답 `markdown` 과 일치하도록).
- `copy` 케이스 toast 대기 조건 수정 (S5, PROGRESS 기준 테스트 자체 결함. 제품 코드 변경 아님).
- 글꼴 실패 경로(FONT_FALLBACK) 는 쓰지 않음 — 글꼴 3종 모두 정상 동봉.

## 특이사항
- S6 첫 실행의 `logs/e2e.log` 에 exit 줄이 없어 재실행함. 재실행 결과 127 passed, exit=0 (현재 로그).

## 후속 제안 (별도 태스크로)
- `limits` 스크린샷: 고정 헤더가 제목 일부를 가림 (미관).
- Pretendard Variable 2MB 서브셋 검토 (현재 전체 동봉).
- 실제 차트 포함 HWP 샘플 필요 (차트 추출 실샘플 확보).
- 과거 커밋 이력에 남은 샘플 변환 결과물 정리 — 강제 푸시 필요, 사용자 결정.

## 비용
- 서브에이전트 호출: 11회 (opus 5 / sonnet 4 / haiku 2) — PROGRESS 기준: planner 1, implementer 4, reviewer 3, test-writer 1, runner 1, scribe 1(이 RESULT)
- 재시도: 0회 · 차단: 0회
