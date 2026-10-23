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

## [2026-10-23 17:59] S8 | implementer(opus) | DONE
- 한 일: 순수 파이썬 AES-128 ECB 복호 + distdoc(키 유도·decrypt_view_text), synth_distdoc, test_distdoc 28(FIPS-197). 실제 배포용 2개 복호 0.004s/0.013s, 레코드 819/5006 정상. P1 통합: unit 510P, 기준선 61 동일, reviewer PASS
- 변경 파일(미커밋, .ai 제외): src/hwp2md/hwp5/aes.py src/hwp2md/hwp5/distdoc.py tests/synth_distdoc.py tests/unit/test_distdoc.py 
- 커밋: c5b1bc5 [T-20261023-extract-dropped][s7] OLE·OOXML 차트 모듈
- 다음: R1 (S9~S11)
- 메모: P1 worktree 가 main 에서 생성돼 S5·S7 은 메인 트리 재실행, S6·S8 은 새 파일만이라 복사로 합침. 메모리 기록 갱신

## [2026-10-23 17:59] S9 | orchestrator | START
- 한 일: R1 worktree .claude/worktrees/s9
- 변경 파일(미커밋, .ai 제외): .claude/ 
- 커밋: 1acb24c [T-20261023-extract-dropped][s8] 배포용 문서 복호 모듈 (순수 파이썬 AES)

## [2026-10-23 17:59] S10 | orchestrator | START
- 한 일: R1 worktree .claude/worktrees/s10
- 변경 파일(미커밋, .ai 제외): .claude/ 
- 커밋: 1acb24c [T-20261023-extract-dropped][s8] 배포용 문서 복호 모듈 (순수 파이썬 AES)

## [2026-10-23 17:59] S11 | orchestrator | START
- 한 일: R1 worktree .claude/worktrees/s11
- 변경 파일(미커밋, .ai 제외): .claude/ 
- 커밋: 1acb24c [T-20261023-extract-dropped][s8] 배포용 문서 복호 모듈 (순수 파이썬 AES)

## [2026-10-23 18:00] R1 | hook | AUTO
- 한 일: 도구 호출 150회 경과
- 변경 파일(미커밋, .ai 제외): .claude/ 
- 커밋: 1acb24c [T-20261023-extract-dropped][s8] 배포용 문서 복호 모듈 (순수 파이썬 AES)

## [2026-10-23 18:00] R1 | hook | AUTO
- 한 일: 도구 호출 165회 경과
- 변경 파일(미커밋, .ai 제외): .claude/ 
- 커밋: 1acb24c [T-20261023-extract-dropped][s8] 배포용 문서 복호 모듈 (순수 파이썬 AES)

## [2026-10-23 18:01] R1 | hook | AUTO
- 한 일: 도구 호출 180회 경과
- 변경 파일(미커밋, .ai 제외): .claude/ 
- 커밋: 1acb24c [T-20261023-extract-dropped][s8] 배포용 문서 복호 모듈 (순수 파이썬 AES)

## [2026-10-23 18:03] R1 | hook | AUTO
- 한 일: 도구 호출 195회 경과
- 변경 파일(미커밋, .ai 제외): .claude/ 
- 커밋: 1acb24c [T-20261023-extract-dropped][s8] 배포용 문서 복호 모듈 (순수 파이썬 AES)

## [2026-10-23 18:04] R1 | hook | AUTO
- 한 일: 도구 호출 210회 경과
- 변경 파일(미커밋, .ai 제외): .claude/ 
- 커밋: 1acb24c [T-20261023-extract-dropped][s8] 배포용 문서 복호 모듈 (순수 파이썬 AES)

## [2026-10-23 18:05] R1 | hook | AUTO
- 한 일: 도구 호출 225회 경과
- 변경 파일(미커밋, .ai 제외): .claude/ 
- 커밋: 1acb24c [T-20261023-extract-dropped][s8] 배포용 문서 복호 모듈 (순수 파이썬 AES)

## [2026-10-23 18:06] R1 | hook | AUTO
- 한 일: 도구 호출 240회 경과
- 변경 파일(미커밋, .ai 제외): .claude/ 
- 커밋: 1acb24c [T-20261023-extract-dropped][s8] 배포용 문서 복호 모듈 (순수 파이썬 AES)

## [2026-10-23 18:08] R1 | hook | AUTO
- 한 일: 도구 호출 255회 경과
- 변경 파일(미커밋, .ai 제외): .claude/ 
- 커밋: 1acb24c [T-20261023-extract-dropped][s8] 배포용 문서 복호 모듈 (순수 파이썬 AES)

