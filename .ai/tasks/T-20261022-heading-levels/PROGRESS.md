# PROGRESS — T-20261022-heading-levels

> append-only.

---

## [2026-10-22 18:27] S0 | hook | AUTO
- 한 일: 자동 체크포인트 (stop)
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: ce0a3f5 chore(state): branch main after merge, next action
- 메모: STATE.md의 '다음 행동' 확인 후 이어서

## [2026-10-22 18:28] S0 | hook | AUTO
- 한 일: 도구 호출 15회 경과
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 93f7cea [T-20261022-heading-levels][S0][wip] auto checkpoint (stop)

## [2026-10-22 18:35] S0 | hook | AUTO
- 한 일: 도구 호출 30회 경과
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 93f7cea [T-20261022-heading-levels][S0][wip] auto checkpoint (stop)

## [2026-10-22 18:51] S0 | planner(fable) | DONE
- 한 일: PLAN.md 작성 (9단계, §7 질문 7개, 실제 샘플 5개 개요 조사). orchestrator 셀프체크 10/10
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 93f7cea [T-20261022-heading-levels][S0][wip] auto checkpoint (stop)
- 다음: 사용자 승인 대기
- 메모: 샘플: form2000… 최상위 개요 18(수준1×6,2×4,3×4,7×4) → (100,8,18); 나머지 4개 제목 0. 판정은 문단 모양만(style_id 전부 0)

## [2026-10-22 19:05] S0 | orchestrator | DONE
- 한 일: 플랜 승인(§7 7개 기본값). 사용자 요청으로 실행은 한도 초기화 후 '계속해'에 시작. HANDOFF.md 작성
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: da18025 [T-20261022-heading-levels][plan] 제목 계층(개요 수준 → Markdown heading) 플랜
- 다음: S1 START (implementer opus)

## [2026-10-22 22:56] S1 | hook | AUTO
- 한 일: 도구 호출 45회 경과
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 2e7a7fc [T-20261022-heading-levels][plan] approved (defaults), handoff for later start

## [2026-10-22 22:56] S1 | orchestrator | START
- 한 일: 블록 모델 level 필드·제목 렌더·heading_count
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: abcc6b4 [T-20261022-heading-levels][plan] approved, start

## [2026-10-22 22:57] S1 | implementer(opus) | DONE
- 한 일: Paragraph.level·_render_paragraph·heading_count, 단위 7개
- 변경 파일(미커밋, .ai 제외): src/hwp2md/blocks.py src/hwp2md/convert.py src/hwp2md/render.py tests/unit/test_render_heading.py 
- 커밋: abcc6b4 [T-20261022-heading-levels][plan] approved, start
- 다음: S2
- 메모: mypy14 OK, unit120, e2e21

## [2026-10-22 22:57] S1 | reviewer(sonnet) | DONE
- 한 일: VERDICT PASS, findings 없음
- 변경 파일(미커밋, .ai 제외): src/hwp2md/blocks.py src/hwp2md/convert.py src/hwp2md/render.py tests/unit/test_render_heading.py 
- 커밋: abcc6b4 [T-20261022-heading-levels][plan] approved, start

## [2026-10-22 22:57] S1 | orchestrator | DONE
- 한 일: 블록 모델 검증 통과
- 변경 파일(미커밋, .ai 제외): src/hwp2md/blocks.py src/hwp2md/convert.py src/hwp2md/render.py tests/unit/test_render_heading.py 
- 커밋: abcc6b4 [T-20261022-heading-levels][plan] approved, start
- 다음: S2 시작

## [2026-10-22 22:57] S2 | orchestrator | START
- 한 일: 합성 HWP 5.0 생성기 SynthHeading
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: ca0355f [T-20261022-heading-levels][s1] blocks: Paragraph.level, heading render, heading_count

## [2026-10-22 22:57] S2 | hook | AUTO
- 한 일: 도구 호출 60회 경과
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: ca0355f [T-20261022-heading-levels][s1] blocks: Paragraph.level, heading render, heading_count

## [2026-10-22 22:58] S2 | hook | AUTO
- 한 일: 도구 호출 75회 경과
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: ca0355f [T-20261022-heading-levels][s1] blocks: Paragraph.level, heading render, heading_count

## [2026-10-22 22:59] S2 | implementer(opus) | DONE
- 한 일: SynthHeading·PARA_SHAPE/STYLE·fixture·단위 8
- 변경 파일(미커밋, .ai 제외): tests/synth_hwp5.py tests/unit/test_synth_hwp5.py 
- 커밋: ca0355f [T-20261022-heading-levels][s1] blocks: Paragraph.level, heading render, heading_count
- 다음: S2 리뷰
- 메모: 계약 충돌 지적: PARA_HEADER para_shape_id @12→@8 (orchestrator가 PLAN §1·§4.3-F·§4.4 수정)

