# PROGRESS — T-20261023-extract-dropped (버려지던 HWP 요소 추출과 추출 한계 명시)

> append-only.

---

## [2026-10-23 17:32] S0 | planner(opus) | DONE
- 한 일: PLAN.md·OpenSpec extract-dropped 작성, 사용자 승인(Q7 MIT, Q8 기본 변환+고지)
- 변경 파일(미커밋, .ai 제외): ".ai/tasks/T-20261023-extract-dropped openspec/changes/extract-dropped/ 
- 커밋: ae6ed95 [T-20261023-extract-dropped][s0] V3 프론트엔드 시안·Stitch 원본·기능 명세 (선행 작업 커밋)
- 다음: S1 기준선 기록

## [2026-10-23 17:33] S1 | orchestrator | START
- 한 일: 기준선 기록
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 0d1546a [T-20261023-extract-dropped][record] PROGRESS 위치 정정 (STATE 태스크 줄 형식)

## [2026-10-23 17:35] S1 | runner(haiku) | DONE
- 한 일: 기준선: unit 6F/360P, e2e 6F/92P(샘플 집합 변화 4 + 브라우저 모드 2), CLI 69파일(종료0 61, 종료3 8)
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 0d1546a [T-20261023-extract-dropped][record] PROGRESS 위치 정정 (STATE 태스크 줄 형식)
- 다음: S2 샘플 선정 규칙

## [2026-10-23 17:35] S2 | orchestrator | START
- 한 일: 실제 샘플 선정 규칙 고정
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 7a6518d [T-20261023-extract-dropped][s1] 기준선 기록

## [2026-10-23 17:36] S2 | hook | AUTO
- 한 일: 도구 호출 15회 경과
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 7a6518d [T-20261023-extract-dropped][s1] 기준선 기록

## [2026-10-23 17:38] S2 | test-writer(sonnet) | DONE
- 한 일: tests/samples.py(LEGACY 5개·classify·all_samples) + 기존 테스트 7개 샘플 정의만 교체. 1회 수정(HWPML DOCTYPE 분류). unit 338P, e2e cli/api 51P, web_ui 8P(브라우저 모드 포함)
- 변경 파일(미커밋, .ai 제외): tests/e2e/conftest.py tests/e2e/test_cli_heading.py tests/e2e/test_cli_hwpx.py tests/e2e/test_cli_image.py tests/fixtures/README.md tests/unit/test_memory.py tests/unit/test_source_bytes.py tests/unit/test_web_app.py tests/samples.py 
- 커밋: 7a6518d [T-20261023-extract-dropped][s1] 기준선 기록
- 다음: S3 블록 모델·렌더 계약
- 메모: S1 브라우저 모드 실패 2건도 샘플 집합 원인이었음. test_cli_convert.py:16 *.hwp glob 잔존(현재 통과, 범위 밖)

## [2026-10-23 17:38] S3 | orchestrator | START
- 한 일: 블록 모델·렌더 계약
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: bced79e [T-20261023-extract-dropped][s2] 실제 샘플 선정 규칙 고정 (tests/samples.py)

## [2026-10-23 17:39] S3 | hook | AUTO
- 한 일: 도구 호출 30회 경과
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: bced79e [T-20261023-extract-dropped][s2] 실제 샘플 선정 규칙 고정 (tests/samples.py)

## [2026-10-23 17:45] S3 | hook | AUTO
- 한 일: 도구 호출 45회 경과
- 변경 파일(미커밋, .ai 제외): src/hwp2md/blocks.py src/hwp2md/render.py src/hwp2md/numbering.py src/hwp2md/skips.py tests/synth_items.py tests/unit/test_render_extract.py 
- 커밋: bced79e [T-20261023-extract-dropped][s2] 실제 샘플 선정 규칙 고정 (tests/samples.py)

## [2026-10-23 17:47] S3 | implementer(opus)+reviewer(sonnet) | DONE
- 한 일: blocks(Link/NoteRef/Math/ListInfo/Note/make_*/iter_images)·skips·numbering·render(safe_link_url·인라인·목록·Note)·synth_items(EXT_FIXTURES 16). unit 408P, 기준선 md 61개 동일, reviewer PASS
- 변경 파일(미커밋, .ai 제외): src/hwp2md/blocks.py src/hwp2md/numbering.py src/hwp2md/render.py src/hwp2md/skips.py tests/synth_items.py tests/unit/test_render_extract.py 
- 커밋: bced79e [T-20261023-extract-dropped][s2] 실제 샘플 선정 규칙 고정 (tests/samples.py)
- 다음: S4 결과·페이로드 건너뜀
- 메모: 수식 기대값은 to_latex('a over b')=='\frac{a}{b}' 가정(S6/S9 확인). _count_blocks 는 S4 에서 iter_images·Note 반영