## [2026-10-23 18:10] R1 | hook | AUTO
- 한 일: 도구 호출 270회 경과
- 변경 파일(미커밋, .ai 제외): .claude/worktrees/s10 .claude/worktrees/s11 .claude/worktrees/s9 src/hwp2md/convert.py src/hwp2md/detect.py src/hwp2md/hwp5/body.py src/hwp2md/hwp5/reader.py src/hwp2md/hwp5/records.py src/hwp2md/hwpml/__init__.py src/hwp2md/hwpml/body.py src/hwp2md/hwpml/reader.py src/hwp2md/hwpx/body.py src/hwp2md/hwpx/reader.py tests/synth_hwp5.py tests/synth_hwpml.py tests/synth_hwpx.py tests/unit/test_hwp5_inline.py tests/unit/test_hwpml.py tests/unit/test_hwpx_body.py tests/unit/test_hwpx_inline.py 
- 커밋: 1acb24c [T-20261023-extract-dropped][s8] 배포용 문서 복호 모듈 (순수 파이썬 AES)

## [2026-10-23 18:11] S9 | implementer(opus) | DONE
- 한 일: decode_para_runs·CtrlMark, 컨트롤 1:1 대응(불일치 폴백), %hlk→Link, fn/en→NoteRef+Note, eqed→Math, head/foot·tcmt·memo 건너뜀. 실제: 수식 3/3, 각주 3/3, 링크 2, 머리말 5/5, 누름틀 1/1
- 변경 파일(미커밋, .ai 제외): src/hwp2md/convert.py src/hwp2md/detect.py src/hwp2md/hwp5/body.py src/hwp2md/hwp5/reader.py src/hwp2md/hwp5/records.py src/hwp2md/hwpml/__init__.py src/hwp2md/hwpml/body.py src/hwp2md/hwpml/reader.py src/hwp2md/hwpx/body.py src/hwp2md/hwpx/reader.py tests/synth_hwp5.py tests/synth_hwpml.py tests/synth_hwpx.py tests/unit/test_hwp5_inline.py tests/unit/test_hwpml.py tests/unit/test_hwpx_body.py tests/unit/test_hwpx_inline.py 
- 커밋: 1acb24c [T-20261023-extract-dropped][s8] 배포용 문서 복호 모듈 (순수 파이썬 AES)
- 다음: S10 커밋

## [2026-10-23 18:11] S10 | implementer(opus) | DONE
- 한 일: HWPX fieldBegin HYPERLINK→Link, footNote/endNote→NoteRef+Note(DocContext), equation→Math, header/footer·hiddenComment·memo 건너뜀. test_hwpx_body §1-D 1개 갱신. 실제 HWPX 11개 header_footer 2
- 변경 파일(미커밋, .ai 제외): src/hwp2md/convert.py src/hwp2md/detect.py src/hwp2md/hwpml/__init__.py src/hwp2md/hwpml/body.py src/hwp2md/hwpml/reader.py src/hwp2md/hwpx/body.py src/hwp2md/hwpx/reader.py tests/synth_hwpml.py tests/synth_hwpx.py tests/unit/test_hwpml.py tests/unit/test_hwpx_body.py tests/unit/test_hwpx_inline.py 
- 커밋: 398fb83 [T-20261023-extract-dropped][s9] HWP 5.0 단락 안 요소 (링크·각주·수식·필드, 머리말 건너뜀)
- 다음: S11 커밋
- 메모: 표 칸 안 각주 참조는 칸이 글자만이라 미표시 → S13 칸 인라인에서 해결

## [2026-10-23 18:11] S11 | implementer(opus) | DONE
- 한 일: hwpml 패키지(looks_like_hwpml·prepare_xml 안전 엔티티·read_blocks 본문/제목/표/그림), detect ④, convert 분기. 실제 HWPML 2개 종료 3→0. R1 통합: unit 617P, 실제 샘플 md 변화 7(머리말 제거3·링크2·각주1·수식1), reviewer PASS
- 변경 파일(미커밋, .ai 제외): src/hwp2md/convert.py src/hwp2md/detect.py src/hwp2md/hwpml/__init__.py src/hwp2md/hwpml/body.py src/hwp2md/hwpml/reader.py tests/synth_hwpml.py tests/unit/test_hwpml.py 
- 커밋: 50f20a9 [T-20261023-extract-dropped][s10] HWPX 단락 안 요소
- 다음: R2 (S12~S14)
- 메모: orchestrator: synth_hwpml 의 SubVersion 속성 1줄 삭제(sanitize IPv4 오탐, 리더 미사용). reviewer 가 git add -N 으로 .claude worktree 를 인덱스에 올린 것 git reset 으로 제거. worktree venv 가 Python 3.14 로 생성됨 → 다음 묶음은 uv sync --python 3.12

