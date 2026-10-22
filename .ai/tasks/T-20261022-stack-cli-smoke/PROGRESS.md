# PROGRESS — T-20261022-stack-cli-smoke

> append-only.

---

## [2026-10-22 11:37] S0 | hook | AUTO
- 한 일: 자동 체크포인트 (stop)
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 308f1fb chore: add agent workflow scaffold (.ai, tests/e2e, CLAUDE.md command block)
- 메모: STATE.md의 '다음 행동' 확인 후 이어서

## [2026-10-22 11:53] S0 | hook | AUTO
- 한 일: 도구 호출 15회 경과
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: f37049c [T-20261022-stack-cli-smoke][S0][wip] auto checkpoint (stop)

## [2026-10-22 11:53] S0 | planner(fable) | DONE
- 한 일: PLAN.md 작성 (9단계, §7 질문 6개), 셀프체크 10/10
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: f37049c [T-20261022-stack-cli-smoke][S0][wip] auto checkpoint (stop)
- 다음: 사용자 승인 대기

## [2026-10-22 11:58] S1 | orchestrator | START
- 한 일: 패키지 메타데이터 pyproject.toml
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: f151c33 [T-20261022-stack-cli-smoke][plan] approved

## [2026-10-22 12:00] S1 | implementer(opus) | DONE
- 한 일: pyproject.toml 생성 (§4.2 그대로)
- 변경 파일(미커밋, .ai 제외): pyproject.toml uv.lock 
- 커밋: f151c33 [T-20261022-stack-cli-smoke][plan] approved
- 다음: orchestrator: uv lock·커밋
- 메모: tomllib 검증 OK, uv lock --dry-run Resolved 15 packages, 범위 내 파일 1개. 로그 logs/s1-pyproject.log

## [2026-10-22 12:00] S1 | orchestrator | DONE
- 한 일: pyproject.toml 검증 통과 (§4.2 verbatim diff 0, uv lock → uv.lock 15 pkgs, sanitize OK). 설정 단계라 runner/reviewer 생략, orchestrator가 직접 검증
- 변경 파일(미커밋, .ai 제외): pyproject.toml uv.lock 
- 커밋: f151c33 [T-20261022-stack-cli-smoke][plan] approved
- 다음: S2 시작 (CLAUDE.md 명령 블록, orchestrator 직접)

## [2026-10-22 12:00] S2 | orchestrator | START
- 한 일: CLAUDE.md 명령 블록·전용 파일 추가분·.gitignore
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 2b392a3 [T-20261022-stack-cli-smoke][s1] build: pyproject.toml (hatchling, olefile, dev tools)

## [2026-10-22 12:00] S2 | hook | AUTO
- 한 일: 도구 호출 30회 경과
- 변경 파일(미커밋, .ai 제외): .gitignore CLAUDE.md 
- 커밋: 2b392a3 [T-20261022-stack-cli-smoke][s1] build: pyproject.toml (hatchling, olefile, dev tools)

## [2026-10-22 12:01] S2 | orchestrator | DONE
- 한 일: CLAUDE.md 명령 블록 §4.7 치환, 전용 파일 추가분 §4.8, .gitignore 2줄. 검증: 채워 넣을 것 0, 명령 6줄, fixtures ignore 1
- 변경 파일(미커밋, .ai 제외): .gitignore CLAUDE.md 
- 커밋: 2b392a3 [T-20261022-stack-cli-smoke][s1] build: pyproject.toml (hatchling, olefile, dev tools)
- 다음: S3 시작 (implementer opus: records 파서·에러·뼈대)

## [2026-10-22 12:01] S3 | orchestrator | START
- 한 일: hwp5 레코드 파서·에러 타입·패키지 뼈대
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: c29039d [T-20261022-stack-cli-smoke][s2] chore: fill CLAUDE.md command block, ignore real fixtures

## [2026-10-22 12:03] S3 | implementer(opus) | DONE
- 한 일: errors.py·hwp5/records.py(iter_records, decode_para_text)·__init__·py.typed·test_hwp5_records.py(12 passed)
- 변경 파일(미커밋, .ai 제외): src/hwp2md/__init__.py src/hwp2md/errors.py src/hwp2md/hwp5/__init__.py src/hwp2md/hwp5/records.py src/hwp2md/py.typed tests/unit/test_hwp5_records.py 
- 커밋: c29039d [T-20261022-stack-cli-smoke][s2] chore: fill CLAUDE.md command block, ignore real fixtures
- 다음: runner 검증 → reviewer
- 메모: uv sync 첫 성공(.venv). mypy OK, ruff OK(E501 2건 수정), 12 passed. truncated 메시지 offset=헤더 시작. 로그 logs/s3-*.log

