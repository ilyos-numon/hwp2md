# PROGRESS — T-20261022-hwpx-reader

> append-only.

---

## [2026-10-22 14:34] S0 | hook | AUTO
- 한 일: 자동 체크포인트 (stop)
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: e13ae70 chore(state): next action after merge
- 메모: STATE.md의 '다음 행동' 확인 후 이어서

## [2026-10-22 14:35] S0 | hook | AUTO
- 한 일: 도구 호출 15회 경과
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: ac09c84 [T-20261022-hwpx-reader][S0][wip] auto checkpoint (stop)

## [2026-10-22 17:51] S0 | planner(fable) | DONE
- 한 일: PLAN.md 작성 (7단계+조건부 4b, §7 질문 5개, 실제 HWPX 샘플 3개 조사 포함). planner는 파일을 완성한 뒤 rate limit(17:50 리셋)으로 종료돼 보고 유실 → orchestrator가 셀프체크 10/10 직접 수행
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: ac09c84 [T-20261022-hwpx-reader][S0][wip] auto checkpoint (stop)
- 다음: 사용자 승인 대기
- 메모: HANDOFF.md 작성(한도 임박, orchestrator 직접). 샘플 기대값: (1,1) (80,31) (32,8)

## [2026-10-22 17:53] S1 | orchestrator | START
- 한 일: 의존성 추가(lxml, lxml-stubs)와 실제 샘플 폴더 이동
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: e879a18 [T-20261022-hwpx-reader][plan] approved

## [2026-10-22 17:54] S1 | orchestrator | DONE
- 한 일: uv add lxml>=5(6.1.3)·--dev lxml-stubs(0.5.1), uv sync. 샘플 3개 tests/fixtures/hwpx/로 이동(unsupported/hwpx 제거). mypy OK, unit 64, E2E 11 — 회귀 없음
- 변경 파일(미커밋, .ai 제외): pyproject.toml uv.lock 
- 커밋: e879a18 [T-20261022-hwpx-reader][plan] approved
- 다음: S2 시작 (implementer opus: hwpx/body.py·reader.py)
- 메모: pyproject +12/-3, uv.lock +149. fixtures는 gitignore라 git 변경 없음

## [2026-10-22 17:54] S2 | orchestrator | START
- 한 일: HWPX 섹션 파서와 리더 (hwpx/body.py, hwpx/reader.py)
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 2bff126 [T-20261022-hwpx-reader][s1] deps: lxml>=5 runtime, lxml-stubs dev

## [2026-10-22 17:55] S2 | hook | AUTO
- 한 일: 도구 호출 30회 경과
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 2bff126 [T-20261022-hwpx-reader][s1] deps: lxml>=5 runtime, lxml-stubs dev

## [2026-10-22 17:57] S2 | implementer(opus) | DONE
- 한 일: hwpx/{__init__,body,reader}.py + test_hwpx_body.py 18케이스. unit 82 passed, mypy 13 files OK, ruff OK. 실제 샘플 (1,1)(80,31)(32,8) 일치
- 변경 파일(미커밋, .ai 제외): src/hwp2md/hwpx/__init__.py src/hwp2md/hwpx/body.py src/hwp2md/hwpx/reader.py tests/unit/test_hwpx_body.py 
- 커밋: 2bff126 [T-20261022-hwpx-reader][s1] deps: lxml>=5 runtime, lxml-stubs dev
- 다음: runner 검증 → reviewer
- 메모: 의사코드 차이 1건: rowCnt/colCnt 속성이 명시적 0이면 표 생략(§4.7 케이스13과 일치, 의사코드 'or len(trs)'는 0을 덮어씀) — reviewer 판정. 로그 logs/s2-*.log

## [2026-10-22 17:58] S2 | hook | AUTO
- 한 일: 도구 호출 45회 경과
- 변경 파일(미커밋, .ai 제외): src/hwp2md/hwpx/__init__.py src/hwp2md/hwpx/body.py src/hwp2md/hwpx/reader.py tests/unit/test_hwpx_body.py 
- 커밋: 2bff126 [T-20261022-hwpx-reader][s1] deps: lxml>=5 runtime, lxml-stubs dev