## [2026-10-23 18:12] S12 | orchestrator | START
- 한 일: R2 worktree .claude/worktrees/s12
- 변경 파일(미커밋, .ai 제외): .claude/ 
- 커밋: d59ecd1 [T-20261023-extract-dropped][s11] HWPML 2.x 입력 (판별·본문·표·그림)

## [2026-10-23 18:12] S13 | orchestrator | START
- 한 일: R2 worktree .claude/worktrees/s13
- 변경 파일(미커밋, .ai 제외): .claude/ 
- 커밋: d59ecd1 [T-20261023-extract-dropped][s11] HWPML 2.x 입력 (판별·본문·표·그림)

## [2026-10-23 18:12] S14 | orchestrator | START
- 한 일: R2 worktree .claude/worktrees/s14
- 변경 파일(미커밋, .ai 제외): .claude/ 
- 커밋: d59ecd1 [T-20261023-extract-dropped][s11] HWPML 2.x 입력 (판별·본문·표·그림)

## [2026-10-23 18:13] R2 | hook | AUTO
- 한 일: 도구 호출 285회 경과
- 변경 파일(미커밋, .ai 제외): .claude/ 
- 커밋: d59ecd1 [T-20261023-extract-dropped][s11] HWPML 2.x 입력 (판별·본문·표·그림)

## [2026-10-23 18:13] R2 | hook | AUTO
- 한 일: 도구 호출 300회 경과
- 변경 파일(미커밋, .ai 제외): .claude/ 
- 커밋: d59ecd1 [T-20261023-extract-dropped][s11] HWPML 2.x 입력 (판별·본문·표·그림)

## [2026-10-23 18:13] R2 | hook | AUTO
- 한 일: 도구 호출 315회 경과
- 변경 파일(미커밋, .ai 제외): .claude/ 
- 커밋: d59ecd1 [T-20261023-extract-dropped][s11] HWPML 2.x 입력 (판별·본문·표·그림)

## [2026-10-23 18:14] R2 | hook | AUTO
- 한 일: 도구 호출 330회 경과
- 변경 파일(미커밋, .ai 제외): .claude/ 
- 커밋: d59ecd1 [T-20261023-extract-dropped][s11] HWPML 2.x 입력 (판별·본문·표·그림)

## [2026-10-23 18:15] R2 | hook | AUTO
- 한 일: 도구 호출 345회 경과
- 변경 파일(미커밋, .ai 제외): .claude/ 
- 커밋: d59ecd1 [T-20261023-extract-dropped][s11] HWPML 2.x 입력 (판별·본문·표·그림)

## [2026-10-23 18:17] R2 | hook | AUTO
- 한 일: 도구 호출 360회 경과
- 변경 파일(미커밋, .ai 제외): .claude/ 
- 커밋: d59ecd1 [T-20261023-extract-dropped][s11] HWPML 2.x 입력 (판별·본문·표·그림)

## [2026-10-23 18:19] R2 | hook | AUTO
- 한 일: 도구 호출 375회 경과
- 변경 파일(미커밋, .ai 제외): .claude/ 
- 커밋: d59ecd1 [T-20261023-extract-dropped][s11] HWPML 2.x 입력 (판별·본문·표·그림)

## [2026-10-23 18:20] R2 | hook | AUTO
- 한 일: 도구 호출 390회 경과
- 변경 파일(미커밋, .ai 제외): .claude/ 
- 커밋: d59ecd1 [T-20261023-extract-dropped][s11] HWPML 2.x 입력 (판별·본문·표·그림)

## [2026-10-23 18:21] S13 | implementer(opus) | DONE
- 한 일: HWPX 칸 인라인(make_table, 칸 그림·각주 참조), 캡션, 도형 drawText·container 재귀, chart/ole, textart·form_control·image_missing. test_hwpx_objects 41. 실제 HWPX 11개 오류 0, 칸 그림 XML 수와 일치
- 변경 파일(미커밋, .ai 제외): .claude/ 
- 커밋: d59ecd1 [T-20261023-extract-dropped][s11] HWPML 2.x 입력 (판별·본문·표·그림)
- 다음: S12·S14 대기 후 R2 합침
- 메모: 옛 칸 그림 단언 2개 실패 → PLAN §1-D·CELL_DESELECT 보완(orchestrator)

## [2026-10-23 18:21] R2 | hook | AUTO
- 한 일: 도구 호출 405회 경과
- 변경 파일(미커밋, .ai 제외): .claude/ 
- 커밋: d59ecd1 [T-20261023-extract-dropped][s11] HWPML 2.x 입력 (판별·본문·표·그림)

