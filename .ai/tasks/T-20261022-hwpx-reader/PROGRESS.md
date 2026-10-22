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
