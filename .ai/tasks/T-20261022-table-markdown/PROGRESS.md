# PROGRESS — T-20261022-table-markdown

> append-only.

---

## [2026-10-22 13:38] S0 | hook | AUTO
- 한 일: 도구 호출 15회 경과
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 6e24c12 chore(fixtures): ignore all sample documents, split unsupported formats into subfolders

## [2026-10-22 13:55] S0 | planner(fable) | DONE
- 한 일: PLAN.md 작성 (7단계, §7 질문 5개, 실제 샘플 레코드 조사 포함), 셀프체크 10/10
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 6e24c12 chore(fixtures): ignore all sample documents, split unsupported formats into subfolders
- 다음: 사용자 승인 대기
- 메모: 실제 샘플: form2000… 표 8개(셀 67), form2100…0268 표 0개. LIST_HEADER 38B·ctrl_id 역순 함정 §4에 고정

## [2026-10-22 13:56] S0 | hook | AUTO
- 한 일: 도구 호출 30회 경과
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: a359cdc [T-20261022-table-markdown][plan] approved

## [2026-10-22 13:56] S1 | orchestrator | START
- 한 일: 블록 모델과 표 레코드 파서 (blocks.py, hwp5/body.py)
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: a359cdc [T-20261022-table-markdown][plan] approved

## [2026-10-22 13:58] S1 | implementer(opus) | DONE
- 한 일: blocks.py·hwp5/body.py(parse_table_header/parse_cell_header/parse_blocks)·records.py CTRL_ID_TABLE 1줄·test_hwp5_body.py 14케이스. unit 49 passed, mypy 10 files OK, ruff OK
- 변경 파일(미커밋, .ai 제외): src/hwp2md/blocks.py src/hwp2md/hwp5/body.py src/hwp2md/hwp5/records.py tests/unit/test_hwp5_body.py 
- 커밋: a359cdc [T-20261022-table-markdown][plan] approved
- 다음: runner 검증 → reviewer
- 메모: §4.3 의사코드 그대로. 로그 logs/s1-*.log

## [2026-10-22 13:59] S1 | hook | AUTO
- 한 일: 도구 호출 45회 경과
- 변경 파일(미커밋, .ai 제외): src/hwp2md/blocks.py src/hwp2md/hwp5/body.py src/hwp2md/hwp5/records.py tests/unit/test_hwp5_body.py 
- 커밋: a359cdc [T-20261022-table-markdown][plan] approved

## [2026-10-22 14:00] S1 | runner(haiku) | DONE
- 한 일: 검증: mypy OK(10 files), ruff OK(18 files), unit 49 passed, records.py +1/-0, grep OUT 0건
- 변경 파일(미커밋, .ai 제외): src/hwp2md/blocks.py src/hwp2md/hwp5/body.py src/hwp2md/hwp5/records.py tests/unit/test_hwp5_body.py 
- 커밋: a359cdc [T-20261022-table-markdown][plan] approved
- 다음: reviewer 판정 대기
- 메모: 로그 logs/s1-*.log

## [2026-10-22 14:00] S1 | reviewer(sonnet) | DONE
- 한 일: PASS — 9기준 OK (§4.2 타입·§4.3 의사코드·§4.4 offset·테스트 (a)~(l)·OUT 없음·익명화)
- 변경 파일(미커밋, .ai 제외): src/hwp2md/blocks.py src/hwp2md/hwp5/body.py src/hwp2md/hwp5/records.py tests/unit/test_hwp5_body.py 
- 커밋: a359cdc [T-20261022-table-markdown][plan] approved
- 다음: orchestrator 마감
- 메모: 생성기 주의: 셀 PARA_HEADER level = 자리표시자+2(TABLE/LIST_HEADER와 형제), 셀 PARA_TEXT level+3. 표 인식은 CTRL_HEADER payload[:4]==b' lbt'만. (row,col) 중복 금지

## [2026-10-22 14:00] S1 | orchestrator | DONE
- 한 일: 블록 모델·표 파서 검증 통과 (runner·reviewer PASS)
- 변경 파일(미커밋, .ai 제외): src/hwp2md/blocks.py src/hwp2md/hwp5/body.py src/hwp2md/hwp5/records.py tests/unit/test_hwp5_body.py 
- 커밋: a359cdc [T-20261022-table-markdown][plan] approved
- 다음: S2 시작 (implementer opus: synth_hwp5 표 확장)