## [2026-10-23 18:21] S12 | implementer(opus) | DONE
- 한 일: HWP5 칸 인라인 그림(번호 소비), 캡션 LIST_HEADER 분리(30B vs 칸 47B), gso 하위 글상자·묶음·OLE(ID 오프셋 12, 4B 길이 접두 CFB)·글맵시, image_link/missing. test_hwp5_objects 20. 실제: 칸 그림 11/11, 글상자 2/2·10/10, 차트 샘플 OLE 는 스트림 0개 빈 CFB → ole 1
- 변경 파일(미커밋, .ai 제외): .claude/ 
- 커밋: d59ecd1 [T-20261023-extract-dropped][s11] HWPML 2.x 입력 (판별·본문·표·그림)
- 다음: S14 대기 후 R2 합침
- 메모: 실제 OOXML 차트 샘플 없음 → 차트 추출은 합성으로만 검증 (S22 한계 문서에 기록). collect_images 가 TEXTBOX_IMAGE 도 수집(합침 후 S13·S14 테스트 재확인)

## [2026-10-23 18:23] S14 | implementer(opus) | DONE
- 한 일: HWPML 링크·각주·수식·머리말 건너뜀·숨은 설명·캡션·글상자·묶음·OLE·칸 그림·목록, test_hwpml_elements 33(EXT_FIXTURES 16). 실제 HWPML 2개 rc 0, header_footer 2씩. R2 통합: unit 707P(+4 옛 칸 그림 단언 → S18), 실제 샘플 오류 0·md 변화 15, reviewer PASS
- 변경 파일(미커밋, .ai 제외): src/hwp2md/hwpml/body.py src/hwp2md/hwpml/reader.py src/hwp2md/hwpx/bindata.py src/hwp2md/hwpx/body.py src/hwp2md/hwpx/reader.py tests/synth_hwpml.py tests/synth_hwpx.py .claude/ tests/unit/test_hwpml_elements.py tests/unit/test_hwpx_objects.py 
- 커밋: 663b98f [T-20261023-extract-dropped][s12] HWP 5.0 개체 (칸 그림·캡션·글상자·묶음·OLE)
- 다음: R3 (S15~S17)
- 메모: S18: 글자-개체-글자 혼합 단락 교차 fixture 추가해 HWPX(개체 뒤)·HWPML(분할) 배치 차이 확인. S14 CAPTION·DRAWTEXT·OLE 위치는 샘플 없이 추정

## [2026-10-23 18:23] R2 | hook | AUTO
- 한 일: 도구 호출 420회 경과
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 81169a0 [T-20261023-extract-dropped][s14] HWPML 요소 (링크·각주·수식·캡션·글상자·목록·OLE)

## [2026-10-23 18:23] S15 | orchestrator | START
- 한 일: R3 worktree .claude/worktrees/s15
- 변경 파일(미커밋, .ai 제외): .claude/ 
- 커밋: 81169a0 [T-20261023-extract-dropped][s14] HWPML 요소 (링크·각주·수식·캡션·글상자·목록·OLE)

## [2026-10-23 18:23] S16 | orchestrator | START
- 한 일: R3 worktree .claude/worktrees/s16
- 변경 파일(미커밋, .ai 제외): .claude/ 
- 커밋: 81169a0 [T-20261023-extract-dropped][s14] HWPML 요소 (링크·각주·수식·캡션·글상자·목록·OLE)

## [2026-10-23 18:23] S17 | orchestrator | START
- 한 일: R3 worktree .claude/worktrees/s17
- 변경 파일(미커밋, .ai 제외): .claude/ 
- 커밋: 81169a0 [T-20261023-extract-dropped][s14] HWPML 요소 (링크·각주·수식·캡션·글상자·목록·OLE)

## [2026-10-23 18:24] R3 | hook | AUTO
- 한 일: 도구 호출 435회 경과
- 변경 파일(미커밋, .ai 제외): .claude/ 
- 커밋: 81169a0 [T-20261023-extract-dropped][s14] HWPML 요소 (링크·각주·수식·캡션·글상자·목록·OLE)

## [2026-10-23 18:25] R3 | hook | AUTO
- 한 일: 도구 호출 450회 경과
- 변경 파일(미커밋, .ai 제외): .claude/ 
- 커밋: 81169a0 [T-20261023-extract-dropped][s14] HWPML 요소 (링크·각주·수식·캡션·글상자·목록·OLE)