## [2026-10-22 22:59] S2 | hook | AUTO
- 한 일: 도구 호출 90회 경과
- 변경 파일(미커밋, .ai 제외): tests/synth_hwp5.py tests/unit/test_synth_hwp5.py 
- 커밋: ca0355f [T-20261022-heading-levels][s1] blocks: Paragraph.level, heading render, heading_count

## [2026-10-22 23:00] S2 | reviewer(sonnet) | DONE
- 한 일: VERDICT PASS, findings 없음
- 변경 파일(미커밋, .ai 제외): tests/synth_hwp5.py tests/unit/test_synth_hwp5.py 
- 커밋: ca0355f [T-20261022-heading-levels][s1] blocks: Paragraph.level, heading render, heading_count

## [2026-10-22 23:00] S2 | orchestrator | DONE
- 한 일: 합성 HWP5 생성기 검증 통과
- 변경 파일(미커밋, .ai 제외): tests/synth_hwp5.py tests/unit/test_synth_hwp5.py 
- 커밋: ca0355f [T-20261022-heading-levels][s1] blocks: Paragraph.level, heading render, heading_count
- 다음: S3 시작

## [2026-10-22 23:00] S3 | orchestrator | START
- 한 일: HWP5 DocInfo 파서·본문·리더 연결
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 0442c71 [T-20261022-heading-levels][s2] tests: synthetic hwp5 headings (PARA_SHAPE/STYLE docinfo), byte-stability hashes

## [2026-10-22 23:01] S3 | hook | AUTO
- 한 일: 도구 호출 105회 경과
- 변경 파일(미커밋, .ai 제외): src/hwp2md/hwp5/body.py src/hwp2md/hwp5/reader.py src/hwp2md/hwp5/records.py src/hwp2md/hwp5/docinfo.py tests/unit/test_hwp5_docinfo.py 
- 커밋: 0442c71 [T-20261022-heading-levels][s2] tests: synthetic hwp5 headings (PARA_SHAPE/STYLE docinfo), byte-stability hashes

## [2026-10-22 23:01] S3 | implementer(opus) | PARTIAL
- 한 일: 구현·단위 145·e2e 21 통과. 실제 샘플1 @8 기준 제목 0개(기대 18)
- 변경 파일(미커밋, .ai 제외): src/hwp2md/hwp5/body.py src/hwp2md/hwp5/reader.py src/hwp2md/hwp5/records.py src/hwp2md/hwp5/docinfo.py tests/unit/test_hwp5_docinfo.py 
- 커밋: 0442c71 [T-20261022-heading-levels][s2] tests: synthetic hwp5 headings (PARA_SHAPE/STYLE docinfo), byte-stability hashes
- 다음: orchestrator: PARA_HEADER 오프셋 계약(@8 vs @12) 결정

## [2026-10-22 23:03] S3 | implementer(opus) | PARTIAL
- 한 일: docinfo.py·body/reader 연결·단위 12건, unit 145
- 변경 파일(미커밋, .ai 제외): src/hwp2md/hwp5/body.py src/hwp2md/hwp5/reader.py src/hwp2md/hwp5/records.py src/hwp2md/hwp5/docinfo.py tests/unit/test_hwp5_docinfo.py 
- 커밋: 0442c71 [T-20261022-heading-levels][s2] tests: synthetic hwp5 headings (PARA_SHAPE/STYLE docinfo), byte-stability hashes
- 다음: sample1 기대값 판단 대기
- 메모: @8에서 sample1 = 118 0 {}; @12 일치만 계획값과 맞음

## [2026-10-22 23:03] S3 | orchestrator | RETRY
- 한 일: @12 매치 18개가 본문임을 진단 → @8 유지, PLAN §2·§4.11·§4.13·§4.14·S7·S9 기대값 정정, .ai/decisions 기록
- 변경 파일(미커밋, .ai 제외): src/hwp2md/hwp5/body.py src/hwp2md/hwp5/reader.py src/hwp2md/hwp5/records.py src/hwp2md/hwp5/docinfo.py tests/unit/test_hwp5_docinfo.py 
- 커밋: 0442c71 [T-20261022-heading-levels][s2] tests: synthetic hwp5 headings (PARA_SHAPE/STYLE docinfo), byte-stability hashes
- 다음: S3 검증