## [2026-10-22 14:00] S2 | orchestrator | START
- 한 일: 합성 생성기 표 확장 (synth_hwp5.py)
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 4f1b92f [T-20261022-table-markdown][s1] feat(hwp5): block model and table record parser

## [2026-10-22 14:03] S2 | hook | AUTO
- 한 일: 도구 호출 60회 경과
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 4f1b92f [T-20261022-table-markdown][s1] feat(hwp5): block model and table record parser

## [2026-10-22 14:05] S2 | implementer(opus) | RETRY
- 한 일: 1차: 표 빌더·fixture·테스트 7개 추가, unit 56 passed, 왕복 OK. 그러나 build_paragraph/build_section0을 파일 끝에 중복 정의(noqa F811)
- 변경 파일(미커밋, .ai 제외): tests/synth_hwp5.py tests/unit/test_synth_hwp5.py 
- 커밋: 4f1b92f [T-20261022-table-markdown][s1] feat(hwp5): block model and table record parser
- 다음: 같은 에이전트에 제자리 병합 요청 (플랜 §4.6은 시그니처 제자리 확장을 명시; orchestrator의 '삭제 줄 0' 검증 항목이 잘못됨)
- 메모: RETRY 1/3. 원인은 orchestrator 프롬프트

## [2026-10-22 14:07] S2 | implementer(opus) | DONE
- 한 일: 2차: build_paragraph(level=)·build_section0(Item) 제자리 확장, 중복 정의·noqa 제거, 표 빌더·SynthCell/SynthTable·fixture 4종·테스트 7개. unit 56 passed, mypy OK, ruff OK. (g) sha256으로 BASE 바이트 동일성 고정
- 변경 파일(미커밋, .ai 제외): tests/synth_hwp5.py tests/unit/test_synth_hwp5.py 
- 커밋: 4f1b92f [T-20261022-table-markdown][s1] feat(hwp5): block model and table record parser
- 다음: runner 검증 → reviewer
- 메모: orchestrator가 BASE 모듈과 직접 비교해 section0/hwp5 바이트 동일 확인

## [2026-10-22 14:07] S2 | hook | AUTO
- 한 일: 도구 호출 75회 경과
- 변경 파일(미커밋, .ai 제외): tests/synth_hwp5.py tests/unit/test_synth_hwp5.py 
- 커밋: 4f1b92f [T-20261022-table-markdown][s1] feat(hwp5): block model and table record parser

## [2026-10-22 14:08] S2 | runner(haiku) | DONE
- 한 일: 검증: mypy OK, ruff OK(18 files), unit 56 passed, olefile 두 fixture 3 스트림(Section0 223B/202B 압축), noqa 0·def 2
- 변경 파일(미커밋, .ai 제외): tests/synth_hwp5.py tests/unit/test_synth_hwp5.py 
- 커밋: 4f1b92f [T-20261022-table-markdown][s1] feat(hwp5): block model and table record parser
- 다음: reviewer 판정 대기
- 메모: 로그 logs/s2-*.log

## [2026-10-22 14:09] S2 | reviewer(sonnet) | DONE
- 한 일: PASS — 9기준 OK (§4.6 API·fixture 값·§4.4 바이트·level·BASE 바이트 불변·테스트 7+8·익명화)
- 변경 파일(미커밋, .ai 제외): tests/synth_hwp5.py tests/unit/test_synth_hwp5.py 
- 커밋: 4f1b92f [T-20261022-table-markdown][s1] feat(hwp5): block model and table record parser
- 다음: orchestrator 마감
- 메모: build_hwp5/write_hwp5 인자명은 paragraphs 유지(타입만 Item으로, 플랜 허용). 병합 가림 칸은 파서가 채움

## [2026-10-22 14:09] S2 | orchestrator | DONE
- 한 일: 합성 표 fixture 검증 통과 (runner·reviewer PASS)
- 변경 파일(미커밋, .ai 제외): tests/synth_hwp5.py tests/unit/test_synth_hwp5.py 
- 커밋: 4f1b92f [T-20261022-table-markdown][s1] feat(hwp5): block model and table record parser
- 다음: S3 시작 (implementer opus: read_blocks·render_blocks·table_count)