## [2026-10-23 18:25] R3 | hook | AUTO
- 한 일: 도구 호출 465회 경과
- 변경 파일(미커밋, .ai 제외): .claude/ 
- 커밋: 81169a0 [T-20261023-extract-dropped][s14] HWPML 요소 (링크·각주·수식·캡션·글상자·목록·OLE)

## [2026-10-23 18:26] R3 | hook | AUTO
- 한 일: 도구 호출 480회 경과
- 변경 파일(미커밋, .ai 제외): .claude/ 
- 커밋: 81169a0 [T-20261023-extract-dropped][s14] HWPML 요소 (링크·각주·수식·캡션·글상자·목록·OLE)

## [2026-10-23 18:27] R3 | hook | AUTO
- 한 일: 도구 호출 495회 경과
- 변경 파일(미커밋, .ai 제외): .claude/ 
- 커밋: 81169a0 [T-20261023-extract-dropped][s14] HWPML 요소 (링크·각주·수식·캡션·글상자·목록·OLE)

## [2026-10-23 18:28] R3 | hook | AUTO
- 한 일: 도구 호출 510회 경과
- 변경 파일(미커밋, .ai 제외): .claude/ 
- 커밋: 81169a0 [T-20261023-extract-dropped][s14] HWPML 요소 (링크·각주·수식·캡션·글상자·목록·OLE)

## [2026-10-23 18:31] R3 | hook | AUTO
- 한 일: 도구 호출 525회 경과
- 변경 파일(미커밋, .ai 제외): src/hwp2md/hwp5/body.py src/hwp2md/hwp5/docinfo.py src/hwp2md/hwp5/reader.py src/hwp2md/hwpx/body.py src/hwp2md/hwpx/header.py tests/synth_distdoc.py tests/synth_hwp5.py tests/synth_hwpx.py .claude/ tests/unit/test_hwp5_distribution.py tests/unit/test_hwp5_lists.py tests/unit/test_hwpx_lists.py 
- 커밋: 81169a0 [T-20261023-extract-dropped][s14] HWPML 요소 (링크·각주·수식·캡션·글상자·목록·OLE)

## [2026-10-23 18:32] S15 | implementer(opus) | DONE
- 한 일: HWP5 ParaShape head_id(@30, 1-기준), NUMBERING(문단 머리 12B, 수준별 시작번호)·BULLET, 단락 ListInfo. test_hwp5_lists 19. 실제: 본문 목록 4/4, 칸 안 22개는 계약상 미표시
- 변경 파일(미커밋, .ai 제외): src/hwp2md/hwp5/body.py src/hwp2md/hwp5/docinfo.py src/hwp2md/hwp5/reader.py src/hwp2md/hwpx/body.py src/hwp2md/hwpx/header.py tests/synth_distdoc.py tests/synth_hwp5.py tests/synth_hwpx.py .claude/ tests/unit/test_hwp5_distribution.py tests/unit/test_hwp5_lists.py tests/unit/test_hwpx_lists.py 
- 커밋: 81169a0 [T-20261023-extract-dropped][s14] HWPML 요소 (링크·각주·수식·캡션·글상자·목록·OLE)
- 다음: S16 커밋
- 메모: 칸 안 목록 머리 글자 → PLAN §4-D 추가, S18 구현

## [2026-10-23 18:32] S16 | implementer(opus) | DONE
- 한 일: HWPX header numbering/bullet/paraHead, paraPr heading NUMBER/BULLET(switch 포함) → ListInfo. test_hwpx_lists 24. 실제 HWPX 목록 0(inventory 일치)
- 변경 파일(미커밋, .ai 제외): src/hwp2md/hwp5/reader.py src/hwp2md/hwpx/body.py src/hwp2md/hwpx/header.py tests/synth_distdoc.py tests/synth_hwpx.py .claude/ tests/unit/test_hwp5_distribution.py tests/unit/test_hwpx_lists.py 
- 커밋: 6baa303 [T-20261023-extract-dropped][s15] HWP 5.0 번호·글머리표 목록
- 다음: S17 커밋

## [2026-10-23 18:32] S17 | implementer(opus) | DONE
- 한 일: 배포용 문서 ViewText 복호→inflate→변환, _strip_aes_padding, ViewText 없음/inflate 실패 → UnsupportedHwpError. test_hwp5_distribution 12. 실제 배포용 2개 rc 0 (0.12s/0.08s). R3 통합: unit 762P(+4 S18), 실제 오류 0·rc 3→0 4개(HWPML2+배포용2)·md 변화 17, reviewer PASS
- 변경 파일(미커밋, .ai 제외): src/hwp2md/hwp5/reader.py tests/synth_distdoc.py .claude/ tests/unit/test_hwp5_distribution.py 
- 커밋: edc21b6 [T-20261023-extract-dropped][s16] HWPX 번호·글머리표 목록
- 다음: S18 교차 포맷
- 메모: 비차단: inflate 실패·패딩 제거 직접 단위 테스트 없음(간접 커버)