## [2026-10-22 12:04] S3 | hook | AUTO
- 한 일: 도구 호출 45회 경과
- 변경 파일(미커밋, .ai 제외): src/hwp2md/__init__.py src/hwp2md/errors.py src/hwp2md/hwp5/__init__.py src/hwp2md/hwp5/records.py src/hwp2md/py.typed tests/unit/test_hwp5_records.py 
- 커밋: c29039d [T-20261022-stack-cli-smoke][s2] chore: fill CLAUDE.md command block, ignore real fixtures

## [2026-10-22 12:04] S3 | runner(haiku) | DONE
- 한 일: 검증 실행: mypy OK(4 files), ruff check+format OK, pytest unit 12 passed, grep lxml|hwpx 0건
- 변경 파일(미커밋, .ai 제외): src/hwp2md/__init__.py src/hwp2md/errors.py src/hwp2md/hwp5/__init__.py src/hwp2md/hwp5/records.py src/hwp2md/py.typed tests/unit/test_hwp5_records.py 
- 커밋: c29039d [T-20261022-stack-cli-smoke][s2] chore: fill CLAUDE.md command block, ignore real fixtures
- 다음: reviewer 판정 대기
- 메모: 로그 logs/s3-{typecheck,lint,test}.log

## [2026-10-22 12:05] S3 | reviewer(sonnet) | DONE
- 한 일: PASS — 7기준 OK (쓰기범위·§4.3 계약·헤더 비트·PARA_TEXT 제어문자·테스트 8+4·OUT 없음·익명화)
- 변경 파일(미커밋, .ai 제외): src/.gitkeep src/hwp2md/__init__.py src/hwp2md/errors.py src/hwp2md/hwp5/__init__.py src/hwp2md/hwp5/records.py src/hwp2md/py.typed tests/unit/test_hwp5_records.py 
- 커밋: c29039d [T-20261022-stack-cli-smoke][s2] chore: fill CLAUDE.md command block, ignore real fixtures
- 다음: orchestrator 마감
- 메모: truncated offset = 레코드 헤더 시작. S4 테스트에서 가정 가능

## [2026-10-22 12:05] S3 | orchestrator | DONE
- 한 일: hwp5 레코드 파서 검증 통과 (runner·reviewer PASS), src/.gitkeep 삭제
- 변경 파일(미커밋, .ai 제외): src/.gitkeep src/hwp2md/__init__.py src/hwp2md/errors.py src/hwp2md/hwp5/__init__.py src/hwp2md/hwp5/records.py src/hwp2md/py.typed tests/unit/test_hwp5_records.py 
- 커밋: c29039d [T-20261022-stack-cli-smoke][s2] chore: fill CLAUDE.md command block, ignore real fixtures
- 다음: S4 시작 (implementer opus: 합성 HWP 5.0 생성기)

## [2026-10-22 12:05] S4 | orchestrator | START
- 한 일: 합성 HWP 5.0 생성기 (순수 파이썬 CFB writer)
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 59848cd [T-20261022-stack-cli-smoke][s3] feat(hwp5): record iterator and PARA_TEXT decoder

## [2026-10-22 12:07] S4 | hook | AUTO
- 한 일: 도구 호출 60회 경과
- 변경 파일(미커밋, .ai 제외): tests/synth_hwp5.py tests/unit/test_synth_hwp5.py 
- 커밋: 59848cd [T-20261022-stack-cli-smoke][s3] feat(hwp5): record iterator and PARA_TEXT decoder

## [2026-10-22 12:07] S4 | implementer(opus) | DONE
- 한 일: tests/synth_hwp5.py(CFB writer+HWP 레코드 빌더)·test_synth_hwp5.py 8케이스, unit 20 passed
- 변경 파일(미커밋, .ai 제외): tests/synth_hwp5.py tests/unit/test_synth_hwp5.py 
- 커밋: 59848cd [T-20261022-stack-cli-smoke][s3] feat(hwp5): record iterator and PARA_TEXT decoder
- 다음: runner 검증 → reviewer
- 메모: HWP5_SIGNATURE 사본을 synth에 정의(reader.py는 S5). 레이아웃: 섹터0 FAT, 1-2 dir, 3 MiniFAT, 4~ ministream. olefile strict 모드 무결점. 로그 logs/s4-*.log

## [2026-10-22 12:09] S4 | runner(haiku) | DONE
- 한 일: 검증: mypy OK, ruff OK(7 files), unit 20 passed, olefile listdir 3 스트림+FileHeader 256 (exit 0은 orchestrator가 재확인)
- 변경 파일(미커밋, .ai 제외): tests/synth_hwp5.py tests/unit/test_synth_hwp5.py 
- 커밋: 59848cd [T-20261022-stack-cli-smoke][s3] feat(hwp5): record iterator and PARA_TEXT decoder
- 다음: reviewer 판정 대기
- 메모: zsh에서 PIPESTATUS 미지원 → 이후 runner 명령은 pipe 없이 exit 캡처

