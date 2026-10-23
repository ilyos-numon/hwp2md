# RESULT — T-20261023-web-preview hwp2md 웹 미리보기 (메모리 변환 API + `hwp2md serve` + 브라우저 전용 모드)

> 작성: scribe · 2026-10-23 10:55 · 최종 상태: DONE
> 사용자는 이 파일만 읽고 받아들일지 판단한다. 3분 안에 읽히게 쓴다.

## 결론 (3줄)
- 되는 것: `hwp2md serve` 로컬 화면에서 HWP/HWPX 미리보기·원문 보기·zip(.md+이미지) 다운로드, "브라우저 안에서만 처리" 모드(파일 서버 전송 0), 메모리 변환 API. 성공 기준 C1~C18 전부 통과.
- 안 되는 것: 브라우저 모드 첫 로딩 약 65초, 인터넷(jsDelivr) 필요. 나머지 알려진 한계는 아래 참고.
- 지금 바로 쓸 수 있는가: 예. 실행은 `cd /Users/illi/illy-projects/hwp2md && uv run hwp2md serve` 후 http://localhost:8765 . main 병합은 사용자 검토 후 (미커밋 변경 있음, 아래 참고).

## 성공 기준 대비
| # | 기준 | 결과 | 근거 |
|---|------|------|------|
| C1 | 단위 테스트 회귀 없음 (≥284) | ✅ | `uv run pytest tests/unit -q` → 338 passed, 1 warning |
| C2 | E2E 전체 (≥66) | ✅ | `.ai/tasks/T-20261023-web-preview/logs/e2e.log` → 70 passed, exit=0, 72초 |
| C3 | 린트·타입 | ✅ | ruff check/format 통과, mypy `Success: no issues found in 23 source files` |
| C4 | 메모리 API = 경로 API | ✅ | `-k same_as_convert` → 5 passed |
| C5 | 디스크 쓰기 없음 (정적) | ✅ | grep 출력 0줄 (memory.py, web/app.py, source.py) |
| C6 | 디스크 쓰기 없음 (동적) | ✅ | E2E `test_no_files_written` pass |
| C7 | 기본 설치는 웹 없이 동작 | ✅ | `hwp2md.web` in sys.modules → False, 종료 0 |
| C8 | extra 미설치 안내 | ✅ | stderr `hwp2md: error: web extra not installed — pip install 'hwp2md[web]'`, exit=1 |
| C9 | 기존 CLI 불변 | ✅ | `--help` diff 0줄, 기존 E2E pass |
| C10 | 서버 기동 health | ✅ | `curl /api/health` → `{"ok":true,"version":"0.1.0"}` |
| C11 | 브라우저 모드 무전송 | ✅ | E2E `test_browser_mode_sends_no_file` pass (non-GET 0, `/api/` 0). 서버 모드 대조군 POST 1, 본문 길이 = 파일 크기 |
| C12 | 두 모드 출력 동일 | ✅ | E2E `test_modes_produce_identical_markdown` pass (5개 샘플, server == browser == CLI) |
| C13 | wheel 정적 파일·extra 선언 | ✅ | static 파일 5개, `Provides-Extra: web` 1 |
| C14 | 화면 — 서버 모드 | ✅ | `.ai/tasks/T-20261023-web-preview/screenshots/web_server_preview.png` |
| C15 | 화면 — 브라우저 모드 | ✅ | `.ai/tasks/T-20261023-web-preview/screenshots/web_browser_preview.png` |
| C16 | 화면 — 오류 | ✅ | `.ai/tasks/T-20261023-web-preview/screenshots/web_error.png` |
| C17 | OpenSpec | ✅ | `openspec validate web-preview` → valid, tasks 17/17 완료 |
| C18 | 익명화 | ✅ | `scripts/sanitize-check.sh hwp2md` → OK |