## [2026-10-22 23:03] S3 | hook | AUTO
- 한 일: 도구 호출 120회 경과
- 변경 파일(미커밋, .ai 제외): src/hwp2md/hwp5/body.py src/hwp2md/hwp5/reader.py src/hwp2md/hwp5/records.py src/hwp2md/hwp5/docinfo.py tests/unit/test_hwp5_docinfo.py 
- 커밋: 0442c71 [T-20261022-heading-levels][s2] tests: synthetic hwp5 headings (PARA_SHAPE/STYLE docinfo), byte-stability hashes

## [2026-10-22 23:03] S3 | reviewer(sonnet) | DONE
- 한 일: VERDICT PASS, 실제 샘플 level>0 0개 확인
- 변경 파일(미커밋, .ai 제외): src/hwp2md/hwp5/body.py src/hwp2md/hwp5/docinfo.py src/hwp2md/hwp5/reader.py src/hwp2md/hwp5/records.py tests/unit/test_hwp5_docinfo.py 
- 커밋: 0442c71 [T-20261022-heading-levels][s2] tests: synthetic hwp5 headings (PARA_SHAPE/STYLE docinfo), byte-stability hashes

## [2026-10-22 23:03] S3 | orchestrator | DONE
- 한 일: HWP5 DocInfo 파서 검증 통과 (샘플1 기대값 정정)
- 변경 파일(미커밋, .ai 제외): src/hwp2md/hwp5/body.py src/hwp2md/hwp5/docinfo.py src/hwp2md/hwp5/reader.py src/hwp2md/hwp5/records.py tests/unit/test_hwp5_docinfo.py 
- 커밋: 0442c71 [T-20261022-heading-levels][s2] tests: synthetic hwp5 headings (PARA_SHAPE/STYLE docinfo), byte-stability hashes
- 다음: S4 시작

## [2026-10-22 23:03] S4 | orchestrator | START
- 한 일: 합성 HWPX 생성기 header.xml paraPr
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 0906b09 [T-20261022-heading-levels][s3] hwp5: DocInfo PARA_SHAPE outline level -> Paragraph.level

## [2026-10-22 23:04] S4 | hook | AUTO
- 한 일: 도구 호출 135회 경과
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 0906b09 [T-20261022-heading-levels][s3] hwp5: DocInfo PARA_SHAPE outline level -> Paragraph.level

## [2026-10-22 23:04] S4 | implementer(opus) | DONE
- 한 일: synth_hwpx header.xml paraPr/heading/styles·단위 7
- 변경 파일(미커밋, .ai 제외): tests/synth_hwpx.py tests/unit/test_synth_hwpx.py 
- 커밋: 0906b09 [T-20261022-heading-levels][s3] hwp5: DocInfo PARA_SHAPE outline level -> Paragraph.level
- 다음: S4 리뷰
- 메모: unit 154

## [2026-10-22 23:05] S4 | hook | AUTO
- 한 일: 도구 호출 150회 경과
- 변경 파일(미커밋, .ai 제외): tests/synth_hwpx.py tests/unit/test_synth_hwpx.py 
- 커밋: 0906b09 [T-20261022-heading-levels][s3] hwp5: DocInfo PARA_SHAPE outline level -> Paragraph.level

## [2026-10-22 23:05] S4 | reviewer(sonnet) | DONE
- 한 일: VERDICT PASS, findings 없음
- 변경 파일(미커밋, .ai 제외): tests/synth_hwpx.py tests/unit/test_synth_hwpx.py 
- 커밋: 0906b09 [T-20261022-heading-levels][s3] hwp5: DocInfo PARA_SHAPE outline level -> Paragraph.level

## [2026-10-22 23:05] S4 | orchestrator | DONE
- 한 일: 합성 HWPX 생성기 검증 통과
- 변경 파일(미커밋, .ai 제외): tests/synth_hwpx.py tests/unit/test_synth_hwpx.py 
- 커밋: 0906b09 [T-20261022-heading-levels][s3] hwp5: DocInfo PARA_SHAPE outline level -> Paragraph.level
- 다음: S5 시작

## [2026-10-22 23:05] S5 | orchestrator | START
- 한 일: HWPX header.xml 파서·리더 연결
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: d76e0c1 [T-20261022-heading-levels][s4] tests: synthetic hwpx headings (header.xml paraPr/heading), byte-stability hashes

## [2026-10-22 23:06] S5 | hook | AUTO
- 한 일: 도구 호출 165회 경과
- 변경 파일(미커밋, .ai 제외): src/hwp2md/hwpx/body.py src/hwp2md/hwpx/reader.py src/hwp2md/hwpx/header.py 
- 커밋: d76e0c1 [T-20261022-heading-levels][s4] tests: synthetic hwpx headings (header.xml paraPr/heading), byte-stability hashes