## [2026-10-22 12:09] S4 | reviewer(sonnet) | DONE
- 한 일: PASS — 10기준 OK (§4.4-A~H 바이트 레이아웃·시그니처·테스트 (a)~(g)·OUT 없음·익명화)
- 변경 파일(미커밋, .ai 제외): tests/synth_hwp5.py tests/unit/test_synth_hwp5.py 
- 커밋: 59848cd [T-20261022-stack-cli-smoke][s3] feat(hwp5): record iterator and PARA_TEXT decoder
- 다음: orchestrator 마감
- 메모: reader는 미니스트림 순서에 의존 금지. HWP5_SIGNATURE 사본 synth_hwp5.py — S5 reader.py 상수와 값 일치 필요

## [2026-10-22 12:09] S4 | orchestrator | DONE
- 한 일: 합성 HWP 5.0 생성기 검증 통과 (runner·reviewer PASS)
- 변경 파일(미커밋, .ai 제외): tests/synth_hwp5.py tests/unit/test_synth_hwp5.py 
- 커밋: 59848cd [T-20261022-stack-cli-smoke][s3] feat(hwp5): record iterator and PARA_TEXT decoder
- 다음: S5 시작 (implementer opus: reader·render·convert)

## [2026-10-22 12:09] S5 | orchestrator | START
- 한 일: hwp5 리더·Markdown 렌더·convert API
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 42210a1 [T-20261022-stack-cli-smoke][s4] test: synthetic HWP 5.0 fixture generator (CFB writer)

## [2026-10-22 12:09] S5 | hook | AUTO
- 한 일: 도구 호출 75회 경과
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 42210a1 [T-20261022-stack-cli-smoke][s4] test: synthetic HWP 5.0 fixture generator (CFB writer)

## [2026-10-22 12:11] S5 | implementer(opus) | DONE
- 한 일: reader.py·render.py·convert.py·__init__ export·test_convert.py 15케이스, unit 35 passed, mypy 7 files OK
- 변경 파일(미커밋, .ai 제외): src/hwp2md/__init__.py src/hwp2md/convert.py src/hwp2md/hwp5/reader.py src/hwp2md/render.py tests/unit/test_convert.py 
- 커밋: 42210a1 [T-20261022-stack-cli-smoke][s4] test: synthetic HWP 5.0 fixture generator (CFB writer)
- 다음: runner 검증 → reviewer
- 메모: ConvertResult(source, output, paragraph_count, markdown). 예외: FileNotFoundError / NotHwpFileError / UnsupportedHwpError / Hwp2mdError(상위). __init__ import 순서를 __version__ 위로(ruff E402). 로그 logs/s5-*.log

## [2026-10-22 12:12] S5 | hook | AUTO
- 한 일: 도구 호출 90회 경과
- 변경 파일(미커밋, .ai 제외): src/hwp2md/__init__.py src/hwp2md/convert.py src/hwp2md/hwp5/reader.py src/hwp2md/render.py tests/unit/test_convert.py 
- 커밋: 42210a1 [T-20261022-stack-cli-smoke][s4] test: synthetic HWP 5.0 fixture generator (CFB writer)

## [2026-10-22 12:12] S5 | runner(haiku) | DONE
- 한 일: 검증: mypy OK(7 files), ruff OK(11 files), unit 35 passed, import '0.1.0 convert', grep lxml|hwpx 0건
- 변경 파일(미커밋, .ai 제외): src/hwp2md/__init__.py src/hwp2md/convert.py src/hwp2md/hwp5/reader.py src/hwp2md/render.py tests/unit/test_convert.py 
- 커밋: 42210a1 [T-20261022-stack-cli-smoke][s4] test: synthetic HWP 5.0 fixture generator (CFB writer)
- 다음: reviewer 판정 대기
- 메모: 로그 logs/s5-{typecheck,lint,test,import,grep}.log

## [2026-10-22 12:13] S5 | reviewer(sonnet) | DONE
- 한 일: PASS — 10기준 OK (§4.3 API·§4.4-A/B·예외 매핑·mypy strict·테스트 (a)~(h)+시그니처 동일성·OUT 없음·익명화)
- 변경 파일(미커밋, .ai 제외): src/hwp2md/__init__.py src/hwp2md/convert.py src/hwp2md/hwp5/reader.py src/hwp2md/render.py tests/unit/test_convert.py 
- 커밋: 42210a1 [T-20261022-stack-cli-smoke][s4] test: synthetic HWP 5.0 fixture generator (CFB writer)
- 다음: orchestrator 마감
- 메모: cli: NotHwpFileError/UnsupportedHwpError(3) → FileNotFoundError(2) → Hwp2mdError(1) 순. 깨진 OLE의 OSError는 reader가 변환 안 함(범위 밖) → cli 일반 예외 처리(1). ConvertResult.output은 out_dir 상대경로 유지