## [2026-10-22 17:58] S2 | runner(haiku) | DONE
- 한 일: 검증: mypy OK(13 files), ruff OK(23 files), unit 82 passed, 실제 샘플 1 1 / 80 31 / 32 8, grep hwp5|BinData|footNote 0
- 변경 파일(미커밋, .ai 제외): src/hwp2md/hwpx/__init__.py src/hwp2md/hwpx/body.py src/hwp2md/hwpx/reader.py tests/unit/test_hwpx_body.py 
- 커밋: 2bff126 [T-20261022-hwpx-reader][s1] deps: lxml>=5 runtime, lxml-stubs dev
- 다음: reviewer 판정 대기
- 메모: 로그 logs/s2-*.log

## [2026-10-22 17:59] S2 | reviewer(sonnet) | DONE
- 한 일: PASS — 10기준 OK. rowCnt=0 처리는 의사코드 오류로 판정(hwp5/body.py와 동일 동작, 케이스13 일치) → 플랜 변경 이력 추가
- 변경 파일(미커밋, .ai 제외): src/hwp2md/hwpx/__init__.py src/hwp2md/hwpx/body.py src/hwp2md/hwpx/reader.py tests/unit/test_hwpx_body.py 
- 커밋: 2bff126 [T-20261022-hwpx-reader][s1] deps: lxml>=5 runtime, lxml-stubs dev
- 다음: orchestrator 마감
- 메모: S3·S4 주의: 표는 rowCnt/colCnt 반드시 명시, cellAddr/cellSpan 모두 기록, 빈 단락은 라운드트립 기대값에서 제외. run 밖 hp:tbl은 무시됨

## [2026-10-22 17:59] S2 | orchestrator | DONE
- 한 일: HWPX 파서·리더 검증 통과 (runner·reviewer PASS)
- 변경 파일(미커밋, .ai 제외): src/hwp2md/hwpx/__init__.py src/hwp2md/hwpx/body.py src/hwp2md/hwpx/reader.py tests/unit/test_hwpx_body.py 
- 커밋: 2bff126 [T-20261022-hwpx-reader][s1] deps: lxml>=5 runtime, lxml-stubs dev
- 다음: S3 시작 (implementer opus: synth_hwpx.py·리더 오류/보안 테스트)

## [2026-10-22 17:59] S3 | orchestrator | START
- 한 일: 합성 HWPX 생성기와 리더 오류·보안 테스트 (synth_hwpx.py)
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 3ab729b [T-20261022-hwpx-reader][s2] feat(hwpx): section parser and reader (lxml, secure parser, blocks)

## [2026-10-22 18:01] S3 | hook | AUTO
- 한 일: 도구 호출 60회 경과
- 변경 파일(미커밋, .ai 제외): tests/synth_hwpx.py 
- 커밋: 3ab729b [T-20261022-hwpx-reader][s2] feat(hwpx): section parser and reader (lxml, secure parser, blocks)

## [2026-10-22 18:02] S3 | implementer(opus) | DONE
- 한 일: synth_hwpx.py + test_synth_hwpx.py 9 + test_hwpx_reader.py 9. unit 100 passed, -k entity 2 passed, mypy 13 OK, ruff OK, src·synth_hwp5 변경 0, zip mimetype 첫 엔트리 STORED 6개
- 변경 파일(미커밋, .ai 제외): tests/synth_hwpx.py tests/unit/test_hwpx_reader.py tests/unit/test_synth_hwpx.py 
- 커밋: 3ab729b [T-20261022-hwpx-reader][s2] feat(hwpx): section parser and reader (lxml, secure parser, blocks)
- 다음: runner → reviewer
- 메모: §4.7 케이스9: lxml 6.1.3 XMLParser에 resolve_entities 속성 없음 → 동작 기반 검사(내부 엔티티가 _Entity 노드로 남음)로 대체, 이름 유지 — reviewer 판정 후 변경 이력 대상. synth_hwpx docstring noqa E501

## [2026-10-22 18:03] S3 | runner(haiku) | DONE
- 한 일: 검증: mypy OK(13), ruff OK(26 files), unit 100 passed, entity 2 passed, zip 'mimetype 0 6', src·synth_hwp5 diff 0
- 변경 파일(미커밋, .ai 제외): tests/synth_hwpx.py tests/unit/test_hwpx_reader.py tests/unit/test_synth_hwpx.py 
- 커밋: 3ab729b [T-20261022-hwpx-reader][s2] feat(hwpx): section parser and reader (lxml, secure parser, blocks)
- 다음: reviewer 판정 대기
- 메모: 로그 logs/s3-*.log