## [2026-10-23 17:47] S4 | orchestrator | START
- 한 일: 결과·페이로드 건너뜀 연결
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 85410e8 [T-20261023-extract-dropped][s3] 블록 모델·렌더 계약

## [2026-10-23 17:48] S4 | hook | AUTO
- 한 일: 도구 호출 60회 경과
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 85410e8 [T-20261023-extract-dropped][s3] 블록 모델·렌더 계약

## [2026-10-23 17:49] S4 | hook | AUTO
- 한 일: 도구 호출 75회 경과
- 변경 파일(미커밋, .ai 제외): src/hwp2md/__init__.py src/hwp2md/convert.py src/hwp2md/hwp5/reader.py src/hwp2md/hwpx/reader.py src/hwp2md/memory.py tests/unit/test_memory.py tests/unit/test_convert_skipped.py 
- 커밋: 85410e8 [T-20261023-extract-dropped][s3] 블록 모델·렌더 계약

## [2026-10-23 17:50] S4 | implementer(opus) | DONE
- 한 일: convert/memory/__init__/리더 read_blocks(skips) 연결, ConvertResult·MemoryResult.skipped, 페이로드 skipped, _count_blocks·_write_images iter_images, 한컴 문구 docstring. unit 417P, 기준선 diffs 0
- 변경 파일(미커밋, .ai 제외): src/hwp2md/__init__.py src/hwp2md/convert.py src/hwp2md/hwp5/reader.py src/hwp2md/hwpx/reader.py src/hwp2md/memory.py tests/unit/test_memory.py tests/unit/test_convert_skipped.py 
- 커밋: 85410e8 [T-20261023-extract-dropped][s3] 블록 모델·렌더 계약
- 다음: P1 (S5~S8 병렬)
- 메모: test_memory 의 _raise_value_error 스텁이 skips 인자를 못 받아 TypeError 로 convert_failed 통과 → S5 에서 스텁 시그니처 보정

## [2026-10-23 17:50] S5 | orchestrator | START
- 한 일: P1 worktree
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 425f05a [T-20261023-extract-dropped][s4] 결과·페이로드 건너뜀 연결

## [2026-10-23 17:50] S6 | orchestrator | START
- 한 일: P1 worktree
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 425f05a [T-20261023-extract-dropped][s4] 결과·페이로드 건너뜀 연결

## [2026-10-23 17:50] S7 | orchestrator | START
- 한 일: P1 worktree
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 425f05a [T-20261023-extract-dropped][s4] 결과·페이로드 건너뜀 연결

## [2026-10-23 17:50] S8 | orchestrator | START
- 한 일: P1 worktree
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 425f05a [T-20261023-extract-dropped][s4] 결과·페이로드 건너뜀 연결

## [2026-10-23 17:53] S5 | implementer(opus) | RETRY
- 한 일: worktree 가 main(e18cd70)에서 생성되어 S3·S4 없음 + worktree 안 git 훅 차단 → 작업 0
- 변경 파일(미커밋, .ai 제외): .claude/ 
- 커밋: 425f05a [T-20261023-extract-dropped][s4] 결과·페이로드 건너뜀 연결
- 다음: 메인 트리에서 재실행 (S7 과 동시, 쓰기 범위 비중첩)

## [2026-10-23 17:53] S7 | orchestrator | RETRY
- 한 일: worktree 기반 커밋 오류로 중단(TaskStop)
- 변경 파일(미커밋, .ai 제외): .claude/ 
- 커밋: 425f05a [T-20261023-extract-dropped][s4] 결과·페이로드 건너뜀 연결
- 다음: 메인 트리에서 재실행

## [2026-10-23 17:54] P1 | hook | AUTO
- 한 일: 도구 호출 90회 경과
- 변경 파일(미커밋, .ai 제외): .claude/ 
- 커밋: 425f05a [T-20261023-extract-dropped][s4] 결과·페이로드 건너뜀 연결

## [2026-10-23 17:55] P1 | hook | AUTO
- 한 일: 도구 호출 105회 경과
- 변경 파일(미커밋, .ai 제외): src/hwp2md/__init__.py src/hwp2md/detect.py src/hwp2md/errors.py src/hwp2md/hwp5/reader.py src/hwp2md/hwpx/reader.py src/hwp2md/memory.py .claude/ NOTICE src/hwp2md/equation/ tests/unit/test_equation.py 
- 커밋: 425f05a [T-20261023-extract-dropped][s4] 결과·페이로드 건너뜀 연결

