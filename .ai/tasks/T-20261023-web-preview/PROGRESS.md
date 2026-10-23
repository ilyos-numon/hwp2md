# PROGRESS — T-20261023-web-preview

> append-only.

---

## [2026-10-23 10:02] S0 | planner(opus) | DONE
- 한 일: PLAN.md 작성 (fable 중단 → 사용자 지시로 opus)
- 변경 파일(미커밋, .ai 제외): openspec/changes/web-preview/design.md openspec/changes/web-preview/specs/web-preview/spec.md 
- 커밋: 7de7720 [T-20261023-web-preview][plan] web preview: memory API, hwp2md serve, browser-only Pyodide mode
- 다음: 사용자 승인 대기

## [2026-10-23 10:06] S1 | orchestrator | START
- 한 일: 의존성 추가와 브라우저 설치
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 1ba4225 [T-20261023-web-preview][plan] approved (§7 기본값)

## [2026-10-23 10:06] S1 | runner(haiku) | BLOCKED
- 한 일: 설치 명령이 Bash 권한 거부로 실행 안 됨
- 변경 파일(미커밋, .ai 제외): CLAUDE.md pyproject.toml 
- 커밋: 1ba4225 [T-20261023-web-preview][plan] approved (§7 기본값)
- 다음: 사용자 결정: 설치를 메인 세션에서 실행할지
- 메모: pyproject·CLAUDE.md 수정은 미커밋 상태

## [2026-10-23 10:07] S1 | orchestrator | DONE
- 한 일: 의존성 추가와 브라우저 설치 검증 통과 (uv sync, chromium, wheel extra=1, 286 passed)
- 변경 파일(미커밋, .ai 제외): CLAUDE.md openspec/changes/web-preview/tasks.md pyproject.toml uv.lock 
- 커밋: 1ba4225 [T-20261023-web-preview][plan] approved (§7 기본값)
- 다음: S2 시작
- 메모: runner Bash 권한 거부 → 사용자 선택 1로 메인 세션이 직접 실행

## [2026-10-23 10:07] S2 | hook | AUTO
- 한 일: 도구 호출 15회 경과
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 5e68dd4 [T-20261023-web-preview][s1] deps: web extra, dev starlette/uvicorn/httpx/playwright

## [2026-10-23 10:07] S2 | orchestrator | START
- 한 일: Pyodide 스파이크
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 5e68dd4 [T-20261023-web-preview][s1] deps: web extra, dev starlette/uvicorn/httpx/playwright

## [2026-10-23 10:12] S2 | hook | AUTO
- 한 일: 도구 호출 30회 경과
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 5e68dd4 [T-20261023-web-preview][s1] deps: web extra, dev starlette/uvicorn/httpx/playwright

## [2026-10-23 10:13] S2 | implementer(opus) | DONE
- 한 일: 스파이크 SPIKE OK 5/5
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 5e68dd4 [T-20261023-web-preview][s1] deps: web extra, dev starlette/uvicorn/httpx/playwright
- 다음: S3
- 메모: PYODIDE_VERSION=0.27.7 LXML=5.2.1(build 0) LOAD=65.04,1.02,1.01 (콜드 로드 65s → S8/S10 타임아웃 넉넉히, goto wait_until=commit)

## [2026-10-23 10:13] S2 | orchestrator | DONE
- 한 일: Pyodide 스파이크 검증 통과
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 5e68dd4 [T-20261023-web-preview][s1] deps: web extra, dev starlette/uvicorn/httpx/playwright
- 다음: S3 시작

## [2026-10-23 10:13] S3 | orchestrator | START
- 한 일: 리더 바이트 입력
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 2d3fe1f [T-20261023-web-preview][s2] spike: pyodide 0.27.7 + lxml converts 5/5 samples

## [2026-10-23 10:14] S3 | hook | AUTO
- 한 일: 도구 호출 45회 경과
- 변경 파일(미커밋, .ai 제외): src/hwp2md/detect.py src/hwp2md/hwp5/reader.py src/hwp2md/hwpx/reader.py src/hwp2md/source.py 
- 커밋: 2d3fe1f [T-20261023-web-preview][s2] spike: pyodide 0.27.7 + lxml converts 5/5 samples

## [2026-10-23 10:16] S3 | subagent | DONE
- 한 일: 리더 바이트 입력
- 변경 파일(미커밋, .ai 제외): src/hwp2md/detect.py src/hwp2md/hwp5/reader.py src/hwp2md/hwpx/reader.py src/hwp2md/source.py tests/unit/test_source_bytes.py 
- 커밋: 2d3fe1f [T-20261023-web-preview][s2] spike: pyodide 0.27.7 + lxml converts 5/5 samples
- 다음: review PASS
- 메모: implementer(opus) DONE 19 tests, 305 passed; reviewer(sonnet) PASS