## [2026-10-22 18:03] S3 | hook | AUTO
- 한 일: 도구 호출 75회 경과
- 변경 파일(미커밋, .ai 제외): tests/synth_hwpx.py tests/unit/test_hwpx_reader.py tests/unit/test_synth_hwpx.py 
- 커밋: 3ab729b [T-20261022-hwpx-reader][s2] feat(hwpx): section parser and reader (lxml, secure parser, blocks)

## [2026-10-22 18:04] S3 | reviewer(sonnet) | DONE
- 한 일: PASS — 9기준 OK (§4.6 API·XML 템플릿·zip 구조·테스트 9+9·엔티티 보안·src 불변·익명화). 케이스9 동작 기반 대체 수용 → 변경 이력 추가
- 변경 파일(미커밋, .ai 제외): tests/synth_hwpx.py tests/unit/test_hwpx_reader.py tests/unit/test_synth_hwpx.py 
- 커밋: 3ab729b [T-20261022-hwpx-reader][s2] feat(hwpx): section parser and reader (lxml, secure parser, blocks)
- 다음: orchestrator 마감
- 메모: S4: 같은 fixture를 write_hwp5/write_hwpx에 넣으면 convert().markdown 동일해야 함. INLINE fixture는 synth_hwpx.py에 있음

## [2026-10-22 18:04] S3 | orchestrator | DONE
- 한 일: 합성 HWPX 생성기·리더 테스트 검증 통과 (runner·reviewer PASS)
- 변경 파일(미커밋, .ai 제외): tests/synth_hwpx.py tests/unit/test_hwpx_reader.py tests/unit/test_synth_hwpx.py 
- 커밋: 3ab729b [T-20261022-hwpx-reader][s2] feat(hwpx): section parser and reader (lxml, secure parser, blocks)
- 다음: S4 시작 (implementer opus: detect.py·convert.py·__init__.py)

## [2026-10-22 18:04] S4 | orchestrator | START
- 한 일: 포맷 감지와 convert 디스패치 (detect.py, convert.py, __init__.py)
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 71c5304 [T-20261022-hwpx-reader][s3] test: synthetic HWPX generator, reader error and entity-safety tests

## [2026-10-22 18:07] S4 | implementer(opus) | DONE
- 한 일: detect.py(내용 기반 판정)·convert.py 디스패치·__init__ export·test_detect.py·test_cross_format.py. unit 113 passed, mypy 14 OK, ruff OK, 실제 HWPX 3개 CLI (1,1)(80,31)(32,8) exit0, 기존 E2E 11 passed, cli.py 불변
- 변경 파일(미커밋, .ai 제외): src/hwp2md/__init__.py src/hwp2md/convert.py src/hwp2md/detect.py tests/unit/test_cross_format.py tests/unit/test_detect.py 
- 커밋: 71c5304 [T-20261022-hwpx-reader][s3] test: synthetic HWPX generator, reader error and entity-safety tests
- 다음: runner → reviewer
- 메모: corrupt zip 케이스 추가(중앙 디렉터리 시그니처 훼손). 로그 logs/s4-*.log

## [2026-10-22 18:08] S4 | hook | AUTO
- 한 일: 도구 호출 90회 경과
- 변경 파일(미커밋, .ai 제외): src/hwp2md/__init__.py src/hwp2md/convert.py src/hwp2md/detect.py tests/unit/test_cross_format.py tests/unit/test_detect.py 
- 커밋: 71c5304 [T-20261022-hwpx-reader][s3] test: synthetic HWPX generator, reader error and entity-safety tests

## [2026-10-22 18:08] S4 | runner(haiku) | DONE
- 한 일: 검증: mypy OK(14), ruff OK(29 files), unit 113 passed, 실제 HWPX 3개 CLI (1,1)(80,31)(32,8) exit0, 구분선 1/31/8, 기존 E2E 11 passed, not-hwp exit3 문구 불변, suffix 0
- 변경 파일(미커밋, .ai 제외): ".ai/tasks/T-20261022-hwpx-reader/screenshots/(\354\204\234\354\213\2351) ".ai/tasks/T-20261022-hwpx-reader/screenshots/(\354\204\234\354\213\2352) ".ai/tasks/T-20261022-hwpx-reader/screenshots/\353\270\214\353\235\274\353\215\224 src/hwp2md/__init__.py src/hwp2md/convert.py src/hwp2md/detect.py tests/unit/test_cross_format.py tests/unit/test_detect.py 
- 커밋: 71c5304 [T-20261022-hwpx-reader][s3] test: synthetic HWPX generator, reader error and entity-safety tests
- 다음: reviewer 판정 대기
- 메모: 증거 .md 3개 screenshots/에 저장. 로그 logs/s4-*.log

