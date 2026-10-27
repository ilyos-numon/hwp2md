# PROGRESS — T-20261027-v3-backend (V3 프론트엔드를 실제 백엔드에 연결)

> append-only.

---

## [2026-10-27 14:08] S0 | planner(opus) | DONE
- 한 일: PLAN.md 작성, §7 기본값 자동 승인
- 변경 파일(미커밋, .ai 제외): ".ai/tasks/T-20261027-v3-backend openspec/changes/v3-backend/ 
- 커밋: f80a6a3 [T-20261023-extract-dropped][record] main 병합·푸시
- 다음: /implement S1

## [2026-10-27 14:09] S1 | orchestrator | START
- 한 일: vendor 자원 내려받기와 라이선스 동봉
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 8ecbc3f [T-20261027-v3-backend][record] PROGRESS 위치 정정

## [2026-10-27 14:10] S1 | hook | AUTO
- 한 일: 자동 체크포인트 (stop)
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 8ecbc3f [T-20261027-v3-backend][record] PROGRESS 위치 정정
- 메모: STATE.md의 '다음 행동' 확인 후 이어서

## [2026-10-27 14:10] S1 | hook | AUTO
- 한 일: 도구 호출 15회 경과
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 1cc5cd5 [T-20261027-v3-backend][S1][wip] auto checkpoint (stop)

## [2026-10-27 14:12] S1 | implementer(opus) | DONE
- 한 일: GSAP 4·글꼴 4·라이선스·README 동봉 (2.4M). Pretendard LICENSE 실제 위치 dist/LICENSE.txt
- 변경 파일(미커밋, .ai 제외): src/hwp2md/web/static/vendor/README.md src/hwp2md/web/static/vendor/fonts/JetBrainsMono-Medium.woff2 src/hwp2md/web/static/vendor/fonts/JetBrainsMono-Regular.woff2 src/hwp2md/web/static/vendor/fonts/JetBrainsMono-SemiBold.woff2 src/hwp2md/web/static/vendor/fonts/OFL-JetBrainsMono.txt src/hwp2md/web/static/vendor/fonts/OFL-Pretendard.txt src/hwp2md/web/static/vendor/fonts/PretendardVariable.woff2 src/hwp2md/web/static/vendor/fonts/fonts.css src/hwp2md/web/static/vendor/gsap/LICENSE.md src/hwp2md/web/static/vendor/gsap/ScrambleTextPlugin.min.js src/hwp2md/web/static/vendor/gsap/ScrollTrigger.min.js src/hwp2md/web/static/vendor/gsap/SplitText.min.js src/hwp2md/web/static/vendor/gsap/gsap.min.js src/hwp2md/web/static/vendor/marked.LICENSE.md 
- 커밋: 1cc5cd5 [T-20261027-v3-backend][S1][wip] auto checkpoint (stop)
- 다음: S2
- 메모: FONT_FALLBACK 아님, GSAP 재다운로드 바이트 일치

## [2026-10-27 14:12] S1 | orchestrator | DONE
- 한 일: vendor 자원 내려받기와 라이선스 동봉 검증 통과
- 변경 파일(미커밋, .ai 제외): src/hwp2md/web/static/vendor/README.md src/hwp2md/web/static/vendor/fonts/JetBrainsMono-Medium.woff2 src/hwp2md/web/static/vendor/fonts/JetBrainsMono-Regular.woff2 src/hwp2md/web/static/vendor/fonts/JetBrainsMono-SemiBold.woff2 src/hwp2md/web/static/vendor/fonts/OFL-JetBrainsMono.txt src/hwp2md/web/static/vendor/fonts/OFL-Pretendard.txt src/hwp2md/web/static/vendor/fonts/PretendardVariable.woff2 src/hwp2md/web/static/vendor/fonts/fonts.css src/hwp2md/web/static/vendor/gsap/LICENSE.md src/hwp2md/web/static/vendor/gsap/ScrambleTextPlugin.min.js src/hwp2md/web/static/vendor/gsap/ScrollTrigger.min.js src/hwp2md/web/static/vendor/gsap/SplitText.min.js src/hwp2md/web/static/vendor/gsap/gsap.min.js src/hwp2md/web/static/vendor/marked.LICENSE.md 
- 커밋: 1cc5cd5 [T-20261027-v3-backend][S1][wip] auto checkpoint (stop)
- 다음: S2 시작