## [2026-10-22 12:13] S5 | orchestrator | DONE
- 한 일: 리더·렌더·convert API 검증 통과 (runner·reviewer PASS)
- 변경 파일(미커밋, .ai 제외): src/hwp2md/__init__.py src/hwp2md/convert.py src/hwp2md/hwp5/reader.py src/hwp2md/render.py tests/unit/test_convert.py 
- 커밋: 42210a1 [T-20261022-stack-cli-smoke][s4] test: synthetic HWP 5.0 fixture generator (CFB writer)
- 다음: S6 시작 (implementer opus: cli.py 전용 단계)

## [2026-10-22 12:13] S6 | orchestrator | START
- 한 일: CLI 진입점 cli.py
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 17a6f6c [T-20261022-stack-cli-smoke][s5] feat: HWP 5.0 reader, markdown renderer, convert API

## [2026-10-22 12:54] S6 | implementer(opus) | RETRY
- 한 일: 1차 호출이 API rate limit(session limit, 12:50 리셋)으로 시작 직후 종료. cli.py 미생성, 로그 없음
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 17a6f6c [T-20261022-stack-cli-smoke][s5] feat: HWP 5.0 reader, markdown renderer, convert API
- 다음: 12:54 같은 프롬프트로 implementer(opus) 재호출
- 메모: limit → 수동 재호출 (RETRY 1/3)

## [2026-10-22 12:55] S6 | hook | AUTO
- 한 일: 도구 호출 105회 경과
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 17a6f6c [T-20261022-stack-cli-smoke][s5] feat: HWP 5.0 reader, markdown renderer, convert API

## [2026-10-22 12:56] S6 | implementer(opus) | DONE
- 한 일: src/hwp2md/cli.py 작성 (재호출 성공). --version/성공 2줄/exit 2·3·1 전부 §4.5 일치, ruff·mypy(8 files) OK, unit 35 passed
- 변경 파일(미커밋, .ai 제외): src/hwp2md/cli.py 
- 커밋: 17a6f6c [T-20261022-stack-cli-smoke][s5] feat: HWP 5.0 reader, markdown renderer, convert API
- 다음: runner 검증(stderr 분리 확인 포함) → reviewer
- 메모: except 순서 NotHwp→Unsupported→FileNotFound→Hwp2mdError→Exception. 로그는 stderr를 stdout에 합쳐 저장 → runner가 2>와 1>로 분리 확인. 로그 logs/s6-cli.log

## [2026-10-22 12:57] S6 | runner(haiku) | DONE
- 한 일: 검증: --version OK, S2 성공 2줄+exit0+파일 바이트 일치(orchestrator 재확인), S3 exit2, S4 exit3(md 미생성), encrypted exit3, no-args exit2, stderr 분리 확인, ruff·mypy(8 files) OK, unit 35 passed
- 변경 파일(미커밋, .ai 제외): src/hwp2md/cli.py 
- 커밋: 17a6f6c [T-20261022-stack-cli-smoke][s5] feat: HWP 5.0 reader, markdown renderer, convert API
- 다음: reviewer 판정 대기
- 메모: 로그 logs/s6-runner.log

## [2026-10-22 12:58] S6 | reviewer(sonnet) | DONE
- 한 일: PASS — 8기준 OK (쓰기범위·§4.3 시그니처·§4.5 인자/출력/종료코드/메시지·stdlib만·로그 일치·익명화)
- 변경 파일(미커밋, .ai 제외): src/hwp2md/cli.py 
- 커밋: 17a6f6c [T-20261022-stack-cli-smoke][s5] feat: HWP 5.0 reader, markdown renderer, convert API
- 다음: orchestrator 마감
- 메모: E2E: 성공 경로는 str(Path(out_dir)/'sample.md')와 비교, 인자 없음은 접두+exit만 단언, PYTHONIOENCODING=utf-8 필요(§4.6 conftest)

## [2026-10-22 12:58] S6 | orchestrator | DONE
- 한 일: CLI 진입점 검증 통과 (runner·reviewer PASS)
- 변경 파일(미커밋, .ai 제외): src/hwp2md/cli.py 
- 커밋: 17a6f6c [T-20261022-stack-cli-smoke][s5] feat: HWP 5.0 reader, markdown renderer, convert API
- 다음: S7 시작 (scribe haiku: decisions.md·README)