## [2026-10-23 10:16] S3 | orchestrator | DONE
- 한 일: 리더 바이트 입력 검증 통과
- 변경 파일(미커밋, .ai 제외): src/hwp2md/detect.py src/hwp2md/hwp5/reader.py src/hwp2md/hwpx/reader.py src/hwp2md/source.py tests/unit/test_source_bytes.py 
- 커밋: 2d3fe1f [T-20261023-web-preview][s2] spike: pyodide 0.27.7 + lxml converts 5/5 samples
- 다음: S4 — 메모리 변환 API 시작

## [2026-10-23 10:16] S4 | orchestrator | START
- 한 일: 메모리 변환 API
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 4ca0f5f [T-20261023-web-preview][s3] readers accept bytes via BytesIO

## [2026-10-23 10:16] S4 | hook | AUTO
- 한 일: 도구 호출 60회 경과
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 4ca0f5f [T-20261023-web-preview][s3] readers accept bytes via BytesIO

## [2026-10-23 10:19] S4 | hook | AUTO
- 한 일: 도구 호출 75회 경과
- 변경 파일(미커밋, .ai 제외): src/hwp2md/__init__.py src/hwp2md/convert.py src/hwp2md/errors.py src/hwp2md/memory.py tests/unit/test_memory.py 
- 커밋: 4ca0f5f [T-20261023-web-preview][s3] readers accept bytes via BytesIO

## [2026-10-23 10:19] S4 | subagent | DONE
- 한 일: 메모리 변환 API
- 변경 파일(미커밋, .ai 제외): src/hwp2md/__init__.py src/hwp2md/convert.py src/hwp2md/errors.py src/hwp2md/memory.py tests/unit/test_memory.py 
- 커밋: 4ca0f5f [T-20261023-web-preview][s3] readers accept bytes via BytesIO
- 다음: review PASS
- 메모: implementer(opus) DONE 55 tests, 360 passed; reviewer(sonnet) PASS

## [2026-10-23 10:19] S4 | orchestrator | DONE
- 한 일: 메모리 변환 API 검증 통과
- 변경 파일(미커밋, .ai 제외): src/hwp2md/__init__.py src/hwp2md/convert.py src/hwp2md/errors.py src/hwp2md/memory.py tests/unit/test_memory.py 
- 커밋: 4ca0f5f [T-20261023-web-preview][s3] readers accept bytes via BytesIO
- 다음: S5 — 웹 서버 앱 시작

## [2026-10-23 10:19] S5 | orchestrator | START
- 한 일: 웹 서버 앱
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 7bdaab6 [T-20261023-web-preview][s4] memory conversion API (convert_bytes, zip, payload)

## [2026-10-23 10:21] S5 | hook | AUTO
- 한 일: 도구 호출 90회 경과
- 변경 파일(미커밋, .ai 제외): src/hwp2md/web/ tests/unit/test_web_app.py 
- 커밋: 7bdaab6 [T-20261023-web-preview][s4] memory conversion API (convert_bytes, zip, payload)

## [2026-10-23 10:23] S5 | subagent | DONE
- 한 일: 웹 서버 앱
- 변경 파일(미커밋, .ai 제외): src/hwp2md/web/__init__.py src/hwp2md/web/app.py src/hwp2md/web/server.py src/hwp2md/web/static/index.html tests/unit/test_web_app.py 
- 커밋: 7bdaab6 [T-20261023-web-preview][s4] memory conversion API (convert_bytes, zip, payload)
- 다음: review PASS
- 메모: implementer(opus) DONE 22 tests, 382 passed; reviewer(sonnet) PASS; sanitize 1회 실패(테스트의 IPv4 리터럴→localhost); starlette TestClient httpx deprecation warning

## [2026-10-23 10:23] S5 | orchestrator | DONE
- 한 일: 웹 서버 앱 검증 통과
- 변경 파일(미커밋, .ai 제외): src/hwp2md/web/__init__.py src/hwp2md/web/app.py src/hwp2md/web/server.py src/hwp2md/web/static/index.html tests/unit/test_web_app.py 
- 커밋: 7bdaab6 [T-20261023-web-preview][s4] memory conversion API (convert_bytes, zip, payload)
- 다음: S6 — CLI serve 시작

## [2026-10-23 10:23] S6 | orchestrator | START
- 한 일: CLI serve
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 4e110e4 [T-20261023-web-preview][s5] web app: convert/zip/health/pkg endpoints, serve()