## [2026-10-23 18:32] S18 | orchestrator | START
- 한 일: 교차 포맷 정합
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: e0a7da1 [T-20261023-extract-dropped][s17] 배포용 문서 변환 (ViewText 복호)

## [2026-10-23 18:33] R3 | hook | AUTO
- 한 일: 도구 호출 540회 경과
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: e0a7da1 [T-20261023-extract-dropped][s17] 배포용 문서 변환 (ViewText 복호)

## [2026-10-23 18:34] R3 | hook | AUTO
- 한 일: 도구 호출 555회 경과
- 변경 파일(미커밋, .ai 제외): tests/synth_hwp5.py tests/unit/test_cross_format.py 
- 커밋: e0a7da1 [T-20261023-extract-dropped][s17] 배포용 문서 변환 (ViewText 복호)

## [2026-10-23 18:37] R3 | hook | AUTO
- 한 일: 도구 호출 570회 경과
- 변경 파일(미커밋, .ai 제외): src/hwp2md/hwpml/body.py tests/synth_hwp5.py tests/unit/test_cross_format.py tests/unit/test_cross_format_extract.py 
- 커밋: e0a7da1 [T-20261023-extract-dropped][s17] 배포용 문서 변환 (ViewText 복호)

## [2026-10-23 18:39] S18 | implementer(opus) | BLOCKED
- 한 일: 칸 그림 기대값·칸 목록 머리 글자·교차 테스트 34개 통과, HWPML 개체 블록을 앵커 단락 뒤로 맞춤
- 변경 파일(미커밋, .ai 제외): src/hwp2md/hwp5/body.py src/hwp2md/hwpml/body.py src/hwp2md/hwpx/body.py tests/synth_hwp5.py tests/unit/test_cross_format.py tests/unit/test_cross_format_extract.py 
- 커밋: e0a7da1 [T-20261023-extract-dropped][s17] 배포용 문서 변환 (ViewText 복호)
- 다음: test_hwpml_elements::test_container_children_in_order 기대값을 [앞뒤,상자,타원]으로 바꾸는 §1-D 추가 승인 필요

## [2026-10-23 18:39] R3 | hook | AUTO
- 한 일: 도구 호출 585회 경과
- 변경 파일(미커밋, .ai 제외): src/hwp2md/hwp5/body.py src/hwp2md/hwpml/body.py src/hwp2md/hwpx/body.py tests/synth_hwp5.py tests/unit/test_cross_format.py tests/unit/test_cross_format_extract.py 
- 커밋: e0a7da1 [T-20261023-extract-dropped][s17] 배포용 문서 변환 (ViewText 복호)

## [2026-10-23 18:39] S18 | implementer(opus) | RETRY
- 한 일: 칸 그림 기대값·칸 목록 머리 글자·HWPML 개체 배치 통일·image_missing 완료, S14 신규 테스트 1개가 옛 HWPML 분할 동작 고정
- 변경 파일(미커밋, .ai 제외): src/hwp2md/hwp5/body.py src/hwp2md/hwpml/body.py src/hwp2md/hwpx/body.py tests/synth_hwp5.py tests/unit/test_cross_format.py tests/unit/test_cross_format_extract.py 
- 커밋: e0a7da1 [T-20261023-extract-dropped][s17] 배포용 문서 변환 (ViewText 복호)
- 다음: §1-D 추가 후 같은 에이전트 재호출(테스트 1개 기대값 갱신)

## [2026-10-23 18:40] S18 | implementer(opus) | DONE
- 한 일: 칸 그림 기대값 갱신(번호 소비), 칸 안 목록 머리 글자(세 리더), HWPML 개체 배치를 앵커 단락 뒤로 통일 + image_missing, test_cross_format_extract 34. unit 800P(제외 없음). 실제 칸 목록 머리 19/22(3개는 빈 단락)
- 변경 파일(미커밋, .ai 제외): src/hwp2md/hwp5/body.py src/hwp2md/hwpml/body.py src/hwp2md/hwpx/body.py tests/synth_hwp5.py tests/unit/test_cross_format.py tests/unit/test_hwpml_elements.py tests/unit/test_cross_format_extract.py 
- 커밋: e0a7da1 [T-20261023-extract-dropped][s17] 배포용 문서 변환 (ViewText 복호)
- 다음: S19 CLI
- 메모: §1-D 추가 2건(test_container_children_in_order, _IMAGE_BYTES 키) orchestrator 승인