## [2026-10-22 23:07] S5 | implementer(opus) | DONE
- 한 일: hwpx/header.py·reader/body 연결·단위 10+2
- 변경 파일(미커밋, .ai 제외): src/hwp2md/hwpx/body.py src/hwp2md/hwpx/header.py src/hwp2md/hwpx/reader.py tests/unit/test_cross_format.py tests/unit/test_hwpx_header.py 
- 커밋: d76e0c1 [T-20261022-heading-levels][s4] tests: synthetic hwpx headings (header.xml paraPr/heading), byte-stability hashes
- 다음: S5 리뷰
- 메모: unit 171, 실제 HWPX 1 0/80 0/32 0. resolve_entities 속성 미노출 → 동작 기반 테스트

## [2026-10-22 23:07] S5 | hook | AUTO
- 한 일: 도구 호출 180회 경과
- 변경 파일(미커밋, .ai 제외): src/hwp2md/hwpx/body.py src/hwp2md/hwpx/header.py src/hwp2md/hwpx/reader.py tests/unit/test_cross_format.py tests/unit/test_hwpx_header.py 
- 커밋: d76e0c1 [T-20261022-heading-levels][s4] tests: synthetic hwpx headings (header.xml paraPr/heading), byte-stability hashes

## [2026-10-22 23:07] S5 | reviewer(sonnet) | DONE
- 한 일: VERDICT PASS; E-8 동작 기반 대체는 약화 아님
- 변경 파일(미커밋, .ai 제외): src/hwp2md/hwpx/body.py src/hwp2md/hwpx/header.py src/hwp2md/hwpx/reader.py tests/unit/test_cross_format.py tests/unit/test_hwpx_header.py 
- 커밋: d76e0c1 [T-20261022-heading-levels][s4] tests: synthetic hwpx headings (header.xml paraPr/heading), byte-stability hashes
- 메모: lxml 6 resolve_entities 속성 없음 — _Entity 비공개 타입 의존

## [2026-10-22 23:07] S5 | orchestrator | DONE
- 한 일: HWPX header 파서 검증 통과
- 변경 파일(미커밋, .ai 제외): src/hwp2md/hwpx/body.py src/hwp2md/hwpx/header.py src/hwp2md/hwpx/reader.py tests/unit/test_cross_format.py tests/unit/test_hwpx_header.py 
- 커밋: d76e0c1 [T-20261022-heading-levels][s4] tests: synthetic hwpx headings (header.xml paraPr/heading), byte-stability hashes
- 다음: S6 시작

## [2026-10-22 23:07] S6 | orchestrator | START
- 한 일: 결정 기록·README·fixtures README
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: a6285ea [T-20261022-heading-levels][s5] hwpx: header.xml OUTLINE paraPr -> Paragraph.level, cross-format parity

## [2026-10-22 23:08] S6 | hook | AUTO
- 한 일: 도구 호출 195회 경과
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: a6285ea [T-20261022-heading-levels][s5] hwpx: header.xml OUTLINE paraPr -> Paragraph.level, cross-format parity

## [2026-10-22 23:08] S6 | implementer(opus) | DONE
- 한 일: decisions 3건·README·fixtures README
- 변경 파일(미커밋, .ai 제외): README.md docs/decisions.md tests/fixtures/README.md 
- 커밋: a6285ea [T-20261022-heading-levels][s5] hwpx: header.xml OUTLINE paraPr -> Paragraph.level, cross-format parity

## [2026-10-22 23:08] S6 | orchestrator | DONE
- 한 일: 문서 검증 통과 (grep 기준 전부 일치, diff 3파일 직접 확인)
- 변경 파일(미커밋, .ai 제외): README.md docs/decisions.md tests/fixtures/README.md 
- 커밋: a6285ea [T-20261022-heading-levels][s5] hwpx: header.xml OUTLINE paraPr -> Paragraph.level, cross-format parity
- 다음: S7 시작

## [2026-10-22 23:08] S7 | orchestrator | START
- 한 일: CLI 2행 제목 K개
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: f6bb4a8 [T-20261022-heading-levels][s6] docs: heading decisions (para shape source, clamp, CLI), README

## [2026-10-22 23:08] S7 | orchestrator | DONE
- 한 일: cli.py 2행 제목 K개 (3줄), 실제 샘플 5개 2행 불변, e2e 21 unit 171
- 변경 파일(미커밋, .ai 제외): src/hwp2md/cli.py 
- 커밋: f6bb4a8 [T-20261022-heading-levels][s6] docs: heading decisions (para shape source, clamp, CLI), README
- 다음: S8 시작