## 변경 요약
- 커밋 범위: `7ef9aa1..2cc095c` (15 commits, `main..ai/T-20261023-web-preview`)
- 추가/수정 파일: 62개 (+5864 / -51) — 핵심: `src/hwp2md/memory.py`, `src/hwp2md/web/app.py`, `src/hwp2md/web/static/`, `src/hwp2md/cli.py`, `pyproject.toml`
- OpenSpec: `openspec/changes/archive/2026-10-23-web-preview/` 로 아카이브. main spec 신규 `openspec/specs/memory-conversion/`, `openspec/specs/web-preview/` (archive 로그 기준 추가 항목 +5 / +4)
- 새 의존성: optional extra `web` = starlette>=0.37, uvicorn>=0.30. 개발용 starlette/uvicorn/httpx/playwright. 브라우저 측은 Pyodide 0.27.7 (CDN 로드)
- 새 환경변수: 없음 (grep 확인)

## 테스트
- 단위/통합: `uv run pytest tests/unit -q` → pass (338 passed, 1 warning)
- E2E: `uv run pytest tests/e2e -q` → pass (70 passed, exit=0, 72초), 케이스 목록:
  - `test_web_api.py` — 변환 API, 디스크 무기록(`test_no_files_written`), serve CLI
  - `test_web_ui.py` — 서버/브라우저 모드 화면, 브라우저 모드 무전송, 두 모드 출력 동일, 스크린샷 3장
  - 기존 CLI E2E — 회귀 없음

## 실행 방법
```bash
cd /Users/illi/illy-projects/hwp2md && uv run hwp2md serve
# → http://localhost:8765  (다른 포트: --port N, 브라우저 자동 열기 끔: --no-browser)
```

## 못 한 것 / 알려진 문제
- 브라우저 모드 첫 로딩 약 65초 — Pyodide 다운로드 때문 — 캐시 후 개선 여부 미측정
- 브라우저 모드는 인터넷(jsDelivr) 필요 — 오프라인 번들은 미구현 — 필요 시 별도 태스크
- starlette 1.9 TestClient 의 httpx 사용 중단 경고 1건 — 기능 영향 없음 — 테스트 라이브러리 갱신 시 정리
- 프로토콜 상대 URL(`//host`) 링크는 허용 — XSS 아님 — 필요 시 정책 강화
- 기본 포트 8765 는 다른 로컬 프로젝트와 겹칠 수 있음 — `--port` 로 변경
- 미커밋 변경 있음: OpenSpec 아카이브·main spec 신규 3 경로, change 파일 6개 삭제, `.ai` 기록 2 파일 — 병합 전에 커밋 필요 (git 조작은 scribe 범위 밖이라 미실행)

## 결정 사항 (플랜에 없었는데 실행 중 정한 것)
- S7 리뷰 FAIL: marked 의 link/image 주소 미필터로 `javascript:` 링크 XSS 가능 → 허용목록 렌더러로 수정. xss_check 16/16 통과.
- S8 플랜 외 수정: `serve()` 포트 시험이 TIME_WAIT 를 사용 중으로 오판 → `SO_REUSEADDR` 적용 + 회귀 테스트 2개 추가.
- S9/S11 병렬 실행 실패: worktree 가 원격 main 의 스캐폴드 커밋에서 생성됨 → 메인 체크아웃에서 순차 실행.
- S10 서버 모드 대조군: Chromium `post_data_buffer=None` 때문에 본문 검증을 Content-Length == 파일 크기로 대체.
- S1 설치: 서브에이전트 Bash 권한 거부 → 사용자 선택에 따라 메인 세션이 실행.
- S6·S11: diff 가 작아 orchestrator 직접 리뷰.
- sanitize 가 루프백 IP 리터럴과 4단 버전 문자열을 IP 로 탐지 → 문서·테스트에서 `localhost` 로 통일.

## 후속 제안 (별도 태스크로)
- 브라우저 모드 오프라인 지원 (Pyodide·패키지 로컬 번들)
- 기본 포트 충돌 시 자동 다음 포트 선택

## 비용
- 서브에이전트 호출: 확인 필요 (PROGRESS 기록이 모델별로 불완전하여 집계 불가)
- 재시도: 2회 (S7 reviewer, S9 test-writer) · 차단: 1회 (S1 runner, 권한 거부 → 메인 세션 실행으로 해제)