## [2026-10-23 10:23] S6 | hook | AUTO
- 한 일: 도구 호출 105회 경과
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 4e110e4 [T-20261023-web-preview][s5] web app: convert/zip/health/pkg endpoints, serve()

## [2026-10-23 10:24] S6 | subagent | DONE
- 한 일: CLI serve
- 변경 파일(미커밋, .ai 제외): CLAUDE.md src/hwp2md/cli.py 
- 커밋: 4e110e4 [T-20261023-web-preview][s5] web app: convert/zip/health/pkg endpoints, serve()
- 다음: review PASS
- 메모: implementer(opus) DONE; help diff 0, C8 exit=1, health OK, 382 passed; diff 21줄로 계약 그대로라 orchestrator 직접 리뷰(reviewer 생략)

## [2026-10-23 10:24] S6 | orchestrator | DONE
- 한 일: CLI serve 검증 통과
- 변경 파일(미커밋, .ai 제외): CLAUDE.md src/hwp2md/cli.py 
- 커밋: 4e110e4 [T-20261023-web-preview][s5] web app: convert/zip/health/pkg endpoints, serve()
- 다음: S7 — 서버 모드 화면 시작

## [2026-10-23 10:24] S7 | orchestrator | START
- 한 일: 서버 모드 화면
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 0001cd3 [T-20261023-web-preview][s6] cli: serve subcommand; claude.md dev commands

## [2026-10-23 10:25] S7 | hook | AUTO
- 한 일: 도구 호출 120회 경과
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 0001cd3 [T-20261023-web-preview][s6] cli: serve subcommand; claude.md dev commands

## [2026-10-23 10:28] S7 | hook | AUTO
- 한 일: 도구 호출 135회 경과
- 변경 파일(미커밋, .ai 제외): src/hwp2md/web/static/index.html src/hwp2md/web/static/app.js src/hwp2md/web/static/style.css src/hwp2md/web/static/vendor/ 
- 커밋: 0001cd3 [T-20261023-web-preview][s6] cli: serve subcommand; claude.md dev commands

## [2026-10-23 10:28] S7 | reviewer(sonnet) | RETRY
- 한 일: 리뷰 FAIL 1건: marked link/image href 미필터 → javascript: 링크 XSS
- 변경 파일(미커밋, .ai 제외): src/hwp2md/web/static/app.js src/hwp2md/web/static/index.html src/hwp2md/web/static/style.css src/hwp2md/web/static/vendor/marked.min.js .impeccable/ 
- 커밋: 0001cd3 [T-20261023-web-preview][s6] cli: serve subcommand; claude.md dev commands
- 다음: implementer(opus)에 허용목록 렌더러 수정 요청

## [2026-10-23 10:30] S7 | hook | AUTO
- 한 일: 도구 호출 150회 경과
- 변경 파일(미커밋, .ai 제외): src/hwp2md/web/static/app.js src/hwp2md/web/static/index.html src/hwp2md/web/static/style.css src/hwp2md/web/static/vendor/marked.min.js .impeccable/ 
- 커밋: 0001cd3 [T-20261023-web-preview][s6] cli: serve subcommand; claude.md dev commands

## [2026-10-23 10:31] S7 | subagent | DONE
- 한 일: 서버 모드 화면
- 변경 파일(미커밋, .ai 제외): src/hwp2md/web/static/app.js src/hwp2md/web/static/index.html src/hwp2md/web/static/style.css src/hwp2md/web/static/vendor/marked.min.js .impeccable/ 
- 커밋: 0001cd3 [T-20261023-web-preview][s6] cli: serve subcommand; claude.md dev commands
- 다음: review PASS
- 메모: implementer(opus) DONE; reviewer FAIL(javascript: 링크 XSS) → 허용목록 렌더러 수정 → 재리뷰 PASS, XSS OK 16/16; impeccable side-tab 오탐(blockquote) ignore-value 처리(.impeccable/config.json); serve() 포트 bind 시험이 TIME_WAIT 오판 → S8에 server.py 수정 추가

## [2026-10-23 10:31] S7 | orchestrator | DONE
- 한 일: 서버 모드 화면 검증 통과
- 변경 파일(미커밋, .ai 제외): src/hwp2md/web/static/app.js src/hwp2md/web/static/index.html src/hwp2md/web/static/style.css src/hwp2md/web/static/vendor/marked.min.js .impeccable/ 
- 커밋: 0001cd3 [T-20261023-web-preview][s6] cli: serve subcommand; claude.md dev commands
- 다음: S8 — 브라우저 전용 모드 시작