## [2026-10-23 17:56] P1 | hook | AUTO
- 한 일: 도구 호출 120회 경과
- 변경 파일(미커밋, .ai 제외): src/hwp2md/__init__.py src/hwp2md/detect.py src/hwp2md/errors.py src/hwp2md/hwp5/reader.py src/hwp2md/hwpx/reader.py src/hwp2md/memory.py tests/unit/test_memory.py NOTICE src/hwp2md/equation/ src/hwp2md/hwp5/aes.py src/hwp2md/hwp5/distdoc.py src/hwp2md/ole.py tests/synth_distdoc.py tests/synth_ole.py tests/unit/test_distdoc.py tests/unit/test_equation.py tests/unit/test_protection.py 
- 커밋: 425f05a [T-20261023-extract-dropped][s4] 결과·페이로드 건너뜀 연결

## [2026-10-23 17:58] P1 | hook | AUTO
- 한 일: 도구 호출 135회 경과
- 변경 파일(미커밋, .ai 제외): NOTICE src/hwp2md/__init__.py src/hwp2md/detect.py src/hwp2md/equation/__init__.py src/hwp2md/equation/eqedit.py src/hwp2md/equation/tokens.py src/hwp2md/errors.py src/hwp2md/hwp5/aes.py src/hwp2md/hwp5/distdoc.py src/hwp2md/hwp5/reader.py src/hwp2md/hwpx/reader.py src/hwp2md/memory.py src/hwp2md/ole.py tests/synth_distdoc.py tests/synth_ole.py tests/unit/test_distdoc.py tests/unit/test_equation.py tests/unit/test_memory.py tests/unit/test_ole_chart.py tests/unit/test_protection.py 
- 커밋: 425f05a [T-20261023-extract-dropped][s4] 결과·페이로드 건너뜀 연결

## [2026-10-23 17:59] S5 | implementer(opus) | DONE
- 한 일: DrmProtectedError·EncryptedDocumentError, DRM 서명 판별, HWP5 비트 1/4/10, HWPX manifest 암호화, 오류 코드 drm/encrypted 415. 실제 DRM 2개 → drm. test_protection 28
- 변경 파일(미커밋, .ai 제외): NOTICE src/hwp2md/__init__.py src/hwp2md/detect.py src/hwp2md/equation/__init__.py src/hwp2md/equation/eqedit.py src/hwp2md/equation/tokens.py src/hwp2md/errors.py src/hwp2md/hwp5/aes.py src/hwp2md/hwp5/distdoc.py src/hwp2md/hwp5/reader.py src/hwp2md/hwpx/reader.py src/hwp2md/memory.py src/hwp2md/ole.py tests/synth_distdoc.py tests/synth_ole.py tests/unit/test_distdoc.py tests/unit/test_equation.py tests/unit/test_memory.py tests/unit/test_ole_chart.py tests/unit/test_protection.py 
- 커밋: 425f05a [T-20261023-extract-dropped][s4] 결과·페이로드 건너뜀 연결
- 다음: S6 커밋

## [2026-10-23 17:59] S6 | implementer(opus) | DONE
- 한 일: python-hwpx 7ca4582 수식 변환기 벤더링(eqedit·tokens, noqa 1줄), to_latex 래퍼, NOTICE. to_latex('a over b')=\frac{a}{b}. test_equation 15
- 변경 파일(미커밋, .ai 제외): NOTICE src/hwp2md/equation/__init__.py src/hwp2md/equation/eqedit.py src/hwp2md/equation/tokens.py src/hwp2md/hwp5/aes.py src/hwp2md/hwp5/distdoc.py src/hwp2md/ole.py tests/synth_distdoc.py tests/synth_ole.py tests/unit/test_distdoc.py tests/unit/test_equation.py tests/unit/test_ole_chart.py 
- 커밋: 85e5abd [T-20261023-extract-dropped][s5] 보호 문서 판별 (DRM·비밀번호 전용 예외·오류 코드)
- 다음: S7 커밋

## [2026-10-23 17:59] S7 | implementer(opus) | DONE
- 한 일: ole.py(unwrap_hwpx_ole·chart_xml_to_blocks·ole_to_outcome), synth_ole(직접 CFB 구성: build_cfb 가 HWP 스트림만 받아 이탈, reviewer 수용), test_ole_chart 21
- 변경 파일(미커밋, .ai 제외): src/hwp2md/hwp5/aes.py src/hwp2md/hwp5/distdoc.py src/hwp2md/ole.py tests/synth_distdoc.py tests/synth_ole.py tests/unit/test_distdoc.py tests/unit/test_ole_chart.py 
- 커밋: e48c5c2 [T-20261023-extract-dropped][s6] 수식 변환기 벤더링 (python-hwpx, Apache-2.0)
- 다음: S8 커밋