## [2026-10-22 18:09] S4 | reviewer(sonnet) | DONE
- 한 일: PASS — 10기준 OK (§4.2 판정·문구, §4.5, 테스트 13개, 실제 샘플 증거 직접 확인: 구분선 1/31/8, 병합 빈 칸, 머리말·그림 미혼입)
- 변경 파일(미커밋, .ai 제외): ".ai/tasks/T-20261022-hwpx-reader/screenshots/(\354\204\234\354\213\2351) ".ai/tasks/T-20261022-hwpx-reader/screenshots/(\354\204\234\354\213\2352) ".ai/tasks/T-20261022-hwpx-reader/screenshots/\353\270\214\353\235\274\353\215\224 src/hwp2md/__init__.py src/hwp2md/convert.py src/hwp2md/detect.py tests/unit/test_cross_format.py tests/unit/test_detect.py 
- 커밋: 71c5304 [T-20261022-hwpx-reader][s3] test: synthetic HWPX generator, reader error and entity-safety tests
- 다음: orchestrator 마감
- 메모: 서식 박스(제목·목차)도 표로 변환됨 → README 문구 후보. detect 문구 'not an HWP 5.0 or HWPX file'은 convert 내부, CLI stderr는 'not an HWP 5.0 file' 유지 — S6 E2E에서 구분

## [2026-10-22 18:09] S4 | orchestrator | DONE
- 한 일: 포맷 감지·convert 디스패치 검증 통과 (runner·reviewer PASS). Stage 4b는 §7-2 기본값이라 건너뜀
- 변경 파일(미커밋, .ai 제외): ".ai/tasks/T-20261022-hwpx-reader/screenshots/(\354\204\234\354\213\2351) ".ai/tasks/T-20261022-hwpx-reader/screenshots/(\354\204\234\354\213\2352) ".ai/tasks/T-20261022-hwpx-reader/screenshots/\353\270\214\353\235\274\353\215\224 src/hwp2md/__init__.py src/hwp2md/convert.py src/hwp2md/detect.py tests/unit/test_cross_format.py tests/unit/test_detect.py 
- 커밋: 71c5304 [T-20261022-hwpx-reader][s3] test: synthetic HWPX generator, reader error and entity-safety tests
- 다음: S5 시작 (implementer opus: decisions·README·fixtures README)

## [2026-10-22 18:09] S5 | orchestrator | START
- 한 일: 결정 기록·README·fixtures README 갱신
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 616857c [T-20261022-hwpx-reader][s4] feat: content-based format detection and hwp5/hwpx dispatch in convert

## [2026-10-22 18:10] S5 | hook | AUTO
- 한 일: 도구 호출 105회 경과
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 616857c [T-20261022-hwpx-reader][s4] feat: content-based format detection and hwp5/hwpx dispatch in convert

## [2026-10-22 18:11] S5 | implementer(opus) | DONE
- 한 일: decisions.md +3항목(§4.9), README 2곳(+2/-1), fixtures README 전체 교체. grep 8/4/1/0, 플랜 원문 diff 0, sanitize OK
- 변경 파일(미커밋, .ai 제외): README.md docs/decisions.md tests/fixtures/README.md 
- 커밋: 616857c [T-20261022-hwpx-reader][s4] feat: content-based format detection and hwp5/hwpx dispatch in convert
- 다음: orchestrator 검증·커밋
- 메모: implementer가 발견: decisions.md 22행 잔여 펜스(전 태스크 19e4bdf). 이번 복사도 플랜 닫는 펜스(407행) 포함 → orchestrator가 22·35행 삭제

## [2026-10-22 18:11] S5 | orchestrator | DONE
- 한 일: 문서 3개 검증 통과. 잔여 코드 펜스 2줄 제거(전 태스크 잔재 1 + 이번 행 범위 오류 1). 문서 단계라 runner 생략, orchestrator 직접 검증(플랜의 reviewer도 생략 — grep·diff로 결정적 확인)
- 변경 파일(미커밋, .ai 제외): README.md docs/decisions.md tests/fixtures/README.md 
- 커밋: 616857c [T-20261022-hwpx-reader][s4] feat: content-based format detection and hwp5/hwpx dispatch in convert
- 다음: S6 시작 (test-writer sonnet: tests/e2e/test_cli_hwpx.py)
