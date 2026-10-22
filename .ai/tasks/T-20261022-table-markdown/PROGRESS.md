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