## [2026-10-27 14:12] S2 | orchestrator | START
- 한 일: 변환 화면 이식과 실제 MODES 연결
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 6b1e797 [T-20261027-v3-backend][s1] vendor GSAP·글꼴·라이선스 동봉

## [2026-10-27 14:12] S2 | hook | AUTO
- 한 일: 자동 체크포인트 (stop)
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 6b1e797 [T-20261027-v3-backend][s1] vendor GSAP·글꼴·라이선스 동봉
- 메모: STATE.md의 '다음 행동' 확인 후 이어서

## [2026-10-27 14:12] S2 | hook | AUTO
- 한 일: 도구 호출 30회 경과
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 81a9365 [T-20261027-v3-backend][S2][wip] auto checkpoint (stop)

## [2026-10-27 14:14] S2 | hook | AUTO
- 한 일: 도구 호출 45회 경과
- 변경 파일(미커밋, .ai 제외): src/hwp2md/web/static/app.js src/hwp2md/web/static/index.html src/hwp2md/web/static/style.css src/hwp2md/web/static/css/ src/hwp2md/web/static/js/ 
- 커밋: 81a9365 [T-20261027-v3-backend][S2][wip] auto checkpoint (stop)

## [2026-10-27 14:17] S2 | hook | AUTO
- 한 일: 자동 체크포인트 (stop)
- 변경 파일(미커밋, .ai 제외): src/hwp2md/web/static/app.js src/hwp2md/web/static/css/app.css src/hwp2md/web/static/css/base.css src/hwp2md/web/static/index.html src/hwp2md/web/static/js/app.js src/hwp2md/web/static/js/theme.js src/hwp2md/web/static/style.css 
- 커밋: 81a9365 [T-20261027-v3-backend][S2][wip] auto checkpoint (stop)
- 메모: STATE.md의 '다음 행동' 확인 후 이어서

## [2026-10-27 14:17] S2 | hook | AUTO
- 한 일: 도구 호출 60회 경과
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 0286fe7 [T-20261027-v3-backend][S2][wip] auto checkpoint (stop)

## [2026-10-27 14:18] S2 | implementer(opus) | DONE
- 한 일: V3 index.html·js/app.js·theme.js·base/app.css 이식, MODES 원본 이식, 구 app.js·style.css 삭제. 62 passed
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 0286fe7 [T-20261027-v3-backend][S2][wip] auto checkpoint (stop)
- 다음: reviewer
- 메모: renderRaw 끝 개행 보정 추가. 8765 포트는 voice-agent 사용 중이라 8766 사용

## [2026-10-27 14:18] S2 | reviewer(sonnet) | DONE
- 한 일: PASS, FINDINGS none
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 0286fe7 [T-20261027-v3-backend][S2][wip] auto checkpoint (stop)
- 다음: S3

## [2026-10-27 14:18] S2 | orchestrator | DONE
- 한 일: 변환 화면 이식과 실제 MODES 연결 검증 통과
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 0286fe7 [T-20261027-v3-backend][S2][wip] auto checkpoint (stop)
- 다음: S3 시작

## [2026-10-27 14:18] S3 | orchestrator | START
- 한 일: 소개 페이지 /about 연결
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 82325b7 [T-20261027-v3-backend][s2] V3 변환 화면을 /api·브라우저 모드에 연결

## [2026-10-27 14:18] S3 | hook | AUTO
- 한 일: 자동 체크포인트 (stop)
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 82325b7 [T-20261027-v3-backend][s2] V3 변환 화면을 /api·브라우저 모드에 연결
- 메모: STATE.md의 '다음 행동' 확인 후 이어서