## [2026-10-23 18:40] S19 | orchestrator | START
- 한 일: CLI 오류 문구·건너뜀 요약
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: c3e51db [T-20261023-extract-dropped][s18] 교차 포맷 정합 (칸 그림·칸 목록·개체 배치)

## [2026-10-23 18:41] S19 | hook | AUTO
- 한 일: 도구 호출 600회 경과
- 변경 파일(미커밋, .ai 제외): src/hwp2md/cli.py 
- 커밋: c3e51db [T-20261023-extract-dropped][s18] 교차 포맷 정합 (칸 그림·칸 목록·개체 배치)

## [2026-10-23 18:41] S19 | implementer(opus) | DONE
- 한 일: cli.py: DRM·암호 전용 문구(rc3), 건너뜀 요약 줄, INPUT 도움말. unit 800P, CLI e2e 24P, DRM 합성 rc3, 머리말 합성 '건너뜀: 머리말·꼬리말 2개'
- 변경 파일(미커밋, .ai 제외): src/hwp2md/cli.py 
- 커밋: c3e51db [T-20261023-extract-dropped][s18] 교차 포맷 정합 (칸 그림·칸 목록·개체 배치)
- 다음: P3 (S20~S23 메인 트리 동시)

## [2026-10-23 18:41] S20 | orchestrator | START
- 한 일: P3 메인 트리
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 1b855d4 [T-20261023-extract-dropped][s19] CLI 보호 문서 문구·건너뜀 요약

## [2026-10-23 18:41] S21 | orchestrator | START
- 한 일: P3 메인 트리
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 1b855d4 [T-20261023-extract-dropped][s19] CLI 보호 문서 문구·건너뜀 요약

## [2026-10-23 18:41] S22 | orchestrator | START
- 한 일: P3 메인 트리
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 1b855d4 [T-20261023-extract-dropped][s19] CLI 보호 문서 문구·건너뜀 요약

## [2026-10-23 18:41] S23 | orchestrator | START
- 한 일: P3 메인 트리
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 1b855d4 [T-20261023-extract-dropped][s19] CLI 보호 문서 문구·건너뜀 요약

## [2026-10-23 18:43] P3 | hook | AUTO
- 한 일: 도구 호출 615회 경과
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 1b855d4 [T-20261023-extract-dropped][s19] CLI 보호 문서 문구·건너뜀 요약

## [2026-10-23 18:43] P3 | hook | AUTO
- 한 일: 도구 호출 630회 경과
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 1b855d4 [T-20261023-extract-dropped][s19] CLI 보호 문서 문구·건너뜀 요약

## [2026-10-23 18:44] P3 | hook | AUTO
- 한 일: 도구 호출 645회 경과
- 변경 파일(미커밋, .ai 제외): src/hwp2md/web/static/app.js src/hwp2md/web/static/index.html src/hwp2md/web/static/style.css tests/unit/test_web_runtime_zip.py 
- 커밋: 1b855d4 [T-20261023-extract-dropped][s19] CLI 보호 문서 문구·건너뜀 요약

## [2026-10-23 18:44] P3 | hook | AUTO
- 한 일: 도구 호출 660회 경과
- 변경 파일(미커밋, .ai 제외): README.md src/hwp2md/web/static/app.js src/hwp2md/web/static/index.html src/hwp2md/web/static/style.css tests/unit/test_web_runtime_zip.py 
- 커밋: 1b855d4 [T-20261023-extract-dropped][s19] CLI 보호 문서 문구·건너뜀 요약

## [2026-10-23 18:45] P3 | hook | AUTO
- 한 일: 도구 호출 675회 경과
- 변경 파일(미커밋, .ai 제외): README.md design/v3/app.html design/v3/css/app.css design/v3/js/app.js design/v3/js/demo-engine.js design/v3/js/demo-payload.js docs/decisions.md src/hwp2md/web/static/app.js src/hwp2md/web/static/index.html src/hwp2md/web/static/style.css tests/unit/test_web_runtime_zip.py 
- 커밋: 1b855d4 [T-20261023-extract-dropped][s19] CLI 보호 문서 문구·건너뜀 요약

## [2026-10-23 18:46] P3 | hook | AUTO
- 한 일: 도구 호출 690회 경과
- 변경 파일(미커밋, .ai 제외): NOTICE README.md design/v3/app.html design/v3/css/app.css design/v3/index.html design/v3/js/app.js design/v3/js/demo-engine.js design/v3/js/demo-payload.js docs/decisions.md docs/system-overview.md src/hwp2md/web/static/app.js src/hwp2md/web/static/index.html src/hwp2md/web/static/style.css LICENSE tests/unit/test_web_runtime_zip.py 
- 커밋: 1b855d4 [T-20261023-extract-dropped][s19] CLI 보호 문서 문구·건너뜀 요약

