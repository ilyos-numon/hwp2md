# PROGRESS — T-20261022-image-extract

> append-only.

---

## [2026-10-22 23:54] S0 | orchestrator | DONE
- 한 일: PLAN.md·openspec change image-extract 작성 (validate OK, 매핑 18/18, 셀프체크)
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 18d054d [T-20261022-image-extract][plan] 이미지 추출 (BinData → <stem>_images/, 상대 경로 링크)
- 다음: 사용자 승인 대기
- 메모: fable 한도 → opus 전환 지시. planner는 완성 직후 중단돼 재호출 불필요

## [2026-10-22 23:56] S1 | orchestrator | START
- 한 일: 블록 모델·이미지 헬퍼·렌더·변환 결과
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: ec3b8a9 [T-20261022-image-extract][plan] approved (§7 기본값)

## [2026-10-22 23:57] S1 | implementer(opus) | PARTIAL
- 한 일: Image·images.py·render·convert, unit 184 e2e 33
- 변경 파일(미커밋, .ai 제외): src/hwp2md/__init__.py src/hwp2md/blocks.py src/hwp2md/convert.py src/hwp2md/render.py src/hwp2md/images.py tests/unit/test_images.py 
- 커밋: ec3b8a9 [T-20261022-image-extract][plan] approved (§7 기본값)
- 다음: mypy 2건 범위 밖
- 메모: Block Union 확장으로 hwp5/body.py:142, hwpx/body.py:122 else 분기가 Table 가정

## [2026-10-22 23:57] S1 | orchestrator | RETRY
- 한 일: 쓰기 범위에 hwp5/body.py·hwpx/body.py의 else→elif isinstance(b, Table) 1줄씩 추가
- 변경 파일(미커밋, .ai 제외): src/hwp2md/__init__.py src/hwp2md/blocks.py src/hwp2md/convert.py src/hwp2md/render.py src/hwp2md/images.py tests/unit/test_images.py 
- 커밋: ec3b8a9 [T-20261022-image-extract][plan] approved (§7 기본값)
- 다음: implementer 재호출

## [2026-10-22 23:57] S1 | hook | AUTO
- 한 일: 도구 호출 15회 경과
- 변경 파일(미커밋, .ai 제외): src/hwp2md/__init__.py src/hwp2md/blocks.py src/hwp2md/convert.py src/hwp2md/render.py src/hwp2md/images.py tests/unit/test_images.py 
- 커밋: ec3b8a9 [T-20261022-image-extract][plan] approved (§7 기본값)

## [2026-10-22 23:58] S1 | implementer(opus) | DONE
- 한 일: Image·images.py·render·convert + 리더 else→elif 2줄
- 변경 파일(미커밋, .ai 제외): src/hwp2md/__init__.py src/hwp2md/blocks.py src/hwp2md/convert.py src/hwp2md/hwp5/body.py src/hwp2md/hwpx/body.py src/hwp2md/images.py src/hwp2md/render.py tests/unit/test_images.py 
- 커밋: ec3b8a9 [T-20261022-image-extract][plan] approved (§7 기본값)
- 다음: S1 리뷰
- 메모: mypy17 OK unit184 e2e33

## [2026-10-22 23:59] S1 | reviewer(sonnet) | DONE
- 한 일: VERDICT PASS
- 변경 파일(미커밋, .ai 제외): src/hwp2md/__init__.py src/hwp2md/blocks.py src/hwp2md/convert.py src/hwp2md/hwp5/body.py src/hwp2md/hwpx/body.py src/hwp2md/images.py src/hwp2md/render.py tests/unit/test_images.py 
- 커밋: ec3b8a9 [T-20261022-image-extract][plan] approved (§7 기본값)

## [2026-10-22 23:59] S1 | orchestrator | DONE
- 한 일: 블록 모델·이미지 헬퍼 검증 통과
- 변경 파일(미커밋, .ai 제외): src/hwp2md/__init__.py src/hwp2md/blocks.py src/hwp2md/convert.py src/hwp2md/hwp5/body.py src/hwp2md/hwpx/body.py src/hwp2md/images.py src/hwp2md/render.py tests/unit/test_images.py 
- 커밋: ec3b8a9 [T-20261022-image-extract][plan] approved (§7 기본값)
- 다음: S2 시작

## [2026-10-22 23:59] S2 | orchestrator | START
- 한 일: 합성 HWP5 생성기 이미지
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 2e036b9 [T-20261022-image-extract][s1] blocks/render/convert: Image block, images dir, ConvertResult image fields

## [2026-10-22 23:59] S2 | hook | AUTO
- 한 일: 도구 호출 30회 경과
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 2e036b9 [T-20261022-image-extract][s1] blocks/render/convert: Image block, images dir, ConvertResult image fields

## [2026-10-23 00:01] S2 | implementer(opus) | DONE
- 한 일: SynthImage·BIN_DATA·BinData 스트림·gso 레코드·fixture 4종, 단위 10
- 변경 파일(미커밋, .ai 제외): tests/synth_hwp5.py tests/unit/test_synth_hwp5.py 
- 커밋: 2e036b9 [T-20261022-image-extract][s1] blocks/render/convert: Image block, images dir, ConvertResult image fields
- 다음: S2 리뷰
- 메모: synth 38 passed(플랜 33은 parametrize 미산입 오기), unit 194

## [2026-10-23 00:01] S2 | hook | AUTO
- 한 일: 도구 호출 45회 경과
- 변경 파일(미커밋, .ai 제외): tests/synth_hwp5.py tests/unit/test_synth_hwp5.py 
- 커밋: 2e036b9 [T-20261022-image-extract][s1] blocks/render/convert: Image block, images dir, ConvertResult image fields

## [2026-10-23 00:01] S2 | reviewer(sonnet) | DONE
- 한 일: VERDICT PASS; PICTURE bindata id @71 스펙 기억 기준 일치
- 변경 파일(미커밋, .ai 제외): tests/synth_hwp5.py tests/unit/test_synth_hwp5.py 
- 커밋: 2e036b9 [T-20261022-image-extract][s1] blocks/render/convert: Image block, images dir, ConvertResult image fields

## [2026-10-23 00:01] S2 | orchestrator | DONE
- 한 일: 합성 HWP5 생성기 이미지 검증 통과
- 변경 파일(미커밋, .ai 제외): tests/synth_hwp5.py tests/unit/test_synth_hwp5.py 
- 커밋: 2e036b9 [T-20261022-image-extract][s1] blocks/render/convert: Image block, images dir, ConvertResult image fields
- 다음: S3 시작