## [2026-10-27 14:18] S3 | hook | AUTO
- 한 일: 도구 호출 75회 경과
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: b89d39c [T-20261027-v3-backend][S3][wip] auto checkpoint (stop)

## [2026-10-27 14:20] S3 | hook | AUTO
- 한 일: 자동 체크포인트 (stop)
- 변경 파일(미커밋, .ai 제외): src/hwp2md/web/app.py src/hwp2md/web/static/about.html src/hwp2md/web/static/css/landing.css src/hwp2md/web/static/js/effects.js src/hwp2md/web/static/js/landing.js tests/unit/test_web_app.py 
- 커밋: b89d39c [T-20261027-v3-backend][S3][wip] auto checkpoint (stop)
- 메모: STATE.md의 '다음 행동' 확인 후 이어서

## [2026-10-27 14:21] S3 | implementer(opus) | DONE
- 한 일: about.html·landing.css·effects.js·landing.js 이식, GET /about, 단위 테스트 2개. 26 passed, 외부 요청 0
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 61f2fd8 [T-20261027-v3-backend][S3][wip] auto checkpoint (stop)
- 다음: reviewer

## [2026-10-27 14:21] S3 | reviewer(sonnet) | DONE
- 한 일: PASS, FINDINGS 없음
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 61f2fd8 [T-20261027-v3-backend][S3][wip] auto checkpoint (stop)
- 다음: S4
- 메모: full_page 스크린샷은 ScrollTrigger 로 빈 구간 있음(정상)

## [2026-10-27 14:21] S3 | orchestrator | DONE
- 한 일: 소개 페이지 /about 연결 검증 통과
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 61f2fd8 [T-20261027-v3-backend][S3][wip] auto checkpoint (stop)
- 다음: S4 시작

## [2026-10-27 14:21] S4 | orchestrator | START
- 한 일: 문서 갱신
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 1198aee [T-20261027-v3-backend][s3] 소개 페이지 /about 연결

## [2026-10-27 14:21] S4 | hook | AUTO
- 한 일: 도구 호출 90회 경과
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 1198aee [T-20261027-v3-backend][s3] 소개 페이지 /about 연결

## [2026-10-27 14:21] S4 | hook | AUTO
- 한 일: 자동 체크포인트 (stop)
- 변경 파일(미커밋, .ai 제외): 없음
- 커밋: 1198aee [T-20261027-v3-backend][s3] 소개 페이지 /about 연결
- 메모: STATE.md의 '다음 행동' 확인 후 이어서

## [2026-10-27 14:23] S4 | hook | AUTO
- 한 일: 도구 호출 105회 경과
- 변경 파일(미커밋, .ai 제외): NOTICE README.md design/v3/README.md docs/decisions.md docs/feature-reference.md 
- 커밋: f16f42d [T-20261027-v3-backend][S4][wip] auto checkpoint (stop)

## [2026-10-27 14:23] S4 | implementer(opus) | DONE
- 한 일: README②·feature-reference(표1·§8.1·§9·§9.1·§9.8·§12)·decisions·NOTICE·design/v3/README 갱신
- 변경 파일(미커밋, .ai 제외): NOTICE README.md design/v3/README.md docs/decisions.md docs/feature-reference.md 
- 커밋: f16f42d [T-20261027-v3-backend][S4][wip] auto checkpoint (stop)
- 다음: S5
- 메모: NOTICE 머리말 Apache 2.0 → original licenses 일반화

## [2026-10-27 14:23] S4 | orchestrator | DONE
- 한 일: 문서 갱신 검증 통과(grep·sanitize)
- 변경 파일(미커밋, .ai 제외): NOTICE README.md design/v3/README.md docs/decisions.md docs/feature-reference.md 
- 커밋: f16f42d [T-20261027-v3-backend][S4][wip] auto checkpoint (stop)
- 다음: S5 시작