## [2026-10-23 18:48] P3 | hook | AUTO
- 한 일: 도구 호출 705회 경과
- 변경 파일(미커밋, .ai 제외): NOTICE README.md design/v3/README.md design/v3/app.html design/v3/css/app.css design/v3/index.html design/v3/js/app.js design/v3/js/demo-engine.js design/v3/js/demo-payload.js docs/decisions.md docs/feature-reference.md docs/system-overview.md pyproject.toml src/hwp2md/web/static/app.js src/hwp2md/web/static/index.html src/hwp2md/web/static/style.css LICENSE docs/extraction-limits.md tests/unit/test_web_runtime_zip.py 
- 커밋: 1b855d4 [T-20261023-extract-dropped][s19] CLI 보호 문서 문구·건너뜀 요약

## [2026-10-23 18:51] P3 | hook | AUTO
- 한 일: 도구 호출 720회 경과
- 변경 파일(미커밋, .ai 제외): NOTICE README.md design/v3/README.md design/v3/app.html design/v3/css/app.css design/v3/index.html design/v3/js/app.js design/v3/js/demo-engine.js design/v3/js/demo-payload.js docs/decisions.md docs/feature-reference.md docs/system-overview.md pyproject.toml src/hwp2md/web/static/app.js src/hwp2md/web/static/index.html src/hwp2md/web/static/style.css LICENSE docs/extraction-limits.md tests/unit/test_web_runtime_zip.py 
- 커밋: 1b855d4 [T-20261023-extract-dropped][s19] CLI 보호 문서 문구·건너뜀 요약

## [2026-10-23 18:54] P3 | hook | AUTO
- 한 일: 도구 호출 735회 경과
- 변경 파일(미커밋, .ai 제외): NOTICE README.md design/v3/README.md design/v3/app.html design/v3/css/app.css design/v3/index.html design/v3/js/app.js design/v3/js/demo-engine.js design/v3/js/demo-payload.js docs/decisions.md docs/feature-reference.md docs/system-overview.md pyproject.toml src/hwp2md/web/static/app.js src/hwp2md/web/static/index.html src/hwp2md/web/static/style.css LICENSE docs/extraction-limits.md tests/unit/test_web_runtime_zip.py 
- 커밋: 1b855d4 [T-20261023-extract-dropped][s19] CLI 보호 문서 문구·건너뜀 요약

## [2026-10-23 18:55] S20 | implementer(opus) | DONE
- 한 일: 웹 UI: ERROR_TEXT drm·encrypted·unsupported, #skipped(textContent), 바닥글 한컴 문구, test_web_runtime_zip(C17). unit 806P
- 변경 파일(미커밋, .ai 제외): NOTICE README.md design/v3/README.md design/v3/app.html design/v3/css/app.css design/v3/index.html design/v3/js/app.js design/v3/js/demo-engine.js design/v3/js/demo-payload.js docs/decisions.md docs/feature-reference.md docs/system-overview.md pyproject.toml src/hwp2md/web/static/app.js src/hwp2md/web/static/index.html src/hwp2md/web/static/style.css LICENSE docs/extraction-limits.md tests/unit/test_web_runtime_zip.py 
- 커밋: 1b855d4 [T-20261023-extract-dropped][s19] CLI 보호 문서 문구·건너뜀 요약
- 다음: S21 커밋

## [2026-10-23 18:55] S21 | implementer(opus) | DONE
- 한 일: design/v3: #limits 불가6·부분5·제외4·예정3·범위밖1 + extraction-limits 링크, 된 항목 기능으로 이동, 변환 화면 #skipped + '왜 빠졌나요?', drm·encrypted 문구·DRM 데모 버튼, 한컴 고지, demo-payload 재생성(make_payload.py). impeccable 0. 리뷰 불일치 3건 수정
- 변경 파일(미커밋, .ai 제외): NOTICE README.md design/v3/README.md design/v3/app.html design/v3/css/app.css design/v3/index.html design/v3/js/app.js design/v3/js/demo-engine.js design/v3/js/demo-payload.js docs/decisions.md docs/feature-reference.md docs/system-overview.md pyproject.toml LICENSE docs/extraction-limits.md 
- 커밋: 1a5e96d [T-20261023-extract-dropped][s20] 웹 UI 오류 코드·건너뜀 경고·한컴 고지
- 다음: S22 커밋
